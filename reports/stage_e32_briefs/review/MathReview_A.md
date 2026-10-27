# MathReview_A: independent check of M2_lead_lag.md and the arithmetic sections of R3a_crush.md

Stage E.32, review group A. Reviewer MathReviewer-FableXHigh (model claude-fable-5-1 per the session banner; the lead
verifies from the transcript's message.model). Written 2026-10-27 02:50 PDT. Brief:
reports/stage_e32_briefs/work/lead/brief_MathReviewer_A.md.

Method. Every number was recomputed before the reader's calculators were opened, with my own script
reports/stage_e32_briefs/review/work_A/recompute_A.py (output recompute_A.json, 114 named results; own seeds for the
two Monte Carlos). Quotes were checked by grep against the saved pages under reports/stage_e32_briefs/pages/; no page
was read whole. No market data, no Databento, broker or ProjectX call, no web fetch
(reports/stage_e32_briefs/review/work_A/log.tsv records that none was made). No reviewed file was edited.

Standard numbers used (READER_BRIEF.md "Standard ZM numbers"; verified at source): ZM tick 0.10 USD/short ton =
10 USD; sigma_1m 3.15 (ZM), 3.11 (ZS), 5.52 (ZL) ticks; Topstep ZM fee 5.28 USD = 0.528 ticks; break-even mu*_mkt =
1.59 ticks (reports/stage_e28_ranking.md line 130, row `| 6 | topstep | ZM | ... | 0.59 | 1.59 | ...`, confirmed);
E.31 gross 10 s edges -0.970 (c), -0.287 (a), -0.252 (b) ticks (reports/E.31_RETURN.md lines 185-193, confirmed; the
-1.100 / -0.652 split is at line 202, confirmed).

Severity: BLOCKING = wrong equation or number that changes a verdict or would mislead the frozen protocol; SHOULD FIX =
wrong number or derivation without a verdict change, missing or unstated assumption, quote not found, [unverified]
item carrying weight; NOTE = clarity or minor.

Totals: BLOCKING 0, SHOULD FIX 5, NOTE 11. Per file: M2_lead_lag.md 0 / 4 / 7; R3a_crush.md (arithmetic sections)
0 / 1 / 4.

---

## Part 1: reports/stage_e32_briefs/M2_lead_lag.md

### Findings table (M2)

| ID | file:line | Claim as written | What is wrong | Correct value or derivation | Severity |
|---|---|---|---|---|---|
| A-1 | M2:193 and M2:280 | HRY "show 'a simple central limit theorem cannot hold' (Proposition 2)"; evidence row quotes "a simple central limit theorem cannot hold for our estimator" as verbatim | The string is not in the saved text. hry2013_leadlag.pdf.txt lines 488-489 read: "In that case, it becomes impossible, in general, to derive a simple central limit theorem for ϑ̂_n." The meaning is kept; the quotation marks are not earned | Replace with the verbatim sentence above (and keep the Proposition 1 context: the normalised estimator "weakly converges to a Dirac mass at point ϑ") | SHOULD FIX |
| A-2 | M2:140-142 ((a) trap ii), M2:253-254 ((b) trap iii), M2:131 ((a) data) | Clock-offset trap; tests: "the HY lead-lag contrast of a stream against itself must peak at lag 0"; "a placebo pair with a known zero lag (bid against ask of the same root) must give theta_hat = 0" | The trap is real but neither test can detect it. A stream against itself peaks at lag 0 by construction, and the bid and ask of one root come from the same stream (ZM MBO, or ZS/ZL MBP-1), so neither sees an offset between the ZM MBO stream and the ZS/ZL MBP-1 streams, which is the offset named. (a)(4) also makes receive time the primary clock for an estimator whose fine mesh is 0.05-0.1 s | Use ts_event (exchange time; the three roots clear on the same CME matching complex) for the HY/HRY estimator and keep ts_recv for the latency/tradability analysis. Detecting test: (i) per root and session, the distribution of ts_recv - ts_event; the difference of medians across roots must be below the fine mesh; (ii) a cross-root placebo with a known simultaneous timestamp (the first message at or after the 08:30:00 open and the 13:20:00 close in each root, or the settlement/clearing message sequence) must give theta_hat = 0. Field semantics belong to DataFacts, as M2 says; the test design belongs here | SHOULD FIX |
| A-3 | M2:377-379 ((c) data), M2:503 ((d) data), M2:744-747 ((f) data), traps of (c), (d), (f) | "1-minute (and 5-minute) mids or last-trade prices"; "Previous-tick bars suffice at 1 minute or longer (see (a): 9% correlation loss at 1 minute under the assumptions)". No trap for bid-ask bounce or stale legs | Two obvious traps are missing. (1) Last-trade prices carry bid-ask bounce (negative first-order autocorrelation), so a residual built on them shows spurious fast reversion: (d)'s HL is biased down and the kill rule "HL CI upper bound exceeds the time stop" is biased toward survival. (2) A stale leg makes an apparent dislocation that "closes" when the stale leg updates; nothing is tradable in it. The 9% figure holds only for the assumed 3 s / 6 s gaps. Under the analytic approximation attenuation ≈ 1 - E\|U1 - U2\|/Δ with exponential backward-recurrence times (E\|U1-U2\| = m1 + m2 - 2 m1 m2/(m1 + m2); it gives 0.917 at 1 min and 0.983 at 5 min for 3/6 s, matching the reader's MC 0.909/0.972 and mine 0.906/0.976), gaps of 10/20 s give 0.72 at 1 min, 20/40 s give 0.44 (a 56% loss) and 0.89 at 5 min, 30/60 s give 0.17. A0 Table 1 (reports/stage_e28_briefs/A0_contract_stats.md line 115) puts ZM's overnight volume at a median of 2 contracts per minute (mean 8.5) against 71 (109.2) in the main session, so the day-session assumption does not carry to the overnight stratum that (d), (f) and R3a section 7 single out (volume, not quote-update rate; the latter awaits DataFacts) | Fix: residual and HL from BBO mids only, never last trades; add the trap with tests: (i) HL from mids and from last trades must agree within the grid-bootstrap CI; (ii) an entry requires every leg's BBO to have updated inside a frozen staleness window, and the protocol reports the share of candidate dislocations that collapse on the next update of the stalest leg; (iii) the 1-minute versus HY/5-minute choice for the hedge-ratio input is re-derived from DataFacts' measured gaps per stratum before K and the bar length are frozen. Not BLOCKING because (f)(4) and trap (iv) already price entries and exits at the touch after latency, which protects the P&L from bounce; the exposed pieces are the HL kill rule of (d) and the dislocation frequency that (f)(3) names as a binding unknown | SHOULD FIX |
| A-4 | M2:558-564 ((e) eq.), M2:689 ((f) eq.), M2:650-655 ((e) verdict), M2:771-772 | s_i = beta_i alpha_i / (beta' alpha), derived "With Gamma = 0"; "With Gamma != 0 the same shares come from the long-run impulse response [derived; not checked against a fetched text]" | The Gamma = 0 result is right (I re-derived it and reproduced the iteration check). The generalisation is not "the same shares": with short-run terms the cumulative leg moves solve a linear system in alpha and Gamma and can differ materially. Since (e)(6) fits a VECM with k <= 20 lags and the kill rule of (e)(7)/(f)(7) uses s_M from that fit, the frozen protocol needs an operational definition | Derivation (one lag; k lags replace Gamma by the sum of the Gamma_j): dP_t = alpha z_{t-1} + Gamma dP_{t-1}; summing over t with dP_0 = 0 gives (I - Gamma) ΣdP = alpha Σz, so ΣdP = (I - Gamma)^{-1} alpha Σz; z_inf - z_0 = beta' ΣdP = -z_0 gives Σz = -z_0 / (beta' (I - Gamma)^{-1} alpha). Hence s_i = beta_i [(I - Gamma)^{-1} alpha]_i / (beta' (I - Gamma)^{-1} alpha), which is the stated formula with alpha replaced by alpha~ = (I - ΣGamma_j)^{-1} alpha, and reduces to it when Gamma = 0. Equivalent, and simplest to freeze: s_M = ZM's share of the cumulative closure in the fitted model's deterministic impulse response from z_0 = 1 c with all lagged differences zero (what (e)(3)'s 5,000-step iteration already does). Weak-exogeneity tests on alpha are unaffected | SHOULD FIX |
| A-5 | M2:56-156 ((a) equations and data) | HY sums every overlapping pair of increments | Nothing says the sum is taken within a session. An increment spanning the 13:20-19:00 break (5 h 40 min) or the 07:45-08:30 halt exists in each root, the two overlap, and their product dominates U_n for that day. (b)(4) says "per session"; (d)(4) drops straddling pairs; (a) does not | State: HY and RV within a session, increments across the break and the halt dropped | NOTE |
| A-6 | M2:408-409 | "2.6 million rows. That is about 60 MB as float64" | 3 x 1,055 x 815 = 2,579,475 values x 8 B = 20.6 MB; 60 MB only if three float64 fields are stored per (root, minute) | 20.6 MB per float64 field; immaterial for compute | NOTE |
| A-7 | M2:692-694 | "1.59 is Topstep's ZM market-order break-even mu*_mkt ... It includes the 5.28 USD fee, which is 0.528 ticks" | True but incomplete. Per reports/stage_e28_briefs/A3_econ.md lines 86-92, mu*_mkt is the smallest mu with EV >= 0 in E.28's cycle simulator in the market case, with S_rt = 1 tick so mu*_mkt = mu*_lim + 1.00; EV is the trader's net cash per cycle including the API subscription and the payout split. So 1.59 = 1.00 tick of spread + 0.59, of which 0.528 is the fee and about 0.06 is subscription and payout effects, not spread + fee = 1.528 | State the decomposition so the netting N = G - 1.59 (G a mid-to-mid expected move) is read correctly; the use itself is right | NOTE |
| A-8 | M2:729-735 | "A 1.0-tick NET edge gives Sharpe 1.0/18.9 = 0.0529 per trade, so ... 3,215 trades" | The illustration's net edge is not reachable at the section's own D = 1 c numbers (net is negative at every m in (3)(ii)). At the median vector, m = 2, G = 0.3089 x 0.75 / 0.19 = 1.219 ticks per cent, so net +1 tick needs D = 2.59 / 1.219 = 2.12 c (net 0 at 1.304 c) | Say that the 1-tick net case corresponds to D of about 2.1 c (median vector, m = 2), or run the illustration at the net edge the table implies | NOTE |
| A-9 | M2:334-342 | MacKinnon response surface evaluated at T = 290 and 5,800 | Values recomputed and correct (-3.77032, -3.74214). MacKinnon's T_k is the number of observations in the ADF regression (290 minus lags minus 1), which moves the fourth decimal | Say which T is used when the protocol freezes the critical value | NOTE |
| A-10 | M2:48-49, M2:381-383 | ZS months F,H,K,N,Q,U,X; ZM and ZL F,H,K,N,Q,U,V,Z, "[unverified: contract months from contract knowledge, not a fetched spec]" | Correctly marked. No saved page states these months: grep of pages/M2_lead_lag and pages/R3a_crush for "contract months\|delivery months" finds only corn, cattle and NG (hu_mallory_nccc2017, kit_wp27). My own contract knowledge agrees with the list, which is not evidence | Keep [unverified] until DataFacts confirms from the definitions files; the month-map rule in (c)(7) should be written as conditional on that confirmation | NOTE |
| A-11 | M2:75 | "Implement it as a two-pointer sweep, as M2_examples.py does" | The toy (M2_examples.py lines 24-42) uses a double loop over all increment pairs (with the correct strict half-open overlap predicate max(a0, b0) < min(a1, b1)); the Monte Carlo (lines 94-99) uses the vectorised searchsorted sweep. Accurate for the MC only | Point at the MC implementation so no one copies the O(n1 n2) toy loop | NOTE |

### Checked and found correct (M2), by topic

Conventions (M2:16-22): sigma_1s = 3.15/sqrt(60) = 0.4067 (ZM), 0.4015 (ZS), 0.7126 (ZL) ticks: recomputed, equal.

(a) Hayashi-Yoshida and Epps.
- Equations: target covariation and HY sum (HY 2008 eq. 3) with half-open intervals and the overlap indicator; linear
  cost (n1 + n2 minus common times); rho_HY normalisation; previous-tick RC definition; the sign of the noise bias on
  rho_HY (RV biased up, rho toward zero). All consistent with the saved text and with my own derivation.
- Toy example: my HY implementation gives U = 2 ticks^2, RC(1 s) = 0, RC(0.5 s) = 1, the two overlapping pairs named
  at M2:99-100 and no other, the previous-tick grid values at M2:104-109 exactly.
- Epps Monte Carlo (own seed, 40 reps): previous-tick correlation 0.060 / 0.227 / 0.407 / 0.543 / 0.586 at 1 / 5 / 15 /
  60 / 300 s against the reader's 0.060 / 0.229 / 0.411 / 0.546 / 0.583; HY 0.597 (SD 0.033) against 0.600 (0.022).
  Within Monte Carlo error (my SE of the 300 s mean is 0.012). OLS-beta attenuation 0.906 at 1 min and 0.976 at
  5 min against 0.909 / 0.972; the analytic approximation gives 0.917 / 0.983. The assumptions are labelled as such.
- Compute: 2 x 10^6 x 815 = 1.63 x 10^9; 16 MB per 10^6 events at 16 B each.
- Quotes verified in hayashi_yoshida_2008_aism.pdf.txt: "free of" + "'synchronization' processing" (lines 22 and 85,
  line break), "only when the respective observation intervals I i and J j are overlapping", "minus the number of
  grids that are common in both 1 and 2" (lines 197-198), "suffer 'synchronization' bias" (line 83). Toth-Kertesz:
  "1979 Epps reported" (epps_revisited), "traced back to the trading asynchronic-ity" and "insufficient to give account
  for the whole effect" (origin_epps lines 20-23, hyphenated at the break). HY 2005 is correctly [unverified].

(b) HRY contrast.
- Equations: HRY model (eq. 1-3) with the lagged representation; shifted contrast; argmax over G_n; rate Δ_n^{-1}
  ("essentially ∆n−1 and not ... −1/2", lines 122-123, verified); degeneracy for small rho; LLR definition and sign
  convention (Huth-Abergel line 326 "we state that X leads Y if" and line 378 "LLR := ... > 1").
- Pure-shift worked example: I re-derived the predictable ZM move after latency as rho sigma_ZM,1s sqrt(theta - L)
  (the ZM path over (t+L, t+theta] copies B1 over (t+L-theta, t], known at t). SD 0.2041 ticks (theta 1 s, L 0.3 s,
  rho 0.6), 7.79 SDs to 1.59; 0.5302 ticks (theta 2 s, rho 1), 3.0 SDs. Static bound: slope 3.15/3.11 = 1.0129,
  1.57 ZS ticks, 3.91 one-second ZS SDs; crush-equivalent 0.25/0.22 = 1.136, 1.40 ZS ticks. All equal.
- Grid 121 + 101 = 222 passes; 222 x 4 x 10^5 x 815 = 7.2 x 10^10.
- Quotes verified in hry2013_leadlag.pdf.txt: "contrast optimization based on a modified version", "over the finite
  grid", "robust to non-synchronous" + "pre-processing" (line break), "does not locate the true value", "lies beyond
  the scope of this paper", "with a small lead lag value of −0.8 second" (line 1420), "order of one second",
  "systematically negative". Huth-Abergel: "60% of accuracy", "cannot make any profit of this effect", "spurious
  liquidity effects", "synchronously correlated Brownian motions", "tend to lead smaller stocks". Shiotani et al.:
  "at 5 milliseconds", "one millisecond or less". E.31 context numbers -1.100 / -0.652 at E.31_RETURN.md line 202.
  Dobrev-Schaumburg correctly [unverified].

(c) Error-correction and OU models.
- Units chain: 44 lb = 0.022 short ton of meal and 11 lb of oil per 60-lb bushel; oil value 11 ZL c/bu; meal value
  0.022 ZM USD/bu = 2.2 ZM c/bu; C = 11 ZL + 2.2 ZM - ZS c/bu; per tick 0.11 (ZL), 0.22 (ZM), 0.25 (ZS) c/bu;
  C = 0.11 nL + 0.22 nM - 0.25 nS in ticks; Zhou's (1, -0.11, -0.22) reproduced with ZS in cents and ZL/ZM in ticks
  (z = -C); ratio-based use of 0.19/0.22 is scale-free. 10:11:9 in contract units: 50,000 bu, 1,100 t (exact),
  540,000 lb = 10.8 lb/bu (1.8% short); 500 USD per cent on the 10-lot; 11 ZM ticks = 110 USD = 50,000 bu x 0.22 c.
  Example prices: 660 + 924 - 1,400 = 184 c/bu; 4.545 and 5.263 ZM ticks per cent; 45.45 USD per lot; 0.864 c.
- Engle-Granger form and MacKinnon Table 2 values for N = 3, tau_c, 5% (-3.74066, -8.5631, -10.852, 27.982: each
  found once in mackinnon_2010_critvals.pdf.txt); response surface at T = 290 (-3.77032) and 5,800 (-3.74214).
- Johansen VECM, trace and max-eigenvalue statistics; phi = 1 + beta' alpha by premultiplying with beta' (re-derived).
- Compute: 765 + 290 = 1,055 min; 2.58 M values.
- Quotes verified: Rechner-Poitras "48 lbs" / "11 lbs" / "12 meal" / "9 oil" / "$500.00 change" (M2 copy and R3a
  copy); Poitras "uses 10 Soybean, 11 / Soy Meal and 9 Soy Oil" (lines 18-19, line break); Zhou Table 6 rows
  "Median 1 -0.11 -0.19" and "CME (physical) 1 -0.11 -0.22" (lines 1430, 1435), "Kalman smoother", "missing data";
  Boero "The maximum eigenvalue statistic", "do not enter"; statsmodels "Pi = alpha beta'". Mitchell and
  Ericsson-MacKinnon correctly [unverified] in M2 (R3a fetched Mitchell separately).

(d) Half-life.
- Equations: AR(1)-OU map, HL = dt ln 2 / (-ln b); HL_z from b = 1 + beta' alpha; Kendall / Marriott-Pope
  -(1 + 3 lambda)/T (Kiviet-Phillips eq. 3.12, quote verified; the page image is the right way to read the sign);
  inverted correction b_c = (T b_hat + 1)/(T - 3) (re-derived); se = sqrt((1 - b^2)/T); monotone CI mapping with
  HL = infinity at b_hi >= 1.
- Worked numbers: kappa 0.05129, HL 13.51; T = 60: b_hat 0.88583, HL 5.72 (57.7% short); T = 290: 0.93672, 10.60
  (21.5% short); T = 5,800: 0.94934, 13.33; corrections return 0.95000 exactly; T = 290 se 0.02056, b in [0.89643,
  0.97702], HL in [6.34, 29.81]; T = 60 se 0.0599, b in [0.76842, 1.00324], HL in [2.63, inf). All equal.
- Monte Carlo (own seed, 400 reps): segment-demeaned pooled OLS 0.9057 (LSDV 0.9062; SE 0.0008) against the
  reader's 0.90628; global mean 0.9467 against 0.94700; single 290-minute series 0.9357 against 0.93599. Nickell's
  (1981) LSDV formula at T = 60 gives -0.040 (b_hat 0.910), the same order. HL from the demeaned design 7.0 min.
- Compute: 200 x 1,999 x 290 = 1.16 x 10^8; 24 x 2 x 40 = 1,920 intervals.
- Quotes verified: Kiviet-Phillips "understates the actual bias" and "Marriott and Pope (1954) gave an approximation";
  Hansen "rst-order correct globally in the parameter space" (line 15, ligature dropped by pdftotext) and
  "setting G 5 200 and B 5 1999 in most" (line 339, "=" rendered as "5"); Kim-Silvapulle-Hyndman and Cardiff
  correctly [unverified].

(e) Which leg adjusts.
- Equations: s_i derivation at Gamma = 0 (re-derived; see A-4 for Gamma != 0); ZM ticks per cent = s_M / b_M; weak
  exogeneity reading; Gonzalo-Granger A1 and gamma; bivariate CS_1 = alpha_2/(alpha_2 - alpha_1); Hasbrouck IS with
  the lower Cholesky factor and Putnins' bivariate closed form (M's (2,1) entry rho s2 written m12 in Putnins'
  notation, consistent); bounds coincide at rho = 0; IL and ILS definitions; the three-price / one-relation / two
  common trends argument against trivariate IS/CS; the bivariate device z = p2 - p1 with beta = (-1, 1)' and
  s_M = -alpha_1/(beta' alpha).
- Worked numbers: beta' alpha -0.0387, b 0.9613, HL 17.56 min, shares 0.5168 / 0.1421 / 0.3411 (sum 1), ZM 1.5504
  ticks per cent, iteration moves -0.5168 c / +1.292 / +1.5504 ticks with final z ~ 1e-15; median vector -0.0369,
  HL 18.44, shares 0.5420 / 0.1491 / 0.3089, ZM 1.626 ticks per cent. All equal. 17,400 rows per day session at 1 s.
- Quotes verified: Boero "does not enter that equation"; Yan-Zivot "ordered first (last)", "all permutations",
  "one minute sampling interval"; Putnins "only applicable in bivariate", "relative avoidance of noise", "values above
  (below) / 0.5 indicating the price series leads (does not lead)" (lines 542-543, line break); Hu et al. "then take
  the average", "overstating the price discovery contribution". Hasbrouck 1995 correctly [unverified].

(f) Trading a ZM-only dislocation.
- Equations: signal and sign convention (x > 0: meal cheap; buy ZM when alpha_M > 0; the hypothetical alpha is
  error-correcting in all three legs and beta' alpha < 0); fraction closed 1 - 2^{-m}; G = s_M D (1 - 2^{-m}) / b_M
  (exact under Gamma = 0: ZM's cumulative move by tau is alpha_M z_0 (1 - phi^tau)/(1 - phi)); s_M* inversion;
  Sharpe and (3/Sharpe)^2.
- Worked numbers: planner's 4.545 VERIFIED; G 0.813 / 1.220 / 1.423; D needed 1.956 / 1.304 / 1.118 c (median) and
  2.051 / 1.367 / 1.172 c (physical); check G(D = 1.304, m = 2) = 1.590; break-even table: all 24 s_M* cells and all
  24 gross-at-s_M = 1 cells recomputed and equal to the printed two-decimal values (for example b_M 0.22, D 1:
  0.6996 / 0.4664 / 0.3998 and 2.273 / 3.409 / 3.977; b_M 0.19, D 3: 0.2014 / 0.1343 / 0.1151 and 7.895 / 11.842 /
  13.816); noise 18.9 ticks at 36 min, Sharpe 0.0529, 3,215 trades; 12.2 ticks at 15 min, 1,340 trades; 1.64-3.94 a
  session over 815. Bottom-line s_M* 0.70 (D = 1) and 0.35 (D = 2); "0.40-0.70" at D = 1 is m = 3 to m = 1.
- Evidence rows: E.28 ranking row and header (lines 123, 130) match; E.31 "gross -0.970 [-0.988, -0.950]" at line 21
  matches.

Planner-pointer table (M2:785-794): the arithmetic claims (0.22 c per ZM tick, 4.545, 5.263, 1.55 at s_M 0.34,
10.8 lb/bu, s_M* 0.70 / 0.35, MC 0.906 vs 0.95 and 7.0 vs 13.5 min) all agree with my recomputation.

### Verdict (M2): sound with fixes
No equation or number is wrong. The four SHOULD FIX items are a paraphrase presented as a quote (A-1), two leakage
tests that cannot detect the trap they name (A-2), a missing stale-quote / bid-ask-bounce trap whose size I bound
(A-3), and an s_M definition that must be made operational before a VECM with lags feeds the kill rule (A-4). The
verdicts USE (c, d, f), MAYBE (a), SKIP-as-signal / MAYBE-as-conditioner (b) and the split verdict of (e) follow
from the arithmetic shown; none is stronger than its evidence, with (f)'s own reading ("the family may well die
early") the honest one.

---

## Part 2: reports/stage_e32_briefs/R3a_crush.md, arithmetic sections 1, 2.3, 3.2, 4.2, 6.2, 7.2, 8.2

### Findings table (R3a)

| ID | file:line | Claim as written | What is wrong | Correct value or derivation | Severity |
|---|---|---|---|---|---|
| A-12 | R3a:237-245 (3.2 units caveat, marked "[unverified, needs reviewer]") | Zhou's "CME (physical)" row (1, -0.11, -0.22) "is reproduced only if ZS is in USD/bu and both ZL and ZM are in units 100 times smaller than cents/lb and 10 times smaller than USD/ton respectively, or under some other price scaling the paper does not state" | The stated scaling does not reproduce the row: with ZS in USD/bu, C = 0.11 O[c/lb] + 0.022 M[USD/ton] - S; ZL in 0.01 c/lb units gives 0.11 x 0.01 = 0.0011 per unit, ZM in 0.10 USD/ton units gives 0.022 x 0.10 = 0.0022 per unit, so the vector would be (1, -0.0011, -0.0022). It also contradicts M2 (c) (M2:318-319), which gives a scaling that does work | Two scalings reproduce (1, -0.11, -0.22): (A) ZS in c/bu, ZL in ticks of 0.01 c/lb, ZM in ticks of 0.10 USD/ton (11 x 0.01 = 0.11; 2.2 x 0.10 = 0.22), M2's reading; (B) ZS in USD/bu, ZL in c/lb, ZM in units of 10 USD/ton (0.11; 0.022 x 10 = 0.22). Quote units give (1, -11, -2.2), as Marowka's line confirms. Zhou's text states no units and uses "the last trading price" (zhou_etal_nccc134_2022.pdf.txt line 1019); "log" never appears as a price transform. The internal evidence favours a tick-like scaling: an estimated median within 14% of the paper's own physical row would be an order of magnitude off if the data were in quote units. R3a's conclusion (compare -0.19 with -0.22 only as a ratio inside the paper; use a fixed physical vector or a long-window estimate for the signal) stands and agrees with M2:321-322. Fix: replace the wrong scaling with (A)/(B) and cite M2 (c), so the two files carry one reading | SHOULD FIX |
| A-13 | R3a:113-116 (1.4) | "a residual of 1.59/4.545 = 0.35 c/bu closed fully by ZM pays one break-even" | Arithmetic right, but it is the s_M = 1, complete-closure (m -> infinity) case. M2 (f) shows the binding form D* = 1.59 b_M / (s_M (1 - 2^{-m})): 0.70 c at s_M = 1, m = 1; 1.1-2.1 c at the hypothetical s_M = 0.31-0.34 | Cross-reference M2 (f) so the two files do not read as 0.35 c against 1-2 c | NOTE |
| A-14 | R3a:516-526 (7.2 a) | Day 105.0 and overnight 8.15 contracts per minute derived from ADV x share / minutes; ratio 12.9 | Correct, and it matches A0 Table 1's measured means (109.2 main, 8.5 overnight; reports/stage_e28_briefs/A0_contract_stats.md line 115, columns "Vol/min main median (mean)" and "Vol/min overnight median (mean)"). A0's medians are 71 and 2, so the typical overnight minute is far thinner than the mean-based ratio suggests (median ratio about 35) | Cite the measured row; it strengthens the section's point and is the input A-3 needs | NOTE |
| A-15 | R3a:380-389 (4.2 d), R3a:412 | Abdoh-Chitavi half-lives 26.72 / 27.26 days, b1 -0.0256 / -0.0251, 0.0018 USD/lb, 1,080 / 1,125 / 1,380 / 2,040 / 865 USD, 406 trades, 6.09 days | All recomputed and consistent (26.73, 27.27, 1,080, -45 / +255 / +915 / -260, 600,000 lb each leg, 72 and 75 USD per lot). But the half-lives, b1, 0.0018, 1,080 and 1,380 exist only in abdoh_chitavi_firecrawl_directquote.txt (an extractor's selected passages); the raw pages (abdoh_chitavi_sd.html, _ideas.html) carry only 1,125, 2,040, 865, 406 and 6.09. R3a discloses this ("PARTIAL full text", lines 326-327, 412, 688) | Keep the partial-full-text label on every use, including section 9 if the 27-day half-life is carried into the "daily reversion too slow" reading | NOTE |
| A-16 | R3a:358-359 (4.2 a) | Mitchell "writes .35 where the table says -0.36; a one-cent rounding difference in the second decimal" | The difference is 0.01 c/bu, one hundredth of a cent, not one cent | "a 0.01 c/bu difference" | NOTE |

### Checked and found correct (R3a arithmetic sections)

Section 1 (contract arithmetic).
- Contract sizes from tick values: 10.00/0.10 = 100 short tons, 12.50/0.0025 = 5,000 bu, 6.00/0.0001 = 60,000 lb;
  Poitras's weights (300,000 / 200,000 / 60,000 lb) consistent.
- C_44 = 0.022 M + 0.11 O - S/100 USD/bu; in cents 2.2 M + 11 O - S; C_48 with 0.024; oil-share definition
  (farmdoc "as a percentage of total / revenue", line 80, verified); sensitivities 0.22 / 0.11 / 0.25 c/bu per tick.
- 1.3 (a): 2,200,000 lb = 1,100 t = 11 ZM; 2,400,000 lb = 12 ZM; 550,000/60,000 = 9.17 -> 9 (10.8 lb/bu); husks
  260,000 and 60,000 lb (Poitras lines verified: "260,000", "60,000 lbs. of husks").
- 1.3 (b): 500 USD per cent (Rechner-Poitras "$500.00" verified).
- 1.3 (c): 0.22 c/bu per ZM tick two ways; 4.545 ticks per cent; 45.45 USD; 0.24 and 4.17 under 48 lb.
- 1.3 (d): 0.50 + 0.48 + 0.216 = 1.196 c/bu (Rechner-Poitras "1.196" verified).
- 1.3 (e): 0.693 / 0.778 / 0.607 c/bu per minute; anti-aligned bound 2.08 c/bu (random-walk sigma_1m, labelled).
- 1.3 (f): October 2021 under 48 lb: meal 7.510, oil 6.448, OS 46.2%, margin 2.078 USD/bu (Smith "54%" / "46%"
  / "$2.08" verified in tamu_meal_or_oil.txt); under 44 lb 6.884, 48.4%, 1.452; January 2021 32.9% against Smith's
  "65%" meal (three-month average). All prices (417.60, 312.90, 44.62, 58.62, 13.70, 11.88) verified in the page.
- 1.4: 1.59/4.545 = 0.35 c (see A-13 for the missing factors).
- Quotes verified: farmdoc "11 pounds of soybean oil, 44 pounds", "18.3%", "around 20%", "47 to 48 pound", "closer
  to 44 pounds"; Smith "44 lbs of soybean meal (48% protein)"; Rechner-Poitras "48 lbs" / "11 lbs" / "12 meal";
  Poitras "Crush Guide" / "10 Soybean, 11 / Soy Meal and 9 Soy Oil".

Section 2.3: 0.232 - 0.070 = 0.162; 0.070/0.232 = 0.3017; 0.511 - 0.451 = 0.060; 0.451/0.511 = 0.8826. The four
coefficients verified in farmdoc_fdd101325_oilshare.pdf.txt (each found once). The caveat that these are weekly
cash-price value sensitivities, not contract hedge ratios, is right.

Section 3.2: 180/243 = 0.741, 229/243 = 0.942, 52/243 = 0.214, 64/243 = 0.263, 70/243 = 0.288; 0.03/0.22 = 13.6%;
0.28/0.19 = 1.47; IQR -0.24 to -0.14 (width 0.10). Zhou's tables verified: Table 2 (session 2, 1-min) Johansen
"all price" 64, ZSmatch 69, ZLmatch 70, ZMmatch 68, missing-data filter 180; Table 7 (session 1) 52; Table 6 StDev
0.28, quartiles -0.24 / -0.14; "229 days of cointegration (versus 180 ...)" at line 2756; "290 data points" present.
Units caveat: see A-12.

Section 4.2.
- (a) -0.36 + 1.50 = 1.14; 1.74 + 1.50 = 3.24 c/bu. Rechner-Poitras "-0.36", "1.02", "1.74", "1.5 cents" verified;
  Mitchell "loss of .35 ... +.35, 1.02, and 1.74" verified in mitchell_jrfm2010_firecrawl.md (see A-16 on wording).
- (b) b = rho sd(y)/sd(x): -0.49 x 2.837/2.727 = -0.510; -0.43 x 3.133/3.241 = -0.416; the OLS identity is right and
  the SDs (2.727, 2.837, 3.241, 3.133), correlations (-0.49 (-23.7), -0.43 (-14.2)) and meal -0.019 verified in
  rechner_poitras_1993.pdf.txt.
- (c) theta = ln 2 / 3 = 0.2310 per day; /290 = 7.97e-4 per minute; 1 - exp(-0.0478) = 4.67%; 0.047/0.22 = 0.21 ZM
  ticks; the "all reversion inside the 290 day minutes" assumption is the favourable case and is labelled. The 3-day
  half-life is Mitchell's summary of Simon (secondary; labelled so at R3a:409 and 686; "half-life ... about 3 days"
  verified in the Mitchell file).
- (d) H = ln 0.5 / ln(1 + b1): 26.73 and 27.27 days (paper 26.72 / 27.26); 0.0018 x 600,000 = 1,080; nets -45, +255,
  +915, -260 USD; 2 ZS = 3 ZM = 10 ZL = 600,000 lb; 75 USD cost and 72 USD gross per lot (7.2 ZM-tick equivalents).

Section 6.2: 3 x (-0.30%) = -0.90%; 0.009 x 300 = 2.70 USD/ton = 27 ticks = 270 USD per lot, two ways. Avileis-Swanson
"-0.30" verified (lines 32, 142, 670, 688). The daily (close-to-close) caveat is right.

Section 7.2: (a) 0.83 x 36,690 / 290 = 105.0; 0.17 x 36,690 / 765 = 8.15; ratio 12.88; ZS 9.35; ZL 12.02; 765 and 290
minutes from the brief's session times; the "07:45-08:30 gap closed" assumption is labelled (see A-14). (b) 0.510 x
2.727 = 1.391 c/bu; /0.22 = 6.32 ZM ticks; the three non-transfer reasons are supported by the verified table
values. (c) 52 + 191 = 243; 180 + 63 = 243.

Section 8.2: 39 releases (1 + 12 + 12 + 12 + 2); 11:00 CT = "Noon Eastern" (nopa_release_dates_2025.pdf.txt line 5);
150 and 140 minutes to the session edges; sigma_60 = 3.15 x 7.746 = 24.40 ticks (random walk, stated); SE at n = 39
3.91 ticks; n = (2 x 24.40 / 1.59)^2 = 942; 78.5 years. The "lower bound" reading (event-day vol higher) is right.

### Verdict (R3a arithmetic sections): sound with fixes
Every number recomputes. The one SHOULD FIX (A-12) is a wrong unit statement in a paragraph the reader itself flagged
for review; its conclusion survives and matches M2. The verdict-bearing readings (daily-scale reversion too slow at
hours; a NOPA-day rule untestable on 39 months; ZM thinnest overnight) follow from the arithmetic shown.

---

## Part 3: cross-file consistency (brief items 6 and 7)

| Quantity | M2 | R3a | Agree? | My recomputation |
|---|---|---|---|---|
| Board crush identity | C = 11 ZL + 2.2 ZM - ZS c/bu (M2:311) | C_44 = 2.2 M + 11 O - S c/bu (R3a:58) | yes | from 44 lb = 0.022 t and 11 lb per 60-lb bushel; contract sizes from tick values (100 t, 5,000 bu, 60,000 lb), Poitras's weights agree |
| ZM ticks per cent of crush, ZM alone adjusting | 4.545 (M2:368, 705) | 4.545 (R3a:85) | yes | 1/0.22 = 4.5455 |
| Same at Zhou's 0.19 | 5.263 (M2:372, 707) | not used | n/a | 1/0.19 = 5.2632 |
| Closure-share threshold at D = 1 c to clear 1.59 | s_M* = 0.70 / 0.47 / 0.40 at m = 1 / 2 / 3 (M2:724, 737) | 0.35 c for a full close by ZM (R3a:115) | consistent once R3a's case (s_M = 1, m -> inf) is named (A-13) | 1.59 x 0.22 / (1 x (1 - 2^{-m})) = 0.6996 / 0.4664 / 0.3998 |
| Front-month mapping trap | ZS no V/Z contracts, [unverified] (M2:48, 381) | not discussed | no conflict | no saved page states the months (A-10) |
| Break-even | 1.59 ticks, E.28 row 6 (M2:13, 693) | 1.59 ticks, same row (R3a:113-115) | yes | row confirmed at stage_e28_ranking.md line 130; decomposition in A-7 |
| Topstep ZM fee | 0.528 ticks (M2:694) | 5.28 USD (R3a:389) | yes | 5.28 / 10 |
| Session lengths | 765 + 290 = 1,055 min (M2:408) | 765 and 290 (R3a:518-519) | yes | 12 h 45 min; 4 h 50 min |
| Zhou vector units | ticks reading, [derived] (M2:318-322) | wrong scaling, [unverified] (R3a:237-245) | NO (A-12) | scalings (A) or (B) in A-12 |
| Zhou numbers used | -0.19 / -0.22 (Table 6) | 180, 229, 52, 64-70 of 243; SD 0.28; IQR (Tables 2, 6, 7) | yes | all found in the saved text |
| E.31 edges | -0.970 (M2:695); -1.100 / -0.652 (M2:234) | not used | n/a | E.31_RETURN.md lines 21, 185-193, 202 |

---

## Part 4: coverage counts and what I could not check

Counts of items checked (each recomputed or grepped by me):
- M2 equations and derivations checked: 31 (all topics; all correct, with the Gamma != 0 generalisation needing A-4).
- M2 worked-example numbers recomputed: 118 (toy 3, Epps 12, shift model 10, units 12, MacKinnon 2, half-life 25,
  Monte Carlo 3, shares 16, trade 35: G, D*, 48 table cells, noise 6). Disagreements: none beyond Monte Carlo error.
- M2 verbatim quotes grepped against saved pages: 46 of about 55 (84%). Found: 45. Not found as written: 1 (A-1;
  paraphrase). Five more were found only across a line break or with a pdftotext glyph change and are genuine.
- M2 [unverified] items: 8, all correctly marked, none carrying a verdict alone.
- M2 leakage traps assessed: 22; two tests cannot detect their trap (A-2); two obvious traps missing (A-3, A-5).
- R3a numbers recomputed: 71 across sections 1, 2.3, 3.2, 4.2, 6.2, 7.2, 8.2. Disagreements: none.
- R3a source numbers and quotes grepped: 62 (Rechner-Poitras 15, Zhou 9, farmdoc 9, TAMU 10, Abdoh-Chitavi 15,
  Avileis-Swanson 1, Mitchell 2, Marowka 1). Found: 62.
- Calculators: M2_examples.py (237 lines) and M2_examples2.py (63 lines) compared against my independent results on
  every key used in the text; the HY overlap predicate and the Monte Carlo sweep are correct; the only text-code
  mismatch is descriptive (A-11).

Could not check, and why:
- ZS / ZM / ZL contract months: no saved page quotes a specification and the brief forbids cmegroup.com; left
  [unverified] as M2 has it (A-10).
- Zhou et al.'s price units: not stated anywhere in the saved text; the two consistent scalings are given in A-12,
  but which one Zhou used cannot be established from the page.
- Overnight quote-update gaps for the staleness bound in A-3: a data fact (DataFacts); I give the sensitivity as a
  function of the gaps, not a value.
- The [unverified] sources M2 lists (HY 2005, Mitchell via MDPI, Ericsson-MacKinnon, Kim-Silvapulle-Hyndman,
  Cardiff ORCA, Dobrev-Schaumburg, Hasbrouck 1995): no saved full text; none carries a verdict alone, so no fetch
  was made (fetching would have needed a disputed quote, which there was not).

Scratch: reports/stage_e32_briefs/review/work_A/recompute_A.py, recompute_A.json, log.tsv (no fetches).
