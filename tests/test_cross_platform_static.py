"""Cross-platform static check (Stage E.2b Task 5, user decision V10).

The files Stage E runs on the Windows PC (rules/, sim/, screening/, funnel/, the data loaders and
calendars in data/, ml_route/, compute/, strategy/stage_e/) must not call anything that exists
only on Linux or behaves differently on native Windows Python. The check walks each file's AST
and flags:
- POSIX-only modules: fcntl, resource, termios, pty, tty, grp, pwd, posix, crypt, spwd, syslog;
- os.fork / forkpty / setsid / setpgid / setpgrp / getpgid / killpg / getuid / geteuid / getgid /
  getegid / sysconf / statvfs / uname / getloadavg / mkfifo / chown / lchown / sched_*affinity /
  symlink, os.kill (it terminates the process on Windows whatever the signal), os.system /
  os.popen and subprocess.getoutput / getstatusoutput (they go through the platform shell),
  os.nice outside compute/platform.py, shutil.chown, time.tzset, select.select / poll / epoll,
  loop.add_signal_handler;
- signal.SIGKILL / SIGALRM / SIGHUP / SIGUSR1 / SIGUSR2 / SIGCHLD / SIGQUIT / SIGSTOP / SIGCONT /
  SIGPIPE / SIGTSTP, signal.alarm / setitimer / getitimer / pause / siginterrupt;
- shell=True; a subprocess call given one command string; an argv of sh or bash with -c;
- multiprocessing's 'fork' or 'forkserver' context, and multiprocessing.Pool / Process or
  ProcessPoolExecutor used without an explicit spawn context;
- string literals naming /proc, /dev/shm, /dev/null, /tmp, /bin/, /usr/bin/, /etc/;
- strftime formats with the glibc-only '%-' flag;
- text files opened without an encoding (open(), Path.open(), read_text(), write_text()): the
  Windows default is the ANSI code page, so the same file can read differently on the PC.
compute/platform.py is the one module where platform branches live (its POSIX calls sit in the
non-Windows branch): os.nice and os.sysconf are allowed there only.

Scope ("the parts Stage E runs"): every module under compute/, ml_route/ and strategy/stage_e/,
and every module of rules/, sim/, screening/, funnel/ and data/ in the static import closure of
the modules the far side runs (compute.agent and each job kind's module in compute.jobspec.KINDS),
function-level imports included. Modules that by V10's design never run on the PC (purchases,
sealing, the ledger, and the builder that reads raw vendor files, which never travel) are exempt
by name below, each with its reason. There is no other allowlist: a finding in a file owned by
another worker or frozen by an earlier stage is routed to the lead, never exempted to pass.
Text-file encodings are enforced in compute/ (the agent's own process); elsewhere the agent runs
every job with PYTHONUTF8=1, which makes UTF-8 the default on Windows, so they are reported by
tests/test_cross_platform_static.py's report helper but do not fail the check.
"""
from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
FULL_DIRS = ("compute", "ml_route", "strategy/stage_e")
CLOSURE_DIRS = ("rules", "sim", "screening", "funnel", "data")
PACKAGES = ("rules", "sim", "screening", "funnel", "data", "ml_route", "compute", "strategy")
EXEMPT = {  # ThinkPad-only by V10's design: purchases, sealing, the ledger (V10-4)
    "data/pull_mes.py": "MES purchase path (Databento downloads); purchases stay on the ThinkPad",
    "data/pull_universe.py": "Stage E step 1 purchase path; purchases stay on the ThinkPad",
    "data/pull_step2.py": "step 2 purchase path; purchases stay on the ThinkPad",
    "data/pull_step2_report.py": "step 2 purchase quotes report; purchases stay on the ThinkPad",
    "data/quote_universe.py": "vendor quotes for purchases; purchases stay on the ThinkPad",
    "data/holdout.py": "sealing and the unlock ceremony; sealing stays on the ThinkPad",
    "data/step2_seal.py": "holdout-2 sealing of step 2 chunks; sealing stays on the ThinkPad",
    "data/spend_gate.py": "the spend ledger's gate; the ledger never leaves the ThinkPad",
    "data/build_bars_run.py": "the research-store builder's CLI: it reads raw vendor files, which "
                              "never leave the ThinkPad (V10-4: only built stores travel); only "
                              "data.build_bars.cli imports it, lazily",
}
PLATFORM_MODULE = "compute/platform.py"
# Lead-reviewed findings (Stage E.2b ruling OC-O): each entry names one exact finding and why the
# code is portable as written. It is not a scope exemption: the file stays in scope, and
# test_reviewed_findings_are_still_real fails if an entry stops matching a real finding.
REVIEWED_PORTABLE = {
    ("funnel/simulator.py", "ProcessPoolExecutor without mp_context (spawn)"):
        "run_many's pool takes the platform default, which is spawn on Windows; its initializer "
        "_init_worker and its function _run_chunk are module-level and its state travels in "
        "initargs, so it runs the same under spawn. The file is frozen by D.1f and is part of the "
        "recorded provenance of E.2a's epsilon (funnel/exposure_gate_run.COMPUTE_CODE), so it is "
        "not edited; the PC imports it only through screening/runner.py -> funnel.power_gate.",
}
PLATFORM_ALLOWED = {"os.nice", "os.sysconf"}
POSIX_MODULES = {"fcntl", "resource", "termios", "pty", "tty", "grp", "pwd", "posix", "crypt",
                 "spwd", "syslog"}
OS_CALLS = {"fork", "forkpty", "setsid", "setpgid", "setpgrp", "getpgid", "killpg", "getuid",
            "geteuid", "getgid", "getegid", "sysconf", "statvfs", "uname", "getloadavg",
            "mkfifo", "chown", "lchown", "sched_getaffinity", "sched_setaffinity", "symlink",
            "kill", "system", "popen", "nice", "wait3", "wait4"}
MODULE_ATTRS = {("shutil", "chown"), ("time", "tzset"), ("select", "select"),
                ("select", "poll"), ("select", "epoll"), ("subprocess", "getoutput"),
                ("subprocess", "getstatusoutput")}
SIGNAL_ATTRS = {"SIGKILL", "SIGALRM", "SIGHUP", "SIGUSR1", "SIGUSR2", "SIGCHLD", "SIGQUIT",
                "SIGSTOP", "SIGCONT", "SIGPIPE", "SIGTSTP", "alarm", "setitimer", "getitimer",
                "pause", "siginterrupt"}
SUBPROCESS_CALLS = {"run", "Popen", "call", "check_call", "check_output"}
SHELLS = {"sh", "bash", "/bin/sh", "/bin/bash", "/usr/bin/bash", "zsh", "dash"}
PATH_PREFIXES = ("/proc", "/dev/shm", "/dev/null", "/tmp", "/bin/", "/usr/bin/", "/etc/")
TEXT_MODES = {"r", "w", "a", "x", "rt", "wt", "at", "xt", "r+", "w+", "a+", "r+t", "w+t"}


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    what: str

    def __str__(self) -> str:
        return f"{self.path}:{self.line}: {self.what}"


def pc_entry_modules() -> tuple[str, ...]:
    from compute.jobspec import KINDS

    return ("compute.agent", *sorted({kind.module for kind in KINDS.values()}))


def _module_path(module: str) -> Path | None:
    base = REPO / Path(*module.split("."))
    if base.with_suffix(".py").is_file():
        return base.with_suffix(".py")
    if (base / "__init__.py").is_file():
        return base / "__init__.py"
    return None


def _imported_modules(path: Path, module: str) -> set[str]:
    package = module if path.name == "__init__.py" else module.rpartition(".")[0]
    out: set[str] = set()
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            out.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                parts = package.split(".")
                parts = parts[:len(parts) - (node.level - 1)]
                base = ".".join(parts + ([node.module] if node.module else []))
            else:
                base = node.module or ""
            out.add(base)
            out.update(f"{base}.{alias.name}" for alias in node.names)
    return out


def import_closure(entries: tuple[str, ...]) -> set[str]:
    """Repo files reachable from ``entries`` by import statements anywhere in a module."""
    seen: dict[str, Path] = {}
    stack = list(entries)
    while stack:
        module = stack.pop()
        if module in seen or module.split(".")[0] not in PACKAGES:
            continue
        path = _module_path(module)
        if path is None:
            continue
        seen[module] = path
        parts = module.split(".")
        stack.extend(".".join(parts[:i]) for i in range(1, len(parts)))
        stack.extend(_imported_modules(path, module))
    return {p.relative_to(REPO).as_posix() for p in seen.values()}


def all_files(directories: tuple[str, ...]) -> list[str]:
    return sorted(p.relative_to(REPO).as_posix() for d in directories
                  for p in (REPO / d).rglob("*.py") if "__pycache__" not in p.parts)


def scope_files() -> list[str]:
    closure = import_closure(pc_entry_modules())
    chosen = set(all_files(FULL_DIRS)) | {rel for rel in all_files(CLOSURE_DIRS) if rel in closure}
    return sorted(chosen - set(EXEMPT))


def _dotted(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = _dotted(node.value)
        return None if base is None else f"{base}.{node.attr}"
    return None


def _const_str(node: ast.AST | None) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _kw(call: ast.Call, name: str) -> ast.keyword | None:
    return next((k for k in call.keywords if k.arg == name), None)


def _docstring_ids(tree: ast.AST) -> set[int]:
    ids = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            body = getattr(node, "body", [])
            if body and isinstance(body[0], ast.Expr) and _const_str(body[0].value) is not None:
                ids.add(id(body[0].value))
    return ids


class Scanner(ast.NodeVisitor):
    def __init__(self, rel: str) -> None:
        self.rel = rel
        self.findings: list[Finding] = []
        self.aliases: dict[str, str] = {}  # local name -> module or module.attr it binds

    def flag(self, node: ast.AST, what: str) -> None:
        self.findings.append(Finding(self.rel, getattr(node, "lineno", 0), what))

    def resolve(self, node: ast.AST) -> str | None:
        dotted = _dotted(node)
        if dotted is None:
            return None
        head, _, rest = dotted.partition(".")
        base = self.aliases.get(head, head)
        return f"{base}.{rest}" if rest else base

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            top = alias.name.split(".")[0]
            if top in POSIX_MODULES:
                self.flag(node, f"imports POSIX-only module {alias.name}")
            self.aliases[alias.asname or top] = alias.name if alias.asname else top
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        module = node.module or ""
        if module.split(".")[0] in POSIX_MODULES:
            self.flag(node, f"imports from POSIX-only module {module}")
        for alias in node.names:
            self.aliases[alias.asname or alias.name] = f"{module}.{alias.name}"
            if module == "os" and alias.name in OS_CALLS:
                self.flag(node, f"imports os.{alias.name}")
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        name = self.resolve(node)
        if name:
            self._check_name(node, name)
        self.generic_visit(node)

    def _check_name(self, node: ast.AST, name: str) -> None:
        module, _, attr = name.rpartition(".")
        if module == "os" and attr in OS_CALLS:
            allowed = self.rel == PLATFORM_MODULE and name in PLATFORM_ALLOWED
            if not allowed:
                self.flag(node, f"uses {name} (POSIX-only or different on Windows)")
        elif module == "signal" and attr in SIGNAL_ATTRS:
            self.flag(node, f"uses {name} (not on Windows)")
        elif (module, attr) in MODULE_ATTRS:
            self.flag(node, f"uses {name} (POSIX-only or shell-dependent)")
        elif attr == "add_signal_handler":
            self.flag(node, "uses loop.add_signal_handler (not on Windows)")

    def visit_Call(self, node: ast.Call) -> None:
        name = self.resolve(node.func) or ""
        shell = _kw(node, "shell")
        if shell is not None and isinstance(shell.value, ast.Constant) and shell.value.value:
            self.flag(node, "shell=True")
        module, _, attr = name.rpartition(".")
        if module == "subprocess" and attr in SUBPROCESS_CALLS and node.args:
            first = node.args[0]
            if _const_str(first) is not None or isinstance(first, ast.JoinedStr):
                self.flag(node, f"{name} given one command string")
        if name.endswith(("get_context", "set_start_method")) and node.args:
            method = _const_str(node.args[0])
            if method in ("fork", "forkserver"):
                self.flag(node, f"multiprocessing '{method}' start method")
        if name in ("multiprocessing.Pool", "multiprocessing.Process",
                    "multiprocessing.pool.Pool"):
            self.flag(node, f"{name} without an explicit spawn context")
        if name.endswith("ProcessPoolExecutor") and _kw(node, "mp_context") is None:
            self.flag(node, "ProcessPoolExecutor without mp_context (spawn)")
        if attr == "strftime" or name == "strftime":
            fmt = _const_str(node.args[0]) if node.args else None
            if fmt and "%-" in fmt:
                self.flag(node, f"strftime format {fmt!r} uses the glibc-only '%-' flag")
        self._check_text_open(node, name)
        self.generic_visit(node)

    def _check_text_open(self, node: ast.Call, name: str) -> None:
        if _kw(node, "encoding") is not None:
            return
        attr = name.rpartition(".")[2] if name else (
            node.func.attr if isinstance(node.func, ast.Attribute) else "")
        if name == "open" or (isinstance(node.func, ast.Attribute) and attr == "open"
                              and not name.startswith(("gzip.", "bz2.", "lzma.", "zipfile.",
                                                       "tarfile.", "io.BytesIO"))):
            mode_node = node.args[1] if name == "open" and len(node.args) > 1 else (
                node.args[0] if name != "open" and node.args else None)
            mode_kw = _kw(node, "mode")
            mode = _const_str(mode_kw.value if mode_kw else mode_node)
            if (mode is None and mode_node is None and mode_kw is None) or mode in TEXT_MODES:
                self.flag(node, f"{name or attr}() opens a text file without encoding=")
        elif isinstance(node.func, ast.Attribute) and attr in ("read_text", "write_text"):
            self.flag(node, f"{attr}() without encoding=")

    def visit_List(self, node: ast.List) -> None:
        self._check_argv(node, node.elts)
        self.generic_visit(node)

    def visit_Tuple(self, node: ast.Tuple) -> None:
        self._check_argv(node, node.elts)
        self.generic_visit(node)

    def _check_argv(self, node: ast.AST, elts: list[ast.expr]) -> None:
        values = [_const_str(e) for e in elts]
        for i, value in enumerate(values[:-1]):
            if value in SHELLS and values[i + 1] == "-c":
                self.flag(node, f"argv runs {value} -c")


def scan_file(rel: str) -> list[Finding]:
    return scan_source(rel, (REPO / rel).read_text(encoding="utf-8"))


def scan_source(rel: str, source: str) -> list[Finding]:
    tree = ast.parse(source, filename=rel)
    scanner = Scanner(rel)
    scanner.visit(tree)
    docstrings = _docstring_ids(tree)
    for node in ast.walk(tree):
        text = _const_str(node)
        if text is None or id(node) in docstrings:
            continue
        for prefix in PATH_PREFIXES:
            if text == prefix.rstrip("/") or text.startswith(prefix.rstrip("/") + "/"):
                scanner.flag(node, f"hard-coded path {text!r}")
                break
    return scanner.findings


def scan(files: list[str]) -> list[Finding]:
    return [finding for rel in files for finding in scan_file(rel)]


# ------------------------------------------------------------------ tests ----
def _hard(findings: list[Finding]) -> list[Finding]:
    return [f for f in findings if "without encoding" not in f.what]


def test_scope_holds_the_far_sides_entry_points_and_exemptions_are_real_files() -> None:
    files = scope_files()
    for rel in ("compute/agent.py", "compute/synthetic_job.py", "screening/stage_e_runner.py",
                "screening/harness_freeze.py", "ml_route/train.py", "ml_route/probes.py",
                "data/stage_e_bars.py", "data/research_bars.py", "rules/sessions.py"):
        assert rel in files, rel
    assert not set(EXEMPT) & set(files)
    missing = [rel for rel in EXEMPT if not (REPO / rel).is_file()]
    assert not missing, f"exempt files that do not exist: {missing}"
    assert all(reason.strip() for reason in EXEMPT.values())


def test_scanner_flags_each_kind_of_linux_only_call() -> None:
    sample = '''
import fcntl, os, signal, subprocess, multiprocessing, time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
os.fork(); os.nice(5); os.killpg(1, signal.SIGKILL); os.kill(1, 0)
signal.alarm(3)
subprocess.run("ls -l", shell=True)
subprocess.run(["bash", "-c", "echo hi"])
multiprocessing.get_context("fork")
multiprocessing.Pool(2)
ProcessPoolExecutor(2)
x = "/proc/meminfo"; y = "/dev/shm/a"; z = "/tmp/x"
time.strftime("%-d")
open("f.txt"); open("f.txt", "w"); Path("f").read_text(); Path("f").open("r")
open("f.bin", "rb"); open("f.txt", encoding="utf-8"); Path("f").read_text(encoding="utf-8")
ProcessPoolExecutor(2, mp_context=multiprocessing.get_context("spawn"))
'''
    found = [f.what for f in scan_source("compute/_sample.py", sample)]
    expected = ["POSIX-only module fcntl", "os.fork", "os.nice", "os.killpg", "signal.SIGKILL",
                "os.kill", "signal.alarm", "shell=True", "one command string", "bash -c",
                "'fork' start method", "multiprocessing.Pool", "ProcessPoolExecutor",
                "'/proc/meminfo'", "'/dev/shm/a'", "'/tmp/x'", "'%-'"]
    for fragment in expected:
        assert any(fragment in f for f in found), f"not flagged: {fragment}"
    assert sum("ProcessPoolExecutor" in f for f in found) == 1  # the spawn one passes
    text_opens = [f for f in found if "without encoding" in f]
    assert len(text_opens) == 4, text_opens  # the three explicit-safe calls are not flagged


def test_platform_module_may_branch_but_nothing_else_may() -> None:
    findings = scan([PLATFORM_MODULE])
    assert findings == [], [str(f) for f in findings]
    elsewhere = scan_source("compute/other.py", "import os\nos.nice(1)\nos.sysconf('x')\n")
    assert len(elsewhere) == 2


def test_compute_opens_every_text_file_with_an_encoding() -> None:
    findings = scan(all_files(("compute",)))
    assert findings == [], "\n" + "\n".join(str(f) for f in findings)


def _reviewed(finding) -> bool:
    return (finding.path, finding.what) in REVIEWED_PORTABLE


def test_no_linux_only_calls_in_files_that_run_on_the_windows_pc() -> None:
    findings = [f for f in _hard(scan(scope_files())) if not _reviewed(f)]
    assert findings == [], "\n" + "\n".join(str(f) for f in findings)


def test_reviewed_findings_are_still_real() -> None:
    found = {(f.path, f.what) for f in _hard(scan(scope_files()))}
    stale = [key for key in REVIEWED_PORTABLE if key not in found]
    assert not stale, f"reviewed entries that no longer match a finding: {stale}"
    assert all(reason.strip() for reason in REVIEWED_PORTABLE.values())


def report() -> dict[str, list[str]]:
    """Every finding in the brief's directories, in scope or not (for the worker report)."""
    every = all_files((*CLOSURE_DIRS, *FULL_DIRS))
    scoped = set(scope_files())
    out: dict[str, list[str]] = {"in_scope_hard": [], "in_scope_encoding": [],
                                 "outside_scope_hard": [], "outside_scope_encoding": []}
    for finding in scan(every):
        where = "in_scope" if finding.path in scoped else "outside_scope"
        kind = "encoding" if "without encoding" in finding.what else "hard"
        out[f"{where}_{kind}"].append(str(finding))
    return out
