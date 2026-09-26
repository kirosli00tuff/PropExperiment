# Stage E.2a Task 13: the lead's declaration for the funnel re-derivation of epsilon

Written by the Stage E.2a lead (Opus 5.5, xhigh) on 2026-09-25 at about 02:40 PDT, after FunnelRunner-
OpusXHigh's phase A (reports/stage_e2a_funnel_phaseA.json: the generalized gate reproduces D.1e's
stored MES cells field for field and sample for sample on 7 cells from T = 1 to T = 32; timing probe;
16 open points) and before any funnel run on a Stage E exposure's bars. Its sha256 is recorded in
reports/stage_e2a_STATE.md at writing. Every point below fills in a place where frozen design D3
(with D2 and docs/NULL_CRITERIA.md 2.2, "D.1e's rule exactly") must be read to be computed for a
non-MES exposure. The numbering follows phase A's open points. The independent recomputation (Task 12)
may challenge any of them.

## The quantity (unchanged)

eps_X,funnel = floor(min over cells whose robust_c80_verdict == "pass" of net $/day at q_c / (q_c x
tick_value_c)); marginal cells excluded; the cell set is the 120 grid cells plus D.1e's 100 extension
points (220). eps_X,translated = floor($85.00 / (q_c x tick_value_c)) (readings R12). Operative eps_X =
min(translated, funnel); if no cell of the set passes, the funnel figure is undefined, the translated
bar is used and the exposure is flagged (D3, review R-12). Both figures are reported.

## Declarations

1. **Robust critical value: MES's frozen null baseline** (reports/funnel_null_baseline.json), exactly as
   funnel/power_gate.py reads it. D3 re-runs "the Stage B power gate (funnel/power_gate.py ...)" with
   the exposure's own segment moves and cost; the gate reads the frozen baseline; the robust critical
   value is a dollar bar on 12-month funnel income, and D2's sizing matches every exposure to MES's
   2-micro risk. A per-exposure baseline is not declared (about 20 hours, and it needs costs at sizes
   other than q_c that D8 does not define). Any leniency is capped: the operative eps never exceeds
   the translated bar.
2. **Matched (headline) critical values: not computed** (null), as D.1e did at T >= 8; the verdict that
   counts is the robust one (NULL_CRITERIA.md 2.2).
3. **Size unit:** positions in 0.1-lot units (q_c x 10 x the D9.6 lot weight), with P&L rescaled from
   the vehicle's ticks and tick value; the identity for MES; the Scaling Plan check stays exact.
4. **Segment window: [O_X, C_X)** of D6 on the trade date's own calendar day (ruling L-10), not MES's
   [08:30, 15:08). D2's risk window is [O_X, C_X) and D2 sizes every exposure to MES's risk on that
   window; for MES the two windows differ by the 8 post-close minutes, for rates, FX, energy and metals
   by one to three thin post-settlement hours. The flatten flag still applies.
5. **Dates: D2's dates exactly** (readings R2): the vehicle's research trade dates, less its
   roll-blackout dates (group calendar, ruling L-8), vendor-degraded dates (the trade dates whose day
   session falls on a degraded UTC date, as reports/stage_e2a_bars.json lists them), and dates with a
   full closure or an early halt or early close at or before C_X.
6. **Endpoints and split:** the day's first bar at or after O_X and last bar before C_X, both in
   [O_X, C_X) (readings R3); the window is split into T segments of equal bar count (MES's split).
   Hence at T = 1, E|m_1| x tick value = r_c exactly: phase B asserts it against
   reports/stage_e2a_vehicle_sizes.json for every exposure, and a mismatch stops that exposure.
   Days skipped for lack of bars are counted; over 5% is flagged.
7. **E|m_T| at T = 1, 2, 4, 8, 16 and 32.** D3 names T = 1, 2, 4, 8, but its fixed cell set holds T = 16
   and 32 extension cells, which cannot be evaluated otherwise; dropping them could only raise eps.
8. **Cost:** MES's timing (entry at a segment's first bar, exit at its last bar plus one minute); per
   side, the mean of the buy and sell D8 costs at q_c in that minute's 30-minute bucket (s_b plus the
   side's depth term) plus half the round-turn commission, in USD, rounded up to the cent; from the
   final D8 table (reports/stage_e2a_costs.json, frozen). No event-window cost (D.1e had none; the event
   rule is a member fill rule, E.2b).
9. **p_beats comparison sample:** the exposure's own T = 1 zero-edge sample (informational only).
10. **Undersized exposures: operative eps = min(translated, funnel)**, D3's rule. D2 says the funnel
    figure "then governs"; D3, written after it with the no-passing-cell rule, says the minimum; the
    minimum is the conservative reading (a smaller eps makes a null harder to claim). Both figures are
    reported and the exposure is flagged; for the user.
11. **Cell set and order: the exact ascending evaluation, in two passes.**
    - Every cell's analytic net $/day at q_c is computed before any simulation; cells are evaluated in
      ascending order of it (tied cells together); each cell's verdict depends only on its own fixed
      seed, never on which other cells ran.
    - **Pass B1 (operative, exact):** for each exposure, evaluate in ascending order the cells whose net
      $/day is below eps_X,translated x q_c x tick_value_c, stopping at the first robust "pass". If
      one passes, eps_X,funnel = floor(its $/day / (q_c x tick_value_c)) < eps_X,translated and is the
      operative eps. If none passes, the operative eps is eps_X,translated, exactly (no cell above the
      bar can make floor(.) smaller than it).
    - **Pass B2 (reported figure):** continue in ascending order above the bar until the first pass
      (that gives the reported eps_X,funnel) or the set is exhausted (funnel figure undefined, flagged).
      B2 cannot change any operative eps.
    - B1 runs for every traded exposure first, in the cluster order of U3 (K2, K4, K5, K3, K6, K7, K1);
      then B2. The job is resumable per (exposure, cell).
    - D3's bracketing subset is not used: phase A shows it is inexact and slower than this.
12. **T = 32 cells** exceed D9.3's 20 entries per day; they stay in the set (D3 fixes it) and are flagged
    if one binds.
13. **Vendor tick:** the tick in the vendor's price units per product (100 x the E.0 tick_size for ZC,
    ZW, ZS, ZL, HE, LE), from BarsCoder's and CostCoder's recorded scales, re-checked on the bars.
14. **Price bars:** each exposure's D2 vehicle's own research bars.
15. **Floor:** floor of the stored float, as D.1e; any value within 1e-9 of an integer is flagged.
16. **Seeds and runs:** BASE_SEED and 8,000 careers per cell for every exposure, as Stage B and D.1e;
    forkserver start; two exposures at a time with 7 workers each (14 threads, the overnight profile's
    limit, no other heavy job running); nice 10; no cell starts between 15:20 and 16:05 PT on weekdays
    (the AiTrader window).

## Scope

Traded exposures only: each exposure with a D2 vehicle (including "undersized"). An exposure with no
candidate is not traded in Stage E and gets no epsilon.
