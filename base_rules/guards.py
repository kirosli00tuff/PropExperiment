"""The run discipline of lead_spec section 6: the freeze-manifest check, the registration check
and the run-once marker, all before any bar is read.

The freeze manifest is the lead's reports/stage_e16_freeze.json (written by
reports/stage_e16_briefs/freeze_manifest.py; path a parameter), schema "stage_e16_freeze/1":
  {"schema", "created_pdt", "pins", "frozen_globs", "files": [{"path", "sha256", "bytes"}, ...]}
The registry label and ids are fixed in constants (E16, E16-H1..E16-H5; ruling R-B4: no
run-time override); the registration must hold this manifest's sha256 (F-02). The check:
the manifest's own sha256 equals the given one; every listed file exists with its sha256 and size;
every base_rules/*.py file is listed (no unlisted code runs); every input the runner reads
(``INPUT_ROLES``: the settlement table, the windows, the release calendars, the EC-AUC and
livestock calendars, the quote record and the six hist calendars) is listed. ``input_paths``
may name other paths for the roles (tests, the probe); each must still be a listed file.
"""

from __future__ import annotations

import hashlib
import json
import os
from collections.abc import Mapping
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from base_rules import constants as K
from data.config import REPO_ROOT

INPUT_ROLES: Mapping[str, Path] = {
    "settlement": K.SETTLEMENT_PATH, "windows": K.WINDOWS_PATH,
    "release_frozen": K.RELEASE_FROZEN_PATH, "release_hist": K.RELEASE_HIST_PATH,
    "ecauc_hist": K.ECAUC_HIST_PATH, "ecauc_announcements": K.ANNOUNCEMENTS_PATH,
    "livestock_hist": K.LIVESTOCK_HIST_PATH,
    "quote_record": Path(K.QUOTE_RECORD),
    **{f"hist_calendar_{g}": K.HIST_CALENDAR_DIR / f"{g}.json" for g in K.HIST_GROUPS_FROZEN}}
INPUT_NAMES = tuple(INPUT_ROLES)


class Refused(RuntimeError):
    """A precondition failed: nothing was written and no bar was read."""


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def rel(path: Path) -> str:
    p = Path(path).resolve()
    return p.relative_to(REPO_ROOT).as_posix() if p.is_relative_to(REPO_ROOT) else str(p)


def code_files(code_dir: Path = K.CODE_DIR) -> list[Path]:
    return sorted(Path(code_dir).glob("*.py"))


def manifest_body(files: list[Path], **extra: Any) -> dict[str, Any]:
    """A manifest in the lead's format over ``files`` (tests and the probe)."""
    return {"schema": K.FREEZE_SCHEMA, "pins": {}, "frozen_globs": [], **extra,
            "files": [{"path": rel(p), "sha256": sha256_file(p), "bytes": Path(p).stat().st_size}
                      for p in files]}


def check_freeze(path: Path, expected_sha256: str, *,
                 input_paths: Mapping[str, str | Path] | None = None,
                 code_dir: Path = K.CODE_DIR) -> dict[str, Any]:
    """The verified freeze, normalized: registry_test, test_ids, inputs {role: {path, sha256}}."""
    path = Path(path)
    if not path.is_file():
        raise Refused(f"freeze manifest {path} does not exist")
    if sha256_file(path) != expected_sha256:
        raise Refused(f"freeze manifest {path.name}: sha256 is not {expected_sha256[:12]}...")
    body = json.loads(path.read_bytes())
    if body.get("schema") != K.FREEZE_SCHEMA or not isinstance(body.get("files"), list):
        raise Refused(f"freeze manifest is not {K.FREEZE_SCHEMA!r} with a files list")
    listed: dict[str, str] = {}
    for e in body["files"]:
        p = K.repo_path(e["path"])
        if not p.is_file() or sha256_file(p) != e["sha256"] or p.stat().st_size != e["bytes"]:
            raise Refused(f"frozen file {e['path']} is missing or changed")
        listed[str(p.resolve())] = e["sha256"]
    unlisted = [rel(p) for p in code_files(code_dir) if str(p.resolve()) not in listed]
    if unlisted:
        raise Refused(f"base_rules code not in the freeze: {unlisted}")
    inputs = {}
    for role, default in INPUT_ROLES.items():
        p = K.repo_path((input_paths or {}).get(role, default))
        if str(p.resolve()) not in listed:
            raise Refused(f"input {role} ({rel(p)}) is not a file of the freeze")
        inputs[role] = {"path": str(p), "sha256": listed[str(p.resolve())]}
    return {"registry_test": K.REGISTRY_TEST, "test_ids": dict(K.TEST_IDS), "inputs": inputs}


def check_registered(test: str, freeze: dict[str, Any], registry: Path, freeze_sha256: str
                     ) -> dict[str, Any]:
    """F-02: the one registration holding the test id under label E16 AND made against this
    freeze manifest's sha256 (screening.trial_registry.require_registered)."""
    from screening.trial_registry import TrialRegistryError, require_registered

    try:
        return require_registered([freeze["test_ids"][test]], test=freeze["registry_test"],
                                  freeze_sha256=freeze_sha256, path=registry)
    except TrialRegistryError as exc:
        raise Refused(f"{test}: {exc}") from exc


def check_registry_path(registry: Path, test_mode: bool) -> dict[str, str]:
    """F-03: the registry is the repository's ledger/trial_registrations.jsonl (another path
    only in the test mode, --input-paths); returns its path and sha256 for the outputs."""
    want = K.repo_path(K.REGISTRY_PATH).resolve()
    got = Path(registry).resolve()
    if got != want and not test_mode:
        raise Refused(f"registry {registry} is not {K.REGISTRY_PATH} (only the test mode, "
                      "--input-paths, may name another)")
    if not got.is_file():
        raise Refused(f"registry {registry} does not exist")
    return {"path": rel(got), "sha256": sha256_file(got)}


def marker_path(out_dir: Path, test: str) -> Path:
    return Path(out_dir) / f"{test}_RUN_ONCE.json"


def refuse_if_marked(out_dir: Path, test: str) -> None:
    if marker_path(out_dir, test).exists():
        raise Refused(f"{test} has a run-once marker in {out_dir}: a test runs once, never again")


def write_marker(out_dir: Path, test: str, record: dict[str, Any]) -> Path:
    """Create the marker exclusively (O_EXCL), before any bar is read."""
    path = marker_path(out_dir, test)
    path.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(ZoneInfo("America/Vancouver")).isoformat(timespec="seconds")
    body = json.dumps({"schema": K.MARKER_SCHEMA, "test": test, "written_local": now,
                       **record}, indent=1, default=str).encode()
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o444)
    except FileExistsError as exc:
        raise Refused(f"{test}: run-once marker {path} exists") from exc
    with os.fdopen(fd, "wb") as fh:
        fh.write(body)
    return path


__all__ = ["INPUT_NAMES", "INPUT_ROLES", "Refused", "check_freeze", "check_registered",
           "check_registry_path",
           "code_files", "manifest_body", "marker_path", "refuse_if_marked", "rel",
           "sha256_file", "write_marker"]
