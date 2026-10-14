"""The E.21 freeze manifest (lead_spec section 11): every multiday/*.py, every
tests/test_multiday_*.py, the base_rules/*.py modules E.21 imports (reused, frozen since E.16),
multiday/README.md and screening/trial_registry.py (FR-7), the lead's spec, the
pre-registration and every input file of the spec's section 0, each with its sha256 and size;
schema "stage_e21_freeze/1".

    uv run python -m multiday.freeze_manifest build [--out reports/stage_e21_freeze.json]
    uv run python -m multiday.freeze_manifest verify [--freeze ...] --sha256 <sha>

``build`` refuses to overwrite an existing manifest (O_EXCL); ``--input-paths`` (tests only)
names other paths per role. ``verify`` re-checks every listed file.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections.abc import Mapping
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from base_rules import guards as BG
from data.config import REPO_ROOT
from multiday import constants as K

BASE_RULES_DIR = BG.K.CODE_DIR


def input_roles() -> dict[str, Path]:
    """Role -> default path: base_rules' E.16 inputs, the E.17 run manifest, H2's result, the
    spec and the pre-registration."""
    return {**{r: Path(p) for r, p in BG.INPUT_ROLES.items()},
            **{r: Path(p) for r, p in K.EXTRA_INPUT_ROLES.items()},
            "spec": K.SPEC_PATH, "prereg": K.PREREG_PATH}


def resolve_inputs(overrides: Mapping[str, Any] | None = None) -> dict[str, Path]:
    return {r: K.repo_path((overrides or {}).get(r, p)) for r, p in input_roles().items()}


def code_files(code_dir: Path = K.CODE_DIR) -> list[Path]:
    return sorted(Path(code_dir).glob("*.py"))


def test_files(repo: Path = REPO_ROOT) -> list[Path]:
    return sorted(Path(repo).glob(K.TEST_GLOB))


def base_rules_files() -> list[Path]:
    return sorted(Path(BASE_RULES_DIR).glob("*.py"))


def pinned_files() -> list[Path]:
    """FR-7: the package README (the lead's rulings) and the registry code the run calls."""
    return [K.CODE_DIR / "README.md", REPO_ROOT / "screening" / "trial_registry.py"]


def manifest_body(inputs: Mapping[str, Path]) -> dict[str, Any]:
    files = [*code_files(), *test_files(), *base_rules_files(), *pinned_files(),
             *inputs.values()]
    seen, rows = set(), []
    for p in files:
        key = str(Path(p).resolve())
        if key in seen:
            continue
        seen.add(key)
        if not Path(p).is_file():
            raise FileNotFoundError(f"freeze input {p} does not exist")
        rows.append({"path": BG.rel(p), "sha256": BG.sha256_file(p),
                     "bytes": Path(p).stat().st_size})
    now = datetime.now(ZoneInfo("America/Vancouver")).isoformat(timespec="seconds")
    return {"schema": K.FREEZE_SCHEMA, "created_local": now,
            "registry_test": K.REGISTRY_TEST, "test_ids": dict(K.TEST_IDS),
            "inputs": {r: BG.rel(p) for r, p in inputs.items()}, "files": rows}


def build(out: Path, inputs: Mapping[str, Path]) -> Path:
    body = json.dumps(manifest_body(inputs), indent=1).encode()
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(out, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o444)
    with os.fdopen(fd, "wb") as fh:
        fh.write(body + b"\n")
    return out


class FreezeRefused(RuntimeError):
    """The freeze manifest does not verify; nothing is run."""


def verify(path: Path, expected_sha256: str, *,
           input_overrides: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """The verified freeze: every listed file (sha256, size), every multiday/*.py,
    tests/test_multiday_*.py and base_rules/*.py listed, every input role a listed file.
    Returns {"inputs": {role: {"path", "sha256"}}, "files": {...}}."""
    path = Path(path)
    if not path.is_file():
        raise FreezeRefused(f"freeze manifest {path} does not exist")
    if BG.sha256_file(path) != expected_sha256:
        raise FreezeRefused(f"freeze manifest {path.name}: sha256 is not "
                            f"{expected_sha256[:12]}...")
    body = json.loads(path.read_bytes())
    if body.get("schema") != K.FREEZE_SCHEMA or not isinstance(body.get("files"), list):
        raise FreezeRefused(f"freeze manifest is not {K.FREEZE_SCHEMA!r} with a files list")
    listed: dict[str, str] = {}
    for e in body["files"]:
        p = K.repo_path(e["path"])
        if not p.is_file() or BG.sha256_file(p) != e["sha256"] or p.stat().st_size != e["bytes"]:
            raise FreezeRefused(f"frozen file {e['path']} is missing or changed")
        listed[str(p.resolve())] = e["sha256"]
    unlisted = [BG.rel(p) for p in (*code_files(), *test_files(), *base_rules_files(),
                                    *pinned_files()) if str(p.resolve()) not in listed]
    if unlisted:
        raise FreezeRefused(f"code or tests not in the freeze: {unlisted}")
    roles = {**(body.get("inputs") or {}), **(input_overrides or {})}
    inputs = {}
    for role in input_roles():
        if role not in roles:
            raise FreezeRefused(f"the freeze names no path for input {role}")
        p = K.repo_path(roles[role])
        if str(p.resolve()) not in listed:
            raise FreezeRefused(f"input {role} ({BG.rel(p)}) is not a file of the freeze")
        inputs[role] = {"path": str(p), "sha256": listed[str(p.resolve())]}
    return {"inputs": inputs, "registry_test": K.REGISTRY_TEST, "test_ids": dict(K.TEST_IDS)}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="multiday.freeze_manifest")
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--out", default=str(K.repo_path(K.FREEZE_PATH)))
    b.add_argument("--input-paths", help="tests only: JSON role -> path")
    v = sub.add_parser("verify")
    v.add_argument("--freeze", default=str(K.repo_path(K.FREEZE_PATH)))
    v.add_argument("--sha256", required=True)
    v.add_argument("--input-paths")
    a = ap.parse_args(argv)
    overrides = json.loads(Path(a.input_paths).read_text()) if a.input_paths else None
    try:
        if a.cmd == "build":
            out = build(Path(a.out), resolve_inputs(overrides))
            print(f"freeze -> {out} sha256 {BG.sha256_file(out)}")
        else:
            got = verify(Path(a.freeze), a.sha256, input_overrides=overrides)
            print(f"freeze verified: {len(got['inputs'])} inputs")
    except (FreezeRefused, FileNotFoundError, FileExistsError) as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return K.RC_REFUSED
    return K.RC_OK


if __name__ == "__main__":
    raise SystemExit(main())
