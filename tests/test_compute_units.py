"""Unit tests of the compute backend (Stage E.2b Task 5, V10): job spec, ledgers, manifests,
remote quoting, detachment, machine record, the git export, the agent's state machine and the
preflight refusals of every entry point. Synthetic data and tmp repositories only; no SSH here
(tests/test_compute_remote_e2e.py runs the backend over a localhost SSH server).
"""
from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

import pytest

from compute import agent, detach, remote
from compute.datarules import BACKTEST, NO_DATA, STEP2, TRAINING, DataFile, DataRules
from compute.files import dir_manifest, manifest_problems, sha256_file, write_json_atomic
from compute.gitbundle import (
    EXPORT_IDENTITY,
    INFO_ATTRIBUTES,
    ExportRefused,
    build_export,
    checkout_problems,
    materialize,
)
from compute.jobspec import KINDS, JobSpec, JobSpecRefused
from compute.ledger import JobLedger, LedgerCorrupt
from compute.machine import environment_problems, machine_record
from compute.transport import (
    HostConfig,
    RemoteArgRefused,
    RemoteResult,
    mkdirs_lines,
    put_lines,
    quote_remote,
    remote_command,
)
from screening.harness_freeze import HarnessFreezeError
from tests._compute_fixtures import FAKE_KEY, GIT_ENV, bar_file, git, sealed_blob

SHA = "a" * 64
COMMIT = "b" * 40


def data_file(product: str = "ES", store: str = STEP2) -> DataFile:
    name = f"ohlcv-1m_{product}_v_0_2019-05-06_2024-02-29_step2.parquet"
    return DataFile(store, product, name, "c" * 64, 10, "2019-05-09", "2019-05-15", 5)


def spec(**overrides: object) -> JobSpec:
    base = dict(job_id="job-1", kind="synthetic", user_args=("--items", "2"),
                data_root_kind=TRAINING, data_files=(data_file(),), threads=2,
                harness_sha256=SHA, source_commit=COMMIT, export_commit="d" * 40,
                excluded_paths=("ledger/databento_spend.jsonl",), created="2026-09-26")
    base.update(overrides)
    return JobSpec(**base)  # type: ignore[arg-type]


# ------------------------------------------------------------------ jobspec ----
def test_spec_round_trips_and_hashes_canonically() -> None:
    one = spec().validate()
    again = JobSpec.from_dict(json.loads(json.dumps(one.to_dict())))
    assert again == one and again.sha256() == one.sha256()
    assert spec(threads=3).sha256() != one.sha256()


def test_argv_fills_only_the_backends_placeholders() -> None:
    argv = spec().argv({"data_root": "/d", "out_dir": "/o", "harness_sha256": SHA})
    assert argv == ["--items", "2", "--data-root", "/d", "--out-dir", "/o"]
    fit = spec(kind="ml_fit", user_args=("--challenger", "lgbm", "--horizon", "h30"))
    assert fit.argv({"data_root": "/d", "out_dir": "/o", "harness_sha256": SHA}) == [
        "fit", "--challenger", "lgbm", "--horizon", "h30", "--store-root", "/d", "--out-dir",
        "/o", "--harness-sha256", SHA]
    with pytest.raises(JobSpecRefused, match="no value"):
        spec(kind="screening", data_root_kind=BACKTEST).argv({"out_dir": "/o"})


@pytest.mark.parametrize(("overrides", "match"), [
    ({"kind": "anything"}, "kind"),
    ({"job_id": "Bad ID"}, "job id"),
    ({"user_args": ("--out-dir", "/elsewhere")}, "backend's own option"),
    ({"user_args": ("--data-root=/x",)}, "backend's own option"),
    ({"user_args": ("{data_root}",)}, "characters"),
    ({"user_args": ("a;b",)}, "characters"),
    ({"threads": 0}, "threads"),
    ({"threads": 64}, "threads"),
    ({"harness_sha256": "short"}, "sha256"),
    ({"export_commit": "x"}, "commit"),
    ({"kind": "ml_fit", "data_root_kind": BACKTEST}, "data root"),
    ({"kind": "screening", "data_root_kind": TRAINING}, "data root"),
    ({"data_files": ()}, "no data files"),
    ({"kind": "ml_probe", "data_root_kind": NO_DATA}, "reads no data"),
    ({"data_files": (data_file(), data_file())}, "destination"),
])
def test_spec_validation_refuses(overrides: dict, match: str) -> None:
    with pytest.raises((JobSpecRefused, ValueError), match=match):
        spec(**overrides).validate()


def test_spec_refuses_a_module_other_than_the_registrys() -> None:
    raw = spec().to_dict()
    raw["module"] = "os"
    with pytest.raises(JobSpecRefused, match="module"):
        JobSpec.from_dict(raw)


def test_real_kinds_match_their_entry_points_arguments(capsys: pytest.CaptureFixture) -> None:
    """The backend's fixed options exist in each wired entry point's own parser."""
    from ml_route import probes, train
    from screening import stage_e_runner

    for main, argv, kind in ((stage_e_runner.main, ["--help"], "screening"),
                             (train.main, ["fit", "--help"], "ml_fit"),
                             (probes.main, ["--help"], "ml_probe")):
        with pytest.raises(SystemExit):
            main(argv)
        help_text = capsys.readouterr().out
        for option in KINDS[kind].reserved_options():
            assert option in help_text, (kind, option)


# ------------------------------------------------------------ ledger, files ----
def test_ledger_appends_reads_and_tolerates_only_a_torn_tail(tmp_path: Path) -> None:
    ledger = JobLedger(tmp_path / "l.jsonl")
    ledger.append("sent", files=2)
    ledger.append("started", token="t1")
    read = ledger.read()
    assert read.steps() == ("sent", "started") and read.last("started")["token"] == "t1"
    with ledger.path.open("ab") as handle:
        handle.write(b'{"step": "do')  # a crash mid-line
    torn = ledger.read()
    assert torn.truncated_tail and torn.steps() == ("sent", "started")
    ledger.append("done")
    assert ledger.read().steps() == ("sent", "started", "done")
    ledger.path.write_bytes(b'{"step": "a"}\nnot json\n{"step": "b"}\n')
    with pytest.raises(LedgerCorrupt):
        ledger.read()


def test_manifest_problems_name_every_difference(tmp_path: Path) -> None:
    root = tmp_path / "r"
    write_json_atomic(root / "a.json", {"x": 1})
    (root / "sub").mkdir()
    (root / "sub" / "b.txt").write_bytes(b"hello")
    manifest = dir_manifest(root)
    assert manifest_problems(root, manifest) == []
    (root / "sub" / "b.txt").write_bytes(b"hellO")
    (root / "extra.txt").write_bytes(b"x")
    (root / "a.json").unlink()
    problems = " | ".join(manifest_problems(root, manifest))
    assert "b.txt: sha256" in problems and "extra.txt: present but not in the manifest" in \
        problems and "a.json: in the manifest but missing" in problems
    manifest["sub/b.txt"] = {"bytes": 5}
    assert any("no sha256" in p for p in manifest_problems(root, manifest))
    assert manifest_problems(root, {}) == ["the manifest lists no files"]


# ---------------------------------------------------------------- transport ----
def test_remote_arguments_pass_both_shells_literally_or_are_refused() -> None:
    assert quote_remote("propexp/checkout", "posix") == "propexp/checkout"
    assert quote_remote("C:\\Users\\a\\x", "windows") == "C:\\Users\\a\\x"
    assert quote_remote("dir with space", "posix") == '"dir with space"'
    for bad in ("a;b", "$(x)", "a&b", "%PATH%", "a|b", "a\"b", "", "a`b", "x>y", "!x"):
        with pytest.raises(RemoteArgRefused):
            quote_remote(bad, "windows")
    with pytest.raises(RemoteArgRefused):
        quote_remote("C:\\x", "posix")  # sh would read the backslash as an escape
    with pytest.raises(RemoteArgRefused):
        quote_remote("C:\\with space\\", "windows")  # a trailing backslash escapes the quote
    assert remote_command(["git", "-C", "a b", "status"], "posix") == 'git -C "a b" status'


def test_host_config_validation(tmp_path: Path) -> None:
    base = {"schema": "propexperiment-compute-host/1", "name": "pc", "host": "192.168.1.20",
            "user": "me", "identity_file": str(tmp_path / "k"),
            "known_hosts_file": str(tmp_path / "kh"), "remote_os": "windows"}
    path = tmp_path / "h.json"
    path.write_text(json.dumps(base), encoding="utf-8")
    host = HostConfig.load(path)
    assert host.detach == detach.WINDOWS_BREAKAWAY and host.checkout == "propexp/checkout"
    for change in ({"detach": "posix_session"}, {"agent_root": "../x"},
                   {"agent_root": "C:/propexp"}, {"remote_os": "mac"}, {"host": "a;b"},
                   {"launcher": ["python"]}, {"schema": "x"}):
        path.write_text(json.dumps({**base, **change}), encoding="utf-8")
        with pytest.raises((ValueError, KeyError, detach.DetachRefused)):
            HostConfig.load(path)


def test_sftp_batch_lines_stage_uploads_and_quote_paths() -> None:
    assert mkdirs_lines("propexp/jobs/j1") == ['-mkdir "propexp"', '-mkdir "propexp/jobs"',
                                               '-mkdir "propexp/jobs/j1"']
    lines = put_lines(Path("/l/f.parquet"), "propexp/data/f.parquet", "propexp/incoming/f.p")
    assert lines == ['put "/l/f.parquet" "propexp/incoming/f.p"', '-rm "propexp/data/f.parquet"',
                     'rename "propexp/incoming/f.p" "propexp/data/f.parquet"']
    with pytest.raises(RemoteArgRefused):
        put_lines(Path('/l/"x'), "a", "b")


def test_remote_result_reads_the_last_json_line() -> None:
    result = RemoteResult(0, 'warning: x\n{"ok": true, "a": 1}\n', "")
    assert result.last_json() == {"ok": True, "a": 1}
    assert RemoteResult(1, "no json", "").last_json() is None


# ------------------------------------------------------------------- detach ----
def test_detach_methods_fit_their_os_and_build_the_documented_flags(tmp_path: Path) -> None:
    detach.check_method(detach.POSIX_SESSION, windows=False)
    detach.check_method(detach.WINDOWS_BREAKAWAY, windows=True)
    for method, windows in ((detach.POSIX_SESSION, True), (detach.WINDOWS_SCHTASKS, False),
                            ("nohup", False)):
        with pytest.raises(detach.DetachRefused):
            detach.check_method(method, windows=windows)
    assert detach.popen_kwargs(detach.POSIX_SESSION) == {"start_new_session": True,
                                                        "close_fds": True}
    flags = detach.popen_kwargs(detach.WINDOWS_BREAKAWAY)["creationflags"]
    assert flags == 0x01000000 | 0x00000008 | 0x00000200 | 0x00004000
    wrapper = detach.schtasks_wrapper(["C:\\py.exe", "-m", "compute.agent"],
                                      Path("C:/pe/checkout"), Path("C:/pe/jobs/j/worker.log"))
    assert wrapper.startswith("@echo off\r\ncd /d ") and wrapper.endswith('2>&1\r\n')
    with pytest.raises(detach.DetachRefused):
        detach.schtasks_wrapper(["%x%"], Path("c"), Path("l"))
    create, run = detach.schtasks_argv("PropExperiment-j", Path("C:/pe/worker.cmd"))
    assert create[:3] == ["schtasks", "/Create", "/F"] and run == [
        "schtasks", "/Run", "/TN", "PropExperiment-j"]


def test_a_posix_session_worker_survives_its_parents_process_group_being_killed(
        tmp_path: Path) -> None:
    """What sshd does to a session's processes at disconnect; the detached one lives on."""
    child = tmp_path / "child.py"
    child.write_text("import sys, time\ntime.sleep(3)\n"
                     "open(sys.argv[1], 'w', encoding='utf-8').write('alive')\n",
                     encoding="utf-8")
    script = tmp_path / "parent.py"
    marker = tmp_path / "survivor.txt"
    script.write_text(
        "import os, subprocess, sys, time\n"
        "from pathlib import Path\n"
        "from compute import detach\n"
        f"child = [sys.executable, {str(child)!r}, {str(marker)!r}]\n"
        f"detach.spawn('posix_session', child, cwd=Path({str(tmp_path)!r}), "
        f"log=Path({str(tmp_path / 'w.log')!r}), env=dict(os.environ), task_name='t')\n"
        "plain = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(30)'])\n"
        "print(plain.pid, flush=True)\n"
        "time.sleep(30)\n", encoding="utf-8")
    repo = Path(__file__).parents[1]
    parent = subprocess.Popen([sys.executable, str(script)], cwd=repo,
                              env={**os.environ, "PYTHONPATH": str(repo)},
                              stdout=subprocess.PIPE, start_new_session=True)
    plain_pid = int(parent.stdout.readline())
    os.killpg(parent.pid, signal.SIGKILL)
    parent.wait()
    time.sleep(0.5)
    with pytest.raises(ProcessLookupError):  # the undetached child died with the group
        os.kill(plain_pid, 0)
    deadline = time.monotonic() + 10
    while not marker.exists() and time.monotonic() < deadline:
        time.sleep(0.2)
    assert marker.read_text(encoding="utf-8") == "alive"


# ------------------------------------------------------------------ machine ----
def test_machine_record_names_the_machine() -> None:
    record = machine_record()
    for key in ("hostname", "os", "cpu", "logical_cpus", "memory_bytes", "gpu", "packages"):
        assert key in record
    assert record["hostname"] and record["packages"]["numpy"]


def test_environment_is_checked_against_the_lock(tmp_path: Path) -> None:
    import numpy

    lock = tmp_path / "uv.lock"
    lock.write_text(f'[[package]]\nname = "numpy"\nversion = "{numpy.__version__}"\n',
                    encoding="utf-8")
    assert environment_problems(lock, ("numpy",)) == []
    lock.write_text('[[package]]\nname = "numpy"\nversion = "0.0.1"\n', encoding="utf-8")
    assert "numpy" in environment_problems(lock, ("numpy",))[0]
    assert environment_problems(Path(__file__).parents[1] / "uv.lock") == []


# ------------------------------------------------------------------ git export ----
def _repo(tmp: Path, files: dict[str, bytes]) -> tuple[Path, str]:
    repo = tmp / "src"
    repo.mkdir()
    for rel, data in files.items():
        (repo / rel).parent.mkdir(parents=True, exist_ok=True)
        (repo / rel).write_bytes(data)
    git(repo, "init", "-q", "-b", "main")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "x")
    return repo, git(repo, "rev-parse", "HEAD")


BASE = {"compute/a.py": b"print('a')\n", "docs/n.md": b"line\r\nwindows\r\n",
        "ledger/databento_spend.jsonl": b'{"usd": 3}\n'}


def test_export_cuts_the_ledger_and_is_deterministic(tmp_path: Path) -> None:
    repo, commit = _repo(tmp_path, BASE)
    one = build_export(repo, commit, tmp_path / "w1", FAKE_KEY.encode())
    two = build_export(repo, "HEAD", tmp_path / "w2", FAKE_KEY.encode())
    assert one.export_commit == two.export_commit != commit
    assert one.excluded == ("ledger/databento_spend.jsonl",) and one.files == 2
    tree = tmp_path / "tree"
    materialize(one, tree)
    assert not (tree / "ledger").exists()
    assert (tree / "docs" / "n.md").read_bytes() == BASE["docs/n.md"]  # CRLF kept as committed
    assert git(repo, "status", "--porcelain") == ""  # the source repository is untouched
    assert git(repo, "for-each-ref") .count("refs/") == 1
    assert EXPORT_IDENTITY["GIT_COMMITTER_DATE"] in "2000-01-01T00:00:00+0000"


@pytest.mark.parametrize(("rel", "data", "match"), [
    (".env", b"DATABENTO_API_KEY=x\n", "environment file"),
    ("config/.env.local", b"x=1\n", "environment file"),
    ("reports/log.txt", b"key " + FAKE_KEY.encode() + b"\n", "Databento key"),
    ("data/sealed/x.bin", b"x", "never travel"),
    ("data/blob.sealed", b"x", "never travel"),
    ("reports/bars.parquet", b"PAR1", "never travel"),
    ("data/raw.dbn.zst", b"x", "never travel"),
])
def test_export_refuses_a_commit_holding_forbidden_content(tmp_path: Path, rel: str,
                                                           data: bytes, match: str) -> None:
    repo, commit = _repo(tmp_path, {**BASE, rel: data})
    with pytest.raises(ExportRefused, match=match):
        build_export(repo, commit, tmp_path / "w", FAKE_KEY.encode())


def test_export_refuses_sealed_bytes_under_any_name(tmp_path: Path) -> None:
    blob = sealed_blob(tmp_path / "blob")
    repo, commit = _repo(tmp_path, {**BASE, "reports/innocent.json": blob.read_bytes()})
    with pytest.raises(ExportRefused, match="sealed holdout blob"):
        build_export(repo, commit, tmp_path / "w", FAKE_KEY.encode())


def _far_checkout(tmp: Path, export) -> Path:  # noqa: ANN001
    checkout = tmp / "far" / "checkout"
    subprocess.run(["git", "clone", "-q", "--no-checkout", "--config", "core.autocrlf=false",
                    str(export.bundle), str(checkout)], check=True, capture_output=True)
    (checkout / ".git" / "info").mkdir(parents=True, exist_ok=True)
    (checkout / ".git" / "info" / "attributes").write_text(INFO_ATTRIBUTES, encoding="utf-8")
    subprocess.run(["git", "-C", str(checkout), "checkout", "-q", "--detach",
                    export.export_commit], check=True, capture_output=True,
                   env={**os.environ, **GIT_ENV})
    return checkout


def test_far_checkout_is_proven_byte_identical_and_any_change_is_caught(tmp_path: Path) -> None:
    repo, commit = _repo(tmp_path, BASE)
    export = build_export(repo, commit, tmp_path / "w", FAKE_KEY.encode())
    checkout = _far_checkout(tmp_path, export)
    assert checkout_problems(checkout, export.export_commit) == []
    target = checkout / "compute" / "a.py"
    target.write_bytes(target.read_bytes().replace(b"\n", b"\r\n"))  # an autocrlf conversion
    assert any("compute/a.py: bytes differ" in p
               for p in checkout_problems(checkout, export.export_commit))
    assert any("HEAD" in p for p in checkout_problems(checkout, commit))
    (checkout / ".git" / "info" / "attributes").unlink()
    assert any("attributes" in p for p in checkout_problems(checkout, export.export_commit))


# --------------------------------------------------------------- agent state ----
@pytest.fixture()
def far(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A fake far side: <root>/checkout is the agent's REPO_ROOT; code checks pass."""
    root = tmp_path / "agent"
    (root / "checkout").mkdir(parents=True)
    monkeypatch.setattr(agent, "REPO_ROOT", root / "checkout")
    monkeypatch.setattr(agent, "checkout_problems", lambda *a, **k: [])
    monkeypatch.setattr(agent, "environment_problems", lambda *a, **k: [])
    monkeypatch.setattr(agent, "preflight", lambda sha, root=None: sha)
    return root


def _received_job(root: Path, tmp: Path) -> JobSpec:
    source = bar_file(tmp / "src", STEP2, "ES")
    item = DataFile(STEP2, "ES", source.name, sha256_file(source), source.stat().st_size,
                    "x", "y", 5)
    job = spec(data_files=(item,), export_commit="d" * 40)
    dest = root / item.dest(TRAINING)
    dest.parent.mkdir(parents=True)
    dest.write_bytes(source.read_bytes())
    write_json_atomic(root / "jobs" / job.job_id / "job.json.incoming", job.to_dict())
    return job


def run_agent(argv: list[str], capsys: pytest.CaptureFixture) -> tuple[int, dict]:
    code = agent.main(argv)
    return code, json.loads(capsys.readouterr().out.strip().splitlines()[-1])


def test_agent_receives_checks_and_reports_state(far: Path, tmp_path: Path,
                                                 capsys: pytest.CaptureFixture) -> None:
    job = _received_job(far, tmp_path)
    common = ["--job-id", job.job_id, "--harness-sha256", SHA]
    code, out = run_agent(["inventory", *common], capsys)
    assert code == 0 and list(out["present"].values()) == [job.data_files[0].sha256]
    code, out = run_agent(["receive", *common], capsys)
    assert code == 0 and out["spec_sha256"] == job.sha256()
    code, out = run_agent(["status", "--job-id", job.job_id], capsys)
    assert out["state"] == "received"
    jobdir = far / "jobs" / job.job_id
    ledger = JobLedger(jobdir / "ledger.jsonl")
    ledger.append("started", token="t1")
    assert agent.job_state(jobdir, 30)["state"] == "stale"  # no heartbeat yet
    agent.heartbeat_path(jobdir, "t1").touch()
    assert agent.job_state(jobdir, 30)["state"] == "running"
    assert agent.running_jobs(far, 30, exclude="other") == [job.job_id]
    ledger.append("done", token="t0", exit_code=0)  # a superseded worker's late answer
    assert agent.job_state(jobdir, 30)["state"] == "running"
    ledger.append("done", token="t1", exit_code=2, manifest_sha256=SHA)
    assert agent.job_state(jobdir, 30)["state"] == "failed"


def test_agent_refuses_a_tampered_received_file_and_a_reused_job_id(
        far: Path, tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    job = _received_job(far, tmp_path)
    dest = far / job.data_files[0].dest(TRAINING)
    dest.write_bytes(dest.read_bytes() + b"x")
    code, out = run_agent(["receive", "--job-id", job.job_id, "--harness-sha256", SHA], capsys)
    assert code == agent.EXIT_REFUSED and out["kind"] == "hash-mismatch"
    other = spec(threads=5)
    write_json_atomic(far / "jobs" / job.job_id / "job.json.incoming", other.to_dict())
    code, out = run_agent(["inventory", "--job-id", job.job_id, "--harness-sha256", SHA], capsys)
    assert code == agent.EXIT_REFUSED and "different spec" in out["error"]


def test_agent_start_refuses_when_another_job_runs(far: Path, tmp_path: Path,
                                                   capsys: pytest.CaptureFixture) -> None:
    job = _received_job(far, tmp_path)
    run_agent(["receive", "--job-id", job.job_id, "--harness-sha256", SHA], capsys)
    busy = far / "jobs" / "other-job"
    JobLedger(busy / "ledger.jsonl").append("started", token="zz")
    agent.heartbeat_path(busy, "zz").touch()
    code, out = run_agent(["start", "--job-id", job.job_id, "--harness-sha256", SHA,
                           "--detach", "posix_session"], capsys)
    assert code == agent.EXIT_BUSY and "other-job" in out["busy"]


def test_agent_refuses_to_run_outside_a_checkout_directory(tmp_path: Path) -> None:
    with pytest.raises(agent.CodeRefused, match="checkout"):
        agent.agent_root(tmp_path / "somewhere")


# ------------------------------------ every entry refuses when preflight raises ----
def _raise(*args: object, **kwargs: object) -> str:
    raise HarnessFreezeError("Stage E harness preflight refused: planted")


@pytest.mark.parametrize("command", ["verify-code", "inventory", "receive", "start"])
def test_agent_entries_refuse_when_preflight_raises(command: str, far: Path, tmp_path: Path,
                                                    monkeypatch: pytest.MonkeyPatch,
                                                    capsys: pytest.CaptureFixture) -> None:
    job = _received_job(far, tmp_path)
    if command == "start":
        run_agent(["receive", "--job-id", job.job_id, "--harness-sha256", SHA], capsys)
    monkeypatch.setattr(agent, "preflight", _raise)
    argv = {"verify-code": ["verify-code", "--commit", COMMIT, "--source-commit", COMMIT,
                            "--harness-sha256", SHA],
            "inventory": ["inventory", "--job-id", job.job_id, "--harness-sha256", SHA],
            "receive": ["receive", "--job-id", job.job_id, "--harness-sha256", SHA],
            "start": ["start", "--job-id", job.job_id, "--harness-sha256", SHA, "--detach",
                      "posix_session"]}[command]
    code, out = run_agent(argv, capsys)
    assert code == agent.EXIT_REFUSED and out["refused"] == "HarnessFreezeError"
    assert not (far / "jobs" / job.job_id / "result").exists()


def test_agent_worker_refuses_and_records_it_when_preflight_raises(
        far: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture) -> None:
    job = _received_job(far, tmp_path)
    run_agent(["receive", "--job-id", job.job_id, "--harness-sha256", SHA], capsys)
    jobdir = far / "jobs" / job.job_id
    JobLedger(jobdir / "ledger.jsonl").append("started", token="t9")
    monkeypatch.setattr(agent, "preflight", _raise)
    monkeypatch.setattr(agent, "lower_priority", lambda: None)
    code, out = run_agent(["run-worker", "--job-id", job.job_id, "--token", "t9",
                           "--harness-sha256", SHA], capsys)
    assert code == 0 and out["state"] == "failed"
    record = json.loads((jobdir / "result" / "record.json").read_text(encoding="utf-8"))
    assert "HarnessFreezeError" in record["refused"] and "exit_code" not in record
    assert agent.job_state(jobdir, 30)["state"] == "failed"
    assert not (jobdir / "result" / "out").exists()  # the job never ran


class NoTransport:
    """Any call fails the test: a refusal must come before anything is sent."""

    def __init__(self, host: HostConfig) -> None:
        self.host = host

    def run(self, *a: object, **k: object) -> None:
        raise AssertionError("ssh was called")

    agent = sftp = run


@pytest.fixture()
def runner(tmp_path: Path) -> remote.RemoteRunner:
    host = HostConfig("pc", "127.0.0.1", "me", 22, tmp_path / "k", tmp_path / "kh", "propexp",
                      "posix", "posix_session")
    rules = DataRules((tmp_path / "sealed",), (tmp_path / "ledger",), (tmp_path / ".env",))
    return remote.RemoteRunner(NoTransport(host), tmp_path / "state", repo=tmp_path,  # type: ignore[arg-type]
                               rules=rules, key_loader=lambda: FAKE_KEY)


def _submission(paths: tuple[Path, ...], **kw: object) -> remote.Submission:
    base = dict(kind="synthetic", user_args=(), data_root_kind=TRAINING, data_paths=paths,
                threads=2, harness_sha256=SHA, commit="HEAD", job_id="j1")
    base.update(kw)
    return remote.Submission(**base)  # type: ignore[arg-type]


def test_remote_submit_and_resume_refuse_when_preflight_raises(
        runner: remote.RemoteRunner, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(remote, "preflight", _raise)
    with pytest.raises(HarnessFreezeError):
        runner.submit(_submission((bar_file(tmp_path, STEP2),)), wait=False, max_wait_s=0)
    with pytest.raises(HarnessFreezeError):
        runner.run("j1", SHA, wait=False, max_wait_s=0)
    assert not (tmp_path / "state" / "j1").exists()


def test_remote_sync_code_cli_refuses_when_preflight_raises(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture) -> None:
    monkeypatch.setattr(remote, "preflight", _raise)
    monkeypatch.setattr(remote, "SSHTransport", NoTransport)
    host = tmp_path / "h.json"
    host.write_text(json.dumps({"schema": "propexperiment-compute-host/1", "name": "pc",
                                "host": "h", "user": "u", "identity_file": "k",
                                "known_hosts_file": "kh", "remote_os": "windows"}),
                    encoding="utf-8")
    (tmp_path / "state").mkdir()
    code = remote.main(["sync-code", "--host-config", str(host), "--state-dir",
                        str(tmp_path / "state"), "--harness-sha256", SHA, "--commit", "HEAD"])
    assert code == remote.AGENT_REFUSED
    assert json.loads(capsys.readouterr().out)["refused"] == "HarnessFreezeError"


def test_remote_refuses_without_the_key_to_scan_for(runner: remote.RemoteRunner, tmp_path: Path,
                                                    monkeypatch: pytest.MonkeyPatch) -> None:
    from data.config import MissingSecretError

    def missing() -> str:
        raise MissingSecretError("DATABENTO_API_KEY is not set")

    monkeypatch.setattr(remote, "preflight", lambda sha, root=None: sha)
    runner.key_loader = missing
    with pytest.raises(remote.SendRefused, match="cannot scan"):
        runner.prepare(_submission((bar_file(tmp_path, STEP2),)))


def test_remote_refuses_a_research_file_for_a_training_job(
        runner: remote.RemoteRunner, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from compute.datarules import RESEARCH, DataRuleRefused

    monkeypatch.setattr(remote, "preflight", lambda sha, root=None: sha)
    with pytest.raises(DataRuleRefused) as refused:
        runner.prepare(_submission((bar_file(tmp_path, RESEARCH),)))
    assert refused.value.kind == "not-allowlisted"


def test_waiting_restarts_a_stale_worker_a_bounded_number_of_times_and_refuses_absence(
        runner: remote.RemoteRunner, monkeypatch: pytest.MonkeyPatch) -> None:
    states = iter([{"state": "stale"}, {"state": "running"}, {"state": "done", "exit_code": 0}])
    starts: list[str] = []
    monkeypatch.setattr(runner, "status", lambda job_id: next(states))
    monkeypatch.setattr(runner, "start", lambda job: starts.append(job.job_id))
    runner.poll_s = 0.0
    assert runner.wait(spec(), 60)["state"] == "done" and starts == ["job-1"]
    monkeypatch.setattr(runner, "status", lambda job_id: {"state": "stale"})
    with pytest.raises(remote.RemoteError, match="restarted 3 times"):
        runner.wait(spec(), 60)
    monkeypatch.setattr(runner, "status", lambda job_id: {"state": "absent"})
    with pytest.raises(remote.RemoteError, match="no record"):
        runner.wait(spec(), 60)
    monkeypatch.setattr(runner, "status", lambda job_id: {"state": "running"})
    assert runner.wait(spec(), 0) is None  # past the wait budget: resume later


# ------------------------------------------------------- results verification ----
def _result_dir(tmp: Path, job: JobSpec) -> tuple[Path, str]:
    root = tmp / "result"
    write_json_atomic(root / "out" / "a.json", {"a": 1})
    write_json_atomic(root / "record.json", {"job_id": job.job_id, "export_commit":
                                             job.export_commit, "spec_sha256": job.sha256(),
                                             "harness_sha256": job.harness_sha256,
                                             "exit_code": 0})
    digest = write_json_atomic(root / "manifest.json", dir_manifest(
        root, exclude=frozenset({"manifest.json"})))
    return root, digest


def test_results_verify_only_when_every_file_matches(tmp_path: Path) -> None:
    job = spec()
    root, digest = _result_dir(tmp_path, job)
    assert remote.verify_results(root, job, digest)["exit_code"] == 0


@pytest.mark.parametrize("tamper", ["changed byte", "unhashed extra file", "missing file",
                                    "no manifest", "manifest swapped", "no recorded hash",
                                    "record of another job"])
def test_results_are_refused_on_any_hash_problem(tamper: str, tmp_path: Path) -> None:
    job = spec()
    root, digest = _result_dir(tmp_path, job)
    if tamper == "changed byte":
        (root / "out" / "a.json").write_text('{"a": 2}\n', encoding="utf-8")
    elif tamper == "unhashed extra file":
        (root / "out" / "b.json").write_text("{}", encoding="utf-8")
    elif tamper == "missing file":
        (root / "out" / "a.json").unlink()
    elif tamper == "no manifest":
        (root / "manifest.json").unlink()
    elif tamper == "manifest swapped":
        write_json_atomic(root / "manifest.json", dir_manifest(
            root, exclude=frozenset({"manifest.json"})) | {"x": {"sha256": SHA, "bytes": 1}})
    elif tamper == "no recorded hash":
        digest = ""
    else:
        write_json_atomic(root / "record.json", {"job_id": "someone-else"})
        digest = write_json_atomic(root / "manifest.json", dir_manifest(
            root, exclude=frozenset({"manifest.json"})))
    with pytest.raises(remote.ResultRefused):
        remote.verify_results(root, job, digest)
