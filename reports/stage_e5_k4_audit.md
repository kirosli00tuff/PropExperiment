# Stage E.5: K4-ngpre-01 audit (ConfirmAuditor-K4-FableXHigh)

Auditor: ConfirmAuditor-K4-FableXHigh (Fable 5.1, xhigh). Brief: reports/stage_e5_briefs/C3_confirm_auditor_k4.md.
Independent of every author checked (ReleaseChecker-OpusMed, MemberCoder-OpusXHigh, the lead's freeze write).
Read-only on the repository except this file and reports/stage_e5_briefs/audit_k4_*. No web, no confirmation-window
run, no commits, no freeze write. Holdout `unlocks_logged` 0 at start and end; REGISTRATION.md 0 bytes.

## Part 1: the table amendment

Written 2026-09-27, 19:15 PDT. Scratch: reports/stage_e5_briefs/audit_k4_scratch/ (compare_tables.py, the HEAD
copies of the module and freeze) and reports/stage_e5_briefs/audit_k4_research/ (the research re-run).

Summary of verdicts:

| # | Check | Verdict |
|---|---|---|
| 1 | NGS lost exactly the five rows; every other table and constant unchanged | VERIFIED |
| 2 | Each drop right against the saved captures; 12 keep rows spot-checked | VERIFIED WITH NOTES |
| 3 | New freeze differs from the old only in `_releases.py`'s hash; `verify_cluster_code` passes | VERIFIED |
| 4 | Research series unchanged under harness v6 with the new freeze | VERIFIED |
| 5 | Test file applies both checks, pins the E.5 check's sha256; `pytest` passes | VERIFIED |
| Q | The stored "(lead decides drop vs correction)" wording | No correctness problem; one note below |

### Check 1: the diff is exactly the five drops. VERIFIED

Method: `git show HEAD:strategy/members/k4/_releases.py` saved to scratch, both versions imported side by side
(audit_k4_scratch/compare_tables.py) and every module-level table compared as Python objects; then `git diff HEAD`
read line by line.

Result lines from compare_tables.py:

```
WPSR: identical=True len_old=369 len_new=369
API_DROPPED_WEEKS: identical=True len_old=0 len_new=0
NGS_UNVERIFIED_IN_WINDOW: identical=True len_old=3 len_new=3
FEDERAL_MONDAY_HOLIDAYS: identical=True len_old=46 len_new=46
NYSE_NOT_FULL: identical=True len_old=84 len_new=84
DROPPED_WPSR: identical=True   DROPPED_NGS: identical=True
RELEASE_CALENDAR_SHA256 / RELEASE_CHECK_SHA256 / RESEARCH_CHECK_WINDOW: identical=True
NGS len old/new 372 367
removed: [('2019-12-26','09:30'), ('2020-01-02','09:30'), ('2020-11-12','09:30'), ('2021-01-21','09:30'), ('2023-11-09','09:30')]
added: []            order preserved: True
removed dates == DROPPED_NGS_CONFIRMATION dates: True
new module-level names: CONFIRMATION_CHECK_WINDOW, DROPPED_NGS_CONFIRMATION, E5_NGS_CHECK_SHA256 (no name removed)
sha256(reports/stage_e5_ngs_check.json) = ddfecb3e...7706b44 == E5_NGS_CHECK_SHA256
```

The `git diff` (124 lines) touches only: the docstring (generator line, NGS bullet, "only" removed from the
research-window bullet, a new confirmation-window bullet, the count 372 -> 367), the two new constants, the
`DROPPED_NGS_CONFIRMATION` record, four lines of the NGS literal (each the old line minus the dropped literal;
2019-12-26 and 2020-01-02 share a line), and `__all__`. No Friday row (2019-12-27, 2020-01-03, 2020-11-13,
2021-01-22) was added, as R-C3-1 requires. `sha256sum strategy/members/k4/_releases.py` =
aa8764b375283e812315b90ca699a9671e2c96e7793a02bbeb56b7a94ea4d388, 30616 bytes, which is what the coder's report and
the new freeze record.

### Check 2: each drop, and 12 keep rows, against the saved captures. VERIFIED WITH NOTES

Method: for every row below, the saved capture named in the check's `actual_source` was opened (tags stripped,
whitespace collapsed) and its "Released: ... | Next Release: ..." line quoted; the schedule capture named in
`schedule_source` was grepped for the week's exception row (or for the absence of one); the sha256 of all 30 files
used (15 WNGSR captures, 15 schedule captures) was recomputed and matched against data/vendor/release_pages/e5/
manifest.jsonl (`ok=30 mismatch=0 missing=0`); and the "last capture before the release" and the digest mapping
"last capture -> saved page" were re-derived from the saved CDX listing cdx_ngs_schedule_2019_2024.txt.

The five drops (all table rows 09:30 CT = 10:30 ET Thursday):

| Table row | Saved WNGSR capture, quoted | Schedule capture before the release, quoted | Verdict on the drop |
|---|---|---|---|
| 2019-12-26 | ngs_week_2019-12-26_20191228020346.html: "for week ending December 20, 2019 \| Released: December 27, 2019 at 10:30 a.m. \| Next Release: January 3, 2020" | ngs_sched_20191129075548.txt lines 27-30: "12/27/2019 / Friday / 10:30 a.m. / 12/25/2019 (Wednesday) is Christmas Day"; no row for 12/26/2019 | right |
| 2020-01-02 | ngs_week_2020-01-02_20200104053637.html: "for week ending December 27, 2019 \| Released: January 3, 2020 at 10:30 a.m. \| Next Release: January 9, 2020" | ngs_sched_20191229152905.txt lines 31-34: "1/3/2020 / Friday / 10:30 a.m. / 1/1/2020 (Wednesday) is New Year's Day"; no row for 1/2/2020 | right |
| 2020-11-12 | ngs_week_2020-11-12_20201113155744.html: "for week ending November 6, 2020 \| Released: November 13, 2020 at 10:30 a.m. \| Next Release: November 19, 2020" | ngs_sched_20200128214849.txt lines 35-38 (digest GHSGMTU3, the content of capture 20201031145739): "11/13/2020 / Friday / 10:30 a.m. / 11/11/2020 (Wednesday) is Veterans Day"; no row for 11/12/2020 | right |
| 2021-01-21 | ngs_week_2021-01-21_20210122171117.html: "for week ending January 15, 2021 \| Released: January 22, 2021 at 10:30 a.m. \| Next Release: January 28, 2021" | ngs_sched_20201224001827.txt lines 31-34 (digest ECW57HW7, the content of capture 20210118172825): "1/22/2021 / Friday / 10:30 a.m. / 1/20/2021 (Wednesday) is Inauguration Day"; no row for 1/21/2021 | right |
| 2023-11-09 | data/vendor/release_pages/eia/ngwu/ngwu_2023_11_09.html (E.2b's NGWU save): "Release date: November 9, 2023" and "EIA will not publish weekly natural gas inventories data this week. Please see our October 19 press release for more detail." Corroborated by ngs_week_2023-11-02_20231103010226.html: "Released: November 2, 2023 at 10:30 a.m. \| Next Release: November 16, 2023", and by the WNGSR captures of 2023-11-10 and 2023-11-14 (ngs_week_2023-11-09_20231110072740, _20231114125548), which still show the November 2 release | ngs_sched_20230708153227.txt line 10: "The standard release time and day of the week will be at 10:30 a.m. (Eastern time) on Thursdays with the following exceptions."; its 2023 exception rows are only 7/7/2023 Friday 10:30 a.m. and 11/22/2023 Wednesday 12:00 p.m.; no row for the week of 11/9/2023 | right: scheduled Thursday 10:30 ET, no release took place (C9's first drop rule, literally) |

The twelve keep rows (spread 2019-2024; the exception weeks included on purpose):

| Table row (CT) | Saved WNGSR capture, "Released:" line | Schedule capture before the release | Result |
|---|---|---|---|
| 2019-05-09 09:30 | _20190510024751: "Released: May 9, 2019 at 10:30 a.m." | 20190111124957 (= content of 20190502151029): no row for 5/9/2019 (standard) | matches |
| 2019-07-03 11:00 | _20190704044001: "Released: July 3, 2019 at 12:00 p.m." | 20190613010741 line 47: "7/3/2019" (Wednesday 12:00 p.m.) | matches |
| 2019-11-27 11:00 | _20191128062926: "Released: November 27, 2019 at 12:00 p.m." | 20190714105626 line 51: "11/27/2019" | matches |
| 2020-02-13 09:30 | no WNGSR capture that week; ngwu_2020_02_13.html: "Release date: February 13, 2020" and "The net withdrawal from working gas totaled 115 billion cubic feet (Bcf) for the week ending February 7" | 20200128214849: no row for 2/13/2020 (standard); time taken from the schedule (`time_basis: schedule`) | date matches; time is the schedule's, as the check states |
| 2020-11-25 11:00 | _20201125170101: "Released: November 25, 2020 at 12:00 p.m." | 20201121084027 line 23: "11/25/2020" | matches |
| 2021-06-10 09:30 | _20210610150817: "Released: June 10, 2021 at 10:30 a.m." | 20210319031602 (= content of 20210610031752): no row for 6/10/2021 | matches |
| 2021-11-24 11:00 | _20211124203246: "Released: November 24, 2021 at 12:00 p.m." | 20211111015940 line 23: "11/24/2021" | matches |
| 2022-03-17 09:30 | _20220317180018: "Released: March 17, 2022 at 10:30 a.m." | 20211216230557 (= content of 20220302163029): no row for 3/17/2022 | matches |
| 2022-11-23 11:00 | _20221124060223: "Released: November 23, 2022 at 12:00 p.m." | 20221106051100 line 27: "11/23/2022" | matches |
| 2023-07-07 09:30 | _20230708052433: "Released: July 7, 2023 at 10:30 a.m." | 20230210074654 line 31: "7/7/2023" (Friday 10:30 a.m.) | matches |
| 2023-11-16 09:30 | _20231117144124: "Released: November 16, 2023 at 10:30 a.m." | 20230708153227: no row for 11/16/2023 | matches |
| 2024-02-29 09:30 | _20240229205216: "Released: February 29, 2024 at 10:30 a.m." | 20231208131519: no row for 2/29/2024 | matches |

All 12 keep rows: the table's date and CT time equal the capture's stated ET date and time less one hour, and the
schedule capture before the release agrees. The four Friday drops are exactly the pattern the check describes: the
schedule capture before each release lists the Friday, the release happened on that Friday, and the table carries
the standing Thursday.

Notes (none changes a verdict):

- N2.1 Wayback revisit records. For three rows the check's "last capture before the release" is a CDX record with
  status "-" (a revisit record, same digest as the preceding 200 capture: 20201031145739 for the 2020-11-12 drop,
  20230614124625 for 2023-07-07) or a 301+200 pair (20210610031752 for 2021-06-10). In each case the last status-200
  capture before the release has the same digest (GHSGMTU3, 7SBY5FLP, JJ7NJEKN) as the record cited, so the schedule
  content used is the right one. The other 14 cited captures are the last status-200 capture before the release.
- N2.2 Rule wording. C9's first drop rule reads "a release whose actual date or time differs from its schedule
  entry". For 2023-11-09 it fires literally (scheduled, not released). For the four Friday rows EIA's actual equals
  EIA's schedule entry; what differs is the frozen table's date (the standing Thursday, an E.2 construction error
  the E.4 check did not catch, since 251 of these 252 rows were [unverified] in E.2b). The checker flagged this
  ("the mismatch is between the table and EIA") and ruling R-C3-1 resolves it as a drop. The facts the ruling rests on
  are verified here; whether a drop is the right reading of the rule is the lead's call, and dropping is the
  conservative one: the member no longer holds a phantom event on a non-release day, and no row is added that the
  frozen rule does not license. The cost is four missed real releases in the confirmation window.
- N2.3 Coverage. 5 of 5 drops and 12 of 247 keep rows were opened; the other 235 keep rows rest on the check.

### Check 3: the freeze. VERIFIED

`sha256sum`: HEAD copy cf066cb0507134e2553781f42699165b471be45ebec6b07bfb0d75680e879d1a, working copy
7abcde1705440e97efcf1ce255d979213eed9840f03a8383f2784a74f5f1534a (both as the brief states). Recursive field diff of the
two JSON documents (every key, every member, every file):

```
CHANGED /created_utc  2026-09-27T11:33:06+00:00 -> 2026-09-28T02:08:20+00:00
CHANGED /files/strategy/members/k4/_releases.py/bytes   28278 -> 30616
CHANGED /files/strategy/members/k4/_releases.py/sha256  35bd4730... -> aa8764b3...
```

Nothing else differs: 12 members (labels, ordinals, legs, modules, factories), 14 files, `members_dir`, `schema`,
`cluster`. The new hash equals the current file's. `load_cluster_freeze("K4")` then `verify_cluster_code(freeze)`:
"verify_cluster_code: PASSED (no exception)" (14 files, 12 members).

### Check 4: the research series is unchanged. VERIFIED

Command (run 19:10 PDT, nice 10, pycache outside the repo, exit 0; log audit_k4_research/run.log: "K4 K4-ngpre-01 NG
research: run []"):

```
PYTHONPYCACHEPREFIX=<scratchpad>/pycache nice -n 10 uv run python -m screening.stage_e_runner \
  --harness-sha256 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87 --cluster K4 \
  --member "K4-ngpre-01 NG" --window research --research-root data/processed --step2-root data/processed_step2 \
  --out-dir reports/stage_e5_briefs/audit_k4_research/
```

Field-by-field diff of audit_k4_research/K4_K4-ngpre-01_NG_research.json against
reports/stage_e4_k4_screen/K4_K4-ngpre-01_NG_research.json (8 differing paths, all permitted):

```
CHANGED /cluster_freeze_sha256  cf066cb0... -> 7abcde17...
CHANGED /created_utc            2026-09-27T11:44:27+00:00 -> 2026-09-28T02:10:32+00:00
CHANGED /harness_sha256         82ae8536... -> 9a8ebe73...
/power: status not_run -> run; reason removed; check, start_rule, supply_days added (harness v6 power check)
series identical: True | daily_net_usd identical: True | screen identical: True | engine identical: True
trade_rate identical: True | window_dates identical: True | coverage/bars identical: True
series n = 269, sum 868.262 both; screen: n_days 269, n_trips 50, t_daily 1.814, passes True
```

Trip list (`K4_K4-ngpre-01_NG_research_trips.json`, the E.4 file is named `_research_trips.json`): 50 trips, identical
element by element; the only differing field is `record_sha256`, which equals the sha256 of each record file
(397477042e... for E.4's, cc403f7ac1... for this run's).

### Check 5: the tests. VERIFIED

`uv run pytest -q tests/test_e4_k4_members_b.py` -> `63 passed in 2.00s`. From the diff: the NGS recomputation now
drops `DROPPED_NGS | DROPPED_NGS_CONFIRMATION` and asserts 373 - 1 - 5 rows with 63 in the research window;
`test_the_e5_check_has_the_pinned_sha256_and_window` pins ddfecb3e... in both the test and the module and the window
2019-05-06..2024-02-29, and asserts the two windows do not overlap; `test_the_e5_drops_are_the_e5_checks_drop_verdicts_
on_or_after_s_ng` ties the five rows to the check's `drop_actual_differs` verdicts on or after S_NG, asserts no Friday
row was added and that `ngpre.schedule(NGS)` has no dropped date; `test_research_window_ngs_rows_are_unchanged_by_the_
e5_drops` pins the 21 research-window source lines' sha256; `test_the_e5_amendment_removes_the_five_ngs_rows_and_
nothing_else` asserts the seven other blocks byte-identical to the E.4 rendering; `test_the_module_is_exactly_the_
generators_output` asserts the module equals the E.5 generator's `amend(...)` and that the E.5 generator still renders
the E.4 text. The E.4 pins (calendar 839f2437..., check 4c71d798...) are untouched.

### Q: the "(lead decides drop vs correction)" wording

The five reasons in `DROPPED_NGS_CONFIRMATION` are "drop_actual_differs: " + the check's `reason` verbatim, so four
of them end in the checker's "(lead decides drop vs correction)". I see no correctness problem: nothing at runtime
reads the reason strings (`grep` over strategy/, screening/, rules/, sim/: `DROPPED_*` is referenced only inside
`_releases.py` and the tests; ngpre.py imports only `NGS`), the ruling and its label R-C3-1 are recorded in the module
docstring and in the test, and the verbatim copy is what lets the test prove each row is the check's row. It is a
readability wart in a frozen file: a reader of the tuple alone sees an open question that is closed two paragraphs
above. Rewording it now would change `_releases.py`'s hash and force a third freeze write for no computational
effect; I would leave it and, if the lead wants it gone, do it only at a regeneration that is needed anyway (a
one-line change in gen_k4_releases_e5.py's `e5_drops` and in the test's reason assertion, as the coder notes).

### Not checked, and observations for the lead

- No live Wayback or EIA page was fetched (by the brief); everything rests on the saved captures, whose hashes match
  the manifest. Capture 20231124164907, named in the check's markdown, has no file of its own under e5/ (it maps to
  another saved digest); it postdates the 2023-11-09 release, so it was not needed.
- 235 of the 247 keep rows were not opened (N2.3).
- The coder's open item 1 stands: tests/test_e4_k4_members_b.py loads the untracked
  reports/stage_e5_briefs/gen_k4_releases_e5.py; it must be committed with the amendment or two tests fail on a
  clean checkout. Not an audit discrepancy, a packaging note.
- The rule-wording point N2.2 is recorded for the synthesis; the audit does not overturn R-C3-1.

## Part 2: the recomputation (Task C6)

Written 2026-09-27, 19:32 PDT. Brief: reports/stage_e5_briefs/C6_confirm_auditor_k4.md. Code:
reports/stage_e5_briefs/audit_k4_part2/recompute.py (own numpy/statistics/math code; the one program function called
for a figure is funnel.null_generator.stationary_bootstrap_indices, the frozen generator the criteria name; nothing under
screening/ is imported; funnel.multiple_comparisons is called afterwards as a labelled second check). Output:
audit_k4_part2/figures.json and recompute.log (50 checks). Verdict file audited: reports/stage_e5_k4_verdicts.json,
sha256 b574b4c1edcb394297941fd3ec4dde3ca25efa8622d3bcfc0a43d4df461987b1; rendering reports/stage_e5_k4_verdicts.md.
Holdout `unlocks_logged` 0 at the end; no runner run of any window; no web; no commit.

| Item | Verdict | Evidence |
|---|---|---|
| 0. Run inputs equal the hashed list | VERIFIED WITH NOTES | List sha256 22388c6b... (commit 4161032 "docs: K4 confirmation list"); verdict carries that sha256 and the list's name. Every record: harness 9a8ebe73..., freeze 7abcde17..., member, ordinal, window "confirmation", status "run", legs roots, s_x, primary vehicle, window ends (MCL 2021-07-12..2024-02-29, 586 dates; NG 2019-05-06..2024-02-29, 1070 dates), frozen tables (costs f4360bb7, epsilon 4e2c7731, sizes 280d7e9d, vehicles 1f1cafee, each equal to the file's sha256 now), release calendar 839f2437, and seed = 20260923 + ordinal. Record set = the list's 12 run trials exactly; log: "12 members, 0 refused", 19:15:54-19:22:07. Note: the record stores legs as `[{"root": "NG", "traded": true}]` and the list as `["NG"]`; compared on roots. |
| 1. Per trial: theta_hat, UCB95, SE_boot, p, power, counts, per-trade, status | VERIFIED | Own bootstrap loop (fresh `np.random.default_rng(20260923 + ordinal)`, 10,000 draws of `stationary_bootstrap_indices(rng, n, n, 5.0)`, `np.quantile(means, 0.95)`, `std(ddof=0)`, p = (1 + #{theta* - theta_hat >= theta_hat}) / 10,001, power = Phi(eps / SE - 1.645)): every float field of all 12 trials equal to the verdict's to 0 relative (bit-identical), every integer, boolean and status field equal. Table below. |
| 2. Holm at K = 9 | VERIFIED | One Tier A p (K4-ngpre-01 NG) 0.5375462454 against 0.05 / 9 = 0.0055555556: not rejected; the verdict's row (rank 1, threshold, reject false, m = 1) identical. |
| 3a. DSR at N = 150, V14 (c) | VERIFIED WITH NOTES | Daily Sharpe of each of the 12 run series (mean / population sd), `statistics.pvariance` = 0.00204161346893 (verdict identical). E[max SR] with `statistics.NormalDist.inv_cdf`: 0.120646662985 vs the verdict's 0.120646663075 (7.5e-10 relative, the Acklam ppf approximation's own error). DSR on the trial's own moments (n 1070, SR -0.00210146, skew 1.9273, raw kurtosis 53.882): 3.0995599e-05 vs 3.0995599e-05 (1.3e-8 relative, same cause). Second check with funnel.multiple_comparisons.deflated_sharpe_ratio on my inputs: 3.099559851e-05, equal to the verdict to 1e-9. |
| 3b. Daily t | VERIFIED | mean / (population sd / sqrt 1070) = -0.0687405410103, verdict identical (0 relative). Second check harvey_liu_zhu_verdict: identical. |
| 3c. PBO by L-E5-3 | VERIFIED WITH NOTES | Union of the 12 window-date sets: 1154 dates (NG's 1070 plus 84 MCL dates outside NG's set); each series aligned with zeros off its own dates; 8 blocks of 1154 // 8 = 144 dates (the last 2 union dates fall outside every block, D.1b's `_blocks` convention); 70 balanced splits; own CSCV loop: 45 of 70 splits put the in-sample winner at or below the out-of-sample median, PBO 0.642857142857; winner positive out of sample 13 / 70 = 0.185714; winner mean out-of-sample sum -749.1341071 ticks. All equal to the verdict to 1e-9; second check probability_of_backtest_overfitting: identical. |
| 4. Chain verdict, cluster statement, resolution table | VERIFIED | Passes {holm F, dsr F, t F, pbo F}, composite "pending", first failing step "holm", verdict "no edge" (the word "edge" appears only inside "no edge"). Statement: every one of the 12 covered trials is "null" (min closed trips 55 >= 30, no zero-trip or SE = 0 trial), none "inconclusive by design", so "null"; blocking, not covered, inactivity all empty; note null. Resolution: MCL eps 21 ticks, $84.00 at q_c 4, fewest trips K4-eiafade-01 MCL 55, largest UCB95 / trip 11.192848 (K4-cp3-01 MCL); NG eps 8 ticks, $80.00 at q_c 1, fewest K4-ngpre-01 NG 198, largest 9.584283 (K4-ngpre-01 NG). eps_X, dollars and q_c equal reports/stage_e2a_epsilon.json's K4 rows. |
| 5. K4-ngpre-01 NG daily series rebuilt from its trips | VERIFIED | Trips file binds to the record (record_sha256 fba6ec23... = the record's sha256), 198 trips, all 1 contract, close reasons strategy 189 / mll_liquidation 9. Own cost model from the frozen tables: commission 422 c round turn (211 c per side per contract), slippage per side = ceil(round(qty x s x 1000 c, 6)) with s = the fill bar's 30-minute CT bucket `side_ticks` from stage_e2a_costs.json NG, or the largest s_b (0.99278 ticks) + the bucket's depth (0 on every NG bucket) when the fill instant lies in [release, release + 30 min) of a calendar release naming NG (NGS, WPSR, FOMC in the frozen calendar; 31 of the 396 sides). net = gross - cost reproduced exactly for 198 / 198 trips (Fraction arithmetic). Daily series: per trade date, sum of net_cents / 1000 / contracts; zeros on the other window dates; equals the record's `series.values` (max abs diff 2.8e-14 ticks) and `daily_net_usd` (0); mean -0.0823149533 = theta_hat. One MCL trial was not rebuilt (time). |
| 6. The .md against the JSON | VERIFIED WITH NOTES | All 180 cells of the per-trial table equal the JSON at the printed precision (the single positive theta_hat, cp2-01 NG, carries an explicit "+", the only cell my formatter flagged). The chain table (p 0.5375, threshold 0.005556, DSR 3.1e-05, variance 0.002042, t -0.069, PBO 0.6429, 1154 union dates, 8 blocks of 144, 70 splits, first failing step holm), the statement (12 covered, none blocking, "at least 55 closed trips", S_X dates) and the resolution table all match the JSON; the header's hashes and run times match the files and the log. Note: the "Sign check" paragraph (mean move -1.27 ticks, sd 91.3, t -0.20, 52% negative) is not in the verdict JSON; it is the lead's catalog-side figure and is not verified here (no bar read). |

### Per-trial figures, mine beside the verdict file's

Units: net ticks per contract per day. "mine" is recompute.py; "verdict" is stage_e5_k4_verdicts.json. Max rel diff is over
theta_hat, UCB95, SE_boot, p, power, trips/day and both per-trade figures.

| Ord | Trial | theta_hat (mine) | UCB95 (mine) | SE_boot (mine) | p (mine) | Null power (mine) | UCB95 / trip (mine) | Status (mine) | theta_hat (verdict) | UCB95 (verdict) | SE_boot (verdict) | p (verdict) | Max rel diff |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | K4-cp1-01 MCL | -6.9332423208 | -3.9888856655 | 1.7824664170 | 0.9999000100 | 1.0000000000 | -4.151842 | null | -6.9332423208 | -3.9888856655 | 1.7824664170 | 0.9999000100 | 0 |
| 2 | K4-cp1-01 NG | -1.4305925234 | 0.6633577570 | 1.2570705704 | 0.8749125087 | 0.9999988150 | 0.693157 | null | -1.4305925234 | 0.6633577570 | 1.2570705704 | 0.8749125087 | 0 |
| 3 | K4-cp2-01 MCL | -2.7008873720 | 3.0883425768 | 3.4613830367 | 0.7799220078 | 0.9999951090 | 3.093622 | null | -2.7008873720 | 3.0883425768 | 3.4613830367 | 0.7799220078 | 0 |
| 4 | K4-cp2-01 NG | 1.4389710280 | 5.4654505140 | 2.3455036685 | 0.2600739926 | 0.9612837247 | 5.511812 | null | 1.4389710280 | 5.4654505140 | 2.3455036685 | 0.2600739926 | 0 |
| 5 | K4-cp3-01 MCL | -1.7861860068 | 5.3481183874 | 4.2274022723 | 0.6593340666 | 0.9995540700 | 11.192848 | null | -1.7861860068 | 5.3481183874 | 4.2274022723 | 0.6593340666 | 0 |
| 6 | K4-cp3-01 NG | -5.4138560748 | -1.7005083645 | 2.2948760979 | 0.9900009999 | 0.9671911977 | -3.998998 | null | -5.4138560748 | -1.7005083645 | 2.2948760979 | 0.9900009999 | 0 |
| 7 | K4-ngpre-01 NG | -0.0823149533 | 1.7735402804 | 1.1105796997 | 0.5375462454 | 0.9999999864 | 9.584283 | null | -0.0823149533 | 1.7735402804 | 1.1105796997 | 0.5375462454 | 0 |
| 8 | K4-apipre-01 MCL | -0.4383788396 | 1.6167918089 | 1.2388842366 | 0.6343365663 | 1.0000000000 | 10.187527 | null | -0.4383788396 | 1.6167918089 | 1.2388842366 | 0.6343365663 | 0 |
| 9 | K4-eiafade-01 MCL | -2.7267150171 | -0.7508852389 | 1.2373609943 | 0.9833016698 | 1.0000000000 | -8.000341 | null | -2.7267150171 | -0.7508852389 | 1.2373609943 | 0.9833016698 | 0 |
| 10 | K4-eiamom-01 MCL | -0.0879138225 | 0.4681860068 | 0.3265723231 | 0.5992400760 | 1.0000000000 | 2.743570 | null | -0.0879138225 | 0.4681860068 | 0.3265723231 | 0.5992400760 | 0 |
| 11 | K4-ovr-01 MCL | -5.2969496587 | -0.1226198805 | 3.1556456481 | 0.9533046695 | 0.9999997275 | -0.122411 | null | -5.2969496587 | -0.1226198805 | 3.1556456481 | 0.9533046695 | 0 |
| 12 | K4-ovr-01 NG | -1.0121383178 | 1.5174692991 | 1.5558304651 | 0.7500249975 | 0.9997646936 | 1.488260 | null | -1.0121383178 | 1.5174692991 | 1.5558304651 | 0.7500249975 | 0 |

Every UCB95 is below its eps_X (21 MCL, 8 NG) and every null power is above 0.80 (minimum 0.9613, K4-cp2-01 NG), so
every trial is "null" and none is "null by inactivity" (minimum 55 closed trips).

### Chain figures (Tier A: K4-ngpre-01 NG)

| Figure | Mine | Verdict file | Criterion | Passes |
|---|---|---|---|---|
| Holm p, threshold | 0.5375462454, 0.0055555556 | same | p <= 0.05 / 9 | no |
| Sharpe variance over the 12 run trials | 0.00204161346893 | 0.00204161346893 | V14 (c) | |
| E[max SR] at N = 150 | 0.120646662985 | 0.120646663075 | | |
| DSR | 3.0995599e-05 | 3.0995599e-05 | > 0.95 | no |
| Daily t | -0.0687405410 | -0.0687405410 | > 3.0 | no |
| PBO (45 / 70 splits) | 0.6428571429 | 0.6428571429 | < 0.5 | no |
| Verdict | no edge, first failing step holm | same | | |

Daily Sharpes entering the variance: cp1 MCL -0.1521, cp1 NG -0.0375, cp2 MCL -0.0339, cp2 NG 0.0193, cp3 MCL -0.0160,
cp3 NG -0.0717, ngpre NG -0.0021, apipre MCL -0.0140, eiafade MCL -0.0896, eiamom MCL -0.0106, ovr MCL -0.0718, ovr NG
-0.0202.

### Not checked

- One MCL trial's trip rebuild (item 5, "if time allows").
- The .md's sign-check paragraph (outside the JSON; needs a bar read).
- The confirmation runner itself (the records are taken as written; Part 1 verified the research series under the
  same harness and freeze, and item 5 verifies one record's series from its trips and the frozen cost tables).
