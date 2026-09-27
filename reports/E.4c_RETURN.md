# Stage E.4 return, Part 3 (E.4c): K3 FX coded, audited, frozen and screened

Lead: Opus 5.5 (xhigh). 2026-09-27, 06:09-10:05 PDT, with one pause (06:58-09:11, the usage limit; no worker was running
in it). Harness v4 (82ae8536..., b20163a). Part 1: reports/E.4_RETURN.md (which ends with the table of every trial the session
screened); Part 2: reports/E.4b_RETURN.md.

## 1. Verdict summary

**K3: 30 trials coded, Fable-audited (0 blocking, 2 should-fix test gaps fixed by ruling R-K3-1), frozen (c5dfd5c, cluster
freeze c4fb5da41d69a6be54ea07d1ab35bd2b238d1fbeafaeb3008b886f8fc6888d95) and run once.** The Fable recomputation found no
discrepancy.

| Tier | Trial | Trips | Mean net ticks/contract/day | Daily t |
|---|---|---|---|---|
| A | K3-ldnrev-01 6E | 12 | +0.2842 | 1.422 |
| B | 26 trials (section 3) | 13-561 | -4.3509 to +0.3293 | -5.532 to 0.770 |
| excluded (coverage, not screened) | K3-cp1-01 6S (0.9373), K3-cp1-01 6N (0.9209), K3-cp2-01 6N (0.9461) | | | |

**Not traded: K3-mehedge-01 on EUR** (the EURO STOXX 50's free history could not be obtained; the entry's rule drops the
trial, never substitutes; named for the user). The Nikkei 225 was obtained free, so mehedge trades JPY. No member
unimplementable or refused; no fix instant or calendar date in the research window unverified. **Program N = 123 + 27 = 150.**
K3's confirmation needs the step 2 purchase of 6E, 6A, 6B, 6C, 6J, 6S and 6N ($49.34, reports/stage_e2b_step2_quotes.md; a
top-up is needed).

## 2. Guardrail evidence

**Session end checks, verbatim** (09:57:50), reports/stage_e4_briefs/end_checks_session.out:
```
$ git log --oneline -3
c5dfd5c feat: K3 member freeze (Stage E.4 Part 3), cluster freeze sha256 c4fb5da4
09f1999 feat: K5 member freeze (Stage E.4 Part 2), cluster freeze sha256 1d0c974f
e0ccf63 feat: K4 member freeze (Stage E.4 Part 1), cluster freeze sha256 cf066cb0
$ wc -c REGISTRATION.md
0 REGISTRATION.md
$ uv run python -m data.holdout status (keys)
holdout_1 all_ok True unlocks_logged 0 unlock_log_ok True
holdout_2 all_ok True unlocks_logged 0 unlock_log_ok True
$ python3 reports/stage_e2b_briefs/check_frozen.py
reports/stage_e1_freeze.json: manifest sha256 96166eb39b85d4fdcf132092978ee85393392de52c3857dc3f64ea7281454a7c files 32/32 match
reports/stage_e2a_ml_freeze.json: manifest sha256 077a57e1c00554dd0745302b247673d45ee05b805ac4bfd876f8497f7bbb1ed2 files 4/4 match
OK (the eight E.2a tables) ... ALL_OK
$ PYTHONPYCACHEPREFIX=<fresh> uv run python -m screening.harness_freeze verify --expected 82ae8536738ca43395f43356840c0b799a7925b7b75ddb4fc1353d3ab7491009
preflight OK: 82ae8536738ca43395f43356840c0b799a7925b7b75ddb4fc1353d3ab7491009
$ cluster freezes (load_cluster_freeze + verify_cluster_code)
K2 cluster freeze OK 8815a775e74996419b57751b1104ffa07cd4b3450eb18a9a92c6cbbd5615b7c5 44 members
K4 cluster freeze OK cf066cb0507134e2553781f42699165b471be45ebec6b07bfb0d75680e879d1a 12 members
K5 cluster freeze OK 1d0c974f18e884e1ad073d8f6f94d7bb70ee6f43971c7f23ccacab54103b3655 11 members
K3 cluster freeze OK c4fb5da41d69a6be54ea07d1ab35bd2b238d1fbeafaeb3008b886f8fc6888d95 30 members
$ ledger
14823 ledger/databento_spend.jsonl
02e7caa257bbee7b84d23a0394c9fae34985e884c1306fb47ea683546f15b1ed
$ uv run pytest -q   (the session's end suite, 09:49:43-10:00:28, on the tree committed as c5dfd5c)
4043 passed, 2 skipped, 1 xfailed, 54 warnings in 642.95s (0:10:42)
$ git status --short
 M docs/STAGES.md
 M progress.md
 M reports/stage_e4_member_audit.md
 M reports/stage_e4b_member_audit.md
 M reports/stage_e4c_member_audit.md
?? reports/E.4_RETURN.md, reports/E.4b_RETURN.md (and this file)
?? reports/stage_e4_STATE.md, reports/stage_e4b_STATE.md, reports/stage_e4c_STATE.md, reports/stage_e4_briefs/,
   reports/stage_e4_coder_A.md, _B.md, reports/stage_e4b_coder_A.md, _B.md, reports/stage_e4c_coder_A.md, _B.md,
   reports/stage_e4_harness_fix.md, reports/stage_e4_k2_regression/, reports/stage_e4_k4_screen/,
   reports/stage_e4b_k5_screen/, reports/stage_e4c_k3_screen/
$ git diff --stat
 docs/STAGES.md                    |   7 ++
 progress.md                       |  24 +++++
 reports/stage_e4_member_audit.md  | 140 +++++++++++++++++++++++++++
 reports/stage_e4b_member_audit.md | 199 ++++++++++++++++++++++++++++++++++++++
 reports/stage_e4c_member_audit.md | 112 +++++++++++++++++++++
 5 files changed, 482 insertions(+)
```
(progress.md and docs/STAGES.md gain the Part 3 lines after these checks.) Ledger: 14,823 lines at the session's start and
end, the same sha256; `git diff --stat -- ledger/` empty. No spend, no quote; the index histories were free public files. No
TopstepX reference. No edit to any frozen file, live/ or ops/. Bars read only by the runner (research window). Web used only
by the three Task 1b workers (read-only public pages and files).

## 3. Results per task

### Task 1: member specifications (reports/stage_e4c_member_specs.md)
Nine members, 30 trials: cp1, cp2, cp3 on the seven roots (6C and 6N undersized, screened as E.3-L-20); ldnrev on 6E, 6J, 6S
(R-05's 10-minute signal); ldnmom on 6E, 6J; mehedge on 6J; ecbfix on 6E; tkypre and tkypost on 6J. All q_c 1; O/C 07:20/
14:00. Readings K3-L-01..K3-L-12 (section 6).

### Task 1b: the K3 check (ReleaseChecker-OpusMed; reports/stage_e4c_release_check.md, .json)
All C9 clock known-answer tests pass (T_L 9/9, T_E 2/2, T_T 1/1 and three worked examples); the 11:00 CT London weeks equal
C9's list. EC-EW 63 holidays; TARGET six a year (2019-2021 from the written rule); Japanese holidays 148, gotobi 350, Tokyo
month-ends 87; the 31 Dec-3 Jan rule matches MUFG's TTM files exactly over 2019-2026 (1,868 business days); FX month-ends 87
with the two E&W drops C9 expects (none in the window). Nikkei 225: 1,761 closes from Nikkei Inc.'s file, no gaps. EURO STOXX
50: not obtainable free (rolling three months only; stitched captures leave 889 dates missing).

### Task 2: the modules and their tests
strategy/members/k3/: cp1, cp2, cp3 and _port_common (MemberCoder-A-OpusXHigh; AST-identical to E.3's K2 ports apart from
roots and names), then mehedge and _mehedge_signal (85 months of R_eq; the same coder, which finished first); ldnrev, ldnmom,
ecbfix, tkypre, tkypost, _calendar (FX_FULL_SESSIONS 1,797 after K3-L-11's 17 early-F dates; MONTH_ENDS 85; EW 63; TGT 48;
Tokyo business days 1,761; gotobi or month-end 404), _clocks (T_L, T_E, T_T) and _event_common (MemberCoder-B-OpusXHigh).
Gate suite 09:12-09:23: 4043 passed, 2 skipped, 1 xfailed.

### Task 3: fidelity audit (MemberAuditor-K3-FableXHigh; reports/stage_e4c_member_audit.md Part 1)
0 BLOCKING, 2 SHOULD FIX (two signal tests did not separate closes from opens), 10 NOTE; all nine modules implement their
entries and nothing more; every table recomputes equal (R_eq 85/85 exact); the dropped EUR trial follows the entry's rule.

### Task 4: rulings, the cluster freeze and the commit
R-K3-1 (S-1, S-2, N-5; tests only) and the notes: reports/stage_e4c_member_rulings.md. Freeze written and verified; suite
09:35-09:45 4043 passed; commit c5dfd5c (35 files, including the Nikkei files force-added past .gitignore).

### Task 5: the screening run
Frozen command under v4 (`python -m screening.stage_e_runner --harness-sha256 82ae8536... --cluster K3 --all --window
research ... --out-dir reports/stage_e4c_k3_screen`), 09:45:57-09:49:18, exit 0, `K3 research: 30 members, 0 refused`. 61
files (30 records, 30 trip lists, the cluster record). Window 299 trade dates (316 less 15 roll-blackout and 2 UR-1). Power
`not_run` for every screened trial, by design.

### The screen per trial (from the runner's files; eps 6E, 6B, 6J, 6S 13 ticks; 6A, 6C, 6N 17)

| Ord | Trial | Trips | Mean ticks | Daily t | Coverage | MLL | Tier |
|---|---|---|---|---|---|---|---|
| 1 | K3-cp1-01 6E | 284 | +0.3293 | 0.323 | 0.9908 | 0 | B |
| 2 | K3-cp1-01 6A | 282 | -2.0719 | -3.049 | 0.9787 | 1 | B |
| 3 | K3-cp1-01 6B | 264 | -1.1619 | -2.161 | 0.9571 | 1 | B |
| 4 | K3-cp1-01 6C | 276 | -2.1081 | -5.532 | 0.9629 | 1 | B |
| 5 | K3-cp1-01 6J | 275 | -0.8693 | -1.446 | 0.9743 | 0 | B |
| 6 | K3-cp1-01 6S | - | - | - | 0.9373 | - | excluded (before screening) |
| 7 | K3-cp1-01 6N | - | - | - | 0.9209 | - | excluded (before screening) |
| 8 | K3-cp2-01 6E | 294 | -3.1634 | -1.785 | 0.9956 | 4 | B |
| 9 | K3-cp2-01 6A | 295 | -3.5044 | -2.494 | 0.9885 | 3 | B |
| 10 | K3-cp2-01 6B | 296 | -2.2412 | -2.163 | 0.9780 | 2 | B |
| 11 | K3-cp2-01 6C | 293 | -1.7082 | -1.831 | 0.9741 | 1 | B |
| 12 | K3-cp2-01 6J | 291 | -2.4092 | -1.821 | 0.9848 | 3 | B |
| 13 | K3-cp2-01 6S | 293 | -4.3509 | -1.873 | 0.9631 | 7 | B |
| 14 | K3-cp2-01 6N | - | - | - | 0.9461 | - | excluded (before screening) |
| 15 | K3-cp3-01 6E | 112 | -1.8603 | -0.769 | 0.9970 | 4 | B |
| 16 | K3-cp3-01 6A | 130 | -2.0385 | -0.900 | 0.9924 | 4 | B |
| 17 | K3-cp3-01 6B | 123 | -0.9169 | -0.597 | 0.9841 | 2 | B |
| 18 | K3-cp3-01 6C | 118 | -2.6732 | -2.244 | 0.9821 | 2 | B |
| 19 | K3-cp3-01 6J | 140 | -3.4127 | -1.580 | 0.9881 | 6 | B |
| 20 | K3-cp3-01 6S | 138 | -2.4593 | -0.650 | 0.9735 | 6 | B |
| 21 | K3-cp3-01 6N | 138 | -1.6073 | -0.928 | 0.9593 | 3 | B |
| 22 | K3-ldnrev-01 6E | 12 | +0.2842 | 1.422 | 0.9996 | 0 | **A** |
| 23 | K3-ldnrev-01 6J | 13 | +0.0823 | 0.770 | 0.9948 | 0 | B |
| 24 | K3-ldnrev-01 6S | 13 | +0.0541 | 0.190 | 0.9877 | 0 | B |
| 25 | K3-ldnmom-01 6E | 254 | -0.7346 | -0.793 | 0.9996 | 1 | B |
| 26 | K3-ldnmom-01 6J | 237 | -1.8592 | -3.096 | 0.9952 | 1 | B |
| 27 | K3-mehedge-01 6J | 13 | -0.3457 | -1.574 | 0.9968 | 0 | B |
| 28 | K3-ecbfix-01 6E | 561 | -2.8103 | -0.553 | 0.9957 | 7 | B |
| 29 | K3-tkypre-01 6J | 52 | -0.4358 | -0.832 | 0.9631 | 0 | B |
| 30 | K3-tkypost-01 6J | 269 | -1.8946 | -1.176 | 0.9766 | 3 | B |

No floor label on any trial (the shortest holds are MLL closes). MLL liquidations: 62 on 20 Tier B trials, none on Tier A.

### Task 7: reading the result
- K3 enters with a non-empty Tier A: K3-ldnrev-01 6E, 12 month-end trades in 299 dates, mean 0.28 ticks a day against 6E's
  eps of 13. C10 called the month-end members likely "inconclusive by design" under D4's power check.
- Every port loses on every screened root; CP1 on 6C has the program's most negative t so far (-5.53).
- The three coverage exclusions are the ports that read the Globex-open minute or the long afternoon on the two thinnest
  roots (6S, 6N); CP3 on both, inside the day session, passes coverage.
- **Program N after Part 3: 123 + 27 = 150** (27 screened; the 3 coverage-excluded trials and the dropped EUR mehedge trial
  were never screened).
- K3's confirmation session needs: Tier A K3-ldnrev-01 6E; Tier B the 26 above; the step 2 purchase of the seven FX vehicles,
  $49.34, with an acct-2 top-up (acct-2 holds $21.52 before K4's $11.46 and K5's $9.74, which would leave $0.32); the
  confirmation-window tick check (audit N-4); the start rule and D4's power check.

## 4. Delegation record

| Agent | Worker file | Model | Effort | Objective | Status and deviations |
|---|---|---|---|---|---|
| ReleaseChecker-OpusMed (K3, fresh) | worker-medium | opus | medium | 1b: clocks, calendars, index histories | done 06:13-06:35 |
| MemberCoder-A-OpusXHigh (K3, fresh) | worker-xhigh | opus | xhigh | cp1, cp2, cp3; then mehedge (finished first) | done 06:17-06:31 (ports), resumed 06:36-06:45 (mehedge) |
| MemberCoder-B-OpusXHigh (K3, fresh) | worker-xhigh | opus | xhigh | ldnrev, ldnmom, ecbfix, tkypre, tkypost, tables | done 06:36-06:57; resumed 09:11 (K3-L-12) and 09:33-09:34 (R-K3-1) |
| MemberAuditor-K3-FableXHigh | worker-xhigh | fable | xhigh | Task 3 audit; Task 6 recomputation (resumed) | done 09:12-09:33 and 09:49-09:57 |

## 5. Verification

**Fidelity audit (Part 1).** S-1 and S-2 (SHOULD FIX): the ldnrev and ldnmom signal tests did not separate closes from opens;
R-K3-1 changed the fixtures (and N-5's T_L-10 case); each mutant now fails; no member module changed. N-1: K3-L-11's
engine-F condition binds only from 2024, because rules/sessions.py has no Topstep holiday schedule before then (15 US
holidays in 2019-2023 stay full sessions, and the engine holds trades on them to their natural exits): a harness-coverage fact
for every confirmation session (section 7). N-4: the tick history is confirmed for the research-window bars only. The other
notes: no change (reports/stage_e4c_member_rulings.md).

**Recomputation (Part 2).** Item 0 VERIFIED (the freeze's 16 files equal the audited hashes apart from R-K3-1's test file);
1 VERIFIED (27 screens to 1e-9 on the 299 dates); 2 VERIFIED WITH NOTES (tiers A 1, B 26, excluded 3 match D5 and OC-H; no
floor label); 3 VERIFIED (cp1 6E 284/284 and ldnmom 6J 237/237 trip nets rebuilt exactly from the cost table; series and
daily_net_usd 299/299; the 13:30 FOMC-day fill is outside the half-open D8 window); 4 VERIFIED WITH NOTES (no off-event trip;
untraded events explained, zero signal and missing bar not separable without bars; tkypre's nine untraded dates inferred as
missing 17:29 bars); 5 VERIFIED (N = 150); 6 VERIFIED WITH NOTES (62 liquidations on 20 Tier B trials, none on Tier A; no tier
depends on them). No DISCREPANCY, so no tier is "unverified".

## 6. Open choices

- **K3-L-01..K3-L-12** (specs section 10): tables span 2019-04..2026-06; fix instants as literal per-date tables built with
  zoneinfo; C4's "bars of one position" read as the entry-time guard; the early-halt test on trade date d from a table (a
  bar's field names its CT calendar date); ecbfix's legs sequential; month-ends include halted dates and a halted or E&W
  month-end is skipped; mehedge's index not a leg; Tokyo business days and gotobi as C9 defines them; section 7 settled by the
  frozen text; two coders, mehedge to the first to finish.
- **K3-L-11** (on MemberCoder-A's observation): an FX date whose engine flatten time is early is an early-close date for C4
  (17 dates, all 2024-2026). **Flagged for the user:** the frozen FX calendar and the frozen session rules disagree on these
  US holidays; nothing in the harness changed.
- **K3-L-12** (on MemberCoder-B's question): ecbfix trades leg 2 only after leg 1 opened that date.
- **The EUR mehedge trial is dropped**, as the entry's rule says; nothing substituted (no Datastream index, no other source).
- **The Nikkei files were force-added past .gitignore** into the K3 freeze commit, because the prompt names "the index files if
  obtained"; they are free and small (about 200 KB with the manifest). The unobtained STOXX captures stay untracked.
- **Program N counts only screened trials** (27 of 30), as in Part 2.
- The Task 3 audit ran while the gate suite ran; the files were unchanged after.

## 7. What the next session must do first

- **Push (the planning chat):** four local commits, b20163a (harness v4), e0ccf63 (K4), 09f1999 (K5), c5dfd5c (K3), none
  pushed. Uncommitted for review: the three return documents, the three STATE files, the coder reports, the fix report, Part 2
  of the three audits, the four runner output folders, the briefs, progress.md and docs/STAGES.md.
- **Frozen hashes:** harness v4 82ae8536...; cluster freezes K2 8815a775..., K4 cf066cb0..., K5 1d0c974f..., K3
  c4fb5da41d69a6be54ea07d1ab35bd2b238d1fbeafaeb3008b886f8fc6888d95.
- **Funding:** K4 $11.46 and K5 $9.74 fit acct-2's $21.52 ($0.32 left); K3's $49.34 needs a top-up of about $49.02 (more
  with D13's +10%), a user decision.
- **Before any confirmation run:** the session rules' missing pre-2024 Topstep holiday schedule (audit N-1) should be
  settled, since every cluster's confirmation window lies in 2019-2024; and K3's confirmation-window tick history (N-4).
- **Questions for the user:** the EUR mehedge drop; K3-L-11 and the FX calendar inconsistency; the pre-2024 holiday schedule;
  the questions from Parts 1 and 2.

## 8. Session cost (Part 3)

Wall clock 06:09-10:05 PDT (236 min), of which 06:58-09:11 (133 min) was the usage-limit pause with no worker running: work
time 103 min. Tokens from this session's transcript (17ffffc1-5761-44c4-9f3b-5ee8c14fb08c.jsonl) and its subagent
transcripts, once per message id, over 06:09-10:01 PDT (reports/stage_e4_briefs/cost.py), computed after everything else was
written; the few lead messages after 10:01 are not counted.

Final ETA table (estimate for Part 3: 2 h 30 of work):

| Task / spawn | Owner | Model | Effort | Start | End | Time | Tokens | Status and deviations |
|---|---|---|---|---|---|---|---|---|
| 1 K3 specs (s.11 at 06:37; K3-L-11 06:48; K3-L-12 09:11) | lead | opus | xhigh | 06:09 | 06:17 | 8 min (+ rulings) | in lead total | done |
| 1b Clocks, calendars, index histories | ReleaseChecker-OpusMed | opus | medium | 06:13 | 06:35 | 22 min | 7,036,533 | done; SX5E not obtainable |
| 2 Coder A: ports; then mehedge | MemberCoder-A-OpusXHigh | opus | xhigh | 06:17 | 06:45 | 28 min | 26,602,171 | done; 362 then 414 passed |
| 2 Coder B: 5 event members, tables | MemberCoder-B-OpusXHigh | opus | xhigh | 06:36 | 06:57 | 21 min (+2 resumes, 09:11 and 09:33) | 19,589,682 | done; 198 passed |
| Pause (usage limit) | - | - | - | 06:58 | 09:11 | 133 min | - | not work |
| 2 gate suite | lead | - | - | 09:12 | 09:23 | 11 min | in lead total | 4043 passed |
| 3 Fidelity audit | MemberAuditor-K3-FableXHigh | fable | xhigh | 09:12 | 09:33 | 21 min | in the auditor total | 0/2/10 |
| 4 R-K3-1, freeze, suite, commit c5dfd5c | lead | opus | xhigh | 09:33 | 09:45 | 12 min | in lead total | done |
| 5 Screening run | lead (frozen CLI) | - | - | 09:45:57 | 09:49:18 | 3 min | in lead total | 30 run, 0 refused |
| 6 Recomputation | MemberAuditor-K3-FableXHigh | fable | xhigh | 09:49 | 09:57 | 8 min | 11,275,545 (Tasks 3 and 6) | no DISCREPANCY |
| 7 End checks, end suite (09:49-10:00), returns, final table | lead | opus | xhigh | 09:49 | 10:05 | 16 min | in lead total | done |
| Lead | lead | opus | xhigh | 06:09 | 10:01 | - | 54,867,798 | - |
| **Part 3 total** | lead + 4 agents | - | - | 06:09 | 10:05 | **103 min of work**, 133 min paused | **119,371,729** | estimate 2 h 30; faster than guessed |

Tokens per model (Part 3):

| Model | Input | Output | Cache read | Cache creation | Total |
|---|---|---|---|---|---|
| claude-fable-5-1 | 902 | 1,598 | 10,274,044 | 999,001 | 11,275,545 |
| claude-opus-5-5 | 678 | 151,458 | 105,442,616 | 2,501,432 | 108,096,184 |
| all | 1,580 | 153,056 | 115,716,660 | 3,500,433 | 119,371,729 |

Per worker spawn (Part 3): ReleaseChecker-OpusMed (worker-medium, opus, medium) 7,036,533; MemberCoder-A-OpusXHigh
(worker-xhigh, opus, xhigh; ports and mehedge) 26,602,171; MemberCoder-B-OpusXHigh (worker-xhigh, opus, xhigh) 19,589,682;
MemberAuditor-K3-FableXHigh (worker-xhigh, fable, xhigh; Tasks 3 and 6) 11,275,545. Delegation share: lead 54,867,798
(46.0%), workers 64,503,931 (54.0%). By model: opus 90.6%, fable 9.4%. Cache reads 96.9%.

**Session total (Parts 1-3), 01:54-10:05 PDT.** Wall clock 491 min; pauses 214 min (02:19-02:29 the user's pause and a
process restart; 03:00-04:11 and 06:58-09:11 the usage limit); work 277 min (4 h 37 min) against the initial estimate of
about 8 h. Tokens 01:50-10:01 PDT:

| Model | Input | Output | Cache read | Cache creation | Total |
|---|---|---|---|---|---|
| claude-fable-5-1 | 3,252 | 15,150 | 29,702,100 | 2,922,010 | 32,642,512 |
| claude-opus-5-5 | 2,186 | 535,098 | 280,183,870 | 6,749,028 | 287,470,182 |
| all | 5,438 | 550,248 | 309,885,970 | 9,671,038 | 320,112,694 |

Lead 149,087,223 (46.6%), workers 171,025,471 (53.4%), across 14 worker spawns (6 in Part 1, 4 in Part 2, 4 in Part 3) plus
their resumes. By model: opus 89.8%, fable 10.2%. Cache reads 96.8%. Per-part figures: Part 1 134,937,561 (reports/
E.4_RETURN.md section 8), Part 2 60,082,643 (reports/E.4b_RETURN.md section 8), Part 3 119,371,729 (above); the small
remainder of the session total is lead messages between the parts' slices.
