"""The 45 configurations of ML route v2 and the configuration ledger (V2.6, V2.7, V2.9).

Grid (V2.6, V2.7): five models (ridge lambda in RIDGE_LAMBDAS, LightGBM max_depth in LGBM_DEPTHS)
x three cost-gate multiples k (COST_GATE_KS) x three horizons (HORIZONS) = 45 configurations.

Fixed order of CONFIGS: models outermost in the order ridge 0.01, ridge 0.1, ridge 1.0, LightGBM
depth 2, LightGBM depth 3; then k in COST_GATE_KS order; then horizon in HORIZONS order. So
CONFIGS[0] is ridge_l0.01_k1.5_h60 and CONFIGS[44] is lgbm_d3_k3_hF.

config_id: "<model_id>_k<k:g>_<horizon>", model_id "ridge_l<lambda:g>" or "lgbm_d<depth>".

tie_break_key (V2.9): a smaller key wins a tie. Ridge before LightGBM, then the larger lambda, then
the smaller depth, then the larger k, then the shorter horizon.

ConfigLedger (V2.9): an append-only JSONL file, one line per registered entry with the keys
entry_id, kind ("config", "gate0_A" or "gate0_B"), spec and time (America/Vancouver, ISO 8601).
Every configuration and every Gate 0 test is registered before its first fit or computation, and
the trial count N is read from the ledger: n_total = n_program + entries. Registering an id again
with the same spec is a no-op (resumability); with a different spec it raises.

SplitScore is the selection metric's return value (interfaces section 5). It lives here, a module
without heavy imports, so the portfolio code (Task 4) can import it cheaply; cpcv.py re-exports it.
"""

from __future__ import annotations

import json
import math
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd

from ml_route_v2.constants import (
    COST_GATE_KS,
    HORIZONS,
    LGBM_DEPTHS,
    N_CONFIGURATIONS,
    N_PROGRAM_AT_FREEZE,
    RIDGE_LAMBDAS,
)

MODEL_KINDS = ("ridge", "lgbm")
LEDGER_KINDS = ("config", "gate0_A", "gate0_B")
LEDGER_TZ = ZoneInfo("America/Vancouver")


class LedgerError(RuntimeError):
    """The ledger is inconsistent (a re-registration with another spec, a bad line)."""


@dataclass(frozen=True)
class ModelSpec:
    kind: str  # "ridge" | "lgbm"
    param: float  # ridge: lambda (alpha = lambda x n_train); lgbm: max_depth
    model_id: str  # "ridge_l0.1" | "lgbm_d2"

    def as_dict(self) -> dict:
        return {"kind": self.kind, "param": float(self.param), "model_id": self.model_id}


@dataclass(frozen=True)
class Config:
    config_id: str
    model: ModelSpec
    k: float  # cost-gate multiple (V2.7)
    horizon: str  # one of HORIZONS

    def as_dict(self) -> dict:
        return {"config_id": self.config_id, "model": self.model.as_dict(), "k": float(self.k),
                "horizon": self.horizon}


@dataclass(frozen=True)
class SplitScore:
    """The selection metric on one validation set (V2.9): daily Sharpe, trades, daily net $."""

    sharpe: float
    n_trades: int
    daily: pd.Series  # daily net $ indexed by trade_date, zeros on no-trade dates
    n_risk_unknown: int = 0  # candidates not sized: no usable sigma or loss (code review C-02)


def ridge_spec(lam: float) -> ModelSpec:
    if not (math.isfinite(lam) and lam > 0):
        raise ValueError(f"ridge lambda {lam!r} must be finite and > 0")
    return ModelSpec("ridge", float(lam), f"ridge_l{lam:g}")


def lgbm_spec(depth: int) -> ModelSpec:
    if int(depth) != depth or depth < 1:
        raise ValueError(f"LightGBM max_depth {depth!r} must be a positive integer")
    return ModelSpec("lgbm", float(depth), f"lgbm_d{int(depth)}")


def config_id(model: ModelSpec, k: float, horizon: str) -> str:
    return f"{model.model_id}_k{k:g}_{horizon}"


def _build_configs() -> tuple[Config, ...]:
    models = tuple(ridge_spec(lam) for lam in RIDGE_LAMBDAS) + tuple(
        lgbm_spec(d) for d in LGBM_DEPTHS)
    out = tuple(Config(config_id(m, k, h), m, float(k), h)
                for m in models for k in COST_GATE_KS for h in HORIZONS)
    if len(out) != N_CONFIGURATIONS:
        raise LedgerError(f"grid has {len(out)} configurations, constants say {N_CONFIGURATIONS}")
    if len({c.config_id for c in out}) != len(out):
        raise LedgerError("duplicate config_id in the grid")
    return out


CONFIGS: tuple[Config, ...] = _build_configs()
CONFIGS_BY_ID: Mapping[str, Config] = {c.config_id: c for c in CONFIGS}


def tie_break_key(config: Config) -> tuple:
    """V2.9 smaller-model order; the smallest key wins a tie on the selection score."""
    kind = config.model.kind
    if kind not in MODEL_KINDS:
        raise ValueError(f"unknown model kind {kind!r}")
    size = -config.model.param if kind == "ridge" else config.model.param
    if config.horizon not in HORIZONS:
        raise ValueError(f"unknown horizon {config.horizon!r}")
    return (MODEL_KINDS.index(kind), size, -config.k, HORIZONS.index(config.horizon))


def _canonical(spec: Mapping) -> str:
    """Canonical JSON of a spec (sorted keys, tuples as lists); raises if not serializable."""
    try:
        return json.dumps(spec, sort_keys=True, separators=(",", ":"), allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise LedgerError(f"spec is not canonical JSON: {exc}") from exc


class ConfigLedger:
    """Append-only JSONL ledger of configurations and Gate 0 tests (V2.9 trial accounting)."""

    def __init__(self, path: Path) -> None:
        self._path = Path(path)
        self._entries: dict[str, tuple[str, str]] = {}  # entry_id -> (kind, canonical spec)
        if self._path.exists():
            self._load()

    @property
    def path(self) -> Path:
        return self._path

    def _load(self) -> None:
        text = self._path.read_text(encoding="utf-8")
        for number, line in enumerate(text.splitlines(), start=1):
            if not line.strip():
                continue
            try:
                rec = json.loads(line)
                entry_id, kind, spec = rec["entry_id"], rec["kind"], rec["spec"]
            except (json.JSONDecodeError, KeyError, TypeError) as exc:
                raise LedgerError(f"{self._path}:{number}: unreadable ledger line") from exc
            canon = _canonical(spec)
            if entry_id in self._entries and self._entries[entry_id] != (kind, canon):
                raise LedgerError(f"{self._path}:{number}: {entry_id!r} registered twice with "
                                  "different specs")
            self._entries[entry_id] = (kind, canon)

    def register(self, entry_id: str, kind: str, spec: Mapping) -> None:
        if not isinstance(entry_id, str) or not entry_id:
            raise LedgerError(f"entry_id {entry_id!r} must be a non-empty string")
        if kind not in LEDGER_KINDS:
            raise LedgerError(f"kind {kind!r} not in {LEDGER_KINDS}")
        canon = _canonical(spec)
        known = self._entries.get(entry_id)
        if known is not None:
            if known != (kind, canon):
                raise LedgerError(f"{entry_id!r} is already registered with another spec")
            return
        rec = {"entry_id": entry_id, "kind": kind, "spec": json.loads(canon),
               "time": datetime.now(LEDGER_TZ).isoformat(timespec="seconds")}
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, sort_keys=True, separators=(",", ":")) + "\n")
            fh.flush()
        self._entries[entry_id] = (kind, canon)

    def is_registered(self, entry_id: str) -> bool:
        return entry_id in self._entries

    def require(self, entry_ids: list[str] | tuple[str, ...]) -> None:
        """Raise unless every id is registered (the register-before-compute guard)."""
        missing = [e for e in entry_ids if e not in self._entries]
        if missing:
            raise LedgerError(f"computation before registration: {missing[:3]} "
                              f"({len(missing)} unregistered)")

    def n_registered(self, kind: str | None = None) -> int:
        if kind is not None and kind not in LEDGER_KINDS:
            raise LedgerError(f"kind {kind!r} not in {LEDGER_KINDS}")
        return sum(1 for k, _ in self._entries.values() if kind is None or k == kind)

    def n_total(self, n_program: int = N_PROGRAM_AT_FREEZE) -> int:
        """n_program (default: the program N at the freeze, constants.N_PROGRAM_AT_FREEZE; V23
        build) plus every registered entry."""
        if n_program < 0:
            raise LedgerError(f"n_program {n_program!r} must be >= 0")
        return int(n_program) + self.n_registered()


def register_configs(ledger: ConfigLedger, configs: tuple[Config, ...] | list[Config]) -> None:
    """Register every configuration (V2.9: before its first fit)."""
    for c in configs:
        ledger.register(c.config_id, "config", c.as_dict())
