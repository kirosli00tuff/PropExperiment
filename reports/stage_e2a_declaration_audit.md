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
