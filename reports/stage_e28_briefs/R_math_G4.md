# R_math_G4: adversarial math and evidence review of C2_Control.md and C2_StatsRMT.md

Reviewer: MathReviewer-FableXHigh (Fable 5.1, xhigh), Stage E.28, group G4. Started 2026-10-21 (PDT; times below from `date`).
Scope: equations and derivations, worked-example arithmetic, verbatim quotes against saved sources, [unverified] marks, verdicts against evidence.
Scripts: reports/stage_e28_briefs/work/REV_G4/. Reviewed files are not edited.
Severity: BLOCKING / SHOULD FIX / NOTE as defined in the brief.

Status: IN PROGRESS. Sections are appended as they are checked; an incomplete section is marked (pending).

---

## Part 1. C2_Control.md

Checked 2026-10-21 10:38-11:20 PDT. Scripts: work/REV_G4/REV_G4_control_check.py (output REV_G4_control_check_out.txt),
work/REV_G4/REV_G4_quotecheck.py (output REV_G4_qc_Control.tsv). The reader's scripts C2_examples.py, C2_threshold.py and
C2_gaowang.py were read, not run; every number was recomputed independently.

### 1.1 Equations and derivations checked against the saved sources

| Item | Result | Source line(s) checked |
|---|---|---|
| 1.2 HJB (drift, diffusion, two jump terms, terminal condition) | correct; matches A-S lines 296-310 | avellaneda_stoikov_2008.txt 296-310 |
| 1.3 CARA ansatz, bid bracket -> [1 - e^{-gamma(delta-p)}], p = s - r^b = theta(q) - theta(q+1) + s | correct; A-S (3.2), (3.4) r^b = theta(q+1) - theta(q), (3.6) | 319-320, 337-351 |
| 1.3 FOC for exponential rate: e^{-gamma(delta-p)} = k/(k+gamma), delta* = p + (1/gamma) ln(1+gamma/k); limit 1/k | re-derived by hand; correct | (3.6) with lambda/lambda' = -1/k |
| 1.3 Gueant 2017 xi = 0 condition p = delta* + Lambda/Lambda' | correct | gueant_2017_optimal_mm.txt 462-465 |
| 2.2 Ho-Stoll equations as given by the review | faithfully transcribed (including the review's odd indicator x rate x dt notation) | multiple_dealers_2015_review.txt 149-200 |
| 3.2 (2.3), (2.6), (2.7), r = s - q gamma sigma^2 (T-t), (2.11) A = Lambda/alpha, k = alpha K | correct | 112-156, 268-277 |
| 3.2 (3.17)-(3.18); theta^1 = s, theta^2 = (1/2) sigma^2 gamma (T-t); spread independent of q | correct | 365-442 |
| 4.2 GLFT Prop. 1 (ODE system, alpha, eta), Prop. 2 (v = exp(-M(T-t)) 1), Thm 1 quotes | correct | gueant_lehalle_ft_2013.txt 300-381 |
| 4.2 asymptotic delta^b, delta^a, spread; hftbacktest c1, c2, half-spread, skew | correct; (1/2k) sqrt(alpha/eta) = (1/2) sqrt(sigma^2 gamma/(2kA) (1+gamma/k)^{1+k/gamma}) re-derived | GLFT 612-630; hftbacktest_glft_tutorial.txt 64-80 |
| 5.2 Model A / Model B objectives; eq. (3.9) rewritten with signs flipped; H_xi(p) | correct (source has 0 = -d_t theta + 1/2 gamma sigma^2 q^2 - 1 H^b - 1 H^a; the rewrite multiplies by -1) | gueant_2017_optimal_mm.txt 305-440 |
| 6.2 CJR eq. (1), (4), (11); CDJ eq. (1), (8), (13a) | correct; all terms as in source | CJR 242, 595-600, 729; CDJ 168-171, 829, 967-975 |
| 7.2 A-C eqs (2), (6), (7), (8) with eta~ = eta - gamma tau/2, (16) kappa~^2 = lambda sigma^2/eta~, (17)-(19), theta = 1/kappa | correct | almgren_chriss_2000.txt 352-492, 589-686 |
| 8.2 Gao-Wang E[profit | fill] = lambda+/(lambda+ + lambda/2) - 0.5; Theorem 4.3 (1) condition lambda+ <= lambda/2 | correct | gao_wang_2020_latency.txt 564-575, 690-697 |
| 8.2 fee extension: post iff lambda+/(lambda+ + lambda/2) > 0.5 + f | correct (E[profit|fill] - f > 0) | reader's derivation |
| 9.2 Poisson MLE N/T, se sqrt(N)/T, se(log) = 1/sqrt(N), WLS weights N | correct; WLS with weights N reproduces the Poisson MLE exactly on the toy counts (A = 1.0585, k = 1.5007, se(k) = 0.0362 by both) | REV_G4_control_check_out.txt |

### 1.2 Worked examples recomputed (REV_G4_control_check_out.txt)

- 3.5(a): spread 1.69077, bid 99.1546 / ask 100.8454; q = +1 bid 98.7546 / ask 100.4454; table constants 1.3289 and 1.1507. All match.
- 3.5(b): inventory term 6.0, constant 1.3289, spread 7.329, delta^a(q=+1) = -2.3355. Match.
- 4.5(a): alpha = 0.000135, eta = 0.32568; exact (Q = 10, T = 600) q = 0: 3.324, q = 5: (3.848, 2.840); approx 3.313 and (3.652, 2.974). Match. See MG4-02 for what the Q = 10 comparison shows.
- 4.5(b): Q = 1 flat 0.905, long 0.424; Q = 3 flat 0.746, q = 1 (0.920, 0.583), q = 2 (1.171, 0.409). Match.
- 4.5(c) thresholds: reader's 0.311 reproduced under the approximation for sigma = 1; the sigma = 0.5 value 6.69 is NOT reproduced (approximation gives 1.78; see MG4-01). Exact bounded thresholds differ from all three.
- 4.6: 3/sqrt(80) = 0.3354, annualized 5.32; MES net per fill $0.015 = 0.0120 tick, ES $4.36 = 0.3488 tick, ratio 29.1. Match.
- 6.5, 6.6, 6.7 arithmetic (0.062 tick = $0.078; 0.199 tick = $2.49; 2,950 fills; 30 and 1,010 states). Match.
- 7.5: kappa = 1.414, 0.0447, 0.00447 per s; kappa(discrete) = 0.01413; holdings and trades match to 2 d.p.
- 8.2 / C2_gaowang: thresholds 0.988 and 0.651, ratios 82.3 and 1.867, nets at 0.70/0.80, sample sizes 794/173/914. Match.
- 9.3: lambda_hat, s.e., WLS k = 1.5007 (se 0.0362), A = 1.0585. Match.
- Fee facts: rules/products.py line 154 MES 122, line 153 ES 378; 1.22/1.25 = 97.6%. Match.
- Falces Marin Table 2 AS-Gen column: 28 of 30 days negative (positives: days 21 and 29); mean -0.24; Alpha-AS means -0.11 and -0.13. Match.

### 1.3 Findings

| ID | Severity | Location | What is wrong | Evidence | Proposed fix |
|---|---|---|---|---|---|
| MG4-01 | SHOULD FIX | C2_Control.md:361-364; work/C2_Control/C2_threshold.py | The gamma thresholds at which the flat quote moves one tick behind the touch (0.311, 6.69, 0.052) are computed from the large-Q asymptotic approximation c1 + sigma c2/2, yet the sentence applies them to the Q = 1, 2, 3 policies the section recommends. The exact bounded solution crosses 1.0 tick at much lower gamma. In addition C2_threshold.py has a units bug: its c2 already contains sigma (sigma^2 inside the square root) and is then multiplied by sigma again, so the sigma = 0.5 threshold is wrong even under the approximation. | REV_G4_control_check_out.txt: A=0.5,k=1.5,sigma=1: approx 0.3112, exact Q=1 0.1301, Q=2 0.1912, Q=3 0.1925. sigma=0.5: approx 1.7837 (reader 6.6919), exact Q=1 0.7907, Q=3 0.9523. A=0.1: approx 0.0515, exact Q=1 0.0222, Q=3 0.0350. The qualitative conclusion (at gamma = 0.01 every flat quote rounds to the touch) still holds: exact flat quotes 0.905, 0.778, 0.746 for Q = 1, 2, 3. | Replace lines 362-364 with: "with A = 0.5, k = 1.5, sigma = 1.0 the exact bounded solution needs gamma >= 0.13 (Q = 1) to 0.19 (Q = 3) per tick; with sigma = 0.5, gamma >= 0.79 to 0.95; with A = 0.1, gamma >= 0.022 to 0.035 (REV_G4_control_check_out.txt). (The large-Q approximation gives 0.31, 1.78 and 0.052.)" and fix C2_threshold.py so c2 excludes sigma or is not multiplied by s a second time. |
| MG4-02 | SHOULD FIX | C2_Control.md:347-350 | "The approximation is good near q = 0 and drifts at larger |q|, the same pattern Gueant (2017) reports" is drawn from a Q = 10 run where q = 5 is half-way to the bound. The discrepancy at q = 5 is the inventory bound's effect, not the Gaussian approximation's: with Q = 20 the exact q = 5 quotes are (3.654, 2.972) against approx (3.652, 2.974), and q = 0 is 3.313 = approx. | REV_G4_control_check_out.txt lines "Q=5/10/20/30" | Say: "With Q = 10 the exact q = 5 quotes differ from the approximation by 0.2 and 0.13 tick; the difference comes from the inventory bound (Q = 20 gives 3.654/2.972, equal to the approximation to 3 d.p.). The approximation is the Q -> infinity limit." Drop the Gueant 2017 analogy or attach it to the bounded case only. |
| MG4-03 | SHOULD FIX | C2_Control.md:574-575 | "Table 4, n_Z = 3: e.g. ORCL 11.75 to 33.29 across phi": those numbers are the Table 5 row (n_Z = 5). The Table 4 (n_Z = 3) ORCL row is 11.65 ... 34.25. | cartea_donnelly_jaimungal_2018_obsignals.txt 1599-1601 ("ORCL 11.65 16.76 ... 34.25" then "Table 4: ... nZ = 3") and 1616-1618 ("ORCL 11.75 14.28 ... 33.29" then "Table 5: ... nZ = 5") | "(Table 4, n_Z = 3: e.g. ORCL 11.65 to 34.25 across phi; Table 5, n_Z = 5: 11.75 to 33.29)". No verdict changes. |
| MG4-04 | SHOULD FIX | C2_Control.md:899-902 | The ordering argument "If it [H-GW1] fails on the purchased contract, H-GLFT1 and H-CJ2 cannot pass either, since they earn the same per-fill economics with fewer fills" is wrong for H-CJ2. H-CJ2 gates fills by imbalance bucket precisely to select fills with a higher benign share (the section's own 6.5 example); an unconditional benign share below 0.5 + f does not bound the gated subset's share. It holds for the touch variant of H-GLFT1 only (same fill population). | Internal consistency with 6.5 (bucket markouts -0.40 / -0.15 / +0.05 change the per-fill economics by bucket) and with Gao-Wang's own interpretation of lambda+ as a conditional rate. | "If it fails, the touch variant of H-GLFT1 cannot pass (same fills). H-CJ2 can still pass if the gated buckets' benign share clears 0.5 + f; H-GW1 computed per imbalance bucket is its precondition." |
| MG4-05 | NOTE | C2_Control.md:255-256, 891 | n = (3 x 3.2/0.25)^2 = 1,475 uses the rounded s.d. 3.2; with sigma sqrt(10) = 3.162 it is 1,440. | REV_G4_control_check_out.txt | "about 1,450 fills". |
| MG4-06 | NOTE | C2_Control.md:892 | "~800-900 fills if true share is 0.05 above threshold": 794 is for 0.049 above the ES threshold; 914 is for 0.007 above the MES threshold (0.995 vs 0.988). | C2_gaowang_out.txt; recomputed | "~800 fills (ES, true share 0.70 vs 0.651) or ~900 (MES, 0.995 vs 0.988)". |
| MG4-07 | NOTE | C2_Control.md:179, 73, 1016, 1018, 1034 | Several quotes presented as verbatim are transliterated (Λ -> Lambda, α -> alpha, γ -> gamma) or layout-joined; the evidence-table header says Greek letters are "as extracted", but the quote at line 179 ("where A = Lambda/alpha and k = alpha K") transliterates silently; the source reads "where A = Λ/α and k = αK". | avellaneda_stoikov_2008.txt 276; cartea_jaimungal_ricci 597; CDJ 168-171; HLR 331-333 | Mark transliterated quotes "(Greek transliterated)" or quote the extracted glyphs. |
| MG4-08 | NOTE | C2_Control.md:130 | The Ho-Stoll order-flow line "dq^a = 1{a market buy arrives} Q lambda^a dt" reproduces the review's notation, which mixes an indicator with a rate x dt and is not a well-formed SDE; a reader may take it as Ho-Stoll's equation. | multiple_dealers_2015_review.txt 153-158 | Add "(the review's notation; read: dq^a jumps by Q at the arrivals of a Poisson process of rate lambda^a)". |
| MG4-09 | NOTE | C2_Control.md:319 | "Proposition 3 and the display at lines 612-630": the saved text at 612 says only "From the above proposition"; the proposition number was not verified by me and is not visible in the cited lines. | gueant_lehalle_ft_2013.txt 608-632 | Cite the display lines only, or verify the proposition number. |

Counts: BLOCKING 0, SHOULD FIX 4, NOTE 5.

### 1.4 Quote check (C2_Control.md)

REV_G4_quotecheck.py extracted 106 double-quoted strings of >= 18 characters; 83 matched a saved .txt strictly (lower-case, ligatures, quote glyphs, hyphenation, whitespace), 3 loosely (letters and digits only), 20 flagged. Of the 20: 14 are not source quotes (text between two unrelated quote marks on one line: md 82, 132, 209, 481, 623, 731, 789; the reader's own labels in quotes: 74, 145, 169 x2, 574, 766; a reference title: 973). The 6 genuine quotes flagged were each checked by hand and found in the cited file: md 179 (Greek transliterated; source 276), 705 (source 581, with "−" and "×"), 784 (source 1629-1632, page break inside the quote), 1005 (source 391-394, "T ." in the extraction), 1018 (layout-joined, flagged by the reader), 1034 (layout-joined). Result: 92 of 92 genuine quotes present in the cited files; 0 fabricated; 0 misattributed to the wrong file. Cited line numbers are within 1-2 lines of the source throughout. Every claim I checked says no more than its quote, with one misattribution of table numbers (MG4-03). [unverified] marks are present where full text was not read (Ho-Stoll original, the two books, journal venues, MES spread distribution, fill counts). Note: the reader's evidence table marks the Falces Marin mean row "l.1230"; it is at 1229 in the saved text (within tolerance).

### 1.5 Judgment

The mathematics of C2_Control.md is sound. Every equation I checked (A-S frozen-inventory and approximate quotes, the CARA first-order condition, GLFT's ODE system and asymptotics, Gueant 2017's general Hamiltonian equation, CDJ's comparison rule, Almgren-Chriss's discrete solution, Gao-Wang's conditional profit) matches its saved source, the symbols are defined, and the two re-derivations I did by hand (the FOC and the GLFT root term) agree. The worked examples reproduce to the printed precision. The one computational error (MG4-01) is in a supporting script: the threshold gammas at which a 1-lot policy would step behind the touch are taken from the large-Q approximation, with a sigma-squared bug for sigma = 0.5, while the text applies them to Q = 1-3; the qualitative claim (the continuous family collapses to touch-or-not plus a cap at realistic gamma) survives because the exact flat quotes at gamma = 0.01 are 0.75-0.91 tick for Q = 1-3 and still round to the touch. The evidence handling is careful: quotes are genuine, the negative results (Falces Marin, CDJ zero-intelligence, hftbacktest breakeven) are reported with their numbers, and the section's verdicts (skip A-S as a strategy, maybe GLFT as a cap, maybe CDJ, use the Gao-Wang criterion) follow from the evidence shown. The one recommendation I would not let stand as written is the H-GW1-first ordering logic (MG4-04): an unconditional benign-share failure does not rule out the imbalance-gated policy, which is the only edge mechanism the section identifies.

## Part 2. C2_StatsRMT.md

Checked 2026-10-21 11:20-12:25 PDT. Scripts: work/REV_G4/REV_G4_statsrmt_check.py (output REV_G4_statsrmt_check_out.txt; own
implementations of every estimator, own seed 4242), work/REV_G4/REV_G4_quotecheck.py (output REV_G4_qc_StatsRMT.tsv). The
reader's C2_StatsRMT_examples.py was read in full and its JSON output compared line by line with the text; it was not run.

### 2.1 Equations and derivations checked against the saved sources

| Item | Result | Source checked |
|---|---|---|
| 0: E[max SR] = sqrt(V)[(1-g) PhiInv(1-1/N) + g PhiInv(1-1/(Ne))]; DSR = Phi((SR-SR0) sqrt(T-1)/sqrt(1 - skew SR + (kurt-1)/4 SR^2)) | correct; identical to the program's funnel/multiple_comparisons.py expected_max_sharpe and deflated_sharpe_ratio, and to BLdP eqs (1)-(2) (mangled in extraction, structure visible) | bailey_lopezdeprado_2014_dsr.txt 313-320, 360-374; funnel/multiple_comparisons.py |
| 0: quote of screening/stage_e_verdict.py docstring | exact | screening/stage_e_verdict.py:218 |
| 1: MP density and edges, Laloux Q = T/N form, (1 +- sqrt q)^2 = 1 + q +- 2 sqrt q | correct | laloux_1999_noise_dressing.txt 51-57 (eq. 3, mangled as the reader says) |
| 1: clipping eq. 7.55, lambda_+ quote with lost sqrt, TrE^-1 = TrC^-1/(1-q) | correct | bun_bouchaud_potters_2017_cleaning.txt 5481-5500, 273 |
| 1: N_hat = rho_bar + (1 - rho_bar) M restated from BLdP eq. 9 | consistent with the paper's stated limits (rho_bar -> 1 gives 1, rho_bar -> 0 gives M); eq. 9 itself is mangled | bailey_lopezdeprado_2014_dsr.txt 623-661 |
| 2: RIE eq. 6.5 xi(lambda) = lambda / |1 - q + q lambda lim g_E(lambda - i eta)|^2; eta = N^-1/2 from Bun's figure caption | correct | bun 4236-4243, 3086 |
| 3: LW 2004 rho* = beta^2/delta^2, Sigma* = (beta^2/delta^2) mu I + (alpha^2/delta^2) S; bona fide m, d^2, b_bar^2, b^2, a^2 | correct (standard; quoted FOC checked) | ledoit_wolf_2004_jmva.txt (quote matched) |
| 4: LW 2020 eq. 3.6 d_i = lambda_i/([pi c lambda_i f]^2 + [1 - c - pi c lambda_i Hf]^2); eq. 4.9 bandwidth | correct | ledoit_wolf_analytical_nls.txt 547-553, 770 |
| 5: James-Stein (1 - (K-2)/sum z^2) z (Efron eq. 3.9); grand-mean positive-part with K-3 | correct; Efron 3.7-3.9 quotes present; grand-mean version properly [unverified] | efron_2011_tweedie.txt 497-508 |
| 6: kappa = tau^2/(tau^2 + sigma^2/T), Var = kappa sigma^2/T (JKP eqs 4-6); Tweedie E[mu|z] = z + s^2 l'(z) | correct | jensen_kelly_pedersen_2021_replication.txt 448-469; efron 116 |
| 7: two-level normal model, kappa_b, kappa_w | equations correct; the worked example's tau_b estimator is inconsistent with the stated prior mean (MG4-10) | - |
| 8: BMA eqs 1-3, BIC approximation with the lost 1/2, weights exp(-BIC/2) | correct | hoeting_1999_bma.txt (quotes matched) |
| 9: block entropies, entropy rate, Markov-chain rate, Miller-Madow (occupied cells - 1)/(2n) nats | correct as equations; the application to the rate at k = 4 is overstated (MG4-11) | shannon_1948.txt (Thm 2); schreiber eq. 3 |
| 10: H_lz = n log2 n / sum Lambda_i; Lambda_i definition | correct (Fiedor eq. 5, mangled) | fiedor_2014_frequency_predictability.txt 109 |
| 11: Phi^m, ApEn = Phi^m - Phi^{m+1}, SampEn = -log(B/A) | correct; reader's code uses N-m templates for both Phi^m and Phi^{m+1} (common variant; immaterial) | delgado_bonal_2019_apen_sampen.txt |
| 12: KSG estimator 1 psi(k) - <psi(nx+1) + psi(ny+1)> + psi(N); Gaussian MI -(1/2) ln(1 - rho^2) | correct | kraskov_2004_mi.txt eq. 8 |
| 13: TE eq. 4; 2 T TE -> chi^2(nu), nu = (nA - 1) nA^k (nB^l - 1) (= 12 for 3 symbols, 2 for binary); TE = Granger/2 for Gaussians | correct; the reader's reading of the mangled nu line is the standard conditional-independence df | te_leadlag_pvalues_2022.txt (nu line, mangled); barnett_2009_granger_te.txt eq. 13 |

### 2.2 Worked examples recomputed (REV_G4_statsrmt_check_out.txt; reader's values in brackets)

- A: MP edges for the four settings: 0.1963/2.4240, 0.6207/1.4693, 0.1183/2.7425, 0.9910/1.0090 [all match].
- B (effective trials, own MC, 300 reps, own seed): true top eigenvalues 40.4, 20.4 x 4 [match]; MC mean max SR 0.0835 [0.0849]; formula with N = M +7.0% [+7.6%]; implied N 117 [112]; MP count 5 [5]; entropy rank 37.2 [37.4]; participation 11.8 [11.9]; rho_bar 0.202 [0.198]; N_hat 159.9 [160.7]; benchmark with each estimate 0.0385/0.0698/0.0535/0.0869 [0.0394/0.0714/0.0549/0.0890]. Same ordering and conclusions; differences are Monte Carlo noise. Side result: the BLdP approximation itself overstates the exact expected maximum of 200 iid normals by 0.7% (2.7655 vs 2.7460), so of the reader's +7.6% about 0.7 points is the formula and the rest is correlation.
- C (cleaning race, own code and own random rotation, 40 reps): sample 1.953 [1.967, theory (n-1)/(n-p-1) = 2.01], clip 1.192 [1.283], LW linear 1.208 [1.228], RIE 1.162 [1.181], NLS 1.098 [1.127]. Sample > {clip, LW} > RIE > NLS reproduced; the clip-vs-LW order swapped (MG4-13).
- D: zbar 0.0083, S 10.869; T = 84: B = 1, tau^2 = 0, E[max] 2.8835; T = 1000: B = 0.2087, JS winner 1.5053, tau^2 = 0.7361, kappa 0.7450, EB winner 1.4176, E[max] 0.8357; PhiInv values 1.3830 and 1.8712 [all match].
- D2 (two-level): within SS 0.0457, /9 = 0.0051 < 0.0064, tau_w^2 = 0; family means 0.2000/-0.0125/-0.1675; reader's tau_b^2 = 0.0324, kappa_b = 0.953, posteriors 0.1906/-0.0119/-0.1596 [match]. Under the stated prior-mean-0 model: tau_b^2 = 0.0211, kappa_b = 0.930, posteriors 0.1859/-0.0116/-0.1557 (MG4-10).
- E: dBIC 3.069 and 7.601, weights 0.174/0.808/0.018, BMA beta -0.1606 [match].
- F: iid H 0.9219; stationary (0.1053, 0.7895, 0.1053); marginal 0.9530; rate 0.9366; gap 0.0164 [match]. Own draws: n = 2,000 block k = 4 0.895 (bias 0.042), n = 20,000 0.938 [reader 0.917 and 0.932]; LZ 0.891 and 0.910 [0.929, 0.893]; 3^9 = 19,683 [match]. Theoretical SampEn of iid Gaussian at r = 0.2 sd is 2.185, consistent with the reader's 2.17-2.19.
- G: nu = 12; null E[TE] = 0.000300 at n = 20,000; power sample sizes 48,174/4,818/482 and 86,680/8,668/867; Gaussian MI 0.04716 [all match].
- H: 1,766 / 3,092 / 3,842 fills (z_a = 1.960, 2.865, 3.291); I1 two-sample 3,532 per tercile; cloud 3.56/7.16/7.96 [all match].

### 2.3 Findings

| ID | Severity | Location | What is wrong | Evidence | Proposed fix |
|---|---|---|---|---|---|
| MG4-10 | SHOULD FIX | C2_StatsRMT.md:508-514, 526-533; work/C2_StatsRMT/C2_StatsRMT_examples.py part_d (two-level block) | The stated model has theta_i ~ N(0, tau_b^2) and shrinks family means toward 0, but tau_b^2 is estimated as the sample variance of the three family means about their own grand mean (ddof = 1), which is the moment estimator for a model with an unknown prior mean. The computation mixes two models. | REV_G4_statsrmt_check_out.txt D2: prior-mean-0 moment estimator mean(zbar_i^2) - s^2/J = 0.0211, kappa_b = 0.930, posteriors 0.186/-0.012/-0.156; grand-mean-centred version 0.191/-0.012/-0.159. | Either write the model with an estimated prior mean and shrink toward 0.0067 ("Posteriors: 0.191 for all of A, -0.012 for B, -0.159 for C"), or keep prior mean 0 and use tau_b^2 = 0.0211, kappa_b = 0.930, posteriors 0.186 / -0.012 / -0.156. The 0.30 -> 0.19 message survives either way. |
| MG4-11 | SHOULD FIX | C2_StatsRMT.md:651-652 | "The Miller-Madow k = 4 bias scale (3^5 - 1)/(2n ln 2) is 0.087 bits at n = 2,000 [...] at n = 2,000 the bias is five times the effect." That expression is the first-order bias of the single block entropy H_5; the rate h_4 = H_5 - H_4 has a first-order bias of about (3^5 - 3^4)/(2n ln 2) = 0.058 bits (all cells occupied), and the realized bias in the reader's own run is 0.937 - 0.917 = 0.020 bits, 1.3 times the 0.016-bit effect (0.042 in my draw). "Five times" is not supported by the measurement the sentence sits beside. | reader's JSON F_entropy.estimates["2000"].block_rate_k4 = 0.9169; REV_G4 output F | "The plug-in rate at k = 4 is biased low by 0.020 bits at n = 2,000 in this run (0.005 at 20,000), the same size as the 0.016-bit effect; the first-order bias scale for the rate is (3^5 - 3^4)/(2n ln 2) = 0.058 bits at n = 2,000." |
| MG4-12 | NOTE | C2_StatsRMT.md:215-221, 269, 277, 311, 899 | Timings printed in the text (clip 1.3, LW 3.2, RIE 1.3, NLS 1.5 ms) differ from the saved JSON (1.16, 3.01, 1.18, 1.41 ms); the other "measured" numbers all come from that JSON. | C2_StatsRMT_examples.json C_cleaning_race.ms_per_estimate | Quote the JSON values, or write "about 1 to 3 ms". |
| MG4-13 | NOTE | C2_StatsRMT.md:215-226 | The race uses one random rotation of the population basis; the clip-vs-LW-linear order is not stable across rotations (reader: clip 1.283 > LW 1.228; my rotation: clip 1.192 < LW 1.208), while sample > {clip, LW} > RIE > NLS held. The text draws no conclusion from that pair, but the table invites one. | REV_G4 output C | Add "(one rotation of the population basis; clipping and LW linear swap places across rotations)". |
| MG4-14 | NOTE | C2_StatsRMT.md:673 | "The measured gap is 0.02 to 0.10 bits out of 2": from the quoted estimates (2.04, 1.92, 2.00, 1.90) the gaps to the maximum of 2 are -0.04, 0.08, 0.00 and 0.10; 0.02 is a daily-minus-intraday difference, not a gap. | Fiedor quote at 670-673 | "The measured gaps are 0 to 0.10 bits out of 2, and one estimate exceeds the maximum". |
| MG4-15 | NOTE | C2_StatsRMT.md:38 | "Bailey and López de Prado 2014, eq. 2 and Appendix" for E[max SR]: the formula is the paper's eq. (1); eq. (2) is the DSR, whose "where" clause restates it. (The program code's docstring calls it eq. (3).) | bailey_lopezdeprado_2014_dsr.txt 313-320, 360-374 | "eq. 1 (restated under eq. 2) and Appendix 1". |
| MG4-16 | NOTE | C2_StatsRMT.md:486-487, 1146-1147 | The saved Chen-Dim text contains 1,602 NUL bytes, so a plain grep prints "Binary file matches" and no lines. The claim stands in substance: a text search finds 4 "cost" hits, three accounting variable names and one reference title ("Information Costs"). | python search of chen_dim_high_throughput.txt (REV_G4 session) | "a text search (grep -a) for 'cost' finds only accounting variable names and one reference title". |
| MG4-17 | NOTE | C2_StatsRMT.md:961 | Verdict row says Lempel-Ziv is "highly correlated with plug-in and CTW estimates (Fiedor)". Fiedor's quote covers LZ and CTW only; the plug-in comparison is the reader's own worked example (where LZ was 3% low while the block estimator was within 0.001 at n = 200,000). | fiedor quote (line 717-718 of the md); section 10 (5) | "highly correlated with CTW (Fiedor); in the worked example it is biased low where the block estimator is not". |
| MG4-18 | NOTE | C2_StatsRMT.md:141, 151 | The "+7.6%" overstatement attributed to counting correlated trials includes the BLdP formula's own approximation error for independent trials: E[max of 200 iid N(0,1)] is 2.7460 exactly against 2.7655 from the formula (+0.7%). | REV_G4 output A | "about 7% here, of which 0.7 points is the formula's asymptotic approximation and the rest is the correlation". |

Counts: BLOCKING 0, SHOULD FIX 2, NOTE 7.

### 2.4 Quote check (C2_StatsRMT.md)

REV_G4_quotecheck.py extracted 94 double-quoted strings of >= 18 characters; 72 matched strictly, 3 loosely, 19 flagged. Of the 19: 6 are text between unrelated quote marks (md 52, 57, 119, 279, 301, 485); 6 are the reader's own labels or hypothesis names (66 x2, 406 x2, 655, 862); 2 are the program docstring (37, 1079), verified exact against screening/stage_e_verdict.py:218; 1 is the transcription of Laloux's mangled eq. 3 (91), verified at laloux_1999_noise_dressing.txt 54-55; 3 are the Ledoit-Péché attributions (224, 225, 1092), verified at bun_bouchaud_potters_2017_cleaning.txt 4236 ("the final Ledoit-Péché formula") and ledoit_wolf_analytical_nls.txt 468-469 ("first discovered by Ledoit and Péché (2011, Theo-/rem 3)", hyphenated); 1 is the Pincus abstract (741), verified in pincus_1991_apen_pmc.html.txt ("can classify complex systems, given at least 1000 data values"). Twelve further rows were flagged "cited-file-MISMATCH" only because the match was in the .raw.txt reading-order copy of the same source; the reader's evidence-table header says both copies were searched. The Chen-Dim quotes (29-31 of the evidence table) were verified by a Python search because the file has NUL bytes. Result: 82 of 82 genuine quotes present in the cited source; 0 fabricated; 0 attributed to the wrong paper. The reader's own evidence check ("58 rows, 0 failures") is consistent with mine. Claims stay within their quotes; the [unverified] and (vp) marks cover James-Stein 1961, Miller 1955, Lempel-Ziv 1976/77, Kontoyiannis 1998, Ledoit-Péché 2011, the Pincus full text, the Avramov draft's provenance and all journal volume/page numbers. Cited numbers (Fiedor's 2.04/1.92/2.00/1.90, Chen-Dim's 5.7%, RunPod and Lambda prices, CDJ-style table values) match the saved text.

### 2.5 Judgment

The mathematics of C2_StatsRMT.md is correct and unusually well tied to the program's own code: the DSR and expected-maximum formulas are the ones in funnel/multiple_comparisons.py, and the Marchenko-Pastur, RIE, Ledoit-Wolf, James-Stein, Tweedie, BMA, entropy, KSG and transfer-entropy equations all match their saved sources with symbols defined and extraction damage flagged. The reader's script implements each estimator correctly (I checked the RIE complex shift, the LW 2020 kernel and Hilbert transform, the Kontoyiannis matching rule, the KSG strict-inequality counts and the chi-square degrees of freedom), and my own implementations with a different seed reproduce every headline number: the effective-N ordering (MP count far too low, N_hat closest, N = M mildly conservative), the shrinkage race ordering apart from one draw-dependent pair, the James-Stein and empirical-Bayes figures to four decimals, the entropy-rate values, the TE power table and the fill counts. The two items worth fixing are a model-versus-computation mismatch in the two-level example (shrinking toward 0 while estimating the between-family variance about the grand mean; third-decimal effect) and an overstated bias claim for the k = 4 entropy rate that the reader's own measurement contradicts. The evidence is handled carefully: all 82 genuine quotes are present, negative and gross-of-cost results are stated as such, and the verdicts (RMT skip for the pilot, empirical Bayes use, hierarchical and BMA maybe with frozen structure, entropy as one feature, TE leaning use) follow from the evidence shown; the repeated line that every pooled or averaged configuration still counts into N is consistent with V43. No finding changes a verdict or a recommendation.

## Part 3. Quote-check method and raw results

(pending)
