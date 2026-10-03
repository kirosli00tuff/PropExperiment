"""Small I/O helpers of the phase-1 steps: canonical JSON bytes (NaN -> null, +-inf -> "inf" /
"-inf", numpy scalars to Python), atomic writes, sha256 of bytes, the local time stamp."""

from __future__ import annotations

import hashlib
import json
import math
import os
from collections.abc import Mapping
from datetime import date, datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import numpy as np

LOCAL_TZ = ZoneInfo("America/Vancouver")  # times in PDT/PST (CLAUDE.md, user)


def clean(value: Any) -> Any:  # noqa: ANN401 - any JSON-able tree
    """A JSON-safe copy: NaN -> None, +-inf -> "inf"/"-inf", numpy and dates to Python."""
    if isinstance(value, Mapping):
        return {str(k): clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        items = sorted(value) if isinstance(value, (set, frozenset)) else value
        return [clean(v) for v in items]
    if isinstance(value, (np.bool_, bool)):
        return bool(value)
    if isinstance(value, (np.integer, int)):
        return int(value)
    if isinstance(value, (np.floating, float)):
        f = float(value)
        if math.isnan(f):
            return None
        if math.isinf(f):
            return "inf" if f > 0 else "-inf"
        return f
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, np.ndarray):
        return [clean(v) for v in value.tolist()]
    return value


def json_bytes(doc: Any) -> bytes:  # noqa: ANN401
    return (json.dumps(clean(doc), indent=2, sort_keys=True, allow_nan=False) + "\n").encode()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_atomic(path: Path, data: bytes) -> str:
    """Write ``data`` to ``path`` through a temporary file and a rename; returns its sha256."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    with tmp.open("wb") as fh:
        fh.write(data)
        fh.flush()
        os.fsync(fh.fileno())
    tmp.replace(path)
    return sha256_bytes(data)


def write_json(path: Path, doc: Any) -> str:  # noqa: ANN401
    return write_atomic(path, json_bytes(doc))


def now_local() -> str:
    return datetime.now(LOCAL_TZ).isoformat(timespec="seconds")


__all__ = ["LOCAL_TZ", "clean", "json_bytes", "now_local", "sha256_bytes", "write_atomic",
           "write_json"]
