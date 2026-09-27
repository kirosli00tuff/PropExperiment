"""The machine record every compute job carries (Stage E.2b, V10-3).

Host name, operating system, CPU, logical cores, memory, GPUs with driver and CUDA versions (from
nvidia-smi), Python and the versions of the packages that can change a result. Read without
importing torch or lightgbm (package metadata only), and without any Linux-only file: the CPU
name comes from the registry on Windows, lscpu on Linux and sysctl on macOS.
"""
from __future__ import annotations

import importlib.metadata as metadata
import os
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path

from compute.platform import is_windows, total_memory_bytes

PACKAGES = ("numpy", "pandas", "pyarrow", "lightgbm", "torch", "scikit-learn")
PROBE_TIMEOUT_S = 30
NVIDIA_QUERY = ("--query-gpu=name,driver_version,memory.total", "--format=csv,noheader,nounits")


def _run(argv: list[str]) -> tuple[int, str]:
    try:
        done = subprocess.run(argv, capture_output=True, timeout=PROBE_TIMEOUT_S, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return -1, f"{type(exc).__name__}: {exc}"
    return done.returncode, done.stdout.decode("utf-8", errors="replace")


def cpu_name() -> str:
    if is_windows():
        import winreg  # type: ignore[import-not-found]

        key = r"HARDWARE\DESCRIPTION\System\CentralProcessor\0"
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key) as handle:  # type: ignore[attr-defined]
            return str(winreg.QueryValueEx(handle, "ProcessorNameString")[0]).strip()  # type: ignore[attr-defined]
    if sys.platform == "darwin":
        code, out = _run(["sysctl", "-n", "machdep.cpu.brand_string"])
        return out.strip() if code == 0 else f"unknown ({out.strip()})"
    code, out = _run(["lscpu"])
    for line in out.splitlines():
        if line.startswith("Model name:"):
            return line.split(":", 1)[1].strip()
    return f"unknown (lscpu exit {code})"


def gpus() -> dict[str, object]:
    exe = shutil.which("nvidia-smi")
    if exe is None:
        return {"nvidia_smi": None, "gpus": [], "cuda_driver_version": None}
    code, out = _run([exe, *NVIDIA_QUERY])
    cards = []
    if code == 0:
        for line in out.splitlines():
            parts = [p.strip() for p in line.split(",")]
            if len(parts) == 3:
                cards.append({"name": parts[0], "driver_version": parts[1],
                              "memory_total_mib": parts[2]})
    _, banner = _run([exe])
    match = re.search(r"CUDA Version:\s*([0-9.]+)", banner)
    return {"nvidia_smi": exe, "gpus": cards, "query_exit": code,
            "cuda_driver_version": match.group(1) if match else None}


def package_versions(names: tuple[str, ...] = PACKAGES) -> dict[str, str | None]:
    out: dict[str, str | None] = {}
    for name in names:
        try:
            out[name] = metadata.version(name)
        except metadata.PackageNotFoundError:
            out[name] = None
    return out


def locked_versions(lock_path: Path, names: tuple[str, ...] = PACKAGES) -> dict[str, set[str]]:
    """The versions uv.lock pins for each of ``names`` (a package may appear more than once,
    once per platform marker)."""
    import tomllib

    with Path(lock_path).open("rb") as handle:
        lock = tomllib.load(handle)
    out: dict[str, set[str]] = {name: set() for name in names}
    for package in lock.get("package", []):
        if package.get("name") in out and "version" in package:
            out[package["name"]].add(str(package["version"]))
    return out


def environment_problems(lock_path: Path, names: tuple[str, ...] = PACKAGES) -> list[str]:
    """Every result-relevant package whose installed version is not the one uv.lock pins (a
    local build tag such as +cu130 is ignored). [] means the environment matches the lock."""
    installed = package_versions(names)
    problems = []
    for name, pinned in locked_versions(lock_path, names).items():
        if not pinned:
            continue
        have = installed.get(name)
        base = None if have is None else have.split("+", 1)[0]
        if base not in {p.split("+", 1)[0] for p in pinned}:
            problems.append(f"{name} {have} installed, uv.lock pins {sorted(pinned)}")
    return problems


def machine_record() -> dict[str, object]:
    return {
        "hostname": platform.node(),
        "os": platform.platform(),
        "sys_platform": sys.platform,
        "machine": platform.machine(),
        "cpu": cpu_name(),
        "logical_cpus": os.cpu_count(),
        "memory_bytes": total_memory_bytes(),
        "gpu": gpus(),
        "python": sys.version.split()[0],
        "python_executable": sys.executable,
        "packages": package_versions(),
    }
