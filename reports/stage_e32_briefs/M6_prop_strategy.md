# M6_prop_strategy: from a directional prediction to a prop-firm strategy for ZM (Stage E.32, Part M6)

Worker PropStrategyMath-OpusHigh (Opus 5.5, high), 2026-10-27 00:29-PDT start. Brief: reports/stage_e32_briefs/READER_BRIEF.md
(binding) and reports/stage_e28_briefs/READER_RULES.md. Nothing here is trained, registered or read from market data:
every number is either quoted from an earlier return (E.28, E.29, E.31) or produced by arithmetic and self-written
model scripts on the brief's standard ZM numbers. N stays 538.

Files written by this worker:
- this file;
- reports/stage_e32_briefs/pages/M6_prop_strategy/ (log.tsv, 3 academic PDFs and their text);
- reports/stage_e32_briefs/work/M6_prop_strategy/: M6_limit.py (+ M6_limit_out.json, M6_limit_stdout.txt), the
  Brownian model of limit and market entries; M6_funnel.py (+ M6_funnel_out.json, M6_funnel_stdout.txt), a simplified,
  self-written 50K funnel for topic (c); M6_tables.py (+ M6_tables_out.json), the cost and threshold tables;
  M6_arxq.sh (arXiv discovery helper); M6_variants.py (+ M6_variants_out.json, M6_variants_stdout.txt), the
  per-firm, per-variant model of section 5, with its formatting helper M6_sec5_rows.py (-> M6_sec5_rows.txt) and the
  drafted section text M6_sec5.md. The program's E.19/E.28 simulator (prop_econ/) was read for docstrings and
  signatures only and was not run or imported.

## 0. Conventions and the standard numbers used

- Units: ticks of ZM (0.10 USD per short ton, 10.00 USD per contract), signed in the signal's direction (a long signal
  gains when the price rises). "Round trip" (RT) = entry fill + exit fill. Fees F are per RT.
- sigma_1m = 3.15 ticks (E.28 A0 Table 1, quoted in READER_BRIEF). Random-walk scaling is an ASSUMPTION used
  throughout: sigma_h = sigma_1m sqrt(h). My arithmetic: sqrt(5) = 2.2361, so sigma_5 = 3.15 x 2.2361 = 7.044 ticks;
  sqrt(15) = 3.8730, sigma_15 = 12.200 ticks; sqrt(60) = 7.7460, sigma_60 = 24.400 ticks. (Check: 12.200^2 / 15 =
  9.923 = 3.15^2.)
- Spread: 1 tick (the touch is one tick wide most of the time is the convention E.28 used, "S_rt = 1 tick for every
  pair", A3_econ 2.4; not re-measured here). Half spread = 0.5 tick per market fill.
- Fees per RT (USD, firm pages read 2026-10-21/22, as recorded by E.28/E.31): Topstep 5.28, Lucid 5.60 (all-in status
  unknown; E.28's u-rule reading 9.20), Tradeify 9.20, MFFU 6.12, Bulenox 5.72. In ticks (divide by 10.00): 0.528,
  0.560 (0.920), 0.920, 0.612, 0.572.
- E.28's market-order break-even for ZM at Topstep, exact row (reports/stage_e28_ranking.md line 130): "| 6 | topstep
  | ZM | 2.69 | 2 | 4 | 2 | 1 | 2 | 3 | 2.475 | 2.150 | 2.312 | 0.59 | 1.59 | 0.86 | 49.23 | 2.08 | ok |  |", i.e.
  mu*_lim 0.59, mu*_mkt 1.59 ticks, mu10K 0.86. Its model: "T = 20 round trips per trading day, 1 contract,
  independent trades; gross P&L per trade normal with mean mu and SD sigma_T = sigma_1m (ticks). Cost per round trip
  c_lim = F_rt / v (limit case) or c_mkt = F_rt / v + S_rt (market case)" (A3_econ.md 2.1). Its "limit case" charges
  no adverse selection; under V50 that case is no longer a usable bound (section 2). The other ZM rows: Lucid 0.57 /
  1.57 (fee 9.20: mu*_lim 0.93), Tradeify 0.92 / 1.92, MFFU 0.62 / 1.62, Bulenox 1.08 / 2.08 (A3_econ.md lines 331,
  361, 390, 422, 452).
- E.31 (reports/E.31_RETURN.md lines 183-194, front month ZM.v.0, DAY session, 85,568 placements of a resting 1-lot at
  the touch): fill rate 0.704 / 0.714 / 0.515; half-spread captured +0.341 / +0.359 / -0.425; 10 s markout vs mid
  -0.629 / -0.611 / -0.545; gross 10 s edge E_10 -0.287 [-0.303, -0.273] / -0.252 [-0.267, -0.239] / -0.970
  [-0.988, -0.950] ticks per fill for models (a) K-algorithm, (b) FIFO back of queue, (c) trade-through. These are
  UNCONDITIONAL per-fill figures for a spread-capture placement loop, not conditional on any directional signal.
- V50 item 2 (docs/DECISIONS.md lines 1038-1041): "Limit orders stay allowed as an execution method for a directional
  signal. They are not a source of edge in themselves. Any later stage prices its fills under the trade-through rule
  unless a firm documents otherwise."

The worked examples use one reference signal, called S15 below: horizon H = 15 min, one position at a time, 1
contract, expected move in the signal's direction alpha = 2.0 ticks over H (gross, mid to mid), per-trade SD sigma_15 =
12.2 ticks, T = 6 trades a day (6 x 15 = 90 of the 290 day-session minutes in the market). These are illustrative
choices, not findings.

## 1. Topic (a): from a probability or forecast to entries, exits and holding time

### 1.1 Core idea
A model gives, at signal time t0, either a forecast f = E[G | x] of the signed mid move G over a horizon H, or a
probability p = P(G > 0 | x). The trade is worth taking only when its expected gross move beats the round-trip cost of
the execution design chosen (section 5) plus a margin; the exit rule (time stop, barriers, signal reversal) changes
the expected gross move itself, not only its variance. One position at a time means the traded set is a subset of
the signals, chosen by a state machine that must be replayed exactly.

### 1.2 Equations (symbols in ticks unless stated)
- G = X_{t0+H} - X_{t0}: signed mid change over the horizon; X_t the mid; f = E[G | x_t0]; c = expected cost per round
  trip of the execution design (spread paid, fees, slippage); kappa >= 0 a no-trade margin.
- (A1) Entry rule: trade in direction sign(f) iff |f| > c + kappa. Expected net per trade = |f| - c. (My derivation.)
- (A2) From a probability to an edge, under the location-shift normal model G | x ~ N(f, sigma_H^2) (an ASSUMPTION):
  p = Phi(f / sigma_H), so f = sigma_H Phi^{-1}(p), and the break-even probability is p* = Phi(c / sigma_H). (My
  derivation.) In practice the map p -> E[G | p] must be measured on held-out folds (calibration), not assumed.
- (A3) Barrier exits with no time stop, executed at the barrier: take-profit a, stop l (both in ticks of P&L after the
  half spreads), p_u = P(take-profit first): E[net] = p_u a - (1 - p_u) l - c, so p_u* = (l + c)/(a + l); symmetric
  a = l = b: p_u* = 1/2 + c/(2b). (My derivation.)
- (A4) Two-sided exit for a Brownian mid with drift mu (ticks/min) and variance sigma^2 (ticks^2/min) from 0, levels +a
  and -l: with gamma = 2 mu / sigma^2 and the scale function s(x) = exp(-gamma x),
  P(+a before -l) = (s(0) - s(-l)) / (s(a) - s(-l)) = (1 - exp(gamma l)) / (exp(-gamma a) - exp(gamma l)).
  For mu -> 0 it tends to l/(a + l) (gambler's ruin; E.28 2.7 states the driftless case). The one-sided hitting
  probabilities that this ratio is built from are Landriault, Li and Zhang (2014) eq. (2.2) (they cite Borodin and
  Salminen); the two-sided ratio is my derivation, checked numerically below.
- (A5) Wald's identity for the exit time tau: E[X_tau] = mu E[tau]. So with a constant-drift signal, any exit rule
  earns mu E[tau] in expectation: barriers that end trades early cut the expected gross move in proportion to E[tau]
  (they reduce variance, not raise the mean). Barriers add mean only if the signal's drift is front-loaded and then
  reverses, which is a property to be measured, not assumed. (Standard result, my statement.)
- (A6) One position at a time: let S be the signal set and S_exec subset of S the signals actually traded by the state
  machine (skip while in a position; optional reversal exit). The strategy's edge is the mean over S_exec of
  (G_i - c), which differs from the mean over S when signals cluster. (My statement.)
- (A7) Hysteresis (no-trade zone for exits): exit early only if the updated forecast crosses -kappa_out in the
  opposite direction; each early exit costs one more half spread and fee leg, so kappa_out >= c/2 is the natural
  floor for a reversal that does not open the opposite position, and >= c for one that does. (My derivation.)
[MathReview D-8 (lead: accepted): an early exit does not add a leg (the exit half spread and fee are paid exactly once either way), so there is no cost-based floor for a plain early exit: replace the c/2 floor by 0 (kappa_out is then a pure noise-margin choice, counted in N as (A7) says) and keep c for a reversal that opens the opposite side.]

### 1.3 Worked example on the standard ZM numbers
Reference signal S15 (section 0): H = 15 min, sigma_15 = 12.200 ticks, alpha = E[G] = 2.0 ticks, market entry and
market exit at Topstep: c = 0.5 + 0.5 + 0.528 = 1.528 ticks.
1. Break-even probability (A2): c / sigma_15 = 1.528 / 12.200 = 0.12525. Phi(0.12525) ~= 0.5 + 0.39894 x (0.12525 -
   0.12525^3/6) = 0.5 + 0.39894 x 0.12492 = 0.54984. So the classifier must be right about 55.0% of the time at 15
   minutes, at Topstep with market orders, just to break even per trade. Check: M6_tables.py gives 0.5498.
2. The same at other horizons (same c): sigma_5 = 7.044 -> Phi(0.2169) = 0.5859; sigma_60 = 24.400 -> Phi(0.0626) =
   0.5250. Under random-walk scaling, longer horizons need lower hit rates, but a real signal's alpha usually decays
   with horizon, so this favours long horizons only if alpha does not decay faster than sqrt(h).
   Per firm (market entry and exit, c = 1 + F; M6_tables_out.json):

   | Firm | c (ticks) | p* at 5 min | p* at 15 min | p* at 60 min | p_u* for +-10 barriers (A3) |
   |---|---|---|---|---|---|
   | Topstep | 1.528 | 0.5859 | 0.5498 | 0.5250 | 0.5764 |
   | Lucid | 1.560 (1.920 under the u-rule) | 0.5876 | 0.5509 | 0.5255 | 0.5780 |
   | Tradeify | 1.920 | 0.6074 | 0.5625 | 0.5314 | 0.5960 |
   | MFFU | 1.612 | 0.5905 | 0.5526 | 0.5263 | 0.5806 |
   | Bulenox | 1.572 | 0.5883 | 0.5513 | 0.5257 | 0.5786 |

   This table covers variant (i), market entry and exit. The same thresholds under variants (ii) and (iii), per firm
   route, are in section 5, Table 5.4a (column p*_15).
3. S15 held to H: net = 2.0 - 1.528 = 0.472 ticks a trade = 4.72 USD; at T = 6 trades a day, 28.3 USD a day. Its
   implied hit probability under (A2) is Phi(2.0 / 12.2) = Phi(0.1639) = 0.5651.
4. The same signal with +-10-tick barriers and no time stop (A4): mu = 2.0/15 = 0.13333 ticks/min, sigma^2 = 3.15^2 =
   9.9225 ticks^2/min, gamma = 2 x 0.13333 / 9.9225 = 0.026875 per tick; gamma x 10 = 0.26875; exp(0.26875) =
   1.30832, exp(-0.26875) = 0.76433. P(+10 first) = (1 - 1.30832) / (0.76433 - 1.30832) = -0.30832 / -0.54399 =
   0.5668, below p_u* = 0.5764, so E[net] = (2 x 0.5668 - 1) x 10 - 1.528 = 1.336 - 1.528 = -0.192 ticks. The
   barrier version of a profitable signal loses. Why (A5): E[G at exit] = 1.336 ticks = mu E[tau], so E[tau] =
   1.336 / 0.13333 = 10.0 min of drift collected instead of 15. Check: the driftless expected exit time a l / sigma^2
   = 100 / 9.9225 = 10.08 min, consistent with 10.0 (the drift barely changes E[tau] here).
5. Simulation check of (A5) with spreads (M6_limit.py, 200,000 paths, 1-second steps, market entry, take-profit and
   stop executed as market orders at the levels; rows "MKTatTT"): bracket a = 6, l = 6 around a 2.0-tick constant
   drift: E = -0.528 ticks per trade before fees, against alpha - 1 = 2.030 - 1 = 1.030 for the time stop alone (the
   simulated alpha is 2.030, 1.1 standard errors from 2.0). With a front-loaded drift (most of the 2 ticks in the
   first 3 minutes): E = +0.181, still below 1.030. Barriers are a risk tool for the firm's loss limits (section 3),
   not a source of mean under a drift signal.

### 1.4 Data it needs
Mid (or best bid and offer) at the signal time and along the horizon at event resolution: ZM MBO (ZM.v.0, ZM.v.1)
rebuilt to the top of book; ZS and ZL MBP-1 for context features only. Horizon 5 to 60 minutes; barrier labels need
event time, since a 1-minute bar cannot order a stop and a target touched in the same minute.

### 1.5 Leakage and look-ahead traps (each with a test)
- The cost c or the margin kappa chosen after seeing results. Test: c per firm and variant comes from section 5's
  table, frozen and hashed in the protocol before E.33 reads any label; E.33 recomputes the hash before scoring.
- Features computed with data at or after t0 (including the triggering event matched after its own timestamp).
  Test: recompute every feature from a copy of the book truncated at t0 - 1 ns and assert equality.
- Overlapping labels (15-minute horizons on signals minutes apart). Test: the purged and embargoed CV of V43 (E.28
  2.7); assert that no training label's span intersects a test fold's span plus embargo.
- Calibration of p fitted on test data. Test: the p -> E[G | p] map is fitted inside training folds only; a
  permutation of the test labels must leave the fitted map unchanged.
- Scoring all signals instead of the executed set S_exec (A6). Test: E.33 replays the one-position state machine
  and reports |S_exec| / |S|; scoring uses S_exec only.
- Horizons that cross a session boundary (13:20 CT close, the 07:45-08:30 CT pause) or a firm's flat time. Test:
  assert that every simulated position is closed before the boundary, and drop or truncate signals within H of it.

### 1.6 Compute
Labels and barrier scans are one forward pass per signal: O(signals x horizon events), seconds to minutes per month
of MBO on one core; the 39 months fit in RAM month by month. M6_limit.py (200,000 paths x 900 steps, two drift
profiles) ran in 14 s.

### 1.7 Verdict: use
(A1)-(A7) are definitions E.33 needs. H, kappa and any barrier levels are configurations counted in N. Prefer a time
stop at H as the primary exit (A5); barriers only as a risk overlay for loss limits, declared in advance.

## 2. Topic (b): market versus limit execution under the trade-through rule (V50), and the directional decomposition

### 2.1 Core idea
For a directional signal the question is not what a limit order earns per fill (E.31 measured that) but what it earns
per SIGNAL. A resting limit fills mostly on the paths where the price first moves against the signal and misses the
paths where the price runs in its favour, so the filled trades are worse than the signal on average and the unfilled
ones are better. Under the trade-through rule this selection is made stronger, because a fill needs the level to
trade through first. The market order buys every path at half a spread plus latency.

### 2.2 Equations
Symbols: s spread (1 tick); X_t mid path signed in the signal direction, X_0 = 0 at signal time t0; G = X_H; alpha =
E[G]; L latency (0.3-1.0 s, planner assumption); delta_L = X_L (mid move during the latency); F fee per RT; Xc the
exit leg cost (0.5 tick for a market exit); tau the limit order's timeout; Fill = {the limit at -s/2 fills by tau};
p = P(Fill).
- (B1) Market entry, value per signal: V_M = alpha - s/2 - E[delta_L] - Xc - F.
- (B2) Limit entry at the near touch (buy at the bid, price -s/2), no chase: V_L = p (E[G | Fill] + s/2 - Xc - F),
  0 when unfilled.
- (B3) Decomposition (law of total expectation): alpha = p E[G | Fill] + (1 - p) E[G | no Fill]. With selection,
  E[G | Fill] < alpha < E[G | no Fill].
[MathReview D-9 (lead: accepted): derivation to add (keep the numerical check): X has independent increments, Fill = {min_{t <= tau} X_t <= -d} is a decreasing event of the increment vector and G = X_H an increasing function of it, so the Harris (FKG) inequality gives Cov(1_Fill, G) <= 0, i.e. E[G 1_Fill] <= p E[G] and E[G | Fill] <= E[G], and (B3) then forces E[G | no Fill] >= E[G], both strict when 0 < p < 1 and the dependence is non-trivial. The condition is independent (more generally, associated) increments; it can fail for a path with mean reversion after a touch, which is why 5.6 must measure it on real signals (also applies to 5.5, original lines 690-694).]
- (B4) Exact difference (from B1-B3, my derivation): V_M - V_L = OC - p s - E[delta_L], where
  OC = (1 - p) (E[G | no Fill] - s/2 - Xc - F) is the OPPORTUNITY COST: the market-order value of the signals the
  limit fails to fill. The limit beats the market order only if p s + E[delta_L] > OC.
- (B5) Limit with timeout converting to market (chasing): V_LC = p (E[G | Fill] + s/2 - Xc - F)
  + (1 - p) (E[X_H - X_tau | no Fill] - s/2 - Xc - F). The chase pays the move already missed, E[X_tau | no Fill] > 0.
- (B6) Fill rules in the mid coordinate (stylised, my mapping): a buy limit at price P fills under trade-through (TT)
  only after a trade prints below P, i.e. once the mid has reached P - s/2 (so the order at -s/2 needs X <= -1.0);
  under a queue-depletion proxy (Q) it fills once the mid reaches P (X <= -0.5). A sell limit at P mirrors this (TT:
  X >= P + s/2; Q: X >= P).
- (B7) Marketable entry with a passive take-profit at P = entry + a: under (B6-TT) the order fills when the mid reaches
  P + s/2, at which moment a market sell gets the bid = P. So under TT a passive exit earns the same as a market exit
  triggered at the same mid level; it saves only what the trade-through fill gains over the bid at that instant (E.31:
  half-spread captured -0.425 for a TT fill, i.e. about 0.075 tick better than a market order's -0.5). Under Q it
  saves up to s/2 per take-profit fill. For an exit, a "bad" post-fill markout means the price kept moving in the
  trade's favour after it was closed: an opportunity cost, measured against the time-stop alternative.
- Measured anchors (E.31, unconditional, per fill, gross, vs the mid 10 s later): market order about -0.5 (half
  spread, unconditional markout about 0); TT -0.970; K -0.287; FIFO -0.252. A TT fill is about 0.47 tick worse than a
  market fill; a queue fill about 0.21 to 0.25 better. The stylised model (B6) reproduces the TT half-spread component
  (-0.5 against E.31's -0.425) but not E.31's further -0.545 markout; for the queue models it predicts 0 against
  +0.341 / -0.629. So the model below is run twice: "BM only", and "E.31-calibrated", which subtracts E.31's excess
  adverse markout per fill (TT 0.970 - 0.5 = 0.470; K 0.287; FIFO 0.252) from E[G | Fill]. Whether that excess
  carries over to signal-conditional fills is unknown: it is what E.33 must measure (section 5.4).

Sources for the mechanism: Lehalle and Mounjid (2018, arXiv 1610.00261v4, abstract) state it for an optimally placed
limit order: "if the price has chances to go down the probability to be filled is high but it is better to wait a
little more to get a better price", and that a prediction "is of less use if you do not have enough time to cancel
and reinsert your limit orders" (latency). Peterson and Sirri (2002, JFQA 37:2) find that unconditional cost
comparisons between order types mislead: "We attribute the difference in costs to a selection bias". Harris and
Hasbrouck (1996) impute a penalty for unexecuted limit orders [unverified: abstract via a search summary only].
Linnainmaa (2010) attributes investor-level patterns to limit orders being "price-contingent" and subject to "adverse
selection" [unverified: abstract via a search summary only].

### 2.3 Worked example (S15: alpha = 2.0 ticks over 15 min, sigma_1m = 3.15, s = 1; M6_limit.py)
Model: Brownian mid, constant drift mu = 2.0/15 = 0.13333 ticks/min (and a front-loaded variant: drift rate
proportional to exp(-t/3 min), same 2.0 ticks by 15 min); 200,000 paths on a 1-second grid, seed 20261027; fixed exit
at t0 + 15 min. Simulated alpha 2.030 (1.1 SE above 2.0; all comparisons use the same paths).

Hand check of one cell (TT, tau = 1 min, constant drift). Continuous monitoring, level d = 1.0:
P(min_{t<=1} X_t <= -1) = Phi((-1 - 0.1333)/3.15) + exp(-2 x 0.1333 x 1 / 9.9225) Phi((-1 + 0.1333)/3.15)
= Phi(-0.3598) + 0.97348 x Phi(-0.2751) = 0.3595 + 0.97348 x 0.3916 = 0.7407 (script: 0.7407; numerical integral of
the first-passage density d/(sigma sqrt(2 pi t^3)) exp(-(d + mu t)^2/(2 sigma^2 t)): 0.7407). The 1-second grid gives
0.683; the Broadie-Glasserman-Kou continuity correction (shift the level by 0.5826 sigma sqrt(dt) = 0.5826 x 3.15 x
0.12910 = 0.2369) reproduces it: Phi(-1.3702/3.15) + exp(-2 x 0.1333 x 1.2369/9.9225) Phi(-1.1036/3.15) = Phi(-0.4350) +
0.96730 x Phi(-0.3503) = 0.3318 + 0.96730 x 0.3631 = 0.6830. A fill needs a print, so the discrete grid is the better
stylisation; both are shown.

| Rule, tau | p_fill | E[G \| Fill] | E[G \| no Fill] | V_L gross (p(E[G\|F]+0.5)) | V_LC gross (chase) |
|---|---|---|---|---|---|
| TT, 0.5 min | 0.570 | 0.751 | 3.727 | 0.713 | 1.351 |
| TT, 1 min | 0.683 | 0.747 | 4.798 | 0.852 | 1.298 |
| TT, 2 min | 0.768 | 0.740 | 6.303 | 0.952 | 1.241 |
| TT, 5 min | 0.846 | 0.699 | 9.340 | 1.015 | 1.155 |
| Q, 0.5 min | 0.734 | 1.255 | 4.165 | 1.287 | 1.691 |
| Q, 1 min | 0.807 | 1.253 | 5.278 | 1.414 | 1.696 |
| Q, 2 min | 0.860 | 1.249 | 6.813 | 1.504 | 1.685 |
| Q, 5 min | 0.907 | 1.226 | 9.896 | 1.566 | 1.658 |
| Market entry (gross, alpha - 0.5) | 1 | - | - | 1.530 | - |

(Constant drift. Front-loaded drift, same table in M6_limit_stdout.txt: TT tau = 1: p 0.641, E[G|F] 0.611, E[G|nF]
4.562; chasing after 5 minutes is worth -0.098 per unfilled signal, because the alpha has already been paid out.)

Decomposition check (B3), TT tau = 1: 0.683 x 0.747 + 0.317 x 4.798 = 0.510 + 1.521 = 2.031 = simulated alpha 2.030
(rounding). The selection is large: a filled signal keeps 0.75 of its 2.03 ticks, an unfilled one would have made 4.8.

Net per signal at Topstep (Xc = 0.5 market exit, F = 0.528), TT tau = 1:
- V_M = 2.030 - 0.5 - 0.5 - 0.528 = 0.502 ticks (latency ignored: under a Brownian mid E[delta_L] = mu L = 0.1333 x
  (1/60) = 0.002 tick at L = 1 s; its SD is 3.15 x sqrt(1/60) = 0.41 tick).
- V_L (BM only) = 0.683 x (0.747 + 0.5 - 0.5 - 0.528) = 0.683 x 0.219 = 0.150.
- Identity (B4): OC = 0.317 x (4.798 - 0.5 - 0.5 - 0.528) = 0.317 x 3.270 = 1.037; p s = 0.683; V_M - V_L = 1.037 -
  0.683 = 0.354 against 0.502 - 0.150 = 0.352 (rounding). Check passed.
- V_L (E.31-calibrated) = 0.683 x (0.747 - 0.470 + 0.5 - 0.5 - 0.528) = 0.683 x (-0.251) = -0.171: the limit entry
  turns a +0.50-tick signal into a loser at Topstep.
- V_LC (chasing, BM only) = 1.298 - 0.5 - 0.528 = 0.270 (every signal trades; fee and exit on all): better than the
  pure limit, still 0.23 below the market entry.

Net per signal at Bulenox (Rithmic, queue proxy; F = 0.572), Q tau = 1:
- V_M = 2.030 - 1 - 0.572 = 0.458.
- V_L (BM only) = 0.807 x (1.253 + 0.5 - 0.5 - 0.572) = 0.807 x 0.681 = 0.550: here the limit wins by 0.09.
- V_L (E.31-calibrated, K) = 0.807 x (0.681 - 0.287) = 0.807 x 0.394 = 0.318; (FIFO) 0.807 x 0.429 = 0.346: the
  market entry wins again, by 0.11 to 0.14.

Marketable entry with a passive take-profit (B7), stop at -6 ticks of mid and time stop at 15 min, gross of fees
(M6_limit.py rows BR):

| Take-profit a (ticks) | Market exit at the TT trigger | Passive TP, TT | Passive TP, Q | P(TP), TT / Q |
|---|---|---|---|---|
| 4 | -0.706 | -0.706 | -0.455 | 0.579 / 0.602 |
| 6 | -0.528 | -0.528 | -0.316 | 0.496 / 0.515 |
| 10 | -0.207 | -0.207 | -0.060 | 0.354 / 0.370 |

Under TT the passive exit and the market exit triggered at the same mid are identical path by path (B7); under the
queue proxy the passive exit gains 0.15 to 0.25 tick per signal (about s/2 x P(TP)). All brackets lose against the
1.030-tick time stop under a constant drift (section 1, A5).

What -0.970 means for limit entries (topic b in one paragraph): a resting 1-lot at the ZM touch under TopstepX's rule
fills only after the price has moved through it, about 0.47 tick worse than a market order on the fill itself, and
it fills mostly on the paths that go against the signal. Both effects push V_L below V_M for any signal whose
alpha is not much larger than its cost. A limit entry under TT cannot be justified for a directional signal unless
E.33 measures, on its own signals, that E[G | Fill] after fees exceeds what OC gives up; the stylised model says it
will not. A marketable entry with a passive exit can help only on queue routes (Rithmic: Bulenox, Tradeify-Rithmic,
Lucid-Rithmic), only on the exit leg, and only by up to s/2 x P(TP), before any E.31-type adverse markout.

### 2.4 Data it needs
ZM MBO (ZM.v.0, ZM.v.1) event by event: book rebuild, trade prints with aggressor side, queue ahead at the order's
price; definitions for the tick and session; E.31's engine already implements the K, FIFO and TT fill models on this
data (reports/stage_e31_briefs/work/pilot/mbo_book31.py, kalgo31.py, measure31_core.py). Horizon: the timeout tau
(seconds to minutes) and the signal horizon H.

### 2.5 Leakage and look-ahead traps (each with a test)
- Placing the simulated order at t0 instead of t0 + L. Test: the engine takes L as an input; rerun with L = 0 and
  L = 1 s and require the L = 0 run to be reported only as a bound.
- Queue position initialised from the book after the order's arrival, or from the full depth including orders that
  arrive in the same packet later. Test: initialise from the book state strictly before the arrival timestamp; a
  synthetic test with a same-timestamp add must place the simulated order behind it.
- Cancel or chase decisions that use information after the decision time (for example, cancelling because the
  price "will" run). Test: decisions read only a feature snapshot taken at the decision timestamp; assert by
  recomputing the snapshot from a truncated book.
- Fills against implied liquidity not shown in the outright book (E.31: 5.5% of aggressor prints found no displayed
  resting quantity at their price). Test: report fills from prints with no displayed quantity separately.
- Conditioning the fill model on the outcome (dropping signals whose fill is "unrealistic"). Test: every signal is
  in the denominator of V_L; the count of signals equals the count of rows in the per-signal output.

### 2.6 Compute
E.31 measured 816 dates in 384 s with 4 workers (nice 10). Per-signal fill simulation for E.33 is the same work
restricted to signal times: well under an hour for 39 months on 4 to 8 cores, memory bounded by one day of MBO.

### 2.7 Verdict: use, with market entry as the default
Market entry and market exit (variant i) are the primary execution for a minutes-scale directional ZM search at every
firm. Limit entries are an execution alternative E.33 may measure (each tau is a configuration counted in N), priced
under TT at TT routes (V50) and under the queue model only on Rithmic routes. A passive exit is a "maybe" for Rithmic
routes only.

## 3. Topic (c): daily loss limits, trailing drawdowns, consistency and payout rules against a directional signal

### 3.1 Core idea
A firm's rules act on the account's daily P&L path, so they filter signals by their per-trade SD and trade count as
much as by their edge. For a 50K account the binding numbers are a 2,000 (Bulenox 2,500) trailing drawdown and, at
three firms, a 1,000 to 1,250 soft daily loss limit (DLL); payout rules then add a waiting time (winning-day counts,
minimum balances, consistency caps). A minutes-scale ZM signal has a large per-trade SD (12.2 ticks = 122 USD per
contract at 15 minutes), so at the DLL firms it is held to about one contract no matter how many the position limit
allows.

### 3.2 Equations
Per-trade model (ASSUMPTION, the same form as E.28's per-trade layer, A3_econ 2.1): T trades a day, n contracts, net
P&L per trade normal(mu_net, sigma_T^2) ticks, independent; v = 10 USD per tick.
- (C1) Daily P&L: mean m = n T mu_net v, SD s = n sqrt(T) sigma_T v (USD).
- (C2) DLL hit on a day (the intraday path as a Brownian motion with drift m and variance s^2 over the day; a hit when
  the running minimum reaches -a): P_day(a) = Phi((-a - m)/s) + exp(-2 m a / s^2) Phi((-a + m)/s) (the standard
  finite-horizon first-passage law of a drifted Brownian motion; I did not fetch a full text that prints it, so the
  formula is [unverified against a source] and is checked numerically instead: it equals the integral of the
  first-passage density to 4 decimals in M6_limit.py, and the funnel simulation's monthly DLL rates match it within
  the expected shortfall from early exits. Landriault, Li and Zhang 2014 eq. (2.1)-(2.2) give its Laplace transform
  and the infinite-horizon limit). Per
  month of 21 trading days, P_month = 1 - (1 - P_day)^21.
- (C3) Expected time to a drawdown of size a from the running maximum (continuous trailing, no lock), Landriault, Li
  and Zhang (2014) p. 5 (unnumbered, after (2.5)): E[tau_a] = (sigma^2 exp(2 mu a / sigma^2) - sigma^2 - 2 mu a) /
  (2 mu^2), with mu = m, sigma = s per day; for mu = 0 it is a^2 / s^2.
- (C4) Probability of reaching a profit target x before the first drawdown of a (continuous trailing, no lock),
  from Landriault, Li and Zhang (2014) eq. (2.7): P(M_{tau_a} >= x) = exp(-gamma x / (exp(gamma a) - 1)), gamma = 2 m /
  s^2; for m = 0 it is exp(-x/a).
- (C5) Firm rules in the simulation (M6_funnel.py; my simplification of E.28's mappings, A3_econ section 3): Brownian
  bridge intraday minimum w = (x - sqrt(x^2 + 2 s^2 E1))/2 given the close x (E.19's formula, prop_econ.returns); soft
  DLL checked first (day closes at -DLL when w <= -DLL and DLL is below the distance to the floor), else a breach when
  balance + w <= floor; the floor trails the end-of-day peak by the MLL and stops at the lock; Bulenox trails the
  intraday high (high taken before the low, conservative). Payout eligibility, first payout only:
  Topstep (Standard path) 5 days of +150 and 50% of the balance >= 125; Lucid 3 days, balance >= 2,600 (2,100 buffer
  + 500), best day <= 40% of profit; Tradeify balance >= 3,000, 5 days > 150, best day < 35% of profit; MFFU 2 days,
  balance >= 2,600, best day <= 50%; Bulenox 10 trading days, balance >= 3,600 (2,600 reserve + 1,000 minimum), best
  day <= 40% of cumulative profit. Evaluations: target 3,000 (Topstep's rises to best day / 0.55), MLL 2,000 EOD
  trailing (Topstep and MFFU and Lucid lock at the start or +100; Tradeify's evaluation floor never locks), DLL Lucid
  1,200, Tradeify 1,250, MFFU 1,000, none at Topstep (its 1,000 DLL is optional and not in the standard plan) and
  Bulenox; Bulenox's evaluation ends after 21 trading days (its 30-calendar-day clock). A failed evaluation or a
  breached funded account buys a new evaluation; fees are counted for the "fees to first payout" column (Topstep's
  49 USD rebill per 21 days in evaluation and 14.50 API per 21 days; Bulenox's 100 USD API per 21 days).

### 3.3 Worked example: the signal of (c)
S15 at mu_net = 1.0 tick net per trade (after every per-trade cost), T = 6 trades a day, sigma_T = sigma_15 = 12.200
ticks, n = 1 contract.
1. (C1) m = 1 x 6 x 1.0 x 10 = 60.0 USD a day. s = 1 x sqrt(6) x 12.200 x 10 = 2.44949 x 122.00 = 298.84 USD a day.
2. (C2) at a = 1,000 USD (MFFU; also Topstep's optional DLL): s^2 = 89,305; (-1,000 - 60)/298.84 = -3.5471, Phi =
   0.000195; exp(-2 x 60 x 1,000 / 89,305) = exp(-1.34371) = 0.26087; (-1,000 + 60)/298.84 = -3.1455, Phi = 0.000829;
   P_day = 0.000195 + 0.26087 x 0.000829 = 0.000411; P_month = 1 - (1 - 0.000411)^21 = 0.0086. At a = 1,200 (Lucid):
   P_month 0.00055; at a = 1,250 (Tradeify): 0.00026. Simulation (first 21 evaluation days, MFFU): 0.0078, the gap
   being days lost to passing or breaching before day 21.
3. (C3) a = 2,000: 2 m a / s^2 = 240,000 / 89,305 = 2.68742; exp = 14.693; E[tau] = (89,305 x 14.693 - 89,305 -
   240,000) / (2 x 3,600) = (1,312,160 - 329,305) / 7,200 = 136.5 trading days. At mu_net = 0: 2,000^2 / 89,305 =
   44.8 days. a = 2,500 (Bulenox): 302.8 days (70.0 at zero edge).
4. (C4) gamma = 120 / 89,305 = 0.0013437 per USD; gamma x 3,000 = 4.0311; exp(gamma x 2,000) - 1 = 13.693; P(reach
   +3,000 before a 2,000 drawdown) = exp(-4.0311 / 13.693) = exp(-0.29439) = 0.745 (continuous trailing, no lock, no
   clock). For a = 2,500: 0.865. Check: a 48-steps-a-day simulation of the same continuous model gives 0.870 for a =
   2,500 (discrete monitoring misses some breaches, so slightly higher). Sanity bound: the EOD-trailing evaluations in
   the funnel simulation pass 0.78 to 0.81 of first attempts, above the continuous 0.745, as they must (an
   end-of-day floor trails less than an intraday one).
5. Funnel simulation (M6_funnel.py, 20,000 paths, up to 756 trading days, seed 20261027), mu_net = 1.0, n = 1:

| Firm | P(DLL hit) in eval month 1 | P(trailing breach) in eval month 1 | P(breach) in funded month 1 | P(pass, 1st attempt) | median days to pass | P(1st payout from the 1st funded account) | mean (median) trading days to 1st payout | mean attempts | mean fees to 1st payout (USD) | mean 1st payout, gross (USD) |
|---|---|---|---|---|---|---|---|---|---|---|
| Topstep | 0 (no DLL; optional 1,000 DLL would be 0.0086) | 0.063 | 0.051 | 0.810 | 37 | 0.930 | 68.6 (59) | 1.33 | 366 | 522 |
| Lucid | 0.0006 | 0.063 | 0.061 | 0.806 | 37 | 0.822 | 103.4 (88) | 1.52 | 245 | 693 |
| Tradeify | 0.0003 | 0.064 | 0.061 | 0.782 | 36 | 0.812 | 111.3 (95) | 1.58 | 212 | 1,500 |
| MFFU | 0.0078 | 0.063 | 0.061 | 0.806 | 37 | 0.822 | 103.3 (88) | 1.51 | 232 | 689 |
| Bulenox | 0 (no DLL) | 0.029 | 0.029 | 0.128 | 17 | 0.852 | 226.6 (184) | 8.24 | 2,692 | 1,185 |

   Reading: at one contract the DLL is irrelevant (under 1% a month) and the trailing drawdown takes about 6% of
   accounts a month; the time to the first payout is 3 to 5 months of trading days at four firms. Bulenox is the
   exception: the 21-day P&L has mean 21 x 60 = 1,260 USD and SD 298.84 x sqrt(21) = 1,369 USD, so the 3,000 target
   sits (3,000 - 1,260) / 1,369 = 1.27 SD above the mean; 1 - 0.128 - 0.029 = 84% of first attempts expire unpassed,
   and the 175 USD purchases plus 100 USD a month of API dominate.
6. Sensitivity to edge and size (same model; full grid in M6_funnel_out.json and M6_funnel_stdout.txt):

| mu_net, n | Topstep P(pass) / days to payout | MFFU P(DLL, eval month 1) / P(pass) / days | Tradeify P(DLL) / P(pass) / days | Bulenox P(pass) / days |
|---|---|---|---|---|
| 0.0, 1 | 0.253 / 239.1 | 0.013 / 0.249 / 350.4 | 0.001 / 0.233 / 363.5 | 0.022 / 403.9 |
| 0.5, 1 | 0.562 / 115.7 | 0.010 / 0.557 / 201.9 | 0.000 / 0.529 / 220.3 | 0.057 / 353.0 |
| 1.0, 1 | 0.810 / 68.6 | 0.008 / 0.806 / 103.3 | 0.000 / 0.782 / 111.3 | 0.128 / 226.6 |
| 2.0, 1 | 0.979 / 38.0 | 0.003 / 0.978 / 50.3 | 0.000 / 0.974 / 53.7 | 0.406 / 78.2 |
| 1.0, 2 | 0.580 / 43.9 | 0.537 / 0.573 / 59.1 | 0.211 / 0.548 / 68.9 | 0.498 / 73.0 |
| 1.0, 4 | 0.405 / 43.6 | 0.803 / 0.430 / 47.1 | 0.666 / 0.413 / 59.8 | 0.252 / 94.3 |

   ("days" = mean trading days to the first payout among paths paid within 756 days; at zero edge most paths are
   still eventually paid by variance and repeated purchases, which is why EV, not the payout rate, is the test.)
   At 2 contracts the DLL hits in about half of MFFU evaluation months (closed form 0.76 at a = 1,000; the
   simulation is lower because accounts end early); at 4 contracts in 67-80%. The DLL caps a 15-minute ZM signal at
   about one contract at MFFU, Lucid and Tradeify: s per contract is 298.84 USD, and a = 3 s (P_day ~ 0.1-0.3%) needs
   n <= 1,000 / (3 x 298.84) = 1.1 (MFFU), 1.3 (Lucid), 1.4 (Tradeify).
7. What this means for which signals are usable:
   - Per-trade SD sets the size, not the position limit (4 to 7 lots). A 60-minute signal (sigma_T 24.4) at T = 3 has
     s = sqrt(3) x 24.4 x 10 = 422.6 USD a contract: a DLL of 1,000 is then 2.4 s, a hit about every 55 days at zero
     edge (2 Phi(-2.37) = 0.018 a day).
   - Fewer, larger trades raise the chance of a "best day" that breaks a consistency cap (35% at Tradeify, 40% at
     Lucid and Bulenox, 50% at MFFU, 55% of target in Topstep's evaluation); many small trades make it rarer.
   - Winning-day counts (Topstep 5 x 150, Tradeify 5 x > 150) favour a daily P&L whose median is above 150 USD; at
     m = 60 and s = 299 one day in three clears 150 (P(x >= 150) = Phi((60 - 150)/298.84) = Phi(-0.301) = 0.382).
   - Bulenox's 21-day evaluation clock rewards high daily mean or more contracts (no DLL there): at mu_net = 1.0 two
     contracts nearly quadruple the pass rate (0.128 to 0.498).
   - The edge needed to make a cycle pay its fixed fees, spread over the trades to the first payout (fees / (T x days
     x v)): Topstep 366 / (6 x 68.6 x 10) = 0.089 tick a trade; Lucid 0.039; Tradeify 0.032; MFFU 0.037; Bulenox
     2,692 / (6 x 226.6 x 10) = 0.198. Small next to the execution costs of section 5, except at Bulenox.
   - E.29's finding on micro payout thresholds (reports/E.29_RETURN.md section 1): MGC's break-even "is inflated by
     payout thresholds a one-lot micro rarely clears". ZM has no micro at any of the five firms, and a one-lot ZM
     15-minute signal has a daily P&L SD of about 299 USD. A fixed winning-day threshold such as 150 USD is therefore
     0.50 daily SD, not the several SD it is for a one-lot micro, so ZM does not suffer that inflation. The reverse
     risk applies instead: the DLL binds at two contracts (item 6 above).
   - Section 5 (5.4b) repeats this funnel per firm and per execution variant for S15 at its own net edge.

### 3.4 Data it needs
None from the market for the rule model; E.33's own per-trade P&L series (net, per variant) on the discovery dates
feeds it in place of the normal assumption (block bootstrap of days, as E.19 did).

### 3.5 Leakage and look-ahead traps (each with a test)
- Choosing the contract count or the firm after seeing the discovery P&L. Test: n and the firm list are fixed in the
  protocol; E.33 reports every firm and n in the grid.
- Normal-tail daily P&L understates DLL and breach rates (fat tails at USDA releases: E.31 saw -8.98 ticks per fill in
  the 5 minutes after a release). Test: rerun the funnel on a day-block bootstrap of E.33's own daily P&L and report
  both.
- Intraday ordering: a bridge minimum given the close is exact for Brownian motion only. Test: on E.33's simulated
  trades, compute the realised intraday worst P&L and compare its distribution with the bridge model's.

### 3.6 Compute
M6_funnel.py ran 60 firm x edge x size cells of 20,000 paths x up to 756 days in 125 s on one core. The program's
prop_econ (E.19/E.28) is the reference implementation for any number that enters a verdict.

### 3.7 Verdict: use (as a filter, with the program's simulator for verdict numbers)
Report per firm, for each E.33 signal, the DLL and drawdown probabilities and the time to the first payout from its
own per-trade P&L. Limit size to one contract at DLL firms for minutes-scale ZM signals unless the per-trade SD is
much smaller than 12 ticks. These are my simplified simulations: an independent reviewer should recompute the key
cells with prop_econ before they enter any verdict.

## 4. Topic (d): ZM at each of the five firms

All firm facts below were recorded by E.28's A2 readers on 2026-10-20/21 (or by E.31's planner notes, firm pages read
2026-10-22): 6 to 7 days old, inside the 30-day line, so no firm page was re-fetched (decision logged in
pages/M6_prop_strategy/log.tsv). Each fact is [as recorded by E.28/E.31]; quotes are from E.28's saved files under
reports/stage_e28_briefs/pages/. Lucid, Tradeify and Bulenox forbid automated access in their terms (E.28 decisions),
so a re-fetch would not have been allowed anyway.

### 4.1 The table

| Item | Topstep | Lucid | Tradeify | MFFU | Bulenox |
|---|---|---|---|---|---|
| ZM tradable | yes, "Soybean Meal (ZM)" | yes, "ZM / Soybean Meal Futures / 2.80 / CBOT" | yes (product and fee tables) | yes, "listed", tick 0.10 / 10.00 | yes, "ZM Soybean Meal Futures 2.86 5.72" |
| MZM (micro) | not listed | not listed | not listed | not listed | not listed |
| Max contracts, 50K | Combine 5 minis (10:1 micros); XFA 2 / 3 / 5 by balance (< 1,500 / 1,500-2,000 / > 2,000); no grain volatility cap (caps listed only for energies and metals) | 4 minis (eval and sim funded) | 4 minis (5 for accounts bought before 2025-09-12) | 4 minis | 7 (Option 1, trailing); Option 2 EOD 2 / 4 / 7 by cash on hand |
| Fee per RT, USD (ticks) | 5.28 (0.528) | 5.60 (0.560); all-in status unknown, E.28 u-rule 9.20 (0.920) | 9.20 (0.920), all-in stated | 6.12 (0.612) | 5.72 (0.572) |
| News window | Tier 1 (CPI, FOMC decision and press conference, NFP, PPI): no new opens 5 min either side, for the listed minis only; "Other products (energies, rates, FX, etc.) are unaffected"; grains not listed | LucidPro (standard plan): news allowed, no window; LucidDaily: "Trading red folder news on the LucidDaily is a hard breach" | none: "We do not have any rules against or guidelines around trading news events" | Builder (standard plan): unrestricted in eval and sim funded; Rapid and Pro sim funded: T1 events include "For Agricultural Traders : Agricultural Reports", "No positions or orders (including limit orders) can be open 2 minutes before and after the release" | none: "No blackout windows" |
| USDA reports covered? | no (not in the Tier 1 list); but "Purposefully trading your full Maximum Position Size directly into a scheduled major news event" is a prohibited strategy (whether a USDA report is "major news" is not defined) | not on LucidPro; on LucidDaily only if USDA counts as "red folder" (not defined) | no | only on Rapid / Pro sim funded ("Agricultural Reports"); not on Builder | no |
| Holding through a report | allowed (below max size) | allowed (Pro) | allowed | allowed on Builder; not on Rapid / Pro (2-minute window) | allowed |
| Daily flat time | 15:10 CT, and "If you're trading a product with an earlier daily close than 3:10 PM CT, you must exit before that product's close" (ZM: 13:20 CT) | 16:45 ET (15:45 CT); auto-close, not a failure | 16:45 ET; auto-close, not a failure | 16:10 ET (15:10 CT) auto-liquidation; no overnight | 15:59 CT; "Holding positions overnight is strictly prohibited." |
| ZM overnight session (19:00-07:45 CT) and the 07:45-08:30 CT pause | inside Topstep's trading day (17:00-15:10 CT); "CBOT Commodity Market Pause (Mon-Fri): 7:45 AM - 8:30 AM CT. No orders accepted during this window. TopstepX manual lockout is not available for CBOT positions held during this time." So a position may be held through the pause | inside the firm's day; no rule found [inference] | inside the firm's day (18:00-16:45 ET) [inference] | inside the firm's day (18:00-16:10 ET) [inference] | inside the firm's day (17:00-16:00 CT) [inference] |
| Price-limit rule | no position within 2% of a price limit: "Stop trading above: Settlement x (1 + Price Limit% - 2%)" | none found | none found | "we do not allow market participation when a product is trading within 2% of a price limit" (sim funded and live) | none found |
| Automation | allowed in Combine and XFA via the ProjectX API (14.50 USD/month with code); not on Live; VPS prohibited for order transmission | permitted; HFT banned (no number); microscalping test (> 50% of profit from holds <= 5 s) | bots allowed if solely owned, not shared or multi-firm, not HFT, live video on request; Tradovate API only on Live, so automation runs inside a desktop platform on eval and sim funded | allowed if it does not "exploit the favorable fills offered in the Simulated Environment"; no MFFU API documented [unverified whether Tradovate's API is enabled] | user-built bots allowed; third-party algorithms need approval; "scalping" algorithms banned (undefined); API / Trader Composite 100 USD/month |

### 4.2 What the table means for a minutes-scale ZM bot
- ZM is tradable at all five firms; no firm lists the micro (MZM), so size steps are 10 USD a tick.
- No firm's standard 50K plan blocks USDA reports: Topstep's Tier 1 list does not name grains, and MFFU's
  agricultural-report window applies only to its Rapid and Pro sim funded plans (E.28's standard MFFU plan is
  Builder). E.33 should still treat report windows as a declared feature or exclusion: E.31 measured -8.98 ticks per
  passive fill in the 5 minutes after a USDA release (68 fills, reports/E.31_RETURN.md line 203), and limit days
  trigger the 2% price-limit rules at Topstep and MFFU. USDA times (E.31 data facts, reports/stage_e31_briefs/research/
  data_facts.md lines 150-151): WASDE and Crop Production 12:00 ET (11:00 CT, inside the day session); FAS weekly Export
  Sales 08:30 ET Thursday (07:30 CT, inside the overnight session, 15 minutes before the pause) [rule-derived in E.31,
  unverified].
- Price-limit rules in ticks (illustrative arithmetic, not a data read): at a settlement of P USD/ton and a daily
  limit of D USD/ton, Topstep's stop line is P (D/P - 0.02) = D - 0.02 P from settlement. With D = 20 (the limit on
  trade date 2026-10-21 per the E.31 planner notes [secondary, unverified]; E.31 data facts record 30 USD/ton for
  2022-11 to 2023-04) and an illustrative P = 300, the line is 20 - 6 = 14 USD/ton = 140 ticks from settlement; with
  D = 30 it is 240 ticks. Against a median daily range of 96 ticks it binds only on large-move days, which are the
  report days.
- Every ZM position ends by 13:20 CT. A position opened late in the overnight session can be carried through the
  07:45-08:30 CT pause at Topstep (explicit) and, by inference, at the others, but no order can be sent during the
  pause at Topstep, so a stop cannot be moved: a 45-minute unmanaged gap that E.33 should either forbid or price.
- Size is limited by the DLL (section 3: about one contract at MFFU, Lucid, Tradeify for a 15-minute signal), not
  by the 4-7 lot position limits; Topstep's XFA starts at 2 lots, which does not bind at one contract.

## 5. Topic (e): the three execution variants, per firm and route (planner requirement, user 2026-10-26 23:15 PDT)

Section written 2026-10-27 02:43 PDT (file mtime) by the re-spawned worker. New script: work/M6_prop_strategy/M6_variants.py (+
M6_variants_out.json, M6_variants_stdout.txt; formatting helper M6_sec5_rows.py -> M6_sec5_rows.txt). It uses the
same stylised Brownian model as M6_limit.py: 100,000 paths with common random numbers over a grid of alpha (0 to 6
ticks over 15 minutes), timeouts tau = 0.5, 1 and 5 minutes, and it imports my M6_funnel.run for the payout funnel.
Runtime 35 s, peak RSS 0.32 GB, nice 10. No market data.

### 5.1 Core idea
Each route a firm offers fixes how a simulated limit order fills, and therefore which of three cost models applies:
(i) market orders (every firm; the default); (ii) limit orders under trade-through (documented by TopstepX, assumed
for Tradovate); (iii) limit orders under an estimated-queue rule (Rithmic, as a Rithmic staff post on a forum
describes it). A directional signal is priced per SIGNAL under each variant its route admits (section 2's
decomposition). The table then gives, per firm and variant, the gross move the signal needs before it pays.

### 5.2 Equations: the per-fill and per-round-trip cost of each variant
Symbols as in sections 1-2, in ticks. F is the firm's fee per RT, L the order latency, and touch_t the best price on
the order's side at time t.
- (E1) Variant (i), market: the fill price for a 1-lot buy is touch_{t0+L} (the ask when the order reaches the
  simulator). Cost against the mid at t0: k_M = s/2 + (mid_{t0+L} - mid_{t0}) + (half spread at t0+L - s/2) + a depth
  term. For one contract the depth term is 0 whenever the touch shows at least one lot, which it always does if the
  level exists. For n lots it is the extra ticks walked across levels, summed, read from the book at t0 + L. Round
  trip: c_M = s + F + E[latency terms on both legs]. Under a driftless random walk the latency term has mean mu L and
  SD sigma_1m sqrt(L / 60 s). At 0.3 s the SD is 3.15 x sqrt(0.005) = 0.223 tick; at 1.0 s it is 3.15 x sqrt(1/60) =
  0.407 tick. The means for S15's mu = 0.1333 tick/min are 0.0007 and 0.0022 tick. A signal triggered by a price
  move can have E[mid_{t0+L} - mid_{t0} | signal] far from mu L, through continuation or a bounce. E.33 has to
  measure that quantity; this note cannot bound it.
- (E2) Variant (ii), trade-through: a buy limit at P fills only after a trade prints below P (TopstepX: "the market
  has to trade through your price — not just touch it"). E.31's unconditional anchor is E_10 = -0.970 [-0.988,
  -0.950] ticks per fill (model c). A spread-capture round trip with both legs passive costs 2 x 0.970 + F. A
  directional round trip with a passive entry and a market exit costs 0.970 + 0.5 + F. These per-fill figures are
  unconditional, and section 2 shows why a directional signal's cost per signal differs from them.
- (E3) Variant (iii), estimated queue: Rithmic's post reports a fill "when the market trades through your price and
  when the orders ahead of you in the queue ... are depleted and there is quantity or opposite side order activity at
  your price level". The wording is AMBIGUOUS:
  - JOINT reading ("and"): a Rithmic fill needs both a trade-through and a depleted queue. That is at least as strict
    as (ii), so (ii)'s -0.970 would be an optimistic bound for Rithmic, not a pessimistic one.
  - ALTERNATIVE reading: a fill can occur at the touch once the estimated queue is consumed. E.31's model (a),
    K-algorithm (E_10 -0.287 [-0.303, -0.273]), and model (b), FIFO back of queue (-0.252 [-0.267, -0.239]),
    simulate this reading.

  The post's preceding sentence ("takes into account ... Rithmic's estimated place of the order in the order queue")
  points to a queue model, and its author calls the result "not pessimistic". Both fit the alternative reading
  better, but the text does not settle the question. The proxy below follows the planner's queue reading. Every
  queue-route figure is shown beside the TT figure for the same firm, so under the joint reading the TT row applies.
- (E4) Per-signal values for a directional entry with a market exit (section 2, B1, B2, B5), calibrated variant:
  V_M = alpha - s - F; V_L = p (E[G | Fill] - cal_v - F); V_LC = V_L + (1 - p)(E[X_H - X_tau | no Fill] - s - F).
  Here cal_v is E.31's adverse markout per fill in excess of the stylised model's own (TT 0.470, K 0.287, FIFO 0.252;
  section 2.2); "BM" rows set cal_v = 0. The break-even alpha_v* solves V_v(alpha) = 0. The per-trade target
  alpha_v(1.0) solves (value per EXECUTED trade) = 1.0 tick, which is the signal of (c).
- (E5) When a limit beats a market entry (section 2, B4): p s + E[delta_L] > OC = (1 - p)(E[G | no Fill] - s/2 - Xc
  - F). The E.31 calibration adds p cal_v to the limit's deficit: V_M - V_L = OC - p s + p cal_v - E[delta_L].

### 5.3 The firm-route table
Facts are [as recorded by E.28 (pages read 2026-10-20/21), the E.31 planner notes (2026-10-22) or E.13
(2026-10-03)]. Quotes and saved files are in section 6. Variant labels: (i) market, (ii) TT limit, (iii) queue limit.

| Firm | Platform route(s) | Fill variant(s) admitted | Fee per RT, ticks | Rules bearing on the variant | Minutes-scale directional bot admitted? |
|---|---|---|---|---|---|
| Topstep | TopstepX (web/desktop), Quantower via TopstepX credentials, ProjectX API (Combine and XFA only) | (i); (ii) documented | 0.528 | The 2026-06-10 page bans "hundreds of rapid trades to take advantage of preferential queue position in SIM", "tight brackets or auto-breakeven to take advantage of favorable SIM fills", and "Placing orders at prices outside the current best bid or offer". The last is AMBIGUOUS. Read literally, it covers a resting limit deeper than the touch, and also a passive take-profit or a resting stop, which by construction sit outside the best bid or offer. The page's own context (SIM-fill abuse, "average durations measured in seconds, not minutes") suggests it targets abuse, not brackets. No orders are accepted during the CBOT pause, 07:45-08:30 CT. | Yes in the Combine and XFA, via the ProjectX API (14.50 USD/month). No on the LFA ("automated strategies are not possible at this time in the Live Funded Account"). HFT banned |
| Lucid | CQG route (NinjaTrader, Tradovate, TradingView) and Rithmic route (Quantower, Sierra Chart, R\|Trader Pro, others); Rithmic is the default in the pricing config | (i) on both. (ii) on CQG [ASSUMPTION: CQG's sim fill rule is unpublished and no Lucid page documents one, so per V50 ("unless a firm documents otherwise") it is priced as trade-through]. (iii) on Rithmic [forum pointer; under the joint reading = (ii)] | 0.560 (0.920 if the 5.60 is not all-in) | Microscalping: flagged if "More than 50% of your profits are generated from trades held for 5 seconds or less". HFT banned (no number). Exploiting simulated conditions banned | Yes: "Automated strategies and in-platform/third party trade copiers are permitted". No Lucid API is named, so the bot runs inside a desktop platform or through the route's own API [unverified which] |
| Tradeify | Tradovate (Tradovate, NinjaTrader, TradingView), Rithmic (Tradesea, Quantower, Sierra Chart, R\|Trader), WealthCharts; broker fixed at checkout | (i) on all. (ii) on Tradovate [assumed TT]. (iii) on Rithmic. WealthCharts: rule unknown [ASSUMPTION: TT, as Tradovate] | 0.920 (all-in stated) | Funded payouts gated on "Over 50% of your trades are longer than 10 seconds" and "Over 50% of your profit must come from trades held longer than 10 seconds". Exploiting sim conditions banned. HFT banned | Yes, if solely owned, not shared, not used across firms and not HFT. The Tradovate API is live-only, so on evaluation and sim funded accounts the bot runs inside a desktop platform. Rithmic API status not stated |
| MFFU | Tradovate accounts (Tradovate, NinjaTrader, TradingView; third-party platforms through a dxFeed connection) | (i); (ii) [Tradovate assumed TT] | 0.612 | "Simultaneously placing multiple limit orders at the same price to manipulate order fills is prohibited". "Exploiting the absence of slippage and utilizing tight brackets to gain from favorable fills are not permitted". Automation allowed only if it does not "exploit the favorable fills offered in the Simulated Environment". HFT banned (undefined today; an earlier page said over 200 trades a day) | Yes, inside a platform. No MFFU API documented |
| Bulenox | Rithmic only ("Rithmic Paper Trading"); API through "an approved third-party API or Trader Composite interface", 100 USD/month | (i); (iii) [forum pointer; under the joint reading = (ii)] | 0.572 | Bans "scalping" algorithms, the DTC Protocol Bridge API and "automated discretional trading" (no number, no hold-time threshold). Third-party algorithms need approval | Yes, if user-built and not judged "scalping" (undefined) |
| Apex (not one of the five) | Tradovate route named by the planner; a Canadian page names Tradovate [route list not verified] | (i); (ii) assumed | not recorded | "No Automation or Algorithm Usage allowed" (Wayback capture 2026-03-03, read by E.13). The capture is older than 30 days, and the current terms were unreachable on 2026-10-03 | NO |
| Take Profit Trader (not one of the five) | Tradovate, Rithmic and NinjaTrader listed (tpt_platforms) | (i); (ii) or (iii) by route | not recorded | "#1: No Trading Bots or Algos. Automated trading systems, bots, or algorithmic execution tools are not permitted." (help page updated 2026-06-12, read by E.13 on 2026-10-03). The planner's "excludes automated seconds-scale systems" understates this: every bot is excluded | NO |

What the table shows:
- A minutes-scale directional bot is outside every numeric hold-time threshold (Lucid 5 s, Tradeify 10 s), and at
  Topstep it is not "hundreds or thousands of trades per day".
- Such a bot is admitted at Topstep (Combine and XFA), Lucid, Tradeify, MFFU and Bulenox. At Bulenox it remains
  subject to an undefined "scalping" judgment. It is excluded at Apex and Take Profit Trader.

Two open points belong to the lead:
1. Topstep's "outside the best bid or offer" wording against resting stops and take-profits. The bot could send
   market exits on its own trigger instead, but it would then have no server-side protection during a disconnect,
   and none at all during the CBOT pause.
2. The fill assumptions for CQG and WealthCharts.

### 5.4 Worked example: per firm and variant, the S15 signal and the edge it needs
S15: H = 15 min, 6 signals a day, 1 contract, nominal alpha 2.0 ticks, limit timeout tau = 1 minute, exit by market
order at H. "BM" = stylised model only; "cal" = E.31-calibrated (the primary rows).

Simulation noise in alpha: the common-random-number paths give a simulated alpha of 2.055 at the nominal 2.0. The SE
is 12.2 / sqrt(100,000) = 0.039, so this is 1.4 SE high (M6_limit.py's 200,000 paths gave 2.030). S15 values below
are taken at alpha_sim 2.055, so the market rows are 0.025 tick above the exact alpha - 1 - F. The break-even columns
are interpolated against alpha_sim and are not affected.

Hand check of three cells. Inputs from M6_variants_out.json, alpha 2.0 row: TT tau 1 gives p = 0.684, E[G | Fill] =
0.744, E[X_H - X_tau | no Fill] = 2.002; Q tau 1 gives p = 0.808, E[G | Fill] = 1.273.
- Topstep, (ii) cal: per trade 0.744 - 0.470 - 0.528 = -0.254; per signal 0.684 x (-0.254) = -0.174; with the
  chase, -0.174 + 0.316 x (2.002 - 1 - 0.528) = -0.174 + 0.316 x 0.474 = -0.174 + 0.150 = -0.024 ticks. Market:
  2.055 - 1 - 0.528 = 0.527.
- Bulenox, (iii) K cal: per trade 1.273 - 0.287 - 0.572 = 0.414; per signal 0.808 x 0.414 = 0.335. Market: 2.055 -
  1.572 = 0.483.
- Decomposition check (B3), TT tau 1, alpha row 2.0: 0.684 x 0.744 + 0.316 x 4.895 = 0.509 + 1.547 = 2.056, against
  alpha_sim 2.055. Check passed.

Table 5.4a gives, per firm and variant, the value per signal, the break-even alpha and the alpha needed for 1.0 tick
net per executed trade. Columns:
- p: fill probability.
- V/signal and V/trade: value per signal and per executed trade.
- alpha*: break-even gross move over 15 min (ticks).
- p*_15 = Phi(alpha* / 12.2): the hit rate that alpha* implies under the normal model (A2).
- alpha(1.0): the gross move giving 1.0 tick net per executed trade (the signal of (c)).
- L = limit, no chase; LC = limit, chasing at market after tau.

| Firm | Variant | p | V/signal | V/trade | alpha* | p*_15 | alpha(1.0) |
|---|---|---|---|---|---|---|---|
| Topstep | (i) market | 1 | 0.527 | 0.527 | 1.528 | 0.5498 | 2.528 |
| Topstep | (ii) TT, L, cal | 0.684 | -0.174 | -0.254 | 2.317 | 0.5753 | 3.339 |
| Topstep | (ii) TT, LC, cal | 1 | -0.024 | -0.024 | 2.080 | 0.5677 | 3.112 |
| Topstep | (ii) TT, L, BM | 0.684 | 0.148 | 0.216 | 1.836 | 0.5598 | 2.860 |
| Lucid | (i) market | 1 | 0.495 | 0.495 | 1.560 | 0.5509 | 2.560 |
| Lucid | (ii) TT on CQG [assumed], L, cal | 0.684 | -0.196 | -0.286 | 2.350 | 0.5764 | 3.371 |
| Lucid | (ii) TT on CQG [assumed], LC, cal | 1 | -0.056 | -0.056 | 2.113 | 0.5688 | 3.145 |
| Lucid | (iii) Rithmic K, L, cal | 0.808 | 0.344 | 0.426 | 1.626 | 0.5530 | 2.637 |
| Lucid | (iii) Rithmic FIFO, L, cal | 0.808 | 0.373 | 0.461 | 1.590 | 0.5519 | 2.602 |
| Lucid | (iii) Rithmic K / FIFO, LC, cal | 1 | 0.436 / 0.464 | same | 1.610 / 1.581 | 0.5525 / 0.5515 | 2.633 / 2.604 |
| Lucid | (iii) Rithmic, L, BM | 0.808 | 0.576 | 0.713 | 1.335 | 0.5436 | 2.346 |
| Lucid (u-rule fee 0.920) | (i) / (ii) L cal / (iii) K L cal | 1 / 0.684 / 0.808 | 0.135 / -0.442 / 0.053 | 0.135 / -0.646 / 0.066 | 1.920 / 2.719 / 1.989 | 0.5625 / 0.5882 / 0.5648 | 2.920 / 3.736 / 3.000 |
| Tradeify | (i) market | 1 | 0.135 | 0.135 | 1.920 | 0.5625 | 2.920 |
| Tradeify | (ii) TT on Tradovate, L, cal | 0.684 | -0.442 | -0.646 | 2.719 | 0.5882 | 3.736 |
| Tradeify | (ii) TT on Tradovate, LC, cal | 1 | -0.416 | -0.416 | 2.484 | 0.5807 | 3.517 |
| Tradeify | (iii) Rithmic K, L, cal | 0.808 | 0.053 | 0.066 | 1.989 | 0.5648 | 3.000 |
| Tradeify | (iii) Rithmic FIFO, L, cal | 0.808 | 0.082 | 0.101 | 1.954 | 0.5636 | 2.965 |
| Tradeify | (iii) Rithmic K / FIFO, LC, cal | 1 | 0.076 / 0.104 | same | 1.978 / 1.949 | 0.5644 / 0.5635 | 3.002 / 2.973 |
| MFFU | (i) market | 1 | 0.443 | 0.443 | 1.612 | 0.5526 | 2.612 |
| MFFU | (ii) TT, L, cal | 0.684 | -0.231 | -0.338 | 2.403 | 0.5781 | 3.424 |
| MFFU | (ii) TT, LC, cal | 1 | -0.108 | -0.108 | 2.167 | 0.5705 | 3.199 |
| MFFU | (ii) TT, L, BM | 0.684 | 0.090 | 0.132 | 1.922 | 0.5626 | 2.946 |
| Bulenox | (i) market | 1 | 0.483 | 0.483 | 1.572 | 0.5513 | 2.572 |
| Bulenox | (iii) K, L, cal | 0.808 | 0.335 | 0.414 | 1.638 | 0.5534 | 2.649 |
| Bulenox | (iii) FIFO, L, cal | 0.808 | 0.363 | 0.449 | 1.602 | 0.5522 | 2.614 |
| Bulenox | (iii) K / FIFO, LC, cal | 1 | 0.424 / 0.452 | same | 1.622 / 1.593 | 0.5529 / 0.5519 | 2.646 / 2.617 |
| Bulenox | (iii), L, BM | 0.808 | 0.567 | 0.701 | 1.347 | 0.5440 | 2.359 |

[MathReview D-10 (lead: accepted): Table 5.4a states no Monte Carlo uncertainty; four independent batches of 100,000 CRN paths give an SD of 0.03-0.04 ticks for the limit (L) rows at tau = 1 (interpolated against alpha_sim) and 0.004 for LC rows, so report alpha* to two decimals with its SE (about +-0.04 for L rows, +-0.01 for LC rows at 100k paths). The queue-limit difference of +0.03 to +0.07 against the market entry is one to two SE, so rewrite reading 1-2 (original lines 626-636) and 5.7's "cheapest everywhere" (original lines 752-753) as "cheapest on TT routes; indistinguishable from the calibrated queue limit on Rithmic routes within model noise"; the TT conclusion (+0.69 to +0.80, about 20 SE) and the verdict (market primary; queue "maybe" on Rithmic, measured in E.33) stand.]

Every row for every firm, including the BM chase rows and tau = 0.5 and 5 minutes, is in M6_sec5_rows.txt and
M6_variants_out.json. The timeout barely moves the break-even: at Topstep, (ii) cal, alpha* is 2.336 at tau 0.5,
2.317 at 1 and 2.358 at 5; at Bulenox, (iii) K cal, it is 1.651, 1.638 and 1.656.

Reading of 5.4a:
1. Under the E.31 calibration, the market entry is the cheapest at every firm. The TT limit needs 0.79 tick more
   gross move than a market order (Topstep 2.317 vs 1.528; MFFU 2.403 vs 1.612; Tradeify 2.719 vs 1.920). The queue
   limit needs 0.03 to 0.07 tick more (Bulenox K 1.638 and FIFO 1.602 vs 1.572; Lucid-Rithmic 1.626 / 1.590 vs
   1.560).
2. Only the uncalibrated queue model (BM, (iii)) makes the limit cheaper than the market entry: at Bulenox, 1.347 vs
   1.572, a 0.22-tick saving. E.31's measured adverse markout removes that gain. Whether fills conditional on a
   signal carry E.31's unconditional excess markout is the open question of 5.6.
3. Chasing (LC) recovers part of the TT loss but never beats the market entry.
4. With market orders, the signal of (c) (1.0 tick net per trade) needs a gross alpha of 2.53 to 2.92 ticks over 15
   minutes (Topstep 2.528, Lucid 2.560, Bulenox 2.572, MFFU 2.612, Tradeify 2.920). Under (A2) that is a hit rate of
   Phi(2.53 / 12.2) = Phi(0.2074) = 0.582 to Phi(2.92 / 12.2) = Phi(0.2393) = 0.595.

Table 5.4b runs the payout funnel (section 3 model, M6_funnel.run, 20,000 paths, 1 contract) for S15 under each
variant. Each variant uses its own net per executed trade and its own count of executed trades a day (6 p for L; 6 for
LC and market). Columns:
- mu: net per executed trade (ticks); T: executed trades a day.
- P(DLL) and P(breach): in evaluation month 1. P(breach) funded: in funded month 1.
- P(pass 1st): pass on the first attempt. P(paid, 756 d): paid within 756 trading days.
- Days to payout: mean trading days to the first payout, among paid paths. Fees: mean fees to the first payout (USD).

| Firm | Variant (tau 1, cal) | mu | T | P(DLL) eval m1 | P(breach) eval m1 | P(breach) funded m1 | P(pass 1st) | P(paid, 756 d) | days to payout | fees (USD) |
|---|---|---|---|---|---|---|---|---|---|---|
| Topstep | (i) market | 0.527 | 6.00 | 0 (no DLL) | 0.122 | 0.106 | 0.578 | 1.000 | 111.5 | 519 |
| Topstep | (ii) TT, L | -0.254 | 4.10 | 0 | 0.162 | 0.154 | 0.136 | 0.675 | 341.5 | 1,291 |
| Topstep | (ii) TT, LC | -0.024 | 6.00 | 0 | 0.235 | 0.215 | 0.239 | 0.941 | 246.1 | 1,018 |
| Lucid | (i) market | 0.495 | 6.00 | 0.0008 | 0.128 | 0.127 | 0.554 | 0.990 | 203.4 | 450 |
| Lucid | (ii) TT on CQG [assumed], L | -0.286 | 4.10 | 0.0000 | 0.167 | 0.164 | 0.122 | 0.198 | 416.2 | 831 |
| Lucid | (ii) TT on CQG [assumed], LC | -0.056 | 6.00 | 0.0011 | 0.243 | 0.247 | 0.220 | 0.569 | 361.3 | 930 |
| Lucid | (iii) Rithmic K, L | 0.426 | 4.85 | 0.0001 | 0.099 | 0.099 | 0.508 | 0.951 | 262.0 | 479 |
| Lucid | (iii) Rithmic K, LC | 0.436 | 6.00 | 0.0008 | 0.137 | 0.139 | 0.518 | 0.979 | 222.6 | 495 |
| Lucid | (iii) Rithmic FIFO, L | 0.461 | 4.85 | 0.0001 | 0.095 | 0.094 | 0.529 | 0.963 | 251.0 | 458 |
| Lucid | (iii) Rithmic FIFO, LC | 0.464 | 6.00 | 0.0008 | 0.133 | 0.132 | 0.534 | 0.984 | 213.3 | 473 |
| Tradeify | (i) market | 0.135 | 6.00 | 0.0006 | 0.199 | 0.199 | 0.304 | 0.748 | 336.1 | 652 |
| Tradeify | (ii) TT on Tradovate, L | -0.646 | 4.10 | 0.0000 | 0.235 | 0.230 | 0.038 | 0.025 | 414.2 | 814 |
| Tradeify | (ii) TT on Tradovate, LC | -0.416 | 6.00 | 0.0008 | 0.343 | 0.339 | 0.080 | 0.118 | 410.5 | 1,026 |
| Tradeify | (iii) Rithmic K, L | 0.066 | 4.85 | 0.0000 | 0.153 | 0.154 | 0.264 | 0.579 | 371.3 | 605 |
| Tradeify | (iii) Rithmic K, LC | 0.076 | 6.00 | 0.0006 | 0.211 | 0.212 | 0.272 | 0.671 | 348.3 | 690 |
| Tradeify | (iii) Rithmic FIFO, L | 0.101 | 4.85 | 0.0000 | 0.147 | 0.148 | 0.283 | 0.622 | 364.5 | 587 |
| Tradeify | (iii) Rithmic FIFO, LC | 0.104 | 6.00 | 0.0006 | 0.206 | 0.207 | 0.288 | 0.708 | 343.4 | 673 |
| MFFU | (i) market | 0.443 | 6.00 | 0.0097 | 0.136 | 0.136 | 0.521 | 0.980 | 220.1 | 507 |
| MFFU | (ii) TT, L | -0.338 | 4.10 | 0.0011 | 0.176 | 0.168 | 0.106 | 0.161 | 417.0 | 996 |
| MFFU | (ii) TT, LC | -0.108 | 6.00 | 0.0139 | 0.256 | 0.261 | 0.195 | 0.498 | 371.2 | 1,122 |
| Bulenox | (i) market | 0.483 | 6.00 | 0 (no DLL) | 0.068 | 0.067 | 0.055 | 0.637 | 355.5 | 4,252 |
| Bulenox | (iii) K, L | 0.414 | 4.85 | 0 | 0.046 | 0.044 | 0.025 | 0.339 | 400.2 | 4,701 |
| Bulenox | (iii) K, LC | 0.424 | 6.00 | 0 | 0.075 | 0.074 | 0.049 | 0.571 | 366.3 | 4,383 |
| Bulenox | (iii) FIFO, L | 0.449 | 4.85 | 0 | 0.044 | 0.042 | 0.026 | 0.372 | 396.8 | 4,660 |
| Bulenox | (iii) FIFO, LC | 0.452 | 6.00 | 0 | 0.071 | 0.072 | 0.051 | 0.604 | 362.5 | 4,337 |

Notes on 5.4b:
1. The funnel keeps the per-trade SD at 12.2 ticks for filled trades too. This is an approximation: the SD of G
   conditional on a fill differs from the unconditional SD.
2. "Paid within 756 days" stays high even at a negative edge (Topstep (ii) L: 0.675). The funnel buys a new
   evaluation after every failure, so variance alone eventually produces a payout. The comparisons that matter are
   fees and days to the first payout and, in E.33, expected value per cycle.
3. These are my simplified simulations. Any number that enters a verdict must be recomputed by an independent
   reviewer with the program's prop_econ (E.19/E.28).
4. Hand check of one funnel input, Topstep market: m = 6 x 0.527 x 10 = 31.6 USD a day; s = sqrt(6) x 12.2 x 10 =
   298.8 USD a day. The first-attempt pass rate of 0.578 falls between the section 3.3 grid's 0.562 at mu 0.5 and
   0.810 at mu 1.0, as it should.

### 5.5 The directional decomposition, restated per variant (what section 2 derived)
- E[edge] = p_fill E[edge | fill] + (1 - p_fill) E[edge | no fill] (B3). On the standard numbers at alpha 2.0
  (section 2.3, 200,000 paths): TT, tau 1 min: 0.683 x 0.747 + 0.317 x 4.798 = 2.031. Queue, tau 1 min: 0.807 x
  1.253 + 0.193 x 5.278 = 1.011 + 1.019 = 2.030. The ordering E[G | no fill] (4.80 TT; 5.28 Q) > E[G] (2.03) >
  E[G | fill] (0.75 TT; 1.25 Q) holds under both rules, and more strongly under TT.
- Realised net per signal, limit entry: p_fill (E[edge | fill] + s/2 - Xc - F), with 0 when unfilled (B2). Market
  entry: E[edge] - s/2 - Xc - F (B1).
- Opportunity cost of unfilled limits: OC = (1 - p)(E[G | no fill] - s/2 - Xc - F) (B4). At Topstep, TT, tau 1, it
  is 0.317 x 3.270 = 1.037 ticks per signal, more than the half spread the filled limits save (p s = 0.683).
- Limit with a timeout that converts to market (chasing): the chase pays the move already missed, E[X_tau | no fill]
  > 0 (B5). When the alpha is front-loaded, chasing after 5 minutes is worth -0.098 per unfilled signal (section
  2.3).
- Marketable entry with a passive exit (B7): under TT it is identical to a market exit. Under the queue reading it is
  worth up to s/2 x P(take-profit) = 0.15 to 0.25 tick per signal, before any E.31-type markout. It applies only on
  Rithmic routes (Bulenox, Lucid-Rithmic, Tradeify-Rithmic). At Topstep, the passive take-profit is the order type
  that the "outside the best bid or offer" wording may cover.

### 5.6 What E.33 must measure on the discovery dates, per variant (no outcome computed now)
E.31's figures are unconditional per-fill figures for a spread-capture placement, not conditional on a directional
signal. For each frozen signal configuration, on the discovery dates only, E.33's fill engine replays the steps below
per signal i. The engine is the E.31 code path: mbo_book31.py rebuilds the book, kalgo31.py runs the K-algorithm, and
measure31_core.py holds the FIFO and trade-through rules. The signal time t0 and the signal's side are fixed before
any fill is simulated.
1. Variant (i): the fill price is the touch (walking the book for n lots) in the rebuilt ZM MBO book at t0 + L, for
   L in {0.3 s, 1.0 s}. L = 0 is reported only as a bound. Record delta_L = mid_{t0+L} - mid_{t0}, signed. The exit
   works the same way at H (or at the barrier trigger time plus L). Output per signal: entry and exit fill prices,
   and slippage against the touch at t0.
2. Variant (ii): a 1-lot buy (sell) limit at the bid (ask) at t0 + L. It fills when a trade prints strictly through
   the price (E.31 model c) and is cancelled at tau; each tau is a counted configuration. Output: filled or not, fill
   time, fill price; for unfilled signals, the mid at tau and at H.
3. Variant (iii): the same order under the K-algorithm and FIFO back-of-queue models (E.31 a and b), with the queue
   ahead initialised from the book strictly before t0 + L. Also report (ii) on the same signals, which is the joint
   reading of the Rithmic rule.
4. From these, per variant and firm fee:
   - p_fill = filled signals / all signals (every signal stays in the denominator);
   - E[G | fill] and E[G | no fill], with G measured mid to mid from t0 to t0 + H;
   - E[edge | fill], net of the fill price;
   - the 10 s post-fill markout of the filled signals, compared with E.31's unconditional -0.545 / -0.629 / -0.611,
     to test whether cal_v carries over;
   - the decomposition identity (B3) as a consistency check, to 1e-9 on the sample;
   - V_M, V_L, V_LC and OC per signal, with day-block bootstrap intervals (as in E.31).

   The per-variant series of net P&L per trade then replaces the normal assumption in the funnel (section 3.4).
5. Report separately the signals on report days (USDA release windows; E.31 measured -8.98 ticks per passive fill in
   the 5 minutes after a release) and the signals within H of 13:20 CT or of the 07:45-08:30 CT pause.

Execution uses fills and prices after t0 only, and never feeds back into the signal or its side. A test guards that
boundary: truncate the book at t0 - 1 ns and recompute the signal, as in section 2.5.
[MathReview D-11 (lead: accepted): the plan omits (i) the clock, (ii) the roll rule and (iii) a common comparison set (under "one position at a time" the executed set S_exec differs by variant, so per-variant p_fill and E[edge | fill] are computed on different signal subsets); add to 5.6: "features and order placement on ts_recv; matching on ts_event; roll dates per g.3 rule 5; report each variant on (a) its own replayed S_exec and (b) the common set of all signals evaluated under every variant without the state machine." Otherwise there is no look-ahead (also applies to section 2.5, original lines 282-294).]

### 5.7 Data, leakage, compute, verdict
- Data: ZM MBO (ZM.v.0, ZM.v.1) for the book, prints with aggressor side, and queue ahead; definitions for tick size
  and sessions. ZS and ZL MBP-1 are not needed for execution.
- Leakage traps, each with a test:
  - The fill variant per firm chosen after seeing which gives the best P&L. Test: the protocol lists the variant per
    firm route from table 5.3, hashed before E.33 reads labels.
  - Per-signal outcomes used to pick tau. Test: every tau in the grid is reported and counted in N.
  - The CQG and WealthCharts assumptions changed after results. Test: the frozen protocol states them as TT.
  - Signals dropped as "unfillable". Test: the row count equals the signal count per variant.
- Compute: as in section 2.6 (E.31 ran 816 dates in 384 s on 4 workers). Three variants and three taus multiply the
  fill replay by at most 7 (one market pass, plus three taus x two limit rules). That is still under an hour for 39
  months on 4 to 8 cores, with one day of MBO in memory at a time.
- Verdict:
  - USE variant (i), market entry and market exit, as the primary execution at every firm. It is the cheapest under
    the E.31 calibration everywhere (5.4a).
  - MAYBE variant (iii) on Rithmic routes (Bulenox, Lucid-Rithmic, Tradeify-Rithmic), as a measured alternative for
    the entry or the exit, priced under both K and FIFO and shown beside the TT figure (the joint reading).
  - SKIP variant (ii) limit entries as a source of improvement at TT routes (Topstep, MFFU, Tradeify-Tradovate, and
    Lucid-CQG by assumption). E.33 may still measure them for completeness under V50, with each configuration
    counted in N.
  - The lead decides what enters the protocol.

## 6. Evidence table

Firm facts were not re-fetched; the decision is logged in pages/M6_prop_strategy/log.tsv. Firm pages read on
2026-10-20/21 (E.28) are 6 to 7 days old. The E.13 pages for Apex and Take Profit Trader were read on 2026-10-03,
24 days ago and so inside the 30-day line; Apex's text, however, is a 2026-03-03 Wayback capture. Lucid, Tradeify and
Bulenox forbid automated access (E.28's decisions), and the Apex and TPT terms were unreadable or forbid it (E.13), so
those pages could not have been re-fetched by automation anyway. All paths below are relative to reports/.

| Claim | Source (label) | Verbatim quote | Saved file | Status |
|---|---|---|---|---|
| TopstepX limit orders fill on trade-through | Topstep help centre, Order types, fills and slippage, dateModified 2026-09-16 (firm) | "the market has to trade through your price — not just touch it. You might not get filled. Partial fills happen." | stage_e28_briefs/pages/A2_platforms/ts_8765442_fills.html.txt line 56 | as recorded by E.28 (fetched 2026-10-21) |
| Market orders on TopstepX | same page (firm) | "Executes at the next available price. No price specified — you get the best fill available when your order hits the exchange." | same file, line 52 | as recorded by E.28 |
| Topstep bans queue farming, tight brackets, orders outside the BBO | Topstep, Prohibited Trading Strategies, lastUpdated 2026-06-10 (firm) | "Making hundreds of rapid trades to take advantage of preferential queue position in SIM" / "Using tight brackets or auto-breakeven to take advantage of favorable SIM fills" / "Placing orders at prices outside the current best bid or offer." / "usually hundreds or thousands of trades per day, with average durations measured in seconds, not minute[s]" | stage_e28_briefs/pages/A2_topstep/ts_10305426.html.txt lines 44, 52, 55, 57 | as recorded by E.28 (fetched 2026-10-21) |
| Topstep major-news rule | same page (firm) | "Purposefully trading your full Maximum Position Size directly into a scheduled major news event." | same file, line 46 | as recorded by E.28 |
| No automation on the Topstep LFA | Topstep help 10657969 (firm) | "The API Gateway is built for the simulated environment and isn't available on Live, so automated strategies are not possible at this time in the Live Funded Account." | stage_e28_briefs/pages/A2_topstep/ts_10657969.html.txt line 135 | as recorded by E.28 |
| XFA is simulated with real payouts | Topstep help 8284215 (firm) | "The Express Funded Account® (XFA) is the simulated funded-level account you earn after passing your Trading Combine." | quoted in stage_e28_briefs/A2_firm_topstep.md line 60 (file ts_8284215.html.txt) | as recorded by E.28 |
| Rithmic paper trading fill rule | Rithmic account post on the Optimus Futures forum, 2019-01-31T11:25 UTC (forum: pointer only, quoting the vendor) | "We report a fill when the market trades through your price and when the orders ahead of you in the queue, based upon our estimate of your position in the queue and market activity, are depleted and there is quantity or opposite side order activity at your price level. This is not pessimistic. It is somewhat realistic." / "our filling algorithmic treats each account separately" | stage_e28_briefs/pages/A2_platforms/optimus_rithmic_paper_2413.json (post 3) | pointer only; not a Rithmic document |
| Tradovate sim fills | Tradovate staff on the Tradovate community forum, 2021-05-21 (forum: pointer only) | "While Tradovate tries to mirror the filling algos as close as we can, reproducing the exchange's matching algorithms with 100% accuracy in a simulation environment would be very difficult for any platform to achieve." User (2021-05-14): "It takes price breaking through my limit in order to get filled" | stage_e28_briefs/pages/A2_platforms/tv_community_2279.json (posts 11, 2) | pointer only |
| Lucid routes | Lucid help, supported platforms, updated 2026-07-28 (firm) | "CQG supported platforms: NinjaTrader / Tradovate / TradingView"; "Rithmic supported platforms: MotiveWave (Lucid Partner) / Quantower (Lucid Partner) / Tradesea / Sierra Chart / Jigsaw / Bookmap / ATAS / R\|Trader Pro (official Rithmic platform) / MultiCharts" | quoted in stage_e28_briefs/A2_firm_lucid.md lines 223-226 (file sup_platforms2.html.txt) | as recorded by E.28 |
| Lucid sim fill rule unpublished | E.28 reader (negative evidence) | "Sim fill rule for resting limit orders: not documented on any Lucid page read (rules, platforms, FAQ, TOU)." | stage_e28_briefs/A2_firm_lucid.md line 228 | negative evidence |
| Lucid microscalping | Lucid help 11404742 (firm; Wayback 2026-03-30 and 2026-10-20 captures) | "More than 50% of your profits are generated from trades held for 5 seconds or less" | stage_e28_briefs/pages/A2_lucid/sup_microscalping_wb_20260330.html.txt line 20 | as recorded by E.28 |
| Lucid automation | Lucid general FAQ (firm; Wayback 2026-07-13) | "Automated strategies and in-platform/third party trade copiers are permitted, but traders are responsible for any software errors or unintended outcomes." | quoted in stage_e28_briefs/A2_firm_lucid.md lines 179-181 (file lucid_general_faq_wb.html.txt) | as recorded by E.28 |
| Tradeify brokers | Tradeify platforms page (firm; Wayback 2026-10-13) | "Tradeify supports three broker connections: Tradovate, Rithmic, and WealthCharts. You select your broker at checkout." | quoted in stage_e28_briefs/A2_firm_tradeify.md lines 222-223 | as recorded by E.28 |
| Tradeify 10-second payout gate | Tradeify guidelines (firm; Wayback 2026-08-22) | "Over 50% of your trades are longer than 10 seconds" / "Over 50% of your profit must come from trades held longer than 10 seconds." | stage_e28_briefs/pages/A2_tradeify/tf_guidelines_wb.html.body.txt lines 26-27 | as recorded by E.28 |
| Tradeify API live-only | E.28 reader (firm pages) | "The Tradovate API is not available on evaluation or sim funded accounts; only on LIVE funded accounts." | stage_e28_briefs/A2_firm_tradeify.md line 209 | as recorded by E.28 |
| MFFU sim-fill rules | MFFU fair-play article 8444599 (firm, 2026-08-24) | "Order Placement: Simultaneously placing multiple limit orders at the same price to manipulate order fills is prohibited." / "Slippage and Bracket Usage: Exploiting the absence of slippage and utilizing tight brackets to gain from favorable fills are not permitted." / "Traders may make use of automated trading strategies tailored to their own specific settings so long as these automated tools do not aim to exploit the favorable fills offered in the Simulated Environment." | stage_e28_briefs/pages/A2_mffu/mffu_art_8444599.html.txt lines 24, 26, 18 | as recorded by E.28 |
| MFFU runs on Tradovate | E.28 reader | "Accounts are Tradovate accounts (login at trader.tradovate.com ...)" | stage_e28_briefs/A2_firm_mffu.md line 246 | as recorded by E.28 |
| Bulenox: Rithmic only; scalping algorithms banned | Bulenox terms (firm; Wayback 2026-10-19) and help (E.28) | "using “scalping” algorithms, DTC Protocol Bridge API or automated discretional trading in any of the trading environments." | stage_e28_briefs/A2_firm_bulenox.md lines 200-202 (TERMS lines 261-265) | as recorded by E.28 |
| Apex bans automation | Apex Prohibited Activities (firm; Wayback capture 2026-03-03, read by E.13 on 2026-10-03) | "No Automation or Algorithm Usage allowed:" / "Rewards are intended to recognize human traders actively participating in the learning process, not to reward automated systems executing preprogrammed logic." | stage_e13_briefs/pages/PropVenues1/apex_wb_prohibited_old.txt lines 56-57 | as recorded by E.13; capture older than 30 days |
| Take Profit Trader bans all bots | TPT Universal Trading Policies (firm; updated 2026-06-12, read by E.13 on 2026-10-03) | "#1: No Trading Bots or Algos." / "Automated trading systems, bots, or algorithmic execution tools are not permitted." | stage_e13_briefs/pages/PropVenues1/tpt_utp.txt lines 8-9 | as recorded by E.13 |
| E.31 per-fill edges by fill model | E.31 return (program) | "| 10 s edge E_10, mean | -0.287 [-0.303, -0.273] | -0.252 [-0.267, -0.239] | -0.970 [-0.988, -0.950] |" | reports/E.31_RETURN.md line 191 | program result |
| E.29 micro payout thresholds | E.29 return (program) | "whose alone break-even is inflated by payout thresholds a one-lot micro rarely clears" | reports/E.29_RETURN.md section 1, line 16 | program result |
| V50 trade-through default | docs/DECISIONS.md V50 item 2 (program) | "Any later stage prices its fills under the trade-through rule unless a firm documents otherwise." | docs/DECISIONS.md lines 1038-1041 | program decision |
| Drawdown-time and drawdown-before-target formulas | Landriault, Li and Zhang (2014), arXiv 1403.1183v1 (academic) | eq. (2.7): "P {Mτa ≥ x} = ... = e^{−γx/(e^{γa} −1)}" (typography from pdftotext, cleaned) | pages/M6_prop_strategy/arxiv_1403.1183v1.txt line 230 | verified |
| Selection bias in limit vs market order cost | Peterson and Sirri (2002), JFQA, author copy (academic) | "We attribute the difference in costs to a selection bias" | pages/M6_prop_strategy/babson_limit_orders_jfqa2002.txt line 24 | verified |
| Fill probability vs waiting for a better price | Lehalle and Mounjid (2018), arXiv 1610.00261v4 (academic) | "the probability to be filled is high but it is better to wait a little more to get a better price" | pages/M6_prop_strategy/arxiv_1610.00261v4.txt line 17 | verified |
| Penalty for unexecuted limit orders | Harris and Hasbrouck (1996), JFQA (academic) | none | none | [unverified: abstract via a search summary only] |
| Limit orders are price-contingent and adversely selected | Linnainmaa (2010), JF (academic) | none | none | [unverified: abstract via a search summary only] |

## 7. Planner pointers (reports/stage_e32_inputs/planner_research_prop_sim_fills.md): verification

| Planner pointer | Status | Evidence or reason |
|---|---|---|
| TopstepX help centre (2026-09-16): the market "has to trade through your price — not just touch it… Partial fills happen" | VERIFIED | ts_8765442_fills.html.txt line 56 (dateModified 2026-09-16T21:49:03Z), quote in section 6 |
| Combine and XFA simulated with real payouts; LFA live by call-up | PARTLY VERIFIED | XFA simulated with real payouts verified (ts_8284215 via A2_firm_topstep.md line 60). "Live by call-up only" not re-checked here [unverified] |
| API not allowed on the LFA: "automated strategies are not possible at this time in the Live Funded Account" | VERIFIED | ts_10657969.html.txt line 135 |
| Rithmic staff post on the Optimus Futures forum (2019-01-31) describing fills on trade-through and queue depletion; ambiguous whether joint or alternative; accounts simulated separately | VERIFIED as a pointer (forum post by the Rithmic account, not a Rithmic document) | optimus_rithmic_paper_2413.json post 3, 2019-01-31T11:25:18Z; the quote supports both readings, see (E3). Literally, "and" makes the conditions joint, which would be at least as strict as trade-through |
| Bulenox (Rithmic only; bots allowed if user-built), Tradeify and Lucid on their Rithmic routes | VERIFIED | A2_firm_bulenox.md line 200; A2_firm_tradeify.md lines 220-226; A2_firm_lucid.md lines 223-226 |
| Tradovate sim fill rule unpublished; staff say it "tries to mirror" exchange matching; users report trade-through-like behaviour | VERIFIED as a pointer | tv_community_2279.json posts 11 and 2 (forum). Negative evidence: no Tradovate document read states a sim fill rule |
| Tradovate used by MFFU and by the Tradovate routes at Tradeify, Take Profit Trader and Apex | PARTLY VERIFIED | MFFU and Tradeify verified (E.28). TPT lists Tradovate (tpt_platforms.txt line 22, E.13). Apex: only a page naming Tradovate for Canadian accounts (apex_wb_restricted.txt line 179); the full Apex route list is [unverified] |
| CQG sim fill rule unpublished; Lucid's CQG route uses it | PARTLY VERIFIED | The route is verified (Lucid platforms page). "Unpublished" rests on negative evidence: E.28 found no Lucid page with a fill rule, and no CQG document was read here |
| Market orders fill at the top of book in these sims; about half the spread per fill for one contract | PARTLY VERIFIED | TopstepX: "best fill available when your order hits the exchange" (line 52). No firm states a top-of-book sim rule for market orders; the half spread is E.28's convention, not a firm figure |
| Topstep bans queue farming in SIM, tight brackets and orders outside the BBO (2026-06-10); the last is ambiguous for resting limits deeper than the inside quote | VERIFIED | ts_10305426.html.txt (lastUpdated 2026-06-10T14:02:45Z), quotes in section 6. The ambiguity is real and also reaches stops and passive take-profits (5.3) |
| MFFU bans duplicate limit orders at one price and tight-bracket no-slippage farming | VERIFIED | mffu_art_8444599.html.txt lines 24, 26 |
| Lucid bans microscalping (more than 50% of profit from holds of 5 s or less) | VERIFIED | sup_microscalping_wb_20260330.html.txt line 20 (the E.31 notes had called this a secondary source; the firm page is on disk) |
| Tradeify gates funded payouts on holds over 10 s | VERIFIED | tf_guidelines_wb.html.body.txt lines 26-27: both conditions (over 50% of trades and over 50% of profit from holds over 10 s) |
| Apex bans automation entirely | VERIFIED as of a Wayback capture of 2026-03-03 | apex_wb_prohibited_old.txt lines 56-57. The capture is older than 30 days; the current terms were unreachable on 2026-10-03 (E.13), so it was not re-fetched |
| Take Profit Trader excludes automated seconds-scale systems | REFUTED as worded (the rule is broader) | tpt_utp.txt lines 8-9: "#1: No Trading Bots or Algos." covers every automated system, not only seconds-scale ones |
| A minutes-scale directional bot is outside all of these thresholds | PARTLY VERIFIED | It clears the numeric thresholds (Lucid 5 s, Tradeify 10 s) and Topstep's "seconds, not minutes" description. Apex and TPT ban bots outright, so there it is excluded whatever its horizon; Bulenox's "scalping" is undefined |
| Implication: market about -0.5; TT about -0.97 (about 0.5 worse than market); queue about -0.25 to -0.29 (0.2 to 0.25 better per fill, about 0.5 per round trip) | VERIFIED against E.31 | E.31_RETURN.md line 191. Arithmetic: 0.970 - 0.5 = 0.470; 0.5 - 0.287 = 0.213; 0.5 - 0.252 = 0.248; two legs 0.43 to 0.50 |
| These are unconditional per-fill figures; a directional strategy pays an opportunity cost on unfilled limits | VERIFIED (derivation and model) | Sections 2.2-2.3 (B3, B4) and 5.4: OC = 1.037 tick per signal at Topstep under TT, tau 1 min, in the stylised model |

## 8. Stopping rule and what was not done

- WebSearch calls in total: 2, both in the first spawn (Harris-Hasbrouck and Linnainmaa full texts; nothing free
  found). The re-spawn made no web calls. Every firm fact and planner pointer was checked against pages already saved
  by E.13, E.28 and E.31, which lie inside the 30-day line, except the Apex capture.
- Topics (a), (b) and (e) rest on three full-text academic sources plus derivations checked numerically. No new
  sources were sought on the firm topics, because the firm pages themselves are the evidence.
- Not done: no firm page re-fetched (all within 30 days, or barred by terms); Topstep's LFA "call-up" rule not
  re-checked; the CQG and WealthCharts fill rules are unknown (assumed TT, labelled); the funnel in sections 3 and 5
  is my simplification and not the program's prop_econ.
