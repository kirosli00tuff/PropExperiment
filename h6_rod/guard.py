"""The H6 read guard (docs/prompts/STAGE_E.20.md F3; prereg section 9). Imported by every h6_rod
module through h6_rod/__init__.py; the CLI (h6_rod.run.main) installs the audit hook first.

(a) ``check_store_path``: the loader's check before it opens anything. The only store H6 may open
    is the NQ step 2 file; a path under data/processed_hist/, data/sealed/, a holdout store (the
    sealed roots, the holdout blob and the two parquets data.holdout guards, taken from
    data.holdout and data.step2_seal, never retyped) or any other store raises ``GuardRefusal``.
(b) ``install_audit_hook``: defense in depth. A ``sys.addaudithook`` hook refuses every
    Python-level ``open`` (builtins.open, io.open_code, os.open) of a forbidden prefix: the
    prefixes of (a), every other store root (data/processed, data/processed_step2 except the NQ
    file, data/vendor). pyarrow opens files natively and is not seen by the hook, which is why (a)
    is the primary check; the frozen loader hashes a store with Python ``open`` before pyarrow
    reads it, so a forbidden store is refused there too. The hook cannot be removed once installed,
    so it is installed only by the CLI process (tests run it in a subprocess).
(c) ``check_bars``: after load, any bar whose ts_event is at or after 2024-03-01 00:00 UTC, or
    whose trade_date is on or after 2024-03-01, raises.
"""

from __future__ import annotations

import os
import sys
from collections.abc import Iterable
from datetime import UTC, datetime, time
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from h6_rod import constants as K


class GuardRefusal(PermissionError):
    """An H6 process tried to read something F3 forbids."""


def _repo_root() -> Path:
    from data.config import REPO_ROOT

    return Path(REPO_ROOT)


def nq_store_path() -> Path:
    return _repo_root() / K.NQ_STORE_REL


def _real(path: str | os.PathLike[str]) -> str:
    return os.path.realpath(os.path.abspath(os.fspath(path)))


def holdout_paths() -> tuple[Path, ...]:
    """Every holdout store path data.holdout and data.step2_seal name (sealed roots, the holdout
    blob, the research parquet holdout 1 guards and the confirmation parquet holdout 2 guards)."""
    from data import holdout as ho
    from data import step2_seal

    out: list[Path] = [Path(step2_seal.SEALED_BASE)]
    for paths in (ho.DEFAULT_PATHS, ho.HOLDOUT2_PATHS):
        out += [Path(paths.sealed_root), Path(paths.holdout_blob), Path(paths.research_parquet)]
    return tuple(out)


def forbidden_prefixes() -> dict[str, tuple[str, ...]]:
    """{reason: real path prefixes} of (a) and (b)."""
    from data.config import HIST_ROOT, PROCESSED_ROOT, STEP2_ROOT, VENDOR_ROOT

    return {
        "data/processed_hist (the 2010-2019 stores)": (_real(HIST_ROOT),),
        "a sealed or holdout store": tuple(_real(p) for p in holdout_paths()),
        "another store (not the NQ step 2 file)": (_real(PROCESSED_ROOT), _real(STEP2_ROOT),
                                                   _real(VENDOR_ROOT)),
    }


def _under(real: str, prefix: str) -> bool:
    return real == prefix or real.startswith(prefix.rstrip(os.sep) + os.sep)


def refusal_reason(path: str | os.PathLike[str], *, allowed: str | os.PathLike[str] | None = None,
                   prefixes: dict[str, tuple[str, ...]] | None = None) -> str | None:
    """Why opening ``path`` is forbidden, or None when it is allowed. ``allowed``: the one store
    file that may be opened (default the NQ store)."""
    real = _real(path)
    allow = _real(allowed if allowed is not None else nq_store_path())
    if real == allow:
        return None
    for reason, roots in (prefixes or forbidden_prefixes()).items():
        if any(_under(real, root) for root in roots):
            return reason
    return None


def check_store_path(path: str | os.PathLike[str], *,
                     allowed: str | os.PathLike[str] | None = None) -> Path:
    """(a): the store path the loader may open, or GuardRefusal. Anything other than ``allowed``
    (default the NQ step 2 file) is refused, with the forbidden class named when it has one."""
    allow = Path(allowed) if allowed is not None else nq_store_path()
    if _real(path) == _real(allow):
        return Path(path)
    why = refusal_reason(path, allowed=allow) or "not the NQ step 2 store"
    raise GuardRefusal(f"H6 guard: refused to open {path}: {why} (F3: H6 reads only {allow})")


# ------------------------------------------------------------------ (b) the audit hook ----
_STATE: dict[str, Any] = {"installed": False, "prefixes": None, "allowed": None, "busy": False}
_OPEN_EVENTS = frozenset({"open", "os.open"})


def audit_decision(event: str, args: tuple, *, allowed: str, prefixes: dict[str, tuple[str, ...]]
                   ) -> str | None:
    """The hook's decision for one audit event: the refusal text, or None."""
    if event not in _OPEN_EVENTS or not args:
        return None
    target = args[0]
    if isinstance(target, int) or target is None:
        return None  # a file descriptor: already open
    if isinstance(target, bytes):
        target = os.fsdecode(target)
    try:
        why = refusal_reason(target, allowed=allowed, prefixes=prefixes)
    except (TypeError, ValueError):
        return None
    return None if why is None else f"H6 guard (audit hook): refused open of {target}: {why}"


def _hook(event: str, args: tuple) -> None:
    if _STATE["busy"] or event not in _OPEN_EVENTS:
        return
    _STATE["busy"] = True
    try:
        why = audit_decision(event, args, allowed=_STATE["allowed"], prefixes=_STATE["prefixes"])
    finally:
        _STATE["busy"] = False
    if why is not None:
        raise GuardRefusal(why)


def install_audit_hook() -> bool:
    """Install the hook once per process (irreversible); True when this call installed it."""
    if _STATE["installed"]:
        return False
    _STATE["prefixes"] = forbidden_prefixes()
    _STATE["allowed"] = _real(nq_store_path())
    sys.addaudithook(_hook)
    _STATE["installed"] = True
    return True


def hook_installed() -> bool:
    return bool(_STATE["installed"])


# ------------------------------------------------------------------ (c) the bars ----
FORBIDDEN_FROM_NS = int(datetime.combine(K.FORBIDDEN_FROM, time(0, 0), tzinfo=UTC).timestamp()
                        ) * 1_000_000_000


def check_trade_dates(days: Iterable[Any], where: str = "bars") -> None:
    """GuardRefusal when any trade date is on or after 2024-03-01."""
    late = sorted(str(d)[:10] for d in days if str(d)[:10] >= K.FORBIDDEN_FROM.isoformat())
    if late:
        raise GuardRefusal(f"H6 guard: {where}: {len(late)} rows dated on or after "
                           f"{K.FORBIDDEN_FROM} (first {late[0]})")


def check_bars(frame: pd.DataFrame, where: str = "bars") -> None:
    """(c): GuardRefusal when any bar's ts_event or trade_date is on or after 2024-03-01."""
    if len(frame) == 0:
        return
    ts = frame["ts_event"].to_numpy(np.int64)
    late_ts = ts >= FORBIDDEN_FROM_NS
    if bool(late_ts.any()):
        raise GuardRefusal(f"H6 guard: {where}: {int(late_ts.sum())} bars open at or after "
                           f"{K.FORBIDDEN_FROM} 00:00 UTC")
    check_trade_dates(pd.unique(frame["trade_date"].astype(str)), where)


__all__ = ["FORBIDDEN_FROM_NS", "GuardRefusal", "audit_decision", "check_bars",
           "check_store_path", "check_trade_dates", "forbidden_prefixes", "holdout_paths",
           "hook_installed", "install_audit_hook", "nq_store_path", "refusal_reason"]
