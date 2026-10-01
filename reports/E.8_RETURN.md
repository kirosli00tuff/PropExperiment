# Stage E.8 return: K6 grains, oilseeds and livestock coded, audited, frozen and screened (no purchase)

Lead: Opus 5.5 xhigh, session 94d6572b-fdf2-4814-9116-60c2521d80a0, 2026-09-30 23:57 to 2026-10-01 02:45 PDT (times PDT).
Prompt: docs/prompts/STAGE_E.8.md (commit c865a87). STATE: reports/stage_e8_STATE.md.

## 1. Verdict summary

27 K6 trials coded, Fable-audited (0 blocking, 0 should-fix, 11 notes), **frozen in commit 0a14a9a (cluster freeze
a6f8b497eee727688f3d0e9a3fc7af3abfe41c02f0354a55f5d918c01e61c604)** and run once on the research window: 27 run, 0
refused, none unimplementable. The Fable recomputation found no discrepancy.

| Tier | Trial | Trips | Mean net ticks/day | Daily t |
|---|---|---|---|---|
| A | K6-limitcont-01 HE | 1 | +0.1869 | 1.002 |
| B | the other 26 (best: cp3 LE +1.53, t 0.57; cp3 ZM +0.47, t 0.50) | 0-280 | -4.29 to +1.53 | <= 0.57 |

**K6's Tier A rests on one trade:** a single positive day among 273 gives t = sqrt(273/272) = 1.002 whatever its size, so
D5 passes it mechanically. K6-limitcont-01 LE did not trade (0 trips). Events: all 14 research-window WASDE releases kept
(the moved 2025-11-14 release kept on USDA's notice); none dropped or unverifiable. One limit period dropped for the
member: LE 2026-06-01..06-18 (CME raised the limit to $0.0850; the frozen table says $0.0725). **Program N = 167 + 27 =
194.** A K6 confirmation would need the seven contracts' step 2 history ($26.52 quoted 2026-09-26) and an acct-2 top-up of
about $26.19 ($28.85 with 10%); acct-2 holds $0.33.

## 2. Guardrail evidence

**Start checks** (reports/stage_e8_briefs/start_checks.out, verbatim):

```
$ date
Wed Sep 30 11:57:03 PM PDT 2026
$ git status --short
?? reports/stage_e8_briefs/
$ git log --oneline -3
2e22522 docs: DECISIONS V16 (K8 rules) and V17 (order of work after screening)
2dfaaf7 docs: log Phidias Propfirm as researched, blocked venue candidate
880bfc7 docs: Stage E.7 results, K1 screened, all 11 trials Tier B, N = 167
$ wc -c REGISTRATION.md
0 REGISTRATION.md
$ uv run python -m data.holdout status (keys)
holdout_1 all_ok True unlocks_logged 0 unlock_log_ok True
holdout_2 all_ok True unlocks_logged 0 unlock_log_ok True
$ python3 reports/stage_e2b_briefs/check_frozen.py
reports/stage_e1_freeze.json: manifest sha256 96166eb39b85d4fdcf132092978ee85393392de52c3857dc3f64ea7281454a7c files 32/32 match
reports/stage_e2a_ml_freeze.json: manifest sha256 077a57e1c00554dd0745302b247673d45ee05b805ac4bfd876f8497f7bbb1ed2 files 4/4 match
ALL_OK
$ PYTHONPYCACHEPREFIX=<fresh> uv run python -m screening.harness_freeze verify --expected 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87
preflight OK: 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87
$ cluster freezes (load_cluster_freeze + verify_cluster_code)
K2 cluster freeze OK 8815a775e74996419b57751b1104ffa07cd4b3450eb18a9a92c6cbbd5615b7c5 44 members
K4 cluster freeze OK 7abcde1705440e97efcf1ce255d979213eed9840f03a8383f2784a74f5f1534a 12 members
K5 cluster freeze OK 1d0c974f18e884e1ad073d8f6f94d7bb70ee6f43971c7f23ccacab54103b3655 11 members
K3 cluster freeze OK c4fb5da41d69a6be54ea07d1ab35bd2b238d1fbeafaeb3008b886f8fc6888d95 30 members
K7 cluster freeze OK 46cae3082ae17cfd2a0e731cba27f6cc5dd2bdb94bb757d7ae48c684a5449462 6 members
K1 cluster freeze OK cf48f514dcf26490fa79a4322f764af991ee2555f2147354f12a31621fbe7ce2 11 members
K6 no freeze: ClusterFreezeError
$ ledger
17400 ledger/databento_spend.jsonl
0b5466c4366ca9eaba7e10525545631c83e97c1184a7e745d5ed8ad47a9fe957
$ acct-2 position (pull_step2.account_position on the step 2 gate; reads the ledger only)
stage-E.5-2026-09-27 {'account': 'acct-2', 'account_cap_usd': 125.0, 'account_credit_usd': 125.0, 'spent_usd': 124.673761, 'cap_headroom_usd': 0.326239, 'credit_left_usd': 0.326239}
$ python -m data.pull_step2 --status (ZC ZW ZS ZM ZL HE LE)
roots in status: 45 ; states: ['not_bought', 'sealed']
ZC {"state": "not_bought"}
ZW {"state": "not_bought"}
ZS {"state": "not_bought"}
ZM {"state": "not_bought"}
ZL {"state": "not_bought"}
HE {"state": "not_bought"}
LE {"state": "not_bought"}
```

`uv run pytest -q` at start (reports/stage_e8_briefs/pytest_start.out, run 23:58-00:09:24 without PYTHONPYCACHEPREFIX, as
E.6 and E.7 did: three bytecode tests of tests/test_harness_freeze.py fail under a prefix): **4743 passed, 2 skipped, 1
xfailed** (= E.7's end result). HEAD 2e22522, a descendant of c865a87 (the commit holding the prompt); clean tree but for
the new briefs folder.

**End checks** (reports/stage_e8_briefs/end_checks.out, verbatim):

```
$ date
Thu Oct  1 02:26:54 AM PDT 2026
$ git status --short
 M reports/stage_e8_member_audit.md
?? reports/stage_e8_STATE.md
?? reports/stage_e8_briefs/
?? reports/stage_e8_coder_A.md
?? reports/stage_e8_coder_B.md
?? reports/stage_e8_k6_screen/
$ git log --oneline -3
0a14a9a feat: K6 member freeze (Stage E.8), cluster freeze sha256 a6f8b497
2e22522 docs: DECISIONS V16 (K8 rules) and V17 (order of work after screening)
2dfaaf7 docs: log Phidias Propfirm as researched, blocked venue candidate
$ wc -c REGISTRATION.md
0 REGISTRATION.md
$ uv run python -m data.holdout status (keys)
holdout_1 all_ok True unlocks_logged 0 unlock_log_ok True
holdout_2 all_ok True unlocks_logged 0 unlock_log_ok True
$ python3 reports/stage_e2b_briefs/check_frozen.py
reports/stage_e1_freeze.json: manifest sha256 96166eb39b85d4fdcf132092978ee85393392de52c3857dc3f64ea7281454a7c files 32/32 match
reports/stage_e2a_ml_freeze.json: manifest sha256 077a57e1c00554dd0745302b247673d45ee05b805ac4bfd876f8497f7bbb1ed2 files 4/4 match
ALL_OK
$ PYTHONPYCACHEPREFIX=<fresh> uv run python -m screening.harness_freeze verify --expected 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87
preflight OK: 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87
$ cluster freezes (load_cluster_freeze + verify_cluster_code)
K2 cluster freeze OK 8815a775e74996419b57751b1104ffa07cd4b3450eb18a9a92c6cbbd5615b7c5 44 members
K4 cluster freeze OK 7abcde1705440e97efcf1ce255d979213eed9840f03a8383f2784a74f5f1534a 12 members
K5 cluster freeze OK 1d0c974f18e884e1ad073d8f6f94d7bb70ee6f43971c7f23ccacab54103b3655 11 members
K3 cluster freeze OK c4fb5da41d69a6be54ea07d1ab35bd2b238d1fbeafaeb3008b886f8fc6888d95 30 members
K7 cluster freeze OK 46cae3082ae17cfd2a0e731cba27f6cc5dd2bdb94bb757d7ae48c684a5449462 6 members
K1 cluster freeze OK cf48f514dcf26490fa79a4322f764af991ee2555f2147354f12a31621fbe7ce2 11 members
K6 cluster freeze OK a6f8b497eee727688f3d0e9a3fc7af3abfe41c02f0354a55f5d918c01e61c604 27 members
$ ledger
17400 ledger/databento_spend.jsonl
0b5466c4366ca9eaba7e10525545631c83e97c1184a7e745d5ed8ad47a9fe957
$ acct-2 position (pull_step2.account_position on the step 2 gate; reads the ledger only)
stage-E.5-2026-09-27 {'account': 'acct-2', 'account_cap_usd': 125.0, 'account_credit_usd': 125.0, 'spent_usd': 124.673761, 'cap_headroom_usd': 0.326239, 'credit_left_usd': 0.326239}
$ python -m data.pull_step2 --status (ZC ZW ZS ZM ZL HE LE)
roots in status: 45 ; states: ['not_bought', 'sealed']
ZC {"state": "not_bought"}
ZW {"state": "not_bought"}
ZS {"state": "not_bought"}
ZM {"state": "not_bought"}
ZL {"state": "not_bought"}
HE {"state": "not_bought"}
LE {"state": "not_bought"}
```

`uv run pytest -q` at end (reports/stage_e8_briefs/pytest_end.out, 02:14:57-02:26:46): **5373 passed, 2 skipped, 1
xfailed** (= 4743 + 630 K6 tests). Other suites: gate 01:38-01:50 5373 passed (a first gate run at 01:28 died at about
1% with "Disk quota exceeded", section 4); Task 4 01:58-02:10 5373 passed.

- **Manifest and freeze checks:** E.1 manifest 96166eb3... 32/32 and E.2a ML 077a57e1... 4/4 (ALL_OK) at start and end;
  harness v6 preflight OK at start, end and in the runner; cluster freezes K2, K4, K5, K3, K7, K1 OK at start and end, K6
  absent at start and OK at end (a6f8b497..., 27 members).
- **Ledger diff:** none. 17400 lines, sha256 0b5466c4366ca9eaba7e10525545631c83e97c1184a7e745d5ed8ad47a9fe957 at start
  and end; acct-2 spent $124.673761, $0.326239 left, unchanged. No Databento call, no quote, no purchase.
- **Holdout:** all_ok, unlocks_logged 0 (holdout-1 and holdout-2) at start and end. REGISTRATION.md 0 bytes at start and
  end. No TopstepX reference, no credential, no edit under live/ or ops/, no frozen file or manifest edited.
- **Research window only:** bars were read by the frozen runner alone (data/processed, research parquets with recorded
  sha256). No script of this session opened a bar file. The Task 3 auditor's first scratch copy of the repository included
  data/ (5.7 GB) in /tmp; it was deleted by the lead within minutes, unread (section 4).
- **The one commit:** 0a14a9a "feat: K6 member freeze (Stage E.8), cluster freeze sha256 a6f8b497" (26 files: the 13 member
  modules, 7 test files, the specs, the release check .md and .json, the audit Part 1, the rulings, the cluster freeze).
  No push.

`git status --short` at the end (before this return, progress.md and docs/STAGES.md were written):

```
 M reports/stage_e8_member_audit.md
?? reports/stage_e8_STATE.md
?? reports/stage_e8_briefs/
?? reports/stage_e8_coder_A.md
?? reports/stage_e8_coder_B.md
?? reports/stage_e8_k6_screen/
```

`git diff --stat` at the end: `reports/stage_e8_member_audit.md | 158 +++` (Part 2, written after the commit), 1 file
changed. After this document: also `M docs/STAGES.md`, `M progress.md`, `?? reports/E.8_RETURN.md`.

## 3. Results per task

**Task 0 (startup).** Start checks 23:57 all pass; start suite = E.7's end. Task 0 done 00:09.

**Task 1 (specs, lead).** reports/stage_e8_member_specs.md (sections 0-10, with catalog line references). 27 declarations
in catalog order then ZC, ZW, ZS, ZM, ZL, HE, LE. Readings adopted from earlier clusters (the same text): E.3-L-01, 03, 04,
06-13, 15, 17, 19, 20, 22; K4-L-01, 03, 05, 06, 13; K3-L-11; K7-L-01; K1-L-10, K1-L-14 10(c), K1-L-16. Not adopted:
E.3-L-05 (K6's text differs) and K7-L-03 (no vendor-degraded clause). New readings K6-L-01..K6-L-18, each in section 6
below; the ones that bear on trades:
- K6-L-01 grain CP1's first bar = the earliest bar of d at or after 19:00 CT on the calendar day before d (on the three
  late-open dates, normally the 08:30 bar; amended per R-T3-1);
- K6-L-02 livestock CP1's first bar = the 08:30 bar exactly;
- K6-L-03 crushgap's GPM in exact integer units: GPM x 10^4 = 22 t_ZM + 11 t_ZL - 25 t_ZS; filter 200 units;
- K6-L-06 limitcont's settlements = the D9.7 settlement proxy as the engine computes it (the 01:52 E.0 ruling and D9.7);
- K6-L-07 limitcont reads the frozen initial limit and requires d-2 not to be a limit close (no expanded table frozen);
- K6-L-08 exact equality in vendor ticks; K6-L-09 c and its guard; K6-L-10 C4 by table; K6-L-11 WASDE rows after C9a.

**Task 1b (event check, ReleaseChecker-OpusMed).** reports/stage_e8_release_check.md and .json; evidence pages under
reports/stage_e8_briefs/pages/. Rulings R-1b-1..R-1b-6 (specs section 10):
- WASDE: 14 rows, all keep (date = OCE schedule and ESMIS; 2025-11-14 moved from Nov 10 by the NASS notice of 2025-10-31,
  dated before it; October 2025 cancelled, no row; all 12:00 ET). DROPPED_WASDE empty.
- HE and LE limits: 5 periods keep, 1 drop: LE 2026-06-01..06-18 (CME SER-9736: $0.0850 from trade date 2026-06-01; the
  frozen table $0.0725). The member does not trade a d whose test reads a dropped date (R-1b-2).
- EC-CAL: 32 dates keep, all cited; F agrees across roots. Other inputs: none read; no WASDE-FOMC date.
- No free external series is read by any K6 member, so nothing was fetched into data/vendor/.

**Task 2 (code).** strategy/members/k6/: _port_common.py, cp1.py, cp2.py, cp3.py, crushgap.py (MemberCoder-A);
_calendar.py, _wasde.py, _limits.py, _event_common.py, limitcont.py, wasdepre.py, wasdepost.py (MemberCoder-B); __init__.py
0 bytes (lead). Tests: tests/test_k6_members_ports.py, _ports_cp2.py, _ports_cp3.py, _crushgap.py (A); _tables.py,
_limitcont.py, _wasde.py (B): 630 tests, all passing; they pin entry and exit times, the event windows, the flatten,
missing bars at decision times, a moved and a dropped release, a limit close, the D9.7 limit-proximity exit and entry
refusal through the real engine, and crushgap's signal legs (D11.5). Coders' mutants: A 153/158 killed, B 99/104 killed,
every survivor equivalent. Reports reports/stage_e8_coder_A.md and _coder_B.md (B's saved by the lead after the harness
refused the coder's write).

**Task 3 (audit).** reports/stage_e8_member_audit.md Part 1: 0 BLOCKING, 0 SHOULD FIX, 11 NOTE; all seven tables
recomputed identical; limitcont's proxy equal to the engine's on 28 scenarios and its window and d-1..d-3 chain on all
1,795 livestock dates; 101 of 102 auditor mutants killed (1 equivalent); every reading agreed.

**Task 4 (rulings, freeze, commit).** reports/stage_e8_member_rulings.md: R-T3-1 (specs wording, K6-L-01), R-T3-2 (a
label), R-T3-3 (specs, N-7); no code or test change. Freeze written 01:58, verified; suite 5373 passed; commit 0a14a9a
02:10:12.

**Task 5 (the screening run).** The frozen command once, 02:10:25-02:12:46, exit 0: "K6 research: 27 members, 0
refused" (reports/stage_e8_briefs/t5_run.log; outputs reports/stage_e8_k6_screen/, 27 records, 27 trip lists, the cluster
file). Windows 264-287 dates from 2025-04-01 (roll-blackout dates of every leg read and UR-1 removed by the runner). Power
not_run on every record (StartRuleMissing: no frozen S_X), as in E.6 and E.7. No runner label (coverage 0.9934-1.0 on every
leg; no D9 floor label).

Per trial (from the runner's files; mean in net ticks per contract per day with zeros on no-trade days; MLL liquidations
from the engine's counter, which equals the MLL-closed trips; the accounts restarted in brackets, which exceeds it by one on
cp1 ZW and ZM because a breach on an ordinary closing fill restarts the account without a liquidation fill):

| Ord | Trial | Status | Trips | Days | Mean ticks/day | Daily t | Min coverage | Mean hold min | MLL liquidations (accounts restarted) | D9.7 exits | D9.7 entry refusals | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | K6-cp1-01 ZC | run | 265 | 276 | -1.3932 | -6.013 | 0.9998 | 28.8 | 2 (2) | 0 | 2 | B |
| 2 | K6-cp1-01 ZW | run | 269 | 283 | -1.3931 | -4.334 | 0.9978 | 29.0 | 1 (2) | 0 | 3 | B |
| 3 | K6-cp1-01 ZS | run | 280 | 285 | -2.5301 | -5.756 | 0.9999 | 28.8 | 4 (4) | 0 | 1 | B |
| 4 | K6-cp1-01 ZM | run | 270 | 278 | -1.4134 | -3.820 | 0.9987 | 28.9 | 1 (2) | 0 | 1 | B |
| 5 | K6-cp1-01 ZL | run | 271 | 287 | -1.1361 | -1.235 | 0.9962 | 28.9 | 1 (1) | 1 | 7 | B |
| 6 | K6-cp1-01 HE | run | 255 | 273 | -1.7366 | -3.717 | 0.9963 | 28.6 | 2 (2) | 3 | 9 | B |
| 7 | K6-cp1-01 LE | run | 197 | 266 | -1.6911 | -1.699 | 0.9984 | 27.6 | 2 (2) | 14 | 59 | B |
| 8 | K6-cp2-01 ZC | run | 247 | 276 | -1.2369 | -2.414 | 0.9996 | 72.1 | 2 (2) | 0 | 0 | B |
| 9 | K6-cp2-01 ZW | run | 265 | 283 | -1.5501 | -2.014 | 0.9948 | 74.2 | 3 (3) | 0 | 1 | B |
| 10 | K6-cp2-01 ZS | run | 272 | 285 | -1.9418 | -1.803 | 0.9998 | 72.6 | 5 (5) | 1 | 0 | B |
| 11 | K6-cp2-01 ZM | run | 262 | 278 | -3.2959 | -3.458 | 0.9973 | 72.8 | 5 (5) | 1 | 0 | B |
| 12 | K6-cp2-01 ZL | run | 276 | 287 | -0.5481 | -0.262 | 0.9973 | 73.3 | 3 (3) | 6 | 1 | B |
| 13 | K6-cp2-01 HE | run | 249 | 273 | -3.6279 | -3.046 | 0.9935 | 72.7 | 6 (6) | 9 | 2 | B |
| 14 | K6-cp2-01 LE | run | 232 | 266 | -4.2907 | -1.707 | 0.9991 | 64.5 | 10 (10) | 43 | 24 | B |
| 15 | K6-cp3-01 ZC | run | 135 | 276 | -0.6851 | -1.123 | 0.9996 | 280.3 | 2 (2) | 1 | 0 | B |
| 16 | K6-cp3-01 ZW | run | 131 | 283 | -0.0791 | -0.084 | 0.9948 | 277.3 | 1 (1) | 3 | 0 | B |
| 17 | K6-cp3-01 ZS | run | 136 | 285 | -0.5618 | -0.475 | 0.9998 | 277.0 | 3 (3) | 1 | 0 | B |
| 18 | K6-cp3-01 ZM | run | 119 | 278 | +0.4725 | 0.495 | 0.9973 | 279.2 | 1 (1) | 2 | 0 | B |
| 19 | K6-cp3-01 ZL | run | 143 | 287 | -1.9353 | -0.723 | 0.9973 | 269.5 | 4 (4) | 6 | 1 | B |
| 20 | K6-cp3-01 HE | run | 115 | 273 | -2.4697 | -1.590 | 0.9934 | 245.3 | 5 (5) | 10 | 0 | B |
| 21 | K6-cp3-01 LE | run | 112 | 266 | +1.5336 | 0.568 | 0.9991 | 193.1 | 4 (4) | 42 | 7 | B |
| 22 | K6-crushgap-01 ZS | run | 137 | 264 | -3.4807 | -2.708 | 0.9998 | 271.8 | 7 (7) | 1 | 0 | B |
| 23 | K6-limitcont-01 HE | run | 1 | 273 | +0.1869 | 1.002 | 0.9934 | 99.0 | 0 (0) | 1 | 0 | A |
| 24 | K6-limitcont-01 LE | run | 0 | 266 | +0.0000 | undefined | 0.9991 | - | 0 (0) | 0 | 0 | B |
| 25 | K6-wasdepre-01 ZC | run | 12 | 276 | -0.4729 | -1.315 | 0.9998 | 45.0 | 0 (0) | 0 | 0 | B |
| 26 | K6-wasdepre-01 ZS | run | 13 | 285 | -0.7410 | -1.288 | 0.9999 | 44.5 | 1 (1) | 0 | 0 | B |
| 27 | K6-wasdepost-01 ZC | run | 13 | 276 | -0.1777 | -0.748 | 0.9992 | 114.0 | 0 (0) | 1 | 0 | B |

**Labels** (the runner wrote none; the lead's, from the specs and rulings):
- K6-cp2-01, all seven: "tick history not source-verified for the research window" (K6-L-16 item 13(a); the research bars
  are on the frozen tick grid, 0 off-tick prices in E.2a).
- K6-limitcont-01 HE and LE: "limits are the frozen initial limits; expanded limits not encoded (K6-L-07)"; "settlements by
  the D9.7 proxy (one bar's close); official settlements not tested" (R-T3-2). LE also: "limit table partly contradicted by
  CME in the window (14 dates dropped)" (R-1b-2).
- K6-limitcont-01 HE: "Tier A on a single trip" (t = sqrt(n/(n-1)) for any one positive day; section 6).
- Every K6 member: source-overlap (confirmation only). No member carries "calendar partly unverified".

**The Tier A trial.** K6-limitcont-01 HE traded once: trade date 2025-04-07, sold at the 08:45 open after a limit-down
close on 2025-04-04 as the D9.7 proxy shows it, closed at 10:24 CT by the engine's D9.7 forced exit, gross +53 ticks
($530), net $510.34 (51.03 ticks), hold 99 minutes. Mean 51.034 / 273 = +0.1869 ticks a day; t = 1.0018. The direction and
the limit close cannot be checked without prices (section 5). It is the only K6 trial in Tier A; the tier stands as the
frozen screen wrote it.

**Other results of note.**
- The LE trials meet D9.7 often (cp1 LE 59 entry refusals and 14 forced exits; cp2 LE 43 exits; cp3 LE 42 exits): LE's
  initial limit is about 3% of price, so Topstep's 2-point buffer leaves a band of about 1.2% around the prior settlement.
  On 2026-06-01..06-18 the frozen table's $0.0725 narrows it further (R-1b-2: CME's limit was $0.0850).
- The WASDE members traded 12 (wasdepre ZC), 13 (wasdepre ZS) and 13 (wasdepost ZC) of the 14 WASDE dates; the untraded
  dates (ZC 2025-12-09, ZS 2026-03-10) are not explained by the counters (zero drift is the likely cause; not checkable
  without prices).
- Fresh-state starts (audit N-9): limitcont cannot trade the window's first three livestock dates, crushgap its first grain
  date, CP3 until a complete daily bar exists.
- At one ZS contract the D9.7 lower stop lies about 216 ticks ($2,700) from the prior settlement, beyond the $2,000 MLL
  (coder A, audit N-8): on a large down move the MLL liquidates before D9.7 can fire.

**MLL liquidations per trial:** cp1 ZC 2, ZW 1, ZS 4, ZM 1, ZL 1, HE 2, LE 2; cp2 ZC 2, ZW 3, ZS 5, ZM 5, ZL 3, HE 6, LE 10;
cp3 ZC 2, ZW 1, ZS 3, ZM 1, ZL 4, HE 5, LE 4; crushgap 7; limitcont HE 0, LE 0; wasdepre ZC 0, ZS 1; wasdepost 0. No tier
depends on them (the auditor's bound: removing every MLL-closed trip turns no Tier B trial into a pass).

**Tiers.** Tier A: K6-limitcont-01 HE. Tier B: the other 26. Excluded: none. Refused: none. Not traded: K6-limitcont-01 LE
(0 trips; screened, Tier B, t undefined).

**Program N.** 167 before this stage (reports/E.7_RETURN.md) + 27 K6 trials screened (status "run" with a screen, K6-L-17)
= **194**, counted as E.4 counted.

**What K6's confirmation would need.** Step 2 history of ZC, ZW, ZS, ZM, ZL, HE and LE: quoted $26.52 on 2026-09-26
(reports/stage_e2b_step2_quotes.md table b2: ZC $4.67, ZW $4.53, ZS $5.11, ZM $4.39, ZL $4.88, HE $1.47, LE $1.48). acct-2
holds $0.326239 of its $125.00 cap, so a top-up of about $26.19 at the quote, $28.85 at quote + 10% (D13's session-cap
rule), with ACCOUNT_2_CAP_USD raised to at least $151.19 ($153.85). A fresh quote first. Also owed before a confirmation:
the frozen start rule (S_X) for the seven roots (power is not_run), the tick and unit history over the confirmation window
(C7), and a ruling on the limit-table periods 1b found wrong (section 7). V14(c) applies to DSR (Tier A has one member).

## 4. Delegation record

| Agent (description) | Worker file | Model | Effort | Objective | Time (PDT) | Status and deviations |
|---|---|---|---|---|---|---|
| ReleaseChecker-OpusMed | worker-medium | opus | medium | Task 1b: WASDE dates, HE/LE limits, EC-CAL dates, other inputs | 00:06-00:17 | done; 14 WASDE keep; 1 limit period drop |
| MemberCoder-A-OpusXHigh | worker-xhigh | opus | xhigh | Task 2: the three ports on seven roots and crushgap, tests, mutants | 00:19-01:28 | done; raised the late-open 08:31 case (R-T3-1) and the ZS stop vs MLL fact |
| MemberCoder-B-OpusXHigh | worker-xhigh | opus | xhigh | Task 2: limitcont, wasdepre, wasdepost, the tables, tests, mutants | 00:19-00:53 | done; the harness refused its report write, saved by the lead |
| MemberAuditor-K6-FableXHigh | worker-xhigh | fable | xhigh | Task 3: fidelity audit | 01:28-01:56 | done; incident: its first repo copy included data/ (5.7 GB) in the RAM-backed /tmp, filling the quota; the lead deleted that copy at 01:38 and told it to exclude data/ |
| MemberAuditor-K6-FableXHigh (resumed by SendMessage) | worker-xhigh | fable | xhigh | Task 6: recomputation | 02:13-02:26 | done; no discrepancy |

At most three workers ran at once. No worker spawned another. Fable was available throughout.

## 5. Verification

**Part 1 (Task 3), each finding and its ruling** (reports/stage_e8_member_rulings.md):

| Finding | Grade | Ruling and fix |
|---|---|---|
| N-1 CP1 grain late-open date with a missing 08:30 bar takes 08:31 | NOTE | R-T3-1: code stands (K6-L-01's clause); specs wording amended |
| N-2 limitcont's event is the proxy's, not the official settlement's | NOTE | R-T3-2: label added to both trials |
| N-3 cp2.py F_REGULAR_CT literal (coverage windows only) | NOTE | no action |
| N-4 surviving auditor mutant B-LC-16 | NOTE | no action (equivalent) |
| N-5 the coders' ten surviving mutants | NOTE | no action (each equivalent) |
| N-6 tests that pin only a literal | NOTE | no action (16 of 17 killed by a trade; the other a declaration) |
| N-7 "a contract without a limit" moot only while the roll avoids the last two trading days | NOTE | R-T3-3: specs amended |
| N-8 ZS's lower D9.7 stop beyond the MLL | NOTE | recorded (section 3) |
| N-9 fresh-state starts | NOTE | recorded (section 3) |
| N-10 unreachable ValueError paths | NOTE | no action |
| N-11 the auditor's tmpfs incident | NOTE | recorded (section 4) |

The readings the auditor was asked to rule on: K6-L-01 stands (wording per R-T3-1); K6-L-06, the proxy is the frozen input
(not unimplementable; label per R-T3-2); K6-L-07, K6-L-08, K6-L-03 and R-1b-2 agreed (SER-9736 quote checked against the
saved page).

**Part 2 (Task 6):** item 0 frozen files VERIFIED (14 files equal the freeze and Part 1's hashes); item 1 the screen
recomputed VERIFIED (27 of 27 to 1e-9); item 2 tiers VERIFIED WITH NOTES (26 B, 1 A per D5 and OC-H; nothing in D5 or OC-H
excludes a one-trip series); item 3 cost rebuild from trip lists VERIFIED (cp2 ZC 247/247 and limitcont HE 1/1 trip nets
exact, event-window and D9.7 costs included; gross not checkable without prices; record sha256s match); item 4 trade counts
VERIFIED WITH NOTES (WASDE members as in section 3; limitcont's event condition not checkable without prices; crushgap and
the ports per rule; 106 CP2 holds of 76-88 minutes are present-bar counts over missing minutes, 3 confirmed deferrals);
item 5 N VERIFIED (194); item 6 MLL VERIFIED WITH NOTES (counter = MLL-closed trips; accounts_started - 1 over-counts cp1 ZW
and ZM by one; no tier depends on them). No DISCREPANCY, so no tier is "unverified".

## 6. Open choices (each decided by the lead alone, with the reason; each can be overturned)

1. **K6-L-01 grain CP1's first bar** = the earliest bar of d at or after 19:00 CT on the calendar day before d (a missing
   19:00 bar takes the next; on the late-open dates 2025-11-28, 2025-12-26, 2026-01-02 the 08:30 bar, or the next if it is
   missing, R-T3-1). Reason: K6's C3 says "the first bar at or after that 19:00 CT open" and D6 says "the trade date's first
   bar"; E.3-L-05's exact-bar reading followed K2's different text. Flagged for the user.
2. **K6-L-02 livestock CP1's first bar** is the 08:30 bar exactly (the entry names it; R-03).
3. **K6-L-03 crushgap's GPM** in exact integer units from the frozen vendor_price_factor; comparisons non-strict.
4. **K6-L-04/L-05 crushgap's d-1** is the EC-CAL grain trade date before d, and its guard is per leg.
5. **K6-L-06 limitcont's settlements are the D9.7 proxy** (the 12:59 bar's close, or the fallback), computed as the engine
   computes it. Reason: the 01:52 E.0 ruling on catalog section 7 item 2 ("Databento statistics schema ... or
   settlement-window VWAP proxy") and D9.7 line 542; the statistics schema was never bought. The proxy can miss or add a
   limit close when it differs from the official settlement by a tick (label, R-T3-2). Flagged for the user.
6. **K6-L-07 limitcont reads the frozen initial limit and skips a d whose d-2 was a limit close** (no expanded-limit table is
   frozen; an expansion triggered by another month or by Feeder Cattle is invisible). Reason: the narrowest reading that
   adds no input; it only removes dates. Flagged for the user.
7. **K6-L-08 exact equality, no rounding** (the engine does not round the proxy); **K6-L-09 c and its guard** (every bar
   read carries d's 08:30 contract; the window's first three livestock dates cannot trade).
8. **K6-L-10 C4's early-close test by table** for the four new members (K1-L-10, K3-L-11).
9. **K6-L-11 EC-WASDE = the frozen calendar's 12:00 ET WASDE rows after C9a's drop rule**; a WASDE missing from the
   calendar would not be added (none was).
10. **K6-L-16 catalog section 7 settled**: item 12 read as ordinary market orders (the 08:31 entries after the reopen);
    item 13(a) the CP2 tick-history label (K1-L-14 10(c) precedent).
11. **K6-L-17 the N rule** (pre-declared): a trial counts when the runner writes its screen; N = 194.
12. **R-1b-2: drop the 14 LE limit dates for the member** rather than use CME's $0.0850 (an input outside the frozen
    EC-LIM) or keep $0.0725 (a value CME contradicts). Effect: limitcont LE cannot trade a d whose d-1 or d-2 is in
    2026-06-01..06-18. The harness's own D9.7 keeps $0.0725 on those dates (stricter; no harness change in this stage).
13. **R-1b-1: keep the moved 2025-11-14 WASDE** on the NASS notice of 2025-10-31 (C9a's drop rule).
14. **The one-trip Tier A stands** as the frozen screen wrote it (D5 and OC-H have no minimum-trade rule; the auditor
    confirmed). Reason: the lead does not re-tier or re-run. Flagged for the user and the next session (section 7).
15. **R-T3-1..R-T3-3**: specs wording and one label; no code change after the audit.
16. **Coder B's four implementation choices accepted** (not-full list with reasons; an explicit empty HE entry in
    DROPPED_LIMIT_DATES; is_wasde_date reads the drop table at call time; a bar's open read through asdict, since the static
    check bans the name `open`, precedent R-T2-1). Coder A's 08:31 case accepted (R-T3-1).
17. **The two trials rebuilt in Task 6**: K6-cp2-01 ZC (event windows, deferrals, flattens) and K6-limitcont-01 HE (the Tier
    A trial).
18. **MLL counts from the engine's liquidation counter**, not accounts_started - 1 (the auditor's item 6).
19. **Coder B started with Task 1b's rulings already in the spec** (1b finished first); no follow-up was needed.
20. **The test suites ran without PYTHONPYCACHEPREFIX** (E.6 and E.7 precedent; three bytecode tests fail under a prefix);
    every Stage E command (preflight, freeze, runner) ran with a fresh prefix.
21. **The auditor's scratch copy of data/ removed by the lead** (a copy in RAM-backed /tmp, verified before removal; the
    real data/ untouched), with the auditor told to exclude data/, .venv and .git.
22. **The commit holds exactly the prompt's list.** tests/test_k6_members_tables.py compares the tables with the generator
    reports/stage_e8_briefs/gen_k6_tables.py, which is not in the commit (E.7 had the same dependence; its briefs were
    committed later with the stage records). At commit 0a14a9a alone that one test needs the briefs folder.
23. **Cost method**: each message's LAST usage record (E.7's method).

## 7. What the next session must do first

- **The push the planning chat owes:** 0a14a9a (K6 member freeze) is on main, not pushed. The session made exactly that one
  commit. Uncommitted by design: reports/E.8_RETURN.md, reports/stage_e8_STATE.md, reports/stage_e8_briefs/ (including
  the table generator the table test reads), reports/stage_e8_coder_A.md, _coder_B.md, reports/stage_e8_k6_screen/, the
  audit's Part 2 (reports/stage_e8_member_audit.md modified), and the progress.md and docs/STAGES.md lines.
- **Frozen hashes in force:** harness v6 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87; E.1 manifest
  96166eb3...; E.2a ML 077a57e1...; cluster freezes K2 8815a775..., K4 7abcde17..., K5 1d0c974f..., K3 c4fb5da4..., K7
  46cae308..., K1 cf48f514..., **K6 a6f8b497eee727688f3d0e9a3fc7af3abfe41c02f0354a55f5d918c01e61c604** (27 members).
- **Funding for a K6 confirmation:** step 2 for ZC, ZW, ZS, ZM, ZL, HE, LE quoted $26.52 (2026-09-26); acct-2 has $0.326239;
  top-up about $26.19 at the quote, $28.85 with 10%; ACCOUNT_2_CAP_USD must rise to at least $151.19 ($153.85). A fresh
  quote first.
- **Questions for the user:**
  1. K6-limitcont-01 HE is Tier A on one trade (t = 1.002 is arithmetic, not evidence). Run K6's confirmation with it as
     the Tier A member, or treat the screen's pass on a single trip as uninformative? Either way, D4's power check will
     probably call it inconclusive by design (C11).
  2. K6-L-06 and K6-L-07: limitcont runs on the D9.7 settlement proxy and the initial limit. Accept for confirmation, or buy
     the statistics schema (official settlements) and an expanded-limit table first?
  3. The frozen harness limit table differs from CME's notices on LE 2026-06-01..06-18 (research window, $0.0725 vs
     $0.0850), and, between the confirmation window and the research window, on HE 2024-09-04..09-12 and LE
     2024-10-09..10-24 (Task 1b B2). A harness fix (a new manifest version) or a recorded acceptance before any K6
     confirmation?
  4. K6-L-01 (grain CP1's first bar under K6's "first bar at or after" text).
  5. The ZS stop beyond the MLL at one contract (a sizing fact for deployment, not a screen issue).
  6. The tick and unit history (C7) over the confirmation window, owed before any K6 confirmation bar is read.
- **Next stage:** K8 alone, per V17 (then the ML route).

## 8. Session cost

**Wall clock** 2026-09-30 23:57 to 2026-10-01 02:31 PDT (2 h 34 min), all of it work: no pause, no usage-limit wait, no
crash. First estimate 4 h 25 min (to about 04:25; the prompt expected about 2 h), revised at 00:25 to about 03:50 as Task 1
and Task 1b came in early; the audit (28 min) and the run (3 min) came in shorter still. The five full suites (12 minutes
each) overlap worker time except the Task 4 suite. The gate suite's first run (01:28-01:37) died when the auditor's scratch
copy of data/ filled the RAM-backed /tmp; it is a work row with a deviation, not a pause.

**Final ETA table** (PDT; tokens from the transcripts; no pause rows, since none occurred):

| Task | Owner | Model | Effort | Start | End | Time | Tokens | Status and deviations |
|---|---|---|---|---|---|---|---|---|
| 0 Startup checks (start suite to 00:09) | lead | opus | xhigh | 23:57 | 00:09 | 12 min | in lead | done; suite = E.7's end |
| 1 Member specs (section 10 at 00:18) | lead | opus | xhigh | 23:58 | 00:19 | 21 min | in lead | done |
| 1b Event and limit checks | ReleaseChecker-OpusMed | opus | medium | 00:06 | 00:17 | 11 min | 8,725,689 | done; 1 limit period dropped (R-1b-2) |
| 2A Ports and crushgap | MemberCoder-A-OpusXHigh | opus | xhigh | 00:19 | 01:28 | 69 min | 22,366,723 | done |
| 2B limitcont, WASDE members, tables | MemberCoder-B-OpusXHigh | opus | xhigh | 00:19 | 00:53 | 34 min | 20,920,813 | done; its .md write refused, saved by the lead |
| 2g Gate suite, first run | lead | - | - | 01:28 | 01:37 | 9 min | in lead | failed: /tmp full (the auditor's data/ copy) |
| 2g Gate suite, re-run | lead | - | - | 01:38 | 01:50 | 12 min | in lead | 5373 passed |
| 3 Fidelity audit | MemberAuditor-K6-FableXHigh | fable | xhigh | 01:28 | 01:56 | 28 min | 14,803,740 (Parts 1 and 2) | 0 blocking, 0 should-fix, 11 notes; tmpfs incident |
| 4 Rulings, freeze, suite, commit 0a14a9a | lead | opus | xhigh | 01:56 | 02:10 | 14 min | in lead | done; no code change |
| 5 Screening run | lead | opus | xhigh | 02:10 | 02:13 | 3 min | in lead | 27 run, 0 refused |
| 6 Recomputation | MemberAuditor-K6-FableXHigh (resumed) | fable | xhigh | 02:13 | 02:26 | 13 min | above | no discrepancy |
| 7 Result, return, end suite (02:15-02:27), end checks, cost, progress | lead | opus | xhigh | 02:13 | 02:31 | 18 min | in lead | done |
| **Stage** | | | | 23:57 | 02:31 | **2 h 34 min wall and work** | **129,692,592** (lead 62,875,627, 48.5%; workers 66,816,965, 51.5%) | first estimate 4 h 25 min; the prompt expected about 2 h |

**Tokens per model** (the lead transcript 94d6572b's .jsonl plus every worker transcript under its subagents/ folder; each
assistant message counted once by message id, from its LAST usage record; reports/stage_e8_briefs/cost.py, cost.out; the
lead's last messages after the count, about 02:30-02:35, are not included):

| Model | Input | Output | Cache read | Cache creation | Total |
|---|---|---|---|---|---|
| claude-fable-5-1 | 1,100 | 177,175 | 13,651,766 | 973,699 | 14,803,740 |
| claude-opus-5-5 | 884 | 631,921 | 111,543,180 | 2,712,867 | 114,888,852 |
| all | 1,984 | 809,096 | 125,194,946 | 3,686,566 | 129,692,592 |

Per worker spawn: ReleaseChecker-OpusMed (worker-medium, opus, medium) 8,725,689; MemberCoder-A-OpusXHigh (worker-xhigh,
opus, xhigh) 22,366,723; MemberCoder-B-OpusXHigh (worker-xhigh, opus, xhigh) 20,920,813; MemberAuditor-K6-FableXHigh
(worker-xhigh, fable, xhigh, Parts 1 and 2) 14,803,740. Lead (opus, xhigh) 62,875,627.

Delegation share: lead 48.5%, workers 51.5%; by model opus 88.6%, fable 11.4%. Cache reads are 96.5% of all tokens. These
are token counts, not plan-credit percentages; the /usage meter is the user's to record.
