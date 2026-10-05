# c1_replication: test C1, the backward NG replication (Stage E.14)

The code of test C1 (reports/stage_e14_prereg_C1.md; annex reports/stage_e13_ng_replication_draft.md,
rulings C1-C21). It is hashed into C1's freeze. It never edits a frozen module: ml_route_v2/ (constants.py
byte-identical), data/, rules/, screening/, strategy/, sim/ are imported and called unchanged. Every step
verifies E.12's v2 freeze manifest (reports/stage_e12_ml_v2_freeze.json, pinned sha256) before it runs.

## Modules

| Module | What it does |
|---|---|
| constants.py | Every C1 parameter: tests C1-T1 (NG h60) and C1-T2 (NG hF), window 2010-06-07..2019-04-30, the pass bar (1.5 c, one-sided p <= 0.025, n >= 30), C12's 2% stop, Rule H-1's 30-minute lead, pinned sha256s of E.12's v2 freeze, Gate 0 report and list, output paths. |
| guards.py | The E.12 state manifest check (45 OOF splits, meta, 2 pickles, phase1_build.json, nothing else), the v2 freeze check, a temporary ledger copy, and the no-fit guard around Gate 0's reload. |
| q_m1.py | Part 1: reproduce E.12's NG h60 and hF family B rows from the persisted OOF splits (no fit), q_h = min abs(r_hat) of NG's Gate 0 trades, the single M1 ridge fit per horizon (fitted twice, same sha256 required), C10's reference counts; writes the model JSON and the payloads. |
| tables.py | The 2010-2019 tables from the calendar files: NG's D8 release calendar, the K4 NGS table less C13's drops, the unsourced release dates, the energy full sessions (checked against the rule recomputed on the energy calendar), the Topstep rows by Rule H-1. |
| context.py | ``hist_tables``: swaps the module attributes where the frozen code reads a 2019+ calendar or table for the replication's, restores every original object on exit, clears the calendar caches on entry and exit. The list of patches is in its docstring. |
| exclusions.py | Ruling C12 from the calendars alone: the NG candidate dates, the excluded ones with reasons, the share, the 2% stop. |
| world.py | The Phase1World-shaped world (NG only, six legs compacted one at a time, CL and MBT sentinel frames, D8 releases, frozen costs, roll blackouts, C12 dates in NG's own excluded set) and E.12's panel call. |
| evaluate.py | Part 2: preconditions (refusals, nothing written), the run-once marker before any bar, the world and panel inside the context, the C11 and C10 guards, trades, gate0._b_test's statistic, the verdict, then the descriptive outputs. |

## Commands, in order

Stage E.14, after the freeze commit (the lead; no 2010-2019 byte exists):

```
uv run python -m c1_replication.q_m1 \
    --state ~/.cache/propexp_e14_c1/e12_state_copy \
    --state-manifest reports/stage_e14_c1_e12_state_manifest.json \
    --state-manifest-sha256 8a38eeb150ba7c063e1f7b4292b00efb0bd10549c61e8202fcb926bc8dab1ad9 \
    --out reports/stage_e14_c1_model.json \
    --model-dir ~/.cache/propexp_e14_c1/m1
```
Exit 0: the model JSON is written (record its sha256, q_h60, q_hF and both payload sha256s in STATE).
Exit 3 "C1 STOP: q reproduction mismatch": nothing written; C1 stops. Exit 2: an input refusal, nothing written.
It reads ledger/ml_v2_config_ledger.jsonl through a temporary copy (the real file's sha256 is checked
unchanged), and never writes into the state dir (re-verified after the run).

The later session, under C1's freeze, in this order:

1. Register: `uv run python -m screening.trial_registry register --test C1 --ids C1-T1 C1-T2
   --freeze reports/stage_e14_prereg_C1.md --freeze-sha256 <sha> --harness-sha256 <sha>` (+2 on N then: 471 -> 473 if nothing else registered; C2 stopped in E.14 before its registration).
2. Quote, buy and build the six ext2010 stores (data.pull_step2 --plan ext2010, data.hist_store --plan
   ext2010), harness v10 or the later harness that differs from v10 only in data/config.py (ACCOUNT_2_CAP_USD, E14_EXT2010_SESSION_CAP_USD and the comments beside them) and in the test assertions that pin those two values (tests/test_e14_config_v10.py:20,32-33; tests/test_e14_pull_hist.py:300; tests/test_stage_e_config_v8.py:62-64), nothing else.
3. Write the two hash files (their sha256s go into that session's STATE before the run):
   - store hashes, `{"schema": "stage_e14_c1_store_hashes/1", "plan": "ext2010", "stores":
     {"NG": <sha>, "NQ": ..., "ZN": ..., "6E": ..., "GC": ..., "ZC": ...}}` from reports/hist/bars_<ROOT>_ext2010.json;
   - calendar hashes, `{"schema": "stage_e14_c1_calendar_hashes/1", "calendars": {"equity": {"path":
     "data/calendars/hist2010/equity.json", "sha256": ...}, ... six groups ...}, "releases": {"path":
     "reports/stage_e14_cal_releases.json", "sha256": ...}, "energy_full_sessions": {"path":
     "reports/stage_e14_cal_energy_full_sessions.json", "sha256": ...}}`, the files and sha256s C1's freeze names.
4. Evaluate once:
```
uv run python -m c1_replication.evaluate --harness-sha256 <sha> \
    --freeze reports/stage_e14_prereg_C1.md --freeze-sha256 <sha> \
    --model reports/stage_e14_c1_model.json --model-sha256 <sha> \
    --model-dir ~/.cache/propexp_e14_c1/m1 \
    --store-hashes <store hashes json> --calendar-hashes <calendar hashes json> \
    --out reports/stage_e14_c1_result.json
```
Exit 2: refused before the marker (nothing written, no bar read; the attempt is not used). Exit 0: PASS or
FAIL written. Exit 1: STOPPED written (C10, C11 after the marker, or any error after it); the attempt is
closed, never rerun. The marker is reports/stage_e14_c1_RUN_ONCE.json.

## Tests

`tests/test_c1_*.py` on synthetic data only (tests/_c1_state.py, tests/_c1_fixtures.py, v10's fixture store
builder): `uv run python -m pytest -q tests/test_c1_*.py` (75 tests, about 18 s).
