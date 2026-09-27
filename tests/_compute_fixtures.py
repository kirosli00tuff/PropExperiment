"""Shared fixtures for the compute backend's tests (Stage E.2b Task 5). Synthetic data only.

- ``write_bars``: a synthetic bar parquet in the store layout, with the stores' metadata.
- ``make_tiny_repo``: a small git repository holding the backend (compute/), the preflight and
  the modules they import, a fake tracked ledger, and a tiny harness manifest listing every
  harness *.py file, so the real preflight runs at both ends of a localhost job.
- ``LocalSSHServer``: a user-level SSH server on 127.0.0.1 (asyncssh) that runs each command
  through /bin/sh -c in its own process group, as OpenSSH's sshd does, and serves SFTP from a
  throwaway home directory, so the system ssh and sftp clients work against it.
"""
from __future__ import annotations

import asyncio
import contextlib
import json
import os
import shutil
import signal
import subprocess
import threading
from datetime import date, datetime, timedelta
from datetime import time as dtime
from pathlib import Path
from zoneinfo import ZoneInfo

import pyarrow as pa
import pyarrow.parquet as pq

from compute.datarules import RESEARCH, SEALED_MAGIC, STEP2, STORES

REPO = Path(__file__).resolve().parents[1]
FAKE_KEY = "db-TESTONLYnotarealkey0123456789"
CT = ZoneInfo("America/Chicago")
NS = 1_000_000_000
TINY_ENTRIES = ("compute.agent", "compute.remote", "compute.synthetic_job")
GIT_ENV = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t.invalid",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t.invalid",
           "GIT_AUTHOR_DATE": "2026-09-26T12:00:00+0000",
           "GIT_COMMITTER_DATE": "2026-09-26T12:00:00+0000"}


def ct_ns(day: date, hh: int, mm: int) -> int:
    """A CT wall-clock minute as UTC epoch nanoseconds."""
    return int(datetime.combine(day, dtime(hh, mm), tzinfo=CT).timestamp()) * NS


def store_name(store: str, product: str) -> str:
    if store == STEP2:
        return f"ohlcv-1m_{product}_v_0_2019-05-06_2024-02-29_step2.parquet"
    return f"ohlcv-1m_{product}_v_0_2025-04-01_2026-06-19_research.parquet"


def trading_days(first: date, n: int) -> list[date]:
    out, day = [], first
    while len(out) < n:
        if day.weekday() < 5:
            out.append(day)
        day += timedelta(days=1)
    return out


def default_days(store: str) -> list[date]:
    return trading_days(STORES[store][1] + timedelta(days=3), 5)


def write_bars(path: Path, days: list[date], *, store: str = STEP2,
               meta_range: list[str] | None = None, meta_store: str | None = "default",
               extra_meta: dict | None = None, with_trade_date: bool = True,
               rows: list[tuple[int, str]] | None = None) -> Path:
    """Two day-session bars (08:30 and 08:31 CT) per trade date, labelled with it, so the CME
    group calendar books each row to its label; ``rows`` gives (ts_event ns, label) directly.
    The stores' 'propexperiment' metadata is written with the labels' range."""
    rows = rows if rows is not None else [(ct_ns(d, 8, 30 + k), d.isoformat())
                                          for d in days for k in range(2)]
    columns = {"ts_event": pa.array([r[0] for r in rows], pa.int64()),
               "close": pa.array([100.0 + i for i in range(len(rows))], pa.float64())}
    if with_trade_date:
        columns["trade_date"] = pa.array([r[1] for r in rows], pa.string())
    labels = sorted(r[1] for r in rows)
    meta = {"trade_date_range": meta_range or [labels[0], labels[-1]], **(extra_meta or {})}
    if meta_store == "default":
        meta_store = "step2" if store == STEP2 else None
    if meta_store is not None:
        meta["store"] = meta_store
    table = pa.table(columns).replace_schema_metadata({b"propexperiment": json.dumps(meta)})
    path.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(table, path)
    return path


def bar_file(base: Path, store: str, product: str = "ES", days: list[date] | None = None,
             **kwargs: object) -> Path:
    return write_bars(base / product / store_name(store, product),
                      days if days is not None else default_days(store), store=store,
                      **kwargs)  # type: ignore[arg-type]


def sealed_blob(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(SEALED_MAGIC + b"\x00" * 64)
    return path


# ---------------------------------------------------------------- git repo ----
def git(repo: Path, *args: str) -> str:
    done = subprocess.run(["git", *args], cwd=repo, env={**os.environ, **GIT_ENV},
                          capture_output=True, text=True, check=True)
    return done.stdout.strip()


def tiny_manifest(repo: Path) -> str:
    """Write reports/stage_e2b_harness_freeze.json over every *.py file of the tiny repository
    plus pyproject.toml and uv.lock; returns its sha256."""
    import hashlib

    listed = sorted({*(p.relative_to(repo).as_posix() for p in repo.rglob("*.py")
                       if "__pycache__" not in p.parts), "pyproject.toml", "uv.lock"})
    files = {rel: {"sha256": hashlib.sha256((repo / rel).read_bytes()).hexdigest(),
                   "bytes": (repo / rel).stat().st_size} for rel in listed}
    raw = (json.dumps({"files": files}, indent=1, sort_keys=True) + "\n").encode("utf-8")
    (repo / "reports").mkdir(exist_ok=True)
    (repo / "reports" / "stage_e2b_harness_freeze.json").write_bytes(raw)
    return hashlib.sha256(raw).hexdigest()


def tiny_files() -> list[str]:
    """The backend's modules and everything they import (function-level imports included), the
    group calendars (imported by name at run time), pyproject.toml and uv.lock."""
    from tests.test_cross_platform_static import import_closure

    files = set(import_closure(TINY_ENTRIES))
    files |= {p.relative_to(REPO).as_posix() for p in (REPO / "data" / "calendars").glob("*.py")}
    return sorted(files | {"pyproject.toml", "uv.lock"})


def make_tiny_repo(root: Path, extra: dict[str, bytes] | None = None) -> tuple[Path, str, str]:
    """(repo, harness sha256, commit) of a fresh tiny harness repository."""
    repo = root / "tinyrepo"
    repo.mkdir(parents=True)
    for rel in tiny_files():
        (repo / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(REPO / rel, repo / rel)
    (repo / "ledger").mkdir()
    (repo / "ledger" / "databento_spend.jsonl").write_text('{"usd": 0.0}\n', encoding="utf-8")
    (repo / ".gitignore").write_text("__pycache__/\n.venv/\n", encoding="utf-8")
    for rel, data in (extra or {}).items():
        (repo / rel).parent.mkdir(parents=True, exist_ok=True)
        (repo / rel).write_bytes(data)
    harness = tiny_manifest(repo)
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "core.autocrlf", "false")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "tiny harness")
    return repo, harness, git(repo, "rev-parse", "HEAD")


# -------------------------------------------------------------- ssh server ----
def make_client_key(root: Path) -> Path:
    key = root / "id_ed25519"
    subprocess.run(["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-f", str(key)],
                   check=True, capture_output=True)
    return key


class LocalSSHServer:
    """asyncssh on 127.0.0.1:<free port>, commands via /bin/sh -c in the fake home directory."""

    def __init__(self, home: Path, authorized_keys: Path, env: dict[str, str]) -> None:
        import asyncssh

        self.home = home
        self.authorized_keys = authorized_keys
        self.env = env
        self.host_key = asyncssh.generate_private_key("ssh-ed25519")
        self.session_pgids: set[int] = set()
        self.commands: list[str] = []
        self.port = 0
        self.loop: asyncio.AbstractEventLoop | None = None

    def known_hosts_line(self) -> str:
        public = self.host_key.export_public_key().decode().strip()
        return f"[127.0.0.1]:{self.port} {public}\n"

    def start(self) -> LocalSSHServer:
        self.loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self.loop.run_forever, daemon=True)
        self._thread.start()
        self.port = asyncio.run_coroutine_threadsafe(self._start(), self.loop).result(30)
        return self

    async def _start(self) -> int:
        import asyncssh

        self._server = await asyncssh.create_server(
            asyncssh.SSHServer, "127.0.0.1", 0, server_host_keys=[self.host_key],
            authorized_client_keys=str(self.authorized_keys), process_factory=self._handle,
            sftp_factory=lambda chan: asyncssh.SFTPServer(chan, chroot=str(self.home).encode()),
            encoding=None, allow_scp=False)
        return self._server.sockets[0].getsockname()[1]

    async def _handle(self, process) -> None:  # noqa: ANN001 - asyncssh's process object
        command = process.command
        command = command.decode() if isinstance(command, bytes) else command
        self.commands.append(command)
        proc = await asyncio.create_subprocess_exec(
            "/bin/sh", "-c", command, cwd=str(self.home), env=self.env,
            stdin=asyncio.subprocess.DEVNULL, stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE, start_new_session=True)
        self.session_pgids.add(proc.pid)
        out, err = await proc.communicate()
        process.stdout.write(out)
        process.stderr.write(err)
        code = proc.returncode
        process.exit(code if code >= 0 else 128 - code)

    def stop(self) -> None:
        """Close the server and kill every session's process group, as sshd does when the
        connection ends: a detached worker must survive this."""
        for pgid in self.session_pgids:
            with contextlib.suppress(ProcessLookupError, PermissionError):  # already gone
                os.killpg(pgid, signal.SIGKILL)
        assert self.loop is not None

        async def _close() -> None:
            self._server.close()
            await self._server.wait_closed()

        asyncio.run_coroutine_threadsafe(_close(), self.loop).result(30)
        self.loop.call_soon_threadsafe(self.loop.stop)
        self._thread.join(30)


def server_env() -> dict[str, str]:
    env = {k: v for k, v in os.environ.items()
           if k not in ("VIRTUAL_ENV", "PYTHONPATH", "COVERAGE_PROCESS_START")}
    env["UV_PROJECT_ENVIRONMENT"] = str(REPO / ".venv")
    return env


def write_host_config(path: Path, server: LocalSSHServer, key: Path, known_hosts: Path,
                      **overrides: object) -> Path:
    known_hosts.write_text(server.known_hosts_line(), encoding="utf-8")
    config = {"schema": "propexperiment-compute-host/1", "name": "localhost-test",
              "host": "127.0.0.1", "user": os.environ.get("USER", "tester"), "port": server.port,
              "identity_file": str(key), "known_hosts_file": str(known_hosts),
              "agent_root": "propexp", "remote_os": "posix", "detach": "posix_session",
              **overrides}
    path.write_text(json.dumps(config, indent=1), encoding="utf-8")
    return path


__all__ = ["FAKE_KEY", "RESEARCH", "STEP2", "LocalSSHServer", "bar_file", "default_days",
           "make_client_key", "make_tiny_repo", "sealed_blob", "server_env", "store_name",
           "trading_days", "write_bars", "write_host_config"]
