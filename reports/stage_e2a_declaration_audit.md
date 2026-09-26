# Stage E.2a declaration audit

Auditor: DeclarationAuditor-FableXHigh (Claude Fable 5.1, worker-xhigh), a different model from the
Stage E.2a lead (Opus 5.5). The auditor wrote none of the work audited here. Parts 2 (the
source-window amendment, Task 11) and 3 (the independent recomputation, Task 12) are appended later
in this session.

## Part 1: ML route freeze audit (Task 3)

Written 2026-09-25 00:43 PDT, before the Task 4 freeze commit. Read-only everywhere except this
file; no market data opened; no web access used.

### 1.0 What was audited, and how

- The lead's edits: `git diff 1b54dc1 -- docs/STAGE_E_ML_DESIGN.md` (37 hunks-worth of edits) and
  the whole edited file docs/STAGE_E_ML_DESIGN.md (535 lines; line numbers below refer to it).
- reports/stage_e2a_ml_changes.md (edits ML-00 to ML-36, the coverage table, Q-1 to Q-3, A-1 to
  A-3) and docs/DECISIONS.md, entry of 2026-09-25 (V1 to V9).
- The user's decisions as the stage prompt quotes them (docs/prompts/STAGE_E.2a.md, Task 1).
- The frozen files for contradictions: docs/STAGE_E_DESIGN.md (D1, D2, D4, D5, D6, D8, D9, D10,
  D11, D12, D13, D15's SUPERSEDED banner and D15.3 to D15.7 as the superseded record),
  docs/NULL_CRITERIA_E.md (sections 3, 4, 8), CLAUDE.md's overnight profile,
  reports/stage_e1_freeze.json (its FA-15 note: the ML design is a declared forward reference, not
  frozen by E.1, so editing it breaks no freeze).
- Background used for specific checks: reports/stage_e1_ml_research.md (E1-ML-17, 19, 21),
  reports/E.1_RETURN.md (F-1, F-5, FA-06), reports/stage_d1f_confirmation_list.md (the Family H
  complete-day and warm-up conventions), strategy/research/d_volatility_state/h1_trailing_volatility_regime_gate.py
  (how the MES record actually computes its "family D" trailing volatility), docs/SCREENING.md, and
  reports/stage_e0_quotes.json (quote metadata only: which contract-months resolved; no prices).
- Mechanical checks by script (scratchpad, not committed): sha256 of `git show
  1b54dc1:docs/STAGE_E_ML_DESIGN.md` and of the working file; every Old text of ML-00 to ML-36
  located exactly once in the 1b54dc1 blob and every New text exactly once in the current file; the
  37 replacements replayed in order onto the old blob; the coverage table cross-checked against each
  edit's Decision field; V1 to V9 in DECISIONS.md compared with the prompt after whitespace
  normalization.

### 1.1 Check 1, mapping: HOLDS

- Hashes: before `7ae2d3471c2d2d79da2380db0fa74c5ccef1859718002999e605488fc411d6a1` (the 1b54dc1
  blob, which is also HEAD's), after `185e8cd5c908048ff6de3ae63036b31ed7b8badab62c8d4aec2890d58aeba8a0`
  (working file). Both equal the log's lines 8 and 9.
- Replaying all 37 Old-to-New replacements of the log onto the 1b54dc1 blob reproduces the current
  file byte for byte. So the log is the diff, exactly: nothing in the diff is outside the log and
  nothing in the log is outside the diff. This is stronger than the ten spot-checks the brief asked
  for; the ten pairs I also read by eye against the diff were ML-00, ML-02, ML-05, ML-09, ML-10,
  ML-22, ML-23, ML-24, ML-25, ML-30 and ML-31.
- Every edit carries a decision (ML-01..ML-35 one of V1 to V8; ML-00 and ML-36 are record notes
  citing V1 to V9 and V1 to V8). The coverage table lists exactly the edits whose Decision field
  names that V, and no edit is missing from it.
- Every decision is applied or has a logged, correct "no edit needed": V1 (ML-01, 03, 04, 05, 20,
  35), V2 (06, 07), V3 (08, 11), V4 (12, 14), V5 (15, 16), V6 (17, 18), V7 (09, 10, 21 to 28:
  Windows PC text struck, the RTX 3050 stated, the overnight profile stated with CLAUDE.md's exact
  limits, the time estimate's GPU assumption re-stated as unknown until the probe, the batch-size
  re-plan stated), V8 (02, 13, 19, 29 to 34), V9 (no edit: F-1 is already "31" in M1's table and M2;
  F-5 is a catalog item and the catalog is frozen; FA-06 is Tasks 2 and 11). Each reason checked
  and correct.
- DECISIONS.md quotes V1 to V8 identically to the prompt. V9 differs by one clarifying insertion:
  "(Stage E.2a Tasks 2 and 11)" for the prompt's "(Tasks 2 and 11)". Meaning unchanged (ML-A21).
- The lead's Q-1 to Q-3 and A-1 to A-3 are accurate readings (ML-A20, ML-A22 below). A-1's
  batch-size rule is mechanical and reads no market data, as V7 requires.

### 1.2 Check 2, no choice left after training data is seen: DOES NOT HOLD as written

Read as an implementer who may ask nobody, the design leaves the two quantities that decide the
selection and the candidate set undefined (ML-A01, ML-A02), and leaves a further set of details to
whoever writes the code (ML-A03 to ML-A13, ML-A16). Every one of them is fixable by a sentence or a
paragraph that fills in what the user accepted, and none needs the training data to be written.
The point that turns "code-time detail" into "post-data choice" is that the design does not itself
bind the route's code to a hash before the training history is bought (ML-A04); the frozen D11
requires that manifest, but only by reference. With ML-A01 to ML-A16 fixed and the code hashed in
E.2b before E.ML-buy, the check holds.

### 1.3 Check 3, partition: HOLDS for the forbidden dates, with two things to state

No path in the design lets a research-window date (2025-04-01..2026-06-19), an embargo date (March
2024), a holdout-2 date (2024-04-01..2025-03-31) or anything from 2026-06-21 00:00 UTC into
training, tuning, normalization or distillation:
- rows are trade dates S_X..2024-02-29 (M1), asserted on the saved row index of every step (M7.4);
  every normalization constant is a trailing statistic of bars before t or a literal (M7.5);
  trailing features look backward only, so at the training window's end nothing reaches into
  March 2024 (M7.5's perturbation test asserts it);
- March 2024 and holdout-2 are inside chunks sealed on arrival (D4, U4; M1 and M9 row 2 restate
  it), so they are unreadable, not merely unread;
- the research-window bars are excluded from the route's training store with a planted-bar canary
  (M7.4);
- the block-6 pre-test and the CPCV folds live inside the training window (M5.1, M5.3, M7.3);
- cross-product feature F16 reads the cluster lead's own training-window bars (M4).

Two things the design should say (neither is a breach): (a) at the test window's start, trailing
features cannot be warmed up from holdout-2, so they are missing until the research window's own
bars fill the lookback; the design's silence on missing inputs is ML-A05, and the power consequence
is ML-A19; (b) three research-window-derived constants do enter training: the D8 cost surface
(five mbp-1 dates of 2025-26) in every target, D2's q_c and r_c (research-window bars) through the
depth term and sizing, and S_X through V_ref,X (research-window volume). What kind of leak this is,
and why it is not a partition breach, is ML-A18.

### 1.4 Check 4, consistency with the frozen design and with V1 to V9: HOLDS, with four items

Nothing contradicts V1 to V9. Against the frozen design: D2's sizing (q_c, the 1-lot cap), D9's
constraint set (20-entry floor, 2-minute hold, market orders, no stops, CPI window, event-minute
guard, price-limit rule), D4's windows and start rule, D13's purchase rules (step 2 pulled forward
under U4, cap left to the purchase session as D13 requires), U4's seal-on-arrival, U6's purpose,
D12's session split, and CLAUDE.md's overnight profile are all consistent. Four items need a
statement: the alpha-split reading against frozen D5 (ML-A14), the unit and event-window cost of
the target against D2's price-path convention and D8 (ML-A08), D11's manifest discipline restated
for the route (ML-A04), and the unreachable K8 slot in the 16-rule cap (ML-A17).

### 1.5 Findings

Grades: BLOCKING (a post-data choice that could change which rules are produced, a forbidden date
or research-window information in training, or a contradiction that changes an outcome), SHOULD
FIX (an error or ambiguity to correct before the freeze that cannot by itself change the rules or
leak data, given the code is hashed before the purchase), NOTE. "Within V1-V9" says whether the
minimal fix fills in or corrects a detail consistently with what the user accepted, or needs a new
user decision.

#### ML-A01. BLOCKING. The selection metric of M5.1 has no rule for turning a prediction into a position, no unit for "equal-risk", and no aggregation

- Where: docs/STAGE_E_ML_DESIGN.md lines 279-282 (M5.1), 137-139 (M2's "equal-risk portfolio"),
  228-232 (the net target), 223-225 (one open position).
- What is wrong: "the selection metric is the mean daily net P&L of M2's equal-risk portfolio at
  1.0 x D8 cost" cannot be computed from a model's validation predictions without deciding (a) when
  a prediction becomes a long, a short or no trade; the target is the LONG's net P&L (gross move
  minus cost), so the sign of the prediction is not the sign of the trade: a short entered on
  y_hat < 0 has expected net -E[y] - 2c, negative whenever y_hat is above -2c; (b) what "equal-risk"
  means (sigma units, D2's q_c x r_c, dollars at q_c) and how products with no rows on a date are
  treated; (c) whether M4's one-open-position rule applies while generating validation P&L (with h =
  120 minutes or to-F it changes which rows trade); (d) how the 10 CPCV splits combine (mean of the
  10 split means, pooled dates, or paths). Two implementers would select different configurations
  per horizon and challenger from the same data, and the surrogate rules follow the selected model.
- Why it matters: this is the step that picks 6 of the 36 configurations; everything downstream
  (fidelity target, candidates, survivors, rules) depends on it.
- Minimal fix: one paragraph in M5.1 defining, in the design's own units: entry rule per side with
  the net-long target's asymmetry made explicit (for example: at each validation row, with y_hat and
  the row's D8 round-turn cost c both in sigma units, long if y_hat > 0, short if y_hat < -2c, else
  flat; M4's one-open-position rule applied in time order per product); realized net P&L per trade =
  (gross move in the direction taken, minus c) / sigma_X,d; a product's daily P&L = the sum of its
  trades that date, zero on a date with rows and no trade; the portfolio's daily P&L = the mean over
  the products with rows on that date; a split's score = the mean over its validation dates; the
  configuration's score = the mean of its 10 split scores.
- Within V1-V9: yes as a fill-in of M5 "as written" using the design's own conventions (net-long
  target, 1.0 x cost, sigma units, dates as the unit of evidence); the exact wording is new text the
  user has not seen, so the freeze rulings should quote it.

#### ML-A02. BLOCKING. "The cost threshold" of M5.2 is undefined, and a symmetric threshold on a net-long prediction admits losing shorts

- Where: lines 283-288 (M5.2), 228-232 (M4 target), 260-262 (M4 reasoning: the edge must survive
  1.5 x cost).
- What is wrong: "Each leaf whose mean prediction exceeds the cost threshold in absolute value is a
  candidate rule ... market entry in the sign of the leaf". The prediction is already net of 1.0 x
  cost for a long; the threshold could mean 0 (net positive), 0.5 c (the 1.5 x stress), or c again
  (double counting), and the implementer chooses. Worse, for a short the expected net at stress m
  is -E[y] - (m + 1) c, so a negative leaf with mean prediction -c (which passes any symmetric
  threshold up to c) is a losing short at 1.0 x cost. The candidate set, and so the block-6 test
  count, differs between readings.
- Why it matters: it defines what a candidate rule is. The block-6 pre-test filters some wrong
  shorts, but a biased candidate set changes which rules survive and inflates the route's own search.
- Minimal fix: define the threshold per side at the design's stress m = 1.5 (M4's reasoning
  sentence): with c_bar = the mean D8 round-turn cost of the leaf's rows in sigma units, a leaf is a
  long candidate if its mean prediction > (m - 1) c_bar and a short candidate if its mean prediction
  < -(m + 1) c_bar; state m. (Equivalently: the leaf's predicted net edge in the traded direction is
  positive at 1.5 x cost.)
- Within V1-V9: yes, as a correction that makes M5.2 mean what M4 says ("the model learns net edges
  only"; "survive at 1.5 x the D8 cost"). Changing the target to a gross move (D15.6's form) would
  be a new decision on V4; the side-aware threshold is not.

#### ML-A03. SHOULD FIX. The six contiguous blocks are not defined, and the design gives two incompatible descriptions of block 6

- Where: lines 279-280 (M5.1), 289 ("block 6, 2023-late..2024-02"), 374-375 (M7.3).
- What is wrong: "six contiguous blocks" of what calendar (the union of the 31 price-path contracts'
  trade dates, or MES's calendar), equal in trade dates or in rows, remainder where, and common to
  every product or per product. Common date boundaries are required by M2 ("every product's rows
  for a date fall in the same fold"). Six equal blocks of the pooled calendar 2019-05-06..2024-02-29
  (about 1,200 trade dates) put block 6 at about 2023-05..2024-02, not "2023-late"; the two
  descriptions cannot both hold. Block 6 is the pre-test and the ranking window (M5.3, M5.4), so its
  boundary decides which rules survive and in what order.
- Minimal fix: define the cut (for example: the union calendar of the price-path contracts' trade
  dates from 2019-05-06 to 2024-02-29 after the M4 exclusions, six blocks of equal trade-date count,
  the last taking the remainder, the same boundaries for every product; block boundaries written
  into the route manifest before any fit) and strike "2023-late".
- Within V1-V9: yes (V5, the block-6 pre-test "as written", needs block 6 to be defined).

#### ML-A04. SHOULD FIX. The design claims its procedure is code "frozen with this design" but no code exists, and it does not bind the route's code to a hash before the training history is bought

- Where: line 301 ("Steps 2 to 4 are code, frozen with this design"), 513 ("the surrogate-tree and
  pre-test code (M5, frozen with this design)"), 389-390 (M7.6 hashes models and surrogate trees,
  not the pipeline), 476-478 (M9 rows 1b, 2, 3).
- What is wrong: at this freeze the route's code does not exist; E.2b writes it. The frozen D11
  puts everything E.2 builds under "a manifest committed before the purchase of the confirmation
  history", and D11.7 hands the ML build list to this design, so the discipline applies by
  reference; the ML design never says so, and E.ML-train (which holds the training data) is not
  told to refuse on a manifest mismatch. Every code-time detail in ML-A01 to ML-A03 and ML-A05 to
  ML-A13 would otherwise be settled by the session that can see the data.
- Minimal fix: replace "frozen with this design" by "frozen by E.2b's harness manifest before
  E.ML-buy", and add one sentence to M7 or M9: E.2b's manifest hashes the route's pipeline (feature
  and target builders, the block cut, the CPCV splitter, the selection, the surrogate, pre-test,
  ranking and write-up code, and every M7 test); E.ML-buy runs only after that commit; E.ML-train
  and E.ML-test refuse to run on a mismatch.
- Within V1-V9: yes (V8's ordering and the frozen D11's discipline; no new choice).

#### ML-A05. SHOULD FIX. No rule for missing inputs or for the warm-up of trailing features, at training or at the test

- Where: lines 233-251 (features; sigma 20 dates, F10 20 dates, F17 120-day median of a 20-date
  statistic, F7/F8 one prior date), 42-49 (windows), 380-385 (M7.4), 177-184 (LSTM padding covers
  only intraday sequences).
- What is wrong: the design does not say what happens to a row whose lookback is not full (the
  first rows after S_X, and, at the test, the first rows after 2025-04-01, where the prior bars are
  holdout-2 and unreadable) or whose bar at t, t + 1 or the exit is absent. LightGBM's native NaN
  handling, an LSTM mask, and sklearn's tree would each produce a different model and a different
  rule from the same data; a rule that fires on "F17 missing" is not a plain rule. The frozen MES
  record's convention is explicit ("Until the lookback is full, no trade (warm-up comes from the
  confirmation window's own start)", reports/stage_d1f_confirmation_list.md, Family H), and the
  superseded D15.4 had "Missing input at t_j ... means no trade at t_j; there is no imputation".
- Minimal fix: state in M4: a row with any missing input (a lookback not full from bars on or after
  the store's first date; an absent bar at t, t + 1 minute or the exit; a lead product without a
  bar closing at or before t) is excluded from every training, tuning, normalization and
  distillation set, and produces no trade at the test; no imputation; warm-up at the test comes
  from the research window's own bars, never from holdout-2.
- Within V1-V9: yes (V1 forbids holdout-2; V4's feature list "as written" needs the convention).

#### ML-A06. SHOULD FIX. sigma_X,d is defined by reference to a construction that is not in any frozen text

- Where: lines 128-132 (M2), 250 (F17), 231 (target divided by sigma), 286-287 (cut points are in
  sigma units).
- What is wrong: "the mean absolute day-session move over the 20 complete trade dates before d (the
  frozen B4 construction)". B4 exists only in the SUPERSEDED D15.4, which itself points to "D.1
  family D"; the MES family-D code (h1_trailing_volatility_regime_gate.py) computes an EWMA
  variance of one-minute returns, not a 20-date mean absolute move. "Day-session move" (open-to-close
  or high-low) and "complete trade date" are not defined in the ML design. sigma normalizes every
  price feature, the target, F17 and every cut point, so two definitions give two rule sets.
- Minimal fix: define it in M2: sigma_X,d = the mean over the 20 complete trade dates before d of
  |close of the bar at C_X - 1 min minus open of the bar at O_X| in ticks of the price-path
  contract, O_X and C_X from D6's session table, "complete" as the frozen Family H rule (both bars
  exist, no early halt, one instrument_id); fewer than 20 complete dates available means missing
  (ML-A05). Drop the B4 reference.
- Within V1-V9: yes (V2/V4; it is D2's r_c form applied per date, the design's own reading).

#### ML-A07. SHOULD FIX. "One contract per exposure: the one with the longest history" ties for ten exposures, and the design gives no tie rule and no list

- Where: lines 83-87 (M1), 70-72 (the purchase scope), 247-248 (F16 names NQ, ZN, 6E, CL, GC, ZC,
  MBT as leads).
- What is wrong: E.0's quote metadata (reports/stage_e0_quotes.json; D13's own summary) resolves
  every month from 2019-05 for MNQ, M2K, MYM, M6E, E7, M6A, M6B, QM, QG, MGC and SIL exactly as for
  their full-size siblings; only MCL, MNG, MHG, MBT and MET start later. So "longest history" ties
  for Nasdaq, Russell, Dow, EUR, AUD, GBP, WTI, natural gas, gold and silver; "usually the full-size
  contract" is a tendency, not a rule. The choice fixes the bars, the volume field F10, the cost
  ticks, the lead products' bars (F16), and what E.ML-buy buys.
- Minimal fix: list the 31 price-path contracts in M1 with the tie rule (the full-size contract;
  where the exposure has no permitted full-size contract, its most active permitted contract),
  written before E.ML-buy from quote metadata alone.
- Within V1-V9: yes (V1's "one contract per exposure", the design's "usually the full-size
  contract", and F16's named leads all point the same way; no price data is needed).

#### ML-A08. SHOULD FIX. The target's units and cost do not match D2's price-path convention and D8

- Where: lines 228-232 (M4 target), 85-87 (M1: rules trade D2's vehicle with its cost model),
  frozen D2 ("the exposure's full-size contract bars as the price path with the micro's cost model
  and tick value"), frozen D8 (event-window cost).
- What is wrong: (a) the target is "in ticks of the price-path contract, minus the D8 round-turn
  cost in ticks" of, per M1, the vehicle; where the two contracts' ticks differ (QM 0.025 against CL
  0.01; E7 and M6E against 6E) the subtraction mixes units, and D2's convention (the move converted
  to the vehicle's tick value) is the frozen one; (b) the cost is stated as "at t's and the exit's
  time-of-day buckets" only, omitting D8's event-window rule (a fill in [release, release + 30 min)
  pays the largest bucket per side), which the engine charges at the test. Training targets and
  test P&L would then use different cost models around releases, exactly where F13-F15 give the
  model a handle.
- Minimal fix: state the target as the price move converted to the vehicle's ticks, minus the
  vehicle's full D8 round-turn cost at q_c (bucket half-spreads, depth term, and the event-window
  rule), all divided by sigma_X,d expressed in the same ticks.
- Within V1-V9: yes (V4 accepts the target; D2 and D8 are frozen and govern the units and the cost).

#### ML-A09. SHOULD FIX. The decision-time boundary and the row exclusions are not stated

- Where: lines 221-225 (M4 decision times).
- What is wrong: "every 30 minutes, at O_X + 30, O_X + 60, ... in the product's day session ...
  while t + h <= F_X. At most 13 decision times per product per day": with t < C_X, rates give 13
  and equity 12; with t <= C_X, equity gives 13 and energy 11; both readings satisfy "at most 13".
  Roll-blackout, vendor-degraded and early-halt dates, which D15.3 listed and which the screening
  runner applies at the test (docs/SCREENING.md, NULL_CRITERIA_E section 4), are not stated for the
  route's rows. Different rows, different rules.
- Minimal fix: state the interval (t in [O_X + 30, C_X) or [O_X + 30, C_X]) and the exclusions
  (roll-blackout dates excluded; early-halt dates excluded; vendor-degraded dates treated as the
  runner treats them at the test).
- Within V1-V9: yes (V4; NULL_CRITERIA_E 4 is frozen).

#### ML-A10. SHOULD FIX. Tie rules and the "sign agrees" test are undefined

- Where: line 281 ("ties go to the smaller model"), 289-292 (M5.3 "its sign agrees with blocks
  1-5"), 293-295 (M5.4 ranking).
- What is wrong: "smaller model" has no order on either grid; M5.4's third tie (same condition
  count, same horizon) is unresolved; "sign agrees with blocks 1-5" does not say the sign of what.
- Minimal fix: trees: fewer num_leaves, then larger min_data_in_leaf, then larger lambda_l2; LSTM:
  fewer hidden units, then shorter lookback; M5.4 final tie: the challenger listed first in M3,
  then the surrogate's leaf order; M5.3: the rule's realized net P&L on blocks 1-5 at 1.5 x cost
  has the same sign as on block 6 (so both are positive).
- Within V1-V9: yes (V5).

#### ML-A11. SHOULD FIX. The surrogate tree's implementation and settings are not fixed, and the number of surrogates per cluster is implicit

- Where: lines 283-288 (M5.2).
- What is wrong: "CART, minimum leaf 2% of the cluster's rows" leaves the library, criterion,
  feature-tie handling (sklearn shuffles features by random_state even with max_features=None),
  the cut-point convention (sklearn's midpoint between sorted values) and any rounding of literals
  open. "The selected model's predictions" is singular, but there are six selected models per
  cluster (two challengers x three horizons), so 48 surrogates, up to four leaves each; the text
  does not say so.
- Minimal fix: state: one surrogate per (cluster, challenger, horizon); sklearn
  DecisionTreeRegressor(max_depth=2, min_samples_leaf=0.02, criterion="squared_error",
  max_features=None, random_state=20260924), version pinned in uv.lock; cut points as sklearn
  writes them, rounded to a stated precision in sigma units or not rounded.
- Within V1-V9: yes (V5 "depth-2 surrogate rules ... as written").

#### ML-A12. SHOULD FIX. The LSTM and the indicator encoding are under-specified

- Where: lines 177-184 (LSTM), 170-176 (trees), 251 (F18, F19), 429-437 (batch-size rule).
- What is wrong: no loss is stated for the LSTM (L2 is stated for the trees only); no embedding
  dimension for M2's product embedding; no rule for how the static features "fed to the output
  layer" join the recurrent state; no 5-minute bar grid (aligned to the trade date's first bar or to
  the clock); no statement of gradient clipping, weight decay, sample shuffling seed or cuDNN
  determinism; for LightGBM, whether F18/F19 are categorical features or one-hot columns (different
  trees). Two implementers would fit different models.
- Minimal fix: state each: MSE on the normalized net target; embedding dimension (a number); the
  final hidden state concatenated with the embedding and the static features into one linear
  output; 5-minute bars aligned to the trade date's first bar; no clipping, no weight decay;
  shuffling with seed 20260924; torch.use_deterministic_algorithms(True) with the cuBLAS
  workspace variable set; F18/F19 as one-hot columns (or LightGBM categorical, stated).
- Within V1-V9: yes as fill-ins of V3 "as listed"; the embedding dimension is a number the user has
  not seen, so the rulings should name it.

#### ML-A13. SHOULD FIX. The embargo parenthetical misstates the longest lookback

- Where: lines 374-379 (M7.3).
- What is wrong: "embargo one full trade date on each side of every validation block (at least h,
  and at least the longest lookback, 120 minutes or 6 hours for the LSTM)". The longest lookbacks
  are daily: F7/F8 one date, sigma_X,d and F10 twenty dates, F17 about 140 dates. With a one-date
  embargo, training rows after a validation block carry validation-period bars inside sigma, F10
  and F17. This touches selection inside the training window only (the test is untouched), and a
  140-date embargo on both sides of ~200-date blocks would consume most of the data, so the design
  must say which it accepts; as written it claims a property it does not have. The purge sentence is
  vacuous for intraday targets (no target window crosses a date), which is harmless.
- Minimal fix: keep the one-full-trade-date embargo as the rule and state that trailing daily
  statistics (sigma, F10, F17) are not embargoed, with the reason (slow-moving level information; a
  full-lookback embargo would remove most of the training data; affects selection only); or extend
  the embargo. Correct the parenthetical either way.
- Within V1-V9: the first option is (it states what the accepted rule means); extending the embargo
  is a design change the user should see.

#### ML-A14. SHOULD FIX. The alpha split is stated in a way that either supersedes frozen D5 silently or breaks D5's program-level promise

- Where: lines 333-337 (M6 Holm family), 349-352 (M6 reasoning), 360-361 (V6 note); frozen D5
  (docs/STAGE_E_DESIGN.md lines 308-310: alpha_k = 0.05 / K, K = clusters with a non-empty Tier A,
  "at most 8").
- What is wrong: M6 puts the route at 0.05 / (K + 1) and its reasoning says every cluster then
  tests at 0.05/9 instead of 0.05/8. Frozen D5 fixes the clusters at 0.05 / K with K <= 8. Either
  the clusters' alpha changes (a supersession of frozen D5 text, which V6 authorizes but which must
  be logged as such, never edited into the frozen file) or the clusters keep 0.05 / K and the
  program-level bound becomes 0.05 + 0.05 / (K + 1). The design does not say which; a borderline
  Holm rejection in a cluster session could go either way.
- Minimal fix: state in M6 that V6 reads D5's K as the number of families with a non-empty Tier A
  including the route once it has a tested rule (so every family's alpha is 0.05 / (K + 1) and D5's
  "at most 8" reads "at most 9"), and record that reading in docs/DECISIONS.md as V6's effect on D5.
  Note that K is not known until the last screening session; that timing question is D5's already.
- Within V1-V9: yes (V6 is the user's decision; the fix names its consequence).

#### ML-A15. SHOULD FIX. The test series and unit of a multi-exposure rule are not stated

- Where: lines 338-344 (M6 edge conditions, nulls "per exposure the rule trades"), 296-300 (M5.5
  entry fields), 283-288 (rules are per cluster on pooled rows); frozen NULL_CRITERIA_E section 3
  (the per-member unit; the multi-leg convention).
- What is wrong: a route rule is fit on a cluster's pooled rows, so it trades up to seven exposures
  at their own q_c. Nulls are per exposure (stated). The edge test (Holm p-value, daily t > 3.0,
  DSR, PBO) is one trial per rule (V6), so it needs one daily series; the design does not say which
  (combined dollars in a primary leg's unit, per NULL_CRITERIA_E 3, or something else), nor which
  exposures a rule trades (every exposure of its cluster, or only those with rows in block 6), nor
  the set whose Sharpe variance enters the route's DSR (D5 uses the family's).
- Minimal fix: state: a rule trades every traded exposure of its cluster whose rows entered its
  surrogate, at D2's q_c; its edge series is the combined net dollars per research-window date
  divided by (q x tick value) of a named primary leg (the cluster's lead product of F16 is the
  natural choice); nulls per exposure as written; the DSR Sharpe variance is over the route's tested
  rules' research-window daily Sharpes.
- Within V1-V9: yes as an application of frozen NULL_CRITERIA_E 3 under V6; the primary-leg choice
  is a convention the user should see in the rulings.

#### ML-A16. SHOULD FIX. The write-up step is a human step between distillation and the test and is not constrained

- Where: lines 296-301 (M5.5).
- What is wrong: the entry's products, exposures, decision times, exit, sizing, Topstep check and
  falsification condition are written by the lead. "The lead does not pick among rules" covers
  selection, not transcription; nothing says an exposure cannot be dropped, a decision-time set
  narrowed, or a cut point rounded at write-up.
- Minimal fix: one sentence: the surrogate step writes each surviving rule as machine-readable JSON
  (features, cut points, sign, horizon, cluster, exposures, provenance), the manifest hashes that
  JSON, and the catalog-format entry is a rendering of it with no field changed.
- Within V1-V9: yes (V5).

#### ML-A17. NOTE. The K8 slot in "at most 16" is unreachable

- Where: lines 293-295.
- Every feature is own-product or the own cluster's lead (F16), so no route rule can "read two
  clusters' products"; the cap is effectively 14 (2 x 7). No outcome changes. Optional: say so.

#### ML-A18. NOTE. Research-window-derived constants enter training: what kind of leak, and why it is not a breach

- Where: lines 228-232 (D8 cost in every target), 252-254 and 85-87 (q_c of D2's vehicle), 42-43
  (S_X by D4's start rule), 259-262 (M4 acknowledges the early-era bias).
- The D8 cost surface (per-product, per-30-minute-bucket half-spreads and depth at q_c from five
  mbp-1 dates in 2025-05..2026-04), D2's q_c and r_c (mean absolute day-session move on
  2025-04..2026-06 bars) and S_X (through V_ref,X, research-window volume) all carry information
  about the test period into the training objective. It is level and liquidity information
  (spread by time of day, volatility scale, volume level), never a price path or a direction; it is
  charged identically at the test; it cannot make a direction forecast better on the test window
  under the null of no predictability. It can steer rules toward time-of-day buckets that were cheap
  in 2025-26, which is exactly what the test also assumes, and it makes early-year training costs
  optimistic (NULL_CRITERIA 4.3), which M4's 1.5 x stress addresses. This is the same convention
  every hand-written member lives under (D8; NULL_CRITERIA_E 4). Recommend one sentence in M7
  naming these three as the only research-window-derived quantities the training may see, so the
  window test's intent is complete.

#### ML-A19. NOTE. Warm-up cost at the test window's start

- Where: lines 97-100 (M1's "Known cost" assumes about 290 eligible dates), 233-251.
- With ML-A05's convention, every route rule is silent for the first 20 research dates (sigma),
  rules using F10 likewise, and rules using F17 for about 140 dates (about 47% of the window),
  because holdout-2 cannot supply the warm-up. D4's power check will label such a rule
  "inconclusive by design" where it cannot reach power. No fix required; the design should state
  the cost beside M1's paragraph.

#### ML-A20. NOTE. The LSTM batch-size rule (A-1)

- Where: lines 429-437, 180-181.
- Mechanical and data-free as V7 requires; a halved batch changes the number of optimizer steps at
  fixed learning rate and epochs, so the fitted LSTM depends on the probe's outcome; that outcome is
  fixed and recorded before any fit, which is acceptable within V7. Implementation: "peak memory in
  use (nvidia-smi)" is an instantaneous reading; take torch.cuda.max_memory_reserved() for the peak
  and nvidia-smi's per-process total for the context, record both. The laptop GPU may drive the
  display; the pre-launch free-VRAM check covers it.

#### ML-A21. NOTE. Mapping cosmetics (no effect on meaning)

- (a) ML-32 (lines 486-491) appends V8's note without striking "right after E.2 ... one heavy job
  at a time"; the header's rule that the note governs (line 14-15) covers it. (b) ML-00 strikes the
  DRAFT banner before the FROZEN header exists; between Task 1 and Task 4 the file says neither.
  (c) The E.2 to E.2a/E.2b renames (A-3) rest on V8's mention of E.2b and the prompt's structure,
  not on a V decision that names the split itself; acceptable. (d) DECISIONS.md V9 inserts "Stage
  E.2a" before "Tasks 2 and 11". (e) M1's "avoids a second pass over the same months" (lines
  75-79) holds only where the price-path contract is D2's vehicle; where they differ (for example
  MNQ against NQ, MGC against GC, SIL against SI) the cluster's step 2 purchase still buys the
  vehicle's history.

#### ML-A22. NOTE. Q-1 to Q-3 are correctly left to the user, and Q-2 is not a conflict

- The prompt's scope says the older history "is bought in E.2b or later"; V8's "after E.2b" is
  inside "or later". Q-1 (no cap in V1) and Q-3 (no compute budget in V7) are rightly unapplied;
  D13's per-session rule (quote plus 10%) and per-request cap ($3.00) will bind the purchase session
  when it is written.

#### ML-A23. NOTE. M7.4's "not on disk for the route's process" is a store-level control

- Where: lines 380-385.
- The step 1 research-window files stay on the machine during E.ML-train (beside K2's screening).
  The canary tests the store, not file access. Suggest the training job assert a path allowlist
  (the training-window store only) in code, tested with a planted path. Not required by V1.

#### ML-A24. NOTE. PBO and DSR reporting details are unspecified but cannot change the rules

- Where: lines 327-332.
- Which P&L series feed CSCV over 36 configurations of three horizons, and per-split against path
  aggregation, are not stated; the design says these figures "inform; they do not decide anything".
  Optional to fix.

#### ML-A25. NOTE. Engine-only rules at the test are not modelled in the training target

- D9.7's price-limit exits and the locked-market rule apply through the engine at the test but not
  to training targets (rare dates). Acceptable; one sentence would make it explicit.

#### ML-A26. NOTE. LightGBM determinism needs one more setting

- Where: lines 173-176.
- `deterministic=true` alone does not fix run-to-run reproducibility across thread counts;
  E.2b should set force_col_wise=true (or force_row_wise) and record the lightgbm version in the
  route manifest. Implementation detail, no design change.

### 1.6 Verdict

**READY WITH FIXES.** Findings that must be fixed before the freeze: ML-A01 and ML-A02 (BLOCKING),
and ML-A03 to ML-A16 (SHOULD FIX; the stage prompt's Task 4 requires a ruling and fix for each).
Every fix stays within V1 to V9 as a fill-in or correction of a detail; none needs a new user
decision, though the freeze rulings should quote the new text for ML-A01, ML-A02, ML-A12 (the
embedding dimension), ML-A13 (which embargo option) and ML-A15 (the primary leg), because the user
has not seen those words.

Count per grade: BLOCKING 2, SHOULD FIX 14, NOTE 10 (26 findings).

Checks: 1 mapping HOLDS; 2 no post-data choice DOES NOT HOLD as written, holds after the fixes
with the code hashed before E.ML-buy; 3 partition HOLDS for every forbidden date, with ML-A05 to
state and ML-A18 recorded; 4 consistency HOLDS except the four items named in 1.4, all fixable
within V1 to V9.

Not done: nothing in the brief was left unfinished. I did not read reports/stage_e1_freeze_rulings.md
or reports/stage_e1_changes.md beyond what the manifest's FA-15 note states, since no finding
depended on them.

## Part 2: source-window amendment audit (Task 11)

Written 2026-09-25 06:41 PDT. Auditor: DeclarationAuditor-FableXHigh, resumed for the Task 11 brief. The auditor produced none of the work audited here (neither Task 2's records nor the amendment).

### 2.0 Inputs, the hash question, method

- Audited version of the amendment: reports/stage_e2a_source_window_amendment.md, sha256 `9fe401c1c156ebba38162256bf151d9888dec00e42cd24026d348d039e64f13d`. The brief named `95a040bb7d477e9dc85a17c6e8f9431690a06ebd50cb2a5c07188cd24eb98a9c`; the file on disk did not match. The lead's correction (06:35 PDT message; reports/stage_e2a_STATE.md line dated 06:35) says the earlier hash predates a one-phrase clock-time correction in the header ('about 06:35 PDT' to 'about 06:15 PDT') and nothing else changed. I could not verify the earlier version's content (it is not on disk or in git); this audit is of the version hashed above, mtime 2026-09-25 06:16:33 PDT, which the STATE file also records (finding SW-A01).
- Task 2's evidence: reports/stage_e2a_source_windows.json (sha256 `f2442dcc07566216e29b8190efc098369524497573aeb3c06d4e3b97bb50d7f9`, which equals the hash the amendment cites) and .md; the fetched texts under the scratch directory e2a_sources/ (txt/, txtraw/, passages.json, verify.py, verify_result.json, fetchlog.jsonl). 37 members, 75 sources, 145 rows, 71 passages.
- The rule: docs/NULL_CRITERIA_E.md section 3 (frozen, hash verified in the E.1 manifest check below); V9 (docs/DECISIONS.md, 2026-09-25); the stage prompt's Task 11 wording; the FA-06 list in reports/stage_e1_freeze_rulings.md; the six removed members' entries in reports/stage_e0_catalog_K2.md, _K3.md, _K4.md, _K8.md and their records in reports/stage_e0_catalog.json.
- Own code (scratch fable_p3/check_amendment.py): my own verbatim check (Unicode NFKC, whitespace collapsed, substring test against every fetched text of the source), my own classification of every row from its recorded first and last period at the recorded granularity against [2019-05-06, 2024-02-29], my own recomputation of every member's label under the amendment's readings, and a parse of the amendment's table for the comparison. No web access was needed; every source's fetched text was on disk.

### 2.1 Check 1: passages, periods and classifications

- Verbatim: 71 of 71 passages are substrings of a fetched text of their source under the worker's per-passage keys (K3-020's second passage lives in the companion paper's text, key K3-020b; K3-025's passage is K3-023's description of it, flagged secondary). My first pass, which ignored those two keys, found 69 of 71; the two are explained, not failures (SW-A07). Neither is cited by a removed member.
- Classification: for all 145 rows my class (overlaps, no overlap, unknown, no data sample) equals the amendment's, and my member labels equal its 'After' column for all 37 members and its 'Supporting-only' column as well; the six removed are exactly the six I compute.

Every row of the six removed members (13 rows, 12 distinct sources):

| Member | Source (role) | Recorded window | Passage (excerpt) | States the period? | Class | Verdict |
|---|---|---|---|---|---|---|
| K2-predrift-01 | K2-007 (supporting) | 2008-01-01..2014-03-31 (day) | Our second-by-second transaction data from Genesis Financial Technologies spans the period from January 1, 200... | yes | no overlap | CONFIRMED |
| K3-ldnmom-01 | K3-017 (supporting) | 1996-02..2013-12 (month) | They begin in February 1996 for JPY, GBP, CHF, CAD, NZD, and DKK and in January, 1999 for EUR. Data for all cu... | yes | no overlap | CONFIRMED |
| K3-ldnmom-01 | K3-002 (supporting) | 2006-01-02..2016-06-30 (day) | ICAP EBS Level 5 (or Level 2) data (proprietary data, purchased by the first author) from January 2, 2006 to J... | yes | no overlap | CONFIRMED |
| K3-ldnmom-01 | K3-021 (supporting) | 2008-01..2014-03 (month) | 01/2010-03/2014: EURUSD, EURJPY, EURGBP, EURCHF, GBPCHF, USDJPY, USDGBP, USDCHF 01/2008-03/2014: EURSEK, AUDUS... | yes | no overlap | CONFIRMED |
| K3-ldnmom-01 | K3-019 (other) | 2010-10-28..2017-06-14 (day) | Our sample period is approximately two and a half years from the 28 October 2010, to the 5 June 2015, and arou... | yes | no overlap | CONFIRMED |
| K3-ldnmom-01 | K3-004 (other) | 2002..2013 (year) | The data set runs from 2002 to 2013, and all of the calculations in the analysis are expressed as an average o... | yes | no overlap | CONFIRMED |
| K3-ldnmom-01 | K3-018 (other) | 2010-01-01..2013-12-31 (day) | Our spot data include all GBP/USD, AUD/USD and NZD/USD transactions between January 1, 2010 and December 31, 2... | yes | no overlap | CONFIRMED |
| K3-mehedge-01 | K3-001 (supporting) | 2004-04-28..2012-12-31 (day) | These prices are available starting from April 28, 2004 and end on December 31, 2012 giving us a sample period... | yes | no overlap | CONFIRMED |
| K3-mehedge-01 | R-K3-014 (other) | n/a (documentation, no data sample) | (none) | no sample to state (CME product case-study page, 1,121 words, no data period; checked) | no data sample | CONFIRMED |
| K3-mehedge-01 | K3-002 (other) | 2006-01-02..2016-06-30 (day) | ICAP EBS Level 5 (or Level 2) data (proprietary data, purchased by the first author) from January 2, 2006 to J... | yes | no overlap | CONFIRMED |
| K4-ngpre-01 | K4-001 (supporting) | 2003-03..2018-12 (month) | From Bloomberg, we obtain the daily price, trading volume and open interest series of 499 Henry Hub Natural Ga... | yes | no overlap | CONFIRMED Note: the intraday data are 'over the same sample period' (Thomson Reuters Tick History), checked in the text; the 2019 mentions are the paper's date and citations. |
| K8-flight-01 | K8-003 (supporting) | 2007..2018 (year) | We use high-frequency intra-day gold and S&P500 data covering the period from 2007 to 2018 | yes | no overlap | CONFIRMED Abstract only; the abstract states the period. |
| K8-oilcad-01 | K8-006 (supporting) | 2005-01-03..2009-12-31 (day) | This sample extends from 03/01/2005 to 31/12/2009. // over the period 1986-2015 | yes | no overlap | CONFIRMED Note: the text also has a daily sample 02/01/1986-31/07/2015 (Table 1), which the row omits; it lies before the window too. |
| K8-oilcad-01 | K8-001 (supporting) | 2003-10..2017-10 (month) | The sample period for all data except the exchange rates are 2003M10 to 2017M10. The exchange rate data during... | yes | no overlap | CONFIRMED The exchange-rate series start April 2006 (same passage); the end 2017M10 is what matters. |

Sample of other members' rows (30 sources, covering CP1, CP2 and CP3 chains, K2, K3, K5, K6, K7 and cross-cluster sources; each read against its recorded period):

| Source | Recorded window | Passage (excerpt) | Class | Verdict |
|---|---|---|---|---|
| D1-A10 | 1974-12..2020-05 (month) | Our sample period covers almost 45 years from December 1974 to May 2020. | overlaps | CONFIRMED (1974-12..2020-05 overlaps, so every CP1 port keeps its label through the D6 chain) |
| D1-A28 | 1993..2013 (year) | Based on high frequency S & P 500 exchange-traded fund (ETF) data from 1993–2013, we show an intraday momentum pattern | no overlap | CONFIRMED |
| D1-B5 | 2021-12..2025-08 (month) | The primary dataset is 72,604 five-minute OHLCV bars for MNQ continuous front-month futures, regular trading hours only ... | overlaps | CONFIRMED (the MNQ sample (2021-12..2025-08) overlaps the confirmation window, so every CP2 port keeps its label through the D6 chain) |
| D1-B2 | 2014..2016 (year) | The analysis uses the complete transaction audit trail for the select futures products from the beginning of 2014 until ... | no overlap | CONFIRMED |
| D1-B3 | 2010-05-03..2010-05-06 (day) | This paper uses audit trail data during May 3-6, 2010 to examine the eco-system of the S&P 500 E-mini futures during the... | no overlap | CONFIRMED |
| D1-B4 | 1983-03-30..2011-01-26 (day) | We apply the testing strategy presented above to a time series of U.S. crude oil futures prices obtained from Commodity ... | no overlap | CONFIRMED |
| K1-002 | 2011-01-03..2021-12-31 (day) | the data for Dow Jones futures and Nasdaq futures (3 January 2011–31 December 2021) are from one of the top global finan... | overlaps | CONFIRMED |
| K2-021 | 1990-01..2018 (month) | We consider data from January 1990 to the end of 2018. // The end-of-month effect is persistent over our sample period (... | no overlap | CONFIRMED |
| K2-003 | 2016-01..2025-12 (month) | for each month from January 2016 to December 2025 | overlaps | CONFIRMED |
| K2-005 | 2009-03..2011-06 (month) | averaged across six roll events from March 2010 through June 2011 // using the exponentially weighted rolling average of... | no overlap | CONFIRMED (the text gives two spans (six rolls from March 2010 through June 2011; a forecast history starting March 2009); the recorded window is their union, the conservative choice) |
| K3-016 | 1999-01..2018-12 (month) | Our full sample starts in January 1999 and ends in December 2018 // Data from CME (BA100% CM E ) is daily and covers the... | no overlap | CONFIRMED (two samples in the text (the 1999-2018 quote sample and CME daily data 2009-2018); the recorded window is the wider) |
| K3-005 | 2018..2020 (year) | by analyzing the recent historical data of the USD/JPY rate during 2018 to 2020 | overlaps | CONFIRMED (the fetched text gives only '2018 to 2020'; extended to whole years it overlaps, which keeps K3-tkypre-01 and K3-tkypost-01 labelled; a finer reading could not remove a label since 2019 and 2020 overlap the window anyway) |
| K3-010 | 2012..2024 (year) | Using M5 Dukascopy data for spot pairs (2012–2024) and M1 Databento data for 6J CME futures (2019–2024), with a strict i... | overlaps | CONFIRMED |
| K3-020 | 2015-02-15..2023-12-31 (day) | The sample period available for the analysis covers over 9 years, from February 15, 2015, the day in which the current m... | overlaps | CONFIRMED (the second passage is from the companion paper's text (verify key K3-020b); both papers state the same span) |
| K3-022 | 1999-01..2013-12 (month) | Level 5 data: January 2006 to December 2013. // Level 2 data: January 1999 to December 2005. Currency pairs 'USD-JPY' | no overlap | CONFIRMED (two data levels (1999-2005 and 2006-2013); the recorded window is their union) |
| K3-023 | 1997-01..2007-06 (month) | We employ a detailed transactions data set for the period January 1997 to the beginning of June 2007 from EBS the domina... | no overlap | CONFIRMED |
| K3-024 | 1993-01..2005-08 (month) | The sample periods cover the period from the beginning of January 1993 to the end of August 2005 for the CHF/USD and JPY... | no overlap | CONFIRMED |
| K5-001 | 2007-01-01..2012-12-31 (day) | The full period (Sf) covers 1 January 2007 to 31 December 2012. | no overlap | CONFIRMED |
| K5-006 | 2008-01-01..2018-06-27 (day) | Daily prices, open interest, and the trading volume for futures contracts on silver and gold trading on the Chicago Merc... | no overlap | CONFIRMED |
| K5-012 | 2012-02-14..2015-04-30 (day) | Our data extends from the 14th February 2012 to the 30th of April, 2015, a sample period that allows us to examine the i... | no overlap | CONFIRMED |
| K5-028 | 2009-01-01..2020-03-31 (day) | Daily and hourly data for gold and oil over the period 01.01.2009–31.03.2020 (GMT + 3 time zone) are used. | overlaps | CONFIRMED (the worker recorded the methodology's end date (31.03.2020) over the introduction's (01.09.2019); the row overlaps either way) |
| K6-001 | 1978-02-01..1991-07-31 (day) | A continuous series is constructed using four-month trading periods for each of the March, August, and December contract... | no overlap | CONFIRMED (the abstract says July 30, 1991 and the data section July 31; no overlap either way) |
| K6-011 | 2009..2019 (year) | the yellow line is the average observed from 2009-2018; gray series represent the values observed in other, individual y... | overlaps | CONFIRMED (the window is read from a chart caption (2009-2019 individual years); the 2019 report lies inside the window under either reading) |
| K6-026 | 2015..2015 (year) | The high-frequency data used in this study covers the total trading activity of 2015, amounting to 243 trading days. | no overlap | CONFIRMED |
| K6-028 | 2013..2020 (year) | in the CME corn futures market using high-frequency data from 2013 to 2020 | overlaps | CONFIRMED |
| K7-002 | 2019-04-01..2020-01-31 (day) | The dataset consists of minute-by-minute transaction data and covers the period from 1 April 2019 to 31 January 2020 sum... | overlaps | CONFIRMED |
| K7-025 | 2024-03-05..2024-09-06 (day) | Table 3.20: Descriptive statistics for the event on March 5th 2024: Micro BTC futures on CME and spot BTC on Binance // ... | no overlap | CONFIRMED (the window is read from two table captions naming event dates (2024-03-05 and 2024-09-06); the study's full sample may be wider, but its member (K7-rev2h-01) keeps its label on K7-002 regardless; these dates are holdout-2 dates, as the amendment notes) |
| K7-040 | 2015-10-08..2024-10-15 (day) | Our analysis is based on the hourly BTC data from the Gemini Data page in intervals ranging from 2015-10-08 to 2024-10-1... | overlaps | CONFIRMED |
| K4-050 | 2010..2026 (year) | The study uses sixteen years of one-minute data (2010-2026), split into fixed exploration, confirmation, and reserve win... | overlaps | CONFIRMED |
| R-K6-032 | 2010-01..2021-11 (month) | Using high-frequency tick data from January 2010 to November 2021, we document the presence and drivers of intraday mark... | overlaps | CONFIRMED |

Every unknown row I read is unknown for a stated reason (a book not fetched, an abstract with no period, a blog with no data, a secondary description) and keeps its member's label, as the rule requires.

### 2.2 Check 2: completeness of the six removed members' sources

| Member | What the frozen entry cites (read in full) | Task 2's sources for it | Complete? |
|---|---|---|---|
| K2-predrift-01 | K2-007 (P-K2-007-a to -f); EC-ISM and EC-CAL (release calendars); 'Rule 3' (a catalog convention); the entry's own line 'the paper's sample is 2008-2014 (log)' | K2-007 | yes |
| K3-ldnmom-01 | K3-017 (P-K3-017-a, -b, -c and 'the K3-017 block'); K3-002 (P-K3-002-b, -d); K3-021 (P-K3-021-a, -c); K3-019 (P-K3-019-a); K3-004 (P-K3-004-d); K3-018 (P-K3-018-a); EC-CAL, EC-EW, the T_L clock; the tag 'port of D.1 family C' | K3-017, K3-002, K3-021, K3-019, K3-004, K3-018 | yes |
| K3-mehedge-01 | K3-001 (P-K3-001-a, -b, -d, -e and 'the K3-001 block'); R-K3-014 (BTIC routing, 'verbatim in the log'); K3-002 (P-K3-002-d); STOXX Ltd., Nikkei Inc. and FRED as index-data providers (no sample); EC-CAL, EC-EW; the tag 'port of D.1 family E'; the partition's 21:52 ruling | K3-001, R-K3-014, K3-002 | yes |
| K4-ngpre-01 | K4-001 (P-K4-001-a to -f); EC-NGS and EC-CAL; Topstep F6 (the release table); the tag 'port of D.1 family E' | K4-001 | yes |
| K8-flight-01 | K8-003 (P-K8-003-a, -b, -c); 'D15's B4 feature' (a design reference); K8 conventions C5, C6, C9, C12, C13; EC-CAL, EC-FOMC, EC-BLS; MES's S from D.1f; the entry's own 'Source window and label' line (2007 to 2018, no overlap) | K8-003 | yes |
| K8-oilcad-01 | K8-006 (P-K8-006-a to -e and 'the K8-006 block'); K8-001 (P-K8-001-a, -b, -e, -f, -g, -h, Table 5); K4 catalog C10, K3 catalog C8; EC-CAL, EC-FOMC, EC-BLS, EC-WPSR; 'Rule 7'; the entry's own 'Source window and label' line (K8-006 2005-2009 and 1986-2015; K8-001 2003M10-2017M10; no label) | K8-006, K8-001 | yes |

Items in the entries that are not literature sources and carry no data sample, and so were rightly not recorded: release and holiday calendars (EC-*), Topstep's release table (F6), catalog conventions (C5 to C13, 'Rule 3', 'Rule 7'), design references (D15's B4, D2, D6), the T_L clock, index-data providers (STOXX, Nikkei, FRED), and the program's own MES record. The classification tags 'port of D.1 family C' and 'port of D.1 family E' name a family, not a paper, and are not evidence the member was chosen on (SW-A05). Three of the six entries already carried their own source-window statement (K2-predrift-01 '2008-2014 (log)', K8-flight-01 '2007 to 2018', K8-oilcad-01 both sources), each agreeing with Task 2's record (SW-A06).

### 2.3 Check 3: the readings

- Widest confirmation window [2019-05-06, 2024-02-29]: faithful. The earliest S_X is 2019-05-06 (D4) and the end is frozen; a member's own window (a later S_X; for K8 the intersection, for K8-flight-01 no earlier than 2020-02-03) is inside it, so this reading can only find more overlaps, never fewer. Cannot wrongly remove a label.
- Granularity extension (a year to its whole year, a month to its whole month): faithful and outward, so it can only add overlaps. Cannot wrongly remove.
- 'Any of its sources' (every cited source, supporting or other): the prompt's Task 11 words; stricter than the frozen rule's 'supporting source'. It removes 6 where the supporting-only reading would remove 8 (K3-ldnrev-01 kept on K3-020's 2015-2023 sample; K5-pmfix-01 on K5-013 unknown). Cannot wrongly remove; the lead reports the narrower reading for information only, which is right.
- Unknown keeps the label; a secondary description (K3-025) counts as unknown: faithful to the frozen rule's own fallback ('not recorded is treated as source-overlap') and conservative.
- 'No data sample' (window_applicable false: K6-048, K6-050, R-K3-014, K3-hdr-ECB) neither keeps nor removes: faithful in my judgment. The label exists because a member 'was chosen partly on evidence from that window'; a product page, FAQ, reference guide or calendar page carries no sample and no evidence from any window, so it cannot create the overlap the rule guards against. The reading is decisive for exactly one removal, K3-mehedge-01 (R-K3-014): I read that page's text (a CME case study on BTIC exposure to the WM/Refinitiv fix; its only years are 1994, the fix's creation, and 2000, 2005, 2026 in page furniture) and confirm it has no data sample. The three other documentation rows belong to members that keep their labels on other rows. The stricter alternative, treating documentation as unknown, would keep K3-mehedge-01 labelled; recorded for the lead (SW-A04). Could this reading wrongly remove a label? Only if a source with a real sample were classified as documentation; I checked all four and none is.
- A member loses the label only if every source is 'no overlap' or 'no data sample': the correct conjunction of the prompt's rule; my recomputation reproduces it for all 37.

### 2.4 Check 4: scope

- The amendment's table has 37 rows, exactly the FA-06 fallback list; every 'Before' is 'source-overlap (fallback)'; 'After' is 'not source-overlap' for 6 and 'source-overlap' for 31. The 16 members the frozen catalog already labels are absent from the table and unchanged. In reports/stage_e0_catalog.json the 37 carry source_overlap false and the 16 true, as the amendment's premise states. No member is added, no rule text is changed, no label is added.
- No frozen file changed: every one of the 32 files in reports/stage_e1_freeze.json matches its sha256 (the freeze audit compared against its 848f331 blob). The amendment and Task 2's two files are new, untracked files.

### 2.5 Findings

- SW-A01. NOTE. The brief's hash for the amendment (95a040bb...) does not match the file; the lead's correction attributes the difference to a one-phrase clock-time fix in the header. Audited version: `9fe401c1c156ebba...`. Task 11's commit should name this hash. If the earlier version is ever cited, the two must be diffed, since I could not see it.
- SW-A02. NOTE. K8-006's recorded window (2005-01-03..2009-12-31, the 5-minute Canadian sample) omits the paper's daily sample 02/01/1986-31/07/2015 (Table 1), which the frozen entry itself records ('1986-2015 for the daily data'). Both lie before the window; the class and the removal stand. Task 2's row would be more complete as 1986-01-02..2015-07-31.
- SW-A03. NOTE. K7-025's window is read from two table captions (event dates 2024-03-05 and 2024-09-06); the study's full sample may be wider. K7-rev2h-01 keeps its label on K7-002 regardless, so nothing turns on it; the dates fall in holdout-2, as the amendment's note says.
- SW-A04. NOTE. The 'no data sample' reading decides K3-mehedge-01's removal (R-K3-014). Verified on the text; the alternative (documentation counts as unknown) is the only reading of the frozen rule under which a seventh member would stay labelled. The lead should state the reading in the Task 11 rulings so the choice is on record.
- SW-A05. NOTE. 'Port of D.1 family C/E' tags in K3-ldnmom-01, K3-mehedge-01 and K4-ngpre-01 are family classifications, not cited papers; the D.1 family literature is not treated as a source of these members. I agree: the entries cite it as a class label, and the mechanism evidence is the K-numbered sources recorded.
- SW-A06. NOTE. K2-predrift-01, K8-flight-01 and K8-oilcad-01 already state their source windows in the frozen entries (and K8's two say 'no label'); FA-06's heuristic listed them anyway. The amendment's outcome agrees with the entries' own statements, so the E.1 fallback label on these three was a recording artifact, now resolved.
- SW-A07. NOTE. My first verbatim pass reported 69 of 71 because it did not apply the worker's per-passage verify keys (K3-020b, K3-023); with them, 71 of 71. Recorded so the two numbers are not read as a disagreement.

### 2.6 Verdict of Part 2

- Removed members: K2-predrift-01 CONFIRMED; K3-ldnmom-01 CONFIRMED; K3-mehedge-01 CONFIRMED (on the 'no data sample' reading, SW-A04); K4-ngpre-01 CONFIRMED; K8-flight-01 CONFIRMED; K8-oilcad-01 CONFIRMED.
- Sampled rows of other members: 30 sources CONFIRMED, with the notes in the table; all 145 row classes and all 37 labels reproduced.
- Findings: BLOCKING 0, SHOULD FIX 0, NOTE 7 (SW-A01 to SW-A07).
- Verdict: **the amendment is faithful to the frozen rule and V9; every removal is confirmed.** Labels whose removal I confirm: K2-predrift-01, K3-ldnmom-01, K3-mehedge-01, K4-ngpre-01, K8-flight-01, K8-oilcad-01. The other 31 keep 'source-overlap'.


## Part 3: independent recomputation (Task 12)

### 3a: sizes, vehicles, translated epsilon, costs

Written 2026-09-25 06:33 PDT. Auditor: DeclarationAuditor-FableXHigh, resumed for the Task 12 brief (part 3a). The auditor produced none of the numbers checked here.

#### 3a.0 Inputs, method, boundaries

- Frozen inputs, sha256 verified at the start of this part against the lead's message (all four match): reports/stage_e2a_vehicles.json `1f1cafee43309617...`, reports/stage_e2a_vehicle_sizes.json `280d7e9df1953069...`, reports/stage_e2a_costs.json `f4360bb77272d033...`, reports/stage_e2a_vehicle_rule_readings.md `8c3c29dd6531782b...`.
- Own code, under the scratchpad directory fable_p3/: sizes.py (r_c, q_c, rho_c), compare_sizes.py, choice.py (vehicle, cost per dollar of risk, translated epsilon), costs_fable.py (D8 from the raw mbp-1 files), alts.py (alternative readings), write_part3a.py (this section). None of screening/vehicles*.py, sim/calibrate_costs.py, sim/cost_rule.py, sim/cost_report*.py, sim/product_costs.py or data/build_bars*.py was imported. Used as data: the research parquets, reports/stage_e0_liquidity.json (ticks, tick values), reports/stage_e0_topstep_facts.json F3.7 and F3.6 (commissions), reports/stage_e1_purchase.json (the mbp-1 files and their sha256, each verified by my code before the file was decoded), the group calendar modules data/calendars/*.py and data/cme_calendar.py (closures, early halts, sessions, BOOKED_FORWARD, EARLY_SETTLEMENT_CT), and each parquet's metadata `rolls` record (the vendor's symbology.resolve roll events) for the roll blackout. D1's table (docs/STAGE_E_DESIGN.md) for the admissible contracts, the 31 exposures and the ADV tie rule; D6's session table; D9.5 and D9.11 caps; R* = $360.68.
- Compute: one process, OMP_NUM_THREADS=1, nice 10, one heavy step at a time; the mbp-1 files streamed one file at a time in 1,000,000-record chunks with five int64 arrays kept per day (largest day MBT 2026-02-11, 3,580,827 records, about 170 MB of arrays). Research-window data were used only for r_c and the cost tables; no returns, charts or price summaries were computed.
- Readings applied: R1 to R12 of the lead's readings file and rulings L-1 to L-11 as the brief says; CostCoder's R1 to R10 for the cost tables. Where the frozen text allows another reading, 3a.4 says what it would change.
- Tolerances: sizes, exact equality of the rationals r_c, rho_c and the sum of tick moves, and of the date sets (used, and excluded by cause); choice, exact equality of status, vehicle, q_c, epsilon, candidate and preferred sets, and relative 1e-9 on the cost per dollar of risk and the one-side slippage (floating point); cost tables, 1e-9 ticks on s_b and the round turn, 0.5 s on valid seconds, exact equality of dates with quotes, medians, depth terms, fallback flags, headline bucket sets and event-window sides.

#### 3a.1 r_c, q_c, rho_c for the 45 admissible contracts

Every contract: the same dates used (count and list), the same exclusions by cause (roll blackout, vendor-degraded, closure or early close at or before C_X, no bar in the window), the same list of dates whose exact O_X or C_X - 1 bar was missing (R3's as-of substitution), the same vendor price factor (100 x the E.0 tick for ZC, ZW, ZS, ZL, HE, LE; 1 x elsewhere, checked on the prices), the same sum of tick moves, and identical rationals for r_c and rho_c. For non-crypto products I also asserted that every day-session bar lies on its trade date's own CT calendar day (0 exceptions); for MBT the L-10 rule was applied (bars on the trade date's own CT day only; 7 booked-forward sessions never read).

| Contract | Exposure | O-C (CT) | Dates used | r_c USD (mine) | r_c USD (frozen) | Sum ticks | cap | q_c | rho_c | Exact bars missing O/C | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| MNQ | Nasdaq-100 | 08:30-15:00 | 285 / 285 | 363.4614 | 363.4614 | 207173 / 207173 | 10 / 10 | 1 / 1 | 1.0077 / 1.0077 | 0/0 | VERIFIED |
| NQ | Nasdaq-100 | 08:30-15:00 | 286 / 286 | 3613.0769 | 3613.0769 | 206668 / 206668 | 1 / 1 | 1 / 1 | 10.0174 / 10.0174 | 0/0 | VERIFIED |
| RTY | Russell 2000 | 08:30-15:00 | 286 / 286 | 1060.7168 | 1060.7168 | 60673 / 60673 | 1 / 1 | 1 / 1 | 2.9409 / 2.9409 | 0/0 | VERIFIED |
| M2K | Russell 2000 | 08:30-15:00 | 286 / 286 | 106.1346 | 106.1346 | 60709 / 60709 | 10 / 10 | 3 / 3 | 0.8828 / 0.8828 | 0/0 | VERIFIED |
| MYM | Dow | 08:30-15:00 | 286 / 286 | 131.1486 | 131.1486 | 75017 / 75017 | 10 / 10 | 3 / 3 | 1.0908 / 1.0908 | 0/0 | VERIFIED |
| YM | Dow | 08:30-15:00 | 286 / 286 | 1312.2727 | 1312.2727 | 75062 / 75062 | 1 / 1 | 1 / 1 | 3.6383 / 3.6383 | 0/0 | VERIFIED |
| ZT | 2-year | 07:20-14:00 | 286 / 286 | 112.6803 | 112.6803 | 4125 / 4125 | 1 / 1 | 1 / 1 | 0.3124 / 0.3124 | 0/0 | VERIFIED |
| ZF | 5-year | 07:20-14:00 | 286 / 286 | 135.5441 | 135.5441 | 4962 / 4962 | 1 / 1 | 1 / 1 | 0.3758 / 0.3758 | 0/0 | VERIFIED |
| ZN | 10-year | 07:20-14:00 | 286 / 286 | 204.9279 | 204.9279 | 3751 / 3751 | 1 / 1 | 1 / 1 | 0.5682 / 0.5682 | 0/0 | VERIFIED |
| TN | Ultra 10-year | 07:20-14:00 | 286 / 286 | 259.9432 | 259.9432 | 4758 / 4758 | 1 / 1 | 1 / 1 | 0.7207 / 0.7207 | 0/0 | VERIFIED |
| ZB | Bond | 07:20-14:00 | 286 / 286 | 402.0979 | 402.0979 | 3680 / 3680 | 1 / 1 | 1 / 1 | 1.1148 / 1.1148 | 0/0 | VERIFIED |
| UB | Ultra bond | 07:20-14:00 | 286 / 286 | 501.4205 | 501.4205 | 4589 / 4589 | 1 / 1 | 1 / 1 | 1.3902 / 1.3902 | 0/0 | VERIFIED |
| 6E | EUR | 07:20-14:00 | 293 / 293 | 319.4539 | 319.4539 | 14976 / 14976 | 1 / 1 | 1 / 1 | 0.8857 / 0.8857 | 0/1 | VERIFIED |
| M6E | EUR | 07:20-14:00 | 293 / 293 | 32.0350 | 32.0350 | 7509 / 7509 | 10 / 10 | 10 / 10 | 0.8882 / 0.8882 | 3/6 | VERIFIED |
| E7 | EUR | 07:20-14:00 | 293 / 293 | 160.7295 | 160.7295 | 7535 / 7535 | 1 / 1 | 1 / 1 | 0.4456 / 0.4456 | 51/70 | VERIFIED |
| 6A | AUD | 07:20-14:00 | 293 / 293 | 183.6519 | 183.6519 | 10762 / 10762 | 1 / 1 | 1 / 1 | 0.5092 / 0.5092 | 0/2 | VERIFIED |
| M6A | AUD | 07:20-14:00 | 293 / 293 | 18.4164 | 18.4164 | 5396 / 5396 | 10 / 10 | 10 / 10 | 0.5106 / 0.5106 | 64/55 | VERIFIED |
| 6B | GBP | 07:20-14:00 | 293 / 293 | 186.2201 | 186.2201 | 8730 / 8730 | 1 / 1 | 1 / 1 | 0.5163 / 0.5163 | 0/1 | VERIFIED |
| M6B | GBP | 07:20-14:00 | 293 / 293 | 18.7137 | 18.7137 | 8773 / 8773 | 10 / 10 | 10 / 10 | 0.5188 / 0.5188 | 70/47 | VERIFIED |
| 6C | CAD | 07:20-14:00 | 293 / 293 | 120.2901 | 120.2901 | 7049 / 7049 | 1 / 1 | 1 / 1 | 0.3335 / 0.3335 | 0/4 | VERIFIED |
| 6J | JPY | 07:20-14:00 | 293 / 293 | 204.8208 | 204.8208 | 9602 / 9602 | 1 / 1 | 1 / 1 | 0.5679 / 0.5679 | 0/0 | VERIFIED |
| 6S | CHF | 07:20-14:00 | 293 / 293 | 410.7509 | 410.7509 | 19256 / 19256 | 1 / 1 | 1 / 1 | 1.1388 / 1.1388 | 1/2 | VERIFIED |
| 6N | NZD | 07:20-14:00 | 293 / 293 | 156.4846 | 156.4846 | 9170 / 9170 | 1 / 1 | 1 / 1 | 0.4339 / 0.4339 | 2/2 | VERIFIED |
| CL | WTI crude | 08:00-13:30 | 256 / 256 | 918.7891 | 918.7891 | 23521 / 23521 | 1 / 1 | 1 / 1 | 2.5474 / 2.5474 | 0/0 | VERIFIED |
| MCL | WTI crude | 08:00-13:30 | 258 / 258 | 91.5698 | 91.5698 | 23625 / 23625 | 10 / 10 | 4 / 4 | 1.0155 / 1.0155 | 0/0 | VERIFIED |
| QM | WTI crude | 08:00-13:30 | 258 / 258 | 457.2190 | 457.2190 | 9437 / 9437 | 1 / 1 | 1 / 1 | 1.2677 / 1.2677 | 0/2 | VERIFIED |
| NG | Henry Hub gas | 08:00-13:30 | 259 / 259 | 639.3050 | 639.3050 | 16558 / 16558 | 1 / 1 | 1 / 1 | 1.7725 / 1.7725 | 0/0 | VERIFIED |
| MNG | Henry Hub gas | 08:00-13:30 | 262 / 262 | 65.3092 | 65.3092 | 17111 / 17111 | 10 / 10 | 6 / 6 | 1.0864 / 1.0864 | 1/1 | VERIFIED |
| QG | Henry Hub gas | 08:00-13:30 | 262 / 262 | 159.1603 | 159.1603 | 3336 / 3336 | 1 / 1 | 1 / 1 | 0.4413 / 0.4413 | 4/22 | VERIFIED |
| RB | RBOB | 08:00-13:30 | 241 / 241 | 1012.7925 | 1012.7925 | 58115 / 58115 | 1 / 1 | 1 / 1 | 2.8080 / 2.8080 | 0/0 | VERIFIED |
| HO | ULSD | 08:00-13:30 | 253 / 253 | 1441.3968 | 1441.3968 | 86827 / 86827 | 1 / 1 | 1 / 1 | 3.9963 / 3.9963 | 0/0 | VERIFIED |
| MGC | gold | 07:20-12:30 | 290 / 290 | 258.5897 | 258.5897 | 74991 / 74991 | 10 / 10 | 1 / 1 | 0.7170 / 0.7170 | 0/1 | VERIFIED |
| GC | gold | 07:20-12:30 | 290 / 290 | 2586.9655 | 2586.9655 | 75022 / 75022 | 1 / 1 | 1 / 1 | 7.1725 / 7.1725 | 0/1 | VERIFIED |
| SIL | silver | 07:20-12:25 | 290 / 290 | 931.0517 | 931.0517 | 54001 / 54001 | 2 / 2 | 1 / 1 | 2.5814 / 2.5814 | 0/0 | VERIFIED |
| SI | silver | 07:20-12:25 | 290 / 290 | 4653.9655 | 4653.9655 | 53986 / 53986 | 1 / 1 | 1 / 1 | 12.9033 / 12.9033 | 0/0 | VERIFIED |
| HG | copper | 07:10-12:00 | 290 / 290 | 1101.2931 | 1101.2931 | 25550 / 25550 | 1 / 1 | 1 / 1 | 3.0534 / 3.0534 | 0/0 | VERIFIED |
| MHG | copper | 07:10-12:00 | 290 / 290 | 110.2155 | 110.2155 | 25570 / 25570 | 2 / 2 | 2 / 2 | 0.6112 / 0.6112 | 2/1 | VERIFIED |
| ZC | corn | 08:30-13:15 | 271 / 271 | 158.1642 | 158.1642 | 3429 / 3429 | 1 / 1 | 1 / 1 | 0.4385 / 0.4385 | 0/0 | VERIFIED |
| ZW | wheat | 08:30-13:15 | 277 / 277 | 234.7473 | 234.7473 | 5202 / 5202 | 1 / 1 | 1 / 1 | 0.6508 / 0.6508 | 0/0 | VERIFIED |
| ZS | soybeans | 08:30-13:15 | 279 / 279 | 304.3907 | 304.3907 | 6794 / 6794 | 1 / 1 | 1 / 1 | 0.8439 / 0.8439 | 0/0 | VERIFIED |
| ZM | soybean meal | 08:30-13:15 | 273 / 273 | 212.6374 | 212.6374 | 5805 / 5805 | 1 / 1 | 1 / 1 | 0.5895 / 0.5895 | 0/0 | VERIFIED |
| ZL | soybean oil | 08:30-13:15 | 282 / 282 | 304.8298 | 304.8298 | 14327 / 14327 | 1 / 1 | 1 / 1 | 0.8452 / 0.8452 | 0/0 | VERIFIED |
| HE | lean hogs | 08:30-13:00 | 270 / 270 | 322.9630 | 322.9630 | 8720 / 8720 | 1 / 1 | 1 / 1 | 0.8954 / 0.8954 | 0/0 | VERIFIED |
| LE | live cattle | 08:30-13:00 | 264 / 264 | 707.1591 | 707.1591 | 18669 / 18669 | 1 / 1 | 1 / 1 | 1.9606 / 1.9606 | 0/0 | VERIFIED |
| MBT | bitcoin | 08:30-15:00 | 260 / 260 | 120.6135 | 120.6135 | 62719 / 62719 | 1 / 1 | 1 / 1 | 0.3344 / 0.3344 | 0/0 | VERIFIED |

Counts: VERIFIED 45, VERIFIED WITH NOTES 0, DISCREPANCY 0 (45 contracts).

Notes on the sizes (none changes a number):
- Roll blackout. The frozen rule (NULL_CRITERIA_E 4, D11.4: roll boundaries from symbology.resolve, never inferred from the data; blackout = the splice trade date and the two group trade dates before it, L-8) counts every vendor roll event, including flip-flops that touched no bar. Two such events exist in the window: ZC 2025-04-13 (ZCK5 to ZCN5) reversed on 04-14, and HE 2026-03-15 (HEJ6 to HEM6) reversed on 03-16; both map to a splice trade date whose bars carry one instrument throughout. My first pass, which read splices off the bars' instrument changes, kept ZC 2025-04-10/11/14 and HE 2026-03-12/13/16 and gave ZC r_c 158.1642 -> 158.9872 and HE 322.9630 -> 323.4191; neither q_c nor any band changes (ZC rho 0.4385 vs 0.4408, both undersized; HE 0.8954 vs 0.8967). The frozen reading is the faithful one; the bars-based reading is recorded here only as the alternative. Under the vendor schedule my splice dates equal the frozen ones for all 45 contracts.
- Vendor-degraded dates: reproduced from the parquets' per-bar flag as the trade dates whose day-session bars are flagged (the lead's Q-2 answer); the prior-evening bars of the next trade date do not exclude it (for example ZN 2025-09-18, 09-25, 2026-03-17 are used, as in the frozen file).
- The census (reports/stage_e0_liquidity.json) stores an ADV for some contracts that differs from D1's table (ZT 1,000,000 vs 1,325,938; ZF 1,800,000 vs 1,941,530; ZC 437,000 vs 505,663; SIL 48,000 vs 134,882; MBT 75,000 vs 69,615). R9's tie rule names D1's table, which I used; no cost tie occurred, so the ADV never decided anything.
- Rounding edge: MNG's R*/r_c = 5.523 rounds to q_c = 6; under the exact-bars-only alternative (3a.4 B) it would be 5.498 and q_c = 5. MNG is not a vehicle, so nothing frozen depends on it.

#### 3a.2 Vehicle choice, cost per dollar of risk and translated epsilon for the 31 exposures

The cost per dollar of risk (R8) was recomputed from the frozen cost table's buckets (side_ticks per bucket, minute-weighted over [O_X, C_X), the two sides averaged, times the tick value, plus the F3.7 commission with F3.6's increase for MCL and MNG) over my own r_c; the choice by R7, R9, R10, R11; the epsilon by R12 with the tick values of the census.

| Exposure | Status | Vehicle | q_c | eps_X | Deciding comparison (cost per $ of risk, mine) | Frozen (status / vehicle / q / eps) | Verdict |
|---|---|---|---|---|---|---|---|
| Nasdaq-100 | chosen | MNQ | 1 | 170 | lowest cost per dollar of risk among ['MNQ']: MNQ 0.00566618 | chosen / MNQ / 1 / 170 | VERIFIED |
| Russell 2000 | chosen | M2K | 3 | 56 | lowest cost per dollar of risk among ['M2K']: M2K 0.01862724 | chosen / M2K / 3 / 56 | VERIFIED |
| Dow | chosen | MYM | 3 | 56 | lowest cost per dollar of risk among ['MYM']: MYM 0.01518325 | chosen / MYM / 3 / 56 | VERIFIED |
| 2-year | undersized | ZT | 1 | 10 | lowest cost per dollar of risk among ['ZT']: ZT 0.09021897 | undersized / ZT / 1 / 10 | VERIFIED |
| 5-year | undersized | ZF | 1 | 10 | lowest cost per dollar of risk among ['ZF']: ZF 0.07481033 | undersized / ZF / 1 / 10 | VERIFIED |
| 10-year | chosen | ZN | 1 | 5 | lowest cost per dollar of risk among ['ZN']: ZN 0.08904009 | chosen / ZN / 1 / 5 | VERIFIED |
| Ultra 10-year | chosen | TN | 1 | 5 | lowest cost per dollar of risk among ['TN']: TN 0.07056881 | chosen / TN / 1 / 5 | VERIFIED |
| Bond | chosen | ZB | 1 | 2 | lowest cost per dollar of risk among ['ZB']: ZB 0.08465928 | chosen / ZB / 1 / 2 | VERIFIED |
| Ultra bond | chosen | UB | 1 | 2 | lowest cost per dollar of risk among ['UB']: UB 0.06844882 | chosen / UB / 1 / 2 | VERIFIED |
| EUR | chosen | 6E | 1 | 13 | lowest cost per dollar of risk among ['6E']: 6E 0.03783446 | chosen / 6E / 1 / 13 | VERIFIED |
| AUD | chosen | 6A | 1 | 17 | lowest cost per dollar of risk among ['6A']: 6A 0.05967461 | chosen / 6A / 1 / 17 | VERIFIED |
| GBP | chosen | 6B | 1 | 13 | lowest cost per dollar of risk among ['6B', 'M6B']: 6B 0.06423688, M6B 0.11177039 | chosen / 6B / 1 / 13 | VERIFIED |
| CAD | undersized | 6C | 1 | 17 | lowest cost per dollar of risk among ['6C']: 6C 0.08428011 | undersized / 6C / 1 / 17 | VERIFIED |
| JPY | chosen | 6J | 1 | 13 | lowest cost per dollar of risk among ['6J']: 6J 0.05762520 | chosen / 6J / 1 / 13 | VERIFIED |
| CHF | chosen | 6S | 1 | 13 | lowest cost per dollar of risk among ['6S']: 6S 0.04027844 | chosen / 6S / 1 / 13 | VERIFIED |
| NZD | undersized | 6N | 1 | 17 | lowest cost per dollar of risk among ['6N']: 6N 0.07196189 | undersized / 6N / 1 / 17 | VERIFIED |
| WTI crude | chosen | MCL | 4 | 21 | lowest cost per dollar of risk among ['MCL', 'QM']: MCL 0.03458511, QM 0.04372145 | chosen / MCL / 4 / 21 | VERIFIED |
| Henry Hub gas | chosen | NG | 1 | 8 | lowest cost per dollar of risk among ['NG', 'MNG']: NG 0.02615376, MNG 0.08191186 | chosen / NG / 1 / 8 | VERIFIED |
| RBOB | no candidate: not traded in Stage E | None | None | None | - | no candidate: not traded in Stage E / None / None / None | VERIFIED |
| ULSD | no candidate: not traded in Stage E | None | None | None | - | no candidate: not traded in Stage E / None / None / None | VERIFIED |
| gold | chosen | MGC | 1 | 85 | lowest cost per dollar of risk among ['MGC']: MGC 0.01576225 | chosen / MGC / 1 / 85 | VERIFIED |
| silver | no candidate: not traded in Stage E | None | None | None | - | no candidate: not traded in Stage E / None / None / None | VERIFIED |
| copper | chosen | MHG | 2 | 34 | D9.11 sentence: MHG is a candidate | chosen / MHG / 2 / 34 | VERIFIED |
| corn | undersized | ZC | 1 | 6 | lowest cost per dollar of risk among ['ZC']: ZC 0.11264807 | undersized / ZC / 1 / 6 | VERIFIED |
| wheat | chosen | ZW | 1 | 6 | lowest cost per dollar of risk among ['ZW']: ZW 0.07878321 | chosen / ZW / 1 / 6 | VERIFIED |
| soybeans | chosen | ZS | 1 | 6 | lowest cost per dollar of risk among ['ZS']: ZS 0.06029396 | chosen / ZS / 1 / 6 | VERIFIED |
| soybean meal | chosen | ZM | 1 | 8 | lowest cost per dollar of risk among ['ZM']: ZM 0.07561320 | chosen / ZM / 1 / 8 | VERIFIED |
| soybean oil | chosen | ZL | 1 | 14 | lowest cost per dollar of risk among ['ZL']: ZL 0.04275670 | chosen / ZL / 1 / 14 | VERIFIED |
| lean hogs | chosen | HE | 1 | 8 | lowest cost per dollar of risk among ['HE']: HE 0.05758892 | chosen / HE / 1 / 8 | VERIFIED |
| live cattle | chosen | LE | 1 | 8 | lowest cost per dollar of risk among ['LE']: LE 0.03384317 | chosen / LE / 1 / 8 | VERIFIED |
| bitcoin | undersized | MBT | 1 | 170 | lowest cost per dollar of risk among ['MBT']: MBT 0.03667083 | undersized / MBT / 1 / 170 | VERIFIED |

Per-contract cost per dollar of risk (mine / frozen), every admissible contract:

| Contract | One-side slippage ticks (mine / frozen) | Round-turn cost USD per contract | Cost per $ of risk (mine / frozen) |
|---|---|---|---|
| MNQ | 0.839437 / 0.839437 | 2.059437 / 2.059437 | 0.00566618 / 0.00566618 |
| NQ | 1.177218 / 1.177218 | 15.552175 / 15.552175 | 0.00430441 / 0.00430441 |
| RTY | 0.801588 / 0.801588 | 11.795878 / 11.795878 | 0.01112067 / 0.01112067 |
| M2K | 0.756995 / 0.756995 | 1.976995 / 1.976995 | 0.01862724 / 0.01862724 |
| MYM | 0.771262 / 0.771262 | 1.991262 / 1.991262 | 0.01518325 / 0.01518325 |
| YM | 1.033686 / 1.033686 | 14.116856 / 14.116856 | 0.01075756 / 0.01075756 |
| ZT | 0.502138 / 0.502138 | 10.165900 / 10.165900 | 0.09021897 / 0.09021897 |
| ZF | 0.500487 / 0.500487 | 10.140102 / 10.140102 | 0.07481033 / 0.07481033 |
| ZN | 0.500058 / 0.500058 | 18.246797 / 18.246797 | 0.08904009 / 0.08904009 |
| TN | 0.503164 / 0.503164 | 18.343880 / 18.343880 | 0.07056881 / 0.07056881 |
| ZB | 0.500501 / 0.500501 | 34.041318 / 34.041318 | 0.08465928 / 0.08465928 |
| UB | 0.502426 / 0.502426 | 34.321639 / 34.321639 | 0.06844882 / 0.06844882 |
| 6E | 0.629309 / 0.629309 | 12.086367 / 12.086367 | 0.03783446 / 0.03783446 |
| M6E | 0.560818 / 0.560818 | 2.402045 / 2.402045 | 0.07498194 / 0.07498194 |
| E7 | 0.637061 / 0.637061 | 10.683257 / 10.683257 | 0.06646730 / 0.06646730 |
| 6A | 0.673935 / 0.673935 | 10.959353 / 10.959353 | 0.05967461 / 0.05967461 |
| M6A | 0.585391 / 0.585391 | 2.170781 / 2.170781 | 0.11787229 / 0.11787229 |
| 6B | 0.619376 / 0.619376 | 11.962201 / 11.962201 | 0.06423688 / 0.06423688 |
| M6B | 0.873313 / 0.873313 | 2.091642 / 2.091642 | 0.11177039 / 0.11177039 |
| 6C | 0.591806 / 0.591806 | 10.138063 / 10.138063 | 0.08428011 / 0.08428011 |
| 6J | 0.606627 / 0.606627 | 11.802841 / 11.802841 | 0.05762520 / 0.05762520 |
| 6S | 0.985952 / 0.985952 | 16.544402 / 16.544402 | 0.04027844 / 0.04027844 |
| 6N | 0.704093 / 0.704093 | 11.260931 / 11.260931 | 0.07196189 / 0.07196189 |
| CL | 0.663028 / 0.663028 | 17.280559 / 17.280559 | 0.01880797 / 0.01880797 |
| MCL | 0.723475 / 0.723475 | 3.166950 / 3.166950 | 0.03458511 / 0.03458511 |
| QM | 0.662811 / 0.662811 | 19.990278 / 19.990278 | 0.04372145 / 0.04372145 |
| NG | 0.625012 / 0.625012 | 16.720232 / 16.720232 | 0.02615376 / 0.02615376 |
| MNG | 1.714797 / 1.714797 | 5.349595 / 5.349595 | 0.08191186 / 0.08191186 |
| QG | 0.609908 / 0.609908 | 17.267688 / 17.267688 | 0.10849243 / 0.10849243 |
| RB | 2.278751 / 2.278751 | 23.161507 / 23.161507 | 0.02286896 / 0.02286896 |
| HO | 4.434897 / 4.434897 | 41.273138 / 41.273138 | 0.02863413 / 0.02863413 |
| MGC | 1.077978 / 1.077978 | 4.075956 / 4.075956 | 0.01576225 / 0.01576225 |
| GC | 1.952113 / 1.952113 | 43.362251 / 43.362251 | 0.01676182 / 0.01676182 |
| SIL | 1.116318 / 1.116318 | 13.883183 / 13.883183 | 0.01491129 / 0.01491129 |
| SI | 1.682105 / 1.682105 | 88.425242 / 88.425242 | 0.01899998 / 0.01899998 |
| HG | 1.117183 / 1.117183 | 32.249582 / 32.249582 | 0.02928338 / 0.02928338 |
| MHG | 1.075541 / 1.075541 | 4.608852 / 4.608852 | 0.04181673 / 0.04181673 |
| ZC | 0.501476 / 0.501476 | 17.816893 / 17.816893 | 0.11264807 / 0.11264807 |
| ZW | 0.528566 / 0.528566 | 18.494144 / 18.494144 | 0.07878321 / 0.07878321 |
| ZS | 0.522917 / 0.522917 | 18.352920 / 18.352920 | 0.06029396 / 0.06029396 |
| ZM | 0.539910 / 0.539910 | 16.078192 / 16.078192 | 0.07561320 / 0.07561320 |
| ZL | 0.646126 / 0.646126 | 13.033515 / 13.033515 | 0.04275670 / 0.04275670 |
| HE | 0.668954 / 0.668954 | 18.599087 / 18.599087 | 0.05758892 / 0.05758892 |
| LE | 0.935625 / 0.935625 | 23.932503 / 23.932503 | 0.03384317 / 0.03384317 |
| MBT | 1.602996 / 1.602996 | 4.422996 / 4.422996 | 0.03667083 / 0.03667083 |

Counts: VERIFIED 31, DISCREPANCY 0 (31 exposures). Result: 22 chosen, 6 undersized (ZT, ZF, 6C, 6N, ZC, MBT), 3 not traded (RBOB, ULSD, silver). The D9.11 SIL/MHG sentence binds nowhere (SIL is not a candidate at rho 2.58; MHG is copper's only candidate). R7 removes M6E (rho 0.888, preferred otherwise) and M6A (0.511); had U7 cleared them, the choice would have compared their cost per dollar of risk (0.07498 and 0.11787) with 6E's 0.03783 and 6A's 0.05967, so 6E and 6A would still win. The 22 + 6 translated epsilons equal the lead's hand-checked list in the STATE file (02:44 PDT).

#### 3a.3 D8 cost tables from the raw mbp-1 files: ZN (rates), CL (energy), ZC (grains), MBT (crypto)

Each of the 20 files' sha256 was checked against reports/stage_e1_purchase.json before decoding, and the record count against the manifest (all equal). Under CostCoder's readings R1 to R10 my tables reproduce the frozen ones bucket by bucket:

| Product | Buckets (mine / frozen) | Day-session buckets | Headline round turn, ticks: mean [min, max] (mine) | Frozen | Event-window side ticks buy / sell (mine = frozen) | max abs diff s_b | max abs diff round turn | max abs diff valid s | Dates-with-quotes, median, depth, fallback mismatches | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| ZN | 46 / 46 | 14 (07:00..13:30) | 1.167809 [1.167683, 1.168493] | 1.167809 [1.167683, 1.168493] | 0.501063 / 0.501063 | 1.1e-16 | 2.2e-16 | 0.0e+00 | 0, 0, 0, 0 | VERIFIED |
| CL | 46 / 46 | 11 (08:00..13:00) | 1.728056 [1.698817, 1.768250] | 1.728056 [1.698817, 1.768250] | 1.319154 / 1.319154 | 2.2e-16 | 4.4e-16 | 0.0e+00 | 0, 0, 0, 0 | VERIFIED |
| ZC | 36 / 36 | 10 (08:30..13:00) | 1.425413 [1.423366, 1.429576] | 1.425413 [1.423366, 1.429576] | 0.536617 / 0.536617 | 1.1e-16 | 4.4e-16 | 0.0e+00 | 0, 0, 0, 0 | VERIFIED |
| MBT | 46 / 46 | 13 (08:30..14:30) | 8.845991 [8.554172, 9.009713] | 8.845991 [8.554172, 9.009713] | 2.613201 / 2.613201 | 4.4e-16 | 1.8e-15 | 0.0e+00 | 0, 0, 0, 0 | VERIFIED |

Day-session buckets of the four products (s_b in ticks, mine / frozen; time-weighted lower median top size bid / ask; round turn in ticks, mine):

| Product | Bucket (CT) | Dates with quotes | s_b mine | s_b frozen | Median bid / ask | Depth buy / sell | Round turn ticks (mine) |
|---|---|---|---|---|---|---|---|
| ZN | 07:00-07:30 | 5 | 0.500209 | 0.500209 | 2125 / 1975 | 0.000 / 0.000 | 1.168097 |
| ZN | 07:30-08:00 | 5 | 0.500254 | 0.500254 | 2271 / 2065 | 0.000 / 0.000 | 1.168188 |
| ZN | 08:00-08:30 | 5 | 0.500006 | 0.500006 | 2585 / 2436 | 0.000 / 0.000 | 1.167692 |
| ZN | 08:30-09:00 | 5 | 0.500005 | 0.500005 | 2474 / 2818 | 0.000 / 0.000 | 1.167690 |
| ZN | 09:00-09:30 | 5 | 0.500005 | 0.500005 | 3023 / 2864 | 0.000 / 0.000 | 1.167690 |
| ZN | 09:30-10:00 | 5 | 0.500004 | 0.500004 | 3079 / 3133 | 0.000 / 0.000 | 1.167687 |
| ZN | 10:00-10:30 | 5 | 0.500003 | 0.500003 | 3168 / 3168 | 0.000 / 0.000 | 1.167686 |
| ZN | 10:30-11:00 | 5 | 0.500003 | 0.500003 | 3679 / 3792 | 0.000 / 0.000 | 1.167685 |
| ZN | 11:00-11:30 | 5 | 0.500004 | 0.500004 | 3621 / 3482 | 0.000 / 0.000 | 1.167688 |
| ZN | 11:30-12:00 | 5 | 0.500002 | 0.500002 | 3532 / 3459 | 0.000 / 0.000 | 1.167684 |
| ZN | 12:00-12:30 | 5 | 0.500407 | 0.500407 | 3309 / 3051 | 0.000 / 0.000 | 1.168493 |
| ZN | 12:30-13:00 | 5 | 0.500002 | 0.500002 | 3238 / 4267 | 0.000 / 0.000 | 1.167683 |
| ZN | 13:00-13:30 | 5 | 0.500002 | 0.500002 | 4177 / 3829 | 0.000 / 0.000 | 1.167684 |
| ZN | 13:30-14:00 | 5 | 0.500002 | 0.500002 | 5452 / 5307 | 0.000 / 0.000 | 1.167685 |
| CL | 08:00-08:30 | 5 | 0.657018 | 0.657018 | 8 / 8 | 0.000 / 0.000 | 1.716035 |
| CL | 08:30-09:00 | 5 | 0.656630 | 0.656630 | 7 / 8 | 0.000 / 0.000 | 1.715260 |
| CL | 09:00-09:30 | 5 | 0.683125 | 0.683125 | 7 / 7 | 0.000 / 0.000 | 1.768250 |
| CL | 09:30-10:00 | 5 | 0.672312 | 0.672312 | 7 / 7 | 0.000 / 0.000 | 1.746625 |
| CL | 10:00-10:30 | 5 | 0.661805 | 0.661805 | 7 / 7 | 0.000 / 0.000 | 1.725611 |
| CL | 10:30-11:00 | 5 | 0.654788 | 0.654788 | 7 / 7 | 0.000 / 0.000 | 1.711577 |
| CL | 11:00-11:30 | 5 | 0.659178 | 0.659178 | 7 / 7 | 0.000 / 0.000 | 1.720356 |
| CL | 11:30-12:00 | 5 | 0.653836 | 0.653836 | 7 / 7 | 0.000 / 0.000 | 1.709672 |
| CL | 12:00-12:30 | 5 | 0.648409 | 0.648409 | 8 / 7 | 0.000 / 0.000 | 1.698817 |
| CL | 12:30-13:00 | 5 | 0.663360 | 0.663360 | 8 / 9 | 0.000 / 0.000 | 1.728721 |
| CL | 13:00-13:30 | 5 | 0.682846 | 0.682846 | 8 / 8 | 0.000 / 0.000 | 1.767691 |
| ZC | 08:30-09:00 | 5 | 0.503588 | 0.503588 | 222 / 263 | 0.000 / 0.000 | 1.429576 |
| ZC | 09:00-09:30 | 5 | 0.501383 | 0.501383 | 345 / 313 | 0.000 / 0.000 | 1.425166 |
| ZC | 09:30-10:00 | 5 | 0.500483 | 0.500483 | 349 / 342 | 0.000 / 0.000 | 1.423366 |
| ZC | 10:00-10:30 | 5 | 0.500757 | 0.500757 | 279 / 312 | 0.000 / 0.000 | 1.423915 |
| ZC | 10:30-11:00 | 5 | 0.501589 | 0.501589 | 282 / 496 | 0.000 / 0.000 | 1.425578 |
| ZC | 11:00-11:30 | 5 | 0.501173 | 0.501173 | 675 / 401 | 0.000 / 0.000 | 1.424746 |
| ZC | 11:30-12:00 | 5 | 0.500617 | 0.500617 | 426 / 557 | 0.000 / 0.000 | 1.423634 |
| ZC | 12:00-12:30 | 5 | 0.500997 | 0.500997 | 582 / 379 | 0.000 / 0.000 | 1.424395 |
| ZC | 12:30-13:00 | 5 | 0.502384 | 0.502384 | 456 / 484 | 0.000 / 0.000 | 1.427167 |
| ZC | 13:00-13:20 | 5 | 0.502096 | 0.502096 | 511 / 819 | 0.000 / 0.000 | 1.426591 |
| MBT | 08:30-09:00 | 5 | 1.610598 | 1.610598 | 2 / 2 | 0.000 / 0.000 | 8.861195 |
| MBT | 09:00-09:30 | 5 | 1.684857 | 1.684857 | 2 / 2 | 0.000 / 0.000 | 9.009713 |
| MBT | 09:30-10:00 | 5 | 1.609759 | 1.609759 | 2 / 2 | 0.000 / 0.000 | 8.859518 |
| MBT | 10:00-10:30 | 5 | 1.683378 | 1.683378 | 2 / 2 | 0.000 / 0.000 | 9.006756 |
| MBT | 10:30-11:00 | 5 | 1.586929 | 1.586929 | 2 / 2 | 0.000 / 0.000 | 8.813859 |
| MBT | 11:00-11:30 | 5 | 1.649719 | 1.649719 | 2 / 2 | 0.000 / 0.000 | 8.939439 |
| MBT | 11:30-12:00 | 5 | 1.670625 | 1.670625 | 2 / 2 | 0.000 / 0.000 | 8.981251 |
| MBT | 12:00-12:30 | 5 | 1.629880 | 1.629880 | 2 / 2 | 0.000 / 0.000 | 8.899760 |
| MBT | 12:30-13:00 | 5 | 1.578619 | 1.578619 | 2 / 2 | 0.000 / 0.000 | 8.797239 |
| MBT | 13:00-13:30 | 5 | 1.568411 | 1.568411 | 2 / 2 | 0.000 / 0.000 | 8.776822 |
| MBT | 13:30-14:00 | 5 | 1.596659 | 1.596659 | 2 / 2 | 0.000 / 0.000 | 8.833317 |
| MBT | 14:00-14:30 | 5 | 1.512424 | 1.512424 | 2 / 2 | 0.000 / 0.000 | 8.664848 |
| MBT | 14:30-15:00 | 5 | 1.457086 | 1.457086 | 2 / 2 | 0.000 / 0.000 | 8.554172 |

Counts: VERIFIED 4, DISCREPANCY 0 (4 cost tables). With q_c = 1 for all four, every depth term is zero (median top sizes are at least 1), so the depth reading (R4, R5) is exercised by these four only trivially; 3a.4 E examines it on the frozen table for the five contracts where it is non-zero. One field of CostCoder's per-date statistics, records_in_closed_time, was not reproduced: my code drops closed-time records by interval overlap without counting them; it enters no table value.

#### 3a.4 Challenges to the readings: faithful to the frozen text, and what the alternative gives

Vehicle readings R1 to R12 (reports/stage_e2a_vehicle_rule_readings.md):

- R1 (O_X, C_X from D6; L-1 keeps D6's O where CME publishes none): faithful. D2 says the two prices are read at the exposure's D6 open and close; the calendar builders confirmed every C and no O is a settlement time. No alternative changes a number in the window (L-12's pre-2020-10-26 equity close touches no research-window date). VERIFIED.
- R2 (dates: roll blackout, vendor-degraded, and dates with a full closure or an early halt or close at or before C_X): faithful to D2's literal formula, whose close(C_X - 1 min) does not exist on an early-close day; D2 itself names only the first two exclusions. The alternative that the MES segment table behind R* used (funnel/exposure_segments.py: a day's in-window bars end at the flatten flag, which carries early closes, so an early-close day contributes a truncated move) would keep those dates with the move to the last bar before the halt. Effect (alts.py, A): every r_c falls by 0 to 3% and no contract changes q_c or band; the nearest to the 0.5 edge are 6A n 297, r_c 181.9865, q 1, rho 0.5046 (preferred), M6A n 297, r_c 18.2424, q 10, rho 0.5058 (preferred), 6B n 297, r_c 184.5118, q 1, rho 0.5116 (preferred), M6B n 297, r_c 18.5290, q 10, rho 0.5137 (preferred), and MCL n 265, r_c 90.1849, q 4, rho 1.0002 (preferred) (q_c 4 either way). VERIFIED WITH NOTES: the reading differs from the R* precedent but moves nothing; the epsilon declaration (item 5) ties the funnel's E|m_1| to R2's dates, so the two stay consistent.
- R3 (as-of bars: first bar at or after O_X, last bar before C_X, nearest traded minute on thin contracts): faithful to D2 read with the MES segment table's first-open/last-close convention; D2 does not say. Alternative B (exact bars only, else the date is dropped): E7 n 190, r_c 168.8487, q 1, rho 0.4681 (candidate, undersized), M6A n 187, r_c 20.4064, q 10, rho 0.5658 (preferred), M6B n 194, r_c 18.8434, q 10, rho 0.5224 (preferred), QG n 237, r_c 163.1329, q 1, rho 0.4523 (candidate, undersized), MNG n 260, r_c 65.6038, q 5, rho 0.9094 (preferred) (q_c 5 instead of 6; the only q change); no band changes and no vehicle changes (none of these is a vehicle; 6B still beats M6B and NG still beats MNG on cost). VERIFIED WITH NOTES.
- R4 (dollars via the census tick and tick value): faithful; the vendor price scale (cents for ZC, ZW, ZS, ZL, HE, LE) was found on the prices, as bars.md and the sizes file state. VERIFIED.
- R5 (cap_c = min(D9.5 lot cap, D9.11 50K cap)): faithful to the frozen design as a whole: D2 names D9.5 alone, but D9.11 (frozen) encodes 'every size stays within the 50K figure at all times' with SIL and MHG at most 2. Alternative (D9.5 alone): SIL cap 5, q_c still 1 (R*/r_c = 0.39), rho 2.58, not a candidate either way; MHG cap 10, q_c = round(3.27) = 3, rho 0.917, still the copper vehicle, but eps_X = floor(85 / (3 x 1.25)) = 22 instead of 34. So the R5 reading decides copper's size and epsilon; it is the reading the frozen D9.11 requires. The lead's Q-1 answer (SI and HG keep cap 1; D9.11's discretionary 0 is outside its Encoded list) changes nothing: both have rho > 3. VERIFIED.
- R6 (round half up): D2 says round(); half-up and half-to-even differ only at an exact .5, which no R*/r_c hits (nearest: MNG 5.523, MYM 2.750, M2K 3.398). VERIFIED.
- R7 (M6E, M6A not candidates, U7): faithful; effect shown in 3a.2. VERIFIED.
- R8 (cost per dollar of risk = (commission + 2 x one-side slippage) / r_c, q_c cancelled; one-side slippage = the minute-weighted mean over [O_X, C_X) of s_b plus the mean of the two sides' depth terms at q_c): D2's text is '(commission_c + 2 x one-side slippage_c) / (q_c r_c) at size q_c'. Read with 'at size q_c' scaling the numerator to the position (q_c contracts pay q_c commissions), the q_c cancels and R8 is faithful and economically coherent. The literal alternative D (a per-contract numerator over the position's risk q_c r_c) divides every micro's figure by its q_c and would change two vehicles: GBP to M6B (literal 0.01118 vs 6B 0.06424; q_c 10; eps_X 13, unchanged) and Henry Hub gas to MNG (literal 0.01365 vs NG 0.02615; q_c 6; eps_X 11 instead of 8); WTI stays MCL either way. This is the single reading in the vehicle file that decides a vehicle; it was fixed in writing before any bar was read (the readings file, 00:40 PDT) and I judge it the faithful one. A second alternative F (an unweighted mean over the day-session buckets instead of minute weights) changes no vehicle (GBP 6B 0.06431 vs M6B 0.11200; WTI and Henry Hub unchanged). VERIFIED WITH NOTES (the literal-numerator alternative and its effect are recorded for the lead's rulings).
- R9 (candidates rho <= 2.0 less R7; preferred >= 0.5; lowest R8 cost; ADV tie; the SIL/MHG sentence): faithful to D2 and D9.11; no tie occurred and the sentence never binds. VERIFIED.
- R10 (undersized: at the cap on the lowest-cost candidate): faithful to D2; every undersized exposure has one candidate at cap 1. VERIFIED. R11 (no candidate): faithful. VERIFIED. R12 (eps = floor(85 / (q_c x tick value))): D3 exactly. VERIFIED.

Lead rulings L-1 to L-11 as they touch these numbers:

- L-1: see R1. L-2 (rates' 41 CME early-settlement days are not early closes; Globex trades to 16:00 CT): faithful, since close(C_X - 1 min) exists on those days. Alternative C (exclude the EARLY_SETTLEMENT_CT dates in the window): ZN n 281, r_c 202.9026, q 1, rho 0.5626 (preferred), TN n 281, r_c 257.3955, q 1, rho 0.7136 (preferred), ZT n 281, r_c 111.2100, q 1, rho 0.3083 (candidate, undersized); no q_c or band changes. VERIFIED.
- L-3 (closure bars kept and flagged): affects no r_c (closure bars lie outside [O_X, C_X)). L-4 revised (2025-11-28 outage is not a calendar entry): 2025-11-28 is excluded for every product as vendor-degraded and, for most groups, as an early close, so the ruling moves nothing here. L-5 (FX 2025-11-27 thin trading, no calendar change): FX keeps its 16:00 CT close, so the date is used for the 11 FX contracts; treating it as an early close would drop 1 of 293 dates (well under 1% of r_c). L-6 (grains' scheduled late opens are closed windows): the late open is 08:30 CT = O_X, so the day session is intact. L-7 (metals 2026-02-25 unscheduled halt is not a calendar entry): the date is used with R3's as-of bars (GC and MGC show 1 missing C_X - 1 bar); excluding it would change r_c by about 1/290. L-8 (group-calendar roll blackout): verified above, with the flip-flop note. L-9 (MBT ends 2026-06-18) and L-10 (own CT calendar day): faithful to D4 and D6; MBT's 260 dates reproduced. L-11 (MBT expiry Fridays inside the blackout): no effect on r_c. All VERIFIED as applied; none has an alternative that changes a frozen number.

CostCoder's D8 readings R1 to R10 (reports/stage_e2a_costs.md):

- R1 (ts_recv event-time weighting): faithful to 'time-weighted mean'; D.1's 1-second sampling is an approximation of the same quantity. VERIFIED. R2 (pooled over the five dates' valid time): D8's 'the time-weighted mean, over the five dates' admits the per-date-mean alternative; CostCoder reports its largest effect as 0.0075 ticks (GC 04:30), far below any deciding gap in 3a.2 (the closest is WTI, MCL 0.03459 vs QM 0.04372 per dollar of risk, about 0.9 ticks of MCL slippage apart). VERIFIED WITH NOTES. R3 (quotes on a date = positive valid two-sided time; a standing book counts) and R6 (fallback per side from buckets with >= 3 dates): faithful; no bucket of any of the 45 contracts falls back, so neither reading has an effect. VERIFIED.
- R4 (lower time-weighted median) and R5 (buy hits the ask; depth (q_c - size) / q_c per side): faithful to D8's 'time-weighted median top-of-book size on the side a market order hits'. The upper median would reduce a depth term only where the median straddles q_c; the depth term is non-zero only for M2K, M6B, MCL, MNG and MYM, and no deciding comparison in 3a.2 is within reach of it (removing MCL's 0.25-tick depth term makes MCL cheaper still; MNG's and M6B's disadvantages are 3x and 1.7x). VERIFIED.
- R7 (event window per side = the largest final one-side slippage, s_b plus depth, over all buckets): D8's text is 'pays, per side, the largest s_b of the product's buckets instead of its own bucket's', i.e. the half-spread is replaced and the depth term is the fill's own bucket's. The two readings coincide wherever the depth term is zero (40 of 45 contracts, the four recomputed ones included) and differ for the five depth contracts: M2K 1.9531/1.9531 ticks (CostCoder) vs largest s_b 1.6198 plus the bucket's own depth (at most 0.333); M6B 1.4869/1.5869 ticks (CostCoder) vs largest s_b 0.9869 plus the bucket's own depth (at most 0.600); MCL 1.3132/1.3132 ticks (CostCoder) vs largest s_b 1.0632 plus the bucket's own depth (at most 0.250); MNG 3.2195/3.2195 ticks (CostCoder) vs largest s_b 2.5528 plus the bucket's own depth (at most 0.667); MYM 2.2079/2.5413 ticks (CostCoder) vs largest s_b 2.2079 plus the bucket's own depth (at most 0.333). CostCoder's reading is the more conservative (higher) cost. The event-window value enters no E.2a number (R8 uses the day-session buckets); it is used by E.2b's engine, where the lead should rule which reading applies. Where I read D8 differently: this is the one place. VERIFIED WITH NOTES.
- R8 (30-minute CT clock buckets of the group's segments; partial edge buckets on their own; 1-second grace): faithful to 'per 30-minute CT bucket of its trading hours'; the partial buckets (grains 07:30-07:45 and 13:00-13:20, livestock 13:00-13:05) are an implementation choice with a negligible effect on R8's minute-weighted mean (they carry their own minutes). R9 (headline = unweighted mean over buckets overlapping [O, C)): a reporting figure only. R10 (depth at Task 9's q_c): as D8 says. VERIFIED.
- Commissions: every frozen table's commission equals Topstep F3.7 with F3.6's 2026-10-01 increase applied to MCL ($1.72) and MNG ($1.92), as D8 requires (asserted for all 45 in choice.py). VERIFIED.

#### 3a.5 Verdict of part 3a

- Contracts (r_c, q_c, rho_c): VERIFIED 45, VERIFIED WITH NOTES 0, DISCREPANCY 0 of 45.
- Exposures (choice, cost per dollar of risk, translated epsilon): VERIFIED 31, DISCREPANCY 0 of 31.
- Cost tables from raw mbp-1: VERIFIED 4, DISCREPANCY 0 of 4 (ZN, CL, ZC, MBT).
- Readings challenged: vehicle R1 to R12: 9 VERIFIED, 3 VERIFIED WITH NOTES (R2, R3, R8), 0 DISCREPANCY; rulings L-1 to L-11: 11 VERIFIED as applied; CostCoder R1 to R10: 8 VERIFIED, 2 VERIFIED WITH NOTES (R2, R7), 0 DISCREPANCY.
- No DISCREPANCY. Every frozen vehicle, size and translated epsilon is reproduced exactly from the bars and the frozen cost table under the readings, and the four cost tables are reproduced from the raw books to floating-point precision. Two readings decide frozen numbers and deserve a written ruling in the return document: R8's cancelled q_c (GBP and Henry Hub gas would otherwise go to M6B and MNG) and R5's D9.11 cap (copper's q_c 2 and eps 34 rather than 3 and 22). One reading difference is deferred to E.2b: the event-window cost for the five depth contracts (CostCoder's R7 against D8's literal 'largest s_b').
- Not done in 3a: nothing. Part 3b (the funnel epsilon) awaits its brief.

### 3b: funnel epsilon

Written 2026-09-26 07:19 PDT (final). Auditor: DeclarationAuditor-FableXHigh, resumed for the Task 12 part 3b brief (19:16 PDT on 11 finished exposures) and again at 06:37 PDT on 2026-09-26, when B1 was complete for all 28. The auditor produced none of the numbers checked here.

#### 3b.0 Inputs, the lost brief, method, boundaries

- The brief file scratchpad/brief_task12b.md named in the lead's first message no longer existed when I resumed: the machine rebooted at about 17:08 PDT on 2026-09-25 and /tmp is a tmpfs, so that scratchpad (including my Part 3a scripts) was lost. This section follows the lead's two messages (exposures; the mixed early-stop/full-length rows; the 28 operative figures; B2 checked if finished, else pending) and the stage prompt's Task 12 wording.
- Frozen rules: reports/stage_e2a_epsilon_declaration.md (sha256 `ccdb8ec53f9015d4...`, the STATE file's ccdb8ec5...) and its addendum A-1 (`e6253be2274303f8...`, e6253be2...), both verified against the hashes the STATE file recorded before any cell used them; frozen D3, D2, NULL_CRITERIA.md 2.2; the frozen sizes and cost files of 3a; reports/funnel_null_baseline.json (MES's robust critical values); reports/stage_d1e_gate_extension.json (the 100 extension cells).
- Compared against reports/stage_e2a_epsilon.json and .md as of 2026-09-26 07:19 PDT (B1 done for all 28; B2 as stated in 3b.6), and reports/stage_e2a_funnel/<VEHICLE>/cells.jsonl, status.json and samples/ (read only; nothing written there).
- Own code (scratch fable_p3b/funnel_fable.py): my own segment tables from the parquets under the declaration's points 4 to 7 (D2's dates from the frozen sizes file; [O_X, C_X) on the trade date's own CT day, which for MBT's booked-forward dates is ruling L-10; not in the flatten window; first bar at or after O_X, last before C_X; T equal-count segments by np.array_split; the vendor tick, 100 x the E.0 tick for grains and livestock), my own minute cost book from the frozen cost table under point 8, my own analytic net $/day per cell, my own ascending-order replay of B1 and B2, my own early-stop rule from power_gate.verdict, and my own process pool calling the FROZEN Stage B simulator (funnel.simulator.run_one with BASE_SEED, funnel.quality_generator, funnel.null_generator.SegmentTable, funnel.power_gate.verdict). Nothing was imported from funnel/exposure_gate*.py or funnel/exposure_segments.py; the scaling of ticks to the vehicle's dollars and the size in 0.1-lot units follow the declaration's point 3 and were written independently (MYM at q_c = 3 and lot weight 0.1 exercises both).
- Compute: two worker processes, forkserver, nice 10, OMP_NUM_THREADS=1, beside the funnel driver's 12 threads; peak well under 1 GB. Research-window bars were used for the segment moves only.

#### 3b.1 Segment moves E|m_T| and per-T round-turn costs, 28 exposures

Tolerance: exact equality of the day counts and of the r_c identity (rational), 1e-9 on E|m_T| (ticks) and on the per-T cost (USD).

| Vehicle | Days used (mine / stored) | E|m_1| .. E|m_32| ticks (mine) | max |diff| E|m_T| | RT cost T=1..32 USD (mine) | max |diff| cost | E|m_1| x tv = r_c | Size units, money factor | Verdict |
|---|---|---|---|---|---|---|---|---|
| ZT | 286 / 286 | 14.423, 9.175, 6.213, 4.322, 2.993, 2.163 | 0.0e+00 | 10.160, 10.170, 10.185, 10.175, 10.176, 10.177 | 0.0e+00 | True | 10, 0.6250 | VERIFIED |
| ZF | 286 / 286 | 17.350, 11.108, 7.739, 5.392, 3.752, 2.662 | 0.0e+00 | 10.150, 10.145, 10.152, 10.151, 10.148, 10.149 | 0.0e+00 | True | 10, 0.6250 | VERIFIED |
| ZN | 286 / 286 | 13.115, 8.481, 5.952, 4.121, 2.878, 2.058 | 0.0e+00 | 18.260, 18.260, 18.260, 18.260, 18.260, 18.260 | 0.0e+00 | True | 10, 1.2500 | VERIFIED |
| TN | 286 / 286 | 16.636, 10.883, 7.510, 5.206, 3.611, 2.574 | 0.0e+00 | 18.350, 18.345, 18.350, 18.352, 18.349, 18.352 | 0.0e+00 | True | 10, 1.2500 | VERIFIED |
| ZB | 286 / 286 | 12.867, 8.552, 5.944, 4.078, 2.879, 2.051 | 0.0e+00 | 34.080, 34.070, 34.068, 34.052, 34.053, 34.049 | 0.0e+00 | True | 10, 2.5000 | VERIFIED |
| UB | 286 / 286 | 16.045, 10.757, 7.476, 5.208, 3.665, 2.576 | 0.0e+00 | 34.330, 34.364, 34.348, 34.332, 34.322, 34.332 | 0.0e+00 | True | 10, 2.5000 | VERIFIED |
| MCL | 258 / 258 | 91.570, 61.752, 45.031, 33.777, 23.034, 16.220 | 0.0e+00 | 3.152, 3.151, 3.176, 3.169, 3.168, 3.169 | 0.0e+00 | True | 4, 0.8000 | VERIFIED |
| NG | 259 / 259 | 63.931, 43.550, 30.340, 20.764, 14.643, 10.541 | 0.0e+00 | 16.520, 16.669, 16.655, 16.675, 16.685, 16.724 | 0.0e+00 | True | 10, 0.8000 | VERIFIED |
| MGC | 290 / 290 | 258.590, 176.381, 122.438, 87.789, 62.025, 44.575 | 0.0e+00 | 4.170, 4.075, 4.058, 4.089, 4.069, 4.080 | 0.0e+00 | True | 1, 0.8000 | VERIFIED |
| MHG | 290 / 290 | 88.172, 59.148, 41.409, 29.592, 20.691, 14.662 | 0.0e+00 | 4.775, 4.762, 4.639, 4.607, 4.617, 4.614 | 0.0e+00 | True | 2, 1.0000 | VERIFIED |
| 6E | 293 / 293 | 51.113, 34.800, 24.160, 17.215, 11.981, 8.460 | 0.0e+00 | 12.190, 12.154, 12.150, 12.145, 12.097, 12.106 | 0.0e+00 | True | 10, 0.5000 | VERIFIED |
| 6A | 293 / 293 | 36.730, 25.541, 18.510, 12.961, 8.923, 6.315 | 0.0e+00 | 10.989, 11.031, 11.015, 10.987, 10.990, 10.972 | 0.0e+00 | True | 10, 0.4000 | VERIFIED |
| 6B | 293 / 293 | 29.795, 19.942, 13.962, 9.962, 7.038, 4.990 | 0.0e+00 | 11.960, 11.930, 11.956, 11.974, 11.974, 11.978 | 0.0e+00 | True | 10, 0.5000 | VERIFIED |
| 6C | 293 / 293 | 24.058, 16.631, 12.067, 8.297, 5.708, 4.186 | 0.0e+00 | 10.000, 10.129, 10.086, 10.134, 10.140, 10.149 | 0.0e+00 | True | 10, 0.4000 | VERIFIED |
| 6J | 293 / 293 | 32.771, 21.645, 14.543, 10.267, 7.116, 5.038 | 0.0e+00 | 11.920, 11.897, 11.833, 11.808, 11.815, 11.815 | 0.0e+00 | True | 10, 0.5000 | VERIFIED |
| 6S | 293 / 293 | 65.720, 43.502, 29.394, 21.192, 14.887, 10.489 | 0.0e+00 | 16.419, 16.340, 16.668, 16.579, 16.569, 16.549 | 0.0e+00 | True | 10, 0.5000 | VERIFIED |
| 6N | 293 / 293 | 31.297, 21.853, 15.416, 11.387, 7.747, 5.396 | 0.0e+00 | 11.189, 11.245, 11.325, 11.295, 11.279, 11.270 | 0.0e+00 | True | 10, 0.4000 | VERIFIED |
| ZC | 271 / 271 | 12.653, 8.651, 5.748, 4.073, 2.879, 2.023 | 0.0e+00 | 17.860, 17.840, 17.825, 17.820, 17.823, 17.823 | 0.0e+00 | True | 10, 1.0000 | VERIFIED |
| ZW | 277 / 277 | 18.780, 13.455, 8.847, 6.275, 4.394, 3.097 | 0.0e+00 | 18.590, 18.485, 18.532, 18.505, 18.504, 18.502 | 0.0e+00 | True | 10, 1.0000 | VERIFIED |
| ZS | 279 / 279 | 24.351, 16.771, 11.393, 7.932, 5.620, 3.974 | 0.0e+00 | 18.470, 18.365, 18.328, 18.342, 18.351, 18.358 | 0.0e+00 | True | 10, 1.0000 | VERIFIED |
| ZM | 273 / 273 | 21.264, 15.059, 10.317, 7.103, 4.979, 3.550 | 0.0e+00 | 16.230, 16.165, 16.128, 16.098, 16.093, 16.082 | 0.0e+00 | True | 10, 0.8000 | VERIFIED |
| ZL | 282 / 282 | 50.805, 33.633, 23.110, 16.615, 11.573, 8.145 | 0.0e+00 | 13.190, 13.145, 13.077, 13.008, 13.023, 13.029 | 0.0e+00 | True | 10, 0.4800 | VERIFIED |
| HE | 270 / 270 | 32.296, 22.481, 15.642, 10.797, 7.631, 5.261 | 0.0e+00 | 18.380, 18.560, 18.475, 18.580, 18.588, 18.593 | 0.0e+00 | True | 10, 0.8000 | VERIFIED |
| LE | 264 / 264 | 70.716, 46.527, 31.875, 21.826, 15.275, 10.710 | 0.0e+00 | 23.290, 24.115, 23.913, 23.871, 23.848, 23.917 | 0.0e+00 | True | 10, 0.8000 | VERIFIED |
| MBT | 260 / 260 | 241.227, 167.675, 111.995, 79.513, 55.376, 39.458 | 0.0e+00 | 4.630, 4.565, 4.513, 4.466, 4.444, 4.439 | 0.0e+00 | True | 10, 0.0400 | VERIFIED |
| MNQ | 285 / 285 | 726.923, 490.282, 338.570, 227.446, 157.664, 111.825 | 0.0e+00 | 2.150, 2.095, 2.072, 2.069, 2.068, 2.066 | 0.0e+00 | True | 1, 0.4000 | VERIFIED |
| M2K | 286 / 286 | 212.269, 145.897, 96.850, 66.574, 47.191, 33.195 | 0.0e+00 | 2.110, 2.045, 2.009, 1.994, 1.988, 1.983 | 0.0e+00 | True | 3, 0.4000 | VERIFIED |
| MYM | 286 / 286 | 262.297, 177.323, 119.908, 83.284, 58.601, 41.768 | 0.0e+00 | 2.153, 2.067, 2.033, 2.013, 2.003, 1.998 | 0.0e+00 | True | 3, 0.4000 | VERIFIED |

Counts: VERIFIED 28, DISCREPANCY 0 of 28. No day was skipped for lack of bars at any T (the declaration's 5% flag binds nowhere).

#### 3b.2 Cells, the bar, the ascending order, the first pass (B1), the epsilon arithmetic

The cell set is the 120 grid cells plus D.1e's 100 extension cells (220 keys, reproduced). For each exposure my analytic net $/day at q_c per cell equals the stored row's; the cells below the bar (eps_translated x q_c x tick value) match; replaying B1 in ascending order over the stored verdicts (ties evaluated together) gives exactly the stored evaluated set and the stored first pass; eps_funnel = floor(net $/day / (q_c x tick value)) and the operative epsilon = min(translated, funnel) are reproduced. Row consistency: every early-stopped row records more than 1531 failures (k_min 6469 of 8,000, recomputed from power_gate.verdict) and the verdict 'fail'; every full-length row's verdict and lower bound equal power_gate.verdict(power, 8000); every row's robust critical value equals the baseline's p80 value for its path.

| Vehicle | Bar $/day | Cells below bar (mine / stored) | B1 evaluated (replay / stored) | First pass below the bar (mine = stored) | Net $/day of the pass | eps translated | eps funnel from B1 (mine / stored) | eps operative (mine / stored) | Rows early-stopped / full | Pass full-length | Rows inconsistent | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ZT | 78.12 | 220 / 220 | 212 / 212 | consistency|T2|p0.55|R2.0 (=) | 45.55 | 10 | 5 / 5 | 5 / 5 | 0 / 212 | True | 0 | VERIFIED |
| ZF | 78.12 | 218 / 218 | 206 / 206 | consistency|T2|p0.6|R1.5 (=) | 50.57 | 10 | 6 / 6 | 6 / 6 | 0 / 206 | True | 0 | VERIFIED |
| ZN | 78.12 | 208 / 208 | 194 / 194 | consistency|T1|p0.58|R1.5 (=) | 57.04 | 5 | 3 / 3 | 3 / 3 | 140 / 54 | True | 0 | VERIFIED |
| TN | 78.12 | 194 / 194 | 168 / 168 | consistency|T2|p0.65|R1.0 (=) | 65.34 | 5 | 4 / 4 | 4 / 4 | 114 / 54 | True | 0 | VERIFIED |
| ZB | 62.50 | 144 / 144 | 144 / 144 | none below the bar (=) | - | 2 | - (B2) | 2 / 2 | 159 / 1 | None | 0 | VERIFIED |
| UB | 62.50 | 126 / 126 | 126 / 126 | none below the bar (=) | - | 2 | - (B2) | 2 / 2 | 143 / 1 | None | 0 | VERIFIED |
| MCL | 84.00 | 118 / 118 | 118 / 118 | none below the bar (=) | - | 21 | - (B2) | 21 / 21 | 137 / 1 | None | 0 | VERIFIED |
| NG | 80.00 | 81 / 81 | 81 / 81 | none below the bar (=) | - | 8 | - (B2) | 8 / 8 | 94 / 1 | None | 0 | VERIFIED |
| MGC | 85.00 | 140 / 140 | 102 / 102 | consistency|T4|p0.66|R0.75 (=) | 71.43 | 85 | 71 / 71 | 71 / 71 | 75 / 27 | True | 0 | VERIFIED |
| MHG | 85.00 | 198 / 198 | 176 / 176 | consistency|T2|p0.65|R1.0 (=) | 69.67 | 34 | 27 / 27 | 27 / 27 | 149 / 27 | True | 0 | VERIFIED |
| 6E | 81.25 | 138 / 138 | 136 / 136 | consistency|T2|p0.62|R1.0 (=) | 80.09 | 13 | 12 / 12 | 12 / 12 | 135 / 1 | True | 0 | VERIFIED |
| 6A | 85.00 | 206 / 206 | 182 / 182 | consistency|T2|p0.55|R1.5 (=) | 56.14 | 17 | 11 / 11 | 11 / 11 | 181 / 1 | True | 0 | VERIFIED |
| 6B | 81.25 | 208 / 208 | 176 / 176 | consistency|T2|p0.55|R1.5 (=) | 52.46 | 13 | 8 / 8 | 8 / 8 | 175 / 1 | True | 0 | VERIFIED |
| 6C | 85.00 | 218 / 218 | 206 / 206 | consistency|T1|p0.55|R2.0 (=) | 45.29 | 17 | 9 / 9 | 9 / 9 | 205 / 1 | True | 0 | VERIFIED |
| 6J | 81.25 | 204 / 204 | 186 / 186 | consistency|T1|p0.54|R1.75 (=) | 63.17 | 13 | 10 / 10 | 10 / 10 | 185 / 1 | True | 0 | VERIFIED |
| 6S | 81.25 | 126 / 126 | 126 / 126 | none below the bar (=) | - | 13 | - (B2) | 13 / 13 | 135 / 1 | None | 0 | VERIFIED |
| 6N | 85.00 | 214 / 214 | 198 / 198 | consistency|T1|p0.7|R1.0 (=) | 51.41 | 17 | 10 / 10 | 10 / 10 | 197 / 1 | True | 0 | VERIFIED |
| ZC | 75.00 | 216 / 216 | 208 / 208 | consistency|T2|p0.6|R1.5 (=) | 52.62 | 6 | 4 / 4 | 4 / 4 | 207 / 1 | True | 0 | VERIFIED |
| ZW | 75.00 | 196 / 196 | 174 / 174 | consistency|T4|p0.55|R1.5 (=) | 61.31 | 6 | 4 / 4 | 4 / 4 | 173 / 1 | True | 0 | VERIFIED |
| ZS | 75.00 | 158 / 158 | 154 / 154 | consistency|T1|p0.65|R1.0 (=) | 72.85 | 6 | 5 / 5 | 5 / 5 | 153 / 1 | True | 0 | VERIFIED |
| ZM | 80.00 | 202 / 202 | 174 / 174 | consistency|T1|p0.57|R1.5 (=) | 57.56 | 8 | 5 / 5 | 5 / 5 | 173 / 1 | True | 0 | VERIFIED |
| ZL | 84.00 | 156 / 156 | 136 / 136 | consistency|T4|p0.68|R0.75 (=) | 69.38 | 14 | 11 / 11 | 11 / 11 | 135 / 1 | True | 0 | VERIFIED |
| HE | 80.00 | 152 / 152 | 142 / 142 | consistency|T2|p0.62|R1.0 (=) | 70.79 | 8 | 7 / 7 | 7 / 7 | 141 / 1 | True | 0 | VERIFIED |
| LE | 80.00 | 90 / 90 | 90 / 90 | none below the bar (=) | - | 8 | - (B2) | 8 / 8 | 103 / 1 | None | 0 | VERIFIED |
| MBT | 85.00 | 216 / 216 | 196 / 196 | consistency|T2|p0.52|R1.75 (=) | 45.37 | 170 | 90 / 90 | 90 / 90 | 195 / 1 | True | 0 | VERIFIED |
| MNQ | 85.00 | 78 / 78 | 78 / 78 | none below the bar (=) | - | 170 | - (B2) | 170 / 170 | 83 / 1 | None | 0 | VERIFIED |
| M2K | 84.00 | 115 / 115 | 103 / 103 | consistency|T2|p0.6|R1.0 (=) | 75.27 | 56 | 50 / 50 | 50 / 50 | 102 / 1 | True | 0 | VERIFIED |
| MYM | 84.00 | 85 / 85 | 85 / 85 | none below the bar (=) | - | 56 | - (B2) | 56 / 56 | 86 / 1 | None | 0 | VERIFIED |

Counts: VERIFIED 28, DISCREPANCY 0 of 28.

#### 3b.3 Re-simulation through the frozen simulator (own generator, cost book and pool)

Cells: ZT and MBT (undersized) and MGC and ZS (metals, grains): the binding cell in full and the three cells before it in ascending order; ZB (no pass below the bar): the six cells nearest the bar; MYM (no pass below the bar, q_c = 3): the three nearest the bar. Full-length cells are compared on power, verdict, lower bound, mean and quantiles, and on the stored sorted sample file bit for bit; early-stopped cells on the stop point (runs and failures, deterministic given BASE_SEED and the run index) and the verdict.

| Vehicle | Cell | Runs (mine) | Stopped | Failures in prefix | Power (mine / stored) | Verdict (mine / stored) | Mean $/month (mine / stored) | Samples equal (max abs diff) | Stored stop (runs, failures) | Seconds | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ZT | standard|T4|p0.6|R1.5 | 8000 | - | - | 0.420750 / 0.420750 | fail / fail | 455.26 / 455.26 | True (0.0) | - | 280.8 | VERIFIED |
| ZT | consistency|T1|p0.55|R2.0 | 8000 | - | - | 0.726750 / 0.726750 | fail / fail | 555.59 / 555.59 | True (0.0) | - | 157.8 | VERIFIED |
| ZT | standard|T1|p0.55|R2.0 | 8000 | - | - | 0.492625 / 0.492625 | fail / fail | 550.65 / 550.65 | True (0.0) | - | 115.6 | VERIFIED |
| ZT | consistency|T2|p0.55|R2.0 | 8000 | - | - | 0.817000 / 0.817000 | pass / pass | 713.55 / 713.55 | True (0.0) | - | 213.9 | VERIFIED |
| MGC | consistency|T1|p0.47|R2.0 | 8000 | - | - | 0.803875 / 0.803875 | marginal / marginal | 1356.75 / 1356.75 | True (0.0) | - | 178.2 | VERIFIED |
| MGC | standard|T1|p0.47|R2.0 | 8000 | - | - | 0.579875 / 0.579875 | fail / fail | 1013.43 / 1013.43 | True (0.0) | - | 120.2 | VERIFIED |
| MGC | standard|T32|p0.4|R2.0 | 3450 | True | 1536 | - | fail (pass impossible) / fail | - | - | (3450, 1536) | 675.7 | VERIFIED |
| MGC | consistency|T4|p0.66|R0.75 | 8000 | - | - | 0.845000 / 0.845000 | pass / pass | 1444.06 / 1444.06 | True (0.0) | - | 337.1 | VERIFIED |
| ZB | consistency|T4|p0.45|R2.0 | 2750 | True | 1552 | - | fail (pass impossible) / fail | - | - | (2750, 1552) | 91.1 | VERIFIED |
| ZB | standard|T4|p0.45|R2.0 | 2200 | True | 1539 | - | fail (pass impossible) / fail | - | - | (2200, 1539) | 61.7 | VERIFIED |
| ZB | consistency|T1|p0.5|R1.5 | 2900 | True | 1536 | - | fail (pass impossible) / fail | - | - | (2900, 1536) | 49.5 | VERIFIED |
| ZB | standard|T1|p0.5|R1.5 | 2250 | True | 1561 | - | fail (pass impossible) / fail | - | - | (2250, 1561) | 25.0 | VERIFIED |
| ZB | consistency|T2|p0.62|R1.0 | 4600 | True | 1543 | - | fail (pass impossible) / fail | - | - | (4600, 1543) | 103.7 | VERIFIED |
| ZB | standard|T2|p0.62|R1.0 | 2700 | True | 1550 | - | fail (pass impossible) / fail | - | - | (2700, 1550) | 51.9 | VERIFIED |
| MBT | standard|T1|p0.7|R1.0 | 3850 | True | 1543 | - | fail (pass impossible) / fail | - | - | (3850, 1543) | 58.7 | VERIFIED |
| MBT | consistency|T1|p0.6|R1.5 | 7900 | True | 1542 | - | fail (pass impossible) / fail | - | - | (7900, 1542) | 128.4 | VERIFIED |
| MBT | standard|T1|p0.6|R1.5 | 3650 | True | 1542 | - | fail (pass impossible) / fail | - | - | (3650, 1542) | 53.1 | VERIFIED |
| MBT | consistency|T2|p0.52|R1.75 | 8000 | - | - | 0.815250 / 0.815250 | pass / pass | 730.98 / 730.98 | True (0.0) | - | 210.7 | VERIFIED |
| ZS | standard|T4|p0.45|R2.0 | 3300 | True | 1558 | - | fail (pass impossible) / fail | - | - | (3300, 1558) | 90.7 | VERIFIED |
| ZS | consistency|T1|p0.47|R2.0 | 6550 | True | 1538 | - | fail (pass impossible) / fail | - | - | (6550, 1538) | 105.7 | VERIFIED |
| ZS | standard|T1|p0.47|R2.0 | 3250 | True | 1533 | - | fail (pass impossible) / fail | - | - | (3250, 1533) | 41.0 | VERIFIED |
| ZS | consistency|T1|p0.65|R1.0 | 8000 | - | - | 0.847875 / 0.847875 | pass / pass | 1554.37 / 1554.37 | True (0.0) | - | 148.7 | VERIFIED |
| MYM | standard|T1|p0.5|R1.5 | 2850 | True | 1550 | - | fail (pass impossible) / fail | - | - | (2850, 1550) | 31.7 | VERIFIED |
| MYM | consistency|T4|p0.4|R2.0 | 4900 | True | 1532 | - | fail (pass impossible) / fail | - | - | (4900, 1532) | 157.2 | VERIFIED |
| MYM | standard|T4|p0.4|R2.0 | 3100 | True | 1543 | - | fail (pass impossible) / fail | - | - | (3100, 1543) | 74.5 | VERIFIED |
| LE (B2) | standard|T4|p0.48|R1.5 | 4300 | True | 1537 | - | fail (pass impossible) / fail | - | - | (4300, 1537) | 41.7 | VERIFIED |
| LE (B2) | consistency|T1|p0.6|R1.0 | 8000 | - | - | 0.810500 / 0.810500 | pass / pass | 1739.33 / 1739.33 | True (0.0) | - | 44.9 | VERIFIED |
| MNQ (B2) | standard|T1|p0.45|R2.0 | 3750 | True | 1555 | - | fail (pass impossible) / fail | - | - | (3750, 1555) | 16.6 | VERIFIED |
| MNQ (B2) | consistency|T16|p0.55|R1.0 | 8000 | - | - | 0.872875 / 0.872875 | pass / pass | 2005.85 / 2005.85 | True (0.0) | - | 336.4 | VERIFIED |
| MYM (B2) | consistency|T4|p0.58|R1.0 | 8000 | - | - | 0.846125 / 0.846125 | pass / pass | 1738.15 / 1738.15 | True (0.0) | - | 99.9 | VERIFIED |

Counts: VERIFIED 30, DISCREPANCY 0 of 30 cells (the '(B2)' rows, LE, MNQ and MYM's first pass above the bar and the cell before it, were added after B2 finished).

#### 3b.4 The restart history and the mixed early-stopped / full-length rows

- The driver ran under several starts (per-exposure status.json 'runs'): 02:53 PDT full length; 06:37 with A-1 early stop; 17:10 without `--early-stop` (the lead's logged error, cells at full length); 17:43 with it; 18:05 after the JSONDecodeError fix. Finished cells were kept per cell across the stops, so several exposures mix the two kinds (column 'Rows early-stopped / full' above); ZT and ZF are all full-length; the no-pass exposures are all early-stopped.
- Why the mix changes no verdict: an early-stopped row is a proof that a robust pass is impossible (more than 1531 of its first n careers failed, and careers are seeded by (BASE_SEED, index) alone, so the prefix is the same in either mode); a full-length row is the exact verdict; both are 'not pass' or 'pass' by the same rule (k_min recomputed above). Every stored row of the 28 exposures satisfies its kind's check ('Rows inconsistent' 0), every binding pass is a full-length row with lower bound >= 0.80, and my ascending replay over the mixed rows reproduces every first pass and every epsilon. Step C confirms the two modes on the same cells: the re-simulated stop points and full-length samples equal the stored ones bit for bit (3b.3).
- The 18:05 lead edit: funnel/exposure_gate_run.py wraps the drive_memory.json read in contextlib.suppress(json.JSONDecodeError) and funnel/exposure_gate_mes.py writes that file atomically (both present); the files are untracked, so I cannot diff against a prior copy. Independent evidence that the computation did not change: rows written after 18:05 (the 17 later exposures, MHG, 6E) reproduce under my own driver exactly as rows written before it (ZT, ZB).

#### 3b.5 The 28 operative epsilons

| Vehicle | Exposure | Status | eps translated | eps funnel (stored) | eps operative | Basis (mine) | Verdict |
|---|---|---|---|---|---|---|---|
| ZT | 2-year | undersized | 10 | 5 | 5 | B1 pass consistency|T2|p0.55|R2.0 at $45.55/day | VERIFIED |
| ZF | 5-year | undersized | 10 | 6 | 6 | B1 pass consistency|T2|p0.6|R1.5 at $50.57/day | VERIFIED |
| ZN | 10-year | chosen | 5 | 3 | 3 | B1 pass consistency|T1|p0.58|R1.5 at $57.04/day | VERIFIED |
| TN | Ultra 10-year | chosen | 5 | 4 | 4 | B1 pass consistency|T2|p0.65|R1.0 at $65.34/day | VERIFIED |
| ZB | Bond | chosen | 2 | 2 | 2 | no pass below the bar: operative = translated, exact; the funnel figure is B2's | VERIFIED |
| UB | Ultra bond | chosen | 2 | 2 | 2 | no pass below the bar: operative = translated, exact; the funnel figure is B2's | VERIFIED |
| MCL | WTI crude | chosen | 21 | 24 | 21 | no pass below the bar: operative = translated, exact; the funnel figure is B2's | VERIFIED |
| NG | Henry Hub gas | chosen | 8 | 11 | 8 | no pass below the bar: operative = translated, exact; the funnel figure is B2's | VERIFIED |
| MGC | gold | chosen | 85 | 71 | 71 | B1 pass consistency|T4|p0.66|R0.75 at $71.43/day | VERIFIED |
| MHG | copper | chosen | 34 | 27 | 27 | B1 pass consistency|T2|p0.65|R1.0 at $69.67/day | VERIFIED |
| 6E | EUR | chosen | 13 | 12 | 12 | B1 pass consistency|T2|p0.62|R1.0 at $80.09/day | VERIFIED |
| 6A | AUD | chosen | 17 | 11 | 11 | B1 pass consistency|T2|p0.55|R1.5 at $56.14/day | VERIFIED |
| 6B | GBP | chosen | 13 | 8 | 8 | B1 pass consistency|T2|p0.55|R1.5 at $52.46/day | VERIFIED |
| 6C | CAD | undersized | 17 | 9 | 9 | B1 pass consistency|T1|p0.55|R2.0 at $45.29/day | VERIFIED |
| 6J | JPY | chosen | 13 | 10 | 10 | B1 pass consistency|T1|p0.54|R1.75 at $63.17/day | VERIFIED |
| 6S | CHF | chosen | 13 | 15 | 13 | no pass below the bar: operative = translated, exact; the funnel figure is B2's | VERIFIED |
| 6N | NZD | undersized | 17 | 10 | 10 | B1 pass consistency|T1|p0.7|R1.0 at $51.41/day | VERIFIED |
| ZC | corn | undersized | 6 | 4 | 4 | B1 pass consistency|T2|p0.6|R1.5 at $52.62/day | VERIFIED |
| ZW | wheat | chosen | 6 | 4 | 4 | B1 pass consistency|T4|p0.55|R1.5 at $61.31/day | VERIFIED |
| ZS | soybeans | chosen | 6 | 5 | 5 | B1 pass consistency|T1|p0.65|R1.0 at $72.85/day | VERIFIED |
| ZM | soybean meal | chosen | 8 | 5 | 5 | B1 pass consistency|T1|p0.57|R1.5 at $57.56/day | VERIFIED |
| ZL | soybean oil | chosen | 14 | 11 | 11 | B1 pass consistency|T4|p0.68|R0.75 at $69.38/day | VERIFIED |
| HE | lean hogs | chosen | 8 | 7 | 7 | B1 pass consistency|T2|p0.62|R1.0 at $70.79/day | VERIFIED |
| LE | live cattle | chosen | 8 | 11 | 8 | no pass below the bar: operative = translated, exact; the funnel figure is B2's | VERIFIED |
| MBT | bitcoin | undersized | 170 | 90 | 90 | B1 pass consistency|T2|p0.52|R1.75 at $45.37/day | VERIFIED |
| MNQ | Nasdaq-100 | chosen | 170 | 186 | 170 | no pass below the bar: operative = translated, exact; the funnel figure is B2's | VERIFIED |
| M2K | Russell 2000 | chosen | 56 | 50 | 50 | B1 pass consistency|T2|p0.6|R1.0 at $75.27/day | VERIFIED |
| MYM | Dow | chosen | 56 | 60 | 56 | no pass below the bar: operative = translated, exact; the funnel figure is B2's | VERIFIED |

Counts: VERIFIED 28, DISCREPANCY 0 of 28 operative figures. The translated figures equal 3a's; every operative figure is min(translated, funnel) under the declaration, and for the eight no-pass exposures it is the translated bar exactly (no cell above the bar can lower a floor below it).

#### 3b.6 B2: the reported funnel figure for the eight exposures with no pass below the bar

| Vehicle | B2 state (stored) | Cells at/above the bar evaluated (stored) | First pass above the bar (my replay of stored rows) | eps funnel (mine / stored) | Consistent | Verdict |
|---|---|---|---|---|---|---|
| ZB | done | 16 | consistency|T1|p0.65|R1.0 | 2 / 2 | True and True | VERIFIED |
| UB | done | 18 | consistency|T2|p0.62|R1.0 | 2 / 2 | True and True | VERIFIED |
| MCL | done | 20 | consistency|T1|p0.65|R1.0 | 24 / 24 | True and True | VERIFIED |
| NG | done | 14 | consistency|T8|p0.575|R1.0 | 11 / 11 | True and True | VERIFIED |
| 6S | done | 10 | consistency|T4|p0.68|R0.75 | 15 / 15 | True and True | VERIFIED |
| LE | done | 14 | consistency|T1|p0.6|R1.0 | 11 / 11 | True and True | VERIFIED |
| MNQ | done | 6 | consistency|T16|p0.55|R1.0 | 186 / 186 | True and True | VERIFIED |
| MYM | done | 2 | consistency|T4|p0.58|R1.0 | 60 / 60 | True and True | VERIFIED |

Counts: VERIFIED 8, PENDING 0, DISCREPANCY 0 of 8 (B2 finished 07:19 PDT 2026-09-26; LE, MNQ and MYM checked after). B2 cannot change an operative figure.

#### 3b.7 The declaration's readings, and what an alternative would give

- 1 (MES's frozen robust critical value for every exposure): faithful to D3's 're-run the Stage B power gate', which reads that baseline; D2's sizing puts every exposure at MES's risk, so the dollar bar is comparable. A per-exposure null would change the critical value and hence which cells pass; the leniency, if any, is capped by the translated bar (operative = min). NOTE for the user, as the declaration says.
- 3 (0.1-lot size units, money rescaled): reproduced independently for every exposure (size units and factor in 3b.1); the simulator books round(q_c x ticks x tick value in cents) exactly; MYM (q_c 3, weight 0.1, factor 0.4) and the cents-quoted ZS (vendor tick 0.25, $12.50) reproduce bit for bit in 3b.3. VERIFIED.
- 4 ([O_X, C_X) rather than MES's [08:30, 15:08)): faithful to D2's risk window; the alternative (to F) would add the post-settlement hours to every segment and would not be D2's window. VERIFIED.
- 5 and 6 (D2's dates and R3's endpoints; E|m_1| x tick value = r_c): reproduced exactly for all 28. VERIFIED.
- 7 (T = 16 and 32 kept): including them can only lower eps; no T = 32 cell binds anywhere. VERIFIED.
- 8 (cost at MES's timing, no event-window cost): faithful to D.1e's method; reproduced to 0.0 for all 28. VERIFIED.
- 10 (undersized: min(translated, funnel)): the conservative reading; ZT, ZF, 6C, 6N, ZC and MBT take their funnel figures (5, 6, 9, 10, 4, 90), all below their translated bars. VERIFIED.
- 11 (exact ascending evaluation, B1 then B2): my replay reproduces every B1 evaluated set and first pass; each cell's verdict depends only on its own seed, so the shortcut is exact. VERIFIED.
- 15 (floor of the stored float): no figure lies within 1e-9 of an integer (flags false for all 28). VERIFIED.
- 16 (BASE_SEED, 8,000 careers): my full-length re-simulations reproduce the stored samples bit for bit, which verifies the seed, the run count, the generator's RNG consumption and the money scaling together. VERIFIED.
- A-1 (early stop): k_min = 6,469, max failures 1,531 recomputed; every stopped row exceeds it; my own early-stop driver stops at the same run and failure counts. VERIFIED.

#### 3b.8 Verdict of part 3b

- Segment moves and costs: VERIFIED 28 of 28. Cells, order, first pass and epsilon arithmetic: VERIFIED 28 of 28. Re-simulated cells: VERIFIED 30 of 30. Operative figures: VERIFIED 28 of 28. B2 funnel figures: VERIFIED 8, PENDING 0 of 8.
- Findings: no DISCREPANCY. NOTE: the MES robust critical value applied to every exposure (declaration 1) is the one reading that could move which cells pass; it is capped by the translated bar and is for the user, as declared.
- Not done: nothing.
