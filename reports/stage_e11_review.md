# Stage E.11 review

Two parts. Part 1 (this section) is the independent design review of docs/STAGE_E_ML_V2_DESIGN.md
(DRAFT). Part 2, the code review, is appended by CodeReviewer-FableXHigh.

---

# PART 1: design review (DesignReviewer-FableMax, 2026-10-03)

Reviewer: Fable 5.1 at max effort, spawned by the E.11 lead (brief:
reports/stage_e11_briefs/brief_design_review.md). I did not write anything I review here.

**Inputs read (by section, no market data, no Stage E result report, no progress.md, no .env):**
docs/STAGE_E_ML_V2_DESIGN.md (all 873 lines, in four chunks);
reports/stage_e11_briefs/prompt_findings.md (F1-F13 and the Task 1 list, verbatim);
docs/DECISIONS.md V18-V22 (lines 332-408); docs/STAGE_E_ML_DESIGN.md M1, M2, M6, M7;
docs/STAGE_E_DESIGN.md D2, D3, D4, D5, D6, D8, D9; reports/stage_e0_topstep_facts.json F5.x, F9.x,
F12.2a-h; rules/xfa_rules.py (XfaRules, XFA_50K, trail_mll_floor, reset_mll_after_payout,
max_position_micros); reports/stage_e11_runtime_probe.md; ml_route_v2/constants.py;
reports/stage_e11_interfaces.md; reports/stage_e11_STATE.md (all rulings sections);
reports/stage_e11_signal_coverage.md (counts only). Code was consulted only by grep, to check that
a design rule is implementable or matches constants.py: cpcv.py (_select, final_selection),
pipeline.py (where the risk table is computed), selection_metric.py (fixed D, zeros), payout_sim.py
(reset delay), targets.py (cost per contract), portfolio.py/sizing.py (caps),
screening/stage_e_frozen.py (ProductCosts depth term), ml_route/constants.py (v1 LGBM_FIXED).

**Rulings already made by the lead** (STATE.md Task 2 to 5 rulings) are not re-raised unless I say
the ruling is wrong or incomplete. I do that in D-04 (the "vol only, once" ruling, extended to the
sizing quantities inside the nested selection) and in D-14 (the Gate 0 canary reading).

## Summary of the ten checks

| # | Check | Result |
|---|---|---|
| 1 | Every free parameter a stated rule or a bounded training-window grid | Pass with findings: every literal in the draft is in constants.py and matches (one table of 70+ literals compared; no mismatch). Not yet stated in the draft: the aggregation rule of the nested selection and the "eligible on every fold" rule (D-07); the 4.0 leakage alarm is a rule without a stated source (D-15) |
| 2 | Trial count complete and the "not a trial" arguments sound | Pass with notes: N_total = N_program + 45 + \|A\| + \|B\| is complete for what the draft runs; the c/sigma filter, the risk table, the payout policy and the kill switches are correctly argued not to be trials (volatility, fixed rules, synthetic-data choices). Gaps: Gate 0 runs once on phase 1 and the draft does not say the phase-2 products are never audited (D-06); what v2 adds to the program's carried N is not stated (D-20); N_program = 198 is outside my boundaries to verify (D-20) |
| 3 | Success criteria fixed, achievable by a realistic system, arithmetic correct | **Fails on criterion 7** (D-01, BLOCKING) and on the research-window error-control statement (D-02, BLOCKING). The V2.0 arithmetic reproduces (table below); the joint power of the training-window verdict is unstated and is about a coin flip at S = 1.5 (D-09) |
| 4 | Nothing selects on Stage E results (V20) | Pass. Signal inclusion (all 54 families; 3 excluded for causality or coverage, with reasons), product inclusion (D2 vehicles, volatility-only filter, liquidity census and margin proxy), Gate 0's role (does not choose products), the phase-1 rule and the volatility proxy read no Stage E result. One structural note on the four already-owned stores (D-06) |
| 5 | Cost and risk constraints match the frozen rules; simulator never more generous; 150K honest | Pass with findings. D8 costs, D9.1 flatten, D9.3 floors, D9.5 lot-equivalent, D9.6 weights, D9.11 caps, D9.12 CPI window, the 2/3/5 scaling tiers, the trailing MLL and its $0 reset, the caps and DLL doubling, Standard and Consistency all match xfa_rules.py and facts F12.2a-c. The simulator plan is never more generous than the engine, given the combined-MLL audit. Findings: the per-contract slippage is calibrated at q_c and v2 sizes above q_c; D8's early-era re-check is not carried (D-08); the 150K figures are a lower bound from the 50K trade set, not labelled as one (D-10); the portfolio may sit at 95% of Maximum Position Size where the frozen encoding kept 50% (D-11) |
| 6 | Open points complete; nothing the user should own decided silently | Pass with gaps (D-16): every "Open" in V2.2 to V2.11 appears in V2.12; four alternatives named in the body are missing from V2.12, and five lead decisions the user should at least see are not listed |
| 7 | F1-F13 each a rule or a listed open point | Pass; table at the end. F1, F8 and F9 are rules whose coherence is the subject of D-01, D-03 and D-09 |
| 8 | Gate 0 bar fixed before data; coherent with the cost gate and the canaries | Fixed before data: yes (V2.2b, constants GATE0_*). Coherence: the Gate 0 multiple, the cost-gate reading and tau are three coupled open points presented as independent (D-05); the canary reading departs from F2's pre-cost wording (D-14) |
| 9 | Leakage by design | Pass on decision-time causality, normalizer, targets, purge and embargo, nested structure, window partition, M7.9 constants and the volatility proxy. One finding: sigma(p,h) and L(p,h) are computed once on the whole training window and then used to size trades inside the inner and outer test scoring (D-04) |
| 10 | What a quant would refuse to sign | D-01, D-02 (blocking); D-03, D-04, D-05 (should fix) |

## Recomputation of the draft's arithmetic (check 3)

All from the draft's own formulas; sqrt(252) = 15.8745.

| Item | Draft | Recomputed | Verdict |
|---|---|---|---|
| mu/day at S = 1.0, 1.5, 2.0, sigma $200 | $12.60, $18.90, $25.20 | 12.599, 18.898, 25.198 | correct |
| /month (21 d), 50K | $265, $397, $529 | 264.6, 396.9, 529.2 | correct |
| mu/day, 150K (sigma $450) | $28.35, $42.52, $56.70 | 28.347, 42.521, 56.695 | correct |
| /month, 150K | $595, $893, $1,191 | 595.3, 892.9, 1,190.6 | correct |
| 5 x 150K after 90/10 | $2,679, $4,019, $5,358 | 2,678.9, 4,018.2, 5,357.6 | $4,019 should read $4,018 (rounding of a rounded figure); trivial |
| eps $85/day at sigma $200 | S = 6.75 | 85 x 15.8745 / 200 = 6.747 | correct |
| F1's "near 3.5" (not in the draft) | - | at 10% ruin, fixed barrier: sigma = sqrt(2 x 85 x 2000 / ln 10) = $384/day; S = 85/384 x 15.87 = 3.51 | F1 reproduces; the draft shows only the fixed-sigma figure (D-09) |
| Ruin, fixed size, fixed barrier, ever | 0.28, 0.15, 0.08 | exp(-20 S / 15.8745): 0.284, 0.151, 0.080 | correct |
| Ruin within 252 dates, same model | not given | 0.235, 0.139, 0.078 | 10% needs S >= about 1.8 (D-01) |
| Ruin during the trailing phase (before the $0 lock), fixed size | not given | 1 - exp(-x/(e^x - 1)), x = 20 S/15.87: 0.39, 0.29, 0.20 | (D-01) |
| Minimum detectable S, t = 3 and 80% power | 2.75/3.52; 2.03/2.60; 1.37/1.75; 1.79/2.29; 0.80/1.02 | 3/sqrt(y) and 3.84/sqrt(y) at y = 1.19, 2.19, 4.82, 2.8, 14.2 | correct (calendar years; the probe's 1,248 trade dates would give 4.95 y and 1.35/1.73, immaterial) |
| Research-window power at t >= 1.0 | 0.74, 0.88 | Phi(1.5 x 1.091 - 1) = 0.738; Phi(2.182 - 1) = 0.881 | correct |
| at t >= 1.645 | 0.50, 0.70 | 0.496, 0.704 | correct |
| b at 50K and 150K | $115.47, $259.81 | 200/sqrt 3, 450/sqrt 3 | correct |
| Band lift of one trade's sigma | 1.15 x sigma_target | 2/sqrt 3 = 1.155 | correct |
| MinBTL at 45 configurations | about 5 years | [(1-g) Phi^-1(1-1/45) + g Phi^-1(1-1/(45e))]^2 = 2.236^2 = 5.0 y at E[max SR] = 1 | correct |
| Decision-time table from the rule | 7 rows | recomputed every row from O_X, F_X, 30-min steps | correct |
| Nested CPCV counts | 15 splits, 5 paths, 4 inner folds | C(6,2) = 15; each block tested in 5 splits | correct |
| PBO combinations | 12,870 | C(16,8) | correct |
| Family A tests | 66 x 3 = 198 | coverage report: 66 signals in REGISTRY | correct |
| V2.11 probe figures | 20.4 min, 3.1 GB, 60 MB; 46 min, 7.2 GB, 73% | runtime probe tables | match |

## Findings

Grades: BLOCKING (do not sign as written), SHOULD FIX (sign only with the change or an explicit
user decision), NOTE (record or clarify).

### BLOCKING

**D-01. V2.9 criterion 7 (ruin <= 10%) is near-vacuous under the draft's own sizing rule and does
not test what F1 means by ruin.**
- Problem. Criterion 7 reads "the probability of ruin, the MLL breached within 252 trade dates, is
  <= 10% at 50K and at 150K ... read with the kill switches OFF". Under V2.8, size is proportional
  to D and the loss cap n_loss = floor(0.25 x D_now / ((L + c) x tick)) stops every product from
  trading once D is small (for MNQ at h60 that is roughly D below $130; for full-size vehicles far
  earlier). A path that loses most of the MLL therefore stalls, unbreached, and counts as a
  survivor. An actual breach then needs a single contract's adverse excursion to exceed D, which is
  rare by construction. The event that ends the income, D falling to the KS2b level, is not counted.
- Evidence (the draft's own V2.0 model, fixed size sigma = 0.1 x D_0, drift mu = S x sigma /
  sqrt(252)): ruin within 252 dates is 0.235 / 0.139 / 0.078 at S = 1.0 / 1.5 / 2.0, so the 10% bar
  is met only from S of about 1.8 upward, not at the band's lower edge 1.5. During the trailing
  phase (floor below the $0 lock) the maximum at the first $2,000 drawdown is exponential with mean
  MLL x (e^x - 1)/x, x = 20 S / sqrt(252) (Taylor 1975, Lehoczky 1977), so the probability of
  breaching before the floor locks is about 0.39 / 0.29 / 0.20: F1's statement that the MLL binds.
  With D-proportional sizing, log D is a random walk with daily drift 0.0063 S - 0.005 and sd 0.10;
  the probability of ever reaching D < 0.25 x MLL is about exp(-2 x drift x ln 4 / 0.01) = 0.70 /
  0.29 / 0.12 at S = 1.0 / 1.5 / 2.0 (higher still during the trailing phase, when D is capped at
  the MLL from above), while a breach is structurally rare. So the written criterion passes at
  every S in the band and fails to reject a system F1 calls unviable; the economically meaningful
  figure at S = 1.5 is about 0.3, not under 0.1.
- Fix. Define ruin for criterion 7 as: the MLL breached, OR D at or below 0.25 x MLL (the KS2b
  level) at any close within the 252 dates, read with KS1, KS3 and KS4 off (KS2b's halt probability
  is already an output of payout_sim; reading it with the other switches off is the cheap form).
  Report the plain breach probability beside it. Add the figures above to V2.0 so the user sees
  that the 10% bar is not met by a fixed-size S = 1.5 system and that any pass at S = 1.5 comes
  from the sizing-down mechanics (the loss cap and the rounding band at small D), which V2.12 item
  11 currently presents as minor sizing constants. The same definition should drive the "ruin"
  column of every payout-simulation output.

**D-02. V2.9's research-window test states a Holm family it cannot satisfy; the error-control
statement contradicts its own pass bar.**
- Problem. "Holm family: the route's own, K = 10 (V21). One tested configuration, so Holm is trivial
  at alpha 0.05 / 10" sits beside the pass bar "one-sided daily t >= 1.0 (D5's screen level)". Holm
  at 0.005 one-sided rejects at t >= 2.58. On 1.19 years at S = 1.5 the power at t >= 2.58 is
  Phi(1.636 - 2.576) = 0.17, which is why the draft chose t >= 1.0; but then no Holm rejection is
  made, and the sentence claims one. A pre-registration cannot carry a self-contradictory
  statement of its family-wise error control, and a reader of V21 ("K = 10 ... the ML route kept")
  will expect the route to occupy a Holm slot with a real test.
- Evidence. Frozen D5 separates the screen (t >= 1.0, Tier A entry) from the edge claim (Holm
  rejection, composite verdict, DSR, t > 3, PBO). v1 M6 put the route's Holm test on the research
  window because v1 tested distilled rules there. v2 inverts the windows: the heavy verdict is on
  the training window (nested OOS), and the research window is a regime guard. The draft kept M6's
  Holm words without the test that gives them meaning.
- Fix. Decide, and write, which of two structures the route uses (the user owns this):
  (a) the research-window test is a screen only; v2 makes no Holm claim there; its confirmatory
  control is the DSR at N_total on the nested OOS record plus the registered holdout-2 read, whose
  criteria the registration fixes; then say explicitly that the route's slot in V21's K = 10 is
  unused on the research window (a DECISIONS entry, not an edit of frozen text); or
  (b) the research-window bar is the Holm level (t >= 2.58 at 0.05/10), accepted as a low-power
  gate with the power stated (0.17 at S = 1.5, 0.35 at S = 2.0). Add the choice to V2.12 item 14.
  (a) matches F5 and the draft's own reasoning; either way the current sentence must go.

### SHOULD FIX

**D-03. V2.8: the per-trade risk budget allows a daily sigma up to 1.7 x the F8 target.**
- Problem. b = sigma_target / sqrt(m) with m = 3, "the cap on simultaneous positions", and the draft
  claims "If the day's trades are about independent, the daily sigma is about sigma_target". That
  holds only for exactly three trades a day. V2.2 allows three decision times and the h60 and h120
  positions close before the next decision time on every group (t2 - t1 is 60 to 150 minutes), so
  a day can hold up to 9 trades at risk b each: daily sigma up to sqrt(9) x b = 1.73 x
  sigma_target, or 0.17 x D, and 0.20 x D with the rounding band. KS1 at -0.30 x D_open is then a
  1.5-sigma event (about 7% of days) rather than the 3-sigma event the thresholds imply, and the
  V2.0 ruin arithmetic (sigma = 0.10 D) understates the risk the rule can take.
- Evidence. V2.2: "At most 3 entries per product per trade date"; V2.8: "at most 3 in all"; the
  decision table: equity 09:00, 11:00, 13:00 with h60 exits at 10:00, 12:00, 14:00.
- Fix. Replace the fixed divisor with a daily risk budget: each accepted trade consumes
  (n x sigma(p,h) x tick)^2 of sigma_target^2, and no entry is accepted once the day's budget is
  spent (a stated rule, no new parameter). Alternatively m = 9 (then b = $66.67 at 50K and most
  full-size vehicles are untradeable at 50K; the band would then dominate sizing, which is worse).
  State the result in V2.0: with the budget, daily sigma <= sigma_target by construction.

**D-04. V2.8 and V2.9: sigma(p,h) and L(p,h) are estimated on the whole training window, test
blocks included, and then size the trades scored inside the nested CPCV.**
- Problem. The Task 3 ruling accepted "c/sigma filter on the whole training window once (vol only)".
  For the binary admissibility that is harmless. But the same risk table (interfaces section 4,
  pipeline.py stage 2) feeds score_split, which sizes every trade in every inner fold and every
  outer test block from sigma(p,h) and L(p,h) that already contain that block's volatility. A
  volatility episode inside a test block (March 2020 is in some block) raises sigma(p,h) and
  L(p,h) for the whole window and shrinks the size on that block by foresight. The nested OOS
  record, which every verdict reads (t, DSR, PBO, Sharpe, ruin), is therefore mildly optimistic on
  drawdowns. It is level information under M7.9's convention, but M7.9 allows it because it is
  "charged identically at the test"; here it is estimated on the test blocks themselves.
- Evidence. V2.8: "sigma(p,h) the training window's gross h-return sd in ticks (V2.2's filter
  quantity)"; V2.9 selection metric: "built with V2.7 and V2.8". pipeline.py line 20: "filter:
  c_sigma_table and risk_table on the training rows (once, volatility only)".
- Fix. Compute the risk table per outer split from that split's training blocks (and per inner fold
  from the inner training blocks), and the frozen risk table from all six blocks for the final
  model and the research-window test. It is a cheap recomputation (filter stage 0.2 s). Keep the
  admissibility filter as ruled, once on the whole window, and say that the two differ on purpose.

**D-05. V2.2, V2.2b, V2.7: the Gate 0 multiple, the cost-gate reading and tau are one coupled
decision presented as three independent open points.**
- Problem. tau = 0.10 is derived from "the loosest cost gate (V2.7, k = 1.5) needs a predicted
  gross of 2.5c", the literal reading. If the user takes the alternative reading (gross > k c), the
  same derivation gives tau = 0.25 / 1.5 = 0.167, and Gate 0's 1.5c bar coincides with the loosest
  hurdle instead of sitting 1.0c below it. Under the literal reading, the k = 2 and k = 3 hurdles
  (3c and 4c) exceed the draft's own "strong signal" reach of 0.25 sigma for every pair with c/sigma
  above 0.083 and 0.0625, so a third of the 45 configurations will often fail the 30-trade
  eligibility: harmless for honesty, but the trial count carries configurations that cannot trade,
  and the user is not told. The gap between Gate 0's 1.5c and the gate's 2.5c is also what makes
  the "passes Gate 0, nothing trades" outcome possible after phase 2 has been bought.
- Evidence. V2.2 "Why 0.10" paragraph; V2.7 "the gross must exceed (1 + k) c. Open: the alternative
  reading, gross > k c"; V2.12 items 1, 7 and 10 listed separately.
- Fix. Merge items 1, 7 and 10 into one decision with both consistent sets written out: literal
  reading: hurdles 2.5c / 3c / 4c, tau 0.10, Gate 0 at 2.5c (or 1.5c with the gap stated); gross
  reading: hurdles 1.5c / 2c / 3c, tau 0.167, Gate 0 at 1.5c. Recommend the gross reading: it is the
  usual quant formulation, it aligns Gate 0 with the loosest hurdle, and it keeps the k = 3
  configurations alive at IC 0.10.

**D-06. V2.1: the price path of the already-owned exposures is not fixed, and may differ between
phase 1 and phase 2; Gate 0's run-once status is not stated.**
- Problem. The universe table fixes the price path as the full-size contract (CL, NG, GC, HG), "v1's
  ML-A07 rule". The phase-1 plan then says the owned step 2 stores "of MCL, NG, MGC and MHG (E.5)"
  are "used first ... where they cover the exposure's training window from its own S_X", with the
  full-size path "bought only if budget remains". So phase 1 would run Gate 0, the normalizer and
  the model on MCL, MGC and MHG bars, from the micro's own S_X (a micro's start rule can land years
  after 2019-05-06), and phase 2 may switch those exposures to CL, GC and HG bars. A price-path
  switch changes every feature, sigma_X,d, the risk table and the Gate 0 result for those pairs;
  the Gate 0 pass would not transfer. Separately, the draft never says that Gate 0 runs once (on
  phase 1) and that the phase-2 products enter V2.6 without an audit; that is the right reading of
  N_total but it must be written, and the c/sigma filter must be stated as re-applied to phase 2.
- Evidence. V2.1 lines "Each exposure's price path is the full-size contract where one is
  permitted" versus "History already owned costs $0 and is used first".
- Fix. Fix the price path per exposure once, before Gate 0, in the table: either the owned micro
  store (then say so in the table and keep it in phase 2, with its S_X) or the full-size contract
  (then the owned stores are not price paths and phase 1 buys CL, GC and HG under the ranking).
  Add one sentence: Gate 0 runs once on the phase-1 products; phase-2 products are filtered by
  c/sigma, not audited; N adds the phase-1 Gate 0 tests only.

**D-07. V2.9: the aggregation of the selection metric across folds and splits, and the
"eligible on every validation set" rule, are fixed in code but absent from the draft.**
- Problem. The draft says each configuration "is scored on the inner folds by the selection metric"
  and the final configuration is "chosen by the same metric over the 15 outer splits", without
  saying how four fold scores or fifteen split scores become one number. cpcv.py fixes it: the
  mean of the per-fold (per-split) daily Sharpes, and a configuration is eligible only if it has
  >= 30 trades and a finite score on EVERY fold (every one of the 15 outer splits for the final
  model). An aggregation rule left to the code is a free parameter that could be "chosen later by
  looking" if the code changed; and the every-split rule has a consequence the user should see: a
  configuration that trades sparsely on one block (a k = 3 configuration, a long-horizon one) can
  never be the frozen model, and if no configuration is eligible on all 15 splits the route has no
  model.
- Evidence. cpcv.py line 21 "it is eligible only with >= MIN_TRADES trades and a finite score in
  every fold; the best mean inner score wins"; _select: "Best mean score among configs eligible on
  every one of n_required validation sets"; final_selection docstring.
- Fix. Write both rules into V2.9 (mean of fold Sharpes; eligibility on every fold and every outer
  split; the no-model outcome is a fail), and add the choice "every split versus a majority of
  splits" to V2.12 item 14 if the lead wants the user to own it.

**D-08. V2.5, V2.7: cost fidelity. The per-contract slippage is D8's figure at q_c, and D8's
early-era re-check is not carried into an edge claim made on 2019-2024.**
- Problem. (a) "c is that row's D8 round trip at size 1" is per contract, with s_b + the depth term
  calibrated at D2's q_c (stage_e_frozen ProductCosts: "depth term at q_c"). The frozen catalog
  never traded above q_c; v2 can (10 micros of MCL or MGC at 150K, where b = $260 and an MCL
  h60 sigma of about $60 gives n_risk = 4 against q_c of about 2). Above q_c the depth term is
  understated; the engine charges per contract the same way, so the plan is "never more generous
  than the engine" per contract, but the engine was never asked for these sizes. (b) D8: "calibrated
  on 2025-26 books, the model understates costs in thinner earlier years. That is conservative for
  a null claim and not for an edge: any member that passes confirmation gets a period-appropriate
  cost re-check before discussion." v2's training-window verdict is an edge claim on 2019-2024 at
  2025-26 costs; the re-check is not in V2.9. The paper-trading 1.25x test is forward-looking and
  does not repair the backtest.
- Fix. (a) State the rule for n > q_c: cap n at q_c per vehicle, or add (n - q_c)/n ticks per side
  for the contracts beyond q_c (the D8 form of the depth term), chosen now. (b) Add a fixed cost
  sensitivity to the verdict's reporting: the nested OOS record re-priced at 1.5 x slippage (a
  stated multiplier, not tuned), reported beside every criterion, with D8's re-check named as the
  source; the registration can then say whether a pass must survive it.

**D-09. V2.0 and V2.9: the joint power of the training-window verdict is not stated, and the
success band's lower edge is close to a coin flip.**
- Problem. F1 asks for criteria "a realistic system can meet". On 4.82 years at true S = 1.5:
  criterion 2 (t >= 3) has power Phi(1.5 x 2.195 - 3) = 0.61; criterion 5 (S_hat >= 1.5) has power
  0.50 by construction; since t >= 3 is S_hat >= 1.37 on this length, the two together have power
  0.50. Criterion 3 (DSR > 0.95 at N_total of about 525) adds an unknown haircut: with the trials'
  Sharpe sd at 0.3 or 0.5 annualized, SR0 is about 3.07 x sd = 0.92 or 1.53, and the pass needs
  S_hat of about 1.67 or 2.28 (illustration only; the draft rightly says the variance is unknown).
  Criterion 7 is D-01. At S = 2.0 the joint power of criteria 2 and 5 is about 0.86 before DSR and
  ruin. So a realistic system at the band's lower edge fails more often than it passes, and one at
  V22's realistic middle (S about 1.2) has power about 0.25 on criterion 5 alone. The draft also
  shows the eps line only at a fixed $200 sigma (S = 6.75) and never reproduces F1's "near 3.5"
  (the free-sigma figure at 10% ruin), so a reader sees a conflict with the prompt that is only a
  difference of sizing assumption.
- Fix. Add a power paragraph to V2.9 (criteria 2 and 5 at S = 1.5 and 2.0; the DSR illustration
  with two assumed sd values; the ruin figures of D-01), and say plainly that the band's lower edge
  is a coin flip. Either accept that or drop criterion 5 as redundant with t >= 3 (it adds only
  1.37 -> 1.50) and let t >= 3 and the DSR carry the bar. Add F1's 3.5 beside the 6.75 in V2.0 with
  the one-line reconciliation (sigma free at 10% ruin versus sigma fixed at 0.10 x D).

### NOTE

**D-10. V2.8, V2.9: the 150K figures are a lower bound built from the 50K trade set; label them.**
The engine runs at 50K; the payout simulator re-sizes the 50K trip records under 150K parameters.
Trades that only 150K sizing would have taken (n_risk = 0 at 50K, n >= 1 at 150K) are absent, the
CPI micro cap used is 3 (150K: 9, D9.12), and the D9.11 caps and scaling tiers are 50K's. All
conservative; the draft calls the tiers conservative but does not call the whole 150K figure a lower
bound on income and a figure with a different trade set for ruin. Say so in V2.9 and V2.12 item 12.

**D-11. V2.8: the portfolio cap of tier minus 0.1 lot leaves a 5% margin to Maximum Position Size
where the frozen D9.5 encoding kept 50%.** D9.5 encoded "every member's size is at most 1
lot-equivalent, half the XFA's starting 2-lot maximum, so no member ever trades full maximum
position size, into news or otherwise". v2 is within the letter (never at full size) but an account
holding 1.9 of 2 lots through a scheduled release is the situation D9.5's margin existed to avoid.
Item 11 lists the 0.1 lot as open; add the compliance reading and one alternative (no new entry
whose fill is within [release - 5, release + 30) when open lot-equivalents exceed half the tier).

**D-12. V2.6: three stale or inaccurate statements.** (a) "with under 100 columns" contradicts V2.3's
154 model columns (the Task 2 ruling corrected V2.3 only). (b) "reusing ml_route/lgbm.py's fixed
settings where they apply" is wrong: v1 LGBM_FIXED is learning_rate 0.03, 400 rounds, feature and
bagging fraction 0.8, max_depth -1; v1's grid has min_data_in_leaf {500, 2000} and lambda_l2
{1, 10}. v2's 0.02, 300, 0.7, 0.7, 2000 and 100 are new literals. They are fixed in constants.py and
not tuned, so there is no leakage issue; the provenance claim should go. (c) min_data_in_leaf 2000
on a phase-1 inner-fold training set of roughly 12,000 rows allows at most six leaves, so the
depth-3 challenger cannot grow its 8 leaves at phase-1 scale; say that the two LightGBM
configurations are near-degenerate until phase 2.

**D-13. V2.9 "Partition of the training window (v1 M7.3, kept)" is a change, not a keep.** v1 M7.3
used the first five blocks for CPCV (10 splits) and reserved block 6 for M5's pre-test; v2 uses all
six (15 splits, 5 paths) because M5 is replaced. Label it as the change it is; the block cut rule
itself (calendars only, floor(n/6), remainder to the last) is kept.

**D-14. V2.2b: the effective Gate 0 bar and the canary reading.** (a) With about 282 tests in the
Holm family, the first rejection needs p <= 0.05/282, one-sided z >= 3.57 (two-sided for family A,
3.73); bar 2's t >= 3 is dominated and the user should know the operative bar is about 3.6.
Including family A (198 of the 282 tests) moves it from 3.24 to 3.57, which is the real content of
"whether family A counts in Holm". (b) The prompt's canary sentence, "an edge smaller than the cost
must pass Gate 0 and then be rejected by the cost gate", is literally impossible under a 1.5c bar;
the lead read it as "below the gate's hurdle, above Gate 0's bar" (STATE design choice 2). That is
a fair reading of the Task 1 bar, but F2 calls Gate 0 a "pre-cost" audit of "gross (pre-cost)
out-of-fold predictive power", under which Gate 0 would have no cost multiple at all (bars 2 to 4
only) and the prompt's sentence would be literally true. Make that alternative explicit in V2.12
item 1 so the user chooses between a pre-cost audit and a cost-relative one.

**D-15. V2.0: the 4.0 leakage alarm has no stated source.** It is a rule, fixed before data, so it is
admissible; give its reason in one line (above F1's 3.5, the figure F1 says only HFT clears, and
above the band's 2.5 ceiling), so it is traced like every other literal.

**D-16. V2.12 gaps.** Named in the body but missing from V2.12: the t >= 1.645 research-window
alternative (V2.9); the paper-trading cost tolerance 1.25 x D8 (V2.9); "the generic list" (V2.3, only
implicit in item 8); the research-window warm-up rule sits under item 8 (signals) rather than its own
item. Decided by the lead and not shown to the user, acceptable as design but they should appear in
a "lead decisions, not open" list so nothing is silent: the selection metric (fixed D at the 50K
MLL, daily Sharpe with zeros, 1.0 x D8), fitting on the gross normalized target with the cost gate
after, the DSR Sharpe variance taken over the 45 configurations, the research-window test at 50K
constraints only while the plan is 5 x 150K, and the tie-break order.

**D-17. V2.11: the 2010 extension is costed in time only.** The probe says memory is the binding
limit (7.2 GB at 28 products, 2.4 GB of it bars). Tripling the dates triples the bars and the engine
frames; "about 2.5 h ... still one window" is right on time and silent on memory. State that the
extension runs per product or per path in separate processes, or in date chunks.

**D-18. V2.4: the list of research-window-derived constants is short by two.** M7.9's list (D8 costs,
q_c, r_c, S_X) is reproduced; v2 adds the frozen D1 ADV census (2026 January-August) and, if chosen,
E|m_1| for the purchase ranking. Both are level information used before any training bar is read
and are fine under the convention; list them so the convention's inventory is complete.

**D-19. V2.2: gold and copper decision times fall after the day-session settlement.** D6's C is 12:30
for gold and 12:00 for copper; t3 is 12:50 and 12:40, and the h60 and h120 exits run to 14:50. Rates
and FX (C 14:00) also exit after C at t3 + 120. The D8 bucket costs cover these hours and the cost
gate will mostly refuse them, so this is a statement to add, not an error: the clock uses O_X and
F_X only and deliberately ignores C_X.

**D-20. Trial-count bookkeeping.** (a) N_program = 198 "after E.9" is outside my boundaries
(progress.md and docs/STAGES.md) and is not verified here; the lead's number verifier should read it
from the ledger at the freeze, as constants.py's comment says. (b) The draft states N_total for the
DSR but not what v2 adds to the program's carried N for later stages (45 + |A| + |B| on the training
window, plus 1 for the research-window test if it is counted as a tested rule under v1 M6's logic).
State it; the invariant "every screened hypothesis adds to it" needs a number.

**D-21. V2.9 criterion 2 reads the procedure's record; F4 names "the final configuration".** The
nested OOS record is the honest estimate of the selection procedure and is the right basis. But
different splits may select different configurations, so the record is not the final
configuration's own performance. Report, beside criterion 2, the final configuration's own CPCV
out-of-sample t and Sharpe (its column of the PBO matrix), so F4's wording is also answered.

**D-22. V2.9: the DSR Sharpe variance over the 45 configurations.** It is the program's convention
(D5 uses a Tier A's Sharpes the same way) and the Task 3 ruling fixed its form. Two directions of
bias worth one sentence: the 45 share fits and are highly correlated, so their Sharpe variance
understates the variance of 525 independent-ish trials (lenient); the nested CV already removes the
selection bias within the 45, so counting the 45 in N as well is conservative. Neither needs a
change; both should be written so the DSR figure is read correctly.

**D-23. V2.0 rounding.** "$4,019" in the 5 x 150K column at S = 1.5 is $4,018 from unrounded inputs
(892.94 x 4.5 = 4,018.2). Trivial; fix when the table is regenerated.

**D-24. V2.4: the research-window-only warm-up alternative costs power the draft does not state.**
With 80 to 140 of 299 dates lost, the window is 0.63 to 0.87 years and the power of t >= 1.0 at
S = 1.5 falls from 0.74 to about 0.58 to 0.66. Add the figure to item 8 so the choice is informed.

## F1-F13 in the draft

| F | Finding (short) | Where in the draft | Verdict |
|---|---|---|---|
| F1 | MLL binds; economics at S 1.0/1.5/2.0 and against eps; band 1.5-2.5 | V2.0 table, ruin formula, band; V2.9 criterion 5 | Rule. Arithmetic correct. Coherence findings D-01 (ruin criterion vacuous), D-09 (power at the band's lower edge; F1's 3.5 not reproduced) |
| F2 | Gate 0 first; fail means stop | V2.2b; V2.1 phase 2 conditional | Rule, fixed before data. Coupling with the cost gate open (D-05); pre-cost versus cost-relative alternative to list (D-14) |
| F3 | Ridge primary, shallow LightGBM only challenger, no LSTM | V2.6 | Rule. Depth {2,3} within "at most 3 or 4"; elastic net dropped with a stated reason. Provenance text wrong (D-12) |
| F4 | Nested CPCV with purge and embargo, PBO by CSCV, DSR at full N, t >= 3 | V2.9 | Rule. Partition relabel (D-13); final-configuration reporting (D-21); Holm sentence (D-02) |
| F5 | Power; MDS per data length; selection on the pooled training history | V2.0 table; V2.9 | Rule. Table correct. Joint verdict power unstated (D-09) |
| F6 | Holds >= 60 min, 1-3 fixed decision times, fixed horizons or flatten, c/sigma filter with stated threshold | V2.2 | Rule. tau derivation couples to the cost-gate reading (D-05); post-settlement times to state (D-19) |
| F7 | Cost gate k in {1.5, 2, 3} by nested CPCV | V2.7 | Rule plus open reading (item 10). Coupled decision (D-05) |
| F8 | Sizing by drawdown distance; 0.10 D daily sigma; 0.25 D per trade; size down after payout | V2.8 | Rule. Daily sigma not bounded as claimed (D-03); sizing down is what makes the written ruin criterion vacuous (D-01) |
| F9 | Payout mechanics simulated from the facts file | V2.9 payout simulation; V2.8 reset | Rule. Mechanics match xfa_rules.py and F12.2a-c. Ruin definition (D-01); 150K lower-bound label (D-10) |
| F10 | Five kill switches with thresholds | V2.8 table; item 13 | Rule plus open thresholds. KS1's coherence with the daily sigma (D-03) |
| F11 | Five copied accounts are one bet | V2.0, V2.8 cluster cap, V2.9 "one draw" | Rule |
| F12 | Live Funded prohibits API automation; recorded as a deployment risk | V2.12 item 18; V2.10 | Listed open point, with F12.2g quoted |
| F13 | No tick or order-book data; one-minute bars | V2.1 purchase plan | Rule |

## Overall verdict

The draft is a serious pre-registration: every literal it uses is in ml_route_v2/constants.py and
matches, its arithmetic reproduces, its leakage controls are v1's in full plus sound additions, it
selects nothing on Stage E results, and its Topstep mechanics match the frozen engine and the facts
file. It should not be signed as written, for two reasons that go to what the verdict means rather
than to any computation: criterion 7 counts an MLL breach as ruin while the F8 sizing rule makes
breaches structurally rare and lets a path that has lost three quarters of the MLL count as a
survivor (D-01); and the research-window test claims a Holm family at K = 10 while passing at a bar
Holm would not accept (D-02). Both are fixable in a session: a redefinition of ruin to the KS2b
level with KS off, and a decision on which test carries the route's family-wise control. Of the
seven should-fix items, three are honesty-of-estimate points (the risk table estimated on the test
blocks, D-04; cost fidelity above q_c and D8's early-era re-check, D-08; the unstated joint power,
D-09), two bind open points together that the user would otherwise decide inconsistently (the Gate
0 multiple, the cost-gate reading and tau, D-05; the price path of the owned stores and Gate 0's
run-once status, D-06), one writes into the draft rules the code already fixes (the selection
aggregation and the every-split eligibility, D-07), and one corrects a false claim in the sizing
rule (daily sigma, D-03). With D-01 and D-02 resolved and the should-fix items either changed or
placed before the user as decisions, the design is signable; the notes are for completeness and
can be taken at the freeze.

---

# PART 2: code review (CodeReviewer-FableXHigh, 2026-10-03)

Reviewer: Fable 5.1 at xhigh effort, spawned by the E.11 lead (brief:
reports/stage_e11_briefs/brief_code_review.md). I did not write anything I review here. Written
incrementally as each check completes; a section marked (in progress) was cut short.

**Scope:** ml_route_v2/ (all modules), tests/test_ml_v2_*.py, tests/ml_v2_fixtures.py, the key fix
(commit 5931e30: data/config.py, tests/test_stage_e_config_keys.py). Contracts:
reports/stage_e11_interfaces.md; design: docs/STAGE_E_ML_V2_DESIGN.md V2.2-V2.9; frozen engine and
rules read by line range. No market data, no Stage E result reports, no progress.md, no .env.
Mutation copies live only in the scratchpad (RAM tmpfs), never in the repo.

**Known items not re-raised** (ruled, reports/stage_e11_rulings.md and the brief): C-1 ridge
extrapolation (strict xfail), S-1 across-date shuffle null, the PENDING per-split risk table on the
engine schedule (reviewed for dependents only, under check 2).

**Inputs read (by section; no market data, no Stage E result report, no progress.md, no .env):**
ml_route_v2/: constants, clock, normalize, targets, panel, cost_filter, signals/{__init__, _core,
_daily, _events, generic, k2, k4, ports} (whole), k8 (docstring), configs, models, cpcv, gate0,
decide, selection_metric, account, sizing, portfolio, killswitch, simulate, payout_sim,
engine_stage, pipeline (whole), synthetic (docstring, plants, world), probe (outline). Tests:
test_ml_v2_{simulate, payout, leakage, cpcv (outline and lines 132-172, 500-559)}, ml_v2_fixtures
(whole), test_ml_v2_e2e (assertions), test_stage_e_config_keys (whole). Frozen code by range:
screening/stage_e_rules.py 278-336 and 505-576, stage_e_frozen.py 82-128 and 278-280,
stage_e_engine.py 69-72, 405, 440-470, 509; rules/products.py 66-100, 225-229;
rules/constraints.py 30-43; rules/xfa_rules.py (outline, XFA_50K 135-159); funnel/
multiple_comparisons.py signatures; ml_route/accounting.py moments; strategy/members/k4
{eiafade 49-58, apipre 52-54, ovr 76-80}; reports/stage_e0_topstep_facts.json (150K, F9.1, F12.2
rows by grep); docs/STAGE_E_ML_V2_DESIGN.md 637, 672-675; git show 5931e30 -- data/config.py.

**Test run** (brief): `nice -n 10 uv run pytest -q tests/test_ml_v2_*.py
tests/test_stage_e_config_keys.py` -> **717 passed, 1 xfailed in 300.07 s** (the xfail is the
registered C-1 ridge item). Log: scratchpad/pytest_mlv2.log.

**Id note.** My ids are C-01 .. C-12 (two digits). The lead's "C-1" (ridge extrapolation, the
strict xfail) is the Task 5 item in the rulings and is not re-raised here.

## Summary of the nine checks

| # | Check | Result | Where the evidence is |
|---|---|---|---|
| 1 | Causality: signals, normalizer, targets, selection | **pass** | Section "Check 1" below; 19 signals read, none breakable; 2 real library leaks planted in the scratchpad were caught (m8, m9) |
| 2 | CPCV purge, embargo, 15 splits, 5 paths, inner isolation, resumability | **pass**, one resumability gap (C-01) | cpcv.py 171-222, 226-294, 552-577; tests pin 15, combinations order, embargo dates, 5 paths, 30 units |
| 3 | Simulator = frozen engine except V2.8 | **pass**; hand-computed day recomputed to the cent | simulate.py 137-180; stage_e_rules.py 524-529 are the only `run.traded` reads inside the view; stage_e_frozen.py 278-280 ceil |
| 4 | Payout simulator = xfa_rules and facts | **pass**; all four sequences recomputed by hand | payout_sim.py 216-240, 262-392; account.py 74-121; facts rows 70, 90-92 |
| 5 | Canaries fail when the guard is removed | **pass**, 9/9 mutations caught, control 11/11 | Mutation table below |
| 6 | Key fix | **pass**, two notes (C-10) | data/config.py 140-143, 164-187; tests scrub KEY1/KEY2/LEGACY first; callers zero-argument |
| 7 | Determinism | **pass**, one note (C-07) | models.py 63-68, 71-83; payout_sim.py 487-500; e2e determinism test |
| 8 | Trial accounting | **pass**, one note (C-08) | configs.py 166-209; cpcv.py 521; gate0.py 172-178, 239-245, 306-313; pipeline.py 355 |
| 9 | Silent failures, units, time zones | 4 notes (C-03, C-05, C-06, C-09), no bare except | grep: no `except:`/`except Exception` in ml_route_v2 |

## Check 1: causality, signal by signal

Read against the contract "bars with ts_event <= t - 60 s, calendars known in advance":

- Shared: `BarArrays.last_closed` (signals/_core.py:112-115) is `searchsorted(ts, t - 60 s,
  right) - 1`; `result()` (359-367) stamps not-applicable rows at t and missing ones at -1;
  `apply_event` (404-414) admits an event only with `ev_avail <= t`; `assert_causal`
  (signals/__init__.py:122-141) checks the self-reported `avail`, and `build_panel` re-checks
  `max(avail) <= decision_ts_ns` on kept rows (panel.py:116-117). `assert_causal` therefore
  guarantees nothing about a signal that lies about `avail`; the guarantee rests on the code of
  each `fn` plus the perturbation control (tests/test_ml_v2_leakage.py:196-199), which m8 and m9
  show is sharp.
- sigma_X,d (signals/_daily.py:138-151): `k = searchsorted(comp, arange(n))` counts complete
  dates strictly before d; avail = close of the latest of them. G9's rolling median (122-123)
  is over already-causal sigmas. The same-day `hi`, `lo`, `c1_close` of `Daily` are indexed
  only at the previous port-complete day (ports.py:181-194, `side="left") - 1`).
- Normalizer (normalize.py:26-59): the window is `[max(i - 250, 0), i)` in the root's own row
  dates, so date i never enters its own statistic; warm-up by date count; sd 0 handled.
- G1-G3 (generic.py:106-119): `it = at(t - 1 min)`, `ik = at(t - 1 - k min)`, both closed by t.
  G4 (122-133), G7 (203-215): first bar to `it`. G5 (146-164): O bar of d vs C-1 of the previous
  trade date, avail O + 1 min <= t1 = O + 30. G6 (180-200), G10 (247-264): bars with ts in
  [t - 60/30 min, t - 1 min]; the base is `rolling(20).shift(1)` over the previous row dates at
  the same t_index (167-177). G8 (218-230): latest complete date strictly before d. G9 (233-244):
  `sigma_avail`. G13-G15 (289-312): release calendar, known in advance. G16: calendar.
  G17 (339-356): `last_closed(t)` on the lead, 60 minutes back from that bar, both on the row's
  trade date, avail = that bar's close; own cluster not applicable.
- K4 (k4.py): apipre reads W-1's 15:24 and 15:39 closes and stamps 07:30 of W (conservative,
  apipre.py:52-54); eiafade reads T_W - 1 and T_W + 14 (eiafade.py:49-50) and stamps T_W + 15;
  eiamom 09:29 and 09:59, stamped 10:00; ovr: slots tau with r from bars at tau - 60 and tau - 1,
  avail tau, `slot_rows` takes the latest slot with avail <= t (_events.py:81-96); the reference
  dates are strictly before d (ovr.py:76-80).
- K2 (k2.py): fixed clocks from literal tables; predrift reads 08:30 open and 08:49 close,
  stamped 08:50. CP1-CP3 (ports.py): O + 29 close vs the first bar, stamped O + 30; opening range
  stamped O + 15; the breakout close is the last bar closed by min(t, C); CLV from the previous
  day.
- Targets (targets.py:173-210) are labels, forward by construction; their exit_ts feeds the
  purge. The entry is the open of the bar opening at t, deferred by the D9.5a guard exactly as
  the engine defers (136-160); hF is the open of the bar at F_X, which is the engine's forced
  flatten fill (stage_e_engine.py:405, 509 fill at `bar.open`; the closure-print exception at
  443 cannot arise because the clock excludes those dates). Costs read the fill minute's bucket
  with the D8 event flag; `minute_table` is valid because `bucket_at` keys on the CT minute only
  (stage_e_frozen.py:113-128) and `minutes_after_midnight_ct` converts with tz (clock.py:222-225).
- Units: `per_unit = 1 / (vendor_price_factor x tick_size)` (signals/_core.py:288-299) is the
  right direction for "bars arrive in vendor units, factor x exchange units" (rules/products.py:
  71-72); ticks x tick_value_usd = $ everywhere in portfolio.py and payout_sim.py.
- Selection (cpcv.py:581-596, 666-672): the inner records only; the outer records enter
  `final_selection` by design (V2.9) and the nested OOS record is `_path_series` of the per-split
  selected config's outer record (607-614).

Verdict on check 1: no value used at t depends on a bar closing after t, a release after t, a
same-date normalizer row, or a test-fold outcome.

## Check 3: the hand-computed day, recomputed from the frozen table

Script in the scratchpad (not the test): `load_frozen_tables().costs`, `slippage_cents`,
`leg_inputs`. Buckets MNQ 09:00 buy 0.9031496008866111, MNQ 10:00 sell 0.8278767445171111,
MGC 09:30 sell 1.0264453952502222, MGC 10:30 buy 1.0290423222583334; commission per side 61 / 96
cents; q_c = 1 for both; tick values 50 / 100 cents.
- MNQ buy 3 at 09:00: ceil(3 x 0.9031496 x 50 = 135.47) = 136, + (3 - 1) x 1 tick x 50 = 100 ->
  236; commission 183.  MGC sell 2 at 09:30: ceil(205.29) = 206 + 100 = 306; commission 192.
- MNQ sell 3 at 10:00: ceil(124.18) = 125 + 100 = 225; gross 3 x 41 ticks x 50 = 6,150.
  MGC buy 2 at 10:30: ceil(205.81) = 206 + 100 = 306; gross 2 x 47 ticks x 100 = 9,400.
- Nets 5,323 and 8,404 cents; day 13,727 = $137.27; floor max(-200,000, min(13,727 - 200,000,
  0)) = -186,273. Sizes: b = 200 / sqrt(3) = 115.47; MNQ floor(115.47 / 35) = 3, loss cap
  floor(500 / 51.5) = 9; MGC at D_now 1,995.81 (balance -4.19, unrealized 0 because the 09:29 bar
  still prints 8000, floor -2,000): floor(115.47 / 50) = 2, loss cap floor(498.95 / 103) = 4.
  Budget 105^2 + 100^2 = 21,025 <= 40,000.
Every figure equals tests/test_ml_v2_simulate.py:267-279. The equivalence test (150-172) runs
the member's intents through the unmodified `StageERules` and compares ledger, final state and
counters, with a roll date, fill-guard deferrals, event-window fills, forced flattens and the CPI
cap exercised; test 184-199 shows every fill above q_c differs from the frozen one by exactly
(qty - 1) x 50 cents of slippage and in nothing else. `PortfolioRules` overrides exactly
`_opening_refusal`, `fill_cost`, `close_cost` (pinned by sha256, 112-124); of the six
`run.traded` reads in the frozen rules, the view intercepts only lines 524 and 527
(stage_e_rules.py); `_settlements` (315-321), `account_view` (439), `structural_refusal` (482)
and `gate` (563) read the real run. The cost override only adds (simulate.py:160-168). The
simulator is never more generous than the frozen engine.

## Check 4: the payout sequences, recomputed

From account.py (XFA_50K in dollars: MLL 2,000, lock 0, post-payout floor 0, caps 2,000 /
3,000, x2 with DLL, 50% ceiling, $125 minimum, 5 x $150 / 3 days 40%, 90/10) and run_path:
- STANDARD, keep 0: winners d1, d2, d4, d5, d6 (d3 = 100 is not) -> request d7 min(2,000,
  542.50, 1,085) = 542.50, net 488.25; balance 542.50, d7 +200 excluded -> 742.50; d8 149.90 not
  a winner; five more -> d14 min(2,000, 821.20) = 821.20, net 739.08 -> 871.20. Floors -1,800,
  -1,650, -1,550, -1,250, -1,090, -915, then 0.  Keep 0.5: d7 85 < 125 none, d7 +200 -> 1,285
  (floor -715); d8 285.00 net 256.50 -> 1,000, +149.90 excluded -> 1,149.90; d14 min(2,000,
  949.95, 899.90) = 899.90 net 809.91 -> 1,050.
- CONSISTENCY, keep 0: d1-d3 750, 300 / 750 = 40.00% inclusive -> d4 375.00 net 337.50;
  d5-d10 (d6 no trade): 500/700, 500/1,000 fail, 500/1,250 = 40% -> d11 862.50 net 776.25 ->
  812.50. Keep 0.5: d4 and d5 below 125; d6 min(3,000, 675, 350) = 350 net 315 -> 1,000;
  d7-d10: 300/500 fails, 300/750 = 40% -> d11 750 net 675 -> 950. Floors -1,700, -1,450, -1,250,
  -1,150, -650, then 0.
All equal tests/test_ml_v2_payout.py:99-167. The simulator is also replayed against
rules.xfa_rules (standard_path_eligibility, consistency_path_eligibility, process_payout,
record_realized_pnl, close_trading_day) on 36 random sequences (198-219), and the vectorized
paths are pinned to run_path path for path across 11 settings (362-405). MLL trail and lock
(account.py:149-151 = xfa_rules.trail_mll_floor, test 84-88), post-payout floor 0, the request
date excluded (`exclude_next`), DLL doubling (account.py:141-146), caps by size (facts rows 90-91),
DLL 1,000 / 3,000 (row 92), five accounts as one draw (summarize: payouts x n_accounts, same
ruin; test 455-464) all match. The 150K MLL $4,500 is V22, not in the facts file (account.py:
97-99 says so), and the 150K tiers are the 50K ones (conservative, documented).

## Findings

### BLOCKING

None.

### SHOULD FIX

**C-01. The resumable state is fingerprinted on data inputs but not on the constants the
scoring reads at call time; the switch the design promises to flip in one line
(COST_GATE_READING) is not in any fingerprint.**
- Where: cpcv.py:527-534 (`_prepare`'s `extra`), 348-351 (`_callable_name` strips a partial's
  keyword arguments), 354-359; pipeline.py:188-203 (`_Stages.run` loads any existing
  stages/<name>.pkl unconditionally); engine_stage.py:99-107 and 244 (per-path fingerprints:
  schedule, risk, world, blackouts; days and n_paths).
- Problem: `decide.candidates` reads `constants.COST_GATE_READING` at call time (decide.py:50-55,
  by design D-05), and sizing reads DAILY_SIGMA_FRACTION, TRADE_LOSS_FRACTION, RISK_SPLIT_M,
  BEYOND_QC_EXTRA_TICKS_PER_SIDE, PAYOUT_KEEP_D_FRAC, PAYOUT_RESET_DELAY_DATES, the KS levels and
  SEED. None of these, nor the account, is hashed. `test_risk_fn_joins_the_state_fingerprint`
  (test_ml_v2_cpcv.py:548-559) shows the mechanism exists for `risk_fn` but the constants were
  left out.
- Failing scenario: run the pipeline on the real data into state_dir X under "net"; the freeze
  flips COST_GATE_READING to "gross" (or PAYOUT_RESET_DELAY_DATES from 0, which V2.9 leaves to
  the freeze); rerun into X. Every cpcv unit `has()` its key, every stage pkl loads, every
  payouts checkpoint matches, and the report presents the "net" numbers as "gross" with no
  error. The same happens to a probe directory reused after any constants edit.
- Fix: compute once `CONSTANTS_FP = sha256 of ml_route_v2/constants.py` (or of a sorted dict of
  its public values) and put it into `extra` in `_prepare`, into `_b_state`'s extra, into each
  stage pkl (`{"constants": FP, "out": ...}`, refused on mismatch like `_read_checkpoint`), and
  into `_path_fingerprint` and the payouts fingerprint; hash `fn.keywords` in `_callable_name`.
  One test: write state under one reading, flip the constant with monkeypatch, assert
  StateMismatchError / PipelineError.

**C-02. A (root, horizon) pair with fewer than two training rows in a split's risk table crashes
the whole nested run instead of being skipped for that validation set.**
- Where: cost_filter.py:44-47 (`sd = NaN` when n < 2, `loss = NaN` when n = 0);
  portfolio.py:160-168 (`join_risk` raises `risk_missing_pairs` on any NaN sigma or loss);
  selection_metric.py:83 (`accept_trades` inside the ScoreFn); cpcv.py:423-430 (`_guarded_score`
  catches nothing but its own checks).
- Problem: with D-04 the table is per inner training set (three of six blocks). Admissibility
  is decided once on the whole window (ruled), so a pair admissible on the window can have 0 or
  1 ok rows in an inner training set while its validation set holds candidates (a vehicle listed
  late in the window, a pair whose rows are concentrated in two blocks). The ScoreFn then raises
  PortfolioInputError out of `nested_cpcv` after the fits of that unit; on resume the same unit
  raises again, so the run cannot finish without a code change.
- Failing scenario: panel with vehicle V having ok rows only in blocks 4 and 5; outer split
  testing (4, 5) has no V rows in training -> every inner fold's table has `sigma_ticks` NaN for
  V -> but V candidates do not appear in those folds either (fine); outer split testing (3, 4)
  with inner hold-out of block 5: training {0, 1, 2} has no V rows, validation block 5 has V
  candidates -> `join_risk` raises -> the run stops.
- Fix: in `accept_trades` (or `admit`), treat a candidate whose pair has NaN sigma or loss as
  not sizeable (skip with reason `risk_unknown`, count it in the unit record) rather than
  raising; keep the raise in `join_risk` only for a pair absent from the table. A test with a
  vehicle planted in two blocks only.

### NOTE

**C-03. An engine path with an empty schedule vanishes from the payouts table without a flag.**
engine_stage.py:241-243 (`if not res["days"]: continue`) after `run_engine_path` returned
`_empty_path()` (165-166). A path whose six splits produced no candidate (every selected
config's cost gate passed nothing on those blocks) has no payout rows; an average over the
table's `path` column then runs over fewer than five paths. Fix: emit one row per path with
`n_trips 0`, NaN income/ruin figures and `empty_schedule True`, or raise.

**C-04. The engine run and the payout re-sizing carry the whole-window risk table (the known
PENDING item); what depends on it.** pipeline.py:550 passes `filt["risk"]` to the simulate
stage; simulate.py:573-577 writes `plan.sigma_ticks` / `plan.loss_ticks` into every TradeRecord;
payout_sim.run_path:343-347 and simulate_paths:599-600 size from them. So every stage-8 and
stage-9 figure inherits it: the engine `daily`, `n_trips`, the combined-MLL audit's sizes, and
all payout figures (income, ruin, breach, halt, first-payout days) at 50K and 150K, hence
verdict criteria read from the payout simulator (7, income) and the engine record. Not
affected: the CPCV record and selection, PBO, DSR, the nested median-path t, the 1.0x / 1.5x
cost sensitivity (all per-split via `_nested_schedule`, pipeline.py:428-431). For the fix: the
per-row table is already known in `_nested_schedule` (`table`, line 428), so sigma_ticks and
loss_ticks can be attached to each split's candidates there; but `join_risk` (portfolio.py:163)
currently drops any such columns from the candidates before merging the table, so it must be
changed to prefer row-level values when present, and `PortfolioMember.__init__`
(simulate.py:221) and `_pack` follow.

**C-05. Rows whose fill minute has no calibrated cost bucket drop out silently.**
targets.py:120 (`with suppress(CostLookupError)`) leaves NaN, `ok_<h>` becomes False
(243-244) and the row leaves training and scoring; nothing counts it (panel.counts counts
feature drops only; cost_filter reports n_rows but not the dropped). Fix: count rows with finite
y_gross and NaN cost per (root, horizon) in `build_targets` and surface them in Panel.counts.

**C-06. `decide._exit_ts`'s fallback is dead for the targets' encoding.** decide.py:85-97 fills
the flatten where `exit_ts_ns_<h>` is NaN, but targets encode a missing exit as -1 (int64,
targets.py:209), which passes `isna()` and flows through as -1. Every caller filters on
`ok_<h>` first (cpcv.horizon_data, pipeline._nested_schedule), so it cannot happen today, and
`split_masks` would raise "an exit precedes its decision" if it did. Fix: treat `<= 0` as
missing.

**C-07. Ridge reproducibility across BLAS thread counts is assumed, not enforced.**
models.py:78-80 (`Xc.T @ Xc`, `np.linalg.solve`) is bitwise reproducible for a fixed thread
count; across runs with different OPENBLAS_NUM_THREADS the last bits can differ, and the
schedule stage's `model.sha256 != sha` check (pipeline.py:420-422) then raises PipelineError on
a resumed run. Loud, not silent; probe.py documents `OPENBLAS_NUM_THREADS=1` but nothing in
the package sets it. LightGBM is covered (`deterministic`, `force_col_wise`, every seed,
`num_threads` fixed in fit and predict, models.py:63-68, 142). Fix: `threadpoolctl.
threadpool_limits(1)` around `_fit_ridge`, or record the thread count in the unit record.

**C-08. N_total is per state_dir and `n_program` is a constant default.** configs.py:200-203
counts this run's ledger; pipeline.py:488 defaults `n_program` to N_PROGRAM_AT_DRAFT (198).
Two runs on the real data into two state_dirs (a probe and the run, or "net" and "gross") each
count 45 + |A| + |B| once and nothing accumulates across them; D-06 ("N adds the phase-1 Gate 0
tests only") is not expressible in code. The lead carries N across state_dirs and passes
`n_program`; the code is correct within one run.

**C-09. The payout simulator's scaling tier is read after the day's payout debit.**
payout_sim.py:320 (`tier_max_tenths(account, acct.balance)` after 301-310) and
simulate_paths:578; V2.8 says the tier at the prior session's close. After a payout this gives
the lower tier (conservative) for that date. Document or move the read above the request.

**C-10. Key fix, two small items.** (a) docs/ACCESS.md:9 still says the credential is
`DATABENTO_API_KEY`; stale since 5931e30 (outside the commit's files; not a harness file).
(b) data/config.py:176-179 strips only for the emptiness test and returns the raw value, so a
variable set to " key " is returned with its spaces. `return key.strip()`.

**C-11. The engine record is the switches-off record.** simulate.py:347-350 sizes with
`multiplier=1.0` and the member implements no KS1-KS5 (only "no bar -> skip", 344-345); the
kill switches enter only in payout_sim's re-sizing (the pipeline docstring says so, 56-61).
Consistent with the verdict reading (D-01), but the synthesis should label `run.daily` and the
combined-MLL audit "kill switches off" rather than the live system's path.

**C-12. Naive variance in the normalizer.** normalize.py:45 uses `(sum2 - sum1 x mean) / (n - 1)`
on raw sums; relative cancellation of order 1e-16 x mean^2 / var, absorbed by the flat test only
below 1e-12. No V2.3 feature has |mean| / sd above about 1e3, so it is inert here; a Welford or
shifted-origin sum would remove the dependence on the feature's scale.

## Mutation checks (scratchpad only; repo untouched)

Setup: `ml_route_v2/` and tests/{__init__, ml_v2_fixtures, test_ml_v2_leakage}.py copied to
scratchpad/mut/<name>/ (never data/, .venv, .git); one textual mutation per copy (each pattern
asserted to occur exactly once); `pytest --rootdir=<copy> <copy>/tests/...::<canary>` with
`PYTHONPATH=<copy>:<repo>`, so the copy's `ml_route_v2` shadows the repo's (the tracebacks
point into the copies; the `python -c` origin line in each log ran with the repo as cwd and is
not evidence). Script: scratchpad/run_mutations.sh; logs scratchpad/mut/m*.log.

| Id | Guard removed (file:line, mutation) | Canary | Outcome |
|---|---|---|---|
| m0 | none (control) | the 11 canaries below | 11 passed (25.6 s) |
| m1 | signals/__init__.py:134 `late = zeros` | future_bar_with_its_true_timestamp_fails_assert_causal; future_release_... | both FAILED (DID NOT RAISE) |
| m2 | normalize.py:33 `hi = arange + 1` (current date in the window) | peeking_normalizers_are_caught_and_zscore_causal_is_not | FAILED: PerturbationLeak f1, f2 (2 rows) |
| m3a | cpcv.py:434 `outside` check disabled | score_fn_returning_test_block_pnl_is_refused | FAILED (DID NOT RAISE LeakageError) |
| m3b | cpcv.py:437 trade-count check disabled | score_fn_counting_rows_it_was_not_given_is_refused | FAILED (DID NOT RAISE) |
| m4 | cpcv.py:566 and 570 `_assert_inner_isolated`, `_assert_rows_isolated` removed | inner_fold_handed_an_outer_test_block_is_refused | FAILED (KeyError at cpcv.py:404 instead of LeakageError: the unguarded path crashes, the canary still fails) |
| m5 | cpcv.py:248 `_intersects` returns all False | purge_removes_a_training_label_that_crosses_into_a_test_date | FAILED at line 404 (`assert not train_bad[planted]`) |
| m6 | pipeline.py:210 `assert_bars_on_session_grid` returns at once | shifted_product_fails_the_session_grid_guard_and_the_pipeline_refuses | FAILED (DID NOT RAISE BarGridError) |
| m7 | panel.py:59 `assert_window` never raises | window_guard_refuses_a_planted_row...; pipeline_refuses_a_world_that_reaches_2024_03_01 | both FAILED (second: PipelineError "training panel is empty" instead of WindowError) |
| m8 | generic.py:344, 354: G17 reads the bar opening at t and stamps avail = t | control_every_library_signal_passes_the_perturbation_test | FAILED: PerturbationLeak raw_g17_{nq, zn, 6e, cl, gc, zc, mbt} across 9 cuts |
| m9 | _core.py:411, 413: `apply_event` ignores availability and stamps avail = t | the same control | FAILED: PerturbationLeak raw/z k3_ldnmom_trend, k4_eiafade_move, k4_eiamom_r3, k5_pmfix_move |

Result line: **9 of 9 mutations caught by their canaries; control 11/11 passed.** m8 and m9
are the important ones: they show the perturbation control catches a library signal that reads
a bar closing after t or an event known after t even when the signal lies about `avail`, so
the self-reported availability is not the only line of defence.

Canaries with no removable guard (the planted edge must vanish): shuffled target (Gate 0 fails
and |t| < 2 after an across-date shuffle, with the positive control passing first,
test_ml_v2_leakage.py:291-300); Gate 0 (a)-(d); the within-date shuffle is documented as not a
null (S-1, ruled). Not mutated.

## Verdict (code)

Nothing in ml_route_v2 reads the future, the CPCV machinery is correct and self-checking (15
splits, 5 paths, span purge on timestamps, symmetric one-date embargo, inner folds inside the
purged outer training rows with date- and row-level asserts, selection on inner records only,
per-split risk tables), the simulator is the frozen engine plus exactly the three ruled changes
and a cost override that can only add cost, the payout simulator reproduces rules.xfa_rules and
the facts file and its hand-computed sequences and the two-product day recompute to the cent,
the key fix is clean, and every guard I removed in the scratchpad made its canary fail. The two
should-fix items are robustness, not correctness: the resumable state does not know which
constants produced it (C-01), which is dangerous precisely because the design intends a
one-line flip of COST_GATE_READING at the freeze, and a sparse (root, horizon) pair in one
inner training set would crash the nested run instead of being skipped (C-02). The known
PENDING item (whole-window risk table in the engine run) propagates into every payout figure and
the engine record but not into the CPCV statistics (C-04). With C-01 and C-02 fixed, and the
pending item closed along the path in C-04, the code is fit for the freeze.

---
