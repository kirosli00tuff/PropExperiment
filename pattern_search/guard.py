"""The search's read guard (docs/prompts/STAGE_E.20.md F3; reports/stage_e20_plan.md section 3).
Imported by every pattern_search module through pattern_search/__init__.py; the CLI
(pattern_search.run.main) installs the audit hook first. Pattern of h6_rod/guard.py, copied.

(a) ``check_store_path``: the primary check, on every path handed to a loader
    (data.stage_e_bars.load_confirmation_leg through world.load_search_root, and any direct
    parquet read). The only stores the search may open are the 17 step 2 files
    data/processed_step2/<ROOT>/ohlcv-1m_<ROOT>_v_0_2019-05-06_2024-02-29_step2.parquet of the
    plan's price paths. Refused, with the class named: anything under data/processed_hist/ (the
    2010-2019 stores), data/sealed/ or a holdout store (paths from data.holdout and
    data.step2_seal, never retyped), data/processed/ (the research and MES stores), and any other
    store (another root's step 2 store, the vendor tree, data/raw).
(b) ``install_audit_hook``: defense in depth. A ``sys.addaudithook`` hook repeats (a)'s refusals
    for Python-level opens (builtins.open, io.open_code, os.open). pyarrow opens files natively and
    is not seen by it, which is why (a) is the primary check; the frozen loader hashes a store with
    Python ``open`` before pyarrow reads it. The hook cannot be removed, so only the CLI process
    installs it (tests run it in a subprocess).
(c) ``check_bars``: after load, any bar whose ts_event is at or after 2024-03-01 00:00 UTC (earlier
    than the frozen phase-1 guard's 00:00 CT, so stricter) or whose trade_date is on or after
    2024-03-01 raises.
(d) The E20-B1 exception (plan 3: only the B1 evaluation may open data/processed_hist/, after its
    registration and its O_EXCL run-once marker) is not built in Step 6: every processed_hist path
    is refused, whatever the registry or marker state (``backward_permitted`` is False).
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

from pattern_search import constants as K


class GuardRefusal(PermissionError):
    """A search process tried to read something F3 forbids."""


REASON_HIST = "data/processed_hist (the 2010-2019 stores; only E20-B1 may open them, not built)"
REASON_HOLDOUT = "data/sealed or a holdout store"
REASON_PROCESSED = "data/processed (the research and MES stores)"
REASON_OTHER = "a store that is not one of the 17 search stores"


def _real(path: str | os.PathLike[str]) -> str:
    return os.path.realpath(os.path.abspath(os.fspath(path)))


def step2_store_path(root: str, step2_root: str | os.PathLike[str] | None = None) -> Path:
    """The step 2 parquet of a price path (data.step2_store.step2_parquet_path)."""
    from data.config import STEP2_ROOT
    from data.step2_store import step2_parquet_path

    return Path(step2_parquet_path(root, Path(step2_root) if step2_root else STEP2_ROOT))


def search_store_paths(step2_root: str | os.PathLike[str] | None = None) -> dict[str, str]:
    """{real path: price path} of the 17 stores the search may open."""
    return {_real(step2_store_path(r, step2_root)): r for r in K.PATH_ROOTS}


def holdout_paths() -> tuple[Path, ...]:
    """Every holdout store path data.holdout and data.step2_seal name (sealed roots, the holdout
    blobs, the research parquet holdout 1 guards and the confirmation parquet holdout 2 guards)."""
    from data import holdout as ho
    from data import step2_seal

    out: list[Path] = [Path(step2_seal.SEALED_BASE)]
    for paths in (ho.DEFAULT_PATHS, ho.HOLDOUT2_PATHS):
        out += [Path(paths.sealed_root), Path(paths.holdout_blob), Path(paths.research_parquet)]
    return tuple(out)


def forbidden_prefixes() -> dict[str, tuple[str, ...]]:
    """{reason: real path prefixes}, in the order the classes are named (a path under two
    prefixes gets the first reason: a holdout parquet under data/processed is a holdout store)."""
    from data.config import DATA_ROOT, HIST_ROOT, PROCESSED_ROOT, STEP2_ROOT, VENDOR_ROOT

    return {
        REASON_HIST: (_real(HIST_ROOT),),
        REASON_HOLDOUT: tuple(_real(p) for p in holdout_paths()),
        REASON_PROCESSED: (_real(PROCESSED_ROOT),),
        REASON_OTHER: (_real(STEP2_ROOT), _real(VENDOR_ROOT), _real(Path(DATA_ROOT) / "raw")),
    }


def _under(real: str, prefix: str) -> bool:
    return real == prefix or real.startswith(prefix.rstrip(os.sep) + os.sep)


def refusal_reason(path: str | os.PathLike[str], *, allowed: Iterable[str] | None = None,
                   prefixes: dict[str, tuple[str, ...]] | None = None) -> str | None:
    """Why opening ``path`` is forbidden, or None when it is allowed. ``allowed``: real paths of
    the stores that may be opened (default the 17 search stores)."""
    real = _real(path)
    allow = set(allowed) if allowed is not None else set(search_store_paths())
    if real in allow:
        return None
    for reason, roots in (prefixes or forbidden_prefixes()).items():
        if any(_under(real, root) for root in roots):
            return reason
    return None


def backward_permitted() -> bool:
    """(d): the E20-B1 exception. Not built in Step 6, so never granted."""
    return False


def check_store_path(path: str | os.PathLike[str], *,
                     allowed: Iterable[str] | None = None) -> Path:
    """(a): ``path`` when it is one of the allowed stores (default the 17 search stores);
    GuardRefusal otherwise, naming the forbidden class when it has one."""
    allow = set(allowed) if allowed is not None else set(search_store_paths())
    if _real(path) in allow:
        return Path(path)
    why = refusal_reason(path, allowed=allow) or REASON_OTHER
    raise GuardRefusal(f"E.20 search guard: refused to open {path}: {why} (F3: the search reads "
                       "only the 17 step 2 stores)")


# ------------------------------------------------------------------ (b) the audit hook ----
_STATE: dict[str, Any] = {"installed": False, "prefixes": None, "allowed": None, "busy": False}
_OPEN_EVENTS = frozenset({"open", "os.open"})


def audit_decision(event: str, args: tuple, *, allowed: Iterable[str],
                   prefixes: dict[str, tuple[str, ...]]) -> str | None:
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
    if why is None:
        return None
    return f"E.20 search guard (audit hook): refused open of {target}: {why}"


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
    _STATE["allowed"] = frozenset(search_store_paths())
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
        raise GuardRefusal(f"E.20 search guard: {where}: {len(late)} rows dated on or after "
                           f"{K.FORBIDDEN_FROM} (first {late[0]})")


def check_bars(frame: pd.DataFrame, where: str = "bars") -> None:
    """(c): GuardRefusal when any bar's ts_event or trade_date is on or after 2024-03-01."""
    if len(frame) == 0:
        return
    ts = frame["ts_event"].to_numpy(np.int64)
    late_ts = ts >= FORBIDDEN_FROM_NS
    if bool(late_ts.any()):
        raise GuardRefusal(f"E.20 search guard: {where}: {int(late_ts.sum())} bars open at or "
                           f"after {K.FORBIDDEN_FROM} 00:00 UTC")
    check_trade_dates(pd.unique(frame["trade_date"].astype(str)), where)


def check_frames(frames: dict[str, pd.DataFrame] | Any, where: str = "world") -> None:
    """(c) on every root's bars of a world."""
    for root, frame in frames.items():
        check_bars(frame, f"{where} {root}")


__all__ = ["FORBIDDEN_FROM_NS", "REASON_HIST", "REASON_HOLDOUT", "REASON_OTHER",
           "REASON_PROCESSED", "GuardRefusal", "audit_decision", "backward_permitted",
           "check_bars", "check_frames", "check_store_path", "check_trade_dates",
           "forbidden_prefixes", "holdout_paths", "hook_installed", "install_audit_hook",
           "refusal_reason", "search_store_paths", "step2_store_path"]
