# Stage D.1d — Task 2: declared coarser-timeframe feature space and re-tests

Written 2026-09-21 by the lead (Opus) BEFORE any D.1d computation code existed.

**What was consulted to write it:**
- Task 1's audit (`reports/stage_d1d_horizon_audit.md`);
- the bar schema (`sim.engine.BAR_COLUMNS`, `strategy.interface.Bar`);
- the session and flatten rules (`data.session`, `rules.xfa_rules.flatten_time_ct`,
  `no_new_positions_time_ct`);
- the fold construction (`data.splits`);
- Family F's code, for the inference this file reuses.

No MES bar value was read to write it. Its sha256 and write time are logged in progress.md
and embedded in every output JSON's meta.

**The lists are closed.**
- Nothing may be added to the re-test list (§2) or the stylized-fact list (§3) after this
  file is hashed.
- An idea that arises during computation goes to "ideas for a future round".

## 0. Data discipline

- **Stylized facts** are computed on Family F's EDA dates, unchanged: research trade-date
  indices 142..288, the train-union dates NOT in fold 0's train window, minus
  roll-blackout and `vendor_degraded_day` dates. That is 139 dates.
  - They are rebuilt with `strategy.research.f_data_native._stylized_facts.resolve_eda_dates`,
    which asserts subset-of-train-union and disjoint-from-fold-0.
- **Stated plainly: these dates are not fresh.**
  - Family F used them for 57 statistics.
  - All 24 trials ran on the 289-day train union that contains them.
  - The discipline preserved is the same as F's: any formalized hypothesis is screened
    first on fold 0's train window, which discovery never saw.
- **Re-tests (§2) are sourced hypotheses, not discoveries.** Each runs through
  `screening.screen_candidate` on `fold_train_window(0)` (the D.1 screening window) and
  on `train_union_window()` (the accounting window). Fold 1–7 train windows are run only
  if fold 0's composite verdict passes.

## 1. Resampling rule (the only way D.1d builds a coarser bar)

Timeframes `tf ∈ {5, 15, 30, 60}` minutes. All clock times are America/Chicago, and bars
are identified by their OPEN minute.

- **R1. Source.** The 1-minute research bars already on disk, through
  `data.research_bars.load_research_bars`: for statistics directly, for screening through
  the runner. No new data, no Databento call.
- **R2. Segments of trade date D.**
  - **ETH** = `[17:00 of the evening that opens D, min(08:30, N_D))`.
  - **RTH** = `[08:30, min(15:00, N_D))`.
  - `N_D = rules.xfa_rules.no_new_positions_time_ct(early_close_D)` is 15:08 on a normal
    day, and 17 minutes before a CME early close (the flatten is 15 minutes before it,
    and no new positions 2 minutes earlier still).
  - `early_close_D` is the calendar `early_halt_ct` carried on D's bars.
  - The minutes from the RTH segment end to the next 17:00 open belong to NO coarse bar.
    That covers 15:00–15:10 and the whole 15:10 flatten → 16:00 halt → 17:00 reopen gap.
    A segment with a non-positive length (e.g. RTH on Good Friday) does not exist.
- **R3. Slots.** Within segment S, slot `j` covers `[start_S + j·tf, start_S + (j+1)·tf)`.
  - A slot exists only if it ends at or before the segment's end. A slot that would cross
    08:30, the RTH end, the no-new-positions time, an early halt or the daily halt is
    **dropped, never truncated and never extended**.
  - On a normal day, 5, 15 and 30 tile both segments exactly.
  - At 60 minutes, the ETH stub 08:00–08:30 and the RTH stub 14:30–15:00 are dropped:
    60-min ETH has 15 slots and 60-min RTH has 6.
- **R4. Aggregation.** A slot's coarse bar is built from the 1-minute bars of trade date D
  whose open falls in the slot:
  - open = first bar's open;
  - high = max high;
  - low = min low;
  - close = last bar's close;
  - volume = sum;
  - `n_minutes` = number of bars present.
  - A slot with no 1-minute bar has no coarse bar.
  - A slot whose bars carry two `instrument_id`s is dropped (possible only on a splice
    day, which is a roll-blackout day).
  - Missing minutes inside a slot (no trade that minute) are NOT a reason to drop it: a
    live bar builder aggregates the trades that happened.
  - The share of coarse bars with any missing minute is reported descriptively, per
    timeframe and segment.
- **R5. Adjacency.** Slot `j` and the next slot of the same trade date are adjacent if the
  first ends where the second starts.
  - Within a segment, `j` and `j+1` are always adjacent.
  - The last ETH slot and RTH slot 0 are adjacent only if the ETH slot ends at 08:30
    (tf 5, 15, 30 on a normal day; never at 60).
  - Nothing is adjacent across trade dates.
- **R6. Completion, for strategies.** A coarse bar completes at the decision time of the
  1-minute bar that opens in its last minute (`slot end − 1 min`), which is exactly the
  slot's end.
  - If that minute has no bar, the coarse bar completes at the decision time of the next
    1-minute bar the strategy receives, and that bar is then assigned to its own slot.
  - Decisions on such slots are 1+ minutes late. That is conservative; it is declared,
    not corrected.
  - A market order placed on completion fills at the next 1-minute open, which is the next
    coarse bar's open.
- **R7. Nothing spans a boundary.**
  - No coarse bar, return or forward window crosses a trade date, the daily halt, the
    flatten or the no-new-positions time.
  - Every position a D.1d strategy opens is closed by its own exit at or before
    `min(15:00, N_D)`. The engine's 15:10 forced flatten, MLL and roll blackout remain in
    force regardless (they are the runner's, not the strategy's).

A single shared module implements R1–R7. It is used both by the statistics (vectorised)
and by every D.1d strategy (incrementally, bar by bar), so the two cannot diverge.

## 2. Re-tests: the exact Task 1 flagged list (7 trials), restated at the source's horizon

**Rule for what changes.** A re-test changes only horizon-bearing parameters:
- bar size;
- the length of an opening range, baseline or estimator window;
- hold length.

Each of these takes **the source's value where the source states one**, and otherwise the
trial's own value re-expressed on the coarser grid. Everything else stays exactly as the
original trial had it:
- sides and direction;
- price, ratio and z thresholds;
- tick buffers;
- the base entry of a gate or sizing test;
- one entry per session.

All re-tests use market orders and 1 micro, except D-H2's sizing. All use the
`tf = 5` grid, since every flag maps to 5-minute bars (Task 1).

| ID | Original | Restatement at the source's horizon |
|---|---|---|
| **RT1** | B-H1 ORB (hold 5) | 5-min grid. OR = high/low of RTH slots 0–5 (08:30–09:00 CT), Mesfin's "first six five-minute bars" (the original used OR15). Trigger: the first RTH 5-min bar at slot ≥ 6 whose close ≥ OR high + 4 ticks (long) or ≤ OR low − 4 ticks (short); at most one entry per day. Entry on completion. **Hold 1 bar** (bar+1): exit on completion of the next 5-min bar. |
| **RT2** | B-H1 ORB (hold 75) | As RT1, **hold 15 bars** (bar+15 = 75 min), exiting earlier only if the RTH segment ends first. |
| **RT3** | B-H3 breakout leg | 5-min grid. OR = RTH slots 0–5 (the original's OR30 already matched). Same trigger and ± 4 ticks. Enter in the break direction. **Hold 6 bars** (30 min, the original's hold; the source states none for this comparison). |
| **RT4** | B-H3 fade leg | As RT3, entering **against** the break direction. |
| **RT5** | C-H2 post-spike exhaustion fade | 5-min grid, over the trade date's ETH-then-RTH slot sequence. **Baseline = the previous 20 coarse bars of the same trade date** (Mesfin §4.2's rolling 20-bar average; the original used 60 one-minute bars), reset each trade date, with no trigger until 20 exist. Trigger: volume z > 3.0 OR range / mean range > 3.0 (the original thresholds; population std, as the original). Fade the bar's direction; close == open means no trade. Flat only. **Hold 1 bar** (bar+1, where the source's reversal was measured; the original held 2 one-minute bars). An entry must be able to complete its hold before the RTH segment end. The ETH → RTH hand-off at 08:30 is adjacent on this grid and may be held across. |
| **RT6** | D-H1 trailing-vol regime gate | Vol estimator moved from 1-minute to **daily** observations. `m_d` = the mean squared 5-min close-to-close log return over adjacent slot pairs of trade date d (R5). `s²` = EWMA over trade dates with the original λ = 0.94 (half-life ≈ 11 trade dates, "today's state"), seeded with the first day's `m`; `V_d = sqrt(s²)` uses dates strictly before d. The original's percentile rank vs the trailing 60 `V` values, with ≥ 30 required, and its low-tercile (≤ 1/3) gate are unchanged. The base entry is unchanged: long 1 micro at 1-minute bar index 60 of the trade date, held 30 one-minute bars. |
| **RT7** | D-H2 inverse-vol sizing | Same daily `V_d` as RT6 (per-5-min σ, so Carver's "last month or so" at λ = 0.94). Size = round(75 / risk$) clipped to [1, 5], with `risk$ = close × V_d × sqrt(30/5) / 0.25 × $1.25`: the original formula, with the random-walk scaling re-expressed per 5-minute return. Warm-up: 20 prior trade dates of `m` (replaces 200 one-minute bars). The base entry is unchanged: long at 1-minute bar index 60, every day, held 30 one-minute bars. |

**Pre-registered for every RT** (the D.1b C-H4 template):
- **SUPPORT** needs all of:
  - the fold-0 composite `verdict` is "pass": robust zero-edge AND both drift sub-checks;
  - at least 30 trips;
  - the traded sign matches the mechanism (breakout legs profit in the break direction,
    fades profit against it, D-H1's gate raises R relative to its ungated base);
  - then a pass that does not swing to fail on most of folds 1–7.
- **REFUTE:** the composite fails on fold 0, OR fold-0 net ≤ $0.

**Resolution-effect read (the question this session asks, descriptive only).** Each RT is
compared with its original on the same windows, by net per trip, p, R and gross per trip:
- "Resolution understated the effect" is **supported for that trial** only if the RT
  passes the composite where the original failed.
- An improvement without a pass is reported as a direction of change, not as support.
- The originals' fold-0 and train-union figures come from `reports/stage_d1_accounting.json`.

## 3. Declared coarser-timeframe stylized facts (Family G)

Every G statistic is an **event statistic**:
- **Event:** a completed coarse bar `j` at which a condition holds, with a direction
  `d ∈ {+1, −1}`.
- **Forward move:** `F_j = (close_{j+1} − close_j) / 0.25` ticks, the next slot's close
  minus the event close. It is defined only if slot `j+1` exists and is present **in the
  same segment** (no ETH→RTH forward windows for G).
- **Statistic:** `mean(d · F)` over all events on the EDA dates, in ticks. This is the
  gross ticks per trade of trading `d` from the event close to the next close, so
  **statistic = implied gross edge**, and its sign says whether the fact is continuation
  (> 0) or reversal (< 0).
- **G3 is the one exception:** its forward window runs to the RTH segment end.

**Trailing same-slot baselines (G1, G4)** use the previous 20 EDA dates, averaging the
measure over those on which the same slot index is present:
- at least 10 such observations are required;
- the first 20 EDA dates are warm-up and dropped (Family F's F5.1 convention);
- the relative measure is the value divided by that baseline, and is undefined if the
  baseline is 0.

**Top-quintile thresholds (Q80)** are the 80th percentile of the relative measure, pooled
over all EDA observations of that (fact, segment, tf). They are computed once and FROZEN
across bootstrap resamples, sub-blocks and any later screen.

| Fact | Segments | Event and direction |
|---|---|---|
| **G1 large-body follow-through** | RTH, ETH | body = close − open of slot j; rel = \|body\| / trailing same-slot mean \|body\|. Event if rel ≥ Q80 and body ≠ 0; d = sign(body). |
| **G2 session-extreme breakout** | RTH, ETH | For slot j that is not the segment's first present slot: event up if close_j > the max high of the segment's earlier present slots (d = +1); down if close_j < their min low (d = −1). |
| **G3 opening-range breakout, hold to RTH end** | RTH | OR = high/low of RTH slot 0 (the first tf minutes), which must be present. Event = the first RTH slot j ≥ 1 whose close > OR high (d = +1) or < OR low (d = −1); at most one event per day. Forward = (P_end − close_j)/0.25, where P_end = the close of the last 1-minute bar opening before the RTH segment end. Events on a slot that ends at the RTH segment end are excluded (no remaining window). |
| **G4 VWAP-deviation continuation/reversion** | RTH | VWAP_j = Σ(typical × volume) / Σ volume over RTH 1-minute bars from 08:30 through slot j's end, with typical = (H+L+C)/3 of each 1-minute bar. Dev_j = (close_j − VWAP_j)/0.25; rel = \|Dev\| / trailing same-slot mean \|Dev\|. Event if rel ≥ Q80 and Dev ≠ 0; d = sign(Dev). Negative statistic = reversion to VWAP. |
| **G5 overnight-range break** | RTH | ETH high/low = the max high / min low of trade date D's 1-minute bars in the ETH segment, which must have at least one bar. Event up = the first RTH slot whose close > ETH high (d = +1); event down = the first RTH slot whose close < ETH low (d = −1). Up to 2 events per day. |

**Counting the tested statistics:**
- G1: 2 segments × 4 timeframes = 8.
- G2: 2 × 4 = 8.
- G3: 4.
- G4: 4.
- G5: 4.
- **M = 28 in total.** IDs are `G<k>.<SEG>.<tf>`, e.g. `G2.ETH.15`.

**G0 (descriptive only; not tested, not in M, not eligible).** The lag-1 autocorrelation of
adjacent coarse-bar close-to-close returns within a segment, RTH and ETH, per tf, printed
beside Family F's F1.1 at h = tf.
- **Why not tested:** F1.1 already measured the plain bar-to-bar momentum/reversion of
  clock-aligned h-minute returns at h = 5, 15, 30, 60 on these same dates, and it failed
  F's selection rule at every h. Re-testing it would double-count a known null.
- **What G0 is for:** a continuity check on the resampler. It should agree closely with
  F1.1, differing only through R4's missing-minute rule versus F's.

**Overlap with the re-tests (counted in M, ineligible for formalization):**
- **G1.RTH.5 and G1.ETH.5:** an extreme 5-min bar → the next bar is RT5's mechanism on RT5's
  grid.
- **G3.RTH.5:** an ORB on 5-min bars is RT1–RT4's mechanism on their grid.
- G3 at 15/30/60 is eligible: that is the ORB mechanism at a resolution no trial has
  tested, which is this sweep's purpose.

## 4. Inference (reused from D.1b, applied within this session only)

- **Per statistic:** `strategy.research.f_data_native._stylized_facts.compute_result` is
  imported and called as is. That gives:
  - a stationary day-block bootstrap: seed 20260918, 2,000 resamples, mean block 5 days;
  - a percentile 95% CI;
  - a two-sided bootstrap p against null 0;
  - sign agreement in 4 contiguous equal-count sub-blocks of the 139 EDA dates
    (35/35/35/34).
- **Days resampled:** the dates on which the statistic is defined (for G1/G4, EDA dates
  21–139).
- **|t| for ranking:** estimate / SD of the same 2,000 bootstrap replicates.
- **Multiplicity:** Benjamini–Hochberg at FDR 10% across **this session's M = 28 only**. It
  is not pooled with Family F's 57.
- **Workstreams:** each timeframe computes its 7 statistics separately. BH runs once over
  the merged 28.

## 5. Selection rule and cap (fixed now)

A G statistic is formalized only if ALL of the following hold:
1. It is eligible: not G0, and not G1.RTH.5, G1.ETH.5 or G3.RTH.5.
2. It is BH-significant at FDR 10% across M = 28.
3. Its sign agrees in ≥ 3 of 4 EDA sub-blocks.
4. **|statistic| ≥ 2.11 ticks per trade:** the $2.64 modelled market round turn at $1.25
   per tick.
   - **This bar does not change with the timeframe.** Cost is per round trip. A 60-minute
     trade pays the same 2.11 ticks as a 5-minute one. Fewer trades per day at coarse
     resolution cost statistical power, not cost per trade.
   - The 0.98-tick passive bar ($1.22 commission) is **not available**: every G template
     below is a market-order template, fixed now, so a fact between 0.98 and 2.11 ticks
     is not formalized.
5. It has at least 30 events on the EDA dates.

Qualifiers are ranked by |t| × |statistic|. **At most 8 are formalized, across all four
timeframes combined.** The rest are logged with reasons. If none qualifies, zero G
hypotheses are formalized, and that is the result.

**Formalization template** (mechanical; no tuning):
- **Traded side:** `sign(statistic) · d`, i.e. continuation if the statistic is positive,
  fade if negative.
- **Entry:** market, on completion of the event bar (R6).
- **Exit:**
  - G1, G2, G4, G5: market on completion of the next coarse bar.
  - G3: at the RTH segment end, via a market exit decided on the last 1-minute bar before
    it.
- **Consecutive events (next-bar templates):**
  - a same-direction event on the bar being held keeps the position (no extra round trip);
  - an opposite event reverses it;
  - no event exits.
- **Size:** 1 micro.
- **Thresholds and baselines:** Q80 is the frozen EDA value. Trailing same-slot baselines
  are computed live from the strategy's own history, with its window's first 20 trade
  dates as warm-up.
- **Screening:**
  - `screen_candidate` on `fold_train_window(0)`, which is out-of-sample relative to
    discovery;
  - folds 1–7 only if fold 0 passes;
  - `train_union_window()` for the accounting.
- **Pre-registered:**
  - SUPPORT = fold-0 composite pass, ≥ 30 trips, sign as discovered, then fold stability;
  - REFUTE = composite fail or net ≤ $0.

## 6. Accounting (Task 4)

- **N:** 24 + 7 re-tests + k formalized G hypotheses (0 ≤ k ≤ 8).
- **Recomputed cumulatively** exactly as D.1b did, extending `_d1b_accounting.py`'s
  method:
  - DSR at N (Sharpe variance across all N);
  - Harvey/Liu/Zhu t > 3;
  - CSCV PBO over 8 contiguous 36-day blocks of the train union.
- **Continuity:** the prior 24 trials must reproduce D.1b's net P&L to the cent and their
  daily Sharpe to 1e-6.
- **Contrast:** this session's trials alone.
- **Sensitivity:** N widened by Family F's 57 and this session's 28 EDA statistics.
