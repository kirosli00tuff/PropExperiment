"""The v2 freeze check of every phase-1 step (Stage E.12 Task 1b; the manifest is Task 3's).

``verify_v2_freeze(path, expected_sha256)``: the manifest reports/stage_e12_ml_v2_freeze.json must
hash to ``expected_sha256`` (the sha256 of the file's bytes), have schema "ml_v2_freeze/1" and a
non-empty "files" list of {"path", "sha256", "bytes"}, and every listed file must exist under the
repository root with that size and sha256. Paths are repository-relative POSIX paths; an absolute
path or one with ".." is refused. Every problem is named at once (FreezeError); nothing runs.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
from typing import Any

FREEZE_SCHEMA = "ml_v2_freeze/1"
FREEZE_MANIFEST = "reports/stage_e12_ml_v2_freeze.json"
_HEX = frozenset("0123456789abcdef")
_SHOWN = 10


class FreezeError(RuntimeError):
    """The v2 freeze manifest is not the expected one, or a frozen file changed."""


def is_sha256(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and set(value) <= _HEX


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _entry_problems(entry: Any, root: Path) -> list[str]:
    if not isinstance(entry, dict) or not {"path", "sha256", "bytes"} <= set(entry):
        return [f"malformed entry {entry!r}"[:200]]
    rel, sha, size = entry["path"], entry["sha256"], entry["bytes"]
    if not isinstance(rel, str) or not rel:
        return [f"entry path {rel!r} is not a path"]
    pure = PurePosixPath(rel)
    if pure.is_absolute() or ".." in pure.parts:
        return [f"{rel}: not a repository-relative path"]
    if not is_sha256(sha) or not isinstance(size, int) or isinstance(size, bool) or size < 0:
        return [f"{rel}: sha256 or bytes malformed"]
    path = Path(root) / pure
    if not path.is_file():
        return [f"{rel}: missing"]
    problems = []
    if path.stat().st_size != size:
        problems.append(f"{rel}: {path.stat().st_size} bytes, the manifest says {size}")
    if file_sha256(path) != sha:
        problems.append(f"{rel}: sha256 differs from the manifest")
    return problems


def verify_v2_freeze(path: Path, expected_sha256: str, *, root: Path | None = None
                     ) -> dict[str, Any]:
    """The parsed manifest when it is the expected one and every listed file matches on disk;
    FreezeError otherwise (module docstring). ``root``: the repository root (default)."""
    if root is None:
        from data.config import REPO_ROOT

        root = REPO_ROOT
    if not is_sha256(expected_sha256):
        raise FreezeError(f"expected freeze sha256 is not a sha256: {expected_sha256!r}")
    path = Path(path)
    if not path.is_file():
        raise FreezeError(f"{path} does not exist")
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != expected_sha256:
        raise FreezeError(f"{path.name} sha256 {digest[:12]}... is not the expected "
                          f"{expected_sha256[:12]}...")
    try:
        doc = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise FreezeError(f"{path.name}: not valid JSON ({exc})") from exc
    if not isinstance(doc, dict) or doc.get("schema") != FREEZE_SCHEMA:
        raise FreezeError(f"{path.name}: schema is not {FREEZE_SCHEMA!r}")
    files = doc.get("files")
    if not isinstance(files, list) or not files:
        raise FreezeError(f"{path.name}: no files listed")
    problems = [p for e in files for p in _entry_problems(e, Path(root))]
    paths = [e.get("path") for e in files if isinstance(e, dict)]
    if len(set(paths)) != len(paths):
        problems.append("a path is listed twice")
    if problems:
        more = f" (and {len(problems) - _SHOWN} more)" if len(problems) > _SHOWN else ""
        raise FreezeError(f"v2 freeze check refused: {'; '.join(problems[:_SHOWN])}{more}")
    return doc


__all__ = ["FREEZE_MANIFEST", "FREEZE_SCHEMA", "FreezeError", "file_sha256", "is_sha256",
           "verify_v2_freeze"]
