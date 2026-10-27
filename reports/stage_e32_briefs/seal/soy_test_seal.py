"""Stage E.32 Part 0: seal the soybean-complex test window with data.holdout's own mechanism.

    uv run python reports/stage_e32_briefs/seal/soy_test_seal.py plan     # targets, no writes
    uv run python reports/stage_e32_briefs/seal/soy_test_seal.py seal     # seal them (resumable)
    uv run python reports/stage_e32_briefs/seal/soy_test_seal.py status   # checksums only

What is sealed (reports/stage_e32_test_seal.md): every owned ZM, ZS and ZL market-data file that
touches CME trade dates 2017-05-01..2020-11-30, the one-shot test window of the soybean-complex
directional program (V51). A raw file touches the window when its UTC span overlaps
[2017-04-30T21:00Z, 2020-11-30T22:00Z): 16:00 CT on the Sunday before the first trade date (no
message of trade date 2017-05-01 is earlier) to 16:00 CT on the last trade date (after its 13:20
close and settlement; trade date 2020-12-01's pre-open starts later). A processed bar store or
price cache touches it when its first..last trade dates overlap 2017-05-01..2020-11-30.

Why this file is not under data/: harness v14 pins data/holdout.py and refuses any unlisted *.py
in a harness directory. It imports data.holdout read-only and reuses its primitives unchanged
(seal_bytes and open_sealed, the durable manifest write, the log append, the log pin, proof
before removal), so the order and the proofs are the ones that sealed MES's two holdouts and the
step 2 products' holdout 2.

Deliberate differences from data.step2_seal:
- Its own append-only log, docs/SOY_TEST_UNLOCK_LOG.md. data.holdout.prior_unlocks counts every
  "UNLOCK" heading in the shared log that lacks the holdout-2 mark as holdout 1's, so a soybean
  unlock logged there would change holdout 1's count.
- Its own phrase (ACKNOWLEDGEMENT below), which is also the key material.
- Targets are whole files, fixed in the manifest at the first seal. A file that spans the window
  boundary is sealed whole, so no script ever reads in-window rows to split it; its
  out-of-window part stays rebuildable from the plaintext raw chunks outside the window.
- The unseal ceremony requires the registered soybean test stage, not Stage D.2.
- Fail closed: a ZM/ZS/ZL file whose span cannot be read from its name stops plan and seal, and
  status reports any in-window plaintext that reappears (a re-buy or a rebuilt store).
"""

from __future__ import annotations

import glob
import json
import os
import re
import secrets
import stat
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from data import holdout as ho  # noqa: E402
from data.config import DATA_ROOT, REPO_ROOT, VENDOR_ROOT  # noqa: E402

ROOTS = ("ZM", "ZS", "ZL")
FIRST_TRADE_DATE, LAST_TRADE_DATE = "2017-05-01", "2020-11-30"
WINDOW_UTC = (datetime(2017, 4, 30, 21, tzinfo=UTC), datetime(2020, 11, 30, 22, tzinfo=UTC))
LABEL = "soy test"
ACKNOWLEDGEMENT = (
    "I am running the registered soybean-complex test against the bar pre-registered in "
    "REGISTRATION.md, and I accept that reading the sealed test window spends it."
)
# The ceremony's stage argument (fullmatch, case-insensitive), e.g. "Stage E.34 soy test".
STAGE_PATTERN = r"(stage\s+)?e\.\d+[a-z]?\s+soy\s+test"
DECLARATION = "reports/stage_e32_test_seal.md (Stage E.32 Part 0, V51)"
LOG_HEADER = (
    "# Soybean-complex test seal: unlock log\n\nAppend-only. "
    "reports/stage_e32_briefs/seal/soy_test_seal.py writes each entry BEFORE any sealed byte is "
    "decrypted. Do not edit or delete entries. Kept apart from docs/HOLDOUT_UNLOCK_LOG.md on "
    "purpose: data.holdout.prior_unlocks would count a soybean unlock entry there as holdout "
    "1's.\n"
)

PATHS = ho.HoldoutPaths(
    sealed_root=DATA_ROOT / "sealed" / "SOY_test_v1",
    manifest=REPO_ROOT / "docs" / "soy_test" / "SOY_TEST_MANIFEST.json",
    unlock_log=REPO_ROOT / "docs" / "SOY_TEST_UNLOCK_LOG.md",
    registration=REPO_ROOT / "REGISTRATION.md",
    research_parquet=REPO_ROOT / "docs" / "soy_test",  # unused: this store has no bars blob
    holdout_id=3,
)

_ROOT_TOKEN = re.compile(r"(?:^|[_\-.])(ZM|ZS|ZL)(?=[_\-.]|$)")
_STAMP = r"\d{4}-\d{2}-\d{2}(?:T\d{6}Z)?"
_RAW_RANGE = re.compile(rf"range=({_STAMP})_({_STAMP})\.dbn\.zst")  # end exclusive
_RAW_BATCH = re.compile(r".*-(\d{4}-\d{2}-\d{2})_(\d{4}-\d{2}-\d{2})\.dbn\.zst")  # end inclusive
_STORE = re.compile(r".*_(\d{4}-\d{2}-\d{2})_(\d{4}-\d{2}-\d{2})_[a-z0-9]+\.parquet")
_METADATA_NAMES = frozenset({"manifest.json"})


@dataclass(frozen=True)
class Layout:
    """Where the program keeps market data. Tests pass a temporary one."""

    repo_root: Path
    glbx: Path  # raw vendor files: <glbx>/<schema>/<dataset dir>/<file>
    store_globs: tuple[str, ...]  # bar stores, relative to repo_root, "{root}" filled per root
    caches: tuple[tuple[str, str, str], ...]  # (relpath, first, last trade date) for undated names


DEFAULT_LAYOUT = Layout(
    repo_root=REPO_ROOT,
    glbx=VENDOR_ROOT / "GLBX.MDP3",
    store_globs=("data/processed/{root}/*", "data/processed_step2/{root}/*",
                 "data/processed_hist/*/{root}/*"),
    # Spans read at E.32 from each file's date column (min/max only, no other column).
    caches=(("reports/stage_e22_microbook/cache/ZS.parquet", "2010-07-01", "2024-02-29"),
            ("reports/stage_e22_microbook/cache/ZL.parquet", "2010-07-01", "2024-02-29")),
)


@dataclass(frozen=True)
class Target:
    kind: str  # "raw <schema>", "store" or "cache"
    root: str  # "ZM", "ZS", "ZL", or "+"-joined when one raw dataset holds several
    path: Path  # as the program spells it (symlinks unresolved)
    relpath: str  # relative to the layout's repo root
    span: str

    @property
    def sealed_relpath(self) -> str:
        return self.relpath + ".sealed"


class UnclassifiedFileError(RuntimeError):
    """A ZM/ZS/ZL data file whose dates cannot be read from its name: fail closed."""


# ------------------------------------------------------------------ the window rule ----
def _stamp(text: str) -> datetime:
    if "T" in text:
        return datetime.strptime(text, "%Y-%m-%dT%H%M%SZ").replace(tzinfo=UTC)
    return datetime.strptime(text, "%Y-%m-%d").replace(tzinfo=UTC)


def raw_span(name: str) -> tuple[datetime, datetime] | None:
    """[start, end) in UTC of a raw vendor file, from its name; None if the name has no span."""
    match = _RAW_RANGE.fullmatch(name)
    if match:
        return _stamp(match.group(1)), _stamp(match.group(2))
    match = _RAW_BATCH.fullmatch(name)
    if match:  # a batch file's end date is inclusive: count the whole day
        return _stamp(match.group(1)), _stamp(match.group(2)) + timedelta(days=1)
    return None


def raw_touches_window(start: datetime, end: datetime) -> bool:
    return start < WINDOW_UTC[1] and end > WINDOW_UTC[0]


def store_touches_window(first: str, last: str) -> bool:
    """Inclusive trade-date span against the inclusive window (ISO dates compare as strings)."""
    return first <= LAST_TRADE_DATE and last >= FIRST_TRADE_DATE


def _relpath(path: Path, layout: Layout) -> str:
    return os.path.relpath(os.path.abspath(path), layout.repo_root)


def _roots_in(name: str) -> list[str]:
    return sorted(set(_ROOT_TOKEN.findall(name)), key=ROOTS.index)


def scan(layout: Layout = DEFAULT_LAYOUT) -> tuple[list[Target], list[str]]:
    """(plaintext ZM/ZS/ZL files now on disk that touch the window, unclassified files). Reads
    names and nothing else."""
    targets: list[Target] = []
    unclassified: list[str] = []
    for dataset in sorted(glob.glob(str(layout.glbx / "*" / "*"))):
        roots = _roots_in(Path(dataset).name)
        if not roots or not Path(dataset).is_dir():
            continue
        schema = Path(dataset).parent.name
        for name in sorted(os.listdir(dataset)):
            path = Path(dataset) / name
            if name in _METADATA_NAMES or not path.is_file():
                continue
            span = raw_span(name)
            if span is None:
                unclassified.append(_relpath(path, layout))
            elif raw_touches_window(*span):
                targets.append(Target(f"raw {schema}", "+".join(roots), path,
                                      _relpath(path, layout),
                                      f"{span[0].isoformat()}..{span[1].isoformat()} (UTC)"))
    for root in ROOTS:
        for pattern in layout.store_globs:
            for found in sorted(glob.glob(str(layout.repo_root / pattern.format(root=root)))):
                path = Path(found)
                if not path.is_file():
                    continue
                match = _STORE.fullmatch(path.name)
                if match is None:
                    unclassified.append(_relpath(path, layout))
                elif store_touches_window(match.group(1), match.group(2)):
                    targets.append(Target("store", root, path, _relpath(path, layout),
                                          f"trade dates {match.group(1)}..{match.group(2)}"))
    for relpath, first, last in layout.caches:
        path = layout.repo_root / relpath
        if path.is_file() and store_touches_window(first, last):
            targets.append(Target("cache", _roots_in(path.stem)[0], path, relpath,
                                  f"trade dates {first}..{last}"))
    return sorted(targets, key=lambda t: t.relpath), sorted(unclassified)


def plan(layout: Layout = DEFAULT_LAYOUT) -> list[Target]:
    targets, unclassified = scan(layout)
    if unclassified:
        raise UnclassifiedFileError(f"cannot date {len(unclassified)} ZM/ZS/ZL file(s) from "
                                    f"their names; classify them before sealing: {unclassified}")
    return targets


# ------------------------------------------------------------------ seal ----
def _new_manifest(expected: Sequence[Target]) -> dict:
    return {
        "holdout": LABEL, "created_utc": datetime.now(UTC).isoformat(),
        "declaration": DECLARATION, "roots": list(ROOTS),
        "first_trade_date": FIRST_TRADE_DATE, "last_trade_date": LAST_TRADE_DATE,
        "window_utc": [WINDOW_UTC[0].isoformat(), WINDOW_UTC[1].isoformat()],
        "cipher": ho.CIPHER, "kdf_iterations": ho.KDF_ITERATIONS,
        "salt_hex": secrets.token_bytes(16).hex(),
        "acknowledgement_sha256": ho.sha256_bytes(ACKNOWLEDGEMENT.encode()),
        "expected_targets": [t.relpath for t in expected],
        "raw_files": [],  # the key data.holdout's helpers read; holds every sealed file
    }


def _spellings(record: dict, layout: Layout) -> set[Path]:
    """Both spellings of a sealed file's original location, resolved: as recorded, and
    repo-relative under the layout (data.holdout._record_paths, but layout-aware for tests)."""
    return {Path(record["original_path"]).resolve(),
            (layout.repo_root / record["original_relpath"]).resolve()}


def _ensure_log(paths: ho.HoldoutPaths) -> None:
    if paths.unlock_log.exists():
        return
    paths.unlock_log.parent.mkdir(parents=True, exist_ok=True)
    with paths.unlock_log.open("x") as fh:
        fh.write(LOG_HEADER)
        fh.flush()
        os.fsync(fh.fileno())


def _refuse_seal(target: Target, paths: ho.HoldoutPaths, manifest: dict) -> Path:
    """Every refusal happens before a byte is read, written or removed."""
    if manifest.get("holdout") != LABEL:
        raise ValueError(f"{paths.manifest.name} is not the {LABEL} manifest")
    if target.relpath not in manifest["expected_targets"]:
        raise ValueError(f"{target.relpath} is not in the plan fixed at the first seal")
    if any(r["original_relpath"] == target.relpath for r in manifest["raw_files"]):
        raise FileExistsError(f"{target.relpath} is already sealed: sealed once only")
    if manifest["raw_files"] and not ho._unlock_log_intact(manifest, paths):
        raise ho.SealIntegrityError("the unlock log no longer matches its pinned prefix: "
                                    "refusing to re-pin a rewritten history")
    sealed_path = paths.sealed_root / target.sealed_relpath
    if sealed_path.exists():
        raise FileExistsError(f"{sealed_path} exists but {target.relpath} is not in the "
                              "manifest: an earlier seal was interrupted. Inspect and remove the "
                              "orphan by hand, then re-run.")
    if not target.path.is_file():
        raise FileNotFoundError(f"{target.path} does not exist: nothing to seal")
    return sealed_path


def seal_file(target: Target, paths: ho.HoldoutPaths, manifest: dict, *,
              create: bool) -> dict:
    """data.holdout.seal_holdout2_chunk's order and proofs for one whole file: prove the round
    trip in memory, write the blob ("xb", fsync), prove it again from disk, append the manifest
    record, log SEALED, pin the log, and only then remove the plaintext. Returns the manifest."""
    sealed_path = _refuse_seal(target, paths, manifest)
    salt = bytes.fromhex(manifest["salt_hex"])
    data = target.path.read_bytes()
    sha_plain = ho.sha256_bytes(data)
    blob = ho.seal_bytes(data, ACKNOWLEDGEMENT, salt, secrets.token_bytes(ho.NONCE_BYTES))
    ho.open_sealed(blob, ACKNOWLEDGEMENT, salt, sha_plain)  # raises on mismatch; nothing written
    sealed_path.parent.mkdir(parents=True, exist_ok=True)
    with sealed_path.open("xb") as fh:
        fh.write(blob)
        fh.flush()
        os.fsync(fh.fileno())
    ho._fsync_dir(sealed_path.parent)
    on_disk = sealed_path.read_bytes()
    if ho.sha256_bytes(on_disk) != ho.sha256_bytes(blob):
        raise ho.SealIntegrityError(f"sealed copy of {target.relpath} did not persist intact")
    ho.open_sealed(on_disk, ACKNOWLEDGEMENT, salt, sha_plain)  # the proof licensing removal

    record = {"original_path": str(target.path), "original_relpath": target.relpath,
              "kind": target.kind, "root": target.root, "span": target.span,
              "sealed_relpath": target.sealed_relpath, "bytes": len(data),
              "sha256_plaintext": sha_plain, "sha256_sealed": ho.sha256_bytes(blob)}
    manifest = {**manifest, "raw_files": [*manifest["raw_files"], record]}
    ho._write_manifest(paths.manifest, manifest, create=create)
    ho._append_log(paths, f"{datetime.now(UTC).isoformat()} SEALED {LABEL} {target.root} "
                          f"{target.kind} {target.path.name}", [
        f"file {len(manifest['raw_files'])} of {len(manifest['expected_targets'])}: "
        f"{target.relpath} ({target.span})",
        f"plaintext sha256 {sha_plain}; sealed sha256 {record['sha256_sealed']}",
        f"manifest sha256: {ho.sha256_file(paths.manifest)}",
        "the sealed copy on disk decrypted back to the plaintext sha256 before removal",
    ])
    ho._pin_log_and_remove(target.path, paths, manifest)
    return ho.load_manifest(paths)


def complete_interrupted_seal(record: dict, paths: ho.HoldoutPaths, manifest: dict,
                              layout: Layout = DEFAULT_LAYOUT) -> dict:
    """Finish a seal that stopped after its manifest record (data.holdout's completion, which is
    holdout-2 only): the normal path's proof licenses removal, then log, re-pin, remove."""
    if not ho._unlock_log_intact(manifest, paths):
        raise ho.SealIntegrityError("the unlock log no longer matches its pinned prefix: "
                                    "refusing to re-pin a rewritten history")
    blob = (paths.sealed_root / record["sealed_relpath"]).read_bytes()
    if ho.sha256_bytes(blob) != record["sha256_sealed"]:
        raise ho.SealIntegrityError(f"sealed blob of {record['original_relpath']} does not "
                                    "match the manifest")
    ho.open_sealed(blob, ACKNOWLEDGEMENT, bytes.fromhex(manifest["salt_hex"]),
                   record["sha256_plaintext"])
    raw = layout.repo_root / record["original_relpath"]
    if raw.exists() and ho.sha256_file(raw) != record["sha256_plaintext"]:
        raise ho.SealIntegrityError(f"{record['original_relpath']} is sealed but the file at its "
                                    "path is not the sealed plaintext: kept")
    ho._append_log(paths, f"{datetime.now(UTC).isoformat()} RESUMED {LABEL} "
                          f"{Path(record['original_relpath']).name}",
                   ["plaintext removed on resume: sealed sha256 {sha256_sealed} decrypted back "
                    "to {sha256_plaintext}".format(**record)])
    ho._pin_log_and_remove(raw, paths, manifest)
    return ho.load_manifest(paths)


def seal_all(paths: ho.HoldoutPaths = PATHS, layout: Layout = DEFAULT_LAYOUT) -> dict:
    """Seal every planned file. The plan is fixed in the manifest at the first seal; a rerun
    finishes an interrupted seal and refuses any new in-window file (that needs a stage
    decision, not a silent extension)."""
    found = plan(layout)
    by_relpath = {t.relpath: t for t in found}
    if paths.manifest.exists():
        manifest, create = ho.load_manifest(paths), False
        new = sorted(set(by_relpath) - set(manifest["expected_targets"]))
        if new:
            raise ValueError(f"in-window file(s) not in the fixed plan: {new}")
    else:
        if not found:
            raise ValueError("nothing touches the window: no manifest written")
        manifest, create = _new_manifest(found), True
    _ensure_log(paths)
    for relpath in manifest["expected_targets"]:
        record = next((r for r in manifest["raw_files"] if r["original_relpath"] == relpath),
                      None)
        if record is not None:
            if any(p.exists() for p in _spellings(record, layout)):
                manifest = complete_interrupted_seal(record, paths, manifest, layout)
            continue
        if relpath not in by_relpath:
            raise FileNotFoundError(f"{relpath} is planned but neither sealed nor on disk")
        manifest = seal_file(by_relpath[relpath], paths, manifest, create=create)
        create = False
    return manifest


# ------------------------------------------------------------------ unseal ----
def _refuse_unless_ceremony(stage: str, reason: str, acknowledgement: str,
                            prior_unlocks_acknowledged: int, paths: ho.HoldoutPaths) -> str:
    """data.holdout's ceremony with this store's phrase and stage; returns the registration
    sha256. Raises HoldoutLockedError before anything is logged or decrypted."""
    if acknowledgement != ACKNOWLEDGEMENT:
        raise ho.HoldoutLockedError("acknowledgement does not match this store's phrase")
    if not re.fullmatch(STAGE_PATTERN, stage, re.IGNORECASE):
        raise ho.HoldoutLockedError(f"stage {stage!r} is not the registered soybean test (it "
                                    f"must fullmatch {STAGE_PATTERN!r})")
    if any("\n" in text or "#" in text for text in (stage, reason)):
        raise ho.HoldoutLockedError("stage and reason go into the log's markdown headings: no "
                                    "newlines or '#' characters")
    if len(reason.strip()) < ho.MIN_REASON_CHARS:
        raise ho.HoldoutLockedError(f"state a real reason (>= {ho.MIN_REASON_CHARS} characters)")
    registration = paths.registration.read_text() if paths.registration.exists() else ""
    missing = [w for w in ho.REGISTRATION_REQUIRED_WORDS if w not in registration.lower()]
    if len(registration.strip()) < ho.MIN_REGISTRATION_CHARS or missing:
        raise ho.HoldoutLockedError(f"{paths.registration.name} is not a pre-registered bar "
                                    f"(missing: {missing or 'length'}); write it first")
    already = ho.prior_unlocks(paths)
    if prior_unlocks_acknowledged != already:
        raise ho.HoldoutLockedError(f"the log shows {already} prior unlock(s); pass "
                                    f"prior_unlocks_acknowledged={already} to confirm you know")
    return ho.sha256_file(paths.registration)


def unseal_file(original_path: Path, *, stage: str, reason: str, acknowledgement: str,
                prior_unlocks_acknowledged: int = 0, paths: ho.HoldoutPaths = PATHS,
                layout: Layout = DEFAULT_LAYOUT) -> Path:
    """Restore one sealed file to its original path (read-only). Logs first, then decrypts."""
    registration_sha = _refuse_unless_ceremony(stage, reason, acknowledgement,
                                               prior_unlocks_acknowledged, paths)
    manifest = ho.load_manifest(paths)
    if not ho._unlock_log_intact(manifest, paths):
        raise ho.SealIntegrityError("the unlock log no longer matches its pinned prefix")
    target = Path(original_path).resolve()
    record = next((r for r in manifest["raw_files"] if target in _spellings(r, layout)), None)
    if record is None:
        raise KeyError(f"{original_path} is not in the {LABEL} store")
    if target.exists():
        raise FileExistsError(f"{target} already exists; files are never overwritten")
    blob = (paths.sealed_root / record["sealed_relpath"]).read_bytes()
    if ho.sha256_bytes(blob) != record["sha256_sealed"]:
        raise ho.SealIntegrityError(f"sealed blob for {target.name} does not match the manifest")
    ho._append_log(paths, f"{datetime.now(UTC).isoformat()} UNLOCK {LABEL} file ({stage})", [
        f"reason: {reason.strip()}", f"file: {record['original_relpath']}",
        f"registration: {paths.registration.name} sha256 {registration_sha}",
        f"prior unlocks acknowledged: {prior_unlocks_acknowledged}",
    ])
    plaintext = ho.open_sealed(blob, acknowledgement, bytes.fromhex(manifest["salt_hex"]),
                               record["sha256_plaintext"])
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("xb") as fh:
        fh.write(plaintext)
    target.chmod(stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
    return target


# ------------------------------------------------------------------ status ----
def status(paths: ho.HoldoutPaths = PATHS, layout: Layout = DEFAULT_LAYOUT) -> dict:
    """Checksums and names only. Decrypts nothing and writes no log entry."""
    manifest = ho.load_manifest(paths) if paths.manifest.exists() else None
    records = manifest["raw_files"] if manifest else []
    expected = manifest["expected_targets"] if manifest else []
    files = {}
    for record in records:
        sealed = paths.sealed_root / record["sealed_relpath"]
        files[record["original_relpath"]] = {
            "sealed_ok": sealed.exists() and ho.sha256_file(sealed) == record["sha256_sealed"],
            "plaintext_absent": not any(p.exists() or ho.partial_path(p).exists()
                                        for p in _spellings(record, layout)),
        }
    in_window, unclassified = scan(layout)
    report = {
        "holdout": LABEL, "manifest": str(paths.manifest),
        "state": ("not_yet_sealed" if not records else
                  "sealed" if len(records) == len(expected) else "partially_sealed"),
        "files_expected": len(expected), "files_sealed": len(records),
        "files_ok": sum(v["sealed_ok"] and v["plaintext_absent"] for v in files.values()),
        "plaintext_in_window_present": [t.relpath for t in in_window],
        "unclassified_files": unclassified,
        "unlock_log_ok": bool(manifest) and ho._unlock_log_intact(manifest, paths),
        "unlocks_logged": ho.prior_unlocks(paths),
    }
    report["all_ok"] = bool(
        report["state"] == "sealed" and report["unlock_log_ok"]
        and not report["plaintext_in_window_present"] and not unclassified
        and report["files_ok"] == len(expected))
    report["files"] = files
    return report


def main(argv: Sequence[str]) -> int:
    command = argv[1] if len(argv) > 1 else "status"
    if command == "plan":
        targets = plan()
        kinds = sorted({(t.kind, t.root) for t in targets})
        print(json.dumps({"files": len(targets),
                          "bytes": sum(t.path.stat().st_size for t in targets),
                          "by_kind_root": {f"{k} {r}": sum(1 for t in targets
                                                          if (t.kind, t.root) == (k, r))
                                           for k, r in kinds},
                          "targets": [t.relpath for t in targets]}, indent=1))
        return 0
    if command == "seal":
        manifest = seal_all()
        print(json.dumps({"sealed": len(manifest["raw_files"]),
                          "expected": len(manifest["expected_targets"])}, indent=1))
        return 0
    if command == "status":
        report = status()
        print(json.dumps({k: v for k, v in report.items() if k != "files"}, indent=1))
        return 0 if report["all_ok"] else 1
    print("usage: soy_test_seal.py [plan|seal|status]")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
