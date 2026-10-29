# E.34 P10 compute-stop reference R_ZL (ComputeRef-OpusHigh)

Written 2026-10-29 14:05-14:15 PDT (Opus 5.5, high). This is arithmetic on E.33's recorded wall times only. No market
data, log, statistic or selection output was opened. Script: work/ComputeRef-OpusHigh/ref_zl.py (sha256 57de4f8b...),
run at nice 10 with `python3 -I`; output work/ComputeRef-OpusHigh/ref_zl.json (sha256 6041900a...). The input
reports/stage_e33c_briefs/ref_v03.json was read whole (3 KB, times only). Every value below is a guess range for the
protocol, as prompt Part P allows. No probe was run: E.34 forbids a real-data probe and E.33b D3 forbids a
synthetic-only one. The lead chooses which value becomes the frozen R_ZL.

## 1. E.33's measured components

| component | value | source (file:key or line) |
|---|---|---|
| builder probe, 3 dates | 3.65, 5.41, 5.66 s (mean 4.907 s) | ref_v03.json:builder_probe_s |
| projected build B = 796 x 4.907 / P_b | 976.43 s | ref_v03.json:B_s |
| **measured** feature build (two runs, first to last DONE) | 2,387.0 s = 2.445 x B | ref_v03.json:measured_at_0.2_stop_s.build_s; E.33b_RETURN.md:112 |
| S5 LOGIT (59 features), 216 folds, all measured | 23,602.7 s, mean 109.27 s a fold (max 654.2 s) | ref_v03.json:per_set_model."S5 LOGIT"; E.33b_RETURN.md:113 |
| S5 LGBM, 144 folds, all measured | 721.8 s, mean 5.01 s | ref_v03.json:per_set_model."S5 LGBM" |
| S1 LOGIT (23 features), 56 folds measured (FH15 and part of FH30) | 2,124.0 s (37.9 s mean); same cells in S5 4,311.3 s | ref_v03.json:rho_sums_s.LOGIT |
| S1 LGBM, 24 folds measured (FH15) | 48.9 s; same cells in S5 69.1 s | ref_v03.json:rho_sums_s.LGBM |
| rho (S1 / S5, same label-grid-fold cells) | LOGIT 0.492659, LGBM 0.707670 | ref_v03.json:rho |
| S1-S4 totals, measured plus projected at t_S5 x rho x n/23 | S1 LOGIT 11,628.1, S2 13,144.8, S3 13,650.4, S4 14,155.9 s; LGBM 510.8, 577.4, 599.6, 621.8 s | ref_v03.json:per_set_model |
| sum of fold seconds, all 1,800 folds | LOGIT 76,181.8 s; LGBM 3,031.5 s | ref_v03.json:sum_fold_s |
| parallel divisors | P_b 4 (builder), P_L 8 (single-thread LOGIT processes), P_G 2 (LGBM, 2 x 4 threads) | project_ref_v03.py:21; protocol_v0.3.diff P5 hunk; E.32 protocol P5 lines 550-552 |
| R_0.3 = B + 76,181.8/8 + 3,031.5/2 | 12,014.9 s; 3x 36,044.7 s | ref_v03.json:R_0.3_s, stop_at_s |
| measured fits (net of pauses) | 4,387.8 + 7,272.6 = 11,660.4 s against 11,038.5 projected: **eta = 1.056** | ref_v03.json:measured_at_0.2_stop_s.fits_net_s; E.33c_RETURN.md:107-109 |
| measured total under 0.3 | 14,047.4 s = 1.17 x R_0.3. Of the 2,032.5 s excess, 1,410.6 s is the build (2,387 against 976) and 621.9 s the fits | E.33c_RETURN.md:107-108 |
| earlier reference, set from a synthetic probe (0.2) | 2,255.8 s. The real fits ran 5.3x above it, and the search stopped after 440 of 1,800 folds | E.33b_RETURN.md:111; protocol_v0.3.diff P5 hunk |
| lowest MemAvailable during E.33's resumed search (8 LOGIT processes, sets of 23-28 features) | 6,311 MB | E.33c_RETURN.md:287-288 |

Two lessons from E.33 carry into the design. (i) A synthetic fold-time probe underestimated the real fits by 5.3x.
(ii) A probe of the builder on 3 dates underestimated the measured build by 2.4x. A projection anchored on real fold
times held well: the resumed part ran at 0.98 of its projection.

## 2. Scaling model for ZL

ZL grid (brief): 4 sets x 5 labels (F15, F30, F60, T15, T30) x 10 model settings (6 LOGIT, 4 LGBM) = 200
configurations, 6 blocked folds each. That gives 720 LOGIT folds (180 a set) and 480 LGBM folds (120 a set), on the
same decision grid (08:35..13:12 - h CT) and the same 816 dates (796 OOF) as E.33.

R_ZL = B_ZL + eta x kappa x phi x [ sum over sets of 180 x t_L(n_s) / P_L + sum over sets of 120 x t_G(n_s) / P_G ]

Labelled assumptions:

- **A1 fold time against feature count n.** Central: an affine model t_m(n) = t5_m x (a_m + n)/(a_m + 59), fitted
  exactly through E.33's two measured anchors (S1 at 23 features, S5 at 59). That gives a_LOGIT = 11.96 and
  a_LGBM = 64.15 (feature-equivalents of fixed cost), with t5_LOGIT = 109.27 s and t5_LGBM = 5.01 s. The low and
  high cases take, set by set, the minimum and maximum over three forms: affine, linear anchored at S5 (t5 x n/59),
  and linear anchored at S1 (t5 x rho x n/23, E.33c's projection rule). Replayed on E.33's own sets, affine gives a
  LOGIT sum of 74,107 s and linear-from-S1 gives 82,408 s, against ref_v03's 76,182 s. Affine is within 3% of it.
  The anchor rho comes only from FH15 and FH30 cells (section 1), which is a caveat.
- **A2 feature counts (from M1 section 7 and M2 section (f)).** F10 has 12 (F10.1-F10.12, M1_F10_ZL.md:465-472).
  F09 crush S_crushL has 8, plus 2 optional VECM features (M2_F09_ZL.md:492, 524-526). F09 propagation S_propL has
  9, plus 1 optional rCL_15 (M2_F09_ZL.md:505-511, 519). The context block C: E.33 had 15 (E.32 protocol P4 line
  396 and line 464, "C 15"; C.11-C.14 are the 4 family validity flags). M1's ZL block lists C.1-C.10, C.15 and one
  flag per family (M1_F10_ZL.md:474-478). With 3 families that makes 14 (central), 13 if C.7 or one flag is dropped
  (low), and 15 at E.33's size (high).

  | case | C | crush | prop | book | S_crush | S_prop | S_book | S_pool | sum n_s |
  |---|---|---|---|---|---|---|---|---|---|
  | low | 13 | 8 | 9 | 12 | 21 | 22 | 25 | 42 | 110 |
  | central | 14 | 8 | 9 | 12 | 22 | 23 | 26 | 43 | 114 |
  | high | 15 | 10 | 10 | 12 | 25 | 25 | 27 | 47 | 124 |

  The lead freezes these counts in P4/P5. Section 3 gives the formula for rescaling.
- **A3 label mix phi** (ZL drops E.33's FH05; t5 is a mean over 6 labels). Central 0.98 takes fold time as
  proportional to rows a date: 273, 263, 248, 218, 263, 248 for FH05, FH15, FH30, FH60, TB15, TB30, so the 5-label
  mean is 248 against 252.2 for 6 labels. Bounds: if FH05 had run as fast as the FH15 cells (77 s LOGIT), phi = 1.06.
  If it had run at about 200 s (the slowest-label case: a 5-minute label has the most class-0 rows, and E.32 P5's
  synthetic probes ran saga up to 20x slower at 99% class 0), phi = 0.83. The guess range is 0.83 / 0.98 / 1.08.
  Per-label E.33 fold times exist only in search_real.log and its Haiku CSV, which I did not open. They would
  narrow phi if the lead allows a times-only read.
- **A4 data regime kappa** (ZL labels and features against ZM: class balance, saga convergence, LightGBM
  early-stopping rounds, and the number of rows after ZL's own roll and exclusion rules): 0.6 / 1.0 / 2.0. This is a
  pure guess. It is the widest factor, and E.33 shows that convergence time is data-dependent (section 1).
- **A5 parallel efficiency and reruns eta:** 1.00 / 1.06 / 1.15. The central value is E.33's measured 1.056. It
  includes load imbalance with fold tails up to 654 s and the 8 cut folds that re-ran.
- **A6 feature build B_ZL** (measured as E.33 measured it: first to last DONE, P_b = 4): 460 / 1,200 / 3,580 s.
  - Low scales E.33's measured 2,387 s by records streamed: ZL MBP-1 158.0M (DF34 section 3) against E.33's roughly
    820M, made up of ZM.v.0 MBO at 414.4M (E.32 protocol P5 line 579), ZS MBP-1 at about 248M (DF34 section 6) and
    ZL at 158M. That is 0.19 x 2,387.
  - Central is half of E.33's build. It keeps ZL as the book leg, adds F10's per-second and sub-second work
    (QIbar5 at 300 one-second marks, 100 ms refills, lam60) and adds the new bar loaders for ZS, ZM and CL.
  - High is 1.5 x E.33's build.
  - Records are counts, not values.
- **A7 rows and folds:** the same as E.33. The largest training fold is 664 dates x 263 rows = 174,632 rows.
- **A8 process counts:** P_b 4, P_L 8, P_G 2, as in E.33, under CLAUDE.md's standard limits (at most 8 threads).
  Variants appear in section 4.

## 3. R_ZL and the 3x stop

| scenario | build B | LOGIT wall | LGBM wall | **R_ZL** | **3 x R_ZL** |
|---|---|---|---|---|---|
| low (every factor low) | 460 s | 2,283 s | 279 s | **3,022 s (0.84 h)** | 9,066 s (2.52 h) |
| central | 1,200 s | 5,825 s | 940 s | **7,965 s (2.21 h)** | 23,895 s (6.64 h) |
| high (every factor high) | 3,580 s | 16,221 s | 2,850 s | **22,651 s (6.29 h)** | 67,954 s (18.88 h) |

The low and high rows multiply every extreme together, so each is an outer bound and an unlikely one.

Central per-fold times: S_crush LOGIT 52.3 s and LGBM 3.5 s; S_prop 53.8 and 3.55 s; S_book 58.5 and 3.67 s;
S_pool 84.6 and 4.36 s.

One-at-a-time sensitivity around the central 7,965 s (low, high):

| factor | low | high |
|---|---|---|
| kappa (A4) | 5,259 | 14,730 |
| build (A6) | 7,225 | 10,345 |
| phi (A3) | 6,930 | 8,655 |
| model form (A1) | 6,739 | 8,558 |
| eta (A5) | 7,582 | 8,539 |
| feature counts (A2) | 7,811 | 8,350 |

kappa dominates.

Rescaling by feature count (affine model, central phi, kappa and eta, P_L 8, P_G 2):

R_ZL = B_ZL + 2,372.6 s + 38.53 s x (sum over the 4 sets of n_s),

where sum n_s = 4C + 2 x (F_crush + F_prop + F_book). The 38.53 s is 35.99 s for LOGIT plus 2.54 s for LGBM. The
2,372.6 s is the fixed-cost intercept: 1,721.7 s LOGIT plus 651.0 s LGBM. Each extra context feature therefore adds
154 s. Each extra family feature adds 77 s, because it enters its own set and S_pool. For other phi, kappa or eta,
multiply the two fit terms by (eta x kappa x phi)/1.0388.

Notes for the lead's choice (not a decision):
- 3 x R_central (23,895 s) is above R_high (22,651 s). A stop at 3 x central therefore covers even the all-high
  case.
- 3 x R_low (9,066 s) is close to R_central. A stop at 3 x low would risk a repeat of E.33's 0.2 stop.
- E.33's fit part was 11,038 s for 300 configurations. ZL's central fit part, 6,765 s for 200 configurations with
  smaller sets, is consistent with it (0.61x).

## 4. Peak memory and allowed parallelism

Machine: 15,118 MB total. `free -m` at 14:05 PDT showed 10,988 MB available. 20 logical CPUs.

**Per LOGIT fold process** (largest case: S_pool at 47 features, fold 6, F15):
- training X in float64: 174,632 x 47 x 8 B = 65.7 MB;
- the set's full label table: 816 x 263 rows = 80.7 MB;
- saga's validated and standardised copies: about 2 x 66 MB;
- saga's gradient memory: 174,632 x 3 x 8 B = 4.2 MB;
- the Python, numpy, scikit-learn and LightGBM runtime: about 150-250 MB [assumption].

Estimate per process: 0.3 GB low, 0.45 GB central, 1.0 GB high (pandas copies, or all labels loaded at once).

E.33's resumed search had 8 such processes, on 23-28 features, and never went below 6,311 MB available (section 1).
If it started near 11 GB available (an assumption; the start figure is not in my inputs), 8 processes used at most
about 4.7 GB, or about 0.6 GB each, which agrees with the estimate.

**8 LOGIT processes:** 2.4 / 3.6 / 8.0 GB. The standard rule (CLAUDE.md: chunk if the estimate exceeds half of
available, about 5.5 GB now) holds at low and central. At high it would cut P_L to about 5, and R then becomes
4,392 / 11,460 / 32,384 s (ref_zl.json:PL5_R_s).

**LGBM:** 2 processes. LightGBM bins the data to uint8 (174,632 x 47 = 8 MB) and holds small histograms, so 0.3-0.6 GB
each.

**Feature build:** per process, one ZL date from the split store (14.9 MB median, 38 MB peak; DF34 section 6), plus
book-state and one-second-mark arrays (tens of MB), plus bars (ZS, ZM and CL ohlcv-1m, under 50 MB a root for the
whole span), plus runtime. That is about 0.3-0.5 GB, or 1.2-2.0 GB for 4 processes. If a builder decoded a whole
month instead of reading per date, peak RSS was measured at 0.95 GB for the largest month (DF34 section 6), so about
4 GB for 4 processes. Every case is far below 14 GB. The 12.5 GB split store must stay per-date (DF34 section 6).

**Allowed parallelism:**
- Standard limits: at most half the cores and never more than 8 threads, one heavy job at a time, nice 10. This
  gives P_L 8 x 1 thread, LGBM 2 x 4 threads, and the builder at 4. These are E.33's counts and are what section 3
  assumes.
- Under the overnight profile, if the run-stage prompt invokes it: 14 threads, at most 2 heavy jobs, a combined peak
  under 70% of available (about 7.7 GB now). P_L could be 14 only if the per-process peak is at most about 0.55 GB.
  R becomes 2,044 / 5,469 / 15,700 s, with LGBM left at P_G 2 and no thread gain assumed (ref_zl.json:
  overnight_PL14_R_s). Whatever process counts the run uses, the protocol must freeze them together with R, because
  R depends on them.

## 5. What the run stage measures first, to report against this guess

All of these are times, memory and counts only. No outcome, fit statistic or iteration count is recorded.
1. **The feature build, measured whole** (first to last DONE, net of logged pauses) before any real-outcome fit.
   Report it against A6 (460 / 1,200 / 3,580 s). E.33 showed that a 3-date probe is not a reliable stand-in. If the
   lead still wants a probe, time the median, p90 and maximum ZL message-count dates (counts from DF34 section 3) and
   report probe x 796 / 4 against the measured build.
2. **Per-process peak RSS** of the first LOGIT fold and the first LGBM fold on the largest set (S_pool, fold 6), and
   of one builder process, using `/usr/bin/time -v` or psutil. Also MemAvailable at the start and its minimum during
   the run. Check these against section 4 before raising P_L above 8.
3. **Per-fold wall times of the first finished set**, if S_pool runs first as E.33 ran S5 first. Report each fold's
   seconds, the set's LOGIT and LGBM means against the central 84.6 s and 4.36 s, and the implied kappa x phi. Also
   report the running ratio of measured to R_ZL's pro-rata share after each finished set. These are information
   only: the frozen R_ZL and its 3x stop do not change mid-run (E.33c needed an amendment to change its reference).
4. **The measured eta:** fit wall time divided by (sum of fold seconds / P) at the end.
5. **The final measured total** (build plus fits, net of pauses) as a multiple of R_ZL and of the 3x stop, in the
   same form as E.33c_RETURN 3.3.

## Not done or not verified

- Per-label E.33 fold times, which would narrow phi, were not read: they are in search_real.log and its CSV, which
  are outside my inputs.
- kappa (A4) and the build factor (A6) are unverifiable guesses until the run stage measures them.
- The 11 GB start-memory figure behind the E.33 bound in section 4 is an assumption.
- No independent check of the arithmetic has been run.
