# Stage E.2a Task 4: the lead's rulings on the ML route freeze audit

Audit: reports/stage_e2a_declaration_audit.md, Part 1 (DeclarationAuditor-FableXHigh, Claude Fable 5.1
at xhigh, written 00:43 PDT). Verdict **READY WITH FIXES**: 2 BLOCKING (ML-A01, ML-A02), 14 SHOULD FIX
(ML-A03 to ML-A16), 10 NOTE (ML-A17 to ML-A26). Checks: mapping HOLDS; no post-data choice DOES NOT HOLD
as written, holds after the fixes; partition HOLDS; consistency HOLDS except four fixable items.

Rulings by the lead (Opus 5.5, xhigh), 2026-09-25, 00:50 to 01:00 PDT. The audit was not re-run. Every
fix is an exact-string addition to docs/STAGE_E_ML_DESIGN.md, written as a bracketed "[Stage E.2a ruling
on audit ML-A##]" note in Stage E.1's style (superseded words struck, never deleted); the appendix below
gives every fix's old and new text. No fix needs a new user decision: each fills in, within V1 to V9, a
detail the accepted text left open, and the auditor graded every fix "within V1-V9". Both BLOCKING
findings are fixed, so the freeze proceeds.

## Rulings

| # | Grade | Finding (short) | Ruling | Fix |
|---|---|---|---|---|
| ML-A01 | BLOCKING | selection metric: no prediction-to-position rule, no equal-risk unit, no aggregation | **Fixed** as the auditor proposed: long if y_hat > 0, short if y_hat < -2c, else flat; one open position per product in time order; P&L in sigma units; product day = sum, portfolio day = mean over products with rows; split score = mean over its dates; configuration score = mean of 10 split scores | R-09 |
| ML-A02 | BLOCKING | "the cost threshold" undefined; a symmetric threshold admits losing shorts | **Fixed**: per side at M4's stress m = 1.5: long if mu > 0.5 c_bar, short if mu < -2.5 c_bar | R-10 |
| ML-A03 | SHOULD FIX | six blocks undefined; two descriptions of block 6 | **Fixed**: the blocks are cut from the calendars alone (every CME trade date 2019-05-06..2024-02-29 of at least one group calendar; six blocks of floor(n/6), the sixth takes the remainder; same boundaries for every product; into the route manifest before any fit); "2023-late" struck. The lead chose the calendar over the bars so that the cut needs no data | R-11, R-18 |
| ML-A04 | SHOULD FIX | "frozen with this design" but no code exists; no code hash before the purchase | **Fixed**: frozen by E.2b's harness manifest before E.ML-buy; new M7.8 (E.ML-train and E.ML-test refuse on a mismatch) | R-15, R-20, R-22 |
| ML-A05 | SHOULD FIX | no rule for missing inputs or warm-up | **Fixed** as proposed: exclusion, no imputation, warm-up never from holdout-2 | R-07 |
| ML-A06 | SHOULD FIX | sigma_X,d defined by reference to superseded B4 | **Fixed**: D2's r_c form per date in the vehicle's ticks, the Family H complete-day rule, missing below 20 complete dates; B4 struck | R-03 |
| ML-A07 | SHOULD FIX | "longest history" ties for ten exposures | **Fixed**: ties to the full-size contract, else the most active permitted; the 31 price-path contracts listed | R-02 |
| ML-A08 | SHOULD FIX | target units and cost vs D2 and D8 | **Fixed**: moves in the vehicle's ticks; the vehicle's full D8 cost at q_c including the depth term and the event-window rule; an exposure with no D2 vehicle has no target | R-06 |
| ML-A09 | SHOULD FIX | decision-time boundary and row exclusions | **Fixed**: t < C_X and t + h <= F_X; roll-blackout and early-close dates excluded; degraded dates kept (NULL_CRITERIA_E 4) | R-05 |
| ML-A10 | SHOULD FIX | tie rules; "sign agrees" | **Fixed** as proposed | R-09, R-12, R-13 |
| ML-A11 | SHOULD FIX | surrogate implementation and count | **Fixed**: 42 surrogates (7 clusters x 2 challengers x 3 horizons), sklearn settings and seed, unrounded float64 cuts | R-10 |
| ML-A12 | SHOULD FIX | LSTM and indicator encoding under-specified | **Fixed**: MSE loss, clock-aligned 5-minute bars, embedding dimension **4** (the lead's number), linear output on hidden state + embedding + static features, no clipping or decay, seeded shuffling, deterministic algorithms; one-hot F18/F19 for LightGBM | R-04 |
| ML-A13 | SHOULD FIX | the embargo parenthetical misstates the longest lookback | **Fixed**, first option: the one-trade-date embargo stays; trailing daily statistics are not embargoed, with the reason; parenthetical struck | R-18 |
| ML-A14 | SHOULD FIX | the alpha split against frozen D5 | **Fixed**: D5's K counts every family with a tested set, the route included; every family at 0.05 / (K + 1) when the route tests a rule; recorded in docs/DECISIONS.md as V6's effect on D5 | R-16; DECISIONS.md |
| ML-A15 | SHOULD FIX | test series and unit of a multi-exposure rule | **Fixed**: the rule trades all its cluster's traded exposures at q_c; NULL_CRITERIA_E 3's multi-leg series with the primary leg = the cluster's F16 lead exposure's vehicle (fallback: highest-ADV traded exposure); DSR variance over the route's tested rules | R-17 |
| ML-A16 | SHOULD FIX | the write-up is an unconstrained human step | **Fixed**: machine-readable rule JSON hashed; the entry is a rendering with no field changed | R-14 |
| ML-A17 | NOTE | K8's slot is unreachable | **Acted on**: one sentence (cap 14 in practice) | R-13 |
| ML-A18 | NOTE | research-window constants in training | **Acted on**: new M7.9 names the three quantities and why they are not a partition breach | R-20 |
| ML-A19 | NOTE | warm-up cost at the test's start | **Acted on**: one sentence beside M1's known cost | R-01 |
| ML-A20 | NOTE | how to read peak VRAM | **Acted on**: max_memory_reserved plus the per-process context | R-21 |
| ML-A21 | NOTE | cosmetics (a)-(e) | (b) resolved by the FROZEN header (R-00); (e) acted on inside R-02; (a), (c), (d) left (the header's note-governs rule covers (a); (c) and (d) are accurate) | R-00, R-02 |
| ML-A22 | NOTE | Q-1 to Q-3 correct; Q-2 not a conflict | Recorded | none |
| ML-A23 | NOTE | "not on disk" is a store-level control | **Acted on**: a path allowlist with a planted-path test | R-19 |
| ML-A24 | NOTE | PBO and DSR reporting details | Left: those figures inform and decide nothing (M6) | none |
| ML-A25 | NOTE | engine-only rules not in training targets | **Acted on**: one sentence | R-08 |
| ML-A26 | NOTE | LightGBM determinism | **Acted on** inside R-04: force_col_wise=true, version recorded | R-04 |

R-00b records in the file header that the rulings are bracketed notes and govern like the V notes.

## New wording the user has not seen (quoted, as the auditor asked)

These are fill-ins within V1 to V9, but their exact words are new. The user may overturn any of them
before E.2b builds the route; an overturn is a logged amendment before any fit.

- **ML-A01 (selection metric):** "At each validation row, with the model's prediction y_hat and the row's
  D8 round-turn cost c at 1.0 x (both in sigma_X,d units, as M4's target), the position is long if
  y_hat > 0, short if y_hat < -2c, and flat otherwise ... A split's score is the mean of the portfolio's
  daily P&L over the split's validation dates; a configuration's score is the mean of its 10 split
  scores; the highest score is selected."
- **ML-A02 (candidate threshold):** "the leaf is a long candidate if mu > (m - 1) c_bar = 0.5 c_bar, a short
  candidate if mu < -(m + 1) c_bar = -2.5 c_bar, and otherwise not a candidate".
- **ML-A12 (LSTM):** "the product embedding has 4 dimensions; the output layer is one linear layer on the
  concatenation of the final hidden state, the product embedding and the static features".
- **ML-A13 (embargo):** "the trailing daily statistics (sigma_X,d and F10 over 20 dates, F7 and F8 over
  one, F17 over about 140) are not embargoed".
- **ML-A15 (primary leg):** "the primary leg is the vehicle of the cluster's F16 lead exposure (K1
  Nasdaq-100, K2 10-year, K3 EUR, K4 WTI, K5 gold, K6 corn, K7 bitcoin)".
- Also new, the lead's own: ML-A03's calendar-based block cut, and ML-A07's list of 31 price-path
  contracts (NQ, RTY, YM; ZT, ZF, ZN, TN, ZB, UB; 6E, 6A, 6B, 6C, 6J, 6S, 6N; CL, NG, RB, HO; GC, SI,
  HG; ZC, ZW, ZS, ZM, ZL, HE, LE; MBT).

## After the fixes

- The four checks: mapping holds (Task 1's log is unchanged; these fixes are logged here); no choice is
  left after training data is seen, given M7.8's code freeze in E.2b; the partition holds; consistency
  holds, with D5's split recorded as V6's effect.
- No BLOCKING finding remains, so the freeze proceeds (commit with reports/stage_e2a_ml_freeze.json).

## Appendix: every fix applied to docs/STAGE_E_ML_DESIGN.md

Applied by one script (exact-string replacements, each matched exactly once before anything was written). docs/STAGE_E_ML_DESIGN.md sha256 before the fixes 185e8cd5c908048ff6de3ae63036b31ed7b8badab62c8d4aec2890d58aeba8a0; after the fixes (the frozen text) eb7f9971753f05fa103026617ed8a98a27f28db2429a01ca858faafcfa329747.

### R-00 (freeze header; ML-A21(b))

Old:

```
# Stage E ML route: design

~~**DRAFT.
```

New:

```
# Stage E ML route: design

FROZEN by Stage E.2a on 2026-09-25, manifest reports/stage_e2a_ml_freeze.json

~~**DRAFT.
```

### R-00b (record of the rulings)

Old:

```
differ, the note governs.
```

New:

```
differ, the note governs. Stage E.2a's rulings on the independent freeze audit
(reports/stage_e2a_declaration_audit.md, Part 1; reports/stage_e2a_ml_freeze_rulings.md) are the
bracketed "[Stage E.2a ruling on audit ML-A##]" notes; they fill in details the accepted text left
open, within V1 to V9, and they govern likewise.
```

### R-01 (ML-A19)

Old:

```
"inconclusive by design" before its test, as for any member.
```

New:

```
"inconclusive by design" before its test, as for any member. [Stage E.2a ruling on audit ML-A19:
with M4's missing-input rule, trailing features are missing on the research window's first dates
(about 20 trade dates for sigma_X,d and F10, about 140 for F17), because holdout-2 never supplies a
warm-up; a rule's eligible dates can therefore be fewer than 290, and the power check counts that.]
```

### R-02 (ML-A07; ML-A21(e))

Old:

```
2021-05) is the only permitted contract; BTC is not permitted and is not used.
```

New:

```
2021-05) is the only permitted contract; BTC is not permitted and is not used. [Stage E.2a ruling
on audit ML-A07 (V1): E.0's quote metadata resolves every month from 2019-05 for most micros as
well, so "the longest history" ties; the tie goes to the full-size contract, and where an exposure
has no permitted full-size contract, to its most active permitted contract. The 31 price-path
contracts, fixed now from quote metadata alone: K1 NQ, RTY, YM; K2 ZT, ZF, ZN, TN, ZB, UB; K3 6E,
6A, 6B, 6C, 6J, 6S, 6N; K4 CL, NG, RB, HO; K5 GC, SI, HG; K6 ZC, ZW, ZS, ZM, ZL, HE, LE; K7 MBT.
Where D2's vehicle is another contract of the same exposure, the rule trades the vehicle with its
own cost model and tick value (D2), and that cluster's own step 2 purchase still buys the
vehicle's history (audit ML-A21(e)).]
```

### R-03 (ML-A06)

Old:

```
  complete trade dates before d (the frozen B4 construction), in ticks, computed from bars that
```

New:

```
  complete trade dates before d ~~(the frozen B4 construction)~~ [Stage E.2a ruling on audit ML-A06
  (V2, V4): exactly, sigma_X,d = the mean, over the 20 complete trade dates before d, of |close of
  the bar starting at C_X - 1 min minus open of the bar starting at O_X| of the price-path
  contract, in ticks of the exposure's D2 vehicle (price units divided by the vehicle's tick size;
  M4's target), with O_X and C_X from D6's session table; a trade date is complete when both bars
  exist with one instrument_id and the date is not an early-halt or early-close date (the frozen
  Family H complete-day rule); with fewer than 20 complete dates
  before d, sigma_X,d is missing (M4, missing inputs)], in ticks, computed from bars that
```

### R-04 (ML-A12; ML-A26)

Old:

```
   to the output layer.
```

New:

```
   to the output layer.
   [Stage E.2a ruling on audit ML-A12 (V3): the LSTM's loss is the mean squared error on M4's
   normalized net target; its 5-minute bars are clock-aligned (xx:00, xx:05, ...), each built from
   the one-minute bars inside it, the last one closing at or before t; the product embedding has 4
   dimensions; the output layer is one linear layer on the concatenation of the final hidden state,
   the product embedding and the static features (F1 to F17 and F19's cluster one-hot); no gradient
   clipping and no weight decay; training rows are shuffled each epoch by a generator seeded
   20260924; torch.use_deterministic_algorithms(True), with CUBLAS_WORKSPACE_CONFIG=:4096:8 and
   cuDNN deterministic; the torch version is pinned in uv.lock. For LightGBM, F18 and F19 are one-hot
   columns (one per product with rows, one per cluster), and force_col_wise=true joins the fixed
   settings for run-to-run reproducibility (audit ML-A26), with the lightgbm version recorded in the
   route manifest.]
```

### R-05 (ML-A09)

Old:

```
  (D9.5a) and the CPI window where it binds (D9.12). At most 13 decision times per product per day,
```

New:

```
  (D9.5a) and the CPI window where it binds (D9.12). [Stage E.2a ruling on audit ML-A09 (V4,
  NULL_CRITERIA_E 4): t runs over O_X + 30 k minutes, k = 1, 2, ..., with t < C_X and t + h <= F_X
  of that date (D9.1); a whole trade date is excluded if it is a roll-blackout date of the product
  or an early-halt or early-close date of its group calendar; vendor-degraded dates are kept, since
  trials trade through them (NULL_CRITERIA_E 4).] At most 13 decision times per product per day,
```

### R-06 (ML-A08)

Old:

```
  whole training window), all divided by sigma_X,d. The net target is what is predicted, so the
  model learns net edges only.
```

New:

```
  whole training window), all divided by sigma_X,d. The net target is what is predicted, so the
  model learns net edges only. [Stage E.2a ruling on audit ML-A08 (V4, with D2 and D8 frozen): the
  price move is converted to ticks of the exposure's D2 vehicle (price units divided by the
  vehicle's tick size; the price-path contract and its vehicle quote the same underlying in the same
  price units), and the cost is the vehicle's full D8 round-turn cost at q_c in the same ticks: the
  entry and exit buckets' half-spreads, the depth term at q_c, and D8's event-window rule (a fill in
  [release, release + 30 min) of a scheduled major release that concerns the product pays the
  product's largest bucket half-spread for that side). sigma_X,d is in the same ticks. An exposure
  that D2 leaves without a vehicle ("no candidate") has no cost model, so it has no target and
  contributes no rows.]
```

### R-07 (ML-A05)

Old:

```
- **Size and caps:** q_c of D2's vehicle, the 1-lot-equivalent cap (D9.5), volatility caps
```

New:

```
- **Missing inputs and warm-up [Stage E.2a ruling on audit ML-A05 (V1, V4)].** A row with any
  missing input is excluded from every training, tuning, normalization and distillation set and
  produces no trade at the test; there is no imputation. Missing means: a lookback that is not full
  from bars on or after the store's first date (for example fewer than 20 complete trade dates for
  sigma_X,d); an absent bar at t, at t + 1 minute or at the exit; a lead product (F16) with no bar
  closing at or before t. At the test the warm-up comes from the research window's own bars, never
  from holdout-2 or March 2024 (M1's known cost, audit ML-A19).
- **Size and caps:** q_c of D2's vehicle, the 1-lot-equivalent cap (D9.5), volatility caps
```

### R-08 (ML-A25)

Old:

```
  design. The rules the route produces must satisfy every D9 constraint as written.
```

New:

```
  design. The rules the route produces must satisfy every D9 constraint as written. [Stage E.2a note
  on audit ML-A25: D9.7's price-limit exits and the locked-market rule act through the engine at the
  test and are not modelled in the training targets (rare dates).]
```

### R-09 (ML-A01; ML-A10)

Old:

```
   mean daily net P&L of M2's equal-risk portfolio at 1.0 x D8 cost; ties go to the smaller model.
```

New:

```
   mean daily net P&L of M2's equal-risk portfolio at 1.0 x D8 cost; ties go to the smaller model.
   [Stage E.2a ruling on audit ML-A01 (V5, V4): the selection metric, exactly. At each validation
   row, with the model's prediction y_hat and the row's D8 round-turn cost c at 1.0 x (both in
   sigma_X,d units, as M4's target), the position is long if y_hat > 0, short if y_hat < -2c, and
   flat otherwise (the target is the long's net P&L, so a short's expected net is -y_hat - 2c). M4's
   one-open-position rule applies in time order per product: a decision time is skipped while a
   position from an earlier decision time of the same product is open. A trade's realized net P&L,
   in sigma units, is the row's target y for a long and -y - 2c for a short. A product's daily P&L
   is the sum of its trades' P&L on that date, and zero on a date with rows and no trade; the
   portfolio's daily P&L is the mean over the products with rows on that date (equal risk: every
   product's P&L is in its own sigma units). A split's score is the mean of the portfolio's daily
   P&L over the split's validation dates; a configuration's score is the mean of its 10 split
   scores; the highest score is selected. Ruling on audit ML-A10 (V5): "the smaller model" means,
   for the trees, fewer num_leaves, then larger min_data_in_leaf, then larger lambda_l2; for the
   LSTM, fewer hidden units, then the shorter lookback.]
```

### R-10 (ML-A02; ML-A11)

Old:

```
   bar's open, exit at t + h (or F)".
```

New:

```
   bar's open, exit at t + h (or F)".
   [Stage E.2a ruling on audit ML-A02 (V5, V4): "the cost threshold" is per side, at M4's stress
   m = 1.5. With mu = a leaf's mean prediction and c_bar = the mean of its rows' D8 round-turn cost
   at 1.0 x (both in sigma units), the leaf is a long candidate if mu > (m - 1) c_bar = 0.5 c_bar,
   a short candidate if mu < -(m + 1) c_bar = -2.5 c_bar, and otherwise not a candidate; that is,
   the leaf's predicted net edge in the traded direction is positive at 1.5 x cost. Ruling on audit
   ML-A11 (V5): one surrogate per (cluster, challenger, horizon), fitted to that selected model's
   predictions, for the seven clusters K1 to K7 that have traded exposures (42 surrogates, at most
   four leaves each); scikit-learn DecisionTreeRegressor(max_depth=2, min_samples_leaf=0.02,
   criterion="squared_error", max_features=None, random_state=20260924), its version pinned in
   uv.lock; cut points are sklearn's thresholds as written (float64, not rounded), in sigma units
   where the feature is normalized; a leaf's conditions are "feature <= cut" on each left branch
   and "feature > cut" on each right branch of its path.]
```

### R-11 (ML-A03)

Old:

```
3. **Pre-test inside the training window (block 6, 2023-late..2024-02):** a candidate survives only
```

New:

```
3. **Pre-test inside the training window (block 6, ~~2023-late..2024-02~~ [Stage E.2a ruling on
   audit ML-A03: the sixth block of M7.3's cut]):** a candidate survives only
```

### R-12 (ML-A10)

Old:

```
   step spends none of the test window.
```

New:

```
   step spends none of the test window. [Stage E.2a ruling on audit ML-A10 (V5): "its sign agrees
   with blocks 1-5" means that the rule's realized net P&L on blocks 1-5 at 1.5 x D8 cost is also
   positive. A rule's P&L in steps 3 and 4 is computed as in step 1's ruling (one open position per
   product, sigma units, summed per product and date) over its cluster's exposures with rows.]
```

### R-13 (ML-A10; ML-A17)

Old:

```
   total** (2 x 8 clusters; K8 only if a surviving rule reads two clusters' products).
```

New:

```
   total** (2 x 8 clusters; K8 only if a surviving rule reads two clusters' products). [Stage E.2a
   ruling on audit ML-A10 (V5): after the longer horizon, ties go to the challenger listed first in
   M3 (LightGBM), then to the leaf that comes first in the surrogate's left-to-right leaf order.
   Note on audit ML-A17: every feature is the product's own or its own cluster's lead (F16), so no
   route rule reads two clusters' products; K8 gets no route rule and the cap is 14 (2 x 7) in
   practice.]
```

### R-14 (ML-A16)

Old:

```
   research-window bar is read for the test.
```

New:

```
   research-window bar is read for the test. [Stage E.2a ruling on audit ML-A16 (V5): the surrogate
   step itself writes each surviving rule as machine-readable JSON (features, cut points, sign,
   horizon, cluster, exposures, primary leg, provenance); the route manifest hashes that JSON; the
   catalog-format entry is a rendering of the JSON with no field changed, dropped or rounded.]
```

### R-15 (ML-A04)

Old:

```
Steps 2 to 4 are code, frozen with this design; the lead does not pick among rules.
```

New:

```
Steps 2 to 4 are code, ~~frozen with this design~~ [Stage E.2a ruling on audit ML-A04: frozen by
E.2b's harness manifest before E.ML-buy, M7.8]; the lead does not pick among rules.
```

### R-16 (ML-A14)

Old:

```
  0.05 / (K + 1), where K is the number of clusters with a non-empty Tier A. Holm runs across the
```

New:

```
  0.05 / (K + 1), where K is the number of clusters with a non-empty Tier A. [Stage E.2a ruling on
  audit ML-A14 (V6): V6 changes frozen D5's split; this is recorded in docs/DECISIONS.md as V6's
  effect on D5 and never edited into the frozen file. D5's K counts every family with a non-empty
  tested set, the route included once it has a tested rule; so when the route tests a rule, every
  family, each cluster's Tier A included, tests at 0.05 / (K + 1), D5's "at most 8" reads "at most
  9", and the program-level family-wise error stays at most 5%.] Holm runs across the
```

### R-17 (ML-A15)

Old:

```
  per exposure the rule trades).
```

New:

```
  per exposure the rule trades). [Stage E.2a ruling on audit ML-A15 (V6, NULL_CRITERIA_E 3): a route
  rule trades every traded exposure of its cluster (each with a D2 vehicle) at that vehicle's q_c;
  its edge series is NULL_CRITERIA_E 3's multi-leg series, the combined net dollars per
  research-window date at those sizes divided by (q_c x tick value) of its primary leg; the primary
  leg is the vehicle of the cluster's F16 lead exposure (K1 Nasdaq-100, K2 10-year, K3 EUR, K4 WTI,
  K5 gold, K6 corn, K7 bitcoin), or, if that exposure has no vehicle, of the cluster's traded
  exposure with the highest 2026 January-August ADV in D1's table, named in the rule's entry. The
  DSR's Sharpe variance is over the route's tested rules' research-window daily Sharpes. Nulls stay
  per exposure, as written.]
```

### R-18 (ML-A03; ML-A13)

Old:

```
   trade date on each side of every validation block (at least h, and at least the longest lookback,
   120 minutes or 6 hours for the LSTM).
```

New:

```
   trade date on each side of every validation block ~~(at least h, and at least the longest lookback,
   120 minutes or 6 hours for the LSTM)~~. [Stage E.2a ruling on audit ML-A13 (V1, as accepted): one
   full trade date is at least h and covers every intraday lookback (120 minutes; 6 hours for the
   LSTM), since no target and no intraday lookback crosses a trade date; the trailing daily
   statistics (sigma_X,d and F10 over 20 dates, F7 and F8 over one, F17 over about 140) are not
   embargoed: they are slow-moving level information, a full-lookback embargo would remove most of
   the training data, and the overlap touches model selection inside the training window only,
   never the test. Ruling on audit ML-A03 (V5): the six blocks are cut from the calendars alone,
   with no bar data: the training calendar is every CME trade date from 2019-05-06 to 2024-02-29
   that is a trade date of at least one group calendar (data/calendars/, data/cme_calendar.py); its
   n dates are cut in time order into six contiguous blocks of floor(n / 6) dates, the sixth taking
   the remainder; the boundaries are the same for every product (rows before a product's S_X do not
   exist) and are written into the route manifest before any fit.]
```

### R-19 (ML-A23)

Old:

```
   (a planted research-window bar in that store) must make the job refuse.
```

New:

```
   (a planted research-window bar in that store) must make the job refuse. [Stage E.2a note on audit
   ML-A23: the training job also asserts a path allowlist (the training-window store only), tested
   with a planted research-window path.]
```

### R-20 (ML-A04; ML-A18)

Old:

```
   one leg must not change the other leg's decisions).
```

New:

```
   one leg must not change the other leg's decisions).
8. **Code freeze [Stage E.2a ruling on audit ML-A04 (V8, frozen D11's manifest discipline)].**
   E.2b's harness manifest hashes the route's whole pipeline (the feature and target builders, the
   block cut, the CPCV splitter, the selection, surrogate, pre-test, ranking and write-up code, and
   every M7 test) before E.ML-buy; E.ML-buy runs only after that commit; E.ML-train and E.ML-test
   refuse to run when any hashed file differs.
9. **Research-window-derived constants [Stage E.2a note on audit ML-A18].** The only
   research-window-derived quantities the training may see are D8's cost surface (five mbp-1 dates,
   2025-26), D2's q_c and r_c, and S_X through V_ref,X (D4). They are level and liquidity
   information (spread by time of day, volatility scale, volume level), never a price path or a
   direction, and they are charged identically at the test; every hand-written member lives under
   the same convention (D8, NULL_CRITERIA_E 4).
```

### R-21 (ML-A20)

Old:

```
  (nvidia-smi, CUDA context included); while less than 0.5 GB of the 4 GB stays free, the batch size
```

New:

```
  (nvidia-smi, CUDA context included) [Stage E.2a note on audit ML-A20: the peak is
  torch.cuda.max_memory_reserved() plus the process's CUDA context from nvidia-smi's per-process
  figure, both recorded]; while less than 0.5 GB of the 4 GB stays free, the batch size
```

### R-22 (ML-A04)

Old:

```
  tree and pre-test code (M5, frozen with this design); the route manifest; every M7 test with known
```

New:

```
  tree and pre-test code (M5, ~~frozen with this design~~ [Stage E.2a ruling on audit ML-A04: frozen
  by E.2b's harness manifest before E.ML-buy, M7.8]); the route manifest; every M7 test with known
```

