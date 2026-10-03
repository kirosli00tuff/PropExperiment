"""The constants fingerprint of ML route v2's resumable state (Stage E.11 code review C-01, lead
ruling 2026-10-03).

The scoring and sizing read ml_route_v2/constants.py at call time (decide.gate_reading reads
COST_GATE_READING when it runs; sizing, the kill switches and the payout simulator read their
fractions, levels and SEED). Every piece of resumable state (the CPCV unit store, Gate 0 family
B's state, each pipeline stage file, each engine-path and payout checkpoint) therefore carries
``constants_fingerprint()`` and is refused when it differs, so a state directory written under
one set of constants is never read back under another.

The fingerprint is the sha256 of the bytes of ml_route_v2/constants.py followed by the repr of
every public (upper-case) name of the imported module, read when the function is called. The
file bytes catch any edit of the file; the live values also catch a constant changed at run time
(a test's monkeypatch, or a module that rebinds one), which the file bytes cannot see.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


def _public_names(module: object) -> list[str]:
    return sorted(n for n in vars(module) if not n.startswith("_") and n.isupper())


def constants_fingerprint() -> str:
    """sha256 of constants.py's bytes and of its public values as they are now (docstring)."""
    from ml_route_v2 import constants as v2c

    h = hashlib.sha256()
    h.update(Path(v2c.__file__).read_bytes())
    for name in _public_names(v2c):
        h.update(f"\n{name}={getattr(v2c, name)!r}".encode())
    return h.hexdigest()


def value_digest(value: Any) -> str:
    """A content digest of a functools.partial's bound argument (cpcv._callable_name, C-01):
    frames and arrays by their data (their repr is truncated), anything else by repr."""
    if isinstance(value, (pd.DataFrame, pd.Series)):
        h = hashlib.sha256()
        cols = tuple(value.columns) if isinstance(value, pd.DataFrame) else (value.name,)
        h.update(repr(cols).encode())
        h.update(pd.util.hash_pandas_object(value, index=True).to_numpy().tobytes())
        return f"frame:{h.hexdigest()}"
    if isinstance(value, np.ndarray):
        h = hashlib.sha256(repr((value.dtype.str, value.shape)).encode())
        h.update(np.ascontiguousarray(value).tobytes())
        return f"array:{h.hexdigest()}"
    return repr(value)


__all__ = ["constants_fingerprint", "value_digest"]
