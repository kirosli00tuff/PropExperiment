# Stage D.1f (run) independent verification

Verifier: NumberVerifier-FableXHigh (Fable 5.1, xhigh), a second model's check of the numbers the
Opus-written runner produced. Date: 2026-09-23, 17:55 to 18:05 PDT. Nothing was fixed or re-run;
every finding is reported as found.

## 1. What was checked, inputs, method, tolerances

### 1.1 Scope
The five mandatory items of the brief, then the two cheap extras:
1. UCB95 and achieved null power for the binding member of every class (list section 4), exact
   reproduction plus an independent bootstrap re-implementation; every member with UCB95 in
   [30.6, 37.4] or SE_boot within 10% of 34/2.4865 = 13.674 (none exists, see item 1.8).
2. Holm step-down over the 58 Tier A one-sided p-values (ordering, thresholds, cut-off).
3. The "edge" record: no member has status "edge", so the negative was verified for all 58 Tier A
   members against the five conditions of list 3.2 (Holm, composite, DSR at N = 58, t > 3, PBO).
4. S: V_ref, M*, S and the 0.15/0.40 sensitivities from the logged medians, then every monthly
   median re-computed from the parquets through the program's loaders.
5. Class verdicts, blocking members, "null by inactivity" labels and the class statement fields.
6. Extras: exact re-computation of theta_hat, UCB95, SE_boot, p and power for all 101 members; the
   37 trial daily series rebuilt from raw_trial_series.

### 1.2 Inputs (read-only) and their sha256
| File | sha256 |
|---|---|
| reports/stage_d1f_step5_start_rule.json | 4f2870f51a3551651466e919ba2941d11908c45807ba0ee72be63fb71d9bb11c |
| reports/stage_d1f_step7_list_run.json | ec25209e85e56b47019a58bfa3c564309444ac356b038d493bdc37f77379ea26 |
| reports/stage_d1f_tier_a.json | 88f4695eb35a23112ee6110cf56208287067c3100104df4926151e5e241e979b |
| reports/stage_d1f_tier_b.json | 560b5810059100a44bbcee370f197e7e669351c786e2a254c3fb6af81e5ca778 |
| reports/stage_d1f_decisions.json | 5ff5da4ab35f7ead0cdde1a2a40685db8e39464e04211bfe078849f9312f51cb |
| reports/stage_d1f_confirmation_list.md (frozen rules, 3.1-3.6 and 4 read) | c19cbac191c497a10b5cc756e96510999f13f27c4ac1aa72593aeabf1125147c |
| docs/NULL_CRITERIA.md (sections 2.3, 3, 4.1, 6, 7 read) | 6f69e318c96edf0a58956856c881ec3e1b8c68d89e1c836b3d54cfbf0e3497e2 |

The list and criteria hashes match the `list_sha256` and `criteria_sha256` fields stored in all
five runner JSONs; the runner JSONs' cross-references (`list_run_sha256` in decisions.json =
step 7 file hash; `outputs_sha256.tier_a/tier_b` in decisions.json = the tier file hashes) match
the hashes above. Manifest sha256 in every JSON: d3bd21e50b14c014cf854c3a239fae6d204834e4d360c1cf2b20df7a18b7a3c2.

### 1.3 Method
- Script: reports/_d1f_run_verify_scratch.py (single process, `os.nice(10)`,
  OPENBLAS_NUM_THREADS=1; 58 s wall, peak memory well under 1 GB). Its results JSON went to the
  session scratchpad (d1f_run_verify_results.json), not the repo.
- Allowed helpers used: funnel.null_generator.stationary_bootstrap_indices (exact reproduction
  only), funnel.multiple_comparisons (compared against my own implementations),
  strategy.research._d1b_accounting._moments (compared only), data.research_bars.load_research_bars
  and load_confirmation_bars (item 4). No strategy.research._d1f_* module was imported; no git,
  Databento or data.holdout call; nothing sealed was read. Environment: numpy 2.5.3, pandas 3.0.5.
- Member daily series: taken from step7 `members[*].daily` on the member's own dates
  (`dates_ref` window = 1,055 dates, statistic = 998 dates); checked identical (max |diff| = 0,
  same dates, same activity) to `daily_ticks_per_micro` in tier_a.json / tier_b.json for all 101.
- Exact reproduction (list 3.1): theta_hat = np.mean(d); one fresh
  np.random.default_rng(20260921) per member; 10,000 draws of
  stationary_bootstrap_indices(rng, n, n, 5.0); means[i] = d[idx].mean(); UCB95 =
  np.quantile(means, 0.95) (linear); SE_boot = np.std(means) (ddof 0);
  p = (1 + #{means - theta_hat >= theta_hat}) / 10,001; power = Phi(34 / SE_boot - 1.645) with
  Phi from math.erf.
- Independent bootstrap (own code, no funnel call): geometric block lengths with mean 5
  (numpy geometric, support 1, 2, ...), uniform block starts on 0..n-1, circular wrap-around,
  blocks concatenated and truncated to n; seed 20260923; 10,000 resamples.
- Holm, BH, moments (population sd), DSR (Bailey and Lopez de Prado with the stdlib
  statistics.NormalDist inverse CDF), t, CSCV PBO (70 symmetric splits of 8 blocks of
  1055 // 8 = 131 dates; aligned on the full window date list with 0 off a member's own dates):
  all re-implemented in the scratch script, then compared with the funnel helpers and the stored
  values.
- Start rule: V_ref = median of the 14 reference medians; M* = earliest month whose median and
  every later month's median through 2024-02 are >= fraction x V_ref; S = that month's first trade
  date with bars. Monthly medians from the parquets: the bar's ts_event (UTC ns) converted to
  America/Chicago, clock minute in 08:30..14:59, month = the trade_date's month, median of volume.

### 1.4 Tolerances
- Exact reproduction: 1e-9 on theta_hat, UCB95, SE_boot, p, power (brief). Achieved: 0.0 on
  every field for every member (bit-identical).
- Independent bootstrap (Monte Carlo): two independent 10,000-draw estimates of the same
  resampling distribution differ by noise only. For the bootstrap SE the sd of one estimate is
  about SE/sqrt(2B) (near-normal resample means), so the sd of the difference is SE/sqrt(B) =
  0.0100 SE. For the 95th percentile the sd of one estimate is sqrt(0.05 x 0.95 / B) / f(x_0.95)
  with f(x_0.95) = phi(1.645)/SE = 0.1031/SE, giving 0.0211 SE; the sd of the difference is
  0.0299 SE. Tolerance = 4 sd: |dSE| <= 0.040 SE_boot and |dUCB95| <= 0.120 SE_boot (false-alarm
  probability about 6e-5 per member under normality). The observed z-scores are also reported.
- Holm and BH thresholds, DSR, t, Sharpe variance, PBO: 1e-9 (1e-12 on ranks/rejections, which
  are exact). Moments: 1e-9.
- Monthly medians and first trade dates: exact (medians of integer volumes are k or k + 0.5).

## 2. Verdict table

Abbreviations: "runner" = value stored in the runner JSONs; "verifier" = my re-computation;
"max |diff|" = the largest absolute difference over the row's sub-items. UCB95, SE and theta_hat
are net ticks per micro per day.

| Item | Quantity | Runner value | Verifier value | Max abs diff | Verdict | Note |
|---|---|---|---|---|---|---|
| 1.1 C1 binding, A-H4 rth leg (Tier A trial, n = 1055, 1005 trips) | theta_hat / UCB95 / SE_boot / p / power (exact method) | 2.774453080568719 / 9.5831241706161 / 4.115605420595676 / 0.24817518248175183 / 0.9999999999815774 | identical | 0.0 | VERIFIED | null condition met (UCB95 < 34, power >= 0.80) |
| 1.1 | independent bootstrap UCB95 / SE_boot (seed 20260923) | 9.583124 / 4.115605 | 9.517049 / 4.127890 | 0.066075 (z 0.54) / 0.012284 (z 0.30) | VERIFIED | tolerance 0.4922 / 0.1646; power from the independent SE = 1.0000 |
| 1.2 C2 binding, G3.RTH.5 (Tier B statistic, n = 998, 995 events) | theta_hat / UCB95 / SE_boot / p / power | 0.7450400801603135 / 7.726587675350684 / 4.2853487877571625 / 0.43095690430956907 / 0.9999999998402516 | identical | 0.0 | VERIFIED | null condition met |
| 1.2 | independent UCB95 / SE_boot | 7.726588 / 4.285349 | 7.829669 / 4.257249 | 0.103082 (z 0.80) / 0.028100 (z 0.66) | VERIFIED | tolerance 0.5125 / 0.1714 |
| 1.3 C3 binding, F1_1_h1_RTH (Tier B statistic, n = 998, 381,534 events) | theta_hat / UCB95 / SE_boot / p / power | -796.8424248497033 / -786.1892319639319 / 6.502226832488117 / 1.0 / 0.9998307995939268 | identical | 0.0 | VERIFIED | null condition met |
| 1.3 | independent UCB95 / SE_boot | -786.189232 / 6.502227 | -786.213324 / 6.447254 | 0.024092 (z 0.12) / 0.054973 (z 0.85) | VERIFIED | tolerance 0.7777 / 0.2601; power from the independent SE = 0.999857 |
| 1.4 C4 binding, F2_4_15min_vol_tercile_top (Tier B statistic, n = 998, 8,151 events) | theta_hat / UCB95 / SE_boot / p / power | -23.01764529058118 / -16.485188376753523 / 4.070787447028942 / 1.0 / 0.9999999999900797 | identical | 0.0 | VERIFIED | null condition met |
| 1.4 | independent UCB95 / SE_boot | -16.485188 / 4.070787 | -16.520657 / 4.129093 | 0.035468 (z 0.29) / 0.058306 (z 1.43) | VERIFIED | tolerance 0.4869 / 0.1628 |
| 1.5 C5 binding, E-H1 scheduled macro drift (Tier A trial, n = 1055, 112 trips) | theta_hat / UCB95 / SE_boot / p / power | 1.1518483412322273 / 2.8326017061611366 / 1.053322671352247 / 0.1371862813718628 / 1.0 | identical | 0.0 | VERIFIED | null condition met; smallest p of the family |
| 1.5 | independent UCB95 / SE_boot | 2.832602 / 1.053323 | 2.814071 / 1.046861 | 0.018530 (z 0.59) / 0.006462 (z 0.61) | VERIFIED | tolerance 0.1260 / 0.0421 |
| 1.6 C6 binding, C-H4 passive-fill reversal (Tier A trial, n = 1055, 90,418 trips) | theta_hat / UCB95 / SE_boot / p / power | -186.6302028436019 / -177.17742938388622 / 5.940868005305353 / 1.0 / 0.9999772943954095 | identical | 0.0 | VERIFIED | both null conditions met under the trade-through model; label "null under the pessimistic fill model" is the list 3.5 wording |
| 1.6 | independent UCB95 / SE_boot | -177.177429 / 5.940868 | -176.979500 / 5.958016 | 0.197929 (z 1.11) / 0.017148 (z 0.29) | VERIFIED | tolerance 0.7105 / 0.2376; power from the independent SE = 0.999976 |
| 1.7 C7 binding, H6 prior-close location follow-through (Tier A trial, n = 1055, 504 trips) | theta_hat / UCB95 / SE_boot / p / power | -3.167222748815168 / 1.490205687203787 / 2.862656703709439 / 0.8640135986401359 / 1.0 | identical | 0.0 | VERIFIED | null condition met |
| 1.7 | independent UCB95 / SE_boot | 1.490206 / 2.862657 | 1.477816 / 2.849342 | 0.012390 (z 0.14) / 0.013315 (z 0.47) | VERIFIED | tolerance 0.3424 / 0.1145 |
| 1.8 near-threshold members (30.6 <= UCB95 <= 37.4 or 12.31 <= SE_boot <= 15.04) | count | not listed by the runner | 0 of 101 | n/a | VERIFIED | largest UCB95 over all 101 is 9.5831 (A-H4 rth leg); largest SE_boot is 7.5795 (F4_4_round_number_multiples_of_50, power 0.99775, the lowest power); no member is within 10% of either threshold |
| 2.1 Holm, one-sided p for all 58 Tier A members | p-values | tier_a.json p_one_sided | exact method | 0.0 | VERIFIED | all 58 identical to the runner |
| 2.2 Holm ordering, thresholds | rank, threshold = 0.05/(58 - rank + 1) | tier_a.json holm.rank / holm.threshold | own Holm | ranks: 58/58 equal; thresholds: 0.0 | VERIFIED | Appendix A. Tie at ranks 5/6 (A-H4 eth leg and H3 inside-day, p = 3575/10001 both); the runner's tie order equals mine |
| 2.3 Holm cut-off and rejected set | smallest p vs first threshold | rejected = [] (decisions.json family.holm, alpha 0.05, m 58) | min p = 0.1371862813718628 (E-H1) vs 0.05/58 = 0.000862; step-down stops at rank 1; rejected = [] | n/a | VERIFIED | no Tier A member is rejected; per-member reject flags 58/58 equal |
| 3.1 members with status "edge" | count | 0 (summary.passing_confirmation = [], holm_rejected = []) | 0 | n/a | VERIFIED | status counts: Tier A 58 null, Tier B 43 null (runner); the negative is verified in 3.2-3.7 |
| 3.2 population variance of the 58 Tier A daily Sharpes | sharpe_variance | 0.1150606519783947 | 0.1150606519783947 | 0.0 | VERIFIED | Sharpe = mean / population sd from _moments; my re-implementation vs the helper: max diff 3.4e-13 on any moment of any member; vs stored moments 3.4e-13 |
| 3.3 E[max SR] under the null at N = 58 | expected_max_daily_sharpe_under_null | 0.7912401110461237 | 0.7912401108953087 (stdlib inverse CDF); 0.7912401110461237 via the helper | 1.5e-10 | VERIFIED | the difference is the helper's Acklam ppf approximation (|err| < 1.15e-9) |
| 3.4 DSR at N = 58 per Tier A member | dsr_n58 | 0.0 for all 58 | 0.0 for all 58 (largest z = -24.44, F3_3_overnight_to_close_momentum; E-H1 z = -24.46) | 0.0 | VERIFIED WITH NOTES | Phi(z) underflows to exactly 0.0 at z <= -24 in double precision; every member fails DSR > 0.95 by a wide margin. See note N2 |
| 3.5 t (one-sided, mean / (population sd / sqrt(n))) per Tier A member | t_stat | tier_a.json accounting.t_stat | own t; helper t identical | 7.1e-15 | VERIFIED | largest t = 1.1265 (E-H1); no member exceeds 3.0; 8 of 58 are positive, 50 negative |
| 3.6 PBO over the 58 Tier A series (8 blocks of 131 dates, 70 splits) | pbo / winner mean OOS / P(winner OOS > 0) | 0.44285714285714284 / -804.4268285714288 / 0.35714285714285715 | 0.44285714285714284 / -804.4268285714285 / 0.35714285714285715 | 3e-13 | VERIFIED | own CSCV and the helper agree; PBO < 0.5 holds, so the PBO condition is the only one of the five that any member passes |
| 3.7 five edge conditions per Tier A member | holm_reject, composite_pass, dsr_above_0_95, t_above_3, pbo_below_0_5, passes | tier_a.json edge_checks | own flags | 58/58 members equal on all six fields | VERIFIED | every member fails exactly four conditions (Holm, composite, DSR, t) and passes only PBO; no member meets all five, so no D.2 discussion item arises (Appendix B) |
| 3.8 reported-only figures at N = 101 | sharpe_variance / PBO / winner mean OOS / P(OOS > 0) | 2.640650337124024 / 0.6 / -1918.3969714285727 / 0.11428571428571428 | 2.640650337124024 / 0.6 / -1918.3969714285718 / 0.11428571428571428 | 9e-13 | VERIFIED | not a criterion (list 3.2); checked because it was cheap |
| 4.1 V_ref from the 14 logged reference medians | median | 1763.0 | 1763.0 (sorted middle pair 1709.0, 1817.0) | 0.0 | VERIFIED | 14 months 2025-04..2026-05 |
| 4.2 binding rule (0.25) | threshold / M* / S | 440.75 / 2020-02 / 2020-02-03 | 440.75 / 2020-02 / 2020-02-03 | 0.0 | VERIFIED | 2020-01 median 383.0 < 440.75; 2020-02 median 569.0 and every later month (minimum 813.0, 2021-06) >= 440.75 |
| 4.3 sensitivity 0.15 | threshold / M* / S | 264.45 / 2020-01 / 2020-01-02 | 264.45 / 2020-01 / 2020-01-02 | 0.0 | VERIFIED | 2019-12 median 201.0 < 264.45 |
| 4.4 sensitivity 0.40 | threshold / M* / S | 705.2 / 2020-03 / 2020-03-02 | 705.2 / 2020-03 / 2020-03-02 | 0.0 | VERIFIED | 2020-02 median 569.0 < 705.2; 2020-03 median 1735.0, later minimum 813.0 |
| 4.5 reference monthly medians from the research parquet (load_research_bars, 425,339 rows) | 14 medians | step5 reference_monthly_medians | re-computed | 0.0 on all 14; no month missing | VERIFIED | e.g. 2025-04 3204.5, 2025-07 1248.0, 2026-05 1709.0 |
| 4.6 extension monthly medians from the confirmation parquet (load_confirmation_bars, 1,695,822 rows) | 58 medians 2019-05..2024-02 | step5 extension_monthly_medians | re-computed | 0.0 on all 58; no month missing or extra | VERIFIED | e.g. 2019-05 351.0, 2020-01 383.0, 2020-02 569.0, 2020-03 1735.0, 2024-02 1145.5 |
| 4.7 first trade date with bars per extension month | 58 dates | step5 extension_first_trade_dates | re-computed | all 58 equal | VERIFIED | S = 2020-02-03 is the first 2020-02 trade date with bars |
| 4.8 rule re-applied to the parquet-derived medians | V_ref / M* / S / sensitivities | as 4.1-4.4 | 1763.0 / 2020-02 / 2020-02-03 / 2020-01-02 and 2020-03-02 | 0.0 | VERIFIED | the logged inputs and the parquet inputs give the same S |
| 4.9 window date list | trade dates >= S in the confirmation parquet | step7 window_dates (1,055) | 1,055 dates, list identical | 0 | VERIFIED | statistic dates 998 = 1055 - 57 excluded (exclusion set itself not re-derived, note N5) |
| 5.1 per-member null condition (UCB95 < 34 and power >= 0.80 and activity > 0 and SE_boot > 0) | null.meets for 101 members | 101 True | 101 True | 0 mismatches | VERIFIED | smallest SE_boot 0.0558 (E-H3), no zero; smallest activity 16 (E-H3), no zero |
| 5.2 members blocking any class (not meeting the null) | list | members_not_meeting_null = [] and inconclusive = [] in every class | [] | n/a | VERIFIED | no member is inconclusive under 3.4 |
| 5.3 class verdicts C1-C5, C7 | verdict | null x 6 | null x 6 (every Tier A and Tier B member of each class meets both conditions) | n/a | VERIFIED | class membership in the JSONs equals list 2.3 for all 7 classes |
| 5.4 class verdict C6 | verdict | "inconclusive until Stage D.1g (list 3.5)" | same by design | n/a | VERIFIED | C-H4 meets the null under the trade-through model, which list 3.5 says cannot establish the C6 null |
| 5.5 "null by inactivity" labels (< 30 trips or events while meeting the null) | members | E-H3 quarterly witching short (16 trips); C5 label "null by inactivity" | E-H3 only; no other member below 30 (next lowest H3 inside-day, 80 trips) | n/a | VERIFIED | C5 statement must carry the label (NULL_CRITERIA 7); C1-C4, C6, C7 labels None |
| 5.6 class frequency (median trades per window day of the class's trial members) | C1 / C2 / C3 / C4 / C5 / C6 / C7 | 0.9369668246445497 / 0.9327014218009478 / 38.250236966824644 / 0.7369668246445498 / 0.0962085308056872 / 85.7042654028436 / 0.262085308056872 | identical | 0.0 | VERIFIED | trial-member sets equal the frozen list's (6 / 10 / 4 / 6 / 4 / 1 / 6 trials) |
| 5.7 epsilon per trade = 34 / class frequency | C1 / C2 / C3 / C4 / C5 / C6 / C7 | 36.2873 / 36.4533 / 0.88888 / 46.1350 / 353.3990 / 0.39671 / 129.7288 | identical | 0.0 | VERIFIED | |
| 5.8 least active member and count | C1 / C2 / C3 / C4 / C5 / C6 / C7 | A-H3 388 / B-H4 441 / G4.RTH.60 957 / D-H1 397 / E-H3 16 / C-H4 90418 / H3 inside-day 80 | identical | 0 | VERIFIED | over Tier A and Tier B members of the class |
| 5.9 largest per-trade UCB95 = max over members of UCB95 / (activity per own date) | C1 / C2 / C3 / C4 / C5 / C6 / C7 | A-H4 rth leg 10.0599 / G3.RTH.5 7.7499 / F3_3_overnight_to_close_momentum 3.8368 / F5_1_relvol_tercile_top -0.3140 / E-H1 26.6821 / C-H4 -2.0673 / H3 inside-day 30.3125 | identical | 0.0 | VERIFIED | per_trade.ucb95 of all 101 members also matches at 1e-9 |
| 5.10 runner step-8 claim (C1-C5, C7 null; C6 inconclusive until D.1g; void = False) | class_verdicts / void | as stated | reproduced from my numbers under 3.3-3.5 | n/a | VERIFIED | the verdict claim follows from the verified numbers and the frozen rules; void_reasons = [] (continuity not re-checked, note N5) |
| 6.1 all 101 members, exact method | max abs deviation per field: theta_hat / UCB95 / SE_boot / p / power | tier files | re-computed | 0.0 / 0.0 / 0.0 / 0.0 / 0.0 | VERIFIED | bit-identical for every member and field (Appendix C); n_activity and activity_per_day equal for all 101 |
| 6.2 trial daily series rebuilt from raw_trial_series (37 trials) | per-micro daily = sum over the date's trips of trip_pnl_usd / (1.25 x trip_micros) | step7 members[*].daily | rebuilt | 2.27e-13 (daily per micro); 3.41e-13 (daily_net_usd) | VERIFIED | trip counts per date equal daily_activity for all 37; n_trips equals n_activity; sizes: 29 trials at 1 micro, H1-H6 at 2, D-H2 in 1..5, RT7 in 1..4 (list 3.1) |
| 6.3 Tier B anomaly BH (q = 0.1, m = 43), non-mandatory | rank / threshold / reject for 43 members | tier_b.json anomaly.bh | own BH | ranks 43/43 equal; thresholds 0.0; rejected = [] | VERIFIED | checked because it was cheap; the sign-reversal BH on the gross series was not checked (note N5) |

Overall: every mandatory item is VERIFIED; item 3.4 (DSR) is VERIFIED WITH NOTES for the
underflow remark only. No DISCREPANCY was found.

## 3. Notes

- N1 (exact reproduction). The bit-identical match on all 101 members shows the runner used
  the list 3.1 procedure exactly as written (helper, seed, one rng per member, quantile method,
  ddof 0, the centred p-value count). My implementation was written from the list text and the
  brief, not from the runner's code (strategy.research._d1f_* was neither imported nor used as a
  template).
- N2 (DSR = 0.0). With the population variance of the 58 daily Sharpes at 0.1151 and N = 58,
  E[max SR] under the null is 0.791 per day, far above every observed daily Sharpe (largest
  0.0347, E-H1), so z <= -24.4 for every member and Phi(z) is exactly 0.0 in double precision.
  The variance is driven by the strongly negative high-activity members (C-H1 Sharpe about -1.8,
  F1-type Tier B members are excluded from the 58). This is the frozen rule applied as written;
  it changes no verdict because every member already fails Holm and the composite.
- N3 (independent bootstrap). All seven binding members agree with the exact figures within
  the stated Monte Carlo tolerance; the largest z-scores are 1.43 (F2_4 SE) and 1.11 (C-H4
  UCB95), consistent with pure resampling noise. The null decision (UCB95 < 34, power >= 0.80)
  is unchanged under the independent SE for all seven.
- N4 (statistic daily series). The 64 statistic members' daily series (21 Tier A, 43 Tier B)
  cannot be rebuilt from the inputs: step 7 stores their per-date sums and event counts but not
  the per-event v values. They were taken as given; everything downstream of them was
  re-computed.
- N5 (not checked, outside the brief). The step-6 continuity check (void = False rests on it),
  the composition of the 57 excluded statistic dates (48 roll-blackout + vendor-degraded, per
  step 4b), the year slices (list 3.6, descriptive only), the Tier B sign-reversal test
  (F1_1_h30_ETH flagged), and the composite screening verdicts themselves (taken from the
  stored `composite` field; all 58 Tier A members are "fail").
- N6 (Holm tie). A-H4 eth leg and H3 inside-day opening-range breakout share p = 3575/10001;
  the runner ranked them 5 and 6 in that order, as did my (p, id) sort. Ties do not affect the
  step-down because it stops at rank 1.
- N7 (cross-file consistency). Step 7 daily series, dates and activity equal the tier files for
  all 101 members; decisions.json class member lists equal the class fields of the members and
  the frozen list 2.3; n_after_d1f = 58 = 31 + 6 Family H + 21 statistics (37 Tier A trials + 21
  Tier A statistics).

## Appendix A. Holm ordering over the 58 Tier A one-sided p-values (verifier = runner)

| rank | member | one-sided p (verifier = runner) | Holm threshold 0.05/(58-rank+1) | reject |
|---|---|---|---|---|
| 1 | E-H1 scheduled macro drift | 0.137186 | 0.000862 | False |
| 2 | A-H4 rth leg | 0.248175 | 0.000877 | False |
| 3 | F3_3_overnight_to_close_momentum | 0.262374 | 0.000893 | False |
| 4 | H4 bottom-tercile prior range, breakout | 0.291971 | 0.000909 | False |
| 5 | A-H4 eth leg | 0.357464 | 0.000926 | False |
| 6 | H3 inside-day opening-range breakout | 0.357464 | 0.000943 | False |
| 7 | F6_1_overnight_range_position | 0.460554 | 0.000962 | False |
| 8 | H1 NR4 opening-range breakout | 0.478952 | 0.000980 | False |
| 9 | H2 NR7 opening-range breakout | 0.595440 | 0.001000 | False |
| 10 | F3_2_bucket12_bucket13 | 0.650735 | 0.001020 | False |
| 11 | H5 top-tercile prior range, opening-range fade | 0.658434 | 0.001042 | False |
| 12 | A-H2 rth close window (sell) | 0.679932 | 0.001064 | False |
| 13 | F3_3_opening_30min_to_close_momentum | 0.692631 | 0.001087 | False |
| 14 | A-H3 weekend effect | 0.832317 | 0.001111 | False |
| 15 | E-H3 quarterly witching short | 0.847315 | 0.001136 | False |
| 16 | E-H2 post-release momentum | 0.853415 | 0.001163 | False |
| 17 | B-H1 opening-range breakout (hold 75) | 0.855514 | 0.001190 | False |
| 18 | RT2 B-H1 ORB 5-min bars (hold 15 bars) | 0.859014 | 0.001220 | False |
| 19 | B-H3 fade leg | 0.861914 | 0.001250 | False |
| 20 | H6 prior-close location follow-through | 0.864014 | 0.001282 | False |
| 21 | G5.RTH.30 | 0.868613 | 0.001316 | False |
| 22 | B-H4 narrow-range breakout | 0.888011 | 0.001351 | False |
| 23 | B-H2 prior-day stop cascade | 0.935606 | 0.001389 | False |
| 24 | RT3 B-H3 breakout leg 5-min bars | 0.938806 | 0.001429 | False |
| 25 | F3_2_bucket10_bucket11 | 0.939006 | 0.001471 | False |
| 26 | F3_2_bucket02_bucket03 | 0.949005 | 0.001515 | False |
| 27 | RT4 B-H3 fade leg 5-min bars | 0.950405 | 0.001563 | False |
| 28 | A-H1 european-open overnight drift | 0.950805 | 0.001613 | False |
| 29 | F3_2_bucket06_bucket07 | 0.958204 | 0.001667 | False |
| 30 | G3.RTH.15 | 0.959604 | 0.001724 | False |
| 31 | B-H3 breakout leg | 0.968603 | 0.001786 | False |
| 32 | F3_2_bucket05_bucket06 | 0.973003 | 0.001852 | False |
| 33 | G2.RTH.30 | 0.975002 | 0.001923 | False |
| 34 | F3_2_bucket07_bucket08 | 0.975102 | 0.002000 | False |
| 35 | F3_2_bucket01_bucket02 | 0.975702 | 0.002083 | False |
| 36 | A-H2 rth close window (buy) | 0.980902 | 0.002174 | False |
| 37 | G5.RTH.15 | 0.989701 | 0.002273 | False |
| 38 | F3_2_bucket04_bucket05 | 0.996000 | 0.002381 | False |
| 39 | F4_4_round_number_multiples_of_100 | 0.998000 | 0.002500 | False |
| 40 | D-H4 overnight gap fade | 0.998600 | 0.002632 | False |
| 41 | F3_2_bucket08_bucket09 | 0.999500 | 0.002778 | False |
| 42 | E-H4 turn-of-month long | 0.999700 | 0.002941 | False |
| 43 | B-H1 opening-range breakout (hold 5) | 1.000000 | 0.003125 | False |
| 44 | C-H1 magnitude-conditioned reversal | 1.000000 | 0.003333 | False |
| 45 | C-H2 post-spike exhaustion fade | 1.000000 | 0.003571 | False |
| 46 | C-H3 close-location-value reversal | 1.000000 | 0.003846 | False |
| 47 | C-H4 passive-fill reversal | 1.000000 | 0.004167 | False |
| 48 | D-H1 trailing-vol regime gate | 1.000000 | 0.004545 | False |
| 49 | D-H2 inverse-vol sizing | 1.000000 | 0.005000 | False |
| 50 | D-H3 range-compression gate | 1.000000 | 0.005556 | False |
| 51 | F4_1_rth_open_crossing | 1.000000 | 0.006250 | False |
| 52 | G1.RTH.5 | 1.000000 | 0.007143 | False |
| 53 | G2.ETH.30 | 1.000000 | 0.008333 | False |
| 54 | G2.ETH.5 | 1.000000 | 0.010000 | False |
| 55 | RT1 B-H1 ORB 5-min bars (hold 1 bar) | 1.000000 | 0.012500 | False |
| 56 | RT5 C-H2 spike fade 5-min bars | 1.000000 | 0.016667 | False |
| 57 | RT6 D-H1 daily-vol regime gate | 1.000000 | 0.025000 | False |
| 58 | RT7 D-H2 daily-vol sizing | 1.000000 | 0.050000 | False |

## Appendix B. The five edge conditions per Tier A member (verifier values; PBO = 0.4429 for the family)

| member | class | theta_hat | UCB95 | p | Holm reject | composite | DSR (N=58) | t | PBO < 0.5 | failing conditions | runner edge_checks equal |
|---|---|---|---|---|---|---|---|---|---|---|---|
| E-H1 scheduled macro drift | C5 | 1.1518 | 2.8326 | 0.137186 | False | fail | 0 (z -24.46) | 1.1265 | True | holm_reject, composite_pass, dsr_above_0_95, t_above_3 | True |
| A-H4 rth leg | C1 | 2.7745 | 9.5831 | 0.248175 | False | fail | 0 (z -24.99) | 0.6309 | True | holm_reject, composite_pass, dsr_above_0_95, t_above_3 | True |
| F3_3_overnight_to_close_momentum | C3 | 1.0101 | 3.7023 | 0.262374 | False | fail | 0 (z -24.44) | 0.6339 | True | holm_reject, composite_pass, dsr_above_0_95, t_above_3 | True |
| H4 bottom-tercile prior range, breakout | C7 | 1.0414 | 4.1403 | 0.291971 | False | fail | 0 (z -25.09) | 0.5320 | True | holm_reject, composite_pass, dsr_above_0_95, t_above_3 | True |
| A-H4 eth leg | C1 | 1.0809 | 6.0515 | 0.357464 | False | fail | 0 (z -25.35) | 0.3366 | True | holm_reject, composite_pass, dsr_above_0_95, t_above_3 | True |
| H3 inside-day opening-range breakout | C7 | 0.3966 | 2.2986 | 0.357464 | False | fail | 0 (z -25.09) | 0.3324 | True | holm_reject, composite_pass, dsr_above_0_95, t_above_3 | True |
| F6_1_overnight_range_position | C2 | 0.1973 | 3.3774 | 0.460554 | False | fail | 0 (z -24.88) | 0.0927 | True | holm_reject, composite_pass, dsr_above_0_95, t_above_3 | True |
| H1 NR4 opening-range breakout | C7 | 0.1209 | 3.1772 | 0.478952 | False | fail | 0 (z -25.63) | 0.0614 | True | holm_reject, composite_pass, dsr_above_0_95, t_above_3 | True |
| H2 NR7 opening-range breakout | C7 | -0.3572 | 2.1044 | 0.595440 | False | fail | 0 (z -25.87) | -0.2213 | True | holm_reject, composite_pass, dsr_above_0_95, t_above_3 | True |
| F3_2_bucket12_bucket13 | C3 | -0.6192 | 2.1117 | 0.650735 | False | fail | 0 (z -25.39) | -0.3879 | True | holm_reject, composite_pass, dsr_above_0_95, t_above_3 | True |
| H5 top-tercile prior range, opening-range fade | C7 | -0.9396 | 2.8008 | 0.658434 | False | fail | 0 (z -25.97) | -0.4133 | True | holm_reject, composite_pass, dsr_above_0_95, t_above_3 | True |
| A-H2 rth close window (sell) | C1 | -0.7231 | 1.7039 | 0.679932 | False | fail | 0 (z -26.27) | -0.4648 | True | holm_reject, composite_pass, dsr_above_0_95, t_above_3 | True |
| F3_3_opening_30min_to_close_momentum | C3 | -0.8713 | 1.8344 | 0.692631 | False | fail | 0 (z -25.54) | -0.5645 | True | holm_reject, composite_pass, dsr_above_0_95, t_above_3 | True |
| A-H3 weekend effect | C1 | -2.5228 | 1.7897 | 0.832317 | False | fail | 0 (z -26.86) | -0.9868 | True | holm_reject, composite_pass, dsr_above_0_95, t_above_3 | True |
| E-H3 quarterly witching short | C5 | -0.0558 | 0.0331 | 0.847315 | False | fail | 0 (z -28.47) | -0.9943 | True | holm_reject, composite_pass, dsr_above_0_95, t_above_3 | True |
| E-H2 post-release momentum | C5 | -0.3354 | 0.2039 | 0.853415 | False | fail | 0 (z -27.05) | -0.9908 | True | holm_reject, composite_pass, dsr_above_0_95, t_above_3 | True |
| B-H1 opening-range breakout (hold 75) | C2 | -2.3331 | 1.1187 | 0.855514 | False | fail | 0 (z -26.88) | -1.1262 | True | holm_reject, composite_pass, dsr_above_0_95, t_above_3 | True |
| RT2 B-H1 ORB 5-min bars (hold 15 bars) | C2 | -1.9380 | 1.0194 | 0.859014 | False | fail | 0 (z -26.83) | -1.0529 | True | holm_reject, composite_pass, dsr_above_0_95, t_above_3 | True |
| B-H3 fade leg | C2 | -1.4078 | 0.7073 | 0.861914 | False | fail | 0 (z -26.73) | -1.0952 | True | holm_reject, composite_pass, dsr_above_0_95, t_above_3 | True |
| H6 prior-close location follow-through | C7 | -3.1672 | 1.4902 | 0.864014 | False | fail | 0 (z -27.07) | -1.0294 | True | holm_reject, composite_pass, dsr_above_0_95, t_above_3 | True |
| G5.RTH.30 | C2 | -1.6894 | 0.7920 | 0.868613 | False | fail | 0 (z -27.10) | -1.2091 | True | holm_reject, composite_pass, dsr_above_0_95, t_above_3 | True |
| B-H4 narrow-range breakout | C2 | -0.8462 | 0.2779 | 0.888011 | False | fail | 0 (z -26.96) | -1.1348 | True | holm_reject, composite_pass, dsr_above_0_95, t_above_3 | True |
| B-H2 prior-day stop cascade | C2 | -1.2174 | 0.1012 | 0.935606 | False | fail | 0 (z -27.19) | -1.4833 | True | holm_reject, composite_pass, dsr_above_0_95, t_above_3 | True |
| RT3 B-H3 breakout leg 5-min bars | C2 | -1.8721 | 0.1105 | 0.938806 | False | fail | 0 (z -27.25) | -1.5649 | True | holm_reject, composite_pass, dsr_above_0_95, t_above_3 | True |
| F3_2_bucket10_bucket11 | C3 | -1.8707 | 0.0323 | 0.939006 | False | fail | 0 (z -27.11) | -1.5844 | True | holm_reject, composite_pass, dsr_above_0_95, t_above_3 | True |
| F3_2_bucket02_bucket03 | C3 | -2.0245 | 0.0507 | 0.949005 | False | fail | 0 (z -26.87) | -1.5514 | True | holm_reject, composite_pass, dsr_above_0_95, t_above_3 | True |
| RT4 B-H3 fade leg 5-min bars | C2 | -1.9821 | 0.0033 | 0.950405 | False | fail | 0 (z -27.23) | -1.6561 | True | holm_reject, composite_pass, dsr_above_0_95, t_above_3 | True |
| A-H1 european-open overnight drift | C1 | -1.3904 | 0.0530 | 0.950805 | False | fail | 0 (z -26.87) | -1.6820 | True | holm_reject, composite_pass, dsr_above_0_95, t_above_3 | True |
| F3_2_bucket06_bucket07 | C3 | -1.5743 | -0.0944 | 0.958204 | False | fail | 0 (z -26.64) | -1.7274 | True | holm_reject, composite_pass, dsr_above_0_95, t_above_3 | True |
| G3.RTH.15 | C2 | -6.7992 | -0.0457 | 0.959604 | False | fail | 0 (z -26.28) | -1.6454 | True | holm_reject, composite_pass, dsr_above_0_95, t_above_3 | True |
| B-H3 breakout leg | C2 | -2.4106 | -0.3410 | 0.968603 | False | fail | 0 (z -27.53) | -1.8844 | True | holm_reject, composite_pass, dsr_above_0_95, t_above_3 | True |
| F3_2_bucket05_bucket06 | C3 | -1.8990 | -0.2283 | 0.973003 | False | fail | 0 (z -26.39) | -1.8181 | True | holm_reject, composite_pass, dsr_above_0_95, t_above_3 | True |
| G2.RTH.30 | C2 | -3.5242 | -0.7190 | 0.975002 | False | fail | 0 (z -26.68) | -1.9634 | True | holm_reject, composite_pass, dsr_above_0_95, t_above_3 | True |
| F3_2_bucket07_bucket08 | C3 | -1.8165 | -0.2840 | 0.975102 | False | fail | 0 (z -26.60) | -1.8945 | True | holm_reject, composite_pass, dsr_above_0_95, t_above_3 | True |
| F3_2_bucket01_bucket02 | C3 | -3.1244 | -0.4752 | 0.975702 | False | fail | 0 (z -27.26) | -2.0419 | True | holm_reject, composite_pass, dsr_above_0_95, t_above_3 | True |
| A-H2 rth close window (buy) | C1 | -3.0633 | -0.5703 | 0.980902 | False | fail | 0 (z -27.01) | -1.9691 | True | holm_reject, composite_pass, dsr_above_0_95, t_above_3 | True |
| G5.RTH.15 | C2 | -2.2475 | -0.5899 | 0.989701 | False | fail | 0 (z -25.45) | -2.3116 | True | holm_reject, composite_pass, dsr_above_0_95, t_above_3 | True |
| F3_2_bucket04_bucket05 | C3 | -2.7899 | -1.1403 | 0.996000 | False | fail | 0 (z -27.78) | -2.6249 | True | holm_reject, composite_pass, dsr_above_0_95, t_above_3 | True |
| F4_4_round_number_multiples_of_100 | C2 | -14.9429 | -8.2990 | 0.998000 | False | fail | 0 (z -62.33) | -3.2934 | True | holm_reject, composite_pass, dsr_above_0_95, t_above_3 | True |
| D-H4 overnight gap fade | C4 | -1.2134 | -0.5784 | 0.998600 | False | fail | 0 (z -29.91) | -3.1531 | True | holm_reject, composite_pass, dsr_above_0_95, t_above_3 | True |
| F3_2_bucket08_bucket09 | C3 | -3.5890 | -2.0019 | 0.999500 | False | fail | 0 (z -30.24) | -3.5771 | True | holm_reject, composite_pass, dsr_above_0_95, t_above_3 | True |
| E-H4 turn-of-month long | C5 | -0.6059 | -0.3818 | 0.999700 | False | fail | 0 (z -47.57) | -4.7150 | True | holm_reject, composite_pass, dsr_above_0_95, t_above_3 | True |
| B-H1 opening-range breakout (hold 5) | C2 | -2.1439 | -1.2522 | 1.000000 | False | fail | 0 (z -31.41) | -3.7298 | True | holm_reject, composite_pass, dsr_above_0_95, t_above_3 | True |
| C-H1 magnitude-conditioned reversal | C3 | -275.9694 | -267.9152 | 1.000000 | False | fail | 0 (z -39.11) | -57.6256 | True | holm_reject, composite_pass, dsr_above_0_95, t_above_3 | True |
| C-H2 post-spike exhaustion fade | C3 | -64.7425 | -61.3734 | 1.000000 | False | fail | 0 (z -27.53) | -35.6381 | True | holm_reject, composite_pass, dsr_above_0_95, t_above_3 | True |
| C-H3 close-location-value reversal | C3 | -89.3155 | -85.1059 | 1.000000 | False | fail | 0 (z -25.72) | -37.5462 | True | holm_reject, composite_pass, dsr_above_0_95, t_above_3 | True |
| C-H4 passive-fill reversal | C6 | -186.6302 | -177.1774 | 1.000000 | False | fail | 0 (z -43.61) | -40.3888 | True | holm_reject, composite_pass, dsr_above_0_95, t_above_3 | True |
| D-H1 trailing-vol regime gate | C4 | -0.9222 | -0.5429 | 1.000000 | False | fail | 0 (z -30.73) | -4.2586 | True | holm_reject, composite_pass, dsr_above_0_95, t_above_3 | True |
| D-H2 inverse-vol sizing | C4 | -2.5843 | -1.7956 | 1.000000 | False | fail | 0 (z -30.96) | -5.3899 | True | holm_reject, composite_pass, dsr_above_0_95, t_above_3 | True |
| D-H3 range-compression gate | C4 | -24.2357 | -21.6265 | 1.000000 | False | fail | 0 (z -34.82) | -15.3616 | True | holm_reject, composite_pass, dsr_above_0_95, t_above_3 | True |
| F4_1_rth_open_crossing | C2 | -4.3822 | -2.4294 | 1.000000 | False | fail | 0 (z -28.76) | -3.2715 | True | holm_reject, composite_pass, dsr_above_0_95, t_above_3 | True |
| G1.RTH.5 | C3 | -35.2462 | -30.5080 | 1.000000 | False | fail | 0 (z -41.32) | -13.5210 | True | holm_reject, composite_pass, dsr_above_0_95, t_above_3 | True |
| G2.ETH.30 | C2 | -6.6506 | -4.3519 | 1.000000 | False | fail | 0 (z -27.19) | -4.5489 | True | holm_reject, composite_pass, dsr_above_0_95, t_above_3 | True |
| G2.ETH.5 | C2 | -17.8369 | -16.1484 | 1.000000 | False | fail | 0 (z -24.57) | -15.8012 | True | holm_reject, composite_pass, dsr_above_0_95, t_above_3 | True |
| RT1 B-H1 ORB 5-min bars (hold 1 bar) | C2 | -2.4678 | -1.5798 | 1.000000 | False | fail | 0 (z -31.38) | -4.4306 | True | holm_reject, composite_pass, dsr_above_0_95, t_above_3 | True |
| RT5 C-H2 spike fade 5-min bars | C3 | -21.2189 | -18.8157 | 1.000000 | False | fail | 0 (z -28.05) | -13.1502 | True | holm_reject, composite_pass, dsr_above_0_95, t_above_3 | True |
| RT6 D-H1 daily-vol regime gate | C4 | -1.3628 | -0.8860 | 1.000000 | False | fail | 0 (z -33.10) | -5.2823 | True | holm_reject, composite_pass, dsr_above_0_95, t_above_3 | True |
| RT7 D-H2 daily-vol sizing | C4 | -2.5713 | -1.7610 | 1.000000 | False | fail | 0 (z -32.03) | -5.2430 | True | holm_reject, composite_pass, dsr_above_0_95, t_above_3 | True |

## Appendix C. All 101 members, exact method (verifier values; every field equals the runner's bit for bit)

| member | tier | kind | class | n | activity | theta_hat | UCB95 | SE_boot | p | power | null meets (verifier) | runner status | runner labels |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A-H1 european-open overnight drift | A | trial | C1 | 1055 | 1007 | -1.3904 | 0.0530 | 0.8624 | 0.950805 | 1.000000 | True | null | - |
| A-H2 rth close window (buy) | A | trial | C1 | 1055 | 972 | -3.0633 | -0.5703 | 1.4989 | 0.980902 | 1.000000 | True | null | - |
| A-H2 rth close window (sell) | A | trial | C1 | 1055 | 972 | -0.7231 | 1.7039 | 1.4948 | 0.679932 | 1.000000 | True | null | - |
| A-H3 weekend effect | A | trial | C1 | 1055 | 388 | -2.5228 | 1.7897 | 2.6324 | 0.832317 | 1.000000 | True | null | - |
| A-H4 eth leg | A | trial | C1 | 1055 | 1007 | 1.0809 | 6.0515 | 3.0397 | 0.357464 | 1.000000 | True | null | - |
| A-H4 rth leg | A | trial | C1 | 1055 | 1005 | 2.7745 | 9.5831 | 4.1156 | 0.248175 | 1.000000 | True | null | - |
| B-H1 opening-range breakout (hold 5) | A | trial | C2 | 1055 | 1000 | -2.1439 | -1.2522 | 0.5595 | 1.000000 | 1.000000 | True | null | - |
| B-H1 opening-range breakout (hold 75) | A | trial | C2 | 1055 | 1000 | -2.3331 | 1.1187 | 2.1462 | 0.855514 | 1.000000 | True | null | - |
| B-H2 prior-day stop cascade | A | trial | C2 | 1055 | 810 | -1.2174 | 0.1012 | 0.7972 | 0.935606 | 1.000000 | True | null | - |
| B-H3 breakout leg | A | trial | C2 | 1055 | 991 | -2.4106 | -0.3410 | 1.2675 | 0.968603 | 1.000000 | True | null | - |
| B-H3 fade leg | A | trial | C2 | 1055 | 991 | -1.4078 | 0.7073 | 1.2811 | 0.861914 | 1.000000 | True | null | - |
| B-H4 narrow-range breakout | A | trial | C2 | 1055 | 441 | -0.8462 | 0.2779 | 0.6920 | 0.888011 | 1.000000 | True | null | - |
| C-H1 magnitude-conditioned reversal | A | trial | C3 | 1055 | 149035 | -275.9694 | -267.9152 | 4.9045 | 1.000000 | 1.000000 | True | null | - |
| C-H2 post-spike exhaustion fade | A | trial | C3 | 1055 | 33126 | -64.7425 | -61.3734 | 2.0432 | 1.000000 | 1.000000 | True | null | - |
| C-H3 close-location-value reversal | A | trial | C3 | 1055 | 47582 | -89.3155 | -85.1059 | 2.5419 | 1.000000 | 1.000000 | True | null | - |
| D-H1 trailing-vol regime gate | A | trial | C4 | 1055 | 397 | -0.9222 | -0.5429 | 0.2367 | 1.000000 | 1.000000 | True | null | - |
| D-H2 inverse-vol sizing | A | trial | C4 | 1055 | 1006 | -2.5843 | -1.7956 | 0.4806 | 1.000000 | 1.000000 | True | null | - |
| D-H3 range-compression gate | A | trial | C4 | 1055 | 9817 | -24.2357 | -21.6265 | 1.6185 | 1.000000 | 1.000000 | True | null | - |
| D-H4 overnight gap fade | A | trial | C4 | 1055 | 568 | -1.2134 | -0.5784 | 0.3968 | 0.998600 | 1.000000 | True | null | - |
| E-H1 scheduled macro drift | A | trial | C5 | 1055 | 112 | 1.1518 | 2.8326 | 1.0533 | 0.137186 | 1.000000 | True | null | - |
| E-H2 post-release momentum | A | trial | C5 | 1055 | 91 | -0.3354 | 0.2039 | 0.3251 | 0.853415 | 1.000000 | True | null | - |
| E-H3 quarterly witching short | A | trial | C5 | 1055 | 16 | -0.0558 | 0.0331 | 0.0558 | 0.847315 | 1.000000 | True | null | null by inactivity |
| E-H4 turn-of-month long | A | trial | C5 | 1055 | 196 | -0.6059 | -0.3818 | 0.1476 | 0.999700 | 1.000000 | True | null | - |
| C-H4 passive-fill reversal | A | trial | C6 | 1055 | 90418 | -186.6302 | -177.1774 | 5.9409 | 1.000000 | 0.999977 | True | null | null under the pessimistic fill model |
| RT1 B-H1 ORB 5-min bars (hold 1 bar) | A | trial | C2 | 1055 | 984 | -2.4678 | -1.5798 | 0.5500 | 1.000000 | 1.000000 | True | null | - |
| RT2 B-H1 ORB 5-min bars (hold 15 bars) | A | trial | C2 | 1055 | 984 | -1.9380 | 1.0194 | 1.8204 | 0.859014 | 1.000000 | True | null | - |
| RT3 B-H3 breakout leg 5-min bars | A | trial | C2 | 1055 | 984 | -1.8721 | 0.1105 | 1.2026 | 0.938806 | 1.000000 | True | null | - |
| RT4 B-H3 fade leg 5-min bars | A | trial | C2 | 1055 | 984 | -1.9821 | 0.0033 | 1.2022 | 0.950405 | 1.000000 | True | null | - |
| RT5 C-H2 spike fade 5-min bars | A | trial | C3 | 1055 | 10614 | -21.2189 | -18.8157 | 1.4538 | 1.000000 | 1.000000 | True | null | - |
| RT6 D-H1 daily-vol regime gate | A | trial | C4 | 1055 | 520 | -1.3628 | -0.8860 | 0.2937 | 1.000000 | 1.000000 | True | null | - |
| RT7 D-H2 daily-vol sizing | A | trial | C4 | 1055 | 987 | -2.5713 | -1.7610 | 0.4974 | 1.000000 | 1.000000 | True | null | - |
| H1 NR4 opening-range breakout | A | trial | C7 | 1055 | 266 | 0.1209 | 3.1772 | 1.8838 | 0.478952 | 1.000000 | True | null | - |
| H2 NR7 opening-range breakout | A | trial | C7 | 1055 | 155 | -0.3572 | 2.1044 | 1.5043 | 0.595440 | 1.000000 | True | null | - |
| H3 inside-day opening-range breakout | A | trial | C7 | 1055 | 80 | 0.3966 | 2.2986 | 1.1716 | 0.357464 | 1.000000 | True | null | - |
| H4 bottom-tercile prior range, breakout | A | trial | C7 | 1055 | 336 | 1.0414 | 4.1403 | 1.9121 | 0.291971 | 1.000000 | True | null | - |
| H5 top-tercile prior range, opening-range fade | A | trial | C7 | 1055 | 287 | -0.9396 | 2.8008 | 2.2442 | 0.658434 | 1.000000 | True | null | - |
| H6 prior-close location follow-through | A | trial | C7 | 1055 | 504 | -3.1672 | 1.4902 | 2.8627 | 0.864014 | 1.000000 | True | null | - |
| F3_2_bucket07_bucket08 | A | statistic | C3 | 998 | 962 | -1.8165 | -0.2840 | 0.9255 | 0.975102 | 1.000000 | True | null | - |
| F6_1_overnight_range_position | A | statistic | C2 | 998 | 992 | 0.1973 | 3.3774 | 1.8973 | 0.460554 | 1.000000 | True | null | - |
| F3_3_opening_30min_to_close_momentum | A | statistic | C3 | 998 | 960 | -0.8713 | 1.8344 | 1.6551 | 0.692631 | 1.000000 | True | null | - |
| F3_2_bucket08_bucket09 | A | statistic | C3 | 998 | 962 | -3.5890 | -2.0019 | 0.9893 | 0.999500 | 1.000000 | True | null | - |
| F3_3_overnight_to_close_momentum | A | statistic | C3 | 998 | 963 | 1.0101 | 3.7023 | 1.6671 | 0.262374 | 1.000000 | True | null | - |
| F4_4_round_number_multiples_of_100 | A | statistic | C2 | 998 | 3091 | -14.9429 | -8.2990 | 4.4591 | 0.998000 | 1.000000 | True | null | - |
| F3_2_bucket01_bucket02 | A | statistic | C3 | 998 | 992 | -3.1244 | -0.4752 | 1.5922 | 0.975702 | 1.000000 | True | null | - |
| F3_2_bucket10_bucket11 | A | statistic | C3 | 998 | 963 | -1.8707 | 0.0323 | 1.1855 | 0.939006 | 1.000000 | True | null | - |
| F4_1_rth_open_crossing | A | statistic | C2 | 998 | 2068 | -4.3822 | -2.4294 | 1.1984 | 1.000000 | 1.000000 | True | null | - |
| F3_2_bucket02_bucket03 | A | statistic | C3 | 998 | 995 | -2.0245 | 0.0507 | 1.2578 | 0.949005 | 1.000000 | True | null | - |
| F3_2_bucket05_bucket06 | A | statistic | C3 | 998 | 993 | -1.8990 | -0.2283 | 0.9950 | 0.973003 | 1.000000 | True | null | - |
| F3_2_bucket04_bucket05 | A | statistic | C3 | 998 | 994 | -2.7899 | -1.1403 | 1.0222 | 0.996000 | 1.000000 | True | null | - |
| F3_2_bucket06_bucket07 | A | statistic | C3 | 998 | 992 | -1.5743 | -0.0944 | 0.9061 | 0.958204 | 1.000000 | True | null | - |
| F3_2_bucket12_bucket13 | A | statistic | C3 | 998 | 963 | -0.6192 | 2.1117 | 1.6288 | 0.650735 | 1.000000 | True | null | - |
| G2.RTH.30 | A | statistic | C2 | 998 | 2501 | -3.5242 | -0.7190 | 1.7483 | 0.975002 | 1.000000 | True | null | - |
| G1.RTH.5 | A | statistic | C3 | 998 | 14779 | -35.2462 | -30.5080 | 2.8880 | 1.000000 | 1.000000 | True | null | - |
| G2.ETH.30 | A | statistic | C2 | 998 | 4412 | -6.6506 | -4.3519 | 1.3928 | 1.000000 | 1.000000 | True | null | - |
| G2.ETH.5 | A | statistic | C2 | 998 | 9584 | -17.8369 | -16.1484 | 1.0501 | 1.000000 | 1.000000 | True | null | - |
| G5.RTH.15 | A | statistic | C2 | 998 | 936 | -2.2475 | -0.5899 | 0.9896 | 0.989701 | 1.000000 | True | null | - |
| G5.RTH.30 | A | statistic | C2 | 998 | 882 | -1.6894 | 0.7920 | 1.5174 | 0.868613 | 1.000000 | True | null | - |
| G3.RTH.15 | A | statistic | C2 | 998 | 987 | -6.7992 | -0.0457 | 4.0097 | 0.959604 | 1.000000 | True | null | - |
| F1_1_h1_RTH | B | statistic | C3 | 998 | 381534 | -796.8424 | -786.1892 | 6.5022 | 1.000000 | 0.999831 | True | null | - |
| F1_1_h5_RTH | B | statistic | C3 | 998 | 75491 | -144.0391 | -136.8939 | 4.3532 | 1.000000 | 1.000000 | True | null | - |
| F1_1_h15_RTH | B | statistic | C3 | 998 | 24488 | -58.8213 | -51.7909 | 4.2829 | 1.000000 | 1.000000 | True | null | - |
| F1_1_h30_RTH | B | statistic | C3 | 998 | 11736 | -23.5771 | -16.7489 | 4.1227 | 1.000000 | 1.000000 | True | null | - |
| F1_1_h60_RTH | B | statistic | C3 | 998 | 4870 | -17.5127 | -12.4622 | 3.0769 | 1.000000 | 1.000000 | True | null | - |
| F1_1_h1_ETH | B | statistic | C3 | 998 | 923298 | -1875.2132 | -1866.8970 | 4.9797 | 1.000000 | 1.000000 | True | null | - |
| F1_1_h5_ETH | B | statistic | C3 | 998 | 182289 | -360.9918 | -354.6877 | 3.8789 | 1.000000 | 1.000000 | True | null | - |
| F1_1_h15_ETH | B | statistic | C3 | 998 | 58945 | -115.2314 | -109.4502 | 3.5590 | 1.000000 | 1.000000 | True | null | - |
| F1_1_h30_ETH | B | statistic | C3 | 998 | 28184 | -69.4592 | -64.1526 | 3.2889 | 1.000000 | 1.000000 | True | null | - |
| F1_1_h60_ETH | B | statistic | C3 | 998 | 12377 | -33.4464 | -28.2600 | 3.1515 | 1.000000 | 1.000000 | True | null | - |
| F2_4_15min_vol_tercile_bottom | B | statistic | C4 | 998 | 8151 | -17.3223 | -14.3874 | 1.8346 | 1.000000 | 1.000000 | True | null | - |
| F2_4_15min_vol_tercile_top | B | statistic | C4 | 998 | 8151 | -23.0176 | -16.4852 | 4.0708 | 1.000000 | 1.000000 | True | null | - |
| F3_2_bucket03_bucket04 | B | statistic | C3 | 998 | 994 | -1.4733 | 0.4515 | 1.1475 | 0.899610 | 1.000000 | True | null | - |
| F3_2_bucket09_bucket10 | B | statistic | C3 | 998 | 963 | -0.7144 | 1.2325 | 1.1559 | 0.734227 | 1.000000 | True | null | - |
| F3_2_bucket11_bucket12 | B | statistic | C3 | 998 | 963 | 0.1884 | 1.8912 | 1.0279 | 0.432557 | 1.000000 | True | null | - |
| F4_2_prior_rth_close_crossing | B | statistic | C2 | 998 | 1822 | -5.2379 | -2.8692 | 1.4240 | 0.999800 | 1.000000 | True | null | - |
| F4_4_round_number_multiples_of_50 | B | statistic | C2 | 998 | 6171 | -29.1631 | -17.9132 | 7.5795 | 0.999500 | 0.997750 | True | null | - |
| F5_1_relvol_tercile_bottom | B | statistic | C4 | 998 | 3833 | -7.2080 | -4.7199 | 1.4921 | 1.000000 | 1.000000 | True | null | - |
| F5_1_relvol_tercile_top | B | statistic | C4 | 998 | 3833 | -6.2902 | -1.2060 | 3.1148 | 0.976502 | 1.000000 | True | null | - |
| F5_2_efficiency_tercile_bottom | B | statistic | C4 | 998 | 3915 | -6.1840 | -2.3980 | 2.2867 | 0.995800 | 1.000000 | True | null | - |
| F5_2_efficiency_tercile_top | B | statistic | C4 | 998 | 3913 | -7.8922 | -4.3159 | 2.1816 | 0.999900 | 1.000000 | True | null | - |
| F5_3_range_volume_residual | B | statistic | C4 | 998 | 11736 | -24.1092 | -17.4593 | 4.0259 | 1.000000 | 1.000000 | True | null | - |
| G1.ETH.5 | B | statistic | C3 | 998 | 36310 | -80.2055 | -74.8042 | 3.3635 | 1.000000 | 1.000000 | True | null | - |
| G2.RTH.5 | B | statistic | C2 | 998 | 7369 | -19.0707 | -16.5851 | 1.5242 | 1.000000 | 1.000000 | True | null | - |
| G3.RTH.5 | B | statistic | C2 | 998 | 995 | 0.7450 | 7.7266 | 4.2853 | 0.430957 | 1.000000 | True | null | - |
| G4.RTH.5 | B | statistic | C3 | 998 | 14785 | -28.5795 | -24.7478 | 2.4077 | 1.000000 | 1.000000 | True | null | - |
| G5.RTH.5 | B | statistic | C2 | 998 | 1012 | -1.9232 | -0.9833 | 0.5740 | 0.999800 | 1.000000 | True | null | - |
| G1.ETH.15 | B | statistic | C3 | 998 | 11938 | -28.6284 | -25.4804 | 1.9094 | 1.000000 | 1.000000 | True | null | - |
| G2.ETH.15 | B | statistic | C2 | 998 | 6121 | -10.2348 | -8.0740 | 1.2972 | 1.000000 | 1.000000 | True | null | - |
| G1.RTH.15 | B | statistic | C3 | 998 | 4793 | -15.0704 | -10.8801 | 2.5608 | 1.000000 | 1.000000 | True | null | - |
| G2.RTH.15 | B | statistic | C2 | 998 | 3943 | -9.9486 | -7.2022 | 1.6945 | 1.000000 | 1.000000 | True | null | - |
| G4.RTH.15 | B | statistic | C3 | 998 | 4801 | -13.7727 | -9.8525 | 2.4062 | 1.000000 | 1.000000 | True | null | - |
| G1.ETH.30 | B | statistic | C3 | 998 | 5853 | -10.2904 | -7.2178 | 1.8760 | 1.000000 | 1.000000 | True | null | - |
| G1.RTH.30 | B | statistic | C3 | 998 | 2306 | -8.4516 | -4.8380 | 2.2003 | 0.999800 | 1.000000 | True | null | - |
| G3.RTH.30 | B | statistic | C2 | 998 | 958 | 1.7271 | 7.2947 | 3.3794 | 0.305869 | 1.000000 | True | null | - |
| G4.RTH.30 | B | statistic | C3 | 998 | 2307 | -6.6360 | -3.0825 | 2.1839 | 0.998400 | 1.000000 | True | null | - |
| G1.ETH.60 | B | statistic | C3 | 998 | 2745 | -8.0020 | -5.1508 | 1.7463 | 1.000000 | 1.000000 | True | null | - |
| G2.ETH.60 | B | statistic | C2 | 998 | 2873 | -4.3908 | -1.9703 | 1.4643 | 0.999200 | 1.000000 | True | null | - |
| G1.RTH.60 | B | statistic | C3 | 998 | 969 | -2.9986 | -0.1982 | 1.6701 | 0.965003 | 1.000000 | True | null | - |
| G2.RTH.60 | B | statistic | C2 | 998 | 1183 | -0.8368 | 1.8511 | 1.6573 | 0.685531 | 1.000000 | True | null | - |
| G3.RTH.60 | B | statistic | C2 | 998 | 835 | 0.5833 | 5.3975 | 2.9458 | 0.419258 | 1.000000 | True | null | - |
| G4.RTH.60 | B | statistic | C3 | 998 | 957 | -2.4071 | 0.3344 | 1.6509 | 0.928507 | 1.000000 | True | null | - |
| G5.RTH.60 | B | statistic | C2 | 998 | 755 | -2.1954 | 0.1953 | 1.4580 | 0.934307 | 1.000000 | True | null | - |
