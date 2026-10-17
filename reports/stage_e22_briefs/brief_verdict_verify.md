# Brief: VerdictVerifier-<KX>-FableXHigh, Stage E.22 Part A step 4: recompute every verdict figure of one cluster

Lead: E.22 (Opus 5.5, xhigh). You are independent: recompute in YOUR OWN code (numpy, math, statistics), never by
calling screening/stage_e_verdict.py. You may call funnel.null_generator.stationary_bootstrap_indices (the program's
frozen generator), and funnel.multiple_comparisons for DSR, t and PBO only as a second check after your own formula,
saying which you used. Read-only except your report and your scratch folder; no commits, no web, no bar data reads
(the records and trip lists carry everything; reading a store is out of scope). Context hygiene: read files by section,
print summaries, not rows. Precedent: reports/E.5_RETURN.md Task C6 and reports/stage_e5_briefs/C6_confirm_auditor_k4.md.

## Inputs (KX = your cluster: K5, K8, K3 or K6; kx lower case)
- The hashed list: reports/stage_e22_kx_confirmation_list.json (commit ccd7fa7 "E.22 confirmation lists"; sha256 in that
  commit's message) and reports/stage_e22_confirmation_list.md.
- The run: reports/stage_e22_confirm_kx/ (member records KX_<member>_confirmation.json, their _trips.json, the cluster
  record), the marker reports/stage_e22_KX_RUN_ONCE.json, the log reports/stage_e22_briefs/confirm_kx.log.
- The verdicts under audit: reports/stage_e22_kx_verdict.json (the verdict module's output).
- The criteria: docs/NULL_CRITERIA_E.md sections 1, 3, 5, 6, 7; docs/STAGE_E_DESIGN.md D5 (298-346); docs/DECISIONS.md V14;
  the lead's rulings reports/stage_e22_briefs/partA_rulings.md (K = 5 R-E22-A10, N = 533 R-E22-A11, a Tier A trial with
  no record at p = 1 R-E22-A13, K8's variance rule R-E22-A14, R-E22-A16); E.5's L-E5-3 and L-E5-5.
- Costs for a trip rebuild: reports/stage_e2a_costs.json (frozen), trip fields (gross_cents, net_cents, contracts, times),
  tick value and q_c from reports/stage_e2a_epsilon.json. Price paths: reports/stage_e22_price_paths.json (MGC trials run
  on GC bars with MGC's costs and tick value; check one MGC trip's cents use MGC's $1.00 tick, not GC's $10.00).

## Recompute and report, each item VERIFIED, VERIFIED WITH NOTES or DISCREPANCY
0. The run's inputs equal the hashed list: every record's harness_sha256 (v13 dd2bcc60...), cluster_freeze_sha256, member,
   ordinal, window, s_x, legs and price_path equal the list; the marker names this list's sha256; the record set is exactly
   the list's run trials (not-run trials: no run record; a not-run record, if any, carries exactly the declared label).
1. Per run trial: theta_hat, UCB95, SE_boot with the list's seed (20260923 + ordinal; stationary bootstrap, mean block 5,
   B = 10,000, np.quantile 0.95, SE = std ddof 0), p_upper, n_days, n_trips, trips per day r, theta_hat / r, UCB95 / r,
   achieved null power Phi(eps_X / SE_boot - 1.645) at the list's eps_X, and the null status (null, null by inactivity,
   inconclusive). To 1e-9 relative where deterministic.
2. Holm at K = 5 over the cluster's Tier A p (a not-run Tier A trial at p = 1; family size = the screened Tier A size), and
   the descriptive Holm at K = 9 the verdict reports (holm_descriptive_k9).
3. DSR at N = 533 with the Sharpe variance over Tier A (two or more Tier A series) or over every run trial's daily Sharpe
   (V14 c), population variance, moments on each trial's own series; daily t (mean / (population sd / sqrt n)) > 3.0
   one-sided; CSCV PBO on 8 contiguous blocks by L-E5-3 (over Tier A with two or more series, else every run trial, aligned
   on the union of window dates with zeros off each trial's dates).
4. The Tier A chain verdict and wording ("edge candidate, composite pending" only if Holm, DSR, t and PBO all pass; never
   "edge"), and the cluster's null statement with the per-exposure resolution table (NULL_CRITERIA_E 1, 6, 7): which
   trials are covered, which are not covered and why.
5. One Tier A trial's daily series rebuilt from its trip list and the cost table (every trip's net = gross minus the
   modelled cost; daily sum per window date divided by contracts, in ticks per contract), equal to the record's series.
   For K5 and K8 the Tier A trial runs on GC bars: confirm the cents use MGC's tick value and costs.
6. Anything in the verdict JSON that contradicts the list or the records.

## Output
reports/stage_e22_verify_kx.md: a table item | verdict | evidence, then per-trial tables of your figures beside the
verdict file's (at least the Tier A trials and any trial whose status is not "null"; all trials if time allows), and
what you could not check. Scratch: reports/stage_e22_briefs/verify_kx/.

## Return
The report path, a summary of at most 200 words (each item's verdict; any DISCREPANCY in one line), and anything unchecked.
A DISCREPANCY is resolved by the lead finding the code error, never by a second run.
