"""Stage E harness freeze: the preflight every Stage E runner calls (Stage E.2b Task 6).

reports/stage_e2b_harness_freeze.json lists the sha256 and byte count of every harness file
Stage E's sessions run (rules/, sim/, screening/, funnel/, data/, the ML route pipeline,
compute/, the member template, the E.2a hashed tables, the V10 amendment, the two earlier
freeze manifests, pyproject.toml and uv.lock). ``preflight()`` refuses, naming every problem,
when the manifest is missing or any listed file is missing or differs by a single byte.

Every Stage E entry point (the cluster screening runner, the ML route's train and test jobs,
the Windows backend on both ends, the step 2 buy path) calls ``preflight(expected_sha256)``
before it reads any bar, with the manifest sha256 the session prompt states, taken on its
command line (``--harness-sha256``), and records the returned sha256 in every output it writes.
The manifest cannot hold its own hash, so a session that edited a file and rebuilt the manifest
still fails unless it also passes the new hash, which its prompt does not give (the D.1f review
F1 design). Any *.py file under a harness directory that the manifest does not list is refused
too (D.1f review F3), so an unlisted module cannot be imported into a run. There is no argument
or environment variable that skips the check; tests replace the function with monkeypatch.
"""
from __future__ import annotations

import hashlib
import importlib.machinery
import importlib.util
import json
import marshal
import struct
from pathlib import Path

from data.config import REPO_ROOT

MANIFEST_PATH = "reports/stage_e2b_harness_freeze.json"
HARNESS_DIRS = ("rules", "sim", "screening", "funnel", "data", "ml_route", "compute",
                "strategy/stage_e")
# Data, never code: purchased files, sealed stores, built bars and the release sourcers' fetch
# scripts are git-ignored and hashed by their own records (E.2a's tables, the holdout manifests,
# each run's input hashes, the release source files); neither listed nor scanned.
DATA_SUBDIRS = ("data/processed", "data/processed_step2", "data/vendor", "data/sealed")
# Cluster member code (review F-1): only the frozen, empty package init and per-cluster packages
# k1..k8 (hashed by each cluster's own freeze, screening/stage_e_freeze.py) may hold *.py here.
MEMBERS_DIR = "strategy/members"
MEMBERS_INIT = "strategy/members/__init__.py"
MEMBER_CLUSTER_DIRS = tuple(f"{MEMBERS_DIR}/k{i}/" for i in range(1, 9))


class HarnessFreezeError(RuntimeError):
    """The working tree is not the frozen Stage E harness."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def load_manifest(root: Path = REPO_ROOT) -> tuple[dict | None, str | None, list[str]]:
    """(manifest, its sha256, problems). A missing or unreadable manifest is a problem."""
    path = root / MANIFEST_PATH
    if not path.is_file():
        return None, None, [f"{MANIFEST_PATH} is missing"]
    raw = path.read_bytes()
    try:
        manifest = json.loads(raw)
    except json.JSONDecodeError as exc:
        return None, sha256_bytes(raw), [f"{MANIFEST_PATH} is not valid JSON: {exc}"]
    if not isinstance(manifest.get("files"), dict) or not manifest["files"]:
        return None, sha256_bytes(raw), [f"{MANIFEST_PATH} lists no files"]
    return manifest, sha256_bytes(raw), []


def _in_data_subdir(rel: str) -> bool:
    return any(rel == d or rel.startswith(d + "/") for d in DATA_SUBDIRS)


def unlisted_python_files(root: Path, listed: set[str]) -> list[str]:
    """Every *.py under a harness directory that the manifest does not list."""
    out: list[str] = []
    for directory in HARNESS_DIRS:
        base = root / Path(directory)
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*.py")):
            rel = path.relative_to(root).as_posix()
            if "__pycache__" not in path.parts and rel not in listed and not _in_data_subdir(rel):
                out.append(rel)
    return out


def unlisted_member_files(root: Path, listed: set[str]) -> list[str]:
    """Review F-1: any *.py under strategy/members/ other than the frozen package init and the
    per-cluster packages k1..k8 (which each cluster's freeze hashes)."""
    base = root / Path(MEMBERS_DIR)
    if not base.is_dir():
        return []
    out = []
    for path in sorted(base.rglob("*.py")):
        rel = path.relative_to(root).as_posix()
        if "__pycache__" in path.parts or rel in listed or rel.startswith(MEMBER_CLUSTER_DIRS):
            continue
        out.append(rel)
    return out


def _scan_roots(root: Path) -> list[Path]:
    return [root / Path(d) for d in (*HARNESS_DIRS, MEMBERS_DIR) if (root / Path(d)).is_dir()]


_BINARY_SUFFIXES = tuple(sorted(set(importlib.machinery.EXTENSION_SUFFIXES) | {".so", ".pyd"}))


def stray_binary_modules(root: Path, listed: set[str]) -> list[str]:
    """Review F-2 (1): an extension module or a .pyc outside __pycache__ shadows a listed source
    at import time; any such unlisted file under the harness directories is refused."""
    out = []
    for base in _scan_roots(root):
        for path in sorted(base.rglob("*")):
            rel = path.relative_to(root).as_posix()
            if not path.is_file() or rel in listed or _in_data_subdir(rel):
                continue
            loose_pyc = path.suffix == ".pyc" and "__pycache__" not in path.parts
            if loose_pyc or path.name.endswith(_BINARY_SUFFIXES):
                out.append(rel)
    return out


def _source_of(pyc: Path) -> Path:
    return pyc.parent.parent / (pyc.name.split(".", 1)[0] + ".py")


def bytecode_problems(root: Path) -> list[str]:
    """Review F-2 (2): a __pycache__ file this interpreter would load instead of compiling its
    source must hold exactly that source's code. Unchecked hash-based pycs are refused outright
    (Python never compares them with the source); a timestamp-based pyc whose recorded mtime
    and size match the source (so Python trusts it) must equal a fresh compile of the source.
    Stale pycs (mtime or size differ) and checked-hash pycs are recompiled or checked by Python
    itself and pass."""
    tag = importlib.util.cache_from_source("x.py").split("__pycache__")[-1].split(".")[1]
    out = []
    for base in _scan_roots(root):
        for pyc in sorted(base.rglob("__pycache__/*.pyc")):
            rel = pyc.relative_to(root).as_posix()
            src = _source_of(pyc)
            if _in_data_subdir(rel) or not src.is_file() or pyc.name.split(".")[1] != tag:
                continue
            data = pyc.read_bytes()
            if len(data) < 16:
                out.append(f"{rel}: truncated bytecode")
                continue
            flags, field_a, field_b = struct.unpack("<III", data[4:16])
            if flags & 0b01:
                if not flags & 0b10:
                    out.append(f"{rel}: unchecked hash-based bytecode (never compared with "
                               f"{src.relative_to(root).as_posix()})")
                continue
            stat = src.stat()
            if field_a != (int(stat.st_mtime) & 0xFFFFFFFF) or field_b != (stat.st_size & 0xFFFFFFFF):
                continue  # stale: Python recompiles from the source
            optimize = 2 if ".opt-2." in pyc.name else 1 if ".opt-1." in pyc.name else 0
            try:
                cached = marshal.loads(data[16:])
                fresh = compile(src.read_bytes(), str(src), "exec", dont_inherit=True,
                                optimize=optimize)
            except (ValueError, EOFError, TypeError, SyntaxError) as exc:
                out.append(f"{rel}: unreadable bytecode ({exc})")
                continue
            if cached != fresh:
                out.append(f"{rel}: bytecode differs from its source "
                           f"{src.relative_to(root).as_posix()}")
    return out


def check(root: Path = REPO_ROOT, expected_sha256: str | None = None
          ) -> tuple[list[str], str | None]:
    """(problems, manifest sha256). An empty list means every listed file matches, no harness
    *.py file is unlisted and, when given, the manifest's sha256 equals expected_sha256."""
    manifest, digest, problems = load_manifest(root)
    if expected_sha256 is not None and digest is not None and digest != expected_sha256:
        problems.append(f"{MANIFEST_PATH} sha256 {digest[:12]}... is not the expected "
                        f"{expected_sha256[:12]}...")
    if manifest is None:
        return problems, digest
    listed = set(manifest["files"])
    problems.extend(f"{rel}: not listed in the manifest"
                    for rel in unlisted_python_files(root, listed))
    problems.extend(f"{rel}: member code outside strategy/members/k1..k8 (review F-1)"
                    for rel in unlisted_member_files(root, listed))
    problems.extend(f"{rel}: unlisted binary module or loose bytecode (review F-2)"
                    for rel in stray_binary_modules(root, listed))
    problems.extend(bytecode_problems(root))
    for rel, info in sorted(manifest["files"].items()):
        path = root / Path(rel)
        if not path.is_file():
            problems.append(f"{rel}: missing")
            continue
        data = path.read_bytes()
        if len(data) != info["bytes"] or sha256_bytes(data) != info["sha256"]:
            problems.append(f"{rel}: sha256 {sha256_bytes(data)[:12]}... differs from the "
                            f"frozen {info['sha256'][:12]}...")
    return problems, digest


def preflight(expected_sha256: str, root: Path = REPO_ROOT) -> str:
    """The manifest's sha256 when it equals expected_sha256 and every listed file matches;
    HarnessFreezeError otherwise."""
    if len(expected_sha256) != 64 or any(c not in "0123456789abcdef" for c in expected_sha256):
        raise HarnessFreezeError(f"expected harness sha256 is not a sha256: {expected_sha256!r}")
    problems, digest = check(root, expected_sha256)
    if problems:
        shown = "; ".join(problems[:10])
        more = f" (and {len(problems) - 10} more)" if len(problems) > 10 else ""
        raise HarnessFreezeError(f"Stage E harness preflight refused: {shown}{more}")
    assert digest is not None
    return digest


# ------------------------------------------------------------------------------------------
# The builder (Stage E.2b Task 6, the lead). Run by the lead only:
#     uv run --no-sync python -m screening.harness_freeze build
#     uv run --no-sync python -m screening.harness_freeze verify --expected <sha256>
# ------------------------------------------------------------------------------------------
import argparse  # noqa: E402
import ast  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
from datetime import datetime  # noqa: E402
from zoneinfo import ZoneInfo  # noqa: E402

LOCAL_TZ = ZoneInfo("America/Vancouver")
# Every Stage E entry point; the repo-internal import closure of these is frozen too, so a
# module outside the harness directories that a run imports (strategy/interface.py, the pinned
# D.1 statistics) cannot change either.
ENTRY_MODULES = (
    "screening.stage_e_runner", "screening.stage_e_start_dates", "screening.build_release_calendar",
    "screening.stage_e_stats", "ml_route.train", "ml_route.test", "ml_route.probes",
    "compute.remote", "compute.agent", "data.pull_step2", "data.step2_store", "data.holdout",
    "data.trade_date_guard", "data.stage_e_bars", "strategy.research._d1f_statistics",
)
EARLIER_MANIFESTS = ("reports/stage_e1_freeze.json", "reports/stage_e2a_ml_freeze.json")
# Read-only inputs the harness reads at run time. Append-only logs and files later sessions
# write (docs/HOLDOUT_UNLOCK_LOG.md, docs/ACCESS.md, ledger/, per-product holdout-2 manifests,
# start-rule files, quote reports) are deliberately NOT listed: they change legitimately.
FROZEN_INPUTS = (
    "reports/stage_e2a_costs.json", "reports/stage_e2a_vehicle_sizes.json",
    "reports/stage_e2a_vehicles.json", "reports/stage_e2a_vehicle_rule_readings.md",
    "reports/stage_e2a_epsilon_declaration.md", "reports/stage_e2a_epsilon_declaration_addendum.md",
    "reports/stage_e2a_source_window_amendment.md", "reports/stage_e2a_epsilon.json",
    "reports/stage_e2a_price_limits.json", "reports/stage_e2a_funnel_phaseA.json",
    "reports/stage_e0_liquidity.json", "reports/stage_e0_symbology.json",
    "reports/stage_e1_purchase.json", "reports/stage_d1f_step5_start_rule.json",
    "reports/stage_d1f_release_sources.json", "reports/power_gate.json",
    "reports/walk_forward_folds.json", "docs/HOLDOUT_MANIFEST.json", "docs/HOLDOUT2_MANIFEST.json",
    "reports/stage_e2b_release_calendar.json", "reports/stage_e2b_release_sources_macro.json",
    "reports/stage_e2b_release_sources_commodity.json", "reports/stage_e2b_release_sources_named.json",
    "reports/stage_e2b_release_names.json", "reports/stage_e2b_ml_probes.json",
    "reports/stage_e2b_v10_amendment.md", "pyproject.toml", "uv.lock", MEMBERS_INIT,
)
FROZEN_INPUT_DIRS = ("reports/stage_e2a_funnel",)
# M7.8: "every M7 test" is hashed with the pipeline; the other Stage E tests travel with it.
TEST_PATTERNS = ("test_stage_e_*.py", "test_ml_route_*.py", "test_compute_*.py", "test_e2b_*.py",
                 "test_cross_platform_static.py", "test_build_release_calendar.py",
                 "test_leakage_canaries.py", "test_harness_freeze.py", "_stage_e_*.py",
                 "_compute_fixtures.py")


def harness_dir_files(root: Path) -> list[str]:
    """Every file (any extension) under the harness directories, data sub-directories and
    byte-code excluded."""
    out: list[str] = []
    for directory in HARNESS_DIRS:
        base = root / Path(directory)
        if not base.is_dir():
            continue
        for path in base.rglob("*"):
            rel = path.relative_to(root).as_posix()
            if (path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
                    and not _in_data_subdir(rel)):
                out.append(rel)
    return sorted(out)


def _module_file(root: Path, module: str) -> Path | None:
    base = root.joinpath(*module.split("."))
    for candidate in (base.with_suffix(".py"), base / "__init__.py"):
        if candidate.is_file():
            return candidate
    return None


def _imports(path: Path, module: str) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    package = module if path.name == "__init__.py" else module.rpartition(".")[0]
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                parts = package.split(".")
                base = ".".join(parts[: len(parts) - node.level + 1])
                target = f"{base}.{node.module}" if node.module else base
            else:
                target = node.module or ""
            found.add(target)
            found.update(f"{target}.{alias.name}" for alias in node.names)
    return found


def import_closure(root: Path, entries: tuple[str, ...] = ENTRY_MODULES) -> list[str]:
    """Repo files of the entry modules and everything they import inside the repo, packages'
    __init__ files included (function-level imports count)."""
    seen: dict[str, Path] = {}
    stack = list(entries)
    while stack:
        module = stack.pop()
        if not module or module in seen:
            continue
        path = _module_file(root, module)
        if path is None:
            continue
        seen[module] = path
        parts = module.split(".")
        stack.extend(".".join(parts[:i]) for i in range(1, len(parts)))
        stack.extend(_imports(path, module))
    return sorted(p.relative_to(root).as_posix() for p in seen.values())


def earlier_manifest_files(root: Path) -> list[str]:
    out: list[str] = []
    for rel in EARLIER_MANIFESTS:
        out.append(rel)
        out.extend(json.loads((root / rel).read_text(encoding="utf-8"))["files"])
    return out


def manifest_categories(root: Path) -> dict[str, str]:
    """rel path -> category, for every file the manifest freezes."""
    cats: dict[str, str] = {}
    for rel in earlier_manifest_files(root):
        cats.setdefault(rel, "earlier_freeze")
    for rel in FROZEN_INPUTS:
        cats.setdefault(rel, "frozen_input")
    for directory in FROZEN_INPUT_DIRS:
        for path in sorted((root / directory).rglob("*")):
            if path.is_file():
                cats.setdefault(path.relative_to(root).as_posix(), "frozen_input")
    for rel in import_closure(root):
        cats.setdefault(rel, "import_closure")
    for rel in harness_dir_files(root):
        cats[rel] = "harness_code"
    for pattern in TEST_PATTERNS:
        for path in sorted((root / "tests").glob(pattern)):
            cats.setdefault(path.relative_to(root).as_posix(), "stage_e_test")
    cats.pop(MANIFEST_PATH, None)
    return dict(sorted(cats.items()))


def build_manifest(root: Path = REPO_ROOT) -> dict:
    cats = manifest_categories(root)
    missing = [rel for rel in cats if not (root / Path(rel)).is_file()]
    if missing:
        raise HarnessFreezeError(f"refusing to freeze: listed files missing: {missing}")
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True,
                          text=True, check=True).stdout.strip()
    files = {}
    for rel in cats:
        data = (root / Path(rel)).read_bytes()
        files[rel] = {"sha256": sha256_bytes(data), "bytes": len(data)}
    return {
        "stage": "E.2b",
        "what": "Stage E harness freeze: every file Stage E's sessions run or read as frozen input",
        "created_pdt": datetime.now(LOCAL_TZ).isoformat(timespec="seconds"),
        "head_at_creation": head,
        "harness_dirs": list(HARNESS_DIRS),
        "entry_modules": list(ENTRY_MODULES),
        "categories": cats,
        "files": files,
        "notes": [
            "The manifest cannot hold its own sha256: every Stage E entry point takes it on its "
            "command line (--harness-sha256) and preflight() refuses unless it matches.",
            "The two earlier manifests' audit files are hashed at their current committed bytes "
            "(Parts appended after those freezes included); their freeze-commit blobs are "
            "checked by the start and end checks, not here.",
            "Not frozen, by design: append-only logs and files later sessions write "
            "(docs/HOLDOUT_UNLOCK_LOG.md, docs/ACCESS.md, ledger/, per-product holdout-2 "
            "manifests, reports/stage_e_start_rule_*.json, quote reports), and data files under "
            + ", ".join(DATA_SUBDIRS) + ".",
            "A spend-policy change in data/config.py (a purchase session's session id and caps) "
            "changes a frozen file: that session writes a new manifest whose only difference is "
            "data/config.py's entry, shows the diff, and passes the new sha256 on its commands.",
        ],
    }


def write_manifest(manifest: dict, root: Path = REPO_ROOT) -> str:
    raw = (json.dumps(manifest, indent=1, sort_keys=False) + "\n").encode("utf-8")
    (root / MANIFEST_PATH).write_bytes(raw)
    return sha256_bytes(raw)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m screening.harness_freeze")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("build", help="write reports/stage_e2b_harness_freeze.json (lead only)")
    verify = sub.add_parser("verify", help="run the preflight against an expected sha256")
    verify.add_argument("--expected", required=True)
    args = parser.parse_args(argv)
    if args.command == "build":
        digest = write_manifest(build_manifest())
        manifest = json.loads((REPO_ROOT / MANIFEST_PATH).read_text(encoding="utf-8"))
        counts: dict[str, int] = {}
        for cat in manifest["categories"].values():
            counts[cat] = counts.get(cat, 0) + 1
        print(f"wrote {MANIFEST_PATH}: {len(manifest['files'])} files {counts}")
        print(f"sha256 {digest}")
        return 0
    try:
        print(f"preflight OK: {preflight(args.expected)}")
        return 0
    except HarnessFreezeError as exc:
        print(str(exc))
        return 1


if __name__ == "__main__":
    sys.exit(main())
