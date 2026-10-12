"""Shared synthetic fixtures of the pattern_search tests (synthetic data only; no store, no ledger).

- ``world_small``: the 17-vehicle synthetic world (ml_route_v2.synthetic via
  pattern_search.world.synthetic_world) over 2021-03-01..2021-06-30 with the frozen 210-date
  warm-up; ``panel_small`` its composed search panel; both cached per process.
- ``temp_registry``: a trial registry in a temporary directory chained 471 -> 483 (a stand-in
  line of 12 ids) -> 528 (E20S-01..E20S-45 under the given freeze sha256), or stopped before the
  E20S line.
- ``make_hooks``: run.Hooks for the test mode (no harness, store or release-calendar reads).
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date
from functools import lru_cache
from pathlib import Path
from typing import Any

from pattern_search import constants as K

SMALL_FIRST = date(2021, 3, 1)
SMALL_LAST = date(2021, 6, 30)
SEED = 20261011
STUB_SHA = "0" * 64


@lru_cache(maxsize=4)
def world_small(seed: int = SEED) -> Any:
    from pattern_search.world import synthetic_world

    return synthetic_world(SMALL_FIRST, SMALL_LAST, seed=seed)


@lru_cache(maxsize=2)
def panel_small(seed: int = SEED) -> Any:
    from pattern_search.panel import build_search_panel

    return build_search_panel(world_small(seed))


@lru_cache(maxsize=2)
def rows_small(seed: int = SEED) -> Any:
    from pattern_search.rows import search_rows

    return search_rows(world_small(seed))


def freeze_file(tmp: Path, files: Sequence[Path]) -> tuple[Path, str]:
    """A stage_e20_search_freeze/1 manifest over ``files`` in ``tmp``; (path, sha256)."""
    from pattern_search.freeze_manifest import body, write_once

    path = Path(tmp) / "freeze.json"
    return path, write_once(path, body(list(files)))


def temp_registry(tmp: Path, freeze: Path, freeze_sha256: str, *, with_search: bool = True,
                  label: str = K.REGISTRY_LABEL, ids: Sequence[str] = K.CONFIG_IDS) -> Path:
    from pattern_search import preflight as pf
    from screening.trial_registry import init_registry, register

    reg = Path(tmp) / "registry.jsonl"
    init_registry(reg)
    stand_in = Path(tmp) / "stand_in.txt"
    stand_in.write_text("stand-in freeze\n")
    register("XT", [f"XT-{i}" for i in range(1, 13)], stand_in, pf.sha256_file(stand_in),
             STUB_SHA, path=reg)
    if with_search:
        register(label, list(ids), freeze, freeze_sha256, STUB_SHA, path=reg)
    return reg


def make_hooks(world_fn: Any, *, configs: Sequence[Any] | None = None,
               required: Sequence[Path] = (), pin: str = "synthetic-test") -> Any:
    from pattern_search.run import Hooks

    return Hooks(preflight=lambda s: s, v2_freeze=lambda: {"stub": True},
                 required=lambda: list(required), stores=lambda p: {"stub": True},
                 releases=lambda: {"stub": True}, world=world_fn, world_pin=pin,
                 configs=None if configs is None else tuple(configs))


def run_paths(tmp: Path, freeze: Path, registry: Path) -> Any:
    from pattern_search.run import RunPaths

    tmp = Path(tmp)
    return RunPaths(freeze, registry, tmp / "state", tmp / "reports", tmp / "result.json",
                    tmp / "result.md")


def configs_named(*ids: str) -> tuple[Any, ...]:
    from ml_route_v2.configs import CONFIGS_BY_ID

    return tuple(CONFIGS_BY_ID[i] for i in ids)
