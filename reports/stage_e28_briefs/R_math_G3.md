# R_math_G3: adversarial math and evidence review of C2_LOB.md and C2_Pooled.md

Reviewer: MathReviewer-FableXHigh (group G3), Stage E.28. Started 2026-10-21 10:31 PDT (this run; an
earlier run was cut by a usage limit after writing only the quote-check script and TSVs in
work/REV_G3/, no findings).

Scripts and raw outputs: reports/stage_e28_briefs/work/REV_G3/ (REV_G3_quotecheck.py, REV_G3_cst_cdl.py,
REV_G3_quotes_LOB.tsv, REV_G3_quotes_Pooled.tsv, plus files added in this run).

Status: COMPLETE (both files reviewed; totals at the end of the file).

Severity scale (from the brief): BLOCKING (wrong equation or derivation, wrong number that changes a
verdict, fabricated or misattributed quote, evidence claim the source does not support); SHOULD FIX (error
or ambiguity that would mislead a careful reader, missing [unverified], wrong number that does not change a
verdict); NOTE (clarity, style).

---

## Part 1: C2_LOB.md

What was checked (sections 0-16, 1105 lines): every equation and derivation summary against the saved source text
(grep of pages/C2_LOB/*.txt; LMZ from page images of the scanned PDF); every worked example recomputed (my scripts
REV_G3_cst_cdl.py, REV_G3_cst_variants.py, REV_G3_cst_cond_cdl_tail.py; the reader's C2_LOB_cst_cdl.py and
C2_LOB_examples3.py run read-only); every quote (two scripts, see 1.2); every verdict against its stated evidence.

### 1.1 Findings table

| ID | Severity | Location | What is wrong | Evidence (re-derivation or source line) | Proposed fix |
|---|---|---|---|---|---|
| MG3-01 | SHOULD FIX | C2_LOB.md:183-184 (sec. 2.2, CdL eq. 5) | Eq. (5) is transcribed faithfully, but the paper's eq. (5) (duration tail ~ t^-2 when lambda < mu + theta) is inconsistent with its own eqs. (3)-(4), and the brief passes it on without a flag. For lambda < mu + theta each queue's hitting time has finite mean x/(mu + theta - lambda) and an exponential tail with rate (sqrt(mu+theta) - sqrt(lambda))^2 (large-u asymptotics of I_n in eq. 4). The paper's Tauberian step is misapplied: its own expansion L(s,x) ~ 1 - c s shows a finite mean, which excludes a 1/t tail; its coefficient c = x(lambda+mu+theta)/(2 lambda (mu+theta-lambda)) is also wrong (exact: x/(mu+theta-lambda), from d alpha/ds at 0). | REV_G3_cst_cond_cdl_tail.py evaluates eqs. (3)-(4) at the paper's lambda = 12, mu+theta = 13, (a,b) = (4,5): local exponent d ln P / d ln t = -1.3 (t = 1-5), -2.3 (10-20), -5.1 (50-100), -25.9 (400-800); eq. (5) overstates P by 24x at t = 20 and by 10^16 at t = 800. Numeric E[sigma_1] from (3)-(4) = 1.0000 = 1/(mu'-lambda); the paper's coefficient gives 1.0417. Source: cont_delarrard_2013_markovian.txt:387-389 ("regularly varying tail ... with tail exponent 2 if lambda < mu + theta"), 436-446 (eq. 5). | After eq. (5) add: "(as printed; eq. (5) is not consistent with (3)-(4): for lambda < mu + theta the tail is exponential with rate (sqrt(mu+theta) - sqrt(lambda))^2, only 0.02/s for the paper's 12 vs 13 example, which is why Figure 3 looks like a power law over its plotted range; the mean duration is finite). Not used by any pilot quantity." |
| MG3-02 | SHOULD FIX | C2_LOB.md:457 (sec. 5.3) and 492-493 (sec. 5.8) | "The slides calibrate on one month (BAC and CVX, March 2011) and validate on later days of the same month" misstates the design: the slides fit G* on ONE day and compare it with averages over the whole month (which includes that day), plus a 3-day plot. | stoikov_gatheral60_slides.txt:465-470: "Compute averages of M_{t+60} - M_t, M_{t+300} - M_t and M_{t+600} - M_t grouped by I_t and S_t for the entire month of March." / "Compare to G* obtained from the first day o[f] March."; :452-456 "G* vs 1 min price predictions on three consecutive days". | Replace with: "The slides fit the transition matrices on the first trading day of March 2011 (BAC and CVX) and compare G* with 1, 5 and 10 minute mid changes averaged over the whole month (and on three consecutive days); the calibration day is inside the validation month." Same change in 5.8. |
| MG3-03 | SHOULD FIX | C2_LOB.md:617 (sec. 7.2) | "kappa -> 0 the lognormal" repeats a misprint of the NBER WP. Under eq. (4.4) as printed, W = (lambda T)^p ~ Gamma(shape kappa, rate kappa), so log T is asymptotically normal with variance 1/(p^2 kappa) as kappa -> infinity (with p -> 0); at kappa = 0 the density (4.4) degenerates (kappa^kappa / Gamma(kappa) -> 0). The lognormal is the kappa -> infinity limit (Stacy / Prentice parametrization). | WP p. 17 (PDF page 21), read as an image: "when kappa = 0, it reduces to a lognormal distribution"; eq. (4.4) f(t) = lambda |p| kappa^kappa (lambda t)^{p kappa - 1} exp(-(lambda t)^p kappa) / Gamma(kappa). | "kappa -> infinity the lognormal (the WP prints kappa = 0, a misprint; the published JFE version may differ)". |
| MG3-04 | SHOULD FIX | C2_LOB.md:845-846 (sec. 10.2) | "R_1 = S/2 in the simplest case (eq. 10 with phi = 0)" drops a factor: eq. (10) is S = 2 lambda_inf R_1 + 2 phi with lambda_inf = 1/(1 - C_1) (eq. 7), so phi = 0 gives R_1 = S/(2 lambda_inf); R_1 = S/2 needs also C_1 = 0 (uncorrelated trade signs), the case the paper argues against (long-range correlated order flow, lambda_inf > 1). | wyart_etal_2008_spread_impact_vol.txt:262-266 (eq. 7, lambda_inf = 1/(1 - C_1)), :280 (eq. 10: "S = 2 lambda_inf R_1 + 2 phi"). | "...with R_1 = S/(2 lambda_inf), lambda_inf = 1/(1 - C_1) >= 1 (eq. 7, 10 with phi = 0); R_1 = S/2 only when order signs are uncorrelated (C_1 = 0)." |
| MG3-05 | NOTE | C2_LOB.md:436 (sec. 5.2) | The slide defines S_t = (1/2)(P^a - P^b), a half-spread, while the brief writes "S the spread"; the slide's toy result P^micro = M + I - 1/2 and the brief's "(one-tick spread) ... the weighted mid" both treat S as the full spread, so the slide's 1/2 is probably a slide typo, but the brief should say which convention it uses. | stoikov_gatheral60_slides.txt:153-158 ("S_t = 1/2 (P^a_t - P^b_t) is the bid-ask spread"); :240-242 (toy 2 result). | Add "(the slide prints S_t = (P^a - P^b)/2; this brief uses the full spread, which is what the toy result and the notebook use)". |
| MG3-06 | NOTE | C2_LOB.md:618-619 (sec. 7.2) | The WP prints the Kaplan-Meier exponent as delta_(i), which under its own eq. (4.2) (delta = 1 for censored) is backwards, the same slip the brief flags for eq. (4.3). The brief silently corrects it to (1 - censoring flag). | WP p. 17 (PDF 21): S_hat(t) = prod ((n-i)/(n-i+1))^{delta_(i)}; eq. (4.2): delta_i = 1 if censored. | Add "(the WP prints the exponent as delta_(i); with its eq. 4.2 convention that is a misprint)". |
| MG3-07 | NOTE | C2_LOB.md:216-217 (sec. 2.5) | "lambda = 12 per second, mu + theta = 13 per second": the source gives no units for this example. | cont_delarrard_2013_markovian.txt:428-429 (Figure 3 caption: "for lambda = 12, mu + theta = 13"). | Drop "per second" or mark it as the brief's assumption. |
| MG3-08 | NOTE | C2_LOB.md:120-125, 976-977 (CST Table 4) | Confirmed, with two facts worth adding. My independent exact solve under the brief's reading gives 0.5025 / 0.6980 / 0.8824 / 0.3589 / 0.2915 / 0.2243 / 0.6071 for (b,a) = (1,1),(1,2),(1,5),(2,1),(3,1),(5,1),(5,5) (paper: .497/.641/.776/.302/.206/.118/.393), matching the reader's numbers. Nine further readings fail too (ask death constant; no ask births; others cancel only; Lemma-2 rates mu + i theta on the bid; b ahead of ours; own cancel = failure; no cancellations ahead; own cancel at theta with rejection conditioning; the last with no cancels ahead). Fact 1: the b = 1 row (.497, .641, .709, .749, .776) involves only our own order (rate mu) against the ask queue, so NO queue-ahead convention can explain the gap; it lies in the ask dynamics or in the paper's conditioning. Fact 2: the paper's Lemma 2(2) gives the pure-death process W~_B death rate mu + i theta(S) in state i, while the Prop. 5 proof uses mu + (i-1) theta(1); the paper is internally inconsistent there. | REV_G3_cst_variants.py, REV_G3_cst_cond_cdl_tail.py (printed tables); cst_2010_try1.txt:534-541 (Lemma 2), 674-684 (Prop. 5 proof), 1083-1101 (Table 4). | Add the two facts to 1.5 and 14; keep the recommendation (re-derive Result B, validate on the pilot's own fills). |
| MG3-09 | NOTE | C2_LOB.md:412-415 (sec. 4.8) | The "0.1 tick" gain of buying at the ask when p_up = 0.8 is a mark-to-mid after one move; the round trip the same sentence mentions ("2 x 0.5 tick") would pay another half-spread on exit, giving -0.4 tick. The paragraph is correct as written but a reader can take 0.1 tick as a tradable edge. | Arithmetic: (0.8 - 0.2) x 1 - 0.5 = 0.1 (mark-to-mid); exit at the new bid: 0.1 - 0.5 = -0.4. | Add "(mark-to-mid; exiting at the bid afterwards gives -0.4 tick)". |
| MG3-10 | NOTE | C2_LOB.md:892-896 (sec. 11, F3) | The worked numbers use b = Q_ahead + 1 terms (11, 51, 201), i.e. b counts the order itself as in CST eq. (14), but the text says "10 lots ahead" etc. without stating the convention. | Reader's C2_LOB_examples3.py (run read-only: b = 11/51/201, means 5.2/20.7/55.3 s, P(<=10 s) = 0.994, P(<=60 s) = 1.000/0.875, all reproduced). | Write "b = Q_ahead + 1 (the order itself is the last term)". |
| MG3-11 | NOTE | C2_LOB.md:539-540 (sec. 6.3) | "almost unaffected by depth ahead (-11.5% and -2.2%)": -2.2% is the all-order LEVEL hazard-rate change for Front-of-queue depth (table row "Front-of-queue depth | -0.005*** | -2.2% | 0.7"), but -11.5% is the NON-HFT subsample's coefficient for CHANGES in Front-of-Queue Depth (HFTs: -42.0%), not the all-order changes coefficient; the pair is drawn from two different tables. | dhn_2023_full_scrapling_fetch.md:388 (-2.2%), :504 ("the coefficient for changes in Front-of-Queue Depth is more negative for HFTs (-42.0%) than for others (-11.5%)"); :419 gives the Back-of-Queue HRCs -58.7% (level) and -56.4% (changes) as quoted. | Cite the all-order changes HRC for Front-of-Queue from the same table as the Back-of-Queue ones, or say "-11.5% for non-HFT firms". |
| MG3-12 | NOTE | C2_LOB.md:764-765 (sec. 8.8) | "fill probability 0.039 to 0.095 for the six tickers shown": Arroyo's Table 3 lists nine tickers (AAPL, AMZN, BIDU, COST, CSCO, DELL, INTC, MSFT and one more); the range 0.0392 (DELL) to 0.0948 (BIDU) is right for the best-level column, "six" is not. (The Table 7 repeat claim on lines 762-763 is CORRECT: in the T = 1000 block, MN-CNN prints 13.77 for BIDU, INTC and MSFT, MN-LSTM 7.02 and MN-Conv-Trans 79.29 for the same three, and COST = CSCO in every row; arroyo_etal_2023_survival.txt:1026-1028.) | arroyo_etal_2023_survival.txt:452-472 (Table 3, "between 1 October and 27 December 2022", 9 rows). | "for the nine tickers shown". |

### 1.2 Quote check

Method. (a) REV_G3_quotecheck.py (pass 1): every double-quoted string of >= 12 characters on one line, normalized
(NFKC, ligatures, dashes, case, whitespace; hyphenation variants), searched in every saved .txt/.md/.ipynb under
pages/C2_LOB/. (b) REV_G3_quotecheck2.py (pass 2): quotes may span line breaks inside a paragraph, and "..."
ellipsis quotes are split into fragments that must all be found. Raw rows: REV_G3_quotes_LOB.tsv, REV_G3_quotes2_LOB.tsv.

Pass 1: 109 quotes, 94 found, 15 missed. The 15 misses, each checked by hand:
- 6 LMZ quotes (lines 662, 663, 1075, 1076, 1077, 1078): the source is an image-only scan; I read PDF pages 17, 18,
  36, 37 as images. All six are verbatim (p. 13: "ABT's lower-bound mean is 15.58 minutes ... actual mean is 25.39
  minutes", "range from 5.93 (VO) to 18.18 (GE)", "n-th-passage"; p. 14: "cannot match the empirical distribution of
  actual limit-order execution times", "In summary, hypothetical limit-order executions are very poor substitutes for
  actual limit-order data."; p. 32: the 95% to 20% sentence; p. 33: "fits the data remarkably well"). VERIFIED.
- line 696 "log(1 - e^{Lambda(t)})": the saved MMW text prints "log 1 − eΛ(t)" (maglaras_moallemi_wang_2021_deeplob.txt:545);
  the brief's rendering is fair and its correction to -Lambda(t) is right. VERIFIED.
- line 1103 "The Profitability of Market-Making \| 319-332": the pipe is escaped for the markdown table; the Crossref
  file has "The Profitability of Market-Making | 319-332". VERIFIED.
- line 974 "Insufficient credits": a Firecrawl notice quoted from the log, not a source claim. N/A.
- lines 19, 133, 357, 575: the brief's own labels or hypothesis wording in quotes, not source quotes. N/A.
- lines 794, 935: regex artifacts (text between two unrelated quote marks). N/A.
Pass 1 result: 103 source quotes, 103 matched (94 by script, 9 by hand), 0 missed.

Pass 2 (cross-line and ellipsis quotes) is reported in the addendum below the Part 2 tables (same script, run
after the Part 1 write).

Numbers cited from sources, checked against the saved text (all match unless listed in the table above): CST
Table 2 rates, Table 3 Laplace block, Table 4 both blocks; CdL Table 3 (Citigroup/GE/GM rates), Figure 3 example;
HLR theta = 0.7, theta_reinit = 0.85, eta = N_c/(2 N_a), 5 vs 14 bps, K = 3, estimator (txt:375-386 verbatim),
Assumptions 3-4 (txt:829-834); Gould-Bonart Table 2 (MSFT 0.01/2.49, GOOG 0.03/0.54), Table 4 out-of-sample column
(large-tick 0.752-0.805, small-tick 0.581-0.642), 252 days x 100 = 25,200, 80/20; Stoikov notebook n_imb 10 and 4,
n_spread 2 and 4, dt = 1; Moallemi-Yuan Table 3 (BAC 0.62/0.57/0.14, CSCO 0.63/0.68/0.08, PBR 0.57/0.85/-0.03),
Table 1 row 8/9/13 (mu 1.65/min, gamma 0.71/min, avg jump 0.91 ticks), "0.26 ticks on 8/9/2013 and 0.21 ticks on
8/20/2013", 1000 orders/day, 30 days, 1-minute mid; MMW Tables 6, 8, 9, 502 days, 12+1+1 months x 10; Arroyo Table 3
(fill probabilities 0.039-0.095 at the best level, 1 Oct-27 Dec 2022; the table shows 9 tickers, not "six"),
training window 1 Sep-26 Dec 2022; Lehalle-Mounjid (AstraZeneca Jan-Sep 2013); Baron (Swedish equities 2010-2014;
E-mini 2010-2012); Crossref chapter pages (6 of 6); Lambda A10 $1.29, A100 $1.99; products.py:154 (MES tick 0.25,
$1.25, 122 cents).

[unverified] marks: present where needed (Stoikov abstract, Bouchaud book contents, deep-model compute, MDQR
hardware). One addition suggested: the Arroyo Table 7 sentence (MG3-12).

### 1.3 Counts

BLOCKING 0; SHOULD FIX 4 (MG3-01, 02, 03, 04); NOTE 8 (MG3-05 to 12).

### 1.4 Judgment

The mathematics of C2_LOB.md is sound where it matters for the pilot. Every equation I could check against the
saved text is transcribed correctly with symbols defined (CST eqs. 3, 5, 6, 9-11, 14, 16; CdL eqs. 3-4, 6-9, 13;
HLR estimator and Assumptions 3-4; Gould-Bonart eq. 7; Stoikov's recursion and convergence condition; Moallemi-Yuan
eq. 1 and Theorems 2-3; LMZ eqs. 4.2-4.7; MMW hazard likelihood; Wyart eqs. 6, 20). The reader's own computations
reproduce under independent code: CST Result A to 4 decimals, the queue-length table exactly, CdL eq. (7) by
quadrature AND by a separate discrete Dirichlet solve (0.6977, 0.7560, 0.1860, 0.5000), the arctan limit, every
worked-example number in sections 1-11 (sample sizes, logistic values, AUC standard error, microprice adjustments,
Moallemi-Yuan decompositions and alpha(0), Kaplan-Meier toy, gamma/Weibull survival values, hazard arithmetic,
pro-rata shares, Lambda cost, F3 depletion times). The one place the reader could not reproduce a source (CST
Table 4) is reported honestly and my nine further readings do not resolve it either. The four SHOULD FIX items are
transcription-level: an equation copied from a paper that is wrong in the paper (CdL eq. 5), a misprint copied
from a scan (LMZ kappa limit), a dropped factor in a one-line paraphrase (Wyart R_1 = S/2), and a misstated
validation design (Stoikov slides). None changes a verdict: the verdict table's reasons (Result A reproduces;
arctan exact at 300/100; AUC 0.75-0.81; BAC -0.043 tick without rebate; MMW AUC 0.62-0.72) all check out against
the sources, and the overall reading (a slow 1-lot at the back of a FIFO queue is filled on the adverse paths; no
source shows retail-latency passive profitability after fees) is supported by the evidence table, every row of
which I matched to its saved file.

---

## Part 2: C2_Pooled.md

What was checked (sections 0-12, 915 lines): every equation against the saved text (Sirignano-Cont eq. 2.1, the
score, the linear baseline; Sirignano 2019 eqs. 10-13 and Theorem 4.1; Lucchese smoothed mid, gamma rule, loss,
Definition 4.1; Cont-Cucuringu-Zhang eqs. 1-4; QuantNet eqs. 3-4; the LSTM cell and parameter count; the
DerSimonian-Laird formulas; the equicorrelation K_eff), every number in the tables cited (SC Tables 1-2, Lucchese
Tables 1, 8, 9, DeepLOB Table IV, LOBCAST Table 2, crypto ARC row, LiT, A0_contract_stats.json, products.py,
RunPod and Lambda price strings, NVIDIA spec strings), every worked example (REV_G3_pooled_arith.py), every quote
(two scripts), and the verdict table against its evidence.

### 2.1 Findings table

| ID | Severity | Location | What is wrong | Evidence (re-derivation or source line) | Proposed fix |
|---|---|---|---|---|---|
| MG3-13 | SHOULD FIX | C2_Pooled.md:29 (sec. 0, bottom line) | "Every study that reported trading used mid prices or ignored fees." is not supported for one of the studies the brief itself cites: Bieganowski and Slepaczuk's taker backtest executes "at the best ask and sells at the best bid, reflecting realistic taker costs" and reports "gross and fee adjusted returns using taker fee". Section 5.4 describes that study correctly (latency not modelled); the blanket sentence in the bottom line does not. | crypto_explainable_patterns2026.txt:566-574. | "Every equity LOB study that reported trading used mid prices or ignored fees; the one crypto taker backtest (5.4) nets taker fees but models no latency." |
| MG3-14 | NOTE | C2_Pooled.md:548-549 (sec. 5.4) | "annualized returns on capital of 4.06 to 7.00 (that is 406% to 700%) on three small coins": the ARC row (enj 4.06, etc 5.78, rose 7.00 vs buy-and-hold -0.67, -0.10, -0.71) is correctly read, but the table block does not say whether these are the gross or the fee-adjusted figures the paper says it reports, and "ARC" is expanded by the brief, not by the saved table. | crypto_explainable_patterns2026.txt:586-592 (table under Figure 10), :572-573. | Add "(gross or net of taker fee not stated in the table)". |
| MG3-15 | NOTE | C2_Pooled.md:267 (sec. 2.3) | The quoted words "escape to +infinity" are not verbatim; the source says "probability mass escaping to +∞". | sirignano2019_dl_lob.txt, page 22 block ("the model may not be well-posed due to probability mass escaping to +∞"). | Quote "probability mass escaping to +∞", or drop the quote marks. |
| MG3-16 | NOTE | C2_Pooled.md:454-457 vs 823-824 | The section heading dates Briola, Bartolucci and Aste "(2024)" while the reference list and the saved Crossref record give Quantitative Finance 25(7), 1101-1131, published 2025-07-03. | crossref_briola.json ("volume":"25", "issue":"7", "page":"1101-1131", published-print 2025-07-03). | Use "(2024 arXiv; QF 2025)" in the heading. |
| MG3-17 | NOTE | C2_Pooled.md:135 (sec. 1.3) | "(paper, eq. 3.-1 ...)": the label "(3.-1)" is what the arXiv text prints (a LaTeX counter slip), so the brief is faithful, but a reader will take it for a typo in the brief. | sirignano_cont2019_universal.txt:393-394. | Write "eq. (3.-1) [sic, as printed]". |
| MG3-18 | NOTE | C2_Pooled.md:567-568 and 842-843 (sec. 5.5, ref. 13) | arXiv 2501.08822 (Bodor and Carlier, MDQR) is marked "abstract only [unverified]" here, but its full text is saved by the C2_LOB worker (pages/C2_LOB/dl_meets_qr_2025.txt, 143 KB), which confirms the Bund-futures sample ("trading days over three months from March to June 2022"). | pages/C2_LOB/log.tsv row for arXiv 2501.08822; C2_LOB.md evidence row "MDQR trained with early stopping". | The lead can lift the [unverified] mark by citing the C2_LOB file. |
| MG3-19 | NOTE | C2_Pooled.md:71 (sec. 1.2) | The ellipsis quote "a step ... is on average 1.7 seconds in the dataset" is exact after the ellipsis; before it the source reads "step Δk = τ_{k+1} − τ_k is on average 1.7 seconds" (the brief's "a step" is a paraphrase inside quote marks). Harmless. | sirignano_cont2019_universal.txt:641. | Quote "step Δk = τk+1 − τk is on average 1.7 seconds in the dataset". |

### 2.2 Quote check

Pass 1 (REV_G3_quotecheck.py, single-line quotes): 121 quotes, 86 found, 35 missed. Pass 2 (REV_G3_quotecheck2.py,
cross-line and ellipsis quotes split into fragments): 180 spans, 150 found, 29 missed, 1 skipped (fragments too
short). Raw rows: REV_G3_quotes_Pooled.tsv, REV_G3_quotes2_Pooled.tsv. The 29 pass-2 misses, each read by hand:
- 12 are the brief's own phrases or labels in quote marks (lines 10, 54, 171, 215, 232, 329, 347, 382, 532 x2,
  604, 685), not source quotes. N/A.
- 2 are abstract-only quotes already marked [unverified] (line 561 x2: KANFormer, MDQR). N/A by design (but see MG3-18).
- 14 are verbatim in the source and missed only because of a page break, two-column layout, a bracketed insertion or
  a glyph the normalizer does not map: lines 63 and 860 (Sirignano-Cont data sentence, split across a page break at
  txt:184-190); 283 and 778 ("GPU node hours", curly inner quotes, txt:1505); 357 (Definition 4.1, Greek alpha,
  txt:1002); 363 x3 (txt:1243-1244 "partially inconsistent with / those in Table 4", 1250, 1277-1278); 415 and 860
  (DeepLOB transfer sentence, two columns, txt:540-541); 419 and 860 (mid-prices without transaction costs /
  standalone strategy, two columns, txt:602-605); 460 (Briola rule, angle-bracket glyphs, txt:871); 763 (NVIDIA
  "CUDA ® Cores" glyph). VERIFIED.
- 1 is not verbatim: line 267 "escape to +infinity" (MG3-15).
Result: 166 source quotes, 165 verbatim (150 by script, 14 by hand, 1 by design-unverified pair excluded), 1
non-verbatim paraphrase inside quote marks, 0 fabricated or misattributed.

Numbers checked against sources (all match): SC Table 1 (25/25, 1.45%; 4/25, -0.15%), Table 2 (100%, 7.2/3.7/1.6%,
50 stocks, Aug 2015), 5000 lags x 1.7 s, 25 and about 500 GPU nodes, "500 years (!)", 18 months, Jan-Mar 2017;
Sirignano 2019 489 stocks, 50 TB, 10 M and 5 M samples, 50 GPUs, 3,000 GPU node hours; Lucchese 115 tickers, 10
stocks, LILAK 3.77 / AAPL 127.86 thousand price changes per day (Table 1 "daily averages"), W = 11, k = 5, 5
validation days, Table 8 rows CHTR/AAPL/AAL/ATVI, Table 9 (92/8/0%); DeepLOB Table IV (70.17/68.62, 63.93/63.44,
61.52/61.46; penalties 1.55/0.49/0.06), 3-month test; LOBCAST Table 2 (78.9 -> 71.4, 59.5, 59.5; BINCTABL 61.2;
MAJORITY 55.5), 6-2-2, 155/258 h, 8 GPUs; Briola 15 stocks, rule thresholds; CCZ M = 10, 89%, eqs. 1-4; QuantNet
3103 assets, 58 markets, 51/69%, 15/41%; crypto 2022-01-01..2025-10-12, five coins, purge window, ARC row; LiT
September 2024, "around 5%"; A0_contract_stats.json sigma_1m_ticks MES 6.6147, NQ 27.8254, RTY 10.0077, YM 12.1364
and vol_per_min_main_median 1637/984/255/226; products.py:150-154 (M2K 0.10/$0.50, MYM 1.00/$0.50, ES 50 vs MES 5,
MES $1.25, 122 cents); RunPod ($0.5, $0.89, $0.59, $0.27, $2.89; the extraction shifts row labels, the brief's
reading is the consistent one); Lambda (A100 $1.99, V100 $0.79, H100 SXM $3.99).

Worked examples recomputed (REV_G3_pooled_arith.py; all agree to the printed precision): 1.6(a) SE 0.0005, 20 SE,
n = 5,625 / 22,500 / 90,000; 1.6(b) $0.0625 vs $2.47 (39.5x); 1.7 1,800 fills per tercile; 1.8 18,200 + 40,400 =
58,600; 2.6 (0.70, 0.18, 0.06, 0.06), 1.48 ticks, $1.85; 3.5 0.556 and 0.161 bps, 1.26 and 4.34 ticks; 6.2 0.151,
0.036, 4.21x, $8.26/$13.92/$5.01/$6.07; 6.3 13.6 lots/s, 22 s, 1.8/4.7/4.2 s; 6.4 K_eff 1.875/1.364/1.154/1.071;
6.5 ybar -0.3205, Q 4.240, tau^2 0.00622, mu -0.3224 (SE 0.0626), B = (0.287, 0.507, 0.616), shrunk (-0.306,
-0.385, -0.275); 7.3 0.671/0.474/0.387/0.335; 7.4 108; 8 7.13 and 4.06 TFLOP/s, 35.2 MFLOP per sequence, 1.76e14
per epoch, 126-352 s per epoch, 0.70-1.95 h per 20 epochs, 0.8 GB, $2,670.

[unverified] marks: present on Kolm et al. (snippets), KANFormer and MDQR abstracts, the Eurodollar and rebar
pointers, the DeepLOB journal volume, Hochreiter-Schmidhuber, Hansen-Lunde-Nason and DerSimonian-Laird (not fetched),
and the Section 8 timing estimates. Nothing found that needed a mark and lacks one.

### 2.3 Counts

BLOCKING 0; SHOULD FIX 1 (MG3-13); NOTE 6 (MG3-14 to 19).

### 2.4 Judgment

C2_Pooled.md is mathematically careful and its evidence is well sourced. Every equation is either transcribed
faithfully from the saved text or is a standard textbook form explicitly labelled as such (LSTM cell, l2 penalty
"an assumption", DerSimonian-Laird "standard formula"); every worked example reproduces exactly under independent
code, including the random-effects shrinkage example to four decimals and the compute estimates from first
principles; every table number I checked (SC Tables 1-2, Lucchese 8-9, DeepLOB IV, LOBCAST 2, the A0 statistics,
the contract specifications, the price pages) matches its source; the two-column and page-break splits that defeat
a naive grep are all genuine quotes. The leakage guards (7.5) and the trial-count table (7.4) are internally
consistent with the brief's own arithmetic (108 = 3 x 2 x 2 x 3 x 3). The verdicts in Section 9 follow from the
evidence as stated: the "skip" on full-scale universal models rests on verified scale figures (25 and ~500 GPU
nodes, ~1000 stocks, next-mid-direction target); the "skip" on pooling across tick regimes rests on the verified
4.2x sigma gap and Lucchese's Table 8; the "use" items (depth-scaled OFI, tick-indexed volumes, per-contract
thresholds, out-of-time-and-contract test) are conventions, not claims. The single SHOULD FIX is a one-sentence
over-generalisation in the bottom line (the crypto study did net taker fees); the notes are wording and
citation-hygiene items.

---

## Addendum: pass-2 quote check for C2_LOB.md (run after the Part 1 write)

REV_G3_quotecheck2.py on C2_LOB.md: 148 spans, 110 found, 38 missed. The 38, read by hand: 18 are the brief's
hypothesis statements or own labels in quote marks (lines 14, 39 x2, 115, 136, 219, 307, 355, 392 x2, 478, 568 x2,
646, 734 x2, 812, 859); 6 are artifacts (969 Firecrawl notice; 1045 x5 evidence-table cells spanning two quote
marks); 1 is the [unverified] Stoikov abstract (491); 8 are LMZ quotes verified from page images (609, 631, 658 x2,
1045 x4); 1 is the Crossref chapter row (1045, verified); 689 MMW likelihood (verified, rendering); 327 Hawkes
(verified, txt:21, inner curly quotes dropped); 924 Lehalle-Mounjid (verified, page break at txt:1298 / next page);
and 1 is non-verbatim: line 88 "given the order is not cancelled" where the source reads "given that the order is
not canceled" (cst_2010_try1.txt:642-643), a spelling-level paraphrase in quote marks (add to MG3-05's class of
notes; no severity change). Result for C2_LOB.md over both passes: 123 source quotes, 122 verbatim, 1 paraphrase in
quote marks, 0 fabricated or misattributed.

## Totals

BLOCKING 0; SHOULD FIX 5 (C2_LOB 4, C2_Pooled 1); NOTE 14 (C2_LOB 8, C2_Pooled 6). Both files pass this review:
no finding changes a verdict or recommendation.

## Scripts and raw outputs (reports/stage_e28_briefs/work/REV_G3/)

REV_G3_quotecheck.py, REV_G3_quotecheck2.py (quote checks; TSVs REV_G3_quotes_*.tsv, REV_G3_quotes2_*.tsv);
REV_G3_cst_cdl.py (CST Results A/B exact chain, CdL eq. 7 quadrature vs arctan vs discrete Dirichlet solve);
REV_G3_cst_variants.py (eight CST Table 4 readings, queue-length table); REV_G3_cst_cond_cdl_tail.py (own-cancel
conditioning readings; CdL eqs. 3-4 numeric tail and mean); REV_G3_pooled_arith.py (all C2_Pooled worked examples).
Reader scripts run read-only: work/C2_LOB/C2_LOB_examples3.py. Pages read as images: lo_mackinlay_zhang_nber_w6257.pdf
pp. 17-18, 20-21, 36-37. No new sources fetched (WebSearch used: 0 of 15). No reviewed file edited. No commits.

## What I could not finish or verify

- CST Table 4 remains unreproduced after nine readings; I did not attempt the paper's own Laplace inversion.
- LMZ claims not covered by the six pages I read as images ("ITG", "1994-1995", "S&P 500"): not checked.
- Stoikov's published paper and Bouchaud et al.'s book: not open; the brief's [unverified] marks stand.
- DHN: I located the -2.2% (level) and the non-HFT -11.5% (changes) but not an all-order changes HRC for
  Front-of-Queue depth in the saved text, so MG3-11 says what the two numbers are rather than what the third should be.
- A0_contract_stats.json window dates (2022-11-01..2023-10-31) were not re-derived; only the four sigma and volume
  values were read.

Finished 2026-10-21 (PDT; see file mtime).
