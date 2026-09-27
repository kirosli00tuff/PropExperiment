"""The ThinkPad side of the compute backend: send a job to the far machine and bring its results
back, checked by hash (Stage E.2b, user decision V10).

    python -m compute.remote submit --host-config pc.json --state-dir DIR --harness-sha256 SHA \
        --commit REV --kind screening --research-product ES --research-product NQ \
        [--wait] -- --cluster K1 --all --window research
    python -m compute.remote resume --host-config pc.json --state-dir DIR --harness-sha256 SHA \
        --job-id ID [--wait]
    python -m compute.remote status | sync-code | machine | sync-env ...

Job flow; every step is appended to the job's local ledger (<state-dir>/<job_id>/ledger.jsonl)
and skipped on a restart once recorded:
1. prepared: screening.harness_freeze.preflight(--harness-sha256) on this working tree; every
   data file passes compute.datarules (sealed, holdout and embargo dates from the rows, the key,
   the ledger, the store allowlist of its data root); the harness commit is exported (ledger cut,
   every blob checked) and the exported tree passes the same preflight here before it is sent.
2. code_synced: the bundle goes over SFTP; the far checkout is set to the export commit; the agent
   proves it byte for byte, checks the environment against uv.lock and runs the preflight there.
3. sent: the job spec and only the data files it lists (each with its sha256) go over; the agent
   re-checks every file, its hash and the whole data root of the job's kind.
4. started: the agent starts the detached worker (below normal priority, thread cap).
5. done: polled until the far ledger says done; a stale heartbeat restarts the worker, which
   resumes from the job's own progress.
6. verified: the result directory comes back with its sha256 manifest; the manifest's own hash
   must equal what the far ledger recorded and every file must match it, or the result is
   refused. The result record names the machine that ran the job.
"""
from __future__ import annotations

import argparse
import json
import os
import secrets
import shutil
import sys
import tempfile
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from compute.datarules import (
    NO_DATA,
    ROOT_STORES,
    DataFile,
    DataRuleRefused,
    DataRules,
    check_bar_file,
    default_rules,
)
from compute.files import (
    manifest_problems,
    read_json,
    sha256_file,
    write_json_atomic,
)
from compute.gitbundle import EXPORT_REF, INFO_ATTRIBUTES, Export, build_export, materialize
from compute.jobspec import KINDS, JobSpec, JobSpecRefused
from compute.ledger import JobLedger
from compute.transport import (
    HostConfig,
    RemoteResult,
    SSHTransport,
    mkdirs_lines,
    put_lines,
    sftp_path,
)
from data.config import REPO_ROOT, MissingSecretError, require_databento_key
from screening.harness_freeze import HarnessFreezeError, preflight

DEFAULT_THREADS = 6
POLL_S = 30.0
STALE_AFTER_S = 30.0
MAX_RESTARTS = 3
AGENT_REFUSED, AGENT_BUSY = 3, 4


class SendRefused(RuntimeError):
    """The ThinkPad refuses to send this job (a data rule, the harness, the spec)."""


class RemoteRefused(RuntimeError):
    """The far agent refused (its answer names the rule)."""

    def __init__(self, command: str, answer: dict) -> None:
        super().__init__(f"agent {command} refused [{answer.get('kind') or answer.get('refused')}]"
                         f": {answer.get('error')}")
        self.kind = answer.get("kind")
        self.answer = answer


class RemoteBusy(RuntimeError):
    """Another job is running on the far machine."""


class RemoteError(RuntimeError):
    """The far side failed without a refusal (no JSON answer, an unexpected exit code)."""


class ResultRefused(RuntimeError):
    """The pulled results do not match their sha256 manifest; they are not accepted."""


@dataclass(frozen=True)
class Submission:
    kind: str
    user_args: tuple[str, ...]
    data_root_kind: str
    data_paths: tuple[Path, ...]
    threads: int
    harness_sha256: str
    commit: str
    job_id: str


def new_job_id(kind: str) -> str:
    stamp = datetime.now().strftime("%Y%m%dt%H%M%S")
    return f"{kind.replace('_', '-')}-{stamp}-{secrets.token_hex(3)}"


class RemoteRunner:
    def __init__(self, transport: SSHTransport, state_dir: Path, *, repo: Path = REPO_ROOT,
                 rules: DataRules | None = None,
                 key_loader: Callable[[], str] = require_databento_key,
                 poll_s: float = POLL_S, stale_after_s: float = STALE_AFTER_S) -> None:
        self.transport = transport
        self.host: HostConfig = transport.host
        self.state_dir = Path(state_dir)
        self.repo = Path(repo)
        self.rules = default_rules() if rules is None else rules
        self.key_loader = key_loader
        self.poll_s = poll_s
        self.stale_after_s = stale_after_s

    # ---------------------------------------------------------- local ----
    def job_state_dir(self, job_id: str) -> Path:
        return self.state_dir / job_id

    def ledger(self, job_id: str) -> JobLedger:
        return JobLedger(self.job_state_dir(job_id) / "ledger.jsonl")

    def _key(self) -> bytes:
        try:
            key = self.key_loader()
        except MissingSecretError as exc:
            raise SendRefused(f"cannot scan for the Databento key, so nothing is sent: {exc}") \
                from exc
        if not key:
            raise SendRefused("the Databento key is empty; nothing can be scanned for it")
        return key.encode("utf-8")

    def export(self, commit: str, harness_sha256: str, work_dir: Path, key: bytes) -> Export:
        """The export of ``commit``, whose tree passes the preflight here before it leaves."""
        work_dir.mkdir(parents=True, exist_ok=True)
        export = build_export(self.repo, commit, work_dir, key)
        with tempfile.TemporaryDirectory(dir=work_dir) as tmp:
            tree = Path(tmp) / "tree"
            materialize(export, tree)
            preflight(harness_sha256, root=tree)
        return export

    def prepare(self, sub: Submission) -> JobSpec:
        local_harness = preflight(sub.harness_sha256, root=self.repo)
        jobdir = self.job_state_dir(sub.job_id)
        if (jobdir / "job.json").exists():
            raise SendRefused(f"job {sub.job_id} was already prepared; use resume")
        if sub.kind not in KINDS:
            raise JobSpecRefused(f"kind {sub.kind!r} is not one of {sorted(KINDS)}")
        allowed = ROOT_STORES.get(sub.data_root_kind, ())
        key = self._key()
        files: list[DataFile] = []
        local: dict[str, str] = {}
        for path in sub.data_paths:
            item = check_bar_file(Path(path), allowed_stores=allowed, rules=self.rules, key=key)
            files.append(item)
            local[item.dest(sub.data_root_kind)] = str(Path(path).resolve())
        export = self.export(sub.commit, sub.harness_sha256, jobdir / "export", key)
        del key
        spec = JobSpec(job_id=sub.job_id, kind=sub.kind, user_args=sub.user_args,
                       data_root_kind=sub.data_root_kind, data_files=tuple(files),
                       threads=sub.threads, harness_sha256=sub.harness_sha256,
                       source_commit=export.source_commit, export_commit=export.export_commit,
                       excluded_paths=export.excluded,
                       created=datetime.now().astimezone().isoformat(timespec="seconds"))
        spec.validate()
        write_json_atomic(jobdir / "local_files.json", local)
        write_json_atomic(jobdir / "export.json", export.as_dict())
        write_json_atomic(jobdir / "job.json", spec.to_dict())
        self.ledger(sub.job_id).append("prepared", spec_sha256=spec.sha256(),
                                       harness_sha256=local_harness,
                                       export_commit=export.export_commit,
                                       source_commit=export.source_commit,
                                       excluded=list(export.excluded), files=len(files))
        return spec

    def load(self, job_id: str) -> tuple[JobSpec, dict[str, str]]:
        jobdir = self.job_state_dir(job_id)
        spec = JobSpec.from_dict(read_json(jobdir / "job.json"))
        local = read_json(jobdir / "local_files.json")
        for item in spec.data_files:
            path = Path(local[item.dest(spec.data_root_kind)])
            if not path.is_file() or sha256_file(path) != item.sha256:
                raise SendRefused(f"{path}: changed since the job was prepared (sha256)")
        return spec, local

    def bundle_for(self, spec: JobSpec) -> Path:
        info = read_json(self.job_state_dir(spec.job_id) / "export.json")
        bundle = Path(info["bundle"])
        if not bundle.is_file():
            export = self.export(spec.source_commit, spec.harness_sha256,
                                 self.job_state_dir(spec.job_id) / "export", self._key())
            if export.export_commit != spec.export_commit:
                raise SendRefused("the rebuilt export commit differs from the prepared one")
            bundle = export.bundle
        return bundle

    # --------------------------------------------------------- remote ----
    def agent(self, command: str, *args: str) -> dict:
        result = self.transport.agent(command, *args)
        answer = result.last_json()
        if answer is None:
            raise RemoteError(f"agent {command}: no answer (exit {result.returncode}; is the "
                              "far checkout's environment synced? python -m compute.remote "
                              f"sync-env): {result.stderr.strip()[-600:]}")
        if result.returncode == AGENT_BUSY:
            raise RemoteBusy(str(answer.get("busy")))
        if result.returncode == AGENT_REFUSED or not answer.get("ok"):
            raise RemoteRefused(command, answer)
        if result.returncode != 0:
            raise RemoteError(f"agent {command}: exit {result.returncode}")
        return answer

    def run_git(self, *args: str) -> RemoteResult:
        return self.transport.run(["git", *args])

    def must_git(self, *args: str) -> None:
        result = self.run_git(*args)
        if result.returncode != 0:
            raise RemoteError(f"remote git {' '.join(args[:3])} failed: "
                              f"{result.stderr.strip()[-400:]}")

    def sync_code(self, bundle: Path, export_commit: str, source_commit: str,
                  harness_sha256: str) -> dict:
        """The far checkout at the export commit, proven by the agent there."""
        h = self.host
        head = self.run_git("-C", h.checkout, "rev-parse", "HEAD")
        if head.returncode != 0 or head.stdout.strip() != export_commit:
            name = f"harness-{export_commit[:12]}.bundle"
            remote_bundle = f"{h.agent_root}/incoming/{name}"
            self.transport.sftp([*mkdirs_lines(f"{h.agent_root}/incoming"),
                                 *put_lines(bundle, remote_bundle, remote_bundle + ".partial")])
            if self.run_git("-C", h.checkout, "rev-parse", "--git-dir").returncode != 0:
                self.must_git("clone", "--no-checkout", "--config", "core.autocrlf=false",
                              "--config", "core.longpaths=true", remote_bundle, h.checkout)
            with tempfile.TemporaryDirectory() as tmp:
                attributes = Path(tmp) / "attributes"
                attributes.write_bytes(INFO_ATTRIBUTES.encode("utf-8"))
                self.transport.sftp([*mkdirs_lines(f"{h.checkout}/.git/info"),
                                     f"put {sftp_path(attributes)} "
                                     f"{sftp_path(h.checkout + '/.git/info/attributes')}"])
            self.must_git("-C", h.checkout, "config", "core.autocrlf", "false")
            self.must_git("-C", h.checkout, "fetch", "--no-tags", f"../incoming/{name}",
                          f"+{EXPORT_REF}:refs/remotes/bundle/harness")
        # Always: restore any tracked file changed on the far side, drop untracked ones.
        self.must_git("-C", h.checkout, "checkout", "--force", "--detach", export_commit)
        self.must_git("-C", h.checkout, "clean", "-fdq")
        return self.agent("verify-code", "--commit", export_commit, "--source-commit",
                          source_commit, "--harness-sha256", harness_sha256)

    def send(self, spec: JobSpec, local: dict[str, str]) -> dict:
        h = self.host
        jobdir = f"{h.agent_root}/jobs/{spec.job_id}"
        spec_file = self.job_state_dir(spec.job_id) / "job.json"
        self.transport.sftp([*mkdirs_lines(jobdir),
                             *put_lines(spec_file, f"{jobdir}/job.json.incoming",
                                        f"{jobdir}/job.json.incoming.partial")])
        common = ("--job-id", spec.job_id, "--harness-sha256", spec.harness_sha256)
        present = self.agent("inventory", *common)["present"]
        lines: list[str] = []
        uploaded = 0
        for item in spec.data_files:
            dest = item.dest(spec.data_root_kind)
            if present.get(dest) == item.sha256:
                continue
            parent = dest.rsplit("/", 1)[0]
            lines += [*mkdirs_lines(f"{h.agent_root}/{parent}"),
                      *mkdirs_lines(f"{h.agent_root}/incoming"),
                      *put_lines(Path(local[dest]), f"{h.agent_root}/{dest}",
                                 f"{h.agent_root}/incoming/{item.name}.partial")]
            uploaded += 1
        if lines:
            self.transport.sftp(lines)
        answer = self.agent("receive", *common)
        return {"uploaded": uploaded, "skipped": len(spec.data_files) - uploaded,
                "spec_sha256": answer["spec_sha256"]}

    def start(self, spec: JobSpec) -> dict:
        return self.agent("start", "--job-id", spec.job_id, "--harness-sha256",
                          spec.harness_sha256, "--detach", self.host.detach,
                          "--stale-after-s", str(self.stale_after_s))

    def status(self, job_id: str) -> dict:
        return self.agent("status", "--job-id", job_id, "--stale-after-s",
                          str(self.stale_after_s))

    def wait(self, spec: JobSpec, max_wait_s: float) -> dict | None:
        """The far job's final status, or None when max_wait_s passed first (resume later)."""
        deadline = time.monotonic() + max_wait_s
        restarts = 0
        while True:
            state = self.status(spec.job_id)
            if state["state"] in ("done", "failed"):
                return state
            if state["state"] == "absent":
                raise RemoteError(f"{spec.job_id}: the far machine has no record of this job")
            if state["state"] in ("stale", "received"):
                if restarts >= MAX_RESTARTS:
                    raise RemoteError(f"{spec.job_id}: worker restarted {restarts} times")
                self.ledger(spec.job_id).append("restart_requested", far_state=state["state"],
                                                heartbeat_age_s=state.get("heartbeat_age_s"))
                self.start(spec)
                restarts += 1
            if time.monotonic() >= deadline:
                return None
            time.sleep(self.poll_s)

    def pull_and_verify(self, spec: JobSpec, done: dict) -> dict:
        jobdir = self.job_state_dir(spec.job_id)
        staging = jobdir / "staging"
        if staging.exists():
            shutil.rmtree(staging)
        staging.mkdir(parents=True)
        remote = f"{self.host.agent_root}/jobs/{spec.job_id}/result"
        self.transport.sftp([f"get -r {sftp_path(remote)} {sftp_path(staging / 'result')}"])
        self.ledger(spec.job_id).append("pulled")
        record = verify_results(staging / "result", spec, done.get("manifest_sha256"))
        final = jobdir / "results"
        if final.exists():
            shutil.rmtree(final)
        os.replace(staging / "result", final)
        machine = record.get("machine", {})
        self.ledger(spec.job_id).append(
            "verified", manifest_sha256=done.get("manifest_sha256"),
            exit_code=record.get("exit_code"), refused=record.get("refused"),
            hostname=machine.get("hostname"), os=machine.get("os"), results=str(final))
        return record

    # ------------------------------------------------------------ flow ----
    def run(self, job_id: str, harness_sha256: str, *, wait: bool,
            max_wait_s: float) -> dict:
        """Continue a prepared job from its ledger: sync code, send, start, wait, verify."""
        local_harness = preflight(harness_sha256, root=self.repo)
        spec, local = self.load(job_id)
        if spec.harness_sha256 != harness_sha256:
            raise SendRefused("the job was prepared under another harness sha256")
        ledger = self.ledger(job_id)
        steps = ledger.read()
        if steps.has("verified"):
            return {"job_id": job_id, "state": "verified", **(steps.last("verified") or {})}
        if not steps.has("code_synced"):
            answer = self.sync_code(self.bundle_for(spec), spec.export_commit,
                                    spec.source_commit, harness_sha256)
            machine = answer.get("machine", {})
            ledger.append("code_synced", harness_sha256=answer["harness_sha256"],
                          export_commit=spec.export_commit, hostname=machine.get("hostname"))
            # The bundle is rebuilt deterministically if ever needed again; do not keep a copy
            # per job.
            shutil.rmtree(self.job_state_dir(job_id) / "export", ignore_errors=False)
        if not steps.has("sent"):
            ledger.append("sent", **self.send(spec, local))
        if not steps.has("started"):
            answer = self.start(spec)
            ledger.append("started", token=answer.get("token"), far_state=answer.get("state"))
        done = steps.last("done")
        if done is None:
            state = self.wait(spec, max_wait_s if wait else 0.0)
            if state is None:
                return {"job_id": job_id, "state": "running"}
            done = ledger.append("done", far_state=state["state"],
                                 exit_code=state.get("exit_code"),
                                 manifest_sha256=state.get("manifest_sha256"),
                                 token=state.get("token"))
        record = self.pull_and_verify(spec, done)
        return {"job_id": job_id, "state": "verified", "exit_code": record.get("exit_code"),
                "harness_sha256": local_harness,
                "far_harness_sha256": record.get("harness_sha256"),
                "refused": record.get("refused"),
                "hostname": record.get("machine", {}).get("hostname"),
                "results": str(self.job_state_dir(job_id) / "results")}

    def submit(self, sub: Submission, *, wait: bool, max_wait_s: float) -> dict:
        self.prepare(sub)
        return self.run(sub.job_id, sub.harness_sha256, wait=wait, max_wait_s=max_wait_s)


def verify_results(root: Path, spec: JobSpec, manifest_sha256: str | None) -> dict:
    """The result record once every pulled file matches the manifest the far ledger hashed;
    ResultRefused naming every problem otherwise."""
    manifest_path = root / "manifest.json"
    if not manifest_path.is_file():
        raise ResultRefused(f"{spec.job_id}: the results carry no sha256 manifest")
    if not manifest_sha256:
        raise ResultRefused(f"{spec.job_id}: the far ledger recorded no manifest sha256")
    actual = sha256_file(manifest_path)
    if actual != manifest_sha256:
        raise ResultRefused(f"{spec.job_id}: manifest sha256 {actual[:12]}... is not the "
                            f"recorded {manifest_sha256[:12]}...")
    manifest = read_json(manifest_path)
    problems = manifest_problems(root, manifest, exclude=frozenset({"manifest.json"}))
    if "record.json" not in (manifest if isinstance(manifest, dict) else {}):
        problems.append("record.json is not in the manifest")
    if problems:
        raise ResultRefused(f"{spec.job_id}: " + "; ".join(problems[:10]))
    record = read_json(root / "record.json")
    expected = {"job_id": spec.job_id, "export_commit": spec.export_commit,
                "spec_sha256": spec.sha256()}
    if not record.get("refused"):
        expected["harness_sha256"] = spec.harness_sha256
    wrong = [k for k, v in expected.items() if record.get(k) != v]
    if wrong:
        raise ResultRefused(f"{spec.job_id}: the result record's {', '.join(wrong)} differ "
                            "from the job's")
    return record


# ----------------------------------------------------------------- CLI ----
def _data_paths(args: argparse.Namespace) -> list[Path]:
    paths = [Path(p) for p in args.data_file]
    if args.research_product:
        from data.build_bars import research_parquet_path

        paths += [research_parquet_path(r) for r in args.research_product]
    if args.step2_product:
        from data.step2_store import step2_parquet_path

        paths += [step2_parquet_path(r) for r in args.step2_product]
    return paths


def _submission(args: argparse.Namespace) -> Submission:
    kind = KINDS.get(args.kind)
    if kind is None:
        raise JobSpecRefused(f"kind {args.kind!r} is not one of {sorted(KINDS)}")
    root_kind = args.data_root_kind or (kind.data_root_kinds[0]
                                        if len(kind.data_root_kinds) == 1 else None)
    if root_kind is None:
        raise JobSpecRefused(f"kind {args.kind} needs --data-root-kind "
                             f"({'/'.join(kind.data_root_kinds)})")
    return Submission(kind=args.kind, user_args=tuple(args.job_args), data_root_kind=root_kind,
                      data_paths=tuple(_data_paths(args)), threads=args.threads,
                      harness_sha256=args.harness_sha256, commit=args.commit,
                      job_id=args.job_id or new_job_id(args.kind))


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="command", required=True)
    commands = {name: sub.add_parser(name) for name in
                ("submit", "resume", "status", "sync-code", "machine", "sync-env")}
    for cmd in commands.values():
        cmd.add_argument("--host-config", type=Path, required=True)
    for name in ("submit", "resume", "status", "sync-code"):
        commands[name].add_argument("--state-dir", type=Path, required=True)
    for name in ("submit", "resume", "sync-code"):
        commands[name].add_argument("--harness-sha256", required=True)
    for name in ("submit", "sync-code"):
        commands[name].add_argument("--commit", required=True)
    for name in ("resume", "status"):
        commands[name].add_argument("--job-id", required=True)
    for name in ("submit", "resume"):
        commands[name].add_argument("--wait", action="store_true")
        commands[name].add_argument("--max-wait-s", type=float, default=24 * 3600.0)
        commands[name].add_argument("--poll-s", type=float, default=POLL_S)
    s = commands["submit"]
    s.add_argument("--kind", required=True, choices=sorted(KINDS))
    s.add_argument("--data-root-kind", choices=("training", "backtest", NO_DATA))
    s.add_argument("--data-file", action="append", default=[])
    s.add_argument("--research-product", action="append", default=[])
    s.add_argument("--step2-product", action="append", default=[])
    s.add_argument("--threads", type=int, default=DEFAULT_THREADS)
    s.add_argument("--job-id")
    s.add_argument("job_args", nargs="*", help="the kind's own arguments, after --")
    return p


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    transport = SSHTransport(HostConfig.load(args.host_config))
    if args.command == "machine":
        result = transport.agent("machine")
        print(result.stdout.strip() or result.stderr.strip())
        return result.returncode
    if args.command == "sync-env":
        result = transport.run(["uv", "sync", "--frozen", "--directory",
                                transport.host.checkout])
        print(result.stdout.strip()[-2000:], result.stderr.strip()[-2000:])
        return result.returncode
    runner = RemoteRunner(transport, args.state_dir, poll_s=getattr(args, "poll_s", POLL_S))
    try:
        if args.command == "submit":
            out = runner.submit(_submission(args), wait=args.wait, max_wait_s=args.max_wait_s)
        elif args.command == "resume":
            out = runner.run(args.job_id, args.harness_sha256, wait=args.wait,
                             max_wait_s=args.max_wait_s)
        elif args.command == "status":
            out = {"local": [e.get("step") for e in runner.ledger(args.job_id).read().entries],
                   "far": runner.status(args.job_id)}
        else:
            preflight(args.harness_sha256, root=runner.repo)
            with tempfile.TemporaryDirectory(dir=args.state_dir) as tmp:
                export = runner.export(args.commit, args.harness_sha256, Path(tmp),
                                       runner._key())
                out = runner.sync_code(export.bundle, export.export_commit,
                                       export.source_commit, args.harness_sha256)
    except (HarnessFreezeError, SendRefused, DataRuleRefused, JobSpecRefused, RemoteRefused,
            RemoteBusy, ResultRefused) as exc:
        print(json.dumps({"ok": False, "refused": type(exc).__name__, "error": str(exc)}))
        return AGENT_BUSY if isinstance(exc, RemoteBusy) else AGENT_REFUSED
    print(json.dumps({"ok": True, **out}, sort_keys=True, default=str))
    exit_code = out.get("exit_code")
    return 0 if exit_code in (0, None) and not out.get("refused") else 1


if __name__ == "__main__":
    sys.exit(main())
