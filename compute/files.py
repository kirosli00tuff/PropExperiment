"""File hashing, sha256 manifests and atomic JSON writes for the compute backend (Stage E.2b, V10).

A manifest maps every file under a directory (POSIX relative path) to its sha256 and byte count.
Both ends of a job use the same two functions: ``dir_manifest`` builds one, ``manifest_problems``
lists every way a directory differs from one (a missing file, an extra file, a file with no
hash, a size or hash mismatch). An empty list is the only acceptance.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

CHUNK_BYTES = 1 << 20
SHA256_HEX_CHARS = 64


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(CHUNK_BYTES), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def is_sha256(value: object) -> bool:
    return (isinstance(value, str) and len(value) == SHA256_HEX_CHARS
            and all(c in "0123456789abcdef" for c in value))


def file_entry(path: Path) -> dict[str, object]:
    return {"sha256": sha256_file(path), "bytes": Path(path).stat().st_size}


def dir_files(root: Path, exclude: frozenset[str] = frozenset()) -> list[str]:
    """Every entry under ``root`` that is not a directory, as sorted POSIX relative paths.
    Links and other special files are listed too, so a check can refuse them by name."""
    base = Path(root)
    out = []
    for path in base.rglob("*"):
        if path.is_dir() and not path.is_symlink():
            continue
        rel = path.relative_to(base).as_posix()
        if rel not in exclude:
            out.append(rel)
    return sorted(out)


def dir_manifest(root: Path, exclude: frozenset[str] = frozenset()) -> dict[str, dict[str, object]]:
    """sha256 and byte count of every regular file under ``root`` (links are refused)."""
    base = Path(root)
    out: dict[str, dict[str, object]] = {}
    for rel in dir_files(base, exclude):
        path = base / Path(rel)
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"{rel}: not a regular file; a manifest lists regular files only")
        out[rel] = file_entry(path)
    return out


def manifest_problems(root: Path, manifest: object,
                      exclude: frozenset[str] = frozenset()) -> list[str]:
    """Every difference between the files under ``root`` and ``manifest``; [] means identical."""
    if not isinstance(manifest, dict) or not manifest:
        return ["the manifest lists no files"]
    base = Path(root)
    problems: list[str] = []
    present = set(dir_files(base, exclude))
    for rel in sorted(present - set(manifest)):
        problems.append(f"{rel}: present but not in the manifest (no hash)")
    for rel, entry in sorted(manifest.items()):
        if not isinstance(entry, dict) or not is_sha256(entry.get("sha256")):
            problems.append(f"{rel}: the manifest gives no sha256")
            continue
        path = base / Path(rel)
        if rel not in present or path.is_symlink() or not path.is_file():
            problems.append(f"{rel}: in the manifest but missing")
            continue
        if path.stat().st_size != entry.get("bytes"):
            problems.append(f"{rel}: {path.stat().st_size} bytes, the manifest says "
                            f"{entry.get('bytes')}")
            continue
        actual = sha256_file(path)
        if actual != entry["sha256"]:
            problems.append(f"{rel}: sha256 {actual[:12]}... differs from the manifest's "
                            f"{entry['sha256'][:12]}...")
    return problems


def write_json_atomic(path: Path, payload: object) -> str:
    """Write ``payload`` as sorted, indented UTF-8 JSON through a temporary file and a rename;
    returns the sha256 of the bytes written."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(payload, indent=1, sort_keys=True, default=str) + "\n").encode("utf-8")
    tmp = target.with_name(target.name + ".tmp")
    with tmp.open("wb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp, target)
    return sha256_bytes(data)


def read_json(path: Path) -> object:
    return json.loads(Path(path).read_text(encoding="utf-8"))
