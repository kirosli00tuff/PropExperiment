# Stage E.14 return: C1 frozen and ready, awaiting funds; C2 stopped at its power rule; nothing bought

Lead Opus 5.5 xhigh, 2026-10-05 00:26 to 03:56 PDT, session 19c73927. Prompt docs/prompts/STAGE_E.14.md
(revision V26). STATE: reports/stage_e14_STATE.md. Times are PDT unless marked UTC.

## 1. Verdict summary

**C2 (dealer-gamma-conditioned late-session momentum): STOPPED** at its minimum-power rule (draft section 7),
before its freeze, registration and purchase. Only 135 eligible 2011-05-03..2019-04-30 dates had GEX < 0
(lag 1, share 6.8%), against the floor of 200. No calendar can lift it above 146. Two implementations agree, and
Fable recomputed it independently. The draft expected about 48% negative days, the paper's share for its own
NGE measure; SqueezeMetrics' GEX is negative far less often. No T1 or T2 statistic exists, no ES bar was read,
and nothing is learned about the effect. Per section 7, the user decides C2's next step.

**C1 (backward NG replication): FROZEN, AWAITING FUNDS.**
- The calendar probe passed: 0 of 258 energy dates and 0 of 52 NGS dates unsourced in 2012.
- Six 2010-2019 CME group calendars have 0 unsourced dates. The release calendar has 1 unsourced time.
- Freeze reports/stage_e14_prereg_C1.md: sha256 afc5c10f..., commit 1680982.
- The q reproduction is exact: E.12's NG h60 row (518 trades, t_B 2.5143) and hF row (494 trades, t_B 2.3299)
  rebuild with differences of 0.0.
- q_h60 = 0.033735277284776724 and q_hF = 0.0831931045522869.
- M1 payload sha256s: 9c2d9986... (h60) and 153c2bdc... (hF). Fable reran both bit-identically.

**Money:** bought nothing; spent $0.00 (738 quote lines at $0.00). Funds: acct-1 $1.61, acct-2 $18.07. C1's
fresh quote is $57.742330 (x 1.03 = $59.474600). The top-up it needs is $41.404330: ACCOUNT_2_CAP_USD to $291.08
or more.

**Hashes:** harness v10 fde3a49c... (commit dc93e9b); C1 freeze afc5c10f... (commit 1680982); C1's input list
3356d676.... **N stays 471**: nothing was registered.

## 2. Guardrail evidence

### Start (00:26 PDT), quoted verbatim (reports/stage_e14_briefs/start_checks.txt; script checks.sh)

```
$ date
Mon Oct  5 12:26:37 AM PDT 2026
$ git status --short
[364 lines '?? reports/stage_e12_briefs/margin_pages/' and '?? reports/stage_e13_briefs/pages/...' (the E.12/E.13 DO_NOT_COMMIT page folders) collapsed here; full text in reports/stage_e14_briefs/start_checks.txt]
?? reports/stage_e14_briefs/
$ git log --oneline -3
77be2a9 docs: Stage E.14 prompt revised for funds on hand (V26)
8ca7a21 docs: Stage E.14 prompt (C1 and C2 tests) and V25
ee8db45 Stage E.13 research and scoping
$ uv run python -m data.holdout status (keys)
top all_ok True unlocks_logged 0 unlock_log_ok True
holdout_2 all_ok True unlocks_logged 0 unlock_log_ok True
MCL all_ok True unlocks_logged 0 unlock_log_ok True
MGC all_ok True unlocks_logged 0 unlock_log_ok True
MHG all_ok True unlocks_logged 0 unlock_log_ok True
NG all_ok True unlocks_logged 0 unlock_log_ok True
$ wc -c REGISTRATION.md
0 REGISTRATION.md
$ python3 reports/stage_e2b_briefs/check_frozen.py
reports/stage_e1_freeze.json: manifest sha256 96166eb39b85d4fdcf132092978ee85393392de52c3857dc3f64ea7281454a7c files 32/32 match
reports/stage_e2a_ml_freeze.json: manifest sha256 077a57e1c00554dd0745302b247673d45ee05b805ac4bfd876f8497f7bbb1ed2 files 4/4 match
ALL_OK
$ PYTHONPYCACHEPREFIX=<fresh> uv run python -m screening.harness_freeze verify --expected 7fd757f6d7c3990c2d20756c501f68b0541aa89851dcca9236badabd4f4a9bd9
preflight OK: 7fd757f6d7c3990c2d20756c501f68b0541aa89851dcca9236badabd4f4a9bd9
$ cluster freezes (load_cluster_freeze + verify_cluster_code)
K1 cluster freeze OK cf48f514dcf26490fa79a4322f764af991ee2555f2147354f12a31621fbe7ce2 11 members
K2 cluster freeze OK 8815a775e74996419b57751b1104ffa07cd4b3450eb18a9a92c6cbbd5615b7c5 44 members
K3 cluster freeze OK c4fb5da41d69a6be54ea07d1ab35bd2b238d1fbeafaeb3008b886f8fc6888d95 30 members
K4 cluster freeze OK 7abcde1705440e97efcf1ce255d979213eed9840f03a8383f2784a74f5f1534a 12 members
K5 cluster freeze OK 1d0c974f18e884e1ad073d8f6f94d7bb70ee6f43971c7f23ccacab54103b3655 11 members
K6 cluster freeze OK a6f8b497eee727688f3d0e9a3fc7af3abfe41c02f0354a55f5d918c01e61c604 27 members
K7 cluster freeze OK 46cae3082ae17cfd2a0e731cba27f6cc5dd2bdb94bb757d7ae48c684a5449462 6 members
K8 cluster freeze OK 99f5a6ce4f91fd63ae4a7dc91b5eb39ecbf8a7eac6f210b3472bf49eaf8463b7 4 members
$ ledger
27018 ledger/databento_spend.jsonl
6a074c143670e241b0a383b2778661bbc60e39ec96c501000a4413176efeda4c
$ ledger total per account (SpendGate.account_spent_usd: external ledgers plus this repo's lines)
acct-1: spent 118.390020 cap 120.00 headroom 1.609980
acct-2: spent 231.599730 cap 249.67 headroom 18.070270
$ v2 freeze manifest (ml_route_v2.phase1.freeze.verify_v2_freeze)
v2 freeze OK: 91 files
```
Start suite (without PYTHONPYCACHEPREFIX): `6505 passed, 2 skipped, 3 xfailed, 54 warnings in 1005.53s (0:16:45)` (00:26-00:43).

### After the purchase point (03:07 PDT; nothing was bought), quoted verbatim

```
top all_ok True unlocks_logged 0 unlock_log_ok True
holdout_2 all_ok True unlocks_logged 0 unlock_log_ok True
MCL all_ok True unlocks_logged 0 unlock_log_ok True
MGC all_ok True unlocks_logged 0 unlock_log_ok True
MHG all_ok True unlocks_logged 0 unlock_log_ok True
NG all_ok True unlocks_logged 0 unlock_log_ok True
```
Ledger then: 27,756 lines, sha256 0312fbc0b1ca2da652ca7caaab2313ccbbc6920ae3a19d9651ff2e94cd1c48fb; acct-1 spent
118.390020 (headroom 1.609980), acct-2 spent 231.599730 (headroom 18.070270), as at the start.

### End (03:39 PDT), quoted verbatim (reports/stage_e14_briefs/end_checks.txt)

Run just before this return was written. The untracked files are this stage's outputs, which the final commit adds,
except the git-ignored GEX CSV and its copies and the coder worktrees.

```
$ date
Mon Oct  5 03:39:37 AM PDT 2026
$ git status --short
 M ledger/databento_spend.jsonl
?? .claude/worktrees/
[364 lines '?? reports/stage_e12_briefs/margin_pages/' and '?? reports/stage_e13_briefs/pages/...' (the E.12/E.13 DO_NOT_COMMIT page folders) collapsed here; full text in reports/stage_e14_briefs/end_checks.txt]
?? reports/stage_e14_STATE.md
?? reports/stage_e14_briefs/
?? reports/stage_e14_c1_model.json
?? reports/stage_e14_c1_model.md
?? reports/stage_e14_c2_result.json
?? reports/stage_e14_c2_result.md
?? reports/stage_e14_gex.md
?? reports/stage_e14_purchase.md
?? reports/stage_e14_quotes_es2011.json
?? reports/stage_e14_quotes_es2011.md
?? reports/stage_e14_quotes_ext2010.md
?? reports/stage_e14_review.md
?? reports/stage_e14_rulings.md
$ git log --oneline -3
1680982 E.14 freezes, C1 and C2: C1 frozen; C2 stopped before its freeze
dc93e9b harness v10, E.14 caps and stores
77be2a9 docs: Stage E.14 prompt revised for funds on hand (V26)
$ uv run python -m data.holdout status (keys)
top all_ok True unlocks_logged 0 unlock_log_ok True
holdout_2 all_ok True unlocks_logged 0 unlock_log_ok True
MCL all_ok True unlocks_logged 0 unlock_log_ok True
MGC all_ok True unlocks_logged 0 unlock_log_ok True
MHG all_ok True unlocks_logged 0 unlock_log_ok True
NG all_ok True unlocks_logged 0 unlock_log_ok True
$ wc -c REGISTRATION.md
0 REGISTRATION.md
$ python3 reports/stage_e2b_briefs/check_frozen.py
reports/stage_e1_freeze.json: manifest sha256 96166eb39b85d4fdcf132092978ee85393392de52c3857dc3f64ea7281454a7c files 32/32 match
reports/stage_e2a_ml_freeze.json: manifest sha256 077a57e1c00554dd0745302b247673d45ee05b805ac4bfd876f8497f7bbb1ed2 files 4/4 match
ALL_OK
$ PYTHONPYCACHEPREFIX=<fresh> uv run python -m screening.harness_freeze verify --expected fde3a49c8e15f08b36108e9a32d062f08f342fe2414607d33a7b8981ef00e34b
preflight OK: fde3a49c8e15f08b36108e9a32d062f08f342fe2414607d33a7b8981ef00e34b
$ cluster freezes (load_cluster_freeze + verify_cluster_code)
K1 cluster freeze OK cf48f514dcf26490fa79a4322f764af991ee2555f2147354f12a31621fbe7ce2 11 members
K2 cluster freeze OK 8815a775e74996419b57751b1104ffa07cd4b3450eb18a9a92c6cbbd5615b7c5 44 members
K3 cluster freeze OK c4fb5da41d69a6be54ea07d1ab35bd2b238d1fbeafaeb3008b886f8fc6888d95 30 members
K4 cluster freeze OK 7abcde1705440e97efcf1ce255d979213eed9840f03a8383f2784a74f5f1534a 12 members
K5 cluster freeze OK 1d0c974f18e884e1ad073d8f6f94d7bb70ee6f43971c7f23ccacab54103b3655 11 members
K6 cluster freeze OK a6f8b497eee727688f3d0e9a3fc7af3abfe41c02f0354a55f5d918c01e61c604 27 members
K7 cluster freeze OK 46cae3082ae17cfd2a0e731cba27f6cc5dd2bdb94bb757d7ae48c684a5449462 6 members
K8 cluster freeze OK 99f5a6ce4f91fd63ae4a7dc91b5eb39ecbf8a7eac6f210b3472bf49eaf8463b7 4 members
$ ledger
27756 ledger/databento_spend.jsonl
0312fbc0b1ca2da652ca7caaab2313ccbbc6920ae3a19d9651ff2e94cd1c48fb
$ ledger total per account (SpendGate.account_spent_usd: external ledgers plus this repo's lines)
acct-1: spent 118.390020 cap 120.00 headroom 1.609980
acct-2: spent 231.599730 cap 249.67 headroom 18.070270
$ v2 freeze manifest (ml_route_v2.phase1.freeze.verify_v2_freeze)
v2 freeze OK: 91 files
```
End suite (without PYTHONPYCACHEPREFIX): `6740 passed, 2 skipped, 3 xfailed, 54 warnings in 955.03s (0:15:55)`.

### Order of events per test (times PDT; git commit times from `git log --date=iso-local`)

| Test | Event | Time | Evidence |
|---|---|---|---|
| C2 | SqueezeMetrics terms read; CSV fetched once | 00:38:50 / 00:43:01 | pages/gex/fetch_log.txt; gex/fetch_record.txt |
| C2 | Fresh ES quote ($0.00 lines) | 01:29:26-01:32:41 | ledger lines from 08:29:29Z; quotes_es2011.json |
| C2 | GEX < 0 count 135 (first equity file); stop ruled; cap reset to 0.00 | 01:33 / 01:34 / 01:34:22 | gex_count_first.out; data/config.py mtime |
| C2 | Count rerun on the final equity calendar, two implementations: 135 | 02:28:59-02:29:00 | gex_count_final.out, gex_count_v10helper_final.out |
| C2 | No freeze, no registration, no purchase, no evaluation | n/a | ledger/trial_registrations.jsonl (baseline only); ledger (quotes only) |
| C1 | Probe written; ruled (rule does not fire) | 01:32:17 / 01:36 | stage_e14_probe.md |
| C1 | Calendars final (group files; releases) | 01:31:48-02:26:14; 03:05:37 | file mtimes; stage_e14_calendars.md |
| C1 | Fresh quote of the set ($0.00 lines) | 01:33-01:56 | quotes_ext2010.json |
| C1 | Fable freeze review | 03:06-03:26 | stage_e14_review.md |
| C1 | Harness v10 commit dc93e9b; freeze commit 1680982 | 03:29:15 / 03:29:42 | git log |
| C1 | M1 fit and q (before any 2010-2019 byte; none exists) | 03:29:54-03:29:57 | stage_e14_c1_model.json; STATE |
| C1 | Not registered, not bought, not evaluated (awaits funds) | n/a | trial registry; ledger |

Incident (Fable F-V6): the Task 8 verifier's first look at the CSV printed two rows' values (2011-05-02,
2011-05-03), after C2's stop; nothing was derived from them. No other guardrail event: no TopstepX call, no key
printed, no write to REGISTRATION.md, no edit under live/ or ops/, no MES store opened, no push.

## 3. Results per task

### Task 0: startup
HEAD 77be2a9, clean apart from the E.12/E.13 DO_NOT_COMMIT page folders. Holdouts all_ok with 0 unlocks.
Start suite: 6505 passed, 2 skipped, 3 xfailed (E.12's end state). ~/.cache/propexp_e12_phase1 present (51
files).

### Task 1: the calendar probe (reports/stage_e14_probe.md)
- 2012 energy: 258 trade dates, 0 unsourced, all graded "cme". The session was 17:00-16:15 CT; holiday halts
  12:15 CT; Sandy left energy on regular hours.
- 2012 NGS: 52 releases, 0 unsourced. One release (2012-12-28) rests on EIA's schedule alone.
- Rule ruled at 01:36: it does not fire under any reading the rule defines (open choice 15).

### Task 2: calendars (reports/stage_e14_calendars.md)

| Group | Trade dates | Closures / halts / late opens | Unsourced (2010-06-07..2019-04-30) |
|---|---|---|---|
| Equity | 2,325 | 24 / 78 / 6 | 0 of 2,298 (C2's window 0 of 2,064) |
| Rates | 2,324 | 25 / 97 / 6 | 0 of 2,297 |
| FX | 2,325 | 24 / 96 / 6 | 0 of 2,298 |
| Energy | 2,323 | 26 / 73 / 0 | 0 of 2,296 |
| Metals | 2,323 | 26 / 73 / 0 | 0 of 2,296 |
| Grains | 2,269 | 80 / 23 / 25 | 0 of 2,243 |

- Release calendar: NGS 470 (C13 drops 0), WPSR 470, FOMC 72. One WPSR time is unsourced (2012-11-01); its NG
  date is excluded.
- Energy full sessions: 2,250.
- Every 2% stop is clear.
- Accepted limit: CME's weekly Globex notices were not read one by one.

### Task 3: the GEX file (reports/stage_e14_gex.md)
- Terms read first; ruled that they do not forbid one download of the offered file.
- The CSV was fetched once at 07:43:01 UTC: sha256 51bef9ea..., kept uncommitted and git-ignored.
- Timing rule: lag 1. Evidence: the server's Last-Modified and same-evening captures (a Monday 08:19 CT capture
  holds Friday's row).
- The 2011-2019 rows are unchanged since 2020.
- Count 135 < 200: C2 stopped at 01:34.

### Task 4: harness v10 and the freezes
- **v10** (dc93e9b, manifest fde3a49c...; v9 was 7fd757f6...). 3 files changed, 19 added.
  - Contents: the E.14 caps (all 0.00, acct-2 cap unchanged at 249.67); the es2011 and ext2010 plans, stores and
    loader; the hist calendar loader with the six calendars; C2's inert code; the trial registry (baseline
    N = 471).
  - Full suite on the candidate: 6737 passed. Diff against v9: `git show --stat dc93e9b`.
- **C1's freeze** (1680982): the draft plus V25 item 1, V26, the E.14 facts and the FreezeReviewer's fixes (seven
  listed changes).
  - Code c1_replication/ (75 synthetic tests).
  - E.12's state hashed (51 files) with a read-only copy.
- **C2: not frozen** (stopped in Task 3).

### Task 5: M1 and q (reports/stage_e14_c1_model.md)
- Run 03:29:54-03:29:57, after the freeze commit; no 2010-2019 byte exists.
- Reproduction exact. q and M1 are as in section 1.
- 150 features, feature_cols sha256 af7d43d6...; the ML ledger unchanged.
- C1 is FROZEN, AWAITING FUNDS. The later session's exact steps and hashes are in that file's section 4.

### Task 6: quotes, registration and purchase (reports/stage_e14_purchase.md)
- Fresh quotes ($0.00 lines on acct-2): ES $10.109048 (96 of 96 chunks, would have fitted) and C1 $57.742330
  (642 of 642).
- No registration, no purchase. The holdout status at the post-purchase point (03:07) is all_ok, 0 unlocks.
- C1's top-up: $41.404330.

### Task 7: evaluations (reports/stage_e14_c2_result.md, .json)
- C2: STOPPED at the power rule.
- C1: not evaluated in this stage.

## 4. Delegation record

| Agent (description) | Agent file | Model | Effort | Start | End | Tokens | Status |
|---|---|---|---|---|---|---|---|
| CalendarProbe-OpusHigh | worker-high | opus | high | 00:34 | 03:06 | 63,037,188 | done: probe (Part A 01:32) and release calendars (Part B) |
| CalendarBuilder-Equity-OpusHigh | worker-high | opus | high | 00:34 | 02:28 | 54,066,402 | done: equity, rates, FX, grains |
| CalendarBuilder-Commod-OpusHigh | worker-high | opus | high | 00:36 | 01:33 | 27,839,578 | done: energy, metals, full sessions |
| V10Coder-OpusXHigh | worker-xhigh | opus | xhigh | 00:38 | 01:29 | 56,369,890 | done: harness v10 (worktree, e577d55) |
| C1Coder-OpusXHigh | worker-xhigh | opus | xhigh | 01:29 | 02:48 | 62,360,972 | done: c1_replication (1169b71) and one follow-up via SendMessage (5c4a1cd, 02:46-02:48) |
| FreezeReviewer-FableXHigh | worker-xhigh | fable | xhigh | 03:06 | 03:26 | 7,044,911 | done: APPROVE WITH FIXES (1 BLOCKING, 2 SHOULD FIX, 12 NOTE) |
| VerdictVerifier-FableXHigh | worker-xhigh | fable | xhigh | 03:30 | 03:39 | 3,488,335 | done: all MATCH (0 BLOCKING, 1 SHOULD FIX, 5 NOTE) |

## 5. Verification

Both Fable passes: reports/stage_e14_review.md. Rulings: reports/stage_e14_rulings.md.

- **Freeze review** (FreezeReviewer-FableXHigh, 03:06-03:26): APPROVE WITH FIXES (1 BLOCKING, 2 SHOULD FIX,
  12 NOTE).
  - F-01 BLOCKING: the later-harness clause ignored four tests that pin the caps. Fixed in the C1 freeze text and
    the README.
  - F-02: the C7 sentinel bar is now stated in the freeze text.
  - F-03: the CSV is git-ignored.
  - F-04/F-05: the later session's scripted input check and git-state check were added as text.
  - F-08: the Wayback CSV copies are recorded as a deviation.
  - F-10: times corrected to 01:34.
  - No code change was required. The fixes changed the manifest (a comment), the input list and the freeze sha;
    each was rebuilt in that order.
- **Verification** (VerdictVerifier-FableXHigh, 03:30-03:39): every verdict number MATCHES.
  - C2: 135, the bound 146, the stop. The strictest timing reading gives 131, which also stops.
  - C1: q, both M1 payloads and feature_cols bit-identical on an independent rerun.
  - The order of events in git, the ledgers and the files.
  - F-V1 SHOULD FIX: the terms ruling now states the curl and Wayback fetches. NOTEs F-V2 to F-V5 were recorded or
    applied.
  - F-V6 incident: the verifier's first `head` printed two GEX rows' values. That came after the stop; nothing was
    derived from them. It is disclosed for any future C2-like test.

## 6. Open choices (every decision the lead made on its own)

1. Calendar work started in parallel with the probe, not after it (the delegation table's "parallel, after 1"):
   the equity calendar is needed by C2 whatever the probe finds, and the C1-only groups (rates, FX, grains,
   energy, metals) and the release calendars were started at the same time so the night fits. If the probe
   drops C1, that work is wasted tokens only; no freeze, registration or N depends on it.
2. The probe worker builds the release calendars (NGS, WPSR, FOMC 2010-06..2019-05) after its probe, only if the
   probe's rule does not fire; the equity builder continues with rates, FX and grains from the same CME
   documents. Three calendar builders in total, as the prompt allows; the probe is its own worker.
3. GEX terms: SqueezeMetrics' terms bar "systematically retrieve data ... to create or compile ... a collection,
   compilation, database, or directory without written permission"; robots.txt is 404; the free DIX page offers
   the CSV through its own download button. Ruled: one download of the offered file for one registered test is
   not systematic retrieval; the terms do not forbid this use. The CSV and the Wayback copies stay uncommitted
   (DO_NOT_COMMIT.txt), hashed in the freeze, so the program does not redistribute it.
4. GEX timing: lag 1 (the latest row dated strictly before d). Sources, SqueezeMetrics' CSV page only: the
   server's Last-Modified (16:57 CT on the row's own date) and Wayback captures at 17:20-18:55 CT that already
   hold the same day's row (2020, 2025, 2026). Disclosed: 2011-2019 publication practice is not observable; the
   window's rows are unchanged since 2020-11-29 (hash comparison only, no value read).
5. Revision check: the window's GEX rows were compared across seven captures by sha256 of the rows, without
   reading or printing any value. Not a read of GEX values under the prompt's rule.
6. GEX count: computed on the calendar and GEX only, as Task 3 defines it; the roll blackout (needs bought
   symbology) is bounded as a disclosure (at most 96 dates), not used for the stop.
7. Hist stores (v10): bars inside a scheduled closure beyond the close minute are kept and flagged
   automatically (v9's keep-and-flag principle), fixed in code before any data exists, so no mid-stage hold.
8. Trial registry: a new append-only ledger, ledger/trial_registrations.jsonl (screening/trial_registry.py,
   baseline N = 471), because the only append-only trial ledger, ledger/ml_v2_config_ledger.jsonl, admits only
   ML v2 kinds through frozen code. The ES buy and the C2 run refuse without the registration (order of events
   enforced in code).
9. C2's cost: c = 0.976 + 0.5191 + 0.5428 = 2.0379 ticks (the table's printed values), bar 1.5c = 3.05685; the
   draft's "2.038" and "3.057" are its rounded display of the same sum.
10. C1's code lives in a new top-level package c1_replication/ (outside the harness directories and the v2
    freeze), hashed in C1's freeze, so neither harness v10 nor ml_route_v2/ changes for it.
11. The ES store holds trade dates 2011-05-02..2019-04-30: the first test date 2011-05-03 needs 2011-05-02's
    close. The test window itself is unchanged.
12. C1's E.12 state copy: ~/.cache/propexp_e14_c1/e12_state_copy (read-only), manifest
    reports/stage_e14_c1_e12_state_manifest.json (51 files, including gate0_run.json and gate0_DONE.json, which
    C17's list did not name; hashed too).
13. C2 stopped on its power rule at the Task 3 count (135 < 200; calendar-free bound 146), before its freeze
    and registration: not frozen, not registered, nothing bought. E14_SESSION_CAP_USD was set to 10.41 from the
    fresh ES quote (01:33) and reset to 0.00 (01:34) so v10 authorizes no spend. The es2011 plan, the ES store
    type and screening/stage_e14_c2.py stay in v10 as tested, inert code, in case the user decides to run C2
    under a new decision; nothing in v10 can buy ES while the cap is 0.00 and C2 is unregistered.
14. C1's registration N: with C2 unregistered, C1's later registration takes N from 471 to 473 (+2 on whatever N
    is then), not 473 -> 475 as the prompt anticipated when C2 was to register first.
15. The probe's NGS grade: an EIA release schedule (Wayback) is an "official" record of each release date, as
    calendar_rules.md defines; on that reading 0 of 52 2012 NGS dates are unsourced. On the stricter reading (an
    EIA record of each week's actual release) 1 is (2012-12-28), still within the rule's 2. Only a reading that
    requires each report's own "Released" line (27 weeks lack a capture) would fire, and the rule does not
    define the grade that way. Ruled: the rule does not fire; C1 continues.
16. Deviation (FreezeReviewer F-08): the GEX timing evidence and the revision check used seven Wayback captures of
    SqueezeMetrics' CSV; the prompt's source list names "SqueezeMetrics' public CSV page" and Wayback captures of
    official calendar pages, not Wayback captures of the CSV. Read-only, last-row dates and row hashes only; no
    verdict rests on them (C2 stopped on its count, which uses the fresh file alone).
17. Loader rulings in v10 before its commit (data/hist_calendar.py): a Friday-to-Monday session handover is
    contiguous in trade dates (the weekend is closed onto the earlier row); one day may hold one early halt and
    one late open (grains' day after Thanksgiving, as data/calendars/grains.py holds it). The builders' files
    were not edited.
18. C1 code rulings (C1Coder D-6, D-7, D-8): C7 as one sentinel bar per empty root dated 2019-05-31 (after the
    window); C12 excludes an NG date unsourced in any of the six groups or holding an unsourced release; Rule H-1
    literal (Sandy and 2018-12-05 get Topstep rows). Release rows with no instant are accepted only when listed
    as unsourced by id (WPSR 2012-11-01).
19. The E.14 session cap was set from a quote run before the v10 manifest, as E.12 did (the cap lives in frozen
    config); the quote is the prompt's "fresh quote-only run in this session". The C1 quote ran in the same window.
20. The lead wrote small code itself rather than spawn a worker for each (CLAUDE.md: small tasks inline): the GEX
    count script, the C1 freeze-input script, the two hist-calendar loader fixes with their tests, and the config
    comment. Each is covered by the Fable reviews; the loader fixes are in the v10 manifest.
21. C1Coder was resumed by SendMessage for one small follow-up (release rows with no instant), as CLAUDE.md allows
    for a small brief.
22. The FreezeReviewer reviewed C2's stop (terms, timing, count) instead of a C2 freeze, which does not exist.
    C2's freeze work file stays in reports/stage_e14_briefs/freeze_C2_work.md as a record only; it is not a freeze.
23. Commit messages: commit 2 reads "E.14 freezes, C1 and C2: C1 frozen; C2 stopped before its freeze" and the
    final commit "Stage E.14 C1 frozen, C2 stopped (not evaluated)" instead of the prompt's "... C2 evaluated",
    which would be false.
24. The return quotes the start and end checks verbatim except the 364 untracked E.12/E.13 DO_NOT_COMMIT page
    lines of `git status --short`, collapsed into one counted line; the full outputs are committed
    (reports/stage_e14_briefs/start_checks.txt, end_checks.txt).
25. The two coder worktrees (.claude/worktrees/agent-a94b80ceda0f5c25b, agent-a87e3dc1a4f58c0e5, branches with
    commits e577d55, 1169b71, 5c4a1cd) are left in place, uncommitted to main's history beyond the merged files;
    the user may delete them.
26. Times: the STATE file's task times were corrected from the transcripts where the lead's clock notes drifted
    (the C2 stop 01:34, not 01:42; the final GEX rerun 02:29; the freeze review 03:06-03:26).
27. The saved evidence pages (reports/stage_e14_briefs/pages/, 113 MB, about 1,800 third-party files) stay on disk,
    uncommitted, as in E.12 and E.13; the committed fetch logs, terms checks and calendar source tables hold every
    URL, fetch time and sha256 (pages/DO_NOT_COMMIT.txt).

## 7. Decisions for the user (the lead's recommendation first)

1. **C2's next step.** Recommendation: **close C2 as specified.**
   - Its rule cannot reach 200 trades on SqueezeMetrics' GEX.
   - Any rescue (a threshold other than zero, a GEX quantile, or the paper's own NGE construction) is a new
     hypothesis. It would need a new pre-registration counted in N.
   - The sign count, and now two rows' values, have been seen. A threshold chosen to reach 200 would be informed
     by the data.
   - The unconditional T2 alone was never a C2 pass, and the program's related price-only tests were null.
   - Alternative: a new pre-registration on a GEX quantile, decided before any price is read. The lead rates it
     low value.
2. **C1's top-up and completion session.**
   - Recommendation: if the user keeps searching, top up acct-2 by at least $41.41, plus a cushion for quote
     drift, say $45-50 (ACCOUNT_2_CAP_USD to $291.08 or more). Then run one completion session of about 1-1.5
     hours.
   - That session: verify the 43 inputs, the freeze and M1; raise the two caps (and the asserts that pin them);
     quote; register (N 471 -> 473); buy; build; evaluate once; Fable recomputes.
   - Everything else is built and frozen. The odds of a pass are about 12% (7-35%), and a pass is evidence, not a
     deployment verdict (freeze section 8).
   - If the user would rather not spend, C1 can wait frozen indefinitely; nothing in it expires. The E.12 state
     copy must be kept.
3. **Before the AiTrader readout (2026-10-23 at the earliest).** Recommendation: nothing else is required. The
   only open item is C1's completion session, which is independent of AiTrader. Absent the top-up, pausing until
   the readout costs nothing.

## 8. Session cost

Wall clock: 00:26 to 03:56 PDT, 3:30 of work; no pause and no usage-limit wait.

### Final ETA table (actuals; PDT; the initial estimate in brackets)

| # | Task / spawn | Owner | Model | Effort | Start | End | Time [estimate] | Tokens | Status and deviations |
|---|---|---|---|---|---|---|---|---|---|
| 0 | Startup, start checks, briefs | lead | opus | xhigh | 00:26 | 00:38 | 0:12 [0:32] | lead | done |
| 1 | Probe 2012 (Part A) | CalendarProbe-OpusHigh | opus | high | 00:34 | 01:32 | 0:58 [~1:00] | in row 1b | done; rule does not fire (ruled 01:36) |
| 1b | Release calendars NGS, WPSR, FOMC (Part B) | CalendarProbe-OpusHigh | opus | high | 01:32 | 03:06 | 1:34 [~2:00] | 63,037,188 (A+B) | done; 1 WPSR time unsourced |
| 2a | Equity, then rates, FX, grains | CalendarBuilder-Equity-OpusHigh | opus | high | 00:34 | 02:28 | 1:54 [~3:00] | 54,066,402 | done; 0 unsourced |
| 2b | Energy, metals, full sessions | CalendarBuilder-Commod-OpusHigh | opus | high | 00:36 | 01:33 | 0:57 [~2:30] | 27,839,578 | done; 0 unsourced |
| 3 | GEX terms, fetch, timing, count | lead | opus | xhigh | 00:38 | 01:50 | 1:12 [~0:40] | lead | done; C2 STOPPED 01:34 (deviation: C2 stops, Tasks 6-7 shrink) |
| 4a | Harness v10 code | V10Coder-OpusXHigh | opus | xhigh | 00:38 | 01:29 | 0:51 [~2:30] | 56,369,890 | done |
| 4a' | v10 merge, fresh quotes ES and C1, cap | lead | opus | xhigh | 01:29 | 01:56 | 0:27 [in 4c] | lead | done; quotes moved here from Task 6 (open choice 19) |
| 4b | C1 code | C1Coder-OpusXHigh | opus | xhigh | 01:29 | 02:48 | 1:19 [~2:00] | 62,360,972 | done; one 2-minute follow-up |
| 4c | Calendars into v10, loader fixes, manifest, full suite, freeze text | lead | opus | xhigh | 02:15 | 03:06 | 0:51 [~0:45] | lead | done; full suite 6737 passed |
| 4d | Freeze review | FreezeReviewer-FableXHigh | fable | xhigh | 03:06 | 03:26 | 0:20 [~1:00] | 7,044,911 | APPROVE WITH FIXES |
| 4e | Rulings, fixes, two commits | lead | opus | xhigh | 03:26 | 03:29 | 0:03 [~0:20] | lead | done; dc93e9b, 1680982 |
| 5 | M1 fit and q | lead | opus | xhigh | 03:29:54 | 03:29:57 | 0:00 [~0:20] | lead | done; exact |
| 6 | Quotes (in 4a'), no registration, no purchase; report | lead | opus | xhigh | 03:00 | 03:08 | 0:08 [~0:30] | lead | done; nothing bought |
| 7 | C2 result STOPPED; C1 not evaluated | lead | opus | xhigh | 03:08 | 03:27 | (parallel) [~0:30] | lead | done |
| 8 | Verification | VerdictVerifier-FableXHigh | fable | xhigh | 03:30 | 03:39 | 0:09 [~1:00] | 3,488,335 | all MATCH |
| 9 | Rulings, end checks, end suite, return, progress, commit | lead | opus | xhigh | 03:39 | 03:56 | 0:17  [~0:40] | lead | done; end suite 6740 passed |
| Total | Stage E.14 | lead + 7 spawns | | | 00:26 | 03:56 | 3:30 [estimate ~10:19, to ~10:45] | lead 103,133,858; workers 274,207,276; total 377,341,134 | no pause; no usage-limit wait |

### Tokens per model (this session's transcript and its 7 subagent transcripts, 07:20Z to 2026-10-05T11:30:00Z)

Computed with reports/stage_e10_briefs/cost.py (final usage per streamed message); raw output
reports/stage_e14_briefs/cost_raw.txt. Token counts, not plan-credit percentages.

| Model | Input | Output | Cache read | Cache creation | Total |
|---|---|---|---|---|---|
| claude-fable-5-1 | 1,924 | 138,039 | 9,893,214 | 500,069 | 10,533,246 |
| claude-opus-5-5 | 2,408 | 1,338,038 | 357,781,371 | 7,686,071 | 366,807,888 |
| all | 4,332 | 1,476,077 | 367,674,585 | 8,186,140 | 377,341,134 |

Per spawn: CalendarProbe-OpusHigh (worker-high, opus high) 63,037,188; CalendarBuilder-Equity-OpusHigh (worker-high, opus high) 54,066,402; CalendarBuilder-Commod-OpusHigh (worker-high, opus high) 27,839,578; V10Coder-OpusXHigh (worker-xhigh, opus xhigh) 56,369,890; C1Coder-OpusXHigh (worker-xhigh, opus xhigh) 62,360,972; FreezeReviewer-FableXHigh (worker-xhigh, fable xhigh) 7,044,911; VerdictVerifier-FableXHigh (worker-xhigh, fable xhigh) 3,488,335.

Delegation share: lead 103,133,858 (27.3%), workers 274,207,276 (72.7%). By model:
claude-fable-5-1 10,533,246 (2.8%), claude-opus-5-5 366,807,888 (97.2%).
