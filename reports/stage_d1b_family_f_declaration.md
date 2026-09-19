# Stage D.1b — Family F declared feature space (Task 2a)

Written 2026-09-18 by the lead (Opus) BEFORE any Family F computation. No MES bar value
was read to write this file: only the column schema (`sim.engine.BAR_COLUMNS`) and the
fold construction (`data.splits`). Its sha256 and write time are logged in progress.md.
The list is CLOSED once Task 2b starts; ideas arising during 2b go to "ideas for a future
round", not into this session's feature space.

## 0. Data discipline (decided now, not after)

- **Discovery window (EDA dates):** research trade dates with index 142..288 in the sorted
  research date list, i.e. the train-union dates that are NOT in fold 0's train window
  (fold 0 train = indices 0..141). Asserted in code to be a subset of
  `screening.train_union_window()`. No test-only date, no holdout date.
- **Why:** Task 2d screens every Family F hypothesis on fold 0's train window first. Because
  discovery never sees fold 0's dates, that first screen is out-of-sample relative to the
  discovery step (disjoint in time: fold 0 is the earlier half). The later 8-fold spread
  overlaps the discovery dates and is reported as such.
- **Exclusions from the EDA dates:** canonical roll-blackout dates (splice day + 2 prior
  sessions; the splice carries a +206..+226-tick basis jump), and `vendor_degraded_day`
  dates (a descriptive data-quality filter; strategies cannot see that field anyway).
- **Returns:** log returns of `close`, in ticks where stated (1 tick = 0.25 pt). A return
  is only formed between bars of the same `trade_date` and `instrument_id`; any 1-minute
  step whose later bar has `gap_before_minutes > 0` is dropped, and any h-minute window
  containing such a step or a missing minute is dropped.
- **Clock:** America/Chicago. RTH = bars opening 08:30..14:59 CT. ETH = trade-date bars
  before 08:30 CT (from the 17:00 CT Globex open of the prior evening). Windows aligned to
  the clock grid (a 30-min bucket starts at :00 or :30).
- **Inference:** every tested statistic gets a stationary day-block bootstrap (resample
  EDA days, mean block 5 days, 2,000 resamples, seed 20260918), a two-sided 95% CI and a
  bootstrap p-value. Multiplicity inside Family F: Benjamini–Hochberg at FDR 10% across
  ALL tested statistics below (M = 57). A second persistence check: sign agreement in at
  least 3 of 4 contiguous, equal-count sub-blocks of the EDA dates.
- **Economic companion:** every directional statistic reports the implied gross edge of
  the naive sign-trading rule it implies (mean of sign(predictor) x forward return, ticks
  per trade), so significance is never read without magnitude.

## 1. Declared features (IDs are what the log and code use)

### F1 — Return autocorrelation at fixed horizons (18 tested)
- **F1.1** Lag-1 autocorrelation of consecutive non-overlapping h-minute returns within
  the same trade date and session segment, h in {1, 5, 15, 30, 60}, RTH and ETH
  separately. 10 statistics.
- **F1.2** Variance ratio VR(h) = Var(h-min return) / (h x Var(1-min return)), h in
  {5, 15, 30, 60}, RTH and ETH separately. 8 statistics.
- *Overlap to check:* h = 1 and h = 5 reversal is family C's region (C-H1 fades 5-min
  returns; C-H3 bar-level CLV).

### F2 — Volatility clustering and regime persistence (12 tested)
- **F2.1** Autocorrelation of |1-min return| at lags {1, 5, 15, 60} minutes within a
  session segment, RTH and ETH separately. 8 statistics (non-directional).
- **F2.2** Lag-1 autocorrelation of daily RTH realized variance (sum of squared 1-min
  returns) across consecutive EDA dates. 1 statistic.
- **F2.3** Leverage asymmetry: correlation between a 30-min RTH bucket return and the next
  bucket's realized volatility (sqrt of summed squared 1-min returns). 1 statistic.
- **F2.4** Lag-1 autocorrelation of consecutive non-overlapping 15-min RTH returns, split
  by the tercile of the realized volatility of the 60 minutes before the pair's first
  return (tercile edges from the pooled EDA sample): top tercile and bottom tercile.
  2 statistics.
- *Overlap to check:* D-H1 (trailing-vol regime gate), D-H3 (range compression).

### F3 — Session-conditional structure not covered by A–E (14 tested + descriptive)
- **F3.1 (descriptive only, not tested, INELIGIBLE):** mean, std, skew, excess kurtosis of
  30-min bucket returns for every bucket of the trade date. Bucket means are pure clock
  seasonality, which cannot clear the drift benchmark in-sample (D.1a); they are shown for
  context and may not seed a hypothesis.
- **F3.2** For each pair of consecutive 30-min RTH buckets (13 buckets 08:30..15:00, 12
  pairs), the cross-day correlation between bucket k's return and bucket k+1's return.
  12 statistics.
- **F3.3** Intraday momentum in the Gao-Han-Li-Zhou / Baltussen et al. form (D.1 items
  A10/A28, carried forward but never screened): correlation of (a) the return from the
  trade date's first bar to 09:00 CT, and (b) the 08:30-09:00 return, each with the
  14:30-15:00 return. 2 statistics. Literature-sourced, flagged as such.

### F4 — Asymmetry around reference levels (7 tested)
Event construction is fixed here so it needs no later judgment.
- **F4.1 RTH open.** Reference = open price of the 08:30 CT bar. Crossing event = a bar
  opening 09:00..14:29 CT whose close is strictly on the other side of the reference from
  the previous bar's close. After a counted event, further events that day are ignored for
  15 minutes. Statistic: mean forward 15-min return (event bar close to close 15 bars
  later) signed in the crossing direction, in ticks. 1 statistic.
- **F4.2 Prior RTH close.** Reference = close of the prior trade date's 14:59 CT bar, same
  instrument_id (skip the day otherwise). Same event and statistic as F4.1, RTH
  08:30..14:29. 1 statistic.
- **F4.3 Gap fill (overlap with D-H4, computed for the novelty check only, INELIGIBLE):**
  gap = 08:30 open minus prior RTH close, in ticks; P(RTH trades back to the prior close
  by 15:00) in each |gap| tercile. 3 statistics.
- **F4.4 Round numbers.** Levels L = multiples of 50 index points. Approach event: previous
  bar close < L <= current bar high (from below) or previous close > L >= current low
  (from above), any session, 30-min refractory per level. Statistic: mean forward 15-min
  return measured from L, signed so positive = continuation through L, in ticks. Tested:
  the difference versus the same statistic at control levels (multiples of 50 offset by
  +12.5 and +37.5 points), for (a) multiples of 50 and (b) multiples of 100. 2 statistics.

### F5 — Volume/range relationships not tested by family D (5 tested)
- **F5.1** Relative volume of a 30-min RTH bucket = its volume / mean volume of the same
  bucket over the previous 20 eligible EDA dates (trailing only; the first 20 EDA dates
  have none and are dropped). Lag-1 correlation of consecutive bucket returns when the
  first bucket is in the top relative-volume tercile, and in the bottom tercile.
  2 statistics.
- **F5.2** Trend efficiency of a 30-min RTH bucket = |bucket return| / (bucket high - low).
  Lag-1 correlation of consecutive bucket returns when the first bucket is in the top
  efficiency tercile, and in the bottom tercile. 2 statistics.
- **F5.3** Range-per-volume residual: regress log(range) on log(volume) across 30-min RTH
  buckets (pooled EDA fit). Correlation of residual x sign(bucket return) with the next
  bucket's return. 1 statistic.
- *Overlap to check:* C-H2 (post-spike exhaustion, volume/range spike), D-H3.

### F6 — Addition beyond the starting list: overnight-range position (1 tested)
- **F6.1** Position of the 08:30 CT open within the ETH session's high-low range (0 = at
  the ETH low, 1 = at the ETH high), correlated with the 08:30-09:30 return. 1 statistic.
- *Why added:* the overnight range is a data-native reference level that no family used
  (B used the opening range and the prior day's high/low; D-H4 used the gap to the prior
  close). It is added now, before computation, not after seeing anything.

**Tested-statistic count M = 18 + 12 + 14 + 7 + 5 + 1 = 57.** (F4.3's 3 are tested for the
novelty check but ineligible; F3.1 is descriptive and not counted.)

## 2. Selection rule for Task 2c (fixed now)

A stylized fact may be formalized as a Family F hypothesis only if ALL hold:
1. It is directional or conditional (tells a strategy which side to take). F2.1, F2.2,
   F3.1 and F4.3 are ineligible by declaration; F1.2 and F2.3 are eligible only through
   a directional reading.
2. It survives BH at FDR 10% across the M = 57 statistics.
3. Its sign agrees in at least 3 of the 4 EDA sub-blocks.
4. Its implied gross edge is at least 2.11 ticks per trade (the $2.64 modelled market
   round-turn cost), or at least 0.98 ticks ($1.22 commission) only if the hypothesis is
   specified from the start with passive entry and exit, and says so.
5. It is not the mechanism of an already-screened A–E trial on the same conditioning
   variable (a C-H1/C-H3/D-H4 look-alike is logged as a replication, not a discovery).

Eligible facts are ranked by |t| x implied edge. At most 6 are formalized; the rest are
logged with reasons. Parameters of a formalized hypothesis come directly from the declared
construction (horizon, bucket, tercile edges computed on EDA dates and frozen); no tuning.
If nothing is eligible, zero Family F hypotheses are formalized, and that is the result.
