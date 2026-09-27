# Brief: WindowsBackendCoder-OpusXHigh (Stage E.2b Task 5; worker-xhigh on opus)

Objective: build and test the Windows compute backend (user decision V10, 2026-09-26): ML training and backtests
(screening and confirmation runs) may run on the user's Windows PC when it is available, sent from this ThinkPad over
SSH, with results pulled back and checked by hash. The ThinkPad stays the default and every job must also run on it
unchanged. Also write the user's setup guide. You connect to, configure and run NOTHING on the Windows PC (it is not set
up; E.2c does that). Everything is tested against this machine only.

## Read first (by section)
- reports/stage_e2b_briefs/00_common.md (binding). compute/platform.py (the lead's interface; you now own compute/ and may
  extend platform.py without changing its existing functions' behaviour). screening/harness_freeze.py (the preflight, lead's;
  do not edit).
- docs/STAGE_E_ML_DESIGN.md M7 (esp. M7.4: research-window bars not readable by the training process; ML-A23 path
  allowlist) and M8 (compute), read-only. data/holdout.py (what is sealed and where; never unlock), data/config.py (where
  the Databento key and the ledger live).
- The other workers' reports as they appear (reports/stage_e2b_task1_runner_worker.md, ..._task2_ml_worker.md,
  ..._task4_purchase_worker.md): the cluster screening entry, the ML train job entry, the step 2 store layout.

## Facts about this machine
- There is NO SSH server here (openssh-server is not installed; port 22 refused). Do not install system packages, do not
  use sudo, do not edit ~/.ssh. For the localhost tests, run a user-level SSH server bound to 127.0.0.1 on a free high
  port inside a pytest fixture: asyncssh is the suggested library (a process_factory that execs the command, and an SFTP
  server so OpenSSH's scp/sftp work). You may add exactly one package, as a dev dependency (`uv add --dev asyncssh`), only
  after checking pyproject.toml already lists torch and lightgbm (MLPipelineCoder's dependency step is done); diff uv.lock
  and confirm no existing package's version changed (if one would, stop and report). Generate throwaway keys with
  ssh-keygen in tmp dirs; pass -i, -p, -o UserKnownHostsFile=<tmp>, -o IdentitiesOnly=yes to the system ssh client.
- The system client is OpenSSH (ssh -V above). The Windows side will be Windows OpenSSH Server, default shell cmd.exe
  (the guide may set PowerShell; your remote commands must work regardless: invoke `uv run --no-sync python -m
  compute.agent ...` with a working directory argument rather than shell syntax).

## Build (compute/)
1. compute/remote.py (the ThinkPad side) and a remote agent module (e.g. compute/agent.py) that runs on the far side:
   - code sync without any secret on the PC: the checkout arrives as a git bundle of the frozen harness commit sent over
     SSH (no GitHub credential on the PC); the agent verifies HEAD equals the expected commit and that
     screening.harness_freeze.preflight(expected_sha256) passes there, where the job spec carries the expected harness
     manifest sha256 given to remote.py on its command line (--harness-sha256); the send side runs the same preflight
     locally first (tests monkeypatch preflight or build a tiny manifest). Line
     endings: the checkout must be byte-identical (core.autocrlf false; decide whether a .gitattributes is needed and
     justify it in your report); the preflight catches any difference.
   - copies only the data a job is allowed, with a job manifest listing every file sent and its sha256, checked at both
     ends; runs the job at below-normal priority (compute.platform.lower_priority()) with a thread cap; polls for
     completion; pulls back the results and their sha256 manifest and verifies them; refuses results without hashes or
     with a mismatch. Records which machine ran the job (hostname, OS, CPU, GPU) in the job's result record.
   - resumable: a local job ledger (JSONL) of steps (sent, started, done, pulled, verified), skipped on restart; a job
     interrupted on the far side restarts from its own ledger.
   - process detachment that survives the SSH session ending: POSIX start_new_session for the localhost test; on
     Windows a documented method (Windows OpenSSH puts session processes in a job object; breakaway or a scheduled task
     are the candidates). Implement the Windows path, and list it in the E.2c checklist as unverified.
2. Data rules enforced in code (the send side refuses, and the agent re-checks): never send any sealed chunk (anything
   under the sealed stores or with the sealed suffix), any bar dated in holdout-1 (trade date >= 2026-06-22), holdout-2
   (2024-04-01..2025-03-31) or the March 2024 embargo (check a parquet's trade dates from its contents or metadata, not
   only its name), the Databento key (.env or any file whose bytes contain the key value; read the key locally only to
   scan and never log it), or the ledger (ledger/). ML training jobs get a data root holding only the training-window
   store; research-window stores go to a separate root that a training job cannot read (the agent refuses a training job
   whose data root contains anything but the training store). A planted forbidden file of each kind makes the runner
   refuse (tests).
3. Job kinds: a generic job spec (kind, module, args, data files, data-root kind) plus a synthetic job module for tests.
   Wire the real kinds (the cluster screening/confirmation entry and the ML train job) if their entry points are in the
   other workers' reports when you get there; otherwise report what is missing and the lead routes the wiring.
4. Cross-platform static check (a test): flags Linux-only calls in the files that run on the Windows PC: rules/, sim/,
   screening/, funnel/ (the parts Stage E runs), the data loaders and calendars in data/, ml_route/, compute/,
   strategy/stage_e/. Calls to flag: os.fork, os.nice outside compute/platform.py, fcntl, resource, signal.SIGKILL/SIGALRM,
   shell=True, bash/sh -c, /proc, /dev/shm, hard-coded /tmp, multiprocessing 'fork' context, and similar. Modules that by
   V10's design stay on the ThinkPad (purchases, sealing, the ledger: data/pull_*.py, data/holdout.py, data/spend_gate.py,
   data/quote_universe.py) may be exempted in a declared list with that reason. Fix flagged calls in files no active worker
   owns; for files owned by RunnerCoder, ScreenStatsCoder, MLPipelineCoder or PurchaseCoder2, list them in your report and
   the lead routes the fixes. No allowlist entry just to make the check pass.
5. Tests against this machine: the runner end to end over SSH to localhost (the user-level server) with a synthetic job,
   including an interrupted-and-resumed run, the forbidden-file refusals, hash-mismatch refusal on results, and a
   training job refused when a research-window file is in its root.
6. docs/WINDOWS_SETUP.md, the user's step-by-step guide: install Git, uv and Python via uv, the NVIDIA driver, and the
   OpenSSH server on Windows; add the ThinkPad's public key (administrators_authorized_keys if the account is an admin);
   get the repository onto the PC from the ThinkPad's git bundle; git config core.autocrlf false; set the power plan so
   the PC does not sleep during overnight runs; open the firewall for SSH on the home network only (private profile,
   local subnet); `uv sync` there; and the exact commands E.2c will run from the ThinkPad to verify it (a checklist,
   including everything that can only be verified on the real PC: CUDA torch on the RTX 2060 Super, detachment across
   SSH disconnect, below-normal priority, long paths, the probes repeated there). Nothing in the guide stores a secret on
   the Windows PC. Figures the user gave (Ryzen 5, 32 GB RAM, RTX 2060 Super 8 GB, 2 TB SSD) are to be measured in E.2c.
The V10 amendment itself (reports/stage_e2b_v10_amendment.md, docs/DECISIONS.md) is the lead's; do not write it.

## Ownership
You own compute/ (extend platform.py carefully), docs/WINDOWS_SETUP.md, tests/test_compute_*.py and
tests/test_cross_platform_static.py, and the asyncssh dev dependency only. Do not edit other workers' files (see above).

## Report
reports/stage_e2b_task5_windows_worker.md: the job flow and data rules at the top, the tests and what each proves, the
static check's findings (fixed, and routed to the lead), the E.2c checklist, and anything unfinished.
