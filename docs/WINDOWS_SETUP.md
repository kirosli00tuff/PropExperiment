# Setting up the Windows PC for Stage E jobs (user decision V10)

Written in Stage E.2b (2026-09-26) with the Stage E compute backend in `compute/`. Nothing in
this guide has been run on the Windows PC yet: E.2c does that, and every item in the
checklist at the end stays **unverified** until E.2c has run it.

## What this is for

ML training jobs and backtests (a cluster's screening or confirmation run) may run on the
Windows PC when it is free. The ThinkPad stays the default, and every job must also run on
it unchanged. The ThinkPad keeps the Claude sessions, purchases, sealing, reviews and commits.
It sends each job over SSH with `python -m compute.remote` and brings the results back, checked
by sha256.

What goes to the PC:
- the code, as a git bundle of the frozen harness commit (no history, and without `ledger/`);
- the bar files a job is allowed: the step 2 store (training window) and the Stage E research
  store, each checked file by file.

What never goes to the PC: a sealed holdout chunk; any bar booked to a holdout-1 date (from
2026-06-22), a holdout-2 date (2024-04-01..2025-03-31) or the March 2024 embargo; the
Databento key or any other secret; the spend ledger. **Nothing in this guide stores a secret
on the PC.** The PC never needs a GitHub login.

Figures the user gave for the PC. E.2c measures each one (checklist item 4):

| Part | As given | Measured in E.2c |
|---|---|---|
| CPU | AMD Ryzen 5 | to measure |
| RAM | 32 GB | to measure |
| GPU | NVIDIA RTX 2060 Super, 8 GB | to measure |
| Disk | 2 TB SSD | to measure |

Commands marked **PC, admin PowerShell** run on the PC in a PowerShell window opened with "Run
as administrator". Commands marked **ThinkPad** run in the repository on the ThinkPad.

## 1. The Windows account that runs jobs

Use a dedicated local account, for example `propexp`, as a standard (non-administrator) user.
Jobs need no administrator rights, and a standard account keeps its SSH key in its own profile.
If you use an administrator account instead, its SSH key goes in a different file (step 6).

The account name must use only letters, digits, `.`, `_` or `-`, because the backend's host
config refuses anything else.

**PC, admin PowerShell** (you are asked for a password; this is a Windows login, stored by
Windows, not by the backend):

```powershell
$pw = Read-Host -AsSecureString "Password for propexp"
New-LocalUser -Name propexp -Password $pw -FullName "PropExperiment jobs"
```

Sign in once as `propexp` so Windows creates its profile (`C:\Users\propexp`), then sign out.

## 2. Git for Windows

**PC, admin PowerShell:**

```powershell
winget install --id Git.Git -e --source winget
```

In the installer, pick **"Checkout as-is, commit as-is"** for line endings, if it asks. Then,
as `propexp` (any PowerShell):

```powershell
git config --global core.autocrlf false
git config --global core.longpaths true
```

The backend also sets `core.autocrlf=false` in its own clone, writes `.git/info/attributes`
with `* -text` (which overrides every other attributes file), and proves every checked-out file
byte for byte against the commit. A line-ending conversion therefore makes jobs refuse; it never
changes a result silently.

## 3. uv and Python (as `propexp`)

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
uv python install 3.12
```

Open a new PowerShell window and check that `uv --version` works. The installer puts uv in
`C:\Users\propexp\.local\bin` and adds it to the user's PATH. SSH sessions must see that PATH
(checklist item 2).

## 4. NVIDIA driver

Install the current Game Ready or Studio driver for the RTX 2060 Super from nvidia.com or the
NVIDIA app. The pinned torch is `2.14.0+cu130` (CUDA 13.0 wheels), which needs driver
**580 or later**. Check the version in any PowerShell:

```powershell
nvidia-smi
```

The header shows the driver version and the highest CUDA version it supports.

## 5. OpenSSH Server

**PC, admin PowerShell:**

```powershell
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
Start-Service sshd
Set-Service -Name sshd -StartupType Automatic
```

The default shell stays `cmd.exe`. The backend works with either `cmd.exe` or PowerShell. It
sends only plain arguments (`uv run --directory <dir> --no-sync python -m compute.agent ...`
and `git -C <dir> ...`) and refuses any character either shell would reinterpret.

Allow keys only. In `C:\ProgramData\ssh\sshd_config`, set these lines (add them if missing):

```
PubkeyAuthentication yes
PasswordAuthentication no
AllowUsers propexp
```

Then run `Restart-Service sshd`.

### Firewall: SSH from the home network only

**PC, admin PowerShell.** First make sure the home network uses the Private profile:

```powershell
Get-NetConnectionProfile
Set-NetConnectionProfile -InterfaceAlias "<the interface shown above>" -NetworkCategory Private
```

Then limit the SSH rule to the Private profile and the local subnet:

```powershell
Set-NetFirewallRule -Name OpenSSH-Server-In-TCP -Profile Private -RemoteAddress LocalSubnet
Get-NetFirewallRule -Name OpenSSH-Server-In-TCP | Get-NetFirewallAddressFilter
```

## 6. The ThinkPad's key on the PC

**ThinkPad.** Create a key used only for the PC:

```bash
ssh-keygen -t ed25519 -f ~/.ssh/propexp_pc_ed25519 -C "thinkpad to pc, PropExperiment jobs"
cat ~/.ssh/propexp_pc_ed25519.pub
```

The backend runs ssh with `BatchMode=yes`, so the key must work without a prompt. Either leave
the passphrase empty (the key lives only on the ThinkPad), or load it into ssh-agent before
each session.

**PC.** Add the public key line, prefixed with `restrict`. This turns off port, agent and X11
forwarding and the pty; the backend needs none of them, and SFTP still works.

- **Standard account** (recommended): the file is `C:\Users\propexp\.ssh\authorized_keys`. As
  `propexp`:

  ```powershell
  New-Item -ItemType Directory -Force $HOME\.ssh
  Add-Content $HOME\.ssh\authorized_keys "restrict ssh-ed25519 AAAA...  thinkpad to pc, PropExperiment jobs"
  icacls $HOME\.ssh\authorized_keys /inheritance:r /grant "propexp:F" /grant "SYSTEM:F"
  ```

- **Administrator account**: Windows OpenSSH reads
  `C:\ProgramData\ssh\administrators_authorized_keys` instead. **Admin PowerShell:**

  ```powershell
  Add-Content C:\ProgramData\ssh\administrators_authorized_keys "restrict ssh-ed25519 AAAA...  thinkpad to pc"
  icacls C:\ProgramData\ssh\administrators_authorized_keys /inheritance:r /grant "Administrators:F" /grant "SYSTEM:F"
  ```

### Pin the PC's host key on the ThinkPad

**PC:** `ssh-keygen -lf C:\ProgramData\ssh\ssh_host_ed25519_key.pub` shows the fingerprint.

**ThinkPad:**

```bash
ssh-keyscan -t ed25519 <PC address> > ~/.ssh/known_hosts_propexp_pc
ssh-keygen -lf ~/.ssh/known_hosts_propexp_pc     # must equal the fingerprint shown on the PC
```

Give the PC a fixed address on the home router (a DHCP reservation), so the pinned address
stays valid.

## 7. The host config (ThinkPad, not in the repository)

Save this as `~/.config/propexp/pc.json`. It holds no secret, only paths to the key files.
Paths may not contain spaces.

```json
{
  "schema": "propexperiment-compute-host/1",
  "name": "windows-pc",
  "host": "192.168.1.50",
  "user": "propexp",
  "port": 22,
  "identity_file": "~/.ssh/propexp_pc_ed25519",
  "known_hosts_file": "~/.ssh/known_hosts_propexp_pc",
  "agent_root": "propexp",
  "remote_os": "windows",
  "detach": "windows_breakaway"
}
```

`agent_root` is relative to the PC user's home, so the PC side lives in `C:\Users\propexp\propexp\`:
- `checkout\` holds the code;
- `data\training\` holds the step 2 store only;
- `data\backtest\research\` and `data\backtest\step2\` hold backtest data;
- `jobs\<job id>\` holds each job's spec, ledger, heartbeat, logs and results;
- `incoming\` holds bundles and uploads in progress.

`detach` is how a job outlives the SSH session that started it (see step 10).

## 8. Power: no sleep during overnight runs

**PC, admin PowerShell:**

```powershell
powercfg /change standby-timeout-ac 0
powercfg /change hibernate-timeout-ac 0
powercfg /change monitor-timeout-ac 15
```

Before a long run, pause Windows Update restarts (Settings > Windows Update > Pause updates) or
set active hours to cover the run. A restart does not lose work: the job resumes from its
ledger and its own progress files (checklist item 10). It does cost the time since the last
checkpoint.

## 9. Long paths

**PC, admin PowerShell:**

```powershell
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name LongPathsEnabled -Value 1 -PropertyType DWORD -Force
```

The backend also clones with `core.longpaths=true`.

## 10. Getting the code and environment onto the PC

The code arrives as a git bundle made on the ThinkPad from the frozen harness commit, with no
history and without `ledger/`. Every file in the bundle is checked first: no `.env`, no blob
containing the Databento key, nothing sealed, no bar file. The ThinkPad drives every step.
The frozen commit and the harness sha256 come from the stage prompt.

**ThinkPad:**

```bash
H=<harness sha256 from the stage prompt>; C=<frozen harness commit>
S=~/propexp_jobs            # the local job state and results directory
uv run --no-sync python -m compute.remote sync-code --host-config ~/.config/propexp/pc.json \
    --state-dir $S --harness-sha256 $H --commit $C
```

The first time, `sync-code` clones the bundle into `propexp\checkout`, but its last step fails:
the environment there does not exist yet (the message says "is the far checkout's environment
synced?"). Build the environment from the lock, then run `sync-code` again:

```bash
uv run --no-sync python -m compute.remote sync-env --host-config ~/.config/propexp/pc.json
uv run --no-sync python -m compute.remote sync-code --host-config ~/.config/propexp/pc.json \
    --state-dir $S --harness-sha256 $H --commit $C
```

`sync-env` runs `uv sync --frozen` in the PC checkout. It downloads torch cu130 (a few GB) the
first time. After that, `sync-code` must print `"ok": true`. This means the PC checkout is the
export commit byte for byte, its packages match `uv.lock`, and
`screening.harness_freeze.preflight` passed on the PC.

A manual alternative, if you want to see each step: copy
`$S/<job>/export/harness-*.bundle` to the PC, then run
`git clone --no-checkout --config core.autocrlf=false <bundle> checkout`,
`git -C checkout checkout --detach <export commit>` and
`uv sync --frozen --directory checkout`. The backend's `verify-code` still decides.

### Detachment: which method

Windows OpenSSH runs each session's processes in a job object that ends with the session. The
backend's `start` therefore starts the worker in one of two ways, set by `detach` in the host
config:
- `windows_breakaway` (the default): the worker is created with `CREATE_BREAKAWAY_FROM_JOB`,
  `DETACHED_PROCESS`, `CREATE_NEW_PROCESS_GROUP` and `BELOW_NORMAL_PRIORITY_CLASS`. This works
  only if the session's job object allows breakaway. If it does not, `start` refuses with a
  message that names `windows_schtasks`.
- `windows_schtasks`: the worker runs as a one-off scheduled task of the same user. The Task
  Scheduler starts it outside the SSH session. A task created this way may run only while
  `propexp` is signed in ("Run only when user is logged on"). E.2c checks whether it starts
  with nobody signed in. If it does not, the options are the task setting "Run whether user is
  logged on or not" with "Do not store password" (needs an administrator to set; no password
  is stored), or keeping `propexp` signed in during runs.

Checklist item 9 decides the method.

## 11. Running a job (ThinkPad)

```bash
# a research-window backtest of one cluster
uv run --no-sync python -m compute.remote submit --host-config ~/.config/propexp/pc.json \
    --state-dir $S --harness-sha256 $H --commit $C --kind screening \
    --research-product ES --research-product NQ --wait -- --cluster K1 --all --window research
# an ML fit (the training root holds step 2 files only)
uv run --no-sync python -m compute.remote submit --host-config ~/.config/propexp/pc.json \
    --state-dir $S --harness-sha256 $H --commit $C --kind ml_fit \
    --step2-product ES --step2-product NQ --wait -- --challenger lstm --horizon h30
# later, or after any interruption on either side
uv run --no-sync python -m compute.remote resume --host-config ~/.config/propexp/pc.json \
    --state-dir $S --harness-sha256 $H --job-id <job id> --wait
```

Accepted results are in `$S/<job id>/results/`: the job's own outputs in `out/`, its logs in
`logs/`, the result record in `record.json` and the sha256 manifest in `manifest.json`.
`record.json` names the machine that ran the job: host name, OS, CPU, memory, GPU, driver and
CUDA versions, and the numpy, pandas, pyarrow, lightgbm, torch and scikit-learn versions.

## E.2c checklist (everything here is unverified until E.2c runs it on the PC)

Run from the ThinkPad unless marked PC. Write each result into the E.2c STATE file.

In the commands below, `SSH` stands for this whole command:
`ssh -F none -i ~/.ssh/propexp_pc_ed25519 -o IdentitiesOnly=yes -o UserKnownHostsFile=~/.ssh/known_hosts_propexp_pc -o StrictHostKeyChecking=yes -o BatchMode=yes propexp@<PC>`.

1. **SSH with the pinned host key, key only.** Run `SSH ver`: it prints the Windows version
   with no prompt. `ssh -o PubkeyAuthentication=no propexp@<PC>` must be refused.
2. **Tools on the session PATH.** `SSH git --version`, `SSH uv --version` and
   `SSH nvidia-smi` each work.
3. **Code sync and byte identity.** `sync-code`, then `sync-env`, then `sync-code` again
   (step 10) prints `"ok": true`. `SSH git -C propexp/checkout config --get core.autocrlf`
   prints `false`, and `SSH git -C propexp/checkout rev-parse HEAD` equals the `export_commit`
   in `$S/<job>/export.json`.
4. **Machine figures.** `uv run --no-sync python -m compute.remote machine --host-config ...`
   prints the CPU model, `memory_bytes` (about 32 GB), the GPU (RTX 2060 SUPER, about 8192
   MiB), the driver (580 or later) and the CUDA version. **PC:** `Get-PhysicalDisk` shows the
   SSD size. Record all of them against the table at the top.
5. **CUDA torch on the RTX 2060 Super.** Submit the versions probe:
   `submit ... --kind ml_probe --data-root-kind none --wait -- versions`. In
   `results/out/probe.json`, torch is `2.14.0+cu130` and CUDA is available on the RTX 2060
   SUPER (sm_75).
6. **The probes repeated on the PC.** The same with `-- lgbm` and `-- lstm`. On the PC the LSTM
   probe applies the A-1 batch-size rule to the 8 GB card (V10-2). Record the batch size and
   the memory figures. They go into the route manifest only through V10-2's procedure, before
   the first LSTM fit.
7. **A synthetic job end to end.** Make a synthetic step 2 file on the ThinkPad:
   `uv run --no-sync python -c "from pathlib import Path; from tests._compute_fixtures import bar_file; print(bar_file(Path('/tmp/pe_syn'), 'step2', 'ZZ'))"`.
   Then run `submit ... --kind synthetic --data-root-kind training --data-file <that path> --wait -- --items 3`.
   The result is `"state": "verified"`, and `record.json` shows the PC's host name.
8. **Below-normal priority.** In item 7's `results/out/summary.json`, `priority` reads
   `priority class 0x00004000` (BELOW_NORMAL_PRIORITY_CLASS), and every `*_NUM_THREADS` equals
   `--threads`. **PC:** during a longer job, Task Manager > Details shows the job's python.exe at
   "Below normal".
9. **Detachment across SSH disconnect.** Submit
   `--kind synthetic ... -- --items 30 --sleep-s 3` without `--wait`, so the SSH sessions end
   when the command returns. After a minute, `status --job-id <id>` shows `"state": "running"`.
   Harder: **PC, admin PowerShell** `Restart-Service sshd` while the job runs, then check
   `status` again. Finally `resume ... --wait` reaches `verified` with `"restarts": 0` in
   `record.json`. If the job dies, or `start` refuses with the breakaway message, set
   `"detach": "windows_schtasks"` and repeat. For schtasks, also test with `propexp` signed out
   (see step 10).
10. **Far-side interruption resumes.** While a job from item 9 runs: **PC, admin PowerShell**
    `taskkill /PID <pid> /T /F`. The pid is the `spawned` entry in
    `propexp\jobs\<id>\ledger.jsonl`; for schtasks, kill the worker's python.exe instead. Then
    `resume ... --wait` restarts the worker once the heartbeat is 30 s stale and reaches
    `verified` with `"restarts": 1`. No item is computed twice: each item appears once in
    `results/out/computed.jsonl`. Repeat once with a full reboot of the PC.
11. **Long paths.** Item 3 passing proves every file checked out. `SSH git -C propexp/checkout
    config --get core.longpaths` prints `true`.
12. **Refusal canaries on the PC.** **PC:** copy a research-store file into
    `C:\Users\propexp\propexp\data\training\QQ\`. The next `ml_fit` or synthetic training job is
    refused with `training-root`. Delete the file afterwards.
13. **One heavy job at a time.** Start a second job while one runs. The second `start` is
    refused as busy, and nothing is overwritten.
14. **Result hashes.** **PC:** after a job is done and before `resume`, edit a file under
    `propexp\jobs\<id>\result\out\`. `resume` then refuses the result (ResultRefused), and no
    `results/` directory appears.
15. **Firewall and profile.** **PC:** `Get-NetFirewallRule -Name OpenSSH-Server-In-TCP` shows
    Profile Private, and its address filter shows `LocalSubnet`. `Get-NetConnectionProfile`
    shows the home network as Private.
16. **No secret and no ledger on the PC.** **PC:**
    `Get-ChildItem -Recurse -Force C:\Users\propexp\propexp -Include .env,.env.*,*spend*.jsonl`
    finds nothing. `Test-Path C:\Users\propexp\propexp\checkout\ledger` prints `False`. No Git
    credential helper holds a token: `git config --global --get credential.helper` is empty, or
    no GitHub entry appears in Credential Manager.
17. **Power.** `powercfg /query SCHEME_CURRENT SUB_SLEEP` shows sleep and hibernate "Never" on
    AC. An overnight synthetic job (`--items 200 --sleep-s 120`) finishes.
18. **Line endings stay off.** **PC:**
    `git -C C:\Users\propexp\propexp\checkout check-attr text -- compute/agent.py` prints
    `text: unset`.

Everything above is unverified until E.2c runs it. The backend's own tests
(tests/test_compute_*.py) ran on the ThinkPad only, against a localhost SSH server.
