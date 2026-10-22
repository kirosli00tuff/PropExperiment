# R_math_G2: adversarial math and evidence review, group G2 (Fable 5.1, xhigh)

Reviewer: MathReviewer-FableXHigh. Stage E.28. Started (this run) 2026-10-21 PDT; an earlier
run was cut by a usage limit after writing only work/REV_G2/REV_G2_quotecheck.py and
REV_G2_quotes_hawkes.tsv (no findings on disk). This file is written incrementally.

Files under review:
- reports/stage_e28_briefs/C2_Hawkes.md (deep dive; sources under pages/C2_Hawkes/, scripts under work/C2_Hawkes/)
- reports/stage_e28_briefs/work/lead/C0_front.md
- reports/stage_e28_briefs/C3_lead_draft.md
- reports/stage_e28_briefs/C4_lead_draft.md

Scripts and check outputs: reports/stage_e28_briefs/work/REV_G2/

Severity: BLOCKING (wrong equation or derivation, wrong number that changes a verdict, fabricated or
misattributed quote, evidence claim the source does not support); SHOULD FIX (error or ambiguity that
would mislead a careful reader, missing [unverified], wrong number that does not change a verdict);
NOTE (clarity, style).

Status: DONE 2026-10-21 10:37 PDT. Holdout at end: unlocks_logged 0, all_ok true; REGISTRATION.md 0 bytes;
no reviewed file edited; no commits; no new fetches.

Method. (1) Every worked example and formula in C2_Hawkes.md was recomputed in
work/REV_G2/REV_G2_math_checks.py (scipy, sympy, numpy; output REV_G2_math_checks.out): 84 numeric
checks, 84 pass, 0 fail. Derivations re-done symbolically: the Poisson SE, the kernel integrals, the
tau_k closed form against direct integration, the Engle-Russell variance 8, the 9a ODE, the long-run
variance of N1 - N2 in the Bacry et al. (2013) model via (I - G)^-1 diag(Lambda) (I - G)^-T, and an
exact finite-window variance for the exponential Hawkes process to test the simulation output. (2) The
reader's scripts C2_bench.py and C2_multi.py were read line by line (recursion, compensator, Ogata
thinning, rescaled increments, the shared-beta D-dimensional recursion) and the section 6 "spurious
criticality" experiment was replicated with my own code and seeds (REV_G2_spurious_check.py, .out).
(3) Every double-quoted span of 20 or more characters was extracted with sequential quote pairing
(REV_G2_quotecheck2.py; the cut run's regex paired a closing quote with the next opening quote and
produced false misses) and searched in the saved .txt files after normalising whitespace, hyphenation,
ligatures and typographic punctuation; the misses were checked by hand against the cited line ranges.
(4) Paraphrased claims (data sets, years, dimensions, equation numbers) were grepped in the saved files.
(5) The lead files' quotes were checked against the cited file and line with REV_G2_lead_quotes.py
(REV_G2_quotes_lead.tsv) and the attributions to C2 deep dives were grepped in those files.

---

## 1. reports/stage_e28_briefs/C2_Hawkes.md

### 1.1 Findings

| ID | severity | location | what is wrong | evidence | proposed fix |
|---|---|---|---|---|---|
| MG2-01 | SHOULD FIX | C2_Hawkes.md:148-150 and :1062 | "Lallouache and Challet (2016) found that intraday seasonality is what stops a single Hawkes fit from covering a day" rests on BMM's secondary summary and contradicts LC's own text, which the deep dive itself quotes at lines 576-583. | lallouache_challet_2016.txt lines 12-19 (abstract): "One can achieve statistical significance according to three simultaneous tests provided that one uses kernels with two exponentials for fitting an hour at a time, and two or three exponentials for full days, while longer periods could not be fitted"; lines 903-904: "Hawkes processes can indeed be fitted in a statistically significant way according to three tests to a whole day of data"; lines 922-923: fits "fail to pass the the LB test for two consecutive days". BMM line 1152 says "does not allow to fit well a whole day". | Line 148-150: "Lallouache and Challet (2016) could fit a whole day with two or three exponentials but not two consecutive days; they and BMM (2015) attribute the limit to intraday non-stationarity of the exogenous intensity (BMM summary, lines 1148-1152: '...'; LC lines 922-923)". Evidence-table row 1062 label: "Seasonality limits one kernel to about a day (BMM's reading: 'a whole day'; LC's own abstract: full days fit, longer periods do not)". |
| MG2-02 | SHOULD FIX | C2_Hawkes.md:210-212 | "Hardiman and Bouchaud 2014, their eq. (4) gives the integral of the correlation function as (1 - n)^{-2}" drops the factor Lambda. | hardiman_bouchaud_2014_branching.txt line 114 (eq. 4): the integral of the auto-covariance nu(t) equals Lambda / (1 - int phi)^2 ≡ Lambda / (1 - n)^2 (the file reads "Λ ... Λ / (1 − n)2"); the deep dive's conclusion Var/E -> 1/(1 - n)^2 follows after dividing by Lambda and is correct (checked: finite-window formula reproduces the simulated variances, REV_G2_math_checks.out rows "S3 theory Var"). | "their eq. (4) gives the integral of the autocovariance as Lambda / (1 - n)^2, so Var[N(W)] / E[N(W)] -> 1 / (1 - n)^2". |
| MG2-03 | SHOULD FIX | C2_Hawkes.md:379-380 and :943 (propagates to C3_lead_draft.md:76-77) | "a large share of the excitation acts faster than this program can react" and "much of the excitation is sub-millisecond (0.3 ms, BJM 2016)" quantify what the source does not. | arxiv_1412_7096.txt lines 1081-1087: "there are loosely two kinds of influences: Fast and localized influences, for which the volume of the kernel is localized around the reaction time of the market (on our data 0.3 milliseconds) and influences which are spread over a wide range of time scales"; lines 1091-1092: "Market orders have localized impacts while limit orders take time to have an impact". No share of total excitation mass is given anywhere in the saved text (grep for "most of the", "large part", "majority", "% of the", "norm" finds no such statement). | Line 379-380: "The 0.3 ms figure matters here: BJM find one of the two kinds of influence (the fast, localized kind, which is how market orders act) concentrated at about 0.3 ms, faster than this program can react; the other kind is spread over a wide range of time scales." Line 943: "part of the excitation is sub-millisecond (0.3 ms for the fast, localized influences, BJM 2016)". Rated SHOULD FIX, not BLOCKING, because no quantity enters a verdict: the "maybe" on high-dimensional Hawkes also rests on data needs, and C3/C4's latency conclusion also rests on C2_OFI and E.25. A strict reading of "an evidence claim the source does not support" would make it BLOCKING; the lead decides. |
| MG2-04 | SHOULD FIX | C2_Hawkes.md:930 (copied into C4_lead_draft.md:74) | "If all are run: 7 to 12 configurations added to N" does not match the table's own column. | Section 11 table: H-C2-0 0, H-C2-1 1, H-C2-2 3 or 6, H-C2-3 1 or 3, H-C2-4 1, H-C2-5 2. All six: 8 to 13. Without H-C2-4 (verdict "skip" in section 12): 7 to 12 (REV_G2_math_checks.out, rows "S11 configs"). | "If all six are run: 8 to 13 configurations added to N; without H-C2-4 (skip, section 12): 7 to 12; plus 1 for the kernel-family choice made on the first month." |
| MG2-05 | SHOULD FIX (missing [unverified]) | C2_Hawkes.md:871 | Learner failures are asserted "under Python 3.11, 3.12 and 3.13 with 0.8.0.2, and with 0.8.0.1", but the saved artifacts show only 3.11 (C2_bench_py311.log) and 3.12 (C2_bench_results.json key speed_tick_py312_errors); no saved output names Python 3.13 or tick 0.8.0.1. | `grep -l "3\.13\|cp313\|0\.8\.0\.1" work/C2_Hawkes/*` returns nothing; C2_bench.log and C2_bench_py311.log contain no version lines beyond the python3.11 site-packages path. The 3.11 and 3.12 failures are documented and I do not doubt the others, but they are not on disk. | Either save those two runs' tracebacks under work/C2_Hawkes/ or write "under Python 3.11 and 3.12 with 0.8.0.2 (logged); also seen under 3.13 and with 0.8.0.1 [unverified: not logged]". |
| MG2-06 | NOTE | C2_Hawkes.md:195-197 and :1049 | The Proposition 1 quote drops the index range from "{||φij ||}D i,j=1" without an ellipsis or bracket. | bacry_mastromatteo_muzy_2015.txt lines 186-187: "(H) The matrix ||Φ|| = {||φij ||}D / i,j=1 has spectral radius smaller than 1." | Quote as "{||φij ||} [D, i,j=1] has spectral radius smaller than 1" or add "(index range dropped)". |
| MG2-07 | NOTE | C2_Hawkes.md:295-296, :516-519, :535-537, :1075-1076 | Several quotes presented as verbatim were cleaned beyond the substitutions the text declares: BDHM eqs (6)-(7) show pdftotext's "Z t ... −∞" where the reader wrote "∫" without saying so; Brown's theorem reads "t 2 (0, T]. Dene the transformation L ( uk ) D Z uk" in the file (the reader restored ∈, Define, = and ∫ while declaring only l = lambda, L = Lambda); Brown's KS line reads "condence bounds" (the reader restored "confidence" while declaring only § -> ±). Meaning unchanged in every case. | bacry_delattre_hoffmann_muzy_2013.txt lines 263-268; brown_etal_2002_rescaling.txt lines 219-226 and 339-340. | Add "(symbols restored: ∫, ∈, =, 'fi' ligature)" at each quote, or quote the file's text. |
| MG2-08 | NOTE | C2_Hawkes.md:178 | "BMM Proposition 2, eq. (8), written there with mu = 0" attributes to BMM a choice they do not state. | bacry_mastromatteo_muzy_2015.txt lines 242-246: the proposition is stated for kernels "φij (t) = αij βeβt" (sign lost in extraction) with no assumption on µ; eq. (8) "dλt = −βλt dt + αβ dNt" simply omits the µ term. The reader's own form d lambda = -beta (lambda - mu) dt + n beta dN is the correct one (confirmed by the 9a ODE check). | "(BMM Proposition 2, eq. (8), which omits the µ term: 'dλt = −βλt dt + αβ dNt')". |
| MG2-09 | NOTE | C2_Hawkes.md:429-431 | The qualifier "when the decays are shared per source type" is more restrictive than needed. | With distinct beta_ij one keeps D^2 accumulators R_ij with lazy decay; the cost is O(N D^2) at worst, O(N D) with per-row updates, still linear in N. C2_multi.py implements the shared-beta case correctly (R vector decayed per event, D-vector dot product, column-sum compensator). The reader's conclusion that Martins-Hendricks' "does not translate to the multivariate case" (arxiv_1604_01824_multivar_signif.txt lines 623-626) is wrong stands. | "...show that it does; with distinct decays per pair the recursion keeps D^2 accumulators and stays linear in N." |
| MG2-10 | NOTE | C2_Hawkes.md:559-560 | "a Poisson process whose rate switches between 0.3 and 3.0 per s every 300 s" overstates the regularity of the simulation. | C2_bench.py lines 179-185: each 300 s segment draws its rate from {0.3, 3.0} with rng.choice, so consecutive segments may share a rate. The result itself is robust: my own code and three fresh seeds give n_hat 0.961-0.962, beta_hat 0.093-0.104, KS p 0.49-0.86, and the control (0.5, 0.6, 2.0) is recovered as (0.507, 0.602, 1.931) (REV_G2_spurious_check.out). | "whose rate is drawn afresh from {0.3, 3.0} per s for each 300 s segment". |
| MG2-11 | NOTE | C2_Hawkes.md:52-57 and :106-108 | Background claims stated as fact without a source or [unverified]: the CME index-futures intraday profile (06:30 PT open, near 13:00 PT, lunch, 08:30 ET releases, FOMC) and "CME data have many events in one matching-engine message". | No saved source covers either; the Databento quote covers only the timestamp definition. | Mark as "(background, reader's knowledge; the pilot will measure the profile)" or [unverified]. |
| MG2-12 | NOTE | C2_Hawkes.md:652 | "with W >= 100 it is right (0.80)" over-reads the agreement. | The exact finite-window value of the moment estimator for this exponential kernel is 0.7385 at W = 10 s, 0.7950 at W = 100 s and 0.7995 at W = 1000 s (REV_G2_math_checks.out, "S7 theory n_hat"); measured 0.743, 0.803, 0.795. The measured variances exceed theory by 4-9 % at W = 10 and 100 s (380.9 vs 365.6; 6481 vs 5950), consistent with sampling error of a variance from heavy-tailed counts. | "with W >= 100 it is within 0.01 of the truth (exact finite-window values 0.795 and 0.800)". |
| MG2-13 | NOTE | C2_Hawkes.md:948 | NPHC verdict reason "Built for large D (hundreds of nodes)": the saved text's experiments are 10- and 100-dimensional, not hundreds. | achab_etal_2017_nphc.txt lines 536-541: "a 10-dimensional process with power law kernels named PLaw10 and a 100-dimensional process with exponential kernels named Exp100 ... We extract the top 100 media sites". | "Built for and tested at d = 10 to 100 (MemeTracker top 100 sites); this program has D <= 8." The verdict "skip" is unchanged. |
| MG2-14 | NOTE | C2_Hawkes.md:313 | Line reference for the Toke-Yoshida ratio form points to lines 941-943; the quoted phrase "with some unobserved baseline intensity λ0,R (t)" is at line 951 of toke_yoshida_2020.txt (the equation is at 943-945). | grep. | Cite "lines 943-951". |
| MG2-15 | withdrawn | C2_Hawkes.md:1096 | (Checked: the 16 files of tick 0.8.0.2 carry upload_time 15:02:05 to 15:02:27; the reader quoted the last one. No defect.) | pypi_tick.json releases["0.8.0.2"][*].upload_time. | none |

Counts: BLOCKING 0, SHOULD FIX 5 (MG2-01 to MG2-05), NOTE 9 (MG2-06 to MG2-14), withdrawn 1.

### 1.2 What checked out (so the lead need not re-verify)

- Equations: the intensity definition, the point-process log-likelihood, the Poisson SE sqrt(M)/T, the
  exponential and regularised power-law kernel integrals (n and alpha/gamma), Lambda = mu/(1 - n) and
  its matrix form (I - ||Phi||)^-1 mu = (I + Psi_hat(0)) mu with BMM eq. (20) Psi_hat = (I - Phi_hat)^-1 - I
  (bacry_mastromatteo_muzy_2015.txt lines 427 and 437), the bivariate eigenvalues a_s ± a_c and BMM eq. (7)
  (line 231), ||Psi|| = (I - ||Phi||)^-1 - I, the O(N) recursion and compensator, the tau_k closed form
  (equal to direct integration to 1e-9), the Fano limit 1/(1 - n)^2, the 9a conditional-mean ODE (rate
  beta (1 - n), fixed point mu/(1 - n)), the Ljung-Box and Engle-Russell statistics (Var((X - 1)^2) = 8 for
  Exp(1)), the sample-size formula, BMM eq. (36) g_ij, eq. (66) G_ij, eqs. (72)-(73) contrast function, Thm 2
  eq. (38), eq. (17)-(18) Psi series, eq. (9)-(10) power-law stationarity alpha < gamma.
- The Bacry et al. (2013) signature plot: the deep dive's C(tau), Lambda = 2 mu / (1 - ||phi||),
  kappa = 1 / (1 + ||phi||), gamma = alpha + beta match Proposition 2.1 exactly (bacry_delattre_hoffmann_muzy_2013.txt
  lines 302-308), and C(inf) = Lambda kappa^2 was re-derived independently from the long-run covariance of a
  bivariate Hawkes process with cross-excitation only (0.390625 both ways); gamma = beta (1 + n) = alpha + beta.
- Worked examples: every number in sections 1, 2, 3(5a, 5b), 4(5a-c), 5(5), 6(5), 7(5), 8(5), 9a(5), 9b(7),
  11 agrees with recomputation (84/84). The simulated Hawkes count variances agree with the exact
  finite-window formula Var N(W) = Lambda W + 2 K [W/a - (1 - e^{-aW})/a^2], a = beta (1 - n),
  K = Lambda n (2 - n) beta / (2 (1 - n)): 4.75 vs 4.67 (1 s), 158.2 vs 156.7 (10 s), 1265.9 vs 1265.4 (60 s),
  which independently validates the Ogata-thinning simulator.
- Scripts: C2_bench.py (recursion, naive O(N^2) cross-check, compensator, rescaled increments with
  B_k = 1 + e^{-beta D_k} B_{k-1}, Ogata thinning with the correct upper bound and acceptance, logit/log
  reparametrised multi-start MLE) and C2_multi.py (shared-beta D-dimensional recursion, column-sum
  compensator) are correct; the "spurious" experiment reproduces with other seeds.
- Paraphrased facts verified in the saved files: BJM data (DAX and Bund front futures, June 2013 to June 2014,
  8-dimensional level-I model); Large via BMM (LSE Barclays, 1 s, 22 trading days of January 2002, 10-D);
  Martins-Hendricks JSE; Rambaldi-Bacry-Lillo Eurex (DAX, Bund); Lokin-Yu FX spot; Sfendourakis-Toke 36 Paris
  stocks 2015 with previous-day parameters; Toke-Yoshida next-day out-of-sample (lines 889-892) and Table 2
  (Hawkes global 0.503, MarkedRatio-14689-146-146 0.667); Lallouache-Challet EBS EUR/USD 2012; FS 2012 E-mini
  1998-2010; Kirchner CLS; Achab cumulant costs O(nd), O(nd^2), O(nd^3); HBB "m = 5 and M = 15" (two-column
  interleave, lines 198-199) and footnote 1 (plain pdftotext, as the reader said); Databento's four quotes;
  Lambda's two price rows; PyPI metadata for tick (0.8.0.2, 2026-05-04, cp311-cp314 incl. manylinux,
  numpy>=2.0, requires_python >=3.11; 0.7.0.1 2020-05-24 cp36-cp38; 0.8.0.0 2026-04-18 mac/win only),
  hawkeslib (0.2.2, 2019-06-18, cp36 wheel), hawkes (1.0.0, 2021-04-01, sdist), easy-tpp (0.3.0, 2026-07-13);
  Arroyo et al. contain 0 occurrences of "Hawkes".
- [unverified] marks are present where full text was not read: Lu-Abergel, Ogata 1978, Ozaki 1979,
  Shi-Cartlidge, arXiv 1710.01452, MES event counts, numba speed-up, tick speed claim, neural TPP on 4 GB.

### 1.3 Quote check

REV_G2_quotecheck2.py on C2_Hawkes.md against pages/C2_Hawkes/: 153 quoted spans of 20+ characters
(REV_G2_quotes_hawkes2.tsv). Matched automatically: 126 (84 WS exact, 25 WS in a file implied by the
text but not named in the same block, 3 NOWS, 8 SEG, 6 SEG*). Unmatched 27, resolved by hand:
6 are the reader's own wordings in quotes (hypothesis texts at lines 138, 350, 568, 697, 926; "who
triggers whom" at 269); 3 are tick error strings, verified in C2_bench_results.json; 18 are source
quotes that match the saved file apart from a page break, an equation label, a two-column interleave,
the arXiv sidebar or a pdftotext glyph (listed under MG2-06, MG2-07 and section 1.2). Quotes checked
153, matched 153 (126 by script, 27 by hand), fabricated 0, misattributed 0. Two blocks (lines 92-94)
have an odd number of quote marks because of an inch-style use; no quote is affected.

### 1.4 Pending items, resolved

MG2-05: no saved artefact names Python 3.13 or tick 0.8.0.1 (confirmed; raised to SHOULD FIX as a
missing [unverified]). MG2-13: Achab et al. test at d = 10 and d = 100 (reworded). MG2-15: withdrawn.

### 1.5 Judgment

The mathematics of C2_Hawkes.md is sound: every equation I could re-derive is correct with symbols
defined, every worked example recomputes, the two simulation scripts are correct implementations, and
the one result that feeds a lead-level recommendation (seasonality or regime shifts fitted as n ≈ 0.96
with a passing KS test) replicates with independent code and seeds. The evidence handling is careful
(verbatim quotes, declared glyph problems, [unverified] marks) with four substantive slips: a
secondary-source summary of Lallouache-Challet that the primary text contradicts (MG2-01), a dropped
factor Lambda in reporting HB 2014 eq. (4) (MG2-02), an unquantified "much" / "a large share" put on
BJM's 0.3 ms finding that then travels into C3 (MG2-03), and an arithmetic slip in the configuration
count that travels into C4 (MG2-04). None changes a verdict in section 12; the verdict table follows
from the evidence shown, and the "skip" and "maybe" rows are, if anything, conservative.

---

## 2. The lead's synthesis: work/lead/C0_front.md, C3_lead_draft.md, C4_lead_draft.md

### 2.1 Quote check

REV_G2_lead_quotes.py (REV_G2_quotes_lead.tsv): 24 quoted spans of 15+ characters with a file citation.
C3: 17 quotes, 17 found verbatim (WS) in the cited file; every cited line number confirmed by printing the
lines (progress.md:902-903, :626, :2094; E.20_RETURN.md:562-564; E.12_RETURN.md:683-685; E.21_RETURN.md:19-20
and :650; E.23_RETURN.md:678-679; E.11_RETURN.md:298; docs/DECISIONS.md:394-395 and :30-46 (D.1g, "181
purchased MBO days", trade-through and queue-position reasons); E.25_RETURN.md:25-26, :330, :332; C1_inventory.md
section 3 line 228; C2_OFI.md:1056; C2_SDE.md:536-538). C4: 7 quotes, 6 verbatim (C2_DeepLOB.md:985 and :975,
C2_OFI.md:1056, C2_AFML.md:1147, C2_Pooled.md:804, docs/DECISIONS.md:809 inside the 2026-10-18 V43 record at
:788), 1 not verbatim (MG2-20 below). C0 has no line-cited quotes; its five attributions were grepped.
Quotes checked 24, matched 23, missed 1 (a paraphrase inside quotation marks, right source).

Attributions to C2 deep dives checked by grep: C2_LOB section 13 exists (line 944) and carries the
queue-value identity "value = fill probability x (half-spread - adverse selection)" (955) and the markout
identity "S/2 - adverse move - fee" (959), which C0/C4 combine; C2_Control section 11 (867) and the negative
cost-inclusive Avellaneda-Stoikov test (274-278); C2_Control 4.5(c) exists (356); C2_OFI 13.1 "The first five
together add 5 to 11 trials" (1079), the Jaddu-Bilokon forward-test failure "because of processing delays"
(1019-1020), Stoikov-Waeber 5-year Treasury notes with 81 % of the imbalance signal kept at 100 ms (842-853),
"Trees add little over a linear model" (641); C2_DeepLOB section 12 "60k params, 8 to 34 h per configuration"
(969); C2_StatsRMT section 16 (948); C2_Firms sections 3.1 and 4 (344, 377); C2_Filter section 9 (851);
C2_AFML 6.5 CPCV table (666-672); C1 section 3 constraint table (193-228) and the 19-row never-used table
(152-190). C2_Hawkes attributions: all five (lose to "same as last", n = 0 fitted as 0.956, 0.71 s and 2.95 s,
USD 0.69 to 1.29, 7 to 12 configurations, 0.3 ms) are what C2_Hawkes says; two inherit C2_Hawkes defects.

### 2.2 Findings

| ID | severity | location | what is wrong | evidence | proposed fix |
|---|---|---|---|---|---|
| MG2-16 | SHOULD FIX | C3_lead_draft.md:8-9 | "Costs, statistical power and data granularity were the binding constraints, in that order of how often the returns name them" contradicts the counts C3 itself gives in item 1 and C1's tally. | C3:17-19 and C1_inventory.md:226-228: COST named in 5 returns (D.1b, D.1d, E.12, E.17, E.20), POWER in 7 (D.1, D.1e, E.13, E.14, E.21, E.23, E.25), GRAN in 3. By C1's full table (lines 202-224) COST appears in 7 rows and POWER in 9. On either count POWER is named more often than COST. (C1's own "Reading" sentence has the same slip; C3 repeats it.) The answer "No" does not depend on the order. | "Costs, statistical power and data granularity were the binding constraints: by C1's tally POWER is named in seven returns, COST in five and GRAN in three, and the cost gap is the one no estimator closes." |
| MG2-17 | SHOULD FIX | work/lead/C0_front.md:37-38 | "Every return names costs, statistical power or data granularity as the binding constraint" overstates C1's table. | C1_inventory.md:209 D.1g "PROP (fill rule and queue-position ban)"; :216 E.15 "ACCESS"; :219 E.19 "PROP economics"; also MT and BETA appear (213, 202). | "Every return names costs, statistical power, data granularity, prop-firm rules or data access as the binding constraint, and none names a missing method". |
| MG2-18 | SHOULD FIX | C3_lead_draft.md:76-77 | "much of the Hawkes excitation in futures order flow acts at about 0.3 ms (C2_Hawkes, after Bacry, Jaisson and Muzy 2016)" faithfully repeats C2_Hawkes:943, which overstates its source (MG2-03). | arxiv_1412_7096.txt lines 1081-1087 and 1091-1092: two kinds of influences, the fast localized kind at 0.3 ms (market-order impacts), the other spread over a wide range of time scales; no share quantified. | "part of the Hawkes excitation in futures order flow, the fast localized kind that market orders produce, acts at about 0.3 ms (C2_Hawkes, after Bacry, Jaisson and Muzy 2016)". C4:33 "C2_Hawkes: excitation at about 0.3 ms" needs no change. |
| MG2-19 | SHOULD FIX | C4_lead_draft.md:79 | "Combinatorial purged CV (for example 6 groups, 2 held out, 15 paths)": with N = 6 groups and k = 2 held out there are C(6,2) = 15 train/test splits but phi = (k/N) C(N,k) = 5 backtest paths. | C2_AFML.md:666-672, the reader's own table: "| 6 | 2 | 15 | 5 | 0.667 |" and "Each group is in C(5,1) = 5 of them, so phi = 5"; recomputed. PBO is computed over paths, so the wrong number would misstate the PBO sample. | "(for example 6 groups, 2 held out: 15 splits, 5 backtest paths)". |
| MG2-20 | SHOULD FIX | C4_lead_draft.md:45 | The quoted phrase "rest at the touch, cap the inventory" (C2_Control section 4.5c) is a paraphrase in quotation marks. | C2_Control.md:874: 'on a one-tick book they reduce to "touch, cap at Q" (section 4.5c)'; :895 "(touch, cap Q)". Right source, same meaning, not verbatim. | Quote "touch, cap at Q" or drop the quotation marks: reduces to resting at the touch with the inventory capped at Q. |
| MG2-21 | NOTE | C4_lead_draft.md:74 | "the Hawkes reader's add 7 to 12 (C2_Hawkes summary)" inherits MG2-04; all six Hawkes hypotheses add 8 to 13. The total "N = 538 + 20 to 40" still holds (OFI 5-11 + Hawkes 7-13 + a five-rung ladder over two horizons 10 = 22 to 34). | REV_G2_math_checks.out rows "S11 configs" and "C4 N". | "7 to 13". |
| MG2-22 | NOTE | C4_lead_draft.md:43 | "Without the seasonal baseline, Hawkes fits read seasonality as self-excitation (C2_Hawkes measured a true n = 0 fitted as 0.956)": the measured experiment is a regime-switching Poisson process (rate 0.3 or 3.0 per 300 s segment), which C2_Hawkes:939 describes as "seasonality and regime shifts". | C2_bench.py lines 177-187; C2_Hawkes.md:559-566. | "read seasonality or regime shifts as self-excitation". |
| MG2-23 | NOTE | C4_lead_draft.md:48 | "gaps of H + c tau": H, c and tau are not defined in C4 (they are C2_AFML's label horizon, a constant and the feature memory). | C4 defines no symbols. | "gaps of H + c tau (H the label horizon, tau the longest feature lookback, c a declared safety multiple; C2_AFML section 13)". |
| MG2-24 | NOTE | work/lead/C0_front.md:40-41 | "14 of the 19 listed topics, 5 more only in part": C1 states no such count; the 19-row table (C1:152-190) supports 14 + 5 only if "Bayesian methods and shrinkage" ("Bayesian: never used. Shrinkage: partly") is counted as never used and Ito, HMM, LOB labels, GBT-on-OFI and pooled models as "in part" (13 rows are "Never used" outright). | C1_inventory.md rows 154-190. | Add "(counting a row as 'in part' when C1 marks any component as used; 13 rows are never used outright)". |
| MG2-25 | NOTE | C3_lead_draft.md:69 | "Two honest limits, both already on the record:" is followed by three bullets (latency, fees, venue fill rule). | C3:70-88. | "Three honest limits, all already on the record:". |
| MG2-26 | NOTE | C3_lead_draft.md:19 | "PROP and ACCESS appear in D.1g, E.15, E.19 and E.21" omits E.13 (POWER, PROP, ACCESS) and E.25 (PROP, fill rule) from C1's table. | C1_inventory.md:214, :224. | Add E.13 and E.25, or write "for example". |

Counts: BLOCKING 0, SHOULD FIX 5 (MG2-16 to MG2-20), NOTE 6 (MG2-21 to MG2-26).

### 2.3 Do C3's answer and C4's design follow from the evidence?

C3. The answer "No" follows: C1's table (verified against the cited returns) names cost, power,
granularity, prop rules and access and never a method; the four quoted cost and power facts are
verbatim and the arithmetic (0.1 vs 2.1 ticks; NG h60 t 2.51 under 3.0; $1.25 - $1.22 = $0.03 per
round turn, 0.012 tick per fill, -$0.095 at 0.05 tick adverse selection) recomputes. Two sentences
overstate: the "in that order of how often" ordering (MG2-16) and "much of the Hawkes excitation"
(MG2-18). C3's claim that an OU fit on bar closes is an AR(1) rule is correct (a discretely sampled
OU process is AR(1)). Nothing in C3 overstates what the deep dives show about latency once MG2-18 is
reworded, because the latency limit also rests on C2_OFI's 10 ms and 100 ms evidence and on E.25.

C4. The method set and the phased plan follow from the verdict tables they cite, as far as I checked
them (C2_Hawkes in full; the others by their cited verdict lines). The one wrong number is the CPCV
path count (MG2-19), which matters because PBO is computed over paths. The design's statements that
deep dives "agree" are supported for C2_Hawkes (section 12 says measurement and simulation tools, not
alpha) and by the grepped verdict lines of C2_DeepLOB, C2_Control, C2_OFI and C2_LOB. C4's N arithmetic
("538 + 20 to 40") holds under either Hawkes count. C4 is a design draft and says so; it freezes nothing.

---

## 3. Summary

Files checked: C2_Hawkes.md (1,127 lines), C0_front.md, C3_lead_draft.md, C4_lead_draft.md. Findings
26 (one withdrawn): BLOCKING 0, SHOULD FIX 10 (MG2-01 to MG2-05 in C2_Hawkes; MG2-16 to MG2-20 in the
lead files), NOTE 15. Numeric checks 84/84 pass; the spurious-criticality experiment replicates with
independent code. Quotes: C2_Hawkes 153 checked, 153 matched (126 by script, 27 by hand), 0 fabricated
or misattributed; lead files 24 checked, 23 matched, 1 paraphrase in quotation marks. No verdict or
recommendation in any of the four files changes; the fixes are wording, one dropped factor Lambda in an
equation attribution, one configuration count, one CPCV path count and one missing [unverified].

Not done: I did not re-run the reader's C2_bench.py or C2_multi.py (they write into the reader's results
files); I verified them by reading the code, by an exact finite-window variance formula and by my own
replication of the spurious fit. I did not fetch any new source (0 of the 15-search budget used): every
claim had a saved file or an [unverified] mark except the items in MG2-05 and MG2-11. I checked the
other ten C2 deep dives only at the lines C3 and C4 cite, not in full (those files belong to other
reviewers). BMM's printed eq. (64) could not be read unambiguously from the extracted text (the exponent
on V[N_T]/E[N_T] appears as 1/2 where -1/2 is meant); the deep dive's form n ≈ 1 - sqrt(E/Var) is the
correct one and matches HB 2014 eq. (4), so no finding was raised.

Scripts and outputs: work/REV_G2/REV_G2_quotecheck2.py, REV_G2_quotes_hawkes2.tsv, REV_G2_math_checks.py,
REV_G2_math_checks.out, REV_G2_spurious_check.py, REV_G2_spurious_check.out, REV_G2_lead_quotes.py,
REV_G2_quotes_lead.tsv (plus the cut run's REV_G2_quotecheck.py and REV_G2_quotes_hawkes.tsv, superseded).

Status: DONE.

