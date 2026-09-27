"""Cross-platform process limits for Stage E jobs (Stage E.2b, user decision V10).

Every heavy Stage E job (screening, confirmation, ML training) calls ``lower_priority()`` first
and sets its thread count through ``apply_thread_limits(n)`` before numpy, lightgbm or torch is
imported. On Linux this is nice 10 (CLAUDE.md, compute limits); on native Windows it is the
BELOW_NORMAL priority class, the same intent on the Windows PC.
"""
from __future__ import annotations

import os
import sys

NICE_LEVEL = 10
WINDOWS_BELOW_NORMAL_PRIORITY_CLASS = 0x00004000
THREAD_ENV_VARS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                   "NUMEXPR_NUM_THREADS")


def is_windows() -> bool:
    return sys.platform == "win32"


def lower_priority() -> None:
    """Run the current process below normal priority (nice 10, or BELOW_NORMAL on Windows)."""
    if is_windows():
        import ctypes

        kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined]
        if not kernel32.SetPriorityClass(kernel32.GetCurrentProcess(),
                                         WINDOWS_BELOW_NORMAL_PRIORITY_CLASS):
            raise OSError("SetPriorityClass(BELOW_NORMAL_PRIORITY_CLASS) failed")
        return
    current = os.nice(0)
    if current < NICE_LEVEL:
        os.nice(NICE_LEVEL - current)


def priority_label() -> str:
    """This process's scheduling priority as recorded in job results: 'nice N' on POSIX, the
    Windows priority class (0x4000 is BELOW_NORMAL_PRIORITY_CLASS) on Windows."""
    if is_windows():
        import ctypes

        kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined]
        return f"priority class 0x{kernel32.GetPriorityClass(kernel32.GetCurrentProcess()):08x}"
    return f"nice {os.nice(0)}"


def total_memory_bytes() -> int | None:
    """Physical memory in bytes (GlobalMemoryStatusEx on Windows, sysconf elsewhere); None when
    the platform does not say."""
    if is_windows():
        import ctypes

        class MemoryStatus(ctypes.Structure):
            _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                        ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                        ("ullTotalPageFile", ctypes.c_ulonglong),
                        ("ullAvailPageFile", ctypes.c_ulonglong),
                        ("ullTotalVirtual", ctypes.c_ulonglong),
                        ("ullAvailVirtual", ctypes.c_ulonglong),
                        ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]

        status = MemoryStatus()
        status.dwLength = ctypes.sizeof(MemoryStatus)
        kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined]
        return int(status.ullTotalPhys) if kernel32.GlobalMemoryStatusEx(ctypes.byref(status)) \
            else None
    names = getattr(os, "sysconf_names", {})
    if "SC_PAGE_SIZE" in names and "SC_PHYS_PAGES" in names:
        return int(os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES"))
    return None


def thread_env(n_threads: int) -> dict[str, str]:
    """The environment variables that cap BLAS and OpenMP threads at n_threads."""
    if n_threads < 1:
        raise ValueError(f"n_threads must be at least 1, got {n_threads}")
    return {name: str(n_threads) for name in THREAD_ENV_VARS}


def apply_thread_limits(n_threads: int) -> None:
    """Cap this process's BLAS and OpenMP threads. Call before numpy or torch is imported."""
    os.environ.update(thread_env(n_threads))
