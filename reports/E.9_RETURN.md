# Stage E.9 return: K8 cross-market coded, audited, frozen and screened on the research window (no purchase)

Lead: Opus 5.5 xhigh, session 20d17daf-bbde-4768-93fa-814f35cbb398, 2026-10-01 22:12 to 2026-10-02 00:42 PDT (times
PDT), with one pause 00:04-00:23 (the session exited by accident and was resumed; section 8). Prompt:
docs/prompts/STAGE_E.9.md (commit 0d255d6). STATE: reports/stage_e9_STATE.md.

## 1. Verdict summary

Four K8 trials (three members) coded, Fable-audited (0 blocking, 0 should-fix, 8 notes), **frozen in commit 558a5dc
(cluster freeze 99f5a6ce4f91fd63ae4a7dc91b5eb39ecbf8a7eac6f210b3472bf49eaf8463b7)** and run once: 4 run, 0 refused, none
unimplementable. The Fable recomputation found no discrepancy.

| Tier | Trial | Trips | Mean net ticks/day | Daily t |
|---|---|---|---|---|
| A | K8-flight-01 HEOD MGC | 55 | +10.676 | 1.395 |
| A | K8-wkndbtc-01 MNQ | 39 | +28.975 | 1.072 |
| B | K8-flight-01 H30 MGC | 55 | +4.270 | 0.976 |
| B | K8-oilcad-01 6C | 552 | -4.454 | -5.907 |

Both passes are thin: wkndbtc's t is 0.781 without 2026-06-08, its only post-24/7 trade; HEOD's is 1.085 without its
best day, 0.751 without two. All event items kept; none unverifiable. **Program N = 194 + 4 = 198.** A K8 confirmation
needs 6C, MNQ and MBT step 2 ($17.75 of the $29.65 quote; MGC and MCL bought in E.5) and an acct-2 top-up of about
$17.42 ($19.20 with 10%); acct-2 holds $0.33.

## 2. Guardrail evidence

**Start checks** (reports/stage_e9_briefs/start_checks.out, verbatim):

```
$ date
Thu Oct  1 10:13:05 PM PDT 2026
$ git status --short
?? reports/stage_e9_briefs/
$ git log --oneline -3
9770828 chore: pin the sonnet alias to Sonnet 5.5 (claude-sonnet-5-5), docs updated
0d255d6 docs: Stage E.9 prompt (K8 cross-market screening) and V18 (minimum trades lesson)
e5d17e8 docs: Stage E.8 results, K6 screened, Tier A on one trade (limitcont HE), N = 194
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
K8 no freeze: ClusterFreezeError
$ ledger
17400 ledger/databento_spend.jsonl
0b5466c4366ca9eaba7e10525545631c83e97c1184a7e745d5ed8ad47a9fe957
$ acct-2 position (pull_step2.account_position on the step 2 gate; reads the ledger only)
stage-E.5-2026-09-27 {'account': 'acct-2', 'account_cap_usd': 125.0, 'account_credit_usd': 125.0, 'spent_usd': 124.673761, 'cap_headroom_usd': 0.326239, 'credit_left_usd': 0.326239}
$ python -m data.pull_step2 --status (MES MGC MCL 6C MBT MNQ)
roots in status: 45 ; states: ['not_bought', 'sealed']
MES null
MGC {"holdout": "holdout 2", "product": "MGC", "product_matches": true, "state": "sealed", "chunks_expected": 13, "chunks_sealed": 13, "sealed_in_order": true, "raw_files": {"range=2024-03-01_2024-04-01.dbn.zst": {"sealed_ok": true, "plaintext_absent": true}, "range=2024-04-01_2024-05-01.dbn.zst": {"sea
MCL {"holdout": "holdout 2", "product": "MCL", "product_matches": true, "state": "sealed", "chunks_expected": 13, "chunks_sealed": 13, "sealed_in_order": true, "raw_files": {"range=2024-03-01_2024-04-01.dbn.zst": {"sealed_ok": true, "plaintext_absent": true}, "range=2024-04-01_2024-05-01.dbn.zst": {"sea
6C {"state": "not_bought"}
MBT {"state": "not_bought"}
MNQ {"state": "not_bought"}
```

`uv run pytest -q` at start (reports/stage_e9_briefs/pytest_start.out, 22:13:16-22:26:04, without PYTHONPYCACHEPREFIX as
in E.6-E.8): **5373 passed, 2 skipped, 1 xfailed** (= E.8's end).

**End checks** (reports/stage_e9_briefs/end_checks.out, verbatim):

```
$ date
Fri Oct  2 12:26:54 AM PDT 2026
$ git status --short
 M docs/STAGES.md
 M reports/stage_e9_member_audit.md
?? reports/stage_e9_STATE.md
?? reports/stage_e9_briefs/
?? reports/stage_e9_coder_A.md
?? reports/stage_e9_coder_B.md
?? reports/stage_e9_k8_screen/
$ git log --oneline -3
558a5dc feat: K8 member freeze (Stage E.9), cluster freeze sha256 99f5a6ce
9770828 chore: pin the sonnet alias to Sonnet 5.5 (claude-sonnet-5-5), docs updated
0d255d6 docs: Stage E.9 prompt (K8 cross-market screening) and V18 (minimum trades lesson)
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
K8 cluster freeze OK 99f5a6ce4f91fd63ae4a7dc91b5eb39ecbf8a7eac6f210b3472bf49eaf8463b7 4 members
$ ledger
17400 ledger/databento_spend.jsonl
0b5466c4366ca9eaba7e10525545631c83e97c1184a7e745d5ed8ad47a9fe957
$ acct-2 position (pull_step2.account_position on the step 2 gate; reads the ledger only)
stage-E.5-2026-09-27 {'account': 'acct-2', 'account_cap_usd': 125.0, 'account_credit_usd': 125.0, 'spent_usd': 124.673761, 'cap_headroom_usd': 0.326239, 'credit_left_usd': 0.326239}
$ python -m data.pull_step2 --status (MES MGC MCL 6C MBT MNQ)
roots in status: 45 ; states: ['not_bought', 'sealed']
MES null
MGC {"holdout": "holdout 2", "product": "MGC", "product_matches": true, "state": "sealed", "chunks_expected": 13, "chunks_sealed": 13, "sealed_in_order": true, "raw_files": {"range=2024-03-01_2024-04-01.dbn.zst": {"sealed_ok": true, "plaintext_absent": true}, "range=2024-04-01_2024-05-01.dbn.zst": {"sea
MCL {"holdout": "holdout 2", "product": "MCL", "product_matches": true, "state": "sealed", "chunks_expected": 13, "chunks_sealed": 13, "sealed_in_order": true, "raw_files": {"range=2024-03-01_2024-04-01.dbn.zst": {"sealed_ok": true, "plaintext_absent": true}, "range=2024-04-01_2024-05-01.dbn.zst": {"sea
6C {"state": "not_bought"}
MBT {"state": "not_bought"}
MNQ {"state": "not_bought"}
```

`uv run pytest -q` at end (reports/stage_e9_briefs/pytest_end.out, 00:23:58-00:38:01, after the resume): **5582 passed, 2 skipped, 1 xfailed** (= 5373 +
209 K8 tests). A first end run (23:55) died at about 50% when the session exited (kept as pytest_end_interrupted.out).
Other suites: gate 23:09-23:21 5582 passed; Task 4 23:39-23:52 5582 passed.

- **Manifest and freeze checks:** E.1 manifest 96166eb3... 32/32 and E.2a ML 077a57e1... 4/4 (ALL_OK) at start and end;
  harness v6 preflight OK at start, end and in the runner; cluster freezes K2, K4, K5, K3, K7, K1, K6 OK at start and
  end, K8 absent at start and OK at end (99f5a6ce..., 4 members).
- **Ledger diff:** none. 17400 lines, sha256 0b5466c4366ca9eaba7e10525545631c83e97c1184a7e745d5ed8ad47a9fe957 at start
  and end; acct-2 spent $124.673761, $0.326239 left, unchanged. No Databento call, no quote, no purchase.
- **Holdout:** all_ok, unlocks_logged 0 (holdout-1 and holdout-2) at start and end. REGISTRATION.md 0 bytes at start and
  end. No TopstepX reference, no credential, no edit under live/ or ops/, no frozen file or manifest edited.
- **Research window only:** bars were read by the frozen runner alone (data/processed research parquets with recorded
  sha256). No script of this session opened a bar file. Task 1b left the vendor MES rolls file (which runs into
  holdout-1) unopened. Web access was Task 1b's alone: read-only public pages, no key, no login, WebSearch not used.
- **The one commit:** 558a5dc "feat: K8 member freeze (Stage E.9), cluster freeze sha256 99f5a6ce" (18 files: the 6
  member-package files, 6 test files, the specs, the release check .md and .json, the audit Part 1, the rulings, the
  cluster freeze). No push.
- **Incident (coder B):** a shell heredoc in coder B's report step created two empty stray files ("0" and "=") in the
  repository root at 23:06:58; coder B deleted them at once and the lead confirmed them absent at 23:08. Nothing else
  changed.

`git status --short` and `git diff --stat` at the end (00:27, after docs/STAGES.md and before this return and progress.md were written):

```
$ git status --short
 M docs/STAGES.md
 M reports/stage_e9_member_audit.md
?? reports/stage_e9_STATE.md
?? reports/stage_e9_briefs/
?? reports/stage_e9_coder_A.md
?? reports/stage_e9_coder_B.md
?? reports/stage_e9_k8_screen/
$ git diff --stat
 docs/STAGES.md                   |   4 ++
 reports/stage_e9_member_audit.md | 128 +++++++++++++++++++++++++++++++++++++++
 2 files changed, 132 insertions(+)
```

After this document: also `M progress.md` and `?? reports/E.9_RETURN.md`.

## 3. Results per task

**Task 0 (startup).** Start checks 22:13 all pass; HEAD 9770828 (a descendant of 0d255d6, which holds the prompt); start
suite = E.8's end. Done 22:26.

**Task 1 (specs, lead).** reports/stage_e9_member_specs.md (sections 0-7, with catalog line references). 4 declarations
in catalog order: 1 K8-flight-01 H30 MGC, 2 K8-flight-01 HEOD MGC (strategy.members.k8.flight, make_h30 / make_heod;
legs MGC traded, MES signal), 3 K8-oilcad-01 6C (oilcad.make_6c; 6C traded, MCL signal), 4 K8-wkndbtc-01 MNQ
(wkndbtc.make_mnq; MNQ traded, MBT signal); q_c 1 each (MGC, 6C "undersized", MNQ); operative eps MGC 71, 6C 9, MNQ 170.
Readings adopted from earlier clusters (the same text): E.3-L-01, 03, 04, 08, 17, 18, 19, 20, 22; K4-L-01, 05, 08, 09,
13, 14; K5-L-05; K3-L-01, K3-L-11; K7-L-01, 02, 07; K1-L-10, K1-L-16; K6 S0.4, S0.8, S0.9. New readings K8-L-01..K8-L-17
(each in section 6); the ones that bear on trades:
- K8-L-03 C5's calendar exclusion uses every leg's group calendar; "equity-and-crypto" = both the equity and the crypto
  calendar; full session = no early halt and engine F 15:08;
- K8-L-04 reference dates (flight's Q(d), oilcad's s(d)) = the 20 most recent member full sessions before d, roll-blackout
  dates included; warm-up K4-L-09; values from the signal leg only (R-T3-1);
- K8-L-06 a missing entry bar: flight's first trigger ends the day; oilcad per decision (K4-L-14); wkndbtc no trade;
- K8-L-07 T_e = the actual fill minute; K8-L-08 C6's skip set = the engine's D9.5a set for the traded root (the frozen
  release calendar), a skipped flight trigger does not use the day's entry;
- K8-L-09 flight exact (integer-pair) order statistic; oilcad float z with statistics.stdev (ddof 1); wkndbtc sign of the
  integer tick difference; K8-L-11 oilcad "flat" = no position and no pending order; K8-L-12 wkndbtc's Friday d - 3
  and Sunday d - 1 bars by CT date and clock.
V16 settles C section 6 items 1-4 (K8-L-15): the engine applies the union of every leg's roll blackouts (the catalog's
"signal-leg rolls are not excluded" yields to D4), the legs read MES, MBT and MCL, and the runner checks every leg's
coverage on the declared intervals.

**Task 1b (event checks).** ReleaseChecker-OpusMed, reports/stage_e9_release_check.md and .json (48 evidence pages under
reports/stage_e9_briefs/pages/). A: every release row naming a traded K8 root in the research window kept (NFP 14, CPI
14, FOMC 10, G17 14, ISM_SERVICES 15, WPSR 62) except two WPSR rows E.4 had dropped (2025-12-29 17:00 ET; 2026-05-28
12:00 ET; still in the frozen calendar). Rows on a K8 entry fill minute: FOMC 13:00 CT (flight and oilcad, 10 dates
each), WPSR 09:30 CT (56) and 11:00 CT (7) for oilcad; none for wkndbtc. B: 63 Mondays, 54 eligible (Fridays 2025-04-18,
07-04, 11-28 and 2026-04-03 not full; Mondays 2025-05-26, 09-01, 2026-01-19, 02-16, 05-25 not full). C: CME's 24/7
crypto trading from Friday 2026-05-29 16:00 CT (CME release of 19 Feb 2026, quoted); 51 eligible Mondays before and 3
after. D: research-window roll blackouts MGC 18, MCL 45, 6C 15, MBT 42, MNQ 15 (from earlier frozen runner records);
MES unverifiable before the run. E: full-session sets. F: no external series. **Rulings (specs section 7):** R-1b-1 the
C6 skip set is the frozen calendar unchanged (the two E.4-dropped WPSR rows stay: the engine would otherwise defer a fill
there, which C6 forbids; delayed actual times are hindsight and are not added); R-1b-2 MES's blackouts are the runner's
(it recorded 15: 2025-06-16..18, 09-15..17, 12-15..17, 2026-03-16..18, 06-15..17); R-1b-3 2026-06-01's crypto late open
is not an early close; R-1b-4 unscheduled items (a 2025-08-22 FOMC notation vote, the 2025-11-24 G.17 annual revision)
not added; R-1b-5 expected counts; R-1b-6 the 24/7 counts for the user. No member carries "calendar partly unverified".

**Task 2 (code).** strategy/members/k8/: _calendar.py (five group full-session sets and the three member date tuples,
2019-05-01..2026-06-19; research window: FLIGHT 303, OILCAD 304, WKNDBTC 303 dates; 54 Mondays), _releases.py
(GUARD_INSTANTS MGC 312, 6C 513, MNQ 313, equal to the engine's set; in_guard), flight.py (MemberCoder-A, with the
generator reports/stage_e9_briefs/gen_k8_tables.py), oilcad.py and wkndbtc.py (MemberCoder-B). Tests: tests/test_k8_
members_tables.py, _flight.py, _flight_exits.py, _flight_engine.py (coder A; 87/87 mutants killed), _oilcad.py (60 tests,
with the shared K8 test kit) and _wkndbtc.py (39) (coder B; 88/91 mutants killed, 3 equivalent). 209 K8 tests. The
engine-level tests pin V16(a) end to end: an open on a roll-blackout date of the SIGNAL leg only is refused by the frozen
engine. Coder notes: the freeze allowlist has no `fractions`, so flight's r_k is an exact integer pair compared by cross-
multiplication; the earlier clusters' frozen calendar tables keep confirmation-window dates the K8 F test removes (K3
FX 14 US-holiday dates 2022-2023; K4 and K5 2024-07-03), flagged for the user (section 7).

**Task 3 (fidelity audit).** MemberAuditor-K8-FableXHigh, reports/stage_e9_member_audit.md Part 1 (23:10-23:37): every
module implements its frozen entry and nothing more; 0 BLOCKING, 0 SHOULD FIX, 8 NOTE (section 5). Tables recomputed in
the auditor's own code: identical (full sessions 1779 / 1782 / 1783 / 1783 / 1783 over the table range; guard instants
equal the engine's in_fill_guard at every edge of all 1,138 instants). Cross-leg timing checked on the real engine: no
signal bar used before its close, no forward fill, the traded fill strictly after the signal, the union blackout
applied. 146 auditor mutants, 143 killed, 3 equivalent.

**Task 4 (rulings, freeze).** reports/stage_e9_member_rulings.md (R-T3-1..R-T3-8): no code or test change; the specs'
K8-L-04 wording clarified. Cluster freeze reports/stage_e_k8_member_freeze.json, sha256 99f5a6ce..., 4 members, 7 files,
written 23:39 and verified; the audited files are frozen exactly as audited. Commit 558a5dc 23:52.

**Task 5 (the screen).** `PYTHONPYCACHEPREFIX=<fresh> nice -n 10 uv run python -m screening.stage_e_runner --harness-sha256
9a8ebe73... --cluster K8 --all --window research --research-root data/processed --step2-root data/processed_step2
--out-dir reports/stage_e9_k8_screen`, 23:53:04-23:53:59, exit 0, "K8 research: 4 members, 0 refused" (log
reports/stage_e9_briefs/t5_run.log; field summary t5_summary.out). Power `not_run` for every trial (StartRuleMissing: no
frozen S_X for MES, 6C, MNQ, MBT).

| Trial | Window dates (excluded: not every leg / roll blackout / UR-1) | Coverage (traded, signal) | Trips (days) | Mean hold (min) | Net USD | Mean net ticks/day | sd (pop) | Daily t | MLL liquidations | Labels | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|
| K8-flight-01 H30 MGC | 280, 2025-04-01..2026-06-12 (1 / 33 / 2) | MGC 0.999, MES 1.000 | 55 (55) | 29.6 | +1,195.59 | +4.270 | 73.21 | 0.976 | 0 | none | B |
| K8-flight-01 HEOD MGC | 280 (1 / 33 / 2) | MGC 0.999, MES 1.000 | 55 (55) | 292.3 | +2,989.39 | +10.676 | 128.08 | 1.395 | 0 | none | A |
| K8-oilcad-01 6C | 255, ..2026-06-16 (1 / 60 / 0) | 6C 0.982, MCL 0.9985 | 552 (190) | 15.0 | -5,679.30 | -4.454 | 12.04 | -5.907 | 2 | none | B |
| K8-wkndbtc-01 MNQ | 250, ..2026-06-12 (8 / 57 / 1) | MNQ 0.998, MBT 0.974 | 39 (39) | 1226.8 | +3,621.86 | +28.975 | 427.20 | 1.072 | 0 | none | A |

Labels: none (coverage passes on every leg; no entry-cap, minimum-hold or mean-hold label). Trade-rate: flight 1 entry a
day; oilcad at most 15 a day, holds 15 minutes except the 2 MLL-closed trips (3 and 4 min) and 4 exits deferred 2 minutes
by D9.5a past a 09:30 WPSR release; wkndbtc 1 a week, one trip closed by a D9.7 price-limit exit at Sunday 18:02 on
2025-04-07 (hold 2 minutes, +$18.96 net). Engine counters: flight 10 opens refused off-window; oilcad 158 off-window,
7 while the account was liquidated, 8 fill-guard deferrals (all exits); wkndbtc 2 off-window, 1 price-limit exit.

Descriptive figures the entries name as reported, not trials (reports/stage_e9_briefs/t7_descriptive.out, from the trip
lists; the trip list carries no side, so gross ticks are direction-adjusted): sign checks, mean gross ticks per trade,
flight H30 +25.8 (63.6% positive), HEOD +58.4 (58.2%), oilcad -0.02 (47.1%; gross total -$50 over 552 trips, so its
loss is the cost), wkndbtc +190.2 (66.7%). oilcad's split: 09:35 entries on standard WPSR dates 8 trips, +0.63 gross
ticks; all others -0.03. wkndbtc by regime: 38 trips before the 24/7 change (+$2,488.06 net), 1 after (2026-06-08,
+$1,133.80). The flight clock control and wkndbtc's split by the sign of G need prices or sides and were not computed.

**Task 6 (recomputation).** Audit Part 2 (23:55-00:03): every screen recomputed from its series to relative difference
0.0; tiers A/A/B/B confirmed under D5 and OC-H; all 646 trips' nets rebuilt from gross and the frozen cost table exactly,
daily sums equal to the series; trade counts reconciled (section 5); N = 198; MLL cannot move oilcad's tier (with both
liquidations zeroed its mean is -4.419, t -5.889).

**Task 7 (the result).** Tier A: K8-flight-01 HEOD MGC and K8-wkndbtc-01 MNQ. Tier B: K8-flight-01 H30 MGC and
K8-oilcad-01 6C. Not traded, refused or unimplementable: none. **Program N after the session: 194 + 4 = 198** (counted as
E.4 counted: a trial counts when the runner writes its screen record, K8-L-16).

What K8's confirmation would need (no purchase made or quoted here):
- Step 2 history for every leg root of the four trials: the E.2b quote of 2026-09-26 for the K8 set (b2) is $29.65
  (reports/stage_e2b_step2_quotes.md line 120): MGC $7.30, MCL $4.60, 6C $7.05, MNQ $7.59, MBT $3.11. MGC and MCL were
  bought in E.5 (sealed holdout-2 stores, step 2 status "sealed"); MES's confirmation bars are owned. Remaining: 6C, MNQ,
  MBT = $17.75 at that quote, an acct-2 top-up of about $17.42 ($19.20 with D13's 10%); acct-2 holds $0.326239.
- For the Tier A trials alone: HEOD needs no purchase (MGC bought, MES owned); wkndbtc needs MNQ and MBT ($10.70, a
  top-up of about $10.37, $11.44 with 10%).
- Frozen start rules (S_X) for MES as a Stage E leg, 6C, MNQ and MBT: the runner found none, so the power check could
  not run (section 7). wkndbtc's MBT history starts 2021-05, and the catalog expects "inconclusive by design".

## 4. Delegation record

| Agent name | Worker file | Model | Effort | Objective | Time (PDT) | Tokens | Status and deviations |
|---|---|---|---|---|---|---|---|
| ReleaseChecker-OpusMed | worker-medium | opus | medium | Task 1b: release rows, wkndbtc clock points, the 24/7 change, roll blackouts, EC-CAL, external series (brief reports/stage_e9_briefs/1b_release_checker.md) | 22:20-22:31 | 10,204,160 | done; MES blackouts unverifiable from the named sources; BLS pages saved from Scrapling markdown (curl 403); ISM via Wayback (live page needs login); no WebSearch |
| MemberCoder-A-OpusXHigh | worker-xhigh | opus | xhigh | Task 2: _calendar.py, _releases.py and their generator first, then K8-flight-01 (H30, HEOD) and four test files (2A_member_coder_A.md) | 22:28-23:09 | 20,290,233 | done; 87/87 mutants killed; spawned before Task 1b returned (section 6 item 22); section 7 sent by message; `fractions` not on the allowlist, so exact integer pairs |
| MemberCoder-B-OpusXHigh | worker-xhigh | opus | xhigh | Task 2: K8-oilcad-01 and K8-wkndbtc-01 with two test files (2B_member_coder_B.md) | 22:32-23:09 | 14,813,091 | done; 88/91 mutants killed (3 equivalent); the harness refused its report write (saved by the lead); two stray empty files made and deleted at once (section 2) |
| MemberAuditor-K8-FableXHigh | worker-xhigh | fable | xhigh | Task 3 fidelity audit (auditor_task3_K8.md), then, resumed, Task 6 recomputation (auditor_task6_K8.md) | 23:09-23:37; 23:55-00:03 | 11,285,770 (both parts) | done; 0 blocking, 0 should-fix, 8 notes; Part 2 no discrepancy; ran the holdout status at its end only |

No other worker was spawned; no worker spawned workers. At most three ran at once (1b, coder A, coder B).

## 5. Verification

Part 1 (Task 3), MemberAuditor-K8-FableXHigh, 0 BLOCKING, 0 SHOULD FIX, 8 NOTE; the lead's rulings
(reports/stage_e9_member_rulings.md):

| Finding | Ruling | Fix |
|---|---|---|
| F-1 reference values from the signal leg only (K8-L-04 "a leg") | R-T3-1 confirmed: values are defined by the signal leg's two bars; a date with no traded-leg bars is the runner's to remove | specs wording |
| F-2 oilcad's per-decision missing-entry-bar rule is K4-L-14's, not C5's date-level letter | R-T3-2 kept (consistency with ovr; the letter would be non-causal); open choice | none |
| F-3 reference dates include roll-blackout dates | R-T3-3 kept (K5-L-05, K4-L-08; no roll input in a member); open choice | none |
| F-4 "equity-and-crypto" as one calendar | R-T3-4 agreed: immaterial in the research window | none |
| F-5 flight marks the day used before its position/pending check | R-T3-5 unreachable on real bars | none |
| F-6 engine tests use no release calendar | R-T3-6 the auditor's engine checks with the real calendar show no knowable deferral | none |
| F-7 wkndbtc coverage measured on every window date | R-T3-7 kept by design (stricter) | none |
| F-8 the K8-L-08 edge (missing traded bar at t, fill inside a guard) | R-T3-8 accepted; Task 6 counted it: 0 occurrences | none |

Part 2 (Task 6): items 0 (frozen files), 1 (screens), 2 (tiers), 3 (cost rebuild of HEOD, wkndbtc and oilcad: 55/55,
39/39, 552/552 trips exact), 5 (N = 198) and 6 (MLL and counters) VERIFIED; item 4 (trade counts) VERIFIED WITH NOTES:
- wkndbtc: 40 expected Mondays (54 less 14 blackout Mondays), 39 trips; 2026-03-16 has no trip and no refusal (G = 0, a
  missing bar at a clock point, or an MBT contract change Friday to Sunday; not checkable without prices). The lead rules:
  accepted as not checkable; no tier depends on it.
- oilcad: 541 exits at T_e + 15; 2 MLL; 4 exits deferred to 09:32 by the 09:30 WPSR guard (the 8 fill_guard_deferral
  counts, 2 per exit; no entry deferral, so R-T3-8's count is 0); 5 exits one minute late with no guard, explained only by
  a missing 6C bar at the nominal minute ("first later bar", S0.7). The lead rules: accepted, as the specs require.
- flight: H30 and HEOD have identical entries; every entry on the 5-minute grid; no entry at 13:00 on an FOMC date (the one
  13:00 entry, 2025-11-17, is not an FOMC date); exits as the rules.
Sensitivity (reported, not a ruling): HEOD t 1.085 without its largest day (2026-04-02, +849.9 ticks), 0.751 without the
top two; wkndbtc t 0.781 without 2026-06-08 (+2,267.6 ticks), 0.477 without the top two.
No DISCREPANCY, so no tier is marked "unverified". Not checked: oilcad's |z| = 2.0 equality case (needs bars;
probability zero).

## 6. Open choices (each decided by the lead alone, with the reason; each can be overturned)

Readings (specs section 6; the full text there):
1. **K8-L-01** 4 declarations, labels "<member> [grid] <traded root>", catalog order, traded leg first: the template's
   primary-leg rule; the ordinal seeds the power check.
2. **K8-L-02** bars by CT date and clock per leg (E.3-L-03, K7-L-01): MBT's weekend bars carry Monday's trade date from
   2026-06-01.
3. **K8-L-03** C5's "any leg's D10 group calendar" = every leg's own calendar; "equity-and-crypto" = both the equity and
   the crypto calendar (narrowest); full session = no early halt and engine F 15:08 (K3-L-11, K7-L-02).
4. **K8-L-04 / R-T3-1 / R-T3-3** reference dates = the 20 most recent member full sessions, roll-blackout dates included
   (K5-L-05, K4-L-08; the member cannot read a roll calendar); values from the signal leg only; warm-up K4-L-09.
5. **K8-L-05** signal computations guarded per computation within the signal leg (C4; the entries).
6. **K8-L-06 / R-T3-2** a missing entry bar: flight's first trigger ends the day (C5 "the entry bar is missing"; E.3-L-08's
   analogue); oilcad per decision time (K4-L-14), not C5's date-level letter; wkndbtc no trade.
7. **K8-L-07** T_e = the actual fill minute (the text: "the entry fill minute").
8. **K8-L-08 / R-1b-1** C6's skip set = the engine's D9.5a set for the traded root (the frozen release calendar, unchanged,
   including two WPSR rows E.4 dropped for its own event members); the extra rows (MGC G17 08:15 CT, MNQ ISM 09:00 CT) can
   never meet a K8 fill minute; the skip tests the scheduled fill minute (a missing traded bar could still push a fill into
   a guard: 0 occurrences, Part 2).
9. **K8-L-09** arithmetic: flight exact integer-pair order statistic (no `fractions` on the allowlist); oilcad float z
   with statistics.stdev, ddof 1 (K4-L-05's statistic route); wkndbtc integer tick sign.
10. **K8-L-10** flight requires c6 > 0 only to avoid a division by zero (never binds on MES).
11. **K8-L-11** oilcad's "no open position; no exit pending" = flat: no position and no pending order of either side.
12. **K8-L-12** wkndbtc: d a Monday; the Friday = d - 3 (calendar), full in both calendars; P_F, P_S and the MNQ entry
    bar by CT date, clock and trade date; one instrument_id across P_F and P_S; an MBT blackout on the Friday alone does
    not remove the Monday (V16(a) removes trade dates).
13. **K8-L-13 / R-T3-7** trading_windows measured on every window date (wkndbtc's Friday bar on each date's own 14:59).
14. **K8-L-14** tables span 2019-05-01..2026-06-19.
15. **K8-L-15** C section 6: items 1-4 by V16; item 5 as built in the frozen calendar (WPSR concerns 6C program-wide);
    items 6, 9, 12 as frozen; items 7, 8, 10 no member effect; item 11 for the user (section 7).
16. **K8-L-16** the N rule: a trial counts when the runner writes its screen record.
17. **K8-L-17** two coders; coder A wrote the shared tables first.
Task 1b rulings: 18. **R-1b-2** MES's blackouts taken from the runner's record (15 dates), no member label. 19. **R-1b-3**
a late open (2026-06-01 crypto) is not an early close. 20. **R-1b-4** unscheduled publications not added to any guard.
Audit rulings: 21. **R-T3-4..R-T3-6, R-T3-8** no code or test change (immaterial, unreachable, or checked by the auditor's
own engine runs).
Process choices:
22. Coder A was spawned at 22:29, before Task 1b returned (the prompt runs 2A after Task 1 and only 2B after 1b); section
    7 arrived by message at 22:33 with no table correction.
23. Task 6 rebuilt three trials (HEOD, wkndbtc, oilcad) instead of "one port, one other member": K8 has no port, so both
    Tier A trials and the trial with event-window fills and MLL liquidations were named.
24. Pytest runs used `-p no:cacheprovider` and no PYTHONPYCACHEPREFIX (E.6-E.8 precedent: three bytecode tests fail
    under a prefix); scripts and the runner used a fresh prefix.
25. Coder B's report was saved by the lead from its final message (the harness refused the worker's write), text unchanged.
26. The descriptive sign checks and splits (section 3) were computed by the lead from the trip lists; they are not trials
    and enter no verdict.
27. After the accidental exit, the interrupted end suite was kept and re-run in full rather than resumed.

## 7. What the next session must do first

1. **Push owed by the planning chat:** 558a5dc (the K8 freeze) and the planning chat's own docs commit of this return,
   progress.md, docs/STAGES.md and the untracked E.9 records (reports/stage_e9_*, reports/stage_e9_k8_screen/, the briefs
   folder, and the audit's Part 2, which is a working-tree change to reports/stage_e9_member_audit.md). This session made
   only the one named commit and no push.
2. **Frozen hashes:** harness v6 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87; K8 cluster freeze
   99f5a6ce4f91fd63ae4a7dc91b5eb39ecbf8a7eac6f210b3472bf49eaf8463b7 (558a5dc); K2 8815a775, K4 7abcde17, K5 1d0c974f,
   K3 c4fb5da4, K7 46cae308, K1 cf48f514, K6 a6f8b497; E.1 manifest 96166eb3; E.2a ML 077a57e1; release calendar
   839f2437. Every cluster is now screened (V17); the ML route is next.
3. **Funding a K8 confirmation would need:** 6C, MNQ and MBT step 2 ($17.75 of the $29.65 K8 quote of 2026-09-26; MGC and
   MCL already bought) and an acct-2 top-up of about $17.42 ($19.20 with 10%); for the two Tier A trials only, MNQ and MBT
   ($10.70; top-up about $10.37, $11.44 with 10%), since HEOD needs no purchase. A fresh quote comes first.
4. **Questions for the user:**
   - (a) **Tier A strength.** wkndbtc's pass rests on one Monday (2026-06-08; t 0.781 without it), its only trade after
     the 24/7 change; HEOD passes without its best day (1.085) but not its best two (0.751). D5 is frozen and both pass
     it (V18's minimum-trade concern does not apply at 39 and 55 trips), but neither is strong. Whether a K8
     confirmation is worth funding is yours.
   - (b) **The 24/7 regime (catalog section 6 item 11).** The confirmation window lies wholly in the weekend-closure
     regime; deployment would lie wholly in the continuous one. Research window: 51 eligible Mondays before the change,
     3 after (2026-06-01 and 06-15 were roll-blackout Mondays, so 1 traded). Is a confirmation on the old regime
     acceptable for wkndbtc? It is also labelled source-overlap: no edge could be claimed on it without a registered
     holdout read.
   - (c) **Start rules.** The runner found no frozen S_X for MES (as a Stage E leg), 6C, MNQ or MBT, so no power check
     ran. A confirmation session must build them first (MES's D.1f S = 2020-02-03 is the program's value; D4 says every
     leg starts at its own S).
   - (d) **Earlier clusters' calendar tables.** K3's frozen FX table keeps 14 US-holiday dates of 2022-2023, and K4's and
     K5's keep 2024-07-03, that the current rules/sessions.py gives an early flatten (K8's tables remove them). All are
     in confirmation or holdout-2 windows, none in the research window. Before K3, K4 or K5 confirmation sessions, decide
     whether those members trade those dates.
   - (e) MES's research-window roll-blackout dates were not on file before the run (the vendor rolls file runs into
     holdout-1 and was left unopened); the runner recorded them. A per-root roll list for signal legs would remove this
     gap in later stages.

## 8. Session cost

**Wall clock** 2026-10-01 22:12 to 2026-10-02 00:42 PDT (2 h 30 min), of which **one pause, 00:04-00:23 (19 min)**: the
session exited by accident and was resumed by the user ("resume please accidentally exited"); the end suite running at
the time died at about 50% and was re-run. **Work time 2 h 11 min.** First estimate 3 h 25 min (to about 01:37; the prompt
expected about 1.5 h), revised at 23:10 to about 00:50 as the coders finished 50 minutes early; the screen took 1 minute
and the recomputation 8.

**Final ETA table** (PDT; tokens from the transcripts):

| Task | Owner | Model | Effort | Start | End | Time | Tokens | Status and deviations |
|---|---|---|---|---|---|---|---|---|
| 0 Startup checks (start suite to 22:26) | lead | opus | xhigh | 22:12 | 22:26 | 14 min | in lead | done; suite = E.8's end |
| 1 Member specs (section 7 at 22:33) | lead | opus | xhigh | 22:21 | 22:33 | 12 min | in lead | done |
| 1b Event checks | ReleaseChecker-OpusMed | opus | medium | 22:20 | 22:31 | 11 min | 10,204,160 | done; MES blackouts unverifiable pre-run |
| 2A Tables and flight | MemberCoder-A-OpusXHigh | opus | xhigh | 22:28 | 23:09 | 41 min | 20,290,233 | done; spawned before 1b returned |
| 2B oilcad and wkndbtc | MemberCoder-B-OpusXHigh | opus | xhigh | 22:32 | 23:09 | 37 min | 14,813,091 | done; .md write refused, saved by the lead; stray files deleted |
| 2g Gate suite | lead | - | - | 23:09 | 23:21 | 12 min | in lead | 5582 passed |
| 3 Fidelity audit | MemberAuditor-K8-FableXHigh | fable | xhigh | 23:09 | 23:37 | 28 min | 11,285,770 (Parts 1 and 2) | 0 blocking, 0 should-fix, 8 notes |
| 4 Rulings, freeze, suite, commit 558a5dc | lead | opus | xhigh | 23:37 | 23:53 | 16 min | in lead | done; no code change |
| 5 Screening run | lead | opus | xhigh | 23:53 | 23:54 | 1 min | in lead | 4 run, 0 refused |
| 6 Recomputation | MemberAuditor-K8-FableXHigh (resumed) | fable | xhigh | 23:55 | 00:03 | 8 min | above | no discrepancy |
| 7a Result, return draft, first end suite (died at 50%) | lead | opus | xhigh | 23:54 | 00:04 | 10 min | in lead | interrupted by the exit |
| Pause (accidental exit and resume) | - | - | - | 00:04 | 00:23 | 19 min | - | excluded from work |
| 7b Return, end suite re-run (00:24-00:38), end checks, cost, progress | lead | opus | xhigh | 00:23 | 00:42 | 19 min | in lead | done |
| **Stage** | | | | 22:12 | 00:42 | **2 h 30 min wall, 2 h 11 min work** | **99,814,881** (lead 43,221,627, 43.3%; workers 56,593,254, 56.7%) | first estimate 3 h 25 min; the prompt expected about 1.5 h |

**Tokens per model** (the lead transcript 20d17daf's .jsonl, which the resumed session kept writing to, plus every worker
transcript under its subagents/ folder; reports/stage_e9_briefs/cost.py, output cost.out; counted at 00:38, so the last
few lead steps after it are not in the table):

| Model | Input | Output | Cache read | Cache creation | Total |
|---|---|---|---|---|---|
| claude-opus-5-5 | 786 | 573,924 | 86,658,681 | 1,295,720 | 88,529,111 |
| claude-fable-5-1 | 1,004 | 161,926 | 10,240,730 | 882,110 | 11,285,770 |
| all | 1,790 | 735,850 | 96,899,411 | 2,177,830 | 99,814,881 |

Per worker spawn: worker-medium opus medium (ReleaseChecker) 10,204,160; worker-xhigh opus xhigh (MemberCoder-A)
20,290,233; worker-xhigh opus xhigh (MemberCoder-B) 14,813,091; worker-xhigh fable xhigh (MemberAuditor, both parts)
11,285,770. Delegation share: lead 43.3%, workers 56.7%; by model tier opus 88.7% (lead 43.3%, workers 45.4%), fable
11.3%. Cache reads are 97.1% of the total. E.8 used 129.7M tokens for 27 trials; E.9 used 99.8M for 4 (two-leg members,
four test files per coder, and the extra cross-leg audit items). These are token counts, not plan-credit percentages; the
/usage meter is the user's to record.
