"""E.33 B7: the pipeline freeze list (a sha256 list of every code file, config and environment lock).

Standard: docs/prompts/STAGE_E.33.md B7 ("freeze the pipeline: a sha256 list of every code file, config and
environment lock (uv.lock)"); protocol P0.2 (the readings file's sha256 is a line of the list), P5 (uv.lock is
hashed), P7.1 (the pipeline sha256 is the sha256 of this list file; c1_freeze.py takes it); PipelineReview SF2 (the
list covers the code the pipeline executes outside pipeline/); readings R-L3 (check-proofs).

The files are found by MEASURING. A child interpreter (-I -B, cwd = repo, pipeline/ first on sys.path, as when a
pipeline script runs) imports every pipeline/*.py module without running main, then follows every import written
anywhere in a loaded repo file, harness code included (function-level imports, the sys.path entries those functions
add, importlib.import_module calls: a literal, an f-string fed by literal call sites, else every module of the
package), then runs the read-only PROBES under an audit hook that records every file opened. Data and config files are
the repo files those probes and imports open plus the module-level path constants of the loaded modules: a
pipeline-owned constant naming an existing repo file must be opened by a probe or be classified in CONSTANT_CLASS
(else the build stops); a harness constant is hashed unless classified, never-read or refused by guard33's checks.
Files outside the repo that the loaders read (the E.31 ZM split, the E.33 ZS/ZL re-split, the Z4 definitions) go
into a separate derived-inputs manifest (build-inputs, at most 2 hashing processes at nice 10, resumable); its
sha256 is a line of the pipeline section, and verify re-hashes it. The documents section holds the coder readings
files, INTERFACE.md and the compiled readings; implB/ and the tests form the "verification evidence" section; the
freeze and C1 tools their own section (all hashed, none executed by the search).

  uv run python reports/stage_e33_briefs/work/lead/freeze33.py build-inputs --out INPUTS
  uv run python reports/stage_e33_briefs/work/lead/freeze33.py build --out FILE --inputs INPUTS
  uv run python reports/stage_e33_briefs/work/lead/freeze33.py verify --freeze FILE [--remeasure] [--skip-inputs]
  uv run python reports/stage_e33_briefs/work/lead/freeze33.py check-proofs --freeze FILE [--manifest PATH]

build writes FILE (sha256sum format, `cd <repo> && sha256sum -c FILE` works) and FILE.provenance.tsv (how each
file was found, and every candidate not hashed with the reason). Exit codes: 0 ok; 1 a difference (verify,
check-proofs) or a stopped build; 2 (check-proofs) the manifest check passed but a file the proof run can execute
and the manifest does not pin was modified after the proof run started or differs from git HEAD (evidence for the
lead, not a verdict).
"""
from __future__ import annotations

import argparse
import ast
import fnmatch
import hashlib
import importlib
import importlib.util
import json
import os
import pkgutil
import re
import subprocess
import sys
import tempfile
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
WORK = HERE.parent
PIPE = WORK / "pipeline"
IMPLB = WORK / "implB"
P7_DIR = REPO / "reports" / "stage_e32_briefs" / "protocol"
PROTOCOL = REPO / "reports" / "stage_e32_discovery_protocol.md"
READINGS = REPO / "reports" / "stage_e33_protocol_readings.md"
ENV_FILES = ("uv.lock", "pyproject.toml", ".python-version")  # .python-version only if present
EVIDENCE_DIRS = (IMPLB, PIPE / "tests", PIPE / "tests_b3", PIPE / "tests_b4")
TOOL_FILES = (HERE / "freeze33.py", HERE / "test_freeze33.py", HERE / "c1_freeze.py")
DOCUMENT_GLOBS = ((WORK, "*_readings.md"), (IMPLB, "*_readings.md"))   # the coder readings files (lead, item 4)
DOCUMENT_FILES = (REPO / "reports" / "stage_e33_briefs" / "INTERFACE.md",
                  REPO / "reports" / "stage_e33b_briefs" / "readings_compiled.md")
INPUTS_MARKER = "# E.33 derived-inputs manifest"
MAX_HASH_JOBS = 2             # lead: hash the derived inputs with at most 2 processes, nice 10
HASH_NICE = 10
PROOF_MANIFEST = Path("/mnt/large-storage/market_data/PropExperiment/derived/e33/proofs/run_manifest.json")
PROOF_ROOTS = ("run_proofs33", "synth33", "select33", "search33", "run_search33")  # run_proofs33.pipeline_closure
ENGINE_ROOTS = ("search33", "run_search33")                                         # search33.pipeline_files
NEVER_PREFIXES = ("data/sealed/", ".git/")    # never opened, never hashed (sealed test data, git internals)
NEVER_NAMES = (".env",)                       # credentials
LIBRARIES = (("numpy", "numpy"), ("pandas", "pandas"), ("pyarrow", "pyarrow"), ("scikit-learn", "sklearn"),
             ("lightgbm", "lightgbm"), ("scipy", "scipy"))  # (header name, import name = proof manifest key)
SECTIONS = {
    "pipeline": "code the search executes, the data and config files it reads, the environment lock, "
                "the protocol, the readings file and the derived-inputs manifest",
    "documents": "the coder readings files, INTERFACE.md and the compiled readings (hashed, not executed)",
    "verification evidence": "implB/ and the tests (hashed, not executed by the search)",
    "freeze tools": "the freeze and C1 tools (hashed, not executed by the search)",
}
PT = ZoneInfo("America/Vancouver")

# Read-only probes run in the child under the audit hook: (label, module, function, args, what it reads).
# None reads market data; each is a reader the search itself calls.
PROBES = (
    ("cal33.release_table", "cal33", "release_table", (),
     "the P3.6 release CSVs through guard33.check_reference (also the seal manifest, the unsealed list and the "
     "four discovery manifests)"),
    ("cal33.trade_dates", "cal33", "trade_dates", (),
     "the grains program calendar (data.calendars.grains via data.group_session) and the discovery manifest"),
    ("cost33.load_firm_fees", "cost33", "load_firm_fees", (), "the E.28 fee files (A2 per firm, A3 cross-checks)"),
    ("select33.b_test_at(838)", "select33", "b_test_at", (838,),
     "p7_final / p7_thresholds b_test and the hist2010 grains calendar"),
)

# Module-level path constants that name an existing repo file and that no probe opens: the reviewed class of each.
# "input" is hashed; every other class is listed in the provenance file and not hashed.
# Harness constants naming an existing repo file are hashed (lead, item 2) unless listed here, never-read, or refused
# by guard33's checks; pipeline-owned constants must be opened by a probe or listed here.
CONSTANT_CLASS: dict[str, tuple[str, str]] = {
    "screening.trial_registry.REGISTRY_PATH": ("state", "the trial registry: C1 appends the registrations to it, so "
                                               "a hash of it would fail every verify after C1 by design"),
    "g6_33.REPORT": ("output", "the G6 clock report that g6_33 writes (reports/stage_e33_briefs/work/G6_clock_report.md)"),
    "run_proofs33.SUMMARY": ("output", "B5_proofs.md, rewritten by run_proofs33 after every proof seed"),
}

_DATA_LITERAL = re.compile(r"^[\w.\-/{}*]*\.(json|jsonl|csv|tsv|txt|toml|ya?ml|parquet|npz|npy|md|lock|dbn|zst|pkl|"
                           r"sha256|py)$")
_HASH_LINE = re.compile(r"^([0-9a-f]{64})  (\S.*)$")


# ----------------------------------------------------------------------------------------------- paths, hashes
def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def in_repo(path: str | Path, repo: Path = REPO) -> bool:
    """Inside the repo and not the project environment (.venv/ holds the libraries; uv.lock covers them)."""
    p = os.path.abspath(path)
    if not p.startswith(str(repo) + os.sep):
        return False
    r = p[len(str(repo)) + 1:]
    return not (r.startswith(".venv" + os.sep) or f"{os.sep}site-packages{os.sep}" in p)


def rel(path: str | Path, repo: Path = REPO) -> str:
    """Repo-relative, lexical (a symlink inside the repo keeps its repo path)."""
    return os.path.relpath(os.path.abspath(path), repo)


def owned(path: str | Path) -> bool:
    """Pipeline-owned code (pipeline/, the E.31 pilot modules, the E.32 protocol scripts). Its path constants must be
    opened by a probe or classified, and the literal audit covers it. Every import is followed in all repo code."""
    return in_repo(path) and rel(path).startswith("reports" + os.sep)


def never(relpath: str) -> bool:
    return relpath.startswith(NEVER_PREFIXES) or Path(relpath).name in NEVER_NAMES


def env_versions() -> dict[str, str]:
    """python and the library versions, as module __version__ (the proof manifest's convention)."""
    out = {"python": sys.version.split()[0]}
    for header, name in LIBRARIES:
        out[header] = importlib.import_module(name).__version__
    return out


# ----------------------------------------------------------------------------------------------- file format
def render(env: dict[str, str], sections: dict[str, dict[str, str]]) -> str:
    lines = ["# E.33 pipeline freeze list, written by reports/stage_e33_briefs/work/lead/freeze33.py build",
             "# format: sha256sum (check: cd <repo root> && sha256sum -c <this file>); paths relative to the repo root",
             "# the pipeline sha256 (protocol P7.1) is the sha256 of this file"]
    lines += [f"# env {k} {v}" for k, v in env.items()]
    for name, note in SECTIONS.items():
        lines.append(f"# section {name}: {note}")
        for path in sorted(sections.get(name, {})):
            if "\n" in path or "\\" in path:
                raise ValueError(f"path not representable in sha256sum format: {path!r}")
            lines.append(f"{sections[name][path]}  {path}")
    return "\n".join(lines) + "\n"


def parse(text: str) -> tuple[dict[str, str], dict[str, dict[str, str]]]:
    env: dict[str, str] = {}
    sections: dict[str, dict[str, str]] = {}
    current = None
    for n, line in enumerate(text.splitlines(), 1):
        if line.startswith("# env "):
            key, _, value = line[len("# env "):].partition(" ")
            env[key] = value
        elif line.startswith("# section "):
            current = line[len("# section "):].split(":", 1)[0]
            sections[current] = {}
        elif line.startswith("#") or not line.strip():
            continue
        else:
            m = _HASH_LINE.match(line)
            if not m or current is None:
                raise ValueError(f"line {n}: not a freeze-list line: {line[:80]!r}")
            if m.group(2) in sections[current]:
                raise ValueError(f"line {n}: duplicate path {m.group(2)}")
            sections[current][m.group(2)] = m.group(1)
    return env, sections


# ----------------------------------------------------------------------------------------------- AST helpers
_TREE_CACHE: dict[int, dict] = {}  # per parsed tree (trees are never mutated): parents, import calls, calls by name


def _info(tree: ast.AST) -> dict:
    info = _TREE_CACHE.get(id(tree))
    if info is None or info["tree"] is not tree:
        calls: dict[str, list[ast.Call]] = defaultdict(list)
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                f = node.func
                name = f.id if isinstance(f, ast.Name) else f.attr if isinstance(f, ast.Attribute) else None
                if name:
                    calls[name].append(node)
                if _is_import_call(f) and node.args:
                    imports.append(node)
        info = {"tree": tree, "parents": None, "calls": calls, "imports": imports}
        _TREE_CACHE[id(tree)] = info
    return info


def _parents(tree: ast.AST) -> dict[ast.AST, ast.AST]:
    info = _info(tree)
    if info["parents"] is None:
        info["parents"] = {child: node for node in ast.walk(tree) for child in ast.iter_child_nodes(node)}
    return info["parents"]


def _enclosing_function(node: ast.AST, parents: dict) -> ast.FunctionDef | None:
    while node in parents:
        node = parents[node]
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return node
    return None


def static_import_targets(tree: ast.AST, package: str | None) -> list[tuple[str, int]]:
    """Every module name an import statement anywhere in the file can load (from-imports also as X.name)."""
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            out += [(a.name, node.lineno) for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                if not package:
                    continue
                try:
                    base = importlib.util.resolve_name("." * node.level + (node.module or ""), package)
                except ImportError:
                    continue
            else:
                base = node.module
            out.append((base, node.lineno))
            out += [(f"{base}.{a.name}", node.lineno) for a in node.names if a.name != "*"]
    return out


def _is_import_call(func: ast.AST) -> bool:
    return (isinstance(func, ast.Attribute) and func.attr == "import_module") or \
        (isinstance(func, ast.Name) and func.id in ("import_module", "__import__"))


def _call_site_values(fn: ast.FunctionDef, param: str, trees: dict[str, ast.AST]) -> tuple[list[str], list[str]]:
    """Literal values passed for `param` at every call of a function named fn.name in the given files."""
    params = [a.arg for a in fn.args.posonlyargs + fn.args.args]
    pos = params.index(param) if param in params else None
    values, unresolved = [], []
    for path, tree in trees.items():
        for node in _info(tree)["calls"].get(fn.name, ()):
            arg = next((k.value for k in node.keywords if k.arg == param), None)
            if arg is None and pos is not None and pos < len(node.args):
                arg = node.args[pos]
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                values.append(arg.value)
            else:
                unresolved.append(f"{path}:{node.lineno}")
    return values, unresolved


def string_values(expr: ast.AST, fn: ast.FunctionDef | None, trees: dict[str, ast.AST],
                  depth: int = 0) -> list[str] | None:
    """The literal strings expr can take: a constant, a local name assigned from one, or an f-string whose fields are
    parameters of the enclosing function fed by literal call sites. None when not resolvable."""
    if depth > 3:
        return None
    if isinstance(expr, ast.Constant) and isinstance(expr.value, str):
        return [expr.value]
    if isinstance(expr, ast.Name) and fn is not None:
        assigned = [n.value for n in ast.walk(fn) if isinstance(n, ast.Assign) and len(n.targets) == 1
                    and isinstance(n.targets[0], ast.Name) and n.targets[0].id == expr.id]
        if not assigned:
            return None
        out: list[str] = []
        for value in assigned:
            got = string_values(value, fn, trees, depth + 1)
            if got is None:
                return None
            out += got
        return out
    if isinstance(expr, ast.JoinedStr) and fn is not None:
        combos = [""]
        for part in expr.values:
            if isinstance(part, ast.Constant):
                combos = [c + str(part.value) for c in combos]
            elif isinstance(part, ast.FormattedValue) and isinstance(part.value, ast.Name) and \
                    part.format_spec is None and part.conversion == -1:
                values, unresolved = _call_site_values(fn, part.value.id, trees)
                if unresolved or not values:
                    return None
                combos = [c + v for c in combos for v in sorted(set(values))]
            else:
                return None
        return combos
    return None


def string_pattern(expr: ast.AST, fn: ast.FunctionDef | None) -> str | None:
    """'pkg.sub.*' when expr (or the local name it is assigned from) is an f-string 'pkg.sub.{x}'."""
    if isinstance(expr, ast.Name) and fn is not None:
        assigned = [n.value for n in ast.walk(fn) if isinstance(n, ast.Assign) and len(n.targets) == 1
                    and isinstance(n.targets[0], ast.Name) and n.targets[0].id == expr.id]
        expr = assigned[0] if len(assigned) == 1 else expr
    if not isinstance(expr, ast.JoinedStr):
        return None
    text = "".join(str(v.value) if isinstance(v, ast.Constant) else "*" for v in expr.values)
    head, _, last = text.rpartition(".")
    return f"{head}.*" if last == "*" and head and "*" not in head else None


def dynamic_import_targets(trees: dict[str, ast.AST]) -> tuple[list[tuple[str, str]], list[str],
                                                                list[tuple[str, str]]]:
    """(literal targets, unresolved calls, package patterns): an import_module call whose name is not a literal at
    every call site becomes 'pkg.*' (every module of the package) when the name is an f-string 'pkg.{x}'."""
    targets, unresolved, patterns = [], [], []
    for path, tree in trees.items():
        imports = _info(tree)["imports"]
        parents = _parents(tree) if imports else {}
        for node in imports:
            fn = _enclosing_function(node, parents)
            values = string_values(node.args[0], fn, trees)
            where = f"{path}:{node.lineno} {ast.unparse(node)}"
            if values is not None:
                targets += [(v, f"{where} = {v!r}") for v in values]
            elif (pattern := string_pattern(node.args[0], fn)) is not None:
                patterns.append((pattern, f"{where}: not every call site is a literal, so every {pattern}"))
            else:
                unresolved.append(where)
    return targets, unresolved, patterns


_SAFE_NODES = (ast.Expression, ast.Name, ast.Attribute, ast.Constant, ast.BinOp, ast.Div, ast.Add, ast.Load,
               ast.Subscript, ast.Call)
_SAFE_CALLS = {"str", "Path", "resolve", "expanduser", "absolute"}


def safe_path_expr(expr: ast.AST) -> bool:
    """A sys.path argument we may evaluate in the module's namespace: names, attributes, / and str()/Path()."""
    for node in ast.walk(expr):
        if not isinstance(node, _SAFE_NODES):
            return False
        if isinstance(node, ast.Call):
            f = node.func
            name = f.id if isinstance(f, ast.Name) else f.attr if isinstance(f, ast.Attribute) else None
            if name not in _SAFE_CALLS:
                return False
    return True


def sys_path_args(tree: ast.AST) -> list[ast.AST]:
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and \
                node.func.attr in ("insert", "append") and ast.unparse(node.func.value) == "sys.path" and node.args:
            out.append(node.args[-1])
    return out


def top_level_names(tree: ast.Module) -> set[str]:
    names: set[str] = set()
    todo = list(tree.body)
    while todo:
        node = todo.pop()
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        if isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for t in targets:
                names.update(n.id for n in ast.walk(t) if isinstance(n, ast.Name))
        for field in ("body", "orelse", "finalbody", "handlers"):
            todo += getattr(node, field, [])
    return names


def data_literals(tree: ast.AST) -> list[tuple[int, str]]:
    """String literals and f-string patterns that look like file names (docstrings skipped)."""
    docs = {id(n.value) for n in ast.walk(tree) if isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant)}
    inner = {id(v) for n in ast.walk(tree) if isinstance(n, ast.JoinedStr) for v in n.values}
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and id(node) not in docs | inner:
            text = node.value
        elif isinstance(node, ast.JoinedStr):
            text = "".join(str(v.value) if isinstance(v, ast.Constant) else "*" for v in node.values)
        else:
            continue
        if _DATA_LITERAL.match(text):
            out.append((node.lineno, text))
    return out


# ----------------------------------------------------------------------------------------------- the child
def _path_values(value) -> list[str]:
    if isinstance(value, Path):
        return [str(value)]
    if isinstance(value, str):
        ok = os.sep in value and "\n" not in value and " " not in value and "://" not in value and \
            len(value) < 400 and (value.startswith("/") or re.search(r"\.\w{1,8}$", value))
        return [value] if ok else []
    if isinstance(value, dict):
        return [p for k, v in value.items() for x in (k, v) if isinstance(x, (Path, str)) for p in _path_values(x)]
    if isinstance(value, (tuple, list, set, frozenset)):
        return [p for x in value if isinstance(x, (Path, str)) for p in _path_values(x)]
    return []


def guard_refusal(path: str) -> str | None:
    """guard33 (P1.2) on a file before the freeze reads it. Outside the repo: the full check_path. Inside the repo:
    every check but the last one (the market-data allowlist, which refuses every repo file by design): sealed data,
    sealed originals, E.31 runs/, the unsealed list, test-window or after-cutoff dates in the name."""
    import guard33 as g
    try:
        g.check_path(path)
    except g.GuardRefused as exc:
        if in_repo(path) and "not on the E.33 allowlist" in str(exc):
            return None
        return str(exc)
    return None


def derived_inputs(note_open) -> list[dict]:
    """Every file outside the repo the loaders read, named by data33's own path functions over cal33's trade dates,
    the E.31 markers data33 opens, the Z4 definitions files, and every other file in those input directories."""
    import cal33
    import data33 as d33
    found: dict[str, list[str]] = defaultdict(list)
    for d in cal33.trade_dates():
        found[str(d33.zm_path(d))].append("data33.zm_path(trade date): E.31 ZM split")
        for root in sorted(d33.ROOT_SERIES):
            p = d33.mbp1_path(root, d)
            found[str(p)].append(f"data33.mbp1_path({root}, trade date): E.33 {root} re-split")
            found[str(p.with_suffix(d33.DONE_SUFFIX))].append(f"data33.load_mbp1 DONE marker ({root})")
    d33._e31_markers_ok.cache_clear()  # a probe may have read them already: read again under the hook
    for p in note_open(d33._e31_markers_ok):
        found[p].append("opened by data33._e31_markers_ok (E.31 ZM month markers)")
    for name in ("DEF_ALL", "DEF_OUTRIGHT", "DEF_MANIFEST"):
        found[str(getattr(d33, name))].append(f"data33.{name}: Z4 definitions split")
    found[str(d33.DEF_DIR / f"definitions{d33.DONE_SUFFIX}")].append("data33 definitions DONE marker")
    for folder in sorted({os.path.dirname(os.path.abspath(p)) for p in found}):
        for name in sorted(os.listdir(folder)):
            fp = os.path.join(folder, name)
            if os.path.isfile(fp) and fp not in found:
                found[fp].append("in an input directory, not named by a loader path function")
    return [{"path": os.path.abspath(p), "how": hows, "exists": os.path.isfile(p),
             "refused": guard_refusal(p)} for p, hows in sorted(found.items())]


def child(roots: list[str], run_probes: bool, out_json: Path, loaded_probes_only: bool = False,
          with_derived: bool = False) -> None:
    """Runs in the measurement interpreter: import, follow imports, probe, collect; writes out_json."""
    phase = ["import"]
    opens: list[tuple[str, str, str]] = []
    skip_prefixes = tuple({sys.prefix, sys.base_prefix, "/usr/", "/proc/", "/sys/", "/dev/", "/etc/"})

    def hook(event, args):
        if event != "open" or not isinstance(args[0], (str, bytes)):
            return
        p = os.path.abspath(os.fsdecode(args[0]))
        if p.endswith((".pyc", ".so")) or (p.startswith(skip_prefixes) and not in_repo(p)):
            return
        if isinstance(args[1], str):
            mode = args[1]
        else:  # os.open: read-only unless a write flag is set
            writes = os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_APPEND | os.O_TRUNC
            mode = f"w(flags={args[2]})" if int(args[2] or 0) & writes else f"r(flags={args[2]})"
        opens.append((phase[0], p, mode))

    t0 = time.monotonic()

    def progress(msg: str) -> None:
        print(f"[measure {time.monotonic() - t0:7.1f}s] {msg}", file=sys.stderr, flush=True)

    sys.addaudithook(hook)
    os.chdir(REPO)
    sys.path.insert(0, str(PIPE))
    loaded: dict[str, dict] = {}
    errors: list[str] = []

    main_mod = sys.modules["__main__"]  # this tool (also aliased as __mp_main__ once multiprocessing loads)

    def snapshot(how: str) -> None:
        for name, mod in list(sys.modules.items()):
            f = getattr(mod, "__file__", None)
            if f and mod is not main_mod and in_repo(f) and os.path.abspath(f) not in loaded:
                loaded[os.path.abspath(f)] = {"module": name, "how": how}

    snapshot("loaded before the entry points")
    for root in roots:
        try:
            importlib.import_module(root)
        except BaseException as exc:  # noqa: BLE001 - a failed entry point stops the build
            errors.append(f"import {root}: {type(exc).__name__}: {exc}")
        snapshot(f"loaded by importing entry point {root}")
        progress(f"imported {root}: {len(loaded)} repo files loaded")

    trees: dict[str, ast.AST] = {}
    inserted: list[str] = []
    unresolved_imports: set[str] = set()
    unresolved_dynamic: set[str] = set()
    libraries: set[str] = set()

    def try_import(name: str, where: str) -> None:
        if name in sys.modules:
            return
        try:
            spec = importlib.util.find_spec(name.split(".")[0])
        except BaseException:  # noqa: BLE001
            spec = None
        if spec is None:
            unresolved_imports.add(f"{name} ({where})")
            return
        origin = spec.origin if spec.origin not in (None, "namespace") else \
            next(iter(spec.submodule_search_locations or []), "")
        if not in_repo(origin):
            libraries.add(name.split(".")[0])
            return
        try:
            importlib.import_module(name)
        except ModuleNotFoundError as exc:
            if exc.name != name:  # X.attr of a `from X import attr` is not a module: fine
                unresolved_imports.add(f"{name} ({where}): {exc}")
        except BaseException as exc:  # noqa: BLE001
            errors.append(f"lazy import {name} ({where}): {type(exc).__name__}: {exc}")
        snapshot(f"lazy import at {where}")

    def follow_imports() -> None:
        while True:
            before = len(loaded)
            for f in sorted(loaded):
                if f in trees or not f.endswith(".py"):
                    continue
                trees[f] = ast.parse(Path(f).read_text(encoding="utf-8"), f)
                mod = sys.modules.get(loaded[f]["module"])
                for expr in sys_path_args(trees[f]):
                    if not safe_path_expr(expr) or mod is None:
                        continue
                    try:
                        value = os.path.abspath(os.fspath(eval(compile(ast.Expression(expr), f, "eval"),
                                                               dict(vars(mod)))))
                    except Exception:  # noqa: BLE001 - a local name (loop variable): set at import already
                        continue
                    if value not in sys.path:
                        sys.path.insert(0, value)
                        inserted.append(f"{rel(value)} (sys.path argument in {rel(f)})")
            for f, tree in sorted(trees.items()):
                mod = sys.modules.get(loaded[f]["module"])
                package = getattr(mod, "__package__", None)
                for name, line in static_import_targets(tree, package):
                    try_import(name, f"{rel(f)}:{line}" + ("" if owned(f) else " (harness)"))
            targets, unresolved, patterns = dynamic_import_targets({rel(f): t for f, t in trees.items()})
            unresolved_dynamic.update(unresolved)
            for name, where in targets:
                try_import(name, where)
            for pattern, where in patterns:
                package = pattern[:-2]
                try_import(package, where)
                pkg = sys.modules.get(package)
                for info in pkgutil.iter_modules(getattr(pkg, "__path__", None) or []):
                    try_import(f"{package}.{info.name}", where)
            progress(f"import pass: {len(loaded)} repo files loaded, {len(trees)} parsed")
            if len(loaded) == before:
                return

    follow_imports()
    if run_probes:
        for label, modname, func, args, _why in PROBES:
            if loaded_probes_only and modname not in sys.modules:
                continue  # check-proofs: only readers of modules the measured roots load
            phase[0] = f"probe {label}"
            try:
                getattr(importlib.import_module(modname), func)(*args)
            except BaseException as exc:  # noqa: BLE001 - a failed probe stops the build
                errors.append(f"probe {label}: {type(exc).__name__}: {exc}")
            snapshot(f"imported while running probe {label}")
            progress(f"probe {label} done")
        phase[0] = "import (after probes)"
        follow_imports()

    constants, literals = [], []
    for f, info in sorted(loaded.items()):
        mod = sys.modules.get(info["module"])
        tree = trees.get(f)
        if mod is None or tree is None:
            continue
        own = top_level_names(tree)
        for name in sorted(own):
            for p in _path_values(getattr(mod, name, None)):
                ap = os.path.abspath(p if os.path.isabs(p) else REPO / p)
                kind = "file" if os.path.isfile(ap) else "dir" if os.path.isdir(ap) else "missing"
                refused = guard_refusal(ap) if kind == "file" and in_repo(ap) and not never(rel(ap)) else None
                constants.append({"owner": f"{info['module']}.{name}", "file": rel(f), "path": ap, "kind": kind,
                                  "refused": refused})
        if owned(f):  # the literal audit covers pipeline-owned code (harness inputs are listed as constants)
            literals += [{"file": rel(f), "line": line, "text": text} for line, text in data_literals(tree)]

    derived: list[dict] = []
    if with_derived:
        def note_open(fn) -> list[str]:
            start = len(opens)
            fn()
            return [p for _ph, p, _m in opens[start:] if not in_repo(p)]
        phase[0] = "derived inputs"
        try:
            derived = derived_inputs(note_open)
        except BaseException as exc:  # noqa: BLE001 - the enumeration must succeed
            errors.append(f"derived inputs: {type(exc).__name__}: {exc}")
        progress(f"derived inputs: {len(derived)} files")
    phase[0] = "versions"
    out = {"derived": derived, "roots": roots, "loaded": loaded, "opens": opens, "constants": constants, "literals": literals,
           "sys_path_added": inserted, "unresolved_imports": sorted(unresolved_imports),
           "unresolved_dynamic": sorted(unresolved_dynamic), "libraries": sorted(libraries),
           "errors": errors, "versions": env_versions()}
    out_json.write_text(json.dumps(out, indent=1, sort_keys=True))


def measure(roots: tuple[str, ...], probes: bool = True, loaded_probes_only: bool = False,
            with_derived: bool = False) -> dict:
    """Run the child in a fresh interpreter (no bytecode written, PYTHONPATH and user site ignored)."""
    with tempfile.TemporaryDirectory(prefix="freeze33_") as tmp:
        out = Path(tmp) / "measure.json"
        cmd = [sys.executable, "-I", "-B", str(Path(__file__).resolve()), "_measure", "--roots", ",".join(roots),
               "--json-out", str(out)] + ([] if probes else ["--no-probes"]) + \
            (["--loaded-probes-only"] if loaded_probes_only else []) + (["--derived"] if with_derived else [])
        run = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, timeout=900)
        if run.returncode != 0 or not out.exists():
            raise SystemExit(f"measurement child failed (rc {run.returncode}):\n{run.stderr[-3000:]}")
        return json.loads(out.read_text())


# ----------------------------------------------------------------------------------------------- assembly
def pipeline_modules() -> tuple[str, ...]:
    return tuple(sorted(p.stem for p in PIPE.glob("*.py")))


def _evidence_files() -> list[Path]:
    out = []
    for d in EVIDENCE_DIRS:
        out += [p for p in d.rglob("*") if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"]
    return out


def _document_files() -> tuple[list[Path], list[str]]:
    files = [p for d, pattern in DOCUMENT_GLOBS for p in sorted(d.glob(pattern)) if p.is_file()]
    missing = [rel(p) for p in DOCUMENT_FILES if not p.is_file()]
    return files + [p for p in DOCUMENT_FILES if p.is_file()], missing


def assemble(m: dict, inputs: Path | None = None) -> tuple[dict[str, dict[str, str]], list[tuple[str, str, str]],
                                                           list[str], list[str]]:
    """(sections, provenance rows (kind, path, detail), stopping problems, warnings) from a measurement."""
    how: dict[str, list[str]] = defaultdict(list)
    rows: list[tuple[str, str, str]] = []
    problems = [f"child: {e}" for e in m["errors"]]
    warnings = [f"unresolved import {u}" for u in m["unresolved_imports"]]
    warnings += [f"unresolved dynamic import {u}" for u in m["unresolved_dynamic"]]
    code = {rel(f) for f in m["loaded"]}
    for f, info in m["loaded"].items():
        how[rel(f)].append(f"{info['how']} (module {info['module']})")
    for p in sorted(PIPE.glob("*.py")):
        if rel(p) not in code:
            how[rel(p)].append("pipeline/*.py listing (NOT loaded by the measurement)")
            warnings.append(f"{rel(p)} is in pipeline/ but was not loaded")
    for phase, path, mode in m["opens"]:
        r = rel(path) if in_repo(path) else path
        if not in_repo(path):
            rows.append(("outside-repo-opened", path, f"{phase} mode {mode}: not hashed"))
        elif never(r):
            problems.append(f"{r} was opened by the measurement ({phase}): a never-read path")
        elif not ("r" in mode and "+" not in mode):
            rows.append(("written", r, f"{phase} mode {mode}: an output, not hashed"))
        elif os.path.isfile(path) and r not in code:
            how[r].append(f"opened by {phase}")
    for c in m["constants"]:
        path, owner = c["path"], c["owner"]
        harness = not owned(REPO / c["file"])
        if not in_repo(path):
            rows.append((f"outside-repo-constant-{c['kind']}", path, f"{owner}: not in this list (derived inputs are in "
                         "the derived-inputs manifest)"))
            continue
        r = rel(path)
        if never(r):
            rows.append(("never", r, f"{owner}: sealed, git or credentials: never read, never hashed"))
        elif c["kind"] != "file":
            rows.append((f"constant-{c['kind']}", r, f"{owner}: not a file, not hashed"))
        elif r.endswith(".py") or r in how:
            how[r].append(f"path constant {owner}" + (" (harness)" if harness else ""))
            cls = CONSTANT_CLASS.get(owner)
            if cls and cls[0] != "input":
                problems.append(f"{owner} -> {r}: classified {cls[0]} but opened by a probe or loaded as code")
        elif owner in CONSTANT_CLASS:
            cls, why = CONSTANT_CLASS[owner]
            if cls == "input":
                how[r].append(f"path constant {owner} (classified input: {why})")
            else:
                rows.append((cls, r, f"{owner}: {why}"))
        elif c.get("refused"):
            rows.append(("guard-refused", r, f"{owner}: {c['refused']} (not read, not hashed)"))
        elif harness:
            how[r].append(f"path constant {owner} (harness constant, hashed by the lead's item 2)")
        else:
            problems.append(f"unclassified path constant {owner} -> {r} (add it to CONSTANT_CLASS)")
            rows.append(("unclassified", r, owner))
    for name in ENV_FILES:
        if (REPO / name).is_file():
            how[name].append("environment (prompt B7, P5)")
    how[rel(PROTOCOL)].append("the frozen protocol (P7.1 protocol sha256)")
    how[rel(READINGS)].append("the readings file (P0.2)")
    if inputs is not None:
        how[rel(inputs)].append("the derived-inputs manifest (lead, item 3)")
    pipeline = {}
    for r in sorted(how):
        if never(r):
            problems.append(f"{r}: a never-hashed path reached the pipeline section")
            continue
        if not (REPO / r).is_file():
            problems.append(f"{r}: not a file")
            continue
        pipeline[r] = sha256_file(REPO / r)
        rows.append(("hashed:pipeline", r, "; ".join(dict.fromkeys(how[r]))))
    doc_files, missing_docs = _document_files()
    problems += [f"document {d} does not exist" for d in missing_docs]
    documents = {rel(p): sha256_file(p) for p in doc_files if rel(p) not in pipeline}
    rows += [("hashed:documents", r, "readings file, INTERFACE.md or compiled readings") for r in sorted(documents)]
    evidence = {rel(p): sha256_file(p) for p in _evidence_files() if rel(p) not in pipeline and rel(p) not in documents}
    rows += [("hashed:verification evidence", r, "implB/ or tests listing") for r in sorted(evidence)]
    tools = {rel(p): sha256_file(p) for p in TOOL_FILES
             if p.is_file() and rel(p) not in pipeline and rel(p) not in evidence and rel(p) not in documents}
    rows += [("hashed:freeze tools", r, "freeze/C1 tool") for r in sorted(tools)]
    hashed_names = {Path(r).name for sec in (pipeline, documents, evidence, tools) for r in sec}
    for lit in m["literals"]:
        name = Path(lit["text"]).name
        if not any(fnmatch.fnmatchcase(h, name) for h in hashed_names):
            rows.append(("literal-unmatched", f"{lit['file']}:{lit['line']}", lit["text"]))
    rows += [("sys-path-added", s, "evaluated sys.path argument") for s in m["sys_path_added"]]
    rows += [("library", lib, "lazily imported library, covered by uv.lock") for lib in m["libraries"]]
    rows += [("unresolved", u, "") for u in m["unresolved_imports"] + m["unresolved_dynamic"]]
    return ({"pipeline": pipeline, "documents": documents, "verification evidence": evidence, "freeze tools": tools},
            rows, problems, warnings)


# ----------------------------------------------------------------------------------------------- derived inputs
def _set_nice() -> None:
    try:
        os.setpriority(os.PRIO_PROCESS, 0, max(HASH_NICE, os.getpriority(os.PRIO_PROCESS, 0)))
    except OSError:
        pass


def _hash_job(path: str) -> tuple[str, int, int, str]:
    st = os.stat(path)
    return path, st.st_size, st.st_mtime_ns, sha256_file(Path(path))


def hash_files(paths: list[str], jobs: int, cache: Path | None = None) -> dict[str, tuple[int, str]]:
    """{path: (bytes, sha256)}, at most MAX_HASH_JOBS processes at nice >= 10. With a cache file the run is
    resumable: each finished file is appended as size, mtime_ns, sha256, path, and reused when size and mtime agree."""
    jobs = max(1, min(jobs, MAX_HASH_JOBS))
    _set_nice()
    done: dict[str, tuple[int, str]] = {}
    if cache is not None and cache.exists():
        for line in cache.read_text(encoding="utf-8").splitlines():
            size, mtime, digest, path = line.split("\t", 3)
            st = os.stat(path) if os.path.isfile(path) else None
            if st is not None and st.st_size == int(size) and st.st_mtime_ns == int(mtime):
                done[path] = (int(size), digest)
    todo = [p for p in paths if p not in done]
    log = cache.open("a", encoding="utf-8") if cache is not None else None
    try:
        if todo:
            from concurrent.futures import ProcessPoolExecutor
            with ProcessPoolExecutor(max_workers=jobs, initializer=_set_nice) as pool:
                for n, (path, size, mtime, digest) in enumerate(pool.map(_hash_job, todo, chunksize=4), 1):
                    done[path] = (size, digest)
                    if log is not None:
                        log.write(f"{size}\t{mtime}\t{digest}\t{path}\n")
                        log.flush()
                    if n % 500 == 0:
                        print(f"  hashed {n}/{len(todo)}", flush=True)
    finally:
        if log is not None:
            log.close()
    return {p: done[p] for p in paths}


def render_inputs(hashed: dict[str, tuple[int, str]]) -> str:
    total = sum(size for size, _d in hashed.values())
    lines = [f"{INPUTS_MARKER} (freeze33.py build-inputs): files outside the repo that the pipeline reads",
             "# format: sha256sum with absolute paths (check: sha256sum -c <this file>)",
             f"# files {len(hashed)}, bytes {total}",
             "# section derived inputs: ZM E.31 split and markers, ZS/ZL re-split, Z4 definitions (outputs keyed by "
             "code hash, the feature and label stores, are not inputs)"]
    lines += [f"{hashed[p][1]}  {p}" for p in sorted(hashed)]
    return "\n".join(lines) + "\n"


def is_inputs_manifest(path: Path) -> bool:
    try:
        with path.open(encoding="utf-8") as fh:
            return fh.readline().startswith(INPUTS_MARKER)
    except (OSError, UnicodeDecodeError):
        return False


def derived_problems(derived: list[dict]) -> list[str]:
    out = [f"derived input missing: {d['path']}" for d in derived if not d["exists"]]
    out += [f"derived input refused by guard33: {d['path']}: {d['refused']}" for d in derived if d["refused"]]
    return out + ([] if derived else ["no derived inputs enumerated"])


def cmd_build_inputs(out: Path, jobs: int) -> int:
    t0 = time.monotonic()
    m = measure(pipeline_modules(), with_derived=True)
    problems = [f"child: {e}" for e in m["errors"]] + derived_problems(m["derived"])
    for p in problems:
        print(f"PROBLEM {p}")
    if problems:
        print("build-inputs stopped; nothing written")
        return 1
    paths = [d["path"] for d in m["derived"]]
    cache = out.with_name(out.name + ".partial.tsv")
    print(f"hashing {len(paths)} derived inputs with {min(jobs, MAX_HASH_JOBS)} process(es) at nice {HASH_NICE} "
          f"(resumable: {cache})", flush=True)
    hashed = hash_files(paths, jobs, cache)
    out.write_text(render_inputs(hashed), encoding="utf-8")
    write_provenance(out.with_name(out.name + ".provenance.tsv"),
                     [("derived-input", d["path"], "; ".join(d["how"])) for d in m["derived"]])
    cache.unlink()
    total = sum(size for size, _d in hashed.values())
    print(f"wrote {out}: {len(hashed)} files, {total} bytes ({total / 2**30:.1f} GiB), "
          f"{time.monotonic() - t0:.0f} s wall; sha256 {sha256_file(out)}")
    return 0


def verify_inputs(text: str, jobs: int) -> list[str]:
    _env, sections = parse(text)
    entries = sections.get("derived inputs", {})
    present = [p for p in entries if os.path.isfile(p)]
    diffs = [f"MISSING input: {p}" for p in sorted(set(entries) - set(present))]
    hashed = hash_files(present, jobs)
    diffs += [f"CHANGED input: {p}" for p in sorted(present) if hashed[p][1] != entries[p]]
    return diffs


# ----------------------------------------------------------------------------------------------- build
def build_text(inputs: Path | None = None) -> tuple[str, list[tuple[str, str, str]], list[str], list[str], dict]:
    m = measure(pipeline_modules(), with_derived=inputs is not None)
    sections, rows, problems, warnings = assemble(m, inputs)
    if m["versions"] != env_versions():
        problems.append(f"child versions {m['versions']} != this interpreter's {env_versions()}")
    if inputs is not None:
        if not is_inputs_manifest(inputs):
            problems.append(f"{inputs} is not a derived-inputs manifest (run build-inputs first)")
        else:
            listed = set(parse(inputs.read_text(encoding="utf-8"))[1].get("derived inputs", {}))
            now = {d["path"] for d in m["derived"]}
            problems += derived_problems(m["derived"])
            problems += [f"derived input not in {rel(inputs)}: {p}" for p in sorted(now - listed)]
            problems += [f"{rel(inputs)} lists a file the loaders no longer name: {p}" for p in sorted(listed - now)]
    return render(m["versions"], sections), rows, problems, warnings, m


def write_provenance(path: Path, rows: list[tuple[str, str, str]]) -> None:
    lines = ["kind\tpath\tdetail"] + [f"{k}\t{p}\t{d}" for k, p, d in sorted(set(rows))]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def cmd_build(out: Path, inputs: Path, allow_unclassified: bool) -> int:
    text, rows, problems, warnings, m = build_text(inputs)
    stopping = [p for p in problems if not (allow_unclassified and p.startswith("unclassified"))]
    for w in warnings:
        print(f"WARNING {w}")
    for p in problems:
        print(f"PROBLEM {p}")
    if stopping:
        print(f"build stopped: {len(stopping)} problem(s); nothing written")
        return 1
    out.write_text(text, encoding="utf-8")
    prov = out.with_name(out.name + ".provenance.tsv")
    write_provenance(prov, rows)
    _env, sections = parse(text)
    for name, entries in sections.items():
        print(f"section {name}: {len(entries)} files")
    kinds = defaultdict(int)
    for k, _p, _d in set(rows):
        kinds[k] += 1
    print("provenance kinds: " + ", ".join(f"{k} {n}" for k, n in sorted(kinds.items())))
    print(f"wrote {out} and {prov}")
    print(f"pipeline sha256 {sha256_file(out)}")
    return 0


# ----------------------------------------------------------------------------------------------- verify
def verify_lines(text: str, repo: Path = REPO, env_now: dict | None = None) -> list[str]:
    env, sections = parse(text)
    diffs = []
    for name, entries in sections.items():
        for path, digest in sorted(entries.items()):
            p = repo / path
            if not p.is_file():
                diffs.append(f"MISSING {name}: {path}")
            elif sha256_file(p) != digest:
                diffs.append(f"CHANGED {name}: {path}")
    env_now = env_versions() if env_now is None else env_now
    for key, value in env.items():
        if env_now.get(key) != value:
            diffs.append(f"ENV {key}: frozen {value}, now {env_now.get(key)}")
    return diffs


def cmd_verify(freeze: Path, remeasure: bool, skip_inputs: bool, jobs: int) -> int:
    text = freeze.read_text(encoding="utf-8")
    diffs = verify_lines(text)
    manifests = [REPO / p for p in parse(text)[1].get("pipeline", {}) if is_inputs_manifest(REPO / p)]
    n_inputs = 0
    for man in manifests:
        if skip_inputs:
            print(f"NOTE {rel(man)}: derived inputs NOT re-hashed (--skip-inputs)")
            continue
        t0 = time.monotonic()
        man_text = man.read_text(encoding="utf-8")
        n_inputs += len(parse(man_text)[1].get("derived inputs", {}))
        found = verify_inputs(man_text, jobs)
        print(f"{rel(man)}: re-hashed {n_inputs} derived inputs in {time.monotonic() - t0:.0f} s, "
              f"{len(found)} difference(s)")
        diffs += found
    if remeasure:
        rebuilt, _rows, problems, _w, _m = build_text(manifests[0] if manifests else None)
        diffs += [f"REMEASURE problem: {p}" for p in problems]
        _e0, old = parse(text)
        _e1, new = parse(rebuilt)
        for name in SECTIONS:
            a, b = set(old.get(name, {})), set(new.get(name, {}))
            diffs += [f"REMEASURE added to {name}: {p}" for p in sorted(b - a)]
            diffs += [f"REMEASURE dropped from {name}: {p}" for p in sorted(a - b)]
        if not diffs and rebuilt != text:
            diffs.append("REMEASURE the rebuilt list differs from the frozen file")
    for d in diffs:
        print(d)
    n = sum(len(v) for v in parse(text)[1].values())
    print(f"verify {freeze}: {n} files" + (f" + {n_inputs} derived inputs" if n_inputs else "") +
          f", {len(diffs)} difference(s)" + (" (remeasured)" if remeasure else ""))
    return 1 if diffs else 0


# ----------------------------------------------------------------------------------------------- check-proofs
def _closure(roots: tuple[str, ...], pipe: Path) -> list[str]:
    """search33.pipeline_files / run_proofs33.pipeline_closure: the AST walk over pipeline/ module names."""
    seen: dict[str, Path] = {}
    todo = list(roots)
    while todo:
        name = todo.pop()
        path = pipe / f"{name}.py"
        if name in seen or not path.exists():
            continue
        seen[name] = path
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.Import):
                todo += [a.name.split(".")[0] for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                todo.append(node.module.split(".")[0])
    return sorted(seen)


def engine_sha_from_list(pipeline: dict[str, str], pipe: Path = PIPE, repo: Path = REPO) -> str | None:
    h = hashlib.sha256()
    for name in _closure(ENGINE_ROOTS, pipe):
        digest = pipeline.get(rel(pipe / f"{name}.py", repo))
        if digest is None:
            return None
        h.update(f"{name}.py".encode() + b"\0" + bytes.fromhex(digest))
    return h.hexdigest()


def _manifest_path_of(name: str, pipeline: dict[str, str], repo: Path, pipe: Path, p7_dir: Path) -> str | None:
    for d in (pipe, p7_dir):
        r = rel(d / name, repo)
        if r in pipeline:
            return r
    same = [r for r in pipeline if Path(r).name == name]
    return same[0] if len(same) == 1 else None


def proof_lines(text: str, manifest: dict, repo: Path = REPO, pipe: Path = PIPE,
                p7_dir: Path = P7_DIR) -> tuple[list[str], list[str]]:
    """(report lines, failures) of the R-L3 check: every manifest file, uv.lock, versions and the engine sha."""
    env, sections = parse(text)
    pipeline = sections.get("pipeline", {})
    lines, fails = [], []
    for name, digest in sorted(manifest.get("code_sha256", {}).items()):
        r = _manifest_path_of(name, pipeline, repo, pipe, p7_dir)
        ok = r is not None and pipeline[r] == digest
        lines.append(f"{'OK  ' if ok else 'DIFF'} {name} -> {r or 'not in the pipeline section'}")
        if not ok:
            fails.append(f"manifest file {name}: {r or 'missing'}")
    versions = manifest.get("versions", {})
    lock = versions.get("uv_lock_sha256")
    ok = lock is not None and pipeline.get("uv.lock") == lock
    lines.append(f"{'OK  ' if ok else 'DIFF'} uv.lock (manifest versions.uv_lock_sha256)")
    if not ok:
        fails.append("uv.lock")
    for header, key in (("python", "python"),) + LIBRARIES:
        ok = key in versions and env.get(header) == versions[key]
        lines.append(f"{'OK  ' if ok else 'DIFF'} env {header}: list {env.get(header)}, manifest {versions.get(key)}")
        if not ok:
            fails.append(f"env {header}")
    if "engine_pipeline_sha" in manifest:
        sha = engine_sha_from_list(pipeline, pipe, repo)
        ok = sha == manifest["engine_pipeline_sha"]
        lines.append(f"{'OK  ' if ok else 'DIFF'} engine_pipeline_sha recomputed from the list ({sha})")
        if not ok:
            fails.append("engine_pipeline_sha")
    return lines, fails


def unpinned_evidence(digest: str, mtime: datetime, created: datetime, git_state: str,
                      pinned_text: dict[str, str]) -> tuple[bool, str]:
    """Evidence that a file the manifest does not pin was the same when the proof run started: its sha256 is written
    in a manifest-pinned file (guard33's pins), or it was last modified before the start and equals git HEAD."""
    pins = sorted(p for p, t in pinned_text.items() if digest in t)
    note = f"mtime {mtime:%Y-%m-%d %H:%M %Z}, {git_state}" + (f", sha256 pinned in {', '.join(pins)}" if pins else "")
    return bool(pins) or (mtime < created and git_state == "same as HEAD"), note


def _git_state(r: str) -> str:
    tracked = subprocess.run(["git", "ls-files", "--error-unmatch", r], cwd=REPO, capture_output=True).returncode
    if tracked != 0:
        return "untracked"
    clean = subprocess.run(["git", "diff", "--quiet", "HEAD", "--", r], cwd=REPO).returncode == 0
    return "same as HEAD" if clean else "differs from HEAD"


def cmd_check_proofs(freeze: Path, manifest_path: Path) -> int:
    text = freeze.read_text(encoding="utf-8")
    manifest = json.loads(manifest_path.read_text())
    lines, fails = proof_lines(text, manifest)
    for line in lines:
        print(line)
    created = datetime.strptime(manifest["created"][:19], "%Y-%m-%d %H:%M:%S").replace(tzinfo=PT)
    pinned = {_manifest_path_of(n, parse(text)[1]["pipeline"], REPO, PIPE, P7_DIR) for n in manifest["code_sha256"]}
    m = measure(PROOF_ROOTS, loaded_probes_only=True)
    proof_code = {rel(f) for f in m["loaded"]} | {rel(p) for _ph, p, mode in m["opens"]
                                                   if in_repo(p) and "r" in mode and os.path.isfile(p)}
    pipeline = parse(text)[1]["pipeline"]
    pinned_text = {r: (REPO / r).read_text(encoding="utf-8", errors="replace") for r in pinned if r}
    weak = []
    print(f"files the proof run can execute or read (measured from {', '.join(PROOF_ROOTS)}) that the manifest does "
          f"not pin; proof run created {manifest['created']}:")
    for r in sorted(proof_code - pinned - {"uv.lock"}):
        if r not in pipeline:
            weak.append(r)
            print(f"  NOT IN LIST {r}")
            continue
        mtime = datetime.fromtimestamp(os.stat(REPO / r).st_mtime, PT)
        ok, note = unpinned_evidence(pipeline[r], mtime, created, _git_state(r), pinned_text)
        if not ok:
            weak.append(r)
        print(f"  {'ok  ' if ok else 'WEAK'} {r}: {note}")
    print(f"check-proofs: {len(fails)} manifest difference(s); {len(weak)} unpinned file(s) with weak evidence")
    if fails:
        return 1
    return 2 if weak else 0


# ----------------------------------------------------------------------------------------------- CLI
def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    i = sub.add_parser("build-inputs")
    i.add_argument("--out", required=True, type=Path)
    i.add_argument("--jobs", type=int, default=MAX_HASH_JOBS, help=f"hashing processes (at most {MAX_HASH_JOBS})")
    b = sub.add_parser("build")
    b.add_argument("--out", required=True, type=Path)
    b.add_argument("--inputs", required=True, type=Path, help="the derived-inputs manifest from build-inputs")
    b.add_argument("--allow-unclassified", action="store_true",
                   help="write the list although some path constants are unclassified (they are not hashed)")
    v = sub.add_parser("verify")
    v.add_argument("--freeze", required=True, type=Path)
    v.add_argument("--remeasure", action="store_true", help="also rebuild and compare the file sets")
    v.add_argument("--skip-inputs", action="store_true", help="do not re-hash the derived inputs (reported)")
    v.add_argument("--jobs", type=int, default=MAX_HASH_JOBS)
    c = sub.add_parser("check-proofs")
    c.add_argument("--freeze", required=True, type=Path)
    c.add_argument("--manifest", type=Path, default=PROOF_MANIFEST)
    x = sub.add_parser("_measure")
    x.add_argument("--roots", required=True)
    x.add_argument("--json-out", required=True, type=Path)
    x.add_argument("--no-probes", action="store_true")
    x.add_argument("--loaded-probes-only", action="store_true")
    x.add_argument("--derived", action="store_true")
    args = ap.parse_args(argv)
    if args.cmd == "build-inputs":
        return cmd_build_inputs(args.out.resolve(), args.jobs)
    if args.cmd == "build":
        return cmd_build(args.out.resolve(), args.inputs.resolve(), args.allow_unclassified)
    if args.cmd == "verify":
        return cmd_verify(args.freeze.resolve(), args.remeasure, args.skip_inputs, args.jobs)
    if args.cmd == "check-proofs":
        return cmd_check_proofs(args.freeze.resolve(), args.manifest)
    child([r for r in args.roots.split(",") if r], not args.no_probes, args.json_out, args.loaded_probes_only,
          args.derived)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
