"""SSH and SFTP from the ThinkPad to the far machine, through the system OpenSSH client (V10).

The host config (a JSON file, no secret in it) names the machine, the private key file, a pinned
known_hosts file and the agent root on the far side, relative to the remote user's home. Every
call reads no ~/.ssh/config (-F none), pins the host key (StrictHostKeyChecking=yes), never
prompts (BatchMode=yes) and offers only the configured key (IdentitiesOnly=yes).

A remote command is an argument list. The far shell differs (cmd.exe on Windows OpenSSH, sh on a
POSIX host), so each argument is limited to characters both treat literally, wrapped in double
quotes only when it holds a space; anything else is refused, never escaped (``quote_remote``).
Files move with ``sftp -b`` batches; a failing batch line stops the batch and raises.
"""
from __future__ import annotations

import json
import re
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

from compute.detach import METHODS, WINDOWS_BREAKAWAY, check_method

HOST_SCHEMA = "propexperiment-compute-host/1"
REMOTE_OS = ("windows", "posix")
SAFE_ARG = re.compile(r"^[A-Za-z0-9_\-./:=@,+]+$")
SAFE_ARG_WINDOWS = re.compile(r"^[A-Za-z0-9_\-./:=@,+\\]+$")
SAFE_SPACED = re.compile(r"^[A-Za-z0-9_\-./:=@,+ ]+$")
SAFE_SPACED_WINDOWS = re.compile(r"^[A-Za-z0-9_\-./:=@,+\\ ]+$")
SAFE_SFTP_PATH = re.compile(r"^[A-Za-z0-9_\-./:=@,+~ \\]+$")
DEFAULT_LAUNCHER = ("uv", "run", "--directory", "{checkout}", "--no-sync", "python", "-X", "utf8")
SSH_TIMEOUT_S = 3600
CONNECT_TIMEOUT_S = 15


class TransportFailed(RuntimeError):
    """ssh or sftp failed (connection, authentication, or a failing batch line)."""


class RemoteArgRefused(ValueError):
    """An argument cannot be passed literally through both cmd.exe and sh."""


def quote_remote(arg: str, remote_os: str) -> str:
    windows = remote_os == "windows"
    if arg and (SAFE_ARG_WINDOWS if windows else SAFE_ARG).match(arg):
        return arg
    if arg and (SAFE_SPACED_WINDOWS if windows else SAFE_SPACED).match(arg) \
            and not arg.endswith("\\"):
        return f'"{arg}"'
    raise RemoteArgRefused(f"argument {arg!r} cannot pass literally through the remote shell")


def remote_command(argv: list[str], remote_os: str) -> str:
    return " ".join(quote_remote(a, remote_os) for a in argv)


@dataclass(frozen=True)
class HostConfig:
    name: str
    host: str
    user: str
    port: int
    identity_file: Path
    known_hosts_file: Path
    agent_root: str  # relative to the remote user's home, POSIX separators
    remote_os: str
    detach: str
    launcher: tuple[str, ...] = DEFAULT_LAUNCHER

    @property
    def checkout(self) -> str:
        return f"{self.agent_root}/checkout"

    def validate(self) -> HostConfig:
        if self.remote_os not in REMOTE_OS:
            raise ValueError(f"remote_os {self.remote_os!r} is not one of {REMOTE_OS}")
        if self.detach not in METHODS:
            raise ValueError(f"detach {self.detach!r} is not one of {METHODS}")
        check_method(self.detach, windows=self.remote_os == "windows")
        if not re.fullmatch(r"[A-Za-z0-9_\-]+(/[A-Za-z0-9_\-]+)*", self.agent_root):
            raise ValueError("agent_root is a relative path of [A-Za-z0-9_-] names joined by '/'")
        if not re.fullmatch(r"[A-Za-z0-9_.\-]+", self.host) or \
                not re.fullmatch(r"[A-Za-z0-9_.\-]+", self.user):
            raise ValueError("host and user are plain names")
        for path in (self.identity_file, self.known_hosts_file):
            if " " in str(path):
                raise ValueError(f"{path}: ssh option paths may not contain spaces")
        if "{checkout}" not in self.launcher:
            raise ValueError("the launcher must place {checkout} (uv run --directory)")
        return self

    @classmethod
    def load(cls, path: Path) -> HostConfig:
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        if raw.get("schema") != HOST_SCHEMA:
            raise ValueError(f"{path}: schema is not {HOST_SCHEMA}")
        return cls(
            name=raw["name"], host=raw["host"], user=raw["user"], port=int(raw.get("port", 22)),
            identity_file=Path(raw["identity_file"]).expanduser(),
            known_hosts_file=Path(raw["known_hosts_file"]).expanduser(),
            agent_root=raw.get("agent_root", "propexp"), remote_os=raw["remote_os"],
            detach=raw.get("detach", WINDOWS_BREAKAWAY),
            launcher=tuple(raw.get("launcher", DEFAULT_LAUNCHER)),
        ).validate()


@dataclass(frozen=True)
class RemoteResult:
    returncode: int
    stdout: str
    stderr: str

    def last_json(self) -> dict | None:
        """The last stdout line that parses as a JSON object (the agent's answer)."""
        for line in reversed(self.stdout.strip().splitlines()):
            line = line.strip()
            if line.startswith("{"):
                try:
                    value = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(value, dict):
                    return value
        return None


class SSHTransport:
    def __init__(self, host: HostConfig) -> None:
        self.host = host.validate()

    def _options(self) -> list[str]:
        h = self.host
        return ["-F", "none", "-i", str(h.identity_file), "-o", "IdentitiesOnly=yes",
                "-o", f"UserKnownHostsFile={h.known_hosts_file}",
                "-o", "StrictHostKeyChecking=yes", "-o", "BatchMode=yes",
                "-o", f"ConnectTimeout={CONNECT_TIMEOUT_S}", "-o", "ServerAliveInterval=15",
                "-o", "LogLevel=ERROR"]

    def run(self, argv: list[str], *, timeout: float = SSH_TIMEOUT_S) -> RemoteResult:
        """Run ``argv`` on the far machine; a connection failure (ssh's own 255) raises."""
        h = self.host
        command = remote_command(argv, h.remote_os)
        full = ["ssh", "-p", str(h.port), *self._options(), f"{h.user}@{h.host}", command]
        try:
            done = subprocess.run(full, capture_output=True, timeout=timeout, check=False)
        except subprocess.TimeoutExpired as exc:
            raise TransportFailed(f"ssh {argv[:3]} timed out after {timeout} s") from exc
        result = RemoteResult(done.returncode, done.stdout.decode("utf-8", errors="replace"),
                              done.stderr.decode("utf-8", errors="replace"))
        if done.returncode == 255:
            raise TransportFailed(f"ssh to {h.name} failed: {result.stderr.strip()[:400]}")
        return result

    def agent(self, subcommand: str, *args: str, timeout: float = SSH_TIMEOUT_S) -> RemoteResult:
        """Run ``python -m compute.agent <subcommand> ...`` in the far checkout."""
        launcher = [a.replace("{checkout}", self.host.checkout) for a in self.host.launcher]
        return self.run([*launcher, "-m", "compute.agent", subcommand, *args], timeout=timeout)

    def sftp(self, lines: list[str], *, timeout: float | None = None) -> None:
        """Run an sftp batch; a line starting with '-' may fail, any other failure raises."""
        h = self.host
        with tempfile.TemporaryDirectory() as tmp:
            batch = Path(tmp) / "batch.txt"
            batch.write_text("\n".join(lines) + "\n", encoding="utf-8")
            full = ["sftp", "-b", str(batch), "-P", str(h.port), *self._options(),
                    f"{h.user}@{h.host}"]
            try:
                done = subprocess.run(full, capture_output=True, timeout=timeout, check=False)
            except subprocess.TimeoutExpired as exc:
                raise TransportFailed(f"sftp batch timed out after {timeout} s") from exc
        if done.returncode != 0:
            raise TransportFailed(f"sftp batch to {h.name} failed ({done.returncode}): "
                                  f"{done.stderr.decode('utf-8', errors='replace').strip()[:600]}")


def sftp_path(path: str | Path) -> str:
    text = str(path)
    if not SAFE_SFTP_PATH.match(text):
        raise RemoteArgRefused(f"path {text!r} has characters sftp batches cannot carry")
    return f'"{text}"'


def mkdirs_lines(relpath: str) -> list[str]:
    """'-mkdir' for every prefix of a POSIX relative directory path (existing ones may fail)."""
    parts = relpath.strip("/").split("/")
    return [f"-mkdir {sftp_path('/'.join(parts[:i]))}" for i in range(1, len(parts) + 1)]


def put_lines(local: Path, remote: str, staging: str) -> list[str]:
    """Upload ``local`` to ``staging``, then move it over ``remote`` (a failed upload never
    leaves a partial file at the final path)."""
    return [f"put {sftp_path(local)} {sftp_path(staging)}", f"-rm {sftp_path(remote)}",
            f"rename {sftp_path(staging)} {sftp_path(remote)}"]
