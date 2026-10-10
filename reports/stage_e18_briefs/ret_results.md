## 3. Results per step

### Step 0: startup (11:41-11:48)

- Start checks (reports/stage_e18_briefs/start_checks.txt; section 2 quotes them): holdout all_ok, 0 unlocks;
  REGISTRATION.md 0 bytes; check_frozen ALL_OK; harness v12 preflight OK; cluster freezes K1-K8 OK; v2 freeze 91 files;
  N = 478; the spend ledger 36,402 lines (034a454b...); E.14's C1 freeze-inputs list: 43 entries, one mismatch, the
  harness manifest (replaced by v11 and v12 in E.17, the exception C1b's section 11 names); E.16 freeze OK.
- Start suite: 6913 passed, 3 failed, 3 skipped, 3 xfailed (11:47:32-12:05:36). The three failures
  (tests/test_harness_freeze.py, bytecode tests) came from the lead's invocation, not the code: PYTHONPYCACHEPREFIX was
  set for the suite, so bytecode left the tmp_path the tests inspect. The file rerun without it: 17 passed (12:16).
  The end suite used the prompt's exact command.

### Step 1: C1b's text and code (11:48-11:57)

- Text: reports/stage_e18_prereg_C1b.md, written by reports/stage_e18_briefs/make_c1b_text.py as 15 exact
  replacements on C1's freeze (each must match once; the script checks C1's sha256 first) plus a new section 13 listing
  every change. Final sha256 35b936fb33c32f29365cdd77ce1f8642330270a827795dac4059403d78075dcd (after the Step 2 fixes).
- Diff: reports/stage_e18_c1b_diff.md (generator make_diff_doc.py): the 16 changes classified by THE ONE FIX's items,
  the input-by-input table behind the exempt list, the code change, and the full `diff -u`.
  - Item 2 (C10's clause): "unless the feature is on the exempt list below"; the list is exactly g17_mbt (leg MBT:
    no contract listed on any date of the window; CME Micro Bitcoin futures launched 2021-05-03; BTC, listed from the
    trade date 2017-12-18, is not a leg of the model) and g17_cl (leg CL: listed, but NG's own cluster lead, never
    applicable on NG rows; E.12 reference 0, so a no-op). Decided from listing dates and section 2 only.
  - Item 3: "Every other feature keeps C10 exactly as C1 had it."
  - Item 1 and the bookkeeping it forces: ids C1b-T1/T2, N 478 -> 480 (sections 5, 6, 8), the closed attempt cited,
    C1b's steps without purchase (section 9), V31 (section 10), and two statements of C1 that E.17 made false:
    section 2's "no program file has read NG or any leg before 2019-05" (E.17's store builds, C1's stopped run and the
    base-rule batch read these stores) and section 11's "the harness differs from v10 only in data/config.py" (the
    prompt fixes v12, which also changes data/pull_hist.py, hist_store.py and hist_calendar.py).
  - The design change does not depend on the applicable-row counts E.17's stopped run printed (counts only, known to
    the lead): the exempt list follows from listing dates and section 2, and would be the same whatever they were.
- Listing evidence (reports/stage_e18_briefs/pages/LOG.md): two CME press releases saved raw (scrapling; curl got 403),
  verbatim: "today launched Micro Bitcoin futures" (May 3, 2021) and "effective on Sunday, December 17, 2017 for a trade
  date of December 18" (BTC). The older contracts' launch dates are marked [unverified].
- Code: new c1_replication/c1b.py (sha256 4f8ce49b...). It runs the frozen c1_replication.evaluate.run inside
  c1b_profile(), which swaps five evaluate attributes (TEST, TEST_IDS, HORIZON_OF, c10_check, preconditions) and
  restores them on exit or error. Its c10_check calls C1's function on the reference less the two exempt signals; its
  preconditions adds the C1b record (ids, exempt list) to the marker and result. Every C1 file is byte-identical.
  New tests/test_c1b.py (sha256 4d9394fb...): 74 tests, including every one of the 62 non-exempt covered signals
  still stopping, both exempt signals never stopping, C1's frozen rule stopping on the same reference, the profile
  restored after a run and after an exception, C1's registration not admitting C1b, and the CLI paths. 74 passed.

### Step 2: review (DiffReviewer-FableXHigh, 11:58-12:14)

- APPROVE WITH FIXES: 0 BLOCKING, 1 SHOULD FIX, 9 NOTE; all six checks PASS (scope of the diff; exempt list from
  listing dates and section 2; all 30 live signals' inputs traced, no third feature can meet the contradiction;
  the code does exactly clause 2; v12 changes nothing on the ext2010 evaluation path, get_plan("ext2010") equal on
  every v10 field; 101 tests passed).
- S-1 fixed (the criterion no longer says "as in training"); N-1, N-2, N-3, N-6 taken as text precision; N-4, N-5,
  N-7, N-8, N-9 no action (rulings R-1..R-5, reports/stage_e18_rulings.md). Text and diff regenerated 12:14-12:15.

### Step 3: dry check (12:16:02-12:16:05)

- reports/stage_e18_dry_check.md and .json (8b98a628...). The amended check on E.12's frozen reference against a
  synthetic world (synthetic bars for NG and the five legs over 2010-06-07..2011-09-30; CL and MBT as C1's sentinel
  frames; the pinned official 2010-2019 calendars; no store opened). Expected outcome written into STATE at 12:00:19.
- PASS, every case as expected: with every leg present C1b's check returns nothing while C1's frozen check returns
  g17_mbt (both horizons), reproducing E.17's contradiction; with NQ, ZN, 6E, GC or ZC removed, C1b's check stops on
  exactly that leg's g17 feature. All 28 non-exempt live features applied (smallest: k4_ngpre_mto, 39 rows).

### Step 4: freeze (12:17:07-12:17:35)

- reports/stage_e18_freeze.json, sha256 5ed208a21c2556e84830aca6fb7b2dba08a3012713f62de6e7bd1c57fb702d03: 13 C1b files;
  35 C1 inputs re-hashed against nine pins (C1's freeze, its inputs list, the E.12 state manifest, the model JSON, the
  v2 freeze, the Gate 0 list, the calendar and store hash files, the v12 harness manifest) plus the eight calendar
  files; 10 external items (both M1 payloads, the six ext2010 stores, the E.12 state copy of 51 files, q h60
  0.033735277284776724 and hF 0.0831931045522869). Verify mode OK at 12:17:22.
- Commit b714751 "C1b freeze" at 12:17:35 (37 files, explicit paths). Both freeze files tracked, no diff vs HEAD.

### Step 5: registration and the single evaluation (12:17:46-12:18:38)

- Harness v12 preflight OK; registered r003-C1b at 12:17:48: C1b ['C1b-T1', 'C1b-T2'], N 478 -> 480, freeze
  sha256 35b936fb... (reports/stage_e18_briefs/c1b_register.log; registry sha256 55b1d24c...).
- `python -m c1_replication.c1b` launched detached at 12:18:03 (nice 10); marker reports/stage_e18_c1b_RUN_ONCE.json at
  12:18:05; result reports/stage_e18_c1b_result.json at 12:18:38 (sha256 0b82091933a2b2b40e6cf52461437f7b8e4a6872f4444b8067fae993aebd6466;
  34.7 s wall, 2.05 GB peak, exit 0). Log reports/stage_e18_briefs/c1b_evaluate.log.
- C10 (amended): NG ok rows h60 5,120, hF 4,538; every non-exempt feature live in E.12 applies (g17 legs 4,231-4,858
  rows; k4_ngpre_mto 347/307 the smallest); g17_mbt and g17_cl 0, exempt. No stop. C11: feature_cols equal E.12's.

| Test | n trades | n dates | mean gross (per trade, ticks) | c (ticks) | bar 1.5c | t_B (per-date) | one-sided p | criteria met | decision |
|---|---|---|---|---|---|---|---|---|---|
| C1b-T1 (NG h60) | 814 | 557 | 0.585 | 1.708 | 2.562 | -0.831 | 0.797 | n >= 30 only | FAIL |
| C1b-T2 (NG hF) | 627 | 386 | -0.113 | 1.766 | 2.649 | -0.410 | 0.659 | n >= 30 only | FAIL |

- Verdict: FAIL (no test passes). For comparison, E.12's 2019-2024 Gate 0 rows were h60 mean 5.569 ticks, t_B 2.51,
  518 trades; hF 13.921 ticks, t_B 2.33, 494 trades.
- Descriptive (after the verdict; add nothing to N): share of ok rows at or above q: T1 0.159 (814 of 5,120), T2 0.138
  (627 of 4,538). Long/short: T1 121 long (mean +0.430 ticks) / 693 short (+0.612); T2 117 long (-4.436) / 510 short
  (+0.878). Trades per year (T1): 2010 1, 2011 101, 2012 99, 2013 94, 2014 85, 2015 90, 2016 98, 2017 96, 2018 127, 2019
  23. C14 (1.5x slippage): bars 3.527 (T1) and 3.657 (T2) ticks, not met.
- Note on the statistic: gate0._b_test's `mean` is the mean over trades, while t_B and p use per-date means (T1's
  per-date mean is negative while its per-trade mean is +0.585). The freeze's section 5 calls the statistic a per-date
  mean and criterion 1 "mean gross g". The verdict does not depend on the reading: both means are below 1.5c and
  p > 0.025 in both tests.
