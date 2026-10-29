"""Stage E.32b F3: read guard for the one-minute bar files (spec section 2.1).

Only data/vendor/databento/GLBX.MDP3/ohlcv-1m/<ROOT>_v_0/range=YYYY-MM-01_YYYY-MM-01.dbn.zst files whose range is
one of the 12 calendar months 2022-11 .. 2023-10 may be opened, and only for the 47 Layer 1 codes. The check runs on
the RESOLVED path (os.path.realpath) and on the path as given; any path containing mbo, mbp, tbbo, holdout, sealed
or enc (case-insensitive) is refused before anything is opened. Every open and every refusal is logged.
"""
from __future__ import annotations

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Callable
from zoneinfo import ZoneInfo

CODES_47: tuple[str, ...] = (
    "MCL", "QM", "CL", "MNG", "QG", "NG", "MGC", "GC", "SIL", "SI", "MHG", "HG", "M6E", "6E", "M6A", "6A",
    "MET", "ETH", "MBT", "BTC", "M2K", "RTY", "MYM", "YM", "MNQ", "NQ", "2YY", "5YY", "10Y", "30Y",
    "ZT", "ZF", "ZN", "ZB", "MZC", "MZS", "MZW", "MZL", "MZM", "XC", "XK", "XW", "ZC", "ZS", "ZW", "ZL", "ZM",
)
ALLOWED_MONTHS: tuple[tuple[str, str], ...] = (
    ("2022-11-01", "2022-12-01"), ("2022-12-01", "2023-01-01"), ("2023-01-01", "2023-02-01"),
    ("2023-02-01", "2023-03-01"), ("2023-03-01", "2023-04-01"), ("2023-04-01", "2023-05-01"),
    ("2023-05-01", "2023-06-01"), ("2023-06-01", "2023-07-01"), ("2023-07-01", "2023-08-01"),
    ("2023-08-01", "2023-09-01"), ("2023-09-01", "2023-10-01"), ("2023-10-01", "2023-11-01"),
)
FORBIDDEN_TOKENS: tuple[str, ...] = ("mbo", "mbp", "tbbo", "holdout", "sealed", "enc")
REL_BASE = "data/vendor/databento/GLBX.MDP3/ohlcv-1m"
NAME_RE = re.compile(r"^range=(\d{4}-\d{2}-01)_(\d{4}-\d{2}-01)\.dbn\.zst$")
DIR_RE = re.compile(r"^([A-Z0-9]+)_v_0$")


class GuardError(RuntimeError):
    """Raised for every path the allow-list refuses; nothing is opened."""


def _now_pdt() -> str:
    return datetime.now(ZoneInfo("America/Vancouver")).strftime("%Y-%m-%d %H:%M:%S %Z")


class BarGuard:
    """Allow-list guard. ``repo`` is the repository root (tests pass a synthetic tree)."""

    def __init__(self, repo: Path, log_path: Path) -> None:
        self.base_given = Path(repo) / REL_BASE
        self.base_real = os.path.realpath(self.base_given)
        self.log_path = Path(log_path)
        self.opened: list[str] = []

    def _log(self, line: str) -> None:
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.log_path, "a", encoding="utf-8") as fh:
            fh.write(f"{_now_pdt()} | {line}\n")

    def _refuse(self, given: str, reason: str) -> GuardError:
        self._log(f"REFUSED | {given} | {reason}")
        return GuardError(f"F3 guard refused {given}: {reason}")

    def allowed_path(self, root: str, month: tuple[str, str]) -> Path:
        """The (unresolved) path of one allow-listed file; used by the driver to build its file list."""
        return self.base_given / f"{root}_v_0" / f"range={month[0]}_{month[1]}.dbn.zst"

    def check(self, path: str | os.PathLike) -> str:
        """Return the resolved path if it is allow-listed; raise GuardError otherwise. Never opens the file."""
        given = os.fspath(path)
        resolved = os.path.realpath(given)
        for text, label in ((given, "given"), (resolved, "resolved")):
            low = text.lower()
            for tok in FORBIDDEN_TOKENS:
                if tok in low:
                    raise self._refuse(given, f"{label} path contains forbidden token '{tok}'")
        prefix = self.base_real + os.sep
        if not resolved.startswith(prefix):
            raise self._refuse(given, f"resolved path {resolved} is outside {self.base_real}")
        parts = resolved[len(prefix):].split(os.sep)
        if len(parts) != 2:
            raise self._refuse(given, f"resolved path {resolved} is not <ROOT>_v_0/<file>")
        mdir, mname = DIR_RE.match(parts[0]), NAME_RE.match(parts[1])
        if mdir is None or mname is None:
            raise self._refuse(given, f"resolved path {resolved} does not match <ROOT>_v_0/range=...dbn.zst")
        if mdir.group(1) not in CODES_47:
            raise self._refuse(given, f"root {mdir.group(1)} is not one of the 47 codes")
        if (mname.group(1), mname.group(2)) not in ALLOWED_MONTHS:
            raise self._refuse(given, f"range {mname.group(1)}_{mname.group(2)} is not one of the 12 window months")
        if not os.path.isfile(resolved):
            raise self._refuse(given, f"resolved path {resolved} is not a regular file")
        return resolved

    def open(self, path: str | os.PathLike, reader: Callable[[str], object]) -> object:
        """Check, log, then call ``reader`` on the RESOLVED path (the path that was checked)."""
        resolved = self.check(path)
        self._log(f"OPEN | {resolved} | {os.path.getsize(resolved)} bytes")
        self.opened.append(resolved)
        return reader(resolved)
