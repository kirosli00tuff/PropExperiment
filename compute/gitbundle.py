"""Code sync without credentials: the frozen harness commit as a one-commit git bundle (V10-4).

Send side (``build_export``): the frozen harness commit's tree, minus the paths that never leave
the ThinkPad (the ledger, which is tracked in git), becomes a parentless "export" commit with a
fixed author, committer and date, so the same source commit always gives the same export commit
id. No history travels, so no earlier version of any file does either. Every blob of the export
is checked first (the data rules of compute.datarules: no .env, nothing sealed, no bar file, no
blob containing the Databento key), and the export is bundled from a scratch repository that
borrows the source repository's objects read-only (git alternates); the source repository's refs,
index and working tree are never touched.

Far side (``checkout_problems``): the checkout must be the export commit, byte for byte. The
agent pins ``core.autocrlf=false`` in the clone's own config and writes ``.git/info/attributes``
with ``* -text`` (the highest-precedence attributes file), so no line-ending or filter conversion
applies whatever the machine's global settings are; then every tracked file's raw bytes are
hashed as a git blob and compared with the commit's tree. Git's own status would hide a CRLF
conversion (it compares after normalizing), so it is not used for this.
"""
from __future__ import annotations

import hashlib
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path

from compute.datarules import SEALED_MAGIC, SEALED_SUFFIX

EXCLUDED_PREFIXES = ("ledger/",)  # V10-4: the spend ledger never goes to the PC
FORBIDDEN_SUFFIXES = (".parquet", ".dbn", ".zst", SEALED_SUFFIX)  # bars travel as data, checked
EXPORT_REF = "refs/heads/harness"
INFO_ATTRIBUTES = "* -text -filter -ident -working-tree-encoding\n"
EXPORT_IDENTITY = {
    "GIT_AUTHOR_NAME": "PropExperiment compute export",
    "GIT_AUTHOR_EMAIL": "compute-export@propexperiment.invalid",
    "GIT_AUTHOR_DATE": "2000-01-01T00:00:00+0000",
    "GIT_COMMITTER_NAME": "PropExperiment compute export",
    "GIT_COMMITTER_EMAIL": "compute-export@propexperiment.invalid",
    "GIT_COMMITTER_DATE": "2000-01-01T00:00:00+0000",
}
GIT_TIMEOUT_S = 600
REGULAR_MODES = ("100644", "100755")


class GitFailed(RuntimeError):
    """A git command failed."""


class ExportRefused(RuntimeError):
    """The harness commit holds something that may not leave the ThinkPad."""


def git(args: list[str], *, cwd: Path | None = None, env: dict[str, str] | None = None,
        stdin: bytes | None = None) -> bytes:
    full_env = {**os.environ, **(env or {})}
    done = subprocess.run(["git", *args], cwd=None if cwd is None else str(cwd), env=full_env,
                          input=stdin, capture_output=True, timeout=GIT_TIMEOUT_S, check=False)
    if done.returncode != 0:
        raise GitFailed(f"git {' '.join(args[:3])} ... failed ({done.returncode}): "
                        f"{done.stderr.decode('utf-8', errors='replace').strip()[:500]}")
    return done.stdout


@dataclass(frozen=True)
class TreeEntry:
    mode: str
    kind: str
    sha: str
    path: str


def tree_entries(commit: str, *, cwd: Path) -> list[TreeEntry]:
    out = git(["ls-tree", "-r", "-z", "--full-tree", commit], cwd=cwd)
    entries = []
    for record in out.split(b"\0"):
        if not record:
            continue
        head, path = record.split(b"\t", 1)
        mode, kind, sha = head.decode("ascii").split()
        entries.append(TreeEntry(mode, kind, sha, path.decode("utf-8")))
    return entries


def read_blobs(shas: list[str], *, cwd: Path) -> dict[str, bytes]:
    """The raw contents of the given blobs (git cat-file --batch)."""
    if not shas:
        return {}
    out = git(["cat-file", "--batch"], cwd=cwd, stdin=("\n".join(shas) + "\n").encode("ascii"))
    blobs: dict[str, bytes] = {}
    pos = 0
    for sha in shas:
        header_end = out.index(b"\n", pos)
        name, kind, size = out[pos:header_end].decode("ascii").split()
        if name != sha or kind != "blob":
            raise GitFailed(f"cat-file returned {name} {kind} for {sha}")
        start = header_end + 1
        blobs[sha] = out[start:start + int(size)]
        pos = start + int(size) + 1
    return blobs


def export_problems(entries: list[TreeEntry], blobs: dict[str, bytes], key: bytes) -> list[str]:
    """Every rule an exported file breaks (empty list: the export may leave)."""
    problems = []
    for entry in entries:
        name = entry.path.rsplit("/", 1)[-1]
        if entry.mode not in REGULAR_MODES:
            problems.append(f"{entry.path}: mode {entry.mode} (only regular files are exported)")
            continue
        if name == ".env" or name.startswith(".env."):
            problems.append(f"{entry.path}: an environment file")
        if name.endswith(FORBIDDEN_SUFFIXES) or "sealed" in entry.path.split("/"):
            problems.append(f"{entry.path}: bar, vendor or sealed files never travel as code")
        data = blobs[entry.sha]
        if data.startswith(SEALED_MAGIC):
            problems.append(f"{entry.path}: a sealed holdout blob")
        if key and key in data:
            problems.append(f"{entry.path}: contains the Databento key")
    return problems


@dataclass(frozen=True)
class Export:
    source_commit: str
    export_commit: str
    tree: str
    excluded: tuple[str, ...]
    files: int
    bundle: Path
    git_dir: Path

    def as_dict(self) -> dict[str, object]:
        return {"source_commit": self.source_commit, "export_commit": self.export_commit,
                "tree": self.tree, "excluded": list(self.excluded), "files": self.files,
                "bundle": str(self.bundle)}


def export_message(source_commit: str, excluded: tuple[str, ...]) -> str:
    return (f"PropExperiment harness export of {source_commit}\n\n"
            f"Excluded (never sent to another machine): {', '.join(excluded) or 'nothing'}\n")


def build_export(repo: Path, rev: str, work_dir: Path, key: bytes) -> Export:
    """Bundle ``rev``'s tree minus EXCLUDED_PREFIXES as a parentless export commit."""
    repo = Path(repo)
    source = git(["rev-parse", "--verify", f"{rev}^{{commit}}"], cwd=repo).decode().strip()
    common = git(["rev-parse", "--path-format=absolute", "--git-common-dir"],
                 cwd=repo).decode().strip()
    entries = tree_entries(source, cwd=repo)
    excluded = tuple(sorted(e.path for e in entries if e.path.startswith(EXCLUDED_PREFIXES)))
    kept = [e for e in entries if not e.path.startswith(EXCLUDED_PREFIXES)]
    problems = export_problems(kept, read_blobs(sorted({e.sha for e in kept
                                                        if e.mode in REGULAR_MODES}), cwd=repo),
                               key)
    if problems:
        shown = "; ".join(problems[:10])
        raise ExportRefused(f"the harness commit {source[:12]} cannot be exported: {shown}"
                            + (f" (and {len(problems) - 10} more)" if len(problems) > 10 else ""))
    work_dir = Path(work_dir)
    git_dir = work_dir / "export.git"
    if not git_dir.is_dir():
        git(["init", "--bare", "-q", str(git_dir)])
    (git_dir / "objects" / "info").mkdir(parents=True, exist_ok=True)
    (git_dir / "objects" / "info" / "alternates").write_text(
        str(Path(common) / "objects") + "\n", encoding="utf-8")
    (git_dir / "info").mkdir(parents=True, exist_ok=True)
    (git_dir / "info" / "attributes").write_text(INFO_ATTRIBUTES, encoding="utf-8")
    index_env = {"GIT_DIR": str(git_dir), "GIT_INDEX_FILE": str(work_dir / "export.index")}
    git(["read-tree", source], env=index_env)
    if excluded:
        removal = "".join(f"0 {'0' * 40}\t{path}\n" for path in excluded).encode("utf-8")
        git(["update-index", "--index-info"], env=index_env, stdin=removal)
    tree = git(["write-tree"], env=index_env).decode().strip()
    export = git(["commit-tree", tree, "-m", export_message(source, excluded)],
                 env={**index_env, **EXPORT_IDENTITY}).decode().strip()
    git(["update-ref", EXPORT_REF, export], env=index_env)
    bundle = work_dir / f"harness-{export[:12]}.bundle"
    git(["bundle", "create", str(bundle), EXPORT_REF], env=index_env)
    git(["bundle", "verify", str(bundle)], env=index_env)
    return Export(source, export, tree, excluded, len(kept), bundle, git_dir)


def materialize(export: Export, dest: Path) -> None:
    """Write the export commit's files into ``dest`` as the far side's checkout gets them."""
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=True)
    env = {"GIT_DIR": str(export.git_dir), "GIT_WORK_TREE": str(dest),
           "GIT_INDEX_FILE": str(dest.parent / (dest.name + ".index"))}
    git(["-c", "core.autocrlf=false", "read-tree", export.export_commit], env=env)
    git(["-c", "core.autocrlf=false", "checkout-index", "-a", "-f"], env=env)


def git_blob_sha1(path: Path) -> str:
    data = Path(path).read_bytes()
    return hashlib.sha1(b"blob %d\0" % len(data) + data, usedforsecurity=False).hexdigest()


def checkout_problems(checkout: Path, commit: str, source_commit: str | None = None
                      ) -> list[str]:
    """Every tracked file of ``commit`` whose raw bytes in ``checkout`` differ from its blob,
    plus a HEAD other than ``commit``, an export message not naming ``source_commit`` and
    missing conversion guards. [] means byte-identical."""
    checkout = Path(checkout)
    head = git(["rev-parse", "HEAD"], cwd=checkout).decode().strip()
    if head != commit:
        return [f"HEAD is {head[:12]}, not the export commit {commit[:12]}"]
    problems = []
    if source_commit is not None:
        message = git(["log", "-1", "--format=%B", commit], cwd=checkout).decode()
        if source_commit not in message:
            problems.append(f"the export commit does not name source commit {source_commit[:12]}")
    autocrlf = subprocess.run(["git", "config", "--get", "core.autocrlf"], cwd=str(checkout),
                              capture_output=True, timeout=GIT_TIMEOUT_S, check=False)
    if autocrlf.stdout.decode().strip() != "false":
        problems.append("core.autocrlf is not false in the checkout's config")
    git_dir = Path(git(["rev-parse", "--absolute-git-dir"], cwd=checkout).decode().strip())
    attributes = git_dir / "info" / "attributes"
    if not attributes.is_file() or attributes.read_text(encoding="utf-8") != INFO_ATTRIBUTES:
        problems.append(".git/info/attributes does not switch every conversion off")
    for entry in tree_entries(commit, cwd=checkout):
        path = checkout / Path(entry.path)
        if entry.mode not in REGULAR_MODES:
            problems.append(f"{entry.path}: mode {entry.mode} is not a regular file")
        elif path.is_symlink() or not path.is_file():
            problems.append(f"{entry.path}: missing from the checkout")
        elif git_blob_sha1(path) != entry.sha:
            problems.append(f"{entry.path}: bytes differ from the commit's blob")
    return problems
