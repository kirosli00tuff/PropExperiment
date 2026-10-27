
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
