"""The search freeze manifest reports/stage_e20_search_freeze.json (schema
"stage_e20_search_freeze/1"; reports/stage_e20_plan.md section 11): the plan, every
pattern_search file, every pattern_search test and helper, and every input the search reads,
each with path, sha256 and bytes. The lead builds it once, after the plan's section 10.1 is filled
and the Step 6 dry check has passed, and before the 45 registrations:

    uv run python -m pattern_search.freeze_manifest build
    uv run python -m pattern_search.freeze_manifest verify --sha256 <sha of the file>

Inputs listed: E.12's S_X record, the E.17 store manifest, the 17 step 2 stores (hashed, and each
must equal the E.17 manifest's sha256), their reports/step2 summaries (the degraded-day record),
the release calendar, the four frozen E.2a tables, the group calendar modules, the v2 freeze
manifest, the harness manifest, and every ml_route_v2 module the search imports. A build refuses
when the file already exists (a freeze is written once; the lead deletes it to rebuild before
any registration).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections.abc import Sequence
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from pattern_search import constants as K
from pattern_search import preflight as pf

HARNESS_MANIFEST_REL = "reports/stage_e2b_harness_freeze.json"
V2_MODULES = (  # every ml_route_v2 module the search runs (imported before listing)
    "ml_route_v2.account", "ml_route_v2.clock", "ml_route_v2.configs", "ml_route_v2.constants",
    "ml_route_v2.cost_filter", "ml_route_v2.cpcv", "ml_route_v2.decide",
    "ml_route_v2.fingerprint", "ml_route_v2.models", "ml_route_v2.normalize",
    "ml_route_v2.panel", "ml_route_v2.phase1.freeze", "ml_route_v2.phase1.world",
    "ml_route_v2.pipeline", "ml_route_v2.portfolio", "ml_route_v2.selection_metric",
    "ml_route_v2.signals", "ml_route_v2.synthetic", "ml_route_v2.targets",
)


def import_dependencies() -> None:
    import importlib

    for name in V2_MODULES:
        importlib.import_module(name)


def loaded_v2_files() -> list[Path]:
    v2 = (pf.repo_root() / "ml_route_v2").resolve()
    out = set()
    for mod in list(sys.modules.values()):
        f = getattr(mod, "__file__", None)
        if f and Path(f).resolve().is_relative_to(v2):
            out.add(Path(f).resolve())
    return sorted(out)


def code_files() -> list[Path]:
    return sorted((pf.repo_root() / K.CODE_PACKAGE).glob("*.py"))


def test_files() -> list[Path]:
    root = pf.repo_root()
    return sorted((root / "tests").glob(K.TEST_GLOB)) + [root / p for p in K.TEST_HELPERS]


def input_files() -> list[Path]:
    root = pf.repo_root()
    rels = [K.S_X_SOURCE_REL, K.STORE_MANIFEST_REL, K.RELEASE_CALENDAR_REL, *K.FROZEN_TABLES_REL,
            K.V2_FREEZE_REL, HARNESS_MANIFEST_REL,
            *(f"{K.STEP2_SUMMARIES_REL}/bars_{r}.json" for r in K.PATH_ROOTS)]
    calendars = sorted((root / "data" / "calendars").glob("*.py"))
    return [root / r for r in rels] + calendars


def store_files(step2_root: Path | None = None) -> list[Path]:
    from pattern_search import guard

    return [guard.step2_store_path(r, step2_root) for r in K.PATH_ROOTS]


def required_files(*, with_stores: bool = True) -> list[Path]:
    """Every file the manifest must list (module docstring)."""
    import_dependencies()
    files = [pf.repo_path(K.PLAN_REL), *code_files(), *test_files(), *input_files(),
             *loaded_v2_files()]
    if with_stores:
        files += store_files()
    seen: dict[str, Path] = {}
    for p in files:
        seen.setdefault(str(Path(p).resolve()), Path(p))
    return list(seen.values())


def entry(path: Path, sha256: str | None = None) -> dict[str, Any]:
    p = Path(path)
    return {"path": pf.rel(p), "sha256": sha256 or pf.guarded_sha256(p),
            "bytes": p.stat().st_size}


def body(files: Sequence[Path], store_sha256: dict[str, str] | None = None,
         **extra: Any) -> dict[str, Any]:
    """The manifest over ``files``; a store's hash must equal ``store_sha256`` when given."""
    entries = []
    stores = {str(Path(p).resolve()): r for r, p in zip(K.PATH_ROOTS, store_files(),
                                                         strict=True)}
    for p in files:
        e = entry(p)
        root = stores.get(str(Path(p).resolve()))
        if root is not None and store_sha256 is not None and e["sha256"] != store_sha256[root]:
            raise pf.Refused(f"the {root} store hashes to {e['sha256'][:12]}..., not the E.17 "
                             f"manifest's {store_sha256[root][:12]}...")
        entries.append(e)
    now = datetime.now(ZoneInfo("America/Vancouver")).isoformat(timespec="seconds")
    return {"schema": K.FREEZE_SCHEMA, "created_pdt": now, **extra, "files": entries}


def write_once(path: Path, doc: dict[str, Any]) -> str:
    """Write the manifest with O_EXCL (refused when it exists); return its sha256."""
    raw = (json.dumps(doc, indent=1, sort_keys=False) + "\n").encode()
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o444)
    except FileExistsError as exc:
        raise pf.Refused(f"{path} exists: a freeze is written once") from exc
    with os.fdopen(fd, "wb") as fh:
        fh.write(raw)
    return pf.sha256_file(path)


def build(path: Path | None = None) -> str:
    from pattern_search.world import store_records

    path = Path(path) if path is not None else pf.repo_path(K.FREEZE_MANIFEST_REL)
    recs = store_records()
    doc = body(required_files(), {r: recs[r]["store_sha256"] for r in K.PATH_ROOTS},
               plan=K.PLAN_REL, registry_label=K.REGISTRY_LABEL,
               registry_ids=list(K.CONFIG_IDS), config_ids=K.config_ids(),
               feature_names=list(K.FEATURE_NAMES))
    return write_once(path, doc)


def verify(path: Path, sha256: str) -> dict[str, Any]:
    return pf.check_freeze(path, sha256, required_files())


def main(argv: Sequence[str] | None = None) -> int:
    from pattern_search import guard

    guard.install_audit_hook()
    parser = argparse.ArgumentParser(prog="python -m pattern_search.freeze_manifest")
    parser.add_argument("command", choices=("build", "verify"))
    parser.add_argument("--sha256")
    args = parser.parse_args(argv)
    path = pf.repo_path(K.FREEZE_MANIFEST_REL)
    try:
        if args.command == "build":
            print(f"wrote {pf.rel(path)}: sha256 {build(path)}")
        else:
            if not args.sha256:
                raise pf.Refused("verify needs --sha256")
            rec = verify(path, args.sha256)
            print(f"verified {rec['path']}: {rec['files']} files")
    except (pf.Refused, guard.GuardRefusal) as exc:
        print(f"REFUSED ({type(exc).__name__}): {exc}", file=sys.stderr)
        return K.RC_REFUSED
    return K.RC_OK


if __name__ == "__main__":
    sys.exit(main())


__all__ = ["build", "body", "code_files", "entry", "import_dependencies", "input_files",
           "loaded_v2_files", "main", "required_files", "store_files", "test_files", "verify",
           "write_once"]
