# R1: The alpha research process at proprietary trading firms and systematic funds (Stage E.32, Part R1)

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

## 1. Sources read in full text for this part

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

## 2. (a) How ideas are generated, screened, ranked and killed

### 2.1 Facts

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

### 2.2 Equations (Kahn 2018, Technical Appendix)

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

### 2.3 What this means for a ZM directional search

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

## 3. (b) Research-to-production pipelines

### 3.1 Facts

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

### 3.2 Equations (Bailey and Lopez de Prado 2015, IID normal P&L per bet, mean mu > 0, s.d. sigma)

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

### 3.3 Worked example on the standard ZM numbers (worker's arithmetic; random-walk scaling assumed)

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

### 3.4 What this means for a ZM directional search

- Use (for the period after any pass; the lead's call): a pre-declared kill rule in time-under-water terms (TuW at
  the declared confidence, from the Sharpe claimed at the test), alongside the prop account's hard loss limits.
- Use: one code path from feature computation to order (Chan R1-E12; E.28 2.11 Optiver and Jump practice).
- Note for E.33 itself: E.33 is discovery plus one sealed test; paper or shadow trading is outside it under V43 and
  the 2026-10-18 record (E.28 2.11 table 3.2). Nothing here changes that.

---

## 4. (c) How the multiple-testing problem is handled in practice

### 4.1 Facts

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

### 4.2 What this means for a ZM directional search

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

## 5. (d) Signal decay and capacity

### 5.1 Facts on decay

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

### 5.2 Facts on capacity

1. Capacity is set by costs (AQR, practitioner/academic): from AQR's live execution data, "short-term reversal
   strategies, on the other hand, do not survive transactions costs at sizes greater than $9 billion in the U.S."
   against 52-103 billion USD for size, value and momentum (R1-E35). The fastest style has the least capacity.
2. For this program capacity in the institutional sense is not binding: one ZM contract against a median front-
   contract ADV of 36,690 (A0 Table 1) is 1/36,690 = 0.0027% of daily volume. The binding limits are the prop
   account's position and loss rules and the queue position of a 1-lot (E.31: a resting 1-lot at the ZM touch earned
   a gross -0.970 ticks per fill at 10 s under the trade-through rule; reports/E.31_RETURN.md section 3.5).

### 5.3 Worked example: half-life and breadth of a minutes-scale ZM signal (worker's arithmetic)

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

### 5.4 What this means for a ZM directional search

- Use: measure each candidate signal's decay in discovery (the IC at horizons 1, 5, 15, 60 minutes and the
  signal's own autocorrelation) and report its half-life; prefer, at equal CV score, the more persistent signal,
  because it spreads one round-trip cost over more expected move (Garleanu-Pedersen R1-E34; Isichenko R1-E37).
- Use: an ancillary decay monitor (Kahn R1-E7): the IC-by-horizon profile frozen at discovery is the reference a
  later live record is compared against.
- Do not: estimate capacity; it is irrelevant at one lot. Do record queue and fill limits, which are the real
  constraint (E.31, V50).

---

## 6. (e) How desks decide that a small edge is worth running

### 6.1 Facts

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

### 6.2 Equations for a one-contract directional strategy (worker's derivation; assumptions stated)

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

### 6.3 Worked example on the standard ZM numbers

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

### 6.4 What this means for a ZM directional search

- Use: state every candidate's required IC at its horizon from the frozen cost (step 2 above) before discovery, so
  that a CV result can be read against a known break-even rather than against zero.
- Use: report, for every candidate, gross IC, hit rate, net edge per trade in ticks, trades per year and the
  annualised net Sharpe, side by side; a desk's decision variable is net edge per trade times trade count, not IC.
- Use: an effective-bets adjustment when converting per-trade Sharpe to annual Sharpe (count non-overlapping
  bets; M5a/M5b own the autocorrelation correction).
- Do not: use the fundamental law to justify trading every bar because breadth is "free": breadth multiplies the
  net edge, and a negative net edge times sqrt(B) is a larger loss (step 4, rho = 0.10).

---

## 7. Practices for the E.33 protocol: adopt, and do not adopt

This is a worker's list for the lead. It sets no thresholds, selection rules or verdicts. Each item names the
source. Items already in force in the program (frozen pipeline, sealed window, N counting, DSR/PBO/Holm, purged CV,
one test) are not restated.

### 7.1 Adopt

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

### 7.2 Do not adopt, with reasons

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

## 8. Evidence table

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

## 9. Failures, gaps, negative evidence, budget

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
