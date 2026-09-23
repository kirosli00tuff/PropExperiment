"""Stage D.1f: the refusal checks the list runner makes before every step and again when step 8
completes (reports/stage_d1f_confirmation_list.md 0, 1.5 step 1b, 5.6; R-4, NEW-1).

It refuses (returns problems; ``_d1f_confirmation`` then writes nothing) when:
1. the list or docs/NULL_CRITERIA.md differs from reports/stage_d1e_declaration_hashes.json
   (the criteria must also embed the list's hash, V-1);
2. the freeze manifest reports/stage_d1f_harness_freeze.json is missing, any file it lists
   differs, its file count is off, any ``*.py`` under strategy/, data/, screening/, sim/,
   funnel/ or rules/ on disk (the runner itself included) is not in it (review F3), or the
   manifest file or ANY file it lists is untracked or has uncommitted changes in git (the
   user's commit is the anchor, and it must hold the frozen sources: review F4);
3. any section-0 sha256 differs. Two carve-outs: the E-H1 and E-H2 modules are checked against
   their post-amendment hashes, which this module holds as literals
   (``EH_POST_AMENDMENT_SHA256``, the values the build session declared) and which the
   manifest's ``declared_amendments`` must repeat (NEW-1, review F1: a re-run of the freeze
   script cannot move them); and, LEAD RULING (build worker's finish), data/cme_calendar.py's
   section-0 line pins only "the 2025-2026 entries": the file at commit 9cbd815 must hash to
   the section-0 value and its 2025-2026 block (``cme_calendar.entries_2025_2026_block``) must
   equal the current file's byte for byte; the current whole file is pinned by the manifest.
   Git must be available;
4. LEAD RULING: the confirmation build summary is missing, its ``stop_for_lead_decision`` is
   set, step 4b did not pass, the degraded-date comparison is missing, the build ran under
   another freeze manifest than this run's (review F2), or the parquet's own metadata
   disagrees with the summary on any of these. A degraded-list difference from the eight
   declared dates is logged, not refused (list 1.3);
5. the holdouts are not clean: holdout-1 all_ok with 0 unlocks, holdout-2 sealed, all_ok, 0
   unlocks.
The manifest's own sha256 is returned and goes into every output JSON; the runner also refuses
unless it equals the value declared on its command line (review F1). Checks 1 to 3
(``hash_checks``) also run before the D.1f quote, rolls, pull and confirmation build
(data/pull_mes.py ``d1f_freeze_check``, review F2).
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from types import MappingProxyType

import pyarrow.parquet as pq

from data.build_mes_bars import CONFIRMATION_SUMMARY_PATH, STOP_KEY
from data.cme_calendar import entries_2025_2026_block
from data.config import REPO_ROOT
from data.research_bars import CONFIRMATION_SERIES_PATH

LIST_PATH = "reports/stage_d1f_confirmation_list.md"
CRITERIA_PATH = "docs/NULL_CRITERIA.md"
DECLARATION_HASHES_PATH = "reports/stage_d1e_declaration_hashes.json"
MANIFEST_PATH = "reports/stage_d1f_harness_freeze.json"
# Review F1: the two declared post-amendment E-H hashes (STATE 7.1), held here as literals so
# that a re-run of the freeze script cannot move them; a sanctioned change is a new literal.
EH_POST_AMENDMENT_SHA256 = MappingProxyType({
    "strategy/research/e_calendar_event/h1_scheduled_macro_drift.py":
        "f28529f058e9a6cc63d1030f6e08ce1b78e7c11c7f89ad64aa583468e1eb7a35",
    "strategy/research/e_calendar_event/h2_post_release_momentum.py":
        "7183d9bda56b36b9089b05b9ee02cbd9609392f29d88f14ca005fb6bb341aeca",
})
EH_AMENDED = tuple(EH_POST_AMENDMENT_SHA256)
# Review F3: every *.py under these directories must be in the manifest (nothing may run on
# import, or shadow a frozen module, without being pinned).
PINNED_PY_DIRS = ("strategy", "data", "screening", "sim", "funnel", "rules")
CME_CALENDAR = "data/cme_calendar.py"
CME_ANCHOR_COMMIT = "9cbd815"
N_SECTION0_ENTRIES = 48
_HEX64 = re.compile(r"\b[0-9a-f]{64}\b")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(Path(path).read_bytes())


@dataclass(frozen=True)
class Section0Entry:
    path: str
    sha256: str
    line: str


def parse_section0(list_text: str) -> tuple[Section0Entry, ...]:
    """Every '- <path> ... <sha256>' line between the '## 0.' and '## 1.' headings."""
    lines = list_text.splitlines()
    starts = [i for i, s in enumerate(lines) if s.startswith("## 0.")]
    ends = [i for i, s in enumerate(lines) if s.startswith("## 1.")]
    if len(starts) != 1 or len(ends) != 1 or ends[0] < starts[0]:
        raise ValueError("cannot locate exactly one section 0 in the list")
    out = []
    for line in lines[starts[0] + 1:ends[0]]:
        found = _HEX64.search(line)
        if line.startswith("- ") and found:
            out.append(Section0Entry(line[2:].split()[0], found.group(0), line))
    return tuple(out)


@dataclass(frozen=True)
class Preflight:
    ok: bool
    problems: tuple[str, ...]
    manifest_sha256: str | None
    records: dict = field(default_factory=dict)


def check_declarations(root: Path) -> list[str]:
    hashes = json.loads((root / DECLARATION_HASHES_PATH).read_text())
    problems = []
    for rel in (LIST_PATH, CRITERIA_PATH):
        got = sha256_file(root / rel)
        if got != hashes.get(rel):
            problems.append(f"{rel}: sha256 {got} != declared {hashes.get(rel)}")
    if hashes.get(LIST_PATH) and hashes[LIST_PATH] not in (root / CRITERIA_PATH).read_text():
        problems.append(f"{CRITERIA_PATH} does not embed the list's declared sha256")
    return problems


def python_files_under(root: Path, dirs: tuple[str, ...] | None = None) -> set[str]:
    """Every ``*.py`` under ``dirs`` (default ``PINNED_PY_DIRS``), repo-relative; caches out."""
    out: set[str] = set()
    for rel_dir in PINNED_PY_DIRS if dirs is None else dirs:
        out |= {p.relative_to(root).as_posix() for p in (root / rel_dir).rglob("*.py")
                if p.is_file() and "__pycache__" not in p.parts}
    return out


def eh_amendment_problems(files: dict[str, str], amendments: dict) -> list[str]:
    """Both E-H modules must hash to the declared literal, in the manifest's files and in its
    ``declared_amendments`` (review F1)."""
    problems = []
    for rel, declared in EH_POST_AMENDMENT_SHA256.items():
        post = amendments.get(rel, {}).get("post_amendment_sha256")
        if post != declared or files.get(rel) != declared:
            problems.append(f"{rel}: the manifest's hash is not the declared post-amendment "
                            f"sha256 {declared}")
    return problems


def load_manifest(root: Path) -> tuple[dict | None, str | None, list[str]]:
    path = root / MANIFEST_PATH
    if not path.is_file():
        return None, None, [f"{MANIFEST_PATH} is missing (list 1.5 step 1b not done)"]
    raw = path.read_bytes()
    return json.loads(raw), sha256_bytes(raw), []


def check_manifest(root: Path, manifest: dict) -> list[str]:
    problems = []
    files: dict[str, str] = manifest.get("files", {})
    if manifest.get("file_count") != len(files) or not files:
        problems.append(f"manifest file_count {manifest.get('file_count')} != {len(files)}")
    for rel, want in sorted(files.items()):
        target = root / rel
        if not target.is_file():
            problems.append(f"manifest file missing: {rel}")
        elif sha256_file(target) != want:
            problems.append(f"manifest file changed: {rel}")
    on_disk = python_files_under(root)
    problems += [f"{rel} is not in the freeze manifest" for rel in sorted(on_disk - set(files))]
    return problems + eh_amendment_problems(files, manifest.get("declared_amendments", {}))


def _git(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, check=False)


def check_git_anchor(root: Path, manifest: dict | None,
                     git: Callable[..., subprocess.CompletedProcess] = _git) -> list[str]:
    """The manifest AND every file it lists are tracked and clean in git (review F4): the
    user's freeze commit must hold the frozen sources, not only their hashes."""
    paths = sorted({MANIFEST_PATH, *(manifest or {}).get("files", {})})
    try:
        tracked = git(root, "ls-files", "-z", "--", *paths)
        status = git(root, "status", "--porcelain", "--untracked-files=all", "--", *paths)
    except (FileNotFoundError, OSError) as exc:
        return [f"git unavailable: {exc!r}"]
    if tracked.returncode != 0 or status.returncode != 0:
        return [f"git ls-files / status failed (rc {tracked.returncode} / {status.returncode}): "
                f"{(tracked.stderr or b'') + (status.stderr or b'')!r}"]
    listed = {p.decode() for p in tracked.stdout.split(b"\0") if p}
    problems = [f"{rel} is not tracked in git (the user's freeze commit anchors it)"
                for rel in paths if rel not in listed]
    problems += [f"{line[3:]} has uncommitted changes in git ({line[:2].strip()})"
                 for line in status.stdout.decode(errors="replace").splitlines() if line.strip()]
    return problems


def check_cme_calendar(root: Path, pinned: str,
                       git: Callable[..., subprocess.CompletedProcess] = _git) -> list[str]:
    try:
        shown = git(root, "show", f"{CME_ANCHOR_COMMIT}:{CME_CALENDAR}")
    except (FileNotFoundError, OSError) as exc:
        return [f"git unavailable for the {CME_CALENDAR} check: {exc!r}"]
    if shown.returncode != 0:
        return [f"cannot read {CME_CALENDAR} at commit {CME_ANCHOR_COMMIT}"]
    if sha256_bytes(shown.stdout) != pinned:
        return [f"{CME_CALENDAR} at {CME_ANCHOR_COMMIT} does not hash to section 0's {pinned}"]
    try:
        old = entries_2025_2026_block(shown.stdout.decode())
        new = entries_2025_2026_block((root / CME_CALENDAR).read_text())
    except ValueError as exc:
        return [f"{CME_CALENDAR}: {exc}"]
    return [] if old == new else [f"{CME_CALENDAR}: the 2025-2026 entries changed"]


def check_section0(root: Path, manifest: dict | None,
                   git: Callable[..., subprocess.CompletedProcess] = _git) -> list[str]:
    entries = parse_section0((root / LIST_PATH).read_text())
    problems = []
    if len(entries) != N_SECTION0_ENTRIES:
        problems.append(f"section 0 parsed to {len(entries)} entries, expected "
                        f"{N_SECTION0_ENTRIES}")
    amendments = (manifest or {}).get("declared_amendments", {})
    for entry in entries:
        target = root / entry.path
        if entry.path == CME_CALENDAR:
            problems += check_cme_calendar(root, entry.sha256, git)
            continue
        want = entry.sha256
        if entry.path in EH_POST_AMENDMENT_SHA256:
            record = amendments.get(entry.path, {})
            if record.get("pre_amendment_sha256") != entry.sha256:
                problems.append(f"{entry.path}: manifest's pre-amendment hash is not section 0's")
            want = EH_POST_AMENDMENT_SHA256[entry.path]  # the declared literal (review F1)
            if record.get("post_amendment_sha256") != want:
                problems.append(f"{entry.path}: manifest's post-amendment hash is not the "
                                "declared one")
        if not target.is_file():
            problems.append(f"section 0 file missing: {entry.path}")
        elif sha256_file(target) != want:
            problems.append(f"section 0 file changed: {entry.path}")
    return problems


def check_build(summary_path: Path = CONFIRMATION_SUMMARY_PATH,
                parquet_path: Path = CONFIRMATION_SERIES_PATH, *,
                manifest_sha256: str | None) -> tuple[list[str], dict]:
    """``manifest_sha256`` is this run's freeze manifest: the build must have run under it."""
    if not Path(summary_path).is_file():
        return [f"confirmation build summary missing: {summary_path}"], {}
    summary = json.loads(Path(summary_path).read_text())
    step4b = summary.get("calendar_validation_step4b") or {}
    comparison = summary.get("degraded_dates_comparison")
    built_under = summary.get("manifest_sha256")
    problems = []
    if manifest_sha256 is None or built_under != manifest_sha256:
        problems.append(f"the confirmation build ran under freeze manifest {built_under!r}, "
                        f"not this run's {manifest_sha256!r} (review F2)")
    if summary.get(STOP_KEY) is not False:
        problems.append(f"build summary {STOP_KEY} = {summary.get(STOP_KEY)!r}: stop for the lead")
    if step4b.get("passed") is not True:
        problems.append("step 4b calendar validation did not pass")
    if not isinstance(comparison, dict) or "identical" not in comparison:
        problems.append("the degraded-date comparison is missing from the build summary")
    record = {"manifest_sha256_of_the_build": built_under,
              "stop_for_lead_decision": summary.get(STOP_KEY),
              "calendar_validation_step4b_passed": step4b.get("passed"),
              "degraded_dates_comparison": comparison,
              "degraded_dates_differ_from_declaration": (
                  None if not isinstance(comparison, dict) else not comparison.get("identical"))}
    if not Path(parquet_path).is_file():
        return [*problems, f"confirmation parquet missing: {parquet_path}"], record
    meta = json.loads(pq.read_schema(parquet_path).metadata[b"propexperiment"])
    for key, want in (("manifest_sha256", built_under), (STOP_KEY, summary.get(STOP_KEY)),
                      ("calendar_validation_step4b_passed", step4b.get("passed")),
                      ("degraded_dates_comparison", comparison)):
        if meta.get(key) != want:
            problems.append(f"parquet metadata {key} disagrees with the build summary")
    return problems, record


def check_holdouts(status: Callable[[], dict] | None = None) -> tuple[list[str], dict]:
    if status is None:
        from data.holdout import status_report as status
    report = status()
    h2 = report.get("holdout_2", {})
    record = {"holdout_1": {"all_ok": report.get("all_ok"),
                            "unlocks_logged": report.get("unlocks_logged")},
              "holdout_2": {"state": h2.get("state"), "all_ok": h2.get("all_ok"),
                            "unlocks_logged": h2.get("unlocks_logged")}}
    problems = []
    if report.get("all_ok") is not True or report.get("unlocks_logged") != 0:
        problems.append(f"holdout-1 not clean: {record['holdout_1']}")
    if h2.get("state") != "sealed" or h2.get("all_ok") is not True or h2.get("unlocks_logged") != 0:
        problems.append(f"holdout-2 not sealed and clean: {record['holdout_2']}")
    return problems, record


def hash_checks(root: Path = REPO_ROOT,
                git: Callable[..., subprocess.CompletedProcess] = _git
                ) -> tuple[list[str], str | None]:
    """Checks 1 to 3 (the ones re-run when step 8 completes)."""
    manifest, manifest_sha, problems = load_manifest(root)
    problems += check_declarations(root)
    if manifest is not None:
        problems += check_manifest(root, manifest)
        problems += check_git_anchor(root, manifest, git)
    problems += check_section0(root, manifest, git)
    return problems, manifest_sha


def preflight(root: Path = REPO_ROOT, *, summary_path: Path = CONFIRMATION_SUMMARY_PATH,
              parquet_path: Path = CONFIRMATION_SERIES_PATH,
              holdout_status: Callable[[], dict] | None = None,
              git: Callable[..., subprocess.CompletedProcess] = _git) -> Preflight:
    problems, manifest_sha = hash_checks(root, git)
    build_problems, build_record = check_build(summary_path, parquet_path,
                                               manifest_sha256=manifest_sha)
    holdout_problems, holdout_record = check_holdouts(holdout_status)
    problems += build_problems + holdout_problems
    return Preflight(not problems, tuple(problems), manifest_sha,
                     {"build": build_record, "holdouts": holdout_record})
