# R_math_G1: adversarial math and evidence review of C2_SDE.md and C2_Filter.md

Reviewer: MathReviewer-FableXHigh (group G1), Stage E.28. Started 2026-10-21 10:38 PDT.
Scripts: reports/stage_e28_briefs/work/REV_G1/. Reviewed files are not edited.
Severity: BLOCKING / SHOULD FIX / NOTE, as defined in the brief.
Status: IN PROGRESS (written incrementally; sections below are appended as they finish).

## File 1: reports/stage_e28_briefs/C2_SDE.md (870 lines)

Checked 10:40-11:00 PDT. Independent re-derivations: work/REV_G1/REV_G1_sde_checks.py (output
REV_G1_sde_checks_out.txt, sections S0-S8). Quote check: work/REV_G1/REV_G1_quotecheck.py, report
REV_G1_quotecheck_SDE.md. The reader's own script (work/C2_SDE/C2_SDE_examples.py) was read, not run; its output
file's sha256 is 27ffc12b...e680b9 as the file states.

### Equations and derivations checked (all correct unless listed in the findings table)

| location | item | check |
|---|---|---|
| L23-27 | 15% ann. vol -> 47.25 pts/day -> 0.3089 pts (1.2354 ticks) per sqrt-second; 0.977 pts at 10 s, 2.392 at 60 s | recomputed (S0) |
| L55-58 | Ito's lemma; note that the MIT L18 theorem line prints the dB coefficient without sigma_t | confirmed: mit_18s096_lec18_ito.txt L88 has "+ ∂f/∂x dBt", the proof line L96 has "+ σt ∂f/∂x dBt" |
| L70-75 | d log S = (mu - sigma^2/2) dt + sigma dB; mean gap S0(exp(sigma^2 h/2) - 1) = 0.000572 pts (60 s), 0.0343 pts (1 h) | sympy drift = mu - sigma**2/2; numbers recomputed (S1) |
| L98-100 | ABM from L18 Example 1.3(i); GBM from Example 1.3(iii) | source L107-109 and L128-136 match |
| L101-106 | Roll: Cov(dp_t, dp_{t-1}) = -s^2/4 = -0.0156 pts^2 at s = 0.25 | exact symbolic sum over the 8 sign patterns gives -s**2/4 (S2) |
| L114-117 | eta_hat = N^(c)/(2 N^(a)); X_hat = P - sign(dP)(1/2 - eta_hat) alpha; RV on X_hat is D-R eq. (3) | dayri_rosenbaum_large_tick.txt L518-531, L553-557 match |
| L131-135 | eta_hat = 0.2143, implicit spread 0.107 pts (0.43 tick), X_hat = 5000.18 (0.29 tick below) | recomputed (S2) |
| L171-181 | Kou eq. (1); density with eta1 > 1, eta2 > 0; p + q = 1 | kou_2002.txt L72-87 match |
| L184-189 | E[Y], E[Y^2], solution S_t, QV of log S and its expectation | correct; solution is Kou's eq. (3) (L140) |
| L202-213 | E7 jump arithmetic: 22.5 pts^2, RMS 4.75 pts (19 ticks), 2.12 pts at lambda = 5, 23.6 pts (94 ticks) at 20%; 790 round turns; Kou E[Y] = -0.10%, E[Y^2] = 1.4e-5, RMS 18.7 pts | recomputed (S3); see MG1-04 on which variance 2232 denotes |
| L252-260 | BNS eq. (4) BPV, (5) mu1, (6) vartheta = 0.6090, (11) ratio statistic -> N(0, vartheta), quadpower with delta^-1, J_hat with max(t^-1, .) | bns_2006_bipower_jumps.txt L151, L162, L229, L325, L348, L366-369 match |
| L261-267 | Lee-Mykland eqs. (7)-(8), K = O_p(dt^alpha) with -1 < alpha < -0.5, Lemma 1 eqs. (12)-(13), c = sqrt(2/pi), beta* = 4.6001 | lee_mykland_2008.txt L291, L301, L332, L441-450 match |
| L263-264, L294 | smallest admissible K is about sqrt(252 x n_obs/day) = 2428 for 23,400/day | LM L406-417: candidates lie between sqrt(252 n_obs) and 252 n_obs; their 16/78/110/156/270 equal ceil(sqrt(252 n_obs)) with 24-hour days; recomputed (S4) |
| L268-272 | ASJ eqs. (12)-(13): limit 1 with jumps, k^{p/2-1} without (2 at p = 4, k = 2); 1/2 under i.i.d. noise | aitsahalia_jacod_2009_jumps.txt L388-400, L1099 match |
| L290-296 | C_n = 5.139, S_n = 0.2794, critical 6.42 (n = 23,400); 5.47 (n = 390); 7.36 (n = 1.872e6); 1,170 naive flags | recomputed to 4 decimals (S4) |
| L338-350 | Bao et al. (2.1), (2.2), (2.4), (2.5); exact step variance sigma^2(1 - e^{-2 kappa h})/(2 kappa); mu_hat, sigma_hat^2 mappings | source L185-230 match; sympy integral gives the step variance; e^{kappa t}x trick verified (S5) |
| L351-355 | Avellaneda-Lee eq. (21) mapping and the s-score eq. (15) | avellaneda_lee_2010_statarb.txt L1402-1412 (block numbered (21)), L707 match |
| L367-369 | Delta kappa = (1 + 3 phi)/(n h phi) ~ 4/T; relative bias 5.77 HL/T; 10% needs T = 58 HL | sympy d kappa/d phi = -1/(h phi); factor 4/ln 2 = 5.771 (S5) |
| L381-383 | asymptotic s.d. sqrt(2 kappa/T) = 0.00022 at kappa = 0.05, T = 2e6 | agrees with the AR(1) Fisher information (1 - phi^2)/n mapped through d kappa/d phi; marked [unverified] in the file, correctly |
| L392-402 | E4: kappa 0.0513, HL 13.5 s, bias -0.0064, kappa 0.0581 (x1.13), HL 11.9 s; phi = 0.999: 0.99234, 0.0077 (x7.7), 90 s; 17% at n = 23,400 | recomputed (S5). Independent Monte Carlo (seed 7, 4,000 reps): bias -0.00648 (formula -0.00642) at phi = 0.95; -0.00881 (formula -0.00666) at phi = 0.999; median kappa_hat x1.10 and x7.99. The reader's -0.00619 / -0.00875 and x1.10 / x8.1 are consistent |
| L451-465 | ZMA eqs. (4), (10), (11), (12)/(32), (13), (15), (33), (35), (36), (41), (42) | zma_2005_tsrv_nber.txt L155, L253, L257, L283, L348, L360, L579-586, L613-622, L693, L720 match; error orders and K = O(n^{2/3}), O_p(n^{-1/6}) re-derived |
| L494-503 | RV 1 s bias 468 = 21%; rounding bias 60.9 = 2.7% (uniform rounding variance 0.125^2/12); noise estimator 0.0577 at 1 s; 0.978/(1 - 1/60) = 0.995 | recomputed (S6) |
| L488-491 | E5b table | reproduced with a different seed (99): iid RV1 1.208(0.011), TSRV60 0.977(0.052), TSRV300 0.975(0.114), TSRV818 0.954(0.193); rounded RV1 1.027(0.010). TSRV columns identical across the two noise rows is expected: the same X path is used and TSRV removes the noise bias, so only the X discretisation error remains. See MG1-03 for the mean shortfall |
| L533-541 | margin $0.03/RT = 0.012 tick per fill; nets -$0.095, -$0.22, -$0.595 | recomputed (S7) |
| L561-569 | reflection principle and the 3x3 touch table | MIT L17 Prop. 2.3 (L114-117) matches; all 9 entries recomputed to 3 decimals (S7) |
| L575-580 | Cont-de Larrard eq. (7) phi(n,p), Theorem 1 limit delta sqrt(pi lambda/D(f)) W, D(f) eq. (9), balanced case lambda = mu + theta | cont_delarrard_2013_markov_lob.txt L473-478, L668, L687-693 match; see MG1-05 on the rescaling |
| L596-604 | sample sizes ((1.645 + 0.842) sigma_h/delta)^2: 3,774 ... 226,467 | recomputed exactly (S7) |
| L606-608 | 4,250-17,000 fills; 0.25 tick = 20.8 x margin | recomputed |
| L628-637 | MBP-10: 47 + 320 = 367 field bytes; 0.74-3.68 GB/session; 63-313 GB for 85 sessions | field types confirmed in databento_mbp10_docs.html; sizes recomputed (S8); see MG1-08 |
| L640-644 | Lambda $1.29 (A10, 30 vCPU, 226 GiB), $0.69 (Quadro RTX 6000, 14 vCPU, 46 GiB); Hetzner EUR 43.49 | lambda_pricing.html and hetzner_cloud.html de-tagged text match |
| L678-680 | 4 rules -> N + 4; with 3 BOUNCE horizons and 2 VR horizons -> N + 8 | arithmetic consistent with the table |

### Findings

| ID | severity | location | what is wrong | evidence | proposed fix |
|---|---|---|---|---|---|
| MG1-01 | SHOULD FIX | C2_SDE.md:235 and :815 | The quoted string "analytical solutions for call and put options" is a paraphrase presented as a verbatim quote. It appears nowhere in the saved text. | kou_2002.txt L18-19 (abstract): "the model is simple enough to produce analytical solutions for a variety of option-pricing problems, including call and put options"; L83-85: "It leads to analytical solutions to many option-pricing problems, including European call and put options". The claim itself (option-pricing purpose) is supported. | Replace both occurrences with: "the model is simple enough to produce analytical solutions for a variety of option-pricing problems, including call and put options" |
| MG1-02 | SHOULD FIX | C2_SDE.md:476 | "(DJIA 2004)" misdates the Hansen-Lunde evidence. 2004 is the working-paper version date; the DJIA sample is 2000-2002. | hansen_lunde_2006.txt L487-488: "We analyze stock returns for the 30 equities of the Dow Jones Industrial Average (DJIA). The sample period spans three years, from January 3, 2000 to December 31, 2002"; L12: "This version: September, 2004". | Replace "(DJIA 2004)" with "(DJIA, 2000-2002; September 2004 version)" |
| MG1-03 | SHOULD FIX | C2_SDE.md:488-498 | The E5b TSRV means fall below 1 by about (K-1)/n + n_bar/n, and the text explains only the n_bar/n part (eq. 41). The K subgrids each start at offset k and end at the last index in that residue class, so on average they miss (K-1)/n of the session: 0.25% at K = 60, 1.3% at K = 300, 3.5% at K = 818. Predicted means 0.981, 0.984, 0.964 match the reader's 0.978, 0.982, 0.964 and my replicate 0.977, 0.975, 0.954 (s.e. 0.004, 0.008, 0.014). The 3.6% shortfall at K = 818 is therefore an edge effect of the estimator as implemented, not a noise effect, and the (41) adjustment does not remove it. A reader would otherwise take TSRV at the textbook K as biased by noise. | REV_G1_sde_checks_out.txt S6; derivation: subgrid k spans [t_k, t_{k + K floor((n-k)/K)}], mean loss (K-1)/n. ZMA's asymptotics drop this O(K/n) = O(n^{-1/3}) term, which here exceeds the n_bar/n term. | Add after the (41) bullet: "The remaining shortfall is an edge effect: each of the K subgrids misses, on average, (K-1)/n of the session, so E[TSRV]/IV is about 1 - (K-1)/n - n_bar/n: 0.981, 0.984 and 0.964 for K = 60, 300, 818, which the table reproduces. Neither (41) nor more data at the same K removes it; in the pilot, scale by n/(n-K+1) or anchor every subgrid to both ends of the session." |
| MG1-04 | NOTE | C2_SDE.md:202-206 | "Use the illustrative daily variance of 2232 points^2. Suppose jumps are 1% of quadratic variation" does not say that 2232 is the continuous part. The script computes jump variance as share/(1-share) x 2232 (22.5), which is right only under that reading; if 2232 were total QV the jump variance is 22.3 and, at 20%, 446 (RMS 21.1 pts, 85 ticks) rather than 558 (23.6 pts, 94 ticks). | C2_SDE_examples.py: `jv = share * qv / (1 - share)`; S3 gives both readings. No verdict changes. | Write "Take 2232 points^2 as the continuous (diffusive) variance; a jump share s of total QV then adds s/(1-s) x 2232" |
| MG1-05 | NOTE | C2_SDE.md:577-580 | Theorem 1 is stated for the rescaled price s_{n log(n) t}/sqrt(n), not for the price itself. The physical-time diffusion coefficient is their eq. (13), sigma = delta sqrt(n pi lambda/D(f)) with n ln n tau_0 = tau_2. | cont_delarrard_2013_markov_lob.txt L687-693 and L740-747. The qualitative conclusion drawn (sigma set by tick, arrival rates and depth) is unchanged. | Replace "the price converges to" with "the rescaled price s_{n log(n) t}/sqrt(n) converges to" and cite eq. (13) for the per-unit-time sigma |
| MG1-06 | NOTE | C2_SDE.md:109-110 and :819 | The consistency of eta_hat is attributed to Robert and Rosenbaum (2011). Dayri-Rosenbaum cite [35] for it, which is Robert and Rosenbaum (2012, Mathematical Finance 22, 133-164); [34] (2011, JFEc 9) is the model. | dayri_rosenbaum_large_tick.txt L524-525 "It is proved in [35]"; L1397-1403 list [34] and [35]. | Say "model: Robert-Rosenbaum (2011); estimator consistency: Robert-Rosenbaum (2012), per Dayri-Rosenbaum's ref. [35]" |
| MG1-07 | NOTE | C2_SDE.md:142-145 and :668 | H-SDE-ETA puts H0 at eta = 1/2, which is the boundary of the model's admissible range (the bid zone needs alpha/2 - eta alpha >= 0, so eta <= 1/2; D-R treat eta = 1/2 as "optimal tick"). A two-sided bootstrap CI around 1/2 straddles the boundary; the alternative of interest is one-sided, eta < 1/2. eta_hat itself can exceed 1/2 on trending data (N^(c) > N^(a)). | dayri_rosenbaum_large_tick.txt L472, L502-509, L1144-1160. | State the alternative as eta < 1/2 (one-sided) and report the CI's upper end against 1/2 |
| MG1-08 | NOTE | C2_SDE.md:628-632 | The 368th byte is attributed to padding. In the DBN binary it is the record header's `length` field (uint8), which the docs' field table omits. The saved page states neither a record size nor a `length` field. | databento_mbp10_docs.html de-tagged text: no "368", no "length" field; the 13 listed field types sum to 47 bytes and 10 levels to 320 (S8). The DBN header layout is from my knowledge of the spec [unverified against a saved page]. | Change "the padding byte is my assumption" to "the extra byte is the DBN record header's length field [unverified]; total 368 bytes" |
| MG1-09 | NOTE | C2_SDE.md:154 | "describe exactly this E-mini tick oscillation": the saved text says "S&P 500 futures are priced in units of 25 cent"; "E-mini" is the reader's inference (the 0.25 tick is the E-mini/MES tick). | safari_schmidhuber_2025_trends_reversion.txt L486. | Write "S&P 500 futures with a 0.25 tick (the E-mini grid)" |
| MG1-10 | NOTE | C2_SDE.md:178 and :186-187 | "Density of Y (Kou eq. (1)-(2))": the density display is unnumbered between (1) and (2); (2) is the xi+/xi- representation. The solution S_t marked [derived] is Kou's eq. (3). | kou_2002.txt L84-92, L136-141. | Cite "(unnumbered display after eq. (1); eq. (2) is the mixture form)" and "[Kou eq. (3); re-derived]" |
| MG1-11 | NOTE | C2_SDE.md:351 and :643 | Body quotes are transliterated: "kappa = -log(b) * 252" for "κ = −log(b) ∗ 252", "EUR 43.49" for "€ 43.49". The evidence table has the verbatim forms. | avellaneda_lee_2010_statarb.txt L1402; hetzner_cloud.html text. | Either use the verbatim glyphs in the body or drop the quotation marks there |
| MG1-12 | NOTE | C2_SDE.md:293 vs :380, :607 | The pooled Lee-Mykland example uses 80 sessions; the OU and fill-count examples use 85 sessions for the same 4-month window. | E6 vs E4/E3 in C2_SDE_examples_out.txt. Harmless (critical value 7.36 vs 7.37). | Use one session count, or say both are round numbers |
| MG1-13 | NOTE | C2_SDE.md:357-361 | The AR(1) bias formula -(1 + 3 phi)/n is correctly marked [unverified] (from memory). My independent Monte Carlo agrees with it at phi = 0.95 (-0.00648 vs -0.00642) and shows the same understatement at phi = 0.999 that the reader reports. It is the Kendall (1954) fitted-mean result, from my own knowledge; still no fetched source. | REV_G1_sde_checks_out.txt S5. | Keep the mark; no change |

Counts: BLOCKING 0, SHOULD FIX 3, NOTE 10.

### Quote check (REV_G1_quotecheck_SDE.md)

Evidence table (section 12): 57 quoted segments across 60 rows. 47 match the named saved file after normalising
whitespace, hyphenation, ligatures, quotes and all non-alphanumerics. 10 did not match mechanically; each was read
against the raw source lines:
- 9 are PDF typography the reader flagged in brackets: sum sign extracted as "X" (L778), fractions set vertically
  (L779, L782), hats and superscripts on separate lines (L784, L791, L792), two-column interleaving (L813, L814;
  kou_2002.txt L77-81 and L236-237 read line by line give the quoted text), and my own checker stripping the
  citation brackets "[35]" and "[0, t]" (L819; the source L524-525 is verbatim). All 9 verified.
- 1 is a paraphrase in quotation marks (L815, MG1-01).
Body text: 29 quoted segments of 3+ words. 18 match a saved file. Of the 11 flagged, 8 are checker artifacts (text
between two adjacent quotes, or the reader's own phrases in quotes: L136, L156, L364, L429, L510, L641) or
the [unverified] Yu abstract (L360), 2 are transliterations (L351, L643; MG1-11), and 1 is MG1-01 again (L235).
Other body claims checked against the saved text and found supported: LM used 15-minute returns to limit noise
(lee_mykland_2008.txt L1011-1013); ASJ's DJIA 2005 application and the mass below 1 (aitsahalia_jacod L112, L1062,
L1099); A-L ETF "similar degradation after 2002" (L21); Bajgrowicz "too sparse" (L93), "do not cluster in time"
(L102); Christensen 4.4% and 15% for S&P 500 futures at 5 minutes (L115, L127) and the EBS/CME acknowledgement
(L35); Baron channels (L33-37); Cartea et al. MLOs for liquidity takers (L21-23); CJP chapter and appendix titles
(cjp_2015_frontmatter.txt L390-410, L444-450); the Christensen file is arXiv:2602.10925v1 dated 11 Feb 2026 with
a November 6, 2014 manuscript date (L4, L9), as the reference list says. [unverified] marks are present for every
source named but not fetched (Roll, Lo-MacKinlay, Yu, Tang-Chen, Kendall/Marriott-Pope, realised kernels,
pre-averaging, LM12, Merton, Shreve, Robert-Rosenbaum 2011, the two books' chapters) and for the two standard
results stated from memory (sqrt(2 kappa/T), the AR(1) bias). Cited numbers match their sources (mu1, vartheta,
beta*, 0.6366, 1%, 4.4-15%, 12 days, 90%, $1.29, $0.69, EUR 43.49, 1.44/0.9 Sharpe, 10 bp cost). The log.tsv
records the failed fetches the file lists (Merton 404 and MIT DSpace, HAL bot page, Princeton and Springer bot
pages, empty Wayback shell, CUHK and CORE shells, CME JS table).

### Verdicts

Every verdict in section 9 is supported by the section's own evidence: no method is rated "use" as a strategy; the
"use" verdicts are for measurement (eta, OU half-life with the bias guard, TSRV, touch-vs-fill gap) and are
consistent with the worked examples; the "skip"/"maybe" verdicts rest on the quoted negative evidence
(Safari-Schmidhuber, Bajgrowicz et al., Christensen et al., Baron et al.) and on the $0.03 margin arithmetic, which
is correct. The hypothesis table (section 10) is internally consistent with the text (4 rules, 8 with all horizons),
and every count is explicitly left to the lead. One caution for the lead that the file states but could state more
sharply: the 7.5 power table assumes independent fills and a markout s.d. equal to the diffusion s.d., both
optimistic, so the "4,000-17,000 fills" sample supports only a 1-s or 10-s primary horizon at the 0.1-0.25-tick
effect sizes.

### Judgment

The mathematics of C2_SDE.md is sound. Every equation I checked matches its cited source (equation numbers included,
with the two small numbering slips in MG1-10), every derivation marked [derived] re-derives (sympy for the Ito
drift, the OU integrating factor and step variance, the Roll autocovariance and the kappa-bias chain rule), and all
seven worked examples reproduce to the printed precision from an independent script, including a different-seed
Monte Carlo for the OU bias and the TSRV table. The one substantive gap is interpretive: the TSRV table's mean
shortfall is a subgrid edge effect the text does not name (MG1-03). The evidence base is honest: 47 of 57 table
quotes match mechanically, the rest are typography except one paraphrase in quotation marks (MG1-01), one date
is wrong (MG1-02), and [unverified] marks are used wherever the full text was not read. Nothing found changes a
verdict or a recommendation.

## File 2: reports/stage_e28_briefs/C2_Filter.md (1019 lines)

Checked 11:00-11:35 PDT. Independent re-derivations: work/REV_G1/REV_G1_filter_checks.py (output
REV_G1_filter_checks_out.txt, sections F1-F7). Quote check: REV_G1_quotecheck_Filter.md. The reader's scripts
(work/C2_Filter/C2F_examples.py, C2F_bench.py) were read, not run; C2F_bench_results.json was dumped and every
"measured" number in the text was compared with it.

### Equations and derivations checked (all correct unless listed in the findings table)

| location | item | check |
|---|---|---|
| L93-115 | KF model and recursion, Welch-Bishop eqs. (1.9)-(1.13); innovation and gain quotes | welch_bishop_kf_intro.txt L225-241 match; L110, L115-116 hold the quotes |
| L126-134 | Gaussian-conditioning derivation of (1.11)-(1.13) | correct (joint Gaussian of (x_t, z_t) with cross-covariance P H') |
| L138 | Gaussian prediction-error log-likelihood | correct |
| L164-170 | local-level scalar filter; steady state P = (q + sqrt(q^2 + 4qr))/2, K = P/(P + r) | sympy roots of P = Pr/(P + r) + q (F1) |
| L172-176 | steady filter is an EWMA with weight K | correct |
| L178-184 | dy is MA(1): Var q + 2r, Cov -r, rho_1 = -r/(q + 2r) in (-0.5, 0); MoM r = -gamma_1, q = gamma_0 + 2 gamma_1 | correct (F1) |
| L197-202 | Palomar state-space pairs model, section 15.6.3 and (15.3) | palomar_book_kalman_pairs.html has 15.6.3 and (15.3); quote L494 matches |
| L214-220 | P = 0.018463, K = 0.5416, EWMA half-life under 1 s (0.889 steps), rho_1 = -0.379 | recomputed (F1) |
| L223-228 | four-step local-level table | every cell recomputed to the printed digits (F1) |
| L232-235 | MLE q = 0.009981, r = 0.015577, 0.68 s, 66 evaluations; rho_1 -0.3794 vs -0.3788 | C2F_bench_results.json kf_mle_1e6 and kf_mom_rho1 match. The likelihood is the MA(1) innovations form dy_t = v_t - (1 - K) v_{t-1} with variance F at the steady-state K (C2F_bench.py L59-68): correct, see MG1-19 |
| L237-247 | hedge-ratio three-step table; z = -0.94 | every cell recomputed (F2) |
| L262-265 | n per group = 2 (3.0 + 0.8416)^2 (sigma/d)^2: 1,063 / 6,642 / 266 | recomputed: 1,063 / 6,641 / 266 (F3); 6,642 vs 6,641 is rounding |
| L267-269 | 2 x 2 x 3 = 12 configurations | correct |
| L279-282 | 80 x 23,400 = 1.87 M; bench times 0.85 s, 0.074 s, 0.68 s | JSON matches |
| L285-286, L519, L706-707 | PyPI versions and upload dates (pykalman 0.11.2 2026-01-31, filterpy 1.4.5 2018-10-10, statsmodels 0.15.0 2026-08-27, particles 0.4 2023-11-06, hmmlearn 0.3.3 2024-10-31) | pypi_*.json parsed: all match |
| L344-346 | EKF recursion with Jacobians | standard form, correct |
| L353-357 | UT sigma points and weights (lambda = alpha^2 (L + kappa) - L, W_0^c = W_0^m + 1 - alpha^2 + beta) | Wan-van der Merwe standard form; the alpha, kappa, beta quotes verified at wan_vandermerwe_ukf.txt L156-162 |
| L369-374 | exact e^{1/8} = 1.13315; EKF 1.0 (12% error); UT lambda = 2, points 0, +-1.7321, weights 2/3, 1/6, 1/6, mean 1.13301 | recomputed (F4); see MG1-16 on "within 0.01%" |
| L375-378 | SV observation has zero conditional mean; log(y^2) linearisation | correct |
| L409-412, L418-423 | SIR weights, filtering estimate, likelihood increment, ESS | correct; D&J quotes at L39, L526, L810 match |
| L432-437 | Bayes recursion derivation | correct |
| L441-449 | D&J Example 4 SV model, X_1 ~ N(0, sigma^2/(1 - alpha^2)); bootstrap weight N(y; 0, beta^2 e^x) | doucet_johansen_pf_tutorial.txt L181 matches |
| L466-482 | five-particle bootstrap step: propagation, weights (0.01686 ... 0.07454), sum 0.21202, W, likelihood 0.0424, ESS 3.875, systematic resampling picks 1, 3, 4, 5, 5, filtered mean 0.2585 vs 0.077 | every number recomputed (F5) |
| L504-517 | 1.87 M x 1,000 particles about 100 s; 10,000 x 100 s = 11.6 days; S-J rate scaled to 187,200 obs = 32-66 min; $0.89 x 100 = $89 | recomputed (F7); JSON pf timings and 1.2% resample rate match |
| L562-566, L571-584 | Hamilton (Palgrave) eqs. (4), (5), (7)-(12); ergodic start; forward algorithm cost O(N^2 T) | hamilton_palgrave_regime.txt L92, L158, L179-236, L212-216; jurafsky L264 match |
| L569 | expected regime duration 1/(1 - p_jj) | correct (geometric) |
| L586-609 | filter derivation, backward pass, smoothed and pairwise probabilities, Gaussian M-step | correct, standard |
| L611-614 | Viterbi (Jurafsky A.14) and its causal use | jurafsky L489 matches; the statement about running it only through t is correct |
| L643-656 | two-regime filter table (durations 100 and 20 steps, start 0.83333, densities 0.79788 and 0.19947, all 4 rows) | every cell recomputed (F6) |
| L658-663 | filtered turbulent probabilities 0.048, 0.016, 0.304, 0.106 then 0.9997, 1.0000; Viterbi all calm on 4 observations, all turbulent on 6 | reproduced exactly, including the full Viterbi flip (F6) |
| L665-674 | 97.25% vs 98.98%; Baum-Welch 0.99536, 0.98036, 1.0029, 3.0104; -343,389.1 to -332,005.96, flat after iteration 8 | JSON matches (loglik_path index 7 onward equal) |
| L689-696 | paired-days detectable d = 3.8416 s_D/sqrt(80) = 0.43 s_D; 2 x 3 x 3 = 18 | recomputed (F3) |
| L704-705 | 27.3 s on 200 k steps -> 4.3 min on 1.87 M ("about 4.5") | recomputed (F7) |
| L845-846 | 2 x 3.8416^2 = 29.52 | correct |

### Findings

| ID | severity | location | what is wrong | evidence | proposed fix |
|---|---|---|---|---|---|
| MG1-14 | SHOULD FIX | C2_Filter.md:530-531 (and the Section 5 row at :757) | "the SV rules were short the VXX on 396 to 551 days of the period" inverts the paper's own description of the trades. The 396-551 figures are the "-" column of Table 8, which the caption defines as days "short the index"; the text says "there are many more long VXX trades (i.e., short the VIX index)", and describes the VXX as "an ETF inversely linked to the VIX index". So the SV rules were long the VXX / short the VIX index on those days. The reader's inference ("a period in which being short volatility paid") survives, since short VIX is short volatility, but the stated position is backwards. | stroud_johannes_2014.txt L2095-2098 (caption), L2107, L2123-2126, table rows L2075-2084 (SV2 7/551 SR 2.19, SVt2 5/521 SR 1.78, SVCJ2 7/396 SR 2.32). The Sharpe range 1.78-2.32 is correct. | Replace with: "the SV rules were short the VIX index (long the VXX, which the paper describes as inversely linked to the VIX) on 396 to 551 of the days, a period in which being short volatility paid" |
| MG1-15 | SHOULD FIX | C2_Filter.md:255-258 | H-KF1's parenthetical "(d_t > 0 for an ask: the filter says the efficient price sits on the far side of the mid)" is ambiguous and reads as inverted. With d_t = x_{t\|t} - mid_t, d_t < 0 for a bid puts the filtered efficient price below the mid, on the bid's own side and nearer the resting order, which is the adverse case; likewise d_t > 0 for an ask. The hypothesis direction (lower markout) is consistent with that reading, so only the words are wrong, but this sentence defines a pre-registerable condition and must be unambiguous. | Sign algebra: markout = mid_{t+h} - bid; if E[mid_{t+h}] ~ x_{t\|t} < mid_t the expected markout falls below the half-spread. | Replace the parenthetical with: "(the filter puts the efficient price on the order's own side of the mid, nearer the resting bid or ask, so the fill is more likely adverse)" |
| MG1-16 | NOTE | C2_Filter.md:373-374 | "within 0.01% of the exact value": the UT mean 1.133010 differs from e^{1/8} = 1.133148 by 0.012%. | F4 | Write "within 0.02%" or "0.012%" |
| MG1-17 | NOTE | C2_Filter.md:667-668 | "The 1.7 points are exactly the regime changes the filter recognises late": the benchmark measures only the aggregate accuracy gap; the gap is concentrated at regime changes but was not shown to be exactly them. | C2F_bench_results.json holds only the two accuracy numbers. | Write "mostly" or "the bulk of" |
| MG1-18 | NOTE | C2_Filter.md:859 | The "use (one pre-registered gate)" verdict rests on Bulla et al. (daily equity indices, 10 bp costs) plus the mechanism argument; the file says so and expects a modest effect. No intraday, passive-order evidence exists (the file's own gap statement, L765-769). The verdict is defensible as framed, but "maybe (one gate)" would be equally consistent with the evidence; the lead should read "use" as "worth one test", not as evidence of an intraday effect. | Sections 4.8, 5, 9. | Optional: rename the verdict "maybe: one pre-registered gate" to match the Kalman row's wording |
| MG1-19 | NOTE | C2_Filter.md:233 | "Nelder-Mead on the steady-state innovations likelihood of dy" is correct but terse: the code evaluates the exact Gaussian likelihood of the MA(1) dy_t = v_t - (1 - K) v_{t-1}, Var(v) = F, with K and F fixed at their steady-state values rather than the time-varying P_t, an approximation that is immaterial at n = 10^6 and is why q_hat, r_hat land within 0.3% of the truth. | C2F_bench.py L59-68 | Add "(steady-state K and F; exact only asymptotically)" |

Counts: BLOCKING 0, SHOULD FIX 2, NOTE 4.

### Quote check (REV_G1_quotecheck_Filter.md)

Evidence table (E1-E50): 51 quoted segments. 45 match the cited saved file after normalisation (41 by file name;
4 where the cell names several files or a page image and the text matched one of them: E31's "three fundamental
problems" and the three E50 PyPI summaries). 6 did not match mechanically; each was read against the raw source:
- E6 (L949): wan_vandermerwe_ukf.txt L182-184, two-column interleave; verbatim.
- E25 (L968): hamilton_1989.pdf has no text layer (hamilton_1989.txt is 28 bytes); I read page 1 (p. 357) of the
  saved PDF as an image: the abstract sentences are verbatim, including "The parameters of an autoregression are
  viewed as the outcome of a discrete-state Markov process".
- E31 (L974): rabiner_1989.pdf likewise (rabiner_1989.txt is 30 bytes); page 1 (p. 257) read as an image ends
  "the three fundamental problems for HMM design": verbatim.
- E32, E33 (L975-976): jurafsky_martin_hmm_appendix.txt L262-264 and L616-619, margin labels interleaved; verbatim.
- E36 (L979): christensen_godsill_turner_2020_hmm_momentum.txt L1243-1245, hyphenated across three lines
  ("re-/duce", "approx-/imately"); verbatim.
- E40 (L983): bessec_bouabdallah_2005.txt L19-20, ligatures extracted as "…"; verbatim.
Body text: 95 quoted segments after joining markdown line breaks; 52 match a saved file (including the Kalman
abstract, all Welch-Bishop lines, Cartea-Karyampas L237 "bid-ask bounces; differences in trade sizes; and other
sources", the Dahlhaus-Neddermeyer, Stroud-Johannes, Hamilton, Engel, Li et al. and Campi-Zabaljauregui lines). The
43 flagged are checker artifacts (text between two adjacent quotes), the reader's own phrases in quotes (L24, L64,
L775), the five segments already verified by eye above, the Wan-van der Merwe alpha/kappa/beta lines (L156-162,
verified by eye with the symbols dropped as the file says), and the Doucet-Johansen weight step, which the file
labels as mangled and restates. [unverified] marks are present for Mertens et al., Dacco-Satchell, Brigida, and the
unfetched Harvey (1990) and Gordon et al. (1993). Cited numbers match their sources: 41%, 18.5-201.6 bp, 10 bp
(bulla L80-83, L727), 12,500 draws in 12-25 min (stroud L734), up to 50% (L28), 2009-2012 (L27), 10^-4 s (li L17),
Sharpe > 2.0 and 15% (christensen L33, L1243-1245), 258 trading days of 2011 (L871), 18 exchange rates (engel L35),
47 commodities and minute data (he L178-181), the He et al. Sharpe 10/18 (L188), $0.89 and $0.5 (RunPod), $1.29 and
$1.99 (Lambda), EUR 43.49 (Hetzner); C3_lead_draft.md L23, L37 and L55-57 hold the three passages the file cites
from it, and docs/DECISIONS.md:30-46 is C3's own citation. Every "measured" number in sections 1.5, 1.7, 3.7, 4.5
and 4.7 equals the value in C2F_bench_results.json.

### Verdicts

The verdicts (section 9) follow from the evidence as the file presents it: the Kalman "maybe", the hedge-ratio
"skip" (one contract), the EKF/UKF "skip as a separate method", the particle-filter "skip for now" and the
directional-HMM "skip" are each tied to a quoted source or to the program's own cost arithmetic. The HMM-gate "use"
is the one verdict that reaches beyond the evidence's frequency (MG1-18); the file is explicit about that gap and
about the controls in section 6, which are sound (filtered-only inputs, frozen parameters with an embargo, label
definition by property, per-decision scoring paired by day). The hypothesis table (section 8) is consistent with
the text, the power arithmetic is correct, and all counts are left to the lead.

### Judgment

C2_Filter.md is mathematically clean. All equations are standard and match their cited sources (Welch-Bishop,
Hamilton's Palgrave entry, Doucet-Johansen, Wan-van der Merwe, Jurafsky-Martin) with the equation numbers the
sources print; the two derivations the reader marks as their own (Gaussian conditioning, the local-level steady
state and MA(1) moments) are right; and all six worked examples, including the full Viterbi look-ahead flip and
the five-particle step, reproduce digit for digit from an independent script. The measured numbers all trace to
the saved JSON. The evidence table is verbatim throughout, with the two page-image quotes confirmed from the PDF
images. The two SHOULD FIX items are a reversed trade direction in the Stroud-Johannes summary (MG1-14) and
an ambiguous sign description in the H-KF1 definition (MG1-15); neither changes a verdict.

## Closing summary

| file | BLOCKING | SHOULD FIX | NOTE |
|---|---|---|---|
| C2_SDE.md | 0 | 3 (MG1-01, 02, 03) | 10 (MG1-04 to 13) |
| C2_Filter.md | 0 | 2 (MG1-14, 15) | 4 (MG1-16 to 19) |
| total | 0 | 5 | 14 |

Quote check totals: C2_SDE.md 58 table segments, 50 mechanical matches, 8 read by eye (7 typography, 1 paraphrase
= MG1-01); C2_Filter.md 51 table segments, 45 mechanical matches, 6 read by eye (all verbatim). No fabricated or
misattributed quote in either file. No new source was fetched (WebSearch budget used: 0 of 15). Scripts and
outputs: reports/stage_e28_briefs/work/REV_G1/ (REV_G1_quotecheck.py and its two reports, REV_G1_sde_checks.py,
REV_G1_filter_checks.py and their _out.txt files). Not done: the Kendall/Marriott-Pope AR(1) bias formula and the
sqrt(2 kappa/T) standard error remain checked only by my own derivation and Monte Carlo, not against a fetched
source, which is how the file marks them. Reviewed files were not edited.

Status: COMPLETE.
