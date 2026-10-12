"""Resumable, pinned stages in the state directory (pattern of ml_route_v2.pipeline._Stages).

Each stage writes state_dir/stages/<name>.pkl = {"pin": pin, "out": out} when it finishes and is
loaded, never recomputed, on a restart. The pin holds the frozen constants fingerprint
(fingerprint.constants_fingerprint), the search freeze manifest's sha256 and the world source
(real, or the synthetic seed and window): a stage file written under another pin is refused, so
state from a test, a probe or another freeze is never read back. Wall time and peak RSS (VmHWM,
pipeline._peak_rss_mb) are recorded per stage.
"""

from __future__ import annotations

import pickle
import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pattern_search import guard  # noqa: F401  (F3)

STAGE_KEYS = ("pin", "out")


class StateMismatch(RuntimeError):
    """A stage file was written under another pin."""


@dataclass(frozen=True)
class StageRecord:
    name: str
    status: str  # "computed" | "loaded"
    wall_s: float
    peak_rss_mb: float | None


def _save(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    with tmp.open("wb") as fh:
        pickle.dump(obj, fh, protocol=pickle.HIGHEST_PROTOCOL)
    tmp.replace(path)


def _load(path: Path) -> Any:
    with path.open("rb") as fh:
        return pickle.load(fh)  # noqa: S301 - the search's own state files


class Stages:
    def __init__(self, state_dir: Path, pin: Mapping[str, Any]) -> None:
        from ml_route_v2.fingerprint import constants_fingerprint

        self.dir = Path(state_dir)
        self.pin = {"constants": constants_fingerprint(), **dict(pin)}
        self.records: list[StageRecord] = []

    def path(self, name: str) -> Path:
        return self.dir / "stages" / f"{name}.pkl"

    def load(self, name: str) -> Any:
        saved = _load(self.path(name))
        if not isinstance(saved, dict) or tuple(saved) != STAGE_KEYS:
            raise StateMismatch(f"{self.path(name)} is not a pattern_search stage file")
        if saved["pin"] != self.pin:
            raise StateMismatch(f"{self.path(name)} was written under another pin (constants, "
                                "freeze sha256 or world); use a new state directory")
        return saved["out"]

    def has(self, name: str) -> bool:
        return self.path(name).exists()

    def run(self, name: str, fn: Callable[[], Any]) -> Any:
        from ml_route_v2.pipeline import _peak_rss_mb, _reset_peak

        start = time.perf_counter()
        measured = _reset_peak()
        if self.has(name):
            out, status = self.load(name), "loaded"
        else:
            out, status = fn(), "computed"
            _save(self.path(name), {"pin": self.pin, "out": out})
        self.records.append(StageRecord(name, status, time.perf_counter() - start,
                                        _peak_rss_mb() if measured else None))
        return out


__all__ = ["StageRecord", "Stages", "StateMismatch"]
