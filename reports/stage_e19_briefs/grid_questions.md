# GridCoder-OpusHigh: readings taken and questions for the lead (Stage E.19 grid)

Each item is a place where brief_grid.md or sim_spec.md section 6 left room. The reading closest to
the brief's words was implemented, and the run continued. Code: prop_econ/grid.py,
prop_econ/report.py.

## Seeds and pairing

- Q1. The brief lists the cost model among the shock-seed keys, so the `wall` sensitivity draws
  different shocks (and cycle indices) from the d8 headline twin, and the comparison is unpaired.
  Pairing would need the cost model dropped from the seed. This changes no headline number.
  Normal tail, long direction and per-product runs differ in their shocks anyway. Implemented:
  as written.
- Q2. Slots 1 and 5 share one campaign seed (the brief keys it on size and shock config only), as
  do the two pricing paths and the two payout paths.
- Q3. The T5 differences use unpaired SEs, sqrt(se1^2 + se2^2), which is conservative where seeds
  are shared (keep_d, call-up, readings variants). Per-cycle nets are saved (.npz) only for
  headline jobs, to keep reports/stage_e19_runs/ at about 100 MB instead of about 250 MB.

## Wallet

- Q4. API fee periods: a cycle that ends at elapsed day `end` pays ceil(end / 21) periods. A
  campaign event at the start of day t (a crossing) has paid floor(t / 21) + 1 periods, because
  day t is in operation. The fee is one per user in campaigns, whatever the slot count.
- Q5. Copy-traded five accounts = 5 x (user cash - Combine, activation and B2F fees) of one cycle,
  minus one API fee (one per user). Purchases are also x5. The Responsible Trading Program risk
  (L-14) is not modelled.
- Q6. Voluntary close at the horizon = profit_split_trader x min(frac x max(end_balance -
  start_balance, 0), cap), with split 0.9, frac 0.5 and cap 5000 read from the rules file. It
  applies to every XFA of the cycle alive at the horizon, Back2Funded XFAs included when B2F is
  on.
- Q7. The ACH/wire fee of $30 is charged per payout, overflow payouts included (n_payouts counts
  all of them).
- Q8. global.api_access_monthly_usd has a second reading (29.0, SOURCED). It is not run, because
  the brief does not list it. The other two CONFLICT rules
  (dll_cap_requires_dll_at_combine_purchase, xfa_min_payout_balance_after_first_required) are not
  modelled as sensitivities either. All three would be post hoc or one-line additions if wanted.

## Metrics and derived quantities

- Q9. "attempts per pass" = 1 / P(pass) from the attempt pool. The cycle's mean attempts, capped
  at 60, is reported separately as mean_attempts.
- Q10. "Per funded XFA" = mean user cash of the XFA pool (one XFA, no Back2Funded) minus the
  pricing path's activation fee.
- Q11. Break-even S "at the best f" is the envelope: at each S, the band f with the highest cycle
  mean net, then interpolation. A non-monotone curve takes the first upward crossing. Break-even
  is also reported at each diagnostic f.
- Q12. The optimum f is by cycle mean net including the API fee. Ties go to the smaller f.
- Q13. Effective net Sharpe of zero_k1 / zero_k3: the scalar reference replays the first 200
  attempt rows and the first 200 XFA rows (standard path) of each zero-edge job with a day log.
  Risk-weighted S_eff = -sqrt(252) x sum(n x k x rt_u) / sum(n x sigma_u) over all traded days of
  both phases. The day-weighted mean of -sqrt(252) x k x rt_u / sigma_u and the full-size share
  are also stored. This is a 200 + 200 row subsample, not all 20,000 paths.

## Table layout (compactness; every number is in reports/stage_e19_results.json)

- Q14. T2 "cheaper pricing" = per cell, the pricing path with the lower mean total fees (API
  included), marked s / n.
- Q15. T4 (campaigns) and T5 (sensitivities) show DLL off and one pricing path per row, the
  "better" one: the path with the higher cycle mean net at its own best band f. The DLL-on
  campaigns and the other pricing path are in the JSON.
- Q16. T5 compares each side at its own best band f, and the sensitivity at the twin's best band
  f. The readings variants (f 0.10 and 0.25 only) are compared at both f.

## Lead additions during the run

- Q17 (RR-1 churn). The grid was stopped at 18:01:45, 8 minutes in, and restarted at 18:02:37
  with exact per-cycle churn fields in grid.py's post hoc step. These fields need no new pools,
  but the jobs already finished lacked them, so the partial run was discarded. The fields:
  Combine-phase days (exact: the cycle's attempt days; a reset starts the next attempt the next
  trading day, so the reset gap is 0 days), Combine and XFA MLL breaches, XFA days, and a 5-slot
  first-252-day purchase count. For that count, one slot is chained from consecutive cycles of
  the 20,000-cycle batch and the result is x5, slots being independent. It is not taken from the
  campaign draws: the campaign trace is not kept.
  Rates are ratios of cycle means (long-run rates), not means of per-cycle ratios. The 5-slot
  campaign rate "purchases per 21 elapsed days" is the mean over replications that reached the
  target of 21 x purchases / days at the first crossing.
- Q18. The L-19 label is applied to every record: low <= 2.0, medium <= 4.0, else high. The
  forfeiture column = minus the mean total fees, API fee included. "Best f restricted to low" =
  the band f with the highest mean net among records labelled low. It shows "none low" when no
  band f qualifies.
- Q19 (RR-4 fingerprint). The rules file mtime is 18:01:15 PDT, which is before the restart
  (18:02:37). Every job in the final run therefore carries the new fingerprint d4644acce4988b94.
  The old fingerprint 1509fa8a6926cde9 belongs only to the discarded partial run. results.json
  records both, with the lead's note. The aggregator accepts any fingerprint.
- Q20 (for the lead's judgment, not decided here). Every one of the 4,464 records is labelled
  "low" churn. Purchases per 21 Combine-phase days run from 0.79 to 1.90, because rebills carry
  reset credits, so few resets are paid. The 5-slot first-year rate runs from 2.86 to 8.73
  purchases per 21 elapsed days. As implemented, the L-19 restricted best f always equals the
  unrestricted best f. If the lead meant L-19 to be read on the 5-slot account-level rate, the
  report needs a one-line change in report.add_churn.
