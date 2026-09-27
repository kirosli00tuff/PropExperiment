# Stage E.3 return: K2 rates, eight members coded, audited, frozen and screened (research window)

Lead: Opus 5.5 (claude-opus-5-5), effort xhigh. Session 2026-09-26 23:35 PDT to 2026-09-27 01:15 PDT.
All times America/Vancouver (PDT). Stage prompt: the planning chat's "STAGE E.3 K2 RATES" prompt (commit 9741e63).

## 1. Verdict summary

K2's eight active members (44 trials) were coded from their frozen entries and audited by Fable
(0 BLOCKING, 0 SHOULD FIX, 12 NOTE). They were then frozen, with **cluster freeze sha256
8815a775e74996419b57751b1104ffa07cd4b3450eb18a9a92c6cbbd5615b7c5** in commit **a79b47e** (not pushed),
and screened once on the research window (299 dates, 2025-04-01..2026-06-17). **Every trial fails D5's
screen: Tier A is empty and all 44 trials are Tier B.** No member was unimplementable, refused or
excluded, and no floor label was set. The frozen `python -m` launch crashed before writing anything,
because of a harness double import (C-1). The same frozen `main()` then ran from an import (R-T5-1).
Fable's recomputation confirmed every screen figure (to 1e-9) and every tier, with no discrepancy. The runner does not count program N. Computed: **N = 58 + 44 = 102**. K2's confirmation
session needs the step 2 purchase ($40.50 quoted in E.2b; acct-2 top-up $18.98), the start-rule
build, D4's power check per trial, and then the list hash. All 44 trials go as Tier B (null side).

| Member | Trials | Tier | Trips per trial | Mean net ticks/contract/day | Daily t | Best trial (t) |
|---|---|---|---|---|---|---|
| K2-cp1-01 | 6 | B | 264-276 | -1.077 to -0.314 | -5.34 to -1.12 | ZF (-1.12) |
| K2-cp2-01 | 6 | B | 265-291 | -0.976 to -0.213 | -1.98 to -0.34 | ZF (-0.34) |
| K2-cp3-01 | 6 | B | 121-136 | -1.223 to -0.379 | -1.78 to -0.43 | ZT (-0.43) |
| K2-aucpre-01 | 6 | B | 10-15 | -0.164 to 0.098 | -1.36 to 0.48 | UB (0.48) |
| K2-aucpost-01 | 6 | B | 10-15 | -0.199 to 0.050 | -2.02 to 0.84 | ZT (0.84) |
| K2-fomcpost-01 | 6 | B | 10 | -0.572 to -0.254 | -2.08 to -1.92 | ZB (-1.92) |
| K2-predrift-01 | 2 | B | 11-12 | -0.071 to -0.030 | -1.24 to -0.43 | ZN (-0.43) |
| K2-monthend-01 | 6 | B | 18 | -0.434 to 0.009 | -1.42 to 0.04 | ZT (0.04) |

## 2. Guardrail evidence

**Start checks, verbatim** (run 23:35-23:40 PDT; the suite 23:50:06-00:00:42):
```
$ git status --short
(empty)
$ git log --oneline -3
9741e63 docs: Stage E.3 prompt (K2 member coding, audit, freeze and screening)
9ae322a docs: DECISIONS V11 (F17 20-date median) and V12 (ML compute windows)
9632e50 docs: Stage E.2b return, STATE, worker reports and briefs
$ wc -c REGISTRATION.md
0 REGISTRATION.md
$ uv run python -m data.holdout status (keys)
holdout_1: "unlocks_logged": 0, "all_ok": true
holdout_2: "unlocks_logged": 0, "all_ok": true
$ python3 reports/stage_e2b_briefs/check_frozen.py
reports/stage_e1_freeze.json: manifest sha256 96166eb39b85d4fdcf132092978ee85393392de52c3857dc3f64ea7281454a7c files 32/32 match
reports/stage_e2a_ml_freeze.json: manifest sha256 077a57e1c00554dd0745302b247673d45ee05b805ac4bfd876f8497f7bbb1ed2 files 4/4 match
OK       reports/stage_e2a_costs.json f4360bb7...df14
OK       reports/stage_e2a_vehicle_sizes.json 280d7e9d...7325
OK       reports/stage_e2a_vehicles.json 1f1cafee...9913
OK       reports/stage_e2a_vehicle_rule_readings.md 8c3c29dd...b458
OK       reports/stage_e2a_epsilon_declaration.md ccdb8ec5...8c7c
OK       reports/stage_e2a_epsilon_declaration_addendum.md e6253be2...8d32
OK       reports/stage_e2a_source_window_amendment.md 9fe401c1...f13d
OK       reports/stage_e2a_epsilon.json 4e2c7731...f496
ALL_OK
$ PYTHONPYCACHEPREFIX=<fresh> uv run python -m screening.harness_freeze verify --expected cf939270f0a00be74aa29a43f0c7de964256411a9cdcebc36f22fd3bdc021a45
preflight OK: cf939270f0a00be74aa29a43f0c7de964256411a9cdcebc36f22fd3bdc021a45
$ PYTHONPYCACHEPREFIX=<fresh> uv run pytest -q          (run 1, 23:36:00-23:46:54)
3 failed, 2860 passed, 2 skipped, 1 xfailed, 54 warnings in 650.75s (0:10:50)
$ uv run pytest -q                                       (run 2, as E.2b ran it, 23:50:06-00:00:42)
2863 passed, 2 skipped, 1 xfailed, 54 warnings in 633.88s (0:10:33)
```
Run 1's three failures (tests/test_harness_freeze.py: test_an_unchecked_hash_pyc_beside_an_unchanged_source_is_refused,
test_a_timestamp_pyc_forged_to_match_its_source_is_refused, test_honest_and_stale_bytecode_pass) came from the lead
setting PYTHONPYCACHEPREFIX for the suite. Those tests write bytecode beside the sources. Checked at 23:49: `17 passed`
without the variable, `3 failed, 14 passed` with it. Run 2 equals E.2b's end result, as the prompt expected.

**End checks, verbatim** (the suite 01:02:21-01:13:30; the rest at 01:13:47):
```
$ uv run pytest -q
3008 passed, 2 skipped, 1 xfailed, 54 warnings in 668.06s (0:11:08)
$ git log --oneline -3
a79b47e feat: K2 member freeze (Stage E.3), cluster freeze sha256 8815a775
9741e63 docs: Stage E.3 prompt (K2 member coding, audit, freeze and screening)
9ae322a docs: DECISIONS V11 (F17 20-date median) and V12 (ML compute windows)
$ wc -c REGISTRATION.md
0 REGISTRATION.md
$ uv run python -m data.holdout status (keys)
holdout_1 all_ok True unlocks_logged 0 unlock_log_ok True
holdout_2 all_ok True unlocks_logged 0 unlock_log_ok True
$ python3 reports/stage_e2b_briefs/check_frozen.py
reports/stage_e1_freeze.json: manifest sha256 96166eb39b85d4fdcf132092978ee85393392de52c3857dc3f64ea7281454a7c files 32/32 match
reports/stage_e2a_ml_freeze.json: manifest sha256 077a57e1c00554dd0745302b247673d45ee05b805ac4bfd876f8497f7bbb1ed2 files 4/4 match
OK       reports/stage_e2a_costs.json f4360bb7...df14
OK       reports/stage_e2a_vehicle_sizes.json 280d7e9d...7325
OK       reports/stage_e2a_vehicles.json 1f1cafee...9913
OK       reports/stage_e2a_vehicle_rule_readings.md 8c3c29dd...b458
OK       reports/stage_e2a_epsilon_declaration.md ccdb8ec5...8c7c
OK       reports/stage_e2a_epsilon_declaration_addendum.md e6253be2...8d32
OK       reports/stage_e2a_source_window_amendment.md 9fe401c1...f13d
OK       reports/stage_e2a_epsilon.json 4e2c7731...f496
ALL_OK
$ PYTHONPYCACHEPREFIX=<fresh> uv run python -m screening.harness_freeze verify --expected cf939270...
preflight OK: cf939270f0a00be74aa29a43f0c7de964256411a9cdcebc36f22fd3bdc021a45
$ K2 cluster freeze (load_cluster_freeze + verify_cluster_code)
K2 cluster freeze OK 8815a775e74996419b57751b1104ffa07cd4b3450eb18a9a92c6cbbd5615b7c5 44 members
$ ledger
14823 ledger/databento_spend.jsonl
02e7caa257bbee7b84d23a0394c9fae34985e884c1306fb47ea683546f15b1ed
start sha: 02e7caa257bbee7b84d23a0394c9fae34985e884c1306fb47ea683546f15b1ed
$ git status --short   (at 01:15)
 M docs/STAGES.md
 M progress.md
 M reports/stage_e3_member_audit.md
?? reports/E.3_RETURN.md
?? reports/stage_e3_STATE.md
?? reports/stage_e3_auction_xml_check.json
?? reports/stage_e3_auction_xml_check.md
?? reports/stage_e3_briefs/
?? reports/stage_e3_coder_A.md
?? reports/stage_e3_coder_B.md
?? reports/stage_e3_k2_screen/
$ git diff --stat
 docs/STAGES.md                   |   7 +-
 progress.md                      |  54 ++++++++++
 reports/stage_e3_member_audit.md | 207 +++++++++++++++++++++++++++++++++++++++
 3 files changed, 266 insertions(+), 2 deletions(-)
```
Ledger: 14,823 lines at start and end, with the same sha256 (02e7caa2...b15ed), and `git diff --stat -- ledger/` is
empty. No spend and no quote this session. No TopstepX reference or credential was used. No edit under live/, ops/,
any frozen file or manifest, docs/NULL_CRITERIA.md or reports/stage_d1f_confirmation_list.md. Only the research
window was read, and only by the runner, plus the auditor's four in-memory replays (R-T6-1: K2-cp1-01 ZN,
K2-aucpost-01 ZN, and in the follow-up K2-predrift-01 ZN and ZB, all through the runner's own loader, each equal to its record). No session script opened a bar file.

## 3. Results per task

### Task 0: startup
Start checks passed 23:35-23:40 (section 2). HEAD 9741e63 (a descendant of 9ae322a), tree clean, preflight accepts
cf939270. The first start run of the suite set PYTHONPYCACHEPREFIX, and three bytecode tests in
tests/test_harness_freeze.py fail under that variable. Rerun exactly as E.2b ran it (`uv run pytest -q`, no prefix),
the suite matched E.2b's end result. Rule used for the rest of the session: pytest runs without the prefix, and every
Stage E entry point (harness verify, freeze, runner) runs with a fresh one.

### Task 1: member specifications (lead)
reports/stage_e3_member_specs.md (23:40-23:52; L-23 appended 00:08). For each member it gives products, vehicle,
decision, entry, exit and flatten times, hold, order type, sizing at q_c, every parameter as a literal, the release
instants read, the trials in N and the Topstep checks. Every field carries a catalog or design line reference, or a
logged reading. There are 23 lead readings, L-01..L-23 (section 6). No member was found unimplementable as frozen.

Task 1b (added by the lead, L-02): the catalog's C9 check, "if the announcement XML ... and the query disagree on
closing_time_comp ... that auction is dropped", was assigned to E.2 and never run. AuctionXmlChecker-OpusMed ran it
from 23:45 to 00:05 (reports/stage_e3_auction_xml_check.md/.json). All 340 in-scope 2-, 5-, 10- and 30-year auctions
agree, none was unavailable, and none is dropped. Two reopenings are keyed by an original term that differs from the
term actually sold: 2019-11-05 (10Y key, a 3-year sold) and 2026-01-26 (5Y key, a 2-year sold, research window).
Both stay as the frozen text keys them (L-23). **For the user:** K2-aucpre-01 and K2-aucpost-01 trade the 2026-01-26
2-year auction on ZF, not on ZT.

### Task 2: the modules and their tests
13 files under strategy/members/k2/ (hashes as frozen):

| File | Bytes | sha256 (first 16) |
|---|---|---|
| strategy/members/k2/__init__.py | 0 | e3b0c44298fc1c14 |
| strategy/members/k2/_event_common.py | 7,362 | 5b3b62ee024be329 |
| strategy/members/k2/_month_end.py | 5,308 | b2eb207d1d30e185 |
| strategy/members/k2/_port_common.py | 4,312 | 556b1012c8c6525f |
| strategy/members/k2/_releases.py | 14,623 | a64a041789057a64 |
| strategy/members/k2/aucpost.py | 2,536 | 2ad1b5ed20ae3847 |
| strategy/members/k2/aucpre.py | 2,582 | 1b2d312e9d36b66e |
| strategy/members/k2/cp1.py | 6,257 | b1b52eb3dd6c76d5 |
| strategy/members/k2/cp2.py | 6,056 | 4957faafc0a9475d |
| strategy/members/k2/cp3.py | 8,792 | 3985d957f593a959 |
| strategy/members/k2/fomcpost.py | 2,517 | 5130925a72445107 |
| strategy/members/k2/monthend.py | 4,370 | ca801d5a85be2e68 |
| strategy/members/k2/predrift.py | 5,117 | 3d2d362efc1f5ce5 |

- MemberCoder-A-OpusXHigh (23:53-00:11): cp1.py, cp2.py, cp3.py, monthend.py, _port_common.py, _month_end.py (85
  months 2019-05..2026-05; the rates calendar counts early-halt days as trade dates, and 9 of the 170 dates are halts,
  which the member drops). tests/test_e3_k2_members.py: 98 tests on synthetic bars through the real engine, plus a pin
  test that recomputes the month-end table from the calendar. Report reports/stage_e3_coder_A.md. Five deliberately
  broken variants, one per key rule, each fail a test.
- MemberCoder-B-OpusXHigh (23:53-00:09): aucpre.py, aucpost.py, fomcpost.py, predrift.py, _event_common.py,
  _releases.py (340 auctions, 57 FOMC, 86 ISM; DROPPED_AUCTIONS empty). tests/test_e3_k2_members_events.py: 47 tests,
  plus a pin test that recomputes the tables from the frozen release calendar and the XML check. Report
  reports/stage_e3_coder_B.md. 16 deliberately broken variants, each caught.
- Engine fact found by coder A: a one-leg member is never called on a minute without its leg's bar. The members still
  handle a None bar.
- Ruling R-T2-1: a bar's open is read as `dataclasses.asdict(bar)["open"]`, because the frozen static check bans the
  name `open` even as an attribute. The auditor confirmed it (audit section 4).
- Task 2 gate: the full suite, 00:11:30-00:24:19, gave `3008 passed, 2 skipped, 1 xfailed, 54 warnings`.

### Task 3: the fidelity audit
reports/stage_e3_member_audit.md part 1 (MemberAuditor-FableXHigh, 00:11-00:28): **0 BLOCKING, 0 SHOULD FIX, 12
NOTE**. Every module implements its frozen entry and nothing more. The auditor recomputed every literal table from its
frozen source in its own code, ran all 13 files through the static check (all pass), ran both test files (145 passed),
and ran nine extra engine scenarios. It agrees with all 23 lead readings, each either the narrowest reading or fixed by
its reference. The notes and their rulings are in section 5.

### Task 4: rulings, the cluster freeze and the commit
reports/stage_e3_member_rulings.md. No member code changed after the audit: the 15 audited files were re-checked
against the pre-audit hashes at 00:29. The freeze was written at 00:29:42 by screening.stage_e_freeze.write_cluster_freeze
(script reports/stage_e3_briefs/write_k2_freeze.py): reports/stage_e_k2_member_freeze.json, **sha256
8815a775e74996419b57751b1104ffa07cd4b3450eb18a9a92c6cbbd5615b7c5**, 44 declarations over 14 files. At 00:31 it
verified, and all 44 labels resolved to members whose name equals the label. The suite run 00:29:58-00:42:43 gave
`3008 passed, 2 skipped, 1 xfailed, 54 warnings`. **Commit a79b47e**, "feat: K2 member freeze (Stage E.3), cluster
freeze sha256 8815a775", holds exactly the 13 member files, the two test files, the specs, the audit (part 1), the
rulings and the freeze file (19 files).

### Task 5: the screening run
- Attempt 1, 00:43:15-00:43:26, **crashed (C-1)**. The frozen command, as the E.2b return gives it,
  `PYTHONPYCACHEPREFIX=<fresh> uv run python -m screening.stage_e_runner --harness-sha256 cf939270... --cluster K2
  --all --window research --research-root data/processed --step2-root data/processed_step2 --out-dir
  reports/stage_e3_k2_screen`, raised `screening.stage_e_runner.StartRuleMissing: no frozen S_X for ['ZT']` at
  runner line 442, after the engine had run the first trial, K2-cp1-01 ZT, in memory. No record was written, the
  output directory was never created, and no figure was seen. Cause, in the frozen harness: under `python -m` the
  runner module is `__main__`. screening/stage_e_start_dates.py raises its refusals through `_runner()`, which is
  `from screening import stage_e_runner`: a second copy of the module. So `__main__`'s
  `except (RunnerRefusal, StageEBarRefusal)` does not match, and the refusal that tests/test_stage_e_runner.py:94
  expects to be recorded as `power: not_run` escapes. All 8 raises in stage_e_start_dates go through `_runner()`.
- Ruling R-T5-1: no code or frozen file changed. The same frozen `main()` was re-run from scratch with the identical
  argv, called from the imported module:
  `PYTHONPYCACHEPREFIX=<fresh> nice -n 10 uv run python -c "import sys; from screening.stage_e_runner import main;
  sys.exit(main([...same argv...]))"`. This is the path the harness tests exercise. Preflight, the freeze
  verification and lower_priority all stay inside main() and screen_cluster().
- Attempt 2, 00:44:56-00:50:39, exit 0: `K2 research: 44 members, 0 refused`. 45 records in reports/stage_e3_k2_screen/,
  written by the runner: 44 member records K2_<label>_research.json and K2_research_cluster.json. Each member record
  carries harness cf939270, cluster freeze 8815a775 and release calendar 839f2437.
- The window is 299 trade dates (2025-04-01..2026-06-17). Per trial, the runner removed 15 roll-blackout dates and UR-1's
  2 dates. Power check: `not_run` for all 44 (StartRuleMissing: no start-rule file exists before the step 2 purchase),
  as designed.
- The runner writes no trip list (R-T6-1).

### The screen per member and exposure (from the runner's files)

Units: net ticks per contract per day of the trial's vehicle, zeros on no-trade days (D5). Coverage is the runner's
ratio of present to expected bars in the trial's trading windows (D9, at least 0.95). No trial has a floor label.

| Ord | Trial | Trips | Mean net ticks/contract/day | Pop. sd | Daily t | Screen | Mean hold (min) | Min hold (min) | Coverage (min over leg) | Labels | Power | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | K2-cp1-01 ZT | 264 | -0.5808 | 4.3139 | -2.328 | fail | 29.0 | 28 | 0.9844 | none | not_run | B |
| 2 | K2-cp1-01 ZF | 275 | -0.3141 | 4.8344 | -1.124 | fail | 29.0 | 29 | 0.9954 | none | not_run | B |
| 3 | K2-cp1-01 ZN | 276 | -0.4734 | 3.2042 | -2.555 | fail | 28.9 | 5 | 0.9986 | none | not_run | B |
| 4 | K2-cp1-01 TN | 270 | -0.8905 | 4.1730 | -3.690 | fail | 28.8 | 2 | 0.9621 | none | not_run | B |
| 5 | K2-cp1-01 ZB | 272 | -0.8666 | 2.8060 | -5.340 | fail | 28.7 | 2 | 0.9782 | none | not_run | B |
| 6 | K2-cp1-01 UB | 276 | -1.0765 | 3.5844 | -5.193 | fail | 28.6 | 5 | 0.9681 | none | not_run | B |
| 7 | K2-cp2-01 ZT | 265 | -0.7138 | 9.0376 | -1.366 | fail | 75.9 | 73 | 0.9789 | none | not_run | B |
| 8 | K2-cp2-01 ZF | 283 | -0.2127 | 10.7304 | -0.343 | fail | 75.1 | 66 | 0.9955 | none | not_run | B |
| 9 | K2-cp2-01 ZN | 278 | -0.9762 | 8.5224 | -1.981 | fail | 75.0 | 45 | 0.9982 | none | not_run | B |
| 10 | K2-cp2-01 TN | 286 | -0.7984 | 10.6685 | -1.294 | fail | 75.5 | 6 | 0.9731 | none | not_run | B |
| 11 | K2-cp2-01 ZB | 285 | -0.6085 | 7.7396 | -1.359 | fail | 74.8 | 11 | 0.98 | none | not_run | B |
| 12 | K2-cp2-01 UB | 291 | -0.4993 | 9.4373 | -0.915 | fail | 75.1 | 11 | 0.9762 | none | not_run | B |
| 13 | K2-cp3-01 ZT | 121 | -0.3786 | 15.2973 | -0.428 | fail | 397.5 | 339 | 0.9793 | none | not_run | B |
| 14 | K2-cp3-01 ZF | 127 | -1.1973 | 17.6365 | -1.174 | fail | 389.3 | 17 | 0.9956 | none | not_run | B |
| 15 | K2-cp3-01 ZN | 131 | -0.6358 | 12.4658 | -0.882 | fail | 393.5 | 9 | 0.9982 | none | not_run | B |
| 16 | K2-cp3-01 TN | 136 | -1.1574 | 15.9279 | -1.257 | fail | 390.2 | 113 | 0.9752 | none | not_run | B |
| 17 | K2-cp3-01 ZB | 130 | -1.2233 | 11.8525 | -1.785 | fail | 380.6 | 21 | 0.9816 | none | not_run | B |
| 18 | K2-cp3-01 UB | 134 | -1.1845 | 13.1555 | -1.557 | fail | 376.5 | 15 | 0.9785 | none | not_run | B |
| 19 | K2-aucpre-01 ZT | 13 | -0.0500 | 1.6520 | -0.523 | fail | 179.0 | 179 | 0.9825 | none | not_run | B |
| 20 | K2-aucpre-01 ZF | 10 | -0.1639 | 2.0823 | -1.361 | fail | 179.0 | 179 | 0.9955 | none | not_run | B |
| 21 | K2-aucpre-01 ZN | 15 | 0.0384 | 2.9302 | 0.226 | fail | 179.0 | 179 | 0.998 | none | not_run | B |
| 22 | K2-aucpre-01 TN | 15 | 0.0983 | 4.2805 | 0.397 | fail | 179.0 | 179 | 0.9821 | none | not_run | B |
| 23 | K2-aucpre-01 ZB | 15 | 0.0389 | 2.4823 | 0.271 | fail | 179.0 | 179 | 0.9856 | none | not_run | B |
| 24 | K2-aucpre-01 UB | 15 | 0.0855 | 3.0513 | 0.484 | fail | 179.0 | 179 | 0.9851 | none | not_run | B |
| 25 | K2-aucpost-01 ZT | 13 | 0.0500 | 1.0308 | 0.839 | fail | 180.0 | 180 | 0.9725 | none | not_run | B |
| 26 | K2-aucpost-01 ZF | 10 | -0.0604 | 1.3489 | -0.774 | fail | 180.0 | 180 | 0.9947 | none | not_run | B |
| 27 | K2-aucpost-01 ZN | 15 | -0.1657 | 1.4179 | -2.021 | fail | 180.0 | 180 | 0.9981 | none | not_run | B |
| 28 | K2-aucpost-01 TN | 15 | -0.0871 | 1.8567 | -0.812 | fail | 180.0 | 180 | 0.9622 | none | not_run | B |
| 29 | K2-aucpost-01 ZB | 15 | -0.1625 | 3.4053 | -0.825 | fail | 168.1 | 0 | 0.9734 | none | not_run | B |
| 30 | K2-aucpost-01 UB | 15 | -0.1994 | 4.2058 | -0.820 | fail | 179.6 | 174 | 0.9662 | none | not_run | B |
| 31 | K2-fomcpost-01 ZT | 10 | -0.5651 | 4.7536 | -2.056 | fail | 95.0 | 95 | 0.9794 | none | not_run | B |
| 32 | K2-fomcpost-01 ZF | 10 | -0.5718 | 4.9706 | -1.989 | fail | 95.0 | 95 | 0.9951 | none | not_run | B |
| 33 | K2-fomcpost-01 ZN | 10 | -0.3903 | 3.3872 | -1.992 | fail | 95.0 | 95 | 0.9985 | none | not_run | B |
| 34 | K2-fomcpost-01 TN | 10 | -0.4172 | 3.7228 | -1.938 | fail | 95.1 | 95 | 0.9611 | none | not_run | B |
| 35 | K2-fomcpost-01 ZB | 10 | -0.2538 | 2.2835 | -1.922 | fail | 86.7 | 12 | 0.9737 | none | not_run | B |
| 36 | K2-fomcpost-01 UB | 10 | -0.2808 | 2.3357 | -2.078 | fail | 86.6 | 11 | 0.9643 | none | not_run | B |
| 37 | K2-predrift-01 ZN | 12 | -0.0302 | 1.2178 | -0.429 | fail | 15.0 | 15 | 0.9976 | none | not_run | B |
| 38 | K2-predrift-01 ZB | 11 | -0.0708 | 0.9863 | -1.241 | fail | 15.0 | 15 | 0.9921 | none | not_run | B |
| 39 | K2-monthend-01 ZT | 18 | 0.0087 | 3.4751 | 0.044 | fail | 464.0 | 464 | 0.979 | none | not_run | B |
| 40 | K2-monthend-01 ZF | 18 | -0.0314 | 4.3121 | -0.126 | fail | 464.1 | 464 | 0.9956 | none | not_run | B |
| 41 | K2-monthend-01 ZN | 18 | -0.0871 | 3.1202 | -0.483 | fail | 464.0 | 464 | 0.9982 | none | not_run | B |
| 42 | K2-monthend-01 TN | 18 | -0.1143 | 3.7588 | -0.526 | fail | 464.0 | 464 | 0.9732 | none | not_run | B |
| 43 | K2-monthend-01 ZB | 18 | -0.2262 | 3.3675 | -1.161 | fail | 438.4 | 1 | 0.9803 | none | not_run | B |
| 44 | K2-monthend-01 UB | 18 | -0.4341 | 5.3029 | -1.415 | fail | 415.3 | 20 | 0.9764 | none | not_run | B |

Tiers (K2_research_cluster.json, stage_e_stats.assign_tiers): **Tier A: none. Tier B: all 44** ("fails the D5
screen"). Excluded: none. Not tiered: none. power_check_undefined: none. Six trials have a positive mean
(K2-aucpre-01 ZN, TN, ZB, UB; K2-aucpost-01 ZT; K2-monthend-01 ZT), with daily t from 0.04 to 0.84, all below 1.0.

### Task 7: reading the result
- K2 enters the program with an empty Tier A, so it does not count in D5's K (the number of clusters with a
  non-empty Tier A). Its Holm family is empty, and no K2 member can reach "edge exists" in the confirmation session.
  The confirmation session still runs all 44 trials on the null side (Tier B), for the null-at-eps record (D7 and
  NULL_CRITERIA_E), after D4's power check.
- The three ports lose on every exposure. CP1's t runs from -5.34 (ZB) to -1.12 (ZF). CP2's and CP3's t run from
  -1.98 to -0.34. With one trip a day and a 29-minute hold, CP1's cost is carried on about 270 days. The event members
  trade 10 to 18 times in 299 days (C10's arithmetic), so their daily means sit near zero: largest |mean| 0.57 ticks,
  largest t 0.84.
- Program N after this session: 58 + 44 = 102. The runner does not count N; this is 58 (docs/STAGE_E_DESIGN.md D5
  line 317) plus the 44 screened trials.
- For the confirmation session: Tier A none; Tier B all 44 trials of section 0's ordinal table
  (reports/stage_e3_member_specs.md S0.2); the step 2 purchase for K2's six vehicles, $40.50 as quoted in E.2b.

## 4. Delegation record

| Agent (description) | Worker file | Model | Effort | Objective | Status | Deviations |
|---|---|---|---|---|---|---|
| AuctionXmlChecker-OpusMed | worker-medium | opus | medium | C9 check: announcement XML vs query closing_time_comp for the 340 tenor-matched auctions (brief reports/stage_e3_briefs/auction_xml_check.md) | done; 340/340 agree | Added by the lead (L-02): the prompt did not name it. It first returned an interim "waiting for the fetch" and then finished. |
| MemberCoder-A-OpusXHigh | worker-xhigh | opus | xhigh | Code K2-cp1-01, K2-cp2-01, K2-cp3-01, K2-monthend-01 and their tests (briefs coder_common.md, coder_A.md) | done | Moved the asdict open read into cp1.py after ruling R-T2-1. |
| MemberCoder-B-OpusXHigh | worker-xhigh | opus | xhigh | Code K2-aucpre-01, K2-aucpost-01, K2-fomcpost-01, K2-predrift-01, the release table and their tests (coder_common.md, coder_B.md) | done | Raised the `open` ban (R-T2-1). No other questions. |
| MemberAuditor-FableXHigh, part 1 | worker-xhigh | fable | xhigh | Task 3 fidelity audit (auditor_task3.md) | done; 0 BLOCKING, 0 SHOULD FIX, 12 NOTE | Started before the Task 2 suite gate finished (it passed at 00:24). |
| MemberAuditor-FableXHigh, part 2 (resumed with SendMessage) | worker-xhigh | fable | xhigh | Task 6 recomputation (auditor_task6.md) | done; items 1-5 VERIFIED or VERIFIED WITH NOTES, no DISCREPANCY; predrift follow-up VERIFIED (s = 0) | Item 3 replays two trials in memory to obtain trip lists (R-T6-1). |

No worker spawned another. At most 3 ran at once. Fable was used by the one auditor only, as the prompt set.


## 5. Verification

Both checks were done by MemberAuditor-FableXHigh (fable, xhigh), which wrote none of the code, specs, tests or runs.
Full text: reports/stage_e3_member_audit.md.

**Part 1, the fidelity audit (Task 3, 00:11-00:28).** 0 BLOCKING, 0 SHOULD FIX, 12 NOTE. Each note, with the
lead's ruling (reports/stage_e3_member_rulings.md). No note changed any code.

| Note | Finding | Ruling |
|---|---|---|
| N-1 | write_k2_freeze.py needs `PYTHONPATH=.` | Accepted; the freeze was written that way. |
| N-2 | two copies of the asdict open read | No change (one line each). |
| N-3 | D6 CP1 uses the first bar's open where MES F3.3 used its close | A property of the frozen D6 text. The code follows D6. |
| N-4 | L-15's time filter binds on no calendar row, so its test is vacuous | No change: the tables are identical either way. |
| N-5 | CP2's coverage window ends at the literal 15:08 | No change: only the coverage check uses it. |
| N-6 | S0.12's aucpre window leaves out the one 09:00 T_a | Clarified: that date is an early halt in the confirmation window. |
| N-7 | CP3 does not read O_d | Equivalent: no condition uses O_d. |
| N-8 | some boundaries are pinned only by the auditor's scenarios | No change; the evidence is its scenarios.py. |
| N-9 | the two exit helpers differ on an unreachable pending state | No trade can differ. |
| N-10 | the ISM fill guard concerns ZN and ZB, not TN | The frozen D9.5a and release calendar govern. |
| N-11 | the FOMC table starts 2019-05-01 | Harmless: the runner bounds the window. |
| N-12 | CP2 relies on the engine's flatten across a date change | D6's "or the engine's forced flatten at F". |

The auditor also confirmed R-T2-1 (the asdict read returns the bar's own open and opens no file). It agreed with all 23
lead readings, each either the narrowest reading or fixed by its cited reference. It recomputed every literal table
from its frozen source (340 auctions, 57 FOMC, 86 ISM, 85 months), and it found no vacuous test apart from N-4.

**Part 2, the recomputation (Task 6, 00:51-01:02; follow-up 01:02-01:04).**

| Item | Verdict | Content |
|---|---|---|
| 1 Screen figures, 44 records | VERIFIED WITH NOTES (44 of 44) | Mean, population sd, daily t and passes recomputed in the auditor's own code from each record's series; all agree to 1e-9 relative. Each series is the 299 window dates with zeros, and its non-zero days equal n_trips. Notes: the power check was not run for any trial (StartRuleMissing, by design), and 24 records include MLL liquidations (below). |
| 2 Tiers against D5 | VERIFIED | All 44 fail the screen, so all 44 are Tier B. No labels. Coverage 0.9611-0.9986, all above 0.95. Nothing excluded, refused or not tiered. |
| 3 Two daily series rebuilt from trips and the cost table | VERIFIED (K2-cp1-01 ZN, K2-aucpost-01 ZN) | Replayed in memory under R-T6-1: each replayed series, counters and bar sha equal the record exactly. The trips (reports/stage_e3_briefs/audit/trips_*.json) were costed in the auditor's own code from the frozen table (commission, bucket slippage, the D8 event window, ceil to the cent). Every fill and every day matches, worst difference 0. |
| 4 Trade counts and fill minutes | VERIFIED WITH NOTES, then VERIFIED after the follow-up | Every event member's shortfall against the calendar is explained by roll blackouts (for example ZF's five late-month 5-year auctions) or the 2025-11-28 halt. The follow-up replayed K2-predrift-01 ZN and ZB (both equal their records): on all 7 untraded (date, root) pairs, both signal bars were present, with one instrument_id and no halt, and s = 0 (the 08:49 close equalled the 08:30 open to the tick). So the rule's "no trade" applied, with no member defect. The replayed trials' fill minutes match the rules, apart from one MLL liquidation. |
| 5 Program N | VERIFIED | 44 trials screened, 0 refused, and the records equal the freeze's 44 declarations. N = 58 + 44 = 102. |

No DISCREPANCY, so no tier is "unverified". The tiers are final for the confirmation session.

**Note on the MLL liquidations (harness property, reported, no ruling needed).** The frozen engine simulates the XFA
50K account (MLL $2,000 below the start balance, trailing). When a trial's cumulative losses reach the floor, it
liquidates the open position on that bar and starts a new account, as in the MES regressions. This happens 1 to 11
times in 24 of the 44 series: CP1, CP2 and CP3 on most exposures, with 11 each for CP3 on ZB and UB. Those exits change
the affected days from what the rule alone would give, and the direction of the effect on a mean is not established.
No trial is near the screen (the largest t is 0.84), and the liquidations fall on the ports, whose t runs from -5.34
to -0.34, so the tiers do not depend on them. The same account model will apply in the confirmation window.

## 6. Open choices (each decided by the lead alone, with the reason; each can be overturned)

Readings in the specs (reports/stage_e3_member_specs.md section 10; the auditor agreed with every one):
- **L-01** Event dates reach the members as literal tables in the cluster package (_releases.py, _month_end.py),
  generated from the frozen release calendar and EC-CAL and pinned by tests. Reason: a member can read no file, and
  the interface passes no calendar.
- **L-02** The catalog's C9 XML check was run in this stage (Task 1b). An auction is dropped only on a disagreement.
  Reason: E.2 was assigned the check and never ran it, and it defines the event set.
- **L-03** "The bar at hh:mm" is on CT calendar date d (Family H's reading).
- **L-04** A named entry bar is exact: if it is missing, no entry. Reason: the narrowest reading. The entries say
  "on the bar at" for entries and "first bar at or after" for exits.
- **L-05** CP1's first bar is the 17:00 CT Globex-open bar of d-1; if it is missing, no trade. Reason: the narrowest
  reading, and the catalog's instantiation names that bar. MES F3.3 used the first present bar.
- **L-06** CP1's instrument guard is D6's (two signal bars only).
- **L-07** CP2's 75-minute hold counts present bars, as the MES module does (fixed by reference). There is no C-2 exit.
- **L-08** CP2's range comes from the present bars, with no minimum and no guard. The first qualifying bar uses the
  day's one entry.
- **L-09** CP3 follows Family H by reference: d-1 is the most recent complete daily bar, and an early-halt day d is
  not traded.
- **L-10** CP3 exits on the first bar at or after 13:58.
- **L-11** "Early halt or early close" means the bar's early_halt_ct (C4's parenthesis). Early-settlement-only days
  are traded.
- **L-12** C4's instrument guard covers the bars read at or before the entry decision.
- **L-13** C4's "entry bar" is the bar the entry intent is emitted on.
- **L-14** T_a is the calendar instant in CT (= closing_time_comp ET - 1 h).
- **L-15** FOMC and ISM rows are filtered on 13:00 CT and 10:00 ET. The filter binds on no row.
- **L-16** Month-end N and N-1 come from EC-CAL, with halt days counted as trade dates. C4 applies per date, and
  nothing moves.
- **L-17** trading_windows are the fixed intervals of S0.12, measured on every research date.
- **L-18** 44 declarations. Ordinals in catalog order, then ZT, ZF, ZN, TN, ZB, UB.
- **L-19** All price comparisons are in integer vendor ticks.
- **L-20** ZT and ZF ("undersized") are coded and screened, as the frozen runner trades them.
- **L-21** Two test files (tests/test_e3_k2_members.py and tests/test_e3_k2_members_events.py) instead of the one
  the prompt named. Reason: two coders worked in parallel.
- **L-22** A refused exit is resent on the next present bar.
- **L-23** The two re-keyed reopenings (2019-11-05, 2026-01-26) stay as keyed by original_security_term. Reason: the
  frozen text and its frozen counts. **Flagged for the user:** in substance, ZF trades a 2-year auction on
  2026-01-26.

Rulings during the session:
- **R-T2-1** A bar's open is read through `dataclasses.asdict`, because the frozen static check bans the name `open`.
- **R-T5-1** After crash C-1, the frozen runner's main() was re-run with identical argv from an import rather than
  `python -m`. No code changed, and the crashed attempt wrote nothing. **Flagged for the user:** the harness's CLI
  path lets refusals escape (section 7).
- **R-T6-1** The runner writes no trip list. Task 6's rebuild replays two trials in memory through the runner's own
  functions, after checking the replayed series equals the recorded one. The same conditions were extended at 01:05 to
  replay K2-predrift-01 ZN and ZB, to explain 3 untraded ISM dates common to both (s = 0). Every replay equals its record.
- The audit NOTE rulings N-1..N-12 (reports/stage_e3_member_rulings.md): no change for any.
- pytest runs without PYTHONPYCACHEPREFIX, as E.2b's reference command does (three bytecode tests fail with it set).
  Every Stage E entry point runs with a fresh prefix.
- Program N is computed as 58 + 44 = 102, because the runner does not count N.
- The freeze script and the briefs stay uncommitted in reports/stage_e3_briefs/, as E.2b's did. The commit holds
  exactly the files the prompt names.
- The XML check reports (reports/stage_e3_auction_xml_check.*) are left out of the freeze commit, which the prompt
  limits to named files. They are uncommitted for review.
- Task 3 (the audit) was spawned at 00:11, while Task 2's full-suite gate was still running. The gate passed at 00:24,
  and the audited files were unchanged (hash check at 00:29). Reason: to save time, since any fix would have gone
  through the audit anyway.
- docs/STAGES.md: the "Stage E.3 onward" line is relabelled "Stage E.3b onward" (K2's confirmation and the later
  clusters), and a Stage E.3 line is added above it.

## 7. What the next session must do first

- **Push (the planning chat).** Commit a79b47e (the K2 member freeze) is local and not pushed; origin/main is at
  9741e63 (the local tracking ref), one commit behind. Uncommitted for review: reports/E.3_RETURN.md, reports/stage_e3_STATE.md, the Task 6 part of
  reports/stage_e3_member_audit.md (the committed file holds part 1), reports/stage_e3_k2_screen/ (the runner's
  45 records), reports/stage_e3_auction_xml_check.json/.md, reports/stage_e3_coder_A.md and _B.md,
  reports/stage_e3_briefs/ (briefs, the freeze script, the auditor's scripts and trip files), progress.md and
  docs/STAGES.md.
- **Frozen hashes.** Harness manifest cf939270f0a00be74aa29a43f0c7de964256411a9cdcebc36f22fd3bdc021a45 (unchanged).
  K2 cluster freeze reports/stage_e_k2_member_freeze.json, 8815a775e74996419b57751b1104ffa07cd4b3450eb18a9a92c6cbbd5615b7c5.
  E.1 freeze 96166eb3..., E.2a ML freeze 077a57e1..., release calendar 839f2437... (all unchanged).
- **Funding the user owes for K2's confirmation.** The step 2 history for ZT, ZF, ZN, TN, ZB and UB costs $40.50 as
  quoted in E.2b. acct-2 holds $21.52 of its $125.00 cap, so the top-up is $18.98, or $23.03 with D13's +10%. That
  session edits data/config.py, so it writes harness manifest v3 (only that entry differs) and uses the new sha256.
  It then builds the start rule (`python -m screening.stage_e_start_dates`), runs D4's power check for the 44 trials
  (seeds from the frozen ordinals), hashes the confirmation list and runs it once.
- **Blocker for the confirmation session: harness bug C-1.** Under `python -m screening.stage_e_runner`, every refusal
  that screening/stage_e_start_dates.py raises through `_runner()` escapes the runner's `except` clauses, because
  the runner is loaded twice. That covers StartRuleMissing, StartWindowEmpty and the other six, and on the
  confirmation window they would crash the run instead of being recorded by name. Either fix it in the harness (for
  example, look up the runner module through `sys.modules['__main__']` when it is the runner, or catch by class name),
  which needs a review and goes in with manifest v3, or launch the runner from an import as this session did (R-T5-1).
  This is the user's decision.
- **The runner writes no trip list.** The prompt expected one. If the confirmation session needs trip-level evidence,
  it must replay in memory (R-T6-1) or the harness must write trips. This is the user's decision.
- **Questions for the user from this session:** L-23 (2026-01-26 traded as a 5-year auction on ZF); the C-1 fix; the
  missing trip list. The E.2b return's open decisions (section 7 there) are all still open. Two of them bear on K2's
  confirmation: the non-MES composite verdict (OC-Q) and the power-check-undefined case.

## 8. Session cost

Wall clock 23:35-01:15 PDT (101 min), with no pause or outage, so all of it is work time. Per-task times are in the table, from reports/stage_e3_STATE.md and the transcripts' first and last message times. Tokens are summed from each assistant message's usage fields, deduplicated by message id, over this session's transcript and its subagent transcripts (837e1130-3b1c-4fe2-8242-94af0469e3ba.jsonl and 837e1130-3b1c-4fe2-8242-94af0469e3ba/subagents/*.jsonl), up to 01:15 PDT. The lead's figure excludes the few messages after this computation. These are token counts, not plan-credit percentages.

Final ETA table:

| Task / spawn | Owner | Model | Effort | Start | End | Time | Tokens | Status and deviations |
|---|---|---|---|---|---|---|---|---|
| 0 Startup checks, start suite (2 runs) | lead | opus | xhigh | 23:35 | 00:01 | 26 min | in lead total | done; run 1 set PYTHONPYCACHEPREFIX (3 bytecode tests failed), run 2 as E.2b = 2863 passed |
| 1 Member specs (L-01..L-22; L-23 at 00:08) | lead | opus | xhigh | 23:40 | 23:52 | 12 min | in lead total | done |
| 1b C9 auction XML check (added, L-02) | AuctionXmlChecker-OpusMed | opus | medium | 23:45 | 00:03 | 18 min | 2,182,157 | done; 340/340 agree |
| 2 CP1-CP3, month-end, tests | MemberCoder-A-OpusXHigh | opus | xhigh | 23:53 | 00:11 | 18 min | 14,358,294 | done; 98 tests |
| 2 Event members, release table, tests | MemberCoder-B-OpusXHigh | opus | xhigh | 23:53 | 00:09 | 16 min | 12,103,378 | done; 47 tests; raised the open ban (R-T2-1) |
| 2 gate: full suite | lead | - | - | 00:11 | 00:24 | 13 min | in lead total | 3008 passed |
| 3 Fidelity audit | MemberAuditor-FableXHigh | fable | xhigh | 00:11 | 00:29 | 17 min | 3,467,139 | done; 0 BLOCKING, 0 SHOULD FIX, 12 NOTE |
| 4 Rulings, freeze, suite, commit a79b47e | lead | opus | xhigh | 00:28 | 00:44 | 16 min | in lead total | done; suite 3008 passed |
| 5a Screening attempt 1 | lead (frozen CLI) | - | - | 00:43:15 | 00:43:26 | 0.2 min | in lead total | CRASHED C-1 (harness double import); nothing written |
| 5b Screening run (R-T5-1) | lead (frozen main via import) | - | - | 00:44:56 | 00:50:39 | 6 min | in lead total | done; 44 records, 0 refused |
| 6 Recomputation + predrift follow-up | MemberAuditor-FableXHigh | fable | xhigh | 00:50 | 01:04 | 13 min | 5,447,346 | done; no DISCREPANCY |
| 7 End suite, end checks, return, progress, STAGES, cost | lead | opus | xhigh | 01:02 | 01:15 | 14 min | in lead total | done |
| Lead (all lead rows) | lead | opus | xhigh | 23:35 | 01:15 | - | 46,540,067 | - |
| **Stage total** | lead + 5 spawn records (4 agents) | - | - | 23:35 | 01:15 | **101 min**, no pauses | **84,098,381** | initial estimate about 8 h 30 min (to about 08:10); the coders and the audit ran far faster than guessed |

Tokens per model:

| Model | Input | Output | Cache read | Cache creation | Total |
|---|---|---|---|---|---|
| claude-fable-5-1 | 938 | 1,914 | 8,179,334 | 732,299 | 8,914,485 |
| claude-opus-5-5 | 704 | 232,651 | 73,777,596 | 1,172,945 | 75,183,896 |
| all | 1,642 | 234,565 | 81,956,930 | 1,905,244 | 84,098,381 |

Per worker spawn:

- AuctionXmlChecker-OpusMed: worker-medium, opus (claude-opus-5-5), effort medium: 2,182,157 tokens (input 54, output 4,112, cache read 1,947,023, cache creation 230,968)
- MemberAuditor-FableXHigh part 1 (Task 3): worker-xhigh, fable (claude-fable-5-1), effort xhigh: 3,467,139 tokens (input 546, output 733, cache read 3,162,923, cache creation 302,937)
- MemberAuditor-FableXHigh part 2 (Task 6 + follow-up): worker-xhigh, fable (claude-fable-5-1), effort xhigh: 5,447,346 tokens (input 392, output 1,181, cache read 5,016,411, cache creation 429,362)
- MemberCoder-A-OpusXHigh: worker-xhigh, opus (claude-opus-5-5), effort xhigh: 14,358,294 tokens (input 158, output 5,178, cache read 14,068,984, cache creation 283,974)
- MemberCoder-B-OpusXHigh: worker-xhigh, opus (claude-opus-5-5), effort xhigh: 12,103,378 tokens (input 142, output 18,603, cache read 11,833,649, cache creation 250,984)

Delegation share: lead 46,540,067 (55.3%), workers 37,558,314 (44.7%). By model tier: claude-fable-5-1 8,914,485 (10.6%), claude-opus-5-5 75,183,896 (89.4%). Cache reads are 97.5% of all tokens.
