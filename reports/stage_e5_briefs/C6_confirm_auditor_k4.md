# Brief: ConfirmAuditor-K4-FableXHigh, Part 2 (Stage E.5 Task C6: recompute every K4 verdict figure)

Same repository, same rules as Part 1 (read-only except your report and scratch; no commits, no web; context hygiene).
Independent: recompute in YOUR OWN code (numpy, statistics, math), never by calling screening/stage_e_verdict.py. You may
call funnel.null_generator.stationary_bootstrap_indices (the program's frozen generator), and funnel.multiple_comparisons for
DSR, t and PBO only as a second check after your own formula, saying which you used.

## Inputs
- The hashed list: reports/stage_e5_k4_confirmation_list.json (sha256 22388c6b3cbfb2b32809cba1ffbcd6a72ad6ff2b0bff0890474d80a65037d46c,
  commit 4161032) and its .md.
- The run: reports/stage_e5_k4_confirmation/ (the runner's member records K4_<member>_confirmation.json, their
  _trips.json, the cluster record) and its log reports/stage_e5_briefs/c5_k4_run.log.
- The verdicts under audit: reports/stage_e5_k4_verdicts.json (the verdict module's output) and reports/stage_e5_k4_verdicts.md
  (the lead's rendering).
- The criteria: docs/NULL_CRITERIA_E.md sections 1, 3, 6, 7; docs/DECISIONS.md V14; reports/stage_e5_harness_plan.md
  section 4 (L-E5-3, L-E5-5); the D.1f text reports/stage_d1f_confirmation_list.md 3.1-3.4.
- The cost table for the trip rebuild: reports/stage_e2a_costs.json (frozen); the trip fields (gross_cents, net_cents,
  contracts, open/close times); the vehicle's tick value and q_c from reports/stage_e2a_epsilon.json.

## Recompute and report, each item VERIFIED, VERIFIED WITH NOTES or DISCREPANCY
0. The run's inputs equal the hashed list: every record's harness_sha256, cluster_freeze_sha256, member, ordinal, window,
   s_x and legs equal the list; the run used v6 and freeze 7abcde17; the record set is exactly the list's run trials.
1. Per trial: theta_hat, UCB95, SE_boot with the list's seed (20260923 + ordinal; stationary bootstrap, mean block 5, B =
   10,000, np.quantile 0.95, SE = std ddof 0), p_upper, n_days, n_trips, trips per day, theta_hat / r, UCB95 / r, achieved null
   power Phi(eps_X / SE_boot - 1.645) at the list's eps_X, and the null status (null, null by inactivity, inconclusive). To
   1e-9 relative where deterministic.
2. Holm at K = 9 over the Tier A p (one Tier A trial: alpha 0.05 / 9).
3. DSR at N = 150 with V14 (c) (one Tier A trial: the Sharpe variance over every run trial's daily Sharpe, population
   variance, moments on each trial's own series), daily t (mean / (population sd / sqrt n)) > 3.0, PBO on 8 contiguous blocks
   by L-E5-3 (one Tier A trial: over every run trial, aligned on the union of window dates with zeros off each trial's dates).
4. The Tier A chain verdict and wording ("edge candidate, composite pending" only if Holm, DSR, t and PBO all pass; never
   "edge"), and the cluster's null statement and per-exposure resolution table (NULL_CRITERIA_E 1, 6, 7).
5. One trial's daily series rebuilt from its trip list and the cost table: K4-ngpre-01 NG (every trip's net = gross minus
   the modelled cost; daily sum per window date divided by contracts, in ticks per contract; equal to the record's series).
   If time allows, one MCL trial too.
6. Anything in the verdict rendering (the .md) that misstates the JSON.

## Output
reports/stage_e5_k4_audit.md, append "Part 2: the recomputation": a table item | verdict | evidence, then per-trial tables
of your figures beside the verdict file's. Scratch under reports/stage_e5_briefs/audit_k4_part2/.

## Return
The report path, a summary of at most 200 words (each item's verdict, any DISCREPANCY in one line), and anything unchecked.
