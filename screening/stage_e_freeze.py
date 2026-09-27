"""Per-cluster member code freeze (Stage E.2b Task 1; the D.1f freeze discipline per cluster).

A cluster's screening session writes its members' modules, then, BEFORE it runs any of them,
calls ``write_cluster_freeze``: every *.py file under ``strategy/members/<k#>/`` is hashed into
``reports/stage_e_<k#>_member_freeze.json`` (written once, read-only, never overwritten), with the
member declarations (label, ordinal, module, factory name, legs). The runner then refuses:
- a cluster with no freeze file;
- any *.py under the cluster's member directory that the freeze does not list, or whose bytes
  differ from the frozen hash, or a listed file that is missing;
- a member label the freeze does not declare, a factory that is not the declared module
  attribute, or legs other than the declared ones.
Every output record carries the freeze file's sha256.

Member modules live under ``strategy/members/`` and never under ``strategy/stage_e/``: that
directory is harness code frozen by reports/stage_e2b_harness_freeze.json, whose preflight refuses
any unlisted *.py file there.

Review finding F-1 (lead ruling, Task 8): code that runs on import but is hashed by nothing could
patch the harness while every hash verifies. So:
- ``strategy/members/__init__.py`` (provided by the lead, empty, frozen in the harness manifest)
  must exist and be EMPTY (0 bytes); it is hashed into every cluster freeze as well.
- Every *.py file of the cluster directory (members, helpers, the cluster's __init__.py) passes a
  static check (``check_member_source``, Python's ast; nothing is executed) when the freeze is
  written, when it is verified and before a member is imported. It refuses, naming the file, the
  line and the rule:
  - ``import_not_allowed``: an import outside ``ALLOWED_IMPORTS`` and the member's own cluster
    package (a relative import may not leave the cluster package);
  - ``star_import``: ``from x import *``;
  - ``banned_name``: naming open, exec, eval, compile, __import__, globals, setattr, delattr,
    importlib, os, sys, pathlib, subprocess or builtins (as a name, an attribute or an import
    alias), and, added here, getattr, vars, locals, __builtins__, breakpoint and input (they reach
    the same objects by a constructed string);
  - ``dunder_attribute``: any ``x.__name__``-style attribute other than __init__, __post_init__,
    __name__ and __doc__ (``().__class__.__subclasses__()`` and ``f.__globals__`` escapes);
  - ``assigns_imported``: assigning to, augmenting or deleting an attribute or item reached from an
    imported name (``products.PRODUCTS = ...``, ``PRODUCTS["ZN"] = ...``);
  - ``mutating_call_on_imported``: calling a mutating method (update, pop, clear, setdefault,
    cache_clear, ...) on an object imported from rules, screening or strategy;
  - ``file_io``: file readers and writers reachable from the allowed modules (numpy's load, save,
    loadtxt, fromfile, tofile, memmap, lib, ctypeslib; a Path's read_text, write_bytes, ...).
  The last four and the added names go beyond the ruling's list; each closes a route the ruling's
  forms leave open, and the lead may drop any of them.
- Before a member module is imported, the source file of ``strategy.members``, of the cluster
  package and of the module itself is located without executing anything and must be the file
  that was checked (``importable_origins``).
"""

from __future__ import annotations

import ast
import hashlib
import importlib
import importlib.machinery
import json
import os
import re
import sys
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from data.config import REPO_ROOT
from strategy.stage_e.interface import LegSpec

MEMBERS_ROOT = Path("strategy") / "members"
MEMBERS_INIT = MEMBERS_ROOT / "__init__.py"
CLUSTER_PATTERN = re.compile(r"^K[1-8]$")
FREEZE_SCHEMA = "stage_e_member_freeze/1"
# F-1 (b): the only modules a member file may import (exactly these, plus its own cluster package)
ALLOWED_IMPORTS = frozenset({
    "__future__", "datetime", "math", "decimal", "zoneinfo", "dataclasses", "typing",
    "collections", "collections.abc", "enum", "functools", "itertools", "statistics", "numpy",
    "rules.products", "rules.xfa_rules", "screening.stage_e_frozen", "strategy.stage_e.interface",
})
BANNED_NAMES = frozenset({
    "open", "exec", "eval", "compile", "__import__", "globals", "setattr", "delattr",
    "importlib", "os", "sys", "pathlib", "subprocess", "builtins",
    # added (see the module docstring): the same objects by a constructed string
    "getattr", "vars", "locals", "__builtins__", "breakpoint", "input",
})
ALLOWED_DUNDERS = frozenset({"__init__", "__post_init__", "__name__", "__doc__"})
MUTATING_METHODS = frozenset({
    "update", "pop", "popitem", "clear", "setdefault", "append", "extend", "insert", "remove",
    "add", "discard", "sort", "reverse", "cache_clear", "__setitem__", "__delitem__",
})
HARNESS_PACKAGES = ("rules", "screening", "strategy")
FILE_IO_ATTRIBUTES = frozenset({
    "load", "save", "savez", "savez_compressed", "loadtxt", "savetxt", "genfromtxt", "fromfile",
    "fromregex", "tofile", "memmap", "lib", "ctypeslib", "DataSource",
    "read_text", "read_bytes", "write_text", "write_bytes", "unlink", "rmdir", "mkdir", "touch",
    "chmod", "symlink_to", "hardlink_to", "iterdir", "glob", "rglob",
})
NON_SOURCE_SUFFIXES = (".pyc", ".pyo", ".so", ".pyd")


class ClusterFreezeError(RuntimeError):
    """The cluster's member code is not the frozen code, or the freeze cannot be written."""


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def check_cluster(cluster: str) -> str:
    if not isinstance(cluster, str) or not CLUSTER_PATTERN.match(cluster):
        raise ClusterFreezeError(f"cluster {cluster!r} is not one of K1..K8")
    return cluster


def members_dir(cluster: str) -> Path:
    return MEMBERS_ROOT / check_cluster(cluster).lower()


def freeze_path(cluster: str) -> Path:
    return Path("reports") / f"stage_e_{check_cluster(cluster).lower()}_member_freeze.json"


def module_prefix(cluster: str) -> str:
    return ".".join(members_dir(cluster).parts)


@dataclass(frozen=True)
class MemberDecl:
    label: str
    ordinal: int  # the member's ordinal in the cluster list (power-check seed, NULL_CRITERIA_E 3)
    module: str  # dotted module path under strategy.members.<k#>
    factory: str  # the module attribute returning a fresh member
    legs: tuple[LegSpec, ...]

    def as_dict(self) -> dict:
        return {"label": self.label, "ordinal": self.ordinal, "module": self.module,
                "factory": self.factory,
                "legs": [{"root": leg.root, "traded": leg.traded} for leg in self.legs]}


@dataclass(frozen=True)
class ClusterFreeze:
    cluster: str
    sha256: str
    files: dict[str, dict]
    members: tuple[MemberDecl, ...]
    root: Path = REPO_ROOT  # the repository the freeze was loaded from (its code is checked there)

    def member(self, label: str) -> MemberDecl:
        for m in self.members:
            if m.label == label:
                return m
        raise ClusterFreezeError(f"{self.cluster}: member {label!r} is not in the freeze")


def check_members_init(root: Path) -> dict:
    """F-1 (a): strategy/members/__init__.py exists and is empty. Returns its hash record."""
    path = Path(root) / MEMBERS_INIT
    if not path.is_file():
        raise ClusterFreezeError(f"{MEMBERS_INIT.as_posix()} does not exist (the lead provides it "
                                 "empty and frozen)")
    data = path.read_bytes()
    if data:
        raise ClusterFreezeError(f"{MEMBERS_INIT.as_posix()} must be empty (0 bytes), it has "
                                 f"{len(data)}: code there would run on every screening run")
    return {"sha256": _sha(data), "bytes": 0}


def _cluster_files(cluster: str, root: Path) -> dict[str, dict]:
    """The hash records of strategy/members/__init__.py and every *.py of the cluster directory;
    an importable non-source file (*.pyc, *.so, ...) outside __pycache__ is refused."""
    base = root / members_dir(cluster)
    if not base.is_dir():
        raise ClusterFreezeError(f"{members_dir(cluster).as_posix()} does not exist")
    out: dict[str, dict] = {MEMBERS_INIT.as_posix(): check_members_init(root)}
    for path in sorted(base.rglob("*")):
        if "__pycache__" in path.parts or not path.is_file():
            continue
        if path.suffix in NON_SOURCE_SUFFIXES:
            raise ClusterFreezeError(f"{path.relative_to(root).as_posix()}: an importable "
                                     "non-source file in a member directory")
        if path.suffix != ".py":
            continue
        data = path.read_bytes()
        out[path.relative_to(root).as_posix()] = {"sha256": _sha(data), "bytes": len(data)}
    return out


# ----------------------------------------------------------- static check ----
def _import_allowed(name: str, cluster_pkg: str) -> bool:
    return name in ALLOWED_IMPORTS or name == cluster_pkg or name.startswith(cluster_pkg + ".")


def _resolve_relative(rel: str, level: int, module: str | None) -> str:
    """The absolute module a relative import in file ``rel`` names."""
    parts = list(Path(rel).with_suffix("").parts)
    package = parts if parts[-1] == "__init__" else parts[:-1]
    if package and package[-1] == "__init__":
        package = package[:-1]
    base = package[: len(package) - (level - 1)] if level > 1 else package
    return ".".join([*base, *(module.split(".") if module else [])])


def _root_name(node: ast.expr) -> str | None:
    while isinstance(node, ast.Attribute | ast.Subscript):
        node = node.value
    return node.id if isinstance(node, ast.Name) else None


def check_member_source(rel: str, source: str, cluster: str) -> list[str]:
    """F-1 (b): every refusal of one member file, as "file:line: rule: detail"."""
    cluster_pkg = module_prefix(cluster)
    try:
        tree = ast.parse(source, filename=rel)
    except SyntaxError as exc:
        return [f"{rel}:{exc.lineno}: syntax_error: {exc.msg}"]
    problems: list[str] = []
    imported: dict[str, str] = {}  # local name -> the module it came from

    def refuse(node: ast.AST, rule: str, detail: str) -> None:
        problems.append(f"{rel}:{getattr(node, 'lineno', 0)}: {rule}: {detail}")

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if not _import_allowed(alias.name, cluster_pkg):
                    refuse(node, "import_not_allowed", f"import {alias.name}")
                imported[alias.asname or alias.name.split(".")[0]] = alias.name
        elif isinstance(node, ast.ImportFrom):
            mod = (_resolve_relative(rel, node.level, node.module) if node.level
                   else node.module or "")
            for alias in node.names:
                if alias.name == "*":
                    refuse(node, "star_import", f"from {mod} import *")
                    continue
                full = f"{mod}.{alias.name}"
                if not (_import_allowed(mod, cluster_pkg) or _import_allowed(full, cluster_pkg)):
                    refuse(node, "import_not_allowed", f"from {mod} import {alias.name}")
                if alias.name in BANNED_NAMES or (alias.asname or "") in BANNED_NAMES:
                    refuse(node, "banned_name", f"import of {alias.name}")
                imported[alias.asname or alias.name] = mod
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id in BANNED_NAMES:
            refuse(node, "banned_name", node.id)
        elif isinstance(node, ast.Attribute):
            if node.attr in BANNED_NAMES:
                refuse(node, "banned_name", f".{node.attr}")
            elif (node.attr.startswith("__") and node.attr.endswith("__")
                  and node.attr not in ALLOWED_DUNDERS):
                refuse(node, "dunder_attribute", f".{node.attr}")
            elif node.attr in FILE_IO_ATTRIBUTES:
                refuse(node, "file_io", f".{node.attr}")
        if isinstance(node, ast.Assign | ast.AugAssign | ast.AnnAssign | ast.Delete):
            targets = (node.targets if isinstance(node, ast.Assign | ast.Delete)
                       else [node.target])
            for target in targets:
                for sub in ast.walk(target):
                    base = (_root_name(sub) if isinstance(sub, ast.Attribute | ast.Subscript)
                            else None)
                    if base in imported:
                        refuse(node, "assigns_imported", f"{base} (imported from "
                               f"{imported[base]})")
                        break
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            base = _root_name(node.func)
            origin = imported.get(base or "", "")
            if node.func.attr in MUTATING_METHODS and origin.split(".")[0] in HARNESS_PACKAGES:
                refuse(node, "mutating_call_on_imported", f"{base}...{node.func.attr}() "
                       f"(imported from {origin})")
    return sorted(set(problems), key=lambda p: (int(p.split(":")[1]), p))


def check_cluster_sources(cluster: str, root: Path) -> None:
    """The static check on every *.py file of the cluster directory; refuses on any problem."""
    base = Path(root) / members_dir(cluster)
    problems: list[str] = []
    for path in sorted(base.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        rel = path.relative_to(root).as_posix()
        problems += check_member_source(rel, path.read_text(encoding="utf-8"), cluster)
    if problems:
        raise ClusterFreezeError(f"{cluster} member code fails the static check (F-1): "
                                 + "; ".join(problems[:12])
                                 + (f" (and {len(problems) - 12} more)" if len(problems) > 12
                                    else ""))


def importable_origins(module: str) -> list[Path]:
    """The source file of strategy.members, of the cluster package and of ``module``, located
    without executing any of them (a level already imported gives its __file__)."""
    import strategy

    parts = module.split(".")
    search = list(strategy.__path__)
    out: list[Path] = []
    for i in range(2, len(parts) + 1):
        name = ".".join(parts[:i])
        loaded = sys.modules.get(name)
        if loaded is not None:
            origin = getattr(loaded, "__file__", None)
            search = list(getattr(loaded, "__path__", []) or [])
        else:
            spec = importlib.machinery.PathFinder.find_spec(name, search)
            origin = None if spec is None else spec.origin
            search = list((spec.submodule_search_locations or []) if spec else [])
        if origin is None:
            raise ClusterFreezeError(f"{name}: no source file to import")
        out.append(Path(origin).resolve())
    return out


def _check_decls(cluster: str, members: Sequence[MemberDecl], files: dict[str, dict]) -> None:
    labels = [m.label for m in members]
    ordinals = [m.ordinal for m in members]
    if not members:
        raise ClusterFreezeError(f"{cluster}: no members to freeze")
    if len(set(labels)) != len(labels) or len(set(ordinals)) != len(ordinals):
        raise ClusterFreezeError(f"{cluster}: member labels and ordinals must be unique")
    prefix = module_prefix(cluster) + "."
    for m in members:
        if isinstance(m.ordinal, bool) or not isinstance(m.ordinal, int) or m.ordinal < 1:
            raise ClusterFreezeError(f"{m.label}: ordinal {m.ordinal!r} is not a positive int")
        if not m.module.startswith(prefix):
            raise ClusterFreezeError(f"{m.label}: module {m.module} is not under {prefix}")
        rel = m.module.replace(".", "/") + ".py"
        if rel not in files:
            raise ClusterFreezeError(f"{m.label}: {rel} is not a file of the cluster directory")
        if not m.legs or not any(leg.traded for leg in m.legs):
            raise ClusterFreezeError(f"{m.label}: a member needs at least one traded leg")


def write_cluster_freeze(cluster: str, members: Sequence[MemberDecl], root: Path = REPO_ROOT
                         ) -> str:
    """Hash the cluster's member code and declarations into its freeze file; returns its sha256.
    Written once: an existing freeze file is never overwritten."""
    root = Path(root)
    files = _cluster_files(cluster, root)
    check_cluster_sources(cluster, root)
    _check_decls(cluster, members, files)
    out = root / freeze_path(cluster)
    payload = {
        "schema": FREEZE_SCHEMA, "cluster": cluster,
        "created_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "members_dir": members_dir(cluster).as_posix(), "files": files,
        "members": [m.as_dict() for m in sorted(members, key=lambda m: m.ordinal)],
    }
    data = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    out.parent.mkdir(parents=True, exist_ok=True)
    try:
        with out.open("xb") as fh:
            fh.write(data)
    except FileExistsError as exc:
        raise ClusterFreezeError(f"{freeze_path(cluster).as_posix()} already exists; a freeze is "
                                 "written once") from exc
    os.chmod(out, 0o444)
    return _sha(data)


def load_cluster_freeze(cluster: str, root: Path = REPO_ROOT) -> ClusterFreeze:
    path = Path(root) / freeze_path(cluster)
    if not path.is_file():
        raise ClusterFreezeError(f"{freeze_path(cluster).as_posix()} does not exist: the cluster's "
                                 "member code has not been frozen")
    raw = path.read_bytes()
    doc = json.loads(raw)
    if doc.get("schema") != FREEZE_SCHEMA or doc.get("cluster") != cluster:
        raise ClusterFreezeError(f"{path.name}: not a {FREEZE_SCHEMA} freeze of {cluster}")
    members = tuple(MemberDecl(m["label"], int(m["ordinal"]), m["module"], m["factory"],
                               tuple(LegSpec(leg["root"], bool(leg["traded"]))
                                     for leg in m["legs"]))
                    for m in doc["members"])
    if MEMBERS_INIT.as_posix() not in doc["files"]:
        raise ClusterFreezeError(f"{path.name}: the freeze does not hash "
                                 f"{MEMBERS_INIT.as_posix()} (written before F-1's fix)")
    return ClusterFreeze(cluster, _sha(raw), dict(doc["files"]), members, Path(root))


def verify_cluster_code(freeze: ClusterFreeze, root: Path | None = None) -> None:
    """Refuse unless strategy/members/__init__.py is empty and the cluster directory's *.py files
    are exactly the frozen ones and pass the static check (F-1)."""
    root = Path(root) if root is not None else freeze.root
    current = _cluster_files(freeze.cluster, root)
    problems = [f"{rel}: not in the freeze" for rel in sorted(set(current) - set(freeze.files))]
    problems += [f"{rel}: missing" for rel in sorted(set(freeze.files) - set(current))]
    problems += [f"{rel}: sha256 {current[rel]['sha256'][:12]}... differs from the frozen "
                 f"{info['sha256'][:12]}..." for rel, info in sorted(freeze.files.items())
                 if rel in current and current[rel] != info]
    if problems:
        raise ClusterFreezeError(f"{freeze.cluster} member code is not the frozen code: "
                                 + "; ".join(problems[:10]))
    check_cluster_sources(freeze.cluster, root)


def resolve_member(freeze: ClusterFreeze, label: str, factory: Callable[[], Any] | None = None
                   ) -> tuple[MemberDecl, Callable[[], Any]]:
    """The declared member and its factory; a passed factory must be that very attribute.
    Before the import: the frozen code is verified again, and the files Python would import for
    strategy.members, the cluster package and the module must be the checked ones (F-1)."""
    decl = freeze.member(label)
    verify_cluster_code(freeze)
    parts = decl.module.split(".")
    levels = [freeze.root.joinpath(*parts[:i]) for i in range(2, len(parts) + 1)]
    expected = [(p / "__init__.py" if p.is_dir() else p.with_suffix(".py")).resolve()
                for p in levels]
    origins = importable_origins(decl.module)
    if origins != expected:
        raise ClusterFreezeError(f"{label}: Python would import {[str(o) for o in origins]}, not "
                                 f"the checked files {[str(e) for e in expected]}")
    module = importlib.import_module(decl.module)
    declared = getattr(module, decl.factory, None)
    if declared is None or not callable(declared):
        raise ClusterFreezeError(f"{label}: {decl.module}.{decl.factory} is not a callable")
    if factory is not None and factory is not declared:
        raise ClusterFreezeError(f"{label}: the factory passed is not {decl.module}."
                                 f"{decl.factory}")
    return decl, declared


__all__ = [
    "ALLOWED_IMPORTS", "BANNED_NAMES", "CLUSTER_PATTERN", "FREEZE_SCHEMA", "MEMBERS_INIT",
    "MEMBERS_ROOT", "ClusterFreeze", "ClusterFreezeError", "MemberDecl", "check_cluster",
    "check_cluster_sources", "check_member_source", "check_members_init", "freeze_path",
    "importable_origins", "load_cluster_freeze", "members_dir", "module_prefix", "resolve_member",
    "verify_cluster_code", "write_cluster_freeze",
]
