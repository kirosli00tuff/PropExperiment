# Stage E.4 return, Part 1 (E.4a): harness v4 (C-1 fix, trip lists) and K4 energy coded, audited, frozen and screened

Lead: Opus 5.5 (xhigh). Session 2026-09-27, 01:54-05:02 PDT for Part 1, with two pauses (02:19-02:29, the user's pause
and a process restart; 03:00-04:11, the usage limit). Prompt: commit 0fb61f2. Parts 2 (K5, reports/E.4b_RETURN.md) and
3 (K3, reports/E.4c_RETURN.md) follow in the same session; the cross-cluster table goes at the end of this file when
all three are done.

## 1. Verdict summary

**Harness v4 committed (b20163a), manifest sha256 82ae8536738ca43395f43356840c0b799a7925b7b75ddb4fc1353d3ab7491009.**
C-1 is fixed (a `python -m` launch now runs the imported module, so all 21 `_runner()` refusals are caught by name) and
every member record gets a write-once trip list. The K2 replay through `python -m` matched E.3 on 44/44 records (only the
harness id and timestamp differ), 44/44 trip lists sum to their series, tiers unchanged. Fable review: 0 blocking, 0
should-fix, 9 notes.

**K4: 12 trials coded, Fable-audited (1 blocking, fixed by ruling R-T3-1), frozen (e0ccf63, cluster freeze
cf066cb0507134e2553781f42699165b471be45ebec6b07bfb0d75680e879d1a) and run once.** The Fable recomputation found no
discrepancy.

| Tier | Trial | Trips | Mean net ticks/contract/day | Daily t |
|---|---|---|---|---|
| A | K4-ngpre-01 NG | 50 | +3.2277 | 1.814 |
| B | the other 11 (section 3) | 12-275 | -7.5264 to +0.7996 | -1.649 to 0.347 |

Releases: WPSR 2025-12-29 and 2026-05-28 dropped, NGS 2025-12-29 dropped; three NGS releases unverifiable (kept), so
K4-ngpre-01 carries "calendar partly unverified". No member unimplementable or refused. **Program N = 102 + 12 = 114.**
K4's confirmation needs the step 2 purchase of MCL and NG ($11.46, inside acct-2's remaining $21.52, no top-up) and,
first, a C9 check of ngpre's storage dates.

## 2. Guardrail evidence

**Start checks, verbatim** (01:55; the suite 01:55:25-02:07:01), reports/stage_e4_briefs/start_checks.out:
```
$ git status --short
(empty apart from this session's reports/stage_e4_briefs/ just created)
$ git log --oneline -3
0fb61f2 docs: Stage E.4 extended to K5 and K3 in the same unattended run (V13 c)
64489ad docs: Stage E.4 prompt (harness fix C-1 and trip lists, K4 energy screening) and V13
9d36669 docs: Stage E.3 results, K2 screened, all 44 trials Tier B
$ wc -c REGISTRATION.md
0 REGISTRATION.md
$ uv run python -m data.holdout status (keys)
holdout_1 all_ok True unlocks_logged 0 unlock_log_ok True
holdout_2 all_ok True unlocks_logged 0 unlock_log_ok True
$ python3 reports/stage_e2b_briefs/check_frozen.py
reports/stage_e1_freeze.json: manifest sha256 96166eb39b85d4fdcf132092978ee85393392de52c3857dc3f64ea7281454a7c files 32/32 match
reports/stage_e2a_ml_freeze.json: manifest sha256 077a57e1c00554dd0745302b247673d45ee05b805ac4bfd876f8497f7bbb1ed2 files 4/4 match
OK (the eight E.2a tables) ... ALL_OK
$ PYTHONPYCACHEPREFIX=<fresh> uv run python -m screening.harness_freeze verify --expected cf939270f0a00be74aa29a43f0c7de964256411a9cdcebc36f22fd3bdc021a45
preflight OK: cf939270f0a00be74aa29a43f0c7de964256411a9cdcebc36f22fd3bdc021a45
$ cluster freezes (load_cluster_freeze + verify_cluster_code)
K2 cluster freeze OK 8815a775e74996419b57751b1104ffa07cd4b3450eb18a9a92c6cbbd5615b7c5 44 members
$ ledger
14823 ledger/databento_spend.jsonl
02e7caa257bbee7b84d23a0394c9fae34985e884c1306fb47ea683546f15b1ed
$ uv run pytest -q
3008 passed, 2 skipped, 1 xfailed, 54 warnings in 694.53s (0:11:34)
```
The suite equals E.3's end result. It ran without PYTHONPYCACHEPREFIX, as E.3 established (three bytecode tests fail
with it set); every Stage E entry point ran with a fresh prefix.

**End checks for Part 1, verbatim** (04:55:55), reports/stage_e4_briefs/end_checks_part1.out:
```
$ git log --oneline -3
e0ccf63 feat: K4 member freeze (Stage E.4 Part 1), cluster freeze sha256 cf066cb0
b20163a feat: harness v4 (Stage E.4 H4), C-1 fix and per-trial trip lists
0fb61f2 docs: Stage E.4 extended to K5 and K3 in the same unattended run (V13 c)
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
$ ... verify --expected cf939270... (04:12, after the v4 commit)
Stage E harness preflight refused: reports/stage_e2b_harness_freeze.json sha256 82ae8536738c... is not the expected cf939270f0a0...
$ cluster freezes (load_cluster_freeze + verify_cluster_code)
K2 cluster freeze OK 8815a775e74996419b57751b1104ffa07cd4b3450eb18a9a92c6cbbd5615b7c5 44 members
K4 cluster freeze OK cf066cb0507134e2553781f42699165b471be45ebec6b07bfb0d75680e879d1a 12 members
$ ledger
14823 ledger/databento_spend.jsonl
02e7caa257bbee7b84d23a0394c9fae34985e884c1306fb47ea683546f15b1ed
$ uv run pytest -q   (04:33:11-04:43:19, on the tree committed as e0ccf63; no code or test changed after it)
3256 passed, 2 skipped, 1 xfailed, 54 warnings in 606.19s (0:10:06)
$ git status --short
 M reports/stage_e4_member_audit.md
?? reports/stage_e4_STATE.md
?? reports/stage_e4_briefs/
?? reports/stage_e4_coder_A.md
?? reports/stage_e4_coder_B.md
?? reports/stage_e4_harness_fix.md
?? reports/stage_e4_k2_regression/
?? reports/stage_e4_k4_screen/
$ git diff --stat
 reports/stage_e4_member_audit.md | 140 +++++++++++++++++++++++++++++++++++++++
 1 file changed, 140 insertions(+)
```
Ledger: 14,823 lines at start and end, same sha256; `git diff --stat -- ledger/` empty. No spend, no quote. No TopstepX
reference or credential. No edit under live/ or ops/, to docs/NULL_CRITERIA.md, reports/stage_d1f_confirmation_list.md,
any E.3 record or any frozen file other than the harness files Task H1 names and the manifest Task H4 rebuilt. Bars were
read only by the runner (the K2 replay and the K4 run, research window only). No session script opened a bar file. The
web was used only by Task 1b (read-only public schedule and archive pages).

## 3. Results per task

### Task 0: startup
Start checks passed at 01:55; HEAD 0fb61f2, tree clean; preflight accepted cf939270. Suite 3008 passed (= E.3's end).

### Task H1: the harness fix (HarnessFixer-OpusXHigh; reports/stage_e4_harness_fix.md)
- Shape: the preferred one. The runner's `if __name__ == "__main__":` block imports screening.stage_e_runner and calls
  its main(); the `__main__` copy only defines names. screening/stage_e_start_dates.py unchanged.
- Trip list: `write_member_record` writes the record exactly as before, hashes the written bytes, then writes
  `<record>_trips.json` (write-once) with schema stage_e_member_trips/1: record file and sha256, cluster, member, window,
  status, and every trip (root, open/close ns and ISO UTC, trade date, contracts, gross_cents from the same Fill events,
  net_cents, close_reason, locked, hold_minutes); cents exact (int, or "p/q" with a float beside).
- Diff: screening/stage_e_runner.py +90/-6, tests/test_stage_e_runner.py +123; new tests/_stage_e_launch.py (330 lines)
  and tests/test_stage_e_runner_launch.py (122 lines). Both new files are hashed by the manifest.
- Tests: a real `python -m` subprocess launch over 22 synthetic refusal cases (RED against the pre-fix runner: the
  escaped StartRuleMissing; GREEN after), trip sums against the daily series, write-once and sha256 binding. Suite (worker)
  3019 passed, 2 skipped, 1 deselected (the manifest test, which must fail until the lead rebuilds), 1 xfailed.

### Task H2: K2 regression replay (lead; reports/stage_e4_k2_regression.md)
The preflight has no test mode, so the lead rebuilt the manifest in place, uncommitted (02:30; sha256 82ae8536...; vs
cf939270 only the 2 changed and 2 added files, nothing removed), and ran the E.3 command through `python -m`
(02:31:16-02:37:02, exit 0, `K2 research: 44 members, 0 refused`) into reports/stage_e4_k2_regression/.

| Check | Result |
|---|---|
| 44 records vs E.3, every field (only harness_sha256, created_utc skipped) | 44/44 MATCH |
| trip lists: exact per-date sums = daily_net_usd, count = n_trips, record sha256 | 44/44 |
| cluster record (tiers, members, refusals) | MATCH; all 44 Tier B |
| power under `python -m` | not_run (StartRuleMissing) on 44/44, recorded by name |

### Task H3 and H4: review, rulings, manifest v4, commit
Review 0/0/9, all six checks pass (section 5). Rulings: no code change (reports/stage_e4_harness_rulings.md). The
in-place manifest of 02:30 is v4 (never rebuilt, so the regression ran under exactly v4). Gate suite 02:50-03:00:
3020 passed, 2 skipped, 1 xfailed (K4 member tests, untracked, left out). Commit b20163a (8 files: runner, 3 test files,
manifest, review, rulings, regression report).

### Task 1: member specifications (lead; reports/stage_e4_member_specs.md)
Eight members, 12 trials, every field with a catalog or design line reference, an E.3 precedent or a logged reading.
Ordinals: cp1 MCL 1, NG 2; cp2 MCL 3, NG 4; cp3 MCL 5, NG 6; ngpre NG 7; apipre MCL 8; eiafade MCL 9; eiamom MCL 10; ovr
MCL 11, NG 12. MCL q_c 4, NG q_c 1; O/C (08:00, 13:30); CP2 buffer 0.04 / 0.004 (R-07). E.3 readings adopted: L-01,
L-03..L-13, L-17, L-19, L-22. New readings K4-L-01..K4-L-15 (section 6). Catalog section 7 items settled as the prompt
says (items 1-2 moot; 3 D6 as written; 4 one trial each; 5 reported below as ngpre's cost limitation; 10 (a)-(c) Task 1b,
(f) the runner's coverage).

### Task 1b: research-window release check (ReleaseChecker-OpusMed; reports/stage_e4_release_check.md, .json)
| Release | Rows | Keep | Dropped | Unverifiable (kept) |
|---|---|---|---|---|
| WPSR | 64 | 62 | 2: 2025-12-29 (EIA delay notice; schedule said Monday 10:30), 2026-05-28 (capture 37 min after the slot shows the prior week) | 0 |
| NGS | 64 | 60 | 1: 2025-12-29 ("(Updated)" row first captured after the release) | 3: 2025-05-01, 2025-05-29, 2025-06-18 |

EIA states no WPSR clock time (all WPSR times from the schedule); 61 of 64 NGS times are stated on captures of EIA's
weekly page. API: 56 standard weeks, no federal-holiday Monday, every API row on its Tuesday; no week dropped. NYSE: 69
full closures and 15 early closes 2019-05..2026-06 (research window 13 and 3). Federal Monday holidays: 46 distinct dates.
The checker also dropped 2025-07-16; the audit showed its evidence was a mis-attributed capture and ruling R-T3-1
restored it (section 5). Pre-window rows (2019-05..2025-03) are kept unchecked (K4-L-01).

### Task 2: the modules and their tests
strategy/members/k4/: cp1, cp2, cp3, ovr, _calendar (ENERGY_FULL_SESSIONS, 1,784 dates) and _port_common
(MemberCoder-A-OpusXHigh; tests/test_e4_k4_members_a.py and _a_ovr.py, 181 passed with the freeze and template tests);
ngpre, apipre, eiafade, eiamom, _releases (WPSR 369 rows, NGS 372, drops, API, holidays, NYSE) and _event_common
(MemberCoder-B-OpusXHigh; tests/test_e4_k4_members_b.py and _b_eia.py, 149 passed). Every file passes the freeze's static
check. Gate suite 04:12-04:22: 3256 passed, 2 skipped, 1 xfailed.

### Task 3: fidelity audit (MemberAuditor-K4-FableXHigh; reports/stage_e4_member_audit.md Part 1)
1 BLOCKING (B-1), 0 SHOULD FIX, 9 NOTE. All 12 trials implement their frozen entries and nothing more; the ports equal
E.3's K2 ports in rule body; every table recomputed from its sources is equal; 236 tests pass; 31 literal mutants killed.

### Task 4: rulings, the cluster freeze and the commit
R-T3-1 (B-1) and the notes: reports/stage_e4_member_rulings.md. Freeze written 04:33, verified; suite 04:33-04:43 3256
passed; commit e0ccf63 (23 files: 13 member files, 4 test files, specs, release check .json/.md, audit Part 1, rulings,
freeze).

### Task 5: the screening run
Command (frozen, under v4): `PYTHONPYCACHEPREFIX=<fresh> nice -n 10 uv run python -m screening.stage_e_runner
--harness-sha256 82ae8536... --cluster K4 --all --window research --research-root data/processed --step2-root
data/processed_step2 --out-dir reports/stage_e4_k4_screen`, 04:43:41-04:45:08, exit 0, `K4 research: 12 members, 0
refused`. 25 files (12 records, 12 trip lists, the cluster record). Window: 270 trade dates on MCL, 269 on NG, after
roll blackouts and UR-1. Coverage 0.9921-0.9999 (all above 0.95). No floor label. Power `not_run` for all 12
(StartRuleMissing: no start-rule file before the step 2 purchase), by design.

### The screen per trial (from the runner's files; eps MCL 21, NG 8 ticks)

| Ord | Trial | Trips | Mean ticks | Daily t | Screen | Coverage | Labels | MLL liquidations | Tier |
|---|---|---|---|---|---|---|---|---|---|
| 1 | K4-cp1-01 MCL | 258 | +0.7996 | 0.347 | fail | 0.9963 | none | 1 | B |
| 2 | K4-cp1-01 NG | 257 | -1.3700 | -1.011 | fail | 0.9992 | none | 3 | B |
| 3 | K4-cp2-01 MCL | 269 | -7.5264 | -1.649 | fail | 0.9961 | none | 8 | B |
| 4 | K4-cp2-01 NG | 268 | -2.4909 | -0.976 | fail | 0.9981 | none | 8 | B |
| 5 | K4-cp3-01 MCL | 105 | -0.6230 | -0.130 | fail | 0.9985 | none | 3 | B |
| 6 | K4-cp3-01 NG | 114 | -4.4076 | -1.126 | fail | 0.9992 | none | 10 | B |
| 7 | K4-ngpre-01 NG | 50 | +3.2277 | 1.814 | pass | 0.9999 | none (calendar partly unverified) | 0 | **A** |
| 8 | K4-apipre-01 MCL | 46 | -1.2124 | -0.592 | fail | 0.9994 | none | 1 | B |
| 9 | K4-eiafade-01 MCL | 12 | +0.2701 | 0.226 | fail | 0.9980 | none | 0 | B |
| 10 | K4-eiamom-01 MCL | 48 | -0.5351 | -1.155 | fail | 0.9921 | none | 0 | B |
| 11 | K4-ovr-01 MCL | 275 | -1.8383 | -0.500 | fail | 0.9981 | none | 3 | B |
| 12 | K4-ovr-01 NG | 252 | -1.9921 | -1.024 | fail | 0.9992 | none | 5 | B |

MLL liquidations = accounts_started - 1 (42 in all). The engine's D9.5a guard moved 34 fills to release + 2 minutes
(CP1's 13:00 entries on FOMC days, CP2 exits at 09:32, ngpre's 09:30 entries on the three Wednesday 12:00 ET storage days,
ovr entries at 11:02 or 13:02). One forced flatten (cp2 MCL, 2025-09-01, Labor Day early halt).

### Task 7: reading the result
- K4 enters the program with a non-empty Tier A: K4-ngpre-01 NG, so K4 counts in D5's K, and its confirmation Holm family
  is that one trial. Its research mean (3.23 ticks a day) is below NG's eps (8 ticks); the screen asks only mean > 0 and
  t >= 1.0, and the confirmation test is against eps. The source (P-K4-001-e) expected no effect after 2011. It carries
  "calendar partly unverified" (three kept NGS dates) and NG's Thursday cost-sample limitation (C12; the frozen D8 bucket
  holds no storage release).
- The eleven others fail. Every port but cp1 MCL loses; ovr loses on both. eiafade trades 12 times in 270 dates, so its
  daily mean sits near zero, as C11's arithmetic said.
- Program N after Part 1: 102 + 12 = 114 (58 in D5 line 317, plus E.3's 44, plus these 12). The runner does not count N.
- K4's confirmation session needs: Tier A K4-ngpre-01 NG; Tier B the 11 others (section 0 ordinals); the step 2 purchase
  for MCL and NG, $11.46 (reports/stage_e2b_step2_quotes.md), inside acct-2's remaining $21.52, so no top-up; then the
  start-rule build and D4's power check before the list is hashed. Before ngpre runs, its storage dates must pass C9: the
  three unverifiable research-window dates and every confirmation-window row (K4-L-01).

## 4. Delegation record

| Agent | Worker file | Model | Effort | Objective | Status and deviations |
|---|---|---|---|---|---|
| HarnessFixer-OpusXHigh | worker-xhigh | opus | xhigh | H1: C-1 fix, trip list, tests, suite | done 02:01-02:37; interrupted by the process restart, resumed by SendMessage to finish its suite and report |
| ReleaseChecker-OpusMed | worker-medium | opus | medium | 1b: WPSR/NGS/API/NYSE checks | done 02:01-02:42; scope extended by SendMessage 02:12 (NYSE and federal Monday holidays back to 2019-05); interrupted and resumed; its prose summary called two of its three WPSR drops "keep", its JSON said drop (the JSON governed); one drop reversed on audit (R-T3-1) |
| MemberCoder-A-OpusXHigh | worker-xhigh | opus | xhigh | cp1, cp2, cp3, ovr, _calendar | done 02:12-02:34; interrupted and resumed; two questions ruled (K4-L-13 trim, K4-L-14 confirmed), one follow-up |
| HarnessReviewer-FableXHigh | worker-xhigh | fable | xhigh | H3 review | done 02:37-02:49; 0/0/9 |
| MemberCoder-B-OpusXHigh | worker-xhigh | opus | xhigh | ngpre, apipre, eiafade, eiamom, _releases | done 02:43-03:00; resumed 04:31-04:32 to apply R-T3-1 |
| MemberAuditor-K4-FableXHigh | worker-xhigh | fable | xhigh | Task 3 audit; Task 6 recomputation (resumed) | done 04:12-04:30 and 04:47-04:55 |

## 5. Verification

**Harness (HarnessReviewer-FableXHigh, reports/stage_e4_harness_review.md).** Checks: scope PASS (only routing and the
trip file; stage_e_start_dates.py byte-identical); C-1 PASS (21 raise sites; identity under `python -m`, import, runpy,
and compute/agent.py's `-m` launch); trip list PASS (4,457 trips checked, inside the window); regression PASS (44/44
byte-identical after masking, recomputed in its own code); tests PASS (RED reproduced against HEAD's runner: 3 failed, 4
passed); manifest PASS (4 entries, 2 category rows, header). Notes N-1..N-9 and rulings: reports/stage_e4_harness_rulings.md
(no change; N-2 adds a note to the fix report; N-9: v4 is the in-place manifest the regression ran under).

**K4 fidelity audit (Part 1 of reports/stage_e4_member_audit.md).**

| Finding | Ruling | Fix |
|---|---|---|
| B-1 (BLOCKING): DROPPED_WPSR 2025-07-16 rests on a capture that Wayback served from 2025-07-15; the real 07-16 12:04 ET capture shows the release | R-T3-1: restored (keep) | release-check JSON row amended (original under `lead_ruling`), .md, specs section 11 and K4-L-15; MemberCoder-B regenerated _releases.py and updated its tests; no member module changed; the auditor's own table script then reported every table EQUAL |
| N-1 NGS path label | documentation only | none |
| N-2 D9.5a moves ngpre's 09:30 fills on three Wednesdays | harness behaviour, listed here | specs section 0 note |
| N-3 D9.7 tests use a test-only rules class (MCL, NG have no hard limit) | adequate | none |
| N-4 cp2's refused-exit resend untested | unreachable in practice | none |
| N-5 ovr's coverage-window literal | cosmetic | none |
| N-6 apipre's Tuesday minutes measured on every date | K4-L-07 | none |
| N-7 ovr's energy-specific content is only the clock and calendar | confirms F-7 | K5 checks its twin |
| N-8 pre-window rows unchecked | K4-L-01 | confirmation session checks them |
| N-9 three unverifiable NGS rows kept | C9's letter | label on ngpre |

**K4 recomputation (Part 2).** Item 0 VERIFIED (the frozen _releases.py differs from the audited one only by the R-T3-1
row; every other file equals the audited hash); 1 VERIFIED (12 screens to 1e-9); 2 VERIFIED (Tier A ngpre NG only; D5);
3 VERIFIED (1,954 trips rebuilt from the frozen cost table with the event-window rule, 0 net mismatches, both series match
day by day; gross cannot be checked without prices); 4 VERIFIED WITH NOTES (every untraded event explained except 45
silent no-trades: apipre 3, eiafade 41, eiamom 1, where the rule's own condition (R_API = 0, |M| < 0.5 %, r3 = 0) cannot be
told from a missing bar in the records; 1,870 fills exact, 34 D9.5a, 42 MLL, 1 flatten, 7 one or two minutes late with
no release nearby; ovr at most 4 entries a day, no overlap); 5 VERIFIED (N = 114); 6 VERIFIED (42 MLL liquidations, none
on the Tier A trial; no tier flips when they are zeroed or dropped). No DISCREPANCY, so no tier is "unverified".

## 6. Open choices (each decided by the lead alone, with the reason; each can be overturned)

- **H2's scratch manifest was the working-tree manifest, rebuilt in place, uncommitted.** The preflight has no test mode
  and test_the_real_tree_matches_the_committed_manifest_when_it_exists needs the working-tree manifest to match the tree.
  A separate worktree would have needed its own environment and symlinked data. The committed manifest stayed cf939270
  until H4; the in-place build (82ae8536) became v4 unchanged.
- **Task 1b's scope was extended back to 2019-05 for NYSE closures and federal Monday holidays.** The member code is frozen
  once and reused on the confirmation window; without the lists, eiamom and apipre would trade 2019-2024 NYSE early
  closes and holiday weeks. No verdicts on 2019-2025 WPSR or NGS rows (out of scope).
- **K4-L-01** tables span 2019-05..2026-06; C9's drops apply to the research window only. **K4-L-02** T = the calendar
  instant in CT. **K4-L-03** ngpre and eiafade trade the table rows on dates without an early halt. **K4-L-04** apipre's
  standard week uses the timing rule, not the API rows. **K4-L-05** percent returns from integer ticks; eiafade's threshold
  compared exactly (200 x (t14 - t0) against t0); ovr's percentile with numpy on floats. **K4-L-06** CP2's buffer as 4 x
  vendor_tick (= R-07's literals). **K4-L-07** apipre's Tuesday coverage minutes declared at offset 0. **K4-L-08** ovr's 20
  reference dates from EC-CAL, missing bars reduce the count. **K4-L-09** ovr's warm-up = the first 20 eligible dates of the
  window. **K4-L-10** ovr's P10 = P90 = r tie: no trade. **K4-L-11** 12 declarations, catalog order, crude before gas.
  **K4-L-12** two coders, four test files. **K4-L-13** ENERGY_FULL_SESSIONS trimmed to EC-CAL's coverage (coder A's
  question). **K4-L-14** ovr's instrument check per computation (coder A's question; the entry's own text).
  **K4-L-15** the 2026-05-28 WPSR drop applied as the checker recorded it. **Flagged for the user:** no EIA delay notice
  was captured for that date and a cached page cannot be ruled out; the effect is one Thursday release fewer for eiafade.
- **R-T3-1** WPSR 2025-07-16 restored on the audit's evidence; the release-check JSON was amended in place with the
  original verdict kept under `lead_ruling`, rather than written as a second file, so the frozen table has one source.
- The harness notes N-1..N-9: no change. N-4 (an empty test fragment) was left, because editing a manifest-hashed test
  after the regression would have changed v4 from the manifest the regression ran under.
- The H4 gate suite left out the untracked K4 member tests (then being written); the commit held only harness files.
  The full suite with them ran in Task 2's gate and Task 4.
- Task 3 (the audit) started at 04:12 while Task 2's gate suite was running, as in E.3; the audited files were unchanged
  after the gate (hash check at 04:31).
- The one-off table generators and the lead's scripts stay uncommitted under reports/stage_e4_briefs/, as in E.3.
  Uncommitted by design: the fix report, the coder reports, the regression records, the K4 screen records, the audit's
  Part 2, the STATE file and the briefs.
- Program N is computed as 102 + 12 = 114 by the lead; the runner does not count N.
- Part 1's end suite is the Task 4 suite (04:33-04:43) on the tree committed as e0ccf63; no code or test changed after it.
  The session's final end suite runs after Part 3.

## 7. What the next session must do first

- **Push (the planning chat).** Commits b20163a (harness v4) and e0ccf63 (K4 freeze) are local and unpushed. Parts 2 and 3
  add two more freeze commits in this session. Uncommitted for review: this file, reports/stage_e4_STATE.md,
  reports/stage_e4_harness_fix.md, reports/stage_e4_coder_A.md and _B.md, Part 2 of reports/stage_e4_member_audit.md,
  reports/stage_e4_k2_regression/ (89 scratch files), reports/stage_e4_k4_screen/ (25 runner files),
  reports/stage_e4_briefs/, progress.md and docs/STAGES.md.
- **Frozen hashes.** Harness v4 82ae8536738ca43395f43356840c0b799a7925b7b75ddb4fc1353d3ab7491009 (every Stage E command
  now takes it; cf939270 is refused). K4 cluster freeze reports/stage_e_k4_member_freeze.json,
  cf066cb0507134e2553781f42699165b471be45ebec6b07bfb0d75680e879d1a. K2 cluster freeze 8815a775... E.1 96166eb3...,
  E.2a ML 077a57e1..., release calendar 839f2437... (all unchanged). A purchase session that edits data/config.py writes
  the manifest after v4 (V13 (a)).
- **Funding for K4's confirmation.** MCL and NG step 2 history $11.46 (reports/stage_e2b_step2_quotes.md); acct-2 holds
  $21.52 of its cap, so no top-up.
- **Before K4-ngpre-01 NG's confirmation run:** C9's checks on its storage dates: the three unverifiable research-window
  dates (2025-05-01, 05-29, 06-18) and every confirmation-window NGS row (K4-L-01). If a confirmation-window date drops,
  the frozen table would need an amendment, which is the user's decision.
- **Questions for the user:** K4-L-15 (2026-05-28 dropped on a capture, no captured notice); whether the runner should
  count a member's silent no-trades in a later harness version (Task 6 note); the E.3 questions still open (L-23, OC-Q, the
  power-check-undefined case).

## 8. Session cost (Part 1)

Wall clock 01:54-05:02 PDT (188 min). Pauses, not work: 02:19-02:29 (10 min, the user's pause and the process restart)
and 03:00-04:11 (71 min, the usage limit). Work time 107 min. Tokens are summed from this session's transcript
(17ffffc1-5761-44c4-9f3b-5ee8c14fb08c.jsonl, which spans the restart) and its six subagent transcripts, once per message
id, over 01:50-05:02 PDT (reports/stage_e4_briefs/cost.py). The lead's tokens after 05:02 (progress.md, STAGES.md) fall in
Part 2's slice.

Final ETA table (initial estimate: Part 1 ending about 05:00, 3 h 06 min of work):

| Task / spawn | Owner | Model | Effort | Start | End | Time | Tokens | Status and deviations |
|---|---|---|---|---|---|---|---|---|
| 0 Startup checks, start suite | lead | opus | xhigh | 01:54 | 02:07 | 13 min | in lead total | done; 3008 passed |
| 1 Member specs (s.11 at 02:43-02:50) | lead | opus | xhigh | 02:01 | 02:12 | 11 min (+7) | in lead total | done |
| H1 Harness fix | HarnessFixer-OpusXHigh | opus | xhigh | 02:01 | 02:37 | 36 min (incl. restart) | 17,643,028 | done; resumed once |
| 1b Release check | ReleaseChecker-OpusMed | opus | medium | 02:01 | 02:42 | 41 min (incl. restart) | 17,623,970 | done; scope extended; one drop reversed later |
| 2 Coder A | MemberCoder-A-OpusXHigh | opus | xhigh | 02:12 | 02:34 | 22 min | 13,950,078 | done; 181 passed |
| Pause (user, restart) | - | - | - | 02:19 | 02:29 | 10 min | - | not work |
| H2 K2 regression | lead | - | - | 02:30 | 02:37 | 7 min | in lead total | done; 44/44 |
| H3 Harness review | HarnessReviewer-FableXHigh | fable | xhigh | 02:37 | 02:49 | 12 min | 2,089,180 | done; 0/0/9 |
| 2 Coder B | MemberCoder-B-OpusXHigh | opus | xhigh | 02:43 | 03:00 | 17 min (+1 at 04:31) | 14,477,003 | done; 149 passed; R-T3-1 applied |
| H4 rulings, gate suite, commit b20163a | lead | opus | xhigh | 02:50 | 04:13 | 12 min of work | in lead total | done; 3020 passed |
| Pause (usage limit) | - | - | - | 03:00 | 04:11 | 71 min | - | not work |
| 2 gate suite | lead | - | - | 04:12 | 04:22 | 10 min | in lead total | 3256 passed |
| 3 Fidelity audit | MemberAuditor-K4-FableXHigh | fable | xhigh | 04:12 | 04:30 | 18 min | in the auditor total | done; 1 BLOCKING |
| 4 Rulings R-T3-1, freeze, suite, commit e0ccf63 | lead | opus | xhigh | 04:30 | 04:44 | 14 min | in lead total | done |
| 5 Screening run | lead (frozen CLI) | - | - | 04:43:41 | 04:45:08 | 1.5 min | in lead total | done; 12 run, 0 refused |
| 6 Recomputation | MemberAuditor-K4-FableXHigh | fable | xhigh | 04:47 | 04:55 | 8 min | 9,778,746 (Tasks 3 and 6) | done; no DISCREPANCY |
| 7 End checks, return | lead | opus | xhigh | 04:55 | 05:02 | 7 min | in lead total | done |
| Lead (all lead rows) | lead | opus | xhigh | 01:54 | 05:02 | - | 59,375,556 | - |
| **Part 1 total** | lead + 6 agents | - | - | 01:54 | 05:02 | **107 min of work**, 81 min paused | **134,937,561** | estimate 3 h 06 min; the harness track and the coders ran faster than guessed |

Tokens per model (Part 1):

| Model | Input | Output | Cache read | Cache creation | Total |
|---|---|---|---|---|---|
| claude-fable-5-1 | 1,416 | 11,735 | 10,783,547 | 1,071,228 | 11,867,926 |
| claude-opus-5-5 | 1,098 | 262,844 | 119,597,545 | 3,208,148 | 123,069,635 |
| all | 2,514 | 274,579 | 130,381,092 | 4,279,376 | 134,937,561 |

Per worker spawn: HarnessFixer-OpusXHigh (worker-xhigh, opus, xhigh) 17,643,028; ReleaseChecker-OpusMed (worker-medium,
opus, medium) 17,623,970; MemberCoder-A-OpusXHigh (worker-xhigh, opus, xhigh) 13,950,078; HarnessReviewer-FableXHigh
(worker-xhigh, fable, xhigh) 2,089,180; MemberCoder-B-OpusXHigh (worker-xhigh, opus, xhigh) 14,477,003;
MemberAuditor-K4-FableXHigh (worker-xhigh, fable, xhigh; Tasks 3 and 6) 9,778,746.

Delegation share: lead 59,375,556 (44.0%), workers 75,562,005 (56.0%). By model: opus 91.2%, fable 8.8%. Cache reads are
96.6% of all tokens.

## Final section (after all three parts): every trial of the session with its tier

From the runners' own files (reports/stage_e4_k4_screen/, reports/stage_e4b_k5_screen/, reports/stage_e4c_k3_screen/), each
recomputed by its cluster's Fable auditor with no discrepancy. Mean in net ticks per contract per day with zeros on no-trade
days; t is D5's daily t. "excluded" follows OC-H (coverage below 0.95: not screened; a D9 floor label: screened, then
excluded before confirmation).

| Cluster | Ord | Trial | Status | Trips | Mean ticks | Daily t | Tier |
|---|---|---|---|---|---|---|---|
| K4 | 1 | K4-cp1-01 MCL | run | 258 | +0.7996 | 0.347 | B |
| K4 | 2 | K4-cp1-01 NG | run | 257 | -1.3700 | -1.011 | B |
| K4 | 3 | K4-cp2-01 MCL | run | 269 | -7.5264 | -1.649 | B |
| K4 | 4 | K4-cp2-01 NG | run | 268 | -2.4909 | -0.976 | B |
| K4 | 5 | K4-cp3-01 MCL | run | 105 | -0.6230 | -0.130 | B |
| K4 | 6 | K4-cp3-01 NG | run | 114 | -4.4076 | -1.126 | B |
| K4 | 7 | K4-ngpre-01 NG | run | 50 | +3.2277 | 1.814 | **A** |
| K4 | 8 | K4-apipre-01 MCL | run | 46 | -1.2124 | -0.592 | B |
| K4 | 9 | K4-eiafade-01 MCL | run | 12 | +0.2701 | 0.226 | B |
| K4 | 10 | K4-eiamom-01 MCL | run | 48 | -0.5351 | -1.155 | B |
| K4 | 11 | K4-ovr-01 MCL | run | 275 | -1.8383 | -0.500 | B |
| K4 | 12 | K4-ovr-01 NG | run | 252 | -1.9921 | -1.024 | B |
| K5 | 1 | K5-cp1-01 MGC | run | 284 | -0.6037 | -0.131 | B |
| K5 | 2 | K5-cp1-01 MHG | excluded_before_screening (coverage_below_0.95) | - | - | - | excluded |
| K5 | 3 | K5-cp2-01 MGC | run | 295 | +10.5570 | 0.906 | B |
| K5 | 4 | K5-cp2-01 MHG | excluded_before_screening (coverage_below_0.95) | - | - | - | excluded |
| K5 | 5 | K5-cp3-01 MGC | run | 101 | +8.4945 | 0.793 | B |
| K5 | 6 | K5-cp3-01 MHG | run | 126 | +3.2468 | 0.695 | B |
| K5 | 7 | K5-preauc-01 MGC | run | 280 | +1.3052 | 0.358 | B |
| K5 | 8 | K5-pmfix-01 MGC | run (mean_holding_below_10min) | 278 | -9.9896 | -2.194 | excluded |
| K5 | 9 | K5-fomc-01 MGC | run | 8 | +2.3498 | 1.846 | **A** |
| K5 | 10 | K5-ovr-01 MGC | run | 289 | -3.5608 | -0.330 | B |
| K5 | 11 | K5-ovr-01 MHG | run | 190 | -3.3977 | -1.201 | B |
| K3 | 1 | K3-cp1-01 6E | run | 284 | +0.3293 | 0.323 | B |
| K3 | 2 | K3-cp1-01 6A | run | 282 | -2.0719 | -3.049 | B |
| K3 | 3 | K3-cp1-01 6B | run | 264 | -1.1619 | -2.161 | B |
| K3 | 4 | K3-cp1-01 6C | run | 276 | -2.1081 | -5.532 | B |
| K3 | 5 | K3-cp1-01 6J | run | 275 | -0.8693 | -1.446 | B |
| K3 | 6 | K3-cp1-01 6S | excluded_before_screening (coverage_below_0.95) | - | - | - | excluded |
| K3 | 7 | K3-cp1-01 6N | excluded_before_screening (coverage_below_0.95) | - | - | - | excluded |
| K3 | 8 | K3-cp2-01 6E | run | 294 | -3.1634 | -1.785 | B |
| K3 | 9 | K3-cp2-01 6A | run | 295 | -3.5044 | -2.494 | B |
| K3 | 10 | K3-cp2-01 6B | run | 296 | -2.2412 | -2.163 | B |
| K3 | 11 | K3-cp2-01 6C | run | 293 | -1.7082 | -1.831 | B |
| K3 | 12 | K3-cp2-01 6J | run | 291 | -2.4092 | -1.821 | B |
| K3 | 13 | K3-cp2-01 6S | run | 293 | -4.3509 | -1.873 | B |
| K3 | 14 | K3-cp2-01 6N | excluded_before_screening (coverage_below_0.95) | - | - | - | excluded |
| K3 | 15 | K3-cp3-01 6E | run | 112 | -1.8603 | -0.769 | B |
| K3 | 16 | K3-cp3-01 6A | run | 130 | -2.0385 | -0.900 | B |
| K3 | 17 | K3-cp3-01 6B | run | 123 | -0.9169 | -0.597 | B |
| K3 | 18 | K3-cp3-01 6C | run | 118 | -2.6732 | -2.244 | B |
| K3 | 19 | K3-cp3-01 6J | run | 140 | -3.4127 | -1.580 | B |
| K3 | 20 | K3-cp3-01 6S | run | 138 | -2.4593 | -0.650 | B |
| K3 | 21 | K3-cp3-01 6N | run | 138 | -1.6073 | -0.928 | B |
| K3 | 22 | K3-ldnrev-01 6E | run | 12 | +0.2842 | 1.422 | **A** |
| K3 | 23 | K3-ldnrev-01 6J | run | 13 | +0.0823 | 0.770 | B |
| K3 | 24 | K3-ldnrev-01 6S | run | 13 | +0.0541 | 0.190 | B |
| K3 | 25 | K3-ldnmom-01 6E | run | 254 | -0.7346 | -0.793 | B |
| K3 | 26 | K3-ldnmom-01 6J | run | 237 | -1.8592 | -3.096 | B |
| K3 | 27 | K3-mehedge-01 6J | run | 13 | -0.3457 | -1.574 | B |
| K3 | 28 | K3-ecbfix-01 6E | run | 561 | -2.8103 | -0.553 | B |
| K3 | 29 | K3-tkypre-01 6J | run | 52 | -0.4358 | -0.832 | B |
| K3 | 30 | K3-tkypost-01 6J | run | 269 | -1.8946 | -1.176 | B |

| Cluster | Declared | Screened | Tier A | Tier B | Excluded |
|---|---|---|---|---|---|
| K4 | 12 | 12 | 1 | 11 | 0 |
| K5 | 11 | 9 | 1 | 7 | 3 |
| K3 | 30 | 27 | 1 | 26 | 3 |

**Program N after the session: 150** = 102 (after E.3) + 12 (K4) + 9 (K5) + 27 (K3). N counts screened trials: the five
coverage-excluded trials (K5 2, K3 3) were never screened, and K3-mehedge-01 on EUR was never declared (no free index history);
K5-pmfix-01 MGC was screened and then excluded before confirmation, so it counts.

Tier A after the session, one trial in each of K4, K5 and K3, so K (D5: the clusters with a non-empty Tier A) gains three:
K4-ngpre-01 NG (t 1.814), K5-fomc-01 MGC (t 1.846), K3-ldnrev-01 6E (t 1.422). K2's Tier A is empty (E.3). Each Tier A
trial's research mean is well below its exposure's eps (NG 8, MGC 85, 6E 13 ticks), and two are low-frequency event members
(8 and 12 trades in the window), so D4's power check in each confirmation session decides whether the test can be run.

Session totals (all three parts): commits b20163a, e0ccf63, 09f1999, c5dfd5c; 53 trials declared, 48 screened, 3 Tier A;
nothing bought; both holdouts sealed with 0 unlocks. Cost: each part's section 8 (Part 3's also gives the session total).
