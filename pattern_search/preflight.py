"""The search's run discipline before any bar is read (patterns of h6_rod/preflight.py,
base_rules/guards.py and c1_replication/guards.py, copied, never imported): the harness preflight
at v12, the v2 freeze verification, the search freeze manifest, the store sha256s and, for
``run``, the registration of the 45 configurations (reports/stage_e20_plan.md sections 7 and 11).

The search freeze manifest (constants.FREEZE_MANIFEST_REL, built by the lead with
pattern_search.freeze_manifest; its sha256 is given on the command line) has the schema
"stage_e20_search_freeze/1": {"schema", "created_pdt", "files": [{"path", "sha256", "bytes"}]}.
``check_freeze`` requires its own sha256, every listed file present with its size and sha256
(every listed path first passes the read guard, so nothing forbidden is ever hashed), and every
required file listed (freeze_manifest.required_files: the plan, every pattern_search module, every
pattern_search test, every input the search reads, every ml_route_v2 module loaded).
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any

from pattern_search import constants as K
from pattern_search import guard


class Refused(RuntimeError):
    """A precondition failed: nothing was written and no bar was read."""


def repo_root() -> Path:
    from data.config import REPO_ROOT

    return Path(REPO_ROOT)


def repo_path(rel: str | Path) -> Path:
    p = Path(rel)
    return p if p.is_absolute() else repo_root() / p


def rel(path: Path) -> str:
    p = Path(path).resolve()
    root = repo_root().resolve()
    return p.relative_to(root).as_posix() if p.is_relative_to(root) else str(p)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def guarded_sha256(path: Path) -> str:
    """sha256 of a file the read guard does not refuse (a store must be one of the 17)."""
    why = guard.refusal_reason(path)
    if why is not None:
        raise guard.GuardRefusal(f"E.20 search guard: refused to hash {path}: {why}")
    return sha256_file(path)


# ------------------------------------------------------------------ harness, v2 freeze ----
def check_harness(expected: str, preflight: Callable[[str], str]) -> str:
    if expected != K.HARNESS_SHA256:
        raise Refused(f"--harness-sha256 {expected[:12]}... is not the pinned harness "
                      f"{K.HARNESS_SHA256[:12]}... (v12)")
    got = preflight(expected)
    if got != expected:
        raise Refused("the harness preflight did not confirm the given sha256")
    return got


def check_v2_freeze(path: Path | None = None) -> dict[str, Any]:
    from ml_route_v2.phase1.freeze import FreezeError, verify_v2_freeze

    path = Path(path) if path is not None else repo_path(K.V2_FREEZE_REL)
    try:
        doc = verify_v2_freeze(path, K.V2_FREEZE_SHA256)
    except FreezeError as exc:
        raise Refused(f"v2 freeze check refused: {exc}") from exc
    return {"path": rel(path), "sha256": K.V2_FREEZE_SHA256, "files": len(doc["files"])}


# ------------------------------------------------------------------ the search freeze ----
def check_freeze(path: Path, expected_sha256: str, required: Sequence[Path]) -> dict[str, Any]:
    path = Path(path)
    if not path.is_file():
        raise Refused(f"search freeze manifest {path} does not exist")
    got = sha256_file(path)
    if got != expected_sha256:
        raise Refused(f"search freeze manifest {path.name}: sha256 {got[:12]}... is not the "
                      f"given {str(expected_sha256)[:12]}...")
    try:
        body = json.loads(path.read_bytes())
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise Refused(f"search freeze manifest {path.name} is not JSON ({exc})") from exc
    if not isinstance(body, dict) or body.get("schema") != K.FREEZE_SCHEMA or \
            not isinstance(body.get("files"), list):
        raise Refused(f"search freeze manifest is not {K.FREEZE_SCHEMA!r} with a files list")
    listed: dict[str, str] = {}
    for e in body["files"]:
        p = repo_path(e["path"])
        if not p.is_file() or p.stat().st_size != e["bytes"] or guarded_sha256(p) != e["sha256"]:
            raise Refused(f"frozen file {e['path']} is missing or changed")
        if str(p.resolve()) in listed:
            raise Refused(f"{e['path']} is listed twice")
        listed[str(p.resolve())] = e["sha256"]
    unlisted = [rel(p) for p in required if str(Path(p).resolve()) not in listed]
    if unlisted:
        raise Refused(f"not in the search freeze manifest: {unlisted[:8]}"
                      f"{' ...' if len(unlisted) > 8 else ''}")
    return {"path": rel(path), "sha256": got, "files": len(listed)}


# ------------------------------------------------------------------ stores ----
def check_stores(records: Mapping[str, Mapping[str, Any]], step2_root: Path | None = None
                 ) -> dict[str, str]:
    """Each of the 17 stores hashes to the E.17 manifest's sha256 (bytes only, nothing decoded;
    the guard checks every path first)."""
    out = {}
    for root in K.PATH_ROOTS:
        path = guard.step2_store_path(root, step2_root)
        guard.check_store_path(path)  # only the 17 real stores, whatever step2_root says
        if not path.is_file():
            raise Refused(f"the {root} step 2 store {rel(path)} does not exist")
        got = sha256_file(path)
        if got != records[root]["store_sha256"]:
            raise Refused(f"the {root} store hashes to {got[:12]}..., not the E.17 manifest's "
                          f"{records[root]['store_sha256'][:12]}...")
        out[root] = got
    return out


# ------------------------------------------------------------------ registration ----
def registry_names_valid() -> None:
    from screening.trial_registry import _ID, _TEST

    bad = [] if _TEST.fullmatch(K.REGISTRY_LABEL) else [f"label {K.REGISTRY_LABEL!r}"]
    bad += [f"id {i!r}" for i in K.CONFIG_IDS
            if not (_ID.fullmatch(i) and i.startswith(f"{K.REGISTRY_LABEL}-"))]
    if bad or len(set(K.CONFIG_IDS)) != K.N_CONFIGS:
        raise Refused(f"screening.trial_registry refuses {', '.join(bad) or 'the id list'}")


def check_registry_path(registry: Path, test_mode: bool) -> Path:
    from screening.trial_registry import REGISTRY_PATH

    if Path(registry).resolve() != Path(REGISTRY_PATH).resolve() and not test_mode:
        raise Refused(f"registry {registry} is not {REGISTRY_PATH} (only the test mode may name "
                      "another)")
    if not Path(registry).is_file():
        raise Refused(f"registry {registry} does not exist")
    return Path(registry)


def check_registered(freeze_sha256: str, registry: Path) -> dict[str, Any]:
    """The one registry line holding E20S-01..E20S-45 under label E20S with this freeze sha256,
    whose N after is plan 9's 528 (483 + 45); Refused otherwise (before any fit)."""
    from screening.trial_registry import TrialRegistryError, require_registered

    registry_names_valid()
    try:
        entry = require_registered(list(K.CONFIG_IDS), test=K.REGISTRY_LABEL,
                                   freeze_sha256=freeze_sha256, path=registry)
    except TrialRegistryError as exc:
        raise Refused(f"the 45 configurations are not registered as required: {exc}") from exc
    if list(entry["test_ids"]) != list(K.CONFIG_IDS):
        raise Refused(f"registry line {entry['entry_id']} holds {len(entry['test_ids'])} ids, "
                      "not exactly E20S-01..E20S-45")
    if (int(entry["n_before"]), int(entry["n_after"])) != (K.N_TRIALS_BEFORE,
                                                           K.N_TOTAL_AT_SCREEN):
        raise Refused(f"registry line {entry['entry_id']}: N {entry['n_before']} -> "
                      f"{entry['n_after']}, not plan 11's {K.N_TRIALS_BEFORE} -> "
                      f"{K.N_TOTAL_AT_SCREEN} (the DSR's N would differ from the plan)")
    return dict(entry)


__all__ = ["Refused", "check_freeze", "check_harness", "check_registered",
           "check_registry_path", "check_stores", "check_v2_freeze", "guarded_sha256", "rel",
           "registry_names_valid", "repo_path", "repo_root", "sha256_file"]
