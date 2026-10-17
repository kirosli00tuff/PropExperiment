"""The E.23 freeze manifest (lead_spec section 8), modelled on multiday.freeze_manifest: every
trigger_hold/*.py, every tests/test_trigger_hold_*.py, the reused code (multiday/*.py,
multiday/README.md, base_rules/*.py, screening/trial_registry.py, screening/stage_e_verdict.py),
the lead's spec, the pre-registration, the registration config, the power table, the E.21
freeze, every input of base_rules' E.16 roles and the E.17 run manifest, every events file the
config names and every per-root trend file, each with its sha256 and size; schema
"stage_e23_freeze/1".

    uv run python -m trigger_hold.freeze_manifest build [--out reports/stage_e23_freeze.json]
    uv run python -m trigger_hold.freeze_manifest verify [--freeze ...] --sha256 <sha>

``build`` refuses to overwrite (O_EXCL); ``--input-paths`` (tests only) names other paths per
role. ``verify`` re-checks every listed file.
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
from multiday import freeze_manifest as MFM
from trigger_hold import constants as K
from trigger_hold.config import load_config


def input_roles() -> dict[str, Path]:
    return {**{r: Path(p) for r, p in BG.INPUT_ROLES.items()},
            "run_manifest": K.RUN_MANIFEST_PATH, "e21_freeze": K.E21_FREEZE_PATH,
            "spec": K.SPEC_PATH, "prereg": K.PREREG_PATH, "config": K.CONFIG_PATH,
            "power": K.POWER_PATH}


def resolve_inputs(overrides: Mapping[str, Any] | None = None) -> dict[str, Path]:
    return {r: K.repo_path((overrides or {}).get(r, p)) for r, p in input_roles().items()}


def code_files() -> list[Path]:
    return sorted(K.CODE_DIR.glob("*.py"))


def test_files(repo: Path = REPO_ROOT) -> list[Path]:
    return sorted(Path(repo).glob(K.TEST_GLOB))


def reused_files() -> list[Path]:
    return [*MFM.code_files(), *MFM.base_rules_files(), *MFM.pinned_files(),
            REPO_ROOT / "screening" / "stage_e_verdict.py"]


def data_files(config_path: Path, trend_dir: Path = K.TREND_DIR) -> list[Path]:
    """Every events file of the config and every root's trend file."""
    cfg = load_config(config_path)
    return [*(K.repo_path(p) for p in cfg.event_paths()),
            *(K.repo_path(Path(trend_dir) / f"{r}.json") for r in K.ROOTS)]


def manifest_body(inputs: Mapping[str, Path], trend_dir: Path = K.TREND_DIR) -> dict[str, Any]:
    files = [*code_files(), *test_files(), *reused_files(), *inputs.values(),
             *data_files(inputs["config"], trend_dir)]
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
    cfg = load_config(inputs["config"])
    now = datetime.now(ZoneInfo("America/Vancouver")).isoformat(timespec="seconds")
    return {"schema": K.FREEZE_SCHEMA, "created_local": now, "registry_test": K.REGISTRY_TEST,
            "test_ids": cfg.ids, "trend_dir": BG.rel(K.repo_path(trend_dir)),
            "inputs": {r: BG.rel(p) for r, p in inputs.items()}, "files": rows}


def build(out: Path, inputs: Mapping[str, Path], trend_dir: Path = K.TREND_DIR) -> Path:
    body = json.dumps(manifest_body(inputs, trend_dir), indent=1).encode()
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
    """Every listed file (sha256, size); every trigger_hold/*.py, test, reused file, input role,
    events file of the config and trend file listed. Returns {"inputs": {role: {"path",
    "sha256"}}, "test_ids", "trend_dir"}."""
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
    unlisted = [BG.rel(p) for p in (*code_files(), *test_files(), *reused_files())
                if str(p.resolve()) not in listed]
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
    trend_dir = Path(body.get("trend_dir") or K.TREND_DIR)
    missing = [BG.rel(p) for p in data_files(Path(inputs["config"]["path"]), trend_dir)
               if str(Path(p).resolve()) not in listed]
    if missing:
        raise FreezeRefused(f"events or trend files not in the freeze: {missing[:5]}")
    return {"inputs": inputs, "test_ids": list(body.get("test_ids") or []),
            "trend_dir": str(K.repo_path(trend_dir))}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="trigger_hold.freeze_manifest")
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
            print(f"freeze verified: {len(got['inputs'])} inputs, {len(got['test_ids'])} ids")
    except (FreezeRefused, FileNotFoundError, FileExistsError, ValueError) as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return K.RC_REFUSED
    return K.RC_OK


if __name__ == "__main__":
    raise SystemExit(main())
