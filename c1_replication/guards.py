"""Guards shared by test C1's two steps: the E.12 state manifest, the v2 freeze, a ledger copy for
frozen code that registers, and a no-fit guard around Gate 0's reload.

- ``verify_state(state_dir, manifest)``: the manifest (schema "e14_e12_state_manifest/1",
  "files": {relative path: {"bytes", "sha256"}}) must list E.12's 45 OOF split files, the family B
  meta, both stage pickles and phase1_build.json; every listed file must exist with its size and
  sha256, and the state dir must hold no other file. Checked BEFORE anything is loaded, and again
  after the step (the step never writes there).
- ``verify_v2(manifest, sha)``: ml_route_v2.phase1.freeze.verify_v2_freeze on E.12's manifest
  (every ml_route_v2 file byte-identical to the one E.12 ran).
- ``ledger_copy(path)``: a temporary copy of the ML config ledger for a frozen function that
  registers (gate0.gate0_b_trades); the real file's sha256 is taken before and after.
- ``no_fits()``: while active, ml_route_v2.gate0.fit_model raises (Gate 0's _oof may only reload
  its persisted splits); the frozen attribute is restored on exit.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from pathlib import Path, PurePosixPath
from typing import Any

from c1_replication.constants import E12_GATE0_DIR, STATE_MANIFEST_SCHEMA

SPLITS_PER_HORIZON = 15  # C(6, 2) outer CPCV splits (constants.N_BLOCKS, N_TEST_BLOCKS)
STATE_HORIZONS = ("h60", "h120", "hF")
REQUIRED_STATE_FILES = (
    *(f"{E12_GATE0_DIR}/gate0B_{h}_s{i:02d}.npy" for h in STATE_HORIZONS
      for i in range(SPLITS_PER_HORIZON)),
    f"{E12_GATE0_DIR}/gate0B_meta.json", "stages/phase1_panel.pkl", "stages/phase1_filter.pkl",
    "phase1_build.json",
)


class C1Refused(RuntimeError):
    """An input check failed before anything was computed: nothing is written."""


class C1Stop(RuntimeError):
    """A C1 guard stopped the step ("C1 STOP: ...")."""


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _manifest_files(doc: Any, name: str) -> dict[str, Mapping[str, Any]]:  # noqa: ANN401
    if not isinstance(doc, dict) or doc.get("schema") != STATE_MANIFEST_SCHEMA:
        raise C1Refused(f"{name}: schema is not {STATE_MANIFEST_SCHEMA!r}")
    files = doc.get("files")
    if not isinstance(files, dict) or not files:
        raise C1Refused(f"{name}: no files")
    for rel, rec in files.items():
        pure = PurePosixPath(rel)
        if pure.is_absolute() or ".." in pure.parts:
            raise C1Refused(f"{name}: {rel!r} is not a relative path inside the state dir")
        if not isinstance(rec, dict) or not isinstance(rec.get("sha256"), str) or \
                not isinstance(rec.get("bytes"), int):
            raise C1Refused(f"{name}: {rel}: needs bytes and sha256")
    missing = [f for f in REQUIRED_STATE_FILES if f not in files]
    if missing:
        raise C1Refused(f"{name}: the manifest does not list {missing[:3]} "
                        f"({len(missing)} required files missing)")
    return files


def verify_state(state_dir: Path, manifest: Path, expected_manifest_sha256: str | None = None
                 ) -> dict[str, Any]:
    """Every manifest file present with its size and sha256, and nothing else (module
    docstring). Returns the record written into the outputs."""
    state_dir, manifest = Path(state_dir), Path(manifest)
    if not manifest.is_file():
        raise C1Refused(f"state manifest {manifest} does not exist")
    raw = manifest.read_bytes()
    msha = hashlib.sha256(raw).hexdigest()
    if expected_manifest_sha256 is not None and msha != expected_manifest_sha256:
        raise C1Refused(f"{manifest.name}: sha256 {msha[:12]}... is not the expected "
                        f"{expected_manifest_sha256[:12]}...")
    try:
        doc = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise C1Refused(f"{manifest.name}: not JSON ({exc})") from exc
    files = _manifest_files(doc, manifest.name)
    if not state_dir.is_dir():
        raise C1Refused(f"state dir {state_dir} does not exist")
    problems = []
    for rel, rec in sorted(files.items()):
        path = state_dir / PurePosixPath(rel)
        if not path.is_file():
            problems.append(f"{rel}: missing")
        elif path.stat().st_size != rec["bytes"]:
            problems.append(f"{rel}: {path.stat().st_size} bytes, the manifest says {rec['bytes']}")
        elif file_sha256(path) != rec["sha256"]:
            problems.append(f"{rel}: sha256 differs from the manifest")
    present = {p.relative_to(state_dir).as_posix() for p in state_dir.rglob("*") if p.is_file()}
    extra = sorted(present - set(files))
    if extra:
        problems.append(f"files not in the manifest: {extra[:3]} ({len(extra)})")
    if problems:
        raise C1Refused(f"E.12 state check refused: {'; '.join(problems[:5])}"
                        + (f" (and {len(problems) - 5} more)" if len(problems) > 5 else ""))
    return {"state_dir": str(state_dir), "manifest": str(manifest), "manifest_sha256": msha,
            "n_files": len(files), "n_npy": sum(f.endswith(".npy") for f in files)}


def verify_v2(manifest: Path, sha256: str, root: Path | None = None) -> dict[str, Any]:
    from ml_route_v2.phase1.freeze import FreezeError, verify_v2_freeze

    try:
        doc = verify_v2_freeze(Path(manifest), sha256, root=root)
    except FreezeError as exc:
        raise C1Refused(f"v2 freeze: {exc}") from exc
    return {"manifest": str(manifest), "sha256": sha256, "files": len(doc["files"])}


def pinned_file(path: Path, expected_sha256: str, what: str) -> bytes:
    path = Path(path)
    if not path.is_file():
        raise C1Refused(f"{what} {path} does not exist")
    raw = path.read_bytes()
    got = hashlib.sha256(raw).hexdigest()
    if got != expected_sha256:
        raise C1Refused(f"{what} {path.name}: sha256 {got[:12]}... is not the expected "
                        f"{str(expected_sha256)[:12]}...")
    return raw


@contextmanager
def ledger_copy(real: Path) -> Iterator[tuple[Path, dict[str, Any]]]:
    """(a temporary copy of ``real``, a record filled with the sha256s on exit)."""
    real = Path(real)
    if not real.is_file():
        raise C1Refused(f"ML config ledger {real} does not exist")
    rec: dict[str, Any] = {"path": str(real), "sha256_before": file_sha256(real)}
    with tempfile.TemporaryDirectory(prefix="c1_ledger_") as tmp:
        copy = Path(tmp) / real.name
        shutil.copyfile(real, copy)
        rec["copy_sha256_before"] = file_sha256(copy)
        try:
            yield copy, rec
        finally:
            rec["copy_sha256_after"] = file_sha256(copy)
            rec["sha256_after"] = file_sha256(real)
            rec["unchanged"] = rec["sha256_before"] == rec["sha256_after"]
            rec["copy_unchanged"] = rec["copy_sha256_before"] == rec["copy_sha256_after"]


@contextmanager
def no_fits() -> Iterator[dict[str, int]]:
    """ml_route_v2.gate0.fit_model raises while active (module docstring)."""
    from ml_route_v2 import gate0

    original = gate0.fit_model
    calls = {"fit_attempts": 0}

    def refuse(*_a: Any, **_k: Any) -> Any:  # noqa: ANN401
        calls["fit_attempts"] += 1
        raise C1Stop("C1 STOP: q reproduction mismatch (Gate 0's _oof tried to fit; a "
                     "persisted OOF split is missing or does not match)")

    gate0.fit_model = refuse
    try:
        yield calls
    finally:
        gate0.fit_model = original


__all__ = ["REQUIRED_STATE_FILES", "C1Refused", "C1Stop", "file_sha256", "ledger_copy",
           "no_fits", "pinned_file", "verify_state", "verify_v2"]
