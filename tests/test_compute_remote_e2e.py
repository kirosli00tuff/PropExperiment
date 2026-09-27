"""The compute backend end to end over SSH to this machine (Stage E.2b Task 5, V10).

A user-level SSH server (asyncssh, 127.0.0.1, a free port, throwaway keys) stands in for the
Windows PC's OpenSSH server; the system ssh and sftp clients talk to it exactly as they will to
the PC. The far side's "home" is a tmp directory; its checkout comes from a git bundle of a tiny
harness repository whose manifest the real preflight checks at both ends. Jobs are the synthetic
job on synthetic bars. Covered: a full run (code sync, send, detached start, poll, pull, hash
check), dedupe of code and data on a second job, a backtest root separate from the training
root, a ThinkPad-side interruption resumed from the local ledger, a worker killed on the far
side restarted from the far ledger and resuming its own progress, an SSH session ending while
the job runs, results refused on a hash mismatch, a training job refused for a research-window
file in its root, forbidden files refused before anything is sent, and far-side tampering with
the checkout caught and repaired.
"""
from __future__ import annotations

import json
import os
import platform
import signal
import time
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import pytest

from compute.datarules import RESEARCH, STEP2, DataRuleRefused, DataRules
from compute.ledger import JobLedger
from compute.remote import RemoteRefused, RemoteRunner, ResultRefused, Submission
from compute.transport import HostConfig, SSHTransport
from tests._compute_fixtures import (
    FAKE_KEY,
    LocalSSHServer,
    bar_file,
    make_client_key,
    make_tiny_repo,
    server_env,
    store_name,
    trading_days,
    write_host_config,
)
from tests.test_compute_datarules import FORBIDDEN

pytestmark = pytest.mark.skipif(os.name != "posix", reason="the localhost server runs sh")
STALE_S = 6.0


@dataclass
class Far:
    root: Path
    repo: Path
    harness: str
    commit: str
    home: Path
    key: Path
    rules: DataRules
    server: LocalSSHServer

    @property
    def agent_root(self) -> Path:
        return self.home / "propexp"

    def runner(self, server: LocalSSHServer | None = None, name: str = "host.json"
               ) -> RemoteRunner:
        server = server or self.server
        config = write_host_config(self.root / name, server, self.key,
                                   self.root / f"known_hosts_{server.port}")
        return RemoteRunner(SSHTransport(HostConfig.load(config)), self.root / "state",
                            repo=self.repo, rules=self.rules, key_loader=lambda: FAKE_KEY,
                            poll_s=0.5, stale_after_s=STALE_S)

    def submission(self, job_id: str, files: tuple[Path, ...], *, root_kind: str = "training",
                   args: tuple[str, ...] = ("--items", "2")) -> Submission:
        return Submission(kind="synthetic", user_args=args, data_root_kind=root_kind,
                          data_paths=files, threads=2, harness_sha256=self.harness,
                          commit=self.commit, job_id=job_id)


def start_far(root: Path) -> Far:
    repo, harness, commit = make_tiny_repo(root)
    home = root / "home"
    home.mkdir()
    key = make_client_key(root)
    rules = DataRules((root / "local" / "sealed",), (root / "local" / "ledger",),
                      (root / "local" / ".env",))
    server = LocalSSHServer(home, key.with_suffix(".pub"), server_env()).start()
    return Far(root, repo, harness, commit, home, key, rules, server)


@pytest.fixture(scope="module")
def far(tmp_path_factory: pytest.TempPathFactory):  # noqa: ANN201
    env = start_far(tmp_path_factory.mktemp("far"))
    yield env
    env.server.stop()


@pytest.fixture(scope="module")
def step2_file(far: Far) -> Path:
    return bar_file(far.root / "local" / "processed_step2", STEP2, "ES")


def steps(runner: RemoteRunner, job_id: str) -> list[str]:
    return list(runner.ledger(job_id).read().steps())


def far_ledger(far: Far, job_id: str) -> JobLedger:
    return JobLedger(far.agent_root / "jobs" / job_id / "ledger.jsonl")


def wait_for(predicate, timeout: float = 30.0) -> None:  # noqa: ANN001
    deadline = time.monotonic() + timeout
    while not predicate():
        if time.monotonic() > deadline:
            raise AssertionError("condition not reached in time")
        time.sleep(0.3)


def test_a_synthetic_training_job_runs_end_to_end(far: Far, step2_file: Path) -> None:
    runner = far.runner()
    out = runner.submit(far.submission("e2e-train-1", (step2_file,)), wait=True, max_wait_s=90)
    assert out["state"] == "verified" and out["exit_code"] == 0
    assert steps(runner, "e2e-train-1") == ["prepared", "code_synced", "sent", "started", "done",
                                            "pulled", "verified"]
    results = runner.job_state_dir("e2e-train-1") / "results"
    record = json.loads((results / "record.json").read_text(encoding="utf-8"))
    summary = json.loads((results / "out" / "summary.json").read_text(encoding="utf-8"))
    assert record["machine"]["hostname"] == platform.node()
    assert record["harness_sha256"] == far.harness and record["exit_code"] == 0
    assert summary["priority"] == "nice 10" and summary["threads"]["OMP_NUM_THREADS"] == "2"
    assert summary["inputs"] == {f"ES/{step2_file.name}": 5}
    assert not (runner.job_state_dir("e2e-train-1") / "export").exists()  # no bundle per job
    checkout = far.agent_root / "checkout"
    assert not (checkout / "ledger").exists()  # the tracked ledger never leaves
    assert (far.repo / "ledger" / "databento_spend.jsonl").exists()
    prepared = runner.ledger("e2e-train-1").read().last("prepared")
    assert prepared["excluded"] == ["ledger/databento_spend.jsonl"]
    for path in far.home.rglob("*"):  # the key never reached the far side
        if path.is_file():
            assert FAKE_KEY.encode() not in path.read_bytes(), path


def test_a_second_job_reuses_the_checkout_and_the_data_already_there(far: Far,
                                                                      step2_file: Path) -> None:
    runner = far.runner()
    before = len(far.server.commands)
    out = runner.submit(far.submission("e2e-train-2", (step2_file,)), wait=True, max_wait_s=90)
    assert out["state"] == "verified"
    sent = runner.ledger("e2e-train-2").read().last("sent")
    assert (sent["uploaded"], sent["skipped"]) == (0, 1)
    assert not any(" fetch " in c or " clone " in c for c in far.server.commands[before:])


def test_a_backtest_job_gets_its_own_root_holding_both_stores(far: Far, step2_file: Path) -> None:
    research = bar_file(far.root / "local" / "processed", RESEARCH, "ES")
    runner = far.runner()
    out = runner.submit(far.submission("e2e-backtest-1", (research, step2_file),
                                       root_kind="backtest"), wait=True, max_wait_s=90)
    assert out["state"] == "verified"
    backtest = far.agent_root / "data" / "backtest"
    assert (backtest / "research" / "ES" / research.name).is_file()
    assert (backtest / "step2" / "ES" / step2_file.name).is_file()
    training = far.agent_root / "data" / "training"
    assert not any(p.name == research.name for p in training.rglob("*"))


def test_an_interruption_on_the_thinkpad_resumes_from_the_local_ledger(
        far: Far, step2_file: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    runner = far.runner()

    def interrupted(spec):  # noqa: ANN001, ANN202
        raise KeyboardInterrupt("ThinkPad session died after sending")

    monkeypatch.setattr(runner, "start", interrupted)
    with pytest.raises(KeyboardInterrupt):
        runner.submit(far.submission("e2e-resume-1", (step2_file,)), wait=True, max_wait_s=90)
    assert steps(runner, "e2e-resume-1") == ["prepared", "code_synced", "sent"]
    resumed = far.runner()
    batches: list[list[str]] = []
    real_sftp = resumed.transport.sftp
    monkeypatch.setattr(resumed.transport, "sftp",
                        lambda lines, **kw: (batches.append(lines), real_sftp(lines, **kw))[1])
    out = resumed.run("e2e-resume-1", far.harness, wait=True, max_wait_s=90)
    assert out["state"] == "verified"
    assert all(not line.startswith("put") for batch in batches for line in batch)
    assert steps(resumed, "e2e-resume-1")[3:] == ["started", "done", "pulled", "verified"]


def test_a_worker_killed_on_the_far_side_restarts_and_resumes_its_own_progress(
        far: Far, step2_file: Path) -> None:
    runner = far.runner()
    job = "e2e-kill-1"
    out = runner.submit(far.submission(job, (step2_file,), args=("--items", "5", "--sleep-s",
                                                                  "1.0")),
                        wait=False, max_wait_s=0)
    assert out["state"] == "running"
    computed = far.agent_root / "jobs" / job / "result" / "out" / "computed.jsonl"
    wait_for(lambda: computed.exists() and len(computed.read_text().splitlines()) >= 2)
    pid = far_ledger(far, job).read().last("spawned")["pid"]
    os.killpg(pid, signal.SIGKILL)  # the worker and its job, as a crash or reboot would
    out = runner.run(job, far.harness, wait=True, max_wait_s=120)
    assert out["state"] == "verified" and out["exit_code"] == 0
    items = [json.loads(line)["item"] for line in computed.read_text().splitlines()]
    assert len(items) == len(set(items)), "an item was computed twice"
    results = runner.job_state_dir(job) / "results"
    assert sorted(p.name for p in (results / "out" / "items").iterdir()) == [
        f"item_{i}.json" for i in range(5)]
    record = json.loads((results / "record.json").read_text(encoding="utf-8"))
    assert record["restarts"] == 1
    assert "restart_requested" in steps(runner, job)
    assert far_ledger(far, job).read().has("restarted")


def test_the_ssh_session_ending_does_not_stop_a_running_job(tmp_path: Path) -> None:
    own = start_far(tmp_path)
    try:
        data = bar_file(own.root / "local" / "processed_step2", STEP2, "ES")
        runner = own.runner()
        job = "e2e-hangup-1"
        runner.submit(own.submission(job, (data,), args=("--items", "4", "--sleep-s", "1.0")),
                      wait=False, max_wait_s=0)
        own.server.stop()  # every session's process group is killed, as sshd does
        token = runner.ledger(job).read().last("started")["token"]
        beat = own.agent_root / "jobs" / job / f"heartbeat-{token}"
        stopped_at = time.time()
        wait_for(lambda: beat.stat().st_mtime > stopped_at + 1.0, timeout=15)
        second = LocalSSHServer(own.home, own.key.with_suffix(".pub"), server_env()).start()
        own.server = second
        out = own.runner(second, "host2.json").run(job, own.harness, wait=True, max_wait_s=90)
        assert out["state"] == "verified"
        record = json.loads((runner.job_state_dir(job) / "results" / "record.json")
                            .read_text(encoding="utf-8"))
        assert record["restarts"] == 0
    finally:
        own.server.stop()


def test_results_that_do_not_match_their_hashes_are_refused(far: Far, step2_file: Path) -> None:
    runner = far.runner()
    job = "e2e-tamper-1"
    runner.submit(far.submission(job, (step2_file,), args=("--items", "1")), wait=False,
                  max_wait_s=0)
    wait_for(lambda: runner.status(job)["state"] == "done")
    item = far.agent_root / "jobs" / job / "result" / "out" / "items" / "item_0.json"
    item.write_text('{"item": 0, "tampered": true}\n', encoding="utf-8")
    with pytest.raises(ResultRefused, match="item_0.json"):
        runner.run(job, far.harness, wait=True, max_wait_s=30)
    assert "verified" not in steps(runner, job)
    assert not (runner.job_state_dir(job) / "results").exists()


@pytest.mark.parametrize("case", sorted(FORBIDDEN))
def test_forbidden_files_are_refused_before_anything_is_sent(case: str, far: Far,
                                                             tmp_path: Path) -> None:
    build, kind = FORBIDDEN[case]
    local = tmp_path / "t"
    rules = DataRules((local / "repo" / "data" / "sealed",),
                      (local / "repo" / "ledger", local / "ext" / "ledger.jsonl"),
                      (local / "repo" / ".env",))
    runner = far.runner()
    runner.rules = rules
    before = len(far.server.commands)
    with pytest.raises(DataRuleRefused) as refused:
        runner.submit(far.submission(f"e2e-forbidden-{sorted(FORBIDDEN).index(case)}",
                                     (build(local),), root_kind="backtest"),
                      wait=False, max_wait_s=0)
    assert refused.value.kind == kind
    assert len(far.server.commands) == before  # nothing reached the far side


def test_far_checkout_tampering_is_caught_then_repaired_by_the_next_sync(
        far: Far, step2_file: Path) -> None:
    runner = far.runner()
    target = far.agent_root / "checkout" / "compute" / "files.py"
    original = target.read_bytes()
    target.write_bytes(original.replace(b"\n", b"\r\n"))  # what core.autocrlf=true would do
    answer = runner.transport.agent("verify-code", "--commit", runner.load("e2e-train-1")[0]
                                    .export_commit, "--source-commit", far.commit,
                                    "--harness-sha256", far.harness)
    assert answer.returncode == 3 and "compute/files.py" in answer.stdout
    out = runner.submit(far.submission("e2e-repair-1", (step2_file,)), wait=True, max_wait_s=90)
    assert out["state"] == "verified" and target.read_bytes() == original


def test_a_training_job_is_refused_when_its_root_holds_research_window_bars(
        far: Far, step2_file: Path) -> None:
    training = far.agent_root / "data" / "training"
    planted = bar_file(training, RESEARCH, "NQ")  # a research-store file in the training root
    runner = far.runner()
    try:
        with pytest.raises(RemoteRefused) as refused:
            runner.submit(far.submission("e2e-canary-1", (step2_file,)), wait=True,
                          max_wait_s=30)
        assert refused.value.kind == "training-root"
        assert steps(runner, "e2e-canary-1") == ["prepared", "code_synced"]
        planted.unlink()
        canary = bar_file(training, STEP2, "NQ", days=trading_days(date(2025, 4, 1), 3))
        assert canary.name == store_name(STEP2, "NQ")  # a clean name, research-window rows
        with pytest.raises(RemoteRefused) as refused:
            runner.submit(far.submission("e2e-canary-2", (step2_file,)), wait=True,
                          max_wait_s=30)
        assert refused.value.kind == "outside-window"
    finally:
        for path in (training / "NQ").glob("*"):
            path.unlink()
        (training / "NQ").rmdir()
