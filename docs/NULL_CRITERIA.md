# MES null criteria

STATUS: FROZEN (Stage D.1e, lead, hashed 2026-09-22T08:50:46Z, second after
reports/stage_d1f_confirmation_list.md, whose sha256 section 1 embeds). After
hashing this file does not change; a later stage that needs different criteria issues a
new version under a new name and says why. Every later MES stage (D.1f, D.1g, D.2) is
judged against this document, not against a paraphrase of it.

Written before any bar of the extended MES history was bought or read. Values marked
[FILLED BEFORE HASHING] are computed in Stage D.1e from existing data only.

## 1. The null statement

The claim the program is entitled to make if D.1f's confirmation comes out null for a
class, and nothing more:

> For MES intraday strategies in class {C}, tested on the pre-registered confirmation window
> (trade dates S to 2024-02-29, S fixed by the start rule in section 4): the trials executed
> through the engine with market orders at the modelled retail cost (the Stage A.1 cost
> model: $1.22 commission per round turn plus the time-of-day slippage table, about 2.11
> ticks per round turn) at their coded contract size (1 micro for the 29 fixed-size trials,
> 1 to 5 by rule for D-H2 and RT7, 2 micros for Family H; C-H4, at 1 micro, is section
> 1.1's), the event statistics
> charged the flat modelled round turn of 2.11 ticks per event, all flat by the XFA cutoff:
> for every member of the class, a net edge of at least epsilon = 34 net ticks per micro per
> day ($85.00 per day at 2 micros, the smallest edge that funds the Topstep XFA funnel under
> the Stage B model of the 2026 rules and fee schedule at 2 micros) is rejected at one-sided
> 95% (the upper confidence bound on mean net daily P&L per micro is below epsilon), with
> achieved null power of at least 80%. Per-trade resolution of the class on this window:
> epsilon per trade at the class's confirmation-window frequency [value], least active
> member [name, count], largest per-trade upper bound in the class [value]; [label "null by
> inactivity" where section 7 requires it]. Members and their definitions:
> reports/stage_d1f_confirmation_list.md, sha256 c19cbac191c497a10b5cc756e96510999f13f27c4ac1aa72593aeabf1125147c.

The statement is made per class (C1 to C5 and C7 by D.1f; C6 by D.1g), never for "MES".
A class with any inconclusive member gets no statement.

### 1.1 The C6 variant (Stage D.1g, passive execution)
> For MES short-horizon reversal executed with resting limit orders, filled by the
> queue-position fill model declared and hashed in Stage D.1g from MBO data, at commission
> only (the passive cost bar, 0.98 ticks per round turn), at its coded 1 micro, compared per
> micro with the 2-micro bar as in section 1 (R-1), flat by the
> XFA cutoff, on the N_C6 pre-declared full trade dates (17:00 CT to 16:00 CT books, since
> C-H4 rests orders in every session): for C-H4, a net edge of at least epsilon net ticks
> per micro per day is rejected at one-sided 95% with at least 80% achieved null power.
> The fill model is specified and hashed before the MBO purchase, and any parameter it takes
> from book data is estimated on declared days outside the evaluation dates.

The C6 epsilon is the same daily figure (the funnel's economics do not depend on how a
fill happened); only the gross-equivalent differs (epsilon + 0.98 ticks per trade instead
of epsilon + 2.11 per trade). C-H4's result under the trade-through model in D.1f is a
lower bound (pessimistic fills) and does not establish the C6 null.

## 2. Epsilon: the economic threshold, with its derivation

### 2.1 Where it comes from
Epsilon is set by the program's own economics, the Stage B power gate (funnel/power_gate.py,
reports/power_gate.json, 8,000 simulated 12-month careers per cell, 2 micros), not by
what any sample can resolve. The gate passes a per-trade quality (win probability p,
win/loss ratio R, T round turns per day) when the resulting funnel income beats the most
favourable zero-edge trader's 80th percentile with 80% power (robust verdict, the
program's composite bar since Stage D.1a). Each cell's expected gross edge per trade is
E|m_T| x (p sqrt(R) - (1-p)/sqrt(R)) ticks, where E|m_T| is the mean absolute RTH move of
a 1/T-session segment measured on the research bars (144.27 ticks at T=1, 97.90 at T=2,
65.71 at T=4, 44.43 at T=8). Net edge per trade = gross minus the modelled round-turn cost at that T
(2.111 ticks at T=1, 2.084 at T=2, 2.073 at T=4, 2.064 at T=8). Net edge per day at 2 micros = net per
trade x T x 2 x $1.25.

### 2.2 The boundary, and why it is a daily figure
Tabulated in reports/stage_d1e_power_gate_cells.json (sha256 433a3ea6361cffaa9544e56e3952d047d067d1a788df3706eca21e23770f3acb)
from reports/power_gate.json (sha256 e57088247881c184a411344d6b1b696a782987eb92ef3a4328e6b6f39315c40c)
and refined in reports/stage_d1e_gate_extension.json (final, 100 rows, sha256
d569e261f0eb9297aa7af2c78fb09b65e113adb6c3f9009b2d6fa94867d06858) (Task 2). On the grid, the robust boundary lies
between a net $105 and $122 per day at T=1, $111 and $140 at T=2, and $72 and $111 at
T=4 (standard path), and slightly lower on the consistency path. Read per trade the
boundary falls with T (about 42 to 49 net ticks per trade at T=1, 22 to 28 at T=2, 7 to
11 at T=4); read per day it is roughly constant, because the funnel's outcome depends on
the daily P&L distribution and the daily distribution's scale barely changes with how the
session is cut. Epsilon is therefore fixed as a daily figure and translated per member:

- epsilon_day = 34 net ticks per micro per day ($85.00 per day at 2 micros) is FINAL for
  this list. It was derived once, from the two pinned files above: 220 cells, the 120 grid
  cells of reports/power_gate.json and the 100 extension rows at T = 1, 2, 4, 8 and 16 on
  both payout paths and T = 32 on the standard path (66 pass, 30 fail, 4 marginal; one T = 32
  cell passes, at $188.50 a day). Rule: epsilon_day = floor( min over every cell whose
  robust_c80_verdict == "pass" of net_edge_usd_per_day_at_2_micros / $2.50 ), the field as
  tabulated in power_gate_cells.json for the 120 grid cells and as stored in the extension
  file (NEW-10). "Pass" means
  Monte Carlo power minus 1.96 x its standard error >= 0.80 (power_gate.json's verdict_rule);
  "marginal" cells (point estimate >= 0.80, lower bound below) are excluded. The binding cell
  is the grid's consistency path, T = 2, p = 0.60, R = 1.00: 17.496 net ticks per trade x 2 x
  $2.50 = $87.48 a day, robust power 0.812 with lower bound 0.804, so 34.99, floored to 34.
  The nearest excluded cell is marginal (consistency T = 4, p = 0.58, R = 1.00, $84.41, power
  0.804, lower bound 0.796); it would have given 33. No recomputation, re-simulation,
  re-seeding or extension of the cell set changes epsilon for this list; a different epsilon
  needs a new list under a new name. Rounding down and taking the minimum over paths and T
  are both in the conservative direction for a null claim: a smaller epsilon makes the null
  harder to establish and covers every edge that could possibly pass the gate.
- For a member trading r times per window day, the per-trade equivalent is
  epsilon_day / r ticks per micro per trade, reported for readability. The operative test
  is on the daily series (confirmation list, section 3).

### 2.3 Epsilon per class (per-trade translation at the class's typical frequency)
| Class | Typical trades per day (trial members only: median on the train union; C7: median projected firing fraction) | epsilon per trade (net ticks per micro) | Market cost bar | Passive cost bar | Gross-equivalent per trade at market cost |
|---|---|---|---|---|---|
| C1 | 0.938 | 36.26 | 2.11 | 0.98 | 38.37 |
| C2 | 0.945 | 35.99 | 2.11 | 0.98 | 38.10 |
| C3 | 36.151 | 0.94 | 2.11 | 0.98 | 3.05 |
| C4 | 0.676 | 50.26 | 2.11 | 0.98 | 52.37 |
| C5 | 0.097 | 350.93 | 2.11 | 0.98 | 353.04 |
| C6 | 92.467 | 0.37 | 2.11 | 0.98 | 2.48 |
| C7 | 0.263 | 129.52 | 2.11 | 0.98 | 131.63 |

Typical frequency is the median trades per day of the class's trial members on the 289-day
train union (C7: the median projected firing fraction). The per-trade figure is a translation
for reading; the operative test is on the daily series (section 3).

### 2.4 What epsilon does and does not mean
- It is the smallest edge that would pay in the Topstep funnel at the program's headline
  size of 2 micros with the current fee schedule and the robust null. It is large for
  low-frequency members because a strategy that trades once a day must earn about a
  session's worth of typical movement in edge to fund a Combine; it is small for
  high-frequency members because the same daily figure is spread over many trades.
- It is NOT the cost bar. A member can have a real, positive net edge below epsilon; the
  null statement says only that no member's edge is large enough to matter for this
  program at 2 micros. The confirmation report therefore also states, descriptively, the
  largest upper bound found per class in ticks per trade, so the reader sees what the
  data did resolve.
- Sizing scope: at a larger size the same daily dollar bar corresponds to a smaller edge
  per micro (at 10 micros, one fifth of epsilon per micro). The null is therefore
  scoped to the 2-micro headline. A claim about larger sizes needs the power gate re-run
  at that size (compute only), a new epsilon, and a new confirmation list.
- If epsilon had come out too small for any feasible sample to resolve, this document
  would say so and the program would claim only the descriptive bound. The opposite is the
  case here (section 5): the economic null is cheap to establish, and the question the
  data cannot settle for most classes is the cost-bar-scale structural one.

## 3. The tests (definitions live in the confirmation list; restated in one paragraph)
Per member, on the confirmation window: the daily net series in ticks per micro per day;
theta_hat = its mean; stationary block bootstrap (mean block 5, 10,000 resamples, seed
20260921) for the one-sided 95% upper bound UCB95 and SE_boot. Edge claims: Holm over the
58 Tier A one-sided p-values at family-wise 5%, then the runner's composite verdict
(robust gate plus both drift sub-checks), then DSR > 0.95 at N = 58 (N = 59 for D.1g's
queue-model C-H4, list 3.5), daily t > 3.0 and CSCV PBO < 0.5 (NEW-3). Null per class: every Tier A and Tier B member has UCB95 < epsilon_day and
achieved null power Phi(epsilon_day / SE_boot - 1.645) >= 0.80. Otherwise inconclusive.

## 4. Data-quality rules for the older history (fixed now, applied later, never revised)

### 4.1 Start rule
MES listed in May 2019 and traded thinly at first. The confirmation window starts at S,
computed in D.1f by this rule before any statistic is run, and logged with every input:
- V_ref: for each of the 14 calendar months 2025-04 through 2026-05 (the months wholly
  inside the current research slice), the median over that month's RTH one-minute bars
  PRESENT in the research parquet as it is (CT clock time 08:30 to 14:59; a clock minute
  with no bar contributes nothing; every trade date of the month, with no exclusion of
  roll-blackout or vendor-degraded dates) of the bar's volume; V_ref is the median of those
  14 monthly medians. This is computed from the research parquet already on disk and is
  fixed by this rule, not by a number written here.
- For each calendar month M of the extension from 2019-05, the first month with bars,
  through 2024-02, V_M = the same monthly median over the RTH bars present in the
  confirmation parquet after step 4's drop of dates after 2024-02-29, every trade date of
  the month, no exclusions.
- S = the first trade date with bars of the earliest month M* such that V_M >= 0.25 x V_ref
  for M* and for every later month through 2024-02 (if M* = 2019-05, S = 2019-05-06). If no
  month qualifies, the confirmation window is empty and D.1f stops with that finding (D-1).
- Sensitivity, descriptive only: the dates the same rule yields at 0.15 and 0.40 are
  reported; 0.25 binds. Why 0.25: the cost model's slippage table was calibrated at sizes
  up to 50 micros on 2026 depth; at a quarter of 2025-26 activity a 2-micro market order
  is still small against typical top-of-book depth, while a lower fraction admits the
  launch months in which MES was often two ticks wide. The fraction is a judgment made
  here; it is not tuned to any result because no result exists.

### 4.2 Roll, degraded-day and calendar handling
Identical to the current pipeline: MES.v.0 volume-ranked continuous series; roll
boundaries from symbology.resolve, never inferred from prices; roll blackout = the splice
trade date plus the two preceding sessions (screening.runner.canonical_engine_config);
vendor_degraded_day from metadata.get_dataset_condition, handled as the confirmation
list's section 1.3 says: trials trade through degraded days with the flag hidden from the
strategy and the day's P&L counted, event statistics exclude every trade date with any
flagged bar, the two differ by design and stay so, and the degraded-date list is fetched
once, frozen and compared with the eight dates known at declaration (N-3); CME holidays and early closes
from data/cme_calendar.py extended to 2019-2024 from CME's published schedules before any
run (each entry cites its source); flatten times unchanged. Bars of a trade date whose
session is split across a sealed and an unsealed chunk are dropped, never partially used.

### 4.3 The cost model and its known bias
The cost model stays as calibrated on the 2026-07-15 and 2026-07-31 books (both inside
the sealed holdout) and the $1.22 commission. Early-era MES spreads were likely wider and
depth thinner, so modelled costs UNDERSTATE real costs on the older history. That bias
favours finding an edge, which makes it conservative for a null claim: a member that
shows no edge at understated cost would show less at true cost. It is NOT conservative
for a positive finding: any member that passes confirmation on the older history needs a
cost re-check against period-appropriate spread evidence before it is discussed for
Stage D.2, and that re-check is part of the D.2 discussion item, not a reason to re-run. Two
mechanical facts of the same model (D-3): 2-micro orders (Family H) are costed at the
size-5 slippage bucket, the smallest calibrated size at or above 2, which is slightly
above the size-1 bucket the 1-micro trials pay (conservative for an edge claim, marginally
not for the null); and the event statistics ignore the time-of-day slippage table and pay a
flat 2.11 ticks per event, the RTH/ETH difference being about 0.05 ticks per round turn.
The per-micro daily series of a 1-micro trial is compared with a bar derived at 2 micros on
the assumption that per-micro costs do not rise with size at these sizes; the size-5 bucket
says they rise slightly, so the assumption overstates the 2-micro edge and is conservative
for a null claim (R-1).

### 4.4 Regime slices
Results are also shown per calendar year, descriptively. No slice (2020 or any other) is
chosen, dropped, weighted or excluded after results are seen, and no market-regime
exclusion of any kind is applied in advance either. For the event statistics the
vendor-degraded flag removes five 2020 dates (2020-02-27, 02-28, 05-05, 06-30, 07-01) by the
standing rule; the trials trade through them (D-5).

## 5. Power and sample size (Task 3, filled before hashing)
Computed in Stage D.1e from the existing train-window series (reports/stage_d1e_power.json,
verified in reports/stage_d1e_power_verification.md). Unit: net ticks per micro per day.
n_b = days for 80% null power at epsilon (a member with true edge 0 shows UCB95 < epsilon with
probability 0.80); n_a = days for 80% power to detect a true edge of epsilon at Holm's most
stringent step (alpha = 0.05/58). Chosen = analytic unless the block-bootstrap simulation
differed by more than 15%, then the larger of the two. Days supplied = the confirmation
window S..2024-02-29 after exclusions, for the start dates the start rule could yield
(calendar estimate, +/-3%); S itself is computed in D.1f by section 4.1.

| Class | Binding member for null power | n_b analytic / simulated / chosen | Binding member for detection | n_a chosen | Days supplied at S = 2019-05-06, 2019-07-01, 2020-01-02, 2021-01-04, 2022-01-03, 2023-01-03 | Null power at epsilon reachable |
|---|---|---|---|---|---|---|
| C1 | A-H4 rth leg | 149 / 161 / 149 | A-H4 rth leg | 379 | 1151, 1114, 992, 755, 516, 277 | all S |
| C2 | G3.RTH.5 | 193 / 182 / 193 | G3.RTH.5 | 492 | 1151, 1114, 992, 755, 516, 277 | all S |
| C3 | F1_1_h1_RTH | 566 / 571 / 566 | F1_1_h1_RTH | 1447 | 1151, 1114, 992, 755, 516, 277 | S <= 2021-01-04 |
| C4 | F2_4_15min_vol_tercile_top | 171 / 152 / 171 | F2_4_15min_vol_tercile_top | 436 | 1151, 1114, 992, 755, 516, 277 | all S |
| C5 | E-H1 scheduled macro drift | 16 / 10 / 16 | E-H1 scheduled macro drift | 41 | 1151, 1114, 992, 755, 516, 277 | all S |
| C6 | C-H4 passive-fill reversal | 181 / 174 / 181 | C-H4 passive-fill reversal | 461 | 1151, 1114, 992, 755, 516, 277 | all S |
| C7 | H6 prior-close location follow-through (projected) | 114 / censored / 114 | H6 prior-close location follow-through | 290 | 1151, 1114, 992, 755, 516, 277 | all S |

Supplied days: S = 2019-05-06: 1151, S = 2019-07-01: 1114, S = 2020-01-02: 992, S = 2021-01-04: 755, S = 2022-01-03: 516, S = 2023-01-03: 277.

Achieved null power is MEASURED in D.1f for every member from its own confirmation series
(section 3); the figures above are the plan, not the criterion. Family H rows are projections
from proxies (reports/stage_d1e_coverage.md section 5).

What the confirmation window can and cannot resolve (descriptive, not a criterion): with the
full extension the smallest per-trade edge the data can rule out at 80% null power is
C1 2.45 to 23.62 (A-H3 weekend effect); C2 0.30 to 14.00 (G3.RTH.5); C3 0.02 to 5.22 (G4.RTH.60); C4 0.46 to 3.27 (D-H4 overnight gap fade); C5 1.96 to 37.26 (E-H1 scheduled macro drift); C6 0.15 to 0.15 (C-H4 passive-fill reversal); C7 26.65 to 40.88 (H2 NR7 opening-range breakout) ticks per trade at S = 2019-05-06. 47 of the 95 measured members can be resolved below the 2.11-tick
market cost bar; the 48 that cannot are the members trading about once a day or less. For
those, a null at epsilon is all this program can establish with any purchasable MES history,
and section 7 says so.


## 6. The inconclusive rule and the out-of-scope list
- Inconclusive: any member that neither passes confirmation nor meets both null
  conditions. One inconclusive member keeps its class out of the null verdict. Nothing is
  rounded to null; no member is dropped, moved or re-parametrized after the run; a member
  with zero closed round trips or zero events on the window, or with a zero bootstrap
  standard error, is inconclusive (no evidence), not null, and its class is out of the
  null verdict (N-2). No minimum activity above zero is imposed on the null itself, because
  a member that almost never trades truly cannot fund a Combine and that is the economic
  statement; but a member with fewer than 30 closed round trips or events on the window is
  marked "null by inactivity", and a class statement resting on such a member carries that
  label in the same sentence (E-2).
- Out of scope (the verdict never speaks for these): multi-day holding (excluded by the
  venue, Stage D.1c); instruments other than MES and every cross-asset effect (user
  decision, 2026-09); order-flow signals needing book data beyond C6's fill model; sizes
  other than the 2-micro headline; passive execution for any class other than C6;
  strategy constructions not on the frozen list, including ideas logged for the future in
  D.1b and D.1d.

## 7. What the program may say, and what it may not
If a class comes out null, the program may say the bounded statement in section 1 for
that class, cite this file's hash and the confirmation list's hash, and must carry in the
same sentence the class's per-trade epsilon at its confirmation-window frequency, the
member with the fewest trades or events and its count, the largest per-trade upper bound
found in the class, and the label "null by inactivity" if any member the null rests on has
fewer than 30 closed round trips or events (E-2). It may not say "MES has no edge",
"intraday MES has no edge", "MES is efficient", or anything about sizes, instruments, fill
types, horizons or constructions outside the list. If every class C1 to C5 and C7 comes out
null, the program may say exactly this (W-1): "on trade dates S to 2024-02-29, no member of
any class the program tested on MES (market-order trials at their coded size, event
statistics at the flat modelled round turn, Family H at 2 micros) showed a net edge of at
least epsilon_day = 34 net ticks per micro per day, the smallest edge that funds the Topstep
XFA funnel under the Stage B model of the 2026 rules and fee schedule at 2 micros; every
member's one-sided 95% upper bound was below epsilon at >= 80% achieved null power; per
class, the per-trade resolution was [table]", and must add that C6 awaits D.1g and that the
structural question below epsilon remains open where section 5 says the data cannot
resolve it.
