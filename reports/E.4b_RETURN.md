# Stage E.4 return, Part 2 (E.4b): K5 metals coded, audited, frozen and screened

Lead: Opus 5.5 (xhigh). 2026-09-27, 05:02-06:12 PDT, no pause. Harness v4 (82ae8536..., committed b20163a in Part 1).
Part 1: reports/E.4_RETURN.md; Part 3 (K3) follows.

## 1. Verdict summary

**K5: 11 trials coded, Fable-audited (0 blocking, 1 should-fix test gap fixed by ruling R-K5-1), frozen (09f1999, cluster
freeze 1d0c974f18e884e1ad073d8f6f94d7bb70ee6f43971c7f23ccacab54103b3655) and run once.** The Fable recomputation found no
discrepancy.

| Tier | Trial | Trips | Mean net ticks/contract/day | Daily t |
|---|---|---|---|---|
| A | K5-fomc-01 MGC | 8 | +2.3498 | 1.846 |
| B | cp1 MGC, cp2 MGC, cp3 MGC, cp3 MHG, preauc MGC, ovr MGC, ovr MHG | 101-295 | -3.5608 to +10.5570 | -1.201 to 0.906 |
| excluded (OC-H) | cp1 MHG, cp2 MHG (coverage 0.9196, 0.8966: not screened); pmfix MGC (mean hold 9.964 min: screened, t -2.194) | | | |

No member unimplementable or refused. No release dropped; the 14 PM-only no-auction days (2 in the window) come from
dated LBMA notices; no research-window date is unverified. **Program N = 114 + 9 screened = 123.** K5's confirmation
needs the step 2 purchase of MGC and MHG ($9.74, reports/stage_e2b_step2_quotes.md; acct-2 held $21.52 before K4's
$11.46, so $10.06 would remain and no top-up is needed if K4's purchase goes first).

## 2. Guardrail evidence

Start checks: Part 1's (reports/E.4_RETURN.md section 2). **End checks for Part 2, verbatim** (06:09:05),
reports/stage_e4_briefs/end_checks_part2.out:
```
$ git log --oneline -3
09f1999 feat: K5 member freeze (Stage E.4 Part 2), cluster freeze sha256 1d0c974f
e0ccf63 feat: K4 member freeze (Stage E.4 Part 1), cluster freeze sha256 cf066cb0
b20163a feat: harness v4 (Stage E.4 H4), C-1 fix and per-trial trip lists
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
$ ledger
14823 ledger/databento_spend.jsonl
02e7caa257bbee7b84d23a0394c9fae34985e884c1306fb47ea683546f15b1ed
$ uv run pytest -q   (05:46:02-05:56:10, on the tree committed as 09f1999; no code or test changed after it)
3525 passed, 2 skipped, 1 xfailed, 54 warnings in 606.03s (0:10:06)
$ git status --short   (untracked and modified, apart from this file)
 M docs/STAGES.md
 M progress.md
 M reports/stage_e4_member_audit.md
 M reports/stage_e4b_member_audit.md
?? reports/E.4_RETURN.md
?? reports/stage_e4_STATE.md, reports/stage_e4b_STATE.md, reports/stage_e4_briefs/, reports/stage_e4_coder_A.md, _B.md,
   reports/stage_e4b_coder_A.md, _B.md, reports/stage_e4_harness_fix.md, reports/stage_e4_k2_regression/,
   reports/stage_e4_k4_screen/, reports/stage_e4b_k5_screen/
```
Ledger unchanged (14,823 lines, same sha256); no spend, no quote. No TopstepX reference. No edit to any frozen file,
live/ or ops/. Bars read only by the runner (research window). Web used only by Task 1b (read-only public pages).

## 3. Results per task

### Task 1: member specifications (reports/stage_e4b_member_specs.md)
Seven members, 11 trials: cp1, cp2, cp3 and ovr on MGC and MHG; preauc, pmfix and fomc on MGC (silver has no vehicle;
platinum is out). MGC q_c 1 (O/C 07:20/12:30), MHG q_c 2 (07:10/12:00); CP2 buffer 0.40 / 0.0020. Ordinals: cp1 1-2, cp2
3-4, cp3 5-6, preauc 7, pmfix 8, fomc 9, ovr 10-11. Readings K5-L-01..K5-L-12 (section 6). Catalog section 7: item 1
settled by the frozen harness (K5-L-04: auction starts are not in the release calendar, so no D8 event cost or D9.5a
guard at them); items 3-6 as frozen.

### Task 1b: the K5 release check (ReleaseChecker-OpusMed; reports/stage_e4b_release_check.md, .json)
61 England-and-Wales bank holidays 2019-05..2026-06 (equal in both directions to IBA's holiday calendars); 1,802 scheduled
gold auction days (research window 307); 14 PM-only no-auction days (Christmas and New Year half days, each with a dated
advance LBMA notice; 2025-12-24 and 12-31 in the window); instants 04:30/09:00 CT, or 05:30/10:00 CT on the 124 weekdays
of 5-hour weeks (C10's table matches in all eight years); the 57 FOMC rows equal E.3's table (10 in the window).
Confirmation-window evidence partly rests on PDF metadata (K5-L-01; section 7).

### Task 2: the modules and their tests
strategy/members/k5/: cp1, cp2, cp3, ovr, _calendar (METALS_FULL_SESSIONS, 1,784 dates) and _port_common
(MemberCoder-A-OpusXHigh; 238 passed with the freeze and template tests; ovr copied from K4's with K5's clock); preauc,
pmfix, fomc, _releases (AM 1,802, PM 1,788, NO_AUCTION_DAYS 14, FOMC 57) and _event_common (MemberCoder-B-OpusXHigh;
125 passed). Gate suite 05:23-05:34: 3525 passed, 2 skipped, 1 xfailed.

### Task 3: fidelity audit (MemberAuditor-K5-FableXHigh; reports/stage_e4b_member_audit.md Part 1)
0 BLOCKING, 1 SHOULD FIX (S-1), 9 NOTE; all seven members implement their entries and nothing more; every table
recomputes exactly; F-7 holds; 52 of 56 mutants killed (2 equivalent, S-1, one probe).

### Task 4: rulings, the cluster freeze and the commit
R-K5-1 (S-1, test only) and the notes: reports/stage_e4b_member_rulings.md. Freeze written and verified; suite
05:46-05:56 3525 passed; commit 09f1999 (22 files).

### Task 5: the screening run
Frozen command under v4 (`python -m screening.stage_e_runner --harness-sha256 82ae8536... --cluster K5 --all --window
research ... --out-dir reports/stage_e4b_k5_screen`), 05:56:28-05:57:40, exit 0, `K5 research: 11 members, 0 refused`.
23 files (11 records, 11 trip lists, the cluster record). Window 295 trade dates on both roots. Power `not_run` for every
screened trial, by design.

### The screen per trial (from the runner's files; eps MGC 85, MHG 34 ticks)

| Ord | Trial | Trips | Mean ticks | Daily t | Screen | Coverage | Labels | MLL liquidations | Tier |
|---|---|---|---|---|---|---|---|---|---|
| 1 | K5-cp1-01 MGC | 284 | -0.6037 | -0.131 | fail | 0.9969 | none | 0 | B |
| 2 | K5-cp1-01 MHG | - | - | - | not screened | 0.9196 | coverage_below_0.95 | - | excluded (before screening) |
| 3 | K5-cp2-01 MGC | 295 | +10.5570 | 0.906 | fail | 0.9992 | none | 1 | B |
| 4 | K5-cp2-01 MHG | - | - | - | not screened | 0.8966 | coverage_below_0.95 | - | excluded (before screening) |
| 5 | K5-cp3-01 MGC | 101 | +8.4945 | 0.793 | fail | 0.9996 | none | 2 | B |
| 6 | K5-cp3-01 MHG | 126 | +3.2468 | 0.695 | fail | 0.9576 | none | 0 | B |
| 7 | K5-preauc-01 MGC | 280 | +1.3052 | 0.358 | fail | 0.9966 | none | 0 | B |
| 8 | K5-pmfix-01 MGC | 278 | -9.9896 | -2.194 | fail | 1.0000 | mean_holding_below_10min | 1 | excluded (before confirmation) |
| 9 | K5-fomc-01 MGC | 8 | +2.3498 | 1.846 | pass | 0.9966 | none | 0 | **A** |
| 10 | K5-ovr-01 MGC | 289 | -3.5608 | -0.330 | fail | 0.9992 | none | 2 | B |
| 11 | K5-ovr-01 MHG | 190 | -3.3977 | -1.201 | fail | 0.9559 | none | 1 | B |

### Task 7: reading the result
- K5 enters with a non-empty Tier A: K5-fomc-01 MGC, 8 trades in 295 dates. Its research mean (2.35 ticks a day) is far
  below MGC's eps (85 ticks); the source-window label is on it (R-04), and C12 called it likely "inconclusive by design"
  under D4's power check.
- **Two tiers rest on the account model's liquidations (Task 6 item 6, for the user).** K5-cp3-01 MGC would pass the
  screen (t 1.25) without its two XFA liquidations; as computed it is Tier B. K5-pmfix-01 MGC is excluded only because
  one liquidation at its 09:02 entry bar made a 0.0-minute trip, pulling the mean hold to 9.964 minutes (277 trips hold
  exactly 10.0); it fails the screen either way (t -2.194), so the exclusion changes only B to excluded. Both are
  reported as computed.
- Copper's micro (MHG) fails coverage for the two ports that read its Globex-open minute or its post-settlement afternoon;
  CP3 and ovr, inside the day session, pass.
- **Program N after Part 2: 114 + 9 = 123.** Screened = the 9 records with status "run" and a screen; the two
  coverage-excluded trials were never screened (OC-H: "excluded before screening"), and pmfix was screened and then
  excluded before confirmation, so it counts.
- K5's confirmation session needs: Tier A K5-fomc-01 MGC; Tier B the 7 above; the 3 excluded trials are not run; the step 2
  purchase of MGC and MHG, $9.74; then the start rule and D4's power check.

## 4. Delegation record

| Agent | Worker file | Model | Effort | Objective | Status and deviations |
|---|---|---|---|---|---|
| ReleaseChecker-OpusMed (K5, fresh) | worker-medium | opus | medium | 1b: UK holidays, LBMA auction days and instants, FOMC | done 05:03-05:10 |
| MemberCoder-A-OpusXHigh (K5, fresh) | worker-xhigh | opus | xhigh | cp1, cp2, cp3, ovr, _calendar | done 05:06-05:23; resumed 05:45 for R-K5-1 |
| MemberCoder-B-OpusXHigh (K5, fresh) | worker-xhigh | opus | xhigh | preauc, pmfix, fomc, _releases | done 05:11-05:23 |
| MemberAuditor-K5-FableXHigh | worker-xhigh | fable | xhigh | Task 3 audit; Task 6 recomputation (resumed) | done 05:23-05:43 and 05:58-06:08 |

## 5. Verification

**Fidelity audit (Part 1).** S-1 (SHOULD FIX): the CP2 range test did not pin the 15-minute end (the mutant
RANGE_MINUTES = 14 survived); R-K5-1: a sell-side pair and a literal assertion added, test only; the mutant now fails.
The K4 twin test (committed with the K4 freeze) likely has the same gap; K4's cp2.py is correct and was left as frozen
(section 6). Notes N-1..N-9: no change (reports/stage_e4b_member_rulings.md).

**Recomputation (Part 2).** Item 0 VERIFIED (the frozen files equal the audited hashes apart from R-K5-1's test file);
1 VERIFIED (9 screens to 1e-9; values and daily_net_usd rebuilt from the trips; record_sha256 11/11); 2 VERIFIED WITH
NOTES (tiers agree with OC-H; coverage exclusions' expected minutes recompute exactly; pmfix's label rests on one
liquidation); 3 VERIFIED (all 1,851 trip nets match the frozen cost table); 4 VERIFIED WITH NOTES (preauc 0 unexplained;
pmfix 1 silent no-trade, 2025-07-24; fomc's 2 untraded dates are roll blackouts; 1 D9.5a deferral; late fills consistent
with missing bars, for example a 77-minute MGC gap on 2026-02-25); 5 VERIFIED (N = 123); 6 VERIFIED WITH NOTES (fomc has
no liquidation; cp3 MGC would pass without its two). No DISCREPANCY, so no tier is "unverified".

## 6. Open choices

- **K5-L-01..K5-L-12** (specs section 10): tables span 2019-05..2026-06; London instants by zoneinfo; a scheduled auction
  day is per auction (a PM-only half day is a preauc day, not a pmfix day); catalog section 7 item 1 settled by the frozen
  harness (no LBMA row in the release calendar, so no D8 event cost or D9.5a guard at auction starts); **K5-L-05** ovr's
  "eligible trade dates (C4)" read as EC-CAL full sessions, as K4-L-08, because F-7 records one rule text and the runner,
  not the member, meets C4's roll-blackout clause (the auditor agreed: fixed by R-24/F-7 rather than by the words alone);
  the value floor 80% of the possible values (80/100 gold, 64/80 copper); CP2's buffer as 4 x vendor_tick; both clock
  slots in the coverage windows; pmfix's and fomc's 10-minute hold coded as written (the floor label may apply); preauc
  unconditional; 11 declarations (preauc 1 trial: silver has no vehicle); two coders.
- **R-K5-1** accepted as a test-only fix. **The K4 twin test was not changed**: it was committed with the K4 freeze, and
  K4's cp2.py is correct and rule-identical to K5's. Flagged for the user.
- **Program N counts only screened trials** (9 of 11): the two coverage-excluded trials were never screened. The prompt's
  "the K5 trials screened" and OC-H's text; the auditor agreed; the decision is reserved to the user if they prefer to
  count declared trials.
- The Task 3 audit ran while the gate suite ran, as in Part 1; the files were unchanged after (hash check).
- Part 2's end suite is the Task 4 suite (05:46-05:56) on the tree committed as 09f1999; no code or test changed after.

## 7. What the next session must do first

- **Push (the planning chat):** commit 09f1999 (K5 freeze) joins b20163a and e0ccf63, all local and unpushed.
  Uncommitted for review: this file, reports/stage_e4b_STATE.md, the coder reports, Part 2 of
  reports/stage_e4b_member_audit.md, reports/stage_e4b_k5_screen/ (23 runner files), the briefs.
- **Frozen hashes:** K5 cluster freeze reports/stage_e_k5_member_freeze.json,
  1d0c974f18e884e1ad073d8f6f94d7bb70ee6f43971c7f23ccacab54103b3655; harness v4 82ae8536...; K4 cf066cb0...; K2 8815a775...
- **Funding for K5's confirmation:** MGC and MHG, $9.74. After K4's $11.46 from acct-2's $21.52, $10.06 remains, so no
  top-up is needed for either.
- **Before a Tier A event member's confirmation run:** K5-fomc-01's dates are the frozen calendar's FOMC rows (verified);
  if preauc or pmfix ever reaches Tier A, its 2019-2024 no-auction days need the re-check K5-L-01 names.
- **Questions for the user:** the two liquidation-dependent tiers (cp3 MGC, pmfix MGC; section 3); counting N on screened
  trials; the K4 twin test gap; the E.3 and Part 1 questions still open.

## 8. Session cost (Part 2)

Wall clock 05:02-06:12 PDT (70 min), no pause. Tokens from this session's transcript and its subagent transcripts, once
per message id, over 05:02-06:09 PDT (reports/stage_e4_briefs/cost.py); the lead's later tokens (this file, progress.md,
STAGES.md) fall in Part 3's slice.

Final ETA table (estimate for Part 2: 2 h 00):

| Task / spawn | Owner | Model | Effort | Start | End | Time | Tokens | Status and deviations |
|---|---|---|---|---|---|---|---|---|
| 1 K5 specs (s.11 at 05:12) | lead | opus | xhigh | 05:02 | 05:12 | 10 min | in lead total | done |
| 1b LBMA/FOMC check | ReleaseChecker-OpusMed | opus | medium | 05:03 | 05:10 | 7 min | 2,931,733 | done |
| 2 Coder A | MemberCoder-A-OpusXHigh | opus | xhigh | 05:06 | 05:23 | 17 min (+1 at 05:45) | 9,750,683 | done; 238 passed |
| 2 Coder B | MemberCoder-B-OpusXHigh | opus | xhigh | 05:11 | 05:23 | 12 min | 8,778,078 | done; 125 passed |
| 2 gate suite | lead | - | - | 05:23 | 05:34 | 11 min | in lead total | 3525 passed |
| 3 Fidelity audit | MemberAuditor-K5-FableXHigh | fable | xhigh | 05:23 | 05:43 | 20 min | in the auditor total | 0/1/9 |
| 4 R-K5-1, freeze, suite, commit 09f1999 | lead | opus | xhigh | 05:43 | 05:56 | 13 min | in lead total | done |
| 5 Screening run | lead (frozen CLI) | - | - | 05:56:28 | 05:57:40 | 1 min | in lead total | 11 run, 0 refused |
| 6 Recomputation | MemberAuditor-K5-FableXHigh | fable | xhigh | 05:58 | 06:08 | 10 min | 9,499,041 (Tasks 3 and 6) | no DISCREPANCY |
| 7 End checks, return | lead | opus | xhigh | 06:09 | 06:12 | 3 min | in lead total | done |
| Lead | lead | opus | xhigh | 05:02 | 06:09 | - | 29,123,108 | - |
| **Part 2 total** | lead + 4 agents | - | - | 05:02 | 06:12 | **70 min**, no pause | **60,082,643** | estimate 2 h; faster than guessed |

Tokens per model (Part 2):

| Model | Input | Output | Cache read | Cache creation | Total |
|---|---|---|---|---|---|
| claude-fable-5-1 | 934 | 1,817 | 8,644,509 | 851,781 | 9,499,041 |
| claude-opus-5-5 | 390 | 87,104 | 49,512,835 | 983,273 | 50,583,602 |
| all | 1,324 | 88,921 | 58,157,344 | 1,835,054 | 60,082,643 |

Per worker spawn: ReleaseChecker-OpusMed (worker-medium, opus, medium) 2,931,733; MemberCoder-A-OpusXHigh (worker-xhigh,
opus, xhigh) 9,750,683; MemberCoder-B-OpusXHigh (worker-xhigh, opus, xhigh) 8,778,078; MemberAuditor-K5-FableXHigh
(worker-xhigh, fable, xhigh; Tasks 3 and 6) 9,499,041. Delegation share: lead 29,123,108 (48.5%), workers 30,959,535
(51.5%). By model: opus 84.2%, fable 15.8%. Cache reads 96.8% of all tokens.
