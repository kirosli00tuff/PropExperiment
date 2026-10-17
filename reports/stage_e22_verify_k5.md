# Stage E.22 Part A step 4: independent verification of the K5 confirmation verdict

VerdictVerifier-K5 (Fable 5.1, xhigh), 2026-10-16 18:33 to 18:41 PDT. Brief:
reports/stage_e22_briefs/brief_verdict_verify.md. Every figure below was recomputed in my own code
(reports/stage_e22_briefs/verify_k5/recompute.py, sha256 d9d0b7bc42d66847...; output
reports/stage_e22_briefs/verify_k5/recompute.json, sha256 45389aee3240186f...). The only program function
used for a figure is funnel.null_generator.stationary_bootstrap_indices (the frozen generator, allowed by
the brief); funnel.multiple_comparisons was called afterwards as a labelled second check.
screening/stage_e_verdict.py was read (sha256 54e10a296f4988d9..., unmodified in git) and never imported.
No bar data was read. Read-only except this report and the scratch folder.

Inputs: list reports/stage_e22_k5_confirmation_list.json (sha256 d2a230f3...; commit ccd7fa7, unmodified);
run reports/stage_e22_confirm_k5/ (11 member records, 11 trip files, cluster record) behind
reports/stage_e22_K5_RUN_ONCE.json (created 2026-10-17T01:28:18Z = 18:28:18 PDT); verdict
reports/stage_e22_k5_verdict.json (sha256 51061000f6b00efb..., written 18:31:49 PDT); log
reports/stage_e22_briefs/confirm_k5.log (11 members, 0 refused, rc 0); criteria docs/NULL_CRITERIA_E.md
1, 3, 5, 6, 7; docs/STAGE_E_DESIGN.md D5; DECISIONS V14; reports/stage_e22_briefs/partA_rulings.md
(R-E22-A1, A10, A11, A13); E.5 L-E5-3, L-E5-5; costs reports/stage_e2a_costs.json (sha256 f4360bb7...,
equal to the records' frozen_tables.costs), epsilon reports/stage_e2a_epsilon.json (4e2c7731..., equal),
sizes (280d7e9d..., equal), price paths reports/stage_e22_price_paths.json (860f4b11..., equal to every
record's price_path_declaration).

## 1. Item table

| item | verdict | evidence |
|---|---|---|
| 0. Run inputs equal the hashed list | VERIFIED WITH NOTES | All 11 records: harness_sha256 dd2bcc60..., cluster_freeze_sha256 1d0c974f..., member, ordinal, window "confirmation", s_x, legs, price_path (MGC -> GC on the six MGC trials and pmfix; {} on MHG) and schema equal the list, 0 field mismatches; no record outside the list. Marker names the list's sha256 d2a230f3... and harness dd2bcc60.... NOTE: the record set is 11, the list's run: true set is 8 (E.5 precedent: K4 ran 12 members with --all; the frozen verdict code's evaluate() says "the runner's --all runs every frozen member ... never used"). The three OC-H-excluded trials have records that carry exactly the declared runner label: cp1 MHG and cp2 MHG status excluded_before_screening, labels ["coverage_below_0.95"]; pmfix MGC status "run", labels ["mean_holding_below_10min"], a full 1174-day series and 1080 trips on confirmation bars, marked by the verdict "present and not used". Marker not_run [] and not_run_declaration null (nothing was declared not run to the runner). No verdict figure depends on these three records (checked: DSR variance set, PBO set, covered set, resolution table exclude them). Whether a confirmation-window run of an OC-H-excluded trial is acceptable under R-E22-A1 / L-E5-5 ("listed, not run") is the lead's call. |
| 1. Per run trial: theta_hat, UCB95, SE_boot, p_upper, n_days, n_trips, r, theta/r, UCB95/r, null power, status | VERIFIED | Seven records have a series (six covered MGC trials and pmfix). Seed 20260923 + ordinal equals the list's bootstrap_seed and the verdict's seed for every trial. For the six covered trials every figure equals the verdict's to 1e-9 relative (most bit-equal); status "null" for all six, as the verdict says (section 2 table). pmfix MGC figures are informational only (verdict: "not run"). |
| 2. Holm at K = 5 and descriptive K = 9 | VERIFIED | Tier A = {K5-fomc-01 MGC}, m = 1, p_upper 0.8938106189381062; alpha_5 = 0.01, threshold 0.01, not rejected; K = 9: alpha 0.005555..., not rejected. Both equal the verdict's holm and holm_descriptive_k9 blocks. Family size = the screened Tier A size (1); no Tier A trial was listed not run, so R-E22-A13's p = 1 rule has nothing to apply to. |
| 3. DSR at N = 533, daily t, CSCV PBO | VERIFIED | One Tier A series, so V14 (c): variance over all six run trials' daily Sharpes (population variance) = 0.002690051435367311; E[max SR] at N = 533 = 0.15931535117 (own Phi^-1 via statistics.NormalDist); fomc moments n 1174, mean -0.312947, pop sd 8.560670, skew -1.709, raw kurtosis 112.689, Sharpe -0.036556; DSR = 5.43493e-12; t = -1.252556637394689. PBO over the same six (L-E5-3), union of window dates 1174 (identical date lists), 8 blocks of 146 days (trailing 6 dropped), C(8,4) = 70 splits, PBO = 3/70 = 0.042857, winner mean OOS -438.487 ticks, P(winner OOS > 0) = 11/70. All equal the verdict's to 1e-9 relative. Second check: funnel.multiple_comparisons.deflated_sharpe_ratio, harvey_liu_zhu_verdict and probability_of_backtest_overfitting give the same three numbers. |
| 4. Tier A chain verdict, wording, null statement, resolution table | VERIFIED | Chain for fomc: Holm fail (first failing step), DSR 5e-12 fail, t -1.25 fail, PBO 0.043 pass -> "no edge"; equal to the verdict. No trial reads "edge" or "edge candidate" anywhere in the file. Statement: covered = the 8 run: true trials; not covered = cp1 MHG, cp2 MHG, pmfix MGC with reason "not run: excluded (not Tier A or B)" (L-E5-5); blocking = cp3-01 MHG and ovr-01 MHG, inconclusive -> "no statement". My own application of NULL_CRITERIA_E 1, 6, 7 gives the same sets and the same verdict. Resolution table equal: MGC eps 71 ticks = $71.00 at q_c 1, fewest trips fomc 34, largest UCB95 per trade fomc 3.2120588 ticks, no inactivity label, not covered pmfix; MHG eps 27 ticks = $67.50 at q_c 2, no covered trial with figures (fewest/largest null), not covered cp1 MHG, cp2 MHG. |
| 5. Tier A series rebuilt from trips and the cost table | VERIFIED | fomc: 34 trips, all 1 contract, all opened at 13:05 CT and closed at 13:15 CT on FOMC statement days. Release calendar check (reports/stage_e2b_release_calendar.json, the record's sha256 839f2437...): every open and close instant lies in [release, release + 30 min) of an FOMC instant that concerns MGC (34/34), so D8's event-window cost applies: per side ceil(round(1 x 1.8384635916853809 ticks x 100 cents, 6)) = 184 cents + commission 192 // 2 = 96 cents; round turn 560 cents. gross_cents - net_cents = 560 on 34/34 trips (0 match the regular 13:00 CT bucket at 1.1185 ticks/side). Daily sum of net_cents / 100 / tick value $1.00 / contracts equals the record's series on all 1174 dates (max abs diff 0.0); daily_net_usd = series x $1.00 on all dates; trips sum -$367.40 = series sum -367.4 ticks. MGC, not GC: commission $1.92 (GC $4.32), event side 1.838 ticks (GC 3.074), tick value $1.00 (GC $10.00) all from the MGC entry; 34/34 gross_cents are multiples of 100 (MGC tick = 100 cents) and only 4/34 are multiples of 1000, which rules out GC's $10.00 tick having been applied to the price moves. Epsilon table: MGC tick_value_usd 1.0, q_c 1, consistent. |
| 6. Verdict JSON vs list and records | VERIFIED | harness, freeze, k_holm 5, program_n 533 (program_n_check equal, registry 533), list_sha256 equal. Per trial: tier, run, labels, ordinal, q_c, vehicle, eps_ticks, d4_power, record_status, covered (= run and not by design), n_trips and n_days against the record: all equal on all 11. No contradiction found. |

## 2. The classification of K5-cp3-01 MHG and K5-ovr-01 MHG (the lead's question)

Plain answer: the classification "inconclusive, covered, blocking" follows both NULL_CRITERIA_E as written and
the frozen verdict code as written.

- The records: both are listed Tier B, run: true, labels ["source-overlap"], power "power sufficient"
  (supply 425 days). The runner returned status excluded_before_screening with labels
  ["coverage_below_0.95"], series null, screen null, power null; coverage MHG expected 123250 present 95337
  ratio 0.7735 (cp3) and expected 127500 present 98020 ratio 0.7688 (ovr); both round to 0.77. Trip files
  n_trips 0. (cp1 MHG and cp2 MHG, excluded at screening on the same label, show 0.63 on the same window.)
- NULL_CRITERIA_E 6: "Inconclusive: any member that neither passes confirmation nor meets both null
  conditions; one such member keeps its cluster out of the null statement (except section 1's
  pre-declared label)." A trial with no series has no UCB95 and no achieved power, so it meets neither
  null condition and did not pass confirmation: inconclusive. Section 1: "A cluster with any inconclusive
  member gets no statement, with one exception: a member labelled 'inconclusive by design' in its hashed
  confirmation list BEFORE the run". Neither trial carries that label in the hashed list, so the exception
  does not apply and the cluster gets no statement. The verdict's "no statement" is the reading the
  frozen criteria require.
- The code path (screening/stage_e_verdict.py under dd2bcc60): evaluate() -> check_record(): status is not
  "not_run", s_x {"MHG": "2022-06-01"} equals the list, status != "run" -> returns None (no refusal, by
  design). _trial_row(): series None and trial.run True -> status INCONCLUSIVE, reasons
  ["record status 'excluded_before_screening': no series"]. ListTrial.covered = run and not by_design =
  True. null_statement(): the two are in covered with status not in (null, null by inactivity) -> blocking
  -> NO_STATEMENT. The resolution table lists them under MHG neither as not covered (correct: they are
  covered) nor with figures (correct: none exist). The verdict file records exactly this.
- Observation for the lead, not a discrepancy: the D9 coverage check is a frozen harness step that runs
  only at run time, on the confirmation window's bars; the list's D4 power section for these two trials
  counted 425 supply days and could not see it. The outcome is a by-design consequence of the frozen
  code, not a code error, and a second run cannot change it. Whether a future list should carry a
  pre-declared coverage label for such trials (which would need a confirmation-window bar count before
  hashing, something the program's no-read rule forbids today) is a design question for the lead.

## 3. Per-trial table (mine beside the verdict file's; all 11 list trials)

Units: ticks per contract per day of the vehicle. "/" separates my figure from the file's; "all equal"
means every compared field within 1e-9 relative (seed, n_days, n_trips, theta_hat, UCB95, SE_boot, p_upper,
r, theta/r, UCB95/r, null power, status).

| ord | member | tier | list run | record status | file status | my status | n_days | n_trips | theta_hat (mine / file) | UCB95 (mine / file) | SE_boot (mine / file) | p_upper (mine / file) | r trips/day | theta/r | UCB95/r | null power | all equal |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | K5-cp1-01 MGC | B | yes | run | null | null | 1174 | 1132 | -3.205144804 / -3.205144804 | -2.107243612 / -2.107243612 | 0.6592992714 / 0.6592992714 | 1 / 1 | 0.964225 | -3.32406 | -2.18543 | 1.0 | yes |
| 2 | K5-cp1-01 MHG | excluded | no | excluded_before_screening | not run | not covered | - | - | - | - | - | - | - | - | - | - | no figures (no series) |
| 3 | K5-cp2-01 MGC | B | yes | run | null | null | 1174 | 1166 | -3.852666099 / -3.852666099 | -0.3416635434 / -0.3416635434 | 2.109069526 / 2.109069526 | 0.9692030797 / 0.9692030797 | 0.993186 | -3.8791 | -0.344008 | 1.0 | yes |
| 4 | K5-cp2-01 MHG | excluded | no | excluded_before_screening | not run | not covered | - | - | - | - | - | - | - | - | - | - | no figures (no series) |
| 5 | K5-cp3-01 MGC | B | yes | run | null | null | 1174 | 489 | -5.166678024 / -5.166678024 | -1.599770869 / -1.599770869 | 2.163165946 / 2.163165946 | 0.9916008399 / 0.9916008399 | 0.416525 | -12.4043 | -3.84076 | 1.0 | yes |
| 6 | K5-cp3-01 MHG | B | yes | excluded_before_screening (coverage 0.7735) | inconclusive | inconclusive (no series) | - | - | - | - | - | - | - | - | - | - | no figures (no series); blocking |
| 7 | K5-preauc-01 MGC | B | yes | run | null | null | 1174 | 1115 | -4.036763203 / -4.036763203 | -3.01450937 / -3.01450937 | 0.6180468283 / 0.6180468283 | 1 / 1 | 0.949744 | -4.25037 | -3.17402 | 1.0 | yes |
| 8 | K5-pmfix-01 MGC | excluded | no | run (label mean_holding_below_10min) | not run | (null, if it had been covered) | 1174 | 1080 | -3.277955707 / not used | -1.99869506 / not used | 0.7649235314 / not used | 1 / not used | 0.919932 | -3.56326 | -2.17266 | 1.0 | n/a: the verdict does not use this record |
| 9 | K5-fomc-01 MGC | A | yes | run | null | null | 1174 | 34 | -0.3129471891 / -0.3129471891 | 0.09302385009 / 0.09302385009 | 0.2504942906 / 0.2504942906 | 0.8938106189 / 0.8938106189 | 0.0289608 | -10.8059 | 3.21206 | 1.0 | yes |
| 10 | K5-ovr-01 MGC | B | yes | run | null | null | 1174 | 1221 | -5.572751278 / -5.572751278 | -2.892181005 / -2.892181005 | 1.655009913 / 1.655009913 | 0.99920008 / 0.99920008 | 1.04003 | -5.35824 | -2.78085 | 1.0 | yes |
| 11 | K5-ovr-01 MHG | B | yes | excluded_before_screening (coverage 0.7688) | inconclusive | inconclusive (no series) | - | - | - | - | - | - | - | - | - | - | no figures (no series); blocking |

Null power is 1.0 to display precision for every covered trial (eps 71 ticks against SE_boot of 0.25 to
2.16 ticks). fomc's 34 trips sit 4 above the inactivity floor of 30, so its status is "null", not "null by
inactivity"; its UCB95 per trade (+3.21 ticks) is the largest in the cluster and is the figure the
resolution table carries.

## 4. Edge chain (Tier A: K5-fomc-01 MGC), mine beside the file's

| step | mine | file | equal |
|---|---|---|---|
| Holm K = 5 (alpha_k 0.01, m 1) | p 0.8938106189381062 > 0.01, not rejected | same | yes |
| Holm K = 9 descriptive (alpha_k 0.005556) | not rejected | same | yes |
| composite | pending (V14 a) | "pending" | yes |
| Sharpe variance (pop.) over the six run trials | 0.002690051435367311 | 0.002690051435367311 | yes |
| E[max SR] at N = 533 | 0.15931535123 | 0.15931535117027432 | yes (1e-9 rel.) |
| DSR | 5.43493028359876e-12 | 5.43493028359876e-12 | yes |
| daily t (mean / (pop sd / sqrt n)) | -1.252556637394689 | -1.252556637394689 | yes |
| PBO (six strategies, 8 x 146 days, 70 splits) | 0.04285714285714286 | 0.04285714285714286 | yes |
| verdict | no edge; first failing step holm | "no edge", "holm" | yes |

Daily Sharpes entering the variance: cp1 -0.13734, cp2 -0.05322, cp3 -0.06874, preauc -0.18712,
fomc -0.03656, ovr -0.10190 (all negative; the variance is the spread of six negative Sharpes).

## 5. Statement and resolution, mine beside the file's

- verdict: "no statement" / "no statement".
- covered (8): cp1 MGC, cp2 MGC, cp3 MGC, cp3 MHG, preauc MGC, fomc MGC, ovr MGC, ovr MHG / same order.
- not covered (3): cp1 MHG, cp2 MHG, pmfix MGC, reason "not run: excluded (not Tier A or B)" / same.
- blocking (2): cp3 MHG, ovr MHG, inconclusive, "record status 'excluded_before_screening': no series" /
  same; edge_chain null for both (Tier B) / same.
- null_by_inactivity: [] / [].
- resolution: MGC {q_c 1, eps 71 ticks, $71.00/day, fewest trips fomc 34, largest UCB95/trade fomc
  3.2120588235294085, inactivity [], not covered [pmfix MGC]}; MHG {q_c 2, eps 27 ticks, $67.50/day,
  fewest null, largest null, inactivity [], not covered [cp1 MHG, cp2 MHG]} / equal field by field.

## 6. Observations for the lead (none changes a figure)

1. Item 0 note: 11 records for 8 run trials; pmfix MGC was executed on confirmation bars although the
   list says run: false (OC-H hold floor). The frozen code and the E.5 precedent both expect and ignore
   such records. Lead's call whether this is acceptable or needs a not-run declaration to the runner in
   future stages.
2. The two MHG Tier B trials fell to a run-time D9 coverage check that the hashed list could not
   pre-declare (section 2). "No statement" for K5 is the required reading of NULL_CRITERIA_E 1 and 6.
3. The MHG exposure has no covered trial with a series in this run, so nothing in K5 speaks to copper at
   eps 27 ticks.
4. fomc's daily series has raw kurtosis 112.7 and skew -1.7 (34 trading days out of 1174); DSR and t are
   both far from their thresholds regardless.

## 7. What I could not check

- The coverage ratios themselves (0.7735, 0.7688, 0.63, and the MGC trials' 0.9957 to 0.9998) and the
  gross_cents of every trip: both need bar reads, which the brief puts out of scope. I checked only their
  internal consistency (expected/present/ratio arithmetic; gross on the MGC tick grid).
- MHG's tick value ($1.25) and costs in a confirmation series: no MHG series exists in this run.
- The release calendar's correctness: I used the frozen file the record names (sha256 839f2437...) as
  given.
- The frozen generator stationary_bootstrap_indices is shared with the verdict code (allowed by the
  brief); a defect inside it would not be caught by this agreement. Everything downstream of its indices
  (means, quantile, std, p, power, status) is my own code.
- Series rebuild was done for the one Tier A trial the brief asks for; the five Tier B MGC trips files
  (0.2 to 0.6 MB each) were not rebuilt.
