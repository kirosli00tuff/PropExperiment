"""H6's run discipline before any bar is read (patterns of base_rules/guards.py and
c1_replication/guards.py, copied, never imported): the lead's settings, the registry names, the
freeze manifest, the pinned inputs, the registration and the run-once marker.

The freeze manifest (constants.FREEZE_MANIFEST_REL, written by the lead; its sha256 is given on the
command line) has the schema "stage_e20_h6_freeze/1":
    {"schema", "created_pdt", "files": [{"path", "sha256", "bytes"}, ...], ...}
``check_freeze`` requires: the manifest's own sha256; every listed file present with its sha256 and
size; every h6_rod/*.py listed; the prereg listed; every ml_route_v2 module loaded in this process
listed (the harness manifest does not cover ml_route_v2; gate0._b_test and pipeline.own_blackout
run from it); the GEX CSV listed when T3 is registered.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from collections.abc import Callable, Sequence
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from h6_rod import constants as K

LOCAL_TZ = ZoneInfo("America/Vancouver")


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


# ------------------------------------------------------------------ the lead's settings ----
def registry_names_valid() -> None:
    """The label and ids must be what screening.trial_registry accepts (stop item S1)."""
    from screening.trial_registry import _ID, _TEST

    label = K.REGISTRY_LABEL
    bad = [] if _TEST.fullmatch(label) else [f"label {label!r}"]
    bad += [f"id {i!r}" for i in K.TEST_IDS.values()
            if not (_ID.fullmatch(i) and i.startswith(f"{label}-"))]
    if bad:
        raise Refused(f"screening.trial_registry refuses {', '.join(bad)} (label "
                      f"{_TEST.pattern}, ids <label>-<suffix> matching {_ID.pattern}); the lead "
                      "fixes prereg section 8 and constants.REGISTRY_LABEL / TEST_IDS")


def lead_settings() -> tuple[str, ...]:
    """The registered tests; refused while a lead-set constant is None (constants docstring)."""
    if K.T3_REGISTERED is None:
        raise Refused("constants.T3_REGISTERED is None: the lead sets True or False before the "
                      "freeze (prereg section 7)")
    if K.ENGINE_LEAD_IN_DATES not in (0, 1):
        raise Refused("constants.ENGINE_LEAD_IN_DATES is not 0 or 1: the lead decides stop item "
                      "S3 (reports/stage_e20_briefs/h6_build.md) before the freeze")
    if K.T3_REGISTERED and K.GEX_CSV_SHA256 is None:
        raise Refused("T3 is registered but constants.GEX_CSV_SHA256 is None (the lead fills it "
                      "at the freeze)")
    registry_names_valid()
    return K.registered_tests()


def test_ids(tests: Sequence[str]) -> list[str]:
    return [K.TEST_IDS[t] for t in tests]


# ------------------------------------------------------------------ the freeze manifest ----
def code_files(package_dir: Path | None = None) -> list[Path]:
    d = package_dir if package_dir is not None else repo_root() / K.CODE_PACKAGE
    return sorted(Path(d).glob("*.py"))


def loaded_v2_files() -> list[Path]:
    """Every ml_route_v2 module file loaded in this process."""
    v2 = (repo_root() / "ml_route_v2").resolve()
    out = set()
    for mod in list(sys.modules.values()):
        f = getattr(mod, "__file__", None)
        if f and Path(f).resolve().is_relative_to(v2):
            out.add(Path(f).resolve())
    return sorted(out)


def required_files(tests: Sequence[str], gex_path: Path | None = None) -> list[Path]:
    req = [*code_files(), repo_path(K.PREREG_REL), *loaded_v2_files()]
    if "T3" in tests:
        req.append(Path(gex_path) if gex_path is not None else repo_path(K.GEX_CSV_REL))
    return req


def manifest_body(files: Sequence[Path], **extra: Any) -> dict[str, Any]:
    """A manifest in the expected format over ``files`` (the lead's builder may use it)."""
    return {"schema": K.FREEZE_SCHEMA, **extra,
            "files": [{"path": rel(p), "sha256": sha256_file(p), "bytes": Path(p).stat().st_size}
                      for p in files]}


def check_freeze(path: Path, expected_sha256: str, tests: Sequence[str],
                 gex_path: Path | None = None) -> dict[str, Any]:
    path = Path(path)
    if not path.is_file():
        raise Refused(f"freeze manifest {path} does not exist")
    got = sha256_file(path)
    if got != expected_sha256:
        raise Refused(f"freeze manifest {path.name}: sha256 {got[:12]}... is not the given "
                      f"{str(expected_sha256)[:12]}...")
    try:
        body = json.loads(path.read_bytes())
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise Refused(f"freeze manifest {path.name} is not JSON ({exc})") from exc
    if not isinstance(body, dict) or body.get("schema") != K.FREEZE_SCHEMA or \
            not isinstance(body.get("files"), list):
        raise Refused(f"freeze manifest is not {K.FREEZE_SCHEMA!r} with a files list")
    listed: dict[str, str] = {}
    for e in body["files"]:
        p = repo_path(e["path"])
        if not p.is_file() or p.stat().st_size != e["bytes"] or sha256_file(p) != e["sha256"]:
            raise Refused(f"frozen file {e['path']} is missing or changed")
        listed[str(p.resolve())] = e["sha256"]
    unlisted = [rel(p) for p in required_files(tests, gex_path)
                if str(Path(p).resolve()) not in listed]
    if unlisted:
        raise Refused(f"not in the freeze manifest: {unlisted}")
    return {"path": rel(path), "sha256": got, "files": len(listed),
            "v2_files": [rel(p) for p in loaded_v2_files()]}


# ------------------------------------------------------------------ pinned inputs ----
def check_pinned(path: Path, expected_sha256: str, what: str) -> str:
    path = Path(path)
    if not path.is_file():
        raise Refused(f"{what} {path} does not exist")
    got = sha256_file(path)
    if got != expected_sha256:
        raise Refused(f"{what} {path.name}: sha256 {got[:12]}... is not the pinned "
                      f"{expected_sha256[:12]}...")
    return got


def check_harness(expected: str, preflight: Callable[[str], str]) -> str:
    if expected != K.HARNESS_SHA256:
        raise Refused(f"--harness-sha256 {expected[:12]}... is not H6's pinned harness "
                      f"{K.HARNESS_SHA256[:12]}... (v12)")
    got = preflight(expected)
    if got != expected:
        raise Refused("the harness preflight did not confirm the given sha256")
    return got


# ------------------------------------------------------------------ registration ----
def check_registry_path(registry: Path, test_mode: bool) -> Path:
    from screening.trial_registry import REGISTRY_PATH

    if Path(registry).resolve() != Path(REGISTRY_PATH).resolve() and not test_mode:
        raise Refused(f"registry {registry} is not {REGISTRY_PATH} (only the test mode may name "
                      "another)")
    if not Path(registry).is_file():
        raise Refused(f"registry {registry} does not exist")
    return Path(registry)


def check_registered(tests: Sequence[str], freeze_sha256: str, registry: Path) -> dict[str, Any]:
    from screening.trial_registry import TrialRegistryError, require_registered

    try:
        return require_registered(test_ids(tests), test=K.REGISTRY_LABEL,
                                  freeze_sha256=freeze_sha256, path=registry)
    except TrialRegistryError as exc:
        raise Refused(f"H6 is not registered as required: {exc}") from exc


def refuse_if_registered(tests: Sequence[str], registry: Path) -> None:
    from screening.trial_registry import read_registry

    entries = read_registry(registry)
    taken = {x for e in entries for x in e["test_ids"]}
    if any(e["test"] == K.REGISTRY_LABEL for e in entries) or set(test_ids(tests)) & taken:
        raise Refused(f"{K.REGISTRY_LABEL} is already registered: a registration is never repeated")


# ------------------------------------------------------------------ run-once marker ----
def refuse_if_marked(marker: Path) -> None:
    if Path(marker).exists():
        raise Refused(f"run-once marker {marker} exists: H6 runs once, never again")


def write_marker(marker: Path, record: dict[str, Any]) -> Path:
    """Create the marker exclusively (O_EXCL), before any bar is read."""
    path = Path(marker)
    path.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(LOCAL_TZ).isoformat(timespec="seconds")
    body = json.dumps({"schema": K.MARKER_SCHEMA, "test": K.REGISTRY_LABEL,
                       "written_local": now, **record}, indent=1, default=str).encode()
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o444)
    except FileExistsError as exc:
        raise Refused(f"run-once marker {path} exists") from exc
    with os.fdopen(fd, "wb") as fh:
        fh.write(body)
    return path


__all__ = ["Refused", "check_freeze", "check_harness", "check_pinned", "check_registered",
           "check_registry_path", "code_files", "lead_settings", "loaded_v2_files",
           "manifest_body", "refuse_if_marked", "refuse_if_registered", "registry_names_valid",
           "rel", "repo_path", "required_files", "sha256_file", "test_ids", "write_marker"]
