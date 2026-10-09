# Stage E.16 return (Part A): H1 to H5 frozen, not registered; nothing read, nothing bought

Prompt docs/prompts/STAGE_E.16.md (V29, Part A). Lead Opus 5.5 xhigh, session 4a9d3866. All times PDT.
Freeze commit 8f388c8 "E.16 base-rule freeze"; manifest reports/stage_e16_freeze.json, sha256
5274aa97f3359d7dcfaae15cb0590b6147d1624e6056ea396df08c6215209ad4 (97 files).

## 1. Verdict summary

All five base rules are frozen as written, with every parameter fixed. None was dropped: the overlap audit found
none identical to a tested member. None is registered; N stays 471. The freeze holds:
- five pre-registrations and a shared common file;
- base_rules/ (27 files) and its 75 synthetic tests;
- the sourced settlement minutes for 27 products, 2010-2024;
- the livestock and Treasury-auction calendars for 2010-2019;
- the per-product windows, the power table, the rulings and Fable's review.

The user's rulings of 2026-10-09 are written in as binding:
- U1: E.17 runs C1 first, then a second harness change.
- U2: the window starts.
- U3a: base cost is D8 with no extra tick; D8 plus one tick per side is the stress case.
- U3b: H2's year stability counts years with at least 6 units.

Probability of passing every bar at Holm's first step (0.01), at the low and high priors:

| Test | Full window (2010-07 on) | Fallback window (2019-05 on) |
|---|---|---|
| H1 | 0.11 / 0.71 (3,385 units) | 0.04 / 0.27 |
| H2 | 0.11 / 0.53 (60 units) | 0 (cannot pass) |
| H3 | 0.09 / 0.50 (354 units) | 0.04 / 0.12 |
| H4 | 0.06 / 0.43 (3,385 units) | 0.02 / 0.14 |
| H5 | 0.70 / 1.00 (3,370 units) | 0.25 / 0.80 |

**Purchase for E.17:** the 21 extension roots outside C1's set. That is 1,993 monthly chunks, $153.965349 at E.12's
quote, or $158.584309 x 1.03. With C1 ($59.474600 x 1.03), acct-2 needs about $218.06 beyond today's $18.07 of
headroom.

**What E.17 must do** (reports/stage_e16_handoff.md):
1. Verify both freezes.
2. Run C1 under a caps-only harness through its evaluation.
3. Write harness v12, adding plan "ext2010h" and the livestock calendar.
4. Quote fresh, with the guard that sums the run's own ledger lines.
5. Register E16-H1..H5 (N + 5).
6. Buy, build the stores, run each test once, and have Fable recompute every verdict number.

## 2. Guardrail evidence

No bar of any market data was read in this stage, no Databento endpoint was called, nothing was registered or
bought, no harness file changed, and nothing under live/ or ops/ was touched. The workers read file names, sizes,
JSON manifests and quote records only. The only network access was the public pages and FiscalData calls of Tasks 1
and 3b, each logged with its terms check.

**Start checks, 23:06 on 2026-10-08** (reports/stage_e16_briefs/start_checks.txt):

```
$ date
Thu Oct  8 23:06:41 PDT 2026
$ git status --short
?? .claude/worktrees/
?? reports/stage_e12_briefs/, stage_e13_briefs/, stage_e14_briefs/ page files: 638 lines (collapsed; full text in reports/stage_e16_briefs/start_checks.txt)
?? reports/stage_e16_briefs/
$ git log --oneline -3
be01890 docs: prompts index row for E.16 Part A
9ade2a8 docs: Stage E.16 revised to Part A (no Databento) and V29
f9a3ddc Stage E.15 stopped again before registration: acct-2 still locked
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
29040 ledger/databento_spend.jsonl
a9ad6ab59b94818407042d4faf1ccaaa3bab72447376dcce631f3312cc12b2de
$ ledger total per account (SpendGate.account_spent_usd: external ledgers plus this repo's lines)
acct-1: spent 118.390020 cap 120.00 headroom 1.609980
acct-2: spent 231.599730 cap 249.67 headroom 18.070270
$ v2 freeze manifest (ml_route_v2.phase1.freeze.verify_v2_freeze)
v2 freeze OK: 91 files
$ uv run python -m screening.trial_registry status
N = 471 (1 lines)
$ wc -l ledger/trial_registrations.jsonl; sha256sum
1
a73b4de878caa75066a8c24513e354de0a07d34f15d53407c4450e6f0135de0d
$ C1 freeze file sha256 (reports/stage_e14_prereg_C1.md; pinned afc5c10f628771afa3d1311192316ff3b4b681d7308d2b411fc655c15f821c0b)
afc5c10f628771afa3d1311192316ff3b4b681d7308d2b411fc655c15f821c0b
```

Start suite (reports/stage_e16_briefs/pytest_start.out): `6740 passed, 2 skipped, 3 xfailed, 54 warnings in
1782.36s (0:29:42)`, rc 0.

**End checks, 11:58 on 2026-10-09** (reports/stage_e16_briefs/end_checks.txt):

```
$ date
Fri Oct  9 11:58:55 PDT 2026
$ git status --short
?? .claude/worktrees/
?? reports/stage_e12_briefs/, stage_e13_briefs/, stage_e14_briefs/ page files: 638 lines (collapsed; full text in reports/stage_e16_briefs/end_checks.txt)
?? reports/stage_e16_STATE.md
?? reports/stage_e16_briefs/brief_calendars.md
?? reports/stage_e16_briefs/brief_coder.md
?? reports/stage_e16_briefs/brief_common.md
?? reports/stage_e16_briefs/brief_freeze_review.md
?? reports/stage_e16_briefs/brief_overlap.md
?? reports/stage_e16_briefs/brief_settlement.md
?? reports/stage_e16_briefs/checks.sh
?? reports/stage_e16_briefs/end_checks.txt
?? reports/stage_e16_briefs/pages/
?? reports/stage_e16_briefs/power_table.json
?? reports/stage_e16_briefs/power_table.md
?? reports/stage_e16_briefs/pytest_start.out
?? reports/stage_e16_briefs/runtime_probe.md
?? reports/stage_e16_briefs/settlement_worker_original.json
?? reports/stage_e16_briefs/start_checks.txt
?? reports/stage_e16_handoff.md
$ git log --oneline -3
8f388c8 E.16 base-rule freeze
be01890 docs: prompts index row for E.16 Part A
9ade2a8 docs: Stage E.16 revised to Part A (no Databento) and V29
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
29040 ledger/databento_spend.jsonl
a9ad6ab59b94818407042d4faf1ccaaa3bab72447376dcce631f3312cc12b2de
$ ledger total per account (SpendGate.account_spent_usd: external ledgers plus this repo's lines)
acct-1: spent 118.390020 cap 120.00 headroom 1.609980
acct-2: spent 231.599730 cap 249.67 headroom 18.070270
$ v2 freeze manifest (ml_route_v2.phase1.freeze.verify_v2_freeze)
v2 freeze OK: 91 files
$ uv run python -m screening.trial_registry status
N = 471 (1 lines)
$ wc -l ledger/trial_registrations.jsonl; sha256sum
1
a73b4de878caa75066a8c24513e354de0a07d34f15d53407c4450e6f0135de0d
$ C1 freeze file sha256 (reports/stage_e14_prereg_C1.md; pinned afc5c10f628771afa3d1311192316ff3b4b681d7308d2b411fc655c15f821c0b)
afc5c10f628771afa3d1311192316ff3b4b681d7308d2b411fc655c15f821c0b
$ uv run python reports/stage_e16_briefs/freeze_manifest.py verify --expected 5274aa97f3359d7dcfaae15cb0590b6147d1624e6056ea396df08c6215209ad4
E.16 freeze OK: 97 files; manifest sha256 5274aa97f3359d7dcfaae15cb0590b6147d1624e6056ea396df08c6215209ad4
$ git diff --quiet 8f388c8 -- base_rules tests reports/stage_e16_prereg_common.md reports/stage_e16_prereg_H1.md reports/stage_e16_prereg_H2.md reports/stage_e16_prereg_H3.md reports/stage_e16_prereg_H4.md reports/stage_e16_prereg_H5.md
no diff against 8f388c8
```

End suite (reports/stage_e16_briefs/pytest_end.out): `6815 passed, 2 skipped, 3 xfailed, 54 warnings in 959.94s (0:15:59)`, rc 0 (the 75 new base_rules tests included).

Ledger: 29,040 lines and sha256 a9ad6ab5... at start and end (unchanged); acct-1 spent 118.390020, acct-2 spent
231.599730 at both. Holdout status all_ok, 0 unlocks, at both. REGISTRATION.md 0 bytes at both. No worker or
background shell is running at the end (the coder's probe watcher was stopped at 01:13; every spawn returned).

## 3. Results per task

**Task 0, startup (23:05-00:16; user pause 23:45-00:10).**
- Start checks and suite passed.
- The lead raised three points: E.17's harness, the window starts, and the extra tick and H2's stability bar.
- The user's rulings U1 to U3b followed at 00:10.
- The lead then wrote its operational spec (reports/stage_e16_briefs/lead_spec.md) and the briefs.

**Task 1, settlement minutes** (reports/stage_e16_settlement.json and .md). Sources: 33 in all, 32 of them CME,
CBOT, NYMEX and COMEX rule filings hosted on cftc.gov (primary), plus Baltussen et al. 2021 (secondary). S_p in CT:

| Group | S_p | Changes in 2010-2024 |
|---|---|---|
| Equity (NQ, YM, RTY) | 15:15, then 15:00 | 15:00 from trade date 2020-10-26 (CME/CBOT 20-018) |
| Rates (ZT, ZF, ZN, TN, ZB, UB) | 14:00 | none |
| FX (6E, 6A, 6B, 6C, 6J, 6S, 6N) | 14:00 | none |
| Energy (CL, NG) | 13:30 | none |
| Gold (GC) | 12:30 | none |
| Copper (HG) | 12:00 | none |
| Grains (ZC, ZW, ZS, ZM, ZL) | 13:15 | 14:00 from 2012-06-25 to 2013-04-07 |
| Livestock (LE, HE) | 13:00 | none |

Other findings:
- Grains' day open moved from 09:30 to 08:30 on 2013-04-08.
- RTY was listed 2017-07-10 and TN 2016-01-11.

The lead's grade rulings (lead_grade):
- R-S2 caps inferred periods at secondary: NQ and YM 2010-2012, the FX majors, and HG 2010-2017.
- R-S3: LE 2010-06-07..2014-12-14 is weak (13:00 was assumed, no saved source), so LE has no H1 or H4 unit there.
- R-S4: no unit before a product's listing.
- R-S5: livestock's day open in 2014-10-27..2016-02-28 is 08:00, or 09:05 on the first trade date of the week.
- R-S6: equity's 15:15 settlement is followed as it was.

**Task 2, overlap audit** (reports/stage_e16_overlap.md). All five are KEEP (related, not identical). The closest
tested member for each:
- H1: the CP1 port. Same entry fill on 24 of the 27 markets; the signal is the rest-of-day return instead of the
  first half hour.
- H2: K2-monthend-01 (intraday ZN only).
- H3: K2-aucpre-01 and K2-aucpost-01 (intraday only).
- H4: the CP3 port (same entry fill, a different signal). Gate 0's reversal-leaning, unrejected results are
  disclosed.
- H5: no combination member exists.

Each relation is quoted in its pre-registration. Rulings:
- R-O2: D4's start rule S_X does not bind these tests. ZF and ZT are read from 2019-05, where Gate 0 had cut them.
- R-O3: V24's wording on reusing the 2019-2024 stores and E.17's order (C1 reads its roots first) are disclosed.

**Task 3b, calendars** (reports/stage_e16_calendars/ and reports/stage_e16_calendars.md).
- **Livestock 2010-06..2019-05**, in E.14's hist2010 format: 2,274 trade dates, 75 closures, 26 early halts and 295
  late opens. 25 of 2,349 weekdays are unsourced (1.06%, under the 2% bar), and the 2019 overlap agrees. Rulings
  R-C1 and R-C2 accept CME holiday PDFs re-hosted by Dorman Trading and Cannon Trading's schedule images as
  secondary; without them the 2% check fails.
- **EC-AUC 2010-01..2019-06**, from FiscalData metadata only: 684 rows. None of the 420 tenor-matched rows for
  2010-06..2019-04 was dropped, and the 2019-05/06 overlap equals the frozen rows.
- **Announcement dates, after review F-04:** added to every row, and fetched for the frozen 2019-05..2024-02 rows
  (231 matched). 49 of 420 and 46 of 231 auctions were announced after t-3, mostly 2-year notes.
- **Deviations:** one page fetched before its terms were read was deleted and not used. fia.org's and
  ampfutures.com's terms were read seconds after their single fetches.

**Task 3, build** (base_rules/; tests/test_base_rules_*.py; base_rules/README.md).
- **Contents:** the multi-day simulator (fills at bar opens, rolls at splices with costs, daily marks at settlement),
  the five runners, the statistics, a power module, the store loader for the 2010-2024 splice, run-once markers,
  and checks of registration and the freeze before any bar.
- **Tests:** 75 synthetic tests pass in the main tree. Among them:
  - a hand-computed multi-day trade with a roll, exact to the cent;
  - single-day engine matches, including the R-B1 close fill on a grains session-close day;
  - causality tests for every signal and for every risk and H5 scaling;
  - a planted edge detected and noise rejected, for each runner;
  - loader refusals for holdout-2, the embargo, the research store, MES, sealed paths and dates after 2024-02-29.
- **Lead rulings** (R-B1 to R-B5):
  - R-B1: at a scheduled closure that begins at S_p, an exit or mark is the close of bar S_p - 1, the engine's own
    fill. An entry goes to the first bar after the closure.
  - R-B2: an uncalibrated cost bucket pays the product's largest per-side slippage.
  - R-B3: no data condition stops a run after its marker.
  - R-B4: the registry label is E16.
  - R-B5: the power table was rerun on the real inputs.
- **Release touch** (reports/stage_e16_briefs/release_touch.md): only FOMC touches an H fill minute, and it has
  2010-2019 rows, so the conservative fallback is not needed.

**Runtime probe** (reports/stage_e16_briefs/runtime_probe.md): synthetic stores at full 2010-2024 scale (27 products,
about 3,500 dates), run before rulings R-B1 to R-B4:

| Test | Wall time | Peak RSS |
|---|---|---|
| H1 | 4:32 | 1.2 GB |
| H2 | 0:23 | |
| H3 | 0:45 | |
| H4 | 4:25 | 1.2 GB |
| H5 | 0:01 | |

The fixes add columns, so E.17 should expect a higher peak (recheck R-3).

**Task 4, freeze** (reports/stage_e16_prereg_common.md and _H1.._H5.md, reports/stage_e16_rulings.md,
reports/stage_e16_review.md).
- Fable's review returned APPROVE WITH FIXES: 1 BLOCKING, 8 SHOULD FIX, 7 NOTE.
- Every BLOCKING and SHOULD FIX item was fixed or ruled before the commit (section 5), and the recheck returned
  APPROVE.
- The manifest was written last, then committed as 8f388c8 at 02:09.

**Task 5, hand-off** (reports/stage_e16_handoff.md).
- **Order (U1):** start checks; verify C1's freeze, then this one; C1's fresh quote with the guard (V29); a caps-only
  harness v11; C1's registration, purchase, stores and evaluation.
- **Harness v12, only after C1's evaluation:** plan "ext2010h" for the 21 roots, the livestock calendar and caps.
  v12 must not touch any hashed file.
- **Then:** a fresh 21-root quote with the guard; registration of E16-H1..H5 with the fallback list; the purchase;
  the store builds; the run manifest; the five runs once each; the Holm verdict; Fable's recomputation.
- **Also in it:** the purchase table per root and the funds per step.

## 4. Delegation record

| Agent | File | Model | Effort | Start-end (PDT) | Tokens (transcript) | Status |
|---|---|---|---|---|---|---|
| SettlementSource-OpusHigh | worker-high | opus | high | 00:16-00:39 | 23,306,834 | done; lead grades added |
| OverlapAudit-OpusHigh | worker-high | opus | high | 00:17-00:28 | 13,664,694 | done; keep all five |
| CalendarBuilder-OpusHigh | worker-high | opus | high | 00:16-01:07; F-04 follow-up 01:49-01:52 | 68,346,290 | done; both 2% checks pass |
| BaseRulesCoder-OpusXHigh | worker-xhigh (worktree) | opus | xhigh | 00:16-01:13; R-B follow-up 01:15-01:24; review fixes 01:49-02:04 | 163,022,024 | done; merged twice |
| FreezeReviewer-FableXHigh | worker-xhigh | fable | xhigh | 01:26-01:46; recheck 02:05-02:09 | 8,043,509 | APPROVE WITH FIXES, then APPROVE |

Five spawns. At most four ran at once, and each follow-up went to its original worker through SendMessage.

## 5. Verification

Fable reviewed the freeze before the commit (reports/stage_e16_review.md). No verdict number exists in this stage,
since nothing was run; Fable's recomputation of the verdicts belongs to E.17.

| Finding | Grade | Ruling | Fix |
|---|---|---|---|
| F-01 the loader accepted only plan "ext2010", so it would refuse the 21 roots' stores | BLOCKING | accepted | Plans are fixed per root ("ext2010" for C1's six, "ext2010h" for the 21). The loader checks the name, the metadata and the bookings through an injectable plan. Hand-off step 8 is fixed. |
| F-02 the registration was not tied to the freeze sha256 | SHOULD FIX | accepted | The freeze sha256 is passed to require_registered, with a test. |
| F-03 `verdict --tests` and `--registry` were run-time knobs | SHOULD FIX | accepted | Subset removed. A non-default registry works only in test mode, and the registry path and sha256 are recorded in every output. |
| F-04 49 of 420 auctions announced after t-3 | SHOULD FIX | accepted, option (a), tightening | Announced on or before t-3 is required. Dates were added for 2010-2019 and fetched for 2019-2024. |
| F-05 hand-off label and placeholders | SHOULD FIX | accepted | Label E16 and plan ext2010h. The manifest was written last and the placeholders filled. |
| F-06 imported modules not pinned | SHOULD FIX | accepted | Engine, cost, rules, booking and registry modules and the stage_e2a tables pinned; hist2010 calendars listed by name; v12's files left out on purpose. |
| F-07 limit-locked and no-new-positions fills | SHOULD FIX | accepted | Limit-lock rule where limit tables exist (2019-05 on), excluded and counted. A pre-2019 diagnostic, and a Topstep table that is descriptive only. |
| F-08 no engine match for the R-B1 close fill | SHOULD FIX | accepted | Engine match added on a grains 13:15 close. The equity 15:15 case cannot reach the engine past its 15:08 flatten. |
| F-09 R-B1(b) opens where the engine cancels | SHOULD FIX | ruled: kept as a stated departure | Stated in the common file and in prereg_H2; counted "entry after closure". |
| F-10 to F-16 | NOTE | recorded | Cited scripts hashed; release-touch check and grains note recorded; descriptive H1 table without S_p > 15:08 and H4 table without uncalibrated-bucket units; H2's warm-up cost noted. |
| Recheck | APPROVE | | 12 fixed, 4 accepted as ruled, 0 not fixed. NOTEs R-1 to R-3 carried into the rulings and the hand-off. |

## 6. Open choices (every decision the lead made on its own, with the reason)

1. **Settlement price in signals.** A signal uses the close of bar S_p - 1, the last price at S_p, and never the open
   of the bar it fills on. Reason: the engine's clock (decide at a bar's close, fill at a later bar's open).
2. **No forward fill.** A required bar that is absent excludes the unit, counted. Reason: no price is invented.
3. **H1 and H4 reference date.** The reference is the immediately preceding group trade date; it may be a
   roll-blackout date, and it must be the same contract. Reason: a one-day horizon, with no roll gap in a signal.
4. **Rolls inside multi-day holds** are made at the splice, each leg paying the full D8 cost. Signals chain across
   splices. Reason: dropping roll months would have cut a third of H2 and most month-end 2- and 5-year auctions.
5. **The store boundary.** 2019-05-01..05-03 are in neither store. A date in both stores is refused, and a unit
   spanning the boundary is excluded. Reason: decidable before data, and no date is double-counted.
6. **Risk scaling.** Sigma is the sample std of the last 20 hypothetical gross per-trade P&Ls (per leg for H2, per
   tenor for H3), with warm-up per product. Reason: the prompt's words, made computable without look-ahead.
7. **H2's decision minute** is max(S_NQ, S_ZN): 15:15 before 2020-10-26, 15:00 after. ZN enters at that minute;
   each leg exits at its own S on dL; ties fall to the prompt's else branch. Reason: both month-to-date returns are
   known only then.
8. **H5's grid and scaling.** The grid is the union of the components' dates. H5 is the mean of x/sigma over the
   components with a defined sigma; the first 60 grid dates are warm-up. Reason: the prompt's equal-risk
   combination, made computable.
9. **The one-sided p** is the larger of the plain-t and Newey-West p. NW lags are H1, H4 and H5 5; H2 1; H3 3.
   Reason: a tightening, since H3's same-week auctions overlap.
10. **Year stability** with fewer than 3 qualifying years fails rather than passing vacuously. Reason: a tightening.
11. **Release calendars** use the frozen ones, with a conservative fallback that turned out to be unneeded (only FOMC
    touches, and it has 2010-2019 rows).
12. **HE's window starts 2017-07 under U2.** Its last unpriced month is 2017-06, so this is U2 applied literally;
    the planning chat's message named only TN and RTY.
13. **Settlement grades R-S1 to R-S6** (section 3).
14. **Overlap rulings R-O1 to R-O3.** In particular D4's S_X does not apply, so ZF and ZT are read from 2019-05.
15. **Calendar rulings R-C1 to R-C6.** Broker-hosted CME holiday PDFs and Cannon's images are accepted as
    secondary.
16. **Build rulings R-B1 to R-B5**, and the coder's choices 1 to 12, with 10 and 11 replaced.
17. **Review rulings:** F-04 option (a); F-09 kept; F-06's pin set, which leaves data/hist_calendar.py,
    pull_hist.py, hist_store.py and config.py unhashed for v12.
18. **Not committed:** the raw evidence pages (reports/stage_e16_briefs/pages/: CME-authored filings hosted by
    cftc.gov, broker pages, FiscalData responses). They stay on disk, as E.13's and E.14's pages; their sha256s are
    in the tables and logs.
19. **Lead spec amended before the freeze:** H2's minute set per date, H1 tied to lead_grade, the listing rule, and
    H3's F-04 sentence. The first version's sha256 (651f942d...) is in STATE.
20. **Timestamps** were corrected to the `date` readings: spawns at 00:16, not the 00:27 first written; the rulings
    at about 00:40-00:45.
21. **The usage limit** stopped the session at 02:10, after the freeze commit and the hand-off. It resumed at 11:58
    for Task 6 only.

## 7. Decisions for the user (the lead's recommendation first)

1. **H2's NQ entry after the 15:15 halt** (2012-11..2020-10; review F-09, kept as a stated departure). Recommend
   keeping it. Following the engine's closure-cancel would leave H2 about 15 units and no power. Any amendment must
   come before E.17's registration.
2. **H2 cannot pass on the fallback window** (2 qualifying years). Recommend that the E.17 prompt states before
   registration what happens if NQ's or ZN's extension (C1's purchase) is not bought: drop H2 and register four,
   with N + 4.
3. **Funds.** Recommend topping up acct-2 by about $218.06 before E.17: C1 $59.47, and the 21 roots $158.58 at
   E.12's quote x 1.03. The caps would then be about $291.08 (v11) and $447.93 (v12); the fresh quotes decide.
4. **HE's window from 2017-07 under U2.** Recommend accepting it: HE is one of 27 products in the pooled tests. The
   alternative is a user amendment before registration.
5. **LE 2010-2014 excluded from H1 and H4** (R-S3: weak source). Recommend accepting.
6. **Equity H1 2010-2020 trades 14:45-15:15**, past Topstep's 15:08 flatten (R-S6). Recommend keeping it, with the
   descriptive table without those product-dates.
7. **Power is low at the low priors** (H1 0.11, H3 0.09, H4 0.06 at 0.01) and useful at the high priors and for H5.
   Recommend proceeding: the cost is about $158 for the 21 roots and N + 5.

## 8. Session cost

Wall clock 23:05 (2026-10-08) to 12:15 (2026-10-09) PDT. Work time 2:57: 23:05-02:10 less the user pause
(23:45-00:10), plus Task 6 (11:58-12:15). The usage-limit wait (02:10-11:58, 9:48) is shown separately and not counted.

### Final ETA table (actuals; PDT; the initial estimate in brackets)

| # | Task / spawn | Owner | Model | Effort | Start | End | Time [estimate] | Tokens | Status and deviations |
|---|---|---|---|---|---|---|---|---|---|
| 0 | Startup: checks, start suite, spec, STATE, briefs | lead | opus | xhigh | 23:05 | 00:16 | 0:46 work [done by 00:25] | lead | done; suite 6740 passed |
| - | Pause: the user interrupted after the lead's three points; rulings U1-U3b | user | | | 23:45 | 00:10 | 0:25 (not work) | | pause |
| 1 | Settlement minutes | SettlementSource-OpusHigh | opus | high | 00:16 | 00:39 | 0:23 [1:30] | 23,306,834 | done; lead grades R-S1..R-S6 |
| 2 | Overlap audit | OverlapAudit-OpusHigh | opus | high | 00:17 | 00:28 | 0:11 [0:50] | 13,664,694 | done; keep all five |
| 3b | Livestock and EC-AUC calendars (+ F-04 follow-up 01:49-01:52) | CalendarBuilder-OpusHigh | opus | high | 00:16 | 01:07 | 0:54 [1:30] | 68,346,290 | done; both 2% checks pass |
| 3 | base_rules build, tests, probe, power (+ R-B 01:15-01:24, review fixes 01:49-02:04) | BaseRulesCoder-OpusXHigh | opus | xhigh | 00:16 | 02:04 | 1:21 [2:45] | 163,022,024 | done; merged twice |
| 3' | Rulings, merges, prereg, manifest (parallel with workers) | lead | opus | xhigh | 00:28 | 01:26 | in lead [0:50] | lead | done |
| 4r | Freeze review (+ recheck 02:05-02:09) | FreezeReviewer-FableXHigh | fable | xhigh | 01:26 | 01:46 | 0:24 [0:40] | 8,043,509 | APPROVE WITH FIXES, then APPROVE |
| 4 | Review rulings, fixes, manifest, commit 8f388c8 | lead | opus | xhigh | 01:46 | 02:09 | 0:23 [0:30] | lead | done |
| 5 | E.17 hand-off (drafted 00:18-00:20) | lead | opus | xhigh | 00:18 | 02:10 | in lead [0:25] | lead | done |
| - | Pause: usage limit | | | | 02:10 | 11:58 | 9:48 (not work) | | pause |
| 6 | End checks, end suite (0:16), return, progress, STAGES, commit | lead | opus | xhigh | 11:58 | 12:15 | 0:17 [0:50] | lead | done; suite 6815 passed |
| Total | Stage E.16 Part A | lead + 5 spawns | | | 23:05 | 12:15 | 2:57 work (23:05-02:10 less 0:25, plus 11:58-12:15) [estimate ~5:35] | 338,794,287 | no rerun; two pauses excluded |

### Tokens per model (this session's transcript and its 5 subagent transcripts, 2026-10-09 06:00Z to 19:16Z)

| Model | Input | Output | Cache read | Cache creation | Total |
|---|---|---|---|---|---|
| claude-fable-5-1 | 806 | 107,883 | 7,049,488 | 885,332 | 8,043,509 |
| claude-opus-5-5 | 1,912 | 1,117,668 | 325,639,490 | 3,991,708 | 330,750,778 |
| all | 2,718 | 1,225,551 | 332,688,978 | 4,877,040 | 338,794,287 |

Per spawn (agent file, model, effort, tokens):
- SettlementSource-OpusHigh: worker-high, opus, high, 23,306,834
- OverlapAudit-OpusHigh: worker-high, opus, high, 13,664,694
- CalendarBuilder-OpusHigh: worker-high, opus, high, 68,346,290
- BaseRulesCoder-OpusXHigh: worker-xhigh, opus, xhigh, 163,022,024
- FreezeReviewer-FableXHigh: worker-xhigh, fable, xhigh, 8,043,509

Delegation share: lead 62,410,936 (18.4%), workers 276,383,351 (81.6%). By tier: Opus 97.6%, Fable
2.4%. Cache reads dominate. Token counts are from the transcripts (reports/stage_e10_briefs/cost.py; raw output
reports/stage_e16_briefs/cost_raw.txt); the lead's last few steps after 19:16Z (the final commit and the worktree
removal) are not in them. These are token counts, not plan-credit percentages.
