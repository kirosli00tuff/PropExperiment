# Stage E.23 pre-registration: E23, the program's intraday triggers held for 5 and 20 days (alpha over trend)

Status: FROZEN at the "E.23 freeze" commit (lead, 2026-10-17; drafted from 02:39 PDT, completed 03:10 PDT, before any outcome read),
before registration and before any trigger-hold book is computed. Written by the lead; nothing here is chosen from data.
Binding: docs/prompts/STAGE_E.23.md (governs), then reports/stage_e23_briefs/lead_spec.md (code-level definitions;
governs this file where they differ), then this file. Inputs: reports/stage_e23_briefs/shortlist.md (P1.1-P1.4).

## 1. What is registered
Five trigger-holds, registry label E23; N 533 -> 538. (Registry ids carry one hyphen, screening/trial_registry.py _ID; renamed
from E23-MEZF-h5 etc. at 03:33 PDT when the registry refused the first form; no other change.) Each is read once on its discovery window behind
reports/stage_e23_RUN_ONCE_discovery.json, under the freeze manifest reports/stage_e23_freeze.json and harness v13
dd2bcc6025144e0debd19be1ca8d43c983872a27c9258895ef55ee3c138609e4.

| Id | Trigger (frozen, unchanged) | Root (price path / cost vehicle) | Unit direction m | Hold h | Mechanism (memo) |
|---|---|---|---|---|---|
| E23-MEZFh5 | K2-monthend-01 ZF (BUY at 07:20 CT on N-1 and N) | ZF / ZF | +1 (member's side: long) | 5 | month-end Treasury demand (M7) |
| E23-MEZNh5 | K2-monthend-01 ZN | ZN / ZN | +1 | 5 | same |
| E23-MEZBh5 | K2-monthend-01 ZB | ZB / ZB | +1 | 5 | same |
| E23-H6NQh5 | E20H6-T1 (side sign(r_ROD) at 14:30 CT) | NQ / MNQ | -1 (reversal) | 5 | late-day price pressure reverses; post-2000 index anti-autocorrelation (M4) |
| E23-H6NQh20 | E20H6-T1 | NQ / MNQ | -1 | 20 | same (20-day evidence disputed) |

Directions are fixed by the mechanism memo (reports/stage_e23_briefs/mech/M4_INTRADAY_MOM.md, M7_MONTHEND.md), never by
data. One direction per trigger: for E20H6-T1 the memo's mechanism (late-day price pressure and index anti-autocorrelation)
predicts reversal; the 20-day evidence is disputed (reversal in the first days, continuation from the second week), and
the lead registers the 20-day hold in the mechanism's direction under P1.3's two-holds default [LEAD; review R-06]. Everything else in the inventory is dropped or excluded with its reason (shortlist.md).

## 2. The book (P2.1; lead_spec sections 1-3)
Entry at the settlement mark of the trigger day (the first settlement mark strictly after the trigger's decision time;
both triggers decide before their root's settlement: rates 14:00 CT, NQ 15:15 CT to 2020-10-25 and 15:00 CT after), so
the trigger day's intraday P&L is never counted. Exit at the settlement mark h trading days later. Each trigger opens one
unit in direction m x side; the root's position is clip(sum of active units, -1, +1) and changes only when that value
changes. Size 0.40 / (sigma x notional) at the change date, sigma the E.21 EWMA (centre of mass 60) known strictly before
it. Costs per side at D8 for the vehicle on every entry, exit and roll leg; stress = commission + 2 x the D8 slippage.
Rolls, marks, guards and daily attribution exactly as E.21 (frozen multiday code). Daily marked-to-settlement net values.

## 3. The measure and the bars (P2.2, P2.4; lead_spec sections 4 and 7)
Measure: the intercept a of the OLS y_d = a + b1 T1_d + b2 T2_d + e_d, y the book's base daily net values, T1 and T2 the
same root's E.21 TSMOM-12 and 1/3/12-blend base daily net values (recomputed per root by the frozen E.21 code and checked
against E.21's published sums), over the book's series dates. Alpha t = a / se_HAC(a), Bartlett lags h.
p_alpha = max(one-sided Student p of the plain OLS t, n - 3 df; one-sided normal p of the HAC t).
H0 per trigger-hold: a <= 0; H1: a > 0.

Discovery screen: Holm step-down over the five at one-sided alpha 0.05 on p_alpha; a survivor also needs alpha t >= 2.0
and base net Sharpe >= 0.3 (mean / sd x sqrt(252)); at most 4 survivors (largest alpha t, ties by net Sharpe).
Confirmation (once per survivor; only where the confirmation power gate passes on W_cf: power at the hurdle
b = max(2.0, z_{1 - 0.05/S}), S the number of survivors, must be at least 0.2; the power table's power_gate is the S = 1
value, b = 2.0, and already fails on every W_cf row, so every b gates them; amended 03:25 PDT on review R-03): Holm over the survivors at one-sided 0.05;
alpha t >= 2.0; base net Sharpe >= 0.3; stress net Sharpe > 0; DSR > 0.95 at N = 538; CSCV PBO < 0.5 on the discovery
window. Verdicts: PASS, NULL, INCONCLUSIVE BY DESIGN, UNCONFIRMABLE ON OWNED DATA.
A trigger whose raw P&L is positive but whose alpha is not is a null: it is trend, already known.

Reported beside the verdicts, never part of a bar: raw t (plain and HAC), stress statistics, betas and R^2, alpha3 (the
same regression plus the root's own buy-and-hold daily value: the month-end book is long-only, so its raw drift is shown
separately), in-market fraction, per year, gross, costs and cost share, fills by kind, exclusions by reason, DSR at N 538
and CSCV PBO (8 contiguous blocks) over the five discovery series.

## 4. Windows, data use and power (P1.4, P2.3)
(From reports/stage_e23_briefs/prereg_draft_design.md; approximate day counts, replaced by the power table below.)

### Power on a daily series
For a book whose daily net series has a true annualized Sharpe S, the expected t after T years is S x sqrt(T) whatever
the event count (zeros on flat days included): the program's convention (E.21 prereg section 3; E.22 F1:
power = 1 - Phi(z - S sqrt(T))). At S = 0.5 the per-test hurdle alpha t >= 2.0 is reached with power 0.2 only when
T >= 5.37 years.

| Window | Book days (approx.) | E[t] at S = 0.5 | power at t >= 2.0 | Holm step 1, K = 4 / 8 / 12 / 24 |
|---|---|---|---|---|
| W_ext, 13 long roots (2011-07-27..2019-04-30) | 1,944 | 1.39 | 0.27 | 0.20 / 0.13 / 0.11 / 0.07 |
| W_ext, LE (from 2014-12-15) | 1,096 | 1.04 | 0.17 | below 0.2 |
| W_ext, TN (from 2016-01-11) | 827 | 0.91 | 0.14 | below 0.2 |
| W_ext, RTY and HE (from 2017-07) | 453 | 0.67 | 0.09 | below 0.2 |
| W_cf (2019-05-06..2024-02-29) | 1,208 | 1.10 | 0.18 | below 0.2 |
| (not owned for this use) W_cf + holdout-2 + research window, less the embargo | 1,765 | 1.32 | 0.25 | 0.18 / 0.12 / 0.09 / 0.06 |

Consequences, fixed before any outcome read:
1. W_cf (at most 4.82 years for every root) cannot reach the bar with power 0.2 in either role. Every trigger-hold is
   "inconclusive by design" on W_cf and is not read there.
2. W_ext supports a read only for the 13 roots with history from 2010-07 (NG, NQ, ZN, 6E, GC, ZC, ZT, ZF, ZB, UB, CL, ZL,
   ZS). TN, RTY, HE and LE are inconclusive by design on both windows.

### The window assignment [LEAD]
- The prompt's ideal discovery window is the data each trigger was screened on. For every Stage E cluster member that is
  the research window 2025-04-01..2026-06-19, which P2.4 bars. No owned window is both the screened data and readable.
- Selection versus testing (P1.4): the research window SELECTED the Stage E members (D5 screen); W_cf TESTED them at
  their intraday holds (confirmation and null reads); W_ext never read them at any hold. E.20 H6 was tested once on
  2020-06..2024-02 and never read on W_ext. E.16 H1 and H4 were tested once on 2010-07..2024-02 (both windows); neither
  window selected them. So both W_ext and W_cf are owned data that never selected these triggers.
- Discovery = W_ext, because it is the only owned window that can be read with power 0.2. Confirmation = W_cf, declared
  for every trigger and inconclusive by design (power 0.18 < 0.2), so not read. Survivors of discovery therefore end as
  INCONCLUSIVE BY DESIGN; the others as not surviving discovery.
- Why not the reverse (discovery W_cf, confirmation W_ext): discovery on W_cf is inconclusive by design, so nothing would
  be read at all. The chosen order reads W_ext once and leaves every trigger's multi-day outcome on 2019-05..2024-02 unread,
  so a later registered stage could confirm survivors on W_cf extended by data that never selected them: for E20H6-T1
  (never read on the research window) W_cf + holdout-2 + the research window, less the embargo (about 7.0 years, power
  about 0.25 at t >= 2.0); for K2-monthend-01, whose screen used the research window (so P1.4 bars it as confirmation
  data), W_cf + holdout-2 only (about 5.8 years, power about 0.21). That needs the user's decision and a registered
  holdout read; this stage does not read holdout-2. (Amended 03:25 PDT on review R-01.)
- E.21 read the daily series of 2010-07..2024-02 for the 17 roots, so the aggregate multi-day drift of both windows is
  known. The measure is the alpha over the same root's E.21 T1 and T2 returns, which is what guards against counting
  that drift (or trend) again.

### The power gate [LEAD]
The gate uses the per-test hurdle alpha t >= 2.0, the only part of the discovery bar fixed by the trigger-hold and its
window alone (the Holm threshold a test faces depends on the other tests' realized p values). Holm's step-1 power at the
registered K is reported beside it: at K = 8 to 24 it is 0.13 to 0.07 on W_ext, so only an effect well above S = 0.5
can survive Holm in this family.

Power table (reports/stage_e23_power.json, `python -m trigger_hold.run power`, 03:10 PDT; from trigger events, calendars and
bar existence only; no forward return or mark price read):

| Trigger-hold | Window | Book dates (from first unit) | Events | Units | Non-overlapping | In market | E[t] at S 0.5 | power_gate (t >= 2.0) | power_holm1 (K 5) | Label |
|---|---|---|---|---|---|---|---|---|---|---|
| E23-MEZFh5 | W_ext 2011-07-27..2019-04-30 | 1939 from 2011-07-28 | 137 | 131 | 71 | 0.21 | 1.387 | 0.270 | 0.174 | read (discovery) |
| E23-MEZFh5 | W_cf 2019-05-06..2024-02-29 | 1170 from 2019-06-27 | 79 | 77 | 39 | 0.20 | 1.077 | 0.178 | 0.106 | inconclusive by design |
| E23-MEZNh5 | W_ext 2011-07-27..2019-04-30 | 1939 from 2011-07-28 | 143 | 137 | 77 | 0.23 | 1.387 | 0.270 | 0.174 | read (discovery) |
| E23-MEZNh5 | W_cf 2019-05-06..2024-02-29 | 1170 from 2019-06-27 | 77 | 77 | 39 | 0.20 | 1.077 | 0.178 | 0.106 | inconclusive by design |
| E23-MEZBh5 | W_ext 2011-07-27..2019-04-30 | 1939 from 2011-07-28 | 142 | 136 | 76 | 0.23 | 1.387 | 0.270 | 0.174 | read (discovery) |
| E23-MEZBh5 | W_cf 2019-05-06..2024-02-29 | 1170 from 2019-06-27 | 79 | 77 | 39 | 0.20 | 1.077 | 0.178 | 0.106 | inconclusive by design |
| E23-H6NQh5 | W_ext 2011-07-27..2019-04-30 | 1934 from 2011-07-27 | 1860 | 1727 | 374 | 0.91 | 1.385 | 0.269 | 0.173 | read (discovery) |
| E23-H6NQh5 | W_cf 2019-05-06..2024-02-29 | 1204 from 2019-05-07 | 1147 | 1085 | 233 | 0.93 | 1.093 | 0.182 | 0.109 | inconclusive by design |
| E23-H6NQh20 | W_ext 2011-07-27..2019-04-30 | 1934 from 2011-07-27 | 1860 | 1711 | 95 | 0.94 | 1.385 | 0.269 | 0.173 | read (discovery) |
| E23-H6NQh20 | W_cf 2019-05-06..2024-02-29 | 1204 from 2019-05-07 | 1147 | 1070 | 59 | 0.95 | 1.093 | 0.182 | 0.109 | inconclusive by design |

Every W_cf row is inconclusive by design (power_gate 0.178-0.182 < 0.2), so the confirmation step reads nothing and
every discovery survivor ends INCONCLUSIVE BY DESIGN. Every W_ext row is read (gate 0.269-0.270; at least 71
non-overlapping events). The H6 books are in the market on 91-94% of days with a side that follows the trigger; the
month-end books on 21-23% of days, always long.

## 5. Cost feasibility (DECISIONS V31; before registration)
| Trigger | Published gross per event (memo) | D8 round trip of the vehicle at the settlement minute (base_rules.costs) | Multiple |
|---|---|---|---|
| K2-monthend-01 ZF | +7 bp on day N (HS19 Table 8, futures, se 1) | $10.14 (1.30 ticks), about 0.9 bp at a $115K notional | about 8 |
| K2-monthend-01 ZN | +9 bp (se 1) | $18.26 (1.17 ticks), about 1.5 bp at $125K | about 6 |
| K2-monthend-01 ZB | +15 bp (se 2) | $34.04 (1.09 ticks), about 2.3 bp at $150K | about 6.5 |
| E20H6-T1 NQ | about 6 bp over 2-3 days per a 20 bp last half hour (M4: the reader's arithmetic from BDLM2021 Table 11, not a published figure) | MNQ $2.10 (4.20 ticks), about 0.7-1.5 bp at NQ 7,000-15,000 | about 4-8 |
Each clears 1.5 x its round trip. Notionals are typical-price approximations for this check only.

## 6. N and order (P2.5, P2.6)
N 533 -> 538, entered in ledger/trial_registrations.jsonl (label E23, ids above, this freeze's sha256, harness v13) before
the discovery read. Order: inventory, memo, shortlist and data-use map written (shortlist.md, 02:37 PDT); this freeze
written and hashed; RegReviewer-FableXHigh review (BLOCKING and SHOULD FIX fixed first); freeze commit; registration;
discovery read once behind its marker; screen; the confirmation step once behind a second marker (it reads nothing for a
power-gated trigger-hold); VerdictVerifier-FableXHigh recomputation. A BLOCKING finding on a verdict is resolved by
finding the code error, never by a second read. No outcome read starts after 10:30 PDT.

## 7. Fixed before any outcome read
Everything in this file and in lead_spec.md: triggers, roots, directions, holds, windows, the entry rule, the cap, the
sizing, costs and the stress case, the trend regressors, the statistics and lags, the bars, the survivor rule, the power
gate, and the run discipline. No trigger, hold, window, cost, lag, alpha or bar changes after any outcome read. No test is
added or run twice. Nothing dated 2024-03-01 or later, the research window, holdout-2, the March 2024 embargo or MES's
sealed stores is read.
