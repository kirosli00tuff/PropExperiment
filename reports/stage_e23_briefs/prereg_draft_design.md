# E.23 prereg draft: the window and power reasoning (lead, 2026-10-17, before any outcome read)

Draft section for reports/stage_e23_prereg.md. No bar has been read for any trigger-hold book; the numbers below come from
calendars and arithmetic only (business-day counts less about 4% holidays; the power table in the freeze replaces them
with each book's own n_dates).

## Power on a daily series
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

## The window assignment [LEAD]
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
  so a later registered stage could confirm survivors on W_cf extended by holdout-2 and the research window (about 7.0
  years, power about 0.25 at t >= 2.0). That needs the user's decision and a registered holdout read; this stage does not
  read holdout-2.
- E.21 read the daily series of 2010-07..2024-02 for the 17 roots, so the aggregate multi-day drift of both windows is
  known. The measure is the alpha over the same root's E.21 T1 and T2 returns, which is what guards against counting
  that drift (or trend) again.

## The power gate [LEAD]
The gate uses the per-test hurdle alpha t >= 2.0, the only part of the discovery bar fixed by the trigger-hold and its
window alone (the Holm threshold a test faces depends on the other tests' realized p values). Holm's step-1 power at the
registered K is reported beside it: at K = 8 to 24 it is 0.13 to 0.07 on W_ext, so only an effect well above S = 0.5
can survive Holm in this family.
