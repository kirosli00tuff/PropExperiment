# Stage E.32 methods brief: short-horizon directional signals in the soybean complex (ZM)

Lead synthesis (Opus 5.5 xhigh), 2026-10-27. Parts R and M below are the reader files as corrected by the lead's
rulings on the MathReviewer findings (Part V); each correction is a bracketed "[MathReview X-n ...]" note at the
place it applies. The protocol these findings feed is reports/stage_e32_discovery_protocol.md (frozen, sha256 in
reports/E.32_RETURN.md). Nothing here was computed from market data: no feature, label, return or markout exists.

## Front (one page)

The question (stage prompt, Parts R and M): how professional firms build, test and retire short-horizon directional
strategies, and which mathematics and machine learning a minutes-scale directional search on CBOT soybean meal (ZM)
needs, given ZM's costs, 39 months of owned discovery data and one sealed test window.

What the readers found:
1. The published evidence is thin and mostly negative at the horizons that can pay ZM's costs. No commodity-futures
   study shows positive out-of-sample directional predictability net of costs at 1-240 minutes; CBOT soybean meal's
   first-half-hour momentum is null over 1982-2020 (Baltussen et al., slope -0.95, t -1.58, OOS R2 negative); order-
   flow predictability fades within about 30 minutes; the best minutes-scale out-of-sample results anywhere are
   equity-index R2 of 1-3% at one daily slot (R4 5.3, R5 A and E, M1 a).
2. Costs set the floor. A market round trip costs about one spread plus the fee (Topstep 0.528 ticks, up to Tradeify
   0.920); E.28's break-even is 1.59 ticks (0.528 + a 1.0-tick default spread + 0.062 account economics; M3 e.2,
   MathReview B confirmed). Limit entries are not cheaper once E.31's measured adverse markout is counted: a
   trade-through limit needs about 0.79 tick more gross move, a queue-model limit 0.03-0.07 more (M6 5). Labels
   must be executable: mid-price labels are about 1 tick a round trip too optimistic (M3 e).
3. Statistics set a higher bar still. At N = 838 (538 + a 300-configuration search) the deflated Sharpe on 796
   discovery dates needs a daily Sharpe of 0.172 (t 4.86); a candidate needs about 0.20 (t 5.7) to have even odds
   at the one-shot test, about 1.2 ticks net per 15-minute trade at 4 trades a day or 0.5 per 5-minute trade at 8
   (protocol P7; M5a d, M5b c). As a correlation, a 15-minute forecast traded 4 times a day needs an out-of-sample
   rho of about 0.13 for 1.2 ticks net (R5 E table), above every value published for commodity futures.
4. The structure that works at minutes is cross-asset: the board crush C = 11 ZL + 2.2 ZM - ZS is cointegrated in
   most day sessions (Zhou et al.: 180 of 243 at 1-minute sampling), though ZM must close about 70% of a 1-cent
   dislocation to pay costs and the literature's prior is that ZM is not the adjusting leg (M2, R3a). Seconds-scale
   lead-lag cannot pay at retail latency (M2 b). Order flow is a conditioner, not a standalone forecast (M1).
   Event families (USDA, NOPA: about 49 and 39 days in 39 months) and once-a-day families fail on power (R4 2.4,
   M5b c, R3a 8.2).
5. Methods: regularised logistic regression first, shallow gradient-boosted trees second, no deep order-book models
   (2-34 weights per independent label at the horizons that can pay; M4 c); purged, embargoed, session-aligned
   folds (M5a a); the deflated Sharpe at the literal N, with Holm at the test (M5a d, f); PBO reported, not gated
   (its null band on 39 months is 0.13-0.83; M5a e); stability and power gates (M5b b, c); executable labels with a
   cost-defined dead zone (M3 f).
6. Practice at professional firms (R1, R2): ideas screened for being sensible, predictive, consistent and additive;
   a small declared number of variants; an ancillary non-return test; trial ledgers; kill rules after a pass.
   Merchants' hedging flows are private and not timed intraday; HFT firms' edge in soybeans is spread capture,
   which V50 closed for this program.
7. Data: ZM MBO exists only from 2017-05-21 (Databento GLBX.MDP3 page, saved by Part F), so the testable window is
   2017-05-22..2020-11-30 (890 trade dates), not 2017-05-01. The discovery and test windows straddle the renewable-
   diesel change in the oil share, the 2020 liquidity collapse and the 2021-2022 position-limit change (R3a 2,
   R3b c-d).

What the protocol takes from this: four families (crush-residual reversion; ZS/ZL propagation at minutes; ZM order
flow and book state; ZM's own path), each alone with a context block and all pooled, 6 executable labels (5, 15,
30, 60 minutes; triple barrier at 15 and 30), 2 model families, 300 configurations, mechanical selection of at most
3 finalists.

Honest odds (lead judgement, not a measurement): the probability that E.33 produces a finalist is about 5% (a real
edge of the needed size would be the first published or found at these horizons in a commodity future; R5's reader
put 0.8 ticks net at no better than one in ten, and the selection threshold asks for more); the protocol's
false-positive rate is far below that (P4.2). If a finalist exists, the regime differences make a pass at the test
perhaps 50-70% likely. Overall about 3% (range 1-6%) that the program ends this route with a passing candidate.

## Verdict table (topic, verdict, role in the protocol, reason)

| Topic | Verdict | Role in P | Reason (source) |
|---|---|---|---|
| Best-level OFI, ZM and ZS/ZL, lagged 1-15 min | maybe | features F3.1-F3.3, F2.8-F2.11 | forward R2 small; cross-asset lags the one positive forward finding (M1 a) |
| Integrated multi-level OFI | maybe (integrated only) | F3.4, equal weights | gains are mostly contemporaneous (M1 a) |
| Deep order-flow models | skip | none | effective horizon about two price changes, about 12 s in ZM (M1 a) |
| Trade-sign imbalance | conditioner | F3.5-F3.6 | sign persistence is priced by asymmetric liquidity (M1 b) |
| Kyle's lambda | conditioner | F3.12 | contemporaneous by construction (M1 c) |
| Microprice | skip as signal | none (labels use executable prices) | martingale, within 0.5 tick in a 1-tick book (M1 d) |
| Cancellation, replenishment, icebergs | maybe | F3.9-F3.11 | documented contemporaneously; impact transient (M1 e, f) |
| VPIN | skip | none | unsigned; no incremental power after controls (M1 g) |
| Drift-burst aftermath | use | F4.11-F4.12 | ZC reversal b = -0.20; event timing must avoid look-ahead (M1 9) |
| Hayashi-Yoshida, HRY lead-lag | feature only | minute look-backs F2 | seconds lead cannot pay 1.59 ticks at 300-1,000 ms (M2 a, b) |
| Crush VECM/OU residual, half-life, leg | use | F1; VECM loadings as a diagnostic | the only minutes-scale cross-asset structure (M2 c-f, R3a) |
| Clock bars, CUSUM, volume bars | 1-minute clock grid | P3 decision grid | simplest purging, clock-based rules (M3 a) |
| Fixed-horizon executable labels | use | FH05-FH60 | maps one-to-one to the trade (M3 b, e) |
| Triple barrier, kappa sigma sqrt(h) | maybe (one kappa) | TB15, TB30 | exit realism; no evidence of predictive gain (M3 b) |
| Meta-labeling | maybe; not used | none | no signed base rule exists to meta-label (M3 c, V28) |
| Uniqueness weights | use | P3.7 | overlapping labels carry 1/h of their row count (M3 d) |
| Cost-aware target, dead zone | use | P3.3-P3.5 | dead zone = spread + costs, not a tuned threshold (M3 f) |
| Exclusions (open, close, releases, rolls, limits) | use | P3.6 | release reactions last 30-40 minutes (M3 g, R4, R2) |
| Regularised logistic | use (primary) | LOGIT | parameter-to-sample ratio <= 0.03 at 15-60 min (M4 a, e) |
| LightGBM depth <= 3 | maybe (secondary) | LGBM | interactions; needs calibration and early-stopping discipline (M4 b) |
| Sequence models | skip | none | data size (M4 c) |
| Online / regime-switching | maybe; not used | reversed walk-forward diagnostic | keeps the grid small and the CV analogue exact (M4 d) |
| Purged, embargoed K-fold | use | 6 blocks, 21-date embargo | session-aligned folds make purging free (M5a a) |
| CPCV | maybe; not used | none | finalists only; adds no selection power here (M5a b) |
| Walk-forward | diagnostic | reversed walk-forward (P6.5) | rehearses the backward test (M5a c) |
| DSR at N | use | G3 at discovery; test bar | the program's bar; literal N (M5a d, MathReview C) |
| PBO (CSCV) | report | P6.3 | null band 0.13-0.83 on 39 months (M5a e) |
| Holm / BH / BY / Romano-Wolf / SPA | Holm at the test; others reference | P7.2 | at most 3 finalists, one test (M5a f) |
| Feature importance | report only | P6.5 | must never steer a choice in the same data (M5b a) |
| Stability (quarters, month dominance, volatility terciles) | use | G5 | costs about 1-4 points of power (M5b b) |
| Power at the test | use as a gate | G4 | a fail in an underpowered window is uninformative (M5b c, R1) |
| Probability to entries and exits | use | P3.5, P3.8 | EV rule net of costs (M6 1) |
| Market versus limit | market default; limits reported | P6.4 variants | limits lose once adverse markout counts (M6 2, 5) |
| Firm rules (DLL, drawdown, payouts, news) | report | P6.4 prop simulator | filters usability, not edge (M6 3, 4) |
| Post-USDA drift, NOPA days, overnight handoff, late-session momentum | dropped as families | exclusions, flags, features | power (R4 2.4, R3a 8.2, M5b c) |
