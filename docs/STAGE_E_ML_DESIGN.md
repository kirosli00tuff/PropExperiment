# Stage E ML route: design

FROZEN by Stage E.2a on 2026-09-25, manifest reports/stage_e2a_ml_freeze.json

~~**DRAFT. Nothing in this file is frozen, hashed or registered.**~~ Written by the Stage E.1 lead
(Opus 5.5, max effort) on 2026-09-24, after the Stage E pre-registration freeze (commit 848f331,
manifest reports/stage_e1_freeze.json), for the user's review. ~~Stage E.2 freezes it~~ Stage E.2a
freezes it, with the user's
changes, before any ML fit and before any research-window bar is read. It replaces design section
D15 (superseded by the user's decision U6, docs/DECISIONS.md, 2026-09-24).

**Stage E.2a (2026-09-25) applied the user's decisions V1 to V9 (docs/DECISIONS.md, entry of
2026-09-25) to this draft.** Every edit is logged in reports/stage_e2a_ml_changes.md (old text, new
text, decision). Changed passages carry a bracketed "[V#, 2026-09-25: ...]" note; superseded text
stays visible, struck through, as in Stage E.1. The user accepted every proposed rule below (V1 to
V6, V8) except M8's, which the user amended (V7). Where a bracketed note and the text it annotates
differ, the note governs. Stage E.2a's rulings on the independent freeze audit
(reports/stage_e2a_declaration_audit.md, Part 1; reports/stage_e2a_ml_freeze_rulings.md) are the
bracketed "[Stage E.2a ruling on audit ML-A##]" notes; they fill in details the accepted text left
open, within V1 to V9, and they govern likewise.

Written before any price, bar or order-book data of any Stage E product was read. The only product
figures used here are Databento quote metadata (costs and billable bytes, no prices) and the frozen
design's own numbers.

**Purpose, set by the user (U6).** ML is a strategy-discovery tool. Its findings become plain rules
that are pre-registered and tested like any other member. No model is deployed or makes live
decisions. The deployed output of this route is at most a handful of plain rules in the catalog's
entry format; the models themselves are discarded after distillation, except as a hashed record.

**Evidence base.** reports/stage_e1_ml_research.md (MLLitReader-OpusHigh, 29 full-text reads, 33
logged queries; ids E1-ML-01 to E1-ML-29). Its bottom line, which shapes every item below: evidence
for ML predictability in liquid futures at 15 minutes to one day, net of cost, is thin (Q1); pooling
is the default in the futures literature but nobody measures what it buys in effective sample size
(Q2); the multiple-testing and leakage literature is strong and says the search must be small and
fully counted (Q3); and no source distils a futures model into rules and tests the rules out of
sample net of cost (Q4). The route is therefore designed as a small, fully accounted search whose
most likely honest outcome is a null, and it is built so that a null is informative.

Each item: **Proposed rule**, **Reasoning**, **Alternatives**, **User decides**.

---

## M1. Data partition

**Proposed rule.** [V1, 2026-09-25: accepted by the user.]
- **Training window** (fitting, tuning, model selection, normalization constants, distillation):
  trade dates from S_X (the product's start rule, frozen design D4; earliest 2019-05-06) through
  2024-02-29. This is the older history, which the hand-written catalog uses as its confirmation
  window.
- **Never used by the route:** March 2024 (embargo) and holdout-2 (2024-04-01..2025-03-31), and
  everything from 2026-06-21 00:00 UTC on (holdout-1 side, not bought for new products).
- **Test window** (one test of the frozen distilled rules, once): the research window,
  trade dates 2025-04-01..2026-06-19. The route never trains, tunes, normalizes or distils on it.
  The models themselves are not tested; only the distilled plain rules are (M5, M6).
- **Final gate:** holdout-2 stays sealed. A route rule that passes its test goes to the user as a
  discussion item for a registered holdout-2 read, exactly like a hand-written member that passes
  its confirmation (NULL_CRITERIA_E; D5). No route result is a claim before that read.
- **Order of freezes.** The hand-written catalog was frozen in E.1 (848f331) before any ML
  training, so no ML result can leak into it. ML-derived rules are never tested on data the models
  trained on. The ML route design (this file) is frozen in ~~E.2~~ E.2a [V8, 2026-09-25: Stage E.2 is split
  into E.2a (this freeze and the shared harness) and E.2b (the route's build)] before any ML fit and
  before any research-window bar is read by anyone.
- **Distillation is mechanical** (M5): no human or LLM choice is made between training and the
  test. This matters because cluster screening sessions will read research-window bars (hand-written
  members) before some route rules are tested; a distillation step with free choices could absorb
  what those sessions saw. With a fixed procedure there is nothing to absorb.

**What this implies for data and money.** The route needs the training-window history of every
product it uses, which pulls D13's step 2 purchases forward (U4 allows this). From E.0's quotes in
the ledger (session stage-E.0-2026-09-23; costs only):

| Purchase | Scope | Quoted |
|---|---|---|
| training window only, 2019-05..2024-02 | one contract per traded exposure (31), cheapest to dearest per exposure | $131.89-153.95 |
| training window only | every admissible contract (45) | $211.81 |
| full step 2, 2019-05..2025-03 (training window plus March 2024 and the 13 holdout-2 chunks, sealed on arrival) | one contract per exposure | $164.71-189.31 (frozen D13, audit FA-09) |

Per cluster, training window only, one contract per exposure: K1 $18.06-18.44; K2 $33.10; K3
$33.73-40.22; K4 $12.11-20.54; K5 $11.27-18.03; K6 $21.72; K7 $1.90. Buying the full step 2 range
for the route's contracts (and sealing holdout-2 on arrival, as step 2 always does) costs about $33
more in total and avoids a second pass over the same months later; that is the proposal [V1,
2026-09-25: accepted: the route buys the full step 2 range, 2019-05..2025-03, of one contract per
exposure, holdout-2 sealed on arrival].

acct-2 holds $125.00, of which step 1 uses about $103 (Task 6); **the route's data cannot be bought
without new funding and a new session cap.** [V1, 2026-09-25: funding is pending: the user will
top up acct-2. Nothing is bought in Stage E.2a.] Which contract per exposure: the one with the longest
history (usually the full-size contract: CL, NG, HG rather than MCL, MNG, MHG, which were listed in
2021-2023 and have no bars before; E.0 quote failures). The route learns on the underlying's price
path; its rules trade D2's chosen vehicle, with that vehicle's cost model. For bitcoin, MBT (from
2021-05) is the only permitted contract; BTC is not permitted and is not used. [Stage E.2a ruling
on audit ML-A07 (V1): E.0's quote metadata resolves every month from 2019-05 for most micros as
well, so "the longest history" ties; the tie goes to the full-size contract, and where an exposure
has no permitted full-size contract, to its most active permitted contract. The 31 price-path
contracts, fixed now from quote metadata alone: K1 NQ, RTY, YM; K2 ZT, ZF, ZN, TN, ZB, UB; K3 6E,
6A, 6B, 6C, 6J, 6S, 6N; K4 CL, NG, RB, HO; K5 GC, SI, HG; K6 ZC, ZW, ZS, ZM, ZL, HE, LE; K7 MBT.
Where D2's vehicle is another contract of the same exposure, the rule trades the vehicle with its
own cost model and tick value (D2), and that cluster's own step 2 purchase still buys the
vehicle's history (audit ML-A21(e)).]

**Reasoning.** The research window is about 300 trade dates, too few to fit anything flexible
(E1-ML-01's authors make the same point about four years of one-instrument intraday data; D15.1
said so for its own design). The older window is about 1,200 trade dates per product. Training on
the older history and testing on the recent window uses each block once, keeps the most recent
regime as the test (the one closest to deployment), and leaves holdout-2 untouched for the final
gate of every route. Using the catalog's confirmation window for training does not weaken the
catalog: the catalog is frozen, and its confirmation depends on nothing the route does.

**Known cost of this partition.** The test window is short. For a daily t above 3.0 on about 290
eligible dates, a rule needs a daily Sharpe of about 0.18 (annualized about 2.8). A rule whose
research-window power check (D4's method at eps_X) needs more days than the window has is labelled
"inconclusive by design" before its test, as for any member. [Stage E.2a ruling on audit ML-A19:
with M4's missing-input rule, trailing features are missing on the research window's first dates
(about 20 trade dates for sigma_X,d and F10, about 140 for F17), because holdout-2 never supplies a
warm-up; a rule's eligible dates can therefore be fewer than 290, and the power check counts that.]

**Alternatives.**
- (a) Train on the research window (the superseded D15): too little data; rejected.
- (b) Train on the older window and test on holdout-2 directly: spends the program's final gate on
  a first test; rejected.
- (c) Walk-forward through the whole history with repeated refits: every refit is a new look at
  data later used for the test; rejected (D4's reasoning).
- (d) The proposal, but training only through 2023-02 and using 2023-03..2024-02 as an internal
  pre-test of the distilled rules before the research-window test (M5 uses the last training block
  this way inside the training window, so no separate carve-out is needed).

**User decides:** the partition; funding acct-2 (or another account) for the route's history and
the cap for that purchase; whether the route buys the full step 2 range per contract (proposed) or
only 2019-05..2024-02.
[V1, 2026-09-25: decided. The partition as proposed: train, tune, normalize and distil only on
S_X..2024-02-29; March 2024 and holdout-2 are never touched; the frozen distilled rules are tested
once on the research window; holdout-2 stays the final gate. The route buys the full step 2 range
(2019-05..2025-03) of one contract per exposure, holdout-2 sealed on arrival. Funding is pending
(the user will top up acct-2); V1 sets no cap for that purchase, which stays the user's decision.]

---

## M2. Pooling

**Proposed rule.** [V2, 2026-09-25: accepted by the user.]
- **One pooled model per challenger across all 31 traded exposures**, with per-product
  normalization and product and cluster indicators as features. Not per-cluster models.
- **Per-product normalization:** every price-based feature and the target are divided by the
  product's trailing volatility scale sigma_X,d = the mean absolute day-session move over the 20
  complete trade dates before d ~~(the frozen B4 construction)~~ [Stage E.2a ruling on audit ML-A06
  (V2, V4): exactly, sigma_X,d = the mean, over the 20 complete trade dates before d, of |close of
  the bar starting at C_X - 1 min minus open of the bar starting at O_X| of the price-path
  contract, in ticks of the exposure's D2 vehicle (price units divided by the vehicle's tick size;
  M4's target), with O_X and C_X from D6's session table; a trade date is complete when both bars
  exist with one instrument_id and the date is not an early-halt or early-close date (the frozen
  Family H complete-day rule); with fewer than 20 complete dates
  before d, sigma_X,d is missing (M4, missing inputs)], in ticks, computed from bars that
  close before the decision time. No normalization constant is estimated on any row after the
  training window, and none is estimated on a fold's validation rows (M7).
- **Correlation handling:**
  - validation folds split by trade date, never by row: every product's rows for a date fall in the
    same fold, so correlated same-day rows cannot sit on both sides of a split;
  - purge and embargo by date (M7);
  - the selection metric is computed on the daily P&L of an equal-risk portfolio of all products'
    signals, so the number of independent observations the metric rests on is the number of dates,
    not rows;
  - for accounting, the route states its effective sample as the number of training dates (about
    1,200), not the number of rows (about 450,000).

**Reasoning.** The Oxford-Man futures work pools across all contracts by default (E1-ML-10: "all M
possible prediction and target tuples across all N assets"), with volatility-normalized targets;
X-Trend and DeePM add per-asset embeddings (E1-ML-13, E1-ML-14). At tick level a universal model beat
asset-specific ones (E1-ML-15). No source quantifies the effective-sample gain across correlated
assets (Q2: "no source found"), so the proposal does not claim one: it pools to give the model more
varied examples of the same mechanisms, and it counts evidence in dates. Cross-cluster pooling adds
the most independent variation: E1-ML-05 measured mean daily correlation 0.67 within an asset class
and 0.05 across classes on 16 CME futures. Within a cluster (K2's six rates contracts) pooling adds
little independent information; across clusters it adds much more. A tree model can still learn
cluster-specific structure through the indicators.

**Alternatives.** Per-cluster models (eight models per challenger: eight times the search, each on
less data; rejected on trial accounting); per-product models (worse); pooling with a learned
embedding (only for the deep challenger, M3, where it is the natural form); a correlation-adjusted
effective sample size (no source gives a method for a pooled model; not proposed).

**User decides:** one pooled model versus per-cluster models.
[V2, 2026-09-25: decided: one pooled model per challenger across the 31 traded exposures, evidence
counted in trade dates.]

---

## M3. The challenger list, fixed in advance

**Proposed rule. Two challengers, 36 configurations in total, listed in full.** The TCN is dropped.
[V3, 2026-09-25: accepted by the user.]

1. **Gradient-boosted trees (baseline), LightGBM, regression (L2) on the normalized net target.**
   Grid (8 configurations per horizon, 24 in total over M4's three horizons):
   num_leaves {7, 31} x min_data_in_leaf {500, 2000} x lambda_l2 {1.0, 10.0}.
   Fixed: learning_rate 0.03, 400 boosting rounds, no early stopping, feature_fraction 0.8,
   bagging_fraction 0.8, bagging_freq 1, max_depth -1, deterministic true, num_threads 8 (~~the
   CLAUDE.md maximum~~ [V7, 2026-09-25: inside the overnight profile's 14-thread limit; the value
   stays 8]), seed = bagging_seed = feature_fraction_seed = data_random_seed = 20260924.
2. **One small LSTM on normalized 5-minute bar sequences** (PyTorch), with the product embedding of
   M2. Grid (4 configurations per horizon, 12 in total): hidden units {16, 32} x lookback {24, 72}
   five-minute bars (2 or 6 hours, never crossing the trade date's first bar: shorter sequences are
   left-padded and masked). Fixed: one layer, dropout 0.2, Adam at 1e-3, batch 512 [V7, 2026-09-25: E.2b's probe may lower
   it, by M8's rule, to leave at least 0.5 GB of VRAM free], 8 epochs, no
   early stopping, seed 20260924, deterministic algorithms on. Inputs per step: normalized open-to-
   close return, high-low range, and the log volume ratio of M4, plus the static features of M4 fed
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

**Reasoning, by the evidence (reports/stage_e1_ml_research.md).**
- Trees as the baseline: on medium-sized tabular data trees beat networks (E1-ML-09, general ML,
  about 10k samples, the gap shrinking at 50k); at daily horizons on S&P 500 stocks RF and GBT beat
  a DNN net of costs (E1-ML-08); GBRT was among the net-positive 15-minute SPY forecasters (E1-ML-07).
  Trees also distil naturally into rules (M5; E1-ML-25, E1-ML-27).
- One LSTM, justified: the only sources with net-of-cost gains from deep sequence models on futures
  are the pooled daily Oxford-Man papers (E1-ML-10 LSTM on 88 futures, E1-ML-11, E1-ML-14), and an
  LSTM helped at 1-minute SPY (E1-ML-06). Against it: the one intraday futures comparison, on MNQ,
  found neither GBT nor an LSTM beat the base rate (E1-ML-01), and E1-ML-05 found learned daily
  policies on 16 CME futures only match 1/N in the pooled cross-asset case. That evidence supports
  one small, pooled LSTM as a challenger, not two networks.
- TCN dropped: no source in the log tests a temporal convolutional network on futures at any
  horizon. The prompt's rule is to justify each challenger by the evidence or drop it.
- Grid size: with about 4.8 years of training data, MinBTL says "no more than forty-five
  independent model configurations should be tried" before an in-sample Sharpe of 1 is expected
  from noise (E1-ML-19, for 5 years). 36 configurations stay under that bound, and the bound
  assumes independent trials, which these are not, so the effective count is lower. The grids are
  small on purpose; D15's 48-configuration grid per cluster (384 in total) would have exceeded it
  many times over.

**Alternatives.** A transformer (no intraday futures evidence; E1-ML-05's pooled transformer only
matched 1/N at daily horizons; rejected); a TCN (dropped, above); random forests as a third
challenger (E1-ML-08 favours them, but a third family adds trials for a small expected gain); a
larger tree grid (rejected on MinBTL).

**User decides:** the two challengers (or trees only, which halves the compute and removes the GPU
question in M8); the grids.
[V3, 2026-09-25: decided: LightGBM plus one small LSTM, 36 configurations in total, as listed; the
TCN stays dropped.]

---

## M4. Features and targets

**Proposed rule.** [V4, 2026-09-25: accepted by the user.]
- **Decision times:** every 30 minutes, at O_X + 30, O_X + 60, ... in the product's day session (the
  frozen D6 session table), while t + h <= F_X (D9 flat time), excluding the event-minute guard
  (D9.5a) and the CPI window where it binds (D9.12). [Stage E.2a ruling on audit ML-A09 (V4,
  NULL_CRITERIA_E 4): t runs over O_X + 30 k minutes, k = 1, 2, ..., with t < C_X and t + h <= F_X
  of that date (D9.1); a whole trade date is excluded if it is a roll-blackout date of the product
  or an early-halt or early-close date of its group calendar; vendor-degraded dates are kept, since
  trials trade through them (NULL_CRITERIA_E 4).] At most 13 decision times per product per day,
  so D9's 20-entry floor holds by construction. One open position per product at a time: a
  decision time is skipped while a position from an earlier decision is open.
- **Horizons (three):** h in {30 minutes, 120 minutes, to the flatten F_X}. Each horizon is its own
  model target (M3's grids run per horizon).
- **Target:** y = (open of the bar at t + h, or the forced flatten fill at F) minus (open of the
  bar at t + 1 minute), in ticks of the price-path contract, minus the D8 round-turn cost in ticks
  at t's and the exit's time-of-day buckets (cost model from the step 1 mbp-1 sample, applied to the
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
- **Features** (about 20; every value has an availability time <= t and the validator of M7
  enforces it):
  - F1-F5: normalized returns over the last 5, 15, 30, 60 and 120 minutes (bar closes <= t);
  - F6: return from the trade date's first bar to t (the CP1 family's signal);
  - F7: overnight gap, open of the day session minus the prior day's close at C (D6);
  - F8: prior complete day's close-location value (the CP3 family's signal);
  - F9: intraday range so far / sigma_X,d;
  - F10: log ratio of the last 30 minutes' volume to the median of the same 30 minutes over the
    prior 20 trade dates (the bars' volume field; ~~E.2~~ the route's pipeline [V8, 2026-09-25: built in
    E.2b] reads it, this file does not);
  - F11: minutes since O_X; F12: day of week;
  - F13-F15: scheduled-event flags from calendars known in advance: minutes to the next and since
    the last scheduled major release that concerns the product (D8's list: Topstep's release table
    plus the catalog's named releases, with their published timestamps), and a release-day flag;
  - F16: the cluster's lead product's normalized 30-minute return (K1 NQ, K2 ZN, K3 6E, K4 CL, K5 GC,
    K6 ZC, K7 MBT), from its bars closing <= t, never from a later close (E1-ML-14's asynchronous-
    close look-ahead);
  - F17: trailing 20-day volatility state, sigma_X,d over its own 120-day median (D-family state);
  - F18, F19: product and cluster indicators (M2).
- **Missing inputs and warm-up [Stage E.2a ruling on audit ML-A05 (V1, V4)].** A row with any
  missing input is excluded from every training, tuning, normalization and distillation set and
  produces no trade at the test; there is no imputation. Missing means: a lookback that is not full
  from bars on or after the store's first date (for example fewer than 20 complete trade dates for
  sigma_X,d); an absent bar at t, at t + 1 minute or at the exit; a lead product (F16) with no bar
  closing at or before t. At the test the warm-up comes from the research window's own bars, never
  from holdout-2 or March 2024 (M1's known cost, audit ML-A19).
- **Size and caps:** q_c of D2's vehicle, the 1-lot-equivalent cap (D9.5), volatility caps
  (D9.11), market orders only, no stops (D9.4), the price-limit rule (D9.7), all as in the frozen
  design. The rules the route produces must satisfy every D9 constraint as written. [Stage E.2a note
  on audit ML-A25: D9.7's price-limit exits and the locked-market rule act through the engine at the
  test and are not modelled in the training targets (rare dates).]

**Reasoning.** The features are the frozen program's own mechanisms (the ports, D-family state,
calendar events, cross-product lead) plus generic returns, so a distilled rule is readable in the
catalog's terms. E1-ML-05 found engineered features "added little" beyond raw return history, so
the set is kept short. Net targets follow E1-ML-07's rule of trading only past the cost. The early-
era bias of D8's cost model (calibrated on 2025-26 books, NULL_CRITERIA 4.3) makes training-window
costs optimistic; M5's selection therefore requires the rule's training-window edge to survive at
1.5 x the D8 cost (a conservative default; no source supports a specific multiplier).

**Alternatives.** 15-minute decision spacing (up to 26 a day, above D9's 20-entry floor unless
capped; rejected); classification of direction (loses the size of the move; rejected); more
horizons (each multiplies the grid; rejected); order-book features (the program has mbp-1 on five
days only; E1-ML-02 to 04 find order-book predictability only at seconds).

**User decides:** the three horizons; the feature list; the 1.5 x cost stress in selection.
[V4, 2026-09-25: decided: the three horizons, the feature list and the 1.5 x cost stress, as
written.]

---

## M5. Distillation into plain rules

**Proposed rule. A fixed procedure, no choices after training.** [V5, 2026-09-25: accepted by the
user.]
1. **Model selection (training window only):** combinatorially purged cross-validation by trade date
   (M7) over the training window's first five of six contiguous blocks; the selection metric is the
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
   One configuration is selected per horizon and per challenger; each is refit once on blocks 1-5.
2. **Surrogate rules per cluster:** for each cluster k, fit a depth-2 decision tree (CART, minimum
   leaf 2% of the cluster's rows) to the selected model's predictions on cluster k's training rows
   of blocks 1-5 (fidelity target), using only features F1-F17 (no indicators). Each leaf whose mean
   prediction exceeds the cost threshold in absolute value is a candidate rule: "IF <at most two
   feature conditions at fixed cut points> THEN market entry in the sign of the leaf at the next
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
3. **Pre-test inside the training window (block 6, ~~2023-late..2024-02~~ [Stage E.2a ruling on
   audit ML-A03: the sixth block of M7.3's cut]):** a candidate survives only
   if, on block 6, its net P&L is positive at 1.5 x D8 cost, it makes at least 30 trades, it meets
   D9's floors, and its sign agrees with blocks 1-5. Block 6 is still training-window data, so this
   step spends none of the test window. [Stage E.2a ruling on audit ML-A10 (V5): "its sign agrees
   with blocks 1-5" means that the rule's realized net P&L on blocks 1-5 at 1.5 x D8 cost is also
   positive. A rule's P&L in steps 3 and 4 is computed as in step 1's ruling (one open position per
   product, sigma units, summed per product and date) over its cluster's exposures with rows.]
4. **Keep at most 2 rules per cluster**, ranked by block-6 net P&L per trade date at 1.5 x cost, ties
   to fewer conditions, then to the longer horizon. **The route produces at most 16 rules in
   total** (2 x 8 clusters; K8 only if a surviving rule reads two clusters' products). [Stage E.2a
   ruling on audit ML-A10 (V5): after the longer horizon, ties go to the challenger listed first in
   M3 (LightGBM), then to the leaf that comes first in the surrogate's left-to-right leaf order.
   Note on audit ML-A17: every feature is the product's own or its own cluster's lead (F16), so no
   route rule reads two clusters' products; K8 gets no route rule and the cap is 14 (2 x 7) in
   practice.]
5. **Write-up and freeze:** each surviving rule is written in the catalog's entry format (products,
   exposures, the exact rule with its cut points as fixed literals, decision times, exit, sizing,
   Topstep check, falsification condition, trials in N), with its provenance (model hash,
   configuration, surrogate tree), and hashed in a route manifest committed before any
   research-window bar is read for the test. [Stage E.2a ruling on audit ML-A16 (V5): the surrogate
   step itself writes each surviving rule as machine-readable JSON (features, cut points, sign,
   horizon, cluster, exposures, primary leg, provenance); the route manifest hashes that JSON; the
   catalog-format entry is a rendering of the JSON with no field changed, dropped or rounded.]
Steps 2 to 4 are code, ~~frozen with this design~~ [Stage E.2a ruling on audit ML-A04: frozen by
E.2b's harness manifest before E.ML-buy, M7.8]; the lead does not pick among rules.

**Reasoning.** Short conjunctive rules are what survive distillation in the general-ML literature
(RuleFit, E1-ML-25; E1-ML-24's low-order structure), while feature rankings and effects in
extrapolated regions do not (E1-ML-01's fold-to-fold instability; E1-ML-28's pitfalls), so rules
are shallow and use cut points inside the training data. Model-extraction trees overfit unless
fidelity is checked on new points (E1-ML-26); the block-6 pre-test is that check, on outcomes rather
than on agreement with the model. No source tests distilled futures rules out of sample net of cost
(Q4: no source found), so the conservative defaults are: depth 2, at most 2 rules per cluster, a
cost stress, and a within-training pre-test.

**Alternatives.** RuleFit with a lasso (more rules, a penalty to tune; rejected for trial count);
SHAP-interaction reading by the lead (a free choice; rejected); distilling per exposure (up to 62
rules; rejected); no distillation, testing the model itself (against U6: no model is deployed).

**User decides:** depth 2; at most 2 rules per cluster and 16 in total; the block-6 pre-test.
[V5, 2026-09-25: decided: depth-2 surrogate rules, at most 2 per cluster and 16 in total, and the
block-6 pre-test, as written.]

---

## M6. Trial accounting

**Proposed rule.** [V6, 2026-09-25: accepted by the user.]
- **At the test, each distilled rule is one trial** and adds 1 to the program's cumulative N when
  it is tested (N is 58 before Stage E; the frozen catalog projects 216 after its 158 trials).
- **Training-window accounting, reported beside every rule:** the full search (36 configurations,
  3 horizons included; the surrogate candidates; the pre-test survivors) is counted in the route's
  own training-window ledger, and the training-window DSR of the selected configuration is computed
  at that count, with the effective number of trials estimated as E1-ML-17 (Appendix 3) and
  E1-ML-19 describe. PBO (CSCV) over the 36 configurations' training-window daily P&L series is
  reported. These training-window figures inform; they do not decide anything.
- **Holm family:** the route's rules form their own family. They cannot join a cluster's Tier A:
  Tier A members are tested on the older window, the route's rules on the research window, and one
  Holm family needs one test window. The route is one more family in D5's Bonferroni split: alpha =
  0.05 / (K + 1), where K is the number of clusters with a non-empty Tier A. [Stage E.2a ruling on
  audit ML-A14 (V6): V6 changes frozen D5's split; this is recorded in docs/DECISIONS.md as V6's
  effect on D5 and never edited into the frozen file. D5's K counts every family with a non-empty
  tested set, the route included once it has a tested rule; so when the route tests a rule, every
  family, each cluster's Tier A included, tests at 0.05 / (K + 1), D5's "at most 8" reads "at most
  9", and the program-level family-wise error stays at most 5%.] Holm runs across the
  route's tested rules at that alpha.
- **Edge conditions at the test:** unchanged from D5 and NULL_CRITERIA_E: Holm rejection; the
  composite verdict on the research window; DSR > 0.95 at the cumulative program N; daily t > 3.0;
  PBO < 0.5 on 8 contiguous blocks of the research window. A passing rule is a discussion item for a
  registered holdout-2 read. Nulls follow NULL_CRITERIA_E (UCB95 below eps_X at 80% achieved power,
  per exposure the rule trades). [Stage E.2a ruling on audit ML-A15 (V6, NULL_CRITERIA_E 3): a route
  rule trades every traded exposure of its cluster (each with a D2 vehicle) at that vehicle's q_c;
  its edge series is NULL_CRITERIA_E 3's multi-leg series, the combined net dollars per
  research-window date at those sizes divided by (q_c x tick value) of its primary leg; the primary
  leg is the vehicle of the cluster's F16 lead exposure (K1 Nasdaq-100, K2 10-year, K3 EUR, K4 WTI,
  K5 gold, K6 corn, K7 bitcoin), or, if that exposure has no vehicle, of the cluster's traded
  exposure with the highest 2026 January-August ADV in D1's table, named in the rule's entry. The
  DSR's Sharpe variance is over the route's tested rules' research-window daily Sharpes. Nulls stay
  per exposure, as written.]
- **Source overlap:** a route rule was found on the training window, not on literature whose sample
  overlaps its test window, so it is not labelled source-overlap on that ground.

**Reasoning.** Counting each tested rule once in N and reporting the search beside it follows DSR's
logic (E1-ML-17: a backtest without search accounting is "worthless") while keeping the program's N
tied to what is actually tested out of sample. E1-ML-20 shows DSR and PBO do not detect look-ahead,
so they are not relied on for that (M7 does it by construction). The separate family keeps each
Holm family on one data window; the extra Bonferroni share costs every cluster a little alpha (0.05/9
instead of 0.05/8 with all eight clusters active), which the user may prefer to take from the route
alone.

**Alternatives.** Count the whole search in the program's N (36 + candidates; it would penalize the
hand-written members for a search on data they never use); let route rules join cluster Tier A
families (mixes test windows; rejected); a fixed alpha for the route outside the split (for
example 0.01) instead of 0.05 / (K + 1).

**User decides:** one trial per tested rule; the route as its own family in the Bonferroni split.
[V6, 2026-09-25: decided: one trial per tested rule; the route as its own family at alpha
0.05 / (K + 1).]

---

## M7. Leakage controls

**Proposed rule. ~~E.2~~ E.2b [V8, 2026-09-25] builds and tests all of these before any fit** (the D15.7 set adapted, plus the
window checks).
1. **Feature-timestamp validator:** every feature value carries its availability time; any value
   available after t raises. Canaries: a feature equal to y, and one equal to the next bar's close,
   must be rejected.
2. **Perturbation test:** replacing every bar after t with random values leaves t's features and
   the model's prediction unchanged, for single-product and cross-product (F16) features.
3. **Fold test (CPCV by trade date):** the first five of the training window's six contiguous blocks
   (block 6 is M5's pre-test); combinatorial splits with two test blocks (10 splits); purge every training row whose target window overlaps a validation date; embargo one full
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
   exist) and are written into the route manifest before any fit.] The applied CPCV description in the log (E1-ML-21, 21-day
   purge and embargo on daily data) is the template; the primary purging and CPCV texts could not
   be retrieved (R04, [unverified]), so the rule is stated here in full rather than by citation.
4. **Window test (new):** asserted on the saved row index of every training, tuning,
   normalization and distillation step: no trade date on or after 2024-03-01; none before the
   product's S_X; in particular no research-window date (2025-04-01..2026-06-19), no embargo date, no
   holdout-2 date. The research-window bars are not on disk for the route's process at all during
   training: the training job reads only a training-window bar store built for it, and a canary
   (a planted research-window bar in that store) must make the job refuse. [Stage E.2a note on audit
   ML-A23: the training job also asserts a path allowlist (the training-window store only), tested
   with a planted research-window path.]
5. **Normalization test:** every normalization constant (sigma_X,d, medians, cut points) is a
   trailing statistic of bars before t or a literal; a test perturbs all rows after the training
   window and asserts the fitted model's hash is unchanged.
6. **Model hash chain:** seeds fixed; every fitted model's sha256 and the surrogate trees are
   recorded in the route manifest before the test; the test run refuses on a different hash.
7. **The existing leakage canaries** (tests/test_leakage_canaries.py) run each distilled rule's
   strategy wrapper through the engine, including the cross-product canary (a planted future bar in
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

**Reasoning.** E1-ML-20's leaky oracle (Sharpe 35) passed DSR and PBO, so leakage has to be
prevented by construction and tested directly; statistics will not catch it. E1-ML-14 names the
asynchronous-close look-ahead in cross-asset features, which test 2 covers for F16.

**Alternatives.** Plain walk-forward folds (simpler; fewer training-window paths for PBO); a fixed
purge in minutes instead of full trade dates (weaker for overnight features).

**User decides:** nothing new beyond the partition (M1); the list is the minimum.
[V1, 2026-09-25: the partition is decided; this list stands as written.]

---

## M8. Compute

**Proposed rule.** [V7, 2026-09-25: amended by the user: the LSTM trains on this machine's GPU, the
Windows PC is dropped, and both challengers follow the overnight profile of CLAUDE.md. Struck text
is superseded.]
- **Where:** the gradient-boosted trees on the ThinkPad (CPU). ~~The LSTM on the Windows PC with the
  RTX 2060 Super (8 GB) if the user agrees; otherwise on the ThinkPad CPU with decision times
  sub-sampled to every 60 minutes for the LSTM only, or the LSTM is dropped (M3).~~ [V7, 2026-09-25:
  the LSTM trains on this machine's NVIDIA RTX 3050 Laptop GPU (4 GB of VRAM, found 2026-09-25), on
  the data and decision times of M3 and M4 as written (no sub-sampling). The Windows PC is dropped
  from the route: nothing of the route runs on it and no data is copied to it.]
- **Limits (CLAUDE.md):** ~~at most 8 threads (half the ThinkPad's cores, capped at 8), one heavy job
  at a time across the lead and all workers,~~ [V7, 2026-09-25: the overnight profile of CLAUDE.md
  (added 2026-09-25): at most 14 threads in total across all jobs and at most two heavy jobs at once;
  the combined peak memory estimate of the running jobs under 70% of the memory available just
  before launch, anything larger in chunks; the GPU allowed for model training, one GPU job at a
  time, free VRAM checked with nvidia-smi before launch, batches sized to leave at least 0.5 GB of
  VRAM free;] `nice -n 10` and OPENBLAS_NUM_THREADS=1 outside the
  learner's own thread count, memory checked before each job (rows about 450,000 x 20 float32
  features is under 0.1 GB for the trees; the LSTM's sequences are built in batches, never all in
  memory), resumable (each configuration x fold result appended to a JSONL, skipped on restart),
  and never inside the AiTrader collector window (about 15:30 to 16:00 PT on weekdays).
- **LSTM batch size [V7, 2026-09-25].** E.2b's probe re-plans the LSTM's batch size to leave at
  least 0.5 GB of the RTX 3050's VRAM free. The rule is mechanical and reads no market data: the probe
  runs one forward and backward pass of the largest LSTM configuration (32 hidden units, lookback 72)
  on synthetic inputs of the frozen shapes at batch 512, and reads the card's peak memory in use
  (nvidia-smi, CUDA context included) [Stage E.2a note on audit ML-A20: the peak is
  torch.cuda.max_memory_reserved() plus the process's CUDA context from nvidia-smi's per-process
  figure, both recorded]; while less than 0.5 GB of the 4 GB stays free, the batch size
  is halved (256, then 128, then 64); if 64 still leaves less than 0.5 GB free, the probe stops and
  the case goes to the user. The result is one batch size for all four LSTM configurations; it and
  the probe's memory figures are recorded in the route manifest before any fit. Every other LSTM
  setting of M3 (learning rate, epochs, seed, grid) stays as written.
- **Time per challenger (guesses; ~~E.2~~ E.2b [V7, V8] measures each with a timed probe on one fold
  before the full run and re-plans from the probe):**
  - trees: 24 configurations x (10 CPCV splits + 1 refit) = 264 fits of a few minutes each at 8
    threads: about 7 to 14 hours of CPU in total, run in resumable chunks over several sessions;
  - LSTM: 12 configurations x 11 fits x 8 epochs; ~~on the GPU about 1 to 2 minutes per epoch, so
    about 18 to 35 hours; on the ThinkPad CPU several times that, which is why the CPU fallback
    sub-samples or drops it.~~ [V7, 2026-09-25: on the RTX 3050 Laptop GPU. The draft's 1 to 2
    minutes per epoch was guessed for the Windows PC's desktop RTX 2060 Super; the laptop card's
    speed on this job is unknown until E.2b's probe, so the 1,056 epochs are taken as about 18 to 35
    hours or more, a guess re-planned from the probe. No CPU fallback is planned: the LSTM's data,
    decision times and grid are not reduced to save time without the user's decision.]
- ~~**The Windows PC** is outside this repository's machine rules (CLAUDE.md covers the ThinkPad).
  Using it needs the user's setup (environment, copying the training-window bar store, and bringing
  results back with hashes); no research-window data is ever copied to it.~~ [V7, 2026-09-25: the
  Windows PC is dropped from the route.]

**Reasoning.** The trees fit comfortably on the ThinkPad inside the stability rules; the LSTM does
not at this scale [V7, 2026-09-25: on the CPU; it trains on this machine's GPU]. Every figure here is
a guess until ~~E.2's~~ E.2b's [V8] probe.

**Alternatives.** Fewer CPCV splits (walk-forward with 3 folds: about 5x less compute, fewer paths
for PBO); trees only (removes the GPU question).

**User decides:** whether the Windows PC is used for the LSTM; the compute budget.
[V7, 2026-09-25: decided: the LSTM trains on this machine's RTX 3050 Laptop GPU and the trees on the
CPU, both under the overnight profile; the Windows PC is dropped. V7 sets no compute budget: E.2b's
probe re-plans the time estimates and reports them to the user.]

---

## M9. Session plan and place in the cluster order

**Proposed sequence.** [V8, 2026-09-25: accepted by the user; Stage E.2 is split into E.2a and E.2b.]

| # | Session | What | Needs |
|---|---|---|---|
| ~~1~~ | ~~E.2 (build)~~ | ~~the user's review of this draft; **freeze this design** (hash) before any ML fit and before any research-window bar is read; build the route's pipeline and every M7 test with known answers; the training-window bar store; timed probes for M8~~ | ~~this file reviewed; the harness pieces of D11 the route shares (bars, calendars, costs, rules)~~ |
| 1a | E.2a [V8] | the user's review of this draft (decisions V1 to V9); **freeze this design** (hash) before any ML fit and before any research-window bar is read | this file reviewed |
| 1b | E.2b (build) [V8] | build the route's pipeline and every M7 test with known answers; the training-window bar store's code (filled once the history is bought); timed probes for M8, including the LSTM batch-size probe | the harness pieces of D11 the route shares (bars, calendars, costs, rules; built in E.2a) |
| 2 | E.ML-buy ~~(can be inside E.2)~~ [V8, 2026-09-25: after E.2b] | buy the route's history: the full step 2 range 2019-05..2025-03 of one contract per exposure, holdout-2 chunks sealed on arrival (U4; V1) | funding and a session cap: about $165-190 (M1) [V1: funding pending] |
| 3 | E.ML-train (one or more sessions, resumable) | CPCV selection, refits, surrogate trees, block-6 pre-test, rule write-up; route manifest committed | trees about 7-14 h CPU; LSTM per M8 |
| 4 | E.ML-test (one session) | the frozen rules, once, on the research window; independent Fable check of every number; statements | the research-window bars (bought in E.1) |
| 5 | registered holdout-2 read (D.2-style), only for a rule that passes | as for any member | a registration |

**Place in the cluster order (U3: K2, K4, K5, K3, K6, K7, K1 if needed, K8).** The route's training
reads only the training window, so it can run beside the cluster sessions without touching their
data. The route's test reads the research window, which cluster screening sessions also read; since
the route's rules are frozen by a mechanical procedure (M5), the order does not create leakage. The
proposal: E.ML-buy and E.ML-train run right after E.2, in parallel with K2's screening session
(different windows, one heavy job at a time on the machine); E.ML-test runs once all rules are
frozen, before K8 (whose members read other clusters' products, and which the route's cross-product
rules may overlap). [V8, 2026-09-25: accepted: E.ML-buy and E.ML-train run after E.2b, beside K2's
screening session; E.ML-test runs once all the route's rules are frozen, before K8. V7: the machine
now runs under the overnight profile (at most two heavy jobs at once), not one heavy job at a time.]

**Reasoning.** It keeps the route off the cluster sessions' critical path while guaranteeing that
every route rule is frozen before its test.

**Alternatives.** Run the whole route before K2's screening (cleanest in time order, but delays the
catalog program by the route's purchase and compute); run it after all clusters (no benefit, and
the rules arrive last).

**User decides:** the place in the order; whether E.ML-buy and E.ML-train may start before K2's
screening session ends.
[V8, 2026-09-25: decided: after E.2b and beside K2's screening, so they may start before K2's
screening session ends; the test runs once all the route's rules are frozen, before K8.]

---

## What ~~E.2~~ E.2b [V8] must build for the route, and the data it needs

- **Build:** the training-window bar store (per product, per the start rule, price-path contract per
  M1); the feature pipeline with availability timestamps (M4) and the validator; the net target with
  the D8 cost model; the CPCV splitter with purge and embargo by date (M7.3); the LightGBM and
  PyTorch training jobs with fixed seeds, resumable ledgers and the model hash chain; the surrogate-
  tree and pre-test code (M5, ~~frozen with this design~~ [Stage E.2a ruling on audit ML-A04: frozen
  by E.2b's harness manifest before E.ML-buy, M7.8]); the route manifest; every M7 test with known
  answers; the lightgbm and torch dependencies pinned in uv.lock (neither is there today).
- **Data:** the research window and the mbp-1 sample (bought in E.1, step 1); the training-window
  history (not bought; M1: $131.89-153.95 for 2019-05..2024-02 of one contract per exposure, or
  $164.71-189.31 for the full step 2 range, from E.0's quotes [V1, 2026-09-25: the full step 2 range;
  funding pending]); calendars of scheduled releases with
  timestamps (D10 and the catalog's named releases).

## What the user decides (collected)

1. M1: the partition; funding for the route's history (about $165-190) and its cap; full step 2 range
   or training window only.
2. M2: one pooled model (proposed) or per-cluster models.
3. M3: trees plus one LSTM (proposed), or trees only; the grids (36 configurations in total).
4. M4: horizons {30 min, 120 min, to F}; the features; the 1.5 x cost stress.
5. M5: depth-2 surrogate rules, at most 2 per cluster and 16 in total, with the block-6 pre-test.
6. M6: one trial per tested rule; the route as its own family, alpha 0.05 / (K + 1).
7. M8: the Windows PC for the LSTM, or not.
8. M9: the route's place in the order.

[2026-09-25: all eight decided by the user (docs/DECISIONS.md, V1 to V8): 1 by V1, 2 by V2, 3 by V3,
4 by V4, 5 by V5, 6 by V6, 7 by V7 (this machine's RTX 3050 Laptop GPU for the LSTM; the Windows PC
dropped), 8 by V8.]
