"""Starting a job worker that outlives the SSH session that started it (Stage E.2b, V10).

Three methods, chosen per machine in the host config and checked against the OS the agent runs on:
- ``posix_session``: a new session (``start_new_session``), so the SSH session's process group
  and hang-up never reach the worker. Tested on this machine over a localhost SSH server.
- ``windows_breakaway``: Windows OpenSSH runs each session's processes in a job object that is
  closed when the session ends. CREATE_BREAKAWAY_FROM_JOB takes the worker out of it, which works
  only when the job object allows breakaway; if it does not, CreateProcess fails and the start is
  refused by name (never retried another way). DETACHED_PROCESS and CREATE_NEW_PROCESS_GROUP keep
  it off the session's console and its Ctrl-C group; BELOW_NORMAL_PRIORITY_CLASS is the Windows
  form of nice 10. UNVERIFIED until E.2c runs it on the PC (docs/WINDOWS_SETUP.md, checklist).
- ``windows_schtasks``: the worker runs as a one-off scheduled task of the same user (the Task
  Scheduler service starts it, outside the session's job object). A wrapper .cmd file in the job
  directory holds the command, since schtasks limits /TR to 261 characters. UNVERIFIED likewise.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

from compute.platform import WINDOWS_BELOW_NORMAL_PRIORITY_CLASS, is_windows

POSIX_SESSION = "posix_session"
WINDOWS_BREAKAWAY = "windows_breakaway"
WINDOWS_SCHTASKS = "windows_schtasks"
METHODS = (POSIX_SESSION, WINDOWS_BREAKAWAY, WINDOWS_SCHTASKS)

# Win32 process creation flags (winbase.h).
DETACHED_PROCESS = 0x00000008
CREATE_NEW_PROCESS_GROUP = 0x00000200
CREATE_NO_WINDOW = 0x08000000
CREATE_BREAKAWAY_FROM_JOB = 0x01000000
SCHTASKS_TIMEOUT_S = 60
TASK_PREFIX = "PropExperiment-"


class DetachRefused(RuntimeError):
    """The detachment method does not fit this machine, or starting the worker failed."""


def check_method(method: str, windows: bool | None = None) -> None:
    windows = is_windows() if windows is None else windows
    if method not in METHODS:
        raise DetachRefused(f"detach method {method!r} is not one of {METHODS}")
    if windows != method.startswith("windows_"):
        where = "Windows" if windows else "a POSIX system"
        raise DetachRefused(f"detach method {method} does not run on {where}")


def breakaway_flags() -> int:
    return (CREATE_BREAKAWAY_FROM_JOB | DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
            | WINDOWS_BELOW_NORMAL_PRIORITY_CLASS)


def job_child_flags() -> int:
    """Creation flags for the job process the worker starts on Windows (below normal, no
    console window); 0 elsewhere (nice 10 is inherited)."""
    return (WINDOWS_BELOW_NORMAL_PRIORITY_CLASS | CREATE_NO_WINDOW) if is_windows() else 0


def popen_kwargs(method: str) -> dict[str, object]:
    """The subprocess.Popen keywords that detach the worker, for the two direct methods."""
    if method == POSIX_SESSION:
        return {"start_new_session": True, "close_fds": True}
    if method == WINDOWS_BREAKAWAY:
        return {"creationflags": breakaway_flags(), "close_fds": True}
    raise DetachRefused(f"{method} does not start the worker through Popen")


def schtasks_wrapper(argv: list[str], cwd: Path, log: Path) -> str:
    """The .cmd wrapper a scheduled task runs: change to the checkout, run the worker, append its
    output to the log. Every piece is quoted for cmd.exe; a double quote or percent sign in any
    of them is refused (cmd.exe would reinterpret it)."""
    pieces = [str(cwd), str(log), *argv]
    for piece in pieces:
        if '"' in piece or "%" in piece or "\r" in piece or "\n" in piece:
            raise DetachRefused(f"cannot quote {piece!r} for cmd.exe")
    command = " ".join(f'"{a}"' for a in argv)
    return f'@echo off\r\ncd /d "{cwd}"\r\n{command} >> "{log}" 2>&1\r\n'


def schtasks_argv(task: str, wrapper: Path) -> tuple[list[str], list[str]]:
    """(create, run) argument lists for a one-off task of the current user running ``wrapper``.
    The start time is irrelevant (/Run starts it now); /F replaces a task of the same name."""
    create = ["schtasks", "/Create", "/F", "/TN", task, "/SC", "ONCE", "/ST", "23:59",
              "/RL", "LIMITED", "/TR", f'"{wrapper}"']
    return create, ["schtasks", "/Run", "/TN", task]


def spawn(method: str, argv: list[str], *, cwd: Path, log: Path, env: dict[str, str],
          task_name: str) -> int | None:
    """Start the worker detached; returns its pid (None for a scheduled task, whose pid is
    recorded by the worker itself). Refuses a method that does not fit this OS."""
    check_method(method)
    log.parent.mkdir(parents=True, exist_ok=True)
    if method == WINDOWS_SCHTASKS:
        wrapper = log.parent / "worker.cmd"
        wrapper.write_text(schtasks_wrapper(argv, cwd, log), encoding="utf-8", newline="")
        for step in schtasks_argv(TASK_PREFIX + task_name, wrapper):
            done = subprocess.run(step, capture_output=True, timeout=SCHTASKS_TIMEOUT_S,
                                  check=False)
            if done.returncode != 0:
                raise DetachRefused(f"{step[1]} failed ({done.returncode}): "
                                    f"{done.stderr.decode('utf-8', errors='replace').strip()}")
        return None
    with log.open("ab") as handle:
        try:
            proc = subprocess.Popen(argv, cwd=str(cwd), env=env, stdin=subprocess.DEVNULL,
                                    stdout=handle, stderr=subprocess.STDOUT,
                                    **popen_kwargs(method))  # type: ignore[arg-type]
        except OSError as exc:
            raise DetachRefused(f"{method}: starting the worker failed ({exc}); on Windows "
                                "this means the session's job object forbids breakaway: "
                                "use windows_schtasks (docs/WINDOWS_SETUP.md)") from exc
    return proc.pid
