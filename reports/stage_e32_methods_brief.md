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

## Contents

- Front and verdict table (above)
- Part R: R1-R5
- Part M: M1-M6
- Part V: verification, the lead's rulings and the fixes

# Part R. How professionals build short-horizon directional strategies

## R1. Alpha research process at proprietary firms and systematic funds

Source file: reports/stage_e32_briefs/R1_alpha_process.md (sha256 c8169f0fb7deaa251674a570562f3d59f46c4c5b2d04a9b73f2dd9d781ff6a1c).

### R1: The alpha research process at proprietary trading firms and systematic funds (Stage E.32, Part R1)

Worker: AlphaProcess-OpusHigh (opus, high). Re-spawned 2026-10-27 02:34 PDT after a usage-limit cut at 00:51 PDT
(the first spawn fetched 17 pages and wrote no output; its pages and log were reused, nothing was refetched).
Pages and log: reports/stage_e32_briefs/pages/R1_alpha_process/ (log.tsv: URL, UTC and PDT fetch time, method,
sha256, file, note). Helper scripts: reports/stage_e32_briefs/work/R1_alpha_process/.

Scope. This extends E.28 2.11 (reports/stage_e28_methods_brief.md lines 11557-12146, "How top firms run the
research process"), which already covers: the Man AHL Academic Advisory Board write-up (written data partition,
rejection funnel, 2-3 month test trading on firm capital, heat maps, regime-versus-overfit rule), Harvey-Liu (2015)
Sharpe haircuts, Harvey-Liu-Zhu t > 3, Arnott-Harvey-Markowitz's backtesting protocol, CFM's overfitting discount
and execution-cost practice, Jensen-Kelly-Pedersen, AQR's cost model, Two Sigma, Optiver, HRT, XTX, Virtu,
Citadel Securities, Jane Street, Jump. None of that is repeated here; it is cited as "E.28 2.11 (E-number)".
Statistical machinery that other E.32 workers own (DSR, PBO/CSCV, MinTRL, power, purging) is cited to them
(M5a, M5b) and not re-derived.

Labels. Every source is labelled: academic, practitioner (a book, paper or talk by someone working at a trading
firm or fund, or a firm publication), professional body, or pointer (not evidence). Quotes are verbatim from saved
full text; the evidence table (section 8) gives the file for each R1-E number.

Status: sections 1-9 written in order; see section 9 for gaps.

---

#### 1. Sources read in full text for this part

| Source | Label | File |
|---|---|---|
| Lopez de Prado (2018), "The 10 Reasons Most Machine Learning Funds Fail" (GARP copy; the paper version of AFML ch. 1 themes) | practitioner (then at Guggenheim/AQR, LBNL) | ldp_2018_10reasons_garp.pdf |
| Lopez de Prado (2017), "The 7 Reasons Most Machine Learning Funds Fail", slides (SSRN 3031282 copy on smallake.kr) | practitioner | ldp_2017_7reasons_slides.pdf |
| Bailey and Lopez de Prado (2015), "Stop-outs under serial correlation and the triple penance rule", Journal of Risk (eScholarship copy) | academic / practitioner | bailey_ldp_triple_penance.pdf |
| Kahn (2018), "The Future of Investment Management", CFA Institute Research Foundation (Kahn: head of systematic equity research, BlackRock; Grinold-Kahn co-author) | practitioner | kahn_2018_future_invest_mgmt.pdf |
| Michaud and Michaud (2005), "The Fundamental Law of Mismanagement", New Frontier Advisors newsletter | practitioner (critique) | newfrontier_eqopt4_fl.pdf |
| Polakow and Gebbie (2006), "How many independent bets are there?", arXiv physics/0601166 | academic / practitioner | arxiv_physics0601166.pdf |
| Isichenko (2021), "Costly Trading", arXiv 2110.15239 (author of "Quantitative Portfolio Management", Wiley 2021) | practitioner | isichenko_2021_costly_trading.pdf |
| Kakushadze and Tulchinsky (2015), "Performance v. Turnover: A Story by 4,000 Alphas" (Tulchinsky: WorldQuant founder) | practitioner | kakushadze_tulchinsky_2015_turnover.pdf |
| Kakushadze (2016), "101 Formulaic Alphas" (WorldQuant alphas) | practitioner | kakushadze_2016_101alphas.pdf |
| Chan (2011), "Backtesting" talk slides, CMT Association | practitioner | chan_cmt_backtesting_slides.pdf |
| Chan, "Quantitative Trading" 2nd ed. (2021), Wiley reading sample (front matter only) | practitioner | chan_qt2e_reading_sample.pdf |
| Narang, "Inside the Black Box" 3rd ed. (2024), Wiley reading sample (front matter and ch. 1 only) | practitioner | narang_3e_reading_sample.pdf |
| Falck, Rej and Thesmar (2021), "Why and how systematic strategies decay", arXiv 2105.01380 (CFM) | practitioner / academic | falck_rej_thesmar_2021_decay.pdf |
| Volpati, Benzaquen, Eisler, Mastromatteo, Toth, Bouchaud (2020), "Zooming In on Equity Factor Crowding", arXiv 2001.04185 (CFM) | practitioner / academic | volpati_etal_2020_crowding.pdf |
| McLean and Pontiff (2016), "Does Academic Research Destroy Stock Return Predictability?", JF (author-hosted copy) | academic | mclean_pontiff_2016.pdf |
| Di Mascio, Lines and Naik (2017), "Alpha Decay" (SSRN 2580551 copy) | academic (practitioner data) | dimascio_lines_naik_alpha_decay.pdf |
| Frazzini, Israel and Moskowitz (2012), "Trading Costs of Asset Pricing Anomalies", NBER conference draft (AQR) | practitioner / academic | frazzini_israel_moskowitz_2012_costs.pdf |
| Garleanu and Pedersen (2013), "Dynamic Trading with Predictable Returns and Transaction Costs", JF (author copy; Pedersen at AQR) | academic | garleanu_pedersen_dynamic_trading.pdf |
| Harvey and Liu (2014), "Evaluating Trading Strategies", JPM (author-hosted copy) | academic | harvey_liu_evaluating_trading.pdf |
| AgonAlpha (2026), arXiv 2608.11250 (reports WorldQuant BRAIN's submission checks) | academic (secondary on a firm's criteria) | agonalpha_2026_brain_checks.pdf |

Not obtained in full text (so cited only as [unverified] or not at all): Isichenko's book; Lopez de Prado's
"Advances in Financial Machine Learning" (AFML; the chapter 1 excerpt URL was not archived, see section 9) and
"Machine Learning for Asset Managers"; Grinold (1989) and Grinold-Kahn "Active Portfolio Management" (the
fundamental law is quoted from Kahn 2018 instead); Narang ch. 9 "Research" (only its table of contents is in the
sample); Chan's ch. 3 paper-trading method (only the preface mention is in the sample); Kissell's books; Tulchinsky
"Finding Alphas". See section 9.

---

#### 2. (a) How ideas are generated, screened, ranked and killed

##### 2.1 Facts

1. Research is organised as a production line, not as lone researchers searching. Lopez de Prado: "Every
   successful quantitative firm I am aware of applies the meta-strategy paradigm ... Tasks of the assembly line are
   clearly divided into subtasks. Quality is independently measured and monitored for each subtask" (R1-E1). The
   failure mode he names is the "Sisyphus paradigm": "each PhD will frantically search for investment opportunities
   and eventually settle for (1) a false positive that looks great in an overfit backtest or (2) standard factor
   investing" (R1-E2). Practitioner.
2. The backtest is a final check, not the search tool. "Research through backtesting" is pitfall 2: "It does not
   matter if the backtest is a walk-forward out-of-sample. The fact that we are repeating a test over and over on
   the same data will likely lead to a false discovery" (R1-E3), and "feature importance is a research tool, and
   backtesting is not" (R1-E4). His solution: explain predictive power by feature importance inside cross-validation
   first, then ask whether the important features are stable across regimes and related instruments (R1-E4).
   Practitioner.
3. An explicit screen before any data are touched (BlackRock systematic equity). Kahn: judge every idea on whether
   it is "sensible, predictive, consistent, and additive" (SPCA). "The sensibility criterion forces us to consider
   why an idea might work -- and, relatedly, why the market doesn't already understand it -- before testing it
   empirically" (R1-E5). The criterion can be relaxed for "higher-frequency phenomena, such as short-horizon trading
   signals" because the data are larger (R1-E5). "The additivity criterion judges whether this is a new idea or an
   old idea disguised as new" (R1-E6). "Ancillary testing" (a non-return test of the mechanism the idea claims, for
   example whether an earnings signal predicts earnings surprise) gives "a second statistical test of the signal's
   efficacy" and "an early indication if the signal stops working" (R1-E7). Practitioner.
4. Kahn quantifies what the screen buys with Ioannidis's positive predictive value (PPV), the fraction of
   backtest "passes" that add value out of sample (R1-E8, R1-E9; equations in 2.2). His Exhibit 4.13: scattershot
   data mining with 20 tests gives PPV about 10%; sensibility about 47%; SPCA with ancillary testing about 75%
   (R1-E9). Kahn says the inputs "are just rough estimates" (R1-E9). Practitioner.
5. Ranking and killing by screens on turnover, Sharpe, correlation to existing alphas. WorldQuant's platform runs
   named submission checks; a 2026 paper that submitted alphas reports that its alphas "passed BRAIN's Fitness,
   Sharpe, turnover, weight-concentration, sub-universe, self-correlation, and competition-matching" checks
   (R1-E10). The numeric thresholds (Sharpe 1.25, fitness 1, turnover 1-70%, self-correlation 0.7) appear only in
   community GitHub tools and search snippets: [unverified], pointers only. A sub-universe check (does the alpha
   still work on a subset of the universe) and a self-correlation check (is it a near-duplicate of an existing alpha)
   are the transferable ideas. Practitioner, secondary.
6. Chan's pre-backtest filter (practitioner talk): don't backtest a strategy with a "Low Sharpe ratio (<1) and long
   drawdown duration" because "high average returns may be due to a fluke (overfitting)"; for a 48-minute holding
   period E-mini strategy, ask first "Has the author included transaction costs?" and "can the strategy be readily
   implemented using limit orders instead of market orders?", because "High frequency strategies are very sensitive
   to transaction costs assumptions" (R1-E11). His rules against data snooping: build on "well-researched
   financial/economic principles"; "Rule-of-thumb: every additional parameter to be optimized requires an extra year
   of daily data"; and a look-ahead test: "truncate later part of historical data and re-run backtest program to see
   if positions just before truncation remain unchanged" (R1-E12). Practitioner.
7. Complexity predicts decay. CFM's study of 72 published anomalies finds "the number of operations required to
   calculate the signal and two measures of sensitivity of in-sample Sharpe to outliers together add another 15% of
   explanatory power" for out-of-sample Sharpe decay (R1-E13). The outlier measure drops "the 0.1% observations that
   are most impactful" and recomputes the in-sample Sharpe (R1-E14). Practitioner/academic. This is a screen any
   single researcher can run.
8. The industrial version of idea generation (WorldQuant, practitioner): automation yields "an ever increasing
   number of alphas, whose count can be in hundreds of thousands and even millions", each "faint and ephemeral",
   and the firm trades a combined "mega-alpha" with "automatic internal crossing of trades (and thereby crucial-for-
   profitability savings on trading costs, etc.)" (R1-E44). The working definition quoted from Tulchinsky et al.
   (2015): "An alpha is a combination of mathematical expressions, computer source code, and configuration
   parameters that can be used, in combination with historical data, to make predictions" (R1-E44). The 101 published
   alphas have holding periods of "0.6-6.4 days" and "average pair-wise correlation ... 15.9%" (R1-E45). The model
   depends on thousands of weak, weakly correlated signals netted inside one book; a one-contract program has no
   internal crossing and cannot use it.
9. Narang's third edition structures research as "9.1 Blueprint for Research: The Scientific Method", "9.2 Idea
   Generation", "9.3 Testing" (table of contents only, R1-E15); the chapter text was not in the sample, so nothing
   from it is used [unverified beyond the TOC].

##### 2.2 Equations (Kahn 2018, Technical Appendix)

PPV with no bias and one test (Kahn eq. 4.36):

    PPV = R_pn (1 - f_fn) / ( R_pn (1 - f_fn) + f_fp )

PPV with bias b and N tests of variants (Kahn eq. 4.37, read from the rendered page because the PDF text layer
loses the brackets):

    PPV = R_pn {1 - [(1 - b) f_fn]^N} / ( R_pn {1 - [(1 - b) f_fn]^N} + 1 - [(1 - b)(1 - f_fp)]^N )

Symbols: R_pn, the ex ante ratio of truly positive to truly negative ideas ("fish in barrels or needles in
haystacks"); f_fp, the false-positive fraction from noise (the test size); f_fn, the false-negative fraction (one
minus power); b, the fraction of negative results reported as positive through bias; N, the number of variants
tested per idea, a positive declared if any variant passes (R1-E8, R1-E9).

Recomputation of Exhibit 4.13 with eq. 4.37 (this worker's arithmetic, script output):
- Scattershot: f_fp 0.05, f_fn 0.01, b 0.1, N 20, R_pn 0.1. (1-b) f_fn = 0.009; 0.009^20 ~ 0; numerator
  0.1 x 1 = 0.1. (1-b)(1-f_fp) = 0.855; 0.855^20 = 0.0436; 1 - 0.0436 = 0.9564. PPV = 0.1 / (0.1 + 0.9564) = 0.095.
  Kahn prints 10%. Check: matches to rounding.
- No SPCA: 0.05, 0.05, 0.2, 10, 0.15 gives 0.138 (Kahn 14%). Sensibility: 0.05, 0.05, 0.2, 3, 0.5 gives 0.471
  (Kahn 47%). SPCA with ancillary tests: 0.01, 0.05, 0.05, 3, 0.5 gives 0.748 (Kahn 75%).

What the PPV frame says about the program (worker's reading, not a source claim): N in eq. 4.37 is the per-idea
variant count, and it enters as a power. Holding R_pn, f_fp and b fixed, every extra variant tried raises the
false-positive term 1 - [(1-b)(1-f_fp)]^N. E.33's protection is the same as Kahn's: a small number of declared
variants per mechanism (N small), a mechanism stated first (R_pn up), one frozen test (b near 0), and a non-return
ancillary test. The program's own cumulative N (538) is a family-wise count across ideas, which the DSR handles
(M5a); the PPV is a per-idea complement, not a replacement.

##### 2.3 What this means for a ZM directional search

- Use: Kahn's "sensible" gate written as a short mechanism statement per signal family (who is on the other side,
  why the price does not already reflect it, at what horizon it should decay), before any data are read; Kahn
  relaxes this for short horizons (R1-E5), but E.33 has 39 months of one contract, which is not the "plenty of
  data, high signal-to-noise" case he exempts. Keep it.
- Use: an ancillary, non-return test per family where one exists (for example, an order-flow family should first
  predict the sign of the next trade or the next mid change, before it is asked to predict a 15-minute return net
  of cost). This is a second test of the same mechanism and an early decay monitor (R1-E7).
- Use: an additivity check against families already screened in the program (the 64-feature library and earlier
  rules): a new ZM signal that is a re-expression of a failed one adds to N and nothing else.
- Use: CFM's outlier screen (drop the most impactful 0.1% of returns, recompute; R1-E14) and a complexity count
  (number of operations per feature; R1-E13) as reported diagnostics in discovery.
- Use: Chan's truncation test for look-ahead (R1-E12), run on the feature pipeline (positions or signals before a
  truncation point must not change when later data are removed).
- Drop: WorldQuant-style thresholds (Sharpe 1.25, turnover bands): unverified, built for a cross-section of
  thousands of equities, and not calibrated to one futures contract.

---

#### 3. (b) Research-to-production pipelines

##### 3.1 Facts

1. Stages named by practitioners: backtest, then paper or test trading, then live at small size, then scale. E.28
   2.11 has Man AHL's version (test trading on firm capital, 2-3 months, a mistake-catcher, not a significance test;
   E.28 E7-E8) and Virtu's lockdown rules (E.28 E49-E50). New here:
2. Chan (practitioner): the second edition adds "a mathematically rigorous way to decide how much backtest data and
   how long a paper trading period is needed" and a technique for "how data snooping will affect your live Sharpe
   ratio" (R1-E16). The method itself is in ch. 3, which was not in the sample [content unverified]; the program's
   equivalent is MinTRL (M5b, BLdP 2012 eq. 13), which gives the same kind of answer from the claimed Sharpe.
3. Chan's look-ahead remark doubles as a pipeline rule: "Look-ahead bias will also be detected when you build an
   automated trading system for the strategy" (R1-E12): the live code path is a test of the research code path.
4. Kill rules for a live strategy (Bailey and Lopez de Prado, practitioner/academic): a stop-out at a fixed loss
   "allows preventable problems to grow until it is too late"; instead "For any drawdown, large or small, determine
   the expected time underwater and monitor every recovery. Even if a loss is small, a failure to recover within the
   expected timeframe indicates a latent problem" (R1-E17). The triple penance rule: "On average, the recovery spans
   three times the period involved in accumulating the maximum quantile loss for a given confidence level" (R1-E18).
   Their decision rule: "Should ITuW > TuW_alpha, the strategy or PM will be stopped-out, regardless of the actual
   [loss]" (R1-E19). Ignoring serial correlation "leads to a gross underestimation of the downside potential ... by
   as much as 70%" (R1-E18).
5. The production view of costs (Isichenko, practitioner): "It generally takes a large database of orders and
   executions to run a statistically meaningful trading cost analysis" (R1-E20). Matches CFM and AQR in E.28 2.11
   (E70, E85): the cost model in production is fitted on own fills.

##### 3.2 Equations (Bailey and Lopez de Prado 2015, IID normal P&L per bet, mean mu > 0, s.d. sigma)

    MaxQL_alpha = (Z_alpha sigma)^2 / (4 mu)          (their eq. 5; maximum quantile loss)
    t*_alpha    = (Z_alpha sigma / (2 mu))^2          (their eq. 6; the bet count at which it occurs)
    TuW_alpha   = (Z_alpha sigma / mu)^2              (their eq. 7; quantile time under water)
    ITuW        = pi^2/(mu^2 t) - 2 pi/mu + t         (their eq. 8; implied time under water after a realised loss
                                                      pi < 0 at bet t)

TuW_alpha = 4 t*_alpha, so the recovery after the bottom takes 3 t*_alpha: the "triple penance". Their section 9
(Proposition 4) generalises to AR(1) P&L; not reproduced here.

Check against the paper's own section 7 example (worker's recomputation): PM1 makes 10m USD a year with an annual
s.d. of 10m USD, monthly bets, so mu = 10/12 = 0.8333m and sigma = 10/sqrt(12) = 2.8868m per month; Z = 1.6449.
MaxQL = (1.6449 x 2.8868)^2 / (4 x 0.8333) = (4.7484)^2 / 3.3333 = 22.547 / 3.3333 = 6.764m USD (paper:
"US$6,763,858.64"). TuW = (4.7484 / 0.8333)^2 = 32.47 months = 2.706 years (paper: "2.706 years"). ITuW for a
5m USD loss after 24 months: 25/(0.6944 x 24) + 10/0.8333 + 24 = 1.500 + 12.000 + 24 = 37.5 months = 3.125 years
(paper: "3.125 years"). All three match.

##### 3.3 Worked example on the standard ZM numbers (worker's arithmetic; random-walk scaling assumed)

Assume a 15-minute directional ZM strategy, one contract, day session only, that trades every non-overlapping
15-minute bar (the case built in section 6.3): net mean mu = 0.357 ticks per bet and sigma = 12.20 ticks per bet
(sigma_15 = 3.15 x sqrt(15) = 3.15 x 3.873 = 12.20 ticks). Take 95% confidence, Z = 1.645.
- MaxQL = (1.645 x 12.20)^2 / (4 x 0.357) = (20.07)^2 / 1.428 = 402.8 / 1.428 = 282 ticks = 282 x 10.00 USD =
  2,820 USD on one lot.
- t* = (1.645 x 12.20 / (2 x 0.357))^2 = (20.07 / 0.714)^2 = (28.11)^2 = 790 bets. At 290/15 = 19.33 bets a day,
  790 / 19.33 = 40.9 trading days to the 95% quantile bottom.
- TuW = 4 x 790 = 3,160 bets = 163.5 trading days before the 95% quantile path is back to zero.
- Check: 3,160 - 790 = 2,370 = 3 x 790 (the triple penance identity).
- Reading: a strategy whose annualised net Sharpe is about 2.0 (section 6.3) can, at the 95%
  quantile, lose 282 ticks over about two months and need about eight months to recover. A 2-3 month paper or
  shadow window (Man AHL, E.28 E8) can catch a broken implementation; it cannot confirm a small edge. The ITuW rule
  (R1-E19) gives a kill rule that does not wait for the loss limit.

##### 3.4 What this means for a ZM directional search

- Use (for the period after any pass; the lead's call): a pre-declared kill rule in time-under-water terms (TuW at
  the declared confidence, from the Sharpe claimed at the test), alongside the prop account's hard loss limits.
- Use: one code path from feature computation to order (Chan R1-E12; E.28 2.11 Optiver and Jump practice).
- Note for E.33 itself: E.33 is discovery plus one sealed test; paper or shadow trading is outside it under V43 and
  the 2026-10-18 record (E.28 2.11 table 3.2). Nothing here changes that.

---

#### 4. (c) How the multiple-testing problem is handled in practice

##### 4.1 Facts

1. Count the trials, or no correction is possible. Lopez de Prado: "it is imperative to control for the number of
   trials (I) in the context of WF backtesting. Without this information, it is not possible to determine the
   Family-Wise Error Rate (FWER), False Discovery Rate (FDR), Probability of Backtest Overfitting (PBO) or similar"
   (R1-E21). Lopez de Prado and Lewis (AQR, Guggenheim) call the number of trials and the variance of their Sharpe
   ratios "meta-research variables ... intrinsic to the research process itself" that "cannot be estimated from the
   selected strategy", and add that "it is common for researchers to hide, not track, not report or underreport"
   them; and that "even those careful and knowledgeable researchers who track every single trial ... face the
   problem that trials are not usually independent" (R1-E22). Their remedy clusters the trials' return series
   (ONC) and uses the cluster count as the effective number of independent trials K <= N (R1-E22). The program
   already counts N; ONC and the DSR are M5a's topic and are not re-derived here.
2. The same logic applied to people. The 2017 slides apply multiple-testing reasoning to hiring and oversight:
   replace "Interview candidates with SR ... above a given threshold" by a process that "recognizes the variables
   that affect the probability of making the wrong hire: False positive rate. False negative rate. Skill-to-unskilled
   odds ratio. Number of independent trials. Sampling mechanism" (R1-E23). This is the PPV frame of section 2 in
   another form. Practitioner.
3. The arithmetic of coincidence, as BlackRock teaches it. Kahn: "given 20 informationless strategies, the
   probability of finding at least 1 with a t-statistic of 2 is 64%" (R1-E24). Check (worker): 1 - 0.95^20 = 0.642
   with a 5% test per strategy; with the exact two-sided |t| >= 2 (p = 0.0455 under normality) it is
   1 - 0.9545^20 = 0.606. Kahn's 64% is the 5%-level figure.
4. Hold-out practice. Kahn: "Out-of-sample testing requires us to hold out part of our historical data. We test and
   fit the signal on the in-sample data and then run a final test with the out-of-sample data. The held-out sample
   might be the most recent historical period, but it could also be a subset of the assets" (R1-E25). Cross-
   validation is used alongside (R1-E25). Practitioner.
5. The hold-out has a power cost (Harvey and Liu 2014, academic): "often the OOS period is not really
   out-of-sample because the researcher knows what has happened in that period"; with fewer in-sample observations
   "we might not have enough power to identify true strategies"; and "with only 60 monthly observations in the OOS
   period, a true strategy will have a good chance to fail the OOS test" (R1-E26). Their example strategy has an
   insignificant five-year OOS Sharpe (p = 0.53) while being borderline significant on the full sample (R1-E26).
6. Size of the in-sample to out-of-sample gap, measured on published signals (academic and CFM): McLean and
   Pontiff, 97 predictors: "Portfolio returns are 26% lower out-of-sample and 58% lower post-publication. The
   out-of-sample decline is an upper bound estimate of data mining effects" (R1-E27). CFM (72 anomalies): Sharpe
   "declines by about one half after the results are published", and "Every year, the Sharpe decay of newly-published
   factors increases by 5ppt" (R1-E28). These are monthly equity anomalies; they bound, not measure, what to expect
   from a ZM minutes-scale search.
7. Sequential practice after the test (staged capital and kill rules): Man AHL's test trading (E.28 E7-E8) and the
   time-under-water stop-out rule (section 3, R1-E17 to R1-E19). The public record contains no firm's numeric FDR
   level, hold-out length or staged-capital schedule (E.28 2.11 section 6 found the same; this pass found nothing
   new on it).
8. The largest public test of backtest-to-live decay on one platform (Quantopian, practitioner; 888 algorithms with
   at least 6 months out of sample): "commonly reported backtest evaluation metrics like the Sharpe ratio offer little
   value in predicting out of sample performance (R^2 < 0.025)"; and "the more backtesting a quant has done for a
   strategy, the larger the discrepancy between backtest and out-of-sample performance" (R1-E42). In the body: IS
   Sharpe correlated with OOS Sharpe at "Pearson R^2=0.02"; the log of total backtest days correlated with the
   Sharpe shortfall (IS minus OOS) at "Spearman R^2=0.017" (p < 0.0001); and "using only the last backtest year to
   compute IS Sharpe ratio increased predictability of OOS Sharpe ratio suggesting a recency effect (Pearson
   R^2=0.05)" (R1-E43). Equity algorithms, daily to intraday, mostly retail authors; the direction of the effects,
   not their size, is what transfers.

##### 4.2 What this means for a ZM directional search

- Use: a trial ledger that records every configuration run in discovery, including failed and aborted runs, with
  its return series saved, so that N, the variance of trial Sharpe ratios, and an ONC-style effective K can be
  computed (R1-E21, R1-E22). The program counts N already; saving every trial's out-of-fold return series is the
  addition that lets K and E[V[SR_k]] be estimated rather than assumed.
- Use: a power statement for the sealed test window before E.33 starts (Harvey-Liu's point, R1-E26): the sealed
  window 2017-05-01..2020-11-30 is 43 months; M5b holds the arithmetic. If the window cannot detect the Sharpe the
  discovery CV implies, a fail there is uninformative and the protocol should say so in advance.
- Use: a declared expected decay from discovery to test, written before the test is opened (E.28 E10 band; McLean-
  Pontiff's 26% as an "upper bound" of mining on published anomalies, R1-E27), so that a test Sharpe inside the band
  is a pass of the consistency check and one far below it is a fail.
- Do not: treat the 26%/50%/58% decay figures as a ZM haircut. They come from monthly equity anomalies after
  publication; a private search has no publication effect, and its mining effect depends on its own N (M5a).

---

#### 5. (d) Signal decay and capacity

##### 5.1 Facts on decay

1. Decay of a forecast inside a live process (Kahn, practitioner): in equilibrium "Old information decays as new
   information arrives ... the information turnover rate, gamma, captures both the decay rate of old information and
   the arrival rate of new information" (R1-E29), with

       alpha_n(t) = exp(-gamma dt) alpha_n(t - dt) + s_n(t)            (Kahn eq. 4.21)
       BR = gamma N                                                    (Kahn eq. 4.22)

   alpha_n(t), the forecast for asset n at time t; s_n(t), the new information arriving; gamma, the information
   turnover rate (per year); N, the number of assets; BR, breadth in independent bets per year. Kahn: "if we run a
   cross-sectional regression of alpha(t) against alpha(t - dt), we can estimate exp(-gamma dt) as a regression
   coefficient" (R1-E29). For one asset the regression is a time-series one.
2. Faster signals earn less per trade. WorldQuant's 4,000 live alphas (holding periods 0.7-19 days): "We find a
   simple scaling C ~ 1/T, where C is cents-per-share, and T is the portfolio turnover. Thus, the portfolio return R
   has no statistically significant dependence on the turnover" (R1-E30; the symbols are lost in the PDF text layer
   and are restored from the body, eq. 1). "Shorter-horizon quantitative traders generally are well-aware of the
   simple rule-of-thumb: the higher the turnover, the lower the CPS" (R1-E30). Their figures are "before trading
   costs" (R1-E31). Practitioner. Implication: profit per trade shrinks in proportion to trading frequency while the
   per-trade cost does not, so a faster version of the same idea needs a proportionally lower cost to survive.
3. Decay after discovery, with mining and crowding as causes (sections 4.1 items 6 and CFM R1-E13). CFM's crowding
   study: "the rebalancing of a Momentum portfolio can explain between 1-2% of order flow, and that this percentage
   has been significantly increasing in recent years" (R1-E32). Equity factor crowding, monthly; relevant only as
   evidence that crowding leaves an imprint in order flow.
4. A measured alpha half-life (academic, institutional data): professional managers' new buys earn alpha that
   "resembles a power or exponential function with a half-life of about four months" (R1-E33). Long-only equity;
   context only.
5. How decay should change trading (academic, AQR co-author): "predictors with slower mean-reversion (alpha decay)
   get more weight in the aim portfolio. An investor facing transaction costs should trade more aggressively on
   persistent signals than on fast mean-reverting signals: the benefits from the former accrue over longer periods,
   and are therefore larger" (R1-E34). Their costs are quadratic (market impact); a 1-lot ZM trader's costs are
   linear (fee plus spread), for which Isichenko's no-trade-zone result applies (section 6, R1-E37).
6. Man AHL on very fast effects (E.28 E72, not repeated): non-linear fast structure is "too fast" for client-scale
   alpha but useful in execution.

##### 5.2 Facts on capacity

1. Capacity is set by costs (AQR, practitioner/academic): from AQR's live execution data, "short-term reversal
   strategies, on the other hand, do not survive transactions costs at sizes greater than $9 billion in the U.S."
   against 52-103 billion USD for size, value and momentum (R1-E35). The fastest style has the least capacity.
2. For this program capacity in the institutional sense is not binding: one ZM contract against a median front-
   contract ADV of 36,690 (A0 Table 1) is 1/36,690 = 0.0027% of daily volume. The binding limits are the prop
   account's position and loss rules and the queue position of a 1-lot (E.31: a resting 1-lot at the ZM touch earned
   a gross -0.970 ticks per fill at 10 s under the trade-through rule; reports/E.31_RETURN.md section 3.5).

##### 5.3 Worked example: half-life and breadth of a minutes-scale ZM signal (worker's arithmetic)

Suppose discovery shows that a 1-minute ZM signal has a lag-1 time-series regression coefficient of 0.8 (an
illustrative value, not a measurement).
- exp(-gamma x 1 min) = 0.8, so gamma = -ln(0.8) / 1 min = 0.2231 per minute.
- Half-life = ln 2 / gamma = 0.6931 / 0.2231 = 3.11 minutes.
- Day-session minutes per year: 290 min (08:30-13:20 CT) x 252 days = 73,080 min. gamma per year =
  0.2231 x 73,080 = 16,307. With N = 1 asset, Kahn eq. 4.22 gives BR = 16,307 "independent bets" a year.
- Check: a signal with a 15-minute half-life would have gamma = 0.6931/15 = 0.04621 per minute and BR = 0.04621 x
  73,080 = 3,377; breadth scales with 1/half-life, as eq. 4.22 says.
- Reading: the fundamental law rewards fast decay with breadth, but each "bet" then carries only the edge available
  over a few minutes (Kakushadze-Tulchinsky's C ~ 1/T, R1-E30), against a fixed 0.528-tick fee and, for market
  orders, about 1.59 ticks of total break-even cost (E.28 ranking row 6, topstep ZM, mu*_mkt = 1.59). Breadth is a
  ceiling on what a signal can deliver before costs; section 6 puts the cost back.

##### 5.4 What this means for a ZM directional search

- Use: measure each candidate signal's decay in discovery (the IC at horizons 1, 5, 15, 60 minutes and the
  signal's own autocorrelation) and report its half-life; prefer, at equal CV score, the more persistent signal,
  because it spreads one round-trip cost over more expected move (Garleanu-Pedersen R1-E34; Isichenko R1-E37).
- Use: an ancillary decay monitor (Kahn R1-E7): the IC-by-horizon profile frozen at discovery is the reference a
  later live record is compared against.
- Do not: estimate capacity; it is irrelevant at one lot. Do record queue and fill limits, which are the real
  constraint (E.31, V50).

---

#### 6. (e) How desks decide that a small edge is worth running

##### 6.1 Facts

1. The fundamental law (Grinold 1989, extended by Clarke, de Silva and Thorley 2002), as stated by Kahn
   (practitioner): IR = IC . sqrt(BR) . TC (Kahn eq. 4.20; the radical is lost in the PDF text layer and was read
   from the rendered page). "Breadth -- really breadth of skill -- measures the number of independent bets the
   manager takes per year at an average skill level of IC ... it is a rate, not a number. It's not the number of
   assets in the portfolio" (R1-E36). TC, the transfer coefficient, is the correlation between the paper portfolio
   and the portfolio actually held after constraints and costs (R1-E36).
2. Typical magnitudes (Kahn, citing Grinold and Kahn 2000 and Barra/BlackRock research): a top-quartile manager has
   IR 0.5 before expenses; IC "Average 0.00, Good 0.05, Great 0.10"; "even a great information coefficient is only
   0.1", which "corresponds to correctly forecasting the sign of the residual return about 53% of the time"
   (R1-E38). His sign relation (eq. 4.19, normal errors): f_r = 1/2 + (1/pi) arctan(IC / sqrt(1 - IC^2)), about
   1/2 + IC/pi for small IC (R1-E38). Check: IC 0.10 gives 0.5 + arcsin(0.10)/pi = 0.5 + 0.1002/3.1416 = 0.5319
   (Kahn: 53.2%).
3. The casino case: with 100,000 bets "IR = 5.2% / 0.32% = 16 = IC . sqrt(BR)" and "breadth works to reduce the
   variance of outcomes ... It doesn't alter the expected return" (R1-E39). Check: 5.2/0.32 = 16.25; 16/sqrt(100,000)
   = 16/316.2 = IC of 0.051.
4. The critique (Michaud, practitioner): the law "ignores uncertainty in information and practical constraints";
   its two assumptions that fail in practice are "1) Information level and breadth are independent. 2)
   Unconstrained MV optimization is a useful asset management framework" (R1-E40); and for equity models "breadth is
   unlikely to be much greater than five whatever the size of the optimization universe" (R1-E40). Polakow and
   Gebbie estimate breadth statistically, as the count of covariance eigenvalues >= 1 (Kaiser-Guttman), and find it
   low in a concentrated market (R1-E41). For one contract the same point holds in time: successive minute bets on
   ZM are not independent when volatility clusters and signals overlap.
5. Forecast against cost (Isichenko, practitioner): "An efficient market can be defined as one in which tradable
   predictability of security prices is balanced by trading costs. Such a balance is typical for mid-frequency
   statistical arbitrage where the forecasts and the costs are of the same order of magnitude. It is then the subtle
   difference between the forecast performance and the cost of trading, which separates success from failure"
   (R1-E37). With slippage (linear) cost c, optimal trading has a no-trade zone, and a position is opened only if
   "the forecast at an infinite horizon exceeds this cost: f_inf > 2c, otherwise such tangent does not exist and it
   is best not to trade" (R1-E37; 2c is "the slippage cost of a roundtrip trade").
6. Cost of research (Lopez de Prado, practitioner): "Even if 5 of those PhDs identified a true discovery, the
   profits would not suffice to cover for the expenses of 50" (R1-E2); "It takes almost as much effort to produce one
   true investment strategy as to produce a hundred" (R1-E1). For a one-person program the analogue of salary is
   trial count: every configuration raises the DSR bar (M5a).
7. A practitioner's quick filter (Chan): skip strategies with Sharpe below 1 and long drawdowns; for short holding
   periods, check costs and limit-order feasibility first (R1-E11).

##### 6.2 Equations for a one-contract directional strategy (worker's derivation; assumptions stated)

Assume the forecast z (standardised) and the h-minute return r (ticks) are jointly normal with correlation rho (the
time-series IC), r having s.d. sigma_h. A sign strategy (long if z > 0, short if z < 0) earns per bet

    E[sign(z) r] = rho . sigma_h . sqrt(2/pi)

and a threshold strategy that trades only when |z| > k earns per trade

    E[r | z > k] = rho . sigma_h . phi(k) / (1 - Phi(k)),   traded on a fraction 2(1 - Phi(k)) of bars,

with phi and Phi the standard normal density and CDF (the inverse Mills ratio; standard bivariate-normal result).
Break-even with a round-trip cost c (ticks):

    rho*_sign = c / (sigma_h sqrt(2/pi)),      rho*_k = c / (sigma_h . phi(k)/(1 - Phi(k))).

Per-bet Sharpe s = (gross - c)/sigma_h (s.d. of a bet approximated by sigma_h for small rho); annual Sharpe
= s . sqrt(B), B the number of independent bets per year (the fundamental-law step, valid only if bets are
independent: Michaud's caveat, R1-E40).

##### 6.3 Worked example on the standard ZM numbers

Inputs: sigma_1m = 3.15 ticks (A0 Table 1); random-walk scaling sigma_h = 3.15 sqrt(h) (an assumption); market-
order round-trip break-even c = 1.59 ticks at Topstep (reports/stage_e28_ranking.md row 6, topstep ZM,
mu*_mkt = 1.59; it includes the 0.528-tick fee); day session 290 minutes.

Step 1, horizon volatility: sigma_5 = 3.15 x 2.236 = 7.04 ticks; sigma_15 = 3.15 x 3.873 = 12.20 ticks; sigma_60 =
3.15 x 7.746 = 24.40 ticks.

Step 2, break-even IC for a sign strategy (sqrt(2/pi) = 0.7979):
- 5 min: 1.59 / (7.04 x 0.7979) = 1.59 / 5.62 = 0.283 (sign hit rate 0.5 + arcsin(0.283)/pi = 59.1%).
- 15 min: 1.59 / (12.20 x 0.7979) = 1.59 / 9.73 = 0.163 (hit rate 55.2%).
- 60 min: 1.59 / (24.40 x 0.7979) = 1.59 / 19.47 = 0.082 (hit rate 52.6%).
Against Kahn's "great" IC of 0.10 (monthly equity residuals), a 5-minute market-order ZM strategy needs nearly three
times a "great" IC just to break even, a 15-minute one 1.6 times, and a 60-minute one 0.8 times.

Step 3, trading only on strong forecasts (15 min): inverse Mills ratio at k = 1.5 is phi(1.5)/(1 - Phi(1.5)) =
0.1295 / 0.0668 = 1.939; rho* = 1.59 / (12.20 x 1.939) = 1.59 / 23.65 = 0.067, trading on 2 x 0.0668 = 13.4% of
bars. At k = 2.0: 2.373 ratio, rho* = 0.055, on 4.6% of bars. This is Isichenko's no-trade zone in its simplest
form: only forecasts that exceed the round-trip cost are traded (R1-E37).

Step 4, annual Sharpe for an always-in 15-minute sign strategy: B = (290/15) x 252 = 19.33 x 252 = 4,872 bets.
- rho = 0.10: gross = 0.10 x 9.73 = 0.973 ticks; net = 0.973 - 1.59 = -0.617 ticks; per-bet s = -0.617/12.20 =
  -0.0506; annual = -0.0506 x sqrt(4,872) = -0.0506 x 69.80 = -3.53. A "great" IC loses money.
- rho = 0.20: gross 1.947, net 0.357 ticks; s = 0.0293; annual = 0.0293 x 69.80 = 2.04. (This is the strategy used
  in the section 3.3 time-under-water example.)
- Check: the net edge of 0.357 ticks per bet is 3.57 USD per round trip on a 10 USD tick; at 19.33 bets a day the
  expected profit is 69 USD a day, with a per-day s.d. of 12.20 x sqrt(19.33) = 53.6 ticks = 536 USD. The daily
  Sharpe 69/536 = 0.129 times sqrt(252) = 2.04 agrees.

Reading (worker's): (i) at minutes scale on ZM, costs are of the same order as the forecastable move, as Isichenko
says of mid-frequency stat arb (R1-E37); the edge must be defined net of the 1.59-tick (market) or the measured
passive cost from the start, never gross; (ii) a small net edge per trade gives a large annual Sharpe on paper only
because of the sqrt(B) step, which assumes independent bets; overlapping labels, volatility clustering and
regime dependence cut the effective B (Michaud, Polakow-Gebbie R1-E40, R1-E41); (iii) a threshold rule trades less
often at a lower break-even IC, so the declared feature-to-trade mapping should include the threshold as a frozen
parameter counted in N, not tuned after the test.

##### 6.4 What this means for a ZM directional search

- Use: state every candidate's required IC at its horizon from the frozen cost (step 2 above) before discovery, so
  that a CV result can be read against a known break-even rather than against zero.
- Use: report, for every candidate, gross IC, hit rate, net edge per trade in ticks, trades per year and the
  annualised net Sharpe, side by side; a desk's decision variable is net edge per trade times trade count, not IC.
- Use: an effective-bets adjustment when converting per-trade Sharpe to annual Sharpe (count non-overlapping
  bets; M5a/M5b own the autocorrelation correction).
- Do not: use the fundamental law to justify trading every bar because breadth is "free": breadth multiplies the
  net edge, and a negative net edge times sqrt(B) is a larger loss (step 4, rho = 0.10).

---

#### 7. Practices for the E.33 protocol: adopt, and do not adopt

This is a worker's list for the lead. It sets no thresholds, selection rules or verdicts. Each item names the
source. Items already in force in the program (frozen pipeline, sealed window, N counting, DSR/PBO/Holm, purged CV,
one test) are not restated.

##### 7.1 Adopt

| # | Practice | Source | Why it fits E.33 | How E.33 would carry it |
|---|---|---|---|---|
| A1 | A written mechanism statement per signal family before any data are read: who loses to the trade, why the price does not already reflect it, the horizon at which it should decay | Kahn's "sensible" criterion (R1-E5); E.28 2.11 AHM "research motivation" | Raises R_pn in Kahn's PPV; Kahn exempts short horizons only where data are plentiful and signal-to-noise high, which 39 months of one contract is not | One paragraph per family in the frozen protocol; a family with no mechanism is not run |
| A2 | A small, declared number of variants per family | Kahn eq. 4.37 (N enters as a power; R1-E9); Quantopian (more backtesting, bigger shortfall; R1-E42, R1-E43) | Directly lowers the per-idea false-positive term | The grid per family is declared and counted in N; no unplanned variants |
| A3 | An ancillary, non-return test per family (for order flow: the sign of the next trade or mid change; for a cross-asset lead from ZS/ZL: the sign of ZM's next mid change after a ZS/ZL move) | Kahn (R1-E7) | A second test of the same mechanism, and an early decay monitor | Reported beside the return test in discovery; frozen with the pipeline |
| A4 | An additivity check against the program's earlier families and the 64-feature library | Kahn "additive" (R1-E6); WorldQuant self-correlation check (R1-E10, criteria unverified) | Avoids re-running a failed idea under a new name, which adds to N and nothing else | Correlation of each new feature with the old library reported in discovery |
| A5 | A trial ledger that saves every configuration's out-of-fold return series, failed and aborted runs included | Lopez de Prado (R1-E21); Lopez de Prado and Lewis (R1-E22) | Lets K (effective trials) and the variance of trial Sharpe ratios be estimated, not assumed, for the DSR | Ledger file per run, hashed; M5a owns the estimator |
| A6 | A backtest-count log (how many full-sample evaluations were run on discovery data) | Quantopian (log backtest days predicts shortfall; R1-E43) | A process metric that flags over-iteration even inside the declared grid | One counter in the ledger |
| A7 | Required IC and net edge per trade stated per horizon from the frozen cost before discovery | Isichenko f_inf > 2c (R1-E37); fundamental law (R1-E36); worked example 6.3 | Reads a CV result against break-even, not against zero; a 5-minute market-order ZM signal needs IC about 0.28 at 1.59 ticks of cost, a 60-minute one about 0.08 | A table in the protocol, recomputed by the reviewer |
| A8 | Report net edge per trade (ticks), trade count, hit rate, gross IC and annualised net Sharpe side by side | Kakushadze-Tulchinsky CPS (R1-E30); Kahn (R1-E38) | The desk's decision variable is net edge times trade count; CPS falls with turnover | Fixed reporting table |
| A9 | A trade threshold (no-trade zone) as a frozen, counted parameter | Isichenko (R1-E37); worked example 6.3 step 3 | Lowers the break-even IC at the price of fewer trades; tuning it after the test would be a second test | Declared values only, in N |
| A10 | Decay profile per signal (IC at 1, 5, 15, 60 minutes; signal autocorrelation; half-life) | Kahn eq. 4.21-4.22 (R1-E29); Garleanu-Pedersen (R1-E34) | Persistent signals spread one round-trip cost over more expected move; the profile is the live-decay reference | Reported per candidate; at equal CV score the more persistent one is preferred only if that preference is declared in advance |
| A11 | Robustness diagnostics: drop the most impactful 0.1% of returns and recompute; count operations per feature | CFM (R1-E13, R1-E14) | Both predicted out-of-sample decay in CFM's data | Reported, not used to select unless declared |
| A12 | A look-ahead truncation test on the feature pipeline | Chan (R1-E12) | Cheap; catches the most common silent bug | Unit test: features before time t unchanged when data after t are removed |
| A13 | A power statement for the sealed window, and a declared expected discovery-to-test decay band, both before the test | Harvey-Liu (R1-E26); McLean-Pontiff (R1-E27); E.28 E10 | A fail in an underpowered window is uninformative; a band makes the test a consistency check | M5b computes power; the band is the lead's declaration |
| A14 | For after a pass only (the lead's call): a time-under-water kill rule (ITuW > TuW_alpha) alongside the prop loss limits | Bailey and Lopez de Prado (R1-E17 to R1-E19); worked example 3.3 | Kills a broken strategy before the loss limit and does not kill a sound one on a normal drawdown | Declared with the claimed Sharpe before any live trading |

##### 7.2 Do not adopt, with reasons

| # | Practice | Source | Reason |
|---|---|---|---|
| N1 | Trading a combined "mega-alpha" of thousands of weak signals with internal crossing | WorldQuant (R1-E44) | One contract has no cross-section to net across; costs are paid on every trade |
| N2 | Platform thresholds such as Sharpe > 1.25, turnover 1-70%, self-correlation < 0.7 | WorldQuant BRAIN, via community tools | Unverified (no official page read); calibrated to daily cross-sectional equity alphas |
| N3 | Using the fundamental law's sqrt(BR) to justify trading every bar | Grinold-Kahn via Kahn (R1-E36); Michaud (R1-E40) | Breadth multiplies the net edge; at a negative net edge it multiplies the loss (6.3 step 4); minute bets on one contract are not independent |
| N4 | Applying the 26-58% post-publication decay as the ZM haircut | McLean-Pontiff (R1-E27); CFM (R1-E28) | Monthly equity anomalies after publication; no publication effect here; the mining effect is set by the program's own N (M5a) |
| N5 | Relaxing the "sensible" criterion because the horizon is short | Kahn (R1-E5) | Kahn's exemption assumes plentiful data and high signal-to-noise; one contract over 39 months does not qualify, and the program's history (N = 538, no pass) argues for priors |
| N6 | Paper or shadow trading inside E.33 as a significance test | Man AHL (E.28 E8); worked example 3.3 | 2-3 months cannot confirm a Sharpe-2 edge (95% quantile drawdown lasts about 41 trading days and recovery about 123 more); it is a mistake-catcher after a pass, outside E.33 under V43 |
| N7 | Capacity estimation | AQR (R1-E35) | Irrelevant at one lot (0.0027% of ADV); queue position and fills (V50, E.31) are the binding limits |
| N8 | Fixed-loss stop-outs alone as the live kill rule | Lopez de Prado slides (R1-E17) | "allows preventable problems to grow until it is too late"; pair with the time-under-water rule |
| N9 | Selecting on backtest Sharpe alone | Quantopian (R1-E42) | IS Sharpe explained R^2 = 0.02 of OOS Sharpe in 888 algorithms |
| N10 | Feature-importance-led open exploration across many instruments (Lopez de Prado's research-tool use of MDI/MDA) | Lopez de Prado (R1-E4) | As a search tool it is itself a selection step that must be counted; in E.33 importance is a reported diagnostic on the frozen model, not a way to choose the next variant |

---

#### 8. Evidence table

All files are under reports/stage_e32_briefs/pages/R1_alpha_process/ (raw page or PDF; ".txt" is pdftotext
-layout output; ".raw.txt" is pdftotext without -layout, made for two-column papers). Quotes are verbatim except
where the note says a symbol was restored or an ellipsis used.

| ID | Claim | Source (label) | Verbatim quote | File |
|---|---|---|---|---|
| R1-E1 | Successful quant firms run research as a production line | Lopez de Prado 2018 (practitioner) | "Every successful quantitative firm I am aware of applies the meta-strategy paradigm (López de Prado [2014]). Tasks of the assembly line are clearly divided into subtasks. Quality is independently measured and monitored for each subtask." Also: "It takes almost as much effort to produce one true investment strategy as to produce a hundred" | ldp_2018_10reasons_garp.pdf(.txt) lines 126-138 |
| R1-E2 | Lone-researcher model ends in overfit false positives or crowded factors; research cost | same | "each PhD will frantically search for investment opportunities and eventually settle for (1) a false positive that looks great in an overfit backtest or (2) standard factor investing"; "Even if 5 of those PhDs identified a true discovery, the profits would not suffice to cover for the expenses of 50" | same, lines 117-124 |
| R1-E3 | Repeated backtests on the same data produce false discoveries, walk-forward included | same | "It does not matter if the backtest is a walk-forward out-of-sample. The fact that we are repeating a test over and over on the same data will likely lead to a false discovery." | same, pitfall 2 |
| R1-E4 | Feature importance, not backtesting, is the research tool | same | "This is a much better way of researching strategies than the foolish backtest cycle. Remember, feature importance is a research tool, and backtesting is not." | same, lines 182-184 |
| R1-E5 | BlackRock's SPCA screen; sensibility first; relaxed for short horizons | Kahn 2018 (practitioner) | "one should judge any new investment idea on the basis of whether it is •• sensible, •• predictive, •• consistent, and •• additive." "The sensibility criterion forces us to consider why an idea might work—and, relatedly, why the market doesn't already understand it—before testing it empirically." "There are even areas of investing where we can relax the sensibility criterion: notably, higher-frequency phenomena, such as short-horizon trading signals." | kahn_2018_future_invest_mgmt.pdf(.txt) lines 3034-3053 |
| R1-E6 | Additivity: new idea or old idea disguised | same | "The additivity criterion judges whether this is a new idea or an old idea disguised as new." (the text layer breaks "addi-tivity" across a line) | same, lines 3059-3061 |
| R1-E7 | Ancillary non-return tests | same | "This ancillary test provides a second statistical test of the signal's efficacy, increasing our statistical confidence in the result. Going forward, it can provide an early indication if the signal stops working." | same |
| R1-E8 | PPV definition (Ioannidis) and eq. 4.36 | same | "This measure is the positive predictive value (PPV), and it depends on all the variables introduced above." Eq. 4.36: "PPV = R pn ⋅ (1 − f fn ) / R pn ⋅ (1 − f fn ) + f fp" (text layer) | same, lines 3145-3147, 3466 |
| R1-E9 | PPV with bias and N tests; Exhibit 4.13 values | same | Eq. 4.37 read from rendered page 87 (printed p. 72; text layer garbled). "We start with scattershot data mining ... and run about 20 tests looking for the best results. The PPV is about 10%. In my estimation, adding sensibility boosts the PPV to just under 50%. The full approach ... raises the PPV to 75%. Although many of the inputs to the analysis are just rough estimates" | same, lines 3184-3201; page image work/R1_alpha_process/R1_kahn-087.png |
| R1-E10 | WorldQuant BRAIN runs named submission checks | AgonAlpha 2026 (academic, secondary) | "All five passed BRAIN's Fitness, Sharpe, turnover, weight-concentration, sub-universe, self-correlation, and competition-matching" | agonalpha_2026_brain_checks.pdf.txt lines 576-577 |
| R1-E11 | Chan's pre-backtest filters | Chan 2011 talk (practitioner) | "Low Sharpe ratio (<1) and long drawdown duration indicates performance is not consistent: high average returns may be due to a fluke (overfitting)." "Has the author included transaction costs? ◦ can the strategy be readily implemented using limit orders instead of market orders?" "High frequency strategies are very sensitive to transaction costs assumptions." | chan_cmt_backtesting_slides.pdf.txt |
| R1-E12 | Chan's anti-snooping rules and truncation test | same | "Build models that are based on some well- researched financial/economic principles"; "Rule-of-thumb: every additional parameter to be optimized requires an extra year of daily data."; "truncate later part of historical data and re-run backtest program to see if positions just before truncation remain unchanged."; "Look-ahead bias will also be detected when you build an automated trading system for the strategy." | same |
| R1-E13 | Complexity and outlier sensitivity predict decay | Falck, Rej, Thesmar 2021 (CFM; practitioner/academic) | "the number of operations required to calculate the signal and two measures of sensitivity of in-sample Sharpe to outliers together add another 15% of explanatory power." | falck_rej_thesmar_2021_decay.pdf.txt abstract |
| R1-E14 | Outlier measure | same | "We define a new version of factors, which uses all of the in-sample observations, save for the 0.1% observations that are most impactful." | same, lines 837-839 |
| R1-E15 | Narang ch. 9 structure | Narang 2024 sample (practitioner) | "9.1 Blueprint for Research: The Scientific Method 161 / 9.2 Idea Generation 163 / 9.3 Testing 166" | narang_3e_reading_sample.pdf.txt lines 154-158 |
| R1-E16 | Chan 2e adds a paper-trading length method | Chan 2021 sample (practitioner) | "I discuss a mathematically rigorous way to decide how much backtest data and how long a paper trading period is needed. Another mathematical technique was referenced that determines how data snooping will affect your live Sharpe ratio." | chan_qt2e_reading_sample.pdf.txt lines 409-413 |
| R1-E17 | Stop-out by time under water, not fixed loss | Lopez de Prado 2017 slides (practitioner) | "Stop-out a PM once a certain loss limit has been exceeded ... Cons: It allows preventable problems to grow until it is too late." "For any drawdown, large or small, determine the expected time underwater and monitor every recovery. Even if a loss is small, a failure to recover within the expected timeframe indicates a latent problem." (table cells interleaved in the text layer; reassembled) | ldp_2017_7reasons_slides.pdf.txt lines 142-148 |
| R1-E18 | Triple penance rule; serial correlation understates downside | Bailey and Lopez de Prado 2015 (academic/practitioner) | "On average, the recovery spans three times the period involved in accumulating the maximum quantile loss for a given confidence level." "ignoring the effect of serial correlation leads to a gross underestimation of the downside potential of hedge fund strategies, by as much as 70%." | bailey_ldp_triple_penance.pdf.txt lines 86-97 |
| R1-E19 | Stop-out decision rule; eqs. 5-8 | same | "Should 𝐼𝑇𝑢𝑊̃𝜋𝑡 > 𝑇𝑢𝑊𝛼 , the strategy or PM will be stopped-out, regardless of the actual 𝜋̃𝑡 , because the cost of opportunity (lost performance fee) is just too high for the firm." Eqs. 5-8 at lines 313-356 | same, lines 441-443 |
| R1-E20 | Cost analysis needs many own executions | Isichenko 2021 (practitioner) | "It generally takes a large database of orders and executions to run a statistically meaningful trading cost analysis [1]." | isichenko_2021_costly_trading.pdf.txt line 34-35 |
| R1-E21 | Number of trials is required for any correction | Lopez de Prado 2018 | "That is the reason why it is imperative to control for the number of trials (I) in the context of WF backtesting. Without this information, it is not possible to determine the Family-Wise Error Rate (FWER), False Discovery Rate (FDR), Probability of Backtest Overfitting (PBO) or similar." | ldp_2018_10reasons_garp.pdf.txt lines 633-636 |
| R1-E22 | Trials are hidden or dependent; ONC estimates effective K | Lopez de Prado and Lewis 2019 (practitioner/academic) | "(5)-(6) are meta-research variables, in the sense that they are intrinsic to the research process itself, and they cannot be estimated from the selected strategy." "it is common for researchers to hide, not track, not report or underreport (5)-(6)." "even those careful and knowledgeable researchers who track every single trial that takes place face the problem that trials are not usually independent." | ldp_lewis_2019_false_strategies.pdf.txt lines 395-406 |
| R1-E23 | Multiple-testing logic applied to hiring | Lopez de Prado 2017 slides | "Design an interview process that recognizes the variables that affect the probability of making the wrong hire: False positive rate. False negative rate. Skill-to-unskilled odds ratio. Number of independent trials. Sampling mechanism." (table cells reassembled) | ldp_2017_7reasons_slides.pdf.txt lines 125-132 |
| R1-E24 | 20 informationless strategies: 64% chance of one t = 2 | Kahn 2018 | "given 20 informationless strategies, the probability of finding at least 1 with a t-sta-tistic of 2 is 64%." (hyphenation from the line break) | kahn_2018_future_invest_mgmt.pdf.txt line ~3025 |
| R1-E25 | Hold-out and CV practice at BlackRock | same | "Out-of-sample testing requires us to hold out part of our historical data. We test and fit the signal on the in-sample data and then run a final test with the out-of-sample data. The held-out sample might be the most recent historical period, but it could also be a subset of the assets." | same |
| R1-E26 | OOS tests lose power and are not truly out of sample | Harvey and Liu 2014 (academic) | "First, often the OOS period is not really out-of-sample because the researcher knows what has happened in that period." "The problem is that with only 60 monthly observations in the OOS period, a true strategy will have a good chance to fail the OOS test." | harvey_liu_evaluating_trading.raw.txt lines 545-570 |
| R1-E27 | OOS 26% and post-publication 58% declines | McLean and Pontiff 2016 (academic) | "Portfolio returns are 26% lower out-of-sample and 58% lower post-publication. The out-of-sample decline is an upper bound estimate of data mining effects." | mclean_pontiff_2016.pdf.txt abstract |
| R1-E28 | Sharpe halves after publication; +5ppt decay per year | Falck, Rej, Thesmar 2021 | "we first replicate this observation and find, in line with existing studies, that the Sharpe ratio of these strategies declines by about one half after the results are published." "Every year, the Sharpe decay of newly-published factors increases by 5ppt." | falck_rej_thesmar_2021_decay.pdf.txt abstract and intro |
| R1-E29 | Information decay and breadth, eqs. 4.21-4.22 | Kahn 2018 | "Old information decays as new information arrives. In equilibrium, the two are in balance, and so the information turnover rate, g, captures both the decay rate of old information and the arrival rate of new information." ("g" is gamma in the rendered page.) "if we run a cross-sectional regression of α (t ) against α (t − ∆t ), we can estimate e − γ ⋅∆t as a regression coefficient." | same, lines 2561-2592; page image R1_kahn-066.png |
| R1-E30 | Cents-per-share scales as 1/turnover | Kakushadze and Tulchinsky 2015 (practitioner) | "We find a simple scaling  ~ 1 / , where  is cents-per-share, and  is the portfolio turnover. Thus, the portfolio return  has no statistically significant dependence on the turnover ." (symbols C, T, R lost in the text layer; restored from the body's eq. 1 and the sentence "CPS (cents-per-share) scales inversely with the turnover"); "Shorter-horizon quantitative traders generally are well-aware of the simple “rule-of-thumb”: the higher the turnover , the lower the CPS ." | kakushadze_tulchinsky_2015_turnover.pdf.txt lines 18-20, 63-66, 292-293 |
| R1-E31 | Figures are before costs, live, no survivorship | same | "All alphas are real-life trading alphas and the performance figures are out-of-sample by definition. There is no survivorship bias in our dataset. The Sharpe ratio and CPS are computed before trading costs" | same, lines 144-146 |
| R1-E32 | Crowding imprint in order flow | Volpati et al. 2020 (CFM) | "We show that the rebalancing of a Momentum portfolio can explain between 1–2% of order flow, and that this percentage has been significantly increasing in recent years." | volpati_etal_2020_crowding.pdf.txt abstract |
| R1-E33 | Institutional alpha half-life about four months | Di Mascio, Lines, Naik 2017 (academic) | "The shape of the decay resembles a power or exponential function with a half-life of about four months." | dimascio_lines_naik_alpha_decay.pdf.txt lines 73-74 |
| R1-E34 | Trade persistent signals harder than fast-decaying ones | Garleanu and Pedersen 2013 (academic) | "We show that it is in fact a general principle that predictors with slower mean-reversion (alpha decay) get more weight in the aim portfolio. An investor facing transaction costs should trade more aggressively on persistent signals than on fast mean-reverting signals" | garleanu_pedersen_dynamic_trading.pdf; gp.raw.txt lines 178-181 |
| R1-E35 | Short-term reversal has the least capacity | Frazzini, Israel, Moskowitz 2012 (AQR) | "Short-term reversal strategies, on the other hand, do not survive transactions costs at sizes greater than $9 billion in the U.S. or $13 billion globally." | frazzini_israel_moskowitz_2012_costs.pdf.txt lines 93-94 |
| R1-E36 | Fundamental law with transfer coefficient; breadth is a rate | Kahn 2018 | Eq. 4.20 "IR = IC ⋅ √BR ⋅ TC" (radical read from rendered page 66, printed p. 51; the text layer shows "IR = IC ⋅ BR ⋅ TC"). "Breadth—really breadth of skill—measures the number of independent bets the manager takes per year at an average skill level of IC." "As the number of independent bets per year, it is a rate, not a number. It's not the number of assets in the portfolio." | same, lines 2533-2560; R1_kahn-066.png |
| R1-E37 | Forecasts and costs of the same order; trade only if forecast exceeds round-trip cost | Isichenko 2021 (practitioner) | "An efficient market can be defined as one in which tradable predictability of security prices is balanced by trading costs. Such a balance is typical for mid-frequency statistical arbitrage where the forecasts and the costs are of the same order of magnitude [6]. It is then the subtle difference between the forecast performance1 and the cost of trading, which separates success from failure." "A finite solution for τ in this geometry exists only if the forecast at an infinite horizon exceeds this cost: f∞ > 2c, otherwise such tangent does not exist and it is best not to trade." | isichenko_2021_costly_trading.pdf.txt lines 57-63, 212-216 |
| R1-E38 | Typical IR and IC; sign probability | Kahn 2018 | "A top-quartile manager can add 50 bps of realized residual return for every 100 bps of residual risk, before expenses." Exhibit 4.5 "Average 0.00 / Good 0.05 / Great 0.10". "But even a great information coefficient is only 0.1." "0.1 corresponds to correctly forecasting the sign of the residual return about 53% of the time." | same, lines 2212-2214, 2407-2440, 2450-2452 |
| R1-E39 | Casino example IR = 16 | same | "IR = 5.2% / 0.32% = 16 = IC ⋅ BR ." (radical lost in text layer) "In this simple example, breadth works to reduce the variance of outcomes— exactly what we expect from diversification. It doesn't alter the expected return." | same, lines 2773-2781 |
| R1-E40 | Fundamental law critique | Michaud and Michaud 2005 (practitioner) | "While mathematically correct, the formula ignores uncertainty in information and practical constraints in asset management." "1) Information level and breadth are independent. 2) Unconstrained MV optimization is a useful asset management framework for evaluating optimized portfolio performance." "As a reasonable rule of thumb, the breadth is unlikely to be much greater than five whatever the size of the optimization universe." | newfrontier_eqopt4_fl.pdf.txt |
| R1-E41 | Breadth estimated by eigenvalues >= 1 | Polakow and Gebbie 2006 (academic/practitioner) | "The breadth of a market provides a measure of the number of independent bets available to the investor. We use the Keiser-Gutman stopping criterion to select the integer valued effective dimension - eigenvalues greater-than or equal to 1." | arxiv_physics0601166.pdf.txt abstract |
| R1-E42 | Backtest Sharpe barely predicts OOS; more backtesting, bigger gap | Wiecki et al. 2016 (Quantopian; practitioner) | "we find that commonly reported backtest evaluation metrics like the Sharpe ratio offer little value in predicting out of sample performance (R² < 0.025)." "the more backtesting a quant has done for a strategy, the larger the discrepancy between backtest and out-of-sample performance." | wiecki_etal_2016_glitters.pdf; wiecki.raw.txt abstract |
| R1-E43 | Body figures | same | "Sharpe ratio IS was positively correlated with Sharpe ratio OOS (Pearson R²=0.02; p < 0.0001; figure 1b)." "using only the last backtest year to compute IS Sharpe ratio increased predictability of OOS Sharpe ratio suggesting a recency effect (Pearson R²=0.05; p < 0.0001; not shown)." "we confirmed a weak (Spearman R²=0.017) but highly significant (p < 0.0001) positive correlation between the logarithm of the backtest days and Sharpe ratio shortfall" | wiecki.raw.txt lines 163-166, 208-210 |
| R1-E44 | Mega-alpha; definition of an alpha | Kakushadze 2016 (practitioner) | "This yields an ever increasing number of alphas, whose count can be in hundreds of thousands and even millions"; "with a bonus of automatic internal crossing of trades (and thereby crucial-for-profitability savings on trading costs, etc.)"; "“An alpha is a combination of mathematical expressions, computer source code, and configuration parameters that can be used, in combination with historical data, to make predictions about future movements of various financial instruments.” [Tulchinsky et al, 2015]" | kakushadze_2016_101alphas.pdf.txt lines 48-56, 75-76 |
| R1-E45 | 101 alphas' holding periods and correlation | same | "Their average holding period approximately ranges 0.6-6.4 days. The average pair-wise correlation of these alphas is low, 15.9%." | same, abstract |

Planner pointers (reports/stage_e32_inputs/planner_research_soy_complex.md): none of its claims concern the
research process, decay half-lives at firm level or capacity, and the E.32 brief assigns none to R1; table empty.

| Planner claim | Status | Note |
|---|---|---|
| (none assigned to R1) | n/a | checked by grep for process, decay, half-life, capacity, crowding, paper trading, Isichenko, Narang, Grinold |

---

#### 9. Failures, gaps, negative evidence, budget

Not obtained in full text (searched or tried; nothing from them is used as evidence):
- Isichenko, "Quantitative Portfolio Management" (Wiley 2021): no publisher sample found (Wiley excerpt URL patterns
  returned 404; e-bookshelf search 404; search results were spam mirrors, not used). His arXiv paper (R1-E20,
  R1-E37) is used instead and cites the book as its source for the forecast-cost balance.
- Lopez de Prado, AFML (2018) ch. 1 and ch. 15 ("Understanding Strategy Risk", whose implied-precision formula is
  the nearest published analogue of section 6.2): not obtained. The ch. 1 excerpt URL on thetrustedinsight.com
  returned no response to curl, and Wayback has no capture (afml_ch1_trustedinsight_wayback.html is the "not
  archived" page). quantresearch.org's lecture index links only to SSRN, which is blocked (READER_RULES). The 2018
  GARP paper (R1-E1 to R1-E4, R1-E21) covers the ch. 1 meta-strategy material. Section 6.2 is a worker's
  derivation and is labelled as such; it is not attributed to AFML ch. 15.
- Lopez de Prado, "Machine Learning for Asset Managers": not fetched (SSRN only).
- Grinold (1989) and Grinold-Kahn, "Active Portfolio Management": paywalled; the fundamental law is quoted from Kahn
  (2018), Grinold's co-author, with the radical verified on the rendered page. Clarke, de Silva and Thorley (2002):
  abstract-level only (search snippets), not used beyond Kahn's footnote 35.
- Narang ch. 9, Chan ch. 3 and ch. 5 (paper trading): only front matter in the Wiley reading samples.
- Kissell (execution-cost books): not searched beyond the Wiley excerpt probe; cost modelling is owned by other
  E.32 workers and E.28; no Kissell claim is made.
- Tulchinsky et al., "Finding Alphas": not obtained; its alpha definition is quoted second-hand through Kakushadze
  2016 (R1-E44).
- WorldQuant BRAIN numeric criteria: only community GitHub tools and search snippets; [unverified], not used.
- Firm blogs beyond E.28 2.11: searches for Man Institute alpha-decay pieces, QRT, Squarepoint and Two Sigma research
  process pages returned no firm-published process material (interview-prep sites and job ads only, not used).
  A search for staged-capital or pod drawdown rules (for example 5% / 7.5% stop-outs) returned nothing citable;
  such figures exist only in journalism and are not reported here.
- Negative evidence (consistent with E.28 2.11 section 6): no firm in this pass publishes a numeric FDR level, a
  hold-out length, a paper-trading length or a staged-capital schedule for short-horizon strategies. The quantitative
  practitioner material is from asset managers and quant equity (BlackRock, AQR, CFM, WorldQuant, Quantopian), at
  daily to monthly horizons; nothing practitioner-published was found on the research process for minutes-scale
  directional futures specifically.

Fetch notes: all fetches by curl with browser headers (route 2); no Scrapling, no Firecrawl, no WebFetch was needed.
404s logged: newfrontieradvisors 2019 PDF, JOIM p0158 and p0543, Harvey-Liu "False and missed discoveries" (Duke
URL guessed wrong); the empty or HTML-error files are not kept (log.tsv still lists them with their sha256). Third-party mirrors used and flagged in log.tsv:
smallake.kr (LdP 2017 slides, LdP-Lewis 2019), top1000funds.com (Di Mascio et al.), counterpointfunds.com (McLean-
Pontiff), c.mql5.com (Quantopian paper). Their text carries SSRN's "Electronic copy available" footer where SSRN
was the origin; none was cross-checked against the journal version.

Budget: WebSearch 30 of 80 used (17 by the first spawn, 13 by this one; no budget notice received). The first
spawn's log records a "session limit" notice at 00:51 PDT (a usage limit, not a WebSearch budget notice). No market
data, no keys, no Databento, broker, TopstepX or ProjectX access. No other worker's files touched.

Completion: sections 1-9 written. All worked-example arithmetic was run by a script in this session and is shown
step by step for the reviewer.

Stopping rule (READER_BRIEF rule 6), per topic: (a) 5 full-text sources (LdP 2018, Kahn, Chan, CFM, WorldQuant) and
the last three discovery searches (WorldQuant criteria, QRT/Two Sigma/Squarepoint, Man Institute) found nothing
new: stopped. (b) 4 (Bailey-LdP, LdP slides, Chan, Isichenko) plus E.28 2.11; the last three searches on
incubation, staged capital and paper-trading length found nothing citable: stopped, with the gap stated. (c) 6
(LdP 2018, LdP-Lewis, Kahn, Harvey-Liu, McLean-Pontiff, Quantopian): stopped. (d) 7 (Kahn, Kakushadze-Tulchinsky,
CFM x2, Di Mascio et al., Garleanu-Pedersen, FIM): stopped; the Maven Securities alpha-decay search found nothing.
(e) 5 (Kahn, Michaud, Polakow-Gebbie, Isichenko, Kakushadze-Tulchinsky): stopped; AFML ch. 15 not obtainable.

## R2. Commodity and agricultural trading desks

Source file: reports/stage_e32_briefs/R2_ag_desks.md (sha256 52854a41138d465726a75a22dd83bb71d6b137b36debb9c19e085b404fbc18bc).

### E.32 Part R2: how commodity and agricultural desks trade the soybean complex at short horizons

Worker: AgDesks-OpusHigh (ROOT R2_ag_desks), started 2026-10-27 00:40 PDT.
Evidence pages and log: reports/stage_e32_briefs/pages/R2_ag_desks/ (log.tsv). Helper: work/R2_ag_desks/R2_fetch.sh.
Source labels: [academic], [regulator], [exchange], [firm], [practitioner]. Every quote below is verbatim from the
saved file named next to it; [unverified] marks claims not read in full text.
No market data was read; no statistic was derived from data.

Status: complete (re-spawn finished 2026-10-27 02:42 PDT). Written section by section.

---

#### P0. Planner pointer: Li, Wang and Diersen (NCCC-134 2024)

Source [academic, conference paper]: Li, Z., Z. Wang and M. Diersen (2024), "Do Agricultural Commodity Price
Spikes Always Stem from News?", NCCC-134 proceedings. File: LiWangDiersen_NCCC134_2024.pdf (.txt).

What it studies (verbatim):
- Scope: "We aim to identify and categorize both types of price spikes in corn, soybean, and wheat futures markets."
  (abstract) But the empirical work is corn only: "The analysis of price spikes is based on corn futures trading
  data. The end-of-5-minute intraday original data of prices for agricultural commodity futures were collected from
  the Chicago Mercantile Exchange Group (CME Group) from 01/01/2013 to 12/31/2022." and "only the normal daytime
  trading hours, from Monday to Friday between 8:30 a.m. and 1:20 p.m. CT, have been chosen." Soybeans are future
  work: "In addition, we plan to explore a wide range of agricultural futures, such as soybeans and wheat."
- Counts: "Over 2,403 trading days, we recorded a total of 3,419 jumps. The daily average number of jumps is 1.42."
  "we record 3,094 clusters of jumps ... Of these, there are 994 news-related clusters of jumps on 494 days, which
  occupy 32.13% of all clusters. The non-news-related clusters account for 67.87%."
- News timing is daily, not intraday: "we could not match the daily news precisely to the ... timestamp of our
  intraday trading data" (lines 140-144, paraphrase of a broken line; see file).
- Result on dynamics: "exogenous events exhibit a faster decay in their relaxation exponent, indicating a shorter
  memory span, in contrast to the more prolonged impact of endogenous events." (Conclusions). This is about the
  decay of volatility (jump intensity) after a shock, not about the sign of later returns.
- Jumps in the first and last 15 minutes of the day are dropped: "we exclude jumps occurring in the first and last
  15 minutes of the trading day."

Does it bear on desks or flows? No. It has no trader, position, order-flow or COT data; "endogenous" means only
"no dated news item that day", not "caused by a flow". It bears weakly on idea family 5 (non-news jumps): in corn,
about two-thirds of 5-minute jump clusters have no news that day, and their volatility relaxes more slowly than
USDA-day jumps. It says nothing about direction after a jump, and nothing about ZM. Use: a pointer that non-news
jumps are common and should be a stratum, not evidence of a tradable effect.

---

#### A. Merchants and processors (ADM, Bunge, Cargill, Louis Dreyfus type): hedging and crush flows

##### A.1 Facts

1. Merchants run a net commodity position, hedged with exchange futures, with daily volume limits and weekly VaR.
   [firm, 10-K] ADM Form 10-K FY2023, Item 7A (ADM_10K_FY2023_Item7A_quotes.txt; Firecrawl direct-quote, raw page
   not saved because sec.gov refuses an undeclared User-Agent):
   - "The Company manages its exposure to adverse price movements of agricultural commodities used for, and produced
     in, its business operations, by entering into derivative and non-derivative contracts which reduce the
     Company's overall short or long commodity position. Additionally, the Company uses exchange-traded futures and
     exchange-traded and over-the-counter option contracts as components of merchandising strategies designed to
     enhance margins."
   - "In addition, the Company, from time-to-time, enters into derivative contracts which are designated as hedges
     of specific volumes of commodities that will be purchased and processed, or sold, in a future month."
   - "Volumetric limits are monitored daily and VaR calculations and sensitivity analysis are monitored weekly."
   - Item 1A (WebFetch, cut to 125 characters by the tool): "to continually assess price and basis opportunities."
2. Processors hedge a few months of crush capacity with exchange futures.
   [firm, 10-K] Bunge 10-K FY2007, Note 1 (Bunge_10K_FY2007_hedge_quotes.txt; same route): "Bunge hedges portions
   of its forecasted U.S. oilseed processing production requirements, including forecasted purchases of soybeans and
   sales of soy commodity products, for quantities that usually do not exceed three months of processing capacity.
   The instruments used are exchange-traded futures contracts, which are designated as cash flow hedges."
   Later filings (FY2019, search snippet only) say most commodity contracts are economic hedges not designated for
   hedge accounting [unverified: search snippet].
3. The textbook processor hedge is a three-step crush: long soybeans, short meal and oil, unwound in steps.
   [academic] Dahlgran (2005), JARE 30(3) (Dahlgran_JARE2005.pdf): "Tzang and Leuthold (1990) describe a
   three-step soybean-crushing hedge: (a) at the beginning of the planning horizon, buy soybean futures and sell
   soybean meal and soybean oil futures; (b) when processing is initiated, buy soybeans and sell the soybean futures
   contracts; and (c) when processing is complete, sell soybean oil and meal and buy soybean oil and meal futures.
   These steps are respectively denoted as anticipatory hedging, transformation hedging, and hedge closure."
   And: "The crush spread involves a long soybean futures position and short soybean meal and soybean oil futures
   positions in the ratios of 47 pounds of meal and 11 pounds of oil for each bushel of soybean futures."
   Abstract: "(b) anticipatory hedging provides less risk protection than product-transformation hedging".
   The model allows "up to 52 transactions per year" (weekly), i.e. the academic frame is weekly-to-quarterly
   rebalancing, not intraday.
4. Physical-commodity futures are traded more by end users and manual traders than financial futures.
   [regulator] CFTC OCE, Haynes and Roberts (2015), "Automated Trading in Futures Markets"
   (CFTC_oce_automatedtrading.pdf): "the products with the lowest level of automated participation are the physical
   commodity classes, encompassing energy, metals and agricultural products like oil, copper and wheat. Physical
   commodity futures trading often has a higher level of both buy- and sell-side end users who consume and produce
   these goods, and often trade on a manual basis."
   [regulator] CFTC OCE, Fett and Haynes (2017), "The Futures Trading Landscape" (CFTC_oce_futureslandscape.pdf):
   "Trading in physical futures contracts is more concentrated among the individuals and corporations who are part
   of the manufacturing process." and "Because producers and consumers are exposed to the price fluctuations of a
   physical commodity over extended periods of time, this can often require multi-leg hedges across multiple
   contracts or trading in the relative value of a long-dated versus a shorter-dated contract."
   And: "For the products where they are the most active, Corporations participate, relatively equally, in both
   outright and spread trading."

##### A.2 When do merchant and processor flows hit ZM, and are they predictable intraday?

What the sources support:
- Merchant hedges are tied to cash transactions (purchases from elevators and farmers, product sales to feed
  mills and exporters) and to a crush plan that runs weeks to months ahead (Bunge: up to three months of capacity).
  Their futures orders are therefore triggered by cash deals and by risk limits checked daily (ADM), which are not
  observable to us. No source read gives an intraday timetable for merchant hedging.
- Hedges go on as spreads or multi-leg packages (Fett and Haynes; Dahlgran's crush), so a large share of commercial
  ZM volume plausibly trades in the crush or calendar spread books rather than as outright ZM aggression. R3b
  section (b) covers implied spreads; whether commercial crush orders reach the ZM outright book only through
  implied prices is a microstructure question for R3b, not evidenced here.
- Nothing read supports "merchant flow is predictable intraday". The only predictable commercial behaviour in the
  evidence is weekly and contrarian (Kang, Rouwenhorst and Tang, section C), and it is visible only with a
  three-day lag in the COT.
- What we cannot see: merchants' cash-basis bids (not in our data), customer sales, and the actual times of their
  futures orders. The owned ZM MBO feed is anonymous (no account or firm identifier; per the program's earlier data
  notes, not re-read here), so merchant flow can only be inferred from order size and spread trading.

Null result: three discovery queries (merchant 10-K hedging, Bunge crush margin hedging, processor hedging
transaction frequency) found no study that times processor futures orders within the day.

---

#### B. Proprietary trading shops and market makers in grains

##### B.1 Facts

1. [regulator] CFTC OCE, Haynes and Roberts (2017), "Automated Trading in Futures Markets - Update"
   (CFTC_oce_automatedtrading_update.pdf), Table 3, soybean futures (ZS, not ZM), share of volume by counterparty
   type, first sample Nov 12 2012 - Oct 31 2014, then Nov 1 2014 - Oct 31 2016: "Agriculture - Grain and Oilseed
   Soybean 93 115 15.2 25.1 42.5 45.6 36.3 24.1" (columns: total volume mm; ATS-ATS %; ATS-MAN %; MAN-MAN %, each
   for the two periods). So in 2014-16 about 25% of ZS volume was automated-vs-automated and 24% manual-vs-manual.
2. Same source, Table 1, product group: "Agriculture - Grain and Oilseed 16 13 5.6 (0.4) 4.1 (0.3) 39.0 (2.7)
   49.0 (3.9) 55.4 (3.8) 46.9 (3.8)" (non-electronic %, ATS %, manual %): manual trading still about 47% of grain
   and oilseed volume in 2014-16, against e.g. 15.6% in G10 FX ("FX - G10 ... 16.4 (1.1) 15.6 (1.0)").
3. Small accounts dominate soybean volume. [regulator] Haynes and Roberts (2015), Table (small vs large volume
   traders, 2012-14): "Soybean 59,739 19.2 42.2 815 17.2 15.4" (small traders: N, ATS %, MAN %; large: N, ATS %,
   MAN %), with the text: "for individual products like corn and soybeans, small traders contribute the majority
   share of volume; these contracts have a wide set of participants who, individually, execute small quantities,
   but are significant in aggregate." "Large" is defined there as "an account which contributes at least 0.5
   percent to a given day's volume".
4. Spread trading is a large share of soybean volume. Same 2015 table by order type, soybean row: "Soybean 9.1 2.6
   3.5 17.9 9.0 15.6 9.8 8.1 18.4" (ATS-ATS RO-RO, RO-SP, SP-SP; ATS-MAN RO-RO, RO-SP, SP-SP; MAN-MAN RO-RO, RO-SP,
   SP-SP; RO = regular outright, SP = spread). Summing the SP-SP columns: 3.5 + 15.6 + 18.4 = 37.5% of ZS volume was
   spread-against-spread, and outright-against-outright 9.1 + 17.9 + 9.8 = 36.8% (my arithmetic on the quoted
   row; the row omits non-electronic volume).
5. [regulator] Fett and Haynes (2017): "PTFs, and to a lesser extent banks, are usually active throughout the
   trading day, often trading in smaller sizes and with shorter holding periods. Others, like asset managers, trade
   only a handful of times on an average trading day, with activity often concentrated near the settlement period.
   These traders are usually more tilted to spread trading, where they roll large positions out of an expiring
   contract, usually using a relatively small number of large volume trades."

6. HFT share of soybean volume, account-level. [regulator WP, academic] Coughlan and Orlov (CFTC, July 2022 draft),
   "High-Frequency Trading and Market Quality: Evidence from Account-Level Futures Data"
   (CoughlanOrlov_CFTC_2022_HFT.pdf), trade capture data 2012-2021, nine contracts incl. corn, soybeans, wheat:
   - Table 1: "Agriculture   Soybeans         13.1%    36.0%     175.8%       24.8%" (HFT market share 2012, 2020,
     percent change, average over the sample). Against "Energy        WTI crude oil    29.1%    53.9%" and
     "Financials    E-mini S&P500    31.8%    49.7%".
   - HFT is defined by behaviour, not by firm type: "Accounts are classified as HFTs if they trade more than 0.25% of
     total volume in a calendar year, have an end-of-day inventory less than 20% of their trading volume, and never
     hold more than 30% of their daily trading volume at any point in time within the trading day."
   - Abstract: "greater participation by HFTs is strongly associated with improvements in market quality ...
     although higher rates of aggressive trading, such as those observed when HFTs trade directionally to reduce
     their positions, produce an adverse effect on market quality."
   - Why grain HFT share was low until 2015 (settlement mechanics): "the HFT speed advantage was somewhat hindered
     during the settlement period when pit trades were included in the daily settlement calculations" and "during
     the settlement period a large percentage of daily volume is traded, on average, and large price movements are
     common. The settlement period also happens to be the end of the trading day when HFTs need to close out their
     positions". The blended settlement "was abandoned in 2015 when CME closed its agricultural futures pits."
   - ZM is not in the sample; the soybean row is a proxy only.
7. A market-quality view from an ag economist (extension talk, practitioner/academic; pointer-grade but full text
   read). Janzen (2018), "High Frequency Trading in Agricultural Futures Markets: What Low Frequency Traders Should
   Know" (Janzen_KSU_HFT_ag.pdf): "HFT is prevalent, but not dominant in major ag futures markets." On USDA releases:
   "July 2018, USDA announced end of "lock-up" procedure for major report releases; news organizations no longer
   have early access to WASDE, Grain Stocks, and other reports" and "Some news organizations may have been able to
   send out report up to 2 seconds before USDA posted report".
8. Minute-scale reversal in corn, attributed by the speaker to tick size (academic talk). Jones (2018),
   "High-frequency trading and changes in futures price behavior" (Jones_KSU_HFT_presentation.pdf), on nearby corn
   1-minute returns from RTH transaction prices: "In recent data, almost 30% of the one-minute price change is
   reversed in the next minute"; "Evidence for soybeans is similar"; "Most likely explanation in this case: the
   minimum tick is too big, at least for right now". The benchmark slide says "Bid-ask bounce and temporary moves in
   prices would lead to [rho] < 0." Caution for us: a negative 1-minute autocorrelation measured on LAST-TRADE
   prices is largely bid-ask bounce, which a 1-lot paying the spread cannot harvest (it is the spread). Any ZM
   reversal feature must be measured on mid-quotes (ZM MBO lets us), not on trades. The corn table of big moves
   (0.5% or more) shows the "fraction of big moves that are at least half reversed 1 min. later" at 15%-24% in 2007-2014
   and 37%, 22%, 38% in 2015, 2016, 2017 ("2015 65 -0.15 37%", "2017 34 -0.19 38%"); even in the latest years most
   big 1-minute corn moves are NOT half reversed a minute later, and the counts are small (34-65 a year).
9. Prop-firm behaviour visible through enforcement (regulator). CFTC Press Release 7865-19
   (CFTC_PR_7865-19_soybean_spoofing.html/.txt): "a trader at a proprietary trading firm" who "between August 2013
   and June 2016 ... placed orders to buy or sell futures contracts on soybeans, soybean meal, and soybean oil with
   the intent to cancel the orders before execution", using "an automated tool to place relatively small bids or
   offers on one side of the market (Genuine Orders)" and "manually placed relatively large bids or offers on the
   opposite side of the market (Spoof Orders)". Consequence for an order-book-imbalance feature on ZM MBO: large
   resting size on one side is, at least sometimes, placed to be cancelled; imbalance features should be tested
   with and without large, short-lived orders, and cancellation-adjusted variants (R3b/M1 own the feature design).
10. Formal liquidity provision in grain OPTIONS, not futures (exchange filing hosted by the CFTC). CBOT Submission
    No. 11-489 (CFTC_CBOT_rul120811_options_MM_program.pdf): "a market making program in support of certain CBOT
    grain and oilseed options that are traded on the Globex platform", effective "January 01, 2012", product scope
    including "Soybean Meal options"; "All Product activity shall be conducted through a proprietary account of the
    market maker"; "Up to fifteen (15) participants may be selected"; ranking on "Time in the market", "Bid-Ask
    Spread; Book Size and Responses to requests-for-quotes"; incentives include "mass quote functionality" and fee
    waivers. That option market makers delta-hedge in ZM futures (a flow into the futures book) is the standard
    mechanism but is [unverified] in any source read; no ZM-futures market maker program was found.
11. Pit closure and crush packages (regulator WP). Gousgounis and Onur (CFTC OCE, 2016)
    (CFTC_oce_effectofpitclosure.pdf): "Similar concerns have also been raised by soybean brokers, who argue that
    CME's trading platforms do not allow trading in soy crush spreads with non-standard ratios." And: "although
    futures pit trading has been diminished to very low levels, it has not completely disappeared" (special
    strategy trades with an options leg). This supports A.2: some commercial crush hedging is executed as packages
    that never appear as outright ZM aggression on Globex.
12. Speed of automated versus manual traders (regulator, NOT grains: E-mini). Fishe, Haynes and Onur (CFTC OCE,
    "Speed and Latency in Treasury and e-Mini Futures Contracts - Part 2") (CFTC_oce_speedandlatency2.pdf):
    "algorithmic proprietary traders are the quickest group with 50% of the observations responding with new orders
    in less than 200 milliseconds. In contrast it takes manual proprietary traders over 9 seconds on average for
    one-half of the observations to respond." Equal-weighting participants: "the new cutoff for the algorithmic
    proprietary group increases latency time by a factor of 25 to just over 5 seconds". So the median algorithmic
    participant (not the median message) re-quotes in seconds, not microseconds; a 300-1,000 ms bot is slower than
    the fastest accounts but not out of the population.

##### B.2 Prop shops and market makers: what the public record supports

- Who provides grain liquidity: account-level CFTC data show HFT-type accounts at about a quarter of soybean volume
  on average over 2012-2021 and 36% in 2020 (Coughlan and Orlov), with manual trading still about 47% of grain and
  oilseed volume in 2014-16 (Haynes and Roberts 2017), and small accounts the majority of soybean volume (Haynes and
  Roberts 2015). Grains are therefore less dominated by fast liquidity providers than crude, gold or the E-mini.
- Named firms and their strategies: no filing, paper or regulator document read names a grain prop shop's strategy.
  Public pointers only: a CTA-database page describes a discretionary program trading "mainly ... the soybean
  crush" (County Cork LLC, ctadatabase.fundpeak.com, search snippet; pointer, not evidence); a 2006 CBOT release
  names a Chicago firm as market maker for crush-spread options (cmegroup.com, not fetched under the stage CME rule;
  pointer). One WebSearch for grain prop job descriptions returned none.
- What prop firms are documented doing in the soybean complex: market making (CBOT options program), and one
  enforcement case of spoofing across ZS, ZM and ZL with automated small orders against manual large ones.
- Null result: two discovery queries (grain prop job descriptions and crush market makers; CFTC-hosted CBOT market
  maker filings for grain futures) found no ZM-futures market maker program and no public description of a grain
  prop shop's short-horizon edge. Stopping rule met for (b): full text read from 5 regulator/academic sources
  (Haynes and Roberts 2015, 2017; Fett and Haynes 2017; Coughlan and Orlov 2022; Gousgounis and Onur 2016) plus the
  CBOT filing and the enforcement release; the last 3 queries surfaced nothing new on named shops.

---

#### C. CTAs, index funds and COT positioning

##### C.1 Who the COT categories are, and when the COT is public

[regulator] CFTC Disaggregated COT explanatory notes (CFTC_disagg_explanatory_notes.html/.txt):
- "A "producer/merchant/processor/user" is an entity that predominantly engages in the production, processing,
  packing or handling of a physical commodity and uses the futures markets to manage or hedge risks associated
  with those activities."
- "A "swap dealer" is an entity that deals primarily in swaps for a commodity and uses the futures markets to manage
  or hedge the risk associated with those swaps transactions."
- "A "money manager," for the purpose of this report, is a registered commodity trading advisor (CTA); a registered
  commodity pool operator (CPO); or an unregistered fund identified by CFTC."
- Classification is a judgment call: "the actual placement of a trader in a particular classification based upon
  their predominant business activity may involve some exercise of judgment on the part of Commission staff".
[regulator] CFTC COT page (CFTC_COT_index.html/.txt): "The COT Report is generally published each Friday at
3:30 pm Eastern Time (US), using the data from the immediately preceding Tuesday of that week." and "The CFTC
receives the data from the reporting firms on Wednesday morning and then corrects and verifies the data for release
by Friday afternoon."
- Timing consequence (my arithmetic): 15:30 ET = 14:30 CT, after the 13:20 CT grain close, so the first ZM session
  that can react to a COT release is the Sunday 19:00 CT overnight open (R4 section 1.1 has the session grid). The
  positions are 3 trading days stale by then.
[regulator] Legacy COT notes (CFTC_COT_explanatory_notes.txt) on index traders: "All of these traders ... are
generally replicating a commodity index by establishing long futures positions in the component markets and then
rolling those positions forward from future to future using a fixed methodology."

##### C.2 Does COT positioning predict returns? (academic)

1. Sanders, Irwin and Merrin (2009), JARE 34(2) (SandersIrwinMerrin_JARE2009.pdf) [academic], weekly 1995-2006,
   10 markets including soybean meal: "Bivariate Granger causality tests show very little evidence that traders'
   positions are useful in forecasting (leading) returns in 10 agricultural futures markets. However, there is
   substantial evidence that traders respond to price changes. In particular, noncommercial traders display a
   tendency for trend following." and "The results generally do not support use of the COT data in predicting price
   movements in agricultural futures markets." Table 1 (noncommercial positions lead returns, p-value of
   beta_j = 0 for all j), soybean meal row: "Soybean Meal 1, 1 0.929 0.929 0.687 0.921 0.000". Text: "the null
   hypothesis that noncommercial positions (PNL) lead or forecast market returns is rejected at the 5% level only in
   soybeans (p-value = 0.047)."
2. Kang, Rouwenhorst and Tang (JF 2020; read as the 2016 draft, KangRouwenhorstTang_2016draft.pdf, and NBER
   w19670) [academic], 26 commodities, weekly, 1994-2014:
   - "Short-term position changes are mainly driven by the trading demands of impatient speculators, while
     long-term variation is primarily driven by the hedging demands from commercial hedgers."
   - "speculators are momentum traders and hedgers are contrarians."
   - "during the weeks following a position change, commodities that are most heavily bought by speculators earn
     significantly lower returns than commodities that are sold by them."
   - Size: "the return impact of an average position change by hedgers, which is equal to 3.5% of total open
     interest ... changes the expected return in the subsequent week by 4.77%*3.5% = 0.168%, or by 9.1%
     annualized."
   - Post-publication part (the tradable part): "a positive excess return spread persists during days 5-20
     following the release of the CFTC report: 0.30% during days 5-10 (t = 3.62) and 0.15% (t = 1.23) during days
     11-20." Days 1-4 are before the report is public: "we separately report the excess returns during days 1-4
     when the report is not yet released and days 5-40 when the information contained in the report is in the
     public domain."
   - This is a cross-sectional, weekly, multi-commodity sort. It is not a ZM time-series signal and not intraday.
   Worked scale check (my arithmetic, assumption: ZM at an illustrative 400 USD/short ton, 0.10 USD tick): a 0.30%
   move over days 5-10 is 0.0030 x 400 = 1.2 USD/ton = 12 ticks spread over about 6 trading days, i.e. about 2
   ticks a day, against a daily range median of 96 ticks (E.28 Table 1). As a minutes-scale feature this is noise;
   at most it is a weekly regime tag.

##### C.3 Index funds and their rolls

1. ZM is in the Bloomberg Commodity Index, which rolls on business days 6-10 at settlement prices.
   [firm, index provider] BCOM Methodology, February 2026 (BCOM_Methodology_FEB2026.pdf): the 2026 list includes
   "17. Soybean Meal"; "The "Roll Period" is used in this Methodology to refer to the sixth through tenth Business
   Days of the month"; "On each day of the Roll Period, the dependence of BCOM is shifted, at the rate of 20% per
   day, from WAV1 to WAV2". Contract calendar row (Jan..Dec lead future): "Soybean Meal Mar Mar May May Jul Jul Dec
   Dec Dec Dec Jan Jan". Reading the row (my reading, consistent with R3b c.1): BCOM rolls ZM in February (H to K),
   April (K to N), June (N to Z), October (Z to F) and December (F to H): five roll months a year; it never holds
   the Aug, Sep or Oct ZM contracts.
   - "Hedge Roll Period" means "the period of five Business Days, beginning with the fifth Business Day through and
     including the ninth Business Day of each month" (used for market-disruption handling).
   - Index value is computed at settlement prices (methodology section on daily calculation; "the CIPs are combined
     with the Settlement Prices of all Designated Contracts for such day"), so replicating swap dealers have a
     reason to trade at or near the 13:15 CT settlement (TAS or the closing range). That replicators actually use TAS
     for the BCOM ZM roll is [unverified]; R4 section 5.1 covers TAS.
2. Before BCOM added meal, soybean meal was not in the CFTC's index-trader (CIT) market set.
   [academic] Aulerich, Irwin and Garcia (NBER w19065, 2013) (AulerichIrwinGarcia_NBERw19065.pdf), CFTC
   non-public daily large-trader data: "CITs in 12 agricultural futures markets: CBOT corn, soybeans, soybean oil,
   and wheat; KCBOT wheat; CME feeder cattle, lean hogs, and live cattle; and ICE cocoa, cotton, coffee, and sugar."
   No soybean meal. When BCOM added meal is [unverified] here (R3b reports the current membership only).
3. Roll activity is spread wider than the Goldman window, and its price impact in grains is small and of the wrong
   sign for a pressure story. Same source:
   - "roll #1 and #2 contain about 90% of total rolling activity ... Roll #4 (the Goldman roll) contains
     approximately 65% of roll activity in 2004 but decreases to only about 50% in 2009".
   - "Point estimates of the cumulative impact of a one standard deviation increase in CIT positions on daily
     returns are negative and very small, averaging only about two basis points. The null hypothesis that CIT
     positions do not impact daily returns in a data-defined roll period is rejected in 5 of the 12 markets and
     estimated cumulative impacts are negative in all 12 markets; the opposite of the expected outcome if CIT rolling
     activity simultaneously pressures nearby prices downward and first deferred prices upward."
   - Same paper, literature review: spreads (calendar spreads) "increase during the narrow window when existing
     index positions are rolled from one nearby contract to the next, but the increase is temporary as spreads
     quickly return to the level prevailing before the roll window."
4. Predictable roll trades attract liquidity rather than predators, in a resilient market (crude oil evidence).
   [academic] Bessembinder, Carrion, Tuttle and Venkataraman (2015 draft of JFE 2016)
   (Bessembinder_etal_predictable_trades_2015draft.pdf), USO crude-oil ETF rolls: "The evidence indicates narrower
   bid-ask spreads, greater order book depth and improved resiliency on roll dates. We find that a larger number of
   individual trading accounts provide liquidity on roll dates, and do not find evidence of the systematic use of
   predatory strategies." Not grains; an analogy only.
5. Mou (2010/2011) on front-running the Goldman roll: full text not read (Columbia Academic Commons served a bot
   check page, saved as Mou_ColumbiaThesis.pdf which is HTML; SSRN is blocked). [unverified]. R3b c.1 cites it as
   unverified too.

##### C.4 CTAs and trend followers

- The evidence read says large speculators (noncommercial / managed money) are trend followers at weekly horizons
  (Sanders, Irwin and Merrin: "noncommercial traders display a tendency for trend following"; Kang, Rouwenhorst and
  Tang: "speculators are momentum traders"). Kang et al. read that trend following as liquidity DEMAND that
  commercials supply, with short-run reversal of speculator-driven moves at the weekly horizon.
- Intraday CTA execution (what time of day trend followers trade ZM, how much at the settlement) is not in any
  source read. Fett and Haynes's statement that asset managers' "activity [is] often concentrated near the
  settlement period" is the only regulator evidence on time of day, and it is for asset managers across futures, not
  CTAs in ZM.


##### C.5 Index rolls and calendar spreads (regulator WP), and two abstract-only pointers

1. [regulator WP] Brunetti and Reiffen, "Commodity index trading and hedging costs" (CFTC OCE)
   (CFTC_OCE_commodityindextrading.pdf), non-public daily LTRS positions in corn, soybeans and wheat:
   "We find evidence, consistent with the model, that index traders have become an important supply of price risk
   insurance." On the roll: "One of our key findings is that the inter-maturity spread increases with the percentage
   of CIT holdings in the first deferred contract. This is consistent with the finding elsewhere (e.g., Mou, 2010)
   that the CIT roll is associated with predictable changes in futures prices." Model comparative static: "the larger
   the size of the position being rolled, the more rapidly the spread increases with the percentage of their
   holdings in the first deferred contract." And: "the timing of the roll by major CITs is announced". The effect is
   on the CALENDAR SPREAD (front minus first deferred), at daily settlement frequency, not on the outright ZM
   direction, and soybean meal is not in their sample.
2. [academic, abstract only: unverified in full text] Frino et al. (author list not checked), "Are Hedgers Informed? An
   Examination of the Price Impact of Large Trades in Illiquid Agricultural Futures Markets", Journal of Futures
   Markets 2016, doi 10.1002/fut.21774 (OpenAlex abstract): "in a relatively
   illiquid deliverable agricultural (grain) futures market where most transactions are executed by hedgers ... the
   price impact of large buyer-initiated transactions is permanent, consistent with the proposition that they are
   executed by traders perceived to be informed." Market not named in the abstract (likely not CBOT) [unverified].
   Pointer: if it holds for ZM, large aggressive ZM trades carry information, which is a testable MBO feature (signed
   large-trade flow), owned by M1.
3. [academic, abstract only: unverified in full text] Cheng, Kirilenko and Xiong, "Convective Risk Flows in Commodity
   Futures Markets", Review of Finance 2015 (doi 10.1093/rof/rfu043; NBER w17921): "while financial traders
   accommodate the needs of commercial hedgers in normal times, in times of distress, financial traders reduce their
   net long positions in response to an increase in the VIX causing the risk to flow to commercial hedgers." Weekly
   positions; a regime pointer (VIX spikes) only.
4. Not found in full text: Brunetti, Buyuksahin and Harris (daily LTRS positions and prices; a Bank of Canada copy
   URL guessed from memory returned 404 and was deleted; the BoC author page had no PDF link). [unverified]

Stopping rule for (c): full text read for 6 sources (Sanders, Irwin and Merrin 2009; Kang, Rouwenhorst and Tang;
Aulerich, Irwin and Garcia; Brunetti and Reiffen; BCOM methodology; CFTC COT notes) plus Bessembinder et al.; the
last 3 discovery queries (daily positions and prices; hedger price impact; index roll front-running) surfaced only
the abstract-only items above.

---

#### D. The information desks use, and what of it we can see

Cross-references, not re-verified here: release times against the CBOT session grid are R4 section 1.2 (Export Sales
Thursday 8:30 a.m. ET = 07:30 CT, inside the overnight session; NOPA monthly crush 12:00 noon ET = 11:00 CT for 2026;
WASDE and other USDA reports); board-crush arithmetic and the oil-share regime are R3a sections 1-2 and 8.

##### D.1 Facts

1. Board crush and processing margin [academic]. Dahlgran (2005) gives the futures crush as "a long soybean futures
   position and short soybean meal and soybean oil futures positions in the ratios of 47 pounds of meal and 11 pounds
   of oil for each bushel of soybean futures" and the processor's anticipatory hedge as "buy soybean futures and sell
   soybean meal and soybean oil futures" (Dahlgran_JARE2005.pdf). Bunge hedges "quantities that usually do not exceed
   three months of processing capacity" (Bunge_10K_FY2007_hedge_quotes.txt). Soybean brokers told CME that its
   platforms "do not allow trading in soy crush spreads with non-standard ratios" (CFTC_oce_effectofpitclosure.pdf),
   so a processor's real hedge ratio often differs from the listed crush and is worked as separate legs or packages.
   Mechanism (not evidenced intraday in any source read): a widening board crush invites processors to sell the
   crush (sell ZM and ZL, buy ZS), which pushes ZM down relative to ZS; a narrowing one invites the reverse. This is
   the fundamental anchor behind the crush mean reversion R3a reviews; it works over days to weeks.
2. Cash basis [firm]. ADM states it seeks "to continually assess price and basis opportunities"
   (ADM_10K_FY2023_Item7A_quotes.txt; Item 1A, WebFetch excerpt). Basis bids are set by merchants in the cash market
   and are not in our data. No source read links intraday ZM futures moves to basis changes. Null result.
3. Export inspections [government]. USDA AMS WA_GR101 "Grains Inspected and/or Weighed for Export", dated "Mon
   October 26, 2026" for the "WEEK ENDING OCT 22, 2026" (USDA_AMS_wa_gr101_export_inspections.txt): a Monday report
   on the prior Thursday-ending week. It lists whole grains and soybeans (grade code "YSB"); the word "meal" does not
   occur in the report (grep count 0). So inspections bear on ZS, and on ZM only through the crush. The release
   clock time is not printed in the file [unverified].
4. Export sales and NOPA crush: release times per R4. The NOPA data page (NOPA_datastatistics.html) lists "NOPA
   Monthly Crush Report" next to "Members Only"; R4 records distribution through a data vendor to subscribers.
   The weekly FAS export sales page could not be fetched (FAS 403 to curl and WebFetch; the earlier saved file
   USDA_FAS_export_sales_about.html is 0 bytes). NOPA is the one release that is about meal directly (crush volume,
   meal and oil stocks).
5. USDA reports and how fast they are absorbed [academic, conference paper; found by R2, R4 does not cite it].
   Anderson, McKenzie and Noyes (2024), "The Information Content of The WASDE Report and Intra-Day Price Reactions",
   NCCC-134 (AndersonMcKenzieNoyes_NCCC134_2024.pdf), corn and soybean nearby futures, 2010-2021, N = 122 reports:
   "We do not find a significant market reaction within the first ten minutes after the report" (line 102) and
   "the price reaction continues to grow for soybeans between 30 minutes" [and the close] (line 104; the line breaks
   there); Results: "Neither corn nor soybeans have significant price reaction within 10 minutes of the report
   release. However, both have significant price reactions after 30 minutes of the release." The equations print in
   a broken font; from the text definitions: News_it = (1/n) sum_j ln(WASDE_it / Forecast_ijt), the mean log
   surprise of USDA world ending stocks against analyst j's forecast (eq. 1), and PriceChange_wit =
   ln(Close_wit / Open_wit) over window w in {10 min, 30 min, day close} (eq. 2), regressed by SUR on News with an
   early-release dummy. Window start: "began when the WASDE report was released or the opening price if the report
   was released before the market opened". The authors themselves cite Lehecka, Wang and Garcia (2014) for the
   opposite view ("market reactions happen quickly and are completed within about 10 minutes", line 84). This is a
   regression of the post-release return on the KNOWN surprise; it needs the analyst survey (Bloomberg), which the
   program does not own, and 122 events is small. Soybeans only, not meal. Flag to the lead and R4.
6. Weather and South American crops: no academic study of intraday reaction to weather-model runs or to CONAB
   (Brazil) crop reports was found. Two WebSearch queries returned only trade press (StoneX insights, Reuters columns,
   MarketsFarm; pointers only) and one Crossref query returned Stevens (1991), "Evidence for a weather persistence
   effect on the corn, wheat, and soybean growing season price dynamics", J. Futures Markets, doi
   10.1002/fut.3990110108 (title only, [unverified]). R4 section 4 covers weekend weather and the Sunday open. Null
   result for intraday evidence.
7. COT: section C (public Friday 14:30 CT, Tuesday positions; weak or no forecasting power at the weekly horizon
   in soybean meal; cross-sectional weekly hedging-pressure premium of Kang, Rouwenhorst and Tang).
8. Speed of public information: Janzen (2018) on the end of the USDA lock-up in July 2018: "Some news organizations
   may have been able to send out report up to 2 seconds before USDA posted report" (Janzen_KSU_HFT_ag.pdf).

##### D.2 What this means for which information a 1-lot bot could use

| Information | Desk access | Our access (owned data, no paid feeds) | Horizon at which it matters (sources) |
|---|---|---|---|
| Cash basis, customer flow, crush plans | private, real time | none | days to months (ADM, Bunge, Dahlgran) |
| Board crush (ZS, ZM, ZL futures) | real time | yes, from ZM MBO and ZS/ZL MBP-1 | days to weeks for the margin anchor (R3a); intraday lead-lag is R3a/M2 |
| USDA reports (WASDE etc.) | public, same second | release times yes; surprise needs analyst surveys we do not own | minutes: absorbed in under 10 minutes (Lehecka et al., via Anderson et al.) or still moving after 30 minutes in soybeans (Anderson et al.); R4 owns the event design |
| NOPA crush | subscribers at release | release date yes; numbers not owned | monthly; no intraday study found (R4) |
| Export sales / inspections | public | release times yes; numbers not owned | weekly; inspections exclude meal |
| COT | public, 3 days stale | could be downloaded free (not owned now) | weekly or longer; no evidence at minutes |
| Weather, South America | paid weather services, local agents | none | overnight and weekend gaps (R4 section 4); no intraday study found |

---

#### E. Which edges desks describe as structural, and which a 1-lot retail trader could share

##### E.1 The edges in the evidence, by type

1. Liquidity provision (market making). HFT-type accounts trade about 25% of soybean volume on average and 36% in
   2020 (Coughlan and Orlov), earn the spread, and are hurt when they must trade aggressively to cut inventory
   (same source: "aggressive trading, such as those observed when HFTs trade directionally to reduce their
   positions"). The edge rests on speed and queue position. E.31 measured the outcome for us directly: a resting
   1-lot at the ZM touch under the trade-through rule had a gross 10 s edge of -0.970 ticks per fill (reports/
   E.31_RETURN.md section 3.5; V50 closed passive spread capture). NOT shareable.
2. Hedging-pressure (risk-transfer) premium. Speculators supply insurance to commercial hedgers and earn a premium;
   hedgers are contrarian and speculators are momentum traders (Kang, Rouwenhorst and Tang); index traders now also
   supply insurance (Brunetti and Reiffen). Horizon: weeks; size about 0.30% over days 5-10 after the COT release,
   cross-sectional. Shareable in principle by anyone holding positions for weeks; NOT at minutes (C.2 scale check:
   about 12 ZM ticks over 6 days).
3. Predictable flow (index rolls, settlement-period trading). BCOM rolls ZM on business days 6-10 of five months a
   year at settlement prices; asset managers trade "near the settlement period" (Fett and Haynes); the calendar spread
   moves with CIT roll progress (Brunetti and Reiffen) but the price impact on outrights in grains is "negative and
   very small, averaging only about two basis points" (Aulerich, Irwin and Garcia), and predictable roll days bring
   MORE liquidity, not predators (Bessembinder et al., crude oil). For a 1-lot on the outright: the flow is mostly in
   the spread book and at settlement, and the outright effect is about 2 basis points, i.e. at an illustrative
   400 USD/short ton, 0.0002 x 400 = 0.08 USD = 0.8 tick a day (my arithmetic; assumption stated), below the 1.59
   tick market-order break-even at Topstep (reports/stage_e28_ranking.md, rank 6 row "topstep | ZM", mu*_mkt 1.59).
   Weakly shareable, as a stratum (roll days versus others), not as a signal.
4. Information (fundamental). Merchants see cash basis, customer orders and crush plans; weather desks buy forecasts.
   That edge is private and slow (days). Public-release information is incorporated in seconds to tens of minutes
   (D.1 item 5). NOT shareable for the private part; the public-release part is R4's family 2.
5. Order-book information at the millisecond scale. Algorithmic proprietary traders respond to executions in under
   200 ms for half of messages in the E-mini (Fishe, Haynes and Onur); a 300-1,000 ms bot loses any race. Spoofing
   enforcement (CFTC 7865-19) shows large resting orders on the ZS/ZM/ZL books can be placed to be cancelled, so naive
   book imbalance can be gamed. NOT shareable at the race level.

##### E.2 Latency arithmetic for a minutes-scale signal (standard ZM numbers, random-walk assumption)

Assumption: random-walk scaling sigma_h = sigma_1m x sqrt(h / 1 minute), with sigma_1m = 3.15 ticks (E.28 A0
Table 1, ZM standard window). Then:
- h = 1 s = 1/60 min: sigma = 3.15 x sqrt(1/60) = 3.15 x 0.1291 = 0.407 ticks.
- h = 300 ms = 0.005 min: sigma = 3.15 x sqrt(0.005) = 3.15 x 0.0707 = 0.223 ticks.
- Check: 0.407 / 0.223 = 1.83, and sqrt(1000/300) = sqrt(3.33) = 1.83. Consistent.
So the price noise added by a 300-1,000 ms delay is 0.2-0.4 ticks (one standard deviation), small next to the 1.59
tick break-even, provided the signal itself decays over minutes. A signal that decays within a second (book races,
release-second trading) is out of reach regardless. The latency question is therefore "how fast does the signal
decay", and only signals whose information half-life is well beyond one second qualify. This is an argument, not a
measurement; E.33 can check it by delaying entries by 1 s in the frozen pipeline (a design item for the lead).

##### E.3 What a 1-lot at 300-1,000 ms could plausibly share (sources' mechanisms only; no data looked at)

- Plausible, testable at minutes: (i) the slow part of the reaction to public releases (soybeans still moving after
  30 minutes per Anderson et al.; contested by Lehecka et al.); (ii) commercial or index flow concentrated at known
  times (settlement window, BCOM roll days) as a STRATUM or regime feature; (iii) signed large-trade flow in the ZM
  MBO feed if large aggressive trades are informed (Frino et al., abstract only); (iv) crush-relative moves, where a
  merchant's hedge in one leg moves ZM before ZS/ZL catch up (R3a, M2).
- Implausible: spread capture (E.31), latency races, private information, COT at minutes, trading weather or South
  American news ahead of desks with paid feeds.

---

#### F. What this means for a ZM directional search

Mechanisms worth testing (for the lead to weigh; no decision taken here):
1. Time-of-day and calendar strata from documented flows: the 13:14-13:15 CT closing range and settlement window
   (asset managers, index replication, HFT inventory flattening per Coughlan and Orlov), BCOM roll days 6-10 in
   Feb/Apr/Jun/Oct/Dec, COT Friday afternoon to Sunday open, Thursday export-sales overnight, NOPA days. Use them
   as strata or interaction features, not as stand-alone signals: the documented outright effects are about 2 basis
   points a day or less.
2. Signed aggressive volume by trade size on ZM MBO (large trades as a proxy for informed or commercial flow; Frino
   et al. abstract; Fett and Haynes on large, infrequent asset-manager trades). M1 owns the feature definition.
3. Reversal versus continuation after large 1-minute moves, measured on MID-quotes. Jones's corn evidence shows that
   most big 1-minute moves are not half reversed, and that trade-price autocorrelation is mostly bid-ask bounce.
4. Post-release drift (soybeans after WASDE, Anderson et al.), only if R4 recommends it and a surprise proxy can be
   built from owned data (for example, the first 5-minute return as the market's reading of the surprise; a design
   choice for the lead).
5. Book imbalance with a spoofing guard: test variants that drop large orders cancelled within a short time
   (CFTC 7865-19 pattern).

Mechanisms to drop, and why:
- COT positioning as a minutes-scale signal: no forecasting power at weekly horizons in soybean meal (Sanders, Irwin
  and Merrin, Table 1, noncommercials, soybean meal: p-values 0.929, 0.929, 0.687, 0.921; the last entry, 0.000,
  is the "Direction (sum of beta_j x 10^2)" column, not a p-value) and the only robust effect is a cross-sectional weekly
  premium of about 12 ZM ticks over 6 days.
- Front-running index rolls on the outright: outright impact negative and about 2 basis points (Aulerich et al.),
  liquidity improves on predictable roll days (Bessembinder et al.); the roll effect lives in the calendar spread.
- Merchant hedge timing: no source gives an intraday timetable; merchant orders follow private cash deals and are
  partly executed as packages off the outright book.
- Spread capture or queue-race strategies: closed by E.31 and V50; HFT-type accounts own this edge.

---

#### P. Planner pointer verification (owned by R2)

| Pointer | Status | Evidence |
|---|---|---|
| Li, Wang and Diersen (NCCC-134 2024): what it studies, does it bear on desks or flows | VERIFIED as to content; it does NOT bear on desks or flows | Full text read (LiWangDiersen_NCCC134_2024.pdf). Title "Do Agricultural Commodity Price Spikes Always Stem from News?"; corn futures only ("The analysis of price spikes is based on corn futures trading data"), 5-minute prices 2013-2022, day session; "a total of 3,419 jumps"; "994 news-related clusters ... 32.13% of all clusters. The non-news-related clusters account for 67.87%"; news matched by day, not by minute. No trader, position or flow data. Relevant only as a pointer that non-news jumps are common (a stratum for idea family 5). See P0. |

---

#### G. Evidence index (files in pages/R2_ag_desks/, every row in log.tsv)

| Source | Label | File | Used in |
|---|---|---|---|
| ADM 10-K FY2023 Item 7A / 1A | firm | ADM_10K_FY2023_Item7A_quotes.txt (quotes only; SEC 403) | A.1, D.1 |
| Bunge 10-K FY2007 Note 1 | firm | Bunge_10K_FY2007_hedge_quotes.txt (quotes only) | A.1, D.1 |
| Dahlgran 2005 JARE | academic | Dahlgran_JARE2005.pdf | A.1, D.1 |
| Haynes and Roberts 2015, 2017 (CFTC OCE) | regulator | CFTC_oce_automatedtrading.pdf, _update.pdf | A.1, B.1 |
| Fett and Haynes 2017 (CFTC OCE) | regulator | CFTC_oce_futureslandscape.pdf | A.1, B.1, E |
| Coughlan and Orlov 2022 (CFTC) | regulator WP | CoughlanOrlov_CFTC_2022_HFT.pdf | B.1, E |
| Janzen 2018 (K-State talk) | academic/extension | Janzen_KSU_HFT_ag.pdf | B.1, D.1 |
| Jones 2018 (K-State talk) | academic talk | Jones_KSU_HFT_presentation.pdf | B.1, F |
| CFTC PR 7865-19 | regulator | CFTC_PR_7865-19_soybean_spoofing.html/.txt | B.1, E, F |
| CBOT Submission 11-489 (CFTC-hosted) | exchange filing | CFTC_CBOT_rul120811_options_MM_program.pdf | B.1 |
| Gousgounis and Onur 2016 (CFTC OCE) | regulator WP | CFTC_oce_effectofpitclosure.pdf | B.1, D.1 |
| Fishe, Haynes and Onur, Speed and Latency Part 2 (CFTC OCE) | regulator WP | CFTC_oce_speedandlatency2.pdf | B.1, E (Part 1 saved, not cited) |
| CFTC COT pages and notes | regulator | CFTC_COT_index, CFTC_COT_explanatory_notes, CFTC_disagg_* | C.1 |
| Sanders, Irwin and Merrin 2009 JARE | academic | SandersIrwinMerrin_JARE2009.pdf | C.2, F |
| Kang, Rouwenhorst and Tang (JF 2020 draft; NBER w19670) | academic | KangRouwenhorstTang_2016draft.pdf, _NBERw19670.pdf | C.2, E |
| BCOM Methodology Feb 2026 | firm (index provider) | BCOM_Methodology_FEB2026.pdf | C.3 |
| Aulerich, Irwin and Garcia (NBER w19065) | academic | AulerichIrwinGarcia_NBERw19065.pdf | C.3, E, F |
| Bessembinder et al. 2015 draft | academic | Bessembinder_etal_predictable_trades_2015draft.pdf | C.3, E |
| Brunetti and Reiffen (CFTC OCE) | regulator WP | CFTC_OCE_commodityindextrading.pdf | C.5, E |
| Anderson, McKenzie and Noyes 2024 | academic (conference) | AndersonMcKenzieNoyes_NCCC134_2024.pdf | D.1, E, F |
| Li, Wang and Diersen 2024 | academic (conference) | LiWangDiersen_NCCC134_2024.pdf | P0, P |
| USDA AMS WA_GR101 | government | USDA_AMS_wa_gr101_export_inspections.txt | D.1 |
| NOPA data page | industry association | NOPA_datastatistics.html | D.1 |
| Frino et al. 2016 JFM; Cheng, Kirilenko and Xiong 2015 | academic | none (OpenAlex abstracts only) [unverified] | C.5 |
| Mou thesis | academic | Mou_ColumbiaThesis.pdf is a bot-check HTML page [unverified] | C.3 |

Saved but not used: CFTC_oce_liquidityfuturesmarkets.pdf (no grain content found by grep), CFTC_oce_speedlatency.pdf
(Part 1, Treasuries/E-mini), CFTC_OCE_whitepapers_index.html (discovery), BoC_Brunetti_authorpage.html (discovery),
USDA_FAS_export_sales_about.html (0 bytes), USDA_FAS_ESR_program.html (403 page), NOPA_monthly_crush.html (404 page).

#### H. Search log, stopping and gaps

- Re-spawned at 02:34 PDT 2026-10-27 after the first run stopped at 00:51; sections P0, A, B.1 (items 1-5), C.1-C.4
  were on disk and kept; this run added B.1 items 6-12, B.2, C.5, D, E, F, P, G, H.
- WebSearch calls in this run: 4 (CONAB reaction; weather-model intraday; CFTC-hosted CBOT market maker filings; grain
  prop job descriptions). The first run's count is not recorded in the log [gap]. Crossref: 3 queries; OpenAlex: 2.
- Blocks: sec.gov 403 to undeclared User-Agent (quotes via Firecrawl directQuote only); fas.usda.gov 403 to curl and
  WebFetch (Scrapling not tried: the terms check was not done, so the route was not used); Columbia Academic Commons
  bot check; a guessed Bank of Canada URL 404. No cmegroup.com fetch (stage rule).
- Stopping: (a) merchants: 4 full-text sources plus the pit-closure WP, last 3 queries nothing new on intraday timing;
  (b) prop shops: met (see B.2); (c) met (see C.5); (d) release timing deferred to R4; weather and South America:
  null after 3 queries; (e) synthesis from the above.

## R3a. Soybean complex economics: crush, cointegration, spreads, oil-share regime

Source file: reports/stage_e32_briefs/R3a_crush.md (sha256 455b9e2b8733d53da8eab5f6575936603d2f14a40bdf92f4cc959cb49b07390e).

### R3a_crush: soybean-complex economics for a minutes-to-hours ZM directional search

Stage E.32, Part R3 (first half). Worker CrushEconomics-OpusHigh. Started 2026-10-26 23:03 PDT.
Evidence pages and log: reports/stage_e32_briefs/pages/R3a_crush/ (log.tsv). Scratch: reports/stage_e32_briefs/work/R3a_crush/.
No market data was read and no statistic was derived from data. Every number below is either quoted from a saved
full text (file named) or is arithmetic on contract specifications and quoted numbers, shown step by step.
Source labels: [academic], [practitioner], [regulator], [exchange], [firm], [extension] (university extension
service, e.g. farmdoc daily, Southern Ag Today; written by academics but not peer reviewed).

Status of sections: 1-11 done (sections 7-11 written after a re-spawn, 2026-10-27 00:16-00:22 PDT).

---

#### 1. Contract arithmetic: the board crush, its units, the 10:11:9 and 10:12:9 ratios, and tick conversions

##### 1.1 Facts

- Contract units and ticks used here (E.28 owned-data table, reports/stage_e28_briefs/A0_contract_stats.md lines
  114-117, quoted: `| ZM | yes | 0.10 | 10.00 | 3.15 |`, `| ZS | yes | 0.0025 | 12.50 | 3.11 |`,
  `| ZL | yes | 0.0001 | 6.00 | 5.52 |`): ZM tick 0.10 USD per short ton, 10.00 USD; ZS tick 0.0025 USD/bu
  (0.25 cents/bu), 12.50 USD; ZL tick 0.0001 USD/lb (0.01 cents/lb), 6.00 USD. Contract sizes follow: ZM
  10.00/0.10 = 100 short tons; ZS 12.50/0.0025 = 5,000 bu; ZL 6.00/0.0001 = 60,000 lb. Poitras's course note
  states the same sizes [academic teaching note]: "Weight of one CME soybean contract: (5000 bu.)(60 lbs) =
  300,000 lbs. / Weight of one CME soy meal contract: (100 tons)(2000 lbs.) = 200,000 lbs. / Weight of one CME soy
  oil contract: 60,000 lbs." (poitras_soycrush_wpd.pdf.txt). CME's own pages were not fetched (stage rule).
- The CME "board crush" yield, quoted second-hand from CME by farmdoc daily [extension]: a bushel of soybeans
  yields "11 pounds of soybean oil, 44 pounds of 48 percent protein soybean meal, 4 pounds of hulls and 1 pound of
  waste" (CME Group)" (Janzen and Wang 2025, farmdoc_fdd101325_oilshare.pdf.txt, Appendix).
- The older USDA convention is 48 lb of meal. Rechner and Poitras (1993) [academic]: "a (60 lbs.) bushel of
  soybeans yields 11 lbs. of oil and 48 lbs. of meal [USDA (1988)]" and "Given the CBOT contract specifications,
  this translates into 10 soybeans, 12 meal, and 9 oil contracts for a balanced position."
  (rechner_poitras_1993.pdf.txt lines 105-116). Smith (2021) [extension] explains the two conventions: "There are
  two common approaches to estimating the quantity of soybean meal: (1) the one depicted above, 48 lbs of soybean
  meal at (44% protein) or (2) 44 lbs of soybean meal (48% protein), which is used by CME group."
  (tamu_meal_or_oil.txt).
- Poitras's note [academic teaching note] names both ratios: "The CME Soybean Crush Guide (p.7) (see BUS 419
  webpage) uses 10 Soybean, 11 Soy Meal and 9 Soy Oil" (poitras_soycrush_wpd.pdf.txt). So 10:11:9 is the CME
  (44 lb) ratio and 10:12:9 the USDA-1988 (48 lb) ratio used by Rechner and Poitras.
- Actual yields drift: farmdoc [extension] reports "the standard board crush margin calculation assumes 11 pounds of
  each 60-pound bushel of soybeans, or 18.3%, is oil" while "Oil extraction rates have increased and now are
  routinely around 20% of output" (farmdoc_fdd091025_extraction.pdf.txt lines 57-60); and NOPA data put oil "from
  just more than 11 pounds to about 12 pounds per bushel" and meal "consistently between 47 to 48 pound per
  bushel. USDA crush data indicate a meal share closer to 44 pounds." (farmdoc_fdd101325_oilshare.pdf.txt,
  Appendix). The board formula's weights are a convention, not the physical yield.

##### 1.2 Equations

Board crush margin per bushel (CME 44-lb convention):

    C_44 [USD/bu] = (44/2000) * M + (11/100) * O - S/100
                  = 0.022 * M + 0.11 * O - S/100

    M = ZM price, USD per short ton; O = ZL price, cents per lb; S = ZS price, cents per bu.
    44/2000 = 0.022 short tons of meal per bushel; 11 lb oil per bushel times O/100 USD/lb = 0.11 * O USD/bu.

USDA-1988 (48-lb) convention: C_48 = 0.024 * M + 0.11 * O - S/100.

In cents per bushel: C_44 [c/bu] = 2.2 * M + 11 * O - S.

Oil share of crush output value (the "oil share"): OS = 0.11 * O / (0.022 * M + 0.11 * O) under 44 lb, or
0.11 * O / (0.024 * M + 0.11 * O) under 48 lb (farmdoc's definition: "The share of crush value for each component
is the revenue for each component as a percentage of total revenue", farmdoc_fdd101325_oilshare.pdf.txt).

Leg sensitivities of C_44 (cents/bu per one tick of each leg), from the partial derivatives:
- dC/dM = 2.2 c/bu per USD/ton; one ZM tick (0.10 USD/ton) = 2.2 * 0.10 = 0.22 c/bu.
- dC/dO = 11 c/bu per c/lb; one ZL tick (0.01 c/lb) = 11 * 0.01 = 0.11 c/bu.
- dC/dS = -1; one ZS tick = 0.25 c/bu.

##### 1.3 Worked arithmetic

(a) Ratios. 10 ZS = 10 * 5,000 bu = 50,000 bu.
- Meal at 44 lb/bu: 50,000 * 44 = 2,200,000 lb = 2,200,000/2,000 = 1,100 short tons = 1,100/100 = 11 ZM.
- Meal at 48 lb/bu: 50,000 * 48 = 2,400,000 lb = 1,200 short tons = 12 ZM.
- Oil at 11 lb/bu: 50,000 * 11 = 550,000 lb = 550,000/60,000 = 9.17 ZL, rounded to 9 (540,000 lb, i.e. 10.8 lb/bu).
- Check against Poitras's husk arithmetic: 10:11:9 leaves 3,000,000 - 2,200,000 - 540,000 = 260,000 lb; the note
  says "(300,000)(10) - (200,000)(11) - (60,000)(9) = 260,000 lbs. of husks". 10:12:9 leaves 60,000 lb; the note
  says "= 60,000 lbs. of husks". Both match.

(b) Dollar value of 1 cent/bu of crush on the 10-lot position: 50,000 bu * 0.01 USD/bu = 500 USD. Rechner and
Poitras: "when trading 10 soybean, 12 meal, and 9 oil contracts, a 1-cent per bushel change in the GPM represents a
$500.00 change in the value of the position" (rechner_poitras_1993.pdf.txt line 133). Match.

(c) One ZM tick in crush units. 0.022 ton/bu * 0.10 USD/ton = 0.0022 USD/bu = 0.22 c/bu. Check by dollars: 11 ZM *
10 USD = 110 USD per tick on all 11 lots; 110 USD / 50,000 bu = 0.0022 USD/bu = 0.22 c/bu. Match.
Inverse: 1 c/bu / 0.22 c/bu per tick = 4.545 ZM ticks. So a 1 c/bu crush dislocation closed entirely by ZM is
about 4.5 ZM ticks (45.45 USD per ZM lot). Under 48 lb the factor is 0.24 c/bu per tick and 1/0.24 = 4.17 ticks.

(d) Rechner and Poitras's execution-cost arithmetic as an independent check of the leg conversions on 10:12:9
(two ticks per leg per round trip): "0.5 + 0.48 + 0.216 = 1.196 cents per bushel" (line 142). Recompute: beans
2 * 0.25 = 0.50 c/bu; meal 2 ticks * 0.10 USD/ton * 0.024 ton/bu = 0.0048 USD/bu = 0.48 c/bu; oil 2 ticks * 0.01
c/lb * 10.8 lb/bu = 0.216 c/bu (9 lots * 60,000 lb / 50,000 bu = 10.8 lb/bu). Sum 1.196 c/bu. Match.

(e) One-minute volatility of each leg in crush units on the E.28 standard numbers (2022-11-01..2023-10-31, front
contract): ZM 3.15 ticks * 0.22 = 0.693 c/bu; ZS 3.11 ticks * 0.25 = 0.778 c/bu; ZL 5.52 ticks * 0.11 = 0.607 c/bu.
The three legs move the crush by similar amounts per minute, so none is negligible. An upper bound on the crush's
one-minute SD (legs perfectly anti-aligned in their crush contribution) is 0.693 + 0.778 + 0.607 = 2.08 c/bu; the
legs are positively correlated in price and beans enter with the opposite sign, so the true SD is far lower. No
correlation is computed here (no new statistic from data).

(f) Oil share, worked on quoted futures prices. Smith (2021) [extension] quotes futures moving "from $417.60/ton in
January 2021 to $312.90/ton in October 2021", oil "from 44.62 cents/lb to 58.62 cents/lb", beans "from $13.70/bu
to $11.88/bu" (tamu_meal_or_oil.txt). October 2021 under 48 lb: meal 0.024 * 312.90 = 7.510 USD/bu; oil 0.11 *
58.62 = 6.448 USD/bu; OS = 6.448/(7.510 + 6.448) = 6.448/13.958 = 46.2%; margin = 13.958 - 11.88 = 2.078 USD/bu.
Smith reports "54% of soybean value attributed to meal and 46% to oil" and "the crush margin was $2.08" (as of
October 13, 2021). Match. Under 44 lb: meal 0.022 * 312.90 = 6.884; OS = 6.448/13.332 = 48.4%; C_44 = 13.332 -
11.88 = 1.452 USD/bu. The convention moves the oil share by about 2 points and the margin by 0.6 USD/bu at these
prices, so any oil-share feature must name its convention. January 2021 under 48 lb: 0.024 * 417.60 = 10.022;
0.11 * 44.62 = 4.908; OS = 4.908/14.930 = 32.9% (Smith: meal "65%" of value for "the first three months of 2021",
i.e. oil about 35%, a three-month average, so a rough rather than exact match).

##### 1.4 What this means

- A 1 c/bu crush residual is 4.5 ZM ticks if ZM alone closes it. E.28's Topstep ZM market-order break-even is 1.59
  ticks (reports/stage_e28_ranking.md line 130, row `| 6 | topstep | ZM | ... | 0.59 | 1.59 | ...`, column
  mu*_mkt). So a residual of 1.59/4.545 = 0.35 c/bu closed fully by ZM pays one break-even. Whether ZM is the leg
  that closes it is an empirical question (Section 5).
- The weights are conventions. A residual built on 0.022/0.11 will carry a slow drift as true yields move (oil
  18.3% to about 20% since 2020). For minutes-to-hours horizons this drift is negligible within a day but matters
  for any level-based (not change-based) residual estimated over months.

---

#### 2. The oil-share regime change (renewable diesel) and the discovery/test split

##### 2.1 Facts

- Janzen and Wang (farmdoc daily, 2025-10-13) [extension], weekly Illinois processor prices, 2007-2025: "Between 2013
  and 2020, the oil value share ranged between 25 to 35 percent. Since 2020, it has only rarely been below 35
  percent. In both 2021 and 2025, it briefly reached 50 percent." and "there is a stark jump in the oil value share
  in late 2020 that has persisted to the present" (farmdoc_fdd101325_oilshare.pdf.txt).
- Same source on margins: "Since late 2020, crush margins have periodically increased and become considerably more
  volatile. Changes in crush margins are much larger now than they were before 2020."
- Same source, the key regime statistic. Weekly first-difference regressions of soybean price changes on meal and
  oil price changes: May 2007-September 2020 "dSB(t) = 0.000 + 0.511 dSBM(t) + 0.232 dSO(t), R2 = 0.791", and "The
  results are similar for the 2017 to 2020 period after Irwin concluded his analysis but before the renewable
  diesel boom period." For October 2020-September 2025: "dSB(t) = 0.000 + 0.451 dSBM(t) + 0.070 dSO(t), R2 = 0.322"
  and "It appears a previously stable relationship among soybean crush components has broken down." Also: "the
  correlation between these price changes has broken down." Units there are USD per pound for all three (they
  "convert all prices to dollars per pound"); the regression is weekly cash prices, not futures, not intraday.
- Price levels: "The soybean oil price nearly tripled from $0.26 per pound to $0.94 per pound" between late 2020
  and early 2022, while "Soybean prices roughly doubled and soybean meal prices increased by roughly 60%."
- Physical yields shifted at the same time: "the realized US soybean oil extraction rate jumped to 19.7% in late
  2020 and then continued to increase to around 20.0% for much of 2025. (November and December in both 2022 and
  2023 were short-lived exceptions to this otherwise persistent shift.)" (farmdoc_fdd091025_extraction.pdf.txt
  lines 112-114).
- Smith (Southern Ag Today, 2021-10-25) [extension]: "the percent of value derived from meal and oil changed in April
  2021. For the first three months of 2021, soybean meal was 65% of the soybean value, the same as the January 2006
  to October 2021 average." Drivers named: vegetable-oil stocks ("days-on-hand ... to drop from 41.7 days ... to
  38.5 days") and "current and potential demand for biodiesel derived from soybean oil" (tamu_meal_or_oil.txt).

##### 2.2 Mapping onto E.32's windows

- Sealed test window 2017-05..2020-11: falls inside the pre-boom regime (oil share 25-35%, weekly R2 about 0.79,
  stable leg relations), apart from its last months (the "stark jump" is dated "late 2020"; Janzen and Wang's
  second regression starts October 2020). Other events inside it (US-China trade war 2018-19, Covid 2020) are not
  covered by these sources; the planner's mention of them is [unverified] here.
- Discovery window 2020-12..2024-02: entirely inside the renewable-diesel regime (oil share mostly above 35%, peak
  near 50% in 2021, weekly R2 about 0.32, more volatile margins, the oil price peak of early 2022).
- Therefore the discovery data contain a crush whose legs co-move LESS tightly (at the weekly horizon) than in the
  test window. Two opposite risks follow: (i) a crush-residual signal tuned on discovery could find wider, noisier
  residuals and fewer clean reversions, then meet a test window where reversion is tighter but residuals smaller
  (fewer triggers at a fixed threshold, smaller gross per trade); (ii) fixed ZM/ZS/ZL betas fitted on 2020-24 will
  be wrong in 2017-20 (the oil coefficient fell from 0.232 to 0.070 in the weekly regression). This supports the
  planner's suggestion of adaptive (causal rolling) betas and thresholds in units of a rolling residual SD rather
  than fixed cents.
- No source found measures the regime change at intraday horizons. The weekly evidence does not say whether
  minute-scale leg co-movement changed. [gap, stated as such]

##### 2.3 Worked example: what the regime shift does to ZM's weight in the crush

Using the weekly coefficients as given (USD/lb units, so they are value-per-pound sensitivities, not contract
hedge ratios): the share of a soybean price change "explained" per unit oil change fell by 0.232 - 0.070 = 0.162,
i.e. to 0.070/0.232 = 30% of its earlier size, while the meal coefficient changed by 0.511 - 0.451 = 0.060, i.e. to
0.451/0.511 = 88%. Check: 0.070/0.232 = 0.3017; 0.451/0.511 = 0.8826. Reading: soybean price changes became much
less tied to oil and only slightly less tied to meal. For a ZM-centred residual this is mildly reassuring (the
beans-meal link held better than the beans-oil link), but it is weekly cash-price evidence.

---

#### 3. Intraday cointegration of ZS, ZM and ZL: Zhou, Bagnarosa, Gohin, Pennings and Debie

The only study found that tests crush cointegration inside the trading day on CME data. Two versions read in full:
the journal article (J. Commodity Markets 30 (2023) 100314, open access CC BY, zhou_jcm2023_wur.pdf.txt) and the
NCCC-134 2022 conference version with the supplementary tables (zhou_nccc134_2022.pdf.txt). [academic]

##### 3.1 Facts (verbatim)

- Data: "The high-frequency data used in this study covers the total trading activity of 2015, amounting to 243
  trading days." (JCM line 587). One-minute snapshots, chosen "to limit the Epps effect" (NCCC lines 890-892).
- Sessions: "the electronic trading session from 7PM to 7.45AM (session 1) and the market trading session from
  8.30AM to 1.20PM (session 2), during which most of the trades take place." (NCCC lines 893-895). Note: in 2015
  the day session closed 13:20 CT; E.32 uses 08:30-13:20 for the day session too.
- Model (JCM Eq. (10)): "dP_t = c_0 + Pi P_{t-1} + sum_{j=1}^{p-1} Gamma_j dP_{t-j} + e_t ... where the low-rank
  matrix Pi = kappa beta' can be decomposed into two rank h-matrices kappa and beta of dimensions (n x h) and
  e_t ~ N(0, Sigma)." It is cast in state-space form (Eq. (12), x_t = F x_{t-1} + G e_t) with idle (untraded)
  prices treated as missing and estimated by EM.
- Plain Johansen on raw one-minute prices finds little: "Hardly any cointegration was detected using Johansen's
  approach, regardless of the matching method applied." Table 2 (JCM): Johansen "all price" 64 cointegrated days,
  ZSmatch 69, ZLmatch 70, ZMmatch 68; the missing-data-filtered state-space test 180 days, 11 months, 3 quarters.
- Session effect, NCCC supplementary Tables 7-9 (ZS open-interest rollover row): session 1 (overnight) "52 / 2 / 1"
  (day/month/quarter); session 2 (day) "180 / 11 / 3"; session 1 + session 2 together "52 / 2 / 1". Text: "prices
  in session 1 are so greatly affected by market noise that even the combining of both sessions yields no
  additional information about the joint dynamics of asset prices and, even worse, prevents identification of
  the cointegrated days." (NCCC lines 2649-2653). JCM text: "A high level of cointegration is indeed observed during
  session 2 trading hours, which fades away during session 1." (JCM lines 745-746).
- Sampling frequency: "The two-minute daily data set allows us to detect 229 days of cointegration (versus 180
  using the 1-minute daily data set)" (NCCC line 2756).
- USDA days: "the stronger intraday cointegration observed on average on USDA announcement days, although the
  number of observations available is limited." (JCM lines 746-747).
- Cointegrating vector (JCM Table 4, cointegrated days only, normalised ZS = 1, missing-data filter): Median ZL
  -0.11, ZM -0.19; Average -0.09, -0.21; quartiles 25% -0.17, -0.24 and 75% -0.06, -0.14; StDev 0.28, 0.28; "CME
  (physical)" -0.11, -0.22. Johansen: median -0.13, -0.17, StDev 0.5, 0.47.
- Speed of adjustment, not vector, depends on volume: "traded volumes, epitomizing disagreement on market
  expectations, mainly influence the speed of convergence towards the stationary cointegrated joint process,
  rather than the cointegrating vector itself." (JCM conclusion, line ~984).
- Leadership: "If the traded volumes of soyoil relative to soybean increase, we can expect soymeal to even more
  significantly Granger cause the soyoil dynamics ... Nevertheless, the lower the traded volumes of soymeal
  relative to soyoil, the less soymeal prices will Granger cause soybean prices" (JCM lines 814-820). And:
  "important potential trading volumes in the main market, the soybean market in our case, or a lack of liquidity
  in the secondary markets, i.e., soybean meal and oil, act as a counterbalance and may discourage the fully
  informed traders from building correcting trades to enforce the cointegration relationship." (JCM conclusion).
- Rollover: "some intermediary contract maturities are not considered by informed traders throughout the year,
  thus leaving unused their capacity to counterbalance on an intraday basis" (JCM conclusion); the ZS
  open-interest rollover gave the most cointegrated days (NCCC Table 8: 180 vs monthly rollover 132).
- No half-life, no loading (kappa) magnitudes in time units, and no trading rule are reported. A grep of both
  full texts for "half" finds no half-life. The kappa results are reported only as regression coefficients of
  kappa ratios on volume ratios (JCM Table 3).

##### 3.2 Worked arithmetic

- Share of days cointegrated, day session, 1-minute: 180/243 = 0.741 (74%). At 2-minute: 229/243 = 0.942 (94%).
  Overnight session: 52/243 = 0.214 (21%). Plain Johansen, day session: 64/243 = 0.263 to 70/243 = 0.288.
- The ZM weight: median -0.19 against physical -0.22, a gap of 0.03, i.e. 0.03/0.22 = 13.6% smaller in magnitude.
  Daily SD 0.28 is larger than the median magnitude itself (0.28/0.19 = 1.47), and the interquartile range is
  -0.24 to -0.14 (width 0.10). So a single day's estimated vector is a noisy estimate of the physical weights; a
  fixed physical vector or a long-window estimate is the sensible residual for a trading signal.
- Units caveat [unverified, needs reviewer]: with prices in CBOT quote units (ZS cents/bu, ZL cents/lb, ZM USD per
  short ton) the board crush is S - 11 O - 2.2 M; Marowka et al. [academic] write "the Chicago Board of Trade
  (CBOT) quotes the crush spread as yt(1) - 11yt(2) - 2.2yt(3)" (marowka_spiral_b.pdf.txt lines 67-68). Normalised
  to ZS = 1 that is (1, -11, -2.2). Zhou's "CME (physical)" row (1, -0.11, -0.22) is reproduced only if ZS is in
  USD/bu and both ZL and ZM are in units 100 times smaller than cents/lb and 10 times smaller than USD/ton
  respectively, or under some other price scaling the paper does not state. The ratio of the meal to the oil
  weight is 2.2/11 = 0.2 in quote units but 0.22/0.11 = 2.0 in Zhou's table. The paper does not give its price
  units; the comparison "-0.19 vs -0.22" is internally consistent within the paper, but the vector cannot be
  applied to quote-unit prices without knowing the scaling.
[MathReview A-12 (lead: accepted): the stated scaling does not reproduce the row (ZS in USD/bu, ZL in 0.01 c/lb units and ZM in 0.10 USD/ton units give (1, -0.0011, -0.0022)); two scalings reproduce (1, -0.11, -0.22): (A) ZS in c/bu, ZL in ticks of 0.01 c/lb, ZM in ticks of 0.10 USD/ton (11 x 0.01 = 0.11; 2.2 x 0.10 = 0.22), M2's reading in M2 (c) (M2:318-319), or (B) ZS in USD/bu, ZL in c/lb, ZM in units of 10 USD/ton (0.11; 0.022 x 10 = 0.22), while quote units give (1, -11, -2.2). Zhou's text states no units and uses "the last trading price" (zhou_etal_nccc134_2022.pdf.txt line 1019); the internal evidence favours a tick-like scaling, and the conclusion of this section (compare -0.19 with -0.22 only as a ratio inside the paper; use a fixed physical vector or a long-window estimate for the signal) stands.]

##### 3.3 What it implies for a ZM search

- Day-session (08:30-13:20) crush residuals are mostly stationary within the day at 1-2 minute sampling (in 2015);
  overnight residuals mostly are not. This is direct support for computing any crush residual on day-session data
  and for treating overnight crush moves as weakly anchored.
- Who adjusts depends on relative volumes (the volume ratios move the kappa ratios), so "which leg adjusts" is a
  state variable, not a constant. A ZM-only trade on a crush residual should be conditioned on relative volume
  (ZM vs ZS vs ZL) and, per the theory, it works best when the byproduct markets are liquid relative to beans.
- The study is 2015 only, one year, a different regime (pre-renewable-diesel) from both E.32 windows, and reports
  no speed in minutes, so it cannot size the signal.

---

#### 4. Crush-spread trading rules: profitability and decay

##### 4.1 Facts, in date order of the samples

- Johnson, Zulauf, Irwin and Gerlow (JFM 1991, 11(1) 25-37) [academic; full text not read: the NCR-134 1990
  precursor johnson_etal_nccc1990.pdf is a scanned image (pdftotext returns 81 words, no OCR tool on this
  machine); evidence is second-hand, marked]. Per Rechner and Poitras: "Five trades are initiated at the closing
  price on the 15th of every month and then lifted at preset intervals: 1.5, 3.5, 5.5, 7.5, and 9.5 months" and
  quoting Johnson et al.: "Significant profits above transactions costs are not found at trade lengths of 1.5 and
  3.5 months, but are found at trade lengths of 5.5 months or longer" (rechner_poitras_1993.pdf.txt lines 69-78).
  Per Mitchell: sample "1966-1988"; "While 1.5 month trades result in an average loss of $156, profit increases to
  $3, $241, $235, and $418 as the trade length increases." (mitchell_jrfm2010_firecrawl.md line 101).
  [secondary, unverified against Johnson et al.'s own text]
- Rechner and Poitras (JFM 1993, 13(1) 61-75) [academic, full text read]: rule "If the GPM on the open is less
  (greater) than the previous day's close, a reverse crush (normal crush) spread is placed. In all cases, the
  position is liquidated on the close of the same day." Costs "1.5 cents per bushel" round trip. Daily open/close
  data, "February 1, 1978 to July 31, 1991", pit era. Aggregate table (OCR heading "Table IV", text calls it Table
  II), net of costs, filters 0 / 1 / 2 / 3 cents: mean profit per trade -0.36 / 0.35 / 1.02 / 1.74 c/bu; trades
  3352 / 1861 / 922 / 457; t-values -7.69 / 5.08 / 9.10 / 9.30; percent profitable 39.6 / 52.3 / 62.3 / 69.0.
  Key correlation, Table IA (1978-87): "(Close, - Open,) and (Open, - Close,-1) -0.49 (-23.7)"; Table IB
  (1987-91): "-0.43 (-14.2)". The single legs show no such effect: meal "-0.019 (-0.92)" in 1978-87 and "-0.067
  (-2.22)" in 1987-91. Authors: "it provides indirect support for the possibility of 'opening reversals'; or, in
  other words, the tendency of GPM to change direction at the open." Decay warning: "the small number of trades
  in 1990 combined with the poor performance of 1991 does raise concern ... a substantial upward shift in the GPM
  starting with the June 1, 1989 rollover date." Their explanation: "While the public is in on the close only
  the trading floor is in on the open."
- Simon (JFM 1999, 19(3) 271-289) [academic; full text not obtained (Wiley paywall; no author copy found);
  abstract from IDEAS, simon1999_ideas.html]: "deviations of the soybean crush spread from its long-run
  equilibrium were transitory during the sample period from January 1985 through February 1995. This equilibrium
  is characterized by strong seasonality and by a persistent uptrend in soymeal and soyoil prices relative to
  soybean prices. A tendency also exists for the crush spread to revert toward its most recent 5-day average.
  Simulations demonstrate that trading rules based on these results would have been profitable." Mitchell's
  summary of Simon: "the crush spread tends to revert toward its 5-day moving average with a half-life of
  deviations of about 3 days" and "Trades prove profitable after adjustment for transaction costs ($103.50 per
  round-trip trade)". [half-life is secondary via Mitchell; not seen in Simon's text]
- Liu (JFM 2005, 25(5) 491-514), hog-corn-meal analogue [academic, abstract only]: three series "cointegrated with
  one single cointegrating vector, whose coefficients are comparable to the ratios used by the United States
  Department of Agriculture"; "Ex-post trading simulations that utilize the cointegration results generate
  significant profits" (liu2005_ideas.html). Daily-to-longer horizon; included because the brief names it.
- Mitchell (JRFM 2010, 3(1) 63-96) [academic, full text read via Firecrawl, mitchell_jrfm2010_firecrawl.md]: data
  "June 4, 1984 through April 7, 2006", daily closes, "a naive 1:1:1 relationship". Entry when the spread deviates
  from its 5-day moving average by 200-400 USD, exit at 0-200 USD; costs 103.50 USD per round trip. Results:
  "Average profit ... ranges from a low of -$41.88 at limits of 100/80 to $122.17 at 400/80." The fourth (latest)
  time segment "gives negative average profit results, a higher standard deviation of profit, a lower percentage
  of profitable trades, and longer trade length." Replication of Simon: "A trader who bases their trading
  practices on the results for $200 limits reported by Simon would experience, over the 20-year period, average
  losses of $20 per trade rather than an approximate $200 average profit per trade as reported by Simon."
  Conclusion: "Unless further research demonstrates arbitrage limits (filters) with more appealing risk-return
  characteristics, the soybean crush spread should be considered an efficient market." Trade length: "profitable
  trades are significantly shorter than losing trades"; "no trade at any set of limits up to 400/200 produces a
  profitable trade in excess of 9 days". Also: "In October, 1992 the CBOT changed the soymeal contract
  specifications from 44% protein to 48% protein."
- Liu and Sono (JFM 2016, 36(11) 1057-1075), Dalian [academic, abstract only, jfm2016_v36i11_ideas.html]:
  cointegrated with "significant seasonality and consistent time trends"; "evidence of one-way information flow
  from the soymeal and soyoil markets to the soybean market"; "Trading simulations based on the mean-reverting
  tendencies of the cointegration relationship and 5-day averages of the commonly-used spread both generate
  positive returns."
- Dunis, Laws and Evans (book chapter, 2009) [academic; pointer only, purchase-only, not read]: per the search
  snippet, for "most of the models, trading costs all but eliminate any profit potential". [unverified: search
  snippet only]
- Gu and Lei (ICMMCT 2018, Atlantis) [academic, conference; read]: Dalian/Zhengzhou crush, daily, 2013-2016
  ("from January 4, 2013 to December 2016. The daily", atlantis_25900046.pdf.txt line 106). Low-tier venue; not
  used further.
- Abdoh and Chitavi (IREF 2025, vol. 101, 104186) "Mean reversion of the soybean crush spread: A new model and
  trading strategies" [academic]. Retrieval: ScienceDirect returns 403 to curl; no author or SSRN copy found in two
  searches; Scrapling not used (the page declares Elsevier "tdm-reservation" = 1); Firecrawl (route 4) in
  directQuote mode returned verbatim passages but not the raw page. Those passages are saved in
  abdoh_chitavi_firecrawl_directquote.txt; treat them as PARTIAL full text (the extractor chose the passages; table
  layouts are fragmentary). Abstract (IDEAS, abdoh_chitavi_ideas.html): "no study has examined how intraday
  deviations of soybean products from the processing relationship reflected in USDA estimates affect the soybean
  crush spread. We introduce a new market-based measure that captures these deviations in the short term ...
  trading strategies based on these findings would have been profitable, even after accounting for transaction
  costs. This analysis is based on 8650 trading days from September 1990 to May 2021."
  From the extracted passages:
  - Data: "futures prices captured at 10-min intervals" from tickdata.com; "We use non-missing intraday price data
    of beans and their products, which cover 8650 trading days."
  - The measure: a regression run "each day" of the intraday bean price on meal and oil prices, "Bean_t = a0 + a1
    Meal_t + a2 Oil_t + mu_t" (their Eq. (2)), whose coefficients "can be interpreted as the magnitudes of meal and
    oil inferred by market prices"; means "0.02 and 0.117, which are equivalent to 40 and 11.7 pounds". DEV-GCM
    (their Eq. (3)) values the gap between these market-implied yields and USDA yields at that day's prices.
  - Speed: "the transitory movements from the long-run equilibrium, which lasts 10.4 days on average"; half-life
    "in terms of days as (ln(0.5)/ln(1+b1))"; Table 4 half-lives "38.81 days" (seasonal-dummy-and-trend residual)
    and "28.41 days" (adding lagged DEV-GCM); with 30- and 60-day moving averages of DEV-GCM, b1 "-0.0256" and
    "-0.0251", half-lives "26.72 days" and "27.26 days".
  - Trading: daily rules, entry when the residual exceeds X times its SD with X in {0, 0.05, 0.10, 0.15, 0.20},
    exit "when the residual reverts to zero"; one panel shows "Number of trades | 406 | Average duration (days) |
    6.09 | ... Winning trade percentage | 66.01 % | Average profit (per pound) | 0.0018 | ... t-statistics | 5.137".
    Costs "$75 per contract per round-trip" on "two contracts of soybean, three contracts of soymeal, and ten
    contracts of soyoil" (15 * 75 = 1,125 USD); "if traded applying e1, the average profits become equal to $1,080,
    $1,380, $1,500, $1,800, and $2040 using the thresholds of 0,0.05,0.1,0.15, and 0.2 respectively. However,
    after accounting for transaction costs when applying e2, trading is not profitable."
  This is a DAILY trading rule whose signal uses intraday (10-minute) prices to estimate the day's implied yields.
  It is not a minutes-scale rule.

##### 4.2 Worked arithmetic

(a) Rechner and Poitras gross edge. Net mean at zero filter -0.36 c/bu after 1.5 c/bu costs, so gross = -0.36 +
1.50 = +1.14 c/bu per trade on the 10:12:9 (or 20:24:18) spread. At 3-cent filter gross = 1.74 + 1.50 = 3.24
c/bu. Check: Mitchell's restatement "from a loss of .35 cents per bushel with no filter to +.35, 1.02, and 1.74"
(he writes .35 where the table says -0.36; a one-cent rounding difference in the second decimal, noted).

(b) Implied overnight-to-day reversal fraction. For a regression of the day change y = Close_t - Open_t on the
overnight change x = Open_t - Close_{t-1}, the slope b = rho * sd(y)/sd(x) (standard OLS identity). 1978-87:
b = -0.49 * 2.837/2.727 = -0.49 * 1.0403 = -0.510. 1987-91: b = -0.43 * 3.133/3.241 = -0.43 * 0.9667 = -0.416.
So in the pit era about 42-51% of a GPM overnight change was given back during the next day session, on average.
Check: |b| < 1 and of the same order as |rho|, since the two SDs are within 5% of each other. (Std. devs. from
Tables IA/IB, cents/bu: "Open, - Close,-1 ... 2.727", "Close, - Open, ... 2.837"; "3.241", "3.133".)

(c) What a 3-day half-life means at minutes. Assume (assumption, not from a source) that the deviation from the
5-day mean decays as an Ornstein-Uhlenbeck process, d(z) = -theta z dt, so half-life H = ln 2 / theta.
H = 3 trading days gives theta = 0.6931/3 = 0.2310 per day. If all reversion happens in the 290 day-session
minutes (08:30-13:20 = 4 h 50 min = 290 min; Zhou: "290 data points per trading day using the 1-minute data
set"), theta = 0.2310/290 = 7.97e-4 per minute. Expected fraction of a deviation closed in 60 minutes:
1 - exp(-60 * 7.97e-4) = 1 - exp(-0.0478) = 0.0467 (4.7%). A 1 c/bu deviation would close by 0.047 c/bu in an hour;
if ZM alone closed it, 0.047/0.22 = 0.21 ZM ticks, against the 1.59-tick break-even. Check: 60/290 of a day is
0.207 day; 0.207 * 0.231 = 0.0478, same exponent. Conclusion: the daily-scale reversion documented by Simon and
Mitchell is far too slow to pay at hours horizons by itself; an hours-scale ZM signal needs a fast intraday
component (Zhou's within-day cointegration) or the open-reversal component (Rechner and Poitras), not the 5-day
mean.

(d) Abdoh and Chitavi checks. Half-life formula H = ln(0.5)/ln(1 + b1): b1 = -0.0256 gives ln(0.9744) = -0.025933,
H = -0.693147/-0.025933 = 26.73 days (paper: 26.72); b1 = -0.0251 gives ln(0.9749) = -0.025420, H = 27.27 days
(paper: 27.26). Both match to rounding. Profit per trade: 0.0018 USD/lb * 600,000 lb = 1,080 USD, the paper's
first e1 figure (threshold 0), so the 406-trade panel is e1 at X = 0. Net of the 1,125 USD cost: 1,080 - 1,125 =
-45 USD at X = 0; 1,380 - 1,125 = +255 USD at X = 0.05; 2,040 - 1,125 = +915 USD at X = 0.20. e2's best, 865 USD, is
below cost (865 - 1,125 = -260 USD), as the paper says. Position check: 2 ZS = 2 * 300,000 = 600,000 lb; 3 ZM = 3 *
200,000 = 600,000 lb; 10 ZL = 10 * 60,000 = 600,000 lb. So the traded position is equal POUNDS of each leg (2:3:10),
not the board ratio 10:11:9; per-contract cost share 75 USD on a 6-day hold. In ZM terms per ZM lot: the trade's
average gross 1,080 USD over 15 lots is 72 USD per lot, i.e. 7.2 ZM-tick-equivalents per lot per trade over about
6 days, against Topstep's 5.28 USD round-trip fee plus spread per lot. These are daily-close executions.

##### 4.3 Reading

- Every daily crush-rule study that has an out-of-sample or later-period look shows decay: Rechner and Poitras's
  1990-91 weakness after the 1989 GPM shift; Mitchell's negative fourth segment and his failed replication of
  Simon's 200-USD rule; Janzen and Wang's post-2020 breakdown of the leg relations (Section 2). The gross edges are
  of the size of costs (Rechner and Poitras zero filter: gross 1.14 c/bu vs costs 1.5 c/bu).
- The one positive recent claim (Abdoh and Chitavi 2025) is a daily rule with multi-day holds (about 6 days) and
  a 27-39 day half-life to the long-run equilibrium; at threshold 0 its gross (1,080 USD) is below its own cost
  (1,125 USD), and only its USDA-yield-adjusted residual clears costs. Its novelty for E.32 is the measure, not
  the horizon: market-implied meal and oil yields estimated from the day's intraday bean-on-products regression.
  Read from partial full text only.

---

#### 5. Mean-reversion speed and half-life: what is published

| Horizon | Source | What is published | Status |
|---|---|---|---|
| Daily, 1985-1995 | Simon 1999 via Mitchell 2010 | "half-life of deviations of about 3 days" toward the 5-day MA | secondary (Simon not read) |
| Daily, 1984-2006 | Mitchell 2010 | average length of profitable trades "1.27 days at 220/200 to 2.63 days at 220/0"; unprofitable "2.16 days ... to 7.74 days" | read (line 205, 214) |
| Open-to-close, 1978-91 | Rechner and Poitras 1993 | corr(overnight GPM change, next day-session change) -0.49 and -0.43 | read |
| Daily rule, 10-min inputs, 1990-2021 | Abdoh and Chitavi 2025 | half-life of shocks "38.81 days" / "28.41 days" / "26.72 days" / "27.26 days"; transitory movements "lasts 10.4 days on average"; trades average "6.09" days | partial full text (Firecrawl directQuote) |
| Intraday 1-2 min, 2015 | Zhou et al. 2023 | cointegration on 74% (1-min) / 94% (2-min) of day sessions; no speed in time units | read |
| Daily, 2001-2015 (yearly fits) | Marowka et al. (JRSS-C 2020) | alpha "can be interpreted as the speed of the mean reversion of zt"; the vector varies by year (2014 "considerably higher variability") | read (no time-unit half-life found by grep) |

- No intraday half-life of the crush residual is published in any source found. Three discovery queries aimed at
  it ("crush spread" "half-life"; "crush spread" high-frequency/intraday/5-minute cointegration; intraday soybean
  complex lead-lag price discovery) surfaced only the sources above. The planner's statement "No intraday
  half-life is published" stands as VERIFIED-BY-ABSENCE (absence in what was searched, not proof).

---

#### 6. Which leg adjusts

##### 6.1 Facts

- Zhou et al. 2023 (intraday, 2015) [academic, read]: leadership varies with relative volumes (Section 3.1
  quotes). No fixed leader. Meal "Granger causes" more when byproduct volume is high relative to beans.
- Adrangi (J. Business & Economics Research, 2006, Clute) [academic; abstract only, clute_jber_2679_view.html; the
  full-text PDF link returns a JavaScript viewer page]: daily nearby futures; "Our VAR and bivariate GARCH model
  estimates suggest a strong bi-directional causality in Crush futures prices. We also find that while soybean
  contracts bear the burden of convergence when the spread between soybean and soy meal contract prices widens,
  this is not true of soybean and soy oil contracts." [abstract only]
- Liu and Sono 2016 (Dalian, daily) [abstract only]: "one-way information flow from the soymeal and soyoil markets
  to the soybean market".
- Avileis and Swanson (NCCC-134 2025) [academic, conference, read]: daily Bloomberg futures 2019-February 2025
  ("Daily commodity futures data for the nearby and first deferred contracts were downloaded from Bloomberg from
  2019 until February 2025", lines 345-346); 36 biofuel-policy events 2021-2025. "a 1% biofuel-induced price
  increase in soybean oil leads to a 0.19% rise in soybean prices and a 0.30% drop in soybean meal prices" and
  "meal prices serve as a price anchor when it comes to biofuels." Also "soybean oil futures returns increase
  significantly on announcement days (0.59%) and continue rising the following day (0.62%), exhibiting what we
  term Post-Announcement-Leak Drift (PALD)."
- Janzen and Wang 2025 (weekly cash) [extension]: the oil coefficient in the beans regression fell from 0.232 to
  0.070 after 2020 while meal's moved from 0.511 to 0.451 (Section 2).

##### 6.2 Worked example: a biofuel shock in ZM ticks

Take ZM at 300 USD/ton (an illustrative level; the October 2021 futures price quoted in Section 1 was 312.90). A
biofuel-induced +3% ZL move implies, per Avileis and Swanson's daily causal estimate, a ZM move of 3 * (-0.30%) =
-0.90%; 0.009 * 300 = -2.70 USD/ton = -27 ZM ticks (at 0.10 USD/tick). Check: 27 ticks * 10 USD = 270 USD per ZM
lot; 300 USD/ton * 100 tons * 0.009 = 270 USD. This is a daily (close-to-close) relation, not a minutes one; it
says the sign of ZM's response to an oil-demand shock is negative, which a ZM directional model could use as a
conditioning feature on policy-event days (EPA RVO, CARB, leaks), most of which the paper dates within 2021-2025,
i.e. inside the discovery window and absent from the 2017-20 test window except for the earlier RFS cycle.

##### 6.3 Reading

- Daily evidence (Adrangi; Liu and Sono for Dalian) leans toward beans adjusting to products, especially for the
  beans-meal spread; the intraday evidence (Zhou) says the adjusting leg depends on relative volume. Neither says
  ZM is the leg that closes crush residuals. The planner's test ("test early which leg adjusts: if ZM is not the
  adjusting leg, family 1 dies") is the right gate. Prior from the literature: ZM is NOT the default adjusting
  leg; it leads beans in daily data. That makes a ZM-leg reversion signal less likely than a ZM-leads signal
  (ZM moves first, ZS follows), which E.32 cannot trade on ZM itself.


---

#### 7. The overnight session and the "repaired after the 08:30 open" hypothesis

(Section written after a re-spawn, 2026-10-27 00:16-00:22 PDT; sources fetched in both spawns, all in log.tsv.)

##### 7.1 Facts

- Zhou et al. (NCCC-134 2022 version, supplementary Section E.1) [academic, read]: sessions "the electronic
  trading session from 7PM to 7.45AM (session 1) and the market trading session from 8.30AM to 1.20PM (session 2)"
  (zhou_nccc134_2022.pdf.txt lines 893-894). Counts of cointegrated days, ZS open-interest rollover, 1-minute
  data: session 1 "52", session 2 "180", session 1 + session 2 "52" (Tables 7, 8, 9, lines 2681-2733). Their
  explanation: "The fact that only the official trading hours are informative about the joint dynamics of
  financial assets might be explained by the absence of manufacturers outside of the official trading hours and
  the prevalence of traders during electronic sessions." (lines 2654-2657). And: "the role of traded volumes in
  the market's capacity to revert to equilibrium, and thus enforce the cointegration of asset prices, shrinks
  during electronic trading sessions" (lines 1533-1535).
- What Zhou did NOT test: every test is WITHIN a session (or on the two sessions pooled). No test asks whether a
  residual that opens up during session 1 is closed during the following session 2. The planner's "repaired
  after the 08:30 open" is therefore not addressed by Zhou in either direction.
- Rechner and Poitras (JFM 1993) [academic, read] is the closest published analogue, in the pit era (1978-91, no
  overnight electronic session; "overnight" there means close-to-open). Aggregate GPM: corr(Open_t - Close_{t-1},
  Close_t - Open_t) = -0.49 (1978-87) and -0.43 (1987-91) (Section 4). But the single legs did not reverse: meal
  -0.019 (t -0.92) in 1978-87 and -0.067 (t -2.22) in 1987-91 (Section 4.1 quotes). Their mechanism: "While the
  public is in on the close only the trading floor is in on the open." So in the only data that exist, the
  open-reversal lived in the SPREAD, not in the meal leg.
- Helms, Kaen and Rosenman (1984), via Rechner and Poitras [secondary pointer, not read]: minute-by-minute CBOT
  soybean prices on "a number of days in 1977 and 1978" showed "non-periodic cycles (persistent dependence) in
  both daily and intraday futures prices" (rechner_poitras_1993.pdf.txt lines 56-59). [unverified against the
  original]
- Session history [regulator-hosted exchange filing, read]: CBOT's 2012 self-certification to the CFTC: "Current
  electronic trading hours for these products are Sunday to Friday, 6:00 p.m. to 7:15 a.m. CT and 9:30 a.m. to
  1:15 p.m. CT", proposing "Sunday to Friday, 5:00 p.m. to 2:00 p.m. CT" effective "June 3, 2012"
  (cftc_cbot_rul051612.pdf.txt lines 29-37). By 2015 the sessions were 19:00-07:45 and 08:30-13:20 (Zhou, above).
  Whether the session times were identical across all of 2017-05..2024-02 was not verified here (no CME page may be
  fetched; the DataFacts worker owns session facts). [gap]
- Joseph and Garcia (AAEA 2016) [academic, conference paper, read]: CBOT electronic soybean futures, 15-second
  returns, "WASDE, CP, GS, AC, and PP reports from June 2010-May 2014", 30 reports released outside trading hours
  and 29 inside (joseph_garcia_aaea2016.pdf.txt lines 120-123). Abstract: "report releases during non-trading
  hours cause a large spike in volatility at the onset of trading which subsides quickly ... Return correlations
  provide little evidence to support systematic under- or overreaction in prices regardless of when the report is
  released". Body: "major market reactions persist for about 10 to 15 minutes" (line 317). Relevance: news that
  arrives while a market is shut is absorbed in the first minutes of the next session, with no measured
  continuation or reversal (outright soybeans, not the crush, not ZM).
- Ulibarri (J. Futures Markets 1998, MPRA copy) [academic, read; NYMEX crude, 1993, analogue only]: "ACCESS
  variables are informative in predicting daytime volume but not daytime prices" (ulibarri_mpra14818.pdf.txt,
  conclusions). Different market and era; listed as a weak analogue, not evidence about ZM.

##### 7.2 Worked arithmetic

(a) How thin is the ZM overnight book relative to the day session? From the standard numbers (E.28 Table 1):
ZM day-session volume share 0.83, so the overnight share is 1 - 0.83 = 0.17 (assumption: the 07:45-08:30 gap is
closed, so all non-day volume is overnight). Session lengths: overnight 19:00 to 07:45 = 12 h 45 min = 765 min;
day 08:30 to 13:20 = 290 min. With ADV 36,690 contracts:
  day: 0.83 * 36,690 = 30,452.7 contracts / 290 min = 105.0 contracts per minute;
  overnight: 0.17 * 36,690 = 6,237.3 contracts / 765 min = 8.15 contracts per minute;
  ratio 105.0 / 8.15 = 12.9.
Check: (0.83/0.17) * (765/290) = 4.882 * 2.638 = 12.88. Same calculation for ZS (0.78): (0.78/0.22) * 2.638 =
3.545 * 2.638 = 9.35; ZL (0.82): (0.82/0.18) * 2.638 = 4.556 * 2.638 = 12.02. ZM is the thinnest of the three
overnight per minute relative to its own day session, consistent with Zhou's account that crush-enforcing traders
are absent overnight.

(b) Sizing the repair hypothesis with the only published magnitude (pit era, illustrative, NOT a forecast).
Rechner and Poitras 1978-87: SD of the close-to-open GPM change 2.727 c/bu and implied give-back slope b = -0.510
(Section 4.2 b). A one-SD overnight crush move would on average give back 0.510 * 2.727 = 1.391 c/bu by the day
close. If ZM alone carried the give-back: 1.391 / 0.22 = 6.32 ZM ticks, against the 1.59-tick break-even
(Section 1.4). Check: 1.391 c/bu * 4.545 ticks per c/bu = 6.32. Three reasons this does not transfer: (i) it is
1978-87 pit data; (ii) it is open-to-CLOSE, not minutes after the open; (iii) in the same data the meal leg's own
open reversal was -0.019, i.e. the reversal was not carried by meal. Under (iii) the ZM share of the give-back
could be near zero.

(c) Zhou's session counts as shares: overnight 52/243 = 21.4%; day 180/243 = 74.1%; pooled 52/243 = 21.4%
(pooling the noisy overnight data destroyed day-session detection). Check: 52 + 191 = 243; 180 + 63 = 243.

##### 7.3 Test that E.33 could run (described for the lead; no decision taken here)

Quantities (all from owned schemas: ZM MBO mid, ZS and ZL MBP-1 mids):
  r(t) = 0.022 * M(t) + 0.11 * O(t) - S(t)/100, USD/bu (Section 1.2), at fixed board weights.
  D_on(d) = r(07:45 last mid of the overnight session, day d) - r(13:20 last mid, day d-1): the overnight residual
  change. Its ZM component: 0.022 * (M(07:45) - M(13:20 prior)).
  Label: ZM mid return from 08:30 + L (L = first post-open quote plus latency) to 08:30 + h, h in {15, 30, 60, 120}
  minutes, in ZM ticks, net of 1.59 ticks.
  Test: sign(-D_on) as the trade direction for ZM (ZM long when the crush is too low because meal is cheap
  relative to beans and oil), and, separately, the decomposition: does the day-session change in r come from ZM,
  ZS or ZL? If ZS or ZL closes the gap, the hypothesis is dead for a ZM-only trade (the planner's gate).
Leakage and look-ahead traps, each with a catching test:
  1. Settlement vs last mid: settlement is set in the 13:14-13:15 closing range and published after; using it as
     the 13:20 reference is fine only if it is the published value for that date. Test: recompute with the 13:20
     last mid; the signal's sign agreement should exceed 95% of days.
  2. Cross-schema timestamps: ZM MBO and ZS/ZL MBP-1 must be joined on the same clock (ts_recv or ts_event, one
     of them) with strictly backward as-of joins. Test: shift ZS/ZL by +1 s; a real signal changes little, a leak
     collapses.
  3. Opening match: the 08:30 open prints from an opening auction; a market order sent after it cannot get that
     price. Test: start labels at the first ZM quote after 08:30 plus 300-1,000 ms and compare with labels started
     at the open print; a large gap flags an untradeable edge.
  4. Daily-estimated cointegrating vectors (Zhou fits one per day using the whole day) are look-ahead inside the
     day. Test: use fixed board weights or weights fitted on prior sessions only, and assert in code that no
     weight uses data stamped after the decision time.
  5. Weekend and holiday opens: the Sunday 19:00 session carries weekend news; Mondays and post-holiday opens form
     their own stratum. Test: report results with and without them.
  6. Rolls: the three roots roll on different calendars; a v0 roll in one leg creates a fake residual jump. Test:
     drop days within the roll window of any leg and check the result is stable. (Listed months for each root
     come from the definitions schema; not verified here.)
  7. USDA release days: Joseph and Garcia show 10-15 minutes of report-driven volatility at the open on
     non-trading-hour releases (pre-2012) and Zhou finds stronger cointegration on USDA days. Test: stratify;
     exclude the first 15 minutes after any release.

##### 7.4 Status of the planner's two overnight claims

- "Crush cointegration mostly breaks down overnight": VERIFIED for 2015 (52 vs 180 of 243 days).
- "Overnight ZM dislocations get repaired after the 08:30 open": UNTESTED in any source found, as the planner said.
  The only related evidence (pit era) puts the repair in the spread and NOT in the meal leg (-0.019). Prior: weak.

---

#### 8. Fundamental drivers at short horizons: NOPA crush, biofuel policy, USDA reports, processing margins

##### 8.1 Facts

- NOPA monthly crush report [industry association, read]: "The NOPA Crush Report contains data from 20 member
  companies that account for 99% of the US soybean crush." Contents: "Soybean crush and oils stocks for the
  current month, previous month, and comparable month a year ago", "Soybean meal: tons produced, yield, and
  exports", "Soybean oil pounds produced and yield" (nopa_monthly_crush.html). Timing: "For 2026, the report will
  be published at 12:00 noon (EST) on the dates listed" (same file); the 2025 schedule: "LSEG Release Dates (at
  Noon Eastern)", Wednesday January 15, Tuesday February 18, Monday March 17, ... Monday December 15
  (nopa_release_dates_2025.pdf.txt). Noon Eastern = 11:00 Central, inside the day session. Release times for
  2017-2024 were NOT verified from a primary page (the LSEG product page fetched in the first spawn is a generic
  shell; a search snippet says "within seconds of 11:00AM CT", [unverified: search snippet only]). E.33 needs a
  dated release calendar; that belongs to the lead or DataFacts, not here.
- No academic intraday event study of the NOPA release was found (three queries: "NOPA monthly crush report
  soybean futures price reaction announcement effect"; "NOPA crush report released 11:00 Central time 15th of
  month schedule"; the NOPA-site search). Trade press (agricensus, barchart, S&P Global) describes single-day
  reactions; pointers only, never evidence.
- Biofuel policy (Avileis and Swanson, NCCC-134 2025) [academic, read; full quotes in Section 6]: 36 events
  2021-2025 (EPA, CARB, media "leaks"), DAILY returns; ZL "+0.59%" on the announcement day and "+0.62%" the next
  (their PALD); a 1% biofuel-induced ZL rise moves ZM -0.30%. No intraday timing is reported. Trade-press reports
  of limit moves on EPA days (for example 2022-12-01) are pointers only [unverified].
- USDA reports in soybeans (Joseph and Garcia 2016) [academic, read]: reactions "persist for about 10 to 15
  minutes"; "little evidence to support systematic under- or overreaction" (Section 7.1). Zhou: "stronger
  intraday cointegration observed on average on USDA announcement days" (Section 3.1). The direction of the
  15-90 minute path after USDA releases belongs to another worker's root; not pursued here.
- Processing margins: Janzen and Wang (farmdoc daily 2025) [extension]: "Since late 2020, crush margins have
  periodically increased and become considerably more volatile" (Section 2.1). Kang and Lee (NCCC-134 2026,
  "Preliminary and incomplete") [academic, conference, read abstract in full text]: the renewable-diesel crush
  expansion changed inland spot prices but "The resilience effect appears in spot prices and convenience yields,
  but not in futures prices" (kang_lee_nccc2026.pdf.txt abstract). A basis-level effect, not a futures signal.
- Export demand (weekly export sales, flash sales): NOT researched to full text in this root. [gap, stated]

##### 8.2 Worked arithmetic: can a NOPA-day ZM directional rule be tested on 39 months?

- Events: one release per month; the discovery window 2020-12-01..2024-02-29 holds 39 calendar months, so at most
  39 releases (December 2020 through February 2024, each dated on or after the 15th). Check: 2020-12 (1) + 2021
  (12) + 2022 (12) + 2023 (12) + 2024-01..02 (2) = 39.
- Position in the session: 11:00 CT is 150 minutes after 08:30 (11:00 - 08:30 = 2 h 30 min) and 140 minutes
  before 13:20 (13:20 - 11:00 = 2 h 20 min). A 240-minute label cannot fit inside the session; 60 and 120 can.
- Noise at 60 minutes (random-walk scaling assumed, stated): sigma_60 = 3.15 * sqrt(60) = 3.15 * 7.746 = 24.40
  ZM ticks. Standard error of a mean over n = 39 events: 24.40 / sqrt(39) = 24.40 / 6.245 = 3.91 ticks. To reach
  t = 2 on a true mean edge equal to the 1.59-tick break-even: n = (2 * 24.40 / 1.59)^2 = (30.69)^2 = 942 events.
  Check: 942 / 12 = 78.5 years of monthly releases. Conclusion: a NOPA-day directional rule is not testable on the
  owned data; at best NOPA days are a stratum or an exclusion window. The same arithmetic applies to the 36
  biofuel events of Avileis and Swanson (fewer of them fall inside 2020-12..2024-02).
- Event-day volatility will be higher than sigma_1m on normal days (Joseph and Garcia's report-day volatility
  peaks), which makes n larger still; the 942 is a lower bound under the stated assumption.

##### 8.3 Reading

The fundamental drivers named in the topic list either arrive monthly (NOPA, about 39 events), irregularly (biofuel
policy, tens of events over five years), or are measured at daily or weekly horizons. None gives a sample large
enough for a minutes-scale directional rule on its own. They are useful as STRATA (days on which the crush
relation is stressed or reinforced), as EXCLUSION windows (the first 10-15 minutes after a release), and, for
biofuel events, as a sign prior (an oil-demand shock lowers ZM).

---

#### 9. What this means for a ZM directional search

Mechanisms worth testing (in order of prior strength, all weak):
1. Day-session crush residual -> ZM, conditioned on relative volume. Zhou: day-session residuals are mostly
   stationary at 1-2 minute sampling (74-94% of 2015 days), and the speed of adjustment depends on relative
   volumes. The first gate is the planner's: does ZM, rather than ZS or ZL, close the residual? The literature's
   prior is that ZM is NOT the default adjusting leg (Adrangi daily; Zhou volume-dependent; Rechner and Poitras
   meal leg -0.019). Published reversion speeds are all daily (half-life about 3 days via Mitchell's summary of
   Simon; 27-39 days in Abdoh and Chitavi), which at hours horizons close only about 5% of a deviation per hour
   (Section 4.2 c); a payable signal needs a fast intraday component that no paper measures.
2. Overnight-to-open repair (Section 7.3). Untested anywhere; the pit-era analogue puts the reversal in the
   spread, not the meal leg. Cheap to test once family 1's data are built (same residual, one decision per day,
   about 800 trading days in 39 months).
3. Biofuel event days as a conditioning flag (negative ZM response to oil shocks, Avileis and Swanson), not as a
   standalone rule.

Mechanisms to drop or demote:
- Daily crush rules toward a 5-day mean (Simon) or long-run equilibrium (Mitchell, Abdoh and Chitavi): too slow
  for minutes-to-hours, decayed out of sample (Mitchell's failed replication of Simon), and gross edges of the size
  of costs (Rechner and Poitras zero filter: gross 1.14 c/bu against 1.5 c/bu costs).
- NOPA-day or biofuel-day directional event rules: about 39 events against about 942 needed (Section 8.2).
- Per-day cointegrating vectors (Zhou's daily fits): SD 0.28 around a median of -0.19 for ZM, and look-ahead
  within the day. Use fixed board weights or prior-session rolling weights.
- Fixed betas fitted on 2020-24 and applied to 2017-20: the weekly oil coefficient fell from 0.232 to 0.070 at the
  regime change (Janzen and Wang). Thresholds should be in units of a causal rolling residual SD, not fixed cents.

Regime: the discovery window lies wholly inside the renewable-diesel regime (oil share mostly above 35%, weekly
co-movement R2 0.32); the sealed test window lies wholly before it (oil share 25-35%, R2 about 0.79), apart from
its last weeks. Any crush-based ZM signal selected on discovery data meets a different crush in the test window.
No source measures this break at intraday horizons. [gap]

---

#### 10. Planner pointers I own: verification table

| # | Planner claim | Status | Evidence (file) |
|---|---|---|---|
| 1 | ZM tick 10 USD, ZS 12.50, ZL 6 | VERIFIED (owned-data definitions table via E.28; not from a CME page, stage rule) | A0_contract_stats.md lines 114-117 |
| 2 | Board crush = 0.022 x meal (USD/ton) + 0.11 x oil (c/lb) - beans (USD/bu) | VERIFIED as arithmetic of 44 lb meal and 11 lb oil per 60 lb bushel; CME's yields quoted second-hand by farmdoc; Marowka quote "yt(1) - 11yt(2) - 2.2yt(3)" in cents | farmdoc_fdd101325_oilshare.pdf.txt; marowka_spiral_b.pdf.txt lines 67-68 |
| 3 | Ratio 10 ZS : 11 ZM : 9 ZL; Rechner and Poitras used 10:12:9 | VERIFIED | poitras_soycrush_wpd.pdf.txt; rechner_poitras_1993.pdf.txt lines 105-116 |
| 4 | One ZM tick = 0.22 c/bu of crush; 1 c/bu = about 4.5 ZM ticks | VERIFIED (arithmetic: 0.022 x 0.10 USD = 0.0022 USD/bu = 0.22 c/bu; 1/0.22 = 4.545) | Section 1.2 |
| 5 | Zhou et al.: 180 of 243 day sessions cointegrated (229 at 2-min) | VERIFIED | zhou_jcm2023_wur.pdf.txt; zhou_nccc134_2022.pdf.txt line 2756, Table 8 |
| 6 | Overnight session cointegrated on only 52 | VERIFIED (ZS open-interest rollover; 53/49/33 under other rollovers) | zhou_nccc134_2022.pdf.txt Table 7 |
| 7 | Median vector ZL -0.11, ZM -0.19 vs physical -0.11, -0.22; daily SD 0.28 | VERIFIED (SD 0.28 for both legs); price units of the vector not stated by the paper, see Section 3.2 caveat | zhou_jcm2023_wur.pdf.txt Table 4 |
| 8 | Leadership depends on relative volume; no fixed leader | VERIFIED | zhou_jcm2023_wur.pdf.txt lines 814-820 |
| 9 | No half-life or information-share levels reported (Zhou) | VERIFIED (grep for "half" finds none; kappa reported only as ratios regressed on volume ratios) | both Zhou files |
| 10 | Simon (JFM 1999): crush rules profitable 1985-1995 | PARTLY VERIFIED: abstract only ("January 1985 through February 1995", "would have been profitable"); full text not obtained; the 3-day half-life is Mitchell's summary | simon1999_ideas.html; mitchell_jrfm2010_firecrawl.md |
| 11 | Mitchell (JRFM 2010): unstable | VERIFIED (negative later segment; Simon replication loses 20 USD per trade) | mitchell_jrfm2010_firecrawl.md |
| 12 | Abdoh and Chitavi (IREF 2025): deviations of meal and oil from USDA crushing yields explain transitory crush moves; three-leg daily rules profitable after costs | PARTLY VERIFIED: partial full text (Firecrawl directQuote). Profitable after costs only under cost assumption e1 and thresholds above 0; under e2 "trading is not profitable"; at threshold 0 gross 1,080 USD < 1,125 USD cost; signal uses 10-minute intraday prices but the rule is daily with about 6-day holds | abdoh_chitavi_firecrawl_directquote.txt; abdoh_chitavi_ideas.html |
| 13 | Rechner and Poitras (1993) | VERIFIED (10:12:9; open-to-close rule; costs 1.5 c/bu; opening-reversal correlations -0.49/-0.43; decay after 1989) | rechner_poitras_1993.pdf.txt |
| 14 | "No intraday half-life is published" | VERIFIED BY ABSENCE (not found in any source read or in the targeted queries of both spawns (3 in the first, 2 in this one); absence, not proof) | Section 5, Section 11 |
| 15 | "Crush cointegration mostly breaks down overnight" | VERIFIED for 2015 only | Section 7.1 |
| 16 | Overnight ZM dislocations repaired after the 08:30 open (hypothesis) | UNVERIFIED (untested anywhere; pit-era analogue shows the reversal in the spread, meal leg -0.019) | rechner_poitras_1993.pdf.txt; Section 7 |
| 17 | Expected regime break between discovery (RD oil share) and test (2017-20, trade war and Covid) | PARTLY VERIFIED: the oil-share and co-movement break is verified at weekly cash horizons (Janzen and Wang); the trade-war and Covid parts are not covered by any source read here; no intraday evidence | farmdoc_fdd101325_oilshare.pdf.txt; farmdoc_fdd091025_extraction.pdf.txt |

---

#### 11. Search log, stopping rule and non-survivors

Stopping rule (brief rule 6) by topic:
- Contract arithmetic and ratios: 4 full texts (Rechner and Poitras; Poitras note; farmdoc x2; Smith). Stopped.
- Daily and intraday cointegration: full texts Zhou (two versions), Marowka et al., Mitchell, Rechner and Poitras;
  last three queries (this spawn: "crush spread" high-frequency intraday cointegration 2020-2023; soybean crush
  overnight/day-session price discovery; overnight-vs-intraday returns in grain futures) surfaced nothing new
  except a hedging thesis (below). Stopped.
- Crush trading-rule profitability and decay: full texts Rechner and Poitras, Mitchell, Abdoh and Chitavi
  (partial); Johnson et al. 1991 and Simon 1999 not obtainable as text (scanned precursor; paywall). Stopped.
- Half-life at any horizon: covered by the above; no intraday figure exists in what was searched. Stopped.
- Regime change: farmdoc x2 (Janzen and Wang; extraction rates), Smith 2021, Kang and Lee 2026; last query
  (oil share / structural break / meal price discovery) found only Kang and Lee (spot, not futures). Stopped.
- Which leg adjusts: Zhou, Avileis and Swanson (full); Adrangi and Liu-Sono (abstract only). Stopped.
- Fundamental drivers at short horizons: NOPA pages, Joseph and Garcia, Avileis and Swanson; three NOPA queries
  found no academic intraday study. Stopped. Export sales not researched (gap).

Non-survivors and items read but not used as evidence:
- Emery and Liu (JFM 2002) [academic, abstract only, emery_liu2002_ideas.html]: electricity vs natural gas, daily
  settlements; "statistically significant mean reversion ... also is economically significant in both in-sample
  and out-of-sample tests." An energy analogue of a cointegrated-spread rule at DAILY horizon; no bearing on ZM
  minutes.
- Kanamura, Rachev and Fabozzi (KIT WP 27, 2011) [academic, read title page]: spread-trading profit model for
  energy futures; not soybean. Not used.
- Wu (Illinois MS thesis 2022, ideals_126677_intraday_hedging.html) [academic, abstract read]: intraday data
  improve minimum-variance HEDGING in the soybean crush complex ("there is at least one intraday data-based hedging
  strategy that outperforms the Naive in the soybean crush complex"); covariance forecasting, not direction.
- Ulibarri (1998): NYMEX crude, after-hours session; analogue only (Section 7.1).
- Gu and Lei (Atlantis 2018), atlantis_25886066: Dalian crush stat-arb, low-tier venue; not used.
- shs_gap_soyoil.html: a captcha page (no content); lseg_nopa.html/.txt: a generic product shell with no release
  facts; clute_jber_2679.pdf and adrangi_jber2006.pdf: both are HTML viewer pages, not the PDF (so Adrangi stays
  abstract only); johnson_etal_nccc1990.pdf: a scanned image with no text layer (no OCR tool on the machine).

Budget: WebSearch calls in this spawn: 10 (00:16-00:22 PDT). The first spawn's count was not logged; its
log.tsv shows 36 fetches between 23:03 and 23:15 PDT. Total stays well under the 80-call cap on any reading.
No "budget used up" notice was received. Firecrawl was used twice in the first spawn (mdpi.com, which blocks curl
and whose terms could not be read, so no Scrapling; ScienceDirect, whose page declares a TDM reservation).
Scrapling was not used in either spawn.

Status: all sections 1-11 written. Finished 2026-10-27 00:23 PDT.

## R3b. Soybean complex microstructure: K algorithm, implieds, rolls, liquidity

Source file: reports/stage_e32_briefs/R3b_microstructure.md (sha256 45719f37991734f62a224107bf6141b6a32e09ec815ce4d755ce4cf6cda0e667).

### R3b: soybean-complex market microstructure for minutes-to-hours directional trading in ZM

Stage E.32, worker SoyMicrostructure-OpusHigh (opus, high). ROOT R3b_microstructure. Started 2026-10-27 00:33 PDT.
Research only: no market data read, no statistic derived from data. Evidence pages and log.tsv:
reports/stage_e32_briefs/pages/R3b_microstructure/. Source labels: academic, practitioner, regulator, exchange, firm.
CME material comes only from CFTC-hosted copies, papers or other secondary sources (E.32 rule); cmegroup.com and its
archives were not fetched. Where a fact rests only on a cmegroup.com-origin file that Stage E.31 saved earlier
(reports/stage_e31_briefs/research/pages/K/), it is marked [E.31 cmegroup-origin, not re-fetched].

Status: complete (finished 2026-10-27 00:49 PDT; see the last section for gaps).

#### (a) The K matching algorithm on CBOT grains and oilseeds, and what it means for an aggressor versus a resting order

##### a.1 Facts

- ZM outrights use match algorithm K. Owned data: E.31 checked the definitions files of the owned data and found
  "all outrights K" (reports/E.31_RETURN.md line 168, quoted: "structure checked (every weekday snapshot present,
  all outrights K, ticks 10.00/12.50/6.00 USD ..."). This is a recorded E.31 fact, not a new read of data.
- CME's own description, as presented to the CFTC Agricultural Advisory Committee on 2019-04-11 and hosted on
  cftc.gov [exchange material, regulator-hosted] (R3b_cftc_aac041119_cmegroup.pdf, page 3, "K Matching Algorithm in
  Grain Futures"):
  - TOP: "The first order to "better the market" is eligible for TOP allocation. The most any order can be allocated
    is controlled by TOP MAX. TOP MAX in grain outrights is 100 contracts and 1000 contracts in grain spreads."
  - FIFO: "40% of the incoming aggressing order is allocated by timestamp. The order with the oldest timestamp at
    that price level is first in the queue."
  - Pro rata: "60% of the incoming aggressing order is allocated based on the size of the resting orders. The largest
    order receives the largest allocation, followed by the second largest order, etc."
  - Levelling: "A means by which residual quantity from rounding during the Pro-Rata step are distributed. Any order
    that did not participate in the Pro-Rata pass is eligible for rounding with a maximum of 1 contract allocated per
    order."
  - Residual: "Any residual quantity remaining is filled FIFO."
  - Page 4 (pro-rata rounding): with six resting 10-lots, a 6-lot aggressor gives each 1 lot, but "changing the
    incoming order to a 5 lot completely changes the allocation. 5 cannot be equally split amongst 6 equal shares
    resulting in no Pro-Rata allocation and this 5 lot moves to either Leveling or FIFO."
  - Page 5, "Realized Allocations": "~7% TOP", "~56% FIFO", "~23% Pro-Rata", "~14% Leveling". The slide does not say
    which products, period or unit (lots or fills) these shares cover [the scope is not stated in the source].
- Finer parameters for ZM (Stage E.31's parameter table, reports/stage_e31_briefs/research/K_algorithm.md section
  (a), from the CME Globex product reference sheet and the CME client wiki) [E.31 cmegroup-origin, not re-fetched]:
  TOP Min 1, TOP Max 100 (outright), FIFO 0.4, pro rata 0.6, PR Min 1, residual "Leveling" for the ZM outright and
  "FIFO" for the ZM-ZM calendar spread, no LMM in futures, FIFO share rounded up to a whole lot, pro-rata shares
  rounded down, levelling at most 1 lot per order to orders that took part in the pro-rata step and got 0, ties by
  larger working quantity then earlier time; since 2023-10-01 only fills after an order rests count against TOP Max.
  E.31 also recorded a conflict: the CFTC slide says any order "that did not participate in the Pro-Rata pass" is
  eligible for levelling; the wiki says the order "must have participated in the preceding Pro Rata step" and
  received 0 lots. The wiki is the more detailed text.
- FIFO exception for sweeps [E.31 cmegroup-origin, not re-fetched; K_algorithm.md (a), sources S3/S4]: "In the
  scenario where an aggressing order quantity is greater than or equal to the displayed quantity in an instrument at
  a given price level, for matching efficiency, CME Globex applies FIFO in lieu of the designated product
  algorithm." No CFTC-hosted or academic copy of this rule was found in this stage (one search).
- Academic context on pro-rata books [academic]: Field and Large (CFS Working Paper 2008/40,
  R3b_field_large_2008_prorata.pdf, abstract): in four one-tick short-rate futures markets with pro-rata matching
  "offered depths at the quotes on average exceed mean market order size by two orders of magnitude, and their order
  cancellation rates ... are significantly over 96 per cent", and "strategic complementarities in the choice of limit
  order size cause traders to risk overtrading by submitting over-sized limit orders, most of which they expect to
  cancel." ZM is not a one-tick market (median daily range 96 ticks, E.28 A0) and is 60% pro rata, not 100%, so this
  is an analogy, not a ZM result.
- Grain order life [academic]: Ma and Serra's working version (R3b_afajof_63476_ma_serra.pdf, abstract), CME corn,
  soybean and wheat MBO, 2019-01 to 2020-06: "25%-28% of limit orders submitted are executed, while around 75-79% are
  deleted and 7%-8% revised. Latency of limit orders is low, with half of the limit orders being deleted within 2-5
  seconds after their placement."

##### a.2 Worked example (a resting 1-lot versus an aggressor; arithmetic only, rules as stated above)

Book: ZM best bid, four resting orders in time order A = 50 lots (oldest), B = 30, D = 19, C = 1 (ours, newest);
displayed total 100 lots; no TOP order left at this price (assumption). A sell market order of q = 10 lots arrives.

1. FIFO exception? q = 10 < 100 displayed, so K applies.
2. Split: FIFO lots = ceil(0.4 x 10) = ceil(4.0) = 4 (E.31 (d)4 reads "rounded up to the whole lot just above" as
   ceil, [inferred]); pro-rata lots = 10 - 4 = 6.
3. FIFO: A (oldest) takes 4. A has 46 left.
4. Pro rata on working quantities after FIFO (E.31 (d)2: post-FIFO denominator [inferred]): total 46 + 30 + 19 + 1 =
   96. A: floor(46/96 x 6) = floor(2.875) = 2; B: floor(30/96 x 6) = floor(1.875) = 1; D: floor(19/96 x 6) =
   floor(1.1875) = 1; C: floor(1/96 x 6) = floor(0.0625) = 0. Allocated 2 + 1 + 1 + 0 = 4; residual 6 - 4 = 2.
5. Levelling: only C took part and got 0, so C gets 1 lot. Residual 2 - 1 = 1.
6. FIFO residual: A takes 1.
7. Totals: A 4 + 2 + 1 = 7, B 1, D 1, C 1; sum 10 = q. Check: equals the aggressor's size, and C's fill (1 lot)
   came from levelling although C was last in time; under pure FIFO C would fill only after 99 lots traded.
8. The aggressor's price is the bid in every case: for q at or below the visible plus implied quantity at the touch,
   the algorithm decides WHO is filled among resting orders, never the aggressor's price. If q = 100 or more, the
   FIFO exception fills the level in time order, and any remainder walks to the next price.

Variant: q = 5 with the same book. FIFO = ceil(2.0) = 2 to A (48 left); pro rata 3 on 48 + 30 + 19 + 1 = 98: A
floor(1.469) = 1, B floor(0.918) = 0, D floor(0.582) = 0, C floor(0.031) = 0; residual 2; levelling by larger working
quantity first: B 1, D 1 (residual 0), C gets nothing. Totals A 3, B 1, D 1, C 0 = 5. So a small aggressor can skip the
1-lot entirely; whether C fills depends on the aggressor size and the other orders, not on C's time priority.

##### a.3 What this means for a ZM directional search

- A minutes-scale directional strategy that enters and exits with market (marketable) orders of 1-3 lots is almost
  untouched by K: the fill price is the touch whenever the size is below displayed plus implied quantity. No recorded
  E.28 or E.31 statistic gives ZM touch depth (searched A0_contract_stats.md and E.31_RETURN.md), so "1-3 lots fit at
  the touch" is an assumption for E.33 to check on discovery data. E.31 measured that 11.8% of aggressor PRINTS (26.0%
  of their volume) found less than their size displayed, but those are other traders' sizes, not a 1-lot.
- K matters for (i) any limit-order entry (fills arrive by levelling or FIFO lottery, decoupled from queue position,
  so a resting 1-lot is filled more often when a large aggressor sweeps through, which is the adverse-selection case
  E.31 measured at -0.970 ticks per fill gross at 10 s) and (ii) the meaning of displayed depth. With 60% pro rata,
  resting size buys allocation, so displayed depth includes size that its owners do not expect to trade (the Field
  and Large mechanism, and Ma and Serra's 75-79% deletion share). Depth-imbalance features are therefore noisier
  signals of intent than in a FIFO market, and the sign of a "large bid" is ambiguous. Treat depth and queue features
  as conditioners (planner family 7), with the over-sizing confound written into the feature definition.
- Mechanism to drop: queue-position modelling for a 1-lot. Under K it does not buy priority the way it does under
  FIFO, and V50's trade-through rule decides the simulated fill anyway.
- Test, not assume: whether cancellations at the touch (not additions) carry the information (Ma and Serra's
  information shares, section (e) below, give cancellations at the BBO a large share in grains).

#### (b) Implied spreads (calendar and board crush), implied in and implied out, and what an aggressor sees versus the feed

##### b.1 Facts

- Mechanism [academic]: Ma, Serra, Peterson and Irwin (NCCC-134 2026, R3b_richie_ma_serra_2026_calendar_spreads.pdf,
  lines 88-95 of the text file): "A key feature of CME's electronic trading design is its implied functionality, an
  automated quoting system that tightly integrates liquidity between calendar spreads and outrights. Through this
  system, liquidity in calendar spreads generates synthetic and contingent quotes in outrights ... For example, a
  $0.25 bid quote of the May-July calendar spread and an ask quote of $4.25 of the May outright can generate an
  implied $4 bid quote of the July outright."
- Implied in and implied out [academic]: Peng, Hu, Robe and Adjemian (NCCC-134 2021,
  R3b_peng_hu_robe_adjemian_2021.pdf, lines 266-270): "A trade can be initiated by either a buyer or a seller as well
  as classified as an implied trade when matching with implied order(s)." and "updates in the LOB also reflect
  changes to implied orders that can be either (i) orders in the outright book created based on orders in the spread
  market ("implied-out") or (ii) orders in the calendar spread book created based on orders in the outright market
  ("implied-in")."
- Size of calendar-implied liquidity at the outright touch, corn and soybeans, CME Market Depth data 2015-01-05 to
  2024-12-27, day session [academic] (Ma et al. 2026, lines 636-641): "For the first-nearby futures, implied liquidity
  contributes 16.00%-17.97% to consolidated liquidity, rising to 50.97%-52.48% for second-nearby futures. For more
  deferred contracts, implied liquidity constitutes about 68.92%-72.09% of consolidated depth in grain markets". The
  measure counts implied depth only when its price equals the consolidated best price (lines 631-635). ZM is not in
  their sample (corn and soybeans only, lines 212-215).
- The exchange's public feed carries the calendar-implied book separately and only two levels deep [firm, data
  vendor] (Databento GLBX.MDP3 docs, R3b_databento_glbx_mdp3.md, line 112): "CME's MDP3 feed has support for implied
  orders over their MBP feed. The MBP feed provides up to 10 levels of real liquidity and 2 levels of implied
  liquidity." Ma et al. 2026 (lines 632-633): "Because implied and outright order books are disseminated separately,
  we count implied depth only when its quote matches the consolidated best price."
- What the owned data contain: the owned ZM MBO is an outright order-by-order feed. Databento (line 47): MBO "Add,
  Modify, and Cancel actions are normalized from [Market Data Incremental Refresh - MBOFD]", and line 113: "Databento
  combines the real and implied books, publishing the merged top-of-book on the [CMBP-1] schema." The owned ZS and ZL
  files are MBP-1, not CMBP-1 (READER_BRIEF owned-data list), so neither the owned ZM MBO nor the owned ZS/ZL MBP-1
  shows implied quantity [inferred from the schema names; confirm with the DataFacts worker].
- Trades against implied quantity lose their aggressor side and order detail:
  - Databento (lines 70-71) [firm]: "Implied trades ... may not have an aggressing side set. These trades will be
    normalized with side set to None."
  - Ma and Serra working version (R3b_afajof_63476_ma_serra.pdf, footnotes 2 and 5) [academic]: "Order details (e.g.,
    order ID, matched quantity, aggressor) are not provided for those market orders that are executed against implied
    order(s). If a market order is executed against both outright and implied limit order(s), only matched outright
    order details are recorded." and "the trade summary message that aggregates the matched limit orders does not
    provide the aggressor indicator if implied liquidity is involved in the match." Their fix: assign the aggressor
    as the side opposite the matched outright orders, and delete trades executed entirely against implied liquidity,
    which were "0.03%, 0.01%, and 0.01%, of total number of trades ... in the corn, soybean, and wheat markets,
    respectively, in each trading day."
- Ratio (intercommodity) spreads such as the soybean crush imply into the legs, and those implieds are not shown in
  market data [exchange; E.31 cmegroup-origin, not re-fetched] (reports/stage_e31_briefs/research/pages/K/
  wayback_algorithms_near20231201.txt, CME Globex Matching Algorithms, capture 2023-10-02): "There is an exception
  during Predetermination with ICS ratio spreads. Examples include Treasury ICS and Soybean Crush spreads." and, in the
  ratio-spread example on the same page, "(these implieds will not be visible via market data)". Also: "Implied
  quantity will never match with implied quantity." The planner's exact phrase "not disseminated in market data" (from
  the wiki page "Implied Intercommodity Ratio Spreads") was not found in any file this stage may read; the E.31 page
  says the same thing in other words.
- The crush spread's legs and price formula are R3a's topic (reports/stage_e32_briefs/R3a_crush.md section 1: board
  crush in cents/bu = 2.2 x M + 11 x O - S, the 10:11:9 ratio). A search snippet of a 2009 CME notice gives the SOM
  legs as "Eleven (11) Soybean Meal futures contracts; ... Nine (9) Soybean Oil ...; ... Ten (10) Soybean" [unverified:
  search snippet of a cmegroup.com page, not fetched under the stage rule].
- Exchange history [practitioner, sponsored by the FIA Principal Traders Group] (Overdahl, Futures Industry, Nov 2011,
  R3b_nera_overdahl_2011.pdf): "On Jan. 31, 2011, the CME turned on implied matching functionality for corn futures
  after turning off this functionality in August 2010." and "in these two instances, market quality improved when the
  exchanges turned off their implied matching functionalities." Interested-party research; context only.
- Priority between outright and implied quantity: Ma et al. 2026 (line 764) state "outright quotes have matching
  priority over implied quotes (CME 2007)", while the E.31-saved CME page describes predetermination in which each
  implied "source" is treated "as one large order quantity" and run through the algorithm's steps with the outright
  book. These two descriptions are not obviously the same; the order of priority inside K for ZM is unresolved here.
- Stage E.31's own measurement (reports/E.31_RETURN.md line 204, front month, day session): "5.5% of aggressor prints
  (3.6% of their volume) found no displayed resting quantity at their price, 11.8% (26.0% of volume) found less than
  their size, and 9.1% of prints carry no aggressor side."

##### b.2 Worked example: an implied-out ZM bid from the board crush (units and lot blocks; price convention not checked)

Using R3a's formula per bushel, C [c/bu] = 2.2 x M + 11 x O - S (M in USD/short ton, O in c/lb, S in c/bu).
Suppose a resting crush BUY (buy meal and oil, sell beans) at C* = 150 c/bu, a resting ZL offer at O = 50.00 c/lb and
a resting ZS bid at S = 1300.00 c/bu. A ZM seller can be matched against the crush buyer, with the engine buying ZL
from the ZL offer and selling ZS to the ZS bid. The ZM price that makes the package equal C*:
M = (C* - 11 x O + S) / 2.2 = (150 - 550 + 1300) / 2.2 = 900 / 2.2 = 409.0909 USD/short ton.
That is not on the 0.10 USD tick; how CME rounds or prices SOM legs is not known here [unverified], so this shows the
units only. Lot blocks: one SOM spread is 11 ZM + 9 ZL + 10 ZS (ratio per R3a), so implied ZM quantity from one SOM lot
is 11 ZM lots. The E.31-saved CME page's ratio-spread rule rounds a source's allocation to zero when it is too small to
form whole legs ("If the ZT source ... was allocated 2 lots, round this quantity to zero and work on the other
sources"), so a 1-3 lot ZM aggressor probably does not match crush-implied quantity at all [inferred from a Treasury
example; not stated for the crush]. Check: 2.2 x 409.0909 + 11 x 50 - 1300 = 900.0 + 550 - 1300 = 150.0 c/bu = C*.

##### b.3 What this means for a ZM directional search

- For a 1-lot aggressor at the ZM front month, implied quantity is extra liquidity: it can only fill at the same or a
  better price than the outright book, never worse. It does not hurt a market-order entry.
- It does hurt measurement. In the owned data, a trade print with no visible resting quantity at its price, or with
  side None, is most likely an implied match (E.31: 5.5% and 9.1% of front-month day prints). Any order-flow
  imbalance or trade-sign feature must state how it treats side None prints (drop, or sign by the matched outright
  side as Ma and Serra do) and freeze that choice before the search; E.33 should report the share dropped.
- Depth, spread and touch features built from the owned MBO and MBP-1 are outright-only. The true executable touch is
  at least as good as the outright touch, so a cost model built on outright spreads is conservative for the touch
  price. For the second contract (ZM.v.1) the gap is likely much larger: Ma et al. put implied liquidity at about half
  of consolidated touch depth for the second nearby corn and soybean contract.
- Crush-implied liquidity is invisible in every feed. A ZM move caused by a crush-spread order trading through implied
  quantity looks, in ZM's own book, like an aggressor hitting nothing. That makes "sweeps of empty levels" a candidate
  sign of cross-product (crush) flow, not a ZM-only event; a family built on ZM-only book events should carry ZS and
  ZL trade timing as a control.
- Mechanism to drop: any feature that needs implied depth (the owned data cannot rebuild it). Mechanism worth a test:
  side-None or no-resting-quantity prints as a crush-flow flag, measured in discovery data only.

#### (c) Roll and delivery effects: delivery months, first notice day, index rolls, spot-month limits, volume migration

##### c.1 Facts

- Delivery months and last trading day [exchange; E.28 cmegroup-origin, not re-fetched]
  (reports/stage_e28_briefs/pages/A1_grains/cbot_rulebook_ch13.txt, CBOT Rulebook chapter 13, Wayback 2025):
  "Trading in soybean meal futures is regularly conducted in eight months - September, October, December, January,
  March, May, July, and August." Termination: "No trades in Soybean Meal futures deliverable in the current month
  shall be made after the business day preceding the 15th calendar day of that month." Close on the last day: "the
  close of the expiring future shall begin at 12 o'clock noon and trading shall be permitted thereafter for a period
  not to exceed one minute." Price limits: "There shall be no price limits on the current month contract on or after
  the second business day preceding the first day of the delivery month."
- Stage E.0 recorded a CME statement [exchange, cmegroup-origin, E.0 K6 P-K6-048-d, reports/stage_e0_research_K6.md
  line 672]: "Spot month contracts are not subject to price limits. In Grain and Oilseed contracts, price limits are
  removed on the business day prior to first notice day of an expiring contract month."
- First notice day: no CFTC-hosted or academic text defining it for CBOT grains was found in this stage (two
  searches). A search snippet of a 2017 broker notice says first notice for December CBOT grains "fell on the last
  business day of November" [unverified: search snippet, broker page not fetched]. The two price-limit rules above
  give the same day only if first notice day is the last business day of the month before delivery (worked example
  c.2), which supports that reading [inferred].
- Federal speculative position limits for soybean meal [regulator] (CFTC, "Speculative Limits" page,
  R3b_cftc_speculative_limits.html): "2020 Final Rulemaking Federal Spot Month Limit Level | ... | CBOT Soybean Meal
  (SM) | 1,500" and "Federal Single Month and All-Months-Combined Limit Levels | ... | CBOT Soybean Meal (SM) |
  16,900". The same page: "Exchanges must implement § 150.5 by the 2020 Final Rulemaking's general compliance date of
  January 1, 2022." The pre-2021 legacy levels (relevant to the sealed 2017-2020 test window) were not retrieved
  [unverified]; the GPO appendix table (R3b_govinfo_cfr2025_17_150_appE.pdf) is an image and did not extract.
  The federal definition of the legacy-agricultural spot month was not retrieved [unverified].
- Index rolls:
  - Bloomberg Commodity Index (BCOM) holds soybean meal directly [firm, index provider] (R3b_bcom_methodology.pdf,
    version with January 2023 target weights): soybean meal is an index commodity ("Soybean Meal | CBOT | 100 short
    tons | USD/short ton"), with a 2023 CIP of "3.53%". Roll: "The "Roll Period" is used in this Methodology to refer
    to the sixth through tenth Business Days of the month, during which time the value of BCOM is gradually shifted
    from the utilization of WAV1 for Index calculation to the utilization of WAV2, at the rate of 20% per Business
    Day." Table 9 (contract calendar, Jan to Dec): "Soybean Meal Mar Mar May May Jul Jul Dec Dec Dec Dec Jan Jan".
    Reading the table with the text ("in February the Lead Future is March and the Next Future is May"), BCOM rolls
    its ZM position in February (Mar to May), April (May to Jul), June (Jul to Dec), October (Dec to Jan) and
    December (Jan to Mar) [inferred from Table 9 and the quoted rule]. It never holds the Aug, Sep or Oct ZM contracts.
  - S&P GSCI ("Goldman roll") [academic] (Hu and Peterson, NCCC-134 2014, R3b_nccc_gsci_roll_returns.pdf): "20% of
    the total number of contracts of a sooner-to-expire commodity futures contract will be sold and the same number of
    contracts of a later-to-expire contract will be bought each day from the 5th business day to the 9th business day
    of the month." Its 24 constituents for 2007-2013 include "Corn, Chicago Wheat, and Soybeans" from CBOT, and not
    soybean meal or soybean oil. So the Goldman roll touches ZM only through ZS and the crush. Whether S&P added soy
    products after 2013 was not checked (the S&P methodology PDF returned 403) [unverified].
  - Price impact of index rolls: Mou (2010/2011, SSRN 1716841 and Columbia thesis) reports that front-running the
    GSCI roll earned high Sharpe ratios in 2000-2010 [unverified: search snippet of the abstract; Columbia's copy sits
    behind a bot wall and SSRN is blocked].
- Volume migration before notice [academic]:
  - Arzandeh and Frank (R3b_arzandeh_frank_caes2017.pdf), roll date defined as the day "when its aggregate volume
    traded for two consecutive days falls below that of the second nearest contract": "traders of grains, on average,
    roll their position over three weeks before the expiration date of their contract." Their Table 1 (ZS): January
    2016 contract (expiring 14 Jan 2016) nearby until "20 Dec. 2015"; March 2016 (expiring 14 Mar 2016) nearby "21 Dec.
    2015 - 21 Feb. 2016"; May 2016 from "22 Feb. 2016".
  - Ma and Serra (R3b_afajof_63476_ma_serra.pdf) and Ma et al. 2026 use the same two-day volume rule; E.0 K6-031
    recorded Hu, Mallory, Serra and Garcia (NCCC-134 2017): in corn "the nearby contract loses dominance" in price
    discovery when its volume share falls below 50%, "about 2-3 weeks before expiry" (E.0's summary, abstract quote
    truncated in E.0's file).
  - Ma et al. 2026: implied liquidity is 16-18% of touch depth in the first nearby but about 51-52% in the second
    nearby (section b), so the second contract's displayed outright book understates its liquidity most in the weeks
    before the roll, when it is about to become the front.
- COT [regulator] (CFTC, R3b_cftc_cot_index.html): "The COT Report is generally published each Friday at 3:30 pm
  Eastern Time (US), using the data from the immediately preceding Tuesday of that week." and "Note that holidays can
  change the COT release schedule."

##### c.2 Worked example: one ZM contract's calendar (ZMH3, March 2023), dates only

- Last trading day: business day preceding 15 March 2023 (a Wednesday) = Tuesday 14 March 2023.
- Assumed first notice day (last business day of February 2023) = Tuesday 28 February 2023 [inferred rule].
- Limits removed under chapter 13: "second business day preceding the first day of the delivery month"; 1 March 2023
  is a Wednesday, so the business days before it are 28 Feb (1st) and 27 Feb (2nd): Monday 27 February 2023.
- Limits removed under the E.0 CME text: "business day prior to first notice day" = business day before 28 Feb =
  Monday 27 February 2023. Check: both rules give 27 February, consistent with the assumed first notice day.
- BCOM roll from ZMH3 to ZMK3: business days 6-10 of February 2023. Weekdays from 1 Feb: 1, 2, 3, 6, 7, 8 (6th), 9,
  10, 13, 14 (10th); no US holiday falls before 20 Feb. Roll window 8-14 February 2023, 20% a day.
- Ordering: BCOM roll (8-14 Feb) comes about two weeks before first notice (28 Feb). For ZS in early 2016, Arzandeh and
  Frank's volume crossover for the March contract fell on 22 Feb 2016 (first notice 29 Feb 2016 under the same
  rule, a Monday), while BCOM's 6th-10th business days of February 2016 were 8-12 February (weekdays 1-5, 8, 9, 10,
  11, 12). So, in that one ZS case, the index roll came about ten days before the volume crossover, which came
  about one week before first notice [inferred; one contract, ZS not ZM].

##### c.3 What this means for a ZM directional search

- The front-month label matters: the owned ZM.v.0 is a volume-ranked continuous series, so its switch date moves with
  traders (about 1-2 weeks before first notice in the ZS example), not with the calendar. Every label horizon must be
  computed within one contract (never across a v.0 switch), and the switch day itself should be excluded or flagged.
- Planner family 8 (index roll, first notice, COT) as flags or exclusions, not as alpha families:
  - roll flag: BCOM business days 6-10 in Feb, Apr, Jun, Oct and Dec for ZM; GSCI business days 5-9 in ZS roll
    months (ZS schedule not retrieved here) as a ZS-side flag;
  - notice flag: from the business day before first notice to last trade of the expiring contract (the spot month
    has no price limits and a 1,500-lot federal spot limit, so large speculators exit before it);
  - COT flag: Friday 14:30 CT release (15:30 ET) falls after the 13:20 CT day close, so the first ZM session that can
    react is Sunday 19:00 CT. Any COT-based feature must be stamped no earlier than that release, never at the Tuesday
    as-of date.
- A directional "front-run the index roll" family for ZM is weak: BCOM's ZM weight is about 3.5%, the published
  evidence is for GSCI (which, at least to 2013, did not hold ZM), the Mou result is unverified here, and the
  Dubois-Marechal counterpoint (search snippet only) says the edge vanished after costs. Keep it as a flag.
- Regime break to state in the protocol: federal limits changed with the 2020 final rule (compliance 2022 for
  exchanges), between the sealed test window (2017-2020) and discovery (2020-12 to 2024-02).

#### (d) Seasonality of liquidity: intraday pattern, day versus overnight, growing season, report days

##### d.1 Facts

- Intraday U shape in CBOT grains [academic]:
  - Ma and Serra working version (R3b_afajof_63476_ma_serra.pdf, CME corn, soybean and wheat MBO 2019-01 to 2020-06):
    "the intra-session distribution of market activity is specially concentrated at the market open and close for
    both the day and night trading sessions, leading to the well-known 'U' shape activity pattern" and "the night
    session activity reaches a minimum at around 12 a.m., and subsequently increases reaching peaks at around 7:30 a.m.,
    i.e., 15 minutes before the night session closes." They tie the day-session U to liquidity providers "who do not
    hold significant overnight positions and thus unwind their positions before the end of day".
  - Wang (NCCC-134 2019, R3b_wang_nccc2019_invariance.pdf, corn, soybeans, wheat nearby, 2008-01 to 2015-05, 1-minute
    averages over the day session): "all other metrics of trading activity show the well-known U-shape of intraday
    seasonality, namely higher activity at the beginning and the end of the trading day."
- Day versus overnight:
  - ZM's day session carried 0.83 of front-contract volume in E.28's standard window (READER_BRIEF table, from
    reports/stage_e28_briefs/A0_contract_stats.md Table 1; ZS 0.78, ZL 0.82).
  - Ma and Serra: "most trades occur during the day trading session (e.g., Lehecka, Wang, and Garcia 2014)" and the
    same holds for limit-order submission, execution, deletion and revision (their Figure D1).
  - Peng, Hu, Robe and Adjemian (R3b_peng_hu_robe_adjemian_2021.pdf) analyse day and overnight sessions separately and
    find the 2020 soybean depth collapse "in both the outright and calendar spread markets, and in the daytime and
    overnight sessions" [academic].
  - Overnight market-maker incentives existed for corn, wheat and soybeans from 2009 [regulator-hosted CBOT filing,
    R3b_cftc_rul100909cbot001.pdf]: "Limited to Extended Trading Hours (ETH) from 6PM -7:15AM Chicago time"; soybean
    meal is not named in that program. Whether a ZM program ran in 2017-2024 was not found.
  - A CME 2022 article ranks Asia-hours spreads "corn ... followed by Soybean, Soybean Meal, Wheat, and Soybean Oil"
    [unverified: search snippet of a cmegroup.com page, not fetched under the stage rule].
- Growing season and contract cycle [academic] (Wang, Garcia and Irwin, corn BBO 2008-2010, E.28-saved
  reports/stage_e28_briefs/pages/A1_grains/agecon_wang_garcia_irwin_confp04-12.txt, abstract): "Over the extended
  horizon that a contract is traded there exist a pronounced non-linear U-shaped maturity pattern, and a strong
  seasonality consistent with the term structure of implied volatilities." "the BAS is generally small (well below two
  ticks)". "USDA Grain Stock and Production-WASDE announcements significantly widen the BAS, as do short-term price
  trends. The index fund roll has little impact on the BAS, but contract specific effects are present reflecting a
  seasonal pattern where the BAS is lowest in December, and highest in September." No ZM-specific seasonal liquidity
  study was found (stopping rule: three discovery searches on ZM liquidity seasonality surfaced only ZS, corn or CME
  marketing material).
- Report days [academic]: Ma and Serra study "90 minutes before, during and after the WASDE announcements" (released
  "monthly at 11:00 Central Time"; 17 announcement days in their sample): "the uncertainty prior to the announcement
  causes a change in trading strategy, with the most aggressive limit orders, especially aggressive cancellations, and
  aggressive trades triggering larger price impacts (up to 2 bps) than on non-announcement days." Arzandeh and Frank
  (footnote 9) cite Lehecka et al. (2014): "announcement effects of major USDA reports on corn futures prices and volume
  disappear in ten minutes" [secondary citation; Lehecka et al. not read here; R4_events owns report effects].
- Stress regime inside the sealed test window [academic] (Peng et al. 2021, abstract lines 59-68): "soybean
  futures-market depth collapses weeks before" the March 2020 crash; "Soybean depth drops by half for outright futures
  and by over 90 percent for calendar spreads"; the pullback "coincides with overnight news of bleak COVID-19
  developments in China".
- E.31 (reports/E.31_RETURN.md line 202): passive ZM fills "0-5 minutes after a USDA release -8.98 (68 fills)" ticks
  gross at 10 s, the worst bucket measured.

##### d.2 Worked example: what a one-tick spread costs in basis points at ZM prices, and how volatility scales by session

- One ZM tick is 0.10 USD/short ton. At a price of 400 USD/short ton: 0.10 / 400 = 0.00025 = 2.5 bp. At 300 USD/ton:
  0.10 / 300 = 0.000333 = 3.33 bp. Check: 2.5 bp x 400 / 300 = 3.33 bp.
- A 1-lot round trip by market orders against a one-tick spread pays one tick (half a tick each way) plus fees:
  1 tick + 0.528 ticks (Topstep 5.28 USD / 10.00 USD per tick) = 1.528 ticks, about 1.53 x 2.5 = 3.8 bp at 400 USD/ton.
  This sits just under E.28's market-order break-even for Topstep ZM, reports/stage_e28_ranking.md line 130:
  "| 6 | topstep | ZM | 2.69 | 2 | 4 | 2 | 1 | 2 | 3 | 2.475 | 2.150 | 2.312 | 0.59 | 1.59 | ..." (header line 123:
  "... | mu*_lim | mu*_mkt | ..."), so mu*_mkt = 1.59 ticks. Check: 1.59 - 1.528 = 0.06 ticks, which E.28's model
  attributes to more than a pure one-tick spread [E.28's cost model not re-derived here].
- Volatility per horizon under a random-walk assumption (stated): sigma_h = sigma_1m x sqrt(h), sigma_1m = 3.15 ticks
  (E.28 A0, regular dates). 5 min: 3.15 x 2.236 = 7.04 ticks; 15 min: 3.15 x 3.873 = 12.20; 60 min: 3.15 x 7.746 =
  24.40. Check: 24.40 / 7.04 = 3.47, and sqrt(60/5) = sqrt(12) = 3.46. The 3.15 figure is an all-session regular-date
  average; the U shape means the open, the close and report minutes carry more of it, and the overnight hours less.
  How much less is not recorded in E.28 A0 [no figure available; E.33 must measure it on discovery data].

##### d.3 What this means for a ZM directional search

- Time of day is a first-order conditioner: costs (spread, depth) and volatility both follow the U, so any label or
  feature must be stratified by session and hour (the planner's mandatory strata). A rule that trades evenly through
  the overnight will pay the same 1.53 ticks against much smaller expected moves.
- The overnight minimum near midnight CT and the peak near 07:30 CT (Ma and Serra, grains) suggest the overnight-to-day handover
  (planner family 4, gap at the 08:30 open) sits in the liquid part of the cycle; the 00:00-06:00 CT stretch is the
  thin part, where a market order's cost relative to the move is worst.
- Report windows: exclude a fixed window around 11:00 CT WASDE (and other USDA releases R4 lists) from any
  non-event family; E.31's -8.98 ticks for passive fills 0-5 minutes after releases shows how toxic those minutes are.
- Seasonality by contract month and growing season is documented for corn spreads, not ZM; leave it as a stratum to
  report, not a family.
- The February-April 2020 soybean liquidity collapse sits inside the sealed test window (2017-05 to 2020-11). A model
  selected on 2020-12 to 2024-02 meets a stress regime in the test that discovery never saw; the protocol should say so
  in advance.

#### (e) Liquidity costs and spillovers across the soybean complex

##### e.1 Facts

- de Boer, Gardebroek, Pennings and Trujillo-Barrera, "Intraday liquidity in soybean complex futures markets", J.
  Futures Markets 42(7) 1189-1211, 2022 [academic]. Abstract only (WUR research portal, R3b_wur_deboer2022.html;
  full text not reachable: Wiley pdfdirect 403 (R3b_wiley_deboer2022.pdf, a 5.8 kB block page), no repository file at
  WUR or Maastricht; OpenAlex lists it as "green" but the only OA location is the WUR landing page without a file):
  "A multidimensional liquidity measure is derived from the limit-order-book, and a Vector Heterogeneous Autoregressive
  model estimates high-resoluted liquidity from 30 s to one trading day. We find traders' order placement influenced by
  the liquidity of related markets. Liquidity persistence and positive liquidity spillovers mainly occur within 30 s,
  whereas spillovers for longer horizons are mostly negative." The round-trip costs the planner quotes (9.2 bp ZS,
  12.5 bp ZL, 13.6 bp ZM) and the 2015 sample year are not in the abstract [unverified].
- A liquidity measure of that kind, from the same research group [academic] (Zhou, Bagnarosa, Gohin, Pennings and
  Debie, J. Commodity Markets 30 (2023) 100314, saved by R3a: reports/stage_e32_briefs/pages/R3a_crush/
  zhou_jcm2023_wur.pdf.txt lines 619-633), the Exchange Liquidity Measure:
  "The XLM (Exchange Liquidity Measure) calculates the round-trip liquidity premium for buying and selling a chosen
  volume, i.e., how much the average transaction price deviates from the mid-price."
  Equations (their (17)-(19)):
      XLM_B,t(V) = 10,000 x (P_B,t(V) - MP_t) / MP_t
      XLM_S,t(V) = 10,000 x (MP_t - P_S,t(V)) / MP_t
      XLM_t(V)   = XLM_B,t(V) + XLM_S,t(V)
  "where, MP_t is the mid-price at time t, P_B,t(V) is the average transaction price of a buy-initiated market order
  with dollar value V at time t, P_S,t(V) is the average transaction price of a sell-initiated market order with dollar
  value V at time t". In Zhou et al. "the dollar value is set to be the median dollar value of the order book spanning
  the full year." Whether de Boer et al. use XLM and which V is not verified [inferred: same group, "multidimensional
  liquidity measure ... derived from the limit-order-book"].
  Zhou et al. (line 125): "volume is significantly related to crush-spread cointegration in certain markets,
  particularly soymeal."
- Information beyond the touch, soybeans (ZS) [academic] (Arzandeh and Frank, CAES 2017 working version of the AJAE
  2019 paper, R3b_arzandeh_frank_caes2017.pdf; CME market-depth data 23 Nov 2015 to 31 Mar 2016, ten-level book):
  abstract: "the steps of the LOB beyond the BAS contribute by over 27% to price discovery of futures contracts" (all
  six contracts); soybeans: midpoint IS "30.16% for soybeans", PT "soybeans (43.72%)", MIS "40.66% for soybeans";
  sampling interval = average price duration: "average price duration is 7.60 seconds for soybeans, lower than that
  for corn, 8.63 seconds". Soybean meal is not in their sample.
- What carries price discovery in the soybean book (ZS, corn, wheat) [academic] (Ma and Serra working version,
  R3b_afajof_63476_ma_serra.pdf, MBO 2019-01-07 to 2020-06-26, day session, daily SVAR information shares, medians):
  "while trades moving the BBO contribute by about 27%-30% to corn and soybean price discovery, they represent around
  42% of the wheat price discovery. Limit order submissions or cancellations moving the BBO jointly represent around
  56% of the corn and soybean price discovery". The SVAR "is estimated daily for each market and each trading
  session" in event time; information shares are variance shares of the efficient-price innovation (a contemporaneous
  and short-lag attribution, not a forecast of future returns). Their method: "We consider both implied and outright liquidity in
  our analyses." The published AJAE 2025 version (doi 10.1111/ajae.12479, cc-by-nc-nd per OpenAlex) was not read; its
  IDEAS abstract (saved by M1) gives the deletion share as "Between 75% and 79%".
- Cross-product lead-lag in seconds is M2's topic (reports/stage_e32_briefs/M2_lead_lag.md); not repeated here.

##### e.2 Worked example: converting a basis-point round-trip cost into ZM ticks

- A 1-lot at a one-tick ZM spread, mid 400.00 USD/ton: P_B = 400.05, P_S = 399.95. XLM_B = 10,000 x 0.05 / 400 =
  1.25 bp; XLM_S = 10,000 x 0.05 / 400 = 1.25 bp; XLM = 2.50 bp = 1 tick. Check: 1 tick / 400 x 10,000 = 2.5 bp.
- The planner's 13.6 bp for ZM, IF it is an XLM round trip: at 400 USD/ton, 13.6 / 10,000 x 400 = 0.544 USD/ton =
  5.44 ticks; at 300 USD/ton, 13.6 / 10,000 x 300 = 0.408 USD/ton = 4.08 ticks. Both are several times a one-tick
  spread, so the figure must refer to an order far larger than 1 lot (a median-book dollar value in Zhou et al.'s
  definition), not to a 1-lot trader's cost. Check: 5.44 / 4.08 = 1.333 = 400 / 300.
- Ratios between legs (if the planner's numbers are right): ZM / ZS = 13.6 / 9.2 = 1.48; ZL / ZS = 12.5 / 9.2 = 1.36.
  Cross-leg bp ratios say nothing about ticks per leg without each leg's price and V.

##### e.3 What this means for a ZM directional search

- "ZM is the least liquid leg" is plausible but unverified here; what matters to a 1-lot is the touch spread and depth,
  which the owned ZM MBO measures directly. E.33 should report ZM's spread distribution by session and hour from
  discovery data before any cost assumption is frozen; a bp figure for a large V must not be used as a 1-lot cost.
- Spillovers "within 30 s" and negative beyond: the cross-product liquidity link is a seconds-scale effect. At minutes
  scale, use ZS/ZL liquidity state (spread, depth, recent sweep) only as a conditioner of ZM features; do not build a
  family on "liquidity spills into ZM later" (the abstract says longer-horizon spillovers are mostly negative).
- Information is in the book, not only in trades: in ZS, cancellations and submissions that move the BBO carry about
  56% of price discovery and trades that move it about 27-30%; levels beyond the touch carry 30-44% by the various
  measures in late 2015-early 2016. For ZM this supports MBO-based features (BBO-moving cancellations, depth beyond
  the touch) as conditioners, with two caveats: these are contemporaneous attributions, not forecasts (the planner's
  note says the same), and ZM was in neither sample.
- Mechanism to drop: any claim that a single "leader" leg sets the price for minutes; nothing read here supports a
  minutes-scale liquidity lead from ZS or ZL into ZM.

#### Summary: what this means for a ZM directional search (all sections)

Worth testing (as conditioners or flags, frozen before E.33 looks at returns):
1. Session and hour strata, report-window exclusions (11:00 CT WASDE and R4's list), notice and roll flags (sections c
   and d). These change cost and volatility more than any book feature.
2. MBO book features at and beyond the touch (BBO-moving cancellations and submissions, depth at levels 2+) as
   conditioners, with the pro-rata over-sizing confound written into their definitions (sections a and e).
3. Side-None or no-resting-quantity prints as a candidate flag for implied (calendar or crush) flow, with the share of
   such prints reported (section b).
4. ZS/ZL liquidity state (spread, depth, sweeps) as a conditioner of ZM, not as a lead signal (section e).

Drop:
- queue-position modelling for a 1-lot under K (section a);
- any feature that needs implied depth (the owned data cannot rebuild it; section b);
- a "front-run the index roll" alpha family for ZM (section c; BCOM weight about 3.5%, GSCI did not hold ZM through
  2013, Wang-Garcia-Irwin find the roll has "little impact on the BAS" in corn, Mou unverified);
- minutes-scale cross-product liquidity spillover as a signal (section e; the abstract puts positive spillovers within
  30 s).

Data-handling rules for E.33 that follow from these facts (proposals for the lead; not decisions):
- labels never cross a ZM.v.0 contract switch; the switch day is flagged;
- COT features time-stamped at Friday 14:30 CT, usable from the Sunday 19:00 CT open;
- costs from the owned outright touch (conservative), never from a bp figure measured for a large order;
- the 2020 COVID liquidity collapse and the 2021-2022 change in federal position limits are named in advance as
  regime differences between the sealed test window and discovery.

#### Planner pointers: verification table

| Planner claim | Status | Evidence (file) | What differs or why |
|---|---|---|---|
| de Boer et al. JFM 2022: liquidity spillovers mostly within 30 s | VERIFIED (abstract) | R3b_wur_deboer2022.html: "Liquidity persistence and positive liquidity spillovers mainly occur within 30 s, whereas spillovers for longer horizons are mostly negative." | Abstract only; full text not reachable (Wiley 403, no repository file). The abstract says POSITIVE spillovers within 30 s and mostly negative beyond. |
| de Boer et al.: round-trip liquidity cost 9.2 bp ZS, 12.5 bp ZL, 13.6 bp ZM; ZM least liquid; 2015 data | UNVERIFIED | none | Not in the abstract; full text unread. If the measure is XLM at a median-book dollar value (as in Zhou et al. 2023, same group), 13.6 bp is 4-5.4 ZM ticks for a large order, not a 1-lot cost (section e.2). |
| Arzandeh and Frank AJAE 2019: soybean price duration about 7.6 s | VERIFIED (working-paper version) | R3b_arzandeh_frank_caes2017.pdf: "average price duration is 7.60 seconds for soybeans" | From the CAES 2017 version of the same study (Nov 2015-Mar 2016 data); the AJAE 2019 text was not read. ZS, not ZM. |
| Arzandeh and Frank: book levels beyond the best quote carry more than 27% of price discovery | VERIFIED (working-paper version), with a nuance | same file: "the steps of the LOB beyond the BAS contribute by over 27% to price discovery of futures contracts" | "Over 27%" is the floor across all six contracts; for soybeans the shares are 30.16% (ISM), 43.72% (PT), 40.66% (MIS). |
| Ma and Serra AJAE 2025: trades moving the best quote 27-30% of discovery | VERIFIED (working-paper version) | R3b_afajof_63476_ma_serra.pdf: "trades moving the BBO contribute by about 27%-30% to corn and soybean price discovery" | Working version (AFA listing), not the AJAE text. Corn and soybeans (ZS); wheat about 42%. Day session, median daily IS. |
| Ma and Serra: limit submissions and cancellations at the touch about 56% | PARTLY VERIFIED | same file: "Limit order submissions or cancellations moving the BBO jointly represent around 56% of the corn and soybean price discovery" | The paper says "moving the BBO" (improving submissions and worsening cancellations), not "at the touch"; submissions and cancellations AT the BBO that do not move it are a separate, marginal category. |
| Ma and Serra: contemporaneous; no forward-looking OFI evidence for grains | PARTLY VERIFIED | same file: SVAR "estimated daily for each market and each trading session"; IS as variance decomposition | The method is a contemporaneous/short-lag attribution; "no forward-looking OFI evidence exists for grains" is a literature claim this worker did not search exhaustively (M1 owns OFI). |
| K algorithm: TOP priority capped at 100 contracts on grain outrights | VERIFIED | R3b_cftc_aac041119_cmegroup.pdf (CFTC-hosted CME slide): "TOP MAX in grain outrights is 100 contracts and 1000 contracts in grain spreads." | E.31 found ZM-ZM spread rows showing 100, not 1000, in the product sheet [E.31 cmegroup-origin]. |
| K algorithm: then 40% FIFO, then 60% pro rata with levelling, then FIFO residual | VERIFIED | same file: "40% of the incoming aggressing order is allocated by timestamp"; "60% ... based on the size of the resting orders"; levelling "maximum of 1 contract allocated per order"; "Any residual quantity remaining is filled FIFO." | Levelling eligibility wording differs between the CFTC slide and the CME wiki (section a.1). |
| K algorithm applies to ZM | VERIFIED (owned data, via E.31) | reports/E.31_RETURN.md line 168: "all outrights K" | The CFTC slide says "Grain Futures" without listing products. |
| Globex uses FIFO when the aggressor's size is at least all displayed quantity at the price | PARTLY VERIFIED | E.31-saved CME wiki (cmegroup-origin, not re-fetched): "greater than or equal to the displayed quantity ... CME Globex applies FIFO in lieu of the designated product algorithm" | No CFTC-hosted or academic copy found; rests on a cmegroup-origin file, which the E.32 stage rule does not allow this worker to fetch. |
| Sources named: CME filing 14-270; Peng JFM 2024 | NOT FOUND / NOT A K SOURCE | R3b_ideas_peng_hu_robe_2024.html | Filing 14-270 was not located on cftc.gov (one search). "Peng JFM 2024" is Peng, Hu and Robe, "Maximum order size and market quality", JFM 44(5) 803-825: its abstract is about the 2018 maximum-order-size increase (2,500 to 10,000) in calendar spreads, not about K; full text 403 (Wiley). |
| Implied intercommodity spreads (board crush SOM 10 ZS:11 ZM:9 ZL; calendars; butterflies; ZM-MZM) feed the outright book | PARTLY VERIFIED | Ma et al. 2026 (calendar implieds feed outrights); Peng et al. 2021 (implied-out/implied-in); E.31-saved CME page ("Soybean Crush spreads" are ICS ratio spreads in predetermination) | SOM legs 10:11:9 from R3a and a search snippet only; butterflies and ZM-MZM implieds not checked. |
| Implied bids and offers are eligible but "not disseminated in market data" | PARTLY VERIFIED | E.31-saved CME page: "(these implieds will not be visible via market data)" in the ratio-spread (ICS) context; Databento docs: CME's MBP feed carries "2 levels of implied liquidity" | True for ratio-spread (crush) implieds; FALSE as a general statement: calendar-spread implieds ARE disseminated, on the MBP feed's implied book (2 levels), though not in MBO (and so not in the owned ZM MBO or the owned MBP-1). The exact phrase was not found in any file this stage may read. |
| Ranked family 8: index roll, first notice day and COT as regime flags or exclusions | SUPPORTED as flags | BCOM methodology (ZM roll BD 6-10 in Feb/Apr/Jun/Oct/Dec); Hu-Peterson (GSCI BD 5-9, no ZM to 2013); CBOT ch. 13 (E.28 file); CFTC COT page (Fri 15:30 ET, Tuesday data); Wang-Garcia-Irwin (roll has "little impact on the BAS", corn) | Not supported as an alpha family (section c.3). First notice day definition rests on an inference from two price-limit rules plus a search snippet. |

#### Evidence table

| # | Claim | Source (label) | Verbatim quote | Saved file |
|---|---|---|---|---|
| 1 | K in grain futures: TOP cap 100 outrights | CME slide to CFTC AAC 2019-04-11 (exchange, regulator-hosted) | "TOP MAX in grain outrights is 100 contracts and 1000 contracts in grain spreads." | pages/R3b_microstructure/R3b_cftc_aac041119_cmegroup.pdf |
| 2 | K FIFO 40% | same | "40% of the incoming aggressing order is allocated by timestamp." | same |
| 3 | K pro rata 60% | same | "60% of the incoming aggressing order is allocated based on the size of the resting orders." | same |
| 4 | Levelling 1 lot max | same | "Any order that did not participate in the Pro-Rata pass is eligible for rounding with a maximum of 1 contract allocated per order." | same |
| 5 | Realized allocation shares | same | "~7% TOP", "~56% FIFO", "~23% Pro-Rata", "~14% Leveling" | same |
| 6 | ZM outrights are K (owned data) | E.31 return (program record) | "all outrights K" | reports/E.31_RETURN.md line 168 |
| 7 | FIFO exception for sweeps | CME client wiki (exchange) [E.31 cmegroup-origin, not re-fetched] | "greater than or equal to the displayed quantity ... CME Globex applies FIFO in lieu of the designated product algorithm" | reports/stage_e31_briefs/research/K_algorithm.md (a) |
| 8 | Pro-rata markets oversize and cancel | Field and Large 2008 (academic) | "strategic complementarities in the choice of limit order size cause traders to risk overtrading by submitting over-sized limit orders, most of which they expect to cancel." | R3b_field_large_2008_prorata.pdf |
| 9 | Grain limit-order life | Ma and Serra WP (academic) | "around 75-79% are deleted and 7%-8% revised" / "half of the limit orders being deleted within 2-5 seconds" | R3b_afajof_63476_ma_serra.pdf |
| 10 | Implied functionality mechanism | Ma, Serra, Peterson, Irwin 2026 (academic) | "liquidity in calendar spreads generates synthetic and contingent quotes in outrights" | R3b_richie_ma_serra_2026_calendar_spreads.pdf |
| 11 | Implied share of touch depth, corn/soy | same | "For the first-nearby futures, implied liquidity contributes 16.00%-17.97% to consolidated liquidity, rising to 50.97%-52.48% for second-nearby futures." | same |
| 12 | Outright priority over implied | same (citing CME 2007) | "outright quotes have matching priority over implied quotes (CME 2007)" | same |
| 13 | Implied-out / implied-in definitions | Peng, Hu, Robe, Adjemian 2021 (academic) | "orders in the outright book created based on orders in the spread market ("implied-out") or ... orders in the calendar spread book created based on orders in the outright market ("implied-in")" | R3b_peng_hu_robe_adjemian_2021.pdf |
| 14 | MBP feed: 2 implied levels | Databento GLBX.MDP3 docs (firm) | "The MBP feed provides up to 10 levels of real liquidity and 2 levels of implied liquidity." | R3b_databento_glbx_mdp3.md |
| 15 | Merged book only in CMBP-1 | same | "Databento combines the real and implied books, publishing the merged top-of-book on the [CMBP-1] schema." | same |
| 16 | Implied trades lack aggressor side | same | "Implied trades ... may not have an aggressing side set. These trades will be normalized with side set to None." | same |
| 17 | Implied matches lose order details | Ma and Serra WP (academic) | "Order details (e.g., order ID, matched quantity, aggressor) are not provided for those market orders that are executed against implied order(s)." | R3b_afajof_63476_ma_serra.pdf |
| 18 | Crush is an ICS ratio spread; ratio implieds not visible | CME wiki (exchange) [E.31 cmegroup-origin, not re-fetched] | "Examples include Treasury ICS and Soybean Crush spreads." / "(these implieds will not be visible via market data)" | reports/stage_e31_briefs/research/pages/K/wayback_algorithms_near20231201.txt |
| 19 | Implied never matches implied | same | "Implied quantity will never match with implied quantity." | same |
| 20 | CME switched corn implieds off in 2010 | Overdahl 2011, FIA-PTG sponsored (practitioner) | "On Jan. 31, 2011, the CME turned on implied matching functionality for corn futures after turning off this functionality in August 2010." | R3b_nera_overdahl_2011.pdf |
| 21 | ZM months | CBOT Rulebook ch. 13 (exchange) [E.28 cmegroup-origin, not re-fetched] | "eight months - September, October, December, January, March, May, July, and August" | reports/stage_e28_briefs/pages/A1_grains/cbot_rulebook_ch13.txt |
| 22 | ZM last trading day | same | "after the business day preceding the 15th calendar day of that month" | same |
| 23 | Limits off before delivery month | same | "no price limits on the current month contract on or after the second business day preceding the first day of the delivery month" | same |
| 24 | Limits off before FND | CME (exchange) [E.0 cmegroup-origin] | "price limits are removed on the business day prior to first notice day of an expiring contract month" | reports/stage_e0_research_K6.md line 672 |
| 25 | Federal ZM spot limit | CFTC speculative limits page (regulator) | "CBOT Soybean Meal (SM) | 1,500" (spot month, 2020 final rule) | R3b_cftc_speculative_limits.html |
| 26 | Federal ZM single/all-months limit | same | "CBOT Soybean Meal (SM) | 16,900" | same |
| 27 | BCOM roll window | BCOM methodology (firm) | "the sixth through tenth Business Days of the month ... at the rate of 20% per Business Day" | R3b_bcom_methodology.pdf |
| 28 | BCOM ZM contract calendar | same | "Soybean Meal Mar Mar May May Jul Jul Dec Dec Dec Dec Jan Jan" | same |
| 29 | GSCI roll window | Hu and Peterson NCCC-134 2014 (academic) | "each day from the 5th business day to the 9th business day of the month" | R3b_nccc_gsci_roll_returns.pdf |
| 30 | GSCI CBOT constituents 2007-13 | same | "Corn, Chicago Wheat, and Soybeans, all traded at Chicago Board of Trade (CBOT)" | same |
| 31 | Grain roll timing | Arzandeh and Frank WP (academic) | "traders of grains, on average, roll their position over three weeks before the expiration date of their contract." | R3b_arzandeh_frank_caes2017.pdf |
| 32 | COT timing | CFTC COT page (regulator) | "generally published each Friday at 3:30 pm Eastern Time (US), using the data from the immediately preceding Tuesday" | R3b_cftc_cot_index.html |
| 33 | Intraday U, day and night | Ma and Serra WP (academic) | "concentrated at the market open and close for both the day and night trading sessions, leading to the well-known 'U' shape" | R3b_afajof_63476_ma_serra.pdf |
| 34 | Night minimum and 07:30 peak | same | "the night session activity reaches a minimum at around 12 a.m., and subsequently increases reaching peaks at around 7:30 a.m." | same |
| 35 | U shape 2008-2015 grains | Wang NCCC-134 2019 (academic) | "all other metrics of trading activity show the well-known U-shape of intraday seasonality" | R3b_wang_nccc2019_invariance.pdf |
| 36 | Corn BAS: reports widen, roll little impact, seasonal | Wang, Garcia, Irwin (academic) [E.28-saved] | "The index fund roll has little impact on the BAS, but contract specific effects are present reflecting a seasonal pattern where the BAS is lowest in December, and highest in September." | reports/stage_e28_briefs/pages/A1_grains/agecon_wang_garcia_irwin_confp04-12.txt |
| 37 | WASDE window price impacts | Ma and Serra WP (academic) | "aggressive trades triggering larger price impacts (up to 2 bps) than on non-announcement days" | R3b_afajof_63476_ma_serra.pdf |
| 38 | 2020 soybean depth collapse | Peng et al. 2021 (academic) | "Soybean depth drops by half for outright futures and by over 90 percent for calendar spreads" | R3b_peng_hu_robe_adjemian_2021.pdf |
| 39 | Overnight MM program (corn, wheat, soybeans, 2009) | CBOT filing (exchange, regulator-hosted) | "Limited to Extended Trading Hours (ETH) from 6PM -7:15AM Chicago time" | R3b_cftc_rul100909cbot001.pdf |
| 40 | Soy-complex spillovers within 30 s | de Boer et al. 2022 abstract (academic) | "Liquidity persistence and positive liquidity spillovers mainly occur within 30 s, whereas spillovers for longer horizons are mostly negative." | R3b_wur_deboer2022.html |
| 41 | XLM definition | Zhou et al. JCM 2023 (academic) [R3a-saved] | "The XLM (Exchange Liquidity Measure) calculates the round-trip liquidity premium for buying and selling a chosen volume" | reports/stage_e32_briefs/pages/R3a_crush/zhou_jcm2023_wur.pdf.txt |
| 42 | Beyond-BBO information share | Arzandeh and Frank WP (academic) | "the steps of the LOB beyond the BAS contribute by over 27% to price discovery of futures contracts" | R3b_arzandeh_frank_caes2017.pdf |
| 43 | Soybean price duration | same | "average price duration is 7.60 seconds for soybeans" | same |
| 44 | BBO-moving trades and orders, ZS | Ma and Serra WP (academic) | "trades moving the BBO contribute by about 27%-30% to corn and soybean price discovery" / "Limit order submissions or cancellations moving the BBO jointly represent around 56%" | R3b_afajof_63476_ma_serra.pdf |
| 45 | Index-roll front-running profits | Mou 2010/2011 | Sharpe ratios "as high as 4.4" (abstract wording via search snippet) | none [unverified] |
| 46 | SOM legs 11 ZM, 9 ZL, 10 ZS | CME 2009 notice | "Eleven (11) Soybean Meal futures contracts" (search snippet) | none [unverified] |
| 47 | Planner round-trip bp costs | de Boer et al. 2022 | none | none [unverified] |

#### Search log and stopping

- WebSearch calls used: 18 of 80. No budget notice was seen.
- Topics closed by the stopping rule: (a) K: CFTC slide plus E.31's record; two further searches for CFTC-hosted grain
  K filings surfaced only Treasury and swap filings. (b) implied: three full-text sources (Ma et al. 2026, Peng et al.
  2021, Databento docs) plus E.31's CME page; Arzandeh et al. 2025 (SSRN only) and CME 2007 not reachable.
  (c) roll and delivery: BCOM, Hu-Peterson, CBOT ch. 13, CFTC limits and COT pages; FND definition not found in an
  allowed full text after two searches. (d) seasonality: Ma-Serra, Wang 2019, Wang-Garcia-Irwin, Peng et al. 2021;
  three searches for ZM-specific liquidity seasonality found nothing new. (e) costs and spillovers: de Boer full text
  unreachable after five routes (Wiley, WUR, Maastricht, NCCC archive, OpenAlex OA lookup).

#### Not finished, null results and blocks

- de Boer et al. 2022 full text: not reached (Wiley 403; no repository PDF; the 2019 IATRC and 2020 NCCC versions
  are not in the NCCC archive). Its bp costs stay UNVERIFIED.
- AJAE published versions of Arzandeh-Frank (2019) and Ma-Serra (2025) not read (Wiley); working versions used.
- Peng, Hu and Robe JFM 2024 full text 403; SSRN copy not tried (SSRN blocked). IDEALS (Peng thesis) returns 403.
- S&P GSCI methodology PDF: 403; post-2013 GSCI composition unverified. Mou thesis: Columbia bot wall.
- eCFR: the API renderer is disallowed by robots.txt, so that file was deleted unused; the public page is JavaScript;
  the GPO appendix table is an image. Federal limits came from the CFTC page instead; pre-2021 legacy levels and the
  spot-month definition are unverified.
- CME pages (contract specs, SOM notice, Asia-hours article, client wiki "Implied Intercommodity Ratio Spreads") were
  not fetched under the stage rule; facts that rest on earlier stages' cmegroup-origin files are marked.
- Unresolved: how K orders outright versus implied quantity at one price for ZM (Ma et al.'s "outright priority"
  versus the wiki's source-level predetermination).

## R4. Event structure: USDA releases, limits, gaps, settlement

Source file: reports/stage_e32_briefs/R4_events.md (sha256 39534f17a5d4f548f66f88ee6d4aae2e53fec55bd8fa36b86bbc350057c4b18c).

### R4: Event structure in the soybean complex at minutes-to-hours horizons

Stage E.32, worker EventStructure-OpusHigh (root R4_events). Started 2026-10-26 23:03 PDT (first spawn: fetches only,
no output), resumed 2026-10-27 00:16 PDT (this output). Evidence pages and log:
reports/stage_e32_briefs/pages/R4_events/ (log.tsv). Helper scripts: reports/stage_e32_briefs/work/R4_events/.
No market data was read, no statistic was computed from data, no cmegroup.com page or archived copy of one was fetched.

Source labels: [A] academic (paper, thesis, conference paper), [R] regulator (CFTC staff paper, CFTC-hosted
filing), [X] exchange rule text as filed with the CFTC (CFTC-hosted, so secondary for CME), [G] government agency
(USDA), [F] firm or trade association, [P] pointer only (trade press, extension blog): never evidence.

Unit conversions used throughout. ZM tick = 0.10 USD per short ton = 10.00 USD per contract (E.32 brief table).
Percent moves are turned into ZM ticks with an ILLUSTRATIVE price P = 400 USD/short ton. This is an assumption for
scale, not a data read: 1% of 400 USD = 4.00 USD/ton = 4.00 / 0.10 = 40 ticks. At P = 350 the same 1% is 35 ticks,
at P = 450 it is 45 ticks. Random-walk scaling (an assumption) from the brief's sigma_1m = 3.15 ticks:
sigma_15m = 3.15 x sqrt(15) = 3.15 x 3.873 = 12.2 ticks; sigma_60m = 3.15 x sqrt(60) = 3.15 x 7.746 = 24.4 ticks.

---

#### 1. USDA and industry release times against the CBOT sessions (topic a)

##### 1.1 Current session grid (CT) and how it came about

| Date (trade date) | Globex hours for CBOT grains and oilseeds (CT) | Settlement | Source |
|---|---|---|---|
| before May 2012 | overnight Globex plus a day session opening 9:30; USDA reports at 7:30 fell in the pre-open halt and batch auction | floor, 1:14-1:15 p.m. | Huang 2022 [A]; Onur and Reiffen 2018 [R] |
| May 21, 2012 (Couleau et al.; the CFTC-hosted CBOT filing of 2012-05-16, version 002, names "June 3, 2012, for trade date June 4, 2012", and version 003 asks for "as soon as possible": the exact first date is not settled by the filings read) | from "Sunday to Friday, 6:00 p.m. to 7:15 a.m. CT and 9:30 a.m. to 1:15 p.m. CT" to "Sunday to Friday, 5:00 p.m. to 2:00 p.m. CT"; USDA 7:30 a.m. releases now hit live trading | moved to 2:00 p.m. (June 25, 2012), VWAP of all trades (floor and Globex) in the settlement minute | CBOT filings 2012-05-16 (R4_cftc_cbot_2012-05-16_002.txt, _003.txt) and 2013-03-13 [X]; Onur and Reiffen [R]; Couleau et al. 2018 [A] |
| January 2013 | unchanged | unchanged | USDA moves WASDE, Crop Production, Grain Stocks, Acreage, Prospective Plantings to 12:00 noon ET = 11:00 CT, still inside the day session (Huang 2022 [A]; Farm Progress 2012 [P]) |
| April 8, 2013 | Sun-Fri 7:00 p.m. - 7:45 a.m. and Mon-Fri 8:30 a.m. - 1:15 p.m. | close and settlement both 1:15 p.m. | CBOT filing 2013-03-13 [X] |
| June 8, 2015 | unchanged | TAS (Rule 524) allowed in corn, soybeans, soybean oil, soybean meal, wheat: first three listed months, settlement price +- 4 ticks | CBOT/CME Submission 15-148 [X] |
| July 6, 2015 | Mon-Fri day session extended to 8:30 a.m. - 1:20 p.m. (overnight still 7:00 p.m. - 7:45 a.m.) | settlement window kept at 1:14-1:15 p.m. CT; Globex keeps trading 5 minutes after it | CBOT Submission 15-204 [X] |

Consequence for the owned window (2020-12-01..2024-02-29) and the sealed test window (2017-05-01..2020-11-30): both
lie entirely in the post-July-2015 grid (overnight 19:00-07:45, pause 07:45-08:30, day 08:30-13:20, settlement
13:14-13:15, TAS available). There is no session-grid break inside either window [inference from the filings above;
holidays and early closes are not covered here].

##### 1.2 Release calendar per event type

| Event | Publisher | Schedule | Release time | In CT | Session it lands in | Per year | Source |
|---|---|---|---|---|---|---|---|
| WASDE (with Crop Production in the months it is issued) | USDA WAOB (NASS for Crop Production) | monthly, pre-announced (2026: Jan 12, Feb 10, Mar 10, Apr 9, May 12, Jun 11, Jul 10, Aug 12, Sep 11, Oct 9, Nov 10, Dec 10) | 12:00 p.m. ET | 11:00 | day session, 2 h 30 min after the 08:30 open and 2 h 14 min before settlement | 12 | USDA WASDE page [G] |
| Grain Stocks | USDA NASS | quarterly: January, March, June, September | 12:00 p.m. ET (since Jan 2013) | 11:00 | day session | 4 (Jan with the annual Crop Production and WASDE; end-March with Prospective Plantings; end-June with Acreage) | Joseph and Garcia 2016 fn 1 [A]; Farm Progress [P] |
| Prospective Plantings | USDA NASS | annual, end of March | 12:00 p.m. ET | 11:00 | day session | 1 | Joseph and Garcia 2016 fn 1 [A] |
| Acreage | USDA NASS | annual, end of June | 12:00 p.m. ET | 11:00 | day session | 1 | Joseph and Garcia 2016 fn 1 [A] |
| Crop Progress | USDA NASS | weekly (Mondays) April to November; monthly "State Stories" December to March | 4:00 PM (ESMIS lists no zone; NASS times are Eastern [unverified from the page]) | 15:00 if ET | CLOSED: after the 13:20 close and before the 19:00 overnight open; absorbed at the 19:00 open | about 30-35 weekly issues [count is an estimate from "April to November", not a listed number] | ESMIS Crop Progress page [G] |
| U.S. Export Sales (weekly) | USDA FAS | every Thursday | 8:30 a.m. ET | 07:30 | OVERNIGHT session, 15 minutes before the 07:45 pause; the day session opens 08:30 on it | about 52 | FAS fact sheet (updated 2019-05-08) [G] |
| Daily export sales ("flash" sales) | USDA FAS | any business day a large sale is reported | 9:00 a.m. (zone not stated in the fact sheet; ET assumed [unverified]) | 08:00 if ET | inside the 07:45-08:30 PAUSE, so it is absorbed at the 08:30 open | irregular | FAS fact sheet [G] |
| NOPA monthly crush | NOPA (trade association), distributed by Refinitiv/LSEG to subscribers | monthly, dates published by NOPA (commonly mid-month; the exact day rule is [unverified]) | 12:00 noon "EST" | 11:00 | day session | 12 | NOPA crush report page [F] |

Notes on the table:
- The 2026 NOPA page states the 12:00 noon time for 2026 only. That NOPA used the same 11:00 CT time throughout
  2017-2024 is [unverified] here (no archived NOPA calendar was fetched).
- Grain Stocks, Acreage and Prospective Plantings stack on one release minute with each other or with WASDE, so a
  per-report-type effect cannot be separated on those days; this is a design fact for any event study.
- The March and June report days are also near the roll and first-notice windows of the May and July contracts
  (roll calendars are R-other workers' topic; flagged here only as a confound).

##### 1.3 History of the move to releases during trading hours (verbatim)

- [A] Huang (2022, Illinois PhD thesis, ch. 3, saved R4_ideals_usda_release_policy_2022.txt): "World Agricultural
  Outlook Board reports were released on pre-announced dates at 7:30 AM (Central Time). The release coincided with a
  regular pre-open batch auction that took place during a trading halt for the CME electronic trading platform.
  After the end of the batch auction at 9:30 AM, regular trading hours started on Globex. In May 2012 the CME
  extended the trading hours to cover the early morning USDA release because of the concern of competition from
  another exchange (Arasu & Saphir, 2012). Since then, market participants can trade on the reports in real-time."
  and "In January 2013, the USDA changed the release time to 11:00 AM but the release was still during trading
  hours."
- [A] Couleau, Serra and Garcia (NCCC-134 2018, saved R4_couleau_serra_garcia_nccc2018.txt): "Since May 21, 2012,
  all sensitive USDA reports are released during trading hours (at 7:30:00 am CT until December 2012 and at
  11:00:00 am CT since January 2013)."
- [A] Joseph and Garcia (AAEA 2016, saved R4_joseph_garcia_aaea2016.txt): "In May 2012, the Chicago Mercantile
  Exchange (CME) extended its electronic trading hours. As a result, major United Stated Department of Agriculture
  (USDA) reports released at 7:30 a.m. central time, including World Agricultural Supply and Demand Estimates
  (WASDE), Crop Production (CP), Grain Stocks (GS), Acreage (AC), and Prospective Planting and Small Grains Summary
  (PP), coincided with real-time trading hours. In January 2013, USDA officially shifted these reports releases to
  11:00 a.m., formalizing trading hour releases."
- [P] Farm Progress, 2012-12-19 (saved R4_farmprogress_2012_release_times.html; trade press, pointer only; its
  content matches the [A] sources): "USDA statistical reports affected are: World Agricultural Supply and Demand
  Estimates, Acreage, Crop Production, Grain Stocks, Prospective Plantings, and Small Grains Summary."
- [A] Huang (2022) on the media lockup: "Prior to August 2018, USDA released its reports after an internal lockup
  procedure involving news media to assist with information dissemination. [...] prompted USDA to end news media
  access to the lockup." and "it coincided with more pervasive delays in the release of market information likely
  caused by server congestion or related accessibility issues." The sealed test window (2017-05..2020-11) therefore
  straddles the August 2018 lockup change; the discovery window (2020-12..2024-02) is entirely after it.
- [X] CBOT filing of 2013-03-13 (CFTC-hosted, saved R4_cftc_cbot_2013-03-13.txt): current hours "Sunday to Friday,
  5:00 p.m. to 2:00 p.m. CT", proposed "Sunday to Friday, 7:00 p.m. to 7:45 a.m. CT" and "Monday to Friday, 8:30
  a.m. to 1:15 p.m. CT", effective "Sunday, April 7, 2013 for the Monday, April 8, 2013 trading date"; "In June 2012,
  the Exchange extended afternoon floor hours for these products and moved settlement to 2:00 p.m. CT".
- [X] CBOT Submission 15-204 (CFTC-hosted, saved R4_cftc_cbot_2015_hours_1320.txt): "effective on Sunday, July 5,
  2015 for trade date Monday, July 6, 2015", new hours "Sunday - Friday, 7:00 p.m. - 7:45 a.m. CT and Monday -
  Friday, 8:30 a.m. - 1:20 p.m. CT"; "A continuation of trading would allow TAS liquidity providers to hedge or
  trade as needed after 1:15 p.m./CT and not impact or influence the 1:14-1:15 p.m. CT settlement window."

Verdict on the planner pointer "11:00 CT releases have been made into live trading since 2012": PARTLY VERIFIED.
Releases have hit live trading since May 21, 2012, but at 7:30 CT until December 2012; the 11:00 CT time dates from
January 2013.

---

#### 2. Price discovery after USDA releases: jump, drift or reversal, settling horizon (topic b)

##### 2.1 What is published, per study (full text read unless marked)

| Study | Market, sample | Events | Price result | Volatility result | Direction after the jump |
|---|---|---|---|---|---|
| Huang (2022) ch. 3 [A] | corn nearby, real-time era June 2012 - Aug 2019 | 104 real-time events (WASDE/NASS) | 40% of the 1-hour price change in the first minute, about 75% by 10 minutes, 90-100% by 35-45 minutes | spike in first minutes | conditional on knowing the 60-minute direction: big events keep drifting that way to about 40-49 min; small events overshoot (negative ITR from 40 min) |
| Joseph and Garcia (2016) [A] | soybean nearby (ZS), June 2010 - May 2014, 15-second returns | 29 trading-hour releases (June 2012 - May 2014) vs non-trading-hour releases | not measured as a level | trading-hour releases: smaller first spike, elevated 5-6 min, report-day variance above control for 30-40 min, intermittently to about 60 min | Spearman correlations of first return with later returns: few significant, mostly negative in the first minute, "difficult to establish a solid pattern" |
| Lehecka, Wang and Garcia (2014) [A, abstract only] | corn, July 2009 - May 2012 (pre-real-time) | major USDA reports | "market reactions persist for approximately ten minutes" | - | "little evidence exists to support systematic under- or overreactions" |
| Adjemian and Irwin (2018) [A, abstract only] | grain futures, 2009-2014 | USDA crop reports | - | "heightened volatility dissipates within the space of a few trading minutes" | not stated in the abstract |
| Kauffman (2013) [A] | corn, 2012 WASDE releases | WASDE | - | "excessive for 30 consecutive minutes"; "84 percent of the time" in the 30-60 min window; "only slight evidence" beyond 2.5 h | not studied |
| Couleau, Serra and Garcia (2018) [A] | corn nearby, 2008-2015, tick data | announcement vs other days | announcement-day jumps in period 3 (real-time): +4.1 / -3.8 cents/bu average | jumps on 100% of real-time announcement days, 83% with a cluster inside 2 minutes | not studied |
| Bian, Serra and Garcia (NCCC-134 2018) [A] | corn and soybeans, January 2014 - May 2017 (11:00 CT releases) | USDA announcement days | - | "volatilities in both corn and soybean would response to USDA announcements immediately after the news being published. The elevated level of volatilities would not settle down within the first hour after announcements." (R4_bian_serra_garcia_nccc2018.txt) | not studied |
| Karali (2012), as summarised by Bian et al. [A, secondary; original not read] | daily corn, lean hogs, soybeans, SOYBEAN MEAL, soybean oil, 1995-2009 | Crop Progress, Feed Outlook, Grain Stocks, Hogs and Pigs, others | - | daily: "Crop Progress, Grain stocks, and Hogs and Pigs also increase variances of both corn and soybean meal" | not studied (daily) |
| Hu and Mallory (NCCC-134 2022; JFM 2025 45(11)) [A] | Dalian soybean complex incl. soybean meal, 2010/2011 - 2020/2021 | major USDA reports (released while Dalian is closed) | JFM abstract: "On average, price reactions dissipate within a few minutes, while increased trading volume can last up to an hour"; during the trade war USDA reports "remained influential on soybean no. 2 and soybean meal futures" (R4_hu_mallory_nccc2022.txt; R4_ideas_jfm2025_45_11.html, abstract) | NCCC abstract: reactions "can persist for as long as an hour, depending on the size of the information shock and market liquidity" | not studied in the abstract |
| Shubitidze, Adjemian and Dorfman (AAEA 2026) [A, abstract only] | corn, soybeans, wheat, DAILY prices | WASDE ending stocks, Grain Stocks, with analyst forecast distributions | responses depend on forecast dispersion and "pre-report market tightness"; "the direction of the effect varies across markets and report types" (R4_ideas_shubitidze2026.html) | - | daily only; relevant for building an ex-ante surprise measure, which needs analyst surveys the project does not own |
| Janzen, farmdoc daily 2025-09-15 [P] | corn and soybean new crop, May-Sep 2025 | 5 WASDE + June 30 Acreage | Sep 12 2025: soybeans fell up to 13 c/bu in 11:00-11:15, closed up 13 c | - | pointer: 1 large reversal, and 2 small mismatches, in 6 events |

No study found that tests the sign of the 15-90 minute post-release path against the sign of the initial jump in a
form a trader could use (that is, conditioning only on information available at the entry time). No study of CBOT
soybean MEAL (ZM) or soybean oil (ZL) announcement effects at the intraday level was found; the only intraday
soybean-meal announcement study found is on Dalian (Hu and Mallory), where USDA news lands while that market is
closed, and the only CBOT meal evidence is daily (Karali 2012, via Bian et al.). No intraday study of the NOPA crush
release was found (one WebSearch aimed at it returned none). Discovery status in section 9.

##### 2.2 Verbatim evidence and equations

Huang (2022), complete price change (CPC), eq. (3.1), saved R4_ideals_usda_release_policy_2022.txt:

    CPC_{t,i} = sign(P_{T,i} - P_{c,i}) * (P_{t,i} - P_{c,i})        (3.1)

Symbols: P_{c,i} = log VWAP of the last five trading minutes before announcement i; P_{T,i} = log VWAP of minutes
61-65 after the announcement (real-time era); P_{t,i} = log one-minute VWAP at minute t after the release; CPC in
percent. Quote: "In the real-time era P_{T,i} is the VWAP for the 61-65 minutes after the announcement takes place.
[...] For P_{c,i}, we use the VWAP of the last five trading minutes before announcement in both eras."

Informed trader return (ITR), same section: "ITR_{t,i} = sign(P_{T,i} - P_{c,i}) * (P_{T,i} - P_{t,i})". Quote:
"Our trader is assumed to be informed (i.e., to correctly interpret the implications of the reports to the market)
and to trade in the correct direction".

Results (verbatim): "in the real-time era, price changes necessary to reflect the USDA information are 1.63% for all
events (2.6% and 0.6% for big and small events) [...] it takes only one minute for the price to reflect 40% of the
USDA information. After the first 10 minutes the price reflects about 75% of the information and then moves to a
phase of much slower price discovery. Overall, it takes around 35-45 minutes to reflect 90%-100% of the new
information."

Table 3.1 Panel B (corn, real-time era June 2012 - August 2019, ITR in percent, exit at 60 minutes):

| Entry after release | All | Big | Small |
|---|---|---|---|
| 0-2 s | 1.33*** | 2.14*** | 0.54*** |
| 1 min | 0.72*** | 1.13*** | 0.33*** |
| 2-5 min | 0.61*** | 0.91*** | 0.31*** |
| 6-9 min | 0.47*** | 0.78*** | 0.18** |
| 10-19 min | 0.31*** | 0.65*** | -0.01 |
| 20-29 min | 0.24*** | 0.55*** | -0.06 |
| 30-39 min | 0.15*** | 0.36*** | -0.06 |
| 40-49 min | 0.04 | 0.18*** | -0.10** |
| 50-59 min | -0.02 | 0.04 | -0.07** |

Huang on small events: "Notice that during small events the price initially moves in the opposite direction of the
final price." and on risk: "except for small events during the real-time release era, where ITRs become negative
after 10 minutes following the release."

Critical reading for a directional label (my analysis, not Huang's claim):
- ITR conditions on sign(P_T - P_c), the 60-minute outcome. It is therefore NOT a tradable return: it is the drift
  that remains toward the eventual 60-minute level. It equals the directional label of family 2 only on events where
  the early jump and the 60-minute move share a sign.
- What it does say: for big events, about 0.65% of corn price is still to come after minute 10, in the direction of
  the eventual 60-minute move. Translated to ZM scale (assumption: the same percent applies to ZM; P = 400 USD/t):
  0.65% x 400 = 2.60 USD/t = 26 ticks between minute 10-19 and minute 60. Check: 26 ticks is about 1.07 sigma_60m
  (26 / 24.4), so it is the size of one ordinary hour of ZM noise, and only for big events, and only if the
  direction were known.
- For small events the sign flips after minute 40 (-0.10%; 0.10% x 400 USD = 0.40 USD/t = 4 ticks on the same
  conversion), an overshoot-then-correction pattern. Even direction-known, 4 ticks gross against the 1.59-tick
  Topstep market-order break-even (reports/stage_e28_ranking.md row "| 6 | topstep | ZM |", column mu*_mkt = 1.59)
  leaves about 2.4 ticks, and 4 ticks is 0.16 sigma_60m (4 / 24.4), so it would be invisible in 39 months of events.
- A tradable family-2 label must replace sign(P_T - P_c) by an entry-time quantity (sign of P_{t0} - P_c at
  t0 = 5-15 minutes). No paper read reports that conditional.

Joseph and Garcia (2016), saved R4_joseph_garcia_aaea2016.txt. Returns, eq. (1): "r_{i,t} = ln(P_{i,t}/P_{i,t-1})
x 100, with P_{i,t} being the last price of the nearby soybean futures contract in each 15-second interval i, on
trading day t." Verbatim results: "releases during trading hours result in a smaller volatility spike which extends
for five to six minutes at a higher magnitude"; "the volatility during the first 15-seconds for trading hour release
peaks at lower magnitude (.51) following report release, but persists at a higher level of .15 for the first 2
minutes and .10 for the next 5 to 6 minutes before dropping to a stable .05 level"; "it is significant in the second
period for 30 to 40 minutes after the release and appears to persist intermittently for nearly 60 minutes";
sample: "the second period is June 2012-May 2014 where 29 reports were released during trading" hours; on direction:
"For both periods, the first significant interval correlation is negative which raises the possibility that the
market overreacts to news within the first minute and then corrects quickly in later periods. A clearly persistent,
but not significant pattern of negative cumulative correlation emerges for both periods. [...] Nevertheless, it is
difficult to establish a solid pattern from the results." and caveats "1) the correlations are based on small sample
sizes; 2) only a few intervals reflect significant correlations with the first return; and 3) the magnitude of these
correlations are not large." The units of the ".51" and ".05" volatility figures are average normalized 15-second
return variances as defined in the paper; I do not convert them to ticks because the normalization is not fully
recoverable from the lines read.

Kauffman (2013, NCCC-134 version of the KC Fed Economic Review article), saved R4_kauffman_nccc2013.txt: "trading
during the information releases in 2012 has led to brief periods of excessive volatility immediately after the
reports were released, but the higher volatility did not persist much beyond 60 minutes."; "In 2012, volatility was
excessive for 30 consecutive minutes following WASDE releases. In the 30-to-60-minute window after WASDE releases,
excess volatility was evident 84 percent of the time."; "There was only slight evidence that excess volatility
persisted more than 2.5 hours after WASDE releases." Scope: corn only, and 2012 only, which is when releases were at
7:30 CT (before the January 2013 move to 11:00).

Couleau, Serra and Garcia (2018), saved R4_couleau_serra_garcia_nccc2018.txt: "By turning to announcement days, jumps
occur 100% of the time in period 3 and 83% of those days have a jump cluster within 2 minutes after the announcement
time"; "For announcement days, average positive (negative) jump size has increased from 1.6 (-2.8) cents per bushel
in period 1, to 4.6 (-6) cents per bushel in period 2, and to 4.1 (-3.8) cents per bushel in period 3"; and outside
announcements: "Non-announcement days register efficient price jumps of smaller size [...] 1.1 (-1.2) cents/bu in
period 3". Scope: corn only.

Lehecka, Wang and Garcia (2014) and Adjemian and Irwin (2018): full text not obtained (publisher-restricted; IDEAS
abstract pages saved, R4_ideas_lehecka2014.html, R4_ideas_adjemian_irwin2018.html). Quotes from the abstracts only:
Lehecka et al.: "Strongest price reactions to the releases are found immediately after the market opens, and market
reactions persist for approximately ten minutes. [...] little evidence exists to support systematic under- or
overreactions in prices. Other more subtle reactions occur in the last trading session before USDA announcements as
traders adjust their market exposure in anticipation of the release." (corn, July 2009 - May 2012, i.e. the HALT era:
"after the market opens" means the 9:30 open after a 7:30 release). Adjemian and Irwin: "without a trading halt,
ensuing real-time trading on USDA crop announcements exhibits noticeable volatility spikes in agricultural futures
markets, but that this heightened volatility dissipates within the space of a few trading minutes. [...] continuously
traded crop markets take nearly the same time to fully absorb these shocks, following a very similar time path."
Which markets and the minute counts in the body are [unverified].

##### 2.3 E.31 context (not new evidence)

E.31 measured passive ZM fills 0-5 minutes after a USDA release at an average -8.98 ticks per fill (68 fills;
reports/E.31_RETURN.md, as stated in the R4 brief). That is a markout of a resting order, consistent with the
literature's picture of a fast one-sided repricing in the first minutes (Couleau et al.: jump clusters inside 2
minutes; Huang: 40% of the hour's move in minute 1). It says nothing about the 15-90 minute direction.

##### 2.4 What this means for family 2 (post-USDA path, entry 5-15 minutes after)

- Mechanism worth testing: big-surprise events where price discovery is still incomplete at minute 10 (Huang: ~75%
  done for corn), so continuation toward the 60-minute level is plausible; and small events where the first move is
  wrong-signed or overshoots (Huang small events; Joseph and Garcia negative first-minute correlations; the farmdoc
  2025 anecdote as a pointer). The two give OPPOSITE signs, so the label must be conditioned on jump size (big vs
  small), which Huang splits at the median absolute CPC, an ex-post quantity. An ex-ante proxy is needed: the
  absolute return from P_c to minute 5, scaled by the pre-event sigma.
- Sample size is the binding problem. Distinct "major" 11:00 CT USDA days per year: 12 WASDE days (January also
  carries Grain Stocks) + end-March (Grain Stocks with Prospective Plantings) + end-June (Grain Stocks with Acreage)
  + end-September (Grain Stocks alone) = 15. Over the 39-month discovery window: 15 x 39 / 12 = 48.75, about 49
  (the planner's "about 40" is the same order; government shutdowns, e.g. the cancelled October 2013 WASDE noted by
  Joseph and Garcia, can remove some). NOPA adds 12 per year, 39 in the window, if they never share a day with a
  USDA release [unverified]. A median split of 49 leaves about 24 big events. With a per-event 60-minute noise of
  sigma_60m = 24.4 ticks (random-walk assumption; event days are noisier, so this is optimistic), the standard error
  of a mean over 24 events is 24.4 / sqrt(24) = 24.4 / 4.90 = 4.98 ticks, so only a mean effect of about 10 ticks
  (2 SE) or more would show at the 5% level before any multiple-testing correction. Check: 10 ticks = 0.25% of
  400 USD/t, below Huang's direction-known big-event drift after minute 10 (0.65%, 26 ticks), so the test has power
  only if a tradable signal keeps at least about 40% (10 / 26) of the direction-known drift.
- Drop: anything in minutes 0-2 (fast traders, E.31's -8.98 tick markout).

---

#### 3. Daily price limits and limit-expansion days for ZM, ZS and ZL (topic c)

Sources: CBOT Submission 23-083 (filed 2023-03-31, CFTC-hosted, saved R4_cftc_cbot_2023_daily_limit_amend.txt) [X];
CME Submission of 2020-02-27 on lean hogs, which describes the CBOT 2014 grain mechanism (CFTC-hosted, saved
R4_cftc_cme_sub_2020_leanhog_varlimit.txt) [X]. No cmegroup.com page was used.

##### 3.1 Rule text (ZM, CBOT Rule 13102.D, as shown in the 2023 blackline)

Reset formula (verbatim): "Initial and expanded daily price limits for Soybean Meal futures are reset every six
months. The first reset date would be the first trading day in May based on the following: Daily settlement prices
are collected for the nearest July contract over 45 consecutive trading days before and on the business day prior to
April 16th. The average price is calculated based on the collected settlement prices and then multiplied by seven
percent. The resulting number, rounded to the nearest 5 dollars per ton, or 20 dollars per ton, whichever is higher,
will be the new initial price limits for Soybean Meal futures. The new expanded price limit shall be the new initial
price limit multiplied by 1.5 and rounded up to the nearest 5 dollars per ton." The November reset uses "the nearest
December contract over 45 consecutive trading days before and on the business day prior to October 16th".

Soybean-complex linkage (verbatim; the blackline's insertions and deletions are not distinguishable in the text
extraction, so the exact final wording is uncertain): "Should any futures component of the Soybean Complex (Soybean,
Soybean Meal, and Soybean Oil) settle at the initial price limit, the daily price limits for the other futures
components shall increase to the expanded price limit [...] Price limits will remain at the expanded price limit
until all futures component contract months settle at a price change less than the initial price limit at which
point daily price limits for all futures components of the Soybean Complex shall revert back to their respective
initial price limits the following business day."

Spot month: "There are no price limits on spot-month contracts. Contract expirations become the spot-month on the
second Business Day preceding the first day of the delivery month, which is also first position day." (footnote 1).

Changes effective trade date May 16, 2023 (verbatim, Submission 23-083): (1) trigger: "expanded price limits are
triggered when one contract within the first five (5) through eight (8), depending on the Contract, non-spot
contract months settles at the initial price limit rather than two (2) contract months"; (2) staying expanded: "at
least one (1) contract month must settle at a price change equal to or greater than the initial price limit for
expanded price limits to remain in effect on the next Business Day"; (3) ratchet: "After two (2) consecutive Business
Days of at least one (1) contract month settling at the expanded price limit, the initial price limit is updated to
become the expanded price limit and the expanded price limit will be increased by 50 percent."

History (verbatim, 2020 CME submission): "To avoid frequency in limit settlements, CBOT implemented a variable price
limit mechanism in its grain and oilseeds markets in 2014. Since its implementation in the CBOT grain and oilseed
markets, there has been a significant reduction of the number of days those markets have settled at the limit
price." (its Exhibit 1 with the counts is an image; no count was extracted).

##### 3.2 Worked example (ZM)

Assume the 45-day average July settlement before April 16 is 400.0 USD/short ton (illustrative, not a data read).
- 7% x 400.0 = 28.0 USD/ton. Rounded to the nearest 5 USD = 30 USD (28 is nearer 30 than 25). Max(30, 20) = 30 USD.
  Initial limit = 30 USD/ton = 30 / 0.10 = 300 ticks = 300 x 10.00 = 3,000 USD per contract.
- Expanded = 30 x 1.5 = 45 USD, already a multiple of 5, so 45 USD/ton = 450 ticks.
- Ratchet after two consecutive expanded-limit settlements: initial becomes 45, expanded 45 x 1.5 = 67.5, rounded up
  to 70 USD/ton = 700 ticks.
- Check against the brief's median daily range for ZM, 96 ticks: the initial limit is 300 / 96 = 3.1 median daily
  ranges away from the prior settlement, so limit-bound days are rare tail events. Under the random-walk assumption
  the 1-day sigma over the day session (290 minutes from 08:30 to 13:20) is 3.15 x sqrt(290) = 3.15 x 17.03 = 53.6
  ticks, and 300 ticks is 5.6 of those sigmas (overnight adds variance, so the true distance in sigmas is smaller,
  and limit moves cluster on USDA days and on large weather shifts).

##### 3.3 What this means for a ZM directional search

- Limits bite on large USDA days (June 30 Acreage/Grain Stocks is the classic case) and on ZS- or ZL-driven days,
  because a limit settlement in any one of the three legs expands the other two. A directional label that crosses a
  limit-locked interval has no tradable exit price: E.33 must flag minutes where the best bid or ask sits at the
  limit and drop or censor labels that cross them (the Databento definitions schema carries daily limit prices per
  instrument [field names are DataFacts' topic; not verified here]).
- Limit-day counts for ZM in 2020-12..2024-02 are not published in any source read; they are a DataFacts count
  (settlements against definition limits), not a literature fact.
- Huang (2022, footnote 19) on why limit days distort microstructure measures: "When the price hits one side of the
  limit, one side of the book is restricted from trading and the other side accumulates a large number of contracts.
  This results in misleading BAS and depth measures."

---

#### 4. Overnight gaps, weather and the Sunday-night open (topic d)

##### 4.1 Structure of the gaps (from the session grid in section 1.1)

| Gap | Clock time (CT) | Length | Scheduled information inside it | Where it is priced |
|---|---|---|---|---|
| Daily close to overnight open | 13:20 -> 19:00 (Mon-Thu) | 5 h 40 min | Crop Progress, Mondays 15:00 if ET (April-November); afternoon weather-model updates [timing of model runs unverified] | 19:00 overnight open |
| Weekend | Fri 13:20 -> Sun 19:00 | 53 h 40 min (13:20 Fri to 13:20 Sun is 48 h, plus 5 h 40 min) | weekend weather; any weekend policy news | Sunday 19:00 open |
| Morning pause | 07:45 -> 08:30 | 45 min | daily flash export sales (09:00, zone assumed ET = 08:00 CT [unverified]) | 08:30 day open |
| Inside the overnight session | 19:00 -> 07:45 | 12 h 45 min | weekly Export Sales Thursday 07:30 (8:30 a.m. ET, FAS fact sheet) | continuously, on thin overnight volume |

The "overnight gap at 08:30" of the planner's family 4 therefore covers only a 45-minute pause; the large
information gaps are at 19:00 (daily) and at the Sunday 19:00 open (weekly). For ZM, E.28's table gives a day-session
volume share of 0.83, so about 17% (1 - 0.83) of volume trades in the 12 h 45 min overnight session. A family-4
label at 08:30 should define its "gap" as P(08:30 first trade or mid) minus P(13:15 settlement of the prior day),
which bundles the 19:00 open jump and the whole overnight drift; the two components need separate features.

##### 4.2 Evidence found

- [A] Jin, Kearney, Li and Yang (MPRA 97134, 2019; Dalian Commodity Exchange soybean meal, June 2, 2008 - June 28,
  2013, 1,093 trading days, day session 9:00-11:30 and 13:30-15:00 in that sample, so no night session; saved
  R4_mpra_97134.txt), Table 3: the overnight return r0 (previous close to today's open) predicts the last half-hour
  return of Dalian soybean meal: beta_r0 = 28.895 (t = 2.96) alone, 29.518 (t = 3.05) jointly with r1, R2 0.97% and
  1.91%. For Dalian soybeans the overnight return does not predict (beta = -7.780, t = -0.82). Caption verbatim:
  "r0 is the return from the previous day's close until today's open (overnight return), and r1 represents the return
  during the first half-hour trading session (excluding the overnight return)."
- [A] Baltussen, Da, Lammers and Martens (JFE 2021; CBOT soybean meal "SM", 1982-07-06 to 2020-05-01, 9,458 days,
  hours 08:30-13:20 at the end of the sample; saved R4_baltussen_jfe2021_firecrawl.md), Table B3: the return from the
  previous close to 30 minutes after today's open, r_ONFH, does NOT predict the last half-hour for CBOT soybean meal:
  beta_ONFH = -0.95 (t = -1.58), R2 0.03%, out-of-sample R2 -0.04%. Section 5.3 discusses this paper fully.
- [P] Trade commentary only, no measurement: DTN 2017-06-19 ("selling interest tied to weekend weather had subsided by
  early Monday" per the search summary), Barchart ("weather derivatives at heart"), Pro Farmer "Ahead of the Open"
  notes. These are pointers: they say weekend and overnight weather shifts move the Sunday open and the overnight
  session, and that some of those moves reverse by the morning, but give no sample, no magnitude and no test.
- Discovery leads not read (titles only, Crossref, [unverified]): Stevens (1991, Journal of Futures Markets 11(1),
  doi 10.1002/fut.3990110108), "Evidence for a weather persistence effect on the corn, wheat, and soybean growing
  season price dynamics" (daily data); Singal and Tayal (2019, Journal of Futures Markets, doi 10.1002/fut.22069),
  weekend effect in futures (daily data).

Stopping rule for topic d: four discovery queries (two WebSearch on overnight and weekend weather effects, one on
crop-condition reactions, three Crossref title queries) surfaced no intraday study of CBOT soybean-complex overnight
gaps, Sunday opens or Crop Progress reactions after 2013. The literature gap is real as far as these queries reach;
it is not proof that no such study exists (Google Scholar was not queried directly; AgEconSearch full-text search
was not run).

##### 4.3 What this means for family 4 (gap continuation or reversal)

- Worth testing as a FEATURE inside families 1 and 3 rather than as its own family: the only direct soybean-meal
  evidence is Dalian (a different market with no night session in that sample) and points to overnight-return
  CONTINUATION into the last half-hour (t about 3), while the CBOT soybean meal evidence over 38 years (Baltussen) is
  a NEGATIVE, insignificant slope for the overnight-plus-first-half-hour return. The two disagree in sign.
- Strata that must be separate: Sunday-open days (weekend weather, 53 h 40 min gap) vs Monday-Thursday 19:00 opens;
  growing season (roughly May-August, when weather drives the overnight) vs the rest; Crop Progress Mondays
  (April-November) vs other days; Thursday (Export Sales at 07:30 inside the overnight session).
- Magnitude check under the random-walk assumption: a 45-minute pause carries no ZM trading, so the 08:30 "gap" is
  mostly the overnight session's 12 h 45 min = 765 minutes of drift: 3.15 x sqrt(765) = 3.15 x 27.66 = 87.1 ticks if
  the overnight had the same per-minute sigma as the day (it is quieter, so the true figure is lower). A
  continuation or reversal edge of 2-3 ticks is 2-3% of that noise, which needs hundreds of independent days; 39
  months give about 39 x 21 = 819 trading days, about 160 of them Sunday opens.

---

#### 5. Settlement mechanics, pre-close behaviour and intraday momentum (topic e)

##### 5.1 Settlement window and TAS

- [X] 2008 (CBOT Market Regulation Advisory RA0815-1, CFTC-hosted, saved R4_cftc_cbot_2008-09-08.txt): the Globex
  Control Center "will settle the futures contracts based upon Globex activity occurring from 1:14:00 to 1:15:00 p.m.
  rather than on trading activity occurring in the pit" (then for rough rice, as part of a pilot "presently operating
  in Wheat futures").
- [R] Onur and Reiffen (CFTC, 2018, saved R4_onur_reiffen_cftc.txt): "The settlement price procedure for several grain
  contracts changed on June 25, 2012. Prior to that date, the settlement price was based on trades made during the
  final minute of trading on the CBT trading floor; equal to the weighted average price of trades made on the floor
  during that minute. After that date, the settlement price was based on the weighted average of all trades made in
  that minute, whether on the floor, or through electronic trading." Footnote 11: "Prior to June 25, 2012, the
  settlement period minute was from 1:14 p.m. - 1:15 p.m. and after the change it became 1:59 p.m. - 2:00 p.m."
- [X] Since April 8, 2013 settlement moved back with the close to 1:15 p.m. (CBOT 2013-03-13 filing: "the Exchange
  plans to determine settlement prices consistent with the new market close time of 1:15 p.m."), and since July 6,
  2015 Globex trades until 13:20 while the "1:14-1:15 p.m. CT settlement window" stays (Submission 15-204).
- The exact current ZM settlement algorithm (VWAP over 13:14:00-13:15:00 on Globex, and the tie-break rules when
  volume is thin) is [unverified]: the only full statements read are from 2008 and 2012, and CME's own settlement
  pages are out of bounds for this stage.
- [X] TAS (Submission 15-148, CFTC-hosted, saved R4_cftc_cbot_2015_tas_rule524.txt): Rule 524 "effective on Sunday,
  June 7, 2015 for trade date Monday, June 8, 2015"; "CBOT will begin to permit orders for the first three listed
  contract months and certain spreads in Corn, Soybean, Soybean Oil, Soybean Meal, Wheat and KC HRW Wheat futures to
  be entered into CME Globex for pricing at the settlement price or any valid price increment four ticks higher or
  lower than the settlement price." For ZM, four ticks = 4 x 0.10 = 0.40 USD/ton = 40 USD per contract. The 2015
  hours filing gives the purpose of the 13:15-13:20 extension: "allow TAS liquidity providers to hedge or trade as
  needed after 1:15 p.m./CT".

##### 5.2 Pre-close to settlement reversals (Onur and Reiffen)

Test (verbatim): "we define a binomial variable which is equal to one if (P_{c,t} - P_5) and (P_{o,t+1} - P_{c,t})
have opposite signs and zero if they have the same sign", where "P_{c,t} is the closing price on day t, P_{5,t} is the
volume weighted average price in the 5 minutes before the settlement period on day t, and P_{o,t+1} is the opening
price on day t+1." Result: "We find that the percentage of reversals falls from 57.3% under the old regime to 48.7%
under the new, a decline which is statistically significant at the 1% level." Scope: CBOT corn lead month,
proprietary CFTC trade data, pre- and post-June-2012.

Reading for ZM: the measured reversal is from the last 5 minutes before settlement to the NEXT DAY's open, not an
intraday move. Under the electronic settlement regime the reversal share (48.7%) is at or below a coin flip, i.e.
no evidence of a pre-close move that reverts overnight. Worked number: 48.7% vs 50% on N days has standard error
sqrt(0.25 / N); the share of N needed for 1.3 points to be 2 SE is N = 0.25 x (2 / 0.013)^2 = 0.25 x 23,669 = 5,917
days, far more than any sample, so 48.7% is best read as "no reversal", not as "momentum". The number of days in the
Onur and Reiffen post-period is not in the lines read.

##### 5.3 Intraday momentum: first half-hour (or rest of day) predicting the last half-hour

| Study | Market | Sample | Result for the first-half-hour predictor | Other predictors |
|---|---|---|---|---|
| Gao, Han, Li and Zhou (Dec 2015 draft read; cited as "Gao et al. (2018)" by Jin et al.; published version not read) [A] | S&P 500 ETF (SPY), 10 other ETFs, FTSE and Euro Stoxx futures; crude oil and gold futures; currencies | 1993-2013 (SPY) | SPY: R2 1.6% in sample, OOS R2 1.2%; "the intraday momentum does not show up in major currency pairs or commodity futures" | twelfth half-hour adds; R2 2.6% combined, OOS 1.8% |
| Jin, Kearney, Li and Yang (MPRA 2019) [A] | Shanghai copper and rebar, Dalian soybean and soybean meal | soybean meal 2008-06-02 to 2013-06-28 | soybean meal: beta 51.997 (x10^-3 scale), t = 2.60, R2 0.90%; sign version t = 2.89 | second-to-last half-hour t = 2.48; overnight return t = 2.96 |
| Baltussen, Da, Lammers and Martens (JFE 2021) [A] | 60+ futures incl. CBOT soybean meal (SM), soybeans (SY), soybean oil (BO), corn (CN) | SM 1982-07-06 to 2020-05-01 | SM: beta_ONFH = -0.95 (t = -1.58), OOS R2 -0.04%; SY -1.17 (t = -2.17); BO -0.80 (t = -1.40); CN -0.13 (t = -0.26) | SM: r_M (end of first half-hour to the last hour) beta 2.49 (t = 3.22) in a joint regression with OOS R2 -0.27%; r_ROD beta 0.18 (t = 0.42) |

Verbatim, Gao et al. (saved R4_gao_han_li_zhou_mql5.txt): "For out-of-sample (OOS) predictability, the R2 is 1.2%
using the first half-hour return as the only predictor, and 1.8% when this predictor is combined with the twelfth
half-hour return predictor." and "However, the intraday momentum does not show up in major currency pairs or
commodity futures. This is perhaps expected because, unlike the stock market, the daily open and close for currency
and commodity futures are unclear because they are traded globally around the clock." The commodity futures tested
are "crude oil and gold" (Appendix table note); grains were not tested.

Verbatim, Jin et al.: "We observe that the first 30-minute returns positively predict the last 30-minute returns for
all four contracts with a slope of 0.073 for soybean, 0.052 for soybean meal, 0.067 for copper, and 0.103 for steel.
All of these are significant at a 5% level. Furthermore, the R2 for these four contracts are 1.80%, 0.90% 1.36% and
3.32%, respectively." (Table 2 prints the soybean meal slope as 51.997 on a x10^-3 scale with t = 2.60; the text's
0.052 is the same number.) No t-statistic of 3.07 appears in the Jin et al. tables read; the nearest soybean-meal
values are 3.05 (overnight return, joint regression) and 2.96 (overnight alone).

Verbatim, Baltussen et al. (abstract): "Using intraday returns on over 60 futures on equities, bonds, commodities, and
currencies between 1974 and 2020, we find strong market intraday momentum everywhere. The return during the last 30
minutes before the market close is positively predicted by the return during the rest of the day (from previous
market close to the last 30 minutes). [...] and reverts over the next days." And on commodities: "The results are
slightly weaker for commodity futures (Table B3) and currency futures (Table B4). Still, for about 40% to 50% of the
contracts, r_ROD has a positive and significant R2_OOS." Pooled softs (their label for grains and softs): beta_ONFH
0.25 (t = 0.70), beta_ROD 0.65 (t = 2.16), OOS R2 -0.01%. Equations: eq. (1) "r_{ONFH,t} = P_{o+30,t} / P_{c,t-1} -
1" and eq. (2) "r_{ROD,t} = P_{c-30,t} / P_{c,t-1} - 1", P_c the close, P_o the open, t the day. The Table B3 row for
SM was read from a Firecrawl PDF-to-markdown conversion; the column alignment should be rechecked against the PDF
before any number is used in a decision (the table header has 11 numeric columns and the SM row has 11 values, so
the alignment is plausible).

Caveat for the lead (not a decision): Baltussen et al.'s SM sample ends 2020-05-01 and so includes most of the sealed
test window (2017-05-01..2020-11-30). Using its SM row to choose or drop a family lets published results from the
test period inform selection. The effect is small (3 of 38 years) but it is the lead's call.

Worked example on ZM scale (assumptions stated): suppose a first-half-hour slope of the Jin et al. size, beta =
0.052, applied to ZM. With sigma_30m = 3.15 x sqrt(30) = 3.15 x 5.477 = 17.3 ticks for the first half-hour, a
one-sigma first half-hour (17.3 ticks) predicts 0.052 x 17.3 = 0.90 ticks for the last half-hour. Check: R2 =
beta^2 x var(r1) / var(r13); with equal variances R2 = 0.052^2 = 0.27%, below the 0.90% reported, which says Dalian's
last half-hour is quieter than its first (var ratio 0.0027 / 0.0090 = 0.30). Either way, 0.9 ticks expected per
one-sigma day is below the 1.59-tick market-order break-even (Topstep row of reports/stage_e28_ranking.md), so even
the Dalian effect size does not pay at 1 lot on ZM unless conditioned on large first half-hours (a 3-sigma day
predicts 2.7 ticks).

##### 5.4 What this means for family 3 (late-session momentum or reversal into the 13:15 settlement)

- The only direct CBOT soybean-meal test (Baltussen, 1982-2020) finds no first-half-hour momentum (slope negative,
  insignificant, OOS R2 negative), and the rest-of-day predictor is insignificant for SM. Gao et al. found no
  momentum in the two commodity futures they tested. The positive Dalian result is a different market, an older
  sample, and a day-only session. Prior for family 3 on ZM: weak. If kept, the predictor should be r_M (mid-day
  return), the one SM coefficient that is significant in-sample (t = 3.22), with the warning that its OOS R2 is
  negative.
- Settlement mechanics give a concrete hypothesis that is not the momentum one: TAS liquidity providers and index or
  hedge flows trade in the 13:14-13:15 window, and Globex trades on to 13:20. A 13:00-13:14 label would sit just
  before that flow; a 13:15-13:20 label would sit just after it. Onur and Reiffen's corn evidence says the electronic
  settlement removed the pre-close-to-next-open reversal, so a reversal into the next day is not expected.
- Exclusions: limit-locked closes (section 3), first notice and roll days, and report days whose 11:00 move is still
  settling (Huang: 35-45 minutes, so to about 11:45 in corn).

---

#### 6. Planner pointers owned by R4: verification table

| # | Planner claim | Status | What the full text says (source, saved file) |
|---|---|---|---|
| 1 | Lehecka, Wang and Garcia (2014): price and volatility effect gone within minutes | PARTLY VERIFIED (abstract only) | IDEAS abstract: "market reactions persist for approximately ten minutes"; corn only; July 2009 - May 2012, i.e. releases in the trading HALT, reaction measured "immediately after the market opens" (R4_ideas_lehecka2014.html). Full text not obtained (publisher-restricted). Not a real-time-release study. |
| 2 | Adjemian and Irwin (AJAE 2018): effect gone within minutes | PARTLY VERIFIED (abstract only) | IDEAS abstract: "heightened volatility dissipates within the space of a few trading minutes"; 2009-2014 grain futures (R4_ideas_adjemian_irwin2018.html). The abstract speaks of volatility, not of the price level or direction. Full text not obtained. |
| 3 | Kauffman (2013): volatility elevated up to about 60 minutes | VERIFIED, with scope limits | "the higher volatility did not persist much beyond 60 minutes"; "excessive for 30 consecutive minutes"; 84% of the time in 30-60 min (R4_kauffman_nccc2013.txt). Corn only, 2012 only (7:30 CT releases). Consistent later evidence at 11:00 CT for corn AND soybeans: Bian, Serra and Garcia (2014-2017): volatility "would not settle down within the first hour"; Joseph and Garcia (soybeans): above control for 30-40 minutes, intermittently to about 60. Note the tension with rows 1-2 ("minutes"): the price level settles within minutes to tens of minutes, volatility within about an hour. |
| 4 | "11:00 CT releases have been made into live trading since 2012" | PARTLY VERIFIED | Live-trading releases since May 2012 at 7:30 CT; 11:00 CT since January 2013 (Huang 2022; Couleau et al. 2018; Joseph and Garcia 2016). |
| 5 | "The DIRECTION of the 15-90 minute path after the jump is untested" | PARTLY VERIFIED | No tradable-direction test found. Closest: Joseph and Garcia (soybeans, 29 trading-hour releases) test first-return vs later-return correlations over 15 minutes and find "difficult to establish a solid pattern" with mostly negative signs; Huang (corn) reports direction-conditional drift (ITR) to 60 minutes, positive for big events, negative after 40 min for small events. So the path is partly characterised, but not with an ex-ante direction signal and not beyond 60 minutes, and not for ZM or ZL. |
| 6 | farmdoc daily 2025-09-12 WASDE anecdote (pointer only) | VERIFIED as a pointer | Janzen, farmdoc daily 15:168, 2025-09-15: soybeans fell "as much as [...] 13 cents per bushel" in 11:00-11:15 and November soybeans closed "up 13 cents"; of 6 2025 report days, the author finds two other mismatches (June WASDE tiny moves; June Acreage soybeans) (R4_farmdocdaily_2025-09_wasde.html). Extension blog, 2025, outside all owned windows: pointer only. |
| 7 | Closing range 13:14-13:15 CT | VERIFIED (as the settlement window, CFTC-hosted filing) | "not impact or influence the 1:14-1:15 p.m. CT settlement window" (Submission 15-204, R4_cftc_cbot_2015_hours_1320.txt). The exact current algorithm within the window is [unverified]. |
| 8 | TAS since 2015-06-15 | PARTLY VERIFIED (date differs) | Rule 524 "effective on Sunday, June 7, 2015 for trade date Monday, June 8, 2015", covering "Corn, Soybean, Soybean Oil, Soybean Meal, Wheat and KC HRW Wheat" (Submission 15-148, R4_cftc_cbot_2015_tas_rule524.txt). No source read gives June 15; a later launch date for grains is possible but not seen. |
| 9 | Onur and Reiffen (CFTC 2018): pre-close to settlement reversals declined after 2012 electronic settlement | VERIFIED, with a correction of what is measured | Reversal = sign of (settlement - 5-minute pre-settlement VWAP) opposite to sign of (next-day open - settlement); "falls from 57.3% under the old regime to 48.7% under the new" (R4_onur_reiffen_cftc.txt). Corn only. It is a pre-close to NEXT-OPEN reversal, not a reversal into the settlement. |
| 10 | Gao, Han, Li and Zhou: US ETFs, R2 about 1.2-1.7% out of sample | PARTLY VERIFIED | SPY: in-sample R2 1.6%, OOS R2 1.2% (first half-hour alone), OOS 1.8% with the twelfth half-hour (R4_gao_han_li_zhou_mql5.txt, Dec 2015 draft). "1.7%" does not appear for SPY OOS; the range should read 1.2-1.8% OOS. Same paper: no intraday momentum in commodity futures (crude oil, gold). |
| 11 | Chinese commodities incl. Dalian soybean meal, t about 3.07 | PARTLY VERIFIED (paper found; 3.07 not found) | Paper: Jin, Kearney, Li and Yang, "Intraday Time-series Momentum: Evidence from China" (MPRA 97134, 2019; Hull repository lists a Journal of Futures Markets accepted manuscript, not read: Cloudflare and content-signal block). Dalian soybean meal, 2008-2013: first half-hour t = 2.60 (R2 0.90%), sign version t = 2.89, second-to-last half-hour t = 2.48, overnight return t = 2.96 alone and 3.05 joint. No 3.07 in the tables read; the published JFM version may differ. |
| 12 | Couleau, Serra and Garcia (NCCC-134 2018) | VERIFIED (what it is) | "Are corn futures prices getting 'Jumpy'?": corn nearby 2008-2015; real-time releases raised announcement-day jump frequency (100% of days, 83% with a cluster inside 2 minutes) and size (+4.1/-3.8 c/bu), while non-announcement jumps shrank (R4_couleau_serra_garcia_nccc2018.txt). |
| 13 | Li, Wang and Diersen (NCCC-134 2024): find what it is | FOUND | "Do Agricultural Commodity Price Spikes Always Stem from News?" (South Dakota State). Corn futures, 5-minute prices, 2013-2022, day session 8:30-13:20 only; 3,094 jump clusters on 2,403 days, "994 news-related clusters of jumps on 494 days, which occupy 32.13% of all clusters"; Hawkes fit: "exogenous events exhibit a faster decay in their relaxation exponent [...] in contrast to the more prolonged impact of endogenous events" (R4_li_wang_diersen_nccc2024.txt). Corn only; news matched by date, not time. Relevant to family 5 (non-news jumps), not to USDA paths. |
| 14 | Ranked family 2 (post-USDA path, 15-90 min) | SUPPORTED AS A GAP, WEAK PRIOR | Sections 2.4 and 7: about 49 major USDA days in 39 months; direction-known drift exists in corn after minute 10 for big events; no ex-ante test published; power only for mean effects of about 10 ticks or more. |
| 15 | Ranked family 3 (late-session momentum or reversal into settlement) | EVIDENCE AGAINST on CBOT soybean meal | Baltussen et al. (JFE 2021) Table B3, SM 1982-2020: first-half-hour slope -0.95 (t = -1.58), OOS R2 negative; rest-of-day slope insignificant; Gao et al.: no commodity momentum. The planner's "unpublished for ZM" is REFUTED: it was published (as a null) inside Baltussen et al.'s 60-futures panel. |
| 16 | Ranked family 4 (overnight-gap continuation or reversal at 08:30) | UNTESTED for CBOT; mixed indirect evidence | Dalian soybean meal overnight return predicts the last half-hour (t = 2.96); CBOT SM overnight-plus-first-half-hour does not (Baltussen). No study of the 08:30 or Sunday 19:00 opens found. |

---

#### 7. Per-event-type table (the R4 deliverable)

Counts per year are calendar counts from the USDA, FAS and NOPA pages (section 1.2). "Window" counts are for the
39-month discovery window (x 39 / 12 = x 3.25). Tick conversions use the illustrative 400 USD/ton and are
assumptions, not data reads.

| Event | Schedule and time (CT) | Session it lands in | Per year (window) | Published jump evidence (horizon, size) | Published drift or reversal evidence | Implication for a ZM directional label |
|---|---|---|---|---|---|---|
| WASDE (+ Crop Production Aug-Nov, Jan) | monthly, pre-announced, 11:00 | day session (2 h 30 min after open, 2 h 14 min before settlement) | 12 (39) | corn: 40% of the 60-min move in minute 1, ~75% by minute 10, 90-100% by 35-45 min; complete move 1.63% average, 2.6% big, 0.6% small (Huang 2022). On ZM scale, 1.63% x 400 = 6.52 USD = 65 ticks [assumption that corn's % move transfers]. Soybeans: 15-s variance spike elevated 5-6 min, above control 30-40 min, to ~60 min (Joseph and Garcia 2016). Corn jumps: 100% of real-time report days, 83% clustered within 2 min (Couleau et al.) | direction-known drift after min 10: big +0.65% (~26 ticks), small -0.01% then -0.10% at 40-49 min (Huang, corn); soybeans: first-minute overreaction hint, no solid pattern (Joseph and Garcia); farmdoc 2025-09 full reversal [pointer] | Exclude minutes 0-5 (fast traders; E.31 passive fills -8.98 ticks). Candidate label: 15, 30, 60 min returns from an entry at 11:10-11:15, conditioned on the jump size P(11:05) - P(pre) scaled by pre-event sigma; expect continuation on big jumps and reversal on small ones; power only for |mean| >= ~10 ticks. |
| Grain Stocks | quarterly (Jan, end-Mar, end-Jun, end-Sep), 11:00 | day session | 4 (13), 3 of 4 stacked with WASDE, PP or Acreage | pooled into the "big" USDA events in Joseph and Garcia's soybean sample; WASDE-only days showed a lower first-interval spike (1.24 vs pooled 1.43 in the halt period; .47 vs .51 in the trading-hour period) | none separately | Treat as stacked days; only end-September is a clean Grain Stocks event (about 3 in the window). No separate family. |
| Prospective Plantings | annual, end of March, 11:00 (with Grain Stocks) | day session | 1 (3) | in pooled samples only | none | Too few for its own label; include as a "major USDA day" in family 2 and as a stratum. |
| Acreage | annual, end of June, 11:00 (with Grain Stocks) | day session | 1 (3) | in pooled samples; June Acreage 2025 soybeans: fell "more than a dime" immediately, up slightly on the day [pointer] | pointer only | As above; limit-move risk highest on this day (section 3). |
| NOPA crush | monthly (date set by NOPA), 12:00 noon ET = 11:00 | day session | 12 (39) | NONE found: no intraday study of NOPA releases in any source read | none | Directly relevant to ZM (meal production, exports, crush pace) and the one ZM-specific scheduled event. Unstudied: a genuine gap. Separate stratum in family 2, with the warning that release dates and the 11:00 time before 2026 are [unverified] and must be fixed from a dated source before E.33. |
| Crop Progress | weekly Monday (Apr-Nov), 16:00 ET = 15:00 if ET [zone unverified] | CLOSED (13:20-19:00); priced at the 19:00 Monday open | about 30-35 (about 100) | none found (discovery null, section 4.2) | none found | Feature for family 4 (Monday-evening open gap) and a growing-season stratum; no label of its own. |
| Export Sales (weekly) | Thursday 8:30 ET = 07:30 | OVERNIGHT session, 15 min before the 07:45 pause | about 52 (about 169) | none found | none found | Thin overnight book (ZM day-session volume share 0.83); the move is carried into the 08:30 open. Thursday flag for family 4. |
| Daily (flash) export sales | ad hoc, 9:00 a.m. (zone not stated; 08:00 CT if ET) | PAUSE 07:45-08:30 [if ET] | irregular | none found | none found | Flag only. |
| Weekend weather / Sunday open | Sunday 19:00 open after a 53 h 40 min gap | overnight open | about 52 (about 169) | none found (practitioner commentary only) | Dalian SM overnight-return continuation into the last half-hour (t 2.96, different market, no night session); CBOT SM overnight+first half-hour: no prediction (Baltussen) | Family 4 stratum. Growing season separately. Weak prior. |
| Daily settlement | 13:14-13:15 window; Globex to 13:20; TAS at settlement +- 4 ticks | day session close | about 250 (about 819) | n/a | corn: pre-settlement-to-next-open reversals 48.7% after 2012 (no reversal) (Onur and Reiffen); CBOT SM first-half-hour -> last half-hour slope -0.95 (t -1.58), OOS R2 < 0 (Baltussen) | Family 3 prior is weak and partly REFUTED for SM. If kept: predictor r_M (mid-day, SM t 3.22 in-sample, OOS negative); separate 13:00-13:14 and 13:15-13:20 labels around the TAS-driven settlement minute. |
| Limit days | limits reset May 1 and Nov 1 (7% of 45-day average, nearest 5 USD, min 20 USD; expanded x 1.5); soybean-complex linked | any | rare (no count read; DataFacts item) | n/a | n/a | Censor labels that cross a limit-locked interval; flag expanded-limit days, which follow limit settlements in ZS or ZL too. |

---

#### 8. Summary of what this means for a ZM directional search

Mechanisms worth testing:
1. Post-USDA path (family 2), entry 10-15 minutes after 11:00, with the sign of the early move and its size as
   conditioners. Big events: continuation is plausible (Huang, corn, direction-known drift +0.65% after minute 10).
   Small events: overshoot then correction (Huang; Joseph and Garcia). About 49 major USDA days plus 39 NOPA days in
   the window. Power suffices only for mean effects around 10 ticks or more.
2. NOPA crush days as a ZM-specific event stratum: no published intraday study exists in the sources read.

Mechanisms to drop or demote:
1. Minutes 0-5 after any release (fast traders; E.31).
2. Late-session momentum from the first half-hour (family 3) as a standalone family: the CBOT soybean-meal null in
   Baltussen et al. (1982-2020) and the commodity null in Gao et al. If kept, use r_M and treat it as low prior.
3. Pre-close-to-next-open reversal: corn evidence says it disappeared after 2012.

Open items that need dated, non-CME sources before E.33 freezes anything: the NOPA release calendar and time for
2020-2024; the Crop Progress time zone; the current settlement algorithm inside 13:14-13:15; the TAS start date for
grains (June 8 vs June 15, 2015); ZM limit levels and limit-day counts in 2020-12..2024-02 (DataFacts can count these
from definitions and settlements).

---

#### 9. Discovery and fetch log summary

- Pages saved and logged: see pages/R4_events/log.tsv (49+ entries). Failures: Cao and Robe (JFM 2022, Wiley
  pdfdirect: Cloudflare page, not read), Kansas City Fed Economic Review 2013 (two URLs, no file; the NCCC-134
  version was used), USDA node 13204 (Access Denied), FAS export-sales HTML pages (empty responses; the FAS fact sheet
  PDF was used), Hull repository Jin et al. AAM (Cloudflare; robots.txt carries content signals; not retried),
  Baltussen et al. EUR PDF by curl and by Scrapling get and fetch (Cloudflare 403; stealthy-fetch NOT used because it
  would defeat a bot check), then read through Firecrawl (route 4), logged. ScienceDirect HTML for Baltussen et al.
  carried no article text.
- WebSearch calls in the resumed run: 7 (this worker's budget is 80; the first spawn's count is not in the log).
  Crossref API: 3 title queries. No budget notice was seen. One WebSearch for an author or AgEconSearch copy of
  Adjemian and Irwin (2018) found none (it surfaced Shubitidze et al. 2026 instead).
- Stopping rule, topic b: seven full-text sources read (Huang, Joseph and Garcia, Kauffman, Couleau et al., Bian et
  al., Hu and Mallory NCCC version, Li et al.); the last searches added Bian et al. and Hu and Mallory, so the topic
  was not saturated at the stop; a further sweep (Google Scholar citations of Adjemian and Irwin 2018) is the next
  step if the lead wants more.
- Not done: full texts of Lehecka et al. (2014) and Adjemian and Irwin (2018) (publisher-restricted; no author copy
  found in the queries run); the published JFM version of Jin et al.; any Google Scholar sweep for soybean meal or
  soybean oil USDA intraday studies beyond the queries above.

## R5. Out-of-sample ML evidence at 1-240 minutes, competitions, decay

Source file: reports/stage_e32_briefs/R5_ml_evidence.md (sha256 65aa9d108eaeb49bd30825940769e62ac942c184c375e03f32236513a65c8ee2).

### R5_ml_evidence: how much out-of-sample directional predictability at 1-240 minutes, and did it survive costs

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

#### B. From an out-of-sample correlation to ticks per trade (topic b; placed first because every row of table A is read through it)

Script and full output: work/R5_ml_evidence/R5_rho_arith.py and R5_rho_arith.out (no data read; inputs are the
stage's standard numbers). M1 section 1 already tabulates the OOS R2 a forecast needs at 1-30 minutes for
"trade every bar" and "top decile"; this section derives the same machinery in terms of the correlation rho,
adds the hit-rate and OOS-R2 conversions that published papers need, and answers the brief's 15-minute question.

##### B.1 Assumptions (stated, not measured)

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

##### B.2 Sign-of-forecast strategy: E[r sign(f)] = rho sigma_h sqrt(2/pi)

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

##### B.3 Thresholded strategy: trade only when |f| is large

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

##### B.4 What published R2 values imply in ZM ticks (illustration only; the papers are not ZM)

Using rho >= sqrt(R2_oos) (B3) and B1 at the paper's own horizon, ZM volatility:

| Published OOS number (source, see table A) | horizon | rho implied (lower bound) | ZM gross per trade, sign every bar | note |
|---|---|---|---|---|
| Gao et al. SPY OOS R2 1.2% (R4) | 30 min, once a day | 0.110 | 0.110 x 17.253 x 0.798 = 1.51 | one trade a day, no threshold possible beyond skipping days |
| CRS 1996, 5-min R2 3.32% (M1) | 5 min | 0.182 | 1.02 | top-4-of-58 bars: 2.84 |
| CRS 2002, 5-min R2 0.54% (M1) | 5 min | 0.073 | 0.41 | top-4-of-58 bars: 1.15 (below 1.59) |

The 1996-to-2002 drop is the decay story of section D; the 2002 level, mapped to ZM, does not clear the hurdle
even with aggressive thresholding (M1 section 2.3 iii reaches the same conclusion by the R2 route).

#### C. Public forecasting competitions on market data (topic c)

Access decision (log.tsv, 2026-10-27 00:49 PDT): kaggle.com answered robots.txt with a Google reCAPTCHA page and
its terms page is JavaScript-rendered and unreadable, so Kaggle was treated as NOT open to automated fetch and no
Kaggle page (overview, evaluation, leaderboard, discussion) was read. Consequence: the public-to-private
shake-up of each Kaggle market competition could NOT be measured; facts are taken only from the host firm's own
page [F] or an academic paper [A], and anything else is marked [unverified] with its origin. Competition
write-ups and forums are practitioner pointers only and were not used as evidence.

##### C.1 The competitions, facts by source

| Competition | Task and metric | Validation / final scoring | Winning approach | Source and status |
|---|---|---|---|---|
| Two Sigma Financial Modeling Challenge (launched 2016-12-01) | "submitting code to forecast returns, with scores appearing on the competition leaderboard virtually in real time"; anonymised time-series features; metric (a signed square root of R2, "R") [unverified: memory, not read] | code competition; private score on later, unseen time periods [unverified] | not read | [F] Two Sigma, "Two Sigma Partners with Kaggle" (twosigma_partners_kaggle.html): "On December 1st, we launched our first public coding competition with Kaggle. Their community of over 700k data scientists has been invited to compete in a financial modeling competition, submitting code to forecast returns, with scores appearing on the competition leaderboard virtually in real time." Run dates December 2016 to March 2017 [unverified: WebSearch snippet of a winners' interview] |
| Jane Street Market Prediction (announced 2020-11-24) | trade/no-trade decision on anonymised opportunities; "utility" score [unverified: not read] | forecasting phase scored on live data after the close, with leaderboard updates to 25 Aug 2021 [unverified: WebSearch snippet of a university news post] | not read | [F] Jane Street blog, Craig Falls, Nov 24 2020 (janestreet_blog_kaggle_index.html): "Jane Street is running a Kaggle contest based on a real problem with real financial data ... with a total $100K being paid out." |
| Optiver Realized Volatility Prediction (2021) | forecast 10-minute realised volatility of stocks from order-book snapshots; RMSPE [unverified: memory] | not read | not read | No host page read (the Optiver page fetched for the later contest returned a JavaScript shell with no text). VOLATILITY, not direction: not evidence on directional predictability in any case. |
| Optiver Trading at the Close (2023) | forecast the 60-second-ahead move of a Nasdaq stock's weighted price relative to an index during the closing auction, in basis points; MAE; about 4,000 teams [unverified: WebSearch snippet] | not read | not read | Host page optiver_kaggle_closing_cross.html saved but its body is script-rendered; no fact extracted. |
| G-Research Crypto Forecasting (Nov 2021 - May 2022) | "forecast the short-term returns of 14 different crypto coins ... evaluated on a weighted Pearson correlation coefficient" | "each team selected their two best models for submission and we ran them for three months against real live market data to get our final leaderboard" | "all of our top three used a LightGBM model, though some experimented with other approaches, including neural networks. However, all of our top competitors believed it was their feature engineering that contributed most to their wins." | [F] G-Research, "Wrapping up the G-Research Crypto Forecasting competition", 30 May 2022 (gresearch_crypto_wrapup.html). Also: "With such a noisy dataset, it was unsurprising that the leaderboard saw many big jumps and precipitous drops, particularly early in the competition." Winning correlation value: not stated on the host page; not read elsewhere. |
| M6 Financial Forecasting Competition (Feb 2022 - Feb 2023; monthly horizon, 100 assets; included as the one market competition with a peer-reviewed results paper) | quintile-probability forecasts (RPS) and portfolio weights (information ratio, IR) | live evaluation, 12 monthly submission points | see C.2 | [A] Makridakis, Spiliotis, Hollyman, Petropoulos, Swanson and Gaba, arXiv 2310.13357 (IJF), arxiv_2310_13357_m6_competition.pdf; [A] Stanek, arXiv 2412.04490, arxiv_2412_04490_m6_luck.pdf |

##### C.2 What the measured competition evidence says about selection and overfitting

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

#### A. Evidence table: out-of-sample directional forecasts at 1-240 minutes (topic a)

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

#### D. Decay and crowding of intraday predictability (topic d)

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

#### E. What this implies for E.33 (topic e). Evidence and judgement are marked separately.

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

#### F. Discovery log, stopping rule, and what was not done

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

# Part M. The mathematics and ML for directional signals

## M1. Order-flow measures

Source file: reports/stage_e32_briefs/M1_order_flow.md (sha256 38bd42b19509ceb18c3abedeaed9dcf5502408fa0597f44fc425f0060b44b964).

### E.32 Part M1: order-flow measures for FORWARD directional prediction in ZM (1 s to 30 min)

Worker: OrderFlowMath-OpusHigh (re-spawned run; the first run fetched the evidence pages at 23:05-23:13 PDT on
2026-10-26 but wrote no output). Written 2026-10-27 from 00:23 PDT. ROOT = M1_order_flow.
Evidence pages and log: reports/stage_e32_briefs/pages/M1_order_flow/ (log.tsv). Arithmetic:
reports/stage_e32_briefs/work/M1_order_flow/M1_examples2.py, output M1_examples2.out (every number in a worked
example below is printed there). M1_examples.py / .out from the first run are SUPERSEDED: its Chordia-Roll-
Subrahmanyam R-squared inputs did not match the paper's Table 5 and are corrected here (section 2.3).

Scope rules followed: no market data read, no statistic derived from data, nothing registered, N stays 538.
Every equation or claim from a source carries a quote and the saved file; [unverified] marks abstract-only or
snippet-only knowledge. E.28 sections cited as "E.28 2.x" (reports/stage_e28_methods_brief.md); I read only the
line ranges my brief names (2.9 sections 7 and 9, 4.6; 2.3 section 5 headings and 5.1/5.7/5.8) and do not repeat
them.

#### 0. What is new here relative to E.28, in one paragraph

E.28 2.9 treated order flow as a sub-second, passive-execution problem and concluded that "as an execution aid ...
much of the signal survives 100 ms; as a standalone alpha, almost none does". This part asks the different
question E.32 needs: what order-flow measures can say about the ZM mid-price 1 to 30 MINUTES ahead, where a
taker's round trip costs about 1.59 ticks at Topstep (E.28 ranking row 130, column mu*_mkt = 1.59). The answer
from the sources read: (1) every measure in this part is far stronger contemporaneously than forward; (2) the
forward part decays to statistical insignificance by 5 to 30 minutes in the best-documented case (Chordia, Roll and
Subrahmanyam 2005, NYSE) and to "approximately two average price changes" for deep-learned order-flow forecasts
(Kolm, Turiel and Westray 2023, abstract), which is about 12 seconds in ZM under a stated assumption; (3) trade-sign
persistence is by construction offset by asymmetric liquidity, so it predicts flow, not price; (4) the one
minutes-scale order-flow-adjacent effect with a large published forward R-squared in a CBOT grain is the
post-drift-burst reversal (Christensen, Oomen and Renò: ZC corn, 97 events, b = -0.20, R2 = 41.5%), and its event
time is defined at a local extremum of the test statistic, a look-ahead that a frozen protocol must remove before
trusting the number. Order-flow measures therefore enter a ZM directional search as conditioners and as event
detectors (planner families 5 and 7), not as standalone forecasts.

#### 1. The common hurdle at minutes horizons (extends E.28 2.9 section 7.4 from MES to ZM)

Assumptions, stated: (A1) ZM mid changes follow a random walk across minutes, so sigma_h = sigma_1m x sqrt(h)
with sigma_1m = 3.15 ticks (A0 Table 1); (A2) a forecast f of the h-minute mid change is normal with
sd(f) = sqrt(R2) x sigma_h, R2 being its out-of-sample R-squared; (A3) the taker hurdle is BE = 1.59 ticks per
round trip (E.28 ranking row 130, mu*_mkt). For a normal forecast, E|f| = sd(f) x sqrt(2/pi), sqrt(2/pi) =
0.7979. If only the top decile of |f| is traded, the mean |f| traded is sd(f) x E[|Z| : |Z| > 1.6449] =
sd(f) x phi(1.6449)/0.05 = sd(f) x 0.10314/0.05 = sd(f) x 2.0627. Setting the mean traded |f| equal to BE and
solving gives the out-of-sample R2 a forecast needs merely to break even on average (gross of slippage beyond
the E.28 cost model):

| h (min) | sigma_h = 3.15 x sqrt(h) (ticks) | R2 needed, trade every bar = (1.59/(sigma_h x 0.7979))^2 | R2 needed, top decile only = (1.59/(sigma_h x 2.0627))^2 |
|---|---|---|---|
| 1 | 3.150 | 0.400 | 0.0599 |
| 5 | 7.044 | 0.0800 | 0.0120 |
| 15 | 12.200 | 0.0267 | 0.0040 |
| 30 | 17.253 | 0.0133 | 0.0020 |

Check (h = 5): 3.15 x 2.2361 = 7.044; 7.044 x 2.0627 = 14.53; (1.59/14.53)^2 = 0.01197. Matches.
Reading: a forecast at 1 minute needs an out-of-sample R2 near 6% even when it trades only its top decile; at 30
minutes 0.2% suffices. The "R2 needed" falls as 1/h. In the one source read that reports forward order-imbalance
R2 at 5 to 60 minutes (CRS 2005 Table 5, section 2.3), R2 also falls roughly as 1/h (1996: 3.32% at 5 minutes,
0.53% at 30, a factor 6.3 against 6.0 for 1/h), but the imbalance coefficient itself loses significance by 30
minutes, so the 30-minute R2 is mostly the lagged return and noise. Longer horizons therefore do not rescue an
unconditional order-flow forecast; the only route left is conditioned subsets (events, extremes), which is what
planner families 5 and 7 propose.

#### 2. (a) Order-flow imbalance: best-level, multi-level, integrated, deep; contemporaneous versus forward

E.28 2.9 sections 1-4 give the definitions, the MES worked examples and the sub-second evidence; section 7 gives
the identity R2_pred = rho^2 x R2_c under a linear model; section 9 gives the latency decay. Below: only what a
1 s to 30 min forward search adds.

##### 2.1 Core idea

OFI adds up, over a window, the net change in the best bid queue minus the net change in the best ask queue
(arrivals add, cancels and market orders subtract, a price-level shift books the whole new or lost queue). It
explains about 65% of the variance of mid changes in the SAME window (Cont, Kukanov and Stoikov), because the events
that move the mid are the events counted. Its forward value comes only from the persistence of order flow, which
is small and decays fast; at minutes horizons the published forward R2 is near zero or negative out of sample,
and what survives is cross-asset and short-lived (Cont, Cucuringu and Zhang 2023).

##### 2.2 Equations (source equation numbers where the full text shows them)

- Event contribution (Xu, Gould and Howison, eqs. 2-4; same as CKS): for the n-th book event,
  e_n = DeltaW(tau_n) - DeltaV(tau_n), where DeltaW = r1(tau_n) if the best bid price b1 rose, r1(tau_n) -
  r1(tau_{n-1}) if unchanged, -r1(tau_{n-1}) if it fell; DeltaV is the mirror image for the ask queue q1 at price
  a1 (q1(tau_n) if a1 FELL, q1(tau_n) - q1(tau_{n-1}) if unchanged, -q1(tau_{n-1}) if it rose). r1, q1 are best bid
  and ask sizes in contracts; tau_n event times.
- Window OFI (XGH eq. 5): OFI(t_{k-1}, t_k) = sum of e_n over events in (t_{k-1}, t_k].
- Order-level identity (CKS, text above eq. 1): OFI = L^b - C^b - M^s - L^s + C^s + M^b, with L limit-order
  arrivals, C cancels, M market orders at the best quotes (b bid side, s/a ask side), in contracts.
- Stylized impact (CKS eq. 1): DeltaP = OFI/(2D) + epsilon, D the (equal) depth per level in contracts, DeltaP in
  ticks; regression form (CKS eq. 2): DeltaP_k = beta OFI_k + epsilon_k; depth link (CKS eq. 3):
  beta_i = c / AD_i^lambda + nu_i, AD_i the average best-queue size over the half-hour window i.
- Multi-level OFI (XGH eqs. 9-12): the same e^m computed at the m-th occupied level, m = 1..M, giving the vector
  MLOFI(t_{k-1}, t_k) = (MLOFI^1, ..., MLOFI^M); XGH fit DeltaP on it with OLS and Ridge.
- Integrated OFI (Cont, Cucuringu and Zhang, eq. 4): ofi^I_{i,t} = w1' ofi^(h)_{i,t} / ||w1||_1, w1 the first
  principal vector of the multi-level OFI vector, "computed from historical data".
- Forward model with cross-asset lags (CCZ eq. 15, "FCI^I"): r_{i,t+f} = alpha_i + sum_j sum_{k in L}
  beta_{i,j}^{I,k} ofi^{I,(kh)}_{j,t} + eta, L = {1,2,3,5,10,20,30} minutes of lagged OFI, f the forecast
  horizon in minutes, re-estimated on the previous 30 minutes and rolled forward each minute.
- Linear forward bound (E.28 2.9 section 7.2): R2_pred = rho^2 R2_c, rho the lag-1 autocorrelation of window OFI.

##### 2.3 Worked example on ZM

(i) Stylized impact. Assume (illustrative, no data read) a ZM depth of D = 50 contracts at each best quote.
By CKS eq. 1 one tick of mid move needs OFI = 2D = 100 contracts; an OFI of +30 contracts gives
DeltaP = 30/(2 x 50) = 0.30 tick, contemporaneously. Check: 0.30 x 100 = 30.

(ii) What is left forward. With R2_c = 0.65 (CKS average) and a lag-1 OFI autocorrelation rho of 0.05, 0.1 or
0.2 (assumptions bracketing CKS's "small" 10-second autocorrelations), R2_pred = 0.0016, 0.0065, 0.026
(M1_examples2.out A3). Against section 1, at 1 minute even rho = 0.2 (R2 = 0.026) is below the 0.060 needed for
top-decile trading; at 5 minutes it exceeds the 0.012 top-decile need, but CKS's own statement is that OFI
autocorrelations at 10 s "are small and quickly vanish", so rho at 5-minute aggregation is not expected to be 0.2.

(iii) The one published forward-R2 table at 5-60 minutes (CRS 2005 Table 5, NYSE 150 largest stocks, regression
of the next interval's midpoint return on the lagged midpoint return and lagged trade-count imbalance OIB#;
R2 is the cross-sectional average adjusted R2 in percent). Mapped onto ZM under A1 and A2 (an assumption: that
ZM would show the same R2), sd(f) = sqrt(R2) x sigma_h:

| CRS cell | R2 | sigma_h ZM (ticks) | sd(f) | mean abs f | top-decile mean abs f | vs BE 1.59 |
|---|---|---|---|---|---|---|
| 1996, 5 min | 0.0332 | 7.044 | 1.283 | 1.024 | 2.647 | top decile clears |
| 1996, 30 min | 0.0053 | 17.253 | 1.256 | 1.002 | 2.591 | top decile clears, but OIB# coefficient weak (avg t 2.24, cross-sectional t 2.00) |
| 2002, 5 min | 0.0054 | 7.044 | 0.518 | 0.413 | 1.068 | does not clear |
| 2002, 30 min | 0.0018 | 17.253 | 0.732 | 0.584 | 1.510 | does not clear; OIB# not significant (avg t 0.50) |

Check (2002, 5 min): sqrt(0.0054) = 0.0735; x 7.044 = 0.518; x 2.0627 = 1.068. The decisive fact is the time trend:
between 1996 and 2002 the 5-minute R2 fell from 3.32% to 0.54% (a factor of 6) as markets automated, and CRS add
that the rule was feasible "only for the specialist and perhaps sophisticated floor traders" who could see the
imbalance. In ZM every participant sees the aggressor side in real time, so the starting point is the 2002 row or
below, which does not clear the hurdle.

(iv) Forward horizon of deep order-flow forecasts. Kolm, Turiel and Westray (abstract): "the effective horizon of
stock specific forecasts is approximately two average price changes". Assume ZM mid changes are +-1 tick steps of
a random walk (an assumption; half-tick moves through a 2-tick spread and bid-ask bounce break it). Then the
number of mid changes per minute is about sigma_1m^2 / (1 tick)^2 = 3.15^2 = 9.92, one change every 60/9.92 =
6.05 s, and two average price changes take about 12 s. Check: 9.92 changes x 6.05 s = 60.0 s. So the
deep-learned order-flow edge, if it transfers, lives at about 12 seconds in ZM: inside E.31's measured passive
10-second window (gross -0.970 ticks per fill) and below the 1-minute floor of this search.

(v) Cross-asset lags. CCZ's only positive forward finding is that LAGGED CROSS-ASSET OFI helps: Table 8
out-of-sample R2 for one-minute-ahead returns is -0.37 (own best-level OFI), -0.36 (own integrated OFI) and
-0.10 (with cross-asset OFI), all negative, and "this lagged cross-impact mainly manifests at short-term
horizons and decays rapidly in time". The ZM analogue is lagged ZS and ZL best-level OFI (computable from the
owned MBP-1) as features for the ZM 1-5 minute label; planner family 6 already caps this at "a feature only".
[MathReview B-6 (lead: accepted): CCZ Table 8 (saved lines 1464-1467) has six columns, FPI[1] −0.37, FCI[1] −0.10, FPI^I −0.36, FCI^I −0.10, AR −0.36, CAR −0.10, and the cross-asset lagged RETURNS model (CAR, no OFI) reaches the same −0.10; read "cross-asset lags (OFI or returns alike) are less negative out of sample; Table 8 does not separate OFI from returns". The MAYBE-as-feature verdict is unaffected; the verdict-table reason column (original line 739) should not credit OFI specifically.]

##### 2.4 Data it needs (owned schemas) and horizon

- Best-level OFI: ZM MBO (book rebuilt to level 1) or the level-1 quote and size changes; ZS and ZL MBP-1 give
  exactly the inputs of XGH eqs. 2-5 (best price and size after each event). Aggregate on a 1-second grid, then
  sum to 1, 5, 15, 30 minutes.
- MLOFI and integrated OFI: ZM only (needs levels 2..M, available only by rebuilding the book from MBO; ZS and ZL
  have no depth beyond level 1). The order-level identity (L, C, M separately) is also ZM-only; MBP-1 gives only
  the net queue changes.
- Use ts_recv (receive time) as the knowledge time for every feature; definitions file for tick size and the
  v.0/v.1 roll map.

##### 2.5 Leakage and look-ahead traps, each with a test

1. Contemporaneous overlap: a label window that starts before the feature window ends inherits R2_c (65%). Test:
   assert label_start >= feature_end + delay (delay frozen, e.g. 1 s) in code; and a canary: shift the label back
   by one bar; if the out-of-sample R2 jumps by an order of magnitude, the production alignment is right and the
   canary shows what leakage would look like (log both).
2. Normalizers from the future: OFI divided by depth AD_i (CKS eq. 3 uses the window's own average) or by a
   daily volatility. Test: future-scramble invariance, i.e. replace all data after time t with noise and assert
   every feature at t is bit-identical.
3. Integrated-OFI weights w1 fitted on the full sample (CCZ eq. 4 requires "historical data"). Test: fit w1 inside
   each training fold only; the future-scramble test above also catches it.
4. ts_event versus ts_recv: exchange timestamps precede the time the data could be acted on. Test: recompute
   features with ts_recv + 50 ms; a forward R2 that collapses means the edge was latency (E.28 2.9 section 9).
5. Roll and session joins: OFI summed across the v.0 roll or across the 13:20 close to 19:00 reopen gap. Test:
   assert no feature or label window spans a roll date in the roll blackout or a session gap longer than the
   label horizon.
6. Overlapping labels (5-30 minute labels on a 1-minute grid): purged and embargoed CV per V43. Test: assert
   train/test index sets are separated by at least the label horizon plus the feature lookback.

##### 2.6 Compute (ThinkPad, 39 months)

One streaming pass over ZM MBO per day rebuilds the book and writes per-second OFI vectors (levels 1..M). The
message count is a DataFacts item; at an ASSUMED 2 million ZM messages per day and about 819 trading days
(39 months at 252 days a year) the pass touches about 1.6 billion messages; a compiled (numba or Rust) book
builder at an assumed 5-10 million messages per second needs 3-6 minutes of CPU plus I/O, in day-sized chunks,
single-threaded per day, at most 8 days in parallel under the default limits; memory is per-day (well under 1 GB).
ZS/ZL MBP-1 OFI is cheaper (no book rebuild). The per-second output is about 819 x 23 h x 3600 s x M floats, about
68 million rows x M; at M = 5 float32 that is about 1.4 GB on disk, so store per-day parquet.

##### 2.7 Verdict for a minutes-scale directional ZM search under V43

MAYBE, as features only: best-level OFI of ZM, ZS and ZL lagged 1-30 minutes and ZM integrated OFI enter the
frozen feature set as conditioners; no OFI-only model is a separate configuration (each would add to N with
published forward R2 below the section-1 hurdle). SKIP deep order-flow models (horizon about 12 s in ZM by 2.3 iv)
and SKIP MLOFI as a separate block (contemporaneous gains only; XGH's improvement is "goodness-of-fit" of the
contemporaneous relation).

##### 2.8 Evidence table (a)

| Claim | Source | Verbatim quote | File |
|---|---|---|---|
| OFI explains same-window mid changes with R2 about 65% | Cont, Kukanov and Stoikov (2014), arXiv 1011.6402v3 | "with an average R2 of 65%" | cks_2014_price_impact_order_book_events.txt |
| Stylized impact equation | CKS eq. 1 | "OF I = Lb − C b − M s − Ls + C s + M b and  is the truncation error" (around "∆P = OFI/2D + ε, (1)") | same |
| OFI autocorrelations vanish fast | CKS | "In our data the autocorrelations at a timescale of 10 seconds are small and quickly vanish as well" | same |
| Depth link | CKS eq. 3 | "βi = c / ADi^λ + νi , (3)" (as rendered) | same |
| MLOFI is a contemporaneous fit | Xu, Gould and Howison (arXiv 1907.06230) | "a simple, linear relationship between MLOFI and the contemporaneous change in mid-price" | xu_gould_howison_2018_mlofi.txt |
| MLOFI gain is out-of-sample goodness of fit, large-tick 65-75% | XGH | "improves the goodness-of-fit of the MLOFI regressions for all of the stocks in our sample, with an improvement of about 65–75% for large-tick stocks" | same |
| Integrated OFI: first PC, l1-normalized, from historical data | Cont, Cucuringu and Zhang (arXiv 2112.13213) eq. 4 | "where w 1 is the first principal vector computed from historical data" | ccz_2023_cross_impact_ofi.txt |
| First PC explains most multi-level OFI variance | CCZ | "the first principal component can explain over 89% of the total variance among multi-level OFIs" | same |
| Forward: own OFI out-of-sample R2 negative at 1 min; cross-asset less negative | CCZ Table 8 | "OS R2 -0.37 -0.10 -0.36 -0.10 -0.36 -0.10" | same |
| Forward cross-impact decays fast | CCZ abstract | "this lagged cross-impact mainly manifests at short-term horizons and decays rapidly in time" | same |
| CCZ horizons and lags | CCZ section 4.2 | "including f ∈ {2, 3, 5, 10, 20, 30} minutes" and "L = {1, 2, 3, 5, 10, 20, 30} represents the set of lags" | same |
| Forward imbalance predictability lost by 30 minutes | Chordia, Roll and Subrahmanyam (2005 JFE; 2004 working paper) | "In no more than thirty minutes, order imbalances lose their predictive ability and returns are no longer negatively dependent." | crs_2005_speed_of_convergence_wp.txt |
| Forward R2 values, OIB# regressions | CRS Table 5 | 1996 row: "R2 3.32 1.59 1.42 0.94 1.02 0.78 0.53 0.43 0.52 0.43"; 2002 row: "R2 0.54 0.32 0.35 0.30 0.28 0.93 0.18 0.16 0.17 0.15" (pairs = OIB# then OIB$ at 5, 10, 15, 30, 60 min) | same |
| Only insiders could trade it | CRS | "A trading rule based on the short-period results in Table 5 is therefore feasible only for the specialist and perhaps sophisticated floor traders." | same |
| Deep order-flow forecast horizon | Kolm, Turiel and Westray (2023), Mathematical Finance 33(4) | "the effective horizon of stock specific forecasts is approximately two average price changes" [abstract only, IDEAS page; full text not read: Wiley terms forbid automated access, see section 11] | ideas_ktw_2023.html(.txt) |
| Order flow beats raw book as model input | KTW abstract | "models trained on order flow significantly outperform most models trained directly on order books" [abstract only] | same |

#### 3. (b) Trade-sign imbalance and its long memory: why sign persistence does not predict price

##### 3.1 Core idea

The signs of market orders (buy +1, sell -1) are strongly autocorrelated with a slowly decaying power law,
because large orders are split (Lillo and Farmer 2004; Bouchaud, Gefen, Potters and Wyart 2004). The NEXT trade's
sign is therefore predictable, yet returns are close to uncorrelated: liquidity providers who see the same
persistence make the expected move of the predicted (likely) trade small and of the surprising trade large, so
the expected mid change is zero ("asymmetric liquidity", Bouchaud, Farmer and Lillo 2009). Predicting flow is not
predicting price; at minutes scale extreme sign imbalance even coincides with a PINNED price (Patzelt and
Bouchaud).

##### 3.2 Equations

- Sign autocorrelation (BGPW eq. 7): C0(l) = <eps_{n+l} eps_n> ~= C0 / l^gamma (l >= 1), eps_n the sign of trade
  n, l the lag in trades, 0 < gamma < 1 ("for FT, one finds γ ≈ 1/5, whereas for Total γ ≈ 2/3").
- Effective number of correlated trades out of 1000 (BGPW eq. 8): N_e ~= 1 + sum_{l=1}^{1000} C0(l) ~= 1 +
  C0/(1-gamma) x 1000^(1-gamma).
- Lillo and Farmer (abstract): on the LSE the sign autocorrelation "decays roughly as τ^−α with α ≈ 0.6,
  corresponding to a Hurst exponent H ≈ 0.7" (alpha plays the role of BGPW's gamma; alpha = 2 - 2H).
- Asymmetric liquidity (BFL 2009 eqs. 6.21-6.24): r_n = m_{n+1} - m_n = eta_n + theta (eps_n - eps_hat_n),
  eps_hat_n = E_n[eps_{n+1} | I] the liquidity providers' sign predictor, theta the impact per unit surprise.
  Efficiency E_{n-1}[r_n | I] = 0 implies phi+_n r+_n - phi-_n r-_n = 0 (eq. 6.22) with r+ = theta (1 - eps_hat),
  r- = theta (1 + eps_hat) (eqs. 6.23-6.24); phi+ (phi-) the probability that the trade matches (opposes) the
  predictor.
- Aggregate sign impact (Patzelt and Bouchaud eqs. 2-5, 9): R_N(Q) = <log m_{t+N} - log m_t | Q>, Q the signed
  volume over N trades; R_N(Q) ~= R_N F(Q/Q_N), Q_N ~ N^xi, R_N ~ N^psi; same for the sign imbalance E.

##### 3.3 Worked example

(i) BGPW eq. 8 on their FT numbers (C0 = 0.2, gamma = 0.2, l up to 1000): closed form 1 + 0.2/0.8 x 1000^0.8 =
1 + 0.25 x 251.19 = 63.8; the exact sum 1 + sum 0.2 l^-0.2 = 63.68 (M1_examples2.out B1). The paper's text says
"a factor Ne ≈ 50": the order of magnitude agrees, the paper's rounding is loose (63.7, not 50). Its point
stands: if each trade had a permanent fixed impact, sign memory would amplify impact about 50-60 times between
lag 1 and lag 1000, which is not observed; the impact must therefore be transient or history dependent.

(ii) Asymmetric liquidity, ZM-sized. Assume a ZM sign predictor eps_hat = 0.2 (the next market order is a buy with
probability (1 + 0.2)/2 = 0.6) and theta = 0.5 tick (illustrative). Then r+ = 0.5 x (1 - 0.2) = 0.40 tick when the
trade matches, r- = 0.5 x (1 + 0.2) = 0.60 tick when it does not; phi+ = 0.6, phi- = 0.4. Expected mid change =
0.6 x 0.40 - 0.4 x 0.60 = 0.24 - 0.24 = 0 ticks. Check: a correct 60/40 call on flow earns nothing on price. Any
directional edge from sign imbalance must come from a liquidity provider who UNDER-predicts the persistence
(slow information set), which in an electronic CBOT book with visible aggressor flags is not the base case.

(iii) Minutes scale. Patzelt and Bouchaud: "extreme order flow imbalance is not associated with large returns. To
the contrary, it is observed when the price is 'pinned' to a particular level." A 30-minute ZM window in which 85%
of trades are buys is, on this evidence, more likely a passive seller (an iceberg or a worked offer, section 7)
absorbing flow at one price than the start of a move.

##### 3.4 Data (owned)

ZM MBO trade events (action T or F with aggressor side) give eps_n exactly; ZS and ZL MBP-1 carry trade events
with side. No Lee-Ready inference is needed. Horizons: sign imbalance over the last 100-1000 trades or 1-30 min.

##### 3.5 Leakage traps and tests

1. Counting the trade that defines the label's first mid change in the feature (fill and mid change share a
   timestamp). Test: assert every trade in the feature has ts_recv strictly before the label's start mid.
2. Implied (spread-leg) trades and the trade-summary versus per-fill records double counting volume. Test: count
   per-match volume twice (summary and fills) on a known day and assert one equals the other (DataFacts owns the
   schema detail).
3. Using the full-day sign autocorrelation fit (C0, gamma) as a feature normalizer. Test: future-scramble invariance
   (section 2.5 test 2).

##### 3.6 Compute

Trivial next to the book rebuild: one counter per trade.

##### 3.7 Verdict

SKIP as a standalone directional predictor: the mechanism (3.3 ii) and the evidence (3.3 iii) both say sign
persistence is priced. MAYBE as a conditioner inside families 5 and 7: a large one-sided sign imbalance with NO
price move flags absorption (a refilling passive order, section 7), which conditions a breakout or reversal
label; a sign imbalance WITH a burst-sized move is the drift-burst state of section 9.

##### 3.8 Evidence table (b)

| Claim | Source | Verbatim quote | File |
|---|---|---|---|
| Order signs are long-memory; future signs predictable | Lillo and Farmer (2004), arXiv cond-mat/0311053 | "The autocorrelation function decays roughly as τ −α with α ≈ 0.6, corresponding to a Hurst exponent H ≈ 0.7. This implies that the signs of future orders are quite predictable from the signs of past orders" | lillo_farmer_2004_long_memory.txt |
| Market stays efficient via liquidity and size fluctuations | Lillo and Farmer | "fluctuations in order signs are compensated for by anti-correlated fluctuations in transaction size and liquidity, which are also long-memory processes. This tends to make the returns whiter." | same |
| Power-law sign correlation, stock-dependent gamma | BGPW (2004), arXiv cond-mat/0307332, eq. 7 | "For example, for FT, one finds γ ≈ 1/5, whereas for Total γ ≈ 2/3." | bouchaud_gefen_potters_wyart_2004.txt |
| Amplification puzzle | BGPW eq. 8 | "For FT, γ ≈ 1/5 and C0 ≈ 0.2, which means that the effect of one trade should be amplified, through the correlations, by a factor Ne ≈ 50 !" | same |
| Asymmetric liquidity | Bouchaud, Farmer and Lillo (2009), arXiv 0809.0822, section 6.5.1 | "This result shows that the most likely outcome has the smallest impact. We call this mechanism asymmetric liquidity" | bouchaud_farmer_lillo_2009_digest.txt |
| Small deviations at high frequency only | BFL 6.5.1 | "This is a plausible first approximation, although one can expect (and indeed observes) deviations from strict unpredictability at high frequencies." | same |
| Extreme imbalance means pinned price | Patzelt and Bouchaud (arXiv 1706.04163) | "extreme order flow imbalance is not associated with large returns. To the contrary, it is observed when the price is “pinned” to a particular level." | patzelt_bouchaud_2018_aggregate_impact.txt |

#### 4. (c) Kyle's lambda at minute horizons (Hasbrouck-style regressions)

##### 4.1 Core idea

Kyle's lambda is the slope of the price change on signed order flow over the same interval: a liquidity (price
impact) STATE, contemporaneous by construction. For forward direction it can only scale or condition another
signal (a high-lambda state makes a given flow move the price more; a low-lambda state is where absorption,
section 3.3 iii, happens). Its estimated slope also shrinks with the aggregation window (Patzelt and Bouchaud),
so lambda at 1 minute and at 30 minutes are different numbers, and a frozen protocol must fix one.

##### 4.2 Equations

- Hasbrouck (2009 JF) eq. 4: Delta p_it = lambda_i x S_it + epsilon_it, where S_it is the SIGNED SQUARE ROOT of
  dollar volume over 5-minute interval t ("price changes and signed volume aggregated over 5-minute intervals. A
  separate estimate is computed for each month"); Delta p the log price change.
- Easley, Lopez de Prado, O'Hara and Zhang (2019 NBER version) bar form: lambda_tau = (p_tau - p_{tau-W}) /
  sum_{i=tau-W}^{tau} b_i V_i, b_i = sign(p_i - p_{i-1}) on bars, V_i bar volume, W the lookback.
- Aggregation scaling (Patzelt and Bouchaud, text after eqs. 3-6): the slope of the linear part of aggregate
  impact, dR_N/dQ at Q = 0 = R_N/Q_N, "scales as N^-κ with κ = ξ − ψ ≈ 0.25", N the number of trades in the window.

##### 4.3 Worked example

Assume (illustrative, no data read) a ZM 1-minute lambda of 0.02 tick per contract of signed volume and a 1-minute
signed-volume standard deviation of 60 contracts (for scale: day-session volume 36,690 x 0.83 = 30,453 contracts
over the 290-minute session = 105 contracts per minute on average, M1_examples2.out C1).
- Contemporaneous R2 = (lambda x sd(Q))^2 / sigma_1m^2 = (0.02 x 60)^2 / 3.15^2 = 1.44 / 9.9225 = 0.145.
- Forward, with a lag-1 signed-volume autocorrelation of 0.1 (assumption): 0.01 x 0.145 = 0.0015, far below the
  0.060 needed at 1 minute for top-decile trading (section 1).
- Window scaling: if trades per window are proportional to minutes (assumption), the slope at h minutes is
  0.02 x h^-0.25: 0.0134 at 5, 0.0102 at 15, 0.0086 at 30 ticks per contract. Check: 30^-0.25 = 1/2.340 = 0.4273;
  0.02 x 0.4273 = 0.00855.
- Hasbrouck's unit check: median lambda about 7 x 10^-6 per sqrt(dollar); a 10,000-dollar order moves log price
  by sqrt(10,000) x 7 x 10^-6 = 100 x 7 x 10^-6 = 0.0007 = 7 bp, matching the paper's text.

##### 4.4 Data (owned)

ZM MBO trades with aggressor side (signed volume) and mid; ZS/ZL MBP-1 the same at level 1. Rolling estimate over
a trailing window (for example the last 60 one-minute bars), fixed in the protocol.

##### 4.5 Leakage traps and tests

1. Estimating lambda over a window that overlaps the label (the slope then "knows" the label's move). Test: assert
   the estimation window ends at or before feature time t.
2. Using a full-month lambda (Hasbrouck's monthly estimate) as a feature for days within that month. Test:
   future-scramble invariance.
3. The ELOPZ bar form takes b_i from the bar's price change, so on the bar that contains a burst the "signed
   volume" is the price change's sign: it is a volatility proxy. Test: report its correlation with |return| over
   the same window; above about 0.5 (a frozen threshold) it is treated as a volatility feature, not a flow one.

##### 4.6 Compute

A rolling OLS per bar; seconds over 39 months.

##### 4.7 Verdict

MAYBE as a conditioner (liquidity state, in the feature set at one frozen window); SKIP as a direction source.
ELOPZ, the one 87-futures study that uses Kyle's lambda in out-of-sample prediction, predicts the sign of changes
in spread, realized volatility and higher moments a week ahead, not the sign of returns, and finds "some of
these microstructure features with apparent high explanatory power can exhibit low predictive power".

##### 4.8 Evidence table (c)

| Claim | Source | Verbatim quote | File |
|---|---|---|---|
| Hasbrouck price-impact regression, 5-min, monthly | Hasbrouck (2009 JF), author copy | "The specification is estimated using price changes and signed volume aggregated over 5-minute intervals. A separate estimate is computed for each month." | hasbrouck_2009_jf_gibbs.txt |
| Unit check | Hasbrouck | "a $10,000 buy order would move the log price by 10,000 × 7 × 10−6 = 0.0007, that is, seven basis points" (the square-root sign is lost in the PDF text; the arithmetic requires sqrt(10,000)) | same |
| Bar-level Kyle lambda | Easley, Lopez de Prado, O'Hara, Zhang (NBER conference version 2019) | "where 𝑏𝑖 = sign[𝑝𝑖 − 𝑝𝑖−1 ], which is computed on bar level, and 𝑊 is the lookback window size." | elopz_2019_microstructure_machine_age_nber.txt |
| Their labels are not return direction | ELOPZ | "We focus on predicting six important outcomes of market price dynamics using a one-week forecast horizon: the sign of change of the bid-ask spread; sign of change in realized volatility; ..." | same |
| Explanatory is not predictive | ELOPZ abstract | "some of these microstructure features with apparent high explanatory power can exhibit low predictive power, and vice versa" | same |
| Impact slope falls with window size | Patzelt and Bouchaud | "It scales as N −κ with κ = ξ − ψ ≈ 0.25, i.e. it decreases with N as a power-law" | patzelt_bouchaud_2018_aggregate_impact.txt |

#### 5. (d) The microprice for a large-tick, 1-tick-spread book

E.28 2.3 section 5 covers the definition, the Markov computation and the evidence (from the same Gatheral60
slides, saved again here as stoikov_gatheral60_microprice_slides.pdf). Added here: what the microprice can and
cannot do 1-30 minutes ahead in ZM.

##### 5.1 Core idea

The microprice is the expected mid-price "in the distant future" given today's imbalance and spread, and it is a
martingale, so it is horizon independent: the expected mid change from now to any later time is the same bounded
adjustment, which in a 1-tick-spread book lies between the bid and the ask. It is therefore a better fair-value
estimate (for labels and entry prices), not a source of minutes-scale drift.

##### 5.2 Equations (slides)

- Imbalance I_t = Q^b/(Q^b + Q^a), spread S_t, mid M_t; P^micro_t = lim_i P^i_t, P^i_t = E[M_{tau_i} | F_t], tau_i
  the successive times the mid changes.
- Main result: P^i_t = M_t + sum_{k=1}^{i} g^k(I_t, S_t), g^1(I, S) = E[M_{tau_1} - M_t | I, S], g^{i+1} =
  E[g^i(I_{tau_1}, S_{tau_1}) | I, S]; discrete version g^1 = (1 - Q)^{-1} R^1 k, B = (1 - Q)^{-1} R^2,
  G* = P^micro - M = sum_{i>=2} (eigen-terms of B) g^1.
- Toy model 2 (Brownian imbalance, spread 1): P^micro_t = M_t + I_t - 1/2.

##### 5.3 Worked example (ZM, 1-tick spread)

Take a ZM book with Q^b = 40 and Q^a = 10 contracts at a 1-tick spread (illustrative). I = 40/50 = 0.80. Toy model 2
gives an adjustment of 0.80 - 0.50 = +0.30 tick. The largest possible adjustment in this toy is +-0.5 tick (I -> 1
or 0), which is 0.5/1.59 = 0.31 of the taker hurdle. Because P^micro is a martingale, the 5-minute and the
30-minute expected mid changes given this state are the same +0.30 tick. Check: the slides list "Micro-price is
horizon independent" and "Micro-price seems to live between the bid and the ask".

##### 5.4 Data (owned)

ZM, ZS, ZL best bid and ask sizes from MBP-1 (ZS, ZL) or the rebuilt level 1 (ZM); the transition matrices Q, R1,
R2 are estimated per training fold on a fixed (imbalance bucket, spread) grid.

##### 5.5 Leakage traps and tests

1. The slides' validation fitted G* "obtained from the first day of March" and compared it with averages over the
   whole month including that day. Test: fit the transition matrices only on training folds; future-scramble
   invariance on the fitted G*.
2. Using the microprice as a label's END price while it is also a feature: the label then contains the feature.
   Test: the label uses the mid (or microprice) at t+h only, the feature only at t, assert disjoint timestamps.

##### 5.6 Compute

A 10-30 state matrix inversion per fold; trivial.

##### 5.7 Verdict

SKIP as a directional signal at 1-30 minutes (bounded at 0.5 tick, below 1.59). USE as the price inside labels and
entry marks (replace the mid at t and t+h by the microprice to remove the bid-ask bounce noise from a 1-5 minute
label), which is a design choice, not a trial; whether it counts toward N is the lead's call.

##### 5.8 Evidence table (d)

| Claim | Source | Verbatim quote | File |
|---|---|---|---|
| Definition as the limit of expected future mids | Stoikov, Gatheral60 slides | "Ptmicro = lim Pti ... where the approximating sequence of martingale prices is given by Pti = E [Mτi |Ft ]" (as rendered) | stoikov_gatheral60_microprice_slides.txt |
| Toy model with 1-tick spread | slides | "The spread St = 1 then ... Ptmicro = Mt + It − 1/2" (as rendered across lines) | same |
| Horizon independence, bounded | slides, Summary | "6 Micro-price is horizon independent" and "7 Micro-price seems to live between the bid and the ask" | same |
| Validation horizons and calibration day | slides | "Compute averages of Mt+60 − Mt , Mt+300 − Mt and Mt+600 − Mt grouped by It and St for the entire month of March. Compare to G ∗ obtained from the first day or March." | same |
| Published claim | Stoikov (2018) QF abstract | "The micro-price estimated using high-frequency data is empirically a better predictor of short-term prices than the mid-price or the weighted mid-price" [abstract only, IDEAS] | ideas_stoikov_2018.html(.txt) |

#### 6. (e) Cancellation and replenishment rates; resiliency after a liquidity shock

E.28 2.2 (Hawkes) gives the arrival-intensity machinery (kernels, branching ratio, MLE); E.28 2.3 gives the queue
models. Added here: resiliency as a forward CONDITIONER after a sweep, at seconds-to-minutes scale.

##### 6.1 Core idea

After a market order empties the best queue (a "sweep"), the book refills. How fast and on which side it refills
says whether the shock was absorbed (fast same-side refill: reversion) or is part of one-sided pressure (slow
refill on the side being hit: continuation). Xu et al. (2016, Chinese stocks) find price resiliency after the most
aggressive (book-walking) market orders and price continuation after less aggressive ones; Bechler and Ludkovski
(2017, Nasdaq large-tick, minutes-scale volume buckets) find the side under pressure is replenished LESS than usual.
Both measure the shock and the response in the same window; no source read measures the 1-30 minute forward
return conditional on the refill rate in futures (a gap, not a finding).

##### 6.2 Equations (definitions for the protocol; the papers use these concepts, not these exact formulas)

- Sweep event at time t0 on the ask: a buy market order with penetrability p >= 1 (Xu et al.: Type-1 walks the
  book, p > 1; Type-2 empties the best level, p = 1).
- Refill ratio after Delta seconds: R(Delta) = [Q^a_1(t0 + Delta) - Q^a_1(t0+)] / [Q^a_1(t0-) - Q^a_1(t0+)], Q^a_1
  the depth at the pre-sweep best ask price (0 when that level was emptied), t0- just before, t0+ just after.
- Side-specific net limit flow over a window (Bechler and Ludkovski's V^{L,A}, V^{L,B}): additions minus
  cancellations at the touch on each side, in contracts.
- Cancellation ratio: cancels / adds at the touch over the window (order level, MBO only).
- Exponential-refill toy (an ASSUMPTION used only for the worked example): R(Delta) = 1 - exp(-Delta/tau), tau the
  refill time constant.

##### 6.3 Worked example

ZM ask queue of 50 contracts (illustrative) is swept at t0. In the toy, a "resilient" regime with tau = 2 s has
recovered 1 - exp(-6/2) = 1 - 0.0498 = 95.0% of the queue by Delta = 6 s; a "thin" regime with tau = 20 s has
recovered 1 - exp(-6/20) = 1 - 0.7408 = 25.9% (M1_examples2.out E1). A frozen feature is R(6 s) in [0, 1] (or the
fitted tau); the hypothesis family it conditions is "after a buy sweep, low R(6 s) on the ask predicts a positive
5-15 minute ZM return; high R(6 s) predicts reversion". Check: 0.950 and 0.259 differ by a factor 3.7, so the
feature separates the two regimes well inside 6 seconds, which leaves the minutes-scale label untouched.

##### 6.4 Data (owned)

ZM MBO (order-level adds and cancels by price level: full refill and cancellation ratios). ZS and ZL MBP-1: only the
net best-level size change; cancels at the best can be inferred as size decreases not matched by a trade event,
and only at level 1. Context from the grain literature (abstract level): Ma and Serra report that "Between 75% and
79% of the large number of limit orders submitted are then deleted" in CBOT corn, soybeans and wheat, so
cancellation flow is the bulk of the MBO message stream.

##### 6.5 Leakage traps and tests

1. Defining the sweep by what follows (for example "a sweep that the price did not reverse"). Test: the event
   flag at t0 is a function only of messages with ts_recv <= t0; future-scramble invariance.
2. Measuring refill over a window that overlaps the label. Test: label start >= t0 + Delta + delay.
3. Choosing Delta or tau thresholds after looking at forward returns. Test: Delta and thresholds frozen in the
   protocol; any alternative counts into N.
4. MBO book-rebuild errors at the session open (snapshot versus incremental) creating fake sweeps. Test: count
   sweeps in the first 60 s after each session open and after each data gap; assert the rate is not an outlier
   versus the session average (threshold frozen; DataFacts owns the snapshot mechanics).

##### 6.6 Compute

Event-driven pass inside the same book rebuild as section 2.6; negligible extra cost.

##### 6.7 Verdict

MAYBE, as a conditioner for family 5 (sweep and refill aftermath): it is cheap, ZM-MBO-native, and the
contemporaneous evidence (one-sided replenishment drives impact) gives a mechanism, but there is no forward
evidence in futures, so it enters as ONE frozen feature, not a grid.

##### 6.8 Evidence table (e)

| Claim | Source | Verbatim quote | File |
|---|---|---|---|
| Spread and depth recover within 20 best-limit updates | Xu, Chen, Xiong, Zhang et al. (arXiv 1602.00731v2) | "the spread and depth can return to the sample average within 20 best limit updates" | xu_lob_resiliency_after_mo_2016.txt |
| Resiliency after aggressive, continuation after less aggressive | Xu et al. abstract | "The price resiliency behavior is dominant after aggressive market orders, while the price continuation behavior is dominant after less-aggressive market orders." | same |
| Type-1 walks the book | Xu et al. | "a Type-1 order is an effective buy market order whose penetrability p is greater than 1. This means that these orders walk up the limit order book and result in multiple trades." | same |
| One-sided replenishment drives impact | Bechler and Ludkovski (arXiv 1708.02715) | "the Ask side is replenished less than usual under upside price pressure" and "LOB resilience (and hence price impact) is essentially driven by one-sided flows rather than aggregate two-sided metrics" | meso_scale_resiliency_2017.txt |
| Their "predictive" fits are same-bucket | Bechler and Ludkovski | "Pk+1 − Pk and the concurrent trade imbalance T Ik" and "from about R2 ≃ 0.4 when using only T I as a predictor for ∆P , to R2 ≃ 0.7 when using both T I and V Lj" | same |
| CBOT grain limit orders mostly deleted | Ma and Serra (AJAE 2025) abstract | "Between 75% and 79% of the large number of limit orders submitted are then deleted" [abstract only, IDEAS; full text not read] | ideas_ma_serra_2025.html(.txt) |

#### 7. (f) Detecting large orders being worked, and icebergs, from MBO

##### 7.1 Core idea

CME native icebergs keep their order ID across tranches and can trade more than their displayed size, so they are
detectable exactly from order-level data; synthetic icebergs (vendor-managed) look like a chain of new orders
arriving just after a fill and are detectable only heuristically (Zotikov and Antonov). Detecting that someone is
working a large order says where liquidity is, but Frey and Sandas find iceberg price impact is consistent with
liquidity, not information, and Bacry et al. find metaorder impact is transient and "the market does not anticipate
the size of the meta-orders". The forward directional value is therefore small and the iceberg is better used as
an absorption flag (a price level likely to hold while the iceberg lives).

##### 7.2 Equations

- Native detection (Zotikov and Antonov): an order is iceberg if a trade against it exceeds its resting displayed
  size, or if it is refreshed by a modify after a fill with the same order ID; peak size and tranche count follow
  from the message grammar (their Figure 1 finite-state machine; worked example: total 43, peaks 9, 9, 9, 7).
- Total-size prediction: Kaplan-Meier on accumulated volume with censoring by cancellation; the native mean
  prediction is v_hat_mean = [sum_{u in V_p} f_p(u)]^-1 sum_{u in V_p} u f_p(u), V_p = {u : u > v_r}, v_r the volume
  executed before tranche r, f_p the estimated density of total size given peak p (their section 5.1).
- Square-root impact of a metaorder (Bacry et al.): I(Q) = Y sigma_day sqrt(Q/V_day), with a duration factor
  1/T^gamma, gamma ~= 0.25, and a transient decay with exponent 0.5-0.8 after execution (their abstract).

##### 7.3 Worked example

Assumptions: a native ZM iceberg bid is detected after 40 contracts executed (illustrative); the fitted
Kaplan-Meier mean predicts a total of 120 (illustrative); Y = 1; sigma_day from the random walk over the 290-minute
day session = 3.15 x sqrt(290) = 3.15 x 17.03 = 53.64 ticks; V_day = 36,690 (ADV). If ALL of the iceberg were
informed and its impact permanent, the extra impact still to come is 53.64 x (sqrt(120/36,690) - sqrt(40/36,690)) =
53.64 x (0.05719 - 0.03302) = 1.30 ticks (M1_examples2.out F1). That is below the 1.59-tick hurdle in the most
favourable case, before the Frey-Sandas finding (liquidity, not information) and Bacry's transient decay cut it
further. Check: the impact of a 1,000-lot metaorder by the same formula is 53.64 x 0.1651 = 8.86 ticks, i.e. a
quarter of a typical day's 96-tick range (A0), a plausible order of magnitude.
[MathReview B-1 (lead: accepted): 8.86/96 = 0.092, so 8.86 ticks is under a tenth (9.2%) of the 96-tick median range, not a quarter; the "plausible order of magnitude" conclusion survives.]

##### 7.4 Data (owned)

ZM MBO only: order IDs, modify actions after fills, and trade sizes per order are needed. Whether Databento's CME
MBO preserves the native-iceberg modify sequence and trade-summary sizes exactly as Zotikov and Antonov describe
for the CME feed is [unverified] here and belongs to DataFacts. ZS and ZL MBP-1 cannot see icebergs (no order IDs).

##### 7.5 Leakage traps and tests

1. Labeling an order "iceberg" or "large" using its total executed size or its final fraction executed (known
   only when it dies). Frey and Sandas' impact result is conditional on "the fraction of the iceberg order that is
   eventually executed", an ex-post quantity. Test: the iceberg flag and predicted total at time t use only
   messages up to t (future-scramble invariance); log the detection timestamp and assert label start > it.
2. Fitting the Kaplan-Meier total-size model on the whole sample. Test: fit per training fold.
3. Survivorship: only icebergs that lived long enough to be detected enter the sample; the label must be measured
   from detection time, not from the iceberg's first tranche. Test: assert label_start >= detection time.

##### 7.6 Compute

One extra hash map (order ID to state) in the book rebuild; the Kaplan-Meier fit is seconds.

##### 7.7 Verdict

MAYBE as a conditioner (an "absorption at level L" flag and its predicted remaining size, used to condition
families 5 and 7: a sweep INTO a live iceberg is more likely to reverse); SKIP as a direction source (3.3 iii,
7.3). The synthetic-iceberg heuristic adds frozen parameters (time window after a fill, size match rule) and
false positives; leave it out unless the lead wants it as one counted variant.

##### 7.8 Evidence table (f)

| Claim | Source | Verbatim quote | File |
|---|---|---|---|
| Native CME icebergs keep order ID; trades can exceed display | Zotikov and Antonov (arXiv 1909.09495) | "All new tranches are submitted as modifications of the initial order; this means that the original order ID is preserved throughout the whole lifetime of the iceberg. Additionally, trades against these orders may sometimes be larger in volume than the current resting size, as indicated by trade summary messages." | zotikov_antonov_cme_iceberg.txt |
| Synthetic icebergs only heuristically detectable | Zotikov and Antonov | "Synthetic icebergs, on the other hand, being identical to non-iceberg orders in how they are processed by the exchange, can only be detected heuristically" | same |
| Their data: one week of ES | Zotikov and Antonov | "an almost week-long full order depth (FOD) LOB log of a September E-Mini S&P 500 futures contract" (as rendered across lines) | same |
| Iceberg impact consistent with liquidity, conditional on eventual execution | Frey and Sandas (CFR WP 09-06) | "the observed price impact of an iceberg order of a given size depends critically on the fraction of the iceberg order that is eventually executed. Together this evidence supports the liquidity-based explanation." | frey_sandas_2009_iceberg_cfr.txt |
| Detected icebergs attract market orders | Frey and Sandas | "We find that detected iceberg orders are more likely to attract market orders that undetected iceberg orders" (sic) | same |
| Metaorder impact transient; size not anticipated | Bacry, Iuga, Lasnier, Lehalle (arXiv 1412.0217) | "We observe a power-law for the transient impact with an exponent between 0.5 (for long metaorders) and 0.8 (for shorter ones). Moreover we show that the market does not anticipate the size of the meta-orders." | bacry_etal_2015_metaorder_lifecycle.txt |
| Square-root and duration factor | Bacry et al. | "we confirm a square root temporary impact in the daily participation, and we shed light on a duration factor in 1/T γ with γ ≃ 0.25" | same |

#### 8. (g) VPIN and its critiques

##### 8.1 Core idea

VPIN measures the average absolute buy-sell imbalance over volume buckets, as a real-time proxy for "toxic" flow.
It is UNSIGNED by construction (absolute imbalance), so it carries no direction; its claimed use is to forecast
volatility and turmoil. Andersen and Bondarenko show its forecasting content is mostly a mechanical function of
trading intensity, with no incremental power for future volatility once volume and volatility are controlled, and
that its behaviour reverses with the trade-classification method.

##### 8.2 Equations (Easley, Lopez de Prado and O'Hara 2012, RFS version)

- Bulk volume classification (ELO eq. 7): V^B_tau = sum_{i in bucket tau} V_i Z((P_i - P_{i-1})/sigma_DeltaP),
  V^S_tau = V - V^B_tau; V_i volume of time bar i, Z the standard normal CDF, sigma_DeltaP the standard deviation of
  bar price changes.
- VPIN (ELO eq. 9): VPIN = alpha mu / (alpha mu + 2 epsilon) ~= sum_{tau=1}^{n} |V^S_tau - V^B_tau| / (n V), V the
  fixed bucket volume, n the number of buckets ("V equal to one-fiftieth of the average daily volume ... n=50").

##### 8.3 Worked example

V = ADV/50 = 36,690/50 = 733.8, rounded to 734 contracts per bucket. With five illustrative bucket imbalances
|V^S - V^B| = 200, 150, 400, 100, 300 (n = 5 for brevity), VPIN = (200 + 150 + 400 + 100 + 300)/(5 x 734) =
1,150/3,670 = 0.3134. Bulk classification of one 1-minute ZM bar that rose 3 ticks with sigma_DeltaP = 3.15 ticks:
buy share = Z(3/3.15) = Z(0.952) = 0.8295, so 82.95% of the bar's volume is booked as buys although the MBO data
give the true aggressor of every trade. Check: 1,150/3,670 = 0.31335. In ZM the bulk rule is unnecessary and adds
error; with MBO aggressor flags, an exact VPIN is computable.

##### 8.4 Data (owned)

ZM MBO trades with aggressor side (exact V^B, V^S); ZS, ZL MBP-1 the same. Volume buckets of a frozen size.

##### 8.5 Leakage traps and tests

1. Bucket size from the full-sample average daily volume (ELO: "1/50th of the average daily volume in our sample
   period"). Test: bucket size from a trailing window (for example the previous 20 sessions) only;
   future-scramble invariance.
2. Percentile thresholds from the full-sample CDF (ELO: "We use the entire sample period to determine the
   cumulative distribution function of the estimated parameters"). Test: CDF from training folds only.
3. Volume-clock features joined to a time-clock label: the bucket that is "complete" at time t may close after t.
   Test: a bucket's value is usable only from the ts_recv of its closing trade.
4. Benchmark omission (Andersen and Bondarenko): any VPIN feature must be compared with the same model using
   trailing volume and trailing |return| instead. Test: the protocol includes that benchmark as the
   comparison, not as an extra trial.

##### 8.6 Compute

Trivial.

##### 8.7 Verdict

SKIP for direction (unsigned). At most MAYBE as a regime conditioner, and then only if it beats the
volume-and-volatility benchmark (8.5 test 4); since AB find no incremental volatility power, the expected value of
adding it is low, and it costs a frozen choice of (V, n).

##### 8.8 Evidence table (g)

| Claim | Source | Verbatim quote | File |
|---|---|---|---|
| Bulk classification formula | ELO (2012 RFS, NYU-hosted copy) eq. 7 | "Z is the CDF of the standard normal distribution and 𝜎∆𝑃 is the estimate of the standard derivation of price changes between time bars" | elo_2012_vpin_rfs_nyu.txt |
| Bucket and window choice | ELO | "we focus on V equal to one-fiftieth of the average daily volume. If we then choose n=50, we will calculate the VPIN metric over 50 buckets" | same |
| Full-sample bucket size and CDF | ELO | "We use a bucket size equal to 1/50th of the average daily volume in our sample period (V)" and "We use the entire sample period to determine the cumulative distribution function of the estimated parameters." | same |
| VPIN poor volatility predictor; mechanical with intensity | Andersen and Bondarenko (CREATES RP 2011-50, JFM 2014) abstract | "it is a poor predictor of short run volatility, that it did not reach an all-time high prior, but rather after, the flash crash, and that its predictive content is due primarily to a mechanical relation with the underlying trading intensity" | andersen_bondarenko_2014_vpin_flash_crash.txt |
| No incremental power after controls; classification dependence | Andersen and Bondarenko reply (CREATES RP 2013-42) | "Doing so, we find no evidence of incremental predictive power of VPIN for future volatility." and "the properties of VPIN are strongly dependent on the underlying trade classification" | andersen_bondarenko_2013_reply.txt |
| Counterpoint: VPIN top out-of-sample feature for sign of spread or volatility change, 87 futures, one week | ELOPZ (2019) | "out-of-sample prediction results show that VPIN is the most important predictor for five variables" | elopz_2019_microstructure_machine_age_nber.txt |

#### 9. Planner families 5 and 7 (method side), and the grain forward-OFI evidence

##### 9.1 Family 5: aftermath of non-news jumps and liquidity shocks (sweep and refill) at 1-30 minutes

Core idea. Most price jumps are not news (Joulin et al.: "neither idiosyncratic news nor market wide news can
explain the frequency and amplitude of price jumps") and look like liquidity events: "jumps are followed by
increased volatility, whereas news tend on average to be followed by lower volatility levels", and "most price
jumps are induced by order flow fluctuations close to the point of vanishing liquidity". Marcaccioli, Bouchaud and
Benzaquen show endogenous jumps are preceded by "progressively accelerating growth of volatility", and that the
volatility profile alone classifies events as endogenous or exogenous "without relying on the news feed" (a
volatility result, not a sign result). The one directional, minutes-scale, grain-inclusive measurement is the drift
burst study of Christensen, Oomen and Renò: short-lived explosive trends occur across futures, "the majority of them
are accompanied by subsequent price reversion", and in CBOT corn (ZC), day session 08:30-13:20 CT, 2012-2017, 97
bursts at |T| > 4.0 give a 5-minute reversal slope b = -0.20 (t = -8.25), R2 = 41.5%, 76.3% reversals (Table 4).

Equations (CORe eqs. 35-36): R-_j = X_{t_j} - X_{t_j - 5m}, R+_j = X_{t_j + 5m} - X_{t_j}, X the log mid, t_j the
burst time; R+_j = a + b R-_j + e_j. The test statistic uses a left-sided exponential kernel K(x) = exp(-|x|),
x <= 0, a 5-minute drift bandwidth and a 25-minute volatility bandwidth, on a 5-second grid (their section 5.2).

Worked example. Assume ZM has ZC's burst rate (an assumption; ZM is a different market). Over the discovery window
(39 months, about 3.25 x 252 = 819 trade dates) that is 97/1528 x 819 = 52.0 events at |T| > 4.0, or 29/1528 x 819
= 15.5 at |T| > 4.5. A pre-burst move of 15 ticks over 5 minutes (15/7.044 = 2.13 sigma_5m) and b = -0.20 imply an
expected 5-minute post move of -0.20 x 15 = -3.0 ticks, or 3.0 - 1.59 = 1.41 ticks net of the taker hurdle; the
break-even pre-burst move is 1.59/0.20 = 7.95 ticks (15.9 ticks if the true b is -0.10). Power: with 52 events, a
t-statistic of 3.0 on the mean net post-move needs mean/sd >= 3/sqrt(52) = 0.416. Check: 0.416 x 7.21 = 3.0.
[MathReview B-3 (lead: accepted): 0.416 is the realised-t condition, not a power statement; 80% power at t = 3 needs mean/sd >= (3 + 0.8416)/sqrt(52) = 0.533, and at 15.5 events (|T| > 4.5) 3/sqrt(15.5) = 0.762 realised and 0.976 at 80% power. Relabel as "realised t" or give the power number; the verdict's sentence "statistical power ... is the binding constraint" is strengthened, not weakened.]

The trap that decides the family. CORe count "at most one drift burst ... over any five-minute window at which the
test statistic attains a local extremum and exceeds a set critical value". A local extremum is known only after the
statistic has turned, i.e. after the drift has stopped; conditioning R+ on the extremum time selects the moment the
trend ended, which biases b toward reversal. Their test statistic is real-time (left-sided kernel, chosen "to allow
for real-time updating"), but their event time is not. A tradable protocol must time the entry at a realizable
point: the first 5-second grid time at which |T| crosses the threshold, or the first time |T| has fallen a frozen
margin below its running maximum (plus the latency delay); the published b and R2 must be expected to shrink.
Test: compute the entry time from the stream truncated at that time (future-scramble invariance) and log the
distance between realizable entry and CORe's extremum time.

Data. ZM MBO (mid on a 5-second grid, plus sweep/refill and iceberg conditioners from sections 6-7); ZS and ZL
MBP-1 for "is the burst complex-wide or ZM-only" (an endogenous ZM-only burst is the liquidity case).
Compute: the drift-burst statistic is two kernel-weighted sums per 5-second step: about 819 days x 23 h x 720
steps = 13.6 million evaluations, minutes on one core.
Verdict: USE as a candidate event family (one frozen detector, one frozen entry rule, one label horizon set), with
the realizable-time correction mandatory and the expected sample of about 15-52 events stated up front: the
statistical power, not the mechanism, is the binding constraint. Conditioners from sections 3, 6 and 7 (sign
imbalance with no price move, refill ratio, live iceberg at the level) are where order flow earns its place.

##### 9.2 Family 7: MBO order-flow imbalance, aggressive cancellations and queue features as conditioners only

The evidence in sections 2-8 supports the planner's "conditioners only": forward order-flow predictability is
negative out of sample at 1 minute in the best equity study (CCZ Table 8), gone by 30 minutes in CRS, about 12 s
in ZM by the KTW rule (2.3 iv), priced away for sign persistence (3.3 ii), bounded at 0.5 tick for the microprice
(5.3), and unsigned for VPIN (8.1). Recommended frozen conditioner set (lead's decision; listed for convenience,
each computed at one frozen window): ZM best-level OFI and integrated OFI over the last 1 and 5 minutes; ZS and ZL
best-level OFI over the last 1 and 5 minutes; trade-sign imbalance over the last 5 minutes; refill ratio R(6 s)
after the last sweep; a live-native-iceberg flag at the best levels; a trailing Kyle lambda. None is a separate
configuration; all enter one frozen model, so N grows by the model, not by the feature count.

##### 9.3 Forward OFI evidence in grains (planner pointer: "no forward-looking OFI evidence exists for grains")

Two abstracts state forward predictability from order imbalance in soy-complex or CBOT grain futures, against the
planner's wording:
- Volkenand, Filler and Odening (2018, Agricultural Finance Review), CME best bid and offer data for corn, wheat,
  soy, live cattle and lean hogs, March 2008 and March 2016: "For some contracts, returns can be predicted using
  lagged order imbalance. This offers the opportunity to derive profitable trading strategies." [abstract only]
- Jin, Kearney, Li and Yang (2023, International Journal of Finance & Economics), Chinese soybean meal futures
  (Dalian): "while both OFI and TI are shown to predict future price changes, this predictability diminishes over
  longer measure and price change frequency horizons." [abstract only]
Neither full text was read (Hull repository: Cloudflare challenge, and robots.txt disallows ClaudeBot; Emerald
full-text page: one curl returned a Cloudflare "Just a moment..." challenge, no further routes tried; section 11), so the horizons, the out-of-sample
design and any cost treatment are unknown. Ma and Serra's abstract frames its result as contribution to "price
discovery" by order types (a contemporaneous decomposition), which supports the first half of the planner's
sentence. Net: forward OFI evidence for grains EXISTS at abstract level, is short-lived where described, and has
no verified after-cost result.

##### 9.4 Evidence table (families 5 and 7, grain OFI)

| Claim | Source | Verbatim quote | File |
|---|---|---|---|
| Jumps not explained by news; volatility after jumps rises | Joulin, Lefevre, Grunberg, Bouchaud (arXiv 0803.1769) | "neither idiosyncratic news nor market wide news can explain the frequency and amplitude of price jumps" and "jumps are followed by increased volatility, whereas news tend on average to be followed by lower volatility levels" | joulin_etal_2008_jumps.txt |
| Jumps from vanishing liquidity | Joulin et al. | "We conjecture that most price jumps are induced by order flow fluctuations close to the point of vanishing liquidity." | same |
| Endogenous vs exogenous volatility profiles | Marcaccioli, Bouchaud, Benzaquen (arXiv 2106.07040) | "endogenous price jumps are characterized by progressively accelerating growth of volatility" and "classify large events into endogenous and exogenous dynamical classes, without relying on the news feed" | marcaccioli_bouchaud_benzaquen_2022_jumps.txt |
| Drift bursts common, mostly reversed | Christensen, Oomen, Renò, "The drift burst hypothesis" (arXiv 2601.08974v2, paper dated November 2020) | "Drift bursts occur once a week on average, and the majority of them are accompanied by subsequent price reversion and can thus be regarded as “ﬂash crashes.”" | christensen_oomen_reno_drift_burst.txt |
| ZC sample and session | CORe Table 2 note | "the sample period is January 2012 – December 2017 for all contracts, except ES" and "except for ZC where the interval is restricted to 08:30 – 13:20 Chicago time" | same |
| ZC counts | CORe Table 3 | "ZC Corn 1.15 1.13 2.9 97 29 15 5 2" (counts at |T| > 4.0, 4.5, 5.0, 5.5, 6.0) | same |
| ZC reversal regression | CORe Table 4, Panel A | "ZC 97 −0.20 41.5% 76.3% 87 −0.21 43.0% 77.0%" with t "(−8.25) (−8.05)" | same |
| Reversion regression definition | CORe eqs. 35-36 | "R t+ = a + b R t− + εt j . (36)" and "b < 0 means a drift burst tends to be followed by a retracement of the price" | same |
| Event time at local extremum (look-ahead) | CORe footnote 24 | "we allow for at most one drift burst to be established over any ﬁve-minute window at which the test statistic attains a local extremum and exceeds a set critical value" | same |
| Real-time kernel | CORe footnote 23 | "In practice, a backward-looking kernel is preferred to allow for real-time updating." | same |
| Lagged OI predicts some CME ag returns | Volkenand, Filler, Odening (2018 AFR) | "For some contracts, returns can be predicted using lagged order imbalance." [abstract only, IDEAS] | ideas_volkenand_2018.html(.txt) |
| Soybean meal OFI predicts, decays with horizon | Jin, Kearney, Li, Yang (2023 IJFE) | "while both OFI and TI are shown to predict future price changes, this predictability diminishes over longer measure and price change frequency horizons" [abstract only, IDEAS] | ideas_jin_etal_2023.html(.txt) |
| Ma-Serra is a price-discovery study | Ma and Serra (2025 AJAE) | "We examine limit order dynamics and their role in price discovery in the Chicago Mercantile Exchange (CME) corn, soybean, and wheat futures markets from January 2019 to June 2020, using order‐level data." [abstract only, IDEAS] | ideas_ma_serra_2025.html(.txt) |

#### 10. Verdicts in one table (minutes-scale DIRECTIONAL ZM search under V43)

| Measure | Verdict | Role | Main reason |
|---|---|---|---|
| Best-level OFI (ZM, ZS, ZL), lagged 1-5 min | MAYBE | feature in one frozen model | forward R2 = rho^2 x R2_c is small; CCZ 1-min out-of-sample R2 negative; cross-asset lags the only positive forward finding |
| Multi-level / integrated OFI (ZM) | MAYBE (integrated only) | feature | gains are contemporaneous; integrated OFI is one number, MLOFI vector adds parameters |
| Deep order-flow models (KTW) | SKIP | none | effective horizon about two price changes, about 12 s in ZM (2.3 iv) |
| Trade-sign imbalance | SKIP as signal; MAYBE as conditioner | absorption flag | asymmetric liquidity prices sign persistence; extreme imbalance means a pinned price |
| Kyle lambda (trailing) | MAYBE | liquidity-state conditioner | contemporaneous by construction; slope scales as N^-0.25 so the window must be frozen |
| Microprice | SKIP as signal; USE in labels | de-noised mid for labels and entries | martingale, bounded at 0.5 tick in a 1-tick book |
| Cancellation / refill rates, resiliency | MAYBE | family-5 conditioner | mechanism documented contemporaneously; no forward futures evidence |
| Iceberg / large-order detection | MAYBE | absorption-level flag | impact is liquidity, transient; 1.30-tick best case below 1.59 |
| VPIN | SKIP (direction) | at most regime flag vs benchmark | unsigned; no incremental volatility power after controls |
| Drift-burst aftermath (family 5) | USE | candidate event family | ZC b = -0.20, R2 41.5% published, but event time has look-ahead; 15-52 ZM events expected |

#### 11. Planner pointers (method side; R3b_microstructure owns the grain papers' numbers)

| Planner claim | Status | Evidence |
|---|---|---|
| Ma and Serra (AJAE 2025): "This is contemporaneous" | PARTLY VERIFIED | Abstract (IDEAS) frames the study as the "role in price discovery" of order types, a contemporaneous decomposition; full text not read (Wiley terms; Cloudflare), so the method detail and the 27-30% / 56% shares are not checked here (R3b's item). |
| "no forward-looking OFI evidence exists for grains" | REFUTED as worded (abstract level) | Volkenand, Filler and Odening 2018 (CME corn, wheat, soy): "For some contracts, returns can be predicted using lagged order imbalance."; Jin, Kearney, Li and Yang 2023 (Chinese soybean meal): "both OFI and TI are shown to predict future price changes, this predictability diminishes over longer measure and price change frequency horizons". Both abstract only; no after-cost or minutes-horizon result verified. The planner's practical point (no usable forward OFI edge documented) stands. |
| Family 5: aftermath of non-news jumps and liquidity shocks, sweep and refill, 1-30 minutes | PARTLY VERIFIED (mechanism and one grain measurement) | Drift-burst reversal in ZC at 5 minutes, b = -0.20, R2 41.5%, 97 events (CORe Table 4, full text); non-news jumps are liquidity events (Joulin et al.); but the event time is a local extremum (look-ahead), and no source measures sweep-and-refill conditioned forward returns in futures. |
| Family 7: MBO OFI, aggressive cancellations, queue features as conditioners only | VERIFIED (consistent with every forward source read) | CCZ Table 8 negative 1-min out-of-sample R2; CRS "In no more than thirty minutes, order imbalances lose their predictive ability"; KTW horizon "approximately two average price changes" (abstract); asymmetric liquidity (BFL). |

#### 12. Gaps, failures, stopping rule and route log

- Not read in full (abstract or slides only): Kolm, Turiel and Westray 2023 (Wiley; terms forbid automated access;
  SSRN blocked); Stoikov 2018 journal version (closed; slides used, as in E.28); Ma and Serra 2025 (Wiley:
  WebFetch 403, curl Cloudflare); Jin et al. 2023 (Hull repository Cloudflare, robots disallow ClaudeBot);
  Volkenand et al. 2018 (Emerald Cloudflare challenge, one attempt); Wang, Ye and Zhao 2016 (Chinese ag futures,
  daily; known from a search snippet only; the AUT PDF link returned HTML, not the paper).
- Topic stopping rule: (a) 4 full texts (CKS, XGH, CCZ, CRS); (b) 4 (Lillo-Farmer, BGPW, BFL, Patzelt-Bouchaud);
  (c) 3 (Hasbrouck, ELOPZ, Patzelt-Bouchaud); (d) slides only, all that is accessible (same as E.28); (e) 2 full
  texts (Xu et al., Bechler-Ludkovski) plus E.28 2.2, below the 3-source rule: a third forward-resiliency source
  in futures was not found and no extra discovery query was spent on it in this run; (f) 3 (Zotikov-Antonov,
  Frey-Sandas, Bacry et al.); (g) 4 (ELO, AB 2014, AB reply, ELOPZ); family 5: 3 (CORe, Joulin, Marcaccioli). The
  "last 3 discovery queries surfaced nothing new" condition is documented only for the grain forward-OFI question
  (2 queries in this run returned the same three papers); the first run's discovery queries were not logged, so
  for the other topics this condition is unverified.
- Correction to my own first run: M1_examples.py used Chordia-Roll-Subrahmanyam R2 inputs (0.0261, 0.0028, 0.0007)
  that are not in CRS Table 5; M1_examples2.py uses the Table 5 values (3.32%, 0.53%, 0.54%, 0.18%).
- Numerical caveats a reviewer should recheck: the random-walk scaling (A1) for every sigma_h; the KTW 12-second
  translation assumes unit-tick mid steps (half-tick moves and bounce would change it); the drift-burst event
  count assumes ZM's burst rate equals ZC's 2012-2017 day-session rate; BGPW's "Ne ≈ 50" recomputes to 63.7.
- Databento-specific encoding of native-iceberg modifies and trade-summary sizes in CME MBO is unverified here
  (DataFacts).
- WebSearch: 4 calls in this run; no budget notice seen. No Scrapling or Firecrawl used in this run; all fetches
  by curl (arXiv, IDEAS, Imperial) and logged in log.tsv with sha256.

## M2. Lead-lag and cross-asset structure

Source file: reports/stage_e32_briefs/M2_lead_lag.md (sha256 e52f73bcd4d4eaab711aa1e3df038671c4e19ea6502e7254aace8fbabcbd93b3).

### M2_lead_lag: lead-lag and cross-asset structure for asynchronous ZS, ZL and ZM, and how to trade a ZM dislocation

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

#### Bottom line (for the lead)

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

#### (a) Hayashi-Yoshida covariance for asynchronous ticks, and the Epps effect

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

#### (b) Lead-lag via the Hoffmann-Rosenbaum-Yoshida (2013) contrast

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

#### (c) Error-correction and OU models of the board crush

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

#### (d) Half-life estimation: discretisation, small-sample bias, intervals, and by-session/by-hour estimates

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

#### (e) Which leg adjusts: alpha loadings, Gonzalo-Granger weights, Hasbrouck bounds, Putnins ILS

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

#### (f) How to trade a crush dislocation in ZM only

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

#### Planner pointers owned by M2

| Pointer (planner_research_soy_complex.md) | Status | Evidence / what differs |
|---|---|---|
| "One ZM tick moves the crush by 0.22 cents/bu, so a 1 cent/bu crush dislocation is about 4.5 ZM ticks if ZM alone adjusts" (line 20-22) | VERIFIED (arithmetic) | 2.2 c/bu per USD/ton x 0.10 USD/ton = 0.22 c; 1/0.22 = 4.545. Under the Zhou median vector, 1/0.19 = 5.263 per cent of median-vector residual. With a realistic ZM share s_M the move is s_M x 4.545, for example 1.55 ticks at s_M = 0.34 (hypothetical). See (f). |
| "The ratio is 10 ZS : 11 ZM : 9 ZL; Rechner and Poitras used 10:12:9" (lines 17-19) | VERIFIED; refinement added | Rechner and Poitras: "10 soybeans, 12 meal, and 9 oil contracts" from 48 lb of meal. 10:11:9 per Poitras's note on the CME guide (secondary; CME not fetched). 9 ZL gives 10.8 lb/bu, not 11, so the 10:11:9 oil leg is 1.8% short. |
| Zhou, Bagnarosa, Gohin, Pennings and Debie VECM specification (model section only) | VERIFIED | Eq. (17) VECM with Pi = kappa beta'; eq. (19)-(20) state space with H_t handling idle prices as missing data; EM with "the conventional Kalman filter and Kalman smoother", estimated per day. Units of the prices are not stated in the fetched text; (1, -0.11, -0.22) fits ZS in cents and ZL/ZM in ticks [derived]. The smoother is same-day look-ahead if reused for trading (see (c), trap (i)). Empirical numbers belong to R3a_crush. |
| "A crush residual from both the 10:11:9 weights and a causal rolling beta over 5-20 sessions. Estimate the half-life by session and hour, and test early which leg adjusts: if ZM is not the adjusting leg, family 1 dies" (lines 112-115) | PARTLY VERIFIED (method sound; three amendments) | (1) "Adjusting leg" must be quantitative: the break-even share s_M* = 1.59 b_M / (D (1 - 2^-m)) is 0.70 at D = 1 c, m = 1 and 0.35 at D = 2 c. ZM can adjust and the family still die. (2) By-hour half-lives with per-hour demeaning halve the HL (MC: b_hat 0.906 vs true 0.95, HL 7.0 vs 13.5 min). Use the causal mean, Kendall correction and grid-bootstrap CIs. (3) Use alpha, s_M and weak exogeneity, not trivariate IS/CS, which assume one common trend. Also: fix the contract-month map for rolls. |
| "No intraday half-life is published" (line 56) | UNVERIFIED (a negative claim) | I found none in the sources read for this topic (HRY, Huth and Abergel, Zhou model section, Rechner and Poitras, Hu et al., Putnins). Zhou reports no half-life in the sections read. R3a_crush owns the empirical literature search. |
| "ZS/ZL to ZM lead-lag in seconds: a feature only (under 1 tick, and HFT takes it)" (lines 99-100) | PARTLY VERIFIED | Supported by derivation and analogues, not by a ZM-specific source. Pure-shift model: the predictable ZM move left after 0.3 s latency has SD 0.20 ticks (rho 0.6, theta 1 s) to 0.53 ticks (rho 1, theta 2 s), under 1 tick. Huth and Abergel: a market-order strategy "cannot make any profit of this effect because of the bid/ask spread". Shiotani et al.: CME lags of about 5 ms. "HFT takes it" is not directly evidenced for ZM; E.31's adverse-selection asymmetry (context only) is consistent with it. |

#### Search log summary, stopping rule and failures

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

## M3. Labels and sampling

Source file: reports/stage_e32_briefs/M3_labels.md (sha256 d729737751225b9a69f0b0bee0dec01d1a0914a550c7d13d0ae53b4f75e402c7).

### E.32 Part M3: labels and sampling for a minutes-scale directional ZM search, net of costs

Worker: LabelsMath-OpusHigh (Opus 5.5, effort high), 2026-10-27 00:23-PDT start. Brief: the E.32 lead's spawn message,
reports/stage_e32_briefs/READER_BRIEF.md and reports/stage_e28_briefs/READER_RULES.md. Evidence pages and log:
reports/stage_e32_briefs/pages/M3_labels/ (log.tsv). Arithmetic: reports/stage_e32_briefs/work/M3_labels/M3_calc.py,
output M3_calc.out (every number in this file that is not hand-computed below comes from that script; it reads no
market data). Status: all seven topics (a-g), the per-horizon table (f.3) and both planner pointers written; finished
2026-10-27 00:40 PDT. Nothing was trained and no feature, label, return or markout was computed from data. N stays 538.

What this file adds to E.28. E.28 2.7 (methods brief lines 6941-8259) already defines the triple-barrier method
(section 2), meta-labeling (section 3), uniqueness weights and the sequential bootstrap (section 4) and purged CV
(sections 5-6); E.28 2.9 section 8 (lines 10142-10219) defines taker and maker labels for MES. I cite those as
"E.28 2.7 s2" and so on and do not restate them. New here: bar types and the CUSUM event filter on ZM's two sessions
(a); volatility-scaled barriers and first-passage arithmetic that shows what a +-4-6 tick barrier really measures
(b); meta-labeling for a directional primary rule (c); a 15-minute uniqueness example and time-decay weights (d);
the decomposition of the 1.59-tick break-even and the executable-versus-mid label bias (e); the per-horizon
break-even hit rates and their detectability over 39 months (f); and sampling exclusions on the CBOT grain grid (g).

Standing assumptions (used in every worked example, restated where used):
- A1 (random-walk scaling): ZM mid changes are uncorrelated across minutes with constant variance, so
  sigma_h = sigma_1m x sqrt(h), sigma_1m = 3.15 ticks (A0 Table 1: main-session minutes only, last-trade closes
  carried forward, roll minutes dropped; 18% of minutes have zero change). This is false in detail: intraday
  volatility is U-shaped and release minutes are far noisier, and sigma_1m from trade prices carries bid-ask bounce
  (Roll: a 1-tick spread adds up to s^2/2 = 0.5 tick^2 to a variance of 3.15^2 = 9.92 tick^2, about 5%). Check of A1:
  the expected range of a Brownian path over the 290-minute day session is sqrt(8/pi) x sigma x sqrt(T) =
  1.5958 x 3.15 x 17.029 = 85.6 ticks, against A0's median daily range of 96 ticks for the whole trade date
  (overnight included). Same order; A1 is usable for sizing, not for inference.
- A2 (cost): BE = 1.59 ticks per round trip, E.28's mu*_mkt for Topstep x ZM (section e quotes and decomposes it).
- A3 (sessions, CT): overnight 19:00-07:45, day 08:30-13:20 (290 minutes), settlement window 13:14-13:15 (R4_events.md
  section 1.1, from CBOT filings that R4 saved; section g).

---

#### (a) Clock, tick, volume and dollar bars; event-time sampling with the CUSUM filter

##### a.1 Core idea

A bar is one row of the training table. Clock bars sample every fixed minute; tick, volume and dollar bars sample
after a fixed number of trades, contracts or dollars, so busy periods get more rows and quiet ones fewer. An event
filter (the symmetric CUSUM) goes one step further and creates a row only when the cumulative price move since the
last event passes a threshold, so the model is asked to forecast only after something has happened.

##### a.2 Equations

- Clock bars: bar k closes at t_k = t_0 + k x Delta, Delta = 1 minute.
- Tick, volume, dollar bars (definitions as in mlfinpy, `mlfinpy_FinancialDataStructure.rst.txt` lines 18-20:
  "Tick bars, are sampled after a fixed number of ticks have taken place", "Volume bars, are sampled after a fixed
  number of contracts (volume) has been traded", "Dollar bars, are sampled after a fixed monetary amount has been
  traded"). With trades j = 1, 2, ... since the last bar close, sizes v_j and prices p_j, bar k closes at the first
  trade J where sum_{j<=J} 1 >= theta_N (tick), sum_{j<=J} v_j >= theta_V (volume), or
  sum_{j<=J} p_j x m x v_j >= theta_D (dollar; m = 100 short tons for ZM, p in USD per short ton).
- Volume imbalance bars (mlfinpy restating AFML ch. 2, lines 197-221): tick rule b_t = b_{t-1} if Delta p_t = 0,
  else sign(Delta p_t); theta_T = sum_{t=1}^{T} b_t v_t; a bar closes when |theta_T| >= E_0[T] x |2 v^+ - E_0[v_t]|,
  with E_0[T] and the expected signed volume both EWMAs of earlier bars. (The rst text omits the absolute value on
  the right side; AFML's version has it [unverified: book not fetched].)
- Symmetric CUSUM filter (implementation `mlfinpy_src_filters.py` lines 76-86; the docs call it "the Symmetric
  Dynamic/Fixed CUSUM Filter", line 18). With y_t the price change (log return in the code; ticks below) and
  E_{t-1}[y_t] = 0:
      S+_t = max(0, S+_{t-1} + y_t),   S-_t = min(0, S-_{t-1} + y_t),
      event at t if S-_t < -H (then S-_t := 0) or else if S+_t > H (then S+_t := 0).
  Only the side that fired is reset (lines 81-86). H can be a series (a dynamic threshold, line 66), for example
  H_t = kappa x sigma_hat_t computed from trailing data.
- Event-spacing bound (my statement, standard first-passage result): for a driftless random walk with per-minute sd
  sigma, one CUSUM side alone is a random walk reflected at 0, whose mean time to pass H is H^2 / sigma^2. Two sides
  race, so the mean spacing between events is below H^2 / sigma^2.

##### a.3 Worked example on the standard ZM numbers

Volume bars at 1/50 of ADV (the size Easley, Lopez de Prado and O'Hara used on the E-mini: "if we sample every 1/50
of the average daily volume", `easley_lopezdeprado_ohara_2012_volume_clock.txt` lines 854-855).
1. Bar size: theta_V = 36,690 / 50 = 733.8 contracts.
2. Day session: 36,690 x 0.83 = 30,452.7 contracts in 290 minutes, so 30,452.7 / 733.8 = 41.5 bars a day, one per
   290 / 41.5 = 7.0 minutes on average. Using A0's mean main-session volume of 109.2 contracts a minute instead:
   733.8 / 109.2 = 6.7 minutes per bar.
3. Overnight: 36,690 x 0.17 = 6,237.3 contracts, so 6,237.3 / 733.8 = 8.5 bars a night. At A0's overnight mean of
   8.5 contracts a minute a bar takes 733.8 / 8.5 = 86 minutes; at the overnight median of 2 a minute, 367 minutes.
4. Check: 41.5 + 8.5 = 50.0 bars a trade date, which is 36,690 / 733.8 = 50.0 by construction.
Reading: a volume clock gives ZM about 42 day rows and 8 overnight rows a day, against 290 and 765 one-minute rows.
It removes most of the overnight sample automatically, which is the right direction for a thin overnight book, but
at this bar size a 5-minute label is shorter than one bar.

Dollar bars. For a single futures contract with a fixed multiplier and no corporate actions, dollar bars differ from
volume bars only by the price level. The source's two arguments for dollar bars are price appreciation over long
periods and "corporate actions" on shares (`lopezdeprado_2018_10reasons_jpm.txt` lines 216-233); the second does not
apply to ZM and the first only rescales the bar rate by the price ratio over 39 months.

CUSUM toy (in ticks, H = 6; M3_calc.out section "symmetric CUSUM toy"). Changes y = (+2, +1, -1, +3, +1, -2, -3,
-2, +1, -2, 0, +4):
- t1: S+ = 2, S- = 0. t2: S+ = 3. t3: S+ = 2, S- = -1. t4: S+ = 5, S- = min(0, -1 + 3) = 0. t5: S+ = 6 (not > 6).
- t6: S+ = 4, S- = -2. t7: S+ = 1, S- = -5. t8: S+ = max(0, 1 - 2) = 0, S- = -7 < -6: event, S- := 0.
- t9: S+ = 1. t10: S+ = 0, S- = -2. t11: unchanged. t12: S+ = 4, S- = 0. One event, at t8.
Check: S+ touched exactly 6 at t5 and did not fire, because the test is strict (> H, code line 85); the declared
rule must say "strictly greater", or a tie-handling difference changes the event set.
Rate on ZM (A1): H = 6 ticks gives a spacing below 6^2 / 3.15^2 = 36 / 9.9225 = 3.63 minutes; H = 10 gives below
10.08 minutes; H = 15 below 22.7 minutes. A threshold near sigma_h of the label horizon makes events roughly as
frequent as non-overlapping labels.

##### a.4 Data it needs

Trades from ZM MBO (action = trade or fill messages, with size, price and aggressor side; ts_recv for causal
ordering), aggregated to bars inside each session. ZS and ZL MBP-1 carry trades too and give the same bars for
context. Volume clocks need nothing beyond the trade prints; CUSUM can run on a 1-second or 1-minute mid grid built
from the book.

##### a.5 Leakage and look-ahead traps

1. Bar size from full-sample ADV (36,690 is a 2022-11..2023-10 median). Test: compute theta_V from a trailing window
   only, rebuild bars on data truncated at a date D, and assert that every bar closing before D is identical to the
   full-run bars.
2. A label starting inside the bar that produced the features. Test: assert t_{i,0} > bar close time (strictly
   later message) for every row; shift features by one more bar and check no metric jumps.
3. Bars or CUSUM sums carried across the 13:20 close, the 07:45 pause, a roll (instrument_id change) or a halt.
   Test: reset S+, S- and partial bars at every session boundary and instrument change; count bars spanning a boundary
   (must be 0).
4. A dynamic CUSUM threshold H_t that uses same-minute or future volatility. Test: H_t computed from data at or
   before t - 1 minute; recompute with a one-minute extra lag and require identical events except where the
   threshold moves.
5. Prints that are not outright trades. E.31 found 9.1% of aggressor prints carry no aggressor side and 5.5% found no
   displayed quantity at their price (implied liquidity; reports/E.31_RETURN.md section 3.5). Test: tabulate prints
   by side flag and by whether a resting order existed; run bars with and without the unflagged prints.

##### a.6 Compute (ThinkPad, 39 months)

One pass over the trade messages per date. E.31's pass over the same 816 ZM MBO trade dates (book rebuild plus
markouts) took 384 s on 4 workers; bars and CUSUM are lighter. Minutes in total; memory per date well under 1 GB.

##### a.7 Verdict for a minutes-scale directional ZM search under V43

- Clock bars (1 minute) as the feature and label grid: USE. Horizons, the prop account's daily rules and the
  release calendar are all in clock time; purging and embargo are simplest on a clock grid.
- CUSUM (or another declared event filter) to choose label start times: USE as one declared sampling variant per
  family; each threshold kappa counts as a configuration in N.
- Volume bars: MAYBE, only as a declared robustness variant (one configuration). Their stated advantages are
  statistical ("a partial recovery of Normality and the IID assumption", `easley_lopezdeprado_ohara_2012_volume_clock.txt`
  lines 293-297), not predictive; the only controlled test found (a 2026 crypto study, evidence table) reports "No
  systematic relationship between statistical quality and predictability", and a comment on Ane and Geman (2000)
  reports that returns conditioned on trades or volume "are not Gaussian". Activity measures (volume in the last
  N minutes) carry the same information as features.
- Dollar bars: SKIP (no corporate actions; a price-level rescaling of volume bars).
- Imbalance and run bars: SKIP as a sampling scheme; their statistic (signed volume) belongs in M1's feature set.

##### a.8 Evidence table

| Claim | Source (type) | Verbatim quote | File |
|---|---|---|---|
| Time bars oversample quiet periods | Lopez de Prado 2018, JPM (academic/practitioner) | "time bars oversample information during low-activity periods and undersample information during high-activity periods" | lopezdeprado_2018_10reasons_jpm.txt lines 200-202 |
| Volume clock as a subordinated process | same | "We can avoid the two problems described earlier by forming bars as a subordinated process of trading activity" | same, lines 208-209 |
| Dollar-bar rationale includes corporate actions | same | "the number of outstanding shares often changes multiple times over the course of a security's life, as a result of corporate actions" | same, lines 229-231 |
| Volume time gives partial normality | Easley, Lopez de Prado, O'Hara 2012 (academic; third-party PDF copy of the May 2012 version) | "this time transformation removes most intra-session seasonal effects; second, it allows a partial recovery of Normality and the IID assumption" | easley_lopezdeprado_ohara_2012_volume_clock.txt lines 293-295 |
| Their bar size: 1/50 of ADV on the E-mini | same | "The blue line is the equivalent if we sample every 1/50 of the average daily volume" | same, lines 854-855 |
| Volume-conditioned returns are still not normal | Murphy and Izzeldin 2005 (academic working paper) | "returns conditioned by recentered volume or the number of transactions are not normally distributed" | murphy_izzeldin_2005_comment_ane_geman.txt lines 324-325 |
| Bar statistics do not predict forecast quality | Fayyaz et al. 2026, arXiv 2608.26158 (academic preprint; BTCUSDT perpetual, 3-day labels) | "No systematic relationship between statistical quality and predictability. We do not find that any single statistical criterion predicts classifier AUC" | arxiv_2608.26158_info_bars_crypto.txt lines 2304 and 2315-2316 (two-column extraction interleaves the words; also line 2755: "out-of-sample AUC is near-chance (0.50-0.60)") |
| Same study: near-chance AUC for every bar type | same | "All AUC values lie in 0.48-0.60 (near-chance)" (en dash in original) | same, line 2283 (Table V note at line 2127) |
| CUSUM is symmetric and resets on firing | mlfinpy source (practitioner code implementing AFML) | "if s_neg < -thresh: s_neg = 0 ... elif s_pos > thresh: s_pos = 0" | mlfinpy_src_filters.py lines 81-86 |
| CUSUM avoids repeated triggers near a level | mlfinpy docs | "multiple events are not triggered by raw_time_series hovering around a threshold level" | mlfinpy_Filtering.rst.txt line 29 |
| Volume clock helps Normality per the mlfinpy authors | mlfinpy docs (secondary) | "tick, volume, and dollar bars all exhibit a distribution significantly closer to normal - versus standard time bars" | mlfinpy_FinancialDataStructure.rst.txt lines 150-151 |

Stopping rule: the bar-type topic has four full texts read (LdP 2018, Easley et al. 2012, Murphy-Izzeldin 2005,
Fayyaz et al. 2026); Ane and Geman (2000) itself is paywalled (JF 55(5), known from the search snippet and the
comment only [unverified]); arXiv API queries for "dollar bars", "volume bars" and "volume clock" in q-fin surfaced
only 2608.26158.

---

#### (b) Fixed-horizon versus triple-barrier labels with volatility-scaled barriers; labels to the session close

##### b.1 Core idea

A fixed-horizon label scores the trade at t + h whatever happened in between; a triple-barrier label scores it at
the first of a profit target, a stop, or t + h (E.28 2.7 s2 has the definition and a toy path). The barrier width
decides which horizon the label really measures: for a random walk the expected time to reach +-a is a^2/sigma^2,
so a fixed-tick barrier is a fixed-time label in disguise, and only a barrier that scales with sigma x sqrt(h) keeps
the label tied to the declared horizon h. A label "to the session close" is a fixed-horizon label whose horizon
shrinks with the entry time.

##### b.2 Equations

Notation: tick size delta = 0.10 USD per short ton, so prices below are in ticks; A_t, B_t, M_t are best ask, best
bid and mid; L is the order latency; f = 0.528 ticks the round-trip fee; s = side (+1 long, -1 short).

- Fixed horizon, executable (extends E.28 2.9 s8.2 to both sides and to latency):
      R^exec_{t,h}(s=+1) = B_{t+L+h} - A_{t+L} - f,   R^exec_{t,h}(s=-1) = B_{t+L} - A_{t+L+h} - f.
  Mid-to-mid: R^mid_{t,h} = M_{t+h} - M_t. Label y = sign or value of R (section f adds the dead zone).
- Fixed-horizon definition in the source (`lopezdeprado_2018_10reasons_jpm.txt` lines 327-345): y_i = -1 if
  r < -tau, 0 if |r| <= tau, 1 if r > tau, with r_{t_{i,0}, t_{i,0}+h} = p_{t_{i,0}+h} / p_{t_{i,0}} - 1. The source's
  objection: "the same threshold tau is applied regardless of the observed volatility" (lines 346-347).
- Volatility-scaled barriers (my parameterisation of the AFML idea that barriers are "a dynamic function of
  estimated volatility", lines 356-357): for event i with entry price P_i (the executable entry), declared horizon h
  and multiplier kappa,
      a_i = kappa x sigma_hat_i x sqrt(h),
  with sigma_hat_i a per-minute sd estimated from data strictly before t_i (for example an EWMA of 1-minute mid
  changes over the previous 60 day-session minutes; one declared choice). Upper barrier P_i + a_i, lower P_i - a_i,
  vertical t_i + h. Barrier tests are on the executable exit price (the bid for a long, the ask for a short).
[MathReview B-13 (lead: accepted): under this definition an upper-barrier hit for a long means bid_exit >= ask_entry + k, so the k ticks are already net of the spread, and charging BE = 1.59 (which contains the 1-tick spread) on top as in b.3, c.2 and f.2 (original lines 214-216, 295-297, 642) double-counts the spread by 1.0 tick. The protocol must state which applies: either (i) barriers on the mid, cost BE = 1.59: p* = 0.699/0.659/0.6325 (as written), or (ii) barriers on executable prices, cost c_x = 0.59 (fee + residual): p* = (k + 0.59)/(2k) = 0.574/0.559/0.549 at k = 4/5/6 and 0.5121 at k = 24.40; every mixed reading errs conservative, so no verdict changes.]
- First-passage facts for a driftless Brownian path with per-minute sd sigma and symmetric barriers +-a (standard
  results; my statements, not from the fetched sources):
      P(up first) = 1/2;   E[tau] = a^2 / sigma^2 (minutes);
      P(no barrier by h) = (4/pi) x sum_{n>=0} (-1)^n / (2n+1) x exp( -(2n+1)^2 pi^2 sigma^2 h / (8 a^2) ).
  With a = kappa x sigma x sqrt(h) the last expression depends on kappa only: 0.3708 at kappa = 1 and 0.9090 at
  kappa = 2 (M3_calc.out). So at kappa = 1 about 37% of labels end on the vertical barrier and at kappa = 2 about 91%,
  at which point the triple-barrier label is almost a fixed-horizon label.
- Labels to the close: for an entry at minute u of the day session (u in [0, 290)), h(u) = T_close - u. With A1,
  sigma_{h(u)} = sigma_1m x sqrt(290 - u). Averaged over a uniform entry time, E[sqrt(290 - u)] = (2/3) sqrt(290), so
  the typical to-close label has sd (2/3) x 3.15 x 17.029 = 35.76 ticks, the same as a fixed 128.9-minute label
  ((2/3)^2 x 290 = 128.9).

##### b.3 Worked example on the standard ZM numbers

1. The planner's +-4 to 6 tick triple barrier (planner pointer 1). With sigma = 3.15 ticks a minute:
   - E[tau] = 4^2 / 9.9225 = 1.61 min; 5^2 / 9.9225 = 2.52 min; 6^2 / 9.9225 = 3.63 min.
   - 95% of paths have hit a barrier by 4.23 min (k = 4), 6.61 min (k = 5) and 9.52 min (k = 6) (M3_calc.out,
     bisection on the series above).
   - So a +-5-tick label with a 60-minute vertical barrier is in practice a 2-to-7-minute label; the vertical
     barrier almost never binds. It cannot stand in for the 15-240-minute horizons in the same label set.
   - Break-even hit rate with exits at the barriers and cost BE = 1.59: win k - 1.59, loss -(k + 1.59), so
     p* = (k + 1.59) / (2k): k = 4: 5.59 / 8 = 0.699; k = 5: 6.59 / 10 = 0.659; k = 6: 7.59 / 12 = 0.6325. Check
     (k = 5): 0.659 x 3.41 - 0.341 x 6.59 = 2.247 - 2.247 = 0.000.
2. Volatility-scaled barrier for h = 60 min, kappa = 1: a = 1 x 3.15 x sqrt(60) = 3.15 x 7.746 = 24.40 ticks.
   p* = 1/2 + 1.59 / (2 x 24.40) = 0.5 + 0.0326 = 0.5326; 37% of such labels end at the vertical barrier.
3. Fixed-horizon label at 15 minutes: sigma_15 = 3.15 x 3.873 = 12.20 ticks; the executable label differs from
   the mid label by the spread paid (section e), here about 1 tick, which is 1 / 12.20 = 0.082 sigma.
4. To-close label, entry 08:30: h = 290, sigma = 3.15 x 17.029 = 53.64 ticks; entry 13:00: h = 20,
   sigma = 3.15 x 4.472 = 14.09 ticks. The same model output means 3.8 times less risk at 13:00; the label must be
   scaled by sigma_{h(u)} (or the model trained per entry-time bucket), or late-session rows dominate the loss less
   than their count suggests and early-session rows dominate the P&L.
Check: 53.64 / 14.09 = 3.807 = sqrt(290 / 20) = sqrt(14.5) = 3.808.

##### b.4 Data it needs

ZM MBO rebuilt to the best bid and ask (executable labels need both sides at entry and exit, at the event
resolution of the barrier, plus the book depth for section e); ZS and ZL MBP-1 are not labelled (context only).
sigma_hat from 1-minute mids of the same book. Session and roll calendars (section g).

##### b.5 Leakage and look-ahead traps

1. sigma_hat_i including the label window or the current minute. Test: compute sigma_hat with an extra one-minute
   lag; barriers and labels must change only through the lag, and no feature importance may sit on sigma_hat alone.
2. Ties: a bar where both barriers are inside the bar's high-low range (1-minute bars cannot tell which came first).
   Test: build labels from event-time book updates, not from 1-minute OHLC; count ties under OHLC (report them).
3. Barrier hits measured on mid or last trade while the trade exits at the bid or ask. Test: recompute every label
   with executable prices; report the share of labels whose class changes.
4. To-close labels that end at the 13:14-13:15 settlement VWAP or at 13:20 when the exit price used is the
   settlement price (not tradeable at that price by a market order). Test: the exit is an executable price at a
   declared minute; assert no label uses a settlement field.
5. Barrier multipliers or horizons tuned on the discovery data and reported as one configuration. Test: the
   declared grid in the protocol equals the grid run; N counts each (kappa, h) pair.

##### b.6 Compute

Barrier first-passage per event is a forward scan: O(events x book updates in the window). At one label start per
minute over 816 day sessions there are 816 x 290 = 236,640 starts; a 60-minute window holds on the order of 10^3 to
10^4 book updates, so 10^8 to 10^9 comparisons per (kappa, h) pair. Vectorised per date, minutes on the laptop;
run per date in parallel (at most 8 processes, nice 10).

##### b.7 Verdict

- Fixed-horizon executable labels at the declared horizons: USE (the primary target; they map one-to-one to a trade
  that holds h minutes).
- Triple barrier with kappa x sigma_hat x sqrt(h) barriers: MAYBE, one declared kappa (for example 1) per horizon
  as a secondary target, counted in N. Its advantage is the realism of the exit, not prediction (E.28 2.7 s2.8 found
  no head-to-head test against fixed horizons, and none was found here).
- Fixed +-4-6 tick barriers: SKIP as a multi-horizon label. They measure a 2-7-minute move and need a 63-70% hit
  rate; if kept, they belong to the 1-5-minute family only.
- To the close: USE as one label, with the exit at a declared executable minute before the settlement window
  (section g), and the target scaled by sigma_{h(u)}.

##### b.8 Evidence table

| Claim | Source | Verbatim quote | File |
|---|---|---|---|
| Fixed-horizon threshold ignores volatility | Lopez de Prado 2018 (JPM) | "the same threshold 𝜏 is applied regardless of the observed volatility" | lopezdeprado_2018_10reasons_jpm.txt lines 346-347 |
| Barriers scale with volatility | same | "which are a dynamic function of estimated volatility (whether realized or implied)" | same, lines 356-357 |
| Vertical barrier can be activity-based | same | "The third barrier is defined in terms of number of bars elapsed since the position was taken (an activity-based, not fixed-time expiration limit)" | same, lines 358-360 |
| Implementations label on close prices | mlfinpy source | "cum_returns = (closing_prices / close[loc] - 1) * events_.at[loc, \"side\"]  # Path returns" | mlfinpy_src_labeling.py line 72 |
| First-passage formulas | standard Brownian-motion results | [no fetched source; my statement, checked numerically in M3_calc.py] | - |

---

#### (c) Meta-labeling, and when it helps

##### c.1 Core idea

A fixed primary rule picks the side (for a directional search: follow the post-release move, fade a crush-residual
gap, follow a CUSUM break); a secondary classifier, trained on the primary's own past events, decides act or pass
and possibly the size. E.28 2.7 s3 gives the definitions, the precision-to-P&L link and the evidence, and finds no
independent cost-inclusive test. What is new here is the directional version: the meta-label is the net executable
outcome of the primary's trade, and the break-even precision is the section (f) hit rate.

##### c.2 Equations

- Primary side s_i in {-1, +1} at event time t_i (a declared rule; no fitted parameters, or parameters frozen before
  E.33).
- Meta-label z_i = 1[ R^exec_{t_i,h}(s_i) > 0 ], with R^exec from b.2 (net of fee and spread, after latency).
  mlfinpy's version, for comparison, multiplies the close-price return by the side and sets "bin" to 0 when
  "ret <= 0" (`mlfinpy_src_labeling.py` lines 332-340): gross of costs and on last-trade prices.
- Secondary model p_i = P(z_i = 1 | X_i), act if p_i > c. With symmetric barriers +-k and cost BE, the expected net
  per accepted trade is pi(c)(k - BE) - (1 - pi(c))(k + BE), positive iff precision pi(c) > (k + BE) / (2k)
  (the same p* as b.3; E.28 2.7 s3.2 derives the general form b / (a + b)).
- Trade count: report the number of accepted trades n_acc directly (recall alone does not fix it). The standard
  error on precision is sqrt(pi(1 - pi) / n_eff,acc), with n_eff,acc the uniqueness-adjusted count (section d).

##### c.3 Worked example on the standard ZM numbers

Primary rule: "follow the direction of a CUSUM event (H = 12 ticks) for 15 minutes". Under A1 the rule has no edge,
so its raw precision is 0.50.
1. Barrier at kappa = 1 for h = 15: k = 12.20 ticks. Break-even precision p* = (12.20 + 1.59) / 24.40 = 13.79 / 24.40
   = 0.5652.
2. Events: the one-sided mean spacing H^2 / sigma^2 = 144 / 9.9225 = 14.5 minutes bounds the spacing from above, so
   there are at least about 290 / 14.5 = 20 day-session events a day, about 816 x 20 = 16,320 over the discovery
   window (a lower-end count: two sides racing make events more frequent, and the 15-minute labels then overlap).
3. Suppose the secondary model accepts 20% of events, 3,264, at precision 0.58. Net per trade:
   0.58 x (12.20 - 1.59) - 0.42 x (12.20 + 1.59) = 0.58 x 10.61 - 0.42 x 13.79 = 6.154 - 5.792 = +0.362 ticks.
4. Is 0.58 distinguishable from p* = 0.5652? se = sqrt(0.58 x 0.42 / 3,264) = sqrt(0.2436 / 3,264) =
   sqrt(7.463e-5) = 0.00864; (0.58 - 0.5652) / 0.00864 = 1.71. Not at t > 3, before any multiple-testing deflation.
   To reach t = 3 at the same margin needs n = 0.2436 x (3 / 0.0148)^2 = 0.2436 x 41,088 = 10,009 accepted trades,
   more than half of all events.
Check: 3,264 x 0.362 = 1,182 ticks of total edge over 39 months, about 1.45 ticks per trading day; the per-trade sd is
2 x 12.20 x sqrt(0.58 x 0.42) = 24.40 x 0.4936 = 12.04 ticks, so the per-trade Sharpe is 0.362 / 12.04 = 0.030.

##### c.4 Data it needs

The primary's event list (from ZM MBO and, for cross-market rules, ZS/ZL MBP-1), executable labels (b.2), and
features known at t_i. The secondary's training set is the primary's events only, so its sample is small: plan the
size from the primary's event rate before the run.

##### c.5 Leakage and look-ahead traps

1. Primary parameters tuned on the same data as the secondary. Test: freeze the primary in the protocol; the run
   log shows no fit step for it.
2. The secondary's threshold c chosen on the test fold. Test: c fixed in the protocol or chosen inside the
   training folds only; record the c grid in N.
3. Meta-labels gross of costs or on mid prices (mlfinpy default). Test: assert the label function takes the side,
   fee, latency and bid/ask arrays; a unit test with a one-tick move must return z = 0 for a long.
4. Overlapping primary events counted as independent in the precision test. Test: report n_eff (section d) beside
   n_acc, and use a day-block bootstrap.

##### c.6 Compute

Small: a few thousand to tens of thousands of rows; a shallow GBM fit in seconds (E.28 2.7 s3.7 measured 5.6 s for
10^6 rows x 30 features x 200 trees on 8 threads).

##### c.7 Verdict

MAYBE. It is the right architecture when a family has an economically signed primary rule (post-USDA, crush gap,
open gap), because it keeps the side out of the search and spends the model only on act/pass. It does not create
an edge where the primary has none on any subset, and the arithmetic above shows the binding problem is the count
of accepted trades: precision gains of a few points over p* are not testable at t > 3 with tens of thousands of
events at most. Each threshold c counts in N.

##### c.8 Evidence table

| Claim | Source | Verbatim quote | File |
|---|---|---|---|
| Purpose of the secondary model | Lopez de Prado 2018 (via E.28 2.7 s3) | "The goal of the secondary model is to predict the accuracy of the primary model's prediction" | lopezdeprado_2018_10reasons_jpm.txt lines 387-388 (E.28 2.7 s3.1 cites 389-391 for the same sentence; the copy here shows 387-388) |
| mlfinpy meta-labels are gross close-price returns times side | mlfinpy source | "out_df[\"ret\"] = out_df[\"ret\"] * events_[\"side\"]  # meta-labeling" and "out_df.loc[out_df[\"ret\"] <= 0, \"bin\"] = 0" | mlfinpy_src_labeling.py lines 333 and 340 |
| No new independent cost-inclusive test found | search 2026-10-27: one WebSearch ("meta-labeling futures out-of-sample transaction costs...") and one Crossref query; results were theses, vendor posts and unrelated papers | (null result) | work/M3_labels/M3_crossref_meta.json |

---

#### (d) Sample weights for overlapping labels: average uniqueness, sequential bootstrap, time decay

##### d.1 Core idea

A 15-minute label started every minute shares 14 of its 15 one-minute returns with its neighbour, so 15 rows carry
roughly one row of label information. Average uniqueness measures this per label; weights proportional to it (times
attributed return, optionally times a time-decay factor) stop the model from counting the same move 15 times; the
sequential bootstrap draws bagging samples that overlap less. E.28 2.7 s4 gives the uniqueness and return-attribution
equations and a 6-bar toy; this section adds the minute-sampled ZM case, a closed form for the effective count, time
decay, and the compute limit of the sequential bootstrap.

##### d.2 Equations

- From E.28 2.7 s4.2 (AFML ch. 4 via the JPM summary): 1_{t,i} = 1 if label i uses return bar t; c_t = sum_i 1_{t,i};
  u_bar_i = (sum_t 1_{t,i} / c_t) / (sum_t 1_{t,i}). mlfinpy's statement of concurrency: labels "are concurrent at t
  if they are a function of at least one common return at r_{t-1,t}" (`mlfinpy_Sampling.rst.txt` lines 29-30).
- Effective count, closed form when every span has the same length h (my derivation):
      sum_i u_bar_i = (1/h) sum_i sum_t 1_{t,i} / c_t = (1/h) sum_t (sum_i 1_{t,i}) / c_t = (1/h) x #{t : c_t > 0}.
  So n_eff = (bars covered by at least one label) / h: for minute-sampled labels it equals the number of
  non-overlapping horizons, whatever the sampling step.
- Time decay (AFML 4.7 as implemented, `mlfinpy_src_attribution.py` lines 116-170): let x_i = cumulative average
  uniqueness up to label i in time order and X = x_last. Weights d_i = max(0, a + b x_i) with d_last = 1 and
      b = (1 - C) / X if C >= 0,   b = 1 / ((C + 1) X) if C < 0,   a = 1 - b X.
  The docstring: "``decay`` = 1 means there is no time decay" and "``decay`` < 0 means that the oldes portion c of
  the observations receive zero weight" (lines 136 and 140; "oldes" sic).
- Sequential bootstrap: at each draw, every candidate's probability is proportional to its average uniqueness
  computed together with the labels already drawn (mlfinpy docs lines 141-156; E.28 2.7 s4.2).

##### d.3 Worked example: 15-minute labels sampled every minute in one ZM day session

Setup: 290 one-minute return bars (j = 1..290); a label started at minute t0 uses bars t0+1..t0+15 and must end by
the close, so t0 = 0..275: 276 labels.
1. Concurrency: c_j = min(j, 15, 291 - j) (it rises 1, 2, ..., 15 over the first 15 bars, stays at 15, and falls at
   the end). Maximum 15 (M3_calc.out: "max c 15").
2. Interior label (t0 = 100): every bar has c = 15, so u_bar = (15 x 1/15) / 15 = 1/15 = 0.0667.
3. First label (t0 = 0): bars j = 1..15 have c_j = j, so u_bar = (1/15)(1 + 1/2 + ... + 1/15) = H_15 / 15 =
   3.3182 / 15 = 0.2212. The last label is the mirror image: 0.2212. The second is 0.1590, the third 0.1301.
4. n_eff = sum u_bar = 290 / 15 = 19.33 (closed form above; the script's direct sum gives 19.3333). Mean u_bar =
   19.33 / 276 = 0.0700.
5. Over the 816 trade dates of the discovery window (E.31's count before exclusions): 276 x 816 = 225,216 labels,
   n_eff = 19.333 x 816 = 15,776.
Check: n_eff equals the 19.33 non-overlapping 15-minute windows in 290 minutes, as the closed form says; and 0.0700 is
just above 1/15 = 0.0667 because the edge labels are more unique.
Consequence: sampling every minute multiplies rows by 15 but not information about the label; every standard error
and the power calculation must use about 15,800 (or fewer, after exclusions), not 225,216.

Time decay on four labels with u_bar = (0.5, 0.5, 1, 1), so x = (0.5, 1.0, 2.0, 3.0), X = 3:
- C = 0.5: b = 0.5 / 3 = 0.1667, a = 1 - 0.5 = 0.5; d = (0.5833, 0.6667, 0.8333, 1.0).
- C = -0.25: b = 1 / (0.75 x 3) = 0.4444, a = 1 - 1.3333 = -0.3333; d = (max(0, -0.1111), 0.1111, 0.5556, 1.0) =
  (0, 0.1111, 0.5556, 1.0): the oldest 25% of cumulative uniqueness (x <= 0.75) gets zero weight.
Check: both rows end at 1.0, and the C = 0.5 row starts at a + b x_1 = 0.5 + 0.0833 = 0.5833, above C because x_1 > 0.

##### d.4 Data it needs

Only label spans (from b) on the 1-minute grid and 1-minute mid returns (for return attribution).

##### d.5 Leakage and look-ahead traps

1. Weights computed on the whole sample, including test folds (uniqueness at a fold boundary depends on labels in
   the next fold). Test: compute weights inside each training fold after purging; compare with full-sample weights
   at the boundary rows.
2. Return-attribution weights |sum r / c| use the label's own return, which is the target. As training weights that is
   allowed (AFML), but they must never enter features or model selection metrics. Test: the evaluation metric is
   unweighted or uniqueness-weighted only; assert no attribution weight in the scorer.
3. Time-decay weights tuned on test results (C chosen after looking). Test: C fixed in the protocol; each C counts
   in N.
4. Reporting t-statistics with the raw row count. Test: every reported test lists n_eff beside n.

##### d.6 Compute

Uniqueness: O(labels x span) = 225,216 x 15 = 3.4 x 10^6 operations per horizon; trivial. The sequential bootstrap as
implemented in mlfinpy recomputes uniqueness for every candidate at every draw: about I^2 x h operations for I draws
from I labels, here 225,216^2 x 15 = 7.6 x 10^11, which is not feasible in Python on the laptop. Run it per trade
date (276 labels: 276^2 x 15 = 1.14 x 10^6 per date, 9.3 x 10^8 over 816 dates, minutes) or replace it by a
day-block bootstrap, which removes the cross-day overlap by construction because labels end at the close.

##### d.7 Verdict

- n_eff and HAC or day-block inference: USE (mandatory).
- Uniqueness weights in training: USE as the single declared weighting (cheap; no comparison, so no extra N).
- Time decay: SKIP for discovery (39 months is short; a decay choice is one more configuration with no prior reason
  for a value); revisit only if the lead declares a regime-adaptive variant.
- Sequential bootstrap: SKIP; the day-block bootstrap covers the same need at a fraction of the compute.

##### d.8 Evidence table

| Claim | Source | Verbatim quote | File |
|---|---|---|---|
| Concurrency definition | mlfinpy docs (secondary, citing AFML) | "We say that labels :math:`y_i` and :math:`y_j` are concurrent at :math:`t` if they are a function of at least one common return at :math:`r_{t-1,t}`" | mlfinpy_Sampling.rst.txt lines 29-30 |
| Sequential bootstrap aim | same | "The key idea behind Sequential Bootstrapping is to select samples in such a way that on each iteration we maximize average uniqueness of selected subsamples." | same, lines 77-78 |
| Sequential bootstrap raises uniqueness | Lopez de Prado 2018 (via E.28 2.7 s4) | "can significantly increase the average uniqueness of samples" | lopezdeprado_2018_10reasons_jpm.txt line 490 |
| Time-decay rule | mlfinpy source (AFML 4.7) | "``decay`` = 1 means there is no time decay" ... "``decay`` < 0 means that the oldes portion c of the observations receive zero weight" | mlfinpy_src_attribution.py lines 136-140 |
| Time-decay formula | same | "slope = (1 - decay) / decay_w.iloc[-1]" ... "slope = 1 / ((decay + 1) * decay_w.iloc[-1])" ... "const = 1 - slope * decay_w.iloc[-1]" | same, lines 164-167 |

---

#### (e) The minimum predictable move set by costs; executable-price versus mid-to-mid labels

##### e.1 Core idea

A directional forecast pays three things per round trip: the fee, the spread it crosses (or, for a passive order,
the adverse selection of being filled), and any slippage and latency drift. Its gross expected move must exceed their
sum. The label must be built on the prices the trade would actually get, or the model learns a target that is
systematically about one tick too optimistic per round trip.

##### e.2 The 1.6-tick break-even: the exact row and its decomposition

Exact row (reports/stage_e28_ranking.md line 130, Layer 2 table; header at line 123):

    | Rank | Firm | Code | E | D | R | A | F | P | Rel | L2 | L1 | S | mu*_lim | mu*_mkt | mu10K | cost/attempt | room | gates | u |
    | 6 | topstep | ZM | 2.69 | 2 | 4 | 2 | 1 | 2 | 3 | 2.475 | 2.150 | 2.312 | 0.59 | 1.59 | 0.86 | 49.23 | 2.08 | ok |  |

What mu*_mkt is (reports/stage_e28_ranking_spec.md lines 114-124): the strategy trades "T = 20 round trips per
trading day, 1 contract each", gross P&L per trade is normal with mean mu and "standard deviation sigma_T = sigma_1m
(a one-minute holding scale)"; "Market case c_mkt = F_rt + S_rt, with S_rt the sourced median main-session spread in
ticks (1 if unknown)"; and mu* is "the smallest mu on a 0.01-tick grid from 0 to 4 ticks at which expected net cash
per cycle (all withdrawals minus all fees, a cycle as E.19 defines it) is at least 0".

The Topstep x ZM inputs (reports/stage_e28_briefs/A3_econ.json, record for topstep ZM): F_rt_usd = 5.28,
F_rt_ticks = 0.528, S_rt_ticks = 1.0 with S_rt_status "u" and note "default 1 (u): no sourced median", sigma_T =
3.1522, c_lim_ticks = 0.528, c_mkt_ticks = 1.528, mu_star_mkt = 1.59, cost_per_attempt_usd = 49.23, MLL_usd = 2000,
plan "50K Trading Combine, Standard Path (USD 49/month)", api_monthly_usd = 14.5.

Decomposition of 1.59 ticks per round trip:

| Component | Ticks | Basis |
|---|---|---|
| Fees (commission + NFA + exchange) | 0.528 | 5.28 USD / 10 USD per tick; Topstep page read by E.28 (F_rt_source quote "$5.28") |
| Spread crossing (half a spread at entry, half at exit) | 1.000 | E.28's default S_rt = 1 tick, NOT a sourced or measured ZM spread ("u") |
| Slippage beyond the touch, latency drift | 0 | not in E.28's model |
| Prop-account economics (evaluation and API fees, MLL failures and resets, payout rules) at T = 20, sigma_T = 3.15 | 0.062 | residual: 1.59 - 1.528; part of mu*, not a trading cost; also absorbs the 0.01-tick grid |
| Total (mu*_mkt) | 1.59 | |

Check: c_mkt = 0.528 + 1.000 = 1.528; mu*_lim - c_lim = 0.59 - 0.528 = 0.062, the same residual, as it should be since
both cases share the account economics.

Three caveats the protocol must carry:
1. The spread term is a default. ZM's quoted spread is usually one tick in the day session (E.31's model (a) and (b)
   fills captured +0.34 to +0.36 ticks of half-spread, below the 0.5 a 1-tick market allows; my inference only, not
   a spread measurement), but the mean spread
   paid by a market order, wider at the open, after releases and overnight, is not on disk as a sourced number. E.33
   should measure it from MBO on discovery data as part of the cost model (a cost input, not a signal).
2. Slippage is zero in the 1.59. For a 1-lot, the touch usually holds at least one contract, but E.31 found that
   "5.5% of aggressor prints (3.6% of their volume) found no displayed resting quantity at their price" and "11.8%
   (26.0% of volume) found less than their size" (reports/E.31_RETURN.md section 3.5): depth-conditioned fills
   matter in exactly the minutes a directional signal is likely to fire.
3. mu*_mkt was solved at sigma_T = sigma_1m and 20 trades a day. A 60-minute strategy can hold at most
   floor(290 / 60) = 4 non-overlapping day trades and has per-trade sd 24.4 ticks, so its account economics
   (MLL breach rate, days to payout) differ and the residual 0.062 is not transferable. Rerunning E.28's model at
   (T, sigma_T) = (floor(290/h), sigma_h) per horizon is a lead decision; I did not run it (the brief forbids new
   computation from data, and the model is E.28's code).

##### e.3 Passive entries under V50, and E.31's measured adverse selection

V50 (docs/DECISIONS.md, 2026-10-23): "Limit orders stay allowed as an execution method for a directional signal.
They are not a source of edge in themselves. Any later stage prices its fills under the trade-through rule unless a
firm documents otherwise." Under that rule E.31 measured, for a resting 1-lot at the ZM touch (front month, day
session, 85,568 placements): fill rate 0.515, half-spread captured -0.425 ticks, 10 s markout vs mid -0.545, gross
10 s edge -0.970 [-0.988, -0.950], and -1.234 net of Topstep's fee per fill (E.31_RETURN.md section 3.5).

What this means for a directional entry (my arithmetic on those numbers, not a new statistic):
- A market buy pays half the spread, 0.5 tick at a 1-tick market, relative to the mid at entry.
- A trade-through passive buy that fills sits 0.425 tick worse than the mid at the fill (the half-spread captured is
  negative because the fill only happens after the level trades through), a saving of only 0.5 - 0.425 = 0.075
  tick over the market order; then, unconditionally, the mid moves another 0.545 tick against it within 10 s, and
  48.5% of the orders do not fill.
- For a directional signal the selection is worse than unconditional: the orders that fill are those where price
  moved through the limit, i.e., against the forecast, and the missed fills are the ones where the forecast was right
  at once. A passive entry therefore cannot be costed with the unconditional E.31 number; it must be simulated per
  signal under the trade-through rule, and the comparison "market versus passive entry" is one more configuration.
- Base case for E.33: market-order entry and exit, executable labels (e.4). Passive entry: a declared variant.

##### e.4 Equations: executable versus mid labels, latency and depth

Long trade decided at t, sent at t, arriving at t + L, held h minutes (prices in ticks):
    R^exec = B_{t+L+h} - A_{t+L} - f - slip(q, book_{t+L}) - slip(q, book_{t+L+h}),
    R^mid  = M_{t+h} - M_t.
With A = M + s/2 and B = M - s/2 (s the quoted spread):
    R^exec - R^mid = (M_{t+L+h} - M_{t+h}) - (M_{t+L} - M_t) - (s_{t+L} + s_{t+L+h}) / 2 - f - slip terms.
- Spread bias: E[(s_entry + s_exit)/2] = 1 tick when both spreads are 1 tick; it is deterministic in sign, so a
  model trained on R^mid with a zero threshold labels as "up" every case with 0 < R^mid <= 1.528, all of which lose
  after costs.
- Latency term: (M_{t+L} - M_t) has, under A1, sd sigma_1m x sqrt(L / 60 s): L = 0.3 s gives 3.15 x sqrt(0.005) =
  0.223 tick; L = 1.0 s gives 3.15 x sqrt(1/60) = 0.407 tick (M3_calc.out). Its mean is zero for a signal that
  accrues linearly over h (the fraction lost is L / h: 1 s / 60 s = 1.7% of the edge at h = 1 min, 0.11% at 15 min),
  but it is negative and possibly large for front-loaded signals (sweep and refill, the first minutes after a
  release), where most of the predicted move happens in the first seconds.
- Last-trade labels (mlfinpy's `close`): with a 1-tick spread, last-trade changes carry bid-ask bounce with
  Cov(DeltaP_t, DeltaP_{t-1}) = -s^2/4 = -0.25 tick^2 (Roll's model, standard result [no fetched source]). A feature
  that knows whether the last print hit the bid or the ask then "predicts" the next last-trade change through bounce
  alone, an edge that disappears in R^exec.
- Depth: slip(q, book) = (VWAP of walking q contracts into the opposite side) - touch price; zero for q = 1 unless
  the touch is empty or implied liquidity is not displayed (E.31's 5.5%).

##### e.5 Worked example on the standard ZM numbers

A 15-minute long signal forecasting +2.0 ticks of mid move (0.164 sigma_15; 2.0 / 12.20 = 0.164):
1. Mid-label view: +2.0 > 0, labelled "up", counted as a win.
2. Executable view: 2.0 - 1.0 (spread, 1-tick both ends) - 0.528 (fee) = +0.472 ticks gross of account economics;
   minus the 0.062 residual = +0.41 ticks. Against the E.28 break-even it is 2.0 - 1.59 = +0.41. Same answer.
3. With L = 1 s on a front-loaded signal that realises half its move in the first second (an illustrative
   assumption, not a measurement): the entry is 1.0 tick later, so 2.0 - 1.0 - 1.59 = -0.59 ticks: a winner on mid
   labels, a loser on executable ones.
4. A +1.2-tick forecast is "up" on mid labels and 1.2 - 1.59 = -0.39 net: every such row is a mislabelled loss.
   Under A1 the share of 15-minute mid moves between 0 and +1.528 ticks is Phi(1.528 / 12.20) - 0.5 =
   Phi(0.1252) - 0.5 = 0.5498 - 0.5 = 0.0498, about 5% of all rows (10% counting both signs).
Check: Phi(0.1252) from the series Phi(x) = 0.5 + x/sqrt(2 pi) - x^3/(6 sqrt(2 pi)) = 0.5 + 0.04995 - 0.00013 =
0.5498.

##### e.6 Data it needs

ZM MBO: best bid and ask, the full visible depth for slippage, and order-level arrival times for latency (ts_recv).
ZS and ZL MBP-1 give only the touch; they are features, not traded, so their slippage does not enter.

##### e.7 Leakage and look-ahead traps

1. Entry at the decision-time price (A_t instead of A_{t+L}). Test: rerun labels with L = 0, 0.3 s and 1.0 s; any
   family whose result needs L = 0 is a latency artefact.
2. Mid or last-trade labels in training with executable labels only in the final P&L (or the reverse). Test: one label
   function used everywhere; a unit test on a synthetic book with a 1-tick spread and no mid move must return
   -(1 + 0.528) for a round trip.
3. Spread and depth measured on the full sample and fed back as a per-row cost (the cost model learns from the
   label window). Test: the cost per row uses only the book at t + L and t + L + h, never averages that include
   the test fold.
4. Bounce-driven features (last-print side, last-trade change) scoring well on last-trade labels. Test: compare each
   feature's univariate hit rate on last-trade and on executable labels; drop or flag any feature whose edge vanishes.

##### e.8 Compute

Executable labels need the book at two instants per label: a lookup into the per-date rebuilt book, 236,640 starts x
2 lookups per horizon. Depth walking for q = 1 is a touch check. Minutes in total.

##### e.9 Verdict

USE executable labels (market entry and exit, latency L as a declared parameter with at least two values, depth
from MBO) as the only training and evaluation target. Use mid labels only as a diagnostic, never for selection.
Record the 1.59 as E.28's model value with its three caveats; E.33 should replace the default 1-tick spread by the
measured mean spread a 1-lot market order pays (a cost input).

##### e.10 Evidence table

| Claim | Source | Verbatim quote | File |
|---|---|---|---|
| ZM Topstep break-even 1.59 (market), 0.59 (limit) | E.28 ranking (program record) | "\| 6 \| topstep \| ZM \| 2.69 \| ... \| 0.59 \| 1.59 \| 0.86 \| 49.23 \| 2.08 \| ok \|  \|" | reports/stage_e28_ranking.md line 130 |
| c_mkt = fee + spread, spread 1 if unknown | E.28 ranking spec | "Market case c_mkt = F_rt + S_rt, with S_rt the sourced median main-session spread in ticks (1 if unknown)" | reports/stage_e28_ranking_spec.md lines 118-119 |
| ZM spread was the default | E.28 econ record | "S_rt_note": "default 1 (u): no sourced median" | reports/stage_e28_briefs/A3_econ.json (topstep ZM record) |
| Fee 5.28 USD | E.28 econ record citing the Topstep page | "quote": "$5.28" ... "commission+NFA+exchange; per side = RT/2" | same (F_rt_source) |
| Mid-to-mid labels are not tradable | Lucchese, Pakkanen, Veraart 2024 (academic) | "we focus on mid-to-mid returns, which are not tradable in practice. When considering specific trading applications, one should thus define the return labels appropriately, for example, working with ask-to-bid returns." | lucchese2024_predictability.txt lines 1342-1343 |
| Mid price is not a transaction price | Zhang, Zohren, Roberts 2019 (DeepLOB, academic) | "Although no order can transact exactly at the mid-price" | deeplob_zhang2019.txt line 242 |
| Trade-through passive fills lose about 1 tick in 10 s | E.31 (program measurement) | "10 s edge E_10, mean \| -0.287 [-0.303, -0.273] \| -0.252 [-0.267, -0.239] \| -0.970 [-0.988, -0.950]" | reports/E.31_RETURN.md section 3.5 |
| Limit orders allowed only as execution | V50 (user decision) | "Limit orders stay allowed as an execution method for a directional signal. They are not a source of edge in themselves." | docs/DECISIONS.md (V50 item 2) |
| Implied or undisplayed liquidity | E.31 | "5.5% of aggressor prints (3.6% of their volume) found no displayed resting quantity at their price" | reports/E.31_RETURN.md section 3.5 |
| Latency of 300-1,000 ms | planner claim; no primary source | vendor and blog pages (copier and auto-trader vendors, 5-50 ms claims) are pointers only, not evidence | [unverified] |

---

#### (f) The cost-aware target: dead-zone classification, regression net of cost, the expected-value threshold

##### f.1 Core idea

The target must already contain the cost, so the model is never rewarded for predicting moves too small to trade.
Three equivalent ways: (1) a three-class label whose middle class is "no trade pays", (2) a regression on the net
executable return, traded only when the forecast exceeds zero, (3) a probability of "up" traded only when the implied
expected value clears the cost. Whatever the form, the per-trade net edge required is the same 1.59 ticks at every
horizon; what changes with h is how small that is relative to the noise, and how many independent trades there are
to prove it.

##### f.2 Equations

- Executable three-class label (my construction from b.2/e.4; L and h fixed):
      N_long = B_{t+L+h} - A_{t+L} - c_x,   N_short = B_{t+L} - A_{t+L+h} - c_x,   c_x = f + account residual,
      y = +1 if N_long > 0;  -1 if N_short > 0;  0 otherwise.
  The two cannot both be positive: N_long + N_short = -(s_{t+L} + s_{t+L+h}) - 2 c_x < 0. So the dead zone is not a
  tuned threshold tau: it is the spread plus costs, about |M_{t+L+h} - M_{t+L}| <= 1.59 ticks at 1-tick spreads.
  (Contrast the fixed-tau labels of the source, "0 if |r| <= tau", lopezdeprado_2018_10reasons_jpm.txt lines 327-334,
  and DeepLOB's threshold alpha on smoothed mid changes, deeplob_zhang2019.txt lines 280-283.)
- Regression net of cost: target N_long (or the signed net return for the side chosen); trade long if
  E_hat[M_{t+L+h} - M_{t+L} | X] > BE, short if < -BE. The decision rule is "forecast mid move beyond +-BE".
- Classifier with probability q = P(M_{t+h} > M_t | X) and symmetric magnitudes (A1: the size of the move is
  independent of its sign and of X): expected net of a long = (2q - 1) E|DeltaM_h| - BE, so act iff
      q > q* = 1/2 + BE / (2 E|DeltaM_h|),   E|DeltaM_h| = sigma_h x sqrt(2/pi) = 0.7979 sigma_h.
  For a classifier whose hits are on larger moves than its misses the needed q is lower, and vice versa; the
  calibration of q and of the magnitudes is part of the test, not an assumption to keep.
- Symmetric barriers +-k with all exits on a barrier: q* = (k + BE) / (2k) = 1/2 + BE / (2k).
- Per-trade Sharpe at hit rate p with +-k barriers: SR_trade = ((2p - 1) k - BE) / (2k sqrt(p(1 - p))).
- Detectability over the discovery window (my addition): with n non-overlapping day-session trades,
  n = 816 x floor(290 / h), the sd of an observed hit rate near 0.5 is 0.5 / sqrt(n); a classifier sitting exactly at
  q* shows a t-statistic (q* - 0.5) / (0.5 / sqrt(n)) against "no skill", and needs q* + 3 x 0.5 / sqrt(n) to show
  net skill above break-even at t = 3 (ignoring the deflation that N adds).
[MathReview B-27 (lead: accepted): q* + 3 x 0.5/sqrt(n) is the observed hit rate at which the realised t equals 3, not the true hit rate at which a t = 3 test has a stated power; at 80% power it is q* + (3 + 0.8416) x 0.5/sqrt(n): h = 60: 0.5745 (not 0.5671); h = 120: 0.5764; h = 15: 0.5971. Relabel the f.3 table's last column (original line 656) "observed hit rate giving t = 3" or add the power column, and read reading item 2 (original lines 671-675) the same way; the 60-120 min band is the same either way.]

##### f.3 Worked example: the per-horizon table (A1, BE = 1.59 ticks)

Row h = 15 by hand: sigma_15 = 3.15 x sqrt(15) = 3.15 x 3.8730 = 12.200 ticks; E|DeltaM| = 12.200 x 0.79788 = 9.734;
q* = 0.5 + 1.59 / (2 x 9.734) = 0.5 + 1.59 / 19.468 = 0.5 + 0.0817 = 0.5817; BE / sigma_15 = 1.59 / 12.200 = 0.1303;
barriers at +-sigma_15: q* = 0.5 + 1.59 / 24.40 = 0.5652; n = 816 x floor(290/15) = 816 x 19 = 15,504;
se = 0.5 / 124.5 = 0.00402; t at q* = 0.0817 / 0.00402 = 20.3.

| Horizon h (min) | sigma_h (ticks) | E\|DeltaM_h\| (ticks) | Net edge needed, BE/sigma_h (sd units) | q* fixed horizon, sign classifier | q* fixed horizon at c_mkt = 1.528 | q* barriers +-sigma_h (37% end at vertical) | q* barriers +-2 sigma_h (91% end at vertical) | Non-overlapping day trades in 816 dates | t of a classifier exactly at q* | q needed for net skill at t = 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 3.150 | 2.513 | 0.505 | 0.816 | 0.804 | 0.752 | 0.626 | 236,640 | 307.7 | 0.819 |
| 5 | 7.044 | 5.620 | 0.226 | 0.642 | 0.636 | 0.613 | 0.556 | 47,328 | 61.6 | 0.648 |
| 15 | 12.200 | 9.734 | 0.130 | 0.582 | 0.579 | 0.565 | 0.533 | 15,504 | 20.3 | 0.594 |
| 30 | 17.253 | 13.766 | 0.092 | 0.558 | 0.556 | 0.546 | 0.523 | 7,344 | 9.9 | 0.575 |
| 60 | 24.400 | 19.468 | 0.065 | 0.541 | 0.539 | 0.533 | 0.516 | 3,264 | 4.7 | 0.567 |
| 120 | 34.507 | 27.532 | 0.046 | 0.529 | 0.528 | 0.523 | 0.512 | 1,632 | 2.3 | 0.566 |
| 240 | 48.800 | 38.936 | 0.033 | 0.520 | 0.520 | 0.516 | 0.508 | 816 | 1.2 | 0.573 |
| to close, entry 08:30 (h = 290) | 53.643 | 42.801 | 0.030 | 0.519 | 0.518 | 0.515 | 0.507 | 816 | 1.1 | 0.571 |
| to close, uniform entry (equivalent h = 128.9) | 35.762 | 28.534 | 0.044 | 0.528 | 0.527 | 0.522 | 0.511 | (one per day) | - | - |

Reading the table:
1. The edge required per trade is 1.59 ticks at every horizon. In sd units it falls from 0.51 at 1 minute to 0.03 at
   the close, so the hit rate needed falls from 82% to 52%.
2. The sample to prove it falls faster. A classifier exactly at break-even is invisible (t = 1.1-1.2) at 240 minutes
   and to the close, and only at 60-120 minutes do "needs to be right 54-57% of the time" and "can be shown at t = 3"
   meet. The hit rate needed for a t = 3 demonstration of net skill is lowest, about 0.566-0.567, at 60-120 minutes,
   and rises on both sides (0.594 at 15 minutes, 0.573 at 240), before any multiple-testing deflation and with every
   day-session window traded. A model that trades a subset has fewer trades and needs more.
3. Under A1 a +-5-tick barrier needs q* = 0.659 (b.3); a 5-minute fixed-horizon classifier needs 0.642. They are the
   same short-horizon regime.
4. The dead zone is small at minutes horizons: P(|DeltaM_h| <= 1.59) under A1 is 2 Phi(1.59 / sigma_h) - 1 =
   0.179 at 5 minutes (1.59 / 7.044 = 0.2257; Phi = 0.5893), 0.104 at 15 and 0.052 at 60 (M3_calc.out). Most rows are
   +1 or -1; the dead zone mainly removes the cases where a mid label would be wrong after costs.
5. Per-trade Sharpe at 2 points above break-even with +-5 barriers: p = 0.68, mean (2 x 0.68 - 1) x 5 - 1.59 = 1.80
   - 1.59 = 0.21 ticks, sd 2 x 5 x sqrt(0.68 x 0.32) = 10 x 0.4665 = 4.665 ticks, SR_trade = 0.045 (M3_calc.out).
Check (row 60): 3.15 x 7.746 = 24.40; x 0.79788 = 19.47; 1.59 / 38.94 = 0.0408; q* = 0.5408; n = 816 x 4 = 3,264,
sqrt = 57.13, se = 0.00875, t = 0.0408 / 0.00875 = 4.66; q for t = 3 = 0.5408 + 0.0263 = 0.5671. Matches the table.
Relation to M1 (M1_order_flow.md section 1): M1 states the same 1.59-tick hurdle as an out-of-sample R-squared for a
normal regression forecast (0.0267 at 15 minutes, trading every bar). This table states it as a sign hit rate with
magnitudes independent of the sign. The two rest on different forecast models and are not converted into each other
here; both fall as 1/h (R-squared) or 1/sqrt(h) (excess hit rate) under A1.

Limits of the table: A1 understates noise around the open and releases (where signals fire) and treats ZM overnight
as if it had the day's sigma; the trade count uses all 816 dates before exclusions (E.31 kept 764 day-session dates
after its roll and holiday exclusions, which lowers every n by 6%); and BE's own caveats (e.2) apply.

##### f.4 Data it needs

As e.6. The table itself needs only the brief's standard numbers.

##### f.5 Leakage and look-ahead traps

1. The dead-zone width or q-threshold set from the test-fold cost or class balance. Test: thresholds from the
   protocol (BE, L) only; assert no data-derived threshold.
2. Class rebalancing (up-sampling the minority class, as in the meta-labeling evidence E.28 2.7 s3.8 cites) that
   changes the base rate the threshold assumes. Test: evaluate at the natural class frequencies of the test fold.
3. Choosing the horizon after seeing which one works and reporting it as one trial. Test: every horizon in the
   declared set is run and reported, and N counts all of them.
4. Calibration: q from a GBM is not a probability until calibrated within the training folds. Test: reliability curve
   on purged validation folds; the q > q* rule uses calibrated q.
5. Smoothed labels that contain the past. DeepLOB's second label, l_t = (m+(t) - m-(t)) / m-(t), with m-(t) "the mean
   of the previous k mid-prices" (deeplob_zhang2019.txt lines 251-253, the paper's eqs. 2 and 4), is partly known at t: any feature built from
   the last k mids predicts it without forecasting anything. Test: regress the label on the trailing k-mid mean
   alone; a non-zero out-of-sample fit flags the leak. Use only labels built from prices strictly after t + L.

##### f.6 Compute

Negligible beyond the labels themselves.

##### f.7 Verdict

USE the executable three-class label (dead zone = spread + costs) as the classification target and the net
executable return as the regression target, with the EV rule q > q*(h) or |forecast| > BE. Report hit rate, mean net
ticks per trade and n_eff for each horizon. Given the detectability column, the 60- and 120-minute horizons are where a
modest classifier could be both profitable and provable; the 1- and 5-minute labels need
hit rates (64-82%) that no published order-book model at those horizons reports (E.28 2.9 s8.3 found the same for
MES), and the 240-minute and to-close labels can be profitable but are not provable on 39 months at break-even.

##### f.8 Evidence table

| Claim | Source | Verbatim quote | File |
|---|---|---|---|
| Fixed-threshold three-class label | Lopez de Prado 2018 (JPM) | "where 𝜏 is a pre-defined constant threshold" | lopezdeprado_2018_10reasons_jpm.txt line 334 |
| Threshold labels on mid changes | Zhang, Zohren, Roberts 2019 (DeepLOB) | "The labels are then decided based on a threshold (α) for the percentage change (lt ). If lt > α or lt < −α, we define it as up (+1) or down (−1). For anything else, we consider it as stationary (0)." | deeplob_zhang2019.txt lines 280-283 (left column) |
| Noisy labels cost trades | same | "signals are not consistent here leading to many redundant trading actions thus incurring larger transaction costs" | same, lines 294-295 (left column) |
| q*, detectability, Sharpe link | my derivations under A1 and A2 | - | work/M3_labels/M3_calc.py, M3_calc.out |

---

#### (g) Event-time sampling rules that avoid release windows, rolls, and the open and close

##### g.1 Core idea

A label start (and every minute a label spans) must sit in a market state the strategy could trade in and that the
family is about. Scheduled releases, the 08:30 open after the pre-open, the 13:14-13:15 settlement window, rolls and
limit locks each produce price moves of a different kind; unless a family is about one of them, labels that touch
them mix regimes and inflate both apparent skill and apparent noise. The windows must come from published calendars
fixed in advance, never from the data.

##### g.2 The CBOT grain grid and what is (and is not) an auction

- Sessions (CT), unchanged across both the discovery window and the sealed test window: overnight Sun-Fri 19:00-07:45,
  day Mon-Fri 08:30-13:20, settlement window 13:14-13:15 (R4_events.md section 1.1, from CBOT Submission 15-204 and
  the 2013-03-13 filing that R4 saved). The 2015 filing: the extension lets TAS trade "until 1:15 p.m./CT" and
  "would allow TAS liquidity providers to hedge or trade as needed after 1:15 p.m./CT and not impact or influence the
  1:14-1:15 p.m. CT settlement window" (R4_cftc_cbot_2015_hours_1320.txt lines 88-90).
- Pre-open: a CBOT filing for grain weekly options (options on the same futures) lists "CME Globex Pre-Open: Sunday:
  4:00 p.m. - 7:00 p.m. CT, Monday - Thursday: 4:45 p.m. - 7:00 p.m. CT and Monday - Friday: 8:00 a.m. - 8:30 a.m. CT"
  (R4_cftc_cbot_sub25-045.txt lines 141-147; en dashes in the original). That the futures pre-open has the same
  times is my inference from the shared Globex hours in the same table [unverified for the futures themselves].
- So the "open auction" is the Globex pre-open ending in the 08:30 opening (and the 19:00 opening overnight); its
  matching mechanics (indicative opening price, uncross) come from CME Globex documentation, which this stage may not
  fetch [unverified]. There is no closing auction: the "close" is a one-minute settlement VWAP window (R4 1.1:
  "VWAP of all trades ... in the settlement minute", from the 2012 change), and Globex keeps trading to 13:20.

##### g.3 The rules (a declared set for the lead to adopt or change; each alternative counts in N if compared)

Let W be the set of excluded minutes. A label i with start t_i and span [t_i, t_i + L + h] is kept only if its
whole span lies inside one session of one instrument_id and does not intersect W, unless the family's own event is
the excluded window (then the family declares its own start rule, e.g. "enter at release + 5 minutes").

1. Open: W includes 08:30:00-08:30:00 + D_open (D_open = 5 minutes as a default) and 19:00:00-19:00:00 + D_open.
   Label starts in 08:00-08:30 (pre-open, no executable book) are impossible by construction (no ask and bid to
   trade). Families about the overnight gap at the open (planner family 4) start at 08:30 + D_open by declaration.
2. Close: labels must end by 13:13:00 (one minute before the settlement window); the "to close" label exits at an
   executable price at 13:13:00. A variant ending at 13:19 (after settlement, still trading) is one more
   configuration. Overnight labels end by 07:44.
3. Releases (11:00 CT on WASDE, Crop Production, Grain Stocks, Prospective Plantings, Acreage days; NOPA 11:00 CT;
   R4_events.md section 1.2): W includes [release - 2 minutes, release + D_rel], D_rel = 30 minutes as a default for
   non-event families. Evidence on disk: E.31's passive fills "0-5 minutes after a USDA release" averaged -8.98 ticks
   (68 fills; reports/E.31_RETURN.md section 3.5); Huang (2022) has about 75% of the hour's corn move done by 10
   minutes and Joseph and Garcia (2016) report variance above control for 30-40 minutes on soybeans (as tabulated in
   R4_events.md section 2.1). The planner's "first 1-2 minutes" is shorter than any of these windows (planner
   pointer 2). Event families use release + 5 to 15 minutes as their start (R4 2.4).
4. Overnight releases and closed-market news: Thursday export sales at 07:30 CT fall in the overnight session,
   15 minutes before the pause; Crop Progress at 15:00 CT (if ET is right) falls while closed and is absorbed at
   19:00 (R4 1.2). W includes 07:28-07:44 on Thursdays for overnight labels; day labels are unaffected except
   through the open (rule 1).
5. Rolls: no span crosses an instrument_id change in ZM.v.0; exclude the roll date and the next trade date (E.31's
   precedent: "23 roll days, 20 days after a roll" excluded; E.31_RETURN.md section 3.5). ZS and ZL features are
   read from their own front contracts; a feature roll inside the lookback is flagged and the row dropped.
6. Daily limits: exclude any span during which the ZM book has no bid or no ask (limit-locked or halted); R4 section 3
   covers the limit rule. Count such minutes and report them.
7. Holidays and early closes: use the repo's grain calendar; drop early-close dates entirely (E.31 dropped 4 holidays
   or early closes and 5 late opens).
8. Overnight as a separate stratum: report overnight labels separately and do not pool them with day labels in
   selection (A0: median overnight volume 2 contracts a minute against 71 in the day session).

##### g.4 Worked example on the standard ZM numbers: how many 15-minute label starts survive on a WASDE day

Day session 290 minutes; 15-minute labels need t_i + 15 <= the end of the allowed day, and L is ignored here.
1. Allowed span for label minutes: 08:35 to 13:13 = 278 minutes (open exclusion 5, close cut-off 7 minutes before
   13:20: 290 - 5 - 7 = 278).
2. Release window on a WASDE day: 10:58 to 11:30 = 32 minutes in W.
3. Start minutes on an ordinary day: 278 - 15 + 1 = 264 starts (t_i from 08:35 to 13:13 - 15 = 12:58).
4. On a WASDE day a start t is excluded if [t, t + 15] meets [10:58, 11:30]: t from 10:43 to 11:30, 48 minutes
   (10:43 + 15 = 10:58 touches the window; 11:30 is its last minute). Kept: 264 - 48 = 216 starts.
5. n_eff on the WASDE day: two clean blocks, 08:35-10:58 (143 minutes) and 11:30-13:13 (103 minutes), so
   n_eff = (143 + 103) / 15 = 16.4 non-overlapping windows (section d's closed form, with each block's covered
   bars), against 278 / 15 = 18.5 on an ordinary day.
Check: 216 / 264 = 0.818 of starts and 16.4 / 18.5 = 0.886 of effective information survive; about 15 such release
days a year (R4 2.4) cost 15 x (18.53 - 16.40) = 32 effective 15-minute windows a year, under 0.7% of the year's
roughly 250 x 18.5 = 4,625 (32 / 4,625 = 0.69%).

##### g.5 Data it needs

A release calendar (dates and minutes) built from the publishers' schedules, the repo grain calendar (sessions,
holidays, early closes), ZM.v.0 instrument_id changes from the definitions schema, and the rebuilt book for the
no-bid/no-ask test.

##### g.6 Leakage and look-ahead traps

1. Exclusion windows detected from the data (volatility spikes, volume bursts) instead of the published calendar.
   That makes W depend on the outcome. Test: W is a function of the calendar file and timestamps only; rebuild W
   without loading any price and assert equality.
2. Release dates known only after the fact (rescheduled or cancelled releases, e.g. shutdown years). Test: the
   calendar records the scheduled date as known on the day before; any change is logged with its announcement date.
3. Roll detection from the volume crossover inside the label window (Databento's v.0 is volume-ranked). Test: roll
   dates from the definitions or a fixed calendar rule; compare to v.0's instrument_id switches and report mismatches.
4. Asymmetric exclusions that keep winners (for example dropping only days with a large adverse move). Test: every
   exclusion rule is a declared function of calendar fields; count kept and dropped labels per rule.

##### g.7 Compute

Negligible: interval arithmetic on a few hundred calendar windows.

##### g.8 Verdict

USE all eight rules, with D_open, the close cut-off and D_rel declared once in the protocol (alternatives counted in
N). The sampling of label starts inside the allowed windows: every minute (with n_eff reporting) as the default, and a
CUSUM event filter (section a) as one declared variant per family.

##### g.9 Evidence table

| Claim | Source | Verbatim quote | File |
|---|---|---|---|
| Settlement window 13:14-13:15 CT, trading to 13:20 | CBOT 2015 filing (exchange, CFTC-hosted, saved by R4) | "not impact or influence the 1:14-1:15 p.m. CT settlement window" | R4_events pages: R4_cftc_cbot_2015_hours_1320.txt line 90 |
| Day session 08:30-13:20 | same | "Monday – Friday, 8:30 a.m. – 1:20 p.m. CT" (new hours column) | same, line 78 |
| Grain pre-open times | CBOT Submission 25-045 (grain weekly options, exchange, CFTC-hosted, saved by R4) | "CME Globex Pre-Open: Sunday: 4:00 p.m. – 7:00 p.m. CT Monday – Thursday: 4:45 p.m. – 7:00 p.m. CT and Monday – Friday: 8:00 a.m. – 8:30 a.m. CT" | R4_events pages: R4_cftc_cbot_sub25-045.txt lines 141-144 |
| Release times and stacking | R4_events.md (E.32 worker, sourced there) | "WASDE ... 12:00 p.m. ET \| 11:00 \| day session" | reports/stage_e32_briefs/R4_events.md section 1.2 |
| Post-release passive fills | E.31 (program measurement) | "fills 0-5 minutes after a USDA release -8.98 (68 fills)" | reports/E.31_RETURN.md section 3.5 |
| E.31's exclusion precedent | E.31 | "Exclusions, front month: 52 of 816 dates (23 roll days, 20 days after a roll, 4 holidays or early closes, 5 late opens)" | reports/E.31_RETURN.md section 3.5 |
| Futures pre-open equals options pre-open; opening-match mechanics | - | - | [unverified]; CME documentation not fetched (stage CME rule) |
| CFTC pages were not fetched by M3 | cftc.gov robots.txt | "User-agent: ClaudeBot / Disallow: /" and "Content-Signal: search=yes,ai-train=no,use=reference" | log.tsv (terms decision, 2026-10-27 00:29 PDT) |

---

#### Planner pointers owned by M3 (reports/stage_e32_inputs/planner_research_soy_complex.md lines 110-111 and 123-124)

| Pointer (verbatim) | Status | What the evidence and arithmetic show |
|---|---|---|
| "Labels at 5, 15, 30, 60, 120 and 240 minutes and to the session close, net of 1.6 ticks, plus a triple-barrier label at about +-4-6 ticks." | PARTLY VERIFIED | The 1.6 ticks is E.28's mu*_mkt = 1.59 for Topstep x ZM (ranking line 130), but it is a model value: 0.528 fee + 1.0 default (unsourced) spread + 0.062 account economics, zero slippage, solved at a 1-minute holding scale (e.2). The horizon set is workable; per f.3, the hit rate needed to show net skill at t = 3 is lowest (about 0.566) at 60-120 minutes and higher on both sides (0.594 at 15, 0.648 at 5, 0.573 at 240 minutes); at 240 minutes and to the close a classifier exactly at break-even (about 52%) gives t = 1.1-1.2 on 39 months. The +-4-6 tick triple barrier does not belong with these horizons: under A1 its mean exit time is 1.6-3.6 minutes (95% by 4.2-9.5 minutes) and it needs a 63-70% hit rate (b.3); barriers should scale as kappa x sigma_hat x sqrt(h). "Net of 1.6 ticks" must mean executable labels (buy at the ask, sell at the bid, after latency), not mid labels minus a constant, because the spread part varies by minute. |
| "Market-order execution with depth-conditioned slippage and 300-1,000 ms latency, excluding the first 1-2 minutes after releases." | PARTLY VERIFIED | Market orders as the base case agree with V50 (limit orders are execution only, priced by trade-through; E.31's trade-through fills lose 0.970 ticks gross in 10 s), e.3. Depth-conditioned slippage is supported by E.31's implied-liquidity finding (5.5% of aggressor prints met no displayed quantity) and is computable from ZM MBO (not from ZS/ZL MBP-1), e.4. The 300-1,000 ms latency is UNVERIFIED: no primary source states a TopstepX or ProjectX latency; vendor and blog pages claim 5-50 ms and are pointers only; the program's own note is "tens of milliseconds" network latency to Aurora (E.28 READER_RULES, not a measurement). As a conservative stress range it costs little at minutes horizons (sd 0.22-0.41 ticks; under 2% of a linear 1-minute edge) but matters for front-loaded signals; declare L in {0.3, 1.0} s. The "first 1-2 minutes after releases" exclusion is shorter than the evidence on disk: E.31's 0-5-minute post-USDA bucket averaged -8.98 ticks per passive fill and the literature R4 tabulates has 75% of the move by 10 minutes and elevated variance for 30-60 minutes; g.3 proposes [release - 2, release + 30] for non-event families. |

#### Compute summary (ThinkPad, 39 months)

All label, weight and exclusion work is a few passes over the rebuilt ZM book: minutes per horizon, under 1 GB per
trade date, parallel by date (at most 8 processes, nice 10). The only infeasible item is mlfinpy's sequential
bootstrap on 225,216 labels (about 7.6 x 10^11 operations); per-date sequential bootstrap or a day-block bootstrap
replaces it (d.6). No GPU is needed.

#### Verdicts in one table

| Topic | Verdict | Reason |
|---|---|---|
| 1-minute clock grid for features and labels | USE | horizons, account rules and calendars are clock-based; simplest purging |
| CUSUM event filter for label starts | USE (one declared threshold per family, in N) | conditions on "something happened"; cheap |
| Volume bars | MAYBE (one robustness variant) | statistical gains only; no evidence of predictive gain |
| Dollar, imbalance and run bars | SKIP | no corporate actions; imbalance belongs in features |
| Fixed-horizon executable labels | USE (primary target) | maps one-to-one to the trade |
| Triple barrier at kappa x sigma_hat x sqrt(h) | MAYBE (one kappa, in N) | exit realism; no evidence of predictive gain |
| Fixed +-4-6 tick barriers | SKIP for the multi-horizon set | a 2-7-minute label needing 63-70% hits |
| To-close label | USE, exit 13:13, scaled by sigma_{h(u)} | needs the shortest hit rate (52%) but least provable |
| Meta-labeling | MAYBE (for signed primary rules) | sound architecture, sample-size bound; no independent cost-inclusive evidence |
| Uniqueness weights, n_eff, day-block inference | USE | 15-minute labels sampled each minute carry 1/15 of their row count |
| Time decay, sequential bootstrap | SKIP | an extra configuration without a prior; compute |
| Executable labels with latency and depth | USE (only training and selection target) | mid labels are about 1 tick a round trip too optimistic |
| Dead-zone three-class label and EV threshold | USE | dead zone = spread + costs, not a tuned tau |
| Exclusion rules g.3 (1-8) | USE | calendar-based; declared once |

#### Stopping rule, null results and gaps

- Bar types (a): 4 full texts; last discovery queries (arXiv API for "dollar bars", "volume bars", "volume clock" in
  q-fin; one WebSearch) surfaced nothing beyond those. Ane and Geman (2000) itself not read (paywalled) [unverified].
- Triple barrier versus fixed horizon (b): no head-to-head, cost-inclusive out-of-sample comparison found (as in E.28
  2.7 s2.8); arXiv q-fin "triple barrier" query returned two papers (2404.01866, 2411.12753), both using the label
  without a fixed-horizon control (abstract only for 2404.01866 [unverified beyond the abstract]).
- Meta-labeling (c): no new independent evidence (one WebSearch, one Crossref query, 2026-10-27); E.28's null result
  stands.
- Sample weights (d): no independent evidence that uniqueness weighting improves out-of-sample results (as in E.28
  2.7 s4.8); the effective-count argument is standard and needs none.
- Costs (e): the ZM market-order spread a 1-lot actually pays is not on disk as a sourced number (E.28 used a default);
  Topstep's simulated market-order fill rule (does a market order walk the book, or fill at the touch regardless of
  depth?) was not looked up here [unverified]; it decides whether depth-conditioned slippage applies at all at the
  firm. TopstepX latency: no primary source (5-50 ms vendor claims are pointers only).
- Sessions (g): cftc.gov was not fetched by this worker because its robots.txt disallows ClaudeBot and anthropic-ai
  (logged). Other E.32 workers did fetch CFTC filings; the lead may want to review that against the terms rule.
  Futures pre-open times and the opening-match mechanics are [unverified] (options filing only; CME docs not fetched).
- WebSearch calls used: 4 of 80. No budget notice was seen.
- Every number here assumes A1 (random-walk scaling of sigma_1m = 3.15) and A2 (BE = 1.59); none was computed from
  market data.

## M4. Model families

Source file: reports/stage_e32_briefs/M4_models.md (sha256 93262c1372fd7aa0068920865ba1d9f3b602bb172db92891a8e486f13b565a04).

### E.32 Part M4: model families for a minutes-scale directional ZM search

Worker: ModelsMath-OpusHigh (Opus 5.5, effort high). Started 2026-10-27 00:30 PDT. ROOT M4_models.
Pages and log: `reports/stage_e32_briefs/pages/M4_models/` (log.tsv). Scripts and their outputs:
`reports/stage_e32_briefs/work/M4_models/` (`M4_ess.py/.out`, `M4_examples.py/.out`,
`M4_compute_probe.py/.out`).

Nothing here was computed from market data. The sample-size counts are calendar arithmetic. The compute
numbers come from a timing probe on synthetic random data (seed 20261027) run on this ThinkPad at nice 10
with 8 threads, 00:40:20-00:44:24 PDT. The probe trained nothing on ZM, ZS or ZL. No feature, label or return
was computed.

#### 0. Scope, what was read, and the yardsticks used in every section

**E.28 sections read (by line range) and cited, not repeated:**
- E.28 2.8 (deep LOB models): DeepLOB equations, LOBCAST, Briola et al., Lucchese et al., futures results,
  measured GPU throughput (2.8 section 10.1) and verdicts (2.8 section 12).
- E.28 2.9 (OFI and trees): XGBoost/LightGBM objective, eqs. 2, 4, 5 and 6, the leaf-weight worked example
  (2.9 section 6.3), Aït-Sahalia et al. "trees about equal to LASSO" (2.9 section 6.6), latency decay
  (2.9 section 9).
- E.28 2.5 (Kalman, HMM): the Kalman recursion (Welch-Bishop eqs. 1.9-1.13), the Hamilton filter
  (eqs. 5-12), Baum-Welch, the Viterbi look-ahead trap, measured filter costs (2.5 sections 1.7 and 4.7), and
  the verdict "HMM as a return forecaster (directional): skip" (2.5 section 9).
- E.28 C4.4 (hardware): "a DeepLOB-sized network has about 60k parameters and takes 8 to 34 hours per
  configuration on the RTX 3050".

**E.28's data-size verdict for deep LOB models (E.28 2.8 section 1.3), quoted because the brief asks for it:**
"So 4 months is enough to fit the model (it has only 60k parameters and millions of event samples), but not
enough to show the result is stable across regimes: the test window would be one or two months of one
contract. 12 months allows a 6/3/3 split like the paper's. The binding constraint is independence, not sample
count: successive samples share 99 of 100 input rows and overlapping label windows, so the effective sample
size is closer to the number of non-overlapping horizons than to the number of events." That verdict was
written for event-horizon labels (10 to 100 book events). For minutes-scale labels, section (e) shows the
independent-sample count is smaller again, by orders of magnitude.

**Standard ZM yardsticks (from READER_BRIEF; arithmetic in `M4_examples.out`).** Tick 0.10 USD/short ton,
10.00 USD. sigma_1m = 3.15 ticks. Under a random-walk ASSUMPTION, sigma_h = 3.15 x sqrt(h):
5 min 3.15 x 2.2361 = 7.044 ticks; 15 min 3.15 x 3.8730 = 12.200; 30 min 3.15 x 5.4772 = 17.253;
60 min 3.15 x 7.7460 = 24.400. Market-order hurdle at Topstep: E.28 ranking row 6
(`reports/stage_e28_ranking.md` line 130, "| 6 | topstep | ZM | ... | 0.59 | 1.59 | ..."), column
mu*_mkt = **1.59 ticks** per round trip (the brief's "about 1.6").

**The probability a direction call needs (used in (a) and (c)).** ASSUMPTIONS: the h-minute return r is
normal with mean 0 and standard deviation sigma_h; the model's sign call is independent of |r|; one 1-lot
market round trip costs C = 1.59 ticks. Then E|r| = sigma_h sqrt(2/pi), and a call that is right with
probability p earns (2p - 1) E|r| - C ticks gross of slippage beyond C. Break-even: p* = 1/2 + C / (2 E|r|).
[MathReview D-1 (lead: accepted): 1.59 is not the cost of a round trip but E.28's cycle-EV threshold mu*_mkt at T = 20/day (= 1.528 + 0.062, the 0.062 being the per-trade drift that pays the evaluation and API fees over a cycle at 20 trades a day); the per-round-trip cost is c = 1.528 ticks (c_mkt = F_rt/v + S_rt = 0.528 + 1.00, A3_econ 2.1), as M6 uses, so under this model p*(15 min) = 0.5 + 1.528/(2 x 9.734) = 0.5785, not 0.5817 (also applies to the table below and original line 117).]

| h (min) | sigma_h (ticks) | E\|r\| = 0.79788 sigma_h | p* = 0.5 + 1.59 / (2 E\|r\|) | edge at p = 0.55: 0.10 E\|r\| |
|---|---|---|---|---|
| 1 | 3.150 | 2.513 | 0.8163 | 0.251 |
| 5 | 7.044 | 5.620 | 0.6415 | 0.562 |
| 15 | 12.200 | 9.734 | 0.5817 | 0.973 |
| 30 | 17.253 | 13.766 | 0.5578 | 1.377 |
| 60 | 24.400 | 19.468 | 0.5408 | 1.947 |

Check (h = 15): 1.59 / (2 x 9.734) = 1.59 / 19.468 = 0.0817, so p* = 0.5817. A sanity bound: p* falls like
1/sqrt(h), so going from 15 to 60 minutes (4x) halves the excess: 0.0817 / 2 = 0.0408, and the table has
0.5408. The table shows why the stage's labels sit at 15 to 240 minutes. Below about 5 minutes, no realistic
hit rate pays a market round trip.
[MathReview D-2 (lead: accepted): M6 (A2) and R5 (B2) use a Gaussian model under which the edge for a hit rate p is f = sigma Phi^{-1}(p) = sqrt(2 pi) sigma (p - 1/2) + O((p-1/2)^3) = 2.5066 sigma (p - 1/2), whereas this model gives (2p - 1) sigma sqrt(2/pi) = 1.5958 sigma (p - 1/2), a ratio of exactly pi/2 = 1.571, so the same 15-minute Topstep hurdle is p* = 0.5817 here but 0.5498 in M6 (A2) and 0.552 in R5. State both models in section 0 with the pi/2 factor, say which one E.33 will use, and (better) freeze the trade rule in ticks of the calibrated map p -> E[G | p] measured on held-out folds, as M6 (A2) already requires, so no hit-rate threshold enters the protocol (table for both conventions in d_m4.out, section 0; also applies to a.3 item 3, original lines 115-118).]

#### (a) Regularised linear and logistic models (L1, L2, elastic net) and probability calibration

##### a.1 Core idea
A linear score w'x, or a logistic probability sigma(w'x), is fitted with a penalty that shrinks the weights
toward zero. L2 (ridge) shrinks correlated features together, L1 (lasso) sets some exactly to zero, and the
elastic net mixes the two. With a weak, noisy target and a few thousand independent labels (section (e)),
shrinkage is what keeps the out-of-sample forecast from being mostly noise. A directional rule then trades
only when the predicted probability clears the cost hurdle p* (section 0). That requires the probability to be
calibrated, meaning that among cases forecast at 0.58, about 58% go up. That is the second half of this topic.

##### a.2 Equations
Elastic net, linear (Friedman, Hastie and Tibshirani 2010, JSS 33(1), eqs. 1-3; `friedman2010_glmnet_pmc.txt`):

    min_{beta0, beta}  (1/(2N)) sum_{i=1..N} (y_i - beta0 - x_i' beta)^2 + lambda P_alpha(beta)          (1)
    P_alpha(beta) = (1 - alpha) (1/2) ||beta||_2^2 + alpha ||beta||_1
                  = sum_{j=1..p} [ (1/2)(1 - alpha) beta_j^2 + alpha |beta_j| ]                         (2), (3)

- N: number of training rows. x_i: p-vector of features, standardised to mean 0 and mean square 1 (the paper
  assumes "sum_i x_ij = 0, (1/N) sum_i x_ij^2 = 1"). y_i: the label. beta0: intercept. lambda >= 0: overall
  penalty strength. alpha in [0, 1]: the mix, where alpha = 0 is ridge and alpha = 1 is lasso.
- Coordinate update (described in words in the paper: "we compute the simple least-squares coefficient on the
  partial residual, apply soft-thresholding to take care of the lasso contribution to the penalty, and then
  apply a proportional shrinkage for the ridge penalty"; written out here by me, with no equation number):
  beta_j <- S(z_j, lambda alpha) / (1 + lambda (1 - alpha)), where z_j = (1/N) sum_i x_ij r_ij is the
  least-squares coefficient on the partial residual r_ij = y_i - beta0 - sum_{k != j} x_ik beta_k, and
  S(z, g) = sign(z) max(|z| - g, 0) is soft-thresholding.

Penalised logistic (same paper, eqs. 11, 13, 14): Pr(G = 1 | x) = 1 / (1 + exp(-(beta0 + x' beta))), and

    max_{beta0, beta} [ (1/N) sum_i { y_i (beta0 + x_i' beta) - log(1 + exp(beta0 + x_i' beta)) } - lambda P_alpha(beta) ]   (13)-(14)

with y_i = 1 for "up" and 0 otherwise. It is solved by iteratively reweighted least squares around the current
fit (their eqs. 15-16: weights w_i = p_i(1 - p_i), working response z_i = beta0 + x_i'beta + (y_i - p_i)/w_i).
The paper warns about the unpenalised limit: "the saturated logistic regression fit is undefined (parameters
wander off to ±∞ in order to achieve probabilities of 0 or 1)".

Calibration. Platt scaling (Niculescu-Mizil and Caruana 2005, eqs. 1-3;
`niculescu_caruana2005_calibration.pdf`): P(y = 1 | f) = 1 / (1 + exp(A f + B)), with A and B fitted by
maximum likelihood on a separate calibration set (f is the model's raw score). Isotonic regression (their
eq. 6): m_hat = argmin_z sum_i (y_i - z(f_i))^2 over non-decreasing step functions z, solved by
pair-adjacent violators. Temperature scaling for networks (Guo et al. 2017) is Platt scaling with B = 0 on the
logit. Scores used to judge calibration (standard definitions): Brier score BS = (1/n) sum_i (p_i - y_i)^2;
log loss LL = -(1/n) sum_i [y_i log p_i + (1 - y_i) log(1 - p_i)]; expected calibration error
ECE = sum_{m=1..M} (|B_m| / n) |acc(B_m) - conf(B_m)| (Guo et al. 2017, eq. 3), with B_m the m-th bin of
predicted probabilities.

##### a.3 Worked example (arithmetic in `M4_examples.out`)
1. *One elastic-net coordinate step.* Standardised feature j with partial-residual coefficient z_j = 0.04 (in
   label units per feature standard deviation), lambda = 0.02, alpha = 0.5. Soft-threshold:
   S(0.04, 0.02 x 0.5) = S(0.04, 0.01) = 0.04 - 0.01 = 0.03. Ridge shrink: 0.03 / (1 + 0.02 x 0.5) =
   0.03 / 1.01 = **0.0297**. Check: with alpha = 1 (lasso) the result would be 0.04 - 0.02 = 0.02. With
   alpha = 0 (ridge) it would be 0.04 / 1.02 = 0.0392. The elastic net lies between the two, as it should.
2. *Platt scaling a raw score.* A model outputs f = 0.8, and the calibration fit gives A = -2.0, B = 0.1.
   A f + B = -1.6 + 0.1 = -1.5, and p = 1 / (1 + e^-1.5) = 1 / (1 + 0.22313) = **0.8176**.
3. *Why calibration decides trades.* At h = 15 minutes the hurdle is p* = 0.5817 (section 0). If the
   uncalibrated model says 0.60 but the true frequency in that bin is 0.56, the rule trades a call worth
   (2 x 0.56 - 1) x 9.734 - 1.59 = 1.168 - 1.59 = **-0.42 ticks** per round trip, when it believes it earns
   (0.20 x 9.734) - 1.59 = +0.36 ticks. A 4-point calibration error flips the sign of the edge.
4. *How much calibration data.* Niculescu-Mizil and Caruana: "When the calibration set is small (less than
   about 200-1000 cases), Platt Scaling outperforms Isotonic Regression with all nine learning methods." A
   6-month calibration block (about 126 day sessions, 816 x 6/39 = 125.5) holds 126 x 19 = 2,394
   non-overlapping 15-minute day-session labels, or 126 x 4 = 504 at 60 minutes. At 60 minutes that is inside
   the "small" range, so use Platt or none, not isotonic.

##### a.4 Data it needs
A decision grid (every 1 minute, or every 10 s, inside the day session 08:30-13:20 CT and, if declared, the
overnight 19:00-07:45 CT), with each row's features computed only from events stamped before the decision time
plus the latency. Features come from the ZM MBO book (OFI, queue imbalance, signed trade flow, recent ZM mid
returns), ZS and ZL MBP-1 (their recent returns, a crush residual) and definitions (tick size, expiry and roll
dates for the v.0/v.1 switch). The label is the ZM mid (or the executable price) change over h minutes, as a
sign for logistic or as ticks for linear. One model has p of roughly 10 to 60 coefficients.

##### a.5 Leakage and look-ahead traps, each with a test
- *Scaler fitted on all data.* Means and standard deviations for standardisation must come from the training
  block only. **Test (prefix invariance):** rerun the whole pipeline on data truncated at the end of fold k.
  Fold k's predictions must be bit-identical to the full run's.
- *Penalty lambda chosen by random K-fold.* glmnet's default `cv.glmnet` and sklearn's `LogisticRegressionCV`
  shuffle rows into folds. With overlapping h-minute labels on a 1-minute grid, neighbouring rows share up to
  (h-1)/h of their label, so a random fold leaks. The inner folds must be blocked by day, with a purge of h and
  an embargo. Purge mechanics belong to M5a. **Test (day-block null):** permute the labels across whole days,
  which keeps their within-day overlap, and rerun the inner CV. The selected model's inner deviance must not
  beat the intercept-only model by more than its null spread, measured over 20 permutations.
- *Calibrating on training data.* Niculescu-Mizil and Caruana: "If we use the same data set that was used to
  train the model we want to calibrate, we introduce unwanted bias." Fit A and B on a later block that the
  model did not see. **Test:** the ECE on the calibration block must be compared with the ECE on the next
  block, never with itself.
- *Label-threshold or class-weight statistics from the full sample* (for example quantile thresholds as in
  Lucchese et al., E.28 2.8 section 4.4). **Test:** the same prefix-invariance test catches it.
- *Feature timestamp at or after the decision.* **Test:** shift every feature one extra decision step into the
  past. A large drop in validation skill from one step alone flags a feature that peeks at the label window.

##### a.6 Compute on the ThinkPad (measured, synthetic data, `M4_compute_probe.out`)
1,000,000 rows x 30 float32 features, 8 threads, nice 10. L2 logistic (lbfgs): **0.16 s** per fit. Elastic-net
logistic (saga, l1_ratio 0.5, 50 iterations at tol 1e-3, converged): **10.6 s** per fit. The 39-month window
at 1-minute rows, both sessions, is 860,880 rows (section (e)), so one fit is under 11 s. A 20-value lambda
path x 3 alphas x 5 outer folds = 300 fits x 10.6 s = 53 minutes at most, and much less with warm-started
paths (glmnet computes a whole path in about the time of a few fits). Memory: 1M x 30 x 4 bytes = 120 MB.
No GPU.

##### a.7 Verdict: **use**, as the primary model family
It fits the sample (section (e): tens of parameters against thousands of independent labels). Its
probabilities are well calibrated before any correction: Niculescu-Mizil and Caruana place logistic regression
among the methods "well calibrated initially and post-calibration does not help them on most problems". In
the closest large high-frequency horse race, trees and neural nets beat LASSO by little (Aït-Sahalia et al.,
quoted in E.28 2.9 section 6.6). And one-minute LASSO forecasts on equities did find real, short-lived signal
(Chinco, Clark-Joseph and Ye, below). Each declared (alpha, lambda-rule, feature-set) combination is +1 to N
under V43. The lambda path itself counts as one configuration only if the rule that picks lambda (for example
"1-SE rule on blocked inner CV") is frozen in advance. That is a lead decision.

##### a.8 Evidence table
| Claim | Source | Verbatim quote | Saved file |
|---|---|---|---|
| Elastic net is a ridge-lasso mix | Friedman, Hastie, Tibshirani 2010, JSS (academic) | "P α is a compromise between the ridge-regression penalty (α = 0) and the lasso penalty (α = 1). This penalty is particularly useful in the p ≫ N situation, or any situation where there are many correlated predictor variables." | friedman2010_glmnet_pmc.html/.txt |
| Ridge shares weight among correlated features; lasso picks one | same | "Lasso, on the other hand, is somewhat indifferent to very correlated predictors, and will tend to pick one and ignore the rest." | same |
| Logistic is calibrated without correction | Niculescu-Mizil & Caruana 2005, ICML (academic) | "Examining the histograms and reliability diagrams for logistic regression and bagged trees shows that they behave similar to neural nets. Both learning algorithms are well calibrated initially and post-calibration does not help them on most problems." and "While it is not surprising that logistic regression pre-dicts such well-calibrated probabilities" (the PDF splits the sentence across a page; joined from raw-text lines 837-840 and 1194) | niculescu_caruana2005_calibration.pdf/.raw.txt |
| Boosted trees are distorted until calibrated | same | "maximum margin methods such as boosted trees and boosted stumps push probability mass away from 0 and 1 yielding a characteristic sigmoid shaped distortion in the predicted probabilities" | same |
| Isotonic regression overfits on small calibration sets | same | "A learning curve analysis shows that Isotonic Regression is more prone to overfitting, and thus performs worse than Platt Scaling, when data is scarce." | same |
| Platt is better below about 1,000 cases | same | "When the calibration set is small (less than about 200-1000 cases), Platt Scaling outperforms Isotonic Regression with all nine learning methods." | same |
| Calibrate on independent data | same | "So we need to use an independent calibration set in order to get good posterior probabilities." | same |
| Modern networks are miscalibrated; temperature scaling fixes it | Guo et al. 2017, ICML, arXiv 1706.04599 (academic) | "modern neural networks, unlike those from a decade ago, are poorly calibrated" and "temperature scaling – a single-parameter variant of Platt Scaling – is surprisingly effective at calibrating predictions" | guo2017_calibration.pdf |
| LASSO finds short-lived 1-minute predictors | Chinco, Clark-Joseph, Ye, NBER w23933 (2017), published JF 74(1) 2019 (academic) | "The LASSO increases both out-of-sample fit and forecast-implied Sharpe ratios. And, this out-of-sample success comes from identifying predictors that are unexpected, short-lived, and sparse." | chinco2017_nber_w23933.pdf |
| The size of that gain | same | "increases out-of-sample fit by at least ∆R̄n2 = 1.2%pt relative to just using the benchmark model by itself" and "this forecast-implied strategy generates an annualized Sharpe ratio of 1.8 net of trading costs" | same |
| It refits in short rolling windows | same | "we use the LASSO to make 1-minute-ahead return forecasts in rolling 30-minute estimation windows using the entire cross-section of lagged returns as candidate predictors" | same |

Caveat on Chinco et al.: equities, 2005-2012, 2,191 stocks of cross-sectional predictors. ZM has three
instruments, so the "sparse among thousands" mechanism does not carry over. What carries over is the
evidence that minute-scale signals are short-lived and need frequent refits (topic (d)).

#### (b) Gradient-boosted trees (LightGBM): depth limits, monotone constraints, early stopping

##### b.1 Core idea
A sum of small regression trees, each fitted to the gradient of the loss left by the previous ones (objective,
leaf weights and split gain in E.28 2.9 section 6.2, XGBoost eqs. 2, 4, 5, 6; worked leaf example in E.28 2.9
section 6.3). Three things matter for a weak minutes-scale signal. A depth limit caps how many features can
interact in one tree. A monotone constraint makes the prediction move in a declared direction in a feature
whose sign is economically fixed. Early stopping chooses the number of trees and is the main leakage risk
inside purged folds.

##### b.2 Equations (what is new beyond E.28 2.9)
- Leaves per tree: with depth d, a depth-wise tree has at most L = 2^d leaves, so d = 3 gives L = 8.
  LightGBM grows trees leaf-wise, so depth and leaf count are separate settings: "max_depth ... limit the max
  depth for tree model. This is used to deal with over-fitting when #data is small. Tree still grows
  leaf-wise", and "num_leaves, default = 31". The tuning page: "Theoretically, we can set num_leaves =
  2^(max_depth) to obtain the same number of leaves as depth-wise tree"
  (`lightgbm_parameters.html`, `lightgbm_tuning.html`). Setting max_depth = 3 alone already caps a tree at 8
  leaves, because the default 31 cannot be reached. Declare num_leaves <= 8 anyway, so the frozen
  configuration says what it does.
- Model size: K trees x L leaves gives K L leaf values plus K (L - 1) split thresholds. K = 300 and L = 8
  give 2,400 leaf values and 2,100 thresholds. Leaf values are shrunk by the learning rate eta and by lambda
  (w*_j = -G_j / (H_j + lambda), E.28 2.9 eq. 5), so the effective degrees of freedom are far fewer than
  4,500. No closed form is available. Treat the comparison with independent labels (section (e)) as an upper
  bound on risk.
- Monotone constraint, increasing in feature j: f(x) <= f(x') whenever x_j <= x'_j and all other features are
  equal. In LightGBM: "1 means increasing, -1 means decreasing, 0 means non-constraint". There are three
  enforcement methods: "basic ... does not slow down the training speed at all, but over-constrains the
  predictions"; "intermediate ... much less constraining than the basic method"; "advanced ... even less
  constraining" (`lightgbm_parameters.html`). The method is a hyperparameter. Choosing among methods on
  results adds configurations to N.
- Path smoothing (optional regulariser for small leaves, LightGBM docs): w = w (n/s) / (n/s + 1) +
  w_p / (n/s + 1), with n the leaf count, s = path_smooth and w_p the parent's weight.
- Early stopping: "will stop training if one metric of one validation data doesn't improve in last
  early_stopping_round rounds" (`lightgbm_parameters.html`). The selected K* = argmin_k
  Loss_valid(F_k), where F_k is the model after k rounds. K* is a statistic of the validation block, so
  whatever block it comes from is no longer out-of-sample for K*.

##### b.3 Worked example
1. *Effective leaf occupancy in independent labels.* Rows on a 1-minute grid with a 15-minute label: one
   independent label spans 15 rows. LightGBM's default min_data_in_leaf = 20 rows is therefore about
   20 / 15 = 1.3 independent labels, so a leaf can be fitted to about one label's worth of noise. To require
   at least m = 30 independent labels per leaf, set min_data_in_leaf >= m x (h / Delta) = 30 x 15 / 1 = 450
   rows. At h = 60 on the same grid it is 30 x 60 = 1,800 rows. Check: the training fold of 60% of 816 days
   x 290 rows = 141,984 day-session rows, divided by 8 leaves, gives about 17,700 rows per leaf on average,
   so 1,800 rows is not binding for the average leaf. It is binding only for leaves cut off in a tail.
2. *Model size against independent labels.* 15-minute day-session labels in a 60% training fold:
   0.6 x 15,504 = 9,302 (section (e)). K = 300 trees of 8 leaves give 2,400 leaf values, or 2,400 / 9,302 =
   0.26 leaf values per independent label. With eta = 0.05, each leaf moves the fit only 5% of its
   Newton step, which is why shrinkage plus early stopping, not leaf count, is the real capacity control.
3. *Leaf-weight shrinkage.* E.28 2.9 section 6.3: residuals -0.5, -0.2, +0.1 tick, lambda = 1 gives
   w* = +0.15 tick instead of the plain mean of 0.2. With lambda = 10, w* = 0.6 / (3 + 10) = 0.046 tick.
   Large lambda matters for leaves holding few independent labels.
4. *Monotone sign, honestly.* For minutes-ahead ZM direction, very few signs are economically fixed. Order-flow
   imbalance is contemporaneously positive (E.28 2.9 section 1). Its predictive sign at 15 minutes can be
   continuation or reversal, and is not fixed. A crush-residual reversion feature has a fixed sign only if the
   declared hypothesis is reversion: then "ZM rich relative to the crush, so lower future ZM return" means
   monotone -1. A constraint is legitimate only when it restates a pre-registered directional hypothesis.
   Otherwise it is a free choice that must be counted.

##### b.4 Data it needs
Same rows and features as (a). Trees need no standardisation and handle interactions (session x imbalance,
spread state x flow) without hand-made products. Session indicators (day versus overnight, minutes since
08:30, report-day flags) are natural split variables.

##### b.5 Leakage and look-ahead traps, each with a test
- *Early stopping on the test fold.* K* chosen on the block that is then reported as "out-of-sample" makes
  that score optimistic. This is the selection bias of Cawley and Talbot (2010): "over-fitting in model
  selection can result in biased performance evaluation if model selection is not viewed as an integral part
  of the modelling procedure". **Rule:** K* comes from an inner validation block carved from the end of the
  training fold. That block is purged (label horizon h) from the inner training rows and embargoed from the
  outer test fold. **Test:** log, for every outer fold, which row indices the early-stopping set used. Their
  intersection with the outer test fold's indices, widened by h on each side, must be empty (a mechanical
  assertion).
- *Random-row early-stopping split inside the training fold.* With overlapping labels and autocorrelated
  features, a random 10% holdout sits next to its training neighbours. Its loss keeps falling for longer, so
  K* is too large (overfit), and the inflated validation score feeds any later selection. **Test (day-block
  null):** permute labels across whole days and run the full pipeline. The median K* must stay near the
  minimum number of rounds, and validation AUC must be about 0.5 (within its permutation spread). Under a
  random-row split, the null run will typically show more rounds and AUC above 0.5. That is the leak's
  signature.
- *K* re-tuned per outer fold and then a final model refitted on all data with a K chosen by looking at
  outer-fold scores.* That is a selection on the test folds. **Rule and test:** freeze the refit rule, for
  example "K_final = median of the inner K* times n_full / n_inner". The final score is the one-shot test
  under V43.
- *Binning (histogram) bounds computed on the full sample.* LightGBM builds feature bins from the Dataset it
  is given. Build the Dataset from the training fold only and construct validation and test with
  `reference=` to the training Dataset (installed lightgbm 4.7.0 docstring: "If this is Dataset for validation,
  training data should be used as reference"). **Test:** prefix invariance, as in (a).
- *Monotone constraints or features chosen after looking at fold results.* **Test:** the frozen
  configuration's hash is recorded before the first fit. Any change adds configurations to N.

##### b.6 Compute on the ThinkPad (measured, synthetic data, `M4_compute_probe.out`)
Depth 3, 8 leaves, eta 0.05, min_data_in_leaf 500, lambda_l2 10, 500 rounds, 30 features, 8 threads, nice 10:

| Rows | Unconstrained | Monotone on 5 features (intermediate) |
|---|---|---|
| 1,000,000 | 26.3 s | 27.2 s |
| 5,000,000 | 91.3 s | 74.8 s |

The two 5M timings are within noise of each other: the monotone run happened to be faster, and one run each
is not enough to tell them apart. The 39-month window has 860,880 one-minute rows over both sessions, or
5,165,280 ten-second rows (section (e)). So one fit takes under 30 s at 1-minute and under 2 minutes at
10-second sampling. Memory: 5M x 30 x 4 bytes = 600 MB for the raw matrix, plus LightGBM's binned copy (1
byte per value per feature at <= 255 bins, about 150 MB). An illustrative fixed grid of 3 eta x 2
min_data_in_leaf x 2 feature sets = 12 configurations x 5 outer folds = 60 fits x 26 s = 26 minutes at
1-minute rows. No GPU (LightGBM's GPU build is not needed at this size).

##### b.7 Verdict: **maybe**, as one or two declared secondary configurations next to the linear primary
Shallow (depth <= 3) boosted trees can pick up session-by-state interactions the linear model misses. The
best large comparison found them little better than LASSO at high frequency (E.28 2.9 section 6.6). Their raw
probabilities need Platt calibration (Niculescu-Mizil and Caruana: boosted trees push "probability mass away
from 0 and 1"), which adds a calibration block. Early stopping must sit inside the purged inner split.
Monotone constraints only where the sign restates the declared hypothesis.

##### b.8 Evidence table
| Claim | Source | Verbatim quote | Saved file |
|---|---|---|---|
| max_depth controls over-fitting; tree still grows leaf-wise | LightGBM docs (developer documentation), "latest" page, fetched 2026-10-27; project env has lightgbm 4.7.0 | "limit the max depth for tree model. This is used to deal with over-fitting when #data is small. Tree still grows leaf-wise" | lightgbm_parameters.html |
| num_leaves vs depth | LightGBM tuning docs | "Theoretically, we can set num_leaves = 2^(max_depth) to obtain the same number of leaves as depth-wise tree." | lightgbm_tuning.html |
| Monotone constraint encoding | LightGBM docs | "1 means increasing, -1 means decreasing, 0 means non-constraint you need to specify all features in order." | lightgbm_parameters.html |
| Basic method over-constrains | LightGBM docs | "basic, the most basic monotone constraints method. It does not slow down the training speed at all, but over-constrains the predictions" | same |
| Early stopping definition | LightGBM docs | "will stop training if one metric of one validation data doesn’t improve in last early_stopping_round rounds" | same |
| min_data_in_leaf default 20 | LightGBM docs | "min_data_in_leaf ... default = 20 ... minimal number of data in one leaf. Can be used to deal with over-fitting" | same |
| Selection on the evaluation data biases it | Cawley & Talbot 2010, JMLR 11 (academic) | "Section 5 shows that over-fitting in model selection can result in biased performance evaluation if model selection is not viewed as an integral part of the modelling procedure." | cawley_talbot2010.pdf |
| Unbiased evaluation needs nesting | same | "robust unbiased performance evaluation is likely to require more rigorous and computationally intensive protocols, such a nested cross-validation or “double cross” (Stone, 1974)." | same |
| Variance of the selection criterion causes overfitting in selection | same | "a nonnegligible variance introduces the potential for over-fitting in model selection as well as in training the model" | same |
| Trees add little over LASSO at high frequency | Aït-Sahalia et al. 2022 via E.28 2.9 section 6.6 | "The improvements from a nonlinear method like random forest or gradient boosting trees are limited for most cases when compared with LASSO." | reports/stage_e28_briefs/pages/C2_OFI/afxz2022_hf_predictable.pdf/.txt |
| Boosted-tree probabilities are distorted | Niculescu-Mizil & Caruana 2005 | quoted in (a) | niculescu_caruana2005_calibration.pdf |

#### (c) Small sequence models (DeepLOB-style CNN-LSTM, TCN, small transformers): the data-size verdict

##### c.1 Core idea
Instead of hand-made features, these models read a window of the last T book or bar states and learn their own
features. DeepLOB stacks convolutions over book levels, then an Inception block and an LSTM (equations in E.28
2.8 section 1.2). A temporal convolutional network (TCN) uses causal dilated 1-D convolutions. A small
transformer uses self-attention over the window. The question for this stage is not whether they can be
trained on the laptop (they can). It is whether 39 months of one contract hold enough independent
minutes-scale labels to fit tens of thousands of weights without fitting noise.

##### c.2 Equations
- TCN dilated causal convolution (Bai, Kolter and Koltun 2018, eq. 2; `bai2018_tcn.pdf`):
  F(s) = (x *_d f)(s) = sum_{i=0..k-1} f(i) x_{s - d i}, where x is the input sequence, f a filter of size k,
  and d the dilation factor ("Where d is the dilation factor, k is the filter size, and s − d · i accounts for
  the direction of the past"). Only past inputs enter, so the convolution is causal by construction.
- Receptive field of a TCN with L residual blocks, two convolutions per block, filter size k and dilations
  d_l = 2^l (l = 0..L-1): R = 1 + 2 (k - 1) sum_l 2^l = 1 + 2 (k - 1)(2^L - 1). This is my derivation for
  the block layout of their Figure 1; the paper gives the per-layer rule, not this total.
- Self-attention (standard): Attention(Q, K, V) = softmax(Q K' / sqrt(d_k)) V, with Q, K, V linear maps of
  the T x d input. Parameters per encoder layer are about 4 d^2 (attention) + 2 d d_ff (feed-forward).
- DeepLOB: E.28 2.8 section 1.2 (label eqs. and architecture; 60,947 parameters in the paper version, E.28
  2.8 section 10.1).
- Parameter-to-sample ratio: q = (number of trainable weights) / (number of independent labels in the
  training fold). This is a heuristic, not a bound: weight sharing and early stopping lower the effective
  count. A ratio well above 1 means the label set cannot pin the weights down, and the fit is decided by
  regularisation and the seed.

##### c.3 Worked example (`M4_examples.out`, `M4_compute_probe.out`)
1. *TCN receptive field.* The probe's TCN has L = 6 blocks, k = 3, dilations 1, 2, 4, 8, 16, 32:
   R = 1 + 2 x 2 x 63 = **253** steps. On a 1-minute grid that is 253 minutes, nearly the whole 290-minute
   day session. On a 10-second grid it is 42 minutes.
2. *Parameters against independent labels (whole 39 months, day session only; section (e) gives the
   counts).* q = params / labels:

   | Model (params) | 1-min labels 236,640 | 5-min 47,328 | 15-min 15,504 | 60-min 3,264 |
   |---|---|---|---|---|
   | TCN probe (38,081) | 0.16 | 0.80 | 2.46 | 11.7 |
   | DeepLOB paper (60,947) | 0.26 | 1.29 | 3.93 | 18.7 |
   | Tiny transformer probe (110,209) | 0.47 | 2.33 | 7.11 | 33.8 |

   Check (DeepLOB, 15 min): 60,947 / 15,504 = 3.93. These counts are for the whole window. A training fold of
   60% raises every q by 1/0.6 = 1.67x. At the horizons where the cost hurdle can be met (15 to 60 minutes,
   section 0), every sequence model has 2 to 34 weights per independent label. A 30-feature logistic model has
   30 / 15,504 = 0.002.
3. *What the labels can detect at all.* With n independent labels, a correlation (information coefficient,
   IC) between forecast and outcome is about 3 standard errors from zero when IC = 3 / sqrt(n). For 15-minute
   day-session labels over 39 months, IC = 3 / sqrt(15,504) = 0.024; over a 60% fold, 3 / sqrt(9,302) =
   0.031. Any signal weaker than that is invisible to any model. A model with 60,000 weights must find that
   signal using no more labels than the 30-weight model has.

##### c.4 Data it needs
A T x F tensor per decision row. For DeepLOB proper, the top 10 book levels per event. ZM MBO can rebuild them
(E.28 2.8 section 1.3: "mbo is a superset (mbp-10 can be built from it)"), but ZS and ZL are MBP-1 only, so a
deep book model sees depth for ZM alone. For TCNs and transformers on bars, T bars of F engineered features (as
in (a)). GPU memory is not binding: probe peak 165 MiB (TCN) and 365 MiB (transformer) at batch 256 and
T = 128.

##### c.5 Leakage and look-ahead traps, each with a test
- *Overlapping windows across the train/validation boundary.* A window of T steps for the first validation row
  reaches T - 1 steps into the training block, and its label reaches h past the row. Purge T + h rows (T for
  features, h for labels) at every boundary. **Test:** assert that no validation or test row's input window or
  label window intersects a training row's label window.
- *Non-causal layers.* Same-padding convolutions, bidirectional LSTMs and unmasked attention over a window
  that includes post-decision steps all see the future. **Test (future perturbation):** change the input at
  steps after the decision time. The output must not change, to the bit.
- *Normalisation statistics over the whole dataset.* (DeepLOB normalises with prior-day statistics, E.28 2.8.)
  **Test:** prefix invariance, as in (a).
- *Early stopping, seed choice and architecture search on the test block* (the LOBCAST lesson, E.28 2.8
  section 4.1). Each seed kept by result is a configuration. **Test:** record all seeds and report the mean
  over a fixed seed set, never the best.
- *Calibration.* Guo et al.: modern networks "are poorly calibrated". A probability rule needs temperature
  scaling on a separate block (topic (a)).

##### c.6 Compute on the ThinkPad (measured, synthetic tensors, RTX 3050 4 GB)
Training throughput, batch 256, T = 128, 30 input channels, AdamW: TCN 32 channels x 6 blocks (38,081
params) **18,018 samples/s**, peak 165 MiB. 2-layer transformer, d = 64, 4 heads (110,209 params)
**4,466 samples/s**, peak 365 MiB. DeepLOB (paper) 5,247 samples/s at batch 256 (E.28 2.8 section 10.1).
One epoch over the 39-month day-session 1-minute rows (236,640) takes 236,640 / 18,018 = 13 s for the TCN and
53 s for the transformer. Over 10-second rows, both sessions (5,165,280), it takes 287 s and 1,157 s, so
40 epochs take 3.2 h and 12.9 h. A grid of 10 configurations x 5 seeds x 5 folds at 40 epochs on 10-second
rows is 250 runs x 3.2 h = 800 GPU-hours for the TCN. Compute is not the barrier at 1-minute sampling. It
becomes the barrier at 10-second sampling with seeds, and then only multiplies a problem the data already has.

##### c.7 Verdict: **skip** for the minutes-scale directional search (no pre-registered deep model in E.33)
The data-size verdict: at the horizons where p* is reachable (15 to 60 minutes), every small sequence model
has 2 to 34 weights per independent label over all 39 months (q table above), and the detectable IC floor is
the same for every model. The published evidence for deep LOB models is at 10 to 100 book events, mostly
under 10 seconds (Briola et al. Table 7; E.28 2.8 section 4.3). Even there, the gain over simple models is
disputed (LOBCAST, Briola-Turiel-Aste 2020 "an MLP is as good", E.28 2.8 section 4.2). In long-horizon time
series, a one-layer linear model beat transformers "in all cases", and transformers "are prone to overfit on
noisy financial data" (Zeng et al. 2023). The planner's "No deep LOB models" is supported (planner table). If
the lead wants a non-linear sequence check, a TCN on the same features as the linear model, declared as one
configuration with a fixed seed set, is the cheapest. It is not recommended.

##### c.8 Evidence table
| Claim | Source | Verbatim quote | Saved file |
|---|---|---|---|
| Dilated causal convolution definition | Bai, Kolter, Koltun 2018, arXiv 1803.01271 (academic) | "Where d is the dilation factor, k is the filter size, and s − d · i accounts for the direction of the past." | bai2018_tcn.pdf/.raw.txt |
| TCNs beat canonical RNNs on generic benchmarks | same | "Our results indicate that a simple convolutional architecture outperforms canonical recurrent networks such as LSTMs across a diverse range of tasks and datasets, while demonstrating longer effective memory." | same |
| Linear beats transformers for time-series forecasting | Zeng, Chen, Zhang, Xu 2023, AAAI, arXiv 2205.13504 (academic) | "Experimental results on nine real-life datasets show that LTSF-Linear surprisingly outperforms existing sophisticated Transformer-based LTSF models in all cases, and often by a large margin." | zeng2023_ltsf_linear.pdf |
| Transformers overfit noisy financial data | same | "LTSF-Transformers with different positional and temporal embeddings preserve quite limited temporal relations and are prone to overfit on noisy financial data, while the LTSF-Linear can model the order naturally and avoid overfitting with fewer parameters." | same |
| Networks miscalibrated | Guo et al. 2017 | quoted in (a) | guo2017_calibration.pdf |
| Deep LOB data-size verdict | E.28 2.8 section 1.3 | "The binding constraint is independence, not sample count" (full quote in section 0) | reports/stage_e28_methods_brief.md |
| Deep LOB horizons are seconds | Briola, Bartolucci, Aste (arXiv 2403.09267v4; QF 25(7) 2025) | "for all the stocks, except MCD (small-tick stock) and ABBV (medium-tick stock), 10 LOB’s updates are more likely to happen in a physical time < 1 s" | reports/stage_e28_briefs/pages/C2_DeepLOB/briola_microstructural_guide2024.pdf/.raw.txt (sha256 1642bd28...) |

Caveat on Zeng et al.: their datasets are long-horizon (hours to days ahead) and include one exchange-rate
series, not intraday futures. The quote supports "transformers overfit noisy series", not a ZM-specific result.

#### (d) Online and regime-switching models: online logistic, RLS with forgetting, Markov-switching regression, Kalman time-varying coefficients

##### d.1 Core idea
If the relation between features and future ZM returns drifts (the planner expects a break between discovery,
2020-24, and test, 2017-20), a model fitted once on 39 months predicts with stale weights. Online models update
the weights as each label arrives. Online logistic regression does it by a gradient step. Recursive least
squares (RLS) with a forgetting factor, which is the same thing as a Kalman filter on random-walk
coefficients, does it by an exact weighted least-squares update. A Markov-switching regression lets the
weights jump between K fixed sets. The price is new tuning choices (learning rate, forgetting factor, K), each a
configuration under V43, and a timing trap: an h-minute label is only known h minutes later.

##### d.2 Equations
- *Online logistic regression* (McMahan et al. 2013, eq. 1 and the OGD update; `mcmahan2013_ftrl.pdf`):
  p_t = sigma(w_t . x_t), sigma(a) = 1/(1 + exp(-a)); loss l_t(w_t) = -y_t log p_t - (1 - y_t) log(1 - p_t);
  gradient "∇l_t(w) = (σ(w · x_t) − y_t)x_t = (p_t − y_t)x_t"; online gradient descent
  "w_{t+1} = w_t − η_t g_t, where η_t is a non-increasing learning-rate schedule". Their FTRL-Proximal
  variant adds per-coordinate rates eta_{t,i} = alpha / (beta + sqrt(sum_s g_{s,i}^2)) (their eq. 2) and L1
  sparsity. For a drifting target the schedule must NOT decay to zero. A constant eta gives exponential
  forgetting, roughly over 1/(eta x curvature) steps (my statement, standard for SGD on a quadratic).
- *Kalman time-varying-parameter regression with forgetting* (Raftery, Kárný and Ettler 2010, Technometrics,
  eqs. 1-9; `raftery2010_dma.pdf`):
    observation  y_t = x_t' theta_t + eps_t,  eps_t ~ N(0, V)                     (1)
    state        theta_t = theta_{t-1} + delta_t,  delta_t ~ N(0, W_t)           (2)
    prediction   theta_t | Y^{t-1} ~ N(theta_hat_{t-1}, R_t),  R_t = Sigma_{t-1} + W_t   (3), (4)
    forgetting   R_t = lambda^{-1} Sigma_{t-1}                                    (5)
    update       theta_hat_t = theta_hat_{t-1} + R_t x_t (V + x_t' R_t x_t)^{-1} e_t,  e_t = y_t - x_t' theta_hat_{t-1}   (7)
                 Sigma_t = R_t - R_t x_t (V + x_t' R_t x_t)^{-1} x_t' R_t        (8)
    delayed use  y_hat_t = x_t' theta_hat_{t-d-1}                                (9)
  "λ is called the forgetting factor and is typically slightly below 1", with W_t = a Sigma_{t-1},
  a = lambda^{-1} - 1, and "the effective amount of data used for estimation, or the effective window size, is
  h = 1/(1 − λ)". With V = 1 this is exactly RLS with exponential forgetting: P_t = Sigma_t / V,
  k_t = P_{t-1} x_t / (lambda + x_t' P_{t-1} x_t), theta_t = theta_{t-1} + k_t e_t,
  P_t = (P_{t-1} - k_t x_t' P_{t-1}) / lambda (my algebra: substitute R_t = P_{t-1}/lambda into (7)-(8)).
  Equation (9) is the label-delay rule: when the outcome is known only d steps late, predict with the
  estimate from d + 1 steps back.
- *Markov-switching regression* (statsmodels `MarkovRegression` docs, after Kim and Nelson 1999; Hamilton
  filter in E.28 2.5 section 4.2): y_t = a_{S_t} + x_t' beta_{S_t} + eps_t, eps_t ~ N(0, sigma^2_{S_t}),
  S_t in {1..K} a first-order Markov chain with transition matrix P = [p_ij]. Filtering, likelihood and
  EM are those of E.28 2.5 (Hamilton eqs. 5-12). Optional time-varying transition probabilities
  ("exog_tvtp", logit of observable variables).

##### d.3 Worked example (`M4_examples.out`)
1. *One RLS-with-forgetting step* (one feature). theta_{t-1} = 0.02 ticks per unit, P_{t-1} = 50,
   lambda = 0.99, x_t = 1.5, y_t = 0.8 ticks. Gain k = 50 x 1.5 / (0.99 + 1.5 x 50 x 1.5) = 75 / 113.49 =
   0.66085. Error e = 0.8 - 1.5 x 0.02 = 0.77. theta_t = 0.02 + 0.66085 x 0.77 = **0.52886**.
   P_t = (50 - 0.66085 x 1.5 x 50) / 0.99 = (50 - 49.5638) / 0.99 = **0.44057**. Check: a diffuse prior
   (P = 50) makes the first update almost an OLS fit of one point (y/x = 0.533). theta moved to 0.529, close to
   that, as it should.
2. *Forgetting factor in session time.* Effective window h = 1/(1 - lambda). On a 1-minute day-session grid
   (290 rows a day): lambda = 0.99 gives 100 rows = 0.34 sessions; 0.999 gives 1,000 rows = 3.4 sessions;
   0.9999 gives 10,000 rows = 34.5 sessions. With a 15-minute label, the rows inside a window are not
   independent: 1,000 rows hold about 1,000/15 = 67 independent labels. A window short enough to track
   intraday drift (lambda = 0.999) estimates each coefficient from about 67 labels, so its standard error is
   about 1/sqrt(67) = 0.12 in correlation units. That is five times the IC floor of 0.024 from (c.3), so the
   tracking weights are mostly noise unless the signal is far stronger than anything published for grains.
   This is the bias-variance trade the forgetting factor sets, and why it cannot be tuned freely.
3. *Label delay.* With h = 15 minutes on a 1-minute grid, d = 15: the forecast at 10:00 may use only
   coefficients updated with labels whose 15-minute window closed by 10:00, that is, outcomes for decision
   times up to 09:45 (Raftery eq. 9 with d = 15).
4. *Markov-switching regime durations.* With p_11 = 0.98 on a 1-minute grid, the expected stay in regime 1 is
   1/(1 - 0.98) = 50 minutes (E.28 2.5 section 4.2 formula). With p_11 = 0.9993 it is about 1,430 minutes,
   or about 5 day sessions. The regime's labels per stay are what the regime's beta is fitted from, so the
   same independent-label arithmetic applies within each regime.

##### d.4 Data it needs
Same features and labels as (a), processed strictly in time order, plus a clock of when each label is
realised (decision time + h). For Markov-switching on minute data, the full 39-month series fits in memory.
Session boundaries need a rule: carry the state over the 13:20-19:00 CT break and the weekend, or reset it.
That rule is a frozen choice.

##### d.5 Leakage and look-ahead traps, each with a test
- *Updating with labels not yet realised.* The commonest online-model leak: updating at step t with y_t
  whose window ends at t + h. **Test:** each update record carries the label-realisation timestamp, and the
  forecast at time tau may only use updates with realisation time <= tau - latency (a mechanical assertion
  over every row; Raftery eq. 9).
- *Smoothed regime probabilities or a full-sample Viterbi path used as features* (E.28 2.5 section 4.2:
  "run on the whole sample, it looks ahead"). Only filtered probabilities xi_{t|t} may be used, from
  parameters fitted on the training block. **Test:** future perturbation, as in (c): change data after tau,
  and the regime probability at tau must not move.
- *Hyperparameters (eta, lambda, K, starting values) tuned on the test period.* Every value tried is a
  configuration. **Test:** the frozen configuration hash is recorded before the first test-period prediction.
- *"Online" evaluation that reuses the initial batch fit's sample.* Use progressive validation: score each
  prediction before its label updates the model. McMahan et al.: "We generally use progressive validation
  (sometimes called online loss) [5] rather than cross-validation or evaluation on a held out dataset."
  **Test:** prefix invariance holds by construction. Check it anyway.
- *Label switching in Markov-switching EM across folds* (regime 1 in one fold is regime 2 in another).
  **Rule:** order regimes by a declared statistic (for example sigma_{S}), fixed in advance.

##### d.6 Compute on the ThinkPad
Measured, synthetic data: RLS with forgetting, p = 30, a plain Python and numpy loop: 200,000 steps in 1.64 s,
so 860,880 one-minute rows take about 7 s per pass. A lambda grid of 3 values x 5 folds is under 2 minutes.
Online logistic regression costs less than one RLS step per row. Markov-switching and HMM costs, measured in
E.28 2.5 section 4.7 (numpy): forward filter 200,000 steps in 0.72 s, ten Baum-Welch iterations 27.3 s, about
4.5 minutes for ten iterations on 1.87M steps. A K = 2 Markov-switching regression adds a weighted least-squares
solve per regime per iteration, which is cheap at p = 30. statsmodels 0.15.0 provides `MarkovRegression` but is
not in the project environment (E.28 2.5 section 1.7). A numpy version is short. A Kalman TVP regression is the
RLS loop above. No GPU for any of these.

##### d.7 Verdict
- **Online logistic or RLS/Kalman TVP with a fixed forgetting factor: maybe**, as one declared configuration
  that wraps the primary linear model (same features, lambda fixed in advance from an economic window such
  as "about 20 sessions", lambda = 1 - 1/(20 x 290) = 0.99983 on a 1-minute grid). It is the cheapest
  answer to the expected discovery/test regime break, and Chinco et al.'s 1-minute result came from frequent
  re-estimation. Against: the variance arithmetic in d.3 item 2, and no grain evidence.
- **Markov-switching regression as a directional forecaster: skip.** Same verdict as E.28 2.5 section 9
  ("HMM as a return forecaster (directional): skip") on the same evidence: regime models forecast poorly
  out of sample because misclassification of future regimes dominates (Engel 1994; Bessec and Bouabdallah,
  quoted in E.28 2.5 section 4.8). A 2-state volatility gate (trade or stand aside) remains E.28's "maybe",
  but that is a filter, not a direction model, and belongs to the lead's family design.

##### d.8 Evidence table
| Claim | Source | Verbatim quote | Saved file |
|---|---|---|---|
| Online logistic gradient | McMahan et al. 2013, KDD, "Ad Click Prediction: a View from the Trenches" (firm research, Google) | "It is straightforward to show ∇ℓt(w) = (σ(w · xt) − yt)xt = (pt − yt)xt, and this gradient is all we will need for optimization purposes." | mcmahan2013_ftrl.pdf/.raw.txt |
| OGD update with non-increasing rate | same | "OGD performs the update wt+1 = wt − ηt gt , where ηt is a non-increasing learning-rate schedule" | same |
| Progressive validation | same | "We generally use progressive validation (sometimes called online loss) [5] rather than cross-validation or evaluation on a held out dataset." | same |
| Forgetting factor definition | Raftery, Kárný, Ettler 2010, Technometrics 52(1) (academic) | "where λ is called the forgetting factor and is typically slightly below 1." | raftery2010_dma.pdf/.raw.txt |
| Effective window h = 1/(1−λ) | same | "estimation in this model is essentially age-weighted estimation where data i time points old has weight λi , and the effective amount of data used for estimation, or the effective window size, is h = 1/(1 − λ)." | same |
| Delayed outcomes use an older estimate | same | "The information available for predicting yt is d samples old because of the time-delay problem, and so we use ŷt = xtT θ̂t−d−1 ." | same |
| Markov-switching regression form | statsmodels 0.15.0 docs (developer documentation) | "the model is a dynamic linear regression where the coefficients and the variance of the error term may be switching across regimes" | statsmodels_markovregression.html |
| Regime forecasts fail on misclassification | Bessec & Bouabdallah via E.28 2.5 section 4.8 | "We find that the main source of error is due to the misclassification of future regimes" | reports/stage_e28_briefs/pages/C2_Filter/bessec_bouabdallah_2005.txt (E.28 file) |
| Short rolling windows find 1-minute signals | Chinco et al. | quoted in (a) | chinco2017_nber_w23933.pdf |

Not found: an intraday futures study that compares a fixed-weight model with an online or TVP version of the
same model out of sample and net of costs. Dangl and Halling (2012, JFE), the standard reference for
time-varying-coefficient return prediction, is monthly equity-premium work and was not fetched [unverified,
named from memory only, so no claim rests on it].

#### (e) Effective sample size per horizon and parameter-to-sample ratios

##### e.1 Core idea
The number of rows is not the number of independent pieces of evidence. With an h-minute label sampled every
minute, consecutive labels share h - 1 of their h minutes. The count that limits what any model can learn,
and what any test can show, is close to the number of NON-overlapping label windows. Within-day dependence
(volatility clustering, a day's common news) lowers it further. This section counts the non-overlapping
windows from session lengths and the calendar, without reading data.

##### e.2 Equations
- Non-overlapping labels per session: n_s(h) = floor(L_s / h), with L_s the session length in minutes.
- Over D trade dates: N(h) = D x n_s(h), per session type.
- Session lengths (READER_BRIEF, CT): day 08:30-13:20 = **290 minutes**; overnight 19:00-07:45 =
  **765 minutes** (12 h 45 min); sum 1,055 minutes. Day-session volume share 0.83 (READER_BRIEF table), so
  overnight minutes carry about 17% of the volume over 2.6 times the minutes.
[MathReview D-3 (lead: accepted): M3 g.3 allows label spans only from 08:35 to 13:13 (278 minutes) and 19:05 to 07:44 overnight (759 minutes) and excludes roll dates and the next date (E.31: 52 of 816 dates); on the 278 basis 15-min labels per session are 18 not 19 and 5-min 55 not 58 (30, 60, 120, 240 unchanged), so on D = 816 the 15-min day total is 14,688 (not 15,504), the 60% fold 8,813 (not 9,302), IC floor 0.0248 (not 0.0241), GBM-300 q 0.27 (not 0.26), and with E.31's exclusions (D about 764) 13,752 whole-window, 8,251 in a 60% fold, IC floor 0.033 in the fold (recomputed table in d_m4.out, "day278" columns). Verdicts are unchanged (q <= 0.004 for linear, 0.27-0.29 for GBM-300 at 15 min, 4-125 for sequence models); M4 should state the 278/759-minute basis and that D after g.3 rules 5-7 is about 764, so M5b's power arithmetic reads the smaller n_eff (also applies at original lines 585-594, 601-607, 616-627, 121-122, 234-236, 352-356).]
- Overlapping rows on a grid of step Delta: R(h) = D x L_s / Delta rows, with an overlap factor of about
  h / Delta between rows and independent labels.
- Design effect for day clustering (standard survey formula, my addition): n_eff = N / (1 + (m - 1) rho),
  with m labels per day and rho their average intra-day correlation. Unknown until E.33 measures it.
- Detectable effect at t = 3: IC_min = 3 / sqrt(n_eff) for a correlation-type signal, or equivalently the
  number of labels for an IC: n = (3 / IC)^2.
- Parameter-to-sample ratio: q = k / n_eff, with k the model's free parameters (or leaf values).

##### e.3 Worked example: counts over the 39-month owned window (2020-12-01 to 2024-02-29)
Calendar (`M4_ess.py`): 848 weekdays minus 32 ASSUMED full-day CBOT grain closures (New Year, MLK, Presidents,
Good Friday, Memorial, Juneteenth from 2022, Independence, Labor, Thanksgiving, Christmas, with the observed
dates listed in the script) = **D = 816 trade dates**. The DataFacts worker owns the true calendar.
Early-close days, roll and notice exclusions, and the 1-2 minutes after releases that the planner would drop
all lower these counts. The memory note on the equity calendar booking US holidays as trade dates applies:
do not take D from that calendar.

| h (min) | per day session (290 min) | per overnight (765 min) | day total (D = 816) | overnight total | both | IC_min (t = 3), day | IC_min, both |
|---|---|---|---|---|---|---|---|
| 1 | 290 | 765 | 236,640 | 624,240 | 860,880 | 0.0062 | 0.0032 |
| 5 | 58 | 153 | 47,328 | 124,848 | 172,176 | 0.0138 | 0.0072 |
| 15 | 19 | 51 | 15,504 | 41,616 | 57,120 | 0.0241 | 0.0126 |
| 30 | 9 | 25 | 7,344 | 20,400 | 27,744 | 0.0350 | 0.0180 |
| 60 | 4 | 12 | 3,264 | 9,792 | 13,056 | 0.0525 | 0.0263 |
| 120 | 2 | 6 | 1,632 | 4,896 | 6,528 | 0.0743 | 0.0371 |
| 240 | 1 | 3 | 816 | 2,448 | 3,264 | 0.1050 | 0.0525 |
| to close (13:15-ish) | 1 per decision time | n/a | 816 | n/a | 816 | 0.1050 | n/a |

Check rows: 290 / 15 = 19.33, floored to 19; 19 x 816 = 15,504; 3 / sqrt(15,504) = 3 / 124.5 = 0.0241.
765 / 60 = 12.75, floored to 12; 12 x 816 = 9,792. Sanity bound: the "to close" label has exactly one
independent outcome per day whatever the decision grid, so 816 is a hard ceiling for any session-close
label over the whole window. In a 60% discovery fold that is about 490.

Per-fold arithmetic (fold shares are M5a's and the lead's choice; 60/20/20 is illustration only):

| h | day labels, 60% train | 20% validation | 20% test-in-discovery |
|---|---|---|---|
| 15 | 9,302 | 3,101 | 3,101 |
| 60 | 1,958 | 653 | 653 |
| 240 | 490 | 163 | 163 |

At h = 60, a 653-label validation block detects only IC >= 3 / sqrt(653) = 0.117. That is a large
correlation for a minutes-scale return forecast (Chinco et al.'s 1.2 percentage-point R² gain corresponds,
roughly and only if the added forecast is orthogonal to the benchmark, to an incremental correlation of about
sqrt(0.012) = 0.11 at 1 minute in equities, the strongest result found).
Validation blocks at long horizons cannot rank models with any precision. That favours few, frozen
configurations over a searched grid.

##### e.4 Parameter-to-sample ratios per family (q = k / n, n = 60% training fold of day-session labels)
| Family, illustrative size | k | q at 15 min (n = 9,302) | q at 60 min (n = 1,958) | q at 240 min (n = 490) |
|---|---|---|---|---|
| Logistic / elastic net, 30 features | 31 | 0.0033 | 0.016 | 0.063 |
| Logistic, 60 features | 61 | 0.0066 | 0.031 | 0.12 |
| LightGBM depth 3, 300 trees (leaf values, unshrunk) | 2,400 | 0.26 | 1.23 | 4.9 |
| LightGBM depth 3, 100 trees | 800 | 0.086 | 0.41 | 1.6 |
| RLS, 30 features, lambda = 0.999 (per-window count: about 67 labels at 15 min) | 30 | 0.45 within the window | n/a | n/a |
| Markov-switching regression, K = 2, 30 features (2 x 31 + 2 variances + 2 transitions) | 66 | 0.0071 | 0.034 | 0.13 |
| TCN probe | 38,081 | 4.1 | 19.4 | 77.7 |
| DeepLOB (paper) | 60,947 | 6.6 | 31.1 | 124.4 |
| Tiny transformer probe | 110,209 | 11.8 | 56.3 | 224.9 |

Check one cell: 2,400 / 1,958 = 1.226. A rule of thumb from regression practice (my addition, not sourced:
about 10 or more independent observations per free parameter, so q <= 0.1) admits the linear and
Markov-switching families at every horizon up to 60 minutes, shallow GBM with about 100 or fewer trees at
15 minutes, and no sequence model at any horizon where the cost hurdle can be met. Overnight labels add
2.6 times as many windows but at 17% of the volume, so they are worth fewer than their count. Whether to
pool them is a lead decision.

##### e.5 Data it needs
The calendar, the session clock and the exclusion list. No market data. The real D and the real exclusions
come from DataFacts and the frozen protocol.

##### e.6 Leakage and look-ahead traps
- *Counting rows as observations in a t-statistic.* Using 236,640 rows for a 15-minute label inflates t by
  about sqrt(15) = 3.9. **Test:** recompute the statistic on non-overlapping labels only (one decision time
  per window), or with Newey-West lags >= h - 1 (M5a). The two must agree to within sampling error.
- *Overlap across fold boundaries.* Handled by purge and embargo (M5a). **Test:** the interval-intersection
  assertion in (b) and (c).

##### e.7 Compute
Calendar arithmetic only (`M4_ess.py`, under a second).

##### e.8 Verdict: **use** (mandatory)
Every model and test in E.33 should state its n_eff per horizon and its q. Report n_eff from non-overlapping
labels and, once measured, the design effect.

#### (f) Compute per family on the ThinkPad for a fixed, finite grid

##### f.1 Core idea
Every family fits on the laptop. What scales the cost is configurations x outer folds x seeds, and (for
networks) epochs. V43 counts every configuration into N, so the grid size is fixed by the trial budget long
before it is fixed by compute.

##### f.2 Equations
Total time T = (configurations) x (outer folds) x (seeds) x (time per fit). Time per fit is about rows x
(passes or rounds) / throughput, linear in rows for every family here.

##### f.3 Worked example: measured per-fit times and an illustrative grid (grid sizes are illustrations for the lead, not proposals)
Assumptions: 30 features, float32; rows = 860,880 one-minute decision points (both sessions, 39 months) or
236,640 (day session only), or 5,165,280 ten-second points (both sessions); 5 outer folds; nice 10; 8 CPU
threads (within the 14-thread overnight cap); one GPU job at a time. Measured on synthetic data
(`M4_compute_probe.out`, 2026-10-27 00:40-00:44 PDT) unless marked E.28.

| Family | Per-fit time, measured | Illustrative grid | Fits | Total | Memory peak | GPU |
|---|---|---|---|---|---|---|
| L2 logistic | 0.16 s at 1M rows | 10 lambdas x 2 feature sets | 100 | < 1 min | ~0.2 GB | no |
| Elastic-net logistic (saga) | 10.6 s at 1M rows | 10 lambdas x 3 alphas x 2 sets | 300 | ~53 min (a warm-started path is much less) | ~0.2 GB | no |
| LightGBM depth 3, 500 rounds | 26 s at 1M; 91 s at 5M | 3 eta x 2 min_leaf x 2 sets | 60 | 26 min (1-min rows); 91 min (10-s rows) | ~0.8 GB at 5M | no |
| RLS / Kalman TVP, p = 30 | 1.64 s per 200k steps, so ~7 s per 860,880 | 3 lambdas x 2 sets | 30 | ~4 min | < 0.1 GB | no |
| Online logistic (OGD/FTRL) | below RLS (O(p) vs O(p^2) per step; not timed) | 3 rates x 2 sets | 30 | < 4 min | < 0.1 GB | no |
| Markov-switching / HMM, K = 2 | E.28: 27.3 s per 10 EM iterations at 200k steps, ~4.5 min at 1.87M | 2 feature sets x 5 fixed starts | 50 | ~2 h at 860,880 rows (50 x ~2.1 min) | few hundred MB | no |
| TCN (38k params), 40 epochs | 18,018 samples/s, so 13 s/epoch (day 1-min) or 287 s/epoch (10-s, both) | 4 configs x 5 seeds | 100 | 15 h (day 1-min rows) or 318 h (10-s rows) | 165 MiB GPU | yes |
| Tiny transformer (110k), 40 epochs | 4,466 samples/s, so 53 s/epoch (day 1-min) | 4 configs x 5 seeds | 100 | 59 h (day 1-min rows) | 365 MiB GPU | yes |
| DeepLOB paper (61k) | E.28: 5,247 samples/s at batch 256 | (not recommended) | | E.28: 8.5-34 h per configuration on event rows | 577 MiB at batch 256 (E.28) | yes |

Arithmetic checks: TCN 100 fits x 40 epochs x 13.13 s = 52,520 s = 14.6 h. With 10-second rows, 100 x 40 x
286.7 s = 1,146,800 s = 318.6 h. Transformer 100 x 40 x 52.99 s = 211,960 s = 58.9 h. LightGBM 60 x 26.3 s =
1,578 s = 26.3 min. Markov switching: 4.5 min for 1.87M steps scales to 4.5 x 0.8609 / 1.87 = 2.07 min at
860,880 steps, and 50 fits x 2.07 = 104 min (about 1.7 h, rounded up to ~2 h for the regression solves).

##### f.4 Data it needs
The feature table built once per frozen configuration and stored by trade date in shards (C4.4: "LightGBM on
event-sampled rows from a year of one contract fits in memory if features are built by trade date in shards
and written to disk"). At 860,880 x 30 float32 = 103 MB, the 1-minute table fits in RAM whole. The 10-second
table at 5.17M x 30 x 4 = 620 MB also fits.

##### f.5 Leakage traps
None specific to compute. One practical trap: a non-deterministic fit (LightGBM threads, cuDNN) gives
different models on rerun, so a result cannot be re-derived for verification. **Test:** run each frozen
configuration twice. LightGBM: "setting this to true should ensure the stable results when using the same
data and the same parameters (and different num_threads)" (`deterministic`, `lightgbm_parameters.html`).
For torch, set deterministic algorithms and fixed seeds, and compare two runs' predictions.

##### f.6 Compute caveats
The probe used random features with a weak planted logit (0.05 x1 - 0.03 x2). Real features with heavy
tails and many ties change LightGBM's binning slightly but not its order of time. Early stopping usually
stops well before 500 rounds on a weak signal, so the LightGBM figures are upper bounds per fit. Saga's
convergence time depends on conditioning and may be longer on correlated real features.

##### f.7 Verdict
Compute does not constrain any recommended family (linear, shallow GBM, RLS/TVP): a full illustrative grid of
all three takes under 2 hours of CPU. Sequence models are feasible on the RTX 3050 at 1-minute sampling
(hours to days) but not with seeds at 10-second sampling (hundreds of GPU-hours). They are excluded by (c) and
(e), not by compute.

##### f.8 Evidence
Measured: `work/M4_models/M4_compute_probe.out` (raw JSON line), script `M4_compute_probe.py`. E.28 figures:
E.28 2.8 section 10.1, E.28 2.5 sections 1.7 and 4.7, E.28 C4.4.

#### Summary of verdicts (recommendations to the lead; the lead decides)

| Family | Verdict | One-line reason |
|---|---|---|
| (a) Regularised logistic / linear (L2, elastic net) + Platt check | **use (primary)** | q <= 0.03 at 15-60 min; calibrated by construction; the strongest minute-scale evidence (Chinco et al.) is LASSO; trees and nets add little over LASSO at high frequency (Aït-Sahalia et al. via E.28) |
| (a) Isotonic calibration | **skip** at h >= 60 min | calibration blocks hold < 1,000 independent labels; Platt is better there (Niculescu-Mizil & Caruana) |
| (b) LightGBM depth <= 3, <= ~100-300 trees, early stopping inside a purged inner block, Platt-calibrated | **maybe (one or two declared secondary configurations)** | captures session x state interactions; q 0.09-1.2 at 15-60 min; needs calibration and early-stopping discipline |
| (b) Monotone constraints | **use only where the sign restates a declared hypothesis**; otherwise skip | few minutes-ahead ZM signs are economically fixed; the method choice (basic/intermediate/advanced) is itself a configuration |
| (c) DeepLOB, TCN, small transformers | **skip** | 2-34 weights per independent label at the horizons that can pay costs; published gains are at seconds-scale event horizons; linear baselines match them |
| (d) Online logistic / RLS / Kalman TVP with a fixed forgetting factor | **maybe (one declared wrapper of the primary model)** | cheap answer to the expected regime break; label-delay rule (Raftery eq. 9) mandatory; short windows mean noisy weights |
| (d) Markov-switching regression as a direction model | **skip** | regime forecasts fail on regime misclassification (E.28 2.5); a volatility gate stays E.28's "maybe" as a filter |
| (e) Non-overlapping-label n_eff and q reporting | **use (mandatory)** | rows overstate evidence by about h/Delta |
| (f) Compute | not binding for any recommended family | all three recommended families: under 2 CPU-hours for an illustrative grid |

#### Planner pointers owned by M4 (reports/stage_e32_inputs/planner_research_soy_complex.md)

| # | Planner claim (line) | Status | Evidence and what differs |
|---|---|---|---|
| 1 | "Briola et al. (QF 2025) found deep LOB models help only for very active stocks" (lines 79-80) | **PARTLY VERIFIED** | Publication verified: Crossref gives "Deep limit order book forecasting: a microstructural guide", Quantitative Finance 25(7), 1101-1131, published 2025-07-03 (`crossref_briola_qf2025.json`); full text read from arXiv 2403.09267v4 (E.28 file, sha256 1642bd28...). The finding is about **tick size, not trading activity**: "we find that large-tick stocks are easier to predict, they are overall characterized by a stronger prediction signal, and their forecast performance is robust across prediction horizons", and "the observed behavioural clusters can ultimately be entirely traced back to tick-size-driven effects". All 15 stocks were "liquid" NASDAQ names. Activity enters only through how fast 10-100 updates happen in physical time (their Table 7), and the paper adds that "the utility of this signal is significantly dependent on the presence of low-latency hardware infrastructures" and that "high forecasting power does not necessarily correspond to actionable trading signals". The paper does not say "only for very active stocks". |
| 1b | "ZM is in the sparse regime" (line 80-81, same bullet) | **UNVERIFIED, possibly inverted** | Briola's "sparse LOB structure with empty levels" describes **small-tick** stocks ("This means that the corresponding stocks are characterized by a sparse LOB structure with empty levels"). A contract whose average spread is under about 1.5 ticks is large-tick in their classification ("if (ii) ⟨σ⟩ ≲ 1.5θ, we are dealing with a large-tick stock", E.28 2.8 section 4.3), and large-tick books were the MORE predictable class. ZM's average spread is not measured in anything I may read (no new statistic from data), so its class is open. The planner's conclusion (no deep models for minutes-to-hours labels) still holds, for a different reason: Briola's predictability is at 10-100 book updates (seconds), not minutes, and the sample arithmetic in (c) and (e) rules deep models out. |
| 2 | "no credible grain LOB ML study exists" (line 79) | **NOT REFUTED (absence after search; not proof)** | Searched: arXiv API 2 queries (`arxiv_q1_lob_grain.xml`, `arxiv_q2_commodity_lob_ml.xml`: 7 hits, none on grains); OpenAlex 4 queries (`openalex_oa1-4.json`, top 25 each); WebSearch 3 queries (results in this file's log section). The last three discovery queries surfaced nothing new, which meets the stopping rule. Closest items, none of them a credible grain LOB ML direction study: (i) "Evaluating the Effectiveness of Optimized LSTM and XGBoost Classifiers in High-Frequency Futures Market Prediction" (IGI Global book chapter, 2025, DOI 10.4018/979-8-3693-8186-1.ch014). The abstract (OpenAlex) covers five Chinese futures markets, including soybean, with "backtesting profits", and says XGBoost "demonstrates better stability and efficiency in more stable markets like Soybean and Rebar Futures". Abstract only [unverified]; data granularity and cost model unstated; an edited book chapter, not peer-reviewed journal work. (ii) Jin, Kearney, Li, Yang, "Order book price impact in the Chinese soybean futures market" (IJFE 2020, DOI 10.1002/ijfe.2439): statistical OFI, not ML; known from a search snippet only [unverified]. (iii) "Microstructure and high-frequency price discovery in the soybean complex" (J. Commodity Markets 2023, DOI 10.1016/j.jcomm.2023.100314): cointegration theory and empirics, not ML (abstract from OpenAlex). (iv) Daily or longer grain price forecasting with LSTM and XGBoost (Agricultural Economics 2024; JFM 2023, 22 commodities, monthly LightGBM; SJSU price-level LSTM). Wrong horizon, not LOB. |
| 3 | "Models: regularised linear or logistic, and shallow GBM (depth up to 3, monotone constraints where the sign is economically fixed). No deep LOB models." (lines 126-128) | **VERIFIED, with four qualifications** | Supported by the sample arithmetic (e.4: q <= 0.03 for linear, 0.09-1.2 for depth-3 GBM, 4-225 for sequence models at 15-240 min) and by the evidence in (a)-(c). Qualifications: (1) the probabilities must be calibrated (Platt on a separate block), because the trade rule is a probability threshold (section 0, a.3 item 3); (2) in LightGBM, state num_leaves <= 8 with max_depth 3 explicitly, and set min_data_in_leaf in independent-label units (b.3 item 1); (3) early stopping only on a purged inner block (b.5); (4) for minutes-ahead ZM direction very few signs are economically fixed, so monotone constraints apply only to features whose sign restates a declared hypothesis, and the constraint method is a counted choice. |

#### Gaps, failures and limits

- Not fetched: Tibshirani (1996) and Zou and Hastie (2005) originals. statweb.stanford.edu returned nothing to
  curl, and hastie.su.domains returned an anti-robot validation page (HTTP 403). An anti-bot page signals
  that automated access is not wanted, so Scrapling was not used there. The elastic-net and logistic
  equations are quoted from Friedman, Hastie and Tibshirani (2010, PMC copy) instead.
- Not fetched: Dangl and Halling (2012); Kolm and Westray, "Deep learning alpha signals from limit order
  books" (risk.net, paywalled; pointer only); Jin et al. (2020) full text; the IGI chapter full text.
- Not measured: ZM's average spread (it decides Briola's tick-size class, row 1b); the intra-day correlation
  rho of labels (design effect, e.2); online-logistic timing; statsmodels MarkovRegression timing
  (statsmodels is not installed; the E.28 numpy HMM timing is used).
- The trade-date count D = 816 rests on an assumed holiday list. DataFacts owns the real count.
- WebSearch calls used: 6 of 80. No budget notice was seen. Cost-notice hooks appeared; they are informational
  and did not affect the work.
- The compute probe used synthetic random data only. It is a timing measurement, not a result about ZM.

#### Fetch log summary
All pages are listed with UTC and PDT times and sha256 in `pages/M4_models/log.tsv`. WebSearch queries (for
the record): (1) '"limit order book" soybean OR corn OR wheat futures deep learning mid-price prediction'; (2)
'Dalian commodity exchange soybean meal high-frequency order book machine learning prediction tick data';
(3) 'CBOT soybean OR corn futures intraday high-frequency direction prediction machine learning LightGBM OR
LSTM order flow'; (4) Raftery DMA PDF lookup; (5) RLS forgetting-factor notes lookup; (6) Chinco et al. PDF
lookup.

Completed 2026-10-27 00:51 PDT (all sections (a)-(f), the verdict summary and the planner table written).

## M5a. Validation and overfitting control (CV, DSR, PBO, FWER/FDR)

Source file: reports/stage_e32_briefs/M5a_validation.md (sha256 dac50ace84142f638933c8ec37a39f1149e5d0f5a75f0f5488cce605a13e227b).

### Stage E.32 Part M5 (first half): validation and multiple-testing mathematics for the E.33 ZM discovery search

Worker: ValidationMath-OpusHigh (ROOT M5a_validation). Written 2026-10-27 from 00:25 PDT. Evidence pages and
log: reports/stage_e32_briefs/pages/M5a_validation/ (log.tsv). Scratch and calculators:
reports/stage_e32_briefs/work/M5a_validation/ (`M5a_calc.py` -> `M5a_calc_out.txt`, `M5a_calc2.py` ->
`M5a_calc2_out.txt`). No market data was read; every number below is arithmetic on the brief's standard ZM numbers,
on published formulas, or on synthetic random numbers with fixed seeds. Nothing was registered, N stays 538.

This section extends E.28 1b/1h (what the program already uses: Holm, BH, DSR, PBO/CSCV, effective N, nested CPCV)
and E.28 2.7 sections 5-6 (purged k-fold and CPCV basics: the three overlap conditions, the AFML 0.01T embargo, Li's
H + c tau rule, phi[N,k] = C(N-1, k-1), the CPCV table for N = 6..16). It does not repeat them: it adds the
horizon and session scaling, the discovery-length arithmetic (39 months), the DSR at the E.33 search sizes on
per-trade ZM statistics, and the FWER/FDR choice for a design that takes at most 3 candidates to one one-shot test.

#### 0. Shared inputs and the program's own code

##### 0.1 Standard quantities used in every worked example (assumptions marked)

| Quantity | Value | Where it comes from |
|---|---|---|
| ZM sigma_1m | 3.15 ticks | brief, from E.28 A0 Table 1 (2022-11..2023-10) |
| sigma_h under a random walk (ASSUMPTION: sigma_h = sigma_1m sqrt(h)) | 5 min 7.04, 15 min 12.20, 30 min 17.25, 60 min 24.40, 120 min 34.51, 240 min 48.80 ticks | `M5a_calc_out.txt` section (a); e.g. 3.15 x sqrt(15) = 3.15 x 3.873 = 12.20 |
| Market-order break-even c at Topstep | 1.59 ticks a round trip (mu*_mkt) | reports/stage_e28_ranking.md line 130: "\| 6 \| topstep \| ZM \| ... \| 0.59 \| 1.59 \| 0.86 \| 49.23 \|", columns mu*_lim, mu*_mkt, mu10K, cost/attempt (header line 123). The brief's "about 1.6" is this row. |
| Discovery trade dates T_d (2020-12-01..2024-02-29) | about 816 | 848 weekdays minus 32 assumed CBOT full closures (a holiday list I typed, not read from any data or CME page; error about +-3 dates) |
| Test-window trade dates (2017-05-01..2020-11-30, sealed) | about 899 | 936 weekdays minus an assumed 37 closures. Calendar arithmetic only; no sealed file was opened |
| Minutes per trade date | 765 overnight (19:00-07:45 CT) + 290 day (08:30-13:20 CT) = 1,055 | brief's session times [unverified here: the brief says verify; I did not fetch a CME page, which the E.32 CME rule forbids; DataFacts owns this] |
| 1-minute bar slots over discovery | 816 x 1,055 = 860,880 | arithmetic |
| Discovery length in years | 39 / 12 = 3.25 | arithmetic |

[MathReview C-1 (lead: accepted): row "Test-window trade dates": 37 closures is 6 too many; CBOT grain full closures in the window are 31 (identical date for date to the program's grains/hist2010 calendars), so the count is 936 weekdays - 31 = 905, not about 899. In f.3 (original lines 660-672) SR = z/sqrt(905) gives 0.0547/0.0707/0.0997 for z 1.645/2.128/3.0 (table has 0.0549/0.0710/0.1001), gross ticks unchanged to 2 d.p., power 0.998/0.981, 0.661/0.323, 0.373/0.116 (vs 0.998/0.98, 0.66/0.32, 0.37/0.12), and the summary (original line 758) reads 905 trades; no verdict moves.]

##### 0.2 The program's implementations the lead can call (read, not run)

All signatures and docstrings were read from source on 2026-10-27; none was executed by this worker.

| Function | File:line | Signature (abridged) | What the docstring and body say |
|---|---|---|---|
| `expected_max_sharpe` | funnel/multiple_comparisons.py:63 | `(n_trials: int, sharpe_variance: float) -> float` | "E[max SR] under the null that every trial has true SR = 0. Bailey & Lopez de Prado eq. (3). ``sharpe_variance`` is the variance of the Sharpe estimates ACROSS trials; with one trial the expected maximum is 0". Body: sqrt(V) x ((1 - gamma) Z^-1[1 - 1/N] + gamma Z^-1[1 - 1/(N e)]), gamma = 0.5772156649015329. (The paper's main-text number for this is eq. (1); eq. (3) is in Appendix A.1.) |
| `deflated_sharpe_ratio` | funnel/multiple_comparisons.py:81 | `(observed_sharpe, n_observations, n_trials, sharpe_variance, skewness=0.0, kurtosis=3.0) -> dict` | "Probability the true Sharpe exceeds 0, given the trial count and return shape. ``observed_sharpe`` and ``sharpe_variance`` must be on the SAME period basis as ``n_observations`` ... ``kurtosis`` is the raw fourth standardised moment, so a normal distribution is 3.0". Body: z = (SR - SR0) sqrt(n - 1) / sqrt(1 - skew SR + 0.25 (kurt - 1) SR^2); raises on a non-positive variance term. |
| `harvey_liu_zhu_verdict` | funnel/multiple_comparisons.py:116 | `(mean, stdev, n_observations, hurdle=HLZ_HURDLE=3.0) -> dict` | "t-stat of a mean against the HLZ (2016) hurdle: t > 3.0, not the usual 2.0." |
| `probability_of_backtest_overfitting` | funnel/multiple_comparisons.py:143 | `(performance: list[list[float]], n_blocks: int = 8) -> PBOResult` | rows = strategies, columns = blocks; all C(S, S/2) symmetric splits; OOS relative rank of the IS winner = (number strictly worse + 0.5)/n_strategies; PBO = share of logits <= 0. Fewer than 2 strategies returns NaN with degenerate=True. |
| `dsr`, `dsr_table`, `pbo` | screening/stage_e_verdict.py:197, :216, :231 | `dsr(mom, n_trials, variance)`; `dsr_table(moms, variance_over, n_trials, members)`; `pbo(series)` | `dsr_table`: "the Sharpe variance over ``variance_over`` (population variance)"; `pbo`: "CSCV PBO on 8 contiguous blocks of n_days // 8 dates" (N_PBO_BLOCKS = 8, line 92). Moments use the population sd and raw kurtosis. |
| `holm_alpha_k`, `holm_tier_a` | screening/stage_e_stats.py:288, :317 | `holm_alpha_k(k_clusters: int) -> float`; `holm_tier_a(pvalues: Mapping[str, float], k_clusters: int) -> HolmResult` | "alpha_k = 0.05 / K, K the number of families with a non-empty tested set ... K in 1..9"; "Holm step-down over one family's one-sided p-values ... at family-wise 0.05 / K". FAMILY_ALPHA = 0.05 (line 103), MAX_FAMILIES = MAX_CLUSTERS + 1 (line 108). This is exactly the planner's "Holm across families" structure, already coded. |
| `holm`, `benjamini_hochberg` | strategy/research/_d1f_decisions.py:195, :207 | `holm(pvalues, alpha=HOLM_FWE)`; `benjamini_hochberg(pvalues, q=BH_Q)` | "Holm step-down: sort ascending, reject while p_(i) <= alpha / (m - i + 1)."; "BH step-up: reject ranks 1..k, k the largest rank with p_(k) <= k q / m." (outside screening/; listed for completeness) |
| `pbo_cscv`, `sharpe_variance`, `dsr_at_n` | ml_route_v2/cpcv.py:735, :761, :769 | `pbo_cscv(perf, n_blocks=PBO_BLOCKS)`; `sharpe_variance(sharpes)`; `dsr_at_n(daily, n_trials, sharpe_variance)` | perf = dates x configurations, cut into n_blocks contiguous date blocks, then passed to the funnel function; "Population variance of the configurations' daily Sharpes"; "DSR of a daily series at N trials ... daily, unannualized". Constants (ml_route_v2/constants.py:128-132): N_BLOCKS = 6, N_TEST_BLOCKS = 2 ("15 splits, 5 paths"), EMBARGO_DATES = 1, PBO_BLOCKS = 16. |

Not in the code base (0 hits, as E.28 1b found): White's Reality Check, Hansen's SPA, Romano-Wolf stepdown,
Benjamini-Yekutieli, Storey q-values, probabilistic Sharpe ratio and minimum backtest length, ONC clustering.

Consistency check of the program's DSR against the paper (section (d) below): with the paper's own example inputs
the formula above gives DSR 0.9004 at N = 100, 0.9505 at N = 46, and 0.9505 at N = 88 under normal returns,
matching the three outcomes the paper prints in text ("only a 90% chance", "0.9505", "after N=88";
`bailey_lopezdeprado_2014_dsr.pdf.txt` lines 441-446). The example's inputs sit in equation images that pdftotext
lost; the values I used (N = 100, V = 1/2 annualised, T = 1,250, skew -3, kurtosis 10, SR 2.5 annualised) are
from my memory of the paper [unverified as text], and are confirmed only indirectly, by reproducing all three
printed outcomes.

#### (a) Purged and embargoed K-fold for overlapping labels of horizon h

##### a.1 Core idea
A row decided at time t carries a label that looks h minutes ahead, so its information spans [t, t + h]. A training
row whose span overlaps a test row's span shares realised prices with it (purge it); a training row just after a
test block has features built from the test block's prices (embargo it). E.28 2.7 section 5 gives the three overlap
conditions and the AFML 0.01T rule; this section adds how both cuts scale with h and with ZM's session calendar, and
shows that session-aligned folds make the purge free.

##### a.2 Equations
Notation: decision time t_i,0; label end t_i,1 = t_i,0 + h (clock or trading minutes, to be declared) or the trade
date's 13:20 CT close for "to close" labels; a test fold is the set of rows with decision times in [a_j, b_j]; its
label envelope is [a_j, b_j + h_max]; e is the embargo width.

1. Purge (LdP 2018, Solution #8; the three conditions reduce to one interval test for fixed-horizon labels): drop
   training row i if t_i,1 >= a_j and t_i,0 <= b_j + h_max, i.e. t_i,0 in [a_j - h, b_j + h_max].
2. Embargo (same source): "We can implement this embargo period h by setting Y_j = f[[t_j,0, t_j,1 + h]] before
   purging"; so additionally drop t_i,0 in (b_j + h_max, b_j + h_max + e]. Nothing is embargoed before a test block.
3. Rows lost per split (bar-level folds): about h before the block and h_max + e after it. Over k folds, the
   aggregate share of the sample cut is Li's (2026) "sanitization overhead k(2H + h)/T", which should be << 1
   (Li, Practical guidance item 2; there H is the label horizon and h the embargo).
4. Session alignment (worker's derivation, not from a source): if every fold is a union of whole CME trade dates
   (a trade date runs from 19:00 CT the evening before to 13:20 CT) and every label ends by its own trade date's
   13:20 close, then t_i,1 < a_j for every training row before the block and t_i,0 > b_j + h_max for every row
   after it, so the purge set is empty for any h up to "to close". The only cut left is the embargo, measured in
   trade dates. The 13:20 to 19:00 CT gap (340 minutes) is longer than every intraday horizon on the planner's list
   (5 to 240 minutes) [session times from the brief, unverified here].
5. Embargo width candidates, each in trade dates for the 39-month sample:
   - planner and program: 1 trade date (ml_route_v2 EMBARGO_DATES = 1);
   - AFML: h_emb ~ 0.01T with T the number of bars: 0.01 x 860,880 = 8,609 bar slots = 8,609 / 1,055 = 8.16 trade
     dates (and 0.01 x 816 trade dates = 8.16 if T is counted in dates: the rule is scale-free, 1% of the sample);
   - Li: H + c tau with c about 2 to 3, tau the dependence scale of the losses (not of raw returns);
   - feature lookback L (worker's conservative bound): e >= L makes every training row's features free of test-block
     prices; for a 5-20 session rolling crush beta (planner family 1) that is 5-20 trade dates.

##### a.3 Worked example (h = 60 minutes, k = 10 folds, 816 trade dates)
- Fold size: 816 / 10 = 81.6 trade dates. Training per split before cuts: 816 - 81.6 = 734.4 dates.
- sigma_60 under the random-walk assumption: 3.15 x sqrt(60) = 3.15 x 7.746 = 24.40 ticks (only to show what a
  60-minute label measures; it does not enter the split).
- Bar-level folds (cut at arbitrary minutes): purge removes 60 bar slots on each side of each test block, so
  2 x 60 = 120 slots per block; over 10 folds k x 2H / T = 10 x 120 / 860,880 = 0.00139 = 0.139% of the sample.
  Negligible.
- Session-aligned folds with labels clipped at 13:20: purge removes 0 rows.
- Embargo 1 trade date after each test block: per split 1 / 734.4 = 0.136% of training rows; aggregated over the
  10 folds k x 1 / 816 = 1.23%. Li's overhead with H = 60 min and h = 1 date: 0.139% + 1.23% = 1.36%
  (`M5a_calc_out.txt` line "k=10 H=60").
- Embargo by AFML 0.01T: 8.16 dates per split = 8.16 / 734.4 = 1.11% of training rows per split.
- Embargo by a 20-session feature lookback: 20 / 734.4 = 2.7% of training rows per split.
- At h = 240 minutes and k = 10 the bar-level purge share rises to 10 x 480 / 860,880 = 0.558%, still small.
- Check (independent bound): even the largest choice (20 dates per split) leaves 714 of 734 training dates (97.3%),
  so the choice of e is a leakage question, not a sample-size question, over 39 months.

How the cuts scale: purge rows grow linearly in h (2h per boundary) and vanish under session alignment; embargo is
set by dependence (tau, feature lookback), not by h. A session boundary is the natural fold edge because labels end
there. Labels that cross the 07:45-08:30 CT pause stay within one trade date, so they do not touch a fold edge, but
their horizon must be declared in clock or trading minutes (a 60-minute label from 07:30 ends at 08:30 in clock time
and at 09:15 in trading minutes). Labels that hold across the daily halt (close-to-next-open) cross trade dates and
need a 1-date purge.

##### a.4 Data it needs
Per row: decision timestamp, label end timestamp, trade date, instrument_id of the v.0 contract at t_i,0 and t_i,1
(ZM MBO bars aggregated to the decision grid), and the roll dates from the definitions schema. ZS/ZL MBP-1 features
use the same trade-date key. No outcome is needed to build the splits; they can be frozen and hashed before any
label is computed.

##### a.5 Leakage and look-ahead traps, each with a test
| Trap | Test that catches it |
|---|---|
| A label crosses a fold edge (overnight-hold labels, a fold cut mid-session) | Unit test on timestamps only: for every split assert max(t_i,1 over training rows before the block) < a_j and min(t_i,0 over training rows after) > b_j + h_max + e |
| A label straddles a v.0 roll (two contracts in one return) | Assert instrument_id(t_i,0) == instrument_id(t_i,1) for every labelled row; count and drop the rest before freezing |
| Transforms fitted on the full sample (z-scores, winsorization quantiles, the crush hedge ratio, PCA) | Perturbation test: scramble the prices inside one test block, rebuild the training-fold features, require them bit-identical |
| Features use data after t (bar close used at bar open; a USDA number before its release time) | Truncation test: recompute features on data cut at t for 1,000 random t and require equality with the full-data features; the program's planted-future canaries (E.28 1h V9) are the template |
| Embargo too short for slow features | Pre-declared embargo-sensitivity diagnostic: CV score at e = 1, 5 and 20 dates; a material drop as e grows flags leakage (report only; never used to select) |
| Inner tuning on the reporting folds | Nested CV, as ml_route_v2's nested CPCV already asserts (E.28 1h V5) |
| Leak through the protocol as a whole | E.28 2.7 section 5.6 placebo test H-CV0 (labels from another session must give AUC 0.5 +- 2 SE) |

[MathReview C-3 (lead: accepted): the timestamp-only purge test (row "A label crosses a fold edge") is only as good as the clock; add the row "Decision time and label end taken from different clocks" with the test "declare the clock (ts_recv, or ts_event + a fixed latency) in the protocol; assert both t_i,0 and t_i,1 are built from it; assert t_i,0 >= the ts_recv of the last feature input" (also applies to a.4, original line 116).]

##### a.6 Compute (ThinkPad, 39 months)
Building splits is negligible (816 dates, integer arithmetic). The cost is k fits per configuration: at E.28's
measured 6 s per LightGBM fit on 10^6 rows, 10 folds cost 60 s per configuration (200 configurations: 3.3 h;
5,000: 83 h). Linear or logistic fits are an order of magnitude cheaper [assumed, not measured here].

##### a.7 Verdict: USE (inside discovery, for model selection)
Folds = contiguous blocks of whole trade dates; labels clipped at their trade date's 13:20 close; purge asserted
(it should remove 0 rows); embargo 1 trade date as the frozen default with the 1/5/20-date sensitivity diagnostic.
This costs about 1% of training data and removes the label-overlap leak by construction. It does not address
non-stationarity (section c).

##### a.8 Evidence
| Claim | Source | Verbatim quote | File |
|---|---|---|---|
| Purging definition | Lopez de Prado 2018, JPM "10 reasons" (AFML ch. 7 summary) | "eliminate from the training set all observations whose labels overlapped in time with those labels included in the testing set. I call this process purging." | lopezdeprado_2018_10reasons_jpm.pdf.txt l.506-507 |
| Embargo only after the test; why | same | "we should eliminate from the training set observations that immediately follow an observation in the testing set. I call this process embargo. The embargo does not need to affect training observations prior to a test" | same, l.515-518 |
| 0.01T rule | same | "A small value h ≈ .01T, where T is the number of bars, often suffices to prevent all leakage." | same, l.522-523 |
| Gap unit and overhead | Li 2026, arXiv 2609.29530 (single-author preprint, not peer reviewed) | "All gaps/purges/embargoes should be denominated in H + cτ with c ≈ 2–3."; "Check that the sanitization overhead k(2H + h)/T ≪ 1; otherwise reduce k." | li_2026_arxiv_2609_29530.pdf.txt l.742, l.747-748 |
| Blocked CV is fine for stationary series | Cerqueira, Torgo, Mozetic 2020, Machine Learning (arXiv 1905.11744) | "empirical experiments suggest that cross-validation approaches can be applied to stationary time series" | cerqueira_torgo_mozetic_2020_arxiv_1905_11744.pdf.txt l.35-36 |
| AFML ch. 7 book text itself | Lopez de Prado 2018, AFML | not fetched (no open copy); the JPM summary above is the author's own condensed version [book chapter unverified] | none |

Stopping rule: 3 full-text sources read on this topic (LdP 2018, Li 2026, Cerqueira et al. 2020) plus E.28's two;
the Bergmeir-Hyndman-Koo note could not be fetched (403 and a non-PDF page, logged).

#### (b) Combinatorial purged cross-validation (CPCV)

##### b.1 Core idea
Cut the discovery sample into N_g contiguous groups, test on every set of k groups and train (purged, embargoed) on
the rest, then stitch the test predictions into phi backtest paths that each cover the whole sample once. E.28 2.7
section 6 already gives the counts and the N = 6..16 table; this section adds what the path-Sharpe distribution does
and does not measure, the 39-month numbers, and whether the E.33 search can afford it.

##### b.2 Equations
- Splits: C(N_g, k) = N_g! / (k! (N_g - k)!). Paths: phi[N_g, k] = (k / N_g) C(N_g, k) = C(N_g - 1, k - 1)
  (LdP 2018: "phi[N,k] = (k/N) C(N, N-k)", l.583-588; same number).
- Training fraction per split: (N_g - k)/N_g, minus the embargo after each test group that is not the last group.
- Path Sharpe: for path p, r_p,t is the stitched out-of-sample net P&L on date t (t = 1..T_d); SR_p = mean(r_p)/sd(r_p)
  on the daily basis; the CPCV "distribution" is {SR_1, ..., SR_phi}.
- What the dispersion measures (worker's derivation): every path covers the same T_d dates, so the return-sampling
  noise is common to all paths; paths differ only in which training set produced each group's forecasts. The
  spread across paths therefore measures model instability across training sets, not the sampling error of the
  Sharpe ratio. Under a true SR of 0 the sampling error of any one path's daily SR is still about 1/sqrt(T_d), and
  averaging the phi paths does not shrink it.

##### b.3 Worked example (816 trade dates)
| N_g | k | splits | paths | group size (dates) | training fraction |
|---|---|---|---|---|---|
| 6 | 2 | 15 | 5 | 136.0 | 0.667 |
| 8 | 2 | 28 | 7 | 102.0 | 0.750 |
| 10 | 2 | 45 | 9 | 81.6 | 0.800 |
| 10 | 3 | 120 | 36 | 81.6 | 0.700 |
| 12 | 2 | 66 | 11 | 68.0 | 0.833 |
| 16 | 2 | 120 | 15 | 51.0 | 0.875 |

Row N_g = 10, k = 2 by hand: C(10,2) = 10 x 9 / 2 = 45 splits; phi = (2/10) x 45 = 9 = C(9,1); groups 816 / 10 =
81.6 dates; training 8 groups = 652.8 dates, minus at most 2 embargo dates (one after each test group) = 650.8.
Check: 45 splits x 2 test groups = 90 group-tests = 10 groups x 9 tests each.

Null spread of one path's Sharpe: 1/sqrt(816) = 1/28.57 = 0.0350 per day, or 0.0350 x sqrt(252) = 0.556 annualised.
So even a perfectly stable model with no edge shows path Sharpes centred anywhere in roughly +-1.1 annualised (2 sd)
from the common sampling draw; a tight CPCV path distribution around 1.0 is not evidence by itself.

Compute (fits = configurations x C(N_g, k); E.28 measured about 6 s per LightGBM fit on 10^6 rows; 0.5 s is an
assumption for a linear or logistic fit):

| Configurations | N_g = 6, k = 2 (15 fits each) | N_g = 10, k = 2 (45 fits each) |
|---|---|---|
| 200 | 3,000 fits: 5.0 h at 6 s; 0.42 h at 0.5 s | 9,000 fits: 15.0 h; 1.25 h |
| 1,000 | 15,000: 25.0 h; 2.08 h | 45,000: 75.0 h; 6.25 h |
| 5,000 | 75,000: 125 h; 10.4 h | 225,000: 375 h; 31.3 h |

Rows: one decision per minute over discovery is about 860,880 rows, close to E.28's 10^6 timing; one decision per
15 minutes in the day session only is 816 x 290 / 15 = 15,776 rows, where fits are much cheaper. Memory: 860,880
rows x 100 float32 features = 344 MB per copy, within 14 GB.

##### b.4 Data it needs
The same row table as (a) (decision time, label end, trade date, net label) plus, for the path Sharpe, a daily net
P&L per configuration and path (zeros on no-trade dates, the program's convention).

##### b.5 Leakage traps and tests
| Trap | Test |
|---|---|
| Reading the path distribution as phi independent replications (they share data and most of their training sets) | Report the across-path spread next to 1/sqrt(T_d); never compute a t-stat across paths |
| Selecting hyperparameters on the same CPCV used to report | Nested CPCV (ml_route_v2 V5) or select on CPCV and report only on the sealed test |
| Embargo omitted for interior test groups (a test group with training on both sides) | The split unit test of (a), run on every one of the C(N_g, k) splits |
| A configuration with no eligible model in some split silently scored as 0 | Count and report splits with no model per configuration (ml_route_v2 already records `selected = None`) |

##### b.6 Compute
See b.3. CPCV on every configuration is affordable for linear models up to about 1,000 configurations and for GBMs
only up to about 200 (N_g = 10) on one machine overnight under the CLAUDE.md limits (half the cores, one heavy job).

##### b.7 Verdict: MAYBE (finalists only)
Use plain purged K-fold or walk-forward to score all configurations, and CPCV (or the program's CSCV/PBO on the daily
P&L matrix, which needs no refits) only on the final shortlist, as a model-stability diagnostic declared in advance.
Its Sharpe distribution measures model instability, not sampling error, so it is never the test.

##### b.8 Evidence
| Claim | Source | Verbatim quote | File |
|---|---|---|---|
| Path count formula | LdP 2018 JPM | "from k-sized testing sets on N groups we can backtest a total number of paths phi[N, k]" (formula image garbled; restated in E.28 2.7 section 6.2) | lopezdeprado_2018_10reasons_jpm.pdf.txt l.583-588 |
| Paths grow with N and k | same | "The number of paths phi[N, k] increases with N -> T and with k -> N/2." | same, l.604-605 |
| Claimed advantage | same | "A key advantage of CPCV is that it allows us to derive a distribution of Sharpe ratios, as opposed to a single (likely overfit) Sharpe ratio estimate." | same, l.605-606 |
| CPCV does not fix non-stationarity | Li 2026 | "Stationarity credible, goal is model comparison/tuning → purged k-fold + embargo (or CPCV)" | li_2026_arxiv_2609_29530.pdf.txt l.745 |
| CPCV motivated by coverage of regimes | same | "it is the motivation for the multi-path coverage of combinatorial purged cross-validation" | same, l.524-525 |
| CPCV superior on synthetic data | Arian, Norouzi Mobarekeh, Seco 2024 | not retrieved (E.28 2.7 section 6.8: citing-paper quote only) [unverified] | none |

#### (c) Walk-forward, anchored and rolling, under a regime break

##### c.1 Core idea
Walk-forward trains only on data before each test block, so every decision is causal. Anchored (expanding) folds
keep all history; rolling folds keep a fixed window W and forget older data. Under drift, Li (2026) proves expanding
walk-forward is the causal frontier, and an empirical study of 62 real series finds order-preserving methods more
accurate than CV when the series are non-stationary. Its cost: one historical path, fewer test months, early folds
trained on little data.

##### c.2 Equations
Fold i (i = 1..F) tests on [s_i, s_i + Delta) with s_i = s_1 + (i - 1) Delta, and trains on
- anchored: [t_0, s_i - g);  rolling: [s_i - g - W, s_i - g);
- g = purge + embargo gap, in trade dates (section a: 1 date when labels end by the 13:20 close).
- Number of folds: F = floor((L - W_1)/Delta), L the sample length, W_1 the first training length; out-of-sample
  share beta = F Delta / L.
- Li (2026) Proposition 7: (i) the variance of the average test loss is about sigma_inf^2 / (beta T); (ii) under
  non-stationarity, a risk difference Delta_r confined to the uncovered part of the sample gives worst-case error at
  least (1 - beta) Delta_r / 2, which no estimator can remove. Coverage beta is what walk-forward pays with.

##### c.3 Worked example (39 months, step 3 months)
| First training length | Step | Test folds F = floor((39 - W_1)/3) | Test months | beta |
|---|---|---|---|---|
| 12 months | 3 | floor(27/3) = 9 | 27 | 27/39 = 0.69 |
| 18 months | 3 | floor(21/3) = 7 | 21 | 0.54 |
| 24 months | 3 | floor(15/3) = 5 | 15 | 0.38 |
| 12 months | 6 | floor(27/6) = 4 | 24 | 0.62 |

With W_1 = 12 months: 9 quarterly folds of about 816 x 3/39 = 62.8 trade dates each; anchored training grows from
about 251 to about 754 dates; a rolling W = 12 months keeps about 251 dates. Check: 9 x 3 + 12 = 39 months.

The planner's "positive results in at least two-thirds of quarters" (not one of my pointers; arithmetic only): with
9 test quarters, at least 6 positive. If quarterly signs were independent fair coins under the null, P(>= 6 of 9) =
(C(9,6) + C(9,7) + C(9,8) + C(9,9)) / 2^9 = (84 + 36 + 9 + 1)/512 = 130/512 = 0.254. A null rule passes that filter
one time in four, so it is a stability description, not a significance test.

Direction of the final test (worker's observation for the lead): the sealed test window 2017-05..2020-11 lies BEFORE
the discovery window 2020-12..2024-02. The one-shot test therefore asks whether a rule fitted on later data works on
earlier data. A forward walk-forward inside discovery estimates the opposite direction. LdP (2018) argues that the
two directions are equally legitimate ("it is as easy to overfit a walk-forward backtest as to overfit a
walk-backward backtest"). A mirror diagnostic is cheap: a reversed anchored walk-forward inside discovery (train on
the last 12 months, test the preceding quarters moving backward), reported next to the forward one. If the planner's
expected regime break (renewable-diesel oil share after 2021 versus trade war and Covid in 2017-20) is real, the
reversed folds are the closer rehearsal of the sealed test. This is a suggestion, not a source claim.

##### c.4 Data it needs
The trade-date calendar of discovery, the row table of (a), and roll dates. Rolling windows need W declared in
trade dates.

##### c.5 Leakage traps and tests
| Trap | Test |
|---|---|
| Hyperparameters chosen by looking at walk-forward results, then the same results reported | Nested: tune inside each training window only (Li guidance item 3: "rehearse the tuning process inside the rolling procedure"); the frozen pipeline is re-run end to end |
| Gap g omitted at fold starts | Same timestamp unit test as (a) on every fold |
| Fold boundaries chosen after seeing performance (moving the start to dodge a bad quarter) | Fold dates frozen and hashed with the protocol; a shift test (all boundaries moved by 5 dates) reported alongside |
| Learning-curve bias: early folds starved, the average understates the final model | Report per-fold score against training size (Li Proposition 6 / guidance item 3), not only the mean |

##### c.6 Compute
F fits per configuration (9 for the table's first row), less than 10-fold CV and 5x less than CPCV with N_g = 10,
k = 2. At 6 s per GBM fit: 200 configurations x 9 = 1,800 fits = 3.0 h; 5,000 x 9 = 45,000 fits = 75 h.

##### c.7 Verdict: USE (as the reported discovery estimate); K-fold for tuning only if stationarity is credible
The planner expects a regime break and the final test runs on a different era, which is the case where both Li and
Cerqueira et al. favour order-preserving validation. Recommended for the lead to weigh: expanding walk-forward with
quarterly steps and a 1-date gap as the discovery estimate; the reversed walk-forward as a pre-declared diagnostic;
purged K-fold (a) only inside each training window for tuning.

##### c.8 Evidence
| Claim | Source | Verbatim quote | File |
|---|---|---|---|
| Use expanding walk-forward under non-stationarity | Li 2026 (preprint) | "Non-stationarity feared, or “expected live performance” to be quoted → expanding walk-forward (it is the causal frontier, Corollary 3); report the per-fold-versus-training-size curve rather than a single average" | li_2026_arxiv_2609_29530.pdf.txt l.750-752 |
| Uncovered regimes cannot be repaired | same | "a regime you never tested may hide a ∆, and no statistical technique conjures information out of unobserved intervals" | same, l.522-523 |
| Order-preserving methods win on real non-stationary series | Cerqueira, Torgo, Mozetic 2020 | "in real-world scenarios, when different sources of non-stationary variation are at play, the most accurate estimates are produced by out-of-sample methods that preserve the temporal order of observations" | cerqueira_torgo_mozetic_2020_arxiv_1905_11744.pdf.txt l.36-39 |
| Repeated hold-out recommended | same | "out-of-sample applied in multiple testing periods (Rep-Holdout) is recommended" | same, l.1256-1261 |
| WF is one overfit-prone path; walk-backward equally valid | LdP 2018 JPM | "First, a single scenario is tested (the historical path), which can be easily overfit"; "it is as easy to overfit a walk-forward backtest as to overfit a walk-backward backtest" | lopezdeprado_2018_10reasons_jpm.pdf.txt l.538-544 |
| WF's advantage | same | "History is a filtration; hence, using trailing data guarantees that the testing set is out-of-sample (no leakage), as long as purging has been properly implemented." | same, l.535-536 |

Stopping rule: three full-text sources (Li, Cerqueira et al., LdP 2018); no source compared forward and backward
validation on futures data; I found none in two arXiv-style queries and stopped.

#### (d) The deflated Sharpe ratio at the search's N

##### d.1 Core idea
The best of N trials has a positive expected Sharpe ratio even when every trial is worthless. The DSR (Bailey and
Lopez de Prado 2014) asks how likely the selected strategy's true Sharpe ratio is above zero once the benchmark is
raised from 0 to that expected maximum, and once the standard error is widened for skew, fat tails and a short
sample. The program already computes it (section 0.2). New here: what it implies on ZM per-trade numbers at
N = 538 + 200, 538 + 1,000 and 538 + 5,000 over 39 months, which effective N goes with which variance, and the
per-trade versus annualised bookkeeping.

##### d.2 Equations
Symbols: SR_hat the selected strategy's Sharpe ratio on its own sampling basis (per trade, or per trade date with
zeros on no-trade dates); T the number of observations on that basis; gamma3 its skewness; gamma4 its raw kurtosis
(normal = 3); V = V[{SR_hat_n}] the variance of the Sharpe estimates across the trials, same basis; N the number of
(independent) trials; gamma = 0.5772 the Euler-Mascheroni constant; Z the standard normal CDF.

1. Expected maximum (BLdP 2014 eq. (1); the "False Strategy theorem" in LdP and Lewis 2019 section 6):
   E[max_n SR_hat_n] ~ sqrt(V) x e(N),  e(N) = (1 - gamma) Z^-1[1 - 1/N] + gamma Z^-1[1 - 1/(N e)].
2. DSR (BLdP 2014 eq. (2)):
   DSR = Z[ (SR_hat - SR0) sqrt(T - 1) / sqrt(1 - gamma3 SR_hat + ((gamma4 - 1)/4) SR_hat^2) ],  SR0 = sqrt(V) e(N).
   (Symbols lost in pdftotext; the form matches funnel/multiple_comparisons.py:81 and is confirmed by reproducing the
   paper's three printed outcomes, section 0.2.)
3. Null calibration (worker's derivation): for T iid observations with true SR 0, Var(SR_hat) ~ 1/T (to first order,
   normal returns). Setting V = 1/T and sqrt(T - 1) ~ sqrt(T), DSR >= 0.95 becomes
   SR_hat sqrt(T) >= e(N) + 1.645 sqrt(D),  D = 1 - gamma3 SR_hat + ((gamma4 - 1)/4) SR_hat^2 ~ 1 for per-trade SR ~ 0.1-0.3.
   So the DSR bar is a t-statistic bar t* ~ e(N) + 1.645, independent of T and of the horizon.
4. Basis invariance: if SR_hat and sqrt(V) are both multiplied by sqrt(q) (annualising with q observations a year) then
   T must become years, and z is unchanged. In annual units the bar is SR*_ann ~ t* / sqrt(Y), Y the sample in years.
   Mixing bases (an annualised SR_hat with T counted in trades, or a daily V with a per-trade SR_hat) is the error the
   program's docstring warns against and LdP-Lewis 2019 section 8.2 corrects ("in order to match the frequency").
[MathReview C-2 (lead: accepted): the invariance claim is not true beyond first order: sqrt(T/q - 1) is not sqrt(T - 1)/sqrt(q) at Y = 3.25 years (1.50 vs 1.80), and D's SR^2 term scales by q (annual D = 1 + SR_ann^2/2 = 4.6 at SR_ann 2.68); per-trade SR 0.1689, T 816, N 738, V 1/T gives z 1.644, DSR 0.950, while the same inputs annualised (SR 2.676, V x 251, T 3.25) give z 0.644, DSR 0.74 (monthly basis DSR 0.924). Replace the sentence with the rule: compute DSR on the native basis (per trade or daily with zeros) and never rescale inside the formula; SR*_ann ~ t*/sqrt(Y) stays valid as a display conversion of the t-bar only.]
5. Effective number of trials, three published definitions:
   - BLdP 2014 Appendix 3 eq. (9): N_hat = rho_bar + (1 - rho_bar) M, rho_bar the average off-diagonal correlation
     of the M trials' returns (eq. (8)); implemented, never run, in ml_route/accounting.py (E.28 1b M5).
   - ONC (LdP and Lewis 2019 section 8): cluster the trials on the distance D_ij = sqrt((1 - rho_ij)/2) with k-means
     and silhouette scores; E[K] = number of clusters; form each cluster's minimum-variance portfolio
     w_k = Sigma_k^-1 1 / (1' Sigma_k^-1 1); annualise each cluster Sharpe (aSR_k = SR_k sqrt(Frequency_k),
     Frequency_k = T_k / Years_k); E[V[{SR_k}]] = V[{aSR_k}] / Frequency_k*, k* the selected strategy's cluster.
   - Participation ratio (Nikolopoulos 2026, arXiv 2604.15531, preprint, eq. (4)): K_eff = (tr Sigma)^2 / ||Sigma||_F^2
     = K^2 / sum_ij rho_ij^2.
6. Minimum backtest length (Bailey, Borwein, Lopez de Prado, Zhu 2014, Theorem 3.1, eq. (3.2)), years needed for the
   expected maximum annualised Sharpe of N null trials to equal E[max_N]: MinBTL ~ (e(N) / E[max_N])^2 < 2 ln(N) / E[max_N]^2.

##### d.3 Worked examples

**(i) e(N) at the three search sizes** (`M5a_calc_out.txt`, section "(d) e(N)"):

| N | 1 - 1/N | Z^-1 | N e | Z^-1[1 - 1/(N e)] | e(N) = 0.4228 x col3 + 0.5772 x col5 | Monte Carlo mean max (4,000 draws) | sqrt(2 ln N) |
|---|---|---|---|---|---|---|---|
| 538 + 200 = 738 | 0.998645 | 2.9988 | 2,006.1 | 3.2914 | 3.1677 | 3.1543 | 3.6343 |
| 538 + 1,000 = 1,538 | 0.999350 | 3.2159 | 4,180.7 | 3.4926 | 3.3756 | 3.3596 | 3.8310 |
| 538 + 5,000 = 5,538 | 0.999819 | 3.5670 | 15,053.8 | 3.8211 | 3.7137 | (not run) | 4.1520 |

Check: 0.4228 x 2.9988 + 0.5772 x 3.2914 = 1.2679 + 1.8998 = 3.1677. The approximation sits 0.4-0.5% above the
simulated mean (MC standard error about 0.006), so it is slightly conservative. Seven and a half times more trials
(738 to 5,538) raise the bar by only 3.7137 / 3.1677 = 1.17 times.

**(ii) The DSR bar on ZM per-trade statistics, null-calibrated V = 1/T.** Assumptions: market-order round trip
c = 1.59 ticks; sigma_15 = 12.20 and sigma_60 = 24.40 ticks (random walk); trades do not overlap; gamma3 and
gamma4 are illustrative, not measured. One cell by hand, h = 15 min, one trade per trade date (T = 816), N = 738,
gamma3 = 0, gamma4 = 3:
- sqrt(V) = sqrt(1/816) = 0.035007; SR0 = 0.035007 x 3.1677 = 0.1109 per trade.
- Solve (SR - 0.1109) x sqrt(815) / sqrt(1 + 0.5 SR^2) = 1.645: SR* = 0.1689. Check: (0.1689 - 0.1109) x 28.548 /
  sqrt(1 + 0.5 x 0.1689^2) = 0.0580 x 28.548 / 1.0071 = 1.644.
- t* = 0.1689 x sqrt(816) = 0.1689 x 28.566 = 4.83 (versus e(N) + 1.645 = 4.81).
- Net edge needed = SR* x sigma_15 = 0.1689 x 12.20 = 2.06 ticks a trade; gross = 1.59 + 2.06 = 3.65 ticks.
- Annualised: q = 816 / 3.25 = 251 trades a year; SR*_ann = 0.1689 x sqrt(251.1) = 0.1689 x 15.85 = 2.68 = 4.83 / sqrt(3.25).

| h | trades T (per year) | N | SR0 per trade | SR* per trade (gamma4 3 / 8 / skew -0.5 & 8) | t* | gross edge needed, ticks (gamma4 3) | SR*_ann |
|---|---|---|---|---|---|---|---|
| 15 | 408 (126) | 738 | 0.1568 | 0.2395 / 0.2424 / 0.2473 | 4.84 | 4.51 | 2.68 |
| 15 | 408 (126) | 1,538 | 0.1671 | 0.2499 / 0.2531 / 0.2581 | 5.05 | 4.64 | 2.80 |
| 15 | 408 (126) | 5,538 | 0.1839 | 0.2668 / 0.2704 / 0.2758 | 5.39 | 4.85 | 2.99 |
| 15 | 816 (251) | 738 | 0.1109 | 0.1689 / 0.1699 / 0.1724 | 4.83 | 3.65 | 2.68 |
| 15 | 816 (251) | 1,538 | 0.1182 | 0.1762 / 0.1774 / 0.1799 | 5.03 | 3.74 | 2.79 |
| 15 | 816 (251) | 5,538 | 0.1300 | 0.1881 / 0.1894 / 0.1921 | 5.37 | 3.89 | 2.98 |
| 15 | 3,264 (1,004) | 738 | 0.0554 | 0.0843 / 0.0844 / 0.0850 | 4.82 | 2.62 | 2.67 |
| 15 | 3,264 (1,004) | 5,538 | 0.0650 | 0.0939 / 0.0940 / 0.0947 | 5.36 | 2.74 | 2.97 |
| 60 | 816 (251) | 738 | 0.1109 | 0.1689 / 0.1699 / 0.1724 | 4.83 | 5.71 | 2.68 |
| 60 | 816 (251) | 5,538 | 0.1300 | 0.1881 / 0.1894 / 0.1921 | 5.37 | 6.18 | 2.98 |
| 60 | 3,264 (1,004) | 5,538 | 0.0650 | 0.0939 / 0.0940 / 0.0947 | 5.36 | 3.88 | 2.97 |

Reading: (1) the bar is t ~ 4.8 to 5.4 whatever the horizon or frequency; (2) skew and kurtosis barely move it at
per-trade SR of 0.1-0.3 (at most +2%), unlike the BLdP example where daily skew -3 and kurtosis 10 mattered;
(3) the only lever is the number of independent trades: four non-overlapping 15-minute trades a day bring the gross
edge needed down to 2.6-2.7 ticks, one a day needs 3.6-3.9 ticks, one every other day 4.5-4.9 ticks; (4) the
annualised bar of about 2.7-3.0 equals the expected best null Sharpe plus a margin: with 3.25 years the best of N
null trials shows e(N)/sqrt(3.25) = 1.76 (N = 738), 1.87 (1,538), 2.06 (5,538) annualised.

**(iii) A fixed candidate at the three N** (h = 15, T = 816, gamma4 = 8, V = 1/T): gross 3.0 ticks gives net SR
(3.0 - 1.59)/12.20 = 0.1156 a trade and t = 0.1156 x 28.566 = 3.30 (it passes HLZ t > 3.0), but DSR = 0.589 (N = 538),
0.553 (738), 0.471 (1,538), 0.342 (5,538). Gross 3.5 ticks (t = 4.47): DSR 0.914, 0.899, 0.858, 0.771. None reaches 0.95.

**(iv) Per-trade versus daily-with-zeros** (synthetic, 2,000 samples of 816 days, a trade on half the days, per-trade
SR 0.08, t5 noise): mean z on the per-trade series 1.640, on the daily series with zeros 1.635, correlation 1.0000. The
daily Sharpe is about sqrt(p) times the per-trade Sharpe (sqrt(0.5) x 0.08 = 0.0566) and T is about 1/p times larger,
so z = SR sqrt(T) is unchanged to first order; the zero-inflated series has kurtosis about gamma4 / p (9 / 0.5 = 18
for t5), which enters D only through ((gamma4 - 1)/4) SR^2 and stays small. The program's daily convention is
therefore safe, provided V is also computed on daily Sharpes (it is: `dsr_table`, `sharpe_variance`).

**(v) Which effective N goes with which V** (synthetic, M = 1,000 trials, T = 816, 400 repetitions; `M5a_calc3_out.txt`):

| Correlation structure | Mean max SR (simulated) | sqrt(V_emp) e(M) | sqrt(V_emp) e(K) | sqrt(1/T) e(M) | K_eff (participation) |
|---|---|---|---|---|---|
| one factor, rho 0.5 | 0.0803 | 0.0803 | n/a | 0.1140 | 4.0 |
| one factor, rho 0.8 | 0.0521 | 0.0509 | n/a | 0.1140 | 1.6 |
| 50 clusters of 20, within 0.95 | 0.0927 | 0.1131 | 0.0791 | 0.1140 | 55.1 |
| 200 clusters of 5, within 0.9 | 0.1066 | 0.1138 | 0.0967 | 0.1140 | 235.8 |

Reading (worker's derivation, checked by this simulation): the cross-trial variance V_emp already shrinks by (1 - rho)
under a common factor (simulated V 0.000619 versus (1 - 0.5)/816 = 0.000613, `M5a_calc2_out.txt`), so the
empirical-V benchmark with the literal count M is exact there; combining V_emp with a reduced N (eq. (9) gives
N_hat = 500.5 at rho 0.5, the participation ratio 4.0) double-discounts and is anti-conservative. Under cluster
structure the truth lies between sqrt(V_emp) e(M) (conservative) and sqrt(V_emp) e(K) (slightly anti-conservative).
Rule for the lead to weigh: either the empirical V with the literal N (the program's current pairing, conservative
in both structures) or the null V = 1/T with an effective N, never the empirical V with an effective N.

Effective N by eq. (9), with the 538 earlier trials added literally:

| M (E.33 configurations) | rho_bar 0.3 | 0.5 | 0.7 | 0.9 |
|---|---|---|---|---|
| 200 | 140.3 (N 678, e 3.143) | 100.5 (639, 3.125) | 60.7 (599, 3.106) | 20.9 (559, 3.086) |
| 1,000 | 700.3 (1,238, 3.315) | 500.5 (1,039, 3.266) | 300.7 (839, 3.205) | 100.9 (639, 3.126) |
| 5,000 | 3,500.3 (4,038, 3.633) | 2,500.5 (3,039, 3.559) | 1,500.7 (2,039, 3.453) | 500.9 (1,039, 3.266) |

Even the most generous discount moves e(N) by at most 12% (3.7137 to 3.266 at M = 5,000); the cumulative 538 keeps
the floor near e(538) = 3.07.

**(vi) MinBTL**: at E[max] = 1 annualised, N = 45 needs (e(45))^2 = 5.00 years (the paper's own "if only 5 years of
data are available, no more than 45 independent model configurations should be tried"); N = 738 needs 10.0 years,
1,538 needs 11.4, 5,538 needs 13.8. With 3.25 years, the null maximum is 1.76-2.06 annualised (iii above).

##### d.4 Data it needs
Per configuration: the daily net P&L over discovery (zeros on no-trade dates), from which SR_hat, skew, raw kurtosis
and T; the cross-configuration population variance of the daily Sharpes (V); the full daily matrix (dates x
configurations) for rho_bar, ONC or K_eff. Per-trade P&L only for the overlap diagnostic below.

##### d.5 Leakage traps and tests
| Trap | Test |
|---|---|
| Basis mismatch (annualised SR with T in trades; daily V with a per-trade SR) | Assert one basis in the call (the program's docstring requires it); unit test: DSR unchanged when every input is rescaled consistently |
| Overlapping trades (decisions every 15 minutes, 60-minute holds) inflate T | Compute z on daily-aggregated P&L and on per-trade P&L; a per-trade z more than about 1.2 times the daily z flags overlap; the daily series is the one reported |
| N undercounted (exploratory runs, discarded configurations, re-runs with a bug fix) | Count from the append-only trial registry (E.28 1b M6) and require it to equal the number of distinct configuration hashes in the run logs |
| V computed over survivors only, or over a hand-picked subset | `dsr_table(variance_over=...)` must receive every configuration in the search; assert len(variance_over) == M |
| Empirical V paired with an effective N (double discount, (v) above) | Declare one pairing in the protocol |
| Long and short mirrors of one signal counted as two trials (V and N both inflated, and the sign chosen after the fact) | Fix each signal's sign economically before the run, or count the pair as one trial and report the sign rule |
| Excess kurtosis passed where raw is expected | Unit test: a normal sample must give kurtosis near 3 into `deflated_sharpe_ratio` |
| V, moments or N touched by the sealed window | All inputs from discovery only; the sealed seal check (reports/stage_e32_briefs/seal/) before any DSR run |

##### d.6 Compute
Negligible: moments and a variance over M daily series (816 x 5,000 floats = 33 MB); ONC's k-means over a 5,000 x 5,000
correlation matrix (200 MB in float64) with repeated restarts is minutes on the ThinkPad [estimate].

##### d.7 Verdict: USE (it is the program's bar; the lead sets the threshold)
On ZM it means t ~ 4.8-5.4 on the discovery sample, i.e. an annualised Sharpe of about 2.7-3.0 over 39 months, or a
gross edge of 2.6-3.9 ticks a 15-minute trade at one to four trades a day. Report DSR at the literal cumulative N with
the empirical V (current pairing) and, beside it, the eq. (9) and ONC variants, as E.2b's RA-3 already specified for
the ML route (ml_route/accounting.py:25-31).

##### d.8 Evidence
| Claim | Source | Verbatim quote | File |
|---|---|---|---|
| Expected maximum after N independent trials | Bailey and Lopez de Prado 2014, JPM | "Appendix 1 proves that, under these assumptions, the expected maximum of { ̂ } after independent trials can be approximated as:" (eq. (1), symbols lost) | bailey_lopezdeprado_2014_dsr.pdf.txt l.312-316 |
| Definition of the DSR inputs | same | "[{ ̂ }] is the variance across the trials’ estimated SR and N is the number of independent trials. We also use information concerning the selected strategy: ̂ is its estimated SR, T is the sample length, ̂ is the skewness ... and ̂ is the kurtosis" | same, l.373-379 |
| What DSR deflates | same | "DSR deflates SR by taking into consideration five additional variables: The non-Normality of the returns ( ̂ ̂ ), the length of the returns series ( ), the variance of the SRs tested ( [{ ̂ }]), as well as the number of independent trials" | same, l.389-392 |
| Paper's example outcomes | same | "there is only a 90% chance that the true SR associated with this strategy is greater than zero"; "after running only N=46 independent trials ... would have been 0.9505"; "If the strategy had exhibited Normal returns ( ̂ ̂ ), ̂ after N=88 independent trials" | same, l.440-446 |
| Effective N interpolation | same, Appendix 3 | "Suppose that we run M trials, where only N trials are independent, N<M."; eq. (9) image lost; restated in ml_route/accounting.py:33-43 | same, l.625, l.655-658 |
| False Strategy theorem | Lopez de Prado and Lewis 2019, QF (SSRN 3167017 working-paper copy) | "unless max_k{SR_k} ≫ E[max_k{SR_k}], the discovered strategy is likely to be a false positive" | lopezdeprado_lewis_2019_onc_ssrn3167017.pdf.txt l.344-345 |
| ONC clusters as the trial count | same | "we consider clustering the strategies and using those clusters as a proxy" | same, l.411-412 |
| Frequency matching of V | same | "We need to express the estimated variance of clustered trials in terms of the frequency of the selected strategy, in order to match the frequency of the ̂ SR estimate used by the DSR equation" | same, l.573-575 |
| Participation-ratio K_eff | Nikolopoulos 2026, arXiv 2604.15531 (preprint) | "When candidates are correlated, the nominal K overstates the effective dimensionality of the search." (eq. (4)) | arxiv_2604_15531_spurious_predictability.pdf.txt l.259-264 |
| MinBTL | Bailey, Borwein, Lopez de Prado, Zhu 2014, Notices AMS | "if only 5 years of data are available, no more than 45 independent model configurations should be tried, or we are almost guaranteed to produce strategies with an annualized Sharpe ratio IS of 1, but an expected Sharpe ratio OOS of zero" | bailey_borwein_ldp_zhu_2014_pseudomath.pdf.txt l.426-429 |
| MLAM 2020 ch. 8 (ONC, false strategy) | Lopez de Prado 2020, Cambridge Elements | book not fetched; the 2019 paper above is the same authors' source text [book unverified] | none |
| Var(SR_hat) ~ 1/T under the null | Lo 2002 / Mertens 2002 (cited in BLdP l.357-358) | not fetched; standard result used as an assumption [unverified] | none |

#### (e) PBO by combinatorially symmetric cross-validation (CSCV)

##### e.1 Core idea
Cut the dates x configurations performance matrix into S equal row blocks, form every split of the blocks into two
halves, pick the in-sample best configuration on one half, and record where it ranks on the other. PBO is the share
of splits where the in-sample winner lands at or below the out-of-sample median. The program runs it (funnel, 8
blocks; ml_route_v2, 16 blocks) with a bar of 0.5 (E.20: "0.596 (bar < 0.5)", E.28 1b M4). New here: the paper's own
definitions, a hand-worked split, the sampling noise of the PBO estimate itself on 39 months, and a typo in the paper.

##### e.2 Equations (Bailey, Borwein, Lopez de Prado, Zhu 2017, section 2.2)
- M: the T x N matrix of performance (T dates, N configurations). Partition rows into S (even) blocks M_s of T/S rows.
- C_S: all combinations of the S blocks taken S/2 at a time; #C_S = C(S, S/2) (eq. (2.3)).
- For c in C_S: J = the S/2 training blocks in order, J_bar = the complement (test). R_c and R_bar_c the vectors of
  the N configurations' performance on J and J_bar; n* = argmax R_c (the in-sample best).
- omega_bar_c = r_bar_{n*,c} / (N + 1), with r_bar the out-of-sample rank (1 = worst, N = best).
- lambda_c = ln( omega_bar_c / (1 - omega_bar_c) ) (the paper prints the fraction inverted in the pdftotext line
  "λc = ln (1−ω̄ c) / ω̄c"; its next sentence, "High logit values imply a consistency between IS and OOS performances",
  fixes the orientation as ln(omega / (1 - omega))).
- PBO = phi = integral_{-inf}^{0} f(lambda) d lambda = share of splits with lambda_c <= 0.
- Program convention (funnel/multiple_comparisons.py:143): omega = (number strictly worse + 0.5)/N instead of r/(N+1);
  both give lambda <= 0 exactly when the winner is at or below the median, so PBO agrees; individual logits differ.

##### e.3 Worked example
**Counts.** S = 8: C(8,4) = 70 splits; S = 16: C(16,8) = 12,870 splits. The paper writes "if S = 16, we will form
12, 780 combinations" (`bailey_borwein_ldp_zhu_2017_pbo.pdf.txt` l.453): a typo, C(16,8) = 16!/(8! 8!) = 12,870 (the
program computes 12,870 combinations, which is correct). With 816 discovery dates: S = 8 gives blocks of 102 dates,
S = 16 blocks of 51 dates.

**One split by hand** (4 made-up configurations x 8 blocks, net ticks per block):

| Config | b1 | b2 | b3 | b4 | b5 | b6 | b7 | b8 |
|---|---|---|---|---|---|---|---|---|
| A | 5 | -3 | 4 | -2 | 6 | -4 | 3 | -1 |
| B | 2 | 2 | -1 | 1 | 0 | 1 | -2 | 2 |
| C | -4 | 6 | -3 | 5 | -2 | 4 | -1 | 3 |
| D | 1 | -1 | 1 | -1 | 1 | -1 | 1 | -1 |

Training blocks {b1, b3, b5, b7}: A 5 + 4 + 6 + 3 = 18; B 2 - 1 + 0 - 2 = -1; C -4 - 3 - 2 - 1 = -10; D 1 + 1 + 1 + 1 = 4.
In-sample best n* = A. Test blocks {b2, b4, b6, b8}: A -3 - 2 - 4 - 1 = -10; B 2 + 1 + 1 + 2 = 6; C 6 + 5 + 4 + 3 = 18;
D -1 - 1 - 1 - 1 = -4. A ranks last: r_bar = 1, omega = 1/5 = 0.2, lambda = ln(0.2/0.8) = -1.386 <= 0: overfit on this
split. Over all 70 splits the PBO is 0.800 (56 of 70), and the in-sample winner loses money out of sample in 45.7% of
splits (`M5a_calc_out.txt`, section "(e)"; both conventions give 0.800). Tie rule: on split {b1, b2, b3, b4} A, B and C
tie at 4 in sample; the program's Python `max` takes the first index. Ties must be broken by a declared rule.

**Sampling noise of the PBO estimate** (synthetic iid N(0,1) daily P&L, 816 days; `M5a_calc2_out.txt`):

| Configurations | S | Repetitions | Mean PBO | sd | 5%-95% |
|---|---|---|---|---|---|
| 10 | 8 | 200 | 0.485 | 0.223 | 0.128-0.829 |
| 50 | 8 | 200 | 0.504 | 0.180 | 0.228-0.814 |
| 200 | 16 | 12 | 0.504 | 0.114 | 0.341-0.671 |
| 50, one with a true daily SR 0.10 (about 1.6 annualised) | 8 | 200 | 0.299 | n/a | 0.029-0.657 |

Reading: under pure noise the PBO estimate is centred at 0.5 as it should be, but a single 39-month estimate wanders
from about 0.13 to 0.83 with 8 blocks; with a normal approximation (mean 0.5, sd 0.18-0.22) roughly one null search in three reports PBO below 0.4. A real edge of
annualised Sharpe 1.6 hidden among 49 null configurations gives PBO 0.30 on average, with a 95th percentile of
0.657, so it too can read above 0.5. The program's bar PBO < 0.5 is therefore a weak screen in both directions on this sample; the paper's own
suggested Neyman-Pearson cut is 0.05, which the one-true-edge case meets only in its lowest tail (5th percentile 0.029).
Check: the mean null PBO (0.485-0.504) is within 2 sd/sqrt(reps) of 0.5 in every row.

##### e.4 Data it needs
The daily net P&L matrix over discovery (816 dates x M configurations), from the frozen pipeline's out-of-sample
predictions (walk-forward or CV), not in-sample fits. Configurations that trade at different frequencies are aligned
on the common trade-date index (the paper: "observations should be aggregated to match a common index").

##### e.5 Leakage traps and tests
| Trap | Test |
|---|---|
| PBO computed on in-sample (fitted) P&L instead of out-of-sample predictions | Assert every P&L entry comes from a model that did not train on that date (fold id per date) |
| Blocks not contiguous, or not equal (the last block taking a large remainder) | Assert block sizes differ by at most the remainder (ml_route_v2 `pbo_cscv` reports `block_dates`) |
| Ties in the in-sample argmax resolved by column order | Declare a tie rule; test with a duplicated column |
| A handful of configurations (N < 10) makes ranks coarse | Report N with the PBO; with N = 4 the rank takes only four values |
| Reading PBO as a significance test | Report the null band above next to the estimate |

##### e.6 Compute
C(16,8) = 12,870 splits x M configurations of sums: for M = 5,000 about 64 million additions, seconds in NumPy; the
synthetic run of 200 configurations x 12,870 splits x 12 repetitions took well under a minute.

##### e.7 Verdict: USE (as a reported diagnostic, not as a gate)
Keep it (it is the program's practice and cheap), report it with its null band, and do not let PBO < 0.5 carry weight
in selection on a 39-month sample.

##### e.8 Evidence
| Claim | Source | Verbatim quote | File |
|---|---|---|---|
| Partition into S blocks | Bailey, Borwein, Lopez de Prado, Zhu 2017, J. Computational Finance (author copy) | "we partition M across rows, into an even number S of disjoint submatrices of equal dimensions" | bailey_borwein_ldp_zhu_2017_pbo.pdf.txt l.442-443 |
| Combination count and the typo | same | "For instance, if S = 16, we will form 12, 780 combinations." | same, l.453 |
| Relative rank | same | "Define the relative rank of r̄nc ∗ by ω̄c := r̄nc ∗ /(N + 1) ∈ (0, 1)." | same, l.481 |
| Logit orientation | same | "High logit values imply a consistency between IS and OOS performances, which indicates a low level of backtest overfitting." | same, l.488-490 |
| PBO definition | same | "This represents the rate at which optimal IS strategies underperform the median of the OOS trials." | same, l.540-542 |
| Suggested cut 0.05 | same | "a customary approach would be to reject models for which PBO is estimated to be greater than 0.05" | same, l.553-554 |
| PBO can be low while losses are likely | same | "Note that, even if φ ≈ 0, P rob[Rn∗ < 0] could be high" | same, l.582 |

#### (f) FWER versus FDR for a large search that sends at most 3 candidates to one one-shot test

##### f.1 Core idea
FWER procedures (Bonferroni, Holm, Romano-Wolf, White's Reality Check, Hansen's SPA) bound the chance of even one false
claim; FDR procedures (Benjamini-Hochberg, Benjamini-Yekutieli, Storey's q-values) bound the expected share of false
claims among many. A design that spends one sealed test on at most 3 candidates makes few claims and pays heavily for
a single false one, so it is an FWER problem at both stages. The search's size N matters at the selection stage
(discovery); the one-shot test, on data that played no part in selection, needs a correction over its own 3
hypotheses only. Whether to add more (HLZ t > 3.0, a family layer) is the lead's conservatism choice.

##### f.2 Equations (one-sided p-values p_(1) <= ... <= p_(m); alpha = 0.05)
- Bonferroni (FWER, any dependence): reject H_i if p_i <= alpha / m (HLZ 2016 section 3.4.1).
- Holm 1979 (FWER, any dependence, step-down): with b the rank, reject H_(1)..H_(k-1), k the first index with
  p_(b) > alpha / (M + 1 - b) (HLZ 2016 section 3.4.2; Holm's paper not fetched).
- Benjamini-Hochberg 1995 (FDR at q*, independence; also PRDS): k = largest i with p_(i) <= (i/m) q*; reject H_(1)..H_(k).
  Under PRDS it controls FDR at q* m0/m (BY 2001 as stated by Fithian and Lei 2020).
- Benjamini-Yekutieli 2001 (FDR, arbitrary dependence): BH at q*/L_m, L_m = sum_{i=1}^{m} 1/i = ln m + O(1)
  (HLZ's c(M), their eq. (1); Fithian-Lei restatement).
- Storey's q-value (FDR, needs pi0): pi0_hat(lambda) = #{p_i > lambda} / (m (1 - lambda)); q-value = the smallest FDR
  at which a feature is called significant (Storey and Tibshirani 2003). The pi0 estimate "can fail badly under
  dependence" (Fithian-Lei).
- White 2000 Reality Check (FWER for "the best beats the benchmark"): f_k,t = performance of rule k relative to the
  benchmark at t; H0: max_k E(f_k) <= 0; statistic V_bar = max_k n^{1/2} f_bar_k; p-value from the stationary
  (Politis-Romano) bootstrap distribution of max_k n^{1/2} (f_bar*_k - f_bar_k).
- Hansen 2005 SPA: studentise each n^{1/2} d_bar_k by omega_hat_k, and recentre the bootstrap only for rules that are
  not clearly bad: mu_hat_k = d_bar_k 1{ n^{1/2} d_bar_k / omega_hat_k <= -sqrt(2 log log n) }; "more powerful and less
  sensitive to poor and irrelevant alternatives" than the RC.
- Romano-Wolf 2005 stepdown (FWER, asymptotic, any dependence): at each step compare every remaining studentised
  statistic with the bootstrap 1 - alpha quantile of the max over the remaining set, reject those above, drop them,
  repeat until none is rejected.
- HLZ 2016 hurdle: t > 3.0 (two-sided p 0.0027).

##### f.3 Worked arithmetic
**Thresholds (one-sided alpha 0.05; `M5a_calc_out.txt` section "(f)")**

| m | Bonferroni p | z | BY first rejection p = alpha/(m L_m) | z | L_m | BH at the 3rd rejection p = 3 alpha/m | z |
|---|---|---|---|---|---|---|---|
| 3 | 0.01667 | 2.128 | 0.00909 | 2.362 | 1.833 | 0.05 | 1.645 |
| 200 | 2.50e-4 | 3.481 | 4.25e-5 | 3.930 | 5.878 | 7.50e-4 | 3.175 |
| 738 | 6.78e-5 | 3.816 | 9.43e-6 | 4.278 | 7.182 | 2.03e-4 | 3.536 |
| 1,000 | 5.00e-5 | 3.891 | 6.68e-6 | 4.354 | 7.485 | 1.50e-4 | 3.615 |
| 1,538 | 3.25e-5 | 3.994 | 4.11e-6 | 4.460 | 7.916 | 9.75e-5 | 3.725 |
| 5,000 | 1.00e-5 | 4.265 | 1.10e-6 | 4.734 | 9.095 | 3.00e-5 | 4.013 |
| 5,538 | 9.03e-6 | 4.288 | 9.82e-7 | 4.757 | 9.197 | 2.71e-5 | 4.037 |

By hand for m = 738: 0.05 / 738 = 6.775e-5, z = Z^-1(1 - 6.775e-5) = 3.816; L_738 = ln 738 + 0.5772 + 1/(2 x 738) =
6.604 + 0.577 + 0.0007 = 7.182; 0.05 / (738 x 7.182) = 9.43e-6, z = 4.278. The first BH rejection always equals
Bonferroni (i = 1); BH is only less strict for the 2nd, 3rd, ... rejection, which a design taking at most 3 to the test
barely uses.

HLZ t > 3.0 in these units: one-sided p = 1 - Z(3.0) = 0.00135, two-sided 0.0027; it equals Bonferroni at 5% over
0.05 / 0.00135 = 37 one-sided tests (18.5 two-sided). It is far below the Bonferroni z for the E.33 search sizes (3.8
to 4.3) and far above what 3 sealed-test hypotheses need (2.128).

**Dependence: what a max-statistic method (RC, SPA, Romano-Wolf) saves over Bonferroni.** 95% quantile of the
maximum of m equicorrelated standard normals (one factor; max of m iid normals drawn exactly by the inverse CDF of
U^(1/m); 200,000 draws):

| m | rho = 0 | rho = 0.5 | rho = 0.8 | Bonferroni |
|---|---|---|---|---|
| 738 | 3.812 | 3.472 | 2.903 | 3.816 |
| 1,538 | 3.987 | 3.607 | 2.995 | 3.994 |
| 5,538 | 4.283 | 3.844 | 3.152 | 4.288 |

Check: at rho = 0 the simulated quantile matches Bonferroni to 0.005, as it should for independent tests. Correlated
configurations (shared features, neighbouring parameters) lower the max-statistic bar by 0.3 to 1.1 in z; Bonferroni,
Holm and BY cannot use that.

**DSR as a test.** With V = 1/T, DSR >= 0.95 means t >= e(N) + 1.645 (section d.2), and the chance that any of N
independent null trials passes is 1 - Z(t*)^N = 5.5e-4 (N = 738, t* 4.813), 4.0e-4 (1,538, t* 5.020), 2.3e-4 (5,538,
t* 5.359) (`M5a_calc2_out.txt`). So "DSR >= 0.95" is about 100 times stricter than an FWER 5% test at the same N
(compare Bonferroni z 3.8-4.3 above); it is not an alpha-level procedure, and 1 - DSR is not a p-value with nominal
size.

**The one-shot test with at most 3 candidates (Holm over 3, one-sided 0.05):** first p <= 0.0167 (z >= 2.128), second
p <= 0.025 (z >= 1.960), third p <= 0.05 (z >= 1.645). If the lead adds a family layer by Bonferroni over 3 x K:
K = 4 gives z >= 2.638, K = 5 gives z >= 2.713. What this means in ZM units (test window about 899 trade dates; h = 15
min, sigma 12.20 ticks, c = 1.59; one non-overlapping trade a date):

| Bar | Per-trade SR = z / sqrt(899) | Net ticks a trade | Gross ticks a trade |
|---|---|---|---|
| z 1.645 | 0.0549 | 0.67 | 2.26 |
| z 2.128 (Holm first, Bonferroni over 3) | 0.0710 | 0.87 | 2.46 |
| z 3.0 (HLZ) | 0.1001 | 1.22 | 2.81 |
| the same at 449 trades (every other date), z 2.128 | 0.1004 | 1.23 | 2.82 |

Power of the first Holm step (z 2.128) and of HLZ (3.0) at 899 trades, for a true net per-trade SR: 0.1689 (the
discovery DSR bar of d.3, gross 3.65): expected z = 0.1689 x sqrt(899) = 5.06, power 0.998 and 0.98; 0.0845 (half that
bar, gross 2.62): z 2.53, power 0.66 and 0.32; 0.060 (gross 2.32): z 1.80, power 0.37 and 0.12. Because the discovery
estimate of the winner is inflated by selection, the true SR is likely well below its discovery value, so an extra
HLZ hurdle at the test costs most of the power exactly where the candidate is real but modest.

##### f.4 Which fits the design (for the lead to decide)
1. Discovery (M configurations, choose at most 3): the question is "does the best of this search beat zero after
   selection?", an FWER-of-the-max question. Fits: the program's DSR at the cumulative N (its bar; strictest, d.7) and,
   as a calibrated companion, a Romano-Wolf stepdown or Hansen SPA on the discovery daily net P&L matrix with a
   stationary bootstrap, which uses the configurations' correlation and gives a p-value with nominal size. FDR
   methods (BH, BY, Storey) answer a question this design does not ask (what share of many discoveries is false), and
   Storey's pi0 is unreliable under the strong dependence of a parameter grid.
2. One-shot test (at most 3 hypotheses, sealed 2017-05..2020-11 data): Holm over the tested candidates at one-sided 0.05
   (the program's `holm_tier_a` with K counting only families that send a candidate) controls FWER without any
   dependence assumption. No N-deflation is needed for validity, because the test data played no role in selection;
   HLZ t > 3.0 or a family layer are extra conservatism with the power cost shown above.
[MathReview C-6/C-9 (lead: ruled): the frozen test bar is the program verdict plus a protocol-added DSR >= 0.95 at N with V = 1/(T_test - 1) (t about 4.86 at N 838, T 870); see reports/stage_e32_discovery_protocol.md P7.2 and P9.]
3. Benchmark: for a directional ZM rule the RC/SPA benchmark should be the rule's unconditional counterpart (the
   program's drift benchmark, E.28 1h V10), not zero, so that drift in 2020-24 does not pass as skill.

##### f.5 Data it needs
Discovery: the dates x configurations daily net P&L matrix (816 x M) for RC/SPA/Romano-Wolf and DSR; a block length
for the stationary bootstrap, declared in advance (for example the mean of 5 trade dates). Test: per-candidate daily
net P&L over the sealed window, and HAC or block-bootstrap p-values (the program's Newey-West t, E.28 1a S2).

##### f.6 Leakage traps and tests
| Trap | Test |
|---|---|
| The test statistic, sidedness or alpha chosen after seeing results | Frozen and hashed in the protocol before the run; the runner refuses other values |
| K (families) or m counted after results (dropping a family that failed) | K and m fixed by the registered candidate list; `holm_alpha_k` takes K from it |
| Per-trade p-values from overlapping trades | Use daily P&L with Newey-West or block bootstrap; compare with per-trade p (overlap diagnostic of d.5) |
| Bootstrap block length tuned to the result | Declared in the protocol; a sensitivity row at half and double length, reported only |
| Benchmark = zero for a directional rule in a trending window | RC/SPA run against the unconditional counterpart; report both |
| Sealed data touched by threshold setting (variance, moments, block length) | Everything set from discovery; seal check before the test run |

##### f.7 Compute
RC, SPA and Romano-Wolf on an 816 x 5,000 daily matrix (33 MB): B = 2,000 stationary-bootstrap resamples, each a row
gather and 5,000 column means (about 4 million operations), about 8 x 10^9 operations in all, seconds to a minute in
NumPy [estimate]; Romano-Wolf repeats the max per step on shrinking sets. BH, BY, Holm and Bonferroni are instant.

##### f.8 Verdict
- Holm over the at most 3 tested candidates: USE at the test (already coded).
[MathReview C-6/C-9 (lead: ruled): the frozen test bar is the program verdict plus a protocol-added DSR >= 0.95 at N with V = 1/(T_test - 1) (t about 4.86 at N 838, T 870); see reports/stage_e32_discovery_protocol.md P7.2 and P9.]
- DSR at cumulative N: USE at discovery (program bar), knowing it is about 100 times stricter than a 5% FWER test.
- Romano-Wolf stepdown or Hansen SPA (studentised, stationary bootstrap, drift benchmark): MAYBE, as the calibrated
  discovery p-value beside DSR; the lead decides whether it gates or is reported.
- White's RC: SKIP in favour of SPA or Romano-Wolf (Hansen: RC is less powerful and sensitive to poor alternatives,
  which a parameter grid has many of).
- BH, BY, Storey: SKIP (they control a quantity the design does not use).
- HLZ t > 3.0: MAYBE, lead's conservatism call; it is redundant at discovery (weaker than DSR and Bonferroni at N) and
  costly at the test.

##### f.9 Evidence
| Claim | Source | Verbatim quote | File |
|---|---|---|---|
| t > 3.0 hurdle | Harvey, Liu, Zhu 2016, RFS (Duke author copy) | "A new factor needs to clear a much higher hurdle, with a t-statistic greater than 3.0." | harvey_liu_zhu_2016_rfs.pdf.txt l.16-17 |
| t of 3.0 and its p | same | "While a t-statistic of 3.0 (which corresponds to a p-value of 0.27%) seems like a very high hurdle, we also argue that there are good reasons to expect that 3.0 is too low." | same, l.1752-1754 |
| FWER versus FDR levels | same | "a t-statistic of 3.9 and 3.0 is needed to control FWER at 5% and FDR at 1%, respectively" | same, l.1641-1642 |
| Bonferroni rule | same | "Reject any hypothesis with p-value ≤ αw/M" (layout garbled: "≤ αMw") | same, l.685-686 |
| Holm rule | same | "Let k be the minimum index such that p(b) > αw/(M+1−b)" (layout garbled) and "Holm’s adjustment is a step-down procedure" | same, l.788-800 |
| BY constant | same | "Benjamini and Yekutieli (2001) show that setting c(M) at ... [sum 1/j] allows the procedure to work under arbitrary dependency among the test statistics" | same, l.880-886 |
| BH procedure | Benjamini and Hochberg 1995, JRSS B (third-party copy) | "let k be the largest i for which P(i) ≤ (i/m) q*; then reject all H(i) i = 1, 2, . . . k." (OCR-garbled in the file); "Theorem 1. For independent test statistics and for any configuration of false null hypotheses, the above procedure controls the FDR at q*." | benjamini_hochberg_1995.pdf.txt l.215-220 |
| BH under PRDS; BY | Fithian and Lei 2020, arXiv 2007.10438 (secondary statement of BY 2001; BY's own paper failed to download) | "Benjamini and Yekutieli (2001) show that the BH(α) procedure controls FDR conservatively at αm0/m, provided that p−i is PRD on pi"; "the much more conservative BH(α/Lm) procedure controls FDR at level α under arbitrary dependence" | fithian_lei_2020_arxiv_2007_10438.pdf.txt l.118-120, l.132-134 |
| Storey pi0 fails under dependence | same | "the Storey-BH method (Storey et al., 2004), whose estimate of m0/m can fail badly under dependence" | same, l.122-124 |
| q-value definition | Storey and Tibshirani 2003, PNAS (course copy) | "The q value of a particular feature can be described as the expected proportion of false positives among all features as or more extreme than the observed one." (left column) | storey_tibshirani_2003_pnas.pdf.txt l.227-230 |
| Romano-Wolf stepdown | Romano and Wolf 2005, Econometrica (UZH copy) | "asymptotically controls the familywise error rate. Compared to related single-step methods, the procedure is more powerful and often will reject more false hypotheses. In addition, we advocate the use of studentization when feasible." | romano_wolf_2005_econometrica.pdf.txt l.9-11 |
| RC null and statistic | White 2000, Econometrica (course copy) | "Ho : max k=1,...,l E(f*_k) ≤ 0" and "V_l ≡ max k=1,...,l n^1/2 f_bar_k" (OCR-garbled) | white_2000_reality_check.pdf.txt l.208, l.283 |
| What RC does | same | "This permits data snooping to be undertaken with some degree of confidence that one will not mistake results that could have been generated by chance for genuinely good results." (abstract) | same, l.19-22 |
| SPA versus RC | Hansen 2005, JBES (UNC repository copy) | "The new test compares favorably to the reality check (RC) for data snooping, because it is more powerful and less sensitive to poor and irrelevant alternatives." | hansen_2005_spa_unc.pdf.txt l.5-6 |
| SPA recentring threshold | same | "µ̂k = d̄k 1{n1/2 d̄k /ω̂k ≤− 2 log log n}" (square root lost in extraction) | same, l.227 |
| Holm 1979 original | Holm 1979, Scand. J. Statist. | download timed out twice (logged); procedure taken from HLZ 2016 [original unverified] | none |
| Benjamini-Yekutieli 2001 original | Annals of Statistics | Project Euclid returned a 1 KB HTML page, the TAU author copy failed twice (logged); taken from Fithian-Lei 2020 and HLZ 2016 [original unverified] | none |

#### Planner pointers owned by this section

| Pointer (reports/stage_e32_inputs/planner_research_soy_complex.md) | Status | Evidence and what differs |
|---|---|---|
| "At most 4-5 families, with Holm or Bonferroni across families and a deflated Sharpe or White's reality check within each." (l.108-109) | PARTLY VERIFIED | Holm and Bonferroni control FWER (HLZ 2016 l.667-668: "Both Bonferroni and Holm control FWER, and BHY controls FDR"), and the program already codes the across-family layer (`holm_alpha_k` = 0.05/K, screening/stage_e_stats.py:288). What differs: (1) Bonferroni across K families with Bonferroni inside each is identical to a global Bonferroni (0.05/4/50 = 0.05/200: z 3.481 both ways; same at m = 1,000 and 5,000), so the family layer gains power only when the within-family method uses the configurations' correlation (RC, SPA, Romano-Wolf: 0.3-1.1 z lower at rho 0.5-0.8, f.3). (2) "DSR within" does not combine with Holm: DSR >= 0.95 is not an alpha-level test (size 2-6 x 10^-4 under V = 1/T, f.3) and 1 - DSR is not a p-value, so Holm over DSRs is not a defined FWER procedure. RC or SPA within plus Holm across is coherent; Hansen 2005 shows SPA dominates RC. (3) "4-5 families" has no source; it is a design choice. (4) For the one-shot test, Holm over the at most 3 candidates already covers families if K counts only families that send one. |
| "Walk-forward validation with purge and embargo of at least the label horizon plus one session" (l.120-121) | PARTLY VERIFIED | Purge of at least the label horizon is LdP's rule (purging, LdP 2018 l.506-507), and walk-forward under expected non-stationarity is supported by Li 2026 (l.750-752) and Cerqueira et al. 2020 (l.36-39). What differs: (1) no source gives "one session" as the embargo; AFML's rule is 0.01T, which is 8.16 trade dates on 39 months (a.2), and Li's is H + c tau with c 2-3; one session is a defensible, shorter engineering default that should come with the 1/5/20-date sensitivity diagnostic (a.5). (2) With session-aligned folds and labels clipped at the 13:20 close, the "label horizon" part costs nothing (the purge set is empty), so the rule reduces to a 1-date embargo. (3) LdP 2018 (l.538-544) warns that walk-forward tests one path that can be overfit and that walk-backward is equally legitimate; the sealed test is backward in time (2017-20 before 2020-24), so a reversed walk-forward diagnostic is the closer rehearsal (c.3). |

#### Summary of findings for the lead
1. DSR at the E.33 search sizes is a t-bar of about e(N) + 1.645: 4.81 (N = 738), 5.02 (1,538), 5.36 (5,538) under the
   null-calibrated V = 1/T, independent of horizon and frequency; on ZM that is an annualised Sharpe of 2.7-3.0 over
   39 months, or gross 2.6-2.7 ticks a 15-minute trade at four non-overlapping trades a day, 3.6-3.9 at one a day.
   Skew and kurtosis move it by at most 2% at per-trade Sharpe 0.1-0.3.
2. Pair the empirical cross-trial V with the literal N (the program's current pairing; conservative), or V = 1/T with
   an effective N, never the empirical V with an effective N (double discount; shown by simulation in d.3 (v)).
3. The one-shot test of at most 3 candidates needs Holm over 3 (z 2.128 / 1.960 / 1.645 one-sided); N-deflation at the
   test is not needed for validity. HLZ t > 3.0 there costs half the power for a modest true edge (0.66 to 0.32 at a
   true net Sharpe of 0.0845 a trade, 899 trades).
[MathReview C-6/C-9 (lead: ruled): the frozen test bar is the program verdict plus a protocol-added DSR >= 0.95 at N with V = 1/(T_test - 1) (t about 4.86 at N 838, T 870); see reports/stage_e32_discovery_protocol.md P7.2 and P9.]
4. PBO on 39 months is noisy: a null search's PBO ranges about 0.13-0.83 (8 blocks); report it with that band, do not
   gate on PBO < 0.5. The PBO paper's "12, 780" is a typo for C(16,8) = 12,870.
5. Session-aligned folds (whole trade dates, labels clipped at 13:20 CT) make purging free; the embargo is a dependence
   choice (1 date default, AFML 0.01T = 8.2 dates, feature lookback up to 20 dates) costing at most about 3% of
   training data per split.
6. CPCV path Sharpes measure model instability, not sampling error (all paths share the same test dates); CPCV on
   every configuration is affordable only for linear models or small grids (225,000 GBM fits at N = 5,000).
7. The sealed test runs backward in time from discovery; a reversed walk-forward inside discovery rehearses it.

#### Gaps, failures and negative evidence
- Not fetched (no open copy): AFML 2018 chapters 7, 11, 12, 14 and MLAM 2020; covered by the author's own JPM summary
  (lopezdeprado_2018_10reasons_jpm) and the Lopez de Prado-Lewis ONC paper; book text [unverified].
- Download failures (logged in log.tsv): Holm 1979 (timed out twice), Benjamini-Yekutieli 2001 (Project Euclid
  returned a 1 KB HTML page; the TAU author copy failed twice), Bergmeir-Hyndman-Koo 2018 (403 and a non-PDF page).
  Their procedures are quoted from HLZ 2016 and Fithian-Lei 2020 as secondary statements.
- The BLdP 2014 example inputs were lost in pdftotext (equation images); confirmed only by reproducing the three
  printed outcomes. Lo 2002 / Mertens 2002 (Var(SR_hat) ~ 1/T) not fetched; used as a stated assumption.
- Session times (19:00-07:45 and 08:30-13:20 CT) and the CBOT holiday list are assumptions from the brief and my own
  list, not verified (the E.32 CME rule forbids fetching cmegroup.com); trade-date counts carry about +-3 dates of
  error. Kurtosis and skew values in d.3 are illustrative, not measured. The 0.5 s linear-model fit time is assumed;
  only the 6 s GBM figure is measured (E.28).
- Negative evidence: no source found that compares forward and backward validation on futures data (arXiv API
  queries on 2026-10-27 surfaced none; the closest, Nikolopoulos 2026, is a placebo-audit framework); no source
  supports "one session" as an embargo width; no source supports a PBO bar of 0.5.
- WebSearch: 0 calls in this spawn (discovery by the arXiv API and direct author-copy URLs).

## M5b. Feature importance, stability and power

Source file: reports/stage_e32_briefs/M5b_power.md (sha256 9ff600dfa6fcee5034352537e4ce1c800c054838ac9167bb52080297d5a1aac1).

### Stage E.32 Part M5 (second half): safe feature importance, stability requirements, and power for E.33

Worker PowerStability-OpusHigh (Opus 5.5, high), ROOT M5b_power, started 2026-10-27 00:29 PDT.
Inputs read by line range: READER_BRIEF.md, E.28 READER_RULES.md, reports/stage_e28_methods_brief.md 2.7 (sections 4,
5, 12) and 2.11 (sections 3-4), M5a_validation.md section 0 (shared quantities), R4_events.md lines 230-240 (event
count). M5a owns CV schemes, DSR, PBO and FDR; this file cites "M5a" for them and does not repeat them.

No market data was read. Every number below is arithmetic or a synthetic Monte Carlo on the standard ZM numbers.
Scripts (written by me, run at nice 10): work/M5b_power/M5b_days.py (trade-date count), M5b_calc.py
(-> M5b_calc_out.txt), M5b_calc2.py (-> M5b_calc2_out.txt). Pages and log.tsv: pages/M5b_power/.

#### 0. Shared quantities (assumptions marked)

| Quantity | Value | How |
|---|---|---|
| ZM sigma_1m | 3.15 ticks | brief, E.28 A0 Table 1 (2022-11..2023-10) |
| sigma_h under a random walk (ASSUMPTION: increments uncorrelated, constant variance, so sigma_h = sigma_1m sqrt(h)) | 5 min: 3.15 x 2.2361 = 7.044; 15 min: 3.15 x 3.8730 = 12.200; 60 min: 3.15 x 7.7460 = 24.400; 75 min: 3.15 x 8.6603 = 27.280 ticks | M5b_calc_out.txt "constants". Check: 12.200 x 2 = 24.400 = sigma_60, since sqrt(60/15) = 2 |
| Market-order round-trip break-even at Topstep | 1.59 ticks | stage_e28_ranking.md line 130 (as quoted by M5a 0.1; the brief's "about 1.6") |
| Test window trade dates, 2017-05-01..2020-11-30 | **904** (range 903-905) | 936 weekdays (counted by script) minus 32 typed CBOT-grain full closures (New Year, MLK, Presidents, Good Friday, Memorial, July 4, Labor, Thanksgiving, Christmas, observed dates; plus 2018-12-05, the national day of mourning, [unverified] whether grains closed). Typed from memory, not from a CME page (the E.32 CME rule forbids fetching one); DataFacts owns the real calendar. **M5a 0.1 has 899 (it assumed 37 closures). The two differ by 5 dates; neither is read from data. The difference moves every per-day rate below by 0.6%.** |
| Discovery trade dates, 2020-12-01..2024-02-29 | 816 | 848 weekdays minus 32 typed closures (adds Juneteenth 2022-06-20 and 2023-06-19). Agrees with M5a's 816 |
| Session minutes per trade date | 765 overnight + 290 day = 1,055 | brief's session times; [unverified here, DataFacts owns] |
| Calendar months | test 43, discovery 39 | May 2017..Nov 2020 = 8+12+12+11; Dec 2020..Feb 2024 = 1+12+12+12+2 |
| 3-month blocks | test 14 full + 1 month; discovery 13 | 43 = 14 x 3 + 1; 39 = 13 x 3 |
| Critical values | one-sided alpha 0.05/3: z = 2.1280; t > 3.0 (one-sided alpha 0.00135); power 0.8: z_b = 0.8416; one-sided 0.05: 1.6449 | Python statistics.NormalDist |

[MathReview C-7 (lead: accepted): row "Test window trade dates": 2018-12-05 is not a grain full closure in the program's calendars (31 closures), which are the source of record for E.33, so the count is 905, not 904. Every "/test day" figure moves by 0.1% (e.g. 8,786/905 = 9.71, not 9.72; 1,313/905 = 1.45 unchanged) and the gate formula "k_test x 904" should read 905 (also at original lines 361-390, 466-469, 529, 583-587 and 610-611); no verdict moves.]

Why "net mu in {0.25, 0.5, 1.0} ticks" is the right scale: at h = 15 minutes and a market-order round trip of 1.59
ticks, net mu = 0.5 tick needs a gross 2.09 ticks, and under the assumption that the sign of the move is
independent of its size and moves are normal, gross = (2p - 1) E|r| with E|r| = sigma_h sqrt(2/pi) =
12.200 x 0.7979 = 9.734 ticks, so the hit rate must be p = 0.5 + 2.09 / (2 x 9.734) = 0.6074 (M5b_calc2_out.txt).
At 5 minutes the same net edge needs p = 0.6859, and at 60 minutes p = 0.5537. These are large hit rates for a
minutes-scale futures signal; they are the scale against which every importance number in (a) should be read.

#### (a) Feature importance on purged folds: MDI, MDA, SFI, clustered MDA, and why importance must not steer choices

##### a.1 Core idea
Feature importance asks which inputs a fitted model relies on. MDI (mean decrease impurity) is computed in-sample
from the tree splits. MDA (mean decrease accuracy, Breiman's permutation importance) is the drop in an
out-of-sample score when one feature's values are shuffled in the test fold. SFI (single feature importance) is the
out-of-sample score of a model fitted on that feature alone. Correlated features share credit (the "substitution
effect"), so MDA can call two near-copies of a real signal both unimportant; clustered MDA permutes a whole cluster
of related features at once. Under V43 importance is a diagnostic that is reported, never a lever that changes the
frozen pipeline after its folds have been scored.

##### a.2 Equations
Notation: K purged and embargoed folds (scheme: M5a (a)); for fold k, model f_k is fitted on the training part and
scored on the test part T_k with n_k rows; S(f, X, y) is a score where higher is better (accuracy, minus log loss,
or the net P&L of the traded rule in ticks); X^{(j,pi)} is X with column j permuted by a random permutation pi
inside T_k only; C is a cluster (a set of columns); R is the number of permutation repeats.

- MDI (Breiman 2001 Gini importance, the "Mean decrease impurity" of AFML ch. 8):
  MDI_j = (1/B) sum_{b=1..B} sum_{s in tree b, split on j} w(s) [i(s) - (n_L/n_s) i(L) - (n_R/n_s) i(R)],
  with B trees, w(s) the share of training rows reaching node s, i(.) the impurity (Gini or entropy) and L, R the
  children. It is computed on training rows only, is never negative, and needs no test data. (Standard definition;
  wording as in Falces Marin et al. 2022: "a feature-specific measure of the mean reduction of weighted impurity over
  all the nodes in the tree ensemble".)
- MDA (Breiman 2001 section 10 used out-of-bag rows; López de Prado's version uses purged CV test folds):
  MDA_j = (1/K) sum_k (1/R) sum_{r=1..R} [ S(f_k, X_{T_k}, y_{T_k}) - S(f_k, X_{T_k}^{(j,pi_r)}, y_{T_k}) ].
  A relative form divides each term by |S(f_k, X_{T_k}, y_{T_k}) - S_0|, with S_0 the score of a no-skill predictor.
- Clustered MDA: replace column j by cluster C and permute all columns of C with the SAME row permutation
  (so their mutual dependence is kept and their link to y is broken):
  MDA_C = (1/K) sum_k (1/R) sum_r [ S(f_k, X_{T_k}, y) - S(f_k, X_{T_k}^{(C,pi_r)}, y) ].
  Clusters come from a dependence matrix computed on feature values only (for example the distance
  d_ij = sqrt((1 - rho_ij)/2) and the ONC algorithm of López de Prado and Lewis, used in M5a for trial clustering).
  Clustered MDI = sum_{j in C} MDI_j. [The book's own equations were not read: MLAM section 6.5 is not available as
  free full text; the mechanism is quoted from library documentation and the published table of contents, see a.9.]
- SFI: SFI_j = (1/K) sum_k S(g_{k,j}, x_{j,T_k}, y_{T_k}) - S_0, where g_{k,j} is fitted on column j alone on fold
  k's training rows. No substitution effect (each model sees one feature), but no interactions either.
- Retrain-based importance (Hooker, Mentch and Zhou 2021: "re-learning"; also called leave-one-covariate-out):
  LOCO_j = (1/K) sum_k [ S(f_k) - S(f_k^{(-j)}) ], with f_k^{(-j)} refitted without column j. Avoids the
  extrapolation that permutation forces, at K extra fits per feature.
- Noise canary: add Q columns of pure noise (for example a block-permuted copy of a real feature); the importance
  floor is max_q MDA_{noise q}. A feature is "distinguished" only above that floor.
- Sampling noise of accuracy-based MDA: if the permutation changes the predicted class on a share f of n test rows,
  each change moves accuracy by +-1/n, so SE(MDA_j) <= sqrt(f / n) (a bound I derived; it ignores that changes
  are not independent across overlapping labels, so the effective n is smaller: see (c)).

##### a.3 Worked example (standard ZM numbers; M5b_calc2_out.txt)
1. Units. At h = 15 minutes, E|r| = 12.200 x sqrt(2/pi) = 12.200 x 0.79788 = 9.734 ticks. One percentage point of
   hit rate is worth (2 x 0.01) x 9.734 = 0.195 ticks gross a trade (sign independent of size: assumption). At 60
   minutes it is 0.389 ticks; at 5 minutes 0.112 ticks.
2. Sample. Non-overlapping 15-minute labels over discovery: 1,055 min x 816 days / 15 = 57,392 rows (all sessions;
   about 15,776 for the day session only: 290 x 816 / 15 = 15,776). With 10 folds every row is tested once.
3. Noise. If shuffling a feature flips 20% of predictions, SE(MDA) <= sqrt(0.2 / 57,392) = sqrt(3.485e-6) =
   0.00187, i.e. 0.19 percentage points; a 2-SE detection floor is 0.37 points = 0.37 x 0.195 = 0.073 ticks gross.
   Check: with n = 100,000 and f = 0.2 the bound is 0.00141 (script), and 0.00187 x sqrt(57,392/100,000) =
   0.00187 x 0.7576 = 0.00142. Consistent.
4. Size of what must be found. Net 0.5 tick at h = 15 needs p = 0.6074 (section 0), i.e. 10.7 percentage points of
   hit rate over 0.5 in total, or a log-loss gain of ln 2 - H(0.6074) = 0.693147 - 0.669897 = 0.02325 nats
   (script). A feature with MDA of 1 point carries 0.195 ticks; so a tradeable model needs either a few strong
   features or many weak ones whose importance is split by substitution, which is exactly where single-column MDA
   misleads.
5. Substitution, toy arithmetic. Two features x1 and x2 with correlation 0.99 carry the same signal and the model
   splits on either. Permuting x1 alone leaves x2 intact, so MDA_x1 and MDA_x2 are both near 0 (Hooker et al.:
   permutation also makes the model extrapolate to (x1, x2) pairs that never occur, which can instead inflate both);
   permuting the cluster {x1, x2} together removes the whole signal, so MDA_C equals the full 10.7-point drop in the
   step-4 example. SFI_x1 = SFI_x2 = the full single-feature score. Reading: with correlated order-flow features
   (OFI at several lags, queue imbalance at several depths) use clustered MDA and SFI, never raw MDA alone.

##### a.4 Data it needs
The frozen E.33 feature matrix (from ZM MBO; ZS and ZL MBP-1 for cross-asset features; definitions for roll and tick
size) at the label horizon, the purged fold assignment from M5a (a), and each fold's fitted model. Clustering uses
feature values only, from the training folds. Nothing from the sealed 2017-05..2020-11 window.

##### a.5 Leakage and look-ahead traps, each with a test
1. MDI is in-sample: it rewards features the trees used, including overfit ones, and favours continuous and
   high-cardinality features (Strobl et al. 2007). Test: add noise canaries; MDI gives them positive importance, a
   purged-fold MDA should give them about 0. Rule: MDI is never evidence.
2. Out-of-bag importance on overlapping labels: bagged trees put the row adjacent in time (sharing most of its
   label window) in-bag, so the "out-of-bag" score is contaminated. Test: compute importance both out-of-bag and on
   purged folds for one model; any gap means leakage; ban OOB scoring (for example sklearn `oob_score`) in E.33.
3. Permuting across folds or across the embargo: the permutation must stay inside T_k. Test: assert that the set of
   row indices before and after permutation is identical within each fold.
4. Selection bias: features chosen by importance on all folds and the chosen model then cross-validated on the same
   folds. Ambroise and McLachlan (2002) show the CV error is then biased (it can reach zero on noise). Tests: (i)
   nested CV, selection inside each outer training fold, and compare with the non-nested number; (ii) a null-label
   run: permute labels in whole-day blocks, run the full pipeline including any selection step; the CV score must
   sit at chance, and a non-nested pipeline that scores above chance on shuffled labels has leaked.
5. Scalers, winsorization limits or cluster definitions fitted on all discovery rows before the split. Test: refit
   them per training fold and confirm identical test-fold predictions to 1e-9; any difference shows that test rows
   informed the transform.
6. Importance on the test window: forbidden (V43, one read). Test: the E.33 run log has no importance call after the
   seal is opened.

##### a.6 Why importance must never steer a later choice inside the same data
- It is a selection step that saw the test folds. Any choice made with it (drop features, re-weight, pick a
  cluster, pick a model rung) makes the CV estimate of the result optimistic, as in a.5 item 4 above: "the
  cross-validation of the rule is not external to the selection process" (Ambroise and McLachlan 2002).
- It is an uncounted search. Under V43 every configuration enters N. A feature subset picked after reading
  importance is one draw from up to 2^F subsets (F = 64 gives 1.8e19) that N does not count, so M5a's DSR and PBO
  numbers would be computed at the wrong N.
- The Rashomon effect (Fisher, Rudin and Dominici 2019): many near-equal models rely on different features, so the
  importance ranking of one fitted model is itself unstable (Man and Chan 2020 find MDA "the least stable" of the
  three methods they test, and that no method "converges to a single feature set").
- What is allowed: (i) importance reported after the frozen grid has run, as a diagnostic and a sanity check
  (López de Prado 2018: "feature importance is a research tool, and backtesting is not"); (ii) a feature-selection
  step that is declared in the protocol, runs inside each training fold, and is counted into N as part of the
  pipeline; (iii) using importance to design the NEXT stage's grid, on new data, with the trial count carried.

##### a.7 Compute (ThinkPad, 39 months; estimates, not measured)
Matrix: 860,880 one-minute rows x 64 float32 features = 220 MB (M5a 0.1 gives the row count). MDA: K = 10 fits
already exist; 64 features x 10 folds x R = 5 repeats = 3,200 predictions of about 86,000 rows each; seconds to
minutes on CPU. Clustered MDA: fewer (one per cluster). SFI: 64 x 10 = 640 single-feature fits; for a depth-3
gradient-boosted model on about 775,000 rows a fit takes seconds, so tens of minutes in total at 14 threads [guess,
no probe run]. LOCO: 640 full refits, about 64 times the cost of the base CV: run on finalists only. Memory is not
binding.

##### a.8 Verdict
USE clustered MDA on purged folds with noise canaries, and SFI as the cross-check, as REPORTED diagnostics after the
frozen run. SKIP MDI as evidence (debugging aid only). LOCO: MAYBE, finalists only. Importance-driven feature
selection: SKIP unless the lead pre-declares it as a nested, N-counted step. For a minutes-scale directional ZM
search the realistic signal is a few percentage points of hit rate spread over correlated order-flow features, which
is the regime where single-column MDA understates and MDI overstates.

##### a.9 Evidence
| Claim | Source (type) | Verbatim quote | File |
|---|---|---|---|
| Permutation importance origin: out-of-bag values of one variable permuted, percent increase in error | Breiman 2001, Machine Learning 45 (academic) | "After each tree is constructed, the values of the mth variable in the out-of-bag examples are randomly permuted and the out-of-bag data is run down the corresponding tree." ... "The output is the percent increase in misclassification rate as compared to the out-of-bag rate (with all variables intact)." | breiman_2001_random_forests.pdf/.txt |
| MDI, MDA, SFI definitions; SFI avoids the substitution effect | Falces Marin et al. 2022, PLOS ONE (academic, applying AFML/MLfinlab) | "Mean decrease impurity (MDI), a feature-specific measure of the mean reduction of weighted impurity over all the nodes in the tree ensemble"; "Single feature importance (SFI), an out-of-sample estimator of the individual importance of each feature, that avoids the substitution effect found with MDI and MDA (important features are ignored when highly correlated with other important features)." | falces_marin_2022_plosone.pdf/.txt (lines 729-739) |
| Clustered feature importance comes from MLAM (2020) section 6.5.2 and is used with MDI and MDA | MLfinlab-fork documentation (practitioner software docs) | "described in the book Machine Learning for Asset Manager (snippet 6.5.2.1 page-85). This subsets can be further utilised for getting Clustered Feature Importance using the clustered_subsets argument in the Mean Decreased Impurity (MDI) and Mean Decreased Accuracy (MDA) algorithm." | mlfinlab_fork_feature_clusters.html/.txt |
| MLAM chapter 6 is "Feature Importance Analysis" | Cambridge University Press table of contents (publisher) | "6 Feature Importance Analysis 74" | lopezdeprado_2020_mlam_toc.pdf/.txt |
| Clustered MDA permutes the whole cluster jointly; ONC clustering on a dependence metric | López de Prado 2020, MLAM 6.5 | not read in full text | [unverified: book not available as free full text; mechanism as described in the docs row above] |
| AFML ch. 8 sections "Feature importance with substitution effects" (8.3) and "without substitution effects" (8.4) | AFML 2018 table of contents | search-result snippet only | [unverified: library catalogue page returned an anti-bot stub, see log] |
| Importance is a research tool, backtesting is not | López de Prado 2018, "The 10 reasons most ML funds fail", JPM (practitioner-academic) | "Remember, feature importance is a research tool, and backtesting is not." | lopezdeprado_2018_10reasons_jpm.pdf/.txt (line 183) |
| Gini (MDI) importance unreliable when predictors differ in scale or number of categories | Strobl, Boulesteix, Zeileis, Hothorn 2007, BMC Bioinformatics (academic) | "random forest variable importance measures are a sensible means for variable selection in many applications, but are not reliable in situations where potential predictor variables vary in their scale of measurement or their number of categories"; "the Gini importance is most strongly biased" | strobl_etal_2007_pmc.html/.txt |
| Permutation importance overestimates correlated predictors; conditional permutation proposed | Strobl et al. 2008, BMC Bioinformatics (academic) | "We know that the original permutation importance overestimates the importance of correlated predictor variables."; "we develop a new, conditional permutation scheme for the computation of the variable importance measure" | strobl_etal_2008_conditional_pmc.html/.txt |
| Permutation forces extrapolation; re-learning is the alternative | Hooker, Mentch, Zhou 2021, arXiv 1905.03151v2 (academic) | "breaking dependencies between features in hold-out data places undue emphasis on sparse regions of the feature space by forcing the original model to extrapolate to regions where there is little to no data"; "A more general approach is re-learning, which generally involves measuring the drop in model performance when the effects of the features in question are muted." | hooker_mentch_zhou_arxiv_1905_03151.pdf/.txt |
| Rashomon effect: different good models rely on different covariates | Fisher, Rudin, Dominici 2019, JMLR 20 (academic) | "the model used by one analyst may rely on entirely different covariate information than the model used by another analyst. This common scenario has been called the "Rashomon" effect of statistics" | fisher_rudin_dominici_2019_jmlr.pdf/.txt |
| MDA least stable; no method converges to one feature set; not only substitution | Man and Chan 2020, arXiv 2005.12483 (ICAIF'20, academic) | "the instability index of MDA computed on the validation set is consistently higher than that of LIME and SHAP, which means MDA is the least stable method"; "none of the algorithms converges to a single feature set even if the number of random iterations is large, and this isn't solely due to the substitution effect" | man_chan_2020_arxiv_2005_12483.pdf/.txt |
| Selection bias when CV is not external to selection | Ambroise and McLachlan 2002, PNAS 99(10) (academic) | "the cross-validation of the rule is not external to the selection process; that is, gene selection is not performed in training the rule at each stage of the cross-validation process"; "when correction is made for the selection bias, the cross-validated error is no longer zero for a subset of only a few genes" | ambroise_mclachlan_2002_pnas_pmc.html/.txt |

Stopping rule (a): 8 full-text sources read on this topic; my last 3 discovery searches (clustered feature
importance PDF, MLAM PDF, smallake mirror) surfaced no new primary text, only blogs (MQL5, IBKR Campus, Numerai
forum), which are pointers only and are not cited.

#### (b) Stability across months and regimes

All P&L below is the net per-trade outcome x_i in ticks of the one frozen candidate on the window being judged
(discovery folds' out-of-sample P&L in E.33; the test window once, in the later test stage). Monte Carlo results are
synthetic (M5b_calc_out.txt sections b1-b5), not data.

##### b.1 Core idea
A real minutes-scale edge should show up in most months and quarters, in every volatility regime, and should not
rest on one month. These checks are stability REQUIREMENTS, not significance tests: under the null they are weak
filters (a share-of-quarters rule passes a no-edge candidate 9-13% of the time), but they catch the failure the
t-statistic cannot see, a total built from one episode. Significance comes from the HAC t (M5a, and c.2 here) and a
stationary bootstrap that resamples whole trade dates.

##### b.2 Equations
Notation: trade dates t = 1..T; D_t = sum of x_i over trades whose ENTRY falls on date t (zero if none); months
m = 1..M with P_m = sum_{t in m} D_t; blocks of 3 months q = 1..Q with P_q; total P = sum_m P_m; overall
noncentrality delta = E[t-stat] = mu sqrt(n_eff) / sigma (c.2).

1. Share of months positive: S_M = #{m : P_m > 0}. Null (mu = 0, months independent, P(P_m > 0) = 1/2):
   S_M ~ Binomial(M, 1/2), P0(S_M >= k) = sum_{j=k..M} C(M, j) 2^{-M}.
   Alternative, equal trades per month: P(P_m > 0) = Phi(delta / sqrt(M)), because each month carries 1/M of the
   total and its own z-score has mean delta / sqrt(M).
2. Two-thirds-of-quarters rule (planner pointer): pass if S_Q >= ceil(2Q/3).
3. Dominance: share_max = max_m P_m / P (defined when P > 0); leave-one-month-out t:
   t_{-m} = (P - P_m) / (s_LR sqrt((T - T_m))) computed with the same HAC estimator on the dates outside month m.
   In the Monte Carlo, months are iid N(delta/sqrt(M), 1) units, so t_{-m} = (sum - x_m)/sqrt(M - 1).
4. Stationary bootstrap by day (Politis and Romano 1994): build D*_1..D*_T by taking D*_1 = D_{I_1} with I_1
   uniform on 1..T, and, given D*_i = D_J, set D*_{i+1} = D_{J+1} with probability 1 - p and a fresh uniform draw
   with probability p (indices past T wrap to the start). Block lengths are then geometric with mean 1/p, and the
   resampled series is stationary conditional on the data. One-sided bootstrap p-value for H0: mu <= 0:
   p_boot = (1 + #{b : mean(D*_b) - mean(D) >= mean(D)}) / (B + 1), B >= 10,000.
   Mean block length 1/p by Politis and White (2004) with the Patton, Politis and White (2009) correction, as
   implemented in the `arch` package's `optimal_block_length`:
   b_SB = (2 g^2 / D_SB)^{1/3} T^{1/3}, D_SB = 2 sigma_LR^4 (corrected), so b_SB = (g^2 / sigma_LR^4)^{1/3} T^{1/3},
   g = sum_{k=-m..m} lambda(k/m) |k| gamma_k, sigma_LR^2 = sum_{k=-m..m} lambda(k/m) gamma_k,
   lambda(x) = min(1, 2(1 - |x|)) (flat-top), gamma_k the sample autocovariance of D_t at lag k, m chosen from the
   autocorrelations (arch docs: the first m where k_n consecutive autocorrelations are inside
   +-2 sqrt(log10(T)/T), k_n = max(5, log10 T)).
   For an AR(1) day series with coefficient phi (my closed form, flat-top window ignored):
   gamma_k = gamma_0 phi^|k|, g = 2 gamma_0 phi/(1 - phi)^2, sigma_LR^2 = gamma_0 (1 + phi)/(1 - phi), so
   b_SB = T^{1/3} (2 phi / (1 - phi^2))^{2/3}.
5. Regime splits. Volatility terciles: v_t = a causal volatility measure known before the session that contains the
   trade (for example the realized volatility of ZM 1-minute returns over the previous 20 trade dates); cut points
   c_1 < c_2 are the 1/3 and 2/3 quantiles of v_t over DISCOVERY dates and are frozen in the protocol; the test
   window uses the same cut points (its terciles may be unequal in size). Oil-share regime: OS_t = 0.11 O / (0.022 M +
   0.11 O) with O the ZL price in cents/lb and M the ZM price in USD per short ton, from the previous settlement
   (R3a_crush.md lines 51-60, 44 lb board crush), split at a frozen discovery median or at fixed values. Per-regime
   statistics: mean, HAC t and trade count in each cell; with a share 1/3 of the trades, z_r has mean delta/sqrt(3).

##### b.3 Worked examples (M5b_calc_out.txt)
1. Binomial null, months (b1). Test window M = 43: share >= 2/3 means k = ceil(28.67) = 29, P0 = 0.0158; share
   >= 0.6 (k = 26): P0 = 0.1110; share >= 0.75 (k = 33): 0.0003. Discovery M = 39: k = 26, P0 = 0.0266.
   Check: the normal approximation for M = 43 gives z = (28.5 - 21.5)/sqrt(43 x 0.25) = 7/3.279 = 2.135, upper
   tail 0.0164, close to 0.0158.
2. Two-thirds of quarters (b1, b2). Discovery Q = 13: k = 9, P0 = 0.1334 (so 13% of no-edge candidates pass the
   rule by itself). Test Q = 14: k = 10, P0 = 0.0898. Under an edge sized for 80% power at t > 3 (delta = 3.84, c.3),
   each quarter is positive with probability Phi(3.84/sqrt(13)) = Phi(1.065) = 0.857; Monte Carlo: P(rule passes)
   = 0.971 (discovery), 0.949 (test); P(t > 3 AND rule) = 0.797 (discovery) and 0.791 (test) against P(t > 3) =
   0.800. **Reading: the two-thirds-of-quarters rule costs about 1 point of power at delta = 3.84 and 1-2 points at
   delta = 3.0; it is cheap insurance, not a filter that adds significance.** A two-thirds rule on MONTHS costs more:
   at delta = 3.84 over 43 test months, P(t > 3 AND >= 29 positive months) = 0.726 vs 0.800, a 7-point power loss;
   at delta = 3.0, 0.429 vs 0.501.
3. Dominance (b3), given t > 3, delta = 3.84: the largest month carries a median 10.3% (43 months) or 10.8% (39) of
   the total, 99th percentile 16.9% / 17.7%; a rule "no month above 25% of total P&L" rejects essentially no real
   edge (P(share <= 0.25 | t > 3) = 1.000 in 200,000 draws). The leave-one-month-out minimum t has 1st percentile
   2.63 (43 months); a rule "every LOMO t > 2.5" keeps 99.9% of real-edge passes. Counter-case: 42 noise months and
   one month at +6 SD gives t > 3 in 1.7% of draws (b3 "spike example"). Check by hand: with 42 null months the
   total is N(6, 42), and t > 3 needs total > 3 sqrt(43) = 19.67, i.e. z > (19.67 - 6)/6.481 = 2.11, tail 0.0174.
   Matches 0.0173. Among those false passes (M5b_calc3_out.txt, 2,000,000 draws, spike month = 6 + its own N(0,1)
   noise): the 25% rule catches 78.5%, the LOMO t > 2.5 rule 66.3%, either rule 82.4%; with a +10 SD spike month
   (t > 3 in 7.0% of draws) the 25% rule catches 100%. So the dominance rules remove most, not all, one-episode
   passes, at almost no cost to real edges.
4. Volatility terciles (b4). With 1/3 of the trades in each tercile, z_r has mean delta/sqrt(3). At delta = 3.84:
   2.217, P(all three positive) = Phi(2.217)^3 = 0.9867^3 = 0.961; P(all three z > 1.645) = Phi(0.572)^3 = 0.716^3
   = 0.368. **Same sign in every tercile is a cheap requirement (4% power loss); significance in every tercile is not
   (it keeps 37% of real edges).** Requiring z > 1.0 in each keeps 70%.
5. Stationary-bootstrap block length (b5). Test window T = 904 trade dates, phi = 0.1: T^{1/3} = 9.670,
   2 phi/(1 - phi^2) = 0.2/0.99 = 0.20202, ^(2/3) = 0.34427, b_SB = 9.670 x 0.34427 = 3.33 days (p = 0.300).
   Numeric sums agree to 3 decimals (script). phi = 0.05: 2.09 days; phi = 0.2: 5.39; phi = 0.3: 7.33.
   Discovery T = 816, phi = 0.1: 3.22 days. Sanity bound: b_SB -> 0 as phi -> 0 (iid days, no blocks needed); the
   arch implementation floors it at 1.
6. Month-sign test under skew (a trap, see b.5 item 1): with mean zero, P(P_m > 0) = 1/2 only if the monthly P&L is
   symmetric. A strategy with many small wins and rare large losses (negative skew, typical of fading moves with a
   wide stop) has P(P_m > 0) > 1/2 at zero mean, so the binomial null overstates significance. The day-block
   bootstrap null, which resamples the de-meaned D_t, handles this.

##### b.4 Data it needs
D_t from the candidate's frozen trade list (entries, exits, net P&L in ticks, entry timestamps), the trade-date
calendar (DataFacts), causal ZM realized volatility (from ZM MBO trades or 1-minute bars built from it), ZM and ZL
previous settlements for the oil share (ZL from MBP-1; settlements: if no statistics schema is owned, use the last
trade before the 13:15 CT close, as DataFacts specifies). All on discovery; the test window only at the one test.

##### b.5 Leakage and look-ahead traps, each with a test
1. Binomial null under skew (b.3 item 6). Test: compute the null share-of-months distribution by stationary
   bootstrap of D_t - mean(D) and compare with the binomial; report the bootstrap one.
2. Tercile cut points computed on the whole sample including the test window. Test: cut points are written into
   the frozen protocol with its hash before the seal is opened; the test-stage script reads them, never recomputes.
3. Same-day volatility that includes the trade's own path. Test: assert v_t's latest input timestamp < the entry
   timestamp for every trade; a shift test (v lagged one more day) must leave tercile labels unchanged on days where
   the lag already applies.
4. Bootstrap over trades instead of days: trades on the same day share shocks (c.2 design effect). Test: compare
   the bootstrap SE over trades with the one over days; a smaller trade-level SE is the symptom.
5. Choosing the block length or the month/quarter partition after seeing results. Test: the rule (arch
   `optimal_block_length`, column b_sb, on the discovery D_t) and the partition (calendar months; 3-month blocks
   from the window start) are in the protocol; the test stage recomputes b_sb on test D_t by the same rule.
6. Months with few trades: a month with 3 trades is "positive" by noise. Test: report trades per month; count a month
   in S_M only if it has at least a declared minimum, or use 3-month blocks (the planner's quarters).
7. Oil-share split chosen after looking: the planner expects a regime break between discovery (renewable-diesel era)
   and test (2017-20); the split value must be frozen before the test, and any OS-conditioned rule counts into N.

##### b.6 Compute
Trivial: D_t has under 1,000 entries; 10,000 stationary-bootstrap resamples of 904 values take well under a second
in NumPy; the Monte Carlo above (200,000 draws per cell) ran in seconds.

##### b.7 Verdict
USE: (i) the day-block stationary bootstrap p-value next to the HAC t; (ii) the two-thirds-of-3-month-blocks rule
as a stability requirement (about 1 point of power at delta 3.84); (iii) a dominance requirement "no single month
above 25% of total net P&L" plus "every leave-one-month-out t above a declared floor" (2.5 costs about 0.1 point of
power at delta 3.84); (iv) same sign of mean net P&L in each frozen volatility tercile. MAYBE: oil-share regime
split, reported descriptively (the regime differs between windows by the planner's own account, so a hard
requirement could fail a real edge for a known reason). SKIP: requiring significance inside every regime cell
(keeps only 37% of real edges at delta 3.84). The thresholds are the lead's decision (P8); these numbers are their
cost.

##### b.8 Evidence
| Claim | Source (type) | Verbatim quote | File |
|---|---|---|---|
| Stationary bootstrap algorithm: continue the block with probability 1 - p, jump with p; resampled series stationary | Politis and Romano 1994b, Statistica Sinica 4, 461-476, p. 468 (academic; same authors, describes the JASA 1994 scheme) | "let X*_{i+1} be equal to X_{J+1} with probability 1 - p and picked at random from the original n observations with probability p. This description makes it clear that, conditional on X_1, ..., X_n, the new process X*_1, ..., X*_n is indeed stationary." (read from the scanned page image; subscripts typed) | politis_romano_1994_stat_sinica.pdf (scanned, no text layer; read as images, pp. 1-2, 8-11) |
| Wrap-around past n | same, p. 470 | "with n fixed, let X_j for j > n be defined to be X_{j-n}." | same |
| The stationary bootstrap was introduced by Politis and Romano (1991; published JASA 89(428), 1994) for weakly dependent stationary data | same, abstract p. 461 | "In Politis and Romano (1991), a resampling procedure, called the stationary bootstrap, is introduced as a means of calculating standard errors of estimators and constructing confidence regions for parameters based on weakly dependent stationary observations." | same |
| JASA 1994 paper itself (geometric block lengths in the abstract) | Politis and Romano 1994, JASA 89, 1303-1313 | not read in full text | [unverified: JSTOR only; repository record page returned a Cloudflare 403] |
| Optimal block length corrected: D_SB = 2 g^2(0) | Patton, Politis, White 2009, Econometric Reviews 28(4) (academic) | "The correct value for the variance constant DSB defined in Theorem 3.1 of Politis and White (2004) is DSB = 2g 2 (0);" (pdftotext layout) | patton_politis_white_2009_correction.pdf/.txt |
| Implementation: b_opt = (2 g^2 / d_i n)^{1/3}, flat-top lambda, m rule | arch documentation, optimal_block_length (software docs) | "The block length is then computed as b^{OPT}_i = \left(\frac{2g^2}{d_{i}} n\right)^{\frac{1}{3}}"; "h(x) & = \min(1, 2(1-|x|))"; "d_{i} & = c_{i} \left(\hat{\sigma}^2\right)^2"; "the two remaining constants c_i are 2 for the Stationary" | arch_docs_optimal_block_length.html; arch_bootstrap_base_py.txt (source read, not run) |
| Stability by month and by volatility regime is step 6 of the E.28 minimum research process | E.28 2.11 section 4 (program) | "stability by month and by volatility regime; if every configuration breaks at the same date, record a regime change, not a model failure (E9)." | reports/stage_e28_methods_brief.md line 11968 |
| Board crush 44 lb meal, 11 lb oil; oil share formula | R3a_crush.md lines 27-60 (E.32 sibling worker, sources there) | "OS = 0.11 * O / (0.022 * M + 0.11 * O) under 44 lb" | reports/stage_e32_briefs/R3a_crush.md |

Stopping rule (b): the binomial, Monte Carlo and AR(1) block-length results are my own derivations and need no
source beyond those above; 3 discovery searches for the JASA full text found none.

#### (c) Power: trades needed to detect a minimum net edge, with overlap and autocorrelation

##### c.1 Core idea
The one-shot test on 2017-05..2020-11 can only confirm an edge it has the sample to see. The number of trades
needed grows with the square of (per-trade noise / edge); overlapping or same-day trades add less information than
their count suggests; and testing up to 3 candidates raises the bar. The result is a gate for E.33's selection rule
(P8): a candidate whose expected test-window trade count cannot give about 80% power at the test bar should not use
one of the 3 test slots, however good its discovery numbers look.

##### c.2 Equations
Notation: x_i net P&L of trade i (ticks), mean mu, SD sigma; n trades; rho_k the lag-k autocorrelation of the
trade series (in time order); c the one-sided critical value; z_{1-beta} the power quantile.

1. iid, one-sided test of H0: mu <= 0 (normal approximation; with n in the hundreds or more the t and normal
   critical values agree to 2 decimals):
   delta = mu sqrt(n) / sigma (noncentrality); power = 1 - Phi(c - delta);
   n_iid = ((c + z_{1-beta}) sigma / mu)^2; minimum detectable edge mu_min = (c + z_{1-beta}) sigma / sqrt(n).
   This is E.28 2.7 section 12's rule, made one-sided and with the stage's critical values.
2. Critical values. Up to 3 candidates tested once: Bonferroni (and Holm for the first rejection) uses
   alpha = 0.05/3 one-sided, c = z(0.98333) = 2.1280. The program bar t > 3.0 is one-sided alpha 0.00135 and is
   stricter, so when both apply c = 3.0 binds. z_{0.8} = 0.8416. delta at 80% power: 2.128 + 0.842 = 2.970 or
   3.0 + 0.842 = 3.842.
[MathReview C-6/C-9 (lead: ruled): the frozen test bar is the program verdict plus a protocol-added DSR >= 0.95 at N with V = 1/(T_test - 1) (t about 4.86 at N 838, T 870); see reports/stage_e32_discovery_protocol.md P7.2 and P9.]
3. Dependence (Lo 2002 eq. 19 gives the variance of a q-period sum; dividing by q^2 gives the mean):
   Var(xbar) = (sigma^2 / n) [1 + 2 sum_{k=1..n-1} (1 - k/n) rho_k] ~= (sigma^2 / n) D, D = 1 + 2 sum_k rho_k;
   n_eff = n / D; raw trades needed n = D n_iid. Lo's eq. 20 is the same factor applied to Sharpe ratios:
   SR(q) = eta(q) SR, eta(q) = q / sqrt(q + 2 sum_{k=1..q-1} (q - k) rho_k).
4. Overlapping holds. Entries every Delta minutes, each held h = m Delta minutes, price a random walk: consecutive
   trades share m - k of their m increments, so rho_k = 1 - k/m (k < m) and 0 beyond;
   D = 1 + 2 sum_{k=1..m-1} (1 - k/m) = 1 + (m - 1) = m. So n_eff = n/m: overlapping entries carry no more
   information than non-overlapping ones. (My derivation; simulated check below.)
5. Same-day clustering. k trades a day with a common within-day correlation rho_w (shared regime, news, liquidity):
   D_day = 1 + (k - 1) rho_w (variance of a sum of k equicorrelated terms divided by k sigma^2).
6. HAC estimator (Newey and West 1987, eq. (5) of the 1986 working paper):
   S_hat = Omega_0 + sum_{j=1..m} w(j, m) [Omega_j + Omega_j'], w(j, m) = 1 - j/(m + 1), Omega_j = sum_{t=j+1..T}
   h_t h_{t-j}' / T. For a mean, h_t = D_t - Dbar, and t_NW = Dbar / sqrt(S_hat / T). Run it on the DAILY series D_t
   (b.2), which absorbs all within-day overlap and clustering, so the lag m only has to cover day-to-day dependence.
   A common automatic lag is floor(4 (T/100)^{2/9}) = 6 for T = 816 and for T = 904 [rule attributed to Newey and
   West 1994; not read here].
7. Daily units: with k trades a day, E[D_t] = k mu and Var(D_t) = k sigma^2 D_day; the daily t over T days equals the
   trade-level t with n = kT and D = D_day, so both routes give the same power.
8. Gate for P8 (a formula, the thresholds are the lead's): a candidate with expected test trades a day k_test,
   haircut net edge mu_h (ticks), per-trade SD sigma_h and dependence factor D needs
   k_test x 904 >= D ((c + 0.8416) sigma_h / mu_h)^2, with c = 3.0 if the program bar applies.
[MathReview C-6/C-9 (lead: ruled): the frozen test bar is the program verdict plus a protocol-added DSR >= 0.95 at N with V = 1/(T_test - 1) (t about 4.86 at N 838, T 870); see reports/stage_e32_discovery_protocol.md P7.2 and P9.]

##### c.3 Worked examples (M5b_calc_out.txt c1-c3; sigma from section 0; random-walk scaling ASSUMED; non-overlapping
trades, D = 1)
Arithmetic of one cell by hand: h = 15, mu = 0.5, c = 3.0: (3.0 + 0.8416) x 12.200 / 0.5 = 3.8416 x 24.400 = 93.735;
93.735^2 = 8,786 trades; over 904 test dates 8,786/904 = 9.72 a day; over 816 discovery dates 10.77 a day.
Check: delta = 0.5 sqrt(8,786)/12.2 = 0.5 x 93.73/12.2 = 3.842 = 3.0 + 0.842.

Trades needed for 80% power (n), and per trade date over the test (904) and discovery (816) windows. Last two
columns: the most non-overlapping holds a single position can make per date, all sessions (1,055/h) and day session
only (290/h).

| h (min) | sigma_h | mu net | n, alpha 0.05/3 | /test day | /disc day | n, t > 3.0 | /test day | /disc day | cap all | cap day |
|---|---|---|---|---|---|---|---|---|---|---|
| 5 | 7.044 | 0.25 | 7,000 | 7.74 | 8.58 | 11,715 | 12.96 | 14.36 | 211.0 | 58.0 |
| 5 | 7.044 | 0.50 | 1,750 | 1.94 | 2.14 | 2,929 | 3.24 | 3.59 | 211.0 | 58.0 |
| 5 | 7.044 | 1.00 | 438 | 0.48 | 0.54 | 732 | 0.81 | 0.90 | 211.0 | 58.0 |
| 15 | 12.200 | 0.25 | 21,001 | 23.23 | 25.74 | 35,145 | 38.88 | 43.07 | 70.3 | 19.3 |
| 15 | 12.200 | 0.50 | 5,250 | 5.81 | 6.43 | 8,786 | 9.72 | 10.77 | 70.3 | 19.3 |
| 15 | 12.200 | 1.00 | 1,313 | 1.45 | 1.61 | 2,197 | 2.43 | 2.69 | 70.3 | 19.3 |
| 60 | 24.400 | 0.25 | 84,005 | 92.93 | 102.95 | 140,579 | 155.51 | 172.28 | 17.6 | 4.8 |
| 60 | 24.400 | 0.50 | 21,001 | 23.23 | 25.74 | 35,145 | 38.88 | 43.07 | 17.6 | 4.8 |
| 60 | 24.400 | 1.00 | 5,250 | 5.81 | 6.43 | 8,786 | 9.72 | 10.77 | 17.6 | 4.8 |

Minimum detectable net edge at 80% power over the 904 test dates, by trades a day (non-overlapping, D = 1):

| h | bar | 1/day | 2/day | 5/day | 10/day | 20/day |
|---|---|---|---|---|---|---|
| 5 | 0.05/3 | 0.696 | 0.492 | 0.311 | 0.220 | 0.156 |
| 15 | 0.05/3 | 1.205 | 0.852 | 0.539 | 0.381 | 0.269 |
| 60 | 0.05/3 | 2.410 | 1.704 | 1.078 | 0.762 | 0.539 |
| 5 | t > 3.0 | 0.900 | 0.636 | 0.402 | 0.285 | 0.201 |
| 15 | t > 3.0 | 1.559 | 1.102 | 0.697 | 0.493 | 0.349 |
| 60 | t > 3.0 | 3.118 | 2.204 | 1.394 | 0.986 | 0.697 |

Readings:
- Because sigma_h grows as sqrt(h), n scales with h at fixed mu: 60-minute trades need 4 times the trades of
  15-minute ones (5,250 vs 1,313 at mu = 1, alpha 0.05/3) and 12 times those of 5-minute ones.
- At 60 minutes, mu = 0.5 is not testable: it needs 23.2 (alpha 0.05/3) or 38.9 (t > 3) non-overlapping trades a
  date against a ceiling of 17.6 (all sessions) or 4.8 (day session). Only mu >= 1 tick is testable at 60 minutes,
  and at t > 3 even that needs 9.7 a date, i.e. trading most overnight hours. mu = 0.25 is testable only at 5
  minutes (7.7 to 13.0 a date).
- At 15 minutes: mu = 0.5 needs 5.8 to 9.7 trades a date (feasible in the day session, cap 19.3); mu = 1 needs
  1.5 to 2.4.
- Overlap check (c2-c3): m = 3 (15-minute holds entered every 5 minutes): theory D = 3; simulation (2,000 paths of
  600 five-minute steps) gives 3.04. So entering a 15-minute trade every 5 minutes triples the count but not the
  information.
- Same-day clustering: 10 trades a day with rho_w = 0.05 gives D = 1 + 9 x 0.05 = 1.45, i.e. 45% more trades for the
  same power; with rho_w = 0.1, 1.90. rho_w is unknown until discovery; E.33 should estimate it on discovery D_t
  (ratio of the daily-sum variance to k sigma^2) and carry it into the gate.
- HAC shortfall (c4): Bartlett weights shrink the long-run variance in finite lags. Daily AR(1) phi = 0.2: true
  ratio (1 + 0.2)/(1 - 0.2) = 1.5; Newey-West with 5 lags gives 1 + 2 sum_{j=1..5} (1 - j/6) 0.2^j = 1.3958, so
  the NW t is too large by sqrt(1.5/1.3958) = 1.037. Small, but in the anti-conservative direction; the day-block
  bootstrap is the cross-check.
- Winner's curse: the candidate's discovery edge is the maximum over many configurations and is biased upward; E.28
  2.11 records Harvey and Liu's worked example in which multiple testing cuts a Sharpe ratio by 52.0% (E.28 2.11,
  line 11626). Plan the gate with a haircut mu_h (for example half the discovery net edge) rather than the point
  estimate. The haircut value is the lead's decision.

##### c.4 Planner pointer: "about 40 major events in the discovery window": power of an event-family test
Setup: one trade per event, entered 5-15 minutes after an 11:00 CT USDA release and held to 90 minutes after it, so
at most 75 minutes; sigma_75 = 3.15 x sqrt(75) = 3.15 x 8.660 = 27.28 ticks under the random walk; event days are
noisier, so k_ev in {1.0, 1.5, 2.0} scales sigma. Event counts: 40 (planner), 49 (R4_events.md line 235: 15 major
USDA days a year x 39/12), 24 (R4's median split into "big" events), 54 (the test window: 15 x 43/12 = 53.75).

Minimum detectable net edge at 80% power (ticks) and power at a net edge of 2 ticks (M5b_calc_out.txt c5):

| n events | k_ev | sigma | MDE, one-sided 0.05 | MDE, 0.05/3 | MDE, t > 3 | power at 2 ticks (0.05 / 0.05/3 / t > 3) |
|---|---|---|---|---|---|---|
| 24 | 1.0 | 27.28 | 13.85 | 16.54 | 21.39 | 0.099 / 0.038 / 0.004 |
| 40 | 1.0 | 27.28 | 10.72 | 12.81 | 16.57 | 0.119 / 0.048 / 0.006 |
| 40 | 1.5 | 40.92 | 16.09 | 19.21 | 24.86 | 0.091 / 0.034 / 0.004 |
| 40 | 2.0 | 54.56 | 21.45 | 25.62 | 33.14 | 0.079 / 0.029 / 0.003 |
| 49 | 1.0 | 27.28 | 9.69 | 11.57 | 14.97 | 0.129 / 0.053 / 0.006 |
| 54 | 1.0 | 27.28 | 9.23 | 11.02 | 14.26 | 0.134 / 0.056 / 0.007 |

By hand, n = 40, k_ev = 1, one-sided 0.05: (1.6449 + 0.8416) x 27.28 / sqrt(40) = 2.4865 x 27.28 / 6.3246 =
67.83 / 6.3246 = 10.72 ticks. Power at 2 ticks: 1 - Phi(1.6449 - 2 x 6.3246/27.28) = 1 - Phi(1.6449 - 0.4637) =
1 - Phi(1.1812) = 0.119. (With n = 40 the t critical value with 39 df is 1.685 rather than 1.645, so these normal
numbers are slightly optimistic.)

Reading: with about 40 events, an event-direction family can only detect net edges of 10 to 33 ticks per event,
i.e. 1/3 to more than 1 full 75-minute SD. A plausible edge of 1-2 ticks has 5-12% power at a lenient 5% level and
under 1% at t > 3. More trades per event do not help (c.2 item 4: overlapping holds inside one event window share
the same path, D ~ m). The family is untestable as a stand-alone one-shot candidate; it can enter only as a
conditioning flag on a high-frequency family, or be dropped. This is a power statement, not a statement that the
effect is absent.

##### c.5 Data it needs
Discovery-window estimates of sigma_h (per-trade net P&L SD, not the random-walk proxy), the candidate's trade rate
by session, the lag autocorrelations of the trade series and of D_t, rho_w, and the frozen trade-date calendars of
both windows (DataFacts). The sealed window supplies nothing until the test.

##### c.6 Leakage and look-ahead traps, each with a test
1. Raw counts of overlapping trades used as n (overstates power and the t). Test: compute D on discovery as
   Var(sum over a day)/ (k sigma^2) and from the lag autocorrelations; the gate uses n / D.
2. Power planned on the discovery point estimate (winner's curse). Test: simulate the selection (the max of N
   null-plus-signal configurations) and compare the selected configuration's discovery edge with its true edge;
   the gap is the haircut.
3. sigma or trade rate measured on the test window to "check feasibility" before the test: that is a peek at sealed
   data. Test: the gate's inputs are written into the protocol, hashed, before the seal is opened.
4. A regime with lower volatility in the test window raises power, a higher one lowers it; the gate uses discovery
   sigma and should state the test window's volatility as unknown.
5. Event families: counting events after seeing which releases moved the market (for example dropping "quiet"
   reports) inflates the edge. Test: the event list is the frozen USDA calendar (R4), all events kept.

##### c.7 Compute
Closed-form; the Monte Carlo checks ran in seconds.

##### c.8 Verdict
USE as a P8 gate: a candidate takes a test slot only if D-adjusted, haircut power at the binding bar (t > 3.0, which
is stricter than 0.05/3) is at least the lead's threshold over 904 test dates. On the standard numbers this rules out
60-minute holds below 1 tick net, any 15-minute rule trading under about 2.4 non-overlapping trades a date at
mu = 1 (9.7 at mu = 0.5), and a stand-alone USDA event family.
[MathReview C-6/C-9 (lead: ruled): the frozen test bar is the program verdict plus a protocol-added DSR >= 0.95 at N with V = 1/(T_test - 1) (t about 4.86 at N 838, T 870); see reports/stage_e32_discovery_protocol.md P7.2 and P9.]

##### c.9 Evidence
| Claim | Source (type) | Verbatim quote | File |
|---|---|---|---|
| Variance of a q-period sum with autocorrelation | Lo 2002, FAJ 58(4), eq. 19 (academic) | "= qσ 2 + 2σ 2 ∑ ( q – k )ρk , where ρk ≡ Cov(Rt , Rt–k)/Var(Rt) is the kth-order autocorrelation of Rt." (pdftotext layout) | lo_2002_faj_statistics_sharpe.pdf/.txt, lines 305-311 |
| Time-aggregation factor eta(q) | Lo 2002 eq. 20 | "SR ( q ) = η ( q ) SR, η ( q ) ≡ ... q + 2 ∑ q –1 ( q – k )ρk" and "Note that Equation 20 reduces to Equation 17 if all autocorrelations ρk are zero" | same, lines 313-320 |
| Bartlett-weighted HAC estimator | Newey and West, NBER Technical Working Paper 55 (April 1986; published Econometrica 55, 1987), eq. (5) (academic) | "S_T = Ω_0 + Σ_{j=1}^m w(j,m)[Ω_j + Ω_j'], w(j,m) = 1 - [j/(m+1)]." and "This estimator is numerically equal to 2π times an estimator of the spectral density of h_t(θ*) at frequency zero, where the modified Bartlett weights are used" (scanned page 3 read as an image; hats and tildes typed) | newey_west_1986_nber_t0055.pdf (scanned, no text layer) |
| Program power rule (two-sided form) | E.28 2.7 section 12 (program) | "n = ((1.96 + 0.8416) sigma / delta)^2 *effective* observations" | reports/stage_e28_methods_brief.md line 8054 |
| Event count about 49 in discovery | R4_events.md (E.32 sibling) | "Over the 39-month discovery window: 15 x 39 / 12 = 48.75, about 49" | reports/stage_e32_briefs/R4_events.md line 235 |
| Harvey-Liu haircut example 52.0% | E.28 2.11 (program, sources there) | "autocorrelation-corrected SR is 0.912 and the BHY-adjusted SR is 0.438, a 52.0% haircut (E16)" | reports/stage_e28_methods_brief.md line 11626 |
| Newey-West 1994 automatic lag rule floor(4(T/100)^{2/9}) | Newey and West 1994 | not read | [unverified] |

#### (d) The Sharpe-ratio standard error with non-normal returns, and the minimum track record length

##### d.1 Core idea
The Sharpe ratio is an estimate with a standard error. Lo (2002) gives it under iid returns and under serial
dependence; Mertens (2002) adds skewness and kurtosis for iid non-normal returns, and Opdyke (2007) showed the same
expression holds for stationary and ergodic returns. Bailey and López de Prado (2012) turn it into the probabilistic
Sharpe ratio (PSR) and the minimum track record length (MinTRL): the number of observations needed before an
observed SR is significantly above a benchmark. For this program the per-trade SR is tiny (0.04-0.08), so higher
moments barely move the SE; dependence does. MinTRL is a 50%-power sample size, not an 80% one.

##### d.2 Equations
Notation: SR = mu/sigma per observation (per trade here), SR_hat its estimate from T observations, gamma_3 the
skewness, gamma_4 the kurtosis (3 for the normal; not excess), SR* a benchmark, Z the standard normal CDF.
1. iid normal (Lo 2002 eqs. 8-9): sqrt(T) (SR_hat - SR) ~a N(0, V_IID), V_IID = 1 + SR^2 / 2;
   SE(SR_hat) ~= sqrt((1 + SR^2/2) / T).
2. Dependent returns (Lo 2002 eqs. 14-15): V_GMM from a GMM/HAC estimate of the joint variance of (mu_hat,
   sigma_hat^2) and the delta method; SE(SR_hat) = sqrt(V_GMM_hat / T). For a mean-dominated SR (SR small), V_GMM ~=
   D, the long-run variance ratio of c.2, so SE ~= sqrt(D / T): the same factor as in the power calculation.
3. iid non-normal (Mertens 2002, as given by Bailey and López de Prado 2012 eq. 8; valid for stationary ergodic
   returns per Opdyke 2007):
   SR_hat ~a N( SR, (1 + SR^2/2 - gamma_3 SR + ((gamma_4 - 3)/4) SR^2) / T ).
   Equivalently V = 1 - gamma_3 SR + ((gamma_4 - 1)/4) SR^2, since (gamma_4 - 1)/4 = (gamma_4 - 3)/4 + 1/2; this
   second form is the one in BLdP's code.
4. PSR (BLdP 2012 eq. 11; their code `set_PSR`):
   PSR(SR*) = Z[ (SR_hat - SR*) sqrt(T - 1) / sqrt(1 - gamma_3 SR_hat + ((gamma_4 - 1)/4) SR_hat^2) ].
5. MinTRL (BLdP 2012 eq. 13; their code `set_TRL`), in observations, at confidence 1 - alpha:
   MinTRL = 1 + [1 - gamma_3 SR_hat + ((gamma_4 - 1)/4) SR_hat^2] (Z^{-1}(1 - alpha) / (SR_hat - SR*))^2.
6. Link to power: with SR* = 0 and moments normal, MinTRL ~= (c / SR)^2 = the n at which the expected t equals the
   critical value c, i.e. 50% power. The 80%-power sample is ((c + 0.8416)/SR)^2, larger by ((c + 0.8416)/c)^2:
   1.639 at c = 3.0, 1.776 at c = 2.128.
[MathReview C-8 (lead: accepted): the second number is wrong: ((2.1280 + 0.8416)/2.1280)^2 = (1.3955)^2 = 1.947, matching this file's own worked example 1,313/677 = 1.94 (d.3 item 2); 1.639 at c = 3.0 is right, and the verdict line "1.64 times MinTRL at t > 3" is unaffected.]
7. The DSR (M5a (d)) is the PSR with SR* set to the expected maximum SR of N null trials; it is not repeated here.

##### d.3 Worked examples (M5b_calc_out.txt d1-d2)
1. SE at h = 15, mu = 1 tick net: SR = 1/12.200 = 0.08197 a trade; SR^2 = 0.006719. T = 5,000 trades:
   naive 1/sqrt(5,000) = 0.014142; Lo iid sqrt(1.003359/5,000) = 0.014166 (+0.17%); Mertens with gamma_3 = -0.5,
   gamma_4 = 8: V = 1.003359 + 0.5 x 0.08197 + (5/4) x 0.006719 = 1.003359 + 0.040984 + 0.008399 = 1.052742;
   sqrt(1.052742/5,000) = 0.014510 (+2.6%); gamma_3 = -1, gamma_4 = 20: 0.014926 (+5.5%). Check: the ratio
   0.014510/0.014142 = 1.026 = sqrt(1.052742). Compare dependence: D = 1.45 (10 trades a day, rho_w = 0.05, c.3)
   inflates the SE by sqrt(1.45) = 1.204, i.e. +20%. **Non-normality is second order at these per-trade SRs;
   dependence is first order.**
2. MinTRL vs 80%-power n, SR* = 0 (normal moments; gamma_3 = -0.5, gamma_4 = 8 in brackets):
   - h = 15, mu = 1 (SR 0.08197), c = 3.0: MinTRL = 1 + 1.003359 x (3/0.08197)^2 = 1 + 1.003359 x 1,339.4 =
     1,345 (1,411); 80%-power n = 2,197. With c = 2.128: 677 (711) vs 1,313.
   - h = 5, mu = 0.5 (SR 0.07099), c = 3.0: 1,792 (1,866) vs 2,929.
   - h = 60, mu = 1, or h = 15, mu = 0.5 (both SR 0.04098), c = 3.0: 5,364 (5,485) vs 8,786.
   Check: 2,197 / 1,345 = 1.633, against the theoretical 1.639 (the small gap is the "1 +" and the SR^2 term).
3. In calendar terms: one 15-minute trade a date at mu = 1 is an annualised SR of 0.08197 x sqrt(251) = 1.30. Its
   MinTRL at t > 3 is 1,345 trades = 5.4 years at one a date, longer than the 3.6-year test window (904/251). Its
   power over 904 test dates: delta = 0.08197 x sqrt(904) = 0.08197 x 30.07 = 2.465; power = 1 - Phi(3 - 2.465) =
   1 - Phi(0.535) = 1 - 0.704 = 0.30. An annualised SR of 1.3 is not enough at one trade a day.

##### d.4 Data it needs
The candidate's net per-trade (or daily) P&L series from discovery out-of-sample folds: mean, SD, gamma_3, gamma_4,
autocorrelations. Moments above the second need long series (BLdP 2012 note that the fourth moment needs much longer
samples), so estimate gamma_3 and gamma_4 on all discovery trades, not per fold.

##### d.5 Leakage and look-ahead traps, each with a test
1. Annualising by sqrt(q) with autocorrelated daily P&L (Lo: up to 65% overstatement in his hedge-fund example).
   Test: report eta(q) from Lo eq. 20 with the estimated autocorrelations next to sqrt(q).
2. PSR or MinTRL with SR* = 0 after a search over N configurations: it ignores selection. Test: the program's bar is
   DSR at N (M5a), which uses SR* = the expected maximum of N null SRs.
3. Moments from too few trades: gamma_4 from a few hundred trades is unstable. Test: bootstrap (by day) the
   gamma_4 estimate and show its interval; if it is wide, report the normal-moment version beside it.
4. Mixing units: SR per trade with T in days, or daily SR with trade counts. Test: one unit per calculation, stated
   (M5a (d) checks the per-trade versus daily-with-zeros equivalence).

##### d.6 Compute
Closed form.

##### d.7 Verdict
USE the Lo/Mertens SE (with V_GMM or HAC for dependence) for confidence bands and the PSR as a reported statistic;
the program bar remains the DSR at N (M5a). Use MinTRL only with the warning that it is a 50%-power length; the P8
gate should use the 80%-power n of c.2, which is 1.64 times MinTRL at t > 3.

##### d.8 Evidence
| Claim | Source (type) | Verbatim quote | File |
|---|---|---|---|
| iid asymptotic variance V_IID = 1 + SR^2/2 | Lo 2002, FAJ 58(4) (academic) | "Note: Returns are assumed to be IID, which implies VIID = 1 + 1/2SR ." (pdftotext drops the superscript 2) | lo_2002_faj_statistics_sharpe.pdf/.txt line 223 |
| Non-iid SE from GMM | Lo 2002 eqs. 14-15 | "for non-IID returns, the standard error of the Sharpe ratio can be estimated by SE[SR] = V̂ GMM /T (15)" (square root lost in extraction) | same, lines 276-281 |
| Serial correlation can overstate annual SR by 65% | Lo 2002 abstract | "the annual Sharpe ratio for a hedge fund can be overstated by as much as 65 percent because of the presence of serial correlation in monthly returns" | same, lines 14-16 |
| Mertens: SR normal even if returns are not; skewness and kurtosis widen the band | Bailey and López de Prado 2012, J. Risk 15(2), "The Sharpe ratio efficient frontier", section 2.4 (academic) | "Mertens (2002) concludes that the Normality assumption on returns could be dropped, and still the estimated Sharpe ratio would follow a Normal distribution"; "although skewness and kurtosis does not affect the point estimate of SR, it greatly impacts its confidence bands" | bailey_ldp_2012_sharpe_frontier.pdf/.txt lines 308-318 |
| Opdyke: Mertens = Christie; valid for stationary ergodic returns | same, sections 2.1 and 2.4 | "Opdyke (2007) has shown that Mertens' equation has a limiting distribution that is valid under the more general assumption of stationary and ergodic returns, and not only IID." | same, lines 132-134 |
| PSR and MinTRL formulas | same, appendix code (eqs. 11 and 13 garbled by extraction) | "self.PSR=norm.cdf((sr-self.sr_ref)*(self.obs-1)**0.5/ (1-sr*stats[2]+sr**2*(stats[3]-1)/4.)**0.5)" and "self.minTRL=1+(1-stats[2]*sr+(stats[3]-1)/4.*sr**2)* (norm.ppf(self.prob)/(sr-self.sr_ref))**2" | same, lines 894-902 |
| MinTRL is in observations; moments need long series | same, section 4 | "It is important to note that MinTRL is expressed in terms of number of observations, not annual or calendar terms."; "the moments inputted in Eq. (13) must be computed on longer series for CLT to hold" | same, lines 486-491 |
| Fourth moment needs longer samples | same, section 2.3 | "estimating moments beyond the third, and particularly the fourth moment, requires longer sample lengths than estimating only the first two moments" | same, lines 303-305 |
| Opdyke's formula valid for stationary ergodic returns | Opdyke 2007, J. Asset Management 8(5) (academic), abstract only | "This paper presents an easily implemented formula for the asymptotic distribution that is valid under very general conditions — stationary and ergodic returns — thus permitting time-varying conditional volatilities, serial correlation, and other non-iid returns behaviour." | opdyke_2007_repec_abstract.html [abstract only; full text not obtained: SSRN blocked, journal paywalled] |
| Lo, Mertens, Christie; Opdyke showed equivalence | Benhamou 2018, arXiv 1808.04233 (academic) | "Opdyke (2007) interestingly showed that the derivation provided by Christie (2005) under the non-IID returns condition was in fact identical to the one provided by Mertens (2002)." | benhamou_arxiv_1808_04233.pdf/.txt lines 466-469 |
| PSR uses sample length and four moments | Bailey and López de Prado 2014, JPM, DSR paper (academic) | "PSR takes into account the sample length and the first four moments of the returns' distribution." | bailey_ldp_2014_dsr.pdf/.txt lines 352-353 |
| Mertens 2002 working paper itself | Mertens, "Comments on variance of the IID estimator in Lo (2002)" | not read | [unverified: unpublished note, not found online; formula taken from BLdP 2012 eq. 8 and code] |

Stopping rule (d): 5 full-text sources read (Lo, BLdP 2012, BLdP 2014, Benhamou, plus the Opdyke abstract); two
searches for Opdyke's full text and none for Mertens found anything new.

#### Planner pointers owned by M5b

| Pointer (reports/stage_e32_inputs/planner_research_soy_complex.md) | Status | Evidence and what differs |
|---|---|---|
| "block bootstrap by day, and positive results in at least two-thirds of quarters" (line 121-122) | PARTLY VERIFIED | A protocol suggestion, not an empirical claim. The day-block stationary bootstrap is sound (Politis and Romano 1994; block length by Politis-White with the 2009 correction; quotes in b.8). The two-thirds-of-quarters rule is a weak null filter (passes a no-edge candidate with probability 0.133 over 13 discovery quarters, 0.090 over 14 test quarters) and costs about 1 point of power at delta = 3.84 (b.3 item 2). It is a stability requirement, not significance. Applied to MONTHS instead of quarters it costs about 7 points of power. Under negative skew the binomial null is wrong (b.3 item 6). |
| "There are only about 40 major events in the discovery window" (line 92) | PARTLY VERIFIED (count); power COMPUTED | R4_events.md line 235 counts 15 major 11:00 CT USDA days a year, so about 49 in 39 months ("the planner's 'about 40' is the same order"); from a typed calendar, not a data read. Power: with 40 events, one trade each and a 75-minute hold, the minimum detectable net edge at 80% power is 10.7 ticks (one-sided 0.05, event-day noise as on normal days) up to 33.1 ticks (t > 3, noise doubled); a 2-tick edge has 3-12% power at the lenient bars and under 1% at t > 3 (c.4). A stand-alone event family cannot pass the one-shot test. |

#### What this means for E.33 (inputs for the lead's P8; the thresholds are the lead's)
1. Power gate: a candidate takes one of the 3 test slots only if D x ((3.0 + 0.8416) sigma_h / mu_h)^2 <= expected
   test trades (904 dates x trades a date), with mu_h a haircut discovery net edge and D from discovery
   autocorrelations and same-day clustering. On the standard numbers: 5-minute holds can test mu = 0.25-0.5 at
   3-13 trades a date; 15-minute holds need 2.4 (mu = 1) or 9.7 (mu = 0.5) a date; 60-minute holds can test only
   mu >= 1 and need about 9.7 a date across sessions; the USDA event family is untestable alone.
[MathReview C-6/C-9 (lead: ruled): the frozen test bar is the program verdict plus a protocol-added DSR >= 0.95 at N with V = 1/(T_test - 1) (t about 4.86 at N 838, T 870); see reports/stage_e32_discovery_protocol.md P7.2 and P9.]
2. Stability requirements with their measured cost at delta = 3.84 (80% power at t > 3): two-thirds of 3-month blocks
   positive (about 1 point of power); no month above 25% of net P&L (about 0 points; removes 78-100% of one-spike
   false passes); every leave-one-month-out t above 2.5 (about 0.1 point); same sign in each frozen volatility
   tercile (about 4 points). Significance inside every tercile would cost 63 points: do not require it.
3. Inference: HAC t on the daily P&L series (Newey-West, Bartlett weights, lag by a frozen rule) plus a day-block
   stationary-bootstrap p-value (b_SB from arch's automatic rule on discovery; about 2-5 days for daily AR(1)
   coefficients 0.05-0.2).
4. Feature importance: clustered MDA and SFI on purged folds, with noise canaries, reported after the frozen grid
   runs; no importance-driven selection unless nested and counted into N.
5. MinTRL is a 50%-power length; the gate should use the 80%-power n (1.64 times MinTRL at t > 3).

#### Failures, gaps and negative evidence
- Full text NOT obtained (marked [unverified] where used): Politis and Romano 1994 JASA (JSTOR only; the UCY record
  page returned a Cloudflare 403); López de Prado 2020 MLAM section 6.5 (clustered importance) and AFML ch. 8 (no
  free copy; the SCU library catalogue returned an anti-bot stub); Opdyke 2007 (SSRN blocked, journal paywalled; abstract
  from RePEc only); Mertens 2002 (unpublished note, not found); Newey and West 1994 lag rule (not searched). The
  BMC copy of Strobl et al. 2007 returned a cookie redirect twice; the PMC copy was used instead.
- Two sources are scanned PDFs without a text layer (Newey-West NBER TWP 55; Politis-Romano Statistica Sinica
  1994). I read the relevant pages as images; their quotes were typed from the page images and need a visual check
  by the reviewer (pages named in the evidence rows).
- Lo 2002 was fetched from a copy on a UC Berkeley student-organisation host (traders.studentorg.berkeley.edu);
  authorisation of that copy is unknown; the text matches the FAJ article's first page.
- Test-window trade dates: my typed calendar gives 904; M5a's gives 899. Neither is read from data; DataFacts owns the
  real number. Every per-day rate in (c) moves by 0.6% between the two.
- All sigma values are random-walk scalings of a 2022-23 one-minute SD (an assumption); real minute returns in ZM may
  mean-revert or trend at 5-60 minutes, and 2017-2020 volatility is unknown without opening the seal. The Monte Carlo
  stability results assume equal trades per month and iid months.
- SFI and LOCO compute times in a.7 are guesses; no probe was run (no data may be read in E.32).
- WebSearch calls used: 13 of 80. No budget notice was received.

Finished 2026-10-27 (time in log). Reviewer notes: every number above is reproducible from
work/M5b_power/M5b_calc.py, M5b_calc2.py, M5b_calc3.py and M5b_days.py.

## M6. From prediction to a prop-firm strategy

Source file: reports/stage_e32_briefs/M6_prop_strategy.md (sha256 14ae79e90fabc8eff2aa6b1bc5f62239e7fdd72afe0e98e6113511bb668371fb).

### M6_prop_strategy: from a directional prediction to a prop-firm strategy for ZM (Stage E.32, Part M6)

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

#### 0. Conventions and the standard numbers used

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

#### 1. Topic (a): from a probability or forecast to entries, exits and holding time

##### 1.1 Core idea
A model gives, at signal time t0, either a forecast f = E[G | x] of the signed mid move G over a horizon H, or a
probability p = P(G > 0 | x). The trade is worth taking only when its expected gross move beats the round-trip cost of
the execution design chosen (section 5) plus a margin; the exit rule (time stop, barriers, signal reversal) changes
the expected gross move itself, not only its variance. One position at a time means the traded set is a subset of
the signals, chosen by a state machine that must be replayed exactly.

##### 1.2 Equations (symbols in ticks unless stated)
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

##### 1.3 Worked example on the standard ZM numbers
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

##### 1.4 Data it needs
Mid (or best bid and offer) at the signal time and along the horizon at event resolution: ZM MBO (ZM.v.0, ZM.v.1)
rebuilt to the top of book; ZS and ZL MBP-1 for context features only. Horizon 5 to 60 minutes; barrier labels need
event time, since a 1-minute bar cannot order a stop and a target touched in the same minute.

##### 1.5 Leakage and look-ahead traps (each with a test)
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

##### 1.6 Compute
Labels and barrier scans are one forward pass per signal: O(signals x horizon events), seconds to minutes per month
of MBO on one core; the 39 months fit in RAM month by month. M6_limit.py (200,000 paths x 900 steps, two drift
profiles) ran in 14 s.

##### 1.7 Verdict: use
(A1)-(A7) are definitions E.33 needs. H, kappa and any barrier levels are configurations counted in N. Prefer a time
stop at H as the primary exit (A5); barriers only as a risk overlay for loss limits, declared in advance.

#### 2. Topic (b): market versus limit execution under the trade-through rule (V50), and the directional decomposition

##### 2.1 Core idea
For a directional signal the question is not what a limit order earns per fill (E.31 measured that) but what it earns
per SIGNAL. A resting limit fills mostly on the paths where the price first moves against the signal and misses the
paths where the price runs in its favour, so the filled trades are worse than the signal on average and the unfilled
ones are better. Under the trade-through rule this selection is made stronger, because a fill needs the level to
trade through first. The market order buys every path at half a spread plus latency.

##### 2.2 Equations
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

##### 2.3 Worked example (S15: alpha = 2.0 ticks over 15 min, sigma_1m = 3.15, s = 1; M6_limit.py)
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

##### 2.4 Data it needs
ZM MBO (ZM.v.0, ZM.v.1) event by event: book rebuild, trade prints with aggressor side, queue ahead at the order's
price; definitions for the tick and session; E.31's engine already implements the K, FIFO and TT fill models on this
data (reports/stage_e31_briefs/work/pilot/mbo_book31.py, kalgo31.py, measure31_core.py). Horizon: the timeout tau
(seconds to minutes) and the signal horizon H.

##### 2.5 Leakage and look-ahead traps (each with a test)
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

##### 2.6 Compute
E.31 measured 816 dates in 384 s with 4 workers (nice 10). Per-signal fill simulation for E.33 is the same work
restricted to signal times: well under an hour for 39 months on 4 to 8 cores, memory bounded by one day of MBO.

##### 2.7 Verdict: use, with market entry as the default
Market entry and market exit (variant i) are the primary execution for a minutes-scale directional ZM search at every
firm. Limit entries are an execution alternative E.33 may measure (each tau is a configuration counted in N), priced
under TT at TT routes (V50) and under the queue model only on Rithmic routes. A passive exit is a "maybe" for Rithmic
routes only.

#### 3. Topic (c): daily loss limits, trailing drawdowns, consistency and payout rules against a directional signal

##### 3.1 Core idea
A firm's rules act on the account's daily P&L path, so they filter signals by their per-trade SD and trade count as
much as by their edge. For a 50K account the binding numbers are a 2,000 (Bulenox 2,500) trailing drawdown and, at
three firms, a 1,000 to 1,250 soft daily loss limit (DLL); payout rules then add a waiting time (winning-day counts,
minimum balances, consistency caps). A minutes-scale ZM signal has a large per-trade SD (12.2 ticks = 122 USD per
contract at 15 minutes), so at the DLL firms it is held to about one contract no matter how many the position limit
allows.

##### 3.2 Equations
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

##### 3.3 Worked example: the signal of (c)
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

##### 3.4 Data it needs
None from the market for the rule model; E.33's own per-trade P&L series (net, per variant) on the discovery dates
feeds it in place of the normal assumption (block bootstrap of days, as E.19 did).

##### 3.5 Leakage and look-ahead traps (each with a test)
- Choosing the contract count or the firm after seeing the discovery P&L. Test: n and the firm list are fixed in the
  protocol; E.33 reports every firm and n in the grid.
- Normal-tail daily P&L understates DLL and breach rates (fat tails at USDA releases: E.31 saw -8.98 ticks per fill in
  the 5 minutes after a release). Test: rerun the funnel on a day-block bootstrap of E.33's own daily P&L and report
  both.
- Intraday ordering: a bridge minimum given the close is exact for Brownian motion only. Test: on E.33's simulated
  trades, compute the realised intraday worst P&L and compare its distribution with the bridge model's.

##### 3.6 Compute
M6_funnel.py ran 60 firm x edge x size cells of 20,000 paths x up to 756 days in 125 s on one core. The program's
prop_econ (E.19/E.28) is the reference implementation for any number that enters a verdict.

##### 3.7 Verdict: use (as a filter, with the program's simulator for verdict numbers)
Report per firm, for each E.33 signal, the DLL and drawdown probabilities and the time to the first payout from its
own per-trade P&L. Limit size to one contract at DLL firms for minutes-scale ZM signals unless the per-trade SD is
much smaller than 12 ticks. These are my simplified simulations: an independent reviewer should recompute the key
cells with prop_econ before they enter any verdict.

#### 4. Topic (d): ZM at each of the five firms

All firm facts below were recorded by E.28's A2 readers on 2026-10-20/21 (or by E.31's planner notes, firm pages read
2026-10-22): 6 to 7 days old, inside the 30-day line, so no firm page was re-fetched (decision logged in
pages/M6_prop_strategy/log.tsv). Each fact is [as recorded by E.28/E.31]; quotes are from E.28's saved files under
reports/stage_e28_briefs/pages/. Lucid, Tradeify and Bulenox forbid automated access in their terms (E.28 decisions),
so a re-fetch would not have been allowed anyway.

##### 4.1 The table

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

##### 4.2 What the table means for a minutes-scale ZM bot
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

#### 5. Topic (e): the three execution variants, per firm and route (planner requirement, user 2026-10-26 23:15 PDT)

Section written 2026-10-27 02:43 PDT (file mtime) by the re-spawned worker. New script: work/M6_prop_strategy/M6_variants.py (+
M6_variants_out.json, M6_variants_stdout.txt; formatting helper M6_sec5_rows.py -> M6_sec5_rows.txt). It uses the
same stylised Brownian model as M6_limit.py: 100,000 paths with common random numbers over a grid of alpha (0 to 6
ticks over 15 minutes), timeouts tau = 0.5, 1 and 5 minutes, and it imports my M6_funnel.run for the payout funnel.
Runtime 35 s, peak RSS 0.32 GB, nice 10. No market data.

##### 5.1 Core idea
Each route a firm offers fixes how a simulated limit order fills, and therefore which of three cost models applies:
(i) market orders (every firm; the default); (ii) limit orders under trade-through (documented by TopstepX, assumed
for Tradovate); (iii) limit orders under an estimated-queue rule (Rithmic, as a Rithmic staff post on a forum
describes it). A directional signal is priced per SIGNAL under each variant its route admits (section 2's
decomposition). The table then gives, per firm and variant, the gross move the signal needs before it pays.

##### 5.2 Equations: the per-fill and per-round-trip cost of each variant
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

##### 5.3 The firm-route table
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

##### 5.4 Worked example: per firm and variant, the S15 signal and the edge it needs
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

##### 5.5 The directional decomposition, restated per variant (what section 2 derived)
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

##### 5.6 What E.33 must measure on the discovery dates, per variant (no outcome computed now)
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

##### 5.7 Data, leakage, compute, verdict
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

#### 6. Evidence table

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

#### 7. Planner pointers (reports/stage_e32_inputs/planner_research_prop_sim_fills.md): verification

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

#### 8. Stopping rule and what was not done

- WebSearch calls in total: 2, both in the first spawn (Harris-Hasbrouck and Linnainmaa full texts; nothing free
  found). The re-spawn made no web calls. Every firm fact and planner pointer was checked against pages already saved
  by E.13, E.28 and E.31, which lie inside the 30-day line, except the Apex capture.
- Topics (a), (b) and (e) rest on three full-text academic sources plus derivations checked numerically. No new
  sources were sought on the firm topics, because the firm pages themselves are the evidence.
- Not done: no firm page re-fetched (all within 30 days, or barred by terms); Topstep's LFA "call-up" rule not
  re-checked; the CQG and WealthCharts fill rules are unknown (assumed TT, labelled); the funnel in sections 3 and 5
  is my simplification and not the program's prop_econ.

# Part V. Verification: the reviewers, the lead's rulings and the fixes

## V.1 Reviewers (each model confirmed from its own transcript, message.model; V50 item 5)

| Reviewer | Files | Model (transcript) | BLOCKING | SHOULD FIX | NOTE | Verdict |
|---|---|---|---|---|---|---|
| MathReviewerA-FableXHigh | M2 (all), R3a arithmetic (1, 2.3, 3.2, 4.2, 6.2, 7.2, 8.2) | claude-fable-5-1 | 0 | 5 (A-1 to A-4, A-12) | 11 | sound with fixes |
| MathReviewerB-FableXHigh | M1, M3 | claude-fable-5-1 | 0 | 5 (B-1, B-3, B-6, B-13, B-27) | 14 | sound with fixes |
| MathReviewerC-FableXHigh | M5a, M5b, p7_thresholds.py | claude-fable-5-1 | 1 (C-10) | 7 (C-1, C-2, C-3, C-7, C-8, C-9, C-11) | 8 | sound with fixes; p7 bar to fix |
| MathReviewerD-FableXHigh | M4, M6, R5 section B and E table | claude-fable-5-1 | 0 | 7 (D-1 to D-3, D-8 to D-11) | 12 | sound with fixes |
| X1Verifier-OpusHigh | X1_exposure.md (a Sonnet worker's inventory, re-verified under the user's never-Sonnet rule) | claude-opus-5-5 | - | 8 corrected rows, 4 missing rows | - | fit for P1 as corrected |

Reports: reports/stage_e32_briefs/review/MathReview_A.md to _D.md (scripts under review/work_A to work_D);
reports/stage_e32_briefs/X1_verify.md. The ProtocolReviewer's four lenses are in V.4.

Coverage (from the reviewers' own counts): A recomputed 118 M2 numbers and 71 R3a numbers and two Monte Carlos; B
recomputed every worked example in M1 and M3 and found all 127 evidence-quote segments in the saved pages; C
recomputed about 450 closed-form numbers, all simulated tables, 20 program file:line references and 68 quotes; D
reproduced every worked example of M4, M6 and R5 B, M6's payout funnel cell by cell, and found 58 quote substrings.

## V.2 The lead's rulings

Every BLOCKING and SHOULD FIX finding is accepted as the reviewer proposed it, with these specific rulings:
- C-10 (BLOCKING): p7_thresholds.py's power table used z 2.128 while its own binding test bar was the DSR at N.
  Resolved by reports/stage_e32_briefs/protocol/p7_final.py, which uses one bar everywhere; p7_thresholds.py is kept
  unchanged as the reviewed record, with a superseding note on its output.
- C-6, C-9, C-11 (the test bar): the protocol freezes the test bar as the program verdict exactly as coded
  (screening/stage_e_verdict.py: Holm at K = 9, DSR > 0.95 at the list's N with the population variance of the
  tested Sharpes, t > 3.0, PBO < 0.5) plus a protocol-added DSR >= 0.95 at N with V = 1/(T_test - 1). M5a's point
  that N-deflation at a fresh test is not needed for validity is right; the addition is the conservative reading of
  V43's "DSR at N", independent of how similar the tested candidates are. Dropping it is a user decision (return
  section 7) with its power cost shown both ways (P7.2).
- C-1 and C-7 (trade-date counts): 905 for 2017-05-01..2020-11-30 is right (31 closures); the protocol uses the
  MBO-feasible span 2017-05-22..2020-11-30 = 890, minus a 20-date burn-in = 870 (Part F's saved Databento page).
- A-2 and A-3 (clock offsets across feeds; bid-ask bounce and stale legs): taken into protocol G6 (per-month
  ts_recv - ts_event comparison across the three feeds; mids and executable touch prices only).
- D-1 (1.59 as a per-round-trip cost): E.28's 1.59 is a cycle-EV threshold; the per-trade market cost is 1.528 plus
  the firm's fee difference. The protocol uses executable prices and the fee directly, so no 1.59 enters a label.
- D-11 (M6 5.6's measurement plan): taken into protocol P6.4 (one common signal set, ts_recv clock, P3.6 rules).
- NOTE items: no edit; they are listed in the review files.

## V.3 The fixes

Each accepted correction is a bracketed note "[MathReview X-n (lead: accepted): ...]" in the reader file at the line
it corrects; nothing the reader wrote was deleted. Log: reports/stage_e32_briefs/review/fix_log.md. Applied by
FixApplier-OpusHigh (claude-opus-5-5): 25 accepted findings plus the C-6/C-9 ruling, 0 not applied, 32 notes inserted
(A 5, B 5, C 14 including the ruling at 7 places and the two superseding notes on p7_thresholds_budget500.md, D 8 with
D-1 in both M4 and R5), 0 lines deleted (diff against pre-edit copies). C-9's own figures (t-equivalent 4.92 at N
1,038) are superseded by the ruling's figures at N 838 (t about 4.86).

## V.4 ProtocolReviewer (the frozen protocol)

Four independent ProtocolReviewer lenses (Fable xhigh, worker-xhigh, workflow wf_30d7118e-f81, 07:32-07:57 PDT)
reviewed protocol DRAFT v0.2; each model was confirmed from its own transcript (claude-fable-5-1). A first run
(wf_3d631049-c34, 03:05) was stopped by a usage limit before any lens wrote a file and was re-run in full.

| Lens | File | Model (transcript) | BLOCKING | SHOULD FIX | NOTE |
|---|---|---|---|---|---|
| LeakageReviewer-FableXHigh | review/ProtocolReview_leakage.md | claude-fable-5-1 | 1 (LE-1) | 6 (LE-2 to LE-7) | 11 |
| DofReviewer-FableXHigh | review/ProtocolReview_dof.md | claude-fable-5-1 | 2 (DO-1, DO-2) | 20 (DO-3 to DO-22) | 14 |
| ArithmeticReviewer-FableXHigh | review/ProtocolReview_arithmetic.md | claude-fable-5-1 | 1 (AR-1) | 4 (AR-2 to AR-5) | 11 |
| FeasibilityReviewer-FableXHigh | review/ProtocolReview_feasibility.md | claude-fable-5-1 | 2 (FE-1, FE-2) | 9 (FE-3 to FE-11) | 8 |

The ArithmeticReviewer reproduced 122 numbers and re-ran p7_final.py byte-identically. All 45 BLOCKING and SHOULD
FIX items were accepted and applied by the lead (v0.3); the AR-1 finding (the program verdict as coded, V14 c,
makes the test's power depend on the list's composition) is disclosed in P7.2 and left to the user as a reserved
decision in P9 (amend V14 c to V = 1/(T_test - 1) for this test), since E.32 does not amend a user decision.

Re-check (FixVerifier, four Fable xhigh workers split by item and protocol section, workflow wf_6418603c-1ef,
08:42-08:56 PDT, all claude-fable-5-1; review/recheck/Recheck_W1.md to _W4.md): of the 45 items, 29 CORRECT, 14
PARTIAL, 2 WRONG (AR-1's disclosure overstated the weaker-companion case; DO-19's deadlines were stale against the
E.33 prompt as amended at 08:16); 0 new BLOCKING, 17 new SHOULD FIX, 25 NOTE. The lead applied every item, SHOULD
FIX and NOTE (v0.4; rulings and the options the lead chose in reports/stage_e32_STATE.md, 12:38-12:41).

Spot-check of the v0.3 to v0.4 diff (FixSpotCheck, two Fable xhigh workers by section, workflow wf_22487789-c6a,
both claude-fable-5-1; review/recheck/SpotCheck_A.md and _B.md): 37 hunks: 32 CORRECT, 2 UNTAGGED-OK, 2 PARTIAL, 1 WRONG (one number); no finding left uncovered; 0 BLOCKING, 4 SHOULD FIX, 12 NOTE, all applied (v0.5). A final check of the v0.4 to v0.5 diff (FinalDiffCheck-FableXHigh, claude-fable-5-1; review/recheck/FinalDiffCheck.md): 15 hunks, 11 CORRECT, 2 PARTIAL, 2 UNTAGGED-OK, 0 WRONG; 0 BLOCKING, 3 SHOULD FIX, 5 NOTE, all applied with the checker's own texts (v0.6), plus one consistency edit in P10. Frozen 2026-10-27 13:08 PDT as v1.0.

The frozen text is v1.0, sha256 c4ffb9d79af4bbbf10574ac138668aa49a80b22a8f5fba5879184d357d2c7e05
(reports/stage_e32_discovery_protocol.sha256).

## V.5 Process gaps and source hygiene (stated, not hidden)

- cftc.gov: R3a, R3b and R4 fetched 18 single documents before a terms decision was logged; the lead's check at 00:40
  found robots.txt allows reference use for user-agent * ("ai-train=no, use=reference") while blocking named training
  crawlers; the fetches were consistent with the terms, but the order (fetch, then terms) breaks the reader rules.
- M2 logged 9 failed fetches without trying the Scrapling fallback; Hasbrouck (1995) and Hayashi-Yoshida (2005) are
  cited second-hand. R2 did not retry the FAS export-sales page (403) because no terms check was done. R5 treated
  Kaggle as closed (reCAPTCHA); competition metrics there are [unverified]. Several sources are abstract-only and
  marked [unverified] (Kolm-Turiel-Westray, Stoikov 2018, Ma-Serra, Jin et al., Volkenand et al., Chordia-Roll-
  Subrahmanyam 2008); none of them carries a verdict alone.
- M5b's Lo (2002) copy came from a student-organisation host (authorisation unknown); Newey-West and one Sinica
  quote were typed from page images.
- X1 (the exposure inventory) ran on Sonnet before the user's 23:15 never-Sonnet rule reached the run; X1Verifier
  re-verified all 311 rows on Opus. X1 printed one E.17 pooled daily result series to its context once (disclosed).
- The first lead session stopped at a usage limit (00:51-02:32); its workflow journal could not be resumed in the
  new session, so the three unfinished readers ran from a byte-identical continuation script. A second usage limit
  (about 03:12-07:31) stopped the ProtocolReviewer and FixApplier before either wrote anything; both were re-run.
