# Stage E.16 hand-off to Stage E.17: C1, then the base-rule batch H1 to H5

Written by the E.16 lead (Task 5). Binding inputs: C1's freeze (reports/stage_e14_prereg_C1.md, sha256
afc5c10f628771afa3d1311192316ff3b4b681d7308d2b411fc655c15f821c0b, commit 1680982) and this stage's freeze
(reports/stage_e16_freeze.json, manifest sha256 5274aa97f3359d7dcfaae15cb0590b6147d1624e6056ea396df08c6215209ad4, commit 8f388c8). User rulings U1, U2,
U3a, U3b of 2026-10-09 (reports/stage_e16_rulings.md) apply. Nothing below is optional; a stop condition stops the
named part and the session continues with the rest where the order allows.

## 1. The order of events (U1)

Part 1, C1 under a caps-only harness (C1 freeze section 11):
1. Start checks (reports/stage_e16_briefs/checks.sh pattern: git state, holdout status all_ok with 0 unlocks,
   REGISTRATION.md 0 bytes, check_frozen, harness verify, cluster freezes, ledger lines and per-account totals, v2
   freeze, N = 471) and the full suite.
2. Verify C1's freeze by script first (C1 freeze section 11 step 1; reports/stage_e15_briefs/verify_freeze.py is
   the precedent; write its output to E.17's own briefs folder, never over E.15's files).
3. Verify this freeze: `uv run python reports/stage_e16_briefs/freeze_manifest.py verify --expected 5274aa97f3359d7dcfaae15cb0590b6147d1624e6056ea396df08c6215209ad4`
   and `git diff --quiet 8f388c8 -- base_rules tests/test_base_rules_*.py reports/stage_e16_prereg_*.md`.
   Any mismatch stops Part 2 (the base-rule batch); Part 1 may continue.
4. Confirm Databento acct-2 is unlocked (V29) with the fresh quote itself (step 5); no separate probe call.
5. Fresh quote of C1's plan under v10: `uv run python -m data.pull_step2 --quote-only --plan ext2010 --account acct-2
   --quotes-out <E.17 briefs>/quotes_ext2010.json` at nice 10, recording the ledger line count and the UTC start
   first. THE GUARD (V29, E.15): the fresh total is the sum of THIS run's own new ledger lines (every new line a
   quote event of the run's session on acct-2 with ts at or after the run start; exactly one successful quote per
   chunk of the plan's 642; the tool log saying "642 of 642 ... 0 failed"); the tool's JSON is never trusted, and
   `--retry-failed` is never used (it falls back to earlier sessions' successful lines). E.15's
   reports/stage_e15_briefs/fresh_quote_guard.py is the template. Stop C1 if the guard fails or if the fresh total x
   1.03 exceeds acct-2's headroom under the new cap.
6. Harness v11: the ONLY diff from v10 is data/config.py ACCOUNT_2_CAP_USD and E14_EXT2010_SESSION_CAP_USD (and the
   comments beside them) and the test assertions that pin those two values (C1 freeze section 11:
   tests/test_e14_config_v10.py:20,32-33; tests/test_e14_pull_hist.py:300; tests/test_stage_e_config_v8.py:62-64).
   ACCOUNT_2_CAP_USD = spent (231.599730 unless the ledger moved) + the fresh total x 1.03, rounded up to the cent
   (V27 set $291.08 from E.14's $57.742330 quote; the fresh quote decides); E14_EXT2010_SESSION_CAP_USD = the fresh
   total x 1.03 rounded down to the cent, never above $60.00 (V27). Fable reviews the diff; full suite; commit.
7. Register C1 (screening.trial_registry; N 471 -> 473), buy, build the six ext2010 stores, evaluate once
   (c1_replication/README.md "Commands, in order"). C1's evaluation completes before step 8.

Part 2, the base-rule batch (this freeze):
8. Harness v12, written only after C1's evaluation (U1). Its diff, nothing else:
   - data/pull_hist.py: a new hist plan named exactly "ext2010h" (FIXED by this freeze: base_rules/store.py accepts
     only "ext2010" for NG NQ ZN 6E GC ZC and "ext2010h" for the other 21; review F-01), test label "E16", test ids
     E16-H1..E16-H5 (FIXED: ruling R-B4; the buy requires them registered), holding, for each of the 21 roots, the
     monthly chunks of `<ROOT>.v.0` from its U2 start month through 2019-04 (end exclusive 2019-05-01), exactly as
     reports/stage_e16_windows.json lists them (1,993 chunks; per-root chunk lists, since TN, RTY and HE start
     later); `check_hist_chunk` refuses anything else. Store files are named
     `ohlcv-1m_<ROOT>_v_0_<first>_<last>_ext2010h.parquet` under `processed_hist/ext2010h/<ROOT>/`, last 2019-04-30,
     first at or before the root's window start, with "plan": "ext2010h" in the parquet metadata.
   - data/hist_calendar.py: accept the "livestock" group; data/calendars/hist2010/livestock.json = a byte copy of
     reports/stage_e16_calendars/hist2010_livestock.json (its sha256 is in this freeze).
   - data/hist_store.py: build plan "ext2010h" stores for the 21 roots (same per-root logic as "ext2010").
   - data/config.py: ACCOUNT_2_CAP_USD = spent after C1 + the fresh 21-root total x 1.03, rounded up to the cent; a new
     session id and session cap for the plan (the fresh total x 1.03 rounded down); tests pinning these values.
   - Tests for the new plan, calendar and store paths. Fable reviews v12 before any use; full suite; commit.
   - v12 must not change any file this freeze hashes (reports/stage_e16_freeze.json: among them
     screening/stage_e_engine.py, stage_e_frozen.py, stage_e_rules.py, stage_e_verdict.py, trial_registry.py,
     rules/products.py, rules/price_limits.py, data/stage_e_bars.py, data/hist_bars.py, data/group_session.py,
     data/session.py, the six hist2010 calendars by name and data/calendars/<group>.py). data/hist_calendar.py,
     data/pull_hist.py, data/hist_store.py and data/config.py are deliberately not hashed. If v12 must change a
     hashed file, Part 2 stops for a re-freeze under a new pre-registration; it is never patched around.
9. Fresh quote of plan "ext2010h" under v12, with the same guard as step 5 (its own session id; 1,993 chunks; the
   run's own new ledger lines; never the tool JSON; never --retry-failed). E.12's quote for these months was
   $153.965349 (x 1.03 = $158.584309); the fresh quote decides. Stop Part 2 if the guard fails or the total x 1.03
   exceeds the headroom.
10. Register H1..H5 (N + 5: 473 -> 478 after C1). At registration, write the per-product fallback list (prompt:
    a product whose extension cannot be bought runs on 2019-05-06..2024-02-29) from the fresh quote and the funds,
    before any purchase; any product whose purchase or store build then fails is added to the list, with the reason,
    before any test bar is read. Record the list's sha256 in E.17's STATE.
11. Buy the 21 roots (`--buy --plan ext2010h --account acct-2 --harness-sha256 <v12>`), settle deltas checked
    (billed above quote by more than 3% stops, as data.pull_hist does).
12. Build the 21 ext2010h stores (data.hist_store) and write the base-rule run manifest (root -> {path, sha256, plan} of its ext2010 or ext2010h store from the
    build summaries; root -> E.12 step-2 store path and sha256 from E.12's start-rule
    file), its sha256 into E.17's STATE before any run.
13. The five runs, once each, in the order H1, H2, H3, H4, H5 (`uv run python -m base_rules.run run --test H1 --freeze reports/stage_e16_freeze.json --freeze-sha256 <freeze sha>
    --manifest <run manifest> --manifest-sha256 <sha>`, then H2, H3, H4 the same, then `run --test H5 --freeze ...
    --freeze-sha256 <sha>` (H5 reads no bar; it combines the four complete component results), then `uv run python -m
    base_rules.run verdict --freeze reports/stage_e16_freeze.json --freeze-sha256 <sha>` over all five (no `--tests`
    subset: the family is the five registered tests). Registration first: `screening.trial_registry register --test E16
    --ids E16-H1 E16-H2 E16-H3 E16-H4 E16-H5` with this freeze's path and sha256 (base_rules/README.md "E.17
    commands"). The run manifest (schema stage_e16_run_manifest/1) maps each of the 27 roots to its ext2010 store (path,
    sha256; null = fallback window) and its E.12 step-2 store (path, sha256). Every input problem is refused (exit 2)
    before the run-once marker; exit 1 after the marker means the attempt is closed and the test is reported as
    STOPPED, never rerun). Each writes its run-once marker
    before reading a bar and refuses a second run.
14. Holm across the five, the verdicts written against the prompt's pass bar (base case), the stress case (U3a) and
    the 1.5 x slippage case reported, DSR at N.
15. Fable recomputation (fable, xhigh) of every number entering a verdict, from the run outputs and the stores,
    by an independent script.
16. After all verdicts: descriptive research-window figures only if the stage prompt asks, marked descriptive,
    adding nothing to N. Holdout-2 stays sealed.

## 2. Purchase list (21 roots; E.12's quote record and ledger lines over each root's U2 window)

| Root | U2 start month | Chunks (start..2019-04) | E.12 quoted $ | x 1.03 $ |
|---|---|---|---|---|
| 6A | 2010-07 | 106 | 10.682692 | 11.003173 |
| 6B | 2010-07 | 106 | 10.170910 | 10.476037 |
| 6C | 2010-07 | 106 | 9.812140 | 10.106504 |
| 6J | 2010-07 | 106 | 10.859810 | 11.185604 |
| 6N | 2010-07 | 106 | 7.598356 | 7.826307 |
| 6S | 2010-07 | 106 | 8.668967 | 8.929036 |
| CL | 2010-07 | 106 | 11.023248 | 11.353945 |
| HE | 2017-07 | 22 | 0.454877 | 0.468523 |
| HG | 2010-07 | 106 | 10.084233 | 10.386760 |
| LE | 2010-07 | 106 | 3.127273 | 3.221091 |
| RTY | 2017-06 | 23 | 1.902238 | 1.959305 |
| TN | 2016-01 | 40 | 2.791587 | 2.875335 |
| UB | 2010-07 | 106 | 7.218561 | 7.435118 |
| YM | 2010-07 | 106 | 10.502610 | 10.817688 |
| ZB | 2010-07 | 106 | 9.232754 | 9.509737 |
| ZF | 2010-07 | 106 | 9.091797 | 9.364551 |
| ZL | 2010-07 | 106 | 6.223149 | 6.409843 |
| ZM | 2010-07 | 106 | 5.659884 | 5.829681 |
| ZS | 2010-07 | 106 | 6.931452 | 7.139396 |
| ZT | 2010-07 | 106 | 6.041231 | 6.222468 |
| ZW | 2010-07 | 106 | 5.887580 | 6.064207 |
| Total (21) | | 1993 | 153.965349 | 158.584309 |

C1's six roots (NG, NQ, ZN, 6E, GC, ZC) come from C1's ext2010 plan (Part 1); the H tests use them from 2010-07-01 (U2). Source: reports/stage_e16_windows.json (derive_windows.py).

## 3. Funds per step (acct-2; acct-1's $1.609980 fits no root)

| Step | Needs | At E.12/E.14 prices | Cap after |
|---|---|---|---|
| Today | spent 231.599730, cap 249.67, headroom 18.070270 | | 249.67 |
| C1 (steps 5-7) | fresh C1 total x 1.03 | E.14: $57.742330 x 1.03 = $59.474600 | v11: spent + that, about 291.08 |
| Base-rule batch (steps 9-11) | fresh 21-root total x 1.03 | E.12: $153.965349 x 1.03 = $158.584309 | v12: spent after C1 + that, about 447.93 |
| Both | | $211.707679 x 1.03 = $218.058909 | |

The user funds acct-2 for both before E.17 (the account's credit must cover the cap; the caps only guard).

## 4. What E.17 must not do

No parameter of H1..H5 changes after this freeze; no test runs twice; holdout-2, the embargo, MES's sealed stores,
the research window and anything from 2026-06-21 are never read by a test; no ML, network or RL layer (V28); the
base cost case decides the pass, the stress case is must-survive only at a later holdout-2 registration (U3a).

Notes from the freeze recheck: E.17's Fable recomputation asserts that every output records the registry path ledger/trial_registrations.jsonl (R-2); the runtime probe (H1 4:32, 1.2 GB peak) predates the review fixes, so check free memory before each run and expect a higher peak (R-3).
