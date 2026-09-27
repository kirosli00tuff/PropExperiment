# Stage E.2b Task 5: the Windows compute backend (WindowsBackendCoder-OpusXHigh)

Worker: opus, xhigh. Started 13:08 PDT, finished 14:00 PDT on 2026-09-26. Brief:
reports/stage_e2b_briefs/task5_windows.md. Nothing was run on the Windows PC. Every test ran on
this ThinkPad against a user-level SSH server on 127.0.0.1. The holdout status at the end was
`unlocks_logged: 0` for both holdouts, and REGISTRATION.md is 0 bytes.

## 1. The job flow

`python -m compute.remote submit|resume|status|sync-code|sync-env|machine` runs on the ThinkPad.
`python -m compute.agent` runs on the far side from `<agent_root>/checkout`, launched as
`uv run --directory <agent_root>/checkout --no-sync python -X utf8 -m compute.agent ...`, with no
shell syntax. The local ledger is `<state-dir>/<job_id>/ledger.jsonl`. A restart skips every
step already recorded in it.

1. **prepared** (ThinkPad):
   - `screening.harness_freeze.preflight(--harness-sha256)` runs on the working tree.
   - Every data file passes compute.datarules (section 2).
   - The frozen commit is exported (section 3, D1) and every blob of the export is checked.
   - The exported tree is materialized and passes the same preflight before anything leaves.
   - Written to the ledger: the job spec (`job.json`: kind, arguments, data files with sha256,
     threads, harness sha256, source and export commits), the local preflight's sha256 and the
     excluded paths.
2. **code_synced**:
   - The bundle goes over SFTP. The far checkout is cloned or fetched, then checked out at the
     export commit (`checkout --force`, then `clean -fd`).
   - The agent's `verify-code` confirms three things: HEAD is the export commit and every
     tracked file's raw bytes equal its blob; the installed numpy, pandas, pyarrow, lightgbm,
     torch and scikit-learn versions equal uv.lock's; preflight passes there.
   - The per-job bundle is then deleted; it can be rebuilt deterministically.
3. **sent**:
   - `job.json` goes over first. The agent's `inventory` reports which data files are already
     present with the right sha256 (preflight runs first). Only missing or different files are
     uploaded, each to `incoming/*.partial` and then renamed into place.
   - The agent's `receive` re-checks each file (sha256, data rules) and the job's whole data
     root, then writes `received` to the far ledger.
4. **started**:
   - The agent's `start` checks the code and preflight again, and refuses if another job is
     running (V10-7, one heavy job at a time).
   - It writes `started` with a fresh token, then starts the detached worker. The method comes
     from the host config: `posix_session`, `windows_breakaway` or `windows_schtasks`.
   - The worker lowers its priority (`compute.platform.lower_priority()`), re-checks the code,
     preflight and data, and records the machine.
   - It then runs the kind's module with `thread_env(threads)` and `PYTHONUTF8=1`, at
     BELOW_NORMAL on Windows.
   - It touches `heartbeat-<token>` every 2 s. A restart that supersedes it makes the old worker
     stop its job and exit without writing `done`.
5. **done**:
   - The ThinkPad polls `status`. A stale heartbeat (default 30 s; at least 6 s) makes it call
     `start` again, at most 3 times. The far ledger records `restarted`, and the job resumes
     from its own progress files.
   - The worker writes `result/record.json` and `result/manifest.json` (sha256 of every result
     file). It then writes `done` with the exit code and the manifest's own sha256 to the far
     ledger.
6. **pulled / verified**:
   - `sftp get -r` fetches `result/` into staging.
   - The manifest's sha256 must equal the far ledger's `done` value, and every file must match
     the manifest. A missing file, an extra file or a file without a hash refuses the result.
   - `record.json` must name this job, its export commit, its spec sha256 and its harness
     sha256. Only then do the results move to `<state-dir>/<job_id>/results/`.
   - The record names the machine: host name, OS, CPU, logical cores, memory, GPUs with driver
     and CUDA versions (nvidia-smi), Python and package versions (V10-3).

The far layout is `<agent_root>/{checkout, incoming, data/training/<ROOT>/, data/backtest/{research,step2}/<ROOT>/, jobs/<id>/}`.
The agent derives the agent root from its own checkout, whose directory must be named
`checkout`.

## 2. The data rules (compute/datarules.py)

The send side refuses before any byte leaves. The agent re-checks every rule except the key scan
(see "key" below).

| Rule | Kind named in the refusal |
|---|---|
| inside data/sealed/ (DataRules.sealed_roots) or any directory named `sealed` | sealed-store |
| a `*.sealed` name | sealed-suffix |
| bytes starting with data.holdout's MAGIC, under any name | sealed-content |
| `.env` / `.env.*`, or the repository's .env | secret-env |
| bytes containing the Databento key (send side; key read locally, never logged or stored) | secret-key |
| ledger/, data.config's external ledgers, any `*spend*.jsonl` | ledger |
| name not in the two store allowlists (step 2 `ohlcv-1m_<R>_v_0_2019-05-06_2024-02-29_step2.parquet`, research `..._2025-04-01_2026-06-19_research.parquet`), or a store the data root does not take | not-allowlisted |
| a trade_date label in holdout-1, holdout-2 or embargo-2 (data.research_bars.trade_date_class) | holdout-date |
| a label outside the store's window (step 2 2019-05-06..2024-02-29, research 2025-04-01..2026-06-19) | outside-window |
| metadata `trade_date_range` missing or different from the rows; a step 2 file whose metadata `store` is not `step2` | metadata |
| every row's ts_event booked by its product's CME group calendar with the Stage E loader's own `data.stage_e_bars.check_bookings` (ruling L-9) | holdout-date / outside-window / unbookable / label-mismatch / unknown-product |

Training versus backtest roots (V10-5, M7.4, ML-A23):
- A training job's root (`data/training`) takes step 2 files only, at `<ROOT>/<step 2 name>`.
  The agent walks the whole root and refuses anything else with kind `training-root`, including
  another store's file, a partial upload, a stray file or a nested directory.
- Research and step 2 files for backtests go to `data/backtest/{research,step2}/`, which a
  training job is never given.

The key on the far side: the agent never holds the key, so it cannot rescan for it. Its re-check
is the sha256 binding. Every received file must equal, byte for byte, the file the send side
scanned.

## 3. Decisions and deviations (for the lead)

**D1. Export commit instead of a bundle of the frozen commit itself.** `ledger/databento_spend.jsonl`
is tracked in git. A bundle of the frozen commit would carry the ledger and its whole history,
which breaks "never send the ledger". compute/gitbundle.py therefore takes the frozen commit's
tree minus `ledger/` and commits it as a parentless commit with a fixed author, committer and
date. The same frozen commit always gives the same export commit (tested). The export message
names the source commit, and the job spec carries both ids.
- The agent verifies HEAD == export commit, that the message names the source commit, and the
  byte-for-byte checkout.
- Preflight then gives the harness guarantee.
- No history travels.
- Every exported blob is checked first: no .env, no key bytes, nothing sealed, no
  parquet/dbn/zst.
- The export is built in a scratch bare repository that borrows the source repository's objects
  read-only (alternates). The source repository's refs, index and tree are untouched (tested).

The lead should confirm this reading of "a git bundle of the frozen harness commit".

**D2. No .gitattributes.** It is not needed, and adding one would change a tracked repo-wide file.
- The agent clones with `core.autocrlf=false` and `core.longpaths=true` in the clone's own
  config.
- It writes `.git/info/attributes` = `* -text -filter -ident -working-tree-encoding`. That file
  takes precedence over every .gitattributes and the global core.attributesFile, so no
  conversion applies whatever the PC's Git settings are.
- `verify-code` then hashes every tracked file's raw bytes as a git blob and compares them with
  the commit. Git's own status would hide a CRLF conversion, so it is not used.
- A far checkout with a converted file refuses: tested with a CRLF-converted `compute/files.py`,
  which the next sync then repairs.

**D3. Calendar booking, not only labels.** data/stage_e_bars.py documents that MBT's research file
holds 1,617 bars labelled 2026-06-18..20 that CME books to 2026-06-22 (holdout-1). A
label-only check would have sent them. The backend therefore runs the loader's own
`check_bookings` on every file.
- The same function runs on both ends.
- It needs a real product root, so synthetic tests use ES, NQ and MBT.
- Consequence: MBT's research store as built can never go to the PC. The loader refuses the MBT
  leg on the ThinkPad as well.
- An ES bar past the calendar's coverage (Sunday 2026-06-21) is refused as unbookable (fail
  closed).

**D4. Static check scope.** "The parts Stage E runs" is taken as follows:
- all of compute/, ml_route/ and strategy/stage_e/;
- plus every module of rules/, sim/, screening/, funnel/ and data/ in the static import closure
  (function-level imports included) of compute.agent and each job kind's module;
- minus a declared list of ThinkPad-only modules, each with its reason.

The exemptions:
- the brief's purchases, sealing and ledger modules: data/pull_mes, pull_universe, pull_step2,
  pull_step2_report, quote_universe, holdout, spend_gate;
- data/step2_seal.py (sealing);
- **data/build_bars_run.py**: the research-store builder's CLI. It reads raw vendor files, which
  never travel, and only data.build_bars.cli imports it, lazily. This entry goes beyond the
  brief's list. Removing it makes 5 findings fail. It is one of data/build_bars.py's
  BUILDER_FILES, whose sha256 is stamped into the research stores' metadata, so I did not edit it.

Text-file encodings fail the check only in compute/ (the agent's own process). Elsewhere every
process the backend starts on the PC runs in UTF-8 mode: `-X utf8` for the agent and
`PYTHONUTF8=1` for the worker and jobs. They are reported below.

**D5. `uv add --dev asyncssh`.** It was run after checking that pyproject.toml lists
torch==2.14.0 and lightgbm==4.7.0.
- First `--no-sync`: the uv.lock package table diff added asyncssh 2.24.0, cffi 2.1.1,
  cryptography 50.0.1 and pycparser 3.0, removed nothing and changed nothing.
- Then the synced run: installed versions before and after differ only by those 4 packages.
- pyproject.toml's dev group gained `asyncssh>=2.24.0`.

**D6. compute/platform.py extended** with `priority_label()` and `total_memory_bytes()`. The
existing functions are unchanged. platform.py is the one module allowed POSIX branches (os.nice,
os.sysconf).

**D7. Test helper** tests/_compute_fixtures.py sits outside the brief's `test_compute_*.py`
pattern. It is test-only, following the tests/_stage_e_synthetic.py precedent.

## 4. Files

New:
- compute/agent.py (412 lines), compute/remote.py (526), compute/datarules.py (345),
  compute/gitbundle.py (228), compute/transport.py (194), compute/jobspec.py (191),
  compute/machine.py (121), compute/detach.py (115), compute/files.py (111),
  compute/ledger.py (89), compute/synthetic_job.py (58);
- docs/WINDOWS_SETUP.md;
- tests/_compute_fixtures.py, tests/test_compute_units.py, tests/test_compute_datarules.py,
  tests/test_compute_remote_e2e.py, tests/test_cross_platform_static.py.

Modified: compute/platform.py (D6), pyproject.toml and uv.lock (D5). No other worker's file was
edited, and nothing under screening/ or ml_route/.

**The harness manifest must list the 11 new compute/*.py files.** compute/ is a HARNESS_DIR,
so preflight refuses unlisted ones.

## 5. Tests (125; 124 pass, 1 fails by design until a routed fix lands)

Final run: 13:56 PDT, through heavy.sh:
`pytest -q tests/test_compute_units.py tests/test_compute_datarules.py tests/test_compute_remote_e2e.py tests/test_cross_platform_static.py`.
Results: units and data rules 97 passed; e2e and static 27 passed, 1 failed (4.6 s and 74 s).
`--cov=compute` gives 84% in-process line coverage. Far-side code also runs in subprocesses in
the e2e tests, which this figure does not count. ruff is clean on every new file.

**tests/test_compute_datarules.py (36)** proves:
- clean step 2 and research files pass;
- each forbidden kind is refused on the send side with its named kind (14 parametrized cases):
  sealed store, any `sealed` directory, sealed suffix, sealed bytes under a clean name,
  holdout-1, holdout-2, embargo, a clean name and metadata over holdout rows, .env, a .env
  variant, key bytes inside a store file, the ledger, a spend-ledger copy, an external ledger;
- refusals name the holdout class;
- out-of-window bars are refused, including M7.4's planted research-window bar in a step 2 file;
- metadata mismatch is refused;
- undated, unreadable and misnamed files are refused;
- the L-9 cases: MBT 2026-06-19 12:00 CT labelled 06-19 is refused as holdout-1; unbookable,
  label-mismatch and unknown-product are refused;
- a training root takes step 2 only;
- the far-side training root is refused for each of 7 plants: research file, step 2 name with
  research rows, partial upload, stray file, nested directory, wrong folder, sealed blob;
- the backtest root layout is enforced;
- the key scan works across a chunk boundary;
- default rules name the real data/sealed, ledger and .env;
- constants are pinned to data.holdout.MAGIC, data.step2_store, data.build_bars and
  ml_route.store names and windows.

**tests/test_compute_units.py (61)** proves:
- job spec: round trip and canonical sha256; placeholder filling; 15 validation refusals
  (backend options in the sender's arguments, placeholders, bad ids, threads, data root per
  kind, duplicate destinations...); a foreign module is refused;
- the wired kinds' fixed options exist in screening.stage_e_runner's, ml_route.train fit's and
  ml_route.probes' own parsers (`--help`);
- ledger: a torn tail line is dropped and marked, and a corrupt middle line refuses;
- manifest problems name every difference;
- remote argument quoting passes cmd.exe and sh literally or refuses;
- host config validation, including a detach method for the wrong OS;
- sftp batch lines;
- detach flags (breakaway = 0x01004208), schtasks wrapper and argv;
- **a posix_session worker survives SIGKILL of its parent's process group while an undetached
  sibling dies**;
- machine record; environment versus uv.lock (and the real lock matches the venv);
- export: the ledger is cut; the export is deterministic; CRLF content is kept as committed; the
  source repository is untouched; the export refuses .env, .env variants, key bytes, `sealed`
  paths, `.sealed`, parquet, dbn.zst and sealed bytes under any name;
- far checkout: proven byte-identical; a CRLF conversion, a wrong HEAD and missing attributes are
  each caught;
- agent: receive, inventory and status state machine; a superseded token's late `done` is
  ignored; a tampered received file is refused (hash-mismatch); a reused job id is refused;
  busy refusal; runs only from a `checkout` directory;
- **every entry refuses when preflight raises**: agent verify-code, inventory, receive, start
  and run-worker (the worker records the refusal and never runs the job); remote submit, resume
  and the sync-code CLI (no transport call made);
- a missing key refuses sending; a research file for a training job is refused;
- the wait loop restarts stale workers at most 3 times and refuses a job the far side has no
  record of;
- results verify only when every file matches; 7 tamper cases are refused (changed byte, extra
  unhashed file, missing file, no manifest, swapped manifest, no recorded hash, record of
  another job).

**tests/test_compute_remote_e2e.py (23), over SSH to the localhost server with the system
ssh/sftp**, proves:
- a full synthetic training job: all 7 steps; nice 10; threads 2; this host recorded; the far
  checkout has no ledger/; the fake key appears in no far file; no per-job bundle is kept;
- a second job moves no code (no clone or fetch) and no data (uploaded 0, skipped 1);
- a backtest job gets its own root holding both stores, and the training root is untouched;
- **a ThinkPad-side interruption after `sent` resumes from the local ledger with no re-upload**;
- **a worker SIGKILLed mid-job on the far side is restarted from the far ledger after its
  heartbeat goes stale, and resumes its own progress**: 5 items, none computed twice,
  `restarts` 1;
- **the SSH server stops (every session's process group killed, as sshd does) while a job runs:
  the heartbeat continues, and a new server later pulls verified results with `restarts` 0**;
- **a far result file edited after `done` is refused (ResultRefused), and no results directory
  appears**;
- all 14 forbidden kinds are refused by the real runner with zero commands reaching the server;
- a CRLF-converted far checkout file makes `verify-code` refuse, and the next sync repairs it;
- **a training job is refused (`training-root`) when a research-store file is planted in its far
  root, and (`outside-window`) when a step 2-named file with research-window rows is planted**.

**tests/test_cross_platform_static.py (5)** proves:
- the scope holds the far side's entry points and the exemptions are real files;
- the scanner flags each call kind on a synthetic source, and correct forms pass;
- platform.py may branch but os.nice and os.sysconf elsewhere are flagged;
- compute/ opens every text file with an encoding;
- **no Linux-only call in the scope: fails on 1 finding routed to the lead (section 6)**.

## 6. The static check's findings

Fixed: compute/machine.py used `os.sysconf`. It moved into compute/platform.py as
`total_memory_bytes()`. No other in-scope finding was in a file I may edit.

**Routed to the lead (in scope, fails the test): `funnel/simulator.py:301`**, a
`ProcessPoolExecutor(workers, ...)` without `mp_context`. On Linux it forks, on Windows it
spawns. The fix is `mp_context=multiprocessing.get_context("spawn")`, with picklable
initializer arguments.
- The file is in reports/stage_d1f_harness_freeze.json, so I did not edit it.
- It is reached through screening/runner.py's imports. Whether a Stage E job calls it with
  workers > 1 was not traced.

Exempt with reason (D4): data/build_bars_run.py, 5 findings: `import resource` at module level,
three calls to `os.nice(10)`, and `/proc/meminfo`.

Outside the scope, reported only (E.2a one-off runners, not reached from any far-side entry
point):
- funnel/exposure_gate_mes.py: `os.nice`, four `/proc/` strings;
- funnel/exposure_gate_run.py: `os.nice` twice, `/proc/meminfo`;
- screening/vehicles_choice.py:220 and screening/vehicles_run.py:314: `os.nice`;
- sim/calibrate_costs.py: `os.nice`, and a hard-coded scratchpad `/tmp/...` path at line 75;
- two git-ignored data/vendor/release_pages/commodity_scripts/*.py: `/usr/bin/python3`.

Text files opened without `encoding=`: 27 in scope, informational because of UTF-8 mode (D4):
- data/build_bars.py 7, data/build_mes_bars.py 7, funnel/power_gate.py 5;
- data/adapter.py 2, data/build_bars_reports.py 2;
- data/config.py 1, data/splits.py 1, sim/costs.py 1, sim/engine.py 1.

Outside the scope there are 85 more.

Observation for the manifest:
- `harness_freeze.unlisted_python_files` walks `data/` recursively. On this ThinkPad that
  includes the git-ignored `data/vendor/release_pages/commodity_scripts/crawl_*.py`, so the
  ThinkPad-side preflight will refuse unless the manifest lists them or they move.
- The PC never has them, because the bundle carries tracked files only.

## 7. E.2c checklist

The checklist is in full at the end of docs/WINDOWS_SETUP.md, 18 items, all unverified. The items
that only the real PC can settle:
- SSH key-only login with the pinned host key.
- git, uv and nvidia-smi on the SSH session's PATH.
- cmd.exe accepting the backend's command lines, and Windows sftp resolving paths relative to
  the home directory.
- sync-code, sync-env and sync-code again, with byte identity.
- The measured CPU, RAM, GPU, driver (580 or later for torch 2.14.0+cu130) and SSD.
- CUDA torch on the RTX 2060 Super, via the `ml_probe versions` job.
- The lgbm and lstm probes repeated there. The A-1 batch size against 8 GB goes through V10-2.
- BELOW_NORMAL priority, both as reported and in Task Manager.
- **Detachment across SSH disconnect and `Restart-Service sshd`: `windows_breakaway` first,
  `windows_schtasks` if breakaway is refused. Also check whether a schtasks task runs with the
  user signed out.**
- Far-side kill and reboot, each followed by a resume.
- Long paths.
- The training-root canary on the PC.
- The busy refusal.
- A result-tamper refusal.
- The firewall set to the Private profile and LocalSubnet.
- No .env, ledger or credential on the PC.
- Power settings, and `check-attr text` reading unset.

## 8. Open questions (lead)

1. D1: confirm the export-commit reading.
2. Should the holdout manifests (docs/HOLDOUT_MANIFEST.json, docs/holdout2/*, which carry
   `salt_hex`) and docs/HOLDOUT_UNLOCK_LOG.md also be cut from the export? They travel today.
   The sealed blobs never do, so the salt alone decrypts nothing on the PC.
3. **ML finalize is not wired as a far-side kind.** `ml_fit` jobs each return their own
   `results/out` (candidates/<ch>_<h>.json, ledger, models). `finalize` reads no bars and can run
   on the ThinkPad over the six verified fit outputs, but how to merge them into one `--out-dir`
   is for the lead and MLPipelineCoder to decide. The same applies to any ML ledger file shared
   across fits.
4. M7.4 says research-window bars are "not on disk for the route's process at all during
   training". V10-5 as written (separate roots plus the ML-A23 allowlist) is implemented, but a
   backtest root on the PC may hold research stores while a training job runs. If the literal
   reading is wanted, the agent can also refuse a training job while `data/backtest/research`
   holds files. That is a small change and a new choice, so I did not make it.
5. After a result is refused, re-running is manual: submit a new job id (V10-6 "the job is run
   again").
6. Accept or reject the data/build_bars_run.py exemption; route the funnel/simulator.py fix.

## 9. Commands run (summary)

- `uv add --dev asyncssh --no-sync`, then `uv add --dev asyncssh`, with lock and installed
  version diffs (D5).
- A prototype localhost job (scratch): verified in 7.8 s.
- The pytest runs listed in section 5, through `reports/stage_e2b_briefs/heavy.sh`, each about
  75 s, each at under 1 GB of RAM.
- `ruff check` on the new files.
- `python -m data.holdout status`: unlocks_logged 0 and 0.
- No git command changed the tree. There was no Databento call, no TopstepX reference and no
  access to sealed data. No Stage E bar parquet was opened; every test file is synthetic.

## 10. Unfinished

- Nothing in the brief's build list is left undone on this machine.
- Everything Windows-specific is unverified until E.2c: the breakaway and schtasks paths, the
  Windows priority class, cmd.exe quoting, Windows sftp paths, and CUDA on the PC.
- The real kinds (`screening`, `ml_fit`, `ml_probe`) are wired by registry and checked against
  their parsers only. No real-data job was run, as the rules require.
- The static test fails until the lead resolves funnel/simulator.py:301.
