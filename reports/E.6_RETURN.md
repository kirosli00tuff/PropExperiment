# Stage E.6 return: K7 bitcoin coded, audited, frozen and screened on the research window (no purchase)

Lead: Opus 5.5, effort xhigh, 2026-09-27 PDT, one lead transcript (0f52aad4), 21:22 to 23:31, no pause. The prompt is
docs/prompts/STAGE_E.6.md (commit cdb155e, amended 3eb50c1).

## 1. Verdict summary

**Six K7 trials coded, Fable-audited (0 blocking, 1 should-fix fixed in the tests by R-T3-1, 8 notes), frozen (commit
d661eb6, cluster freeze 46cae3082ae17cfd2a0e731cba27f6cc5dd2bdb94bb757d7ae48c684a5449462) and run once.** All six are
Tier B and K7's Tier A is empty, so K7 adds nothing to D5's K and has no Holm family. The Fable recomputation found no discrepancy.

| Tier | Trials | Trips | Mean net ticks/contract/day | Daily t |
|---|---|---|---|---|
| A | none | - | - | - |
| B | all six (section 3) | 0-466 | -28.9198 to 0.0000 | -2.285 to -0.259 (expiry: t undefined, 0 trips) |

K7-expiry-01 was not traded: every research-window MBT expiry day lies in a roll blackout (E.2a L-11), as predicted
before the run (K7-L-05). No member unimplementable, refused or excluded. Event items: MBTX 2025-12-24 dropped (CME's
calendar gives 12-26; not replaced, R-1b-1), 10 of 14 research expiry dates unverifiable (kept), so K7-expiry-01 carries
"calendar partly unverified". **Program N = 150 + 6 = 156.** K7's confirmation (null side only) would need the step 2
purchase of MBT (quoted $3.11 on 2026-09-26, reports/stage_e2b_step2_quotes.md) and a top-up of about $2.79 ($3.10 with a
10% margin), since acct-2 holds $0.33.

## 2. Guardrail evidence

**Start checks, verbatim** (21:22; reports/stage_e6_briefs/start_checks.out; the suite reports/stage_e6_briefs/pytest_start.out):
```
$ date
Sun Sep 27 09:22:43 PM PDT 2026
$ git status --short
?? reports/stage_e6_briefs/
$ git log --oneline -3
3eb50c1 docs: split screening into E.6 (K7), E.7 (K6) and E.8 (K1), one cluster per session
4f9dfe0 docs: README, About this project section
5e5a737 docs: CLAUDE.md, Scrapling as the page-fetch fallback before Firecrawl
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
K7 no freeze: ClusterFreezeError
$ ledger
17400 ledger/databento_spend.jsonl
0b5466c4366ca9eaba7e10525545631c83e97c1184a7e745d5ed8ad47a9fe957
$ acct-2 position (pull_step2.account_position on the step 2 gate; reads the ledger only)
stage-E.5-2026-09-27 {'account': 'acct-2', 'account_cap_usd': 125.0, 'account_credit_usd': 125.0, 'spent_usd': 124.673761, 'cap_headroom_usd': 0.326239, 'credit_left_usd': 0.326239}
$ python -m data.pull_step2 --status (MBT)
roots in status: 45 ; states: ['not_bought', 'sealed']
MBT {"state": "not_bought"}
$ uv run pytest -q   (21:22:41-21:39:02)
4166 passed, 2 skipped, 1 xfailed, 54 warnings in 978.28s (0:16:18)
```
The start suite equals E.5's end result. Scripts ran with a fresh PYTHONPYCACHEPREFIX in the scratchpad (outside the
repository); the suites ran without it, as E.3 established. The runner's preflight accepted v6 (the harness verify line).

**End checks, verbatim** (23:24; reports/stage_e6_briefs/end_checks.out; the suite reports/stage_e6_briefs/pytest_end.out):
```
$ date
Sun Sep 27 11:24:14 PM PDT 2026
$ git status --short
 M reports/stage_e6_member_audit.md
?? reports/E.6_RETURN.md
?? reports/stage_e6_STATE.md
?? reports/stage_e6_briefs/
?? reports/stage_e6_coder_A.md
?? reports/stage_e6_coder_B.md
?? reports/stage_e6_k7_screen/
$ git log --oneline -3
d661eb6 feat: K7 member freeze (Stage E.6), cluster freeze sha256 46cae308
3eb50c1 docs: split screening into E.6 (K7), E.7 (K6) and E.8 (K1), one cluster per session
4f9dfe0 docs: README, About this project section
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
$ ledger
17400 ledger/databento_spend.jsonl
0b5466c4366ca9eaba7e10525545631c83e97c1184a7e745d5ed8ad47a9fe957
$ acct-2 position (pull_step2.account_position on the step 2 gate; reads the ledger only)
stage-E.5-2026-09-27 {'account': 'acct-2', 'account_cap_usd': 125.0, 'account_credit_usd': 125.0, 'spent_usd': 124.673761, 'cap_headroom_usd': 0.326239, 'credit_left_usd': 0.326239}
$ python -m data.pull_step2 --status (MBT)
roots in status: 45 ; states: ['not_bought', 'sealed']
MBT {"state": "not_bought"}
$ git diff --stat
 reports/stage_e6_member_audit.md | 162 +++++++++++++++++++++++++++++++++++++++
 1 file changed, 162 insertions(+)
$ git diff --stat -- ledger/
(empty)
$ uv run pytest -q   (23:07:38-23:24:09, on d661eb6; no code or test changed after the commit)
4372 passed, 2 skipped, 1 xfailed, 54 warnings in 987.75s (0:16:27)
```
Manifest checks: E.1 and E.2a freezes ALL_OK at start and end; harness v6 preflight OK at start and end; cluster freezes
K2, K4, K5 and K3 unchanged; K7 new (46cae308..., 6 members), verified at 22:45 and at the end. Ledger: 17,400 lines,
sha256 0b5466c4... at start and end; `git diff --stat -- ledger/` empty; acct-2 unchanged ($124.673761 spent, $0.326239
left); MBT not bought. No spend, no quote. REGISTRATION.md 0 bytes and holdout all_ok with 0 unlocks at start and end. No
TopstepX reference, credential or API call (the session's new code and scripts grep clean); no edit under live/ or ops/,
to docs/NULL_CRITERIA.md, docs/NULL_CRITERIA_E.md, any frozen file, manifest or earlier stage's record; no harness change.
The only tracked file modified after the commit is this stage's audit (Part 2). Bars were read only by the runner
(research window; the window's trade dates 2025-04-01..2026-06-17); no session script opened a bar file. The web was used
only by Task 1b (read-only public pages: Wayback captures of CME's rulebook and calendar service, gov.uk, OPM). The end
checks were taken at 23:24, before progress.md and docs/STAGES.md were edited; those two files are the only other tracked
changes, uncommitted.

## 3. Results per task

### Task 0: startup (21:22-21:30)
HEAD 3eb50c1 (the prompt's commit), clean tree, all start checks passed, v6 preflight OK, no K7 freeze. The start suite
(21:22-21:39) equals E.5's end result.

### Task 1: member specifications (lead; reports/stage_e6_member_specs.md, 21:30-21:40, section 9 at 21:47)
Six members, six trials, every field with a catalog or design line reference, an earlier precedent or a logged reading.
Ordinals in catalog order: cp1 1, cp2 2, cp3 3, expiry 4, rev2h 5, montrend 6. MBT q_c 1, O/C (08:30, 15:00), vendor tick
5.00, CP2 buffer 20.00, eps 90 ticks. Adopted: E.3-L-01, 03-11, 13, 17, 19, 20, 22; K4-L-01, 06, 13; K3-L-11. New readings
K7-L-01..K7-L-12 (section 6). The ones that matter:
- **K7-L-01** the program trade date by clock: MBT bars carry CME's trade date, which books 24/7 weekends (from 2026-06-01)
  and the seven booked-forward holidays' sessions to the next trade date; every member identifies a bar by CT date and
  clock and reads nothing outside [d-1 17:00, d 16:00) CT (C3 and section 7 item 2).
- **K7-L-03** vendor-degraded dates removed for the three new members by a literal table (C4 names them; the engine masks
  the per-bar flag and the runner's window keeps them).
- **K7-L-05** K7-expiry-01 kept and run as frozen although no research expiry day survives the roll blackout; pre-declared
  that a trial counts in N when the runner writes its screen record.
- K7-L-06 (entry-bar instrument gate, a K7 narrowing, amended after audit F-2), K7-L-07 (engine closures in the
  multi-decision members), K7-L-08 (rev2h's orders on the decision - 1 bar).

### Task 1b: the K7 check (ReleaseChecker-OpusMed; reports/stage_e6_release_check.md, .json; 21:31-21:47)
| Item | Result |
|---|---|
| A MBTX, research window | 14 months: keep 3 (2025-06-27, 09-26, 2026-03-27), drop 1 (2025-12-24: CME's calendar capture of 2024-09-29 gives `"lastTrade":"26 Dec 2025"`), unverifiable 10 (no CME calendar capture after 2024-09-29; kept). CME's rule (ch. 348, 34802.F) now reads "a business day in either the UK or the US"; the catalog quotes the older "both" wording; the two differ only in 2021-12 and 2025-12. T_exp 11:00 CT on 2025-10-31 and 2026-03-27, 10:00 CT otherwise; final settlement "the BRR published at 4 p.m. London time on the Last Trade Date" |
| B Sunday opens | 63 Mondays; 5 are not trade dates (booked-forward holidays 2025-05-26, 09-01, 2026-01-19, 02-16, 05-25); CME's Sunday 17:00 CT open before 2026-05-29 and 24/7 trading after, cited from E.2a's records |
| C L-9 guard | holds: no bar booked to 2026-06-22 or later is in the file (1,617 dropped at build) and the loader refuses a leg with one; 2026-06-18 bars are delivered but not a window date (untradable); 49 guard tests pass |
| D holidays | England and Wales list equals gov.uk's for 2021-2026; US federal (observed) and Good Friday lists in the JSON |
| E roll blackout | research window: 0 of 14 expiry days outside the blackout; confirmation window: not computable (no 2019-2024 MBT roll metadata on disk) |

Rulings R-1b-1..R-1b-4 (specs section 9): MBTX drops 2025-12-24 and 2021-12-30 (the rows where the old wording gives a
non-final day) and adds nothing; the L-9 guard holds as the prompt defines it.

### Task 2: the modules and their tests
strategy/members/k7/: cp1, cp2, cp3, _port_common (MemberCoder-A-OpusXHigh, 21:37-22:15; tests/test_k7_members_ports.py,
_ports_cp2.py, _ports_cp3.py: 119 cases; mutants 150 of 153 killed, 3 equivalent); expiry, rev2h, montrend, _event_common,
_calendar (CRYPTO_FULL_SESSIONS 1,782 dates, VENDOR_DEGRADED 11, MBTX 60 = 62 by the rule less the two drops,
MBTX_UNVERIFIED 10) (MemberCoder-B-OpusXHigh, 21:37-22:14; tests/test_k7_members_events.py, _events_rev2h.py,
_events_montrend.py: 87 cases; mutants 86 of 87 killed, 1 no-op control). Coder B's three questions were ruled at 22:14
(the entry-bar gate blocks only the entry; VENDOR_DEGRADED keeps the builder's same-date mapping; the US holiday list
noted). Every file passes the freeze's static check. Gate suite 22:15-22:31: 4372 passed, 2 skipped, 1 xfailed.

### Task 3: fidelity audit (MemberAuditor-K7-FableXHigh; reports/stage_e6_member_audit.md Part 1; 22:15-22:43)
0 BLOCKING, 1 SHOULD FIX (F-1: no event test told the t-1 bar's close from its open), 8 NOTE. All six trials implement
their frozen entries and nothing more; no leak (VENDOR_DEGRADED only removes dates); the tables recomputed equal; the
ports equal K4's audited ports in rule body; 104 of 105 of the auditor's mutants killed.

### Task 4: rulings, the cluster freeze and the commit (reports/stage_e6_member_rulings.md)
R-T3-1 (F-1): test-only fix by MemberCoder-B (the end bars' opens now oppose their closes; `ec-end-close` killed by 18
tests; no member file changed). F-2, F-4, F-5: spec wording amended (S0.9, section 5 rows, K7-L-05, K7-L-06, K7-L-12).
F-3, F-7: flagged (section 7). F-6, F-8, F-9: no change. Freeze written 22:45:49 and verified; suite 22:46-23:04: 4372
passed, 2 skipped, 1 xfailed; commit d661eb6 23:04:30 (22 files: 11 member files, 6 test files, specs, release check .md
and .json, audit Part 1, rulings, freeze).

### Task 5: the screening run
Command (frozen, under v6): `PYTHONPYCACHEPREFIX=<fresh> nice -n 10 uv run python -m screening.stage_e_runner
--harness-sha256 9a8ebe73... --cluster K7 --all --window research --research-root data/processed --step2-root
data/processed_step2 --out-dir reports/stage_e6_k7_screen`, 23:04:45-23:06:28, exit 0, `K7 research: 6 members, 0
refused`. 13 files (6 records, 6 trip lists, the cluster record). Window: 265 trade dates 2025-04-01..2026-06-17 after
42 roll-blackout dates and 1 UR-1 date. Coverage 0.9596-0.9985 (all at or above 0.95). No floor label. Power `not_run`
for all six (no start-rule file before a step 2 purchase), by design.

### The screen per trial (from the runner's files; eps MBT 90 ticks)

| Ord | Trial | Trips | Mean ticks | Daily t | Screen | Coverage | Labels | MLL liquidations | Tier |
|---|---|---|---|---|---|---|---|---|---|
| 1 | K7-cp1-01 MBT | 261 | -7.4610 | -1.790 | fail | 0.9985 | none | 0 | B |
| 2 | K7-cp2-01 MBT | 263 | -14.3785 | -1.350 | fail | 0.9969 | none | 1 | B |
| 3 | K7-cp3-01 MBT | 101 | -3.1197 | -0.259 | fail | 0.9969 | none | 0 | B |
| 4 | K7-expiry-01 MBT | 0 | 0.0000 | undefined | fail | 0.9745 | none (calendar partly unverified; not traded) | 0 | B |
| 5 | K7-rev2h-01 MBT | 384 | -28.9198 | -2.285 | fail | 0.9967 | none | 2 | B |
| 6 | K7-montrend-01 MBT | 466 | -4.7260 | -0.441 | fail | 0.9596 | none | 0 | B |

MLL liquidations = accounts_started - 1 (3 in all; engine counter `mll_liquidation` agrees). Engine refusals by name:
`engine_not_a_window_date` (cp1 28, cp2 42, cp3 8, expiry 5, rev2h 56, montrend 248: intents on roll-blackout and UR-1
dates), one `engine_flatten_window` (cp2), one `account_not_active` (rev2h). No locked trip, no closure-gap fill.

### Task 6: recomputation (MemberAuditor-K7-FableXHigh, resumed; reports/stage_e6_member_audit.md Part 2)
23:07-23:15 PDT. The frozen member files equal the audited ones (the 10 member-file hashes in the freeze manifest match the
pre-audit list; only the two R-T3-1 test files changed). Item 1 VERIFIED (all six screens to 1e-9; 265 dates = the trade
dates less 42 roll-blackout dates and UR-1; every series value and daily_net_usd equals the day's trip nets; the six
record_sha256 links match); 2 VERIFIED (six Tier B, no label, coverage all >= 0.95); 3 VERIFIED (cp2's 263 and montrend's
466 trip nets rebuilt exactly from the frozen cost table; no fill in an event window; gross not checkable without prices);
4 VERIFIED WITH NOTES (below); 5 VERIFIED (6 screened, N = 156); 6 VERIFIED (3 MLL liquidations, none can move a tier).
No DISCREPANCY, so no tier is "unverified".

Item 4's note: K7-expiry-01's 12 member-eligible MBTX dates are all roll-blackout dates, so the engine refuses any
opening there as `engine_not_a_window_date` (the window test runs before the blackout test). On 5 dates the member
emitted its BUY on the T_exp - 301 bar and was refused by name; on the other 7 it emitted nothing, which under the audited
code happens only when that exact bar (04:59 or 05:59 CT) is absent. The outputs do not name those 7 dates (no per-date
intent ledger). montrend traded all 44 eligible Mondays (57 in CRYPTO_FULL_SESSIONS less VENDOR_DEGRADED, less 13
blackout Mondays), at most 15 entries a day, 38 of 932 fills shifted by a missing bar (4.1%, matching its 4.0% of missing
minutes); rev2h traded all 259 eligible dates (125 with two trips), every off-minute fill explained (missing bars, 2
liquidations); cp1 all fills 14:30 / 14:59, cp3 08:31 / 14:59, cp2 entries 08:46-13:00 with 75-bar holds (76-81 minutes
where bars were missing).

### Task 7: reading the result
- K7 enters the program with an empty Tier A: no K7 trial passes D5's screen (mean > 0 and t >= 1.0). Five trials lose on
  the research window; K7-expiry-01 never traded. K7 therefore does not count in D5's K and has no Holm family; the
  program's K stays as V14 (b) sets it (K = 9 for every Holm run until every cluster is screened).
- The three ports lose: cp1 -7.46, cp2 -14.38, cp3 -3.12 net ticks a day (eps 90). rev2h, the two-hour reversal, is
  the worst (-28.92, t -2.28, 384 trips). montrend, the Sunday-evening trend window, is near zero (-4.73, t -0.44, 466
  trips on its Mondays). From the trip lists (the lead's sums, descriptive only, not screen figures): gross P&L over
  the window cp1 +$128.50, cp2 -$725.50, cp3 +$27.00, rev2h -$2,155.00, montrend +$1,522.50; frozen D8 costs $440 to
  $2,149 per trial. So rev2h and cp2 lose before costs, while montrend's and cp1's small gross gains are far below their
  costs and far below eps (90 ticks = $45 a day on one MBT).
- K7-expiry-01's zero is structural: MBT.v.0 holds the expiring contract until it stops at T_exp, so every expiry day is
  a roll-blackout date. Its hypothesis was therefore not tested on this window; its trial still counts in N (K7-L-05,
  pre-declared), which is conservative.
- **Program N after the session: 150 + 6 = 156** (every K7 trial has a "run" record with a screen; none refused or
  excluded). The runner does not count N.
- **What K7's confirmation would need.** Only the null side (all six Tier B): the step 2 purchase of MBT's 2021-04..2025-03
  history, quoted at $3.11 (48 of 48 monthly chunks; reports/stage_e2b_step2_quotes.md line 62, quoted 2026-09-26; a fresh
  quote must be logged first) with holdout-2 sealed on arrival, then the D4 start rule and power check before a list is
  hashed. acct-2 holds $0.326239, so a top-up of about $2.79 at the quote ($3.10 with a 10% margin) is needed. Open
  questions before it: whether a K7 null run is worth it with an empty Tier A (the null statement is the only product);
  K7-expiry-01's confirmation-window roll-blackout count (not computable on this machine); the confirmation-window MBTX
  rows (all but 2021-12-30 unchecked); the regime mismatch (C section 7 item 3).

## 4. Delegation record

| Agent | Worker file | Model | Effort | Objective | Status and deviations |
|---|---|---|---|---|---|
| ReleaseChecker-OpusMed | worker-medium | opus | medium | Task 1b: MBTX dates and T_exp, Sunday opens, L-9 guard, holiday lists, roll blackout | done 21:31-21:47; one drop, ten unverifiable; item E's confirmation count and one scope question left to the lead (ruled R-1b-3, R-1b-4) |
| MemberCoder-A-OpusXHigh | worker-xhigh | opus | xhigh | Task 2: cp1, cp2, cp3, _port_common, port tests | done 21:37-22:15; no question; the brief's "19.99" test case was unreachable (off MBT's grid), pinned as the engine's rejection instead; left a `tail -f` process, stopped by the lead |
| MemberCoder-B-OpusXHigh | worker-xhigh | opus | xhigh | Task 2: expiry, rev2h, montrend, _event_common, _calendar, event tests | done 21:37-22:14; started before Task 1b finished (deviation from the plan's order, logged; R-1b-1 applied by SendMessage); three questions ruled; resumed 22:44-22:45 for R-T3-1 (tests only) |
| MemberAuditor-K7-FableXHigh | worker-xhigh | fable | xhigh | Task 3 fidelity audit; Task 6 recomputation (resumed) | done 22:15-22:43 and 23:07-23:15 (resumed by SendMessage for Task 6) |

## 5. Verification

**K7 fidelity audit (Part 1 of reports/stage_e6_member_audit.md).**

| Finding | Ruling | Fix |
|---|---|---|
| F-1 (SHOULD FIX): no event test told the t-1 bar's close from its open; mutant `ec-end-close` survived all 87 event tests (code correct, _event_common.py:203) | R-T3-1: accepted | tests only: end-bar opens set opposite to their closes in rev2h's B1_UP and b2() and montrend's FIRST_UP; the mutant is killed by 18 tests; member files unchanged (hash check) |
| F-2 the entry-bar instrument gate is a K7 narrowing, not E.3-L-12's text; spec rows named the entry bar among the target's bars | accepted as K7-L-06's own reading | specs S0.9, section 5 rows, section 8, K7-L-06 reworded; no code change |
| F-3 per-bar degraded flags: confirmation Mondays 2021-12-06 and 2022-01-03 trade on flagged Sunday-evening bars | K7-L-03's same-date mapping stands | flagged (section 7) |
| F-4 K7-L-12 did not name item 13 (b), (c), (d), (h) | accepted | K7-L-12 amended ((d): MBT is DCB_ONLY, D9.7 does not fire) |
| F-5 K7-L-05 should state its consequence | accepted | K7-L-05 amended |
| F-6 literal windows duplicate derived values | no change (pinned by tests; rules.sessions not importable by a member) | none |
| F-7 2024-07-03: crypto calendar has no early halt, the session rules flatten at 11:30 | no change (holdout-2) | flagged (section 7) |
| F-8 two test-coverage notes | no change (the facts are pinned elsewhere or exercised) | none |
| F-9 coverage windows measured on every date | expected (E.3-L-17) | none |

**K7 recomputation (Part 2).**
Part 2 (MemberAuditor-K7-FableXHigh, resumed, 23:07-23:15): items 1, 2, 3, 5, 6 VERIFIED; item 4 VERIFIED WITH NOTES (the
7 expiry dates without an emitted intent cannot be named from the outputs; every other untraded date and every deviating
fill minute is explained). No DISCREPANCY, so the lead had nothing to rule and no tier is "unverified".

## 6. Open choices (each decided by the lead alone, with the reason; each can be overturned)

- **K7-L-01** the program trade-date convention implemented by clock against CME's booking in the bars (C3 governs;
  section 7 item 2 names and rejects CME's assignment).
- **K7-L-02** CRYPTO_FULL_SESSIONS with K3-L-11's engine-F test (it removes only 2024-07-03, outside every window here).
- **K7-L-03** vendor-degraded dates removed by a literal table for the three new members, with the builder's same-date
  mapping (rev2h loses 2025-09-17, 09-24, 2026-03-16, 04-10; montrend loses 2026-03-16). **Flagged for the user:** the
  ports and other clusters' new members trade such dates; in the confirmation window montrend would trade Mondays
  2021-12-06 and 2022-01-03 whose Sunday-evening bars are flagged (audit F-3).
- **K7-L-04, R-1b-1** MBTX by the catalog's rule less two drops (2025-12-24, 2021-12-30), nothing added. **Flagged for the
  user:** CME's rule now reads "either"; replacing instead of dropping would add 2021-12-31 to the confirmation window.
- **K7-L-05** K7-expiry-01 kept and run as frozen (not withdrawn, roll convention unchanged); counted in N.
- **K7-L-06** the entry bar gates only the entry (a K7 narrowing, amended wording after audit F-2); coder B's question 1.
- **K7-L-07** engine closures: later decisions of rev2h and montrend apply as written.
- **K7-L-08** rev2h's orders computed on the decision - 1 bar; **K7-L-09** trading_windows (expiry's and montrend's as
  their entries state; rev2h to its exit fill bar); **K7-L-10** 6 declarations in catalog order; **K7-L-11** two coders,
  six test files; **K7-L-12** catalog section 7 settled by the frozen text.
- **R-1b-3** the L-9 guard read as the prompt states it (trade dates on or after 2026-06-22); 2026-06-18 bars are visible
  to members but untradable.
- **Coder B started before Task 1b finished** (the plan had it after 1b): only MBTX's research rows depended on 1b, and
  the ruling was applied by a follow-up message.
- **The pre-declared N rule** (K7-L-05): a trial counts when the runner writes its screen record, so the untraded
  K7-expiry-01 counts (N 156 rather than 155).
- The one-off generator (reports/stage_e6_briefs/gen_k7_calendar.py), the lead's scripts, the coder reports, the STATE
  file, the screen records and the audit's Part 2 stay uncommitted, as in E.3 and E.4.
- The end suite was run fresh although no code or test changed after d661eb6 (the prompt lists it among the end checks).
- **Task 1b's scope was extended** beyond the prompt's items: the UR-1 dates (2026-06-18/19) in the L-9 check, the holiday
  lists of the MBTX rule (2021-2026, item D) and the expiry days' roll-blackout survival count (item E, record only), so
  the frozen table serves the confirmation window and section 7 item 8 could be settled on evidence.
- **Coder A's "19.99" test case** (from the lead's brief) was ruled moot: 19.99 is off MBT's 5.00 grid, so the engine
  rejects such a bar before any member call; the test pins that rejection and the on-grid cases 15.00 and 20.00.
- **Audit notes F-6, F-8, F-9** left without change (pinned or exercised elsewhere; expected behaviour of the frozen
  interface), and F-7 (2024-07-03) left for the holdout and confirmation sessions.

## 7. What the next session must do first

- **The push the planning chat owes:** d661eb6 (K7 member freeze) is on main, not pushed. The session made exactly that
  one commit. Uncommitted by design: reports/E.6_RETURN.md, reports/stage_e6_STATE.md, reports/stage_e6_briefs/,
  reports/stage_e6_coder_A.md, _coder_B.md, reports/stage_e6_k7_screen/, the audit's Part 2 (reports/stage_e6_member_audit.md
  modified), and the progress.md and docs/STAGES.md lines.
- **Frozen hashes in force:** harness v6 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87; E.1 manifest
  96166eb3...; E.2a ML 077a57e1...; cluster freezes K2 8815a775..., K4 7abcde17..., K5 1d0c974f..., K3 c4fb5da4..., **K7
  46cae3082ae17cfd2a0e731cba27f6cc5dd2bdb94bb757d7ae48c684a5449462** (6 members).
- **Funding for a K7 confirmation:** MBT step 2 quoted $3.11 (2026-09-26); acct-2 has $0.326239; top-up about $2.79 at the
  quote, $3.10 with 10%. A fresh quote is logged before any spend.
- **Questions for the user:** (1) whether to run K7's null-side confirmation at all, with Tier A empty; (2) R-1b-1's drop
  versus replace for 2021-12 (confirmation window) and 2025-12; (3) K7-L-03's vendor-degraded table and its two
  confirmation Mondays (F-3); (4) K7-expiry-01's confirmation-window roll-blackout survivors cannot be counted without
  MBT's 2021-2024 roll metadata, which the step 2 purchase would bring; (5) the frozen crypto calendar and session rules
  disagree on 2024-07-03 (F-7), in holdout-2.
- **Next stage:** E.7 (K6) per V15 as amended.

## 8. Session cost

**Session cost.** Wall clock 21:22-23:31 PDT (2 h 9 min), all of it work: no pause, no usage-limit wait, no crash.
Tokens (transcripts): 104,210,918 in all; lead 40,507,369 (38.9%), workers 63,703,549 (61.1%); opus 91,808,590 (88.1%),
fable 12,402,328 (11.9%). About 97% are cache reads.

**Final ETA table** (PDT; tokens from the transcripts; no pause rows, since none occurred):

| Task | Owner | Model | Effort | Start | End | Time | Tokens | Status and deviations |
|---|---|---|---|---|---|---|---|---|
| 0 Startup checks (start suite in background to 21:39) | lead | opus | xhigh | 21:22 | 21:30 | 8 min | in lead | done; suite = E.5's end result |
| 1 Member specs (section 9 at 21:47) | lead | opus | xhigh | 21:30 | 21:47 | 17 min | in lead | done |
| 1b Event checks | ReleaseChecker-OpusMed | opus | medium | 21:30 | 21:46 | 16 min | 11,476,899 | done; 1 drop, 10 unverifiable |
| 2A Ports | MemberCoder-A-OpusXHigh | opus | xhigh | 21:37 | 22:15 | 38 min | 18,488,644 | done |
| 2B New members, tables (+ R-T3-1 22:44-22:45) | MemberCoder-B-OpusXHigh | opus | xhigh | 21:37 | 22:45 | 38 min | 21,335,678 | done; started before 1b finished (logged) |
| 2g Gate suite | lead | - | - | 22:15 | 22:31 | 16 min | in lead | 4372 passed |
| 3 Fidelity audit | MemberAuditor-K7-FableXHigh | fable | xhigh | 22:15 | 22:43 | 28 min | 12,402,328 (Parts 1 and 2) | 0 blocking, 1 should-fix, 8 notes |
| 4 Rulings, fix, freeze, suite, commit d661eb6 | lead | opus | xhigh | 22:43 | 23:04 | 21 min | in lead | done |
| 5 Screening run | lead | opus | xhigh | 23:04 | 23:06 | 2 min | in lead | 6 members, 0 refused |
| 6 Recomputation | MemberAuditor-K7-FableXHigh (resumed) | fable | xhigh | 23:07 | 23:16 | 9 min | above | no discrepancy |
| 7 Result, return, end suite (23:07-23:24), end checks, cost, progress | lead | opus | xhigh | 23:06 | 23:31 | 25 min | in lead | done |
| **Stage** | | | | 21:22 | 23:31 | **2 h 9 min wall and work** | **104,210,918** (lead 40,507,369, 38.9%; workers 63,703,549, 61.1%) | first estimate 2 h 50 min (to 00:12), revised 23:49; the prompt expected 1 to 1.5 h. The three full suites (16-18 min each, the prompt's gates) and the parallel coders set the pace |

**Tokens per model** (the lead transcript 0f52aad4's .jsonl plus every worker transcript under its subagents/ folder, from
21:00 PDT to the end; messages de-duplicated by message and request id; reports/stage_e6_briefs/cost.out, method of
reports/stage_e4_briefs/cost.py; the lead's last messages after the count, about 23:25-23:31, are not included):

| Model | Input | Output | Cache read | Cache creation | Total |
|---|---|---|---|---|---|
| claude-fable-5-1 | 1,224 | 12,100 | 11,546,783 | 842,221 | 12,402,328 |
| claude-opus-5-5 | 828 | 179,528 | 89,491,318 | 2,136,916 | 91,808,590 |
| all | 2,052 | 191,628 | 101,038,101 | 2,979,137 | 104,210,918 |

**Per worker spawn:**
- ReleaseChecker-OpusMed (worker-medium, opus, medium; Task 1b): 11,476,899 tokens, 21:30-21:46
- MemberCoder-A-OpusXHigh (worker-xhigh, opus, xhigh; Task 2 ports): 18,488,644 tokens, 21:37-22:15
- MemberCoder-B-OpusXHigh (worker-xhigh, opus, xhigh; Task 2 new members and tables, resumed for R-1b-1 and R-T3-1): 21,335,678 tokens, 21:37-22:45
- MemberAuditor-K7-FableXHigh (worker-xhigh, fable, xhigh; Task 3 audit and Task 6 recomputation): 12,402,328 tokens, 22:15-23:16

**Delegation share:** lead 38.9%, workers 61.1%; by tier opus 88.1%, fable 11.9%. These are token counts, not plan-credit
percentages; the /usage meter is the user's to read.
