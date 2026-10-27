# M2_lead_lag: lead-lag and cross-asset structure for asynchronous ZS, ZL and ZM, and how to trade a ZM dislocation

Stage E.32, Part M2. Worker LeadLagMath-OpusHigh (re-spawned 2026-10-27 00:16 PDT; the first instance saved the
pages and M2_examples.py/.json but no output file). No market data was read, no statistic was derived from data,
N stays 538.

Files:
- Evidence pages and log: reports/stage_e32_briefs/pages/M2_lead_lag/ (log.tsv).
- Worked examples: reports/stage_e32_briefs/work/M2_lead_lag/M2_examples.py -> M2_examples.json (sha256 986e6b00...)
  and M2_examples2.py -> M2_examples2.json (sha256 72694be4...). Every number below that is not hand arithmetic
  comes from one of these two JSON files, named by key.
- Inputs used: the E.32 standard ZM numbers (READER_BRIEF.md; from A0_contract_stats Table 1), the Topstep ZM
  market-order break-even mu*_mkt = 1.59 ticks (reports/stage_e28_ranking.md line 130, row "6 | topstep | ZM",
  column mu*_mkt), and E.28 2.1, 2.5 and 2.10 (cited, not repeated).

Conventions:
- Tick units throughout: ZM tick = 0.10 USD/short ton (10 USD), ZS tick = 0.25 cents/bu (12.50 USD), ZL tick =
  0.01 cents/lb (6 USD).
- "Random-walk scaling" means sigma_h = sigma_1m x sqrt(h); it is an assumption wherever it is used.
- sigma_1s under random-walk scaling (M2_examples2.json, sigma_1s_ticks): ZM 3.15/sqrt(60) = 0.4067 ticks,
  ZS 3.11/sqrt(60) = 0.4015 ticks, ZL 5.52/sqrt(60) = 0.7126 ticks.
- [derived] marks my own algebra; [unverified] marks a claim not checked against fetched full text.

## Bottom line (for the lead)

1. The crush relation is the only cross-asset structure here that operates at minutes. The method chain is:
   - a causal crush residual (fixed 10:11:9-type weights, plus a causal rolling or Kalman-filtered beta);
   - a half-life estimated by session and hour with small-sample bias handled;
   - an early test of which leg closes the residual.
   ZM's gross reversion per trade is s_M x D x (1 - 2^-m) / b_M ticks, where s_M is ZM's share of the
   adjustment, D the dislocation in cents/bu, b_M the ZM weight (0.22 physical, 0.19 Zhou median) and m the time
   stop in half-lives.
   - Break-even share at D = 1 cent, m = 1, b_M = 0.22: s_M* = 1.59 x 0.22 / (1 x 0.5) = 0.70.
   - At D = 2 cents it is 0.35.
   - So "ZM is the adjusting leg" must be read quantitatively. With D around 1 cent, ZM needs about 70% of the
     adjustment.
2. Second-scale lead-lag (HY / HRY) is real in other markets but cannot pay a 1.59-tick hurdle at 300-1,000 ms
   latency. In a pure-shift model even rho = 1 and a 2 s lag leave a predictable ZM move with an SD of 0.53 ticks
   after 0.3 s, so a 3-sigma ZS impulse is needed to break even (M2_examples2.json, b_shift_model).
   Verdict: feature or conditioner only. This agrees with the planner and with Huth and Abergel.
3. Standard price-discovery shares (Hasbrouck IS, Gonzalo-Granger/HMW CS, Putnins ILS) assume ONE common efficient
   price. The board crush has three prices and one cointegrating relation, so two common trends.
   - The shares therefore do not apply directly [derived].
   - Use the VECM alpha loadings, weak-exogeneity tests and the adjustment-contribution share
     s_i = beta_i alpha_i / (beta' alpha).
   - Or apply IS/CS/ILS to the bivariate pair (0.22 x ZM, implied meal = ZS - 0.11 ZL), which has one common trend.
4. Two data traps are specific to this pair set:
   - ZS has no October or December contract, while ZM and ZL do [unverified: contract months from contract
     knowledge, not a fetched spec; DataFacts to confirm from definitions].
   - ZS and ZL are owned only as the front contract (MBP-1).
   - So a v_0 crush mixes contract months around rolls (for example ZS Nov against ZM/ZL Oct or Dec). The
     protocol must fix a month mapping, or exclude those windows.
   - Second trap: Zhou et al.'s cointegrating vector is estimated per day with a Kalman smoother and EM, which is
     same-day look-ahead if reused in a signal.

## (a) Hayashi-Yoshida covariance for asynchronous ticks, and the Epps effect

**1. Core idea.**
- ZS, ZL and ZM update at their own random times. Sampling all three on a common grid with the previous tick
  ("synchronising") makes many true co-movements fall into different grid cells, so measured correlation falls as
  the grid gets finer: the Epps effect.
- The Hayashi-Yoshida (HY) estimator skips the grid. It sums the products of every pair of increments whose
  observation intervals overlap.

**2. Equations.**
- Target (HY 2008, display before eq. 3): <P1, P2>_T = integral_0^T sigma1_t sigma2_t rho_t dt.
  - P1, P2: log prices (here, tick-unit mids are used instead, which only rescales).
  - sigma: spot volatilities; rho_t: spot correlation.
- HY estimator (HY 2008, Definition 1, eq. 3):
  U_n = sum_{i,j} (P1(T1_i) - P1(T1_{i-1})) (P2(T2_j) - P2(T2_{j-1})) 1{I_i intersect J_j != empty}.
  - T1_i: the i-th observation time of P1; I_i = (T1_{i-1}, T1_i]. T2_j and J_j likewise for P2.
  - The pdftotext copy drops the "!=" glyph. The prose fixes it: a product contributes "only when the respective
    observation intervals I i and J j are overlapping".
- Cost: the number of non-zero terms is about n1 + n2 minus the common times (HY 2008, text after eq. 3), so it is
  linear, not quadratic. Implement it as a two-pointer sweep, as M2_examples.py does.
- Correlation: rho_HY = U_n / sqrt(RV1 x RV2), where RVk = sum of squared increments of Pk at its own times.
  - [derived; standard normalisation, not a numbered equation in the fetched text.]
  - RV is biased upward by microstructure noise at tick level (E.28 2.1 section 6 covers TSRV), so rho_HY on raw
    ticks is biased toward zero even when U_n is unbiased.
- Previous-tick realised covariance on grid step Delta: RC_Delta = sum_k (P1(t_k) - P1(t_{k-1})) (P2(t_k) - P2(t_{k-1})),
  with Pk(t) = the last observed price at or before t. This is the estimator that shows the Epps effect.
- Causes of the Epps effect (Toth and Kertesz): it "was traced back to the trading asynchronicity and to the
  occasional lead-lag relation", but these "alone ... are insufficient to give account for the whole effect".

**3. Worked examples.**
- (i) Hand example (M2_examples.json, a_hy_toy). ZS and ZM mids over 3 s, in ticks, at their own times:
  - ZS at t = 0, 0.4, 1.3, 2.1, 2.6, 3.0 s: 0, 1, 1, 2, 1, 1. ZS increments:
    - (0, 0.4]: +1
    - (0.4, 1.3]: 0
    - (1.3, 2.1]: +1
    - (2.1, 2.6]: -1
    - (2.6, 3.0]: 0
  - ZM at t = 0, 0.7, 1.6, 2.4, 3.0 s: 0, 0, 1, 1, 0. ZM increments:
    - (0, 0.7]: 0
    - (0.7, 1.6]: +1
    - (1.6, 2.4]: 0
    - (2.4, 3.0]: -1
  - Non-zero products with overlapping intervals:
    - ZS (1.3, 2.1] x ZM (0.7, 1.6]: they overlap on (1.3, 1.6], giving +1.
    - ZS (2.1, 2.6] x ZM (2.4, 3.0]: they overlap on (2.4, 2.6], giving (-1)(-1) = +1.
    - Every other non-zero pair is disjoint (for example ZS (0, 0.4] x ZM (0.7, 1.6]).
  - So U = 2 ticks^2.
  - Previous-tick on a 1 s grid (t = 0, 1, 2, 3):
    - ZS = 0, 1, 1, 1, so increments +1, 0, 0.
    - ZM = 0, 0, 1, 0, so increments 0, +1, -1.
    - RC_1s = 0.
  - On a 0.5 s grid:
    - ZS = 0, 1, 1, 1, 1, 2, 1.
    - ZM = 0, 0, 0, 0, 1, 1, 0.
    - Only the last pair is non-zero, so RC_0.5s = (-1)(-1) = 1.
  - Check: the JSON gives hy_sum_ticks2 = 2.0, rc = 0 (1 s) and rc = 1 (0.5 s), matching the hand sums.
  - The 1 s grid erased both co-movements; HY kept both.
- (ii) Epps Monte Carlo (M2_examples.json, a_epps_mc; 40 replications).
  - ASSUMPTIONS, not data:
    - Two Brownian mids with sigma_1m = 3.11 (ZS) and 3.15 (ZM) ticks.
    - True correlation 0.6 and no lead-lag.
    - Independent Poisson observation times with mean gaps of 3 s (ZS) and 6 s (ZM), over a 290-minute day
      session.
  - Results:
    - Previous-tick correlation by grid step: 1 s: 0.060; 5 s: 0.229; 15 s: 0.411; 60 s: 0.546; 300 s: 0.583.
    - HY: 0.600 (SD 0.022).
  - Check: HY recovers the true 0.6 within one SD, and the previous-tick curve rises monotonically toward 0.6.
  - Consequence for minute-bar hedge ratios (M2_examples2.json, a_epps_atten): an OLS beta of ZM on ZS returns is
    attenuated by about 0.5457/0.6 = 0.909 at 1 minute and 0.583/0.6 = 0.972 at 5 minutes. This assumes unbiased
    variances and these sampling gaps.

**4. Data.**
- Event-time mids:
  - ZM from MBO, by rebuilding the book to the BBO.
  - ZS and ZL from MBP-1, whose BBO comes directly.
- Use one clock for all three roots (receive time, with exchange time as a check; field semantics belong to
  DataFacts).
- HY matters for sub-minute work (lead-lag, a sub-minute hedge-ratio input). At 5 minutes or longer,
  previous-tick bars lose about 3% of correlation under these assumptions.

**5. Leakage and look-ahead traps.**
- (i) The overlap indicator uses interval END times. An increment ending after decision time t must not enter a
  feature at t.
  - Test: truncate the tick stream at t, recompute, and require bit-identity with the full-stream feature value.
- (ii) A clock offset between the MBO (ZM) and MBP-1 (ZS, ZL) streams creates a false lead-lag.
  - Test: the HY lead-lag contrast of a stream against itself must peak at lag 0.
  - Any cross-root offset found is reported as a clock fact, not traded.
[MathReview A-2 (lead: accepted): neither test can detect the named offset (a stream against itself peaks at lag 0 by construction, and bid and ask of one root come from the same stream); use ts_event (exchange time) for the HY/HRY estimator and keep ts_recv for the latency/tradability analysis, with detecting tests (i) per root and session, the distribution of ts_recv - ts_event, the difference of medians across roots below the fine mesh, and (ii) a cross-root placebo with a known simultaneous timestamp (the first message at or after the 08:30:00 open and the 13:20:00 close in each root, or the settlement/clearing message sequence) giving theta_hat = 0. This also applies to (b) trap iii (original lines 253-254) and the (a) data clock bullet (original line 131).]
- (iii) Normalising rho_HY by full-day realised variances uses the rest of the day.
  - Test: a past-only denominator must equal a truncated recomputation.

**6. Compute.**
- One two-pointer HY pass is O(n1 + n2).
- Daily event counts await DataFacts. Even at 10^6 events per root per day over about 815 sessions (39 months),
  2 x 10^6 x 815 = 1.6 x 10^9 steps is minutes in numba on one core.
- RAM is one day's events: about 16 bytes per event, so 16 MB per 10^6 events.

**7. Verdict: MAYBE.**
- Use HY where sub-minute co-movement enters a design quantity: a sub-minute hedge-ratio input to (c), and the
  lead-lag diagnostic of (b).
- It is not a ZM direction predictor.
- At 5 minutes or longer, previous-tick bars suffice.

**8. Evidence.**

| Claim | Source (type) | Verbatim quote | File |
|---|---|---|---|
| HY needs no synchronisation | Hayashi and Yoshida 2008, AISM 60 (academic) | "we proposed a new estimator which is free of any 'synchronization' processing of the original data and showed that it is consistent for the true covariance" | hayashi_yoshida_2008_aism.pdf(.txt) |
| HY sums overlapping intervals | same, Definition 1, eq. (3) | "will make a contribution to the sum only when the respective observation intervals I i and J j are overlapping" | same |
| HY cost is linear | same | "the number equals to the number of grids in 1 plus that in 2, minus the number of grids that are common in both" | same |
| Synchronisation bias | same | "most of the existing approaches rely on the 'synchronization' of the original data, hence, suffer 'synchronization' bias" | same |
| Epps effect | Toth and Kertesz, arXiv 0704.1099 (academic) | "1979 Epps reported results showing that stock return correlations decrease as the sampling frequency of data increases" | toth_kertesz_epps_revisited.pdf(.txt) |
| Causes of Epps | Toth and Kertesz, arXiv physics/0701110 (academic) | "was traced back to the trading asynchronicity and to the occasional lead-lag relation between the prices ... alone these aspects are insufficient to give account for the whole effect" | toth_kertesz_origin_epps.pdf(.txt) |
| HY 2005 original | Hayashi and Yoshida 2005, Bernoulli 11(2) | [unverified: Project Euclid returned a 1,156-byte bot page; cited via HY 2008 and HRY 2013] | hayashi_yoshida_2005.pdf (bot page) |

## (b) Lead-lag via the Hoffmann-Rosenbaum-Yoshida (2013) contrast

**1. Core idea.**
- Shift one series in time by a candidate lag, compute the HY covariance of the shifted pair, and repeat over a
  lag grid. The lag that maximises |covariance| estimates the lead-lag parameter theta.
- HRY show this estimator is consistent on non-synchronous data, at a rate set by the largest gap between
  observations.
- It tells you WHEN the follower catches up. It does not tell you how much predictable move is left after your
  latency, which is what a 1-lot trader needs.

**2. Equations** (Hoffmann, Rosenbaum and Yoshida 2013, Bernoulli; arXiv 1303.4871).
- Model (HRY eq. 1-3):
  - X_t = x0 + sigma1 B1_t and Y~_t = y0 + sigma2 B2_t, with <B1, B2>_t = rho t.
  - The lagged version is tau_theta(Y~)_t := Y~_{t-theta}, t in [theta, T] (eq. 1).
  - Equivalently, tau_theta(Y~)_t = y0 + rho sigma2 B1_{t-theta} + sigma2 (1 - rho^2)^{1/2} W_{t-theta}.
  - So X anticipates Y by theta when theta >= 0.
- Shifted HY contrast (HRY, display before eq. 9):
  U_n(theta~) = 1{theta~ >= 0} sum_{I,J: I <= T} X(I) Y(J) 1{I intersect (J - theta~) != empty}
              + 1{theta~ < 0} sum_{I,J: J <= T} X(I) Y(J) 1{J intersect (I + theta~) != empty}.
  - X(I), Y(J): increments over observation intervals I, J.
  - J - theta~: J shifted back by theta~.
- Estimator (HRY eq. 9): theta_hat maximises |U_n(theta~)| over a finite grid G_n (assumption B3: G_n contains 0).
- Rate: the accuracy is about Delta_n^{-1} (Delta_n = the largest gap between data points), not Delta_n^{-1/2}
  (HRY section 1.2 and Theorem 1). HRY show "a simple central limit theorem cannot hold" (Proposition 2).
[MathReview A-1 (lead: accepted): that string is not in the saved text; hry2013_leadlag.pdf.txt lines 488-489 read "In that case, it becomes impossible, in general, to derive a simple central limit theorem for ϑ̂_n." (keep the Proposition 1 context: the normalised estimator "weakly converges to a Dirac mass at point ϑ"). The same correction applies to the evidence-table row "Rate Delta_n^{-1}; no simple CLT" (original line 280).]
- Degeneracy: if rho is of order Delta_n^{1/2}, "maximizing |U n (theta)| does not locate the true value"
  (HRY, after Proposition 1).
- Empirical practice in HRY section 6 (FDAX against Bund):
  - Subsample to one trade in 20 (chosen from a signature plot).
  - A coarse grid of -10 to +10 minutes with mesh 30 s, then a fine grid of -5 to +5 s with mesh 0.1 s.
  - Result: FDAX leads by about 0.8 s on 2010-10-13, and "systematically negative" lags over October 2010.
- Lead/Lag Ratio (Huth and Abergel 2014): LLR = sum_{i=1..p} rho^2(l_i) / sum_{i=1..p} rho^2(-l_i), where
  rho(l) is the HY cross-correlation at lag l. LLR > 1 means X leads Y. It is closely related to Granger
  causality. LLR measures asymmetry, not just the peak location, and is a better summary for a feature.

**3. Worked example: what is left for a 1-lot at 300-1,000 ms latency.**
- Setting: pure-shift model with ZS leading ZM by theta seconds.
  - At decision time t, the ZS path over (t - theta, t] is known. ZM will copy rho times that path over the next
    theta seconds.
  - A trader whose order lands L seconds later can only capture the part of the copy after t + L.
- Predictable ZM move after latency [derived from HRY eq. 1-3]: rho x sigma_ZM,1s x sqrt(max(theta - L, 0)), with
  sigma_ZM,1s = 3.15/sqrt(60) = 0.4067 ticks/sqrt(s) under random-walk scaling.
- Cases (M2_examples2.json, b_shift_model):
  - theta = 1 s, L = 0.3 s, rho = 0.6:
    - SD = 0.6 x 0.4067 x sqrt(0.7) = 0.6 x 0.4067 x 0.8367 = 0.2041 ticks.
    - Clearing the 1.59-tick hurdle in expectation needs a ZS impulse of 1.59/0.2041 = 7.8 SDs of that
      conditional move.
  - theta = 2 s, L = 0.3 s, rho = 1 (best case):
    - SD = 0.4067 x sqrt(1.7) = 0.5302 ticks.
    - It needs a 3.0-SD impulse.
  - Any theta <= L leaves exactly 0. HRY's FDAX/Bund lag of about 0.8 s and the millisecond lags reported for
    CME index and Treasury futures (Shiotani et al. 2026: peaks "at 5 milliseconds") fall below or near L.
- Second check with a static bound:
  - The largest ZM move per ZS tick if ZM fully copies ZS at rho = 1 is the regression slope sigma_ZM/sigma_ZS =
    3.15/3.11 = 1.013 ZM ticks per ZS tick.
  - Clearing 1.59 ticks needs 1.59/1.013 = 1.57 ZS ticks of not-yet-copied move.
  - That is 1.57/0.4015 = 3.9 one-second SDs of ZS (M2_examples2.json, b_zs_1s_move_needed_sigma) under
    random-walk scaling.
  - The crush-equivalent ratio (0.25 c ZS tick / 0.22 c ZM tick = 1.136 ZM ticks per ZS tick, if ZM alone absorbs
    the crush change) gives a similar 1.4 ZS ticks.
- One-line check: both routes say a ZS impulse of about 4 one-second SDs must be fully unpriced in ZM at
  order arrival before a market-order trade breaks even. Such impulses are rare, and they are what HFT trades
  first (Huth and Abergel: "a naive strategy based on market orders cannot make any profit of this effect because
  of the bid/ask spread").
- Context only, not analysed: E.31 saw on the discovery dates that passive ZM fills after a ZS move against the
  order in the prior 1 s averaged -1.100 ticks at 10 s, against -0.652 after a ZS move with it
  (reports/E.31_RETURN.md 3.5). The lead-lag information is real enough to show up in adverse selection, which
  is a conditioner, not a directional edge.

**4. Data.**
- ZM BBO mid changes (rebuilt from MBO) and ZS/ZL MBP-1 BBO mid changes, in event time on one clock.
- Lag grid: coarse -60 to +60 s at 1 s mesh, then fine -5 to +5 s at 0.05-0.1 s mesh (HRY's two-step design).
  The grid's bounds and mesh are frozen before any run.
- Estimate per session, then summarise the distribution of theta_hat and LLR by session type and hour.
- For a minutes-scale feature, the useful outputs are:
  - the LLR at lags 1-30 s;
  - "ZS moved >= k ticks in the last 1-5 s and ZM has not" (a conditioner).

**5. Leakage and look-ahead traps.**
- (i) theta_hat chosen on the whole sample and then used as a feature lag is a selected parameter.
  - Count it into N, or fix the lag a priori (for example 1 s).
  - Test: refit theta_hat on fold-only data and check that the feature is built only from that.
- (ii) Subsampling "one trade in 20" chosen from a full-day signature plot uses the day's own noise level.
  - Fix the subsampling rule before the run.
- (iii) Timestamp skew between the feeds creates a spurious theta.
  - Test: a placebo pair with a known zero lag (bid against ask of the same root) must give theta_hat = 0.
- (iv) Liquidity alone makes the more active asset look like the leader under previous-tick sampling. Huth and
  Abergel show this for the previous-tick cross-correlation, not for the HY version.
  - Test (Huth and Abergel's surrogate): simulate synchronously correlated Brownian motions with rho = rho_HY(0),
    and sample them at the true ZS and ZM timestamps. The surrogate LLR must be about 1 (theirs are 1.00).
  - The real LLR is compared with that surrogate distribution, not with 1.

**6. Compute.**
- U_n at one lag is one HY pass, O(n1 + n2).
- A 121-point coarse grid plus a 101-point fine grid is about 222 passes per session.
- At 2 x 10^5 mid changes per day (an assumption) and 815 sessions: 222 x 4 x 10^5 x 815 = 7 x 10^10 steps.
  That is tens of minutes in numba on 8 cores. Memory is one day.

**7. Verdict: SKIP as a signal family; MAYBE as a conditioner.**
- At 300-1,000 ms latency the predictable remainder is under 1 tick except after 3-8 SD ZS impulses.
- It agrees with the planner ("a feature only").
- It belongs as one frozen conditioner in the ML feature set (ZS/ZL impulse in the last 1-5 s that ZM has not
  matched), counted once.

**8. Evidence.**

| Claim | Source (type) | Verbatim quote | File |
|---|---|---|---|
| Lead-lag model and estimator | HRY 2013, Bernoulli (academic; arXiv 1303.4871v1) | "By applying a certain contrast optimization based on a modified version of the Hayashi-Yoshida covariation estimator, we obtain a consistent estimator of the lead-lag parameter" | hry2013_leadlag.pdf(.txt) |
| Contrast maximised over grid | same, eq. (9) | "Our estimator theta_n is obtained by maximizing the contrast ... |U n (theta)| over the finite grid G n" | same |
| No pre-processing needed | same | "Our estimator is robust to non-synchronous data and does not require any pre-processing contrary to the previous tick algorithm" | same |
| Rate Delta_n^{-1}; no simple CLT | same | "the rate of convergence of our estimator is essentially Delta n^-1 and not Delta n^-1/2"; "a simple central limit theorem cannot hold for our estimator" | same |
| Small rho degenerates | same | "if rho is too small ... maximizing |U n (theta)| does not locate the true value" | same |
| Profitability out of scope | same | "The quantization of statistical arbitrage in terms of theta ... lies beyond the scope of this paper" | same |
| FDAX/Bund about 1 s, two-step grid | same, section 6 | "the FDAX seems to lead the Bund, with a small lead lag value of -0.8 second"; "estimated values are relatively small (the order of one second)" | same |
| LLR definition; liquid assets lead | Huth and Abergel 2014 (academic; arXiv 1111.7103v2) | "LLR := sum rho^2(l_i) / sum rho^2(-l_i) > 1"; "the most liquid assets ... tend to lead smaller stocks" | huth_abergel_2014_leadlag.pdf(.txt) |
| 60% hit rate but no market-order profit | same, abstract | "We reach 60% of accuracy when forecasting the next midquote variation of the lagger ... However, a naive strategy based on market orders cannot make any profit of this effect because of the bid/ask spread" | same |
| Liquidity artefact in previous-tick, not in HY | same | "The previous-tick correlation function is blurred by spurious liquidity effects: the asymmetry grows significantly with lambda1/lambda2, yielding he most active Brownian motion to always lead the other. In the contrary, the Hayashi-Yoshida LLR is not impacted by the" (sentence breaks at a footnote) | same |
| Surrogate test design | same | "we generate two synchronously correlated Brownian motions with the same correlation as the two assets rho = rho_HY(0) ... Then we sample these Brownian motions along the true timestamps of the two assets" | same |
| Millisecond lags at CME | Shiotani, Hayashi and Koike 2026 (academic; arXiv 2601.01871) | "such relationships can persist only over very short horizons, even on the order of one millisecond or less"; "sharp peaks ... at 5 milliseconds, which is consistent with the optical propagation time between the futures exchange (in Aurora, Illinois) and the cash" | shiotani_hayashi_koike_2026.pdf(.txt) |
| Dobrev and Schaumburg cross-market activity | Dobrev and Schaumburg 2018 | [unverified: the Atlanta Fed URL returned a 404 page; known only through Shiotani et al.'s description] | dobrev_schaumburg_2018.pdf (404 page) |

## (c) Error-correction and OU models of the board crush

**1. Core idea.**
- Soybeans crush into meal and oil, so a fixed-weight combination of ZS, ZM and ZL (the board crush) should be
  stationary while each price wanders. Deviations of that combination are an error-correction term.
- Engle-Granger estimates the weights by regression and tests the residual for a unit root. Johansen's VECM
  estimates the weights and the adjustment speeds jointly. An OU/AR(1) on the residual gives its speed of
  reversion.
- For trading, the residual must be causal: its weights and its mean come only from data before the decision.

**2. Units and equations.**
- Units conversion, stated explicitly [derived from the contract units in the E.32 brief and the yields quoted
  below].
  - One bushel (60 lb) of soybeans: 11 lb of oil and 44 lb = 0.022 short ton of meal, under the CME board-crush
    convention.
  - Rechner and Poitras quote USDA (1988) as "11 lbs. of oil and 48 lbs. of meal". That gives their 10:12:9.
    Poitras's teaching note says CME's crush guide uses 10:11:9 (a secondary statement; the CME guide itself was
    not fetched, under the stage's CME rule).
  - Oil value per bushel = 11 lb x ZL (cents/lb) = 11 ZL cents/bu.
  - Meal value per bushel = 0.022 ton x ZM (USD/ton) = 0.022 ZM USD/bu = 2.2 ZM cents/bu.
  - Board crush, cents/bu: C = 11 x ZL[c/lb] + 2.2 x ZM[USD/ton] - ZS[c/bu].
  - In ticks (nS, nL, nM = prices in ticks of 0.25 c/bu, 0.01 c/lb, 0.10 USD/ton):
    C = 0.11 nL + 0.22 nM - 0.25 nS cents/bu.
  - Per tick, the crush moves:
    - ZL: 11 x 0.01 = 0.11 c/bu.
    - ZM: 2.2 x 0.10 = 0.22 c/bu.
    - ZS: 0.25 c/bu.
  - Zhou et al.'s normalisation (ZS = 1; "CME (physical)" row 1, -0.11, -0.22; Table 6) is reproduced exactly when
    ZS is in cents/bu and ZL and ZM are in ticks: z = ZS[c] - 0.11 nL - 0.22 nM = -C.
    - Zhou et al. do not state their units in the fetched text, so this reading is [derived].
    - Every cents-per-ZM-tick figure below is unit-invariant, because it uses only the ratio of the ZM
      coefficient to the physical 0.22.
- 10:11:9 in contract units:
  - 10 ZS = 50,000 bu.
  - 11 ZM = 1,100 tons, which is 0.022 ton/bu: exact.
  - 9 ZL = 540,000 lb, which is 10.8 lb/bu, 1.8% short of 11.
  - So the 10:11:9 position's crush is C_10:11:9 = 10.8 ZL + 2.2 ZM - ZS cents/bu, worth 50,000 x 0.01 = 500 USD
    per cent/bu (Rechner and Poitras give the same 500 USD for their 10:12:9).
  - Check: 11 ZM ticks = 11 x 10 USD = 110 USD = 50,000 bu x 0.22 c = 110 USD.
- Engle-Granger (MacKinnon 2010, eq. 1): regress y_t1 = a1 + sum_{j=2..N} a_j y_tj + u_t (here y1 = ZS in cents,
  y2 = ZL ticks, y3 = ZM ticks). Then test z_hat_t = y_t1 - a1_hat - a2_hat y_t2 - a3_hat y_t3 for a unit root
  with an ADF regression.
  - Critical values come from MacKinnon's response surface (eq. 8): C(p, T) = b_inf + b1/T + b2/T^2 + b3/T^3.
    For N = 3, constant, no trend ("tau_c"), 5%: b_inf = -3.74066, b1 = -8.5631, b2 = -10.852, b3 = 27.982
    (Table 2).
  - Worked:
    - T = 290 (one day session of 1-minute bars):
      - 8.5631/290 = 0.029528.
      - 10.852/290^2 = 10.852/84,100 = 0.000129.
      - 27.982/290^3 = 1.15e-6.
      - C = -3.74066 - 0.029528 - 0.000129 + 0.000001 = -3.77032.
    - T = 5,800 (20 sessions): C = -3.74066 - 0.001476 - 0.0000003 = -3.74214.
    - Check: both lie just beyond the asymptotic value, as the negative b1 implies.
- Johansen VECM (statsmodels VECM docs; Boero lecture notes):
  dP_t = alpha (beta' P_{t-1} + eta' D_{t-1}) + Gamma_1 dP_{t-1} + ... + Gamma_{k-1} dP_{t-k+1} + u_t, with
  Pi = alpha beta'.
  - P_t = (ZS, ZL, ZM)'. beta is 3 x r, alpha is 3 x r, and r = 1 is expected.
  - Trace statistic: lambda_trace(r) = -T sum_{i=r+1..n} ln(1 - lambda_hat_i).
  - Max eigenvalue statistic: lambda_max(r) = -T ln(1 - lambda_hat_{r+1}).
  - Zhou et al. (eq. 17) write the same VECM as dP_t = c0 + Pi P_{t-1} + sum Gamma_j dP_{t-j} + e_t,
    Pi = kappa beta'. They cast it in state space (eq. 19-20: x_t = F x_{t-1} + G e_t, y_t = H_t x_t + w_t), with
    idle prices treated as missing data, and estimate by EM with the Kalman filter and smoother, per day.
- OU on the residual (E.28 2.1 section 5, not repeated):
  - z_t = mu + phi (z_{t-1} - mu) + e_t, with phi = exp(-kappa h).
  - In a VECM with r = 1 and no short-run terms, the residual obeys z_t = (1 + beta' alpha) z_{t-1} + beta' u_t,
    so phi = 1 + beta' alpha [derived: premultiply the VECM by beta'].
- Causal rolling beta (planner's "5-20 sessions"):
  - On each session d, beta_d is the Engle-Granger or Johansen estimate over sessions d-K..d-1 only.
  - It is then frozen through session d: z_t = ZS_t - beta_d' (ZL_t, ZM_t) - m_t, where m_t is a past-only mean
    (for example an EWMA with a frozen span).
  - The Kalman alternative is E.28 2.5 section 1.4 (Palomar's dynamic hedge ratio): use the filtered state
    (mu_{t|t-1}, gamma_{t|t-1}) only, never the smoother.

**3. Worked example (illustrative prices, NOT data; M2_examples.json, c_units).**
- Prices: ZS = 1,400 c/bu, ZL = 60.00 c/lb, ZM = 420.0 USD/ton.
  - C = 11 x 60 + 2.2 x 420 - 1,400 = 660 + 924 - 1,400 = 184 c/bu = 1.84 USD/bu.
- A 1-tick rise in ZM (420.0 to 420.1): C rises by 2.2 x 0.1 = 0.22 c/bu.
- A 1 c/bu dislocation closed by ZM alone takes 1/0.22 = 4.545 ZM ticks.
  - Check: 4.545 ticks x 10 USD = 45.45 USD per ZM contract.
  - Per bushel of an 11-contract meal leg, 1,100 tons x 0.4545 USD/ton = 500 USD = 50,000 bu x 1 c. Consistent.
- Under Zhou's median vector (ZM coefficient -0.19 instead of -0.22), one ZM tick moves the residual by 0.19 c,
  so closing a 1-cent residual by ZM alone takes 1/0.19 = 5.263 ZM ticks (M2_examples2.json, e_median).
  - Equivalently, a ZM-only shock of 4.545 ticks (1 cent on the physical crush) is only 0.19 x 4.545 = 0.864 cents
    on the median-vector residual.

**4. Data.**
- 1-minute (and 5-minute) mids or last-trade prices for ZS, ZL (MBP-1) and ZM (MBO rebuilt to the BBO), on one
  clock. Previous-tick bars suffice at 1 minute or longer (see (a): 9% correlation loss at 1 minute under the
  assumptions).
[MathReview A-3 (lead: accepted): build the residual and HL from BBO mids only, never last trades (bid-ask bounce biases (d)'s HL down and its kill rule toward survival; a stale leg makes a dislocation that is not tradable), and add the trap with tests: (i) HL from mids and from last trades must agree within the grid-bootstrap CI; (ii) an entry requires every leg's BBO to have updated inside a frozen staleness window, and the protocol reports the share of candidate dislocations that collapse on the next update of the stalest leg; (iii) the 1-minute versus HY/5-minute choice for the hedge-ratio input is re-derived from DataFacts' measured gaps per stratum before K and the bar length are frozen. The 9% loss holds only for 3 s / 6 s gaps (attenuation ≈ 1 - E|U1 - U2|/Δ gives 0.917 at 1 min and 0.983 at 5 min there; 10/20 s give 0.72 at 1 min, 20/40 s give 0.44 at 1 min and 0.89 at 5 min, 30/60 s give 0.17), and A0 Table 1 puts ZM's overnight volume at a median of 2 contracts per minute (mean 8.5) against 71 (109.2) in the main session, so the day-session assumption does not carry to the overnight stratum; this also applies to (d) data (original line 503) and (f) data (original lines 744-747).]
- Contract months must match; ZS and ZL are owned only as the front contract.
  - Assumed months: ZS F, H, K, N, Q, U, X; ZM and ZL F, H, K, N, Q, U, V, Z.
  - [unverified: contract months from contract knowledge, not a fetched spec; DataFacts must confirm from the
    definitions files.]
  - If those months hold, v_0 crush legs are mismatched whenever ZS's front is X while ZM/ZL's is V or Z, and
    around differing roll dates.
  - The protocol must fix a month map (for example ZS X with ZM/ZL Z) or exclude mismatched windows. ZM v.1 gives
    the deferred meal leg; ZS and ZL deferred legs are not owned.

**5. Leakage and look-ahead traps.**
- (i) Same-day beta.
  - A Johansen or Zhou-style beta estimated on day d's own minutes, then used to trade on day d, is look-ahead.
    Zhou's per-day EM plus smoother is fine for description and wrong for a signal.
  - Test: future-scramble invariance. Replace all data after t with noise; every feature at or before t must be
    bit-identical.
- (ii) Smoother instead of filter in any Kalman beta.
  - Same test. Also compare the filtered beta at t with the beta from a run truncated at t: they must be equal.
- (iii) Full-sample mean or SD in the z-score.
  - Test: the z-score at t from a run on data up to t equals the production value.
- (iv) Roll mismatch.
  - Test: list every minute where any leg's instrument_id changes, and show the residual jump there. The protocol
    excludes a frozen window around each change.
- (v) Bar timing.
  - The 1-minute bar labelled 10:00 must hold prices up to 10:00:00 only, with entries at or after 10:00:00 +
    latency.
  - Test: shift labels by +1 bar and confirm the in-sample "edge" does not jump.

**6. Compute.**
- 3 roots x about 1,055 minutes per full CBOT grain day (19:00-07:45 plus 08:30-13:20, from the brief's session
  times: 765 + 290 = 1,055) x about 815 sessions = 2.6 million rows. That is about 60 MB as float64.
- Rolling Engle-Granger or Johansen per session: milliseconds each.
- A Zhou-style EM state space per day: seconds each, so under an hour for 815 days on one core. RAM under 1 GB.

**7. Verdict: USE.**
- This is the structural core of family 1.
- Freeze in advance:
  - fixed physical weights and one causal rolling beta (K frozen; 5-20 sessions);
  - the month map;
  - the mean and scale estimators;
  - that the Kalman beta runs as a filter only.

**8. Evidence.**

| Claim | Source (type) | Verbatim quote | File |
|---|---|---|---|
| Yields 11 lb oil, 48 lb meal; 10:12:9 | Rechner and Poitras 1993 (academic; author copy) | "a (60 lbs.) bushel of soybeans yields 11 lbs. of oil and 48 lbs. of meal [USDA (1988)]"; "this translates into 10 soybeans, 12 meal, and 9 oil contracts" | rechner_poitras_1993_soy.pdf(.txt) |
| 500 USD per cent/bu | same | "a 1-cent per bushel change in the GPM represents a $500.00 change in the value of the position" | same |
| CME guide uses 10:11:9 (secondary) | Poitras teaching note (academic, SFU) | "The CME Soybean Crush Guide (p.7) ... uses 10 Soybean, 11 Soy Meal and 9 Soy Oil" | poitras_soycrush_wpd.pdf(.txt) |
| Physical vector and median | Zhou et al. NCCC-134 2022, Table 6 (academic) | "Median 1 -0.11 -0.19 ... CME (physical) 1 -0.11 -0.22" | zhou_etal_nccc134_2022.pdf(.txt) |
| Zhou VECM and state space | same, section 3.1 eq. (17)-(20) | "the low-rank matrix Pi = kappa beta' can be decomposed into two rank h-matrices"; "Our model can be cast in a state-space formulation of the VECM model, whereby the idle prices are considered as missing data" | same |
| Kalman smoother used | same | "we can apply the conventional Kalman filter and Kalman smoother" | same |
| EG cointegrating regression | MacKinnon 2010, QED WP 1227 (academic) | "one first has to run the cointegrating regression y_t1 = a1 + sum a_j y_tj + u_t ... and tests to see if z_hat_t is I(1)" | mackinnon_2010_critvals.pdf(.txt) |
| Response surface and N = 3 values | same, eq. (8) and Table 2 | "C_k(p) = b_inf + b1 T_k^-1 + b2 T_k^-2 + e_k"; "3 tau_c 5% 15,000 -3.74066 (0.000067) -8.5631 -10.852 27.982" | same |
| Johansen trace and max tests | Boero, Warwick lecture notes (academic teaching) | "The maximum eigenvalue statistic: H0: rank <= r, H1: rank=r+1"; "trace = -T sum ln(1 - lambda_i)" | warwick_boero_johansen_notes.pdf(.txt) |
| VECM form in software | statsmodels docs (practitioner/software) | "Pi = alpha beta'"; "A VECM(k_ar - 1) with deterministic terms has the form" | statsmodels_vector_ar.html(.txt) |
| Lagged cross-asset OFI decays fast | E.28 2.10 section 5.1 (Cont, Cucuringu and Zhang 2023) | cited from E.28, not re-fetched | reports/stage_e28_methods_brief.md |
| Mitchell 2010 crush | Mitchell 2010, JRFM | [unverified: MDPI returned 403] | mitchell_2010_jrfm.pdf (403 page) |
| Ericsson-MacKinnon ECM test | Ericsson and MacKinnon 2002 | [unverified: the UiO course URL returned 404] | ericsson_mackinnon_ecm_test.pdf (404 page) |

## (d) Half-life estimation: discretisation, small-sample bias, intervals, and by-session/by-hour estimates

**1. Core idea.**
- Sampled every dt, an OU residual is an AR(1) with slope b = exp(-kappa dt), so the half-life is ln 2 / kappa.
- OLS (the conditional MLE under Gaussian errors; E.28 2.1 section 5) biases b down by about (1 + 3b)/T, which
  makes reversion look faster than it is.
- Near b = 1 the usual +-1.96 se interval fails. Hansen's grid bootstrap fixes coverage, and an interval for b
  maps one-to-one into an interval for the half-life.
- Estimating by hour shortens each segment and multiplies the bias unless the design avoids per-segment
  demeaning.

**2. Equations.**
- Discretisation (E.28 2.1 section 5, Bao et al. eq. 2.4-2.5; not repeated):
  - z_{t+dt} = a + b z_t + e, with b = exp(-kappa dt).
  - kappa = -ln(b)/dt.
  - Half-life HL = ln 2 / kappa = dt ln 2 / (-ln b).
- In the VECM of (c): b = 1 + beta' alpha, so HL_z = dt ln 2 / (-ln(1 + beta' alpha)) [derived].
- Kendall / Marriott-Pope bias, AR(1) with unknown mean (Kiviet and Phillips 2009, eq. 3.12):
  MP(T^-1) = -(1 + 3 lambda)/T, with lambda the AR coefficient and T the sample size.
  - This closes the [unverified] mark on the same formula in E.28 2.1. The equation was read from the rendered
    page image (M2_kp_p13-13.png), because pdftotext drops the minus sign and lambda.
- Kiviet and Phillips add that in the fixed start-up model "the classic (1 + 3 lambda)/T result of (3.10)
  understates the actual bias, especially when the bias is really serious".
- Kendall-inverted correction [derived: solve b_hat = b - (1 + 3b)/T for b]: b_c = (T b_hat + 1)/(T - 3).
- Interval:
  - The asymptotic se(b_hat) = sqrt((1 - b^2)/T) [standard result; unverified against a fetched text here].
  - It fails near b = 1. Hansen's grid bootstrap "is first-order correct globally in the parameter space", while
    "conventional bootstrap methods fail to provide correct first-order asymptotic coverage when an
    autoregressive root is close to unity".
  - HL is monotone in b, so CI(HL) = [HL(b_lo), HL(b_hi)], with HL = infinity when b_hi >= 1 [derived].
- MLE:
  - Conditional Gaussian MLE equals OLS (E.28 2.1).
  - Exact MLE adds the stationary density of z_0. It changes little at T >= 60 and does not remove the T^-1 bias.

**3. Worked examples** (residual sampled at dt = 1 minute; M2_examples.json, d_halflife; M2_examples2.json,
d_ci_n60 and d_ci_n290).
- True b = 0.95:
  - kappa = -ln 0.95 = 0.05129 /min.
  - HL = 0.693147/0.05129 = 13.51 min.
- Expected OLS b_hat and the half-life it implies:
  - T = 60 (one hour):
    - Bias = -(1 + 2.85)/60 = -0.06417, so b_hat = 0.88583.
    - kappa_hat = 0.12123 /min, so HL_hat = 5.72 min (58% short).
  - T = 290 (one day session):
    - Bias = -3.85/290 = -0.01328, so b_hat = 0.93672.
    - HL_hat = 10.60 min (22% short).
  - T = 5,800 (20 sessions): b_hat = 0.94934, HL_hat = 13.33 min.
  - Correction check: (290 x 0.93672 + 1)/287 = (271.649 + 1)/287 = 0.95000, and (60 x 0.88583 + 1)/57 = 0.95000.
    This exactly recovers the true b.
- Asymptotic interval at T = 290 around b_hat = 0.93672:
  - se = sqrt((1 - 0.87745)/290) = sqrt(0.0004226) = 0.02056.
  - b in [0.89643, 0.97702], so HL in [6.34, 29.81] min. This is very asymmetric.
- At T = 60: se = 0.0599, b in [0.76842, 1.00324], so HL in [2.63 min, infinity).
  - One hour cannot reject a random walk even when the true HL is 13.5 min.
- Monte Carlo of by-hour designs (400 replications; 20 segments of 60 minutes from one AR(1) with b = 0.95):
  - Pooled OLS with each hour's own mean removed: mean b_hat = 0.90628, so HL_hat = 0.693/0.0984 = 7.04 min,
    about half the truth. The Kendall formula at T = 60 predicted 0.88583, so it overstates the bias for this
    pooled estimator by 0.020.
  - Pooled OLS with one global mean (no cross-segment pairs): 0.94700.
  - One 290-minute session: 0.93599 (the formula's 0.93672 is within 0.001).
- Check: the single-session MC matches the Kendall formula to 0.001. The large bias of the hour-demeaned design
  is the result to carry into the protocol.

**4. Data.**
- The causal crush residual of (c) at 1-minute (or 5-minute) bars. ZS and ZL come from MBP-1 and ZM from MBO.
- Strata:
  - day (08:30-13:20) against overnight (19:00-07:45);
  - hour of day;
  - report days against non-report days;
  - roll windows excluded.
- Pairs (z_{t-1}, z_t) that straddle the 13:20-19:00 break, a roll, or a data gap are dropped.

**5. Leakage and look-ahead traps.**
- (i) Hour-of-day half-life estimated on all sessions, then used to set a time stop on those same sessions.
  - Estimate on training-fold sessions only, then freeze.
  - Test: the HL used on session d must equal the value from a run truncated before d.
- (ii) Per-hour demeaning uses that hour's future minutes and (above) halves the HL.
  - For estimation, use the same causal mean the signal uses (an EWMA with a frozen span), or a global mean per
    stratum from training folds.
  - Test: rerun with demeaning by a past-only mean; the HL must not change by more than its bootstrap SE.
- (iii) Selecting the stratum with the shortest HL after seeing all strata is a selection step.
  - Declare the strata and the rule before the run, and count each traded stratum into N.

**6. Compute.**
- OLS per stratum and session: microseconds.
- Hansen grid bootstrap: G = 200 grid points x B = 1,999 resamples (Hansen's own settings) x T = 290 is 1.2 x 10^8
  AR steps per interval. That is about a second vectorised.
- 24 hour-strata x 2 sessions x about 40 folds is about 2,000 intervals, so tens of minutes on 8 cores.

**7. Verdict: USE** (as a frozen design parameter and a kill diagnostic, not as a signal).
- Report b_hat, the Kendall-corrected b_c, the grid-bootstrap CI and the HL CI per stratum.
- Kill family 1 for a stratum when the HL CI upper bound exceeds the time stop the economics allow (see (f)).

**8. Evidence.**

| Claim | Source (type) | Verbatim quote | File |
|---|---|---|---|
| Kendall / Marriott-Pope T^-1 bias with intercept | Kiviet and Phillips 2009, UvA DP 09/09 (academic) | "They find MP(T^-1) = -(1 + 3 lambda)/T, (3.12)" (sign and lambda read from the page image); "Kendall (1954) and Marriott and Pope (1954) gave an approximation to the bias of the least-squares estimator of the lagged-dependent variable coefficient to the order of T^-1" | kiviet_phillips_2009_ar1bias.pdf(.txt); work/M2_lead_lag/M2_kp_p13-13.png |
| First-order formula understates serious bias | same | "the classic (1 + 3 lambda)/T result of (3.10), understates the actual bias, especially when the bias is really serious" | same |
| Grid bootstrap near a unit root | Hansen 1999, REStat (academic; author copy) | "conventional bootstrap methods fail to provide correct first-order asymptotic coverage when an autoregressive root is close to unity. In contrast, the grid bootstrap is first-order correct globally in the parameter space" | hansen_1999_gridboot.pdf(.txt) |
| Grid settings | same | "setting G = 200 and B = 1999 in most" | same |
| OU-AR(1) map, OLS = conditional MLE, bias depends on span | E.28 2.1 section 5 (Bao, Ullah and Wang 2014) | cited from E.28, not repeated | reports/stage_e28_methods_brief.md |
| Half-life CI methods | Kim, Silvapulle and Hyndman, Monash WP 11/06 | [unverified: Monash returned 403] | kim_silvapulle_hyndman_halflife.pdf (403 page) |
| AR bias (Cardiff ORCA 0631) | candidate paper | [unverified: Cardiff ORCA returned 403] | cardiff_0631.pdf (403 page) |

## (e) Which leg adjusts: alpha loadings, Gonzalo-Granger weights, Hasbrouck bounds, Putnins ILS

**1. Core idea.**
- When the crush is dislocated, some legs move to close it. The VECM's adjustment vector alpha says which, and how
  fast. For a ZM-only trade, the number that matters is ZM's share of the closure.
- The price-discovery shares (IS, CS, ILS) answer a different question: who impounds news about ONE common
  efficient price first. They assume a single common trend. The crush has three different commodities and one
  cointegrating relation, so two common trends.
- So the shares apply cleanly only to a bivariate re-formulation: ZM's value in the crush against the
  "implied meal" value from ZS and ZL.

**2. Equations.**
- VECM with r = 1 (from (c)): dP_t = alpha z_{t-1} + sum_j Gamma_j dP_{t-j} + u_t, with z = beta' P.
  - P = (ZS[c], nL, nM)'. beta = (1, -0.11, -b_M)'. alpha = (alpha_S, alpha_L, alpha_M)'.
- Adjustment-contribution share of leg i [derived]: s_i = beta_i alpha_i / (beta' alpha), and sum_i s_i = 1.
  - With Gamma = 0, z decays as z_t = (1 + beta' alpha)^t z_0.
  - Leg i's cumulative move is alpha_i sum_t z_t = alpha_i z_0 / (-beta' alpha).
  - Leg i's cumulative contribution to closing z is beta_i alpha_i z_0 / (-beta' alpha) = -s_i z_0.
  - ZM's cumulative move, in ZM ticks, per 1 c/bu of z is alpha_M / (-beta' alpha) = s_M / b_M.
  - With Gamma != 0 the same shares come from the long-run impulse response [derived; not checked against a
    fetched text].
[MathReview A-4 (lead: accepted): with short-run terms the shares are not "the same": s_i = beta_i [(I - Gamma)^{-1} alpha]_i / (beta' (I - Gamma)^{-1} alpha), i.e. the stated formula with alpha replaced by alpha~ = (I - ΣGamma_j)^{-1} alpha (from (I - Gamma) ΣdP = alpha Σz and Σz = -z_0 / (beta' (I - Gamma)^{-1} alpha)), which reduces to it when Gamma = 0. The operational definition to freeze is s_M = ZM's share of the cumulative closure in the fitted model's deterministic impulse response from z_0 = 1 c with all lagged differences zero (what (e)(3)'s 5,000-step iteration already does); this also applies at original lines 650-655, 689 and 771-772.]
- Weak exogeneity (Boero notes): if a leg's alpha entries are zero, "the cointegrating vectors ... do not enter
  the equation" for that leg, so it does not adjust.
  - Test H0: alpha_M = 0 (ZM does not adjust), and H0: alpha_S = alpha_L = 0 (ZM does all the adjusting).
  - The likelihood-ratio form of these tests is standard Johansen [unverified: the test statistic is not in the
    fetched notes; only the restriction is].
- Gonzalo-Granger permanent-transitory decomposition (Yan and Zivot eq. 8):
  - p_t = A1 f_t + A2 z_t, with f_t = gamma' p_t, A1 = beta_perp (alpha_perp' beta_perp)^{-1},
    gamma = (alpha_perp' beta_perp)^{-1} alpha_perp', and alpha_perp' alpha = 0.
  - In the bivariate case with beta = (1, -1)', the component share is CS_1 = alpha_2/(alpha_2 - alpha_1) and
    CS_2 = alpha_1/(alpha_1 - alpha_2) (Putnins 2013 eq. 4; read from the rendered page image).
  - With three crush legs and r = 1, alpha_perp is 3 x 2, so there is no single CS vector [derived].
- Hasbrouck information share (Yan and Zivot eq. 7): IS_i = ([psi' F]_i)^2 / (psi' Sigma psi).
  - F is the lower Cholesky factor of Sigma (the VECM residual covariance), and psi is the common-trend loading.
  - Bivariate closed form (Putnins eq. 5-7): Sigma = [[s1^2, rho s1 s2], [rho s1 s2, s2^2]], M = [[s1, 0],
    [rho s2, s2 (1 - rho^2)^{1/2}]], and IS_1 = (g1 m11 + g2 m12)^2 / ((g1 m11 + g2 m12)^2 + (g2 m22)^2), with
    (g1, g2) = alpha_perp.
  - Bounds: "the upper (lower) bound of the IS_i is obtained by computing the Cholesky factorization with the ith
    price ordered first (last)". With n prices, all permutations must be examined (Yan and Zivot, citing
    Hasbrouck 2002).
  - Common practice averages the two orderings (Putnins; Hu et al.).
  - From eq. 6-7, the bounds coincide when rho = 0 [derived].
  - Coarse sampling raises rho: one-minute sampling "produced a substantial contemporaneous residual correlation
    and wide upper and lower bounds for the IS" (Yan and Zivot on Huang 2002).
- Putnins (2013) information leadership share, bivariate only:
  - IL_1 = |IS_1 CS_2 / (IS_2 CS_1)| and IL_2 = |IS_2 CS_1 / (IS_1 CS_2)| (eq. 8, after Yan and Zivot).
  - ILS_1 = IL_1/(IL_1 + IL_2) (eq. 9).
  - ILS_1 > 0.5 means price 1 leads.
  - Why it matters: IS and CS mix speed with "relative avoidance of noise". ZM is the least liquid leg (the
    planner's de Boer et al. figure, which R3a owns), so IS and CS would tend to credit ZS and ZL with leadership
    partly for being less noisy.
- Bivariate device for the crush [derived]:
  - p1 = b_M nM, the meal leg's crush value in c/bu.
  - p2 = ZS[c] - 0.11 nL, the implied meal value in c/bu.
  - Then z = p2 - p1, beta = (-1, 1)', and there is one common trend.
  - IS, CS and ILS of p1 then measure whether ZM moves first or follows. s_M = (-1) alpha_1 / (beta' alpha) is
    the bivariate version of ZM's adjustment share.

**3. Worked example: hypothetical alpha, NOT estimates.**
- Zhou et al. publish no alpha levels, half-lives or shares (planner; R3a to confirm). The alpha below is
  hypothetical, chosen only to show the arithmetic.
- Inputs: alpha = (-0.02, +0.05, +0.06) per minute on (ZS cents, ZL ticks, ZM ticks).
- (i) Physical beta = (1, -0.11, -0.22) (M2_examples.json, e_vecm; M2_examples2.json, e_physical):
  - beta' alpha = 1(-0.02) + (-0.11)(0.05) + (-0.22)(0.06) = -0.02 - 0.0055 - 0.0132 = -0.0387 /min.
  - So b = 0.9613, and HL_z = 0.6931 / (-ln 0.9613) = 0.6931/0.03947 = 17.56 min.
  - Shares:
    - s_S = -0.02/-0.0387 = 0.5168.
    - s_L = -0.0055/-0.0387 = 0.1421.
    - s_M = -0.0132/-0.0387 = 0.3411.
    - Sum = 1.0000.
  - ZM's move per 1 c/bu of z: 0.06/0.0387 = 1.550 ticks = s_M / 0.22 = 0.3411 x 4.545.
  - Check: iterating the deterministic error correction 5,000 times from z_0 = 1 c (a ZS shock) gives moves of
    ZS -0.5168 c, ZL +1.292 ticks and ZM +1.550 ticks, with final z = 1e-15.
- (ii) Zhou median beta = (1, -0.11, -0.19) with the same alpha (M2_examples2.json, e_median):
  - beta' alpha = -0.02 - 0.0055 - 0.0114 = -0.0369.
  - HL_z = 18.44 min.
  - Shares: 0.5420, 0.1491, 0.3089.
  - ZM's move per 1 c of z: 0.06/0.0369 = 1.626 ticks = 0.3089 x 5.263.
  - Iteration check: ZM +1.626 ticks.
- Reading: the same alpha gives ZM 31-34% of the closure. That is about 1.55-1.63 ZM ticks per cent of
  dislocation, against 4.55-5.26 ticks if ZM did it all.

**4. Data.**
- 1-minute (VECM, alpha, s_M) and 1-5 second (IS, CS, ILS on the bivariate device) samplings of the causal
  residual's legs. Each sampling is frozen in advance.
- Coarse sampling widens the IS bounds (Yan and Zivot); fine sampling brings in the Epps and lead-lag issues of
  (a) and (b).
- Estimate per session with beta frozen from prior sessions, then pool alpha by stratum.

**5. Leakage and look-ahead traps.**
- (i) alpha and the shares estimated on a session's own data, then used to gate trades in that session.
  - Gating must use prior-session estimates.
  - Test: future-scramble invariance on the gate.
- (ii) Choosing the IS ordering, the sampling interval, or the bivariate against trivariate form after seeing
  results is a selection step.
  - Freeze each before the run, and report both IS bounds rather than the favourable one.
- (iii) Estimating beta and alpha jointly on the same window understates the residual's variance and overstates
  the reversion (an in-sample fit).
  - Test: compare in-window and next-window s_M. A drop beyond the bootstrap SE flags overfit.

**6. Compute.**
- A trivariate VECM with k <= 20 lags on 290-1,055 rows per session: milliseconds. All sessions take seconds.
- Bivariate IS/CS/ILS at 1 s: 17,400 day-session rows per session, with a VECM of 20 lags (Putnins used 20).
  That is about 0.1 s each, so about 2 minutes for 815 sessions. Bootstraps multiply that by B.

**7. Verdict.**
- USE: alpha loadings, weak-exogeneity tests and s_M, as the early kill test for family 1.
- MAYBE: ILS on the bivariate device (meal leg against implied meal) as a description of who moves first.
- SKIP: the trivariate IS/CS as published, because the single-common-trend assumption fails.
- Suggested early test (protocol content is the lead's decision): on the earliest discovery folds only, estimate
  s_M with a session-block bootstrap CI. Family 1 dies if the CI's upper end is below the break-even share s_M*
  from (f) at the frozen entry D and time stop m.

**8. Evidence.**

| Claim | Source (type) | Verbatim quote | File |
|---|---|---|---|
| Weak exogeneity: zero alpha means the leg does not adjust | Boero, Warwick notes (academic teaching) | "The adjustment coefficients s can be tested to see whether they are zero. If they are zero then that particular error correction term does not enter that equation" | warwick_boero_johansen_notes.pdf(.txt) |
| GG PT decomposition | Yan and Zivot (JFM 2010 working version; academic) | "pt = A1 ft + A2 zt (8) where ft is the permanent component, zt is the transitory component"; "Granger and Gonzalo define ft = gamma' pt and A1 = beta_perp (alpha_perp' beta_perp)^-1" | yan_zivot_structural_pd.pdf(.txt) |
| IS formula and ordering bounds | same, eq. (7) | "The resulting IS depends on the ordering of price variables. In the bivariate case, the upper (lower) bound of the ISi is obtained by computing the Cholesky factorization with the ith price ordered first (last). With n prices, Hasbrouck (2002) shows that one must examine all permutations" | same |
| One-minute sampling widens bounds | same | "used a one minute sampling interval which produced a substantial contemporaneous residual correlation and wide upper and lower bounds for the IS" | same |
| CS, IS, IL and ILS formulas | Putnins 2013, JEF (academic; UTS author copy) | eq. (4)-(9) as above; "ILS1 and ILS2 have the range [0,1] ... with values above (below) 0.5 indicating the price series leads (does not lead)" | putnins_2013_metrics.pdf(.txt); page 14 rendered to work/M2_lead_lag/M2_putnins_p-14.png |
| IS and CS mix speed and noise | same | "If the noise in the price series differs, the information and component shares measure a combination of leadership in impounding new information and relative avoidance of noise" | same |
| ILS is bivariate only | same | "This metric, which is only applicable in bivariate systems, uses IS and CS together" | same |
| Average over orderings | Hu, Mallory, Serra and Garcia (academic; arXiv 1711.03506) | "we calculate the IS measures using each of the two alternative orderings of price series and then take the average" | arxiv1711_03506_price_discovery_commodity.pdf(.txt) |
| IS overstates the less noisy contract | same | "using IS and CS may lead to overstating the price discovery contribution of the less noisy contract" | same |
| Hasbrouck 1995 original | Hasbrouck 1995, JF | [unverified: not fetched; cited via Yan and Zivot, Putnins and Hu et al.] | - |

## (f) How to trade a crush dislocation in ZM only

**1. Core idea.**
- Enter ZM in the direction that closes the causal crush residual when it is far from its causal mean, and exit
  at a time stop measured in half-lives.
- The expected gross gain in ZM ticks is not "the dislocation divided by 0.22". It is that times ZM's share of
  the adjustment, times the fraction of reversion completed by the time stop.
- The trade pays only if that product clears the 1.59-tick market-order hurdle with room for noise.

**2. Equations** [derived from (c)-(e); OU expected path E[z_{t+tau} - mu | z_t] = (z_t - mu) e^{-kappa tau}].
- Signal: x_t = (z_t - m_t)/sigma_t, with m_t and sigma_t past-only (frozen spans).
  - z = ZS[c] - 0.11 nL - b_M nM.
  - x_t > 0 means meal is cheap relative to beans and oil (crush narrow). The ZM order is a buy when
    alpha_M > 0, which is the sign required for ZM to be an adjusting leg.
- Entry when |x_t| >= k, with k frozen. Dislocation D = |z_t - m_t| in c/bu.
- Time stop tau = m x HL (m frozen), so the expected fraction of reversion completed is 1 - e^{-kappa tau} =
  1 - 2^{-m}.
- Expected gross ZM gain: G = s_M x D x (1 - 2^{-m}) / b_M ticks.
  - s_M: ZM's adjustment share from (e).
  - b_M: the ZM weight (0.22 physical, 0.19 Zhou median).
- Net per round trip: N = G - 1.59 ticks.
  - 1.59 is Topstep's ZM market-order break-even mu*_mkt (stage_e28_ranking.md line 130). It includes the 5.28 USD
    fee, which is 0.528 ticks.
  - Passive entry is not assumed to help: E.31's resting 1-lot at the ZM touch lost 0.970 ticks gross at 10 s
    per fill.
- Break-even share: s_M* = 1.59 b_M / (D (1 - 2^{-m})).
- Noise over the hold, under random-walk scaling (an upper bound, since conditioning on cointegration lowers it):
  SD_tau = 3.15 sqrt(tau minutes) ticks.
  - Per-trade Sharpe = N / SD_tau.
  - Trades needed for t = 3 is about (3 / Sharpe)^2.

**3. Worked example.**
- (i) Planner's arithmetic, verified: one ZM tick moves the crush by 2.2 x 0.10 = 0.22 c/bu, so a 1 c/bu crush
  dislocation is 1/0.22 = 4.545 ZM ticks if ZM alone adjusts (s_M = 1). This is "about 4.5": VERIFIED.
- (ii) Redo under the planner's median cointegrating vector (ZM -0.19):
  - If ZM alone closes a 1 c residual, it moves 1/0.19 = 5.263 ticks.
  - With the hypothetical alpha of (e), ZM's share is s_M = 0.3089, so the full eventual ZM move is
    0.3089 x 5.263 = 1.626 ticks per cent (M2_examples2.json, e_median). Under physical weights the same alpha
    gives 0.3411 x 4.545 = 1.550.
  - Gross G by time stop (median vector, s_M = 0.3089, D = 1 c):
    - m = 1: 1.626 x 0.5 = 0.813 ticks.
    - m = 2: 1.626 x 0.75 = 1.220 ticks.
    - m = 3: 1.626 x 0.875 = 1.423 ticks.
    - All are below 1.59.
  - D needed to break even: 1.59/0.813 = 1.96 c (m = 1); 1.304 c (m = 2); 1.118 c (m = 3). Under physical
    weights: 2.05, 1.37 and 1.17 c.
  - Check: at m = 2, D = 1.304 c gives G = 0.3089 x 1.304 x 0.75 / 0.19 = 1.590 ticks.
- (iii) Break-even share s_M* (rows D in c/bu; columns m = 1, 2, 3 half-lives; values above 1 are impossible).
  Gross at s_M = 1 is in brackets.

| b_M | D = 0.5 | D = 1 | D = 2 | D = 3 |
|---|---|---|---|---|
| 0.22 | 1.40 / 0.93 / 0.80 [1.14 / 1.70 / 1.99] | 0.70 / 0.47 / 0.40 [2.27 / 3.41 / 3.98] | 0.35 / 0.23 / 0.20 [4.55 / 6.82 / 7.95] | 0.23 / 0.16 / 0.13 [6.82 / 10.23 / 11.93] |
| 0.19 | 1.21 / 0.81 / 0.69 [1.32 / 1.97 / 2.30] | 0.60 / 0.40 / 0.35 [2.63 / 3.95 / 4.61] | 0.30 / 0.20 / 0.17 [5.26 / 7.89 / 9.21] | 0.20 / 0.13 / 0.12 [7.89 / 11.84 / 13.82] |

  - Check of one cell: b_M = 0.22, D = 1, m = 1: 1.59 x 0.22 / (1 x 0.5) = 0.6996. This matches
    M2_examples.json, f_trade.breakeven_sM "bM0.22_D1.0_m1": 0.6996.
- (iv) Noise and sample size. With the hypothetical HL_z of 17.6-18.4 min and m = 2, the hold is about 36 min:
  - SD = 3.15 x sqrt(36) = 18.9 ticks.
  - A 1.0-tick NET edge gives Sharpe 1.0/18.9 = 0.0529 per trade, so (3/0.0529)^2 = 3,215 trades for t = 3.
  - At a 15-minute hold, SD = 12.2 ticks and 1,340 trades are needed.
  - Over about 815 discovery sessions, that is about 1.6-3.9 qualifying trades a session, every session, at a
    1-tick net edge. A 0.5-tick net edge needs 4 times as many.
  - These counts ignore N-deflation (DSR), which raises them.
- Reading:
  - At realistic D around 1 cent, ZM must do 40-70% of the adjusting (m = 1-3), against a share that published
    work does not report.
  - At D of 2-3 cents, 13-35% suffices, but such dislocations are rarer and their frequency is unknown until
    E.33 measures it (no data is read here).
  - The binding unknowns are the frequency of D >= 2 c events, s_M by stratum, and HL by stratum. Each is
    measurable on discovery data under a frozen protocol.

**4. Data.**
- Causal residual and its legs at 1 minute (from (c)).
- ZM BBO (from MBO) at the decision time plus latency, for the entry price: the ask for a buy and the bid for a
  sell, not the bar mid. The same at exit.
- Strata: day/overnight, hour, report days, and roll windows excluded.

**5. Leakage and look-ahead traps.**
- (i) Threshold k, time stop m and window K chosen after seeing P&L.
  - Freeze them, or count every combination into N (V43).
- (ii) sigma_t or m_t from full-sample or full-day statistics.
  - Test: truncate-at-t recomputation equality.
- (iii) Overlapping labels (holds of 15-40 minutes) across CV folds.
  - Purge and embargo at least one maximum hold (m x HL_max) between folds.
  - Test: the embargo length is at least the maximum realised hold in the fold.
- (iv) Fill at the bar's close mid instead of the next tradable price after latency.
  - Test: the fill price must be a quote with a timestamp >= decision time + latency.
- (v) s_M or HL used for sizing or gating, estimated in-sample.
  - Prior-fold estimates only. Same scramble test.
- (vi) A dislocation that is a roll artefact (contract-month mismatch, see (c)).
  - Test: no entries within the frozen roll exclusion window, checked by instrument_id changes.

**6. Compute.**
- Event detection and P&L on 1-minute bars of about 2.6 million rows: seconds.
- A grid of (k, m, K) of size 3 x 3 x 3 = 27 per CV fold of about 40 folds: minutes.
- RAM under 1 GB.

**7. Verdict: USE as the family-1 trade template.**
- The kill rules come from (d) and (e): the HL CI must fit the time stop, and s_M's CI must reach s_M* at the
  frozen D and m.
- The economics are tight: at D around 1 c it needs s_M >= 0.40-0.70, so the family may well die early. That is
  the intended outcome of an early test, not a reason to skip it.

**8. Evidence.**

| Claim | Source (type) | Verbatim quote | File |
|---|---|---|---|
| ZM market-order break-even 1.59 ticks at Topstep | E.28 ranking (program artefact) | row "6 \| topstep \| ZM \| ... \| 0.59 \| 1.59 \| ..." under header "mu*_lim \| mu*_mkt" | reports/stage_e28_ranking.md lines 123, 130 |
| Passive touch fills lose 0.970 ticks at 10 s | E.31 return (program artefact) | "gross -0.970 [-0.988, -0.950]" | reports/E.31_RETURN.md line 21 |
| 1 cent = 500 USD on a 50,000-bu crush | Rechner and Poitras 1993 | see (c) | rechner_poitras_1993_soy.pdf(.txt) |
| Median ZM weight -0.19 | Zhou et al. Table 6 | see (c) | zhou_etal_nccc134_2022.pdf(.txt) |

## Planner pointers owned by M2

| Pointer (planner_research_soy_complex.md) | Status | Evidence / what differs |
|---|---|---|
| "One ZM tick moves the crush by 0.22 cents/bu, so a 1 cent/bu crush dislocation is about 4.5 ZM ticks if ZM alone adjusts" (line 20-22) | VERIFIED (arithmetic) | 2.2 c/bu per USD/ton x 0.10 USD/ton = 0.22 c; 1/0.22 = 4.545. Under the Zhou median vector, 1/0.19 = 5.263 per cent of median-vector residual. With a realistic ZM share s_M the move is s_M x 4.545, for example 1.55 ticks at s_M = 0.34 (hypothetical). See (f). |
| "The ratio is 10 ZS : 11 ZM : 9 ZL; Rechner and Poitras used 10:12:9" (lines 17-19) | VERIFIED; refinement added | Rechner and Poitras: "10 soybeans, 12 meal, and 9 oil contracts" from 48 lb of meal. 10:11:9 per Poitras's note on the CME guide (secondary; CME not fetched). 9 ZL gives 10.8 lb/bu, not 11, so the 10:11:9 oil leg is 1.8% short. |
| Zhou, Bagnarosa, Gohin, Pennings and Debie VECM specification (model section only) | VERIFIED | Eq. (17) VECM with Pi = kappa beta'; eq. (19)-(20) state space with H_t handling idle prices as missing data; EM with "the conventional Kalman filter and Kalman smoother", estimated per day. Units of the prices are not stated in the fetched text; (1, -0.11, -0.22) fits ZS in cents and ZL/ZM in ticks [derived]. The smoother is same-day look-ahead if reused for trading (see (c), trap (i)). Empirical numbers belong to R3a_crush. |
| "A crush residual from both the 10:11:9 weights and a causal rolling beta over 5-20 sessions. Estimate the half-life by session and hour, and test early which leg adjusts: if ZM is not the adjusting leg, family 1 dies" (lines 112-115) | PARTLY VERIFIED (method sound; three amendments) | (1) "Adjusting leg" must be quantitative: the break-even share s_M* = 1.59 b_M / (D (1 - 2^-m)) is 0.70 at D = 1 c, m = 1 and 0.35 at D = 2 c. ZM can adjust and the family still die. (2) By-hour half-lives with per-hour demeaning halve the HL (MC: b_hat 0.906 vs true 0.95, HL 7.0 vs 13.5 min). Use the causal mean, Kendall correction and grid-bootstrap CIs. (3) Use alpha, s_M and weak exogeneity, not trivariate IS/CS, which assume one common trend. Also: fix the contract-month map for rolls. |
| "No intraday half-life is published" (line 56) | UNVERIFIED (a negative claim) | I found none in the sources read for this topic (HRY, Huth and Abergel, Zhou model section, Rechner and Poitras, Hu et al., Putnins). Zhou reports no half-life in the sections read. R3a_crush owns the empirical literature search. |
| "ZS/ZL to ZM lead-lag in seconds: a feature only (under 1 tick, and HFT takes it)" (lines 99-100) | PARTLY VERIFIED | Supported by derivation and analogues, not by a ZM-specific source. Pure-shift model: the predictable ZM move left after 0.3 s latency has SD 0.20 ticks (rho 0.6, theta 1 s) to 0.53 ticks (rho 1, theta 2 s), under 1 tick. Huth and Abergel: a market-order strategy "cannot make any profit of this effect because of the bid/ask spread". Shiotani et al.: CME lags of about 5 ms. "HFT takes it" is not directly evidenced for ZM; E.31's adverse-selection asymmetry (context only) is consistent with it. |

## Search log summary, stopping rule and failures

- Sources read in full text, about 13: HY 2008, HRY 2013, Huth and Abergel 2014, Toth and Kertesz (2 papers),
  Shiotani, Hayashi and Koike 2026, Zhou et al. (model section and Table 6), Rechner and Poitras 1993, Poitras
  note, Putnins 2013, Yan and Zivot, Hu et al., Kiviet and Phillips 2009, Hansen 1999, MacKinnon 2010, Boero
  notes, statsmodels docs.
- Stopping rule: every topic (a)-(f) has at least 3 full-text sources, or all that exist for a narrow item.
  This re-spawned instance ran no new discovery queries. Its decision rests on the first instance's log and the
  coverage above: no topic was left with fewer than 3 sources except "intraday crush half-life", for which none
  exists in what was read.
- WebSearch: this instance made 0 calls. The first instance's count is not recorded in log.tsv. All fetches were
  curl.
- Failed fetches (not evidence; logged in log.tsv):
  - HY 2005: Project Euclid bot page.
  - Mitchell 2010: MDPI 403.
  - Putnins: first UTS host 404, retry OK.
  - Cardiff ORCA 0631: 403.
  - Kim, Silvapulle and Hyndman: Monash 403.
  - MacKinnon on the Queen's host: no response, AgEcon copy OK.
  - Ericsson and MacKinnon: UiO 404.
  - NYU cointegrated VAR slides: 403.
  - Dobrev and Schaumburg: Atlanta Fed 404 page.
  - No Scrapling or Firecrawl fallback was tried for these. Each gap was covered by another source and is marked
    [unverified] where cited.
- No market data, CME site, Databento, broker or key was touched.

