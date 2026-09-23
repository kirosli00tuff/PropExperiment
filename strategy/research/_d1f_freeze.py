"""Stage D.1f step 1b: the harness-freeze manifest (reports/stage_d1f_confirmation_list.md 1.5
step 1b, R-4, NEW-1, NEW-4, NEW-5). Small and re-runnable; the lead runs it, prints its sha256
into the STATE file, and asks the user to commit the manifest before any quote or purchase.

    uv run python -m strategy.research._d1f_freeze

Writes reports/stage_d1f_harness_freeze.json: the sha256 of every file
- under screening/, sim/ (incl. sim/slippage_calibration.json), funnel/ and rules/;
- every *.py under strategy/, data/, screening/, sim/, funnel/ and rules/ (review F3; the
  preflight refuses any such file the manifest does not list), which includes data/*.py,
  strategy/interface.py, strategy/research/__init__.py, strategy/research/h_daily_bar/*,
  strategy/research/_d1f_*.py and strategy/research/e_calendar_event/_release_table_2019_2024.py;
- docs/HOLDOUT_MANIFEST.json (review N6: it anchors the research parquet's sha256);
- listed in the list's section 0 (incl. reports/power_gate.json and the two E-H modules at
  their CURRENT, amended hashes, which ``declared_amendments`` records beside the section-0
  pre-amendment ones);
- reports/stage_d1e_declaration_hashes.json, docs/NULL_CRITERIA.md and the list itself;
- LEAD RULING (conservative): the repo-internal transitive import closure of
  strategy/research/_d1f_confirmation.py, plus pyproject.toml and uv.lock (a library version
  change can alter a result);
- the recorded facts files the runner reads for Tier B's s (runner inputs).
``__pycache__`` and ``*.pyc`` are excluded. Paths are sorted. The manifest cannot hold its own
sha256: the runner computes it, records it in every output JSON and refuses unless it equals
the value given on its command line (review F1). The script refuses to write a manifest whose
E-H modules differ from the declared post-amendment literals of ``_d1f_preflight``.
"""

from __future__ import annotations

import ast
import json
import sys
from collections.abc import Iterable
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from data.cme_calendar import entries_2025_2026_block
from data.config import REPO_ROOT
from strategy.research._d1f_preflight import (
    CME_ANCHOR_COMMIT,
    CME_CALENDAR,
    CRITERIA_PATH,
    DECLARATION_HASHES_PATH,
    EH_AMENDED,
    LIST_PATH,
    MANIFEST_PATH,
    eh_amendment_problems,
    parse_section0,
    python_files_under,
    sha256_bytes,
    sha256_file,
)

LOCAL_TZ = ZoneInfo("America/Vancouver")
HARNESS_DIRS = ("screening", "sim", "funnel", "rules")
RUNNER = "strategy/research/_d1f_confirmation.py"
SINGLE_FILES = ("strategy/interface.py",
                "strategy/research/e_calendar_event/_release_table_2019_2024.py",
                DECLARATION_HASHES_PATH, CRITERIA_PATH, LIST_PATH, "pyproject.toml", "uv.lock",
                "docs/HOLDOUT_MANIFEST.json")
RUNNER_INPUTS = ("reports/stage_d1b_family_f_facts.json", "reports/stage_d1d_family_g_facts.json")
EXCLUDED_TOP_LEVEL = ("tests",)


def _is_cache(path: Path) -> bool:
    return "__pycache__" in path.parts or path.suffix == ".pyc"


def _files_under(root: Path, rel_dir: str, pattern: str = "*", recursive: bool = True
                 ) -> set[str]:
    base = root / rel_dir
    found = base.rglob(pattern) if recursive else base.glob(pattern)
    return {p.relative_to(root).as_posix() for p in found if p.is_file() and not _is_cache(p)}


def _module_file(root: Path, dotted: str) -> Path | None:
    parts = dotted.split(".")
    for candidate in (root.joinpath(*parts).with_suffix(".py"),
                      root.joinpath(*parts, "__init__.py")):
        if candidate.is_file():
            return candidate
    return None


def _with_packages(root: Path, dotted: str) -> list[Path]:
    """The module's file and every enclosing package's __init__.py (all run on import)."""
    parts = dotted.split(".")
    out = [p for i in range(1, len(parts)) if (p := root.joinpath(*parts[:i], "__init__.py"))
           .is_file()]
    module = _module_file(root, dotted)
    return [*out, module] if module is not None else out


def _internal(root: Path, dotted: str) -> bool:
    top = dotted.split(".")[0]
    return top not in EXCLUDED_TOP_LEVEL and (
        (root / top / "__init__.py").is_file() or (root / f"{top}.py").is_file())


def _imports_of(root: Path, path: Path) -> set[str]:
    """Dotted names a module imports anywhere in its body (lazy imports included)."""
    tree = ast.parse(path.read_text(), filename=str(path))
    package = ".".join(path.relative_to(root).with_suffix("").parts)
    if path.name != "__init__.py":
        package = package.rpartition(".")[0]
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            base = node.module or ""
            if node.level:
                anchor = package.split(".")[:len(package.split(".")) - node.level + 1]
                base = ".".join([*anchor, base] if base else anchor)
            names.add(base)
            names.update(f"{base}.{alias.name}" for alias in node.names)
    return {n for n in names if n}


def import_closure(root: Path, entries: Iterable[str]) -> set[str]:
    """Repo-internal files reached by importing ``entries`` (repo-relative paths)."""
    todo = [root / e for e in entries]
    seen: set[Path] = set()
    while todo:
        path = todo.pop()
        if path in seen:
            continue
        seen.add(path)
        for dotted in _imports_of(root, path):
            if _internal(root, dotted):
                todo.extend(p for p in _with_packages(root, dotted) if p not in seen)
    return {p.relative_to(root).as_posix() for p in seen}


def file_sets(root: Path) -> dict[str, set[str]]:
    """Which rule brings in which files (a file may come from several)."""
    section0 = parse_section0((root / LIST_PATH).read_text())
    return {
        "harness_dirs": set().union(*(_files_under(root, d) for d in HARNESS_DIRS)),
        "data_py": _files_under(root, "data", "*.py", recursive=False),
        "h_daily_bar": _files_under(root, "strategy/research/h_daily_bar"),
        "d1f_modules": _files_under(root, "strategy/research", "_d1f_*.py", recursive=False),
        "pinned_py_dirs": python_files_under(root),
        "single_files": set(SINGLE_FILES),
        "section_0": {e.path for e in section0},
        "import_closure": import_closure(root, [RUNNER]),
        "runner_inputs": set(RUNNER_INPUTS),
    }


def build_manifest(root: Path = REPO_ROOT, now: datetime | None = None) -> dict:
    sets = file_sets(root)
    paths = sorted(set().union(*sets.values()))
    missing = [p for p in paths if not (root / p).is_file()]
    if missing:
        raise FileNotFoundError(f"files to freeze are missing: {missing}")
    files = {p: sha256_file(root / p) for p in paths}
    section0 = {e.path: e.sha256 for e in parse_section0((root / LIST_PATH).read_text())}
    amended = eh_amendment_problems(files, {p: {"post_amendment_sha256": files.get(p)}
                                            for p in EH_AMENDED})
    if amended:
        raise ValueError(f"refusing to freeze: {amended}")
    stamp = (now or datetime.now(LOCAL_TZ)).astimezone(LOCAL_TZ)
    return {
        "stage": "D.1f harness freeze (list 1.5 step 1b, R-4)",
        "generated_local": stamp.isoformat(timespec="seconds"),
        "timezone": "America/Vancouver",
        "note": "this manifest's own sha256 cannot be held in it: "
                "strategy/research/_d1f_confirmation.py computes it at run time and records it "
                "in every output JSON; the user's git commit of this file is the anchor",
        "file_count": len(files),
        "files": files,
        "sources": {k: sorted(v) for k, v in sets.items()},
        "declared_amendments": {
            p: {"pre_amendment_sha256": section0[p], "post_amendment_sha256": files[p],
                "amendment": "list 5.7 (N-1), NEW-1: a release_table argument defaulting to the "
                             "existing table; recorded in reports/stage_d1f_build_STATE.md"}
            for p in EH_AMENDED},
        "cme_calendar": {
            "section_0_sha256_at_commit": section0[CME_CALENDAR],
            "anchor_commit": CME_ANCHOR_COMMIT, "current_sha256": files[CME_CALENDAR],
            "entries_2025_2026_block_sha256": sha256_bytes(
                entries_2025_2026_block((root / CME_CALENDAR).read_text()).encode()),
            "rule": "section 0 pins the 2025-2026 entries only; the runner compares them with "
                    "the file at the anchor commit (lead ruling)"},
    }


def write_manifest(root: Path = REPO_ROOT, out: Path | None = None) -> str:
    """Write the manifest; return its sha256."""
    target = out or root / MANIFEST_PATH
    blob = (json.dumps(build_manifest(root), indent=1, sort_keys=True) + "\n").encode()
    target.write_bytes(blob)
    return sha256_bytes(blob)


def main(argv: list[str] | None = None) -> int:
    del argv
    digest = write_manifest()
    manifest = json.loads((REPO_ROOT / MANIFEST_PATH).read_text())
    print(f"wrote {MANIFEST_PATH}: {manifest['file_count']} files, "
          f"generated {manifest['generated_local']}")
    print(f"sha256 {digest}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
