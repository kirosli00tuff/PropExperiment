# R_math_G6: independent math and evidence review of C2_AFML.md and C2_Firms.md

Reviewer: MathReviewer-FableXHigh (group G6, Fable 5.1, xhigh). Started 2026-10-21 10:43 PDT, finished 11:10 PDT
(`work/REV_G6/REV_G6_start_time.txt`). Files under review: `reports/stage_e28_briefs/C2_AFML.md` (1294 lines) and
`reports/stage_e28_briefs/C2_Firms.md` (573 lines). The reviewed files were not edited. Scripts and outputs are in
`reports/stage_e28_briefs/work/REV_G6/`:

- `REV_G6_quotecheck.py`: extracts every double-quoted span (20+ characters) from a reviewed file, splits it at
  "...", normalises (NFKC, which maps the PDF's math-italic letters to ASCII; curly quotes; dashes; soft hyphens;
  ligatures; whitespace; case) and searches every saved text file under the pages ROOT, in plain and de-hyphenated
  form. Outputs: `REV_G6_quotes_AFML.tsv`, `REV_G6_quotes_Firms.tsv`.
- `REV_G6_math_checks.py` with `REV_G6_math_checks.json`: re-derivations (sympy) and recomputations (numpy, scipy)
  of every equation and worked example, plus a lag-sensitivity study of the random-walk ADF experiment. Synthetic
  data only. statsmodels is not installed in the project environment, so the ADF regression is implemented by hand
  with the same specification as the reader's `adf_t` (constant, p lagged differences, t on the level coefficient).
- `REV_G6_ctx.py`: prints context windows around a keyword in a saved file (the system grep is ugrep, which rejects
  long context patterns).

Severity scale (from the brief): BLOCKING (a wrong equation or derivation, a wrong number that changes a verdict or
recommendation, a fabricated or misattributed quote, an evidence claim the source does not support); SHOULD FIX (an
error or ambiguity that would mislead a careful reader, a missing [unverified], a wrong number that does not change a
verdict); NOTE (clarity, style).

No web fetch or WebSearch was needed (budget 15, used 0): every claim checked had a saved source, and the two claims
without one (MG6-06, the AFML book's ADF lag setting in MG6-01) are reported as unverifiable from disk rather than
fetched.

---

## Part 1: C2_AFML.md

### 1.1 Findings

| ID | Severity | Location | What is wrong | Evidence (re-derivation or source line) | Proposed fix |
|---|---|---|---|---|---|
| MG6-01 | BLOCKING | C2_AFML.md:137-142 (mechanism), 175-194 (section 1.5 headline and table), 241-243 (assessment), 1138 (verdict reason) | (a) The headline result "A pure random walk passes the 'minimum d' test" rests on an ADF with one lagged difference, which the text never states: `adf_t(x, lags=1)` in `work/C2_AFML/C2_AFML_examples.py` lines 45-57 and 84. The result is lag-dependent. (b) The explanation "An ADF test 'passes' in a finite sample because the stationary moving-average part dominates over that span" is wrong: the level component S(l*) x_t carries 92 to 99 percent of the variance of the FFD output at d = 0.2 to 0.4; the spurious rejection comes from an ADF regression with too few lags when Delta x~_t = sum_k w_k r_{t-k} has a long negative moving average (the weights after w_0 sum to S(l*) - 1 = -0.87 at d = 0.3), the Schwert (1989) size distortion. | `REV_G6_math_checks.json`, key `C_random_walk_adf_by_lags` (T = 200,000, sd 1e-4, tau = 1e-4, every 10th point, three seeds). ADF t at d = 0.3: lags = 1 gives -8.73, -6.76, -4.15; lags = 4 gives -6.20, -4.90, -2.90; lags = 12 gives -4.57, -3.84, -1.97; Schwert lags = 45 gives -2.87, -2.78, -1.12 (critical value -2.86). At d = 0.4 with 45 lags: -2.98, -2.99, -1.17. At d = 0.6 with 45 lags: -3.33, -3.21, -1.33. `share_var_level_part`: 0.975, 0.953, 0.918 at d = 0.2, 0.3, 0.4 (seed 0); sd of the level part is 10 to 4 times the sd of the MA part. The decomposition x~_t = S(l*) x_t + finite MA of returns (lines 131-135) is itself correct (sympy identity for l = 0..6 and the exact Gamma form, key `A_sympy_partial_sum_identity_l0_6`). | In 1.5 state "ADF with one lagged difference (p = 1), the setting AFML's own fixed-width-window snippet uses [unverified: book not fetched]". Replace the mechanism sentence (lines 140-141) with: "With p = 1 the ADF regression cannot absorb the long negative moving average in Delta x~_t (the weights after w_0 sum to S(l*) - 1, about -0.87 at d = 0.3), so the test over-rejects (Schwert 1989). With Schwert's lag rule the rejection at d = 0.3 to 0.4 is borderline or absent (REV_G6_math_checks.json). The output still carries a unit root scaled by S(l*)." In the verdict table (line 1138) write "is reproduced on pure noise with the one-lag ADF the rule uses (section 1.5)". The verdict "maybe" stands on the decomposition argument alone; nothing else in the file depends on the one-lag result. |
| MG6-02 | SHOULD FIX | C2_AFML.md:513-516 (section 4.5, pilot scale) | "Each label then overlaps about 2.9 others, so on average u_bar is about 1/(1 + overlap density)". Read with the 2.9 just stated, this gives u_bar = 0.26, which is wrong by a factor of 2 to 3. Average uniqueness is E[1/c_t], and c_t - 1 (other labels covering a given bar) has mean H / spacing = 60 / 41.4 = 1.45, not 2.9 (2.9 is the number of other labels whose spans intersect a given label's span at all). | `REV_G6_math_checks.json` keys `D_*`: simulated u_bar = 0.53 for Poisson arrivals at one order per 41.4 s (closed form (1 - e^{-1.45}) / 1.45 = 0.528) and 0.69 for evenly spaced orders; 1 / (1 + 2.9) = 0.256; 1 / 1.45 = 0.69. | Replace with: "The mean number of other labels covering a bar is H / spacing = 1.45, so u_bar = E[1 / c_t] is about 0.53 for Poisson-like arrivals and 0.69 for evenly spaced orders; n_eff is then 0.5 to 0.7 of the label count before bursts, which push it lower." |
| MG6-03 | SHOULD FIX | C2_AFML.md:424-425 (H-ML1 sample) and 1119 (table: ">= 500 accepted fills per arm") | The one-sample formula gives 503 observations for a paired or one-sample test. An unpaired comparison of two arms with sd 2 ticks in each needs 2 x 502 = 1,005 per arm. The reader's own JSON agrees (`two_sample_delta0.25_sd2_each_group`: 1006) but the text quotes 500 per arm. | `REV_G6_math_checks.json` key `I_power.two_sample_per_arm_0.25_2` = 1004.7. | "about 1,000 accepted fills per arm for an unpaired comparison, or about 500 paired differences (same days, same posted orders)". |
| MG6-04 | SHOULD FIX | C2_AFML.md:204-206 (H-FD1 sample), also 813 (H-W1 "As for H-FD1") | H-FD1's statistic is a per-fill log-loss difference, but the power illustration is "a 0.25-tick difference when the sd is 2 ticks". The units do not match; a tick-denominated power number says nothing about a log-loss test. | Section 12 formula n = ((1.96 + 0.8416) sigma / delta)^2 is unit-free, but delta and sigma must be in the statistic's units. | State delta and sigma in log-loss units as placeholders (for example delta = 0.005, sigma = 0.3 per fill gives n = 28,000), or restrict the tick example to H-TB1 and H-ML1 and say H-FD1's sample is set by the log-loss sd measured in the pilot. |
| MG6-05 | SHOULD FIX | C2_AFML.md:149-150; the 7.2 million figure recurs at 212, 774, 819, 1083, 1087 | "about 7.2 million points (84 trading days times 23 hours times 3600)": 84 x 23 x 3600 = 6,955,200, about 7.0 million. The script used n_big = 7,200,000, so the timings and memory figures are for 7.2M points and stand; the arithmetic in the text does not. No conclusion changes. | `REV_G6_math_checks.json` key `N_misc.84x23x3600` = 6955200. The window check "less than 0.03%" holds (1458 / 6,955,200 = 0.021%). | "about 7.0 million (84 x 23 x 3600 = 6,955,200; the timing runs used 7.2 million)". |
| MG6-06 | SHOULD FIX | C2_AFML.md:449-450 ("E-mini tick data from 2011 to 2019") | The saved text does not state a 2011 start. It gives only the out-of-sample table captions ("Table 1: Out-of-sample (2018-01-04 : 2019-01-28)", line 607; "Table 2: Out-of-sample (2018-01-18 : 2019-01-31)", line 693) and the Tick Data LLC reference. Every "2011" in the body is the Easley, Lopez de Prado and O'Hara (2011) citation. | grep of `singh_joubert_metalabeling_efficacy.txt` for years 2000-2017 and for "in-sample" (REV_G6_ctx.py). | Mark the span [unverified] or cite the page and line it comes from. The "about one year per strategy (Tables 1 and 2, 2018-2019)" statement is supported. |
| MG6-07 | NOTE | C2_AFML.md:459 ("The test set holds on the order of 100 trades") | This is the reader's estimate, not a source statement. The "153" on the same source line (line 366: "464 transactions dated from 2013 to 2019 and 153 features") is the feature count, not a test-set count. | `man_chan_2020_feature_selection_metalabeling.txt` line 366; test window "Jan 2018 to Oct 2019" at line 370. | "(my estimate: 464 trades over seven years with a 22-month test window)". |
| MG6-08 | NOTE | C2_AFML.md:567 | The Li quote "under beta-mixing the leakage bias at a test point is at most 2M betamix (delta)" is at line 23 of `arxiv_2609_29530_trinity_validation.txt`, not line 17. The quote itself is verbatim. | sed of lines 14-32 of the saved file. | Change "line 17" to "line 23". |
| MG6-09 | NOTE | C2_AFML.md:131, 139, 167-173 | The asymptotic column "l^{-d} / Gamma(1-d)" is computed with l = l* + 1 (the window length), while S(l) ~ l^{-d} / Gamma(1-d) is stated for l = l*. Both agree to three decimals in every row except d = 0.4, tau = 1e-3 (0.1352 with l* + 1, 0.1362 with l*, exact 0.1359). Immaterial. | `REV_G6_math_checks.json` key `A_ffd_table` (columns `asym_with_lstar`, `asym_with_L`, `exact_Gamma_formula_lstar`). | Say "l = window length" in the table header, or use l*. |
| MG6-10 | NOTE | C2_AFML.md:1290-1292 ("39 of 39 found") | The evidence table (lines 1225-1264) has 40 rows. All 40 are found: 38 in the saved .txt files and 2 only in the raw HTML `citation_abstract` meta tags of the Joubert 2022 and Thumm 2023 landing pages, as the table says. | `awk` row count 40; `grep -c` of the two landing .html files (3 hits each). | "40 of 40". |
| MG6-11 | NOTE | C2_AFML.md:859-861 | Donoho's line 86 threshold carries a constant ("t_n = sqrt(2 log n) gamma_1 sigma / sqrt(n), gamma_1 a constant defined in section 6.2") that the restatement drops. The abstract's version (lines 12-14), which the text also cites, has no such constant and is the standard universal threshold. | `donoho_1995_denoising_soft_threshold.txt` lines 83-87. | Cite the abstract form only, or mention gamma_1. |
| MG6-12 | NOTE | C2_AFML.md:295-306 versus `C2_AFML_examples.json` key `triple_barrier_toy` | The script's toy uses barriers +/-0.20 (upper 100.2, lower 99.8, first touch at update 1), not the +/-0.50 and +/-0.75 example in the text. The text says "computed by hand" and is correct as written (my recomputation: +/-0.50 touches at update 5, label +1; +/-0.75 touches at update 6, label +1), so this is only a mismatch between script and text. | `REV_G6_math_checks.json` key `Q_triple_barrier`. | Either align the script's toy with the text or drop the JSON key. |
| MG6-13 | NOTE | C2_AFML.md:647 and 675 | "each group tested phi times" (647) and the phrase at 675 are the reader's own words in quotation marks next to genuine source quotes. | Quote check: no saved file contains them. | Use italics or no quotes for paraphrase. |
| MG6-14 | NOTE | C2_AFML.md:63 | "as much memory as possible." is quoted with a full stop; the source phrases it as a question ("How can we make a price series stationary while preserving as much memory as possible?", `lopezdeprado_2018_10reasons_jpm.txt` line 259) and the text cites lines 282-283 for the next quote only. | Quote check (segment matched except the terminal punctuation). | Cite line 259 and drop the full stop inside the quotes. |

Counts for C2_AFML.md: BLOCKING 1, SHOULD FIX 5, NOTE 8 (14 findings).

### 1.2 Equations and derivations checked (all correct unless listed above)

- FFD recursion w_k = -w_{k-1} (d - k + 1) / k, closed form w_k = (-1)^k C(d, k) = Gamma(k - d) / (Gamma(k + 1) Gamma(-d)),
  asymptotic |w_k| ~ k^{-d-1} / |Gamma(-d)|: sympy ratio w_5 / w_4 = -(d - 4) / 5; closed form agrees with the
  recursion to 7e-17 for k <= 50; |w_50| 50^{1.4} |Gamma(-0.4)| = 1.006. Source: `lopezdeprado_2018_10reasons_jpm.txt`
  lines 282-288 (recursion, "with omega_0 = 1"); `hurvich_farima_handout.txt` lines 81-83 (Gamma form) and 118-119
  ("pi j ~ j^{-d-1} / Gamma(-d) as j -> infinity").
- Special cases d = 0 and d = 1; "all weights after omega_0 = 1 are negative and greater than -1": source lines
  293-299.
- Stationarity for d in (-0.5, 0.5), spectral density (sigma^2 / 2 pi) |2 sin(lambda / 2)|^{-2d} ~ lambda^{-2d}:
  `hurvich_farima_handout.txt` lines 121, 151, 158-169 (the extraction shows "f(lambda) = sigma^2/2pi |1 - e^{-i
  lambda}|^{-2d} = sigma^2/2pi |2 sin(lambda/2)|^{-2d}" and "f(lambda) ~ sigma^2/2pi lambda^{-2d}"). I(1 - d) after
  differencing an I(1) series, stationary only for d > 0.5: correct.
- Partial-sum identity S(l) = sum_{k=0}^{l} w_k = prod_{k=1}^{l} (1 - d/k) = Gamma(l + 1 - d) / (Gamma(1 - d)
  Gamma(l + 1)) ~ l^{-d} / Gamma(1 - d): verified symbolically for l = 0..6 and numerically for every table row
  (windows 497, 55, 282, 1458, 140; sums 0.248, 0.136, 0.070, 0.036, 0.023). The decomposition x~_t = S(l*) x_t -
  sum_k w_k (r_t + ... + r_{t-k+1}) is correct.
- ADF regression and the -2.86 critical value (the source quotes -2.8623): correct.
- Triple-barrier definitions and the gambler's-ruin statement P(up first) = b / (a + b): simulation with a = 3,
  b = 1 gives 0.249. Source lines 360-371 confirm the label rule and "t_{i,1} <= t_{i,0} + h".
- Meta-labeling: precision and recall definitions (lines 397-399), F1 harmonic mean (403-404), break-even precision
  b / (a + b), bet-sizing formula marked [unverified] as it should be.
- Uniqueness: u_{t,i} = 1_{t,i} / c_t, average uniqueness, return-attribution weights normalised to I: match source
  lines 455-473 (the garbled fraction reads w~_i = |sum r_{t-1,t} / c_t|, w_i = w~_i I (sum_j w~_j)^{-1}).
- Purging's three overlap conditions and the embargo rule: match source lines 510-523 exactly.
- Li (2026) bound 2M beta_mix(delta) and the H + c tau rule: verbatim at lines 23 and 742 of the saved text; the
  table rows at lines 720-722.
- CPCV: C(N, N - k) = C(N, k); phi[N, k] = (k / N) C(N, k) = C(N - 1, k - 1): matches the source's garbled display at
  lines 575-590 ("phi[N,k] = k/N C(N, N-k) = prod_{i=1}^{k-1} (N - i) / (k - 1)!"); the N = 6, k = 2 example (15 splits,
  5 paths) at lines 592-596.
- Wavelets: filter properties, quadrature mirror g_l = (-1)^{l+1} h_{L-1-l}, Haar and D(4) coefficients, MODWT
  rescaling h~_{j,l} = h_{j,l} / 2^{j/2} and L_j = (2^j - 1)(L - 1) + 1 (`percival_2018_modwt_slides.txt` lines 42,
  45), pyramid and inverse pyramid with the forward-looking index t + 2^{j-1} l (lines 484-494), energy identity
  (372-376), MRA (163), period band 2^j to 2^{j+1}: all correct.
- Donoho: soft threshold, universal threshold, the sqrt(2 log n) argument (lines 381-383), near-minimaxity (163,
  411-414): correct.
- Periodogram and Parseval, GPH slope f^{-2d}: correct.
- Andersen-Bollerslev model r_{t,n} = sigma_t s_n z_{t,n} / sqrt(N) (Yan lines 572-576), the log-squared regression,
  E[log z^2] = -gamma - log 2 = -1.2704 for Gaussian z, 2P + 3 parameters (7 for P = 2, 11 for P = 4): correct.
  The normalising constants in A&B's FFF are marked [unverified], correctly.
- Power rule n = ((1.96 + 0.8416) sigma / delta)^2: 502.3 -> 503 (ceiling), 2009.3 -> 2010, 3139.6 -> 3140;
  Bonferroni z for alpha = 0.05 / 20 = 3.0233 and n = 956.0: correct.

### 1.3 Worked examples recomputed (all reproduce)

FFD weights for d = 0.4 (1, -0.4, -0.12, -0.064, -0.0416, -0.029952) and the window/sum table; the random-walk
table's lags = 1 values are reproducible in form (my seeds give the same ordering and signs; the reader's seed is
20261021); d* by segment matches the JSON; uniqueness toy (c = (1,2,2,1,1,1), u_bar = 0.667, 0.667, 1; w~ = 0.003,
0.002, 0.002; w = 1.286, 0.857, 0.857; n_eff = 2.33); purge toy (41.4 s spacing, 1.45 labels per boundary, h = 1,680
events = 0.84 sessions); CPCV table and the 15-split check; Haar MODWT on X = (4, 6, 10, 12, 8, 6, 5, 5): W~_1, W~_2,
V~_2, D~_1, D~_2, S~_2 all equal the text to the last digit, energy 446 = 446, MRA error 0, and the causality test
(W~_1 changes at t = 0, 7; W~_2 at 0, 1, 2, 7; D~_1 at 0, 6, 7; S~_2 at 0, 1, 2, 4, 5, 6, 7) exactly as stated;
soft-threshold toy (median 0.25, sigma 0.3706, t 0.7559, 2.5 -> 1.7441, -1.8 -> -1.0441); periodogram toy (I(1/4) = 2,
|X_6| = 4, Parseval 4 = 4); meta-labeling toy (-0.21 per fill, break-even 0.5455, +0.01 per fill, sd 1.0945, se 0.0547,
t = 0.18, recall 0.489, F1 0.518); LightGBM timing 5.63 s (`C2_AFML_lgb_probe.json`), 45 x 5.6 s = 4.2 min, 4,500
fits = 7.0 h, 270 x 6 s = 27 min, 10,920 x 6 s = 18.2 h, 18 x $0.89 = $16.02; memory 9 x 7.2M x 8 B = 0.518 GB and
13 arrays = 0.749 GB; 2^12 s = 68.3 min; 84 x 1,380 = 115,920; 20 x 1,380 = 27,600.

### 1.4 Quote check

89 quoted segments of 20 or more characters extracted from the whole file (text and evidence table); 74 matched
verbatim in a saved file; 15 misses, of which 12 are the reader's own phrases or regex spans between two quotes on
one line, 1 (MG6-14) matches except its terminal punctuation, and 2 are fragments of the RunPod price sentence
(shorter than the threshold); I checked the three RunPod prices by hand in the flattened page: "$ 0.89 /hr" is
preceded by "RTX 4090 24 GB VRAM 41 GB RAM 6 vCPUs" and followed by "Deploy RTX 4090"; "$ 1.79 /hr" by "A100 PCIe 80
GB VRAM 117 GB RAM 8 vCPUs" and "Deploy A100 PCIe"; "$ 2.89 /hr" by "H100 PCIe 80 GB VRAM 188 GB RAM 16 vCPUs" and
"Deploy H100 PCIe"; the Lambda rows "A100 SXM 40 GB ... $1.99" and "H100 PCIe 80 GB ... $3.29" are verbatim. Net:
0 real misses. Evidence table: 40 rows, 40 found (2 in HTML meta tags). Two quotes carry the reader's noted
pdftotext hyphen ("pa- rameters") as in the file. Cited numbers checked against sources: Hasumi Table 1 0.7302 and
Table 2 0.4841-0.5238 (lines 214-216, 348-353); Singh precision 0.17 -> 0.20, accuracy 17% -> 63%, 0.48 -> 0.54 (lines
600-602, 686-688); Man and Chan Sharpe 0.360 / 0.743 / 0.829 (line 436), 464 transactions 2013-2019 (366), test set
Jan 2018 to Oct 2019 (370), "100 iterations" (152, 204); Korean study 29-day window and 9% barriers (28-29); Deep et
al. p-value 0.34 (30), 100 US equities (25, 96, 554), 34 test periods (872); Li IC +0.318 / +0.004 / +0.000 (720-722);
highfrequency defaults P1 = P2 = 5 (rdoc lines 69-73); bilkent record volume 289, start page 543, issue 3-4; JCER
Discussion Paper No. 148; Hasumi's data is the S&P 500 (lines 186-187); Slepaczuk listed before Bieganowski on the
arXiv 2411.12753 title page; Li 2026 single author (Jiayu Li); Andersen-Bollerslev 1996 is Deutschemark data (lines
70, 119). [unverified] marks are present at every place where the text relies on an abstract, a citing paper, memory
or an unfetched book (lines 102, 376-378, 439-443, 697-702, 739, 837, 840-841, 862-863, 897-898, 925, 1003), with the
one omission in MG6-06.

### 1.5 Verdicts

The ten verdicts in section 13 follow from the evidence as cited, with one qualification: the FFD "maybe" cites the
pure-noise reproduction (MG6-01), which holds only for the one-lag ADF; the verdict is still supported by the
decomposition argument (an FFD output has a unit root scaled by S(l*) for every d < 1) and by the absence of any
cost-inclusive out-of-sample evidence. The N accounting in section 12 (minimal set 7, maximal 18) adds up. H-CV0 and
H-CV1 as 0-cost diagnostics, and "every order-book model must beat a time-of-day baseline", are recommendations that
the evidence supports; whether to adopt them is the lead's decision.

### 1.6 Judgment

The mathematics of C2_AFML.md is sound: every equation matches its saved source where the source text exists,
every restated garbled equation (Hurvich, Lopez de Prado, Percival, Donoho, Yan) is restated correctly, and all
thirteen worked examples and all compute and memory figures reproduce to the last printed digit. The reader's own
contributions (the FFD partial-sum decomposition, the MODWT causality demonstration, the precision-to-P&L
break-even) are correct and are flagged as the reader's. The one substantive defect is in the file's strongest
original claim: the random walk "passes" the minimum-d ADF test only with the one-lag ADF the script uses, the text
does not say so, and the stated mechanism is wrong (the level component, not the moving-average part, dominates the
output's variance; the rejection is the classic ADF size distortion under a long negative MA). The FFD verdict
survives on the decomposition argument, so the fix is textual, but as written the headline overstates what was
shown. Secondary issues are a misleading effective-sample formula (MG6-02), a halved two-arm sample size (MG6-03), a
units mismatch in one power example (MG6-04) and a 3.5 percent arithmetic slip in the point count (MG6-05). Evidence
handling is careful: 40 of 40 evidence quotes are verbatim, [unverified] marks are used where full text was not read,
and the one unsupported detail (the 2011 data start, MG6-06) is minor.

---

## Part 2: C2_Firms.md

### 2.1 Findings

| ID | Severity | Location | What is wrong | Evidence (source line) | Proposed fix |
|---|---|---|---|---|---|
| MG6-15 | BLOCKING (misattributed speaker; the lead may downgrade, see note) | C2_Firms.md:445 (E4 "same (NS)"); uses at 34-35, 313 ("Parameter-stability ('heat map') checks: Man AHL E4"), 352 ("Man AHL E4"), 408 | The heat-map quote is attributed to Neil Shephard (NS). In the saved page the speaker tag immediately before the sentence is "CH:" (Campbell Harvey, academic board member). Harvey is describing "A common approach", not a Man AHL practice. The quote itself is verbatim and from the cited document, so the document attribution is right; the speaker tag is wrong and the tables in sections 2 and 3 present a board member's general remark as a Man AHL practice ("Man AHL E4"). No verdict depends on it. | `man_overfitting_investor_2015.html.txt` line 201 "CH:", line 202 "A common approach is to look at how slightly different models perform, i.e. you modify the model parameters and look at the corresponding 'heat maps'...", line 203 "NS:" (Shephard's reply begins "Which is the exact opposite of what you are looking for in statistics"). Tags precede speech throughout (line 141 "Cam Harvey (CH):" then line 142 his words). | In E4 replace "same (NS)" with "same (Campbell Harvey, board member, describing 'a common approach')". In the section 2 table row and section 3.1 row write "Man AHL board write-up (Harvey) E4; the write-up's own summary lists 'model stability under parameter variation' (E3)". Note: the brief's scale makes any misattributed quote BLOCKING; the consequence here is limited to attribution, so SHOULD FIX would also be defensible. |
| MG6-16 | SHOULD FIX | C2_Firms.md:334-336 (section 2, pattern 3: "co-location, FPGA inference") | "FPGA inference" and "co-location" carry no evidence ID and no [unverified]. Both are supportable from saved pages but are not in the evidence table. | `hrt_machine_learning.md`: "novel inference devices like ASICs and FPGAs (both off-the-shelf and in-house)"; `optiver_blog_why-market-data-is-a-deep-learning-challenge.html.txt`: "which may require custom inference hardware designed with FPGA engineers. In high-frequency trading, every nanosecond matters." Co-location is in evidence for Virtu only (E93). | Add evidence rows (for example E95 HRT, E96 Optiver) with those quotes and cite them; cite E93 for co-location or mark it [unverified] for the ML firms. |
| MG6-17 | SHOULD FIX | C2_Firms.md:144-146 ("the competition pages were not fetched in this pass [unverified beyond search snippets]") | The reader's own log records a fetch of Optiver's page on the Kaggle closing-cross competition, saved as `optiver_kaggle_closing_cross.html` (2026-10-21 02:51 PDT, curl), and the saved text contains "2023". The sentence contradicts the log; the [unverified] mark is over-cautious rather than missing, but the statement "not fetched" is false as written. | `pages/C2_Firms/log.tsv` row for https://optiver.com/kaggle-and-optiver-predicting-nasdaqs-closing-cross-auction-movements/; `optiver_kaggle_closing_cross.html.txt`. | Either add an evidence row quoting the saved page and drop [unverified], or write "Kaggle's own competition pages were not fetched; Optiver's post on the 2023 closing-cross competition was saved (optiver_kaggle_closing_cross.html) but is not used as evidence". |
| MG6-18 | NOTE | C2_Firms.md:81 ("trade-press interview with AHL's CIO, Risk.net 2018") | The Risk.net piece (dated 08 Dec 2017, Risk Awards 2018) describes Sargaison as "co-chief executive"; CIO was his title at the 2015 board meeting (E1). The speaker attribution for E89-E91 is right ("Matthew Sargaison, Man AHL ... 'he says'"). | `risknet_man_ahl_2018.html.txt`: "Co-chief executive officers Matthew Sargaison and Antoine Forterre"; "says Matthew Sargaison, co-chief executive". | "AHL's co-CEO (its CIO at the time of E1)". |
| MG6-19 | NOTE | C2_Firms.md:133-134 (E32) | "became a customer, then an investor, of BMLL" is supported by the saved page but not by the E32 quote, which only covers "lacking". | `optiver_bmll_level3.html.txt`: "Here's the story of how we became customers of BMLL's Level 3 historical data and, eventually, investors." | Extend the E32 quote with that sentence. |
| MG6-20 | NOTE | C2_Firms.md:244-245 (E78, "reliance has grown sharply") | Supported by the saved page but not by the E78 quote. | `janestreet_what_we_do.html.txt`: "The depth of our reliance on these models has grown dramatically in the last few years". | Extend the E78 quote. |
| MG6-21 | NOTE | C2_Firms.md:450 (E9, "same" with no speaker) | The speaker is Anthony Ledford (tag "AL:" at line 249), Man AHL's Chief Scientist; naming him strengthens the row, since it is a Man staff statement rather than a board member's. | `man_overfitting_investor_2015.html.txt` lines 249-250. | "same (Anthony Ledford, Chief Scientist, Man AHL)". |
| MG6-22 | NOTE | C2_Firms.md:474-475 (E33, E34) and 434-435 (the 94 of 94 claim) | Two E33 segments ("The best bid price, for instance, can be called...", "Sequence numbers (which provide the true ordering...") and the E34 sentence are not findable by grep in the saved `optiver_bmll_case.pdf.txt`, which is a layout-mode extraction that splits them across columns. They are verbatim in a default-mode `pdftotext` run of the saved PDF, which is what `C2_Firms_verify.py` uses (it runs pdftotext on the .pdf). The 94 of 94 claim is therefore true but not reproducible from the .txt alone. | `pdftotext optiver_bmll_case.pdf -` contains all three segments. | Save a default-mode .txt beside the layout one, or note in section 5 that PDF quotes were verified against pdftotext output, not the saved .txt. |
| MG6-23 | NOTE | C2_Firms.md:218, 509, 556 | The AQR title is written Can Machines 'Learn' Finance? (single quotes); the saved page has double quotes around Learn. Harmless. | `aqr_can_machines_learn_finance.html.txt`. | None needed, or match the source's quote marks. |

Counts for C2_Firms.md: BLOCKING 1, SHOULD FIX 2, NOTE 6 (9 findings).

### 2.2 Equations and numbers checked (all correct)

- Section 4 step 1 toy: expected value (2p - 1 - c) ticks, break-even p* = (1 + c) / 2, and 52 percent accuracy breaks
  even only for c <= 0.04 ticks: correct (2 x 0.52 - 1 = 0.04). The reader rightly labels it a toy and defers to
  measured markouts.
- Harvey and Liu example (E16, text lines 65-66): annualised SR 1.0 over 120 months, monthly autocorrelation 0.1
  (source line 643), 100 tests, average correlation 0.4; Lo's autocorrelation correction with q = 12 and rho = 0.1
  gives 0.9122 (reported 0.912); the 52.0 percent haircut equals 1 - 0.438 / 0.912 = 0.5197. Source lines 641-649.
- HLZ counts (E58): "of the 296 published significant factors, 158 would be considered false discoveries under
  Bonferonni, 142 under Holm" at `hlz_2016_cross_section.pdf.txt` lines 1771-1772 (the source's spelling).
- AQR costs (E70): 17 bps at 2 percent and 28 bps at 6 percent of daily volume, lines 859-861.
- McLean-Pontiff as quoted by JKP (E67): "26% lower out-of-sample and 58% lower post-publication", line 314.
- Virtu (E46): "one losing trading day during the period depicted, a total of 1,238 trading days"; the period is
  "January 1, 2009 through December 31, 2013" (lines 294-296), so "(2009-2013)" is right. The 10-K is for the fiscal
  year ended 31 December 2025 (`virt-20251231.htm` in the log; "December 31, 2025" appears 212 times), so "FY2025" is
  right.
- XTX 53,000 instruments and 25,000 GPUs (E44, E45); Jane Street 4,032 GPUs (E77); Optiver's "1,000 trading days ...
  roughly six weeks" (E37; 1,000 hours = 41.7 days); Risk.net "fewer than one in 10" (E89).
- Attributions: Jamil Baz is "Chief Investment Strategist of Man GLG" (line 130); E6 and E7 follow "MS:" tags (lines
  217, 264); E8 follows "NG:" (266); E10 follows "NS:" (268); E11 follows "CH:" (258); Kelly is at Yale, AQR and NBER
  and Pedersen at AQR (`jkp_2023_replication_crisis.pdf.txt` lines 83-86), so "AQR authors" holds; Kelly and Xiu carries
  the AQR disclaimer (line 23).
- Dates: the four Optiver pages carry datePublished 2026-10-06, 2025-12-18, 2026-07-20 and 2025-05-13, matching the
  evidence table; the CFM note is "May 2018"; Rej, Seager and Bouchaud are at Capital Fund Management.
- Arnott-Harvey-Markowitz's seven categories (text line 283-284) match Exhibit 2 headings at lines 681-721 of the
  saved PDF text (Research Motivation; Multiple Testing and Statistical Methods; Data and Sample Choice;
  Cross-Validation; Model Dynamics; Complexity; Research Culture).

### 2.3 Quote check

250 quoted segments of 20 or more characters extracted from the whole file; 224 matched verbatim in a saved file;
26 misses, of which 20 are the reader's own phrases or regex spans between two quotes on one line, 3 are the AQR
title's quote-mark style (MG6-23) and 3 are the E33/E34 segments that are verbatim in pdftotext output of the saved
PDF but split in the saved layout .txt (MG6-22). Net: 0 real misses. Evidence table: 94 rows, 94 found. Every row's
claim says no more than its quote except where noted (MG6-15 framing; MG6-19 and MG6-20, where the saved page
supports the extra claim). [unverified] and POINTER-GRADE marks are present where required (E68 abstract only, E89-E91
trade press, the SEBI order, the six firms not researched, the Suhonen et al. figure), with the one inverted case in
MG6-17.

### 2.4 Verdicts

The file sets no thresholds and states that its section 4 process is a draft for the lead. The section 2 table and
the section 3 transfer tables follow from the cited evidence with two exceptions: the "Man AHL E4" rows (MG6-15), which
should read as a board write-up remark by Harvey, and the "co-location, FPGA inference" clause (MG6-16), which is true
of the saved sources but uncited. The negative-evidence statements in section 6 (no firm publishes a holdout length,
fold design, multiple-testing threshold or capital rule) are consistent with the evidence table: no E-row contradicts
them.

### 2.5 Judgment

C2_Firms.md has almost no mathematics (one toy expected-value formula, correct) and its evidence is well handled:
all 94 quotes are verbatim in the saved files or in pdftotext output of the saved PDFs, the cited numbers (Harvey-Liu
0.912 and 52.0 percent, HLZ 296/158/142, AQR 17/28 bps, Virtu 1,238 days over 2009-2013, the compute figures) check
against their sources and, where derivable, against my own arithmetic, and the claims generally stay within their
quotes. The defects are in attribution and framing rather than content: one speaker tag is wrong and turns an
academic board member's description of "a common approach" into a Man AHL practice in two tables (MG6-15); one
sentence in the cross-firm synthesis asserts FPGA inference and co-location without an evidence row although the
saved HRT and Optiver pages would support it (MG6-16); and one statement that a page was not fetched contradicts the
reader's own log (MG6-17). None of these changes a recommendation in sections 3 or 4, all of which the cited evidence
supports as worker proposals for the lead.

---

## Limits of this review

- statsmodels is not installed in the project environment, so the ADF regressions in MG6-01 use a hand-written OLS
  with the same specification as the reader's `adf_t`; the Schwert lag rule 12 (n / 100)^{1/4} with n = 20,000 gives 45
  lags. Critical values are the standard -2.86 (constant, large n) that both files use.
- The AFML book was not fetched by the reader or by me; my statement that AFML's fixed-width-window snippet calls the
  ADF with one lag is from memory and marked [unverified] in MG6-01. It does not affect the finding, which rests on
  the reader's own script.
- The Singh and Joubert data start (MG6-06) could not be confirmed or refuted from the saved text; it may be in a
  figure the extraction does not carry.
- I did not re-run the reader's scripts; every number was recomputed independently in `REV_G6_math_checks.py` and
  compared with the text and with `C2_AFML_examples.json`.
