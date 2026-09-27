"""The far side of the compute backend: runs in the far machine's checkout (Stage E.2b, V10).

    uv run --directory <agent_root>/checkout --no-sync python -m compute.agent <command> ...

The agent root is the checkout's parent (``<agent_root>/checkout`` is where the code lives):
    <agent_root>/data/training/<ROOT>/<step 2 file>          the ML training root (V10-5)
    <agent_root>/data/backtest/{research,step2}/<ROOT>/<file> the backtest root
    <agent_root>/jobs/<job_id>/{job.json, ledger.jsonl, heartbeat-<token>, worker.log, result/}
Commands (each prints one JSON line; exit 0 ok, 3 refused, 4 another job is running):
    verify-code  HEAD is the export commit byte for byte, the environment matches uv.lock and
                 screening.harness_freeze.preflight(--harness-sha256) passes here;
    inventory    which of a job's data files are already present with the right sha256;
    receive      the job spec is accepted, every data file matches its sha256 and passes the data
                 rules again, and the job's whole data root holds nothing else (V10-4/5);
    start        starts the detached worker (or restarts it when its heartbeat is stale);
    run-worker   the worker: re-checks code and data, runs the job below normal priority with a
                 thread cap, then writes the result record and the result sha256 manifest;
    status       the job's state from its ledger and heartbeat;  machine  the machine record.
No command reads the Databento key (it is never on this machine) or anything outside the agent
root and the checkout.
"""
from __future__ import annotations

import argparse
import json
import os
import secrets
import subprocess
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

from compute import detach
from compute.datarules import (
    BACKTEST,
    NO_DATA,
    RESEARCH,
    ROOT_STORES,
    STEP2,
    DataRuleRefused,
    check_bar_file,
    check_data_root,
    data_root_relpath,
)
from compute.files import dir_manifest, read_json, sha256_file, write_json_atomic
from compute.gitbundle import GitFailed, checkout_problems
from compute.jobspec import JobSpec, JobSpecRefused
from compute.ledger import JobLedger, LedgerRead, now_iso
from compute.machine import environment_problems, machine_record
from compute.platform import lower_priority, priority_label, thread_env
from data.config import REPO_ROOT
from screening.harness_freeze import HarnessFreezeError, preflight

CHECKOUT_DIR_NAME = "checkout"
HEARTBEAT_S = 2.0
STALE_AFTER_S = 30.0
MIN_STALE_AFTER_S = 3 * HEARTBEAT_S
RESULT_SCHEMA = "propexperiment-compute-result/1"
EXIT_OK, EXIT_ERROR, EXIT_REFUSED, EXIT_BUSY = 0, 1, 3, 4


class CodeRefused(RuntimeError):
    """The checkout is not the frozen harness export, or its environment is not the lock's."""


class JobRefused(RuntimeError):
    """The job cannot be received or started as asked."""


class Busy(RuntimeError):
    """Another job is running on this machine (one heavy job at a time, V10-7)."""


# ------------------------------------------------------------------ layout ----
def agent_root(repo_root: Path | None = None) -> Path:
    repo_root = REPO_ROOT if repo_root is None else repo_root
    if repo_root.name != CHECKOUT_DIR_NAME:
        raise CodeRefused(f"the agent runs only from <agent_root>/{CHECKOUT_DIR_NAME}, not "
                          f"{repo_root}")
    return repo_root.parent


def job_dir(job_id: str, root: Path) -> Path:
    return root / "jobs" / job_id


def data_values(spec: JobSpec, root: Path, out_dir: Path) -> dict[str, str]:
    values = {"out_dir": str(out_dir), "harness_sha256": spec.harness_sha256}
    if spec.data_root_kind != NO_DATA:
        base = root / data_root_relpath(spec.data_root_kind)
        values["data_root"] = str(base)
        if spec.data_root_kind == BACKTEST:
            values["research_root"] = str(base / RESEARCH)
            values["step2_root"] = str(base / STEP2)
    return values


# -------------------------------------------------------------- checks ----
def verify_code(export_commit: str, harness_sha256: str, *, source_commit: str | None = None,
                repo_root: Path | None = None) -> str:
    """The manifest sha256 preflight returns, once the checkout is the export commit byte for
    byte and the environment is the lock's; CodeRefused or HarnessFreezeError otherwise."""
    repo_root = REPO_ROOT if repo_root is None else repo_root
    problems = checkout_problems(repo_root, export_commit, source_commit)
    problems.extend(environment_problems(repo_root / "uv.lock"))
    if problems:
        raise CodeRefused("; ".join(problems[:10]))
    return preflight(harness_sha256, root=repo_root)


def load_spec(jobdir: Path, harness_sha256: str) -> JobSpec:
    path = jobdir / "job.json"
    if not path.is_file():
        raise JobRefused(f"{jobdir.name}: no job spec on this machine")
    spec = JobSpec.from_dict(read_json(path))
    if spec.harness_sha256 != harness_sha256:
        raise JobRefused("the job spec's harness sha256 is not the one given")
    return spec


def check_data(spec: JobSpec, root: Path) -> list[dict]:
    """Every listed file present at its layout path with its sha256 and passing the rules, and
    the whole data root of the job's kind holding nothing else."""
    if spec.data_root_kind == NO_DATA:
        return []
    checked = []
    for item in spec.data_files:
        path = root / Path(item.dest(spec.data_root_kind))
        if not path.is_file():
            raise DataRuleRefused("missing", item.dest(spec.data_root_kind), "not received")
        actual = sha256_file(path)
        if actual != item.sha256:
            raise DataRuleRefused("hash-mismatch", item.dest(spec.data_root_kind),
                                  f"sha256 {actual[:12]}... is not the sent {item.sha256[:12]}...")
        check_bar_file(path, allowed_stores=ROOT_STORES[spec.data_root_kind], rules=None,
                       key=None)
        checked.append({"dest": item.dest(spec.data_root_kind), "sha256": actual})
    check_data_root(root / data_root_relpath(spec.data_root_kind), spec.data_root_kind)
    return checked


# --------------------------------------------------------------- state ----
def current_token(ledger: LedgerRead) -> str | None:
    entry = ledger.last("started", "restarted")
    return None if entry is None else str(entry["token"])


def heartbeat_path(jobdir: Path, token: str) -> Path:
    return jobdir / f"heartbeat-{token}"


def job_state(jobdir: Path, stale_after: float) -> dict[str, object]:
    ledger = JobLedger(jobdir / "ledger.jsonl").read()
    token = current_token(ledger)
    restarts = sum(1 for e in ledger.entries if e.get("step") == "restarted")
    base: dict[str, object] = {"job_id": jobdir.name, "token": token, "restarts": restarts}
    if token is None:
        return {**base, "state": "received" if ledger.has("received") else "absent"}
    done = [e for e in ledger.entries if e.get("step") == "done" and e.get("token") == token]
    if done:
        entry = done[-1]
        state = "done" if entry.get("exit_code") == 0 else "failed"
        return {**base, "state": state, "exit_code": entry.get("exit_code"),
                "manifest_sha256": entry.get("manifest_sha256"), "refused": entry.get("refused")}
    beat = heartbeat_path(jobdir, token)
    age = time.time() - beat.stat().st_mtime if beat.exists() else float("inf")
    return {**base, "state": "running" if age <= stale_after else "stale",
            "heartbeat_age_s": None if age == float("inf") else round(age, 1)}


def running_jobs(root: Path, stale_after: float, exclude: str) -> list[str]:
    jobs = root / "jobs"
    if not jobs.is_dir():
        return []
    return sorted(d.name for d in jobs.iterdir()
                  if d.is_dir() and d.name != exclude
                  and job_state(d, stale_after)["state"] == "running")


# ------------------------------------------------------------ commands ----
def cmd_verify_code(args: argparse.Namespace) -> dict:
    digest = verify_code(args.commit, args.harness_sha256, source_commit=args.source_commit)
    return {"harness_sha256": digest, "export_commit": args.commit,
            "machine": machine_record()}


def _incoming_spec(jobdir: Path, harness_sha256: str) -> JobSpec:
    incoming = jobdir / "job.json.incoming"
    current = jobdir / "job.json"
    if incoming.is_file():
        spec = JobSpec.from_dict(read_json(incoming))
        if current.is_file() and JobSpec.from_dict(read_json(current)).sha256() != spec.sha256():
            raise JobRefused(f"job id {jobdir.name} is already used by a different spec here")
        os.replace(incoming, current)
    return load_spec(jobdir, harness_sha256)


def cmd_inventory(args: argparse.Namespace) -> dict:
    root = agent_root()
    spec = _incoming_spec(job_dir(args.job_id, root), args.harness_sha256)
    verify_code(spec.export_commit, args.harness_sha256)  # before any bar file is read
    present = {}
    for item in spec.data_files:
        path = root / Path(item.dest(spec.data_root_kind))
        present[item.dest(spec.data_root_kind)] = sha256_file(path) if path.is_file() else None
    return {"job_id": spec.job_id, "present": present}


def cmd_receive(args: argparse.Namespace) -> dict:
    root = agent_root()
    jobdir = job_dir(args.job_id, root)
    spec = _incoming_spec(jobdir, args.harness_sha256)
    digest = verify_code(spec.export_commit, args.harness_sha256,
                         source_commit=spec.source_commit)
    checked = check_data(spec, root)
    ledger = JobLedger(jobdir / "ledger.jsonl")
    if not ledger.read().has("received"):
        ledger.append("received", spec_sha256=spec.sha256(), harness_sha256=digest,
                      files=len(checked))
    return {"job_id": spec.job_id, "spec_sha256": spec.sha256(), "files": checked}


def cmd_start(args: argparse.Namespace) -> dict:
    stale_after = max(args.stale_after_s, MIN_STALE_AFTER_S)
    root = agent_root()
    jobdir = job_dir(args.job_id, root)
    spec = load_spec(jobdir, args.harness_sha256)
    detach.check_method(args.detach)
    verify_code(spec.export_commit, args.harness_sha256)
    ledger = JobLedger(jobdir / "ledger.jsonl")
    if not ledger.read().has("received"):
        raise JobRefused(f"{spec.job_id}: the data were not received and checked here")
    state = job_state(jobdir, stale_after)
    if state["state"] in ("running", "done", "failed"):
        return state
    busy = running_jobs(root, stale_after, exclude=spec.job_id)
    if busy:
        raise Busy(f"job(s) {', '.join(busy)} running here; one heavy job at a time")
    token = secrets.token_hex(8)
    step = "restarted" if state["state"] == "stale" else "started"
    ledger.append(step, token=token, method=args.detach, previous=state.get("token"))
    heartbeat_path(jobdir, token).touch()
    argv = [sys.executable, "-m", "compute.agent", "run-worker", "--job-id", spec.job_id,
            "--token", token, "--harness-sha256", args.harness_sha256]
    pid = detach.spawn(args.detach, argv, cwd=REPO_ROOT, log=jobdir / "worker.log",
                       env={**os.environ, "PYTHONUTF8": "1"}, task_name=spec.job_id)
    ledger.append("spawned", token=token, pid=pid)
    return {**job_state(jobdir, stale_after), "step": step}


def cmd_status(args: argparse.Namespace) -> dict:
    jobdir = job_dir(args.job_id, agent_root())
    return job_state(jobdir, max(args.stale_after_s, MIN_STALE_AFTER_S))


def cmd_machine(args: argparse.Namespace) -> dict:
    return {"machine": machine_record()}


# -------------------------------------------------------------- worker ----
class Heartbeat:
    """Touches heartbeat-<token> every HEARTBEAT_S and notices when a restart superseded it."""

    def __init__(self, jobdir: Path, token: str) -> None:
        self.jobdir, self.token = jobdir, token
        self.superseded = threading.Event()
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def _run(self) -> None:
        path = heartbeat_path(self.jobdir, self.token)
        while not self._stop.wait(HEARTBEAT_S):
            path.touch()
            ledger = JobLedger(self.jobdir / "ledger.jsonl").read()
            if current_token(ledger) != self.token:
                self.superseded.set()

    def __enter__(self) -> Heartbeat:
        heartbeat_path(self.jobdir, self.token).touch()
        self._thread.start()
        return self

    def __exit__(self, *exc: object) -> None:
        self._stop.set()
        self._thread.join()


def _finish(jobdir: Path, token: str, record: dict, exit_code: int | None,
            refused: str | None = None) -> None:
    result = jobdir / "result"
    result.mkdir(parents=True, exist_ok=True)
    write_json_atomic(result / "record.json", record)
    manifest = dir_manifest(result, exclude=frozenset({"manifest.json", "manifest.json.tmp"}))
    digest = write_json_atomic(result / "manifest.json", manifest)
    ledger = JobLedger(jobdir / "ledger.jsonl")
    if current_token(ledger.read()) == token:
        ledger.append("done", token=token, exit_code=exit_code, manifest_sha256=digest,
                      refused=refused)


def run_job(spec: JobSpec, jobdir: Path, root: Path, beat: Heartbeat) -> int | None:
    """Run the job's module to completion; None when a restart superseded this worker."""
    result = jobdir / "result"
    out_dir, logs = result / "out", result / "logs"
    out_dir.mkdir(parents=True, exist_ok=True)
    logs.mkdir(parents=True, exist_ok=True)
    if spec.data_root_kind == BACKTEST:
        for sub in (RESEARCH, STEP2):
            (root / data_root_relpath(BACKTEST) / sub).mkdir(parents=True, exist_ok=True)
    argv = [sys.executable, "-m", spec.kind_spec().module,
            *spec.argv(data_values(spec, root, out_dir.resolve()))]
    env = {**os.environ, **thread_env(spec.threads), "PYTHONUTF8": "1"}
    with (logs / "stdout.txt").open("ab") as out, (logs / "stderr.txt").open("ab") as err:
        proc = subprocess.Popen(argv, cwd=str(REPO_ROOT), env=env, stdin=subprocess.DEVNULL,
                                stdout=out, stderr=err, creationflags=detach.job_child_flags())
        while proc.poll() is None:
            if beat.superseded.is_set():
                proc.terminate()
                proc.wait()
                return None
            time.sleep(1.0)
    return proc.returncode


def cmd_run_worker(args: argparse.Namespace) -> dict:
    lower_priority()
    root = agent_root()
    jobdir = job_dir(args.job_id, root)
    ledger = JobLedger(jobdir / "ledger.jsonl")
    if current_token(ledger.read()) != args.token:
        return {"job_id": args.job_id, "state": "superseded"}
    started = datetime.now().astimezone()
    with Heartbeat(jobdir, args.token) as beat:
        record: dict = {"schema": RESULT_SCHEMA, "job_id": args.job_id, "token": args.token,
                        "restarts": sum(1 for e in ledger.read().entries
                                        if e.get("step") == "restarted"),
                        "started": started.isoformat(timespec="seconds"),
                        "machine": machine_record(),
                        "priority": priority_label()}
        try:
            spec = load_spec(jobdir, args.harness_sha256)
            record.update(kind=spec.kind, module=spec.kind_spec().module,
                          spec_sha256=spec.sha256(), export_commit=spec.export_commit,
                          source_commit=spec.source_commit, threads=spec.threads)
            record["harness_sha256"] = verify_code(spec.export_commit, args.harness_sha256)
            record["data"] = check_data(spec, root)
        except REFUSALS as exc:
            record.update(refused=f"{type(exc).__name__}: {exc}", finished=now_iso())
            _finish(jobdir, args.token, record, None, refused=type(exc).__name__)
            return {"job_id": args.job_id, "state": "failed", "refused": str(exc)}
        exit_code = run_job(spec, jobdir, root, beat)
        if exit_code is None:
            return {"job_id": spec.job_id, "state": "superseded"}
        finished = datetime.now().astimezone()
        record.update(exit_code=exit_code, finished=finished.isoformat(timespec="seconds"),
                      duration_s=round((finished - started).total_seconds(), 1),
                      argv=spec.argv(data_values(spec, root, (jobdir / "result" / "out")
                                                 .resolve())))
        _finish(jobdir, args.token, record, exit_code)
    return {"job_id": spec.job_id, "state": "done" if exit_code == 0 else "failed",
            "exit_code": exit_code}


# ----------------------------------------------------------------- CLI ----
def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="command", required=True)
    verify = sub.add_parser("verify-code")
    verify.add_argument("--commit", required=True)
    verify.add_argument("--source-commit", required=True)
    verify.add_argument("--harness-sha256", required=True)
    for name in ("inventory", "receive", "start", "run-worker", "status"):
        cmd = sub.add_parser(name)
        cmd.add_argument("--job-id", required=True)
        if name != "status":
            cmd.add_argument("--harness-sha256", required=True)
        if name in ("start", "status"):
            cmd.add_argument("--stale-after-s", type=float, default=STALE_AFTER_S)
        if name == "start":
            cmd.add_argument("--detach", required=True, choices=detach.METHODS)
        if name == "run-worker":
            cmd.add_argument("--token", required=True)
    sub.add_parser("machine")
    return p


COMMANDS = {"verify-code": cmd_verify_code, "inventory": cmd_inventory, "receive": cmd_receive,
            "start": cmd_start, "run-worker": cmd_run_worker, "status": cmd_status,
            "machine": cmd_machine}
REFUSALS = (CodeRefused, HarnessFreezeError, DataRuleRefused, JobRefused, JobSpecRefused,
            detach.DetachRefused, GitFailed)


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        payload = {"ok": True, "command": args.command, **COMMANDS[args.command](args)}
        code = EXIT_OK
    except Busy as exc:
        payload, code = {"ok": False, "command": args.command, "busy": str(exc)}, EXIT_BUSY
    except REFUSALS as exc:
        payload = {"ok": False, "command": args.command, "refused": type(exc).__name__,
                   "kind": getattr(exc, "kind", None), "error": str(exc)}
        code = EXIT_REFUSED
    print(json.dumps(payload, sort_keys=True, default=str), flush=True)
    return code


if __name__ == "__main__":
    sys.exit(main())
