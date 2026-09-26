# Stage E.2a Task 13: addendum A-1 to the epsilon declaration (exact early termination of failing cells)

Written by the Stage E.2a lead (Opus 5.5, xhigh) on 2026-09-25 at about 06:20 PDT, after a session-limit
pause (03:03-06:10 PDT) during which the detached funnel driver kept running: B1 was complete for ZT and
ZF (212 and 206 cells, 2.5 hours for the pair at 2 x 6 workers, about 42 s per cell) and running for ZN
and TN. At that pace B1 for the remaining 26 exposures would take about 20 hours. This addendum changes
how cells are computed, not which cells are evaluated or how any epsilon is defined. It applies only to
cells not yet evaluated when it is written; its sha256 is recorded in reports/stage_e2a_STATE.md.
reports/stage_e2a_epsilon_declaration.md (sha256 ccdb8ec5...) is unchanged and still governs.

## A-1. A failing cell may stop as soon as a pass is impossible

- The verdict rule (funnel.power_gate.verdict, n = 8,000): pass iff power - 1.96 x sqrt(power (1 - power)
  / n) >= 0.80, with power = k / 8,000, k the number of careers whose 12-month net income exceeds the
  robust critical value. Evaluated over k = 0..8,000, the rule passes iff k >= k_min = 6,469 (k = 6,468
  gives "marginal", lower bound 0.79988). So a cell passes iff at most 1,531 of its 8,000 careers fail.
- Careers are simulated in batches in run-index order with per-run seeds that do not depend on the
  batching (to be verified before use, below). Once more than 1,531 careers have failed, no outcome of
  the remaining careers can make the cell pass, so its verdict is "not pass", exactly as the full 8,000
  careers would give. Such a cell is recorded as "fail (pass impossible after n runs)" with n and the
  failure count; its other fields (power, quantiles, samples) are not computed. Whether it would have
  been "fail" or "marginal" is not needed: both are "not pass" (declaration point 11; marginal cells are
  excluded from the minimum).
- A cell that does not stop runs all 8,000 careers and carries every field. In particular every passing
  cell, including each exposure's binding cell, is computed in full.
- Consequence: the set of passing cells, the first pass in ascending order, eps_X,funnel and the
  operative eps are exactly what the full computation gives. Only the recorded detail of early-stopped
  failing cells is reduced.

## Validation required before A-1 is used (FunnelRunner, recorded in reports/stage_e2a_epsilon.md)

1. Batched evaluation reproduces the full run's samples: for at least three stored cells, the first n
   careers' net incomes from the batched path equal the stored full run's (bit for bit), for n at every
   batch boundary up to 8,000.
2. Re-running at least five already-evaluated failing cells of ZT or ZF with early stop gives the same
   verdict ("not pass") and a failure count that is a prefix count of the stored samples.
3. Re-running ZT's binding cell (consistency, T = 2, p = 0.55, R = 2.0) through the new path gives a row
   identical to the stored one.
If any of these fails, A-1 is not used and the run continues at full length.
