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
