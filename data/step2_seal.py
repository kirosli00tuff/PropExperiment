"""Stage E.2b Task 4: holdout-2 sealing per product for the step 2 purchases (design D4, D11.4).

Frozen design D4: each product's holdout-2 raw chunks (range=2024-03-01_2024-04-01 through
range=2025-03-01_2025-04-01, March 2024's embargo included) are "sealed on arrival exactly as
MES's was (each sealed in the download call after its byte check, oldest first), one sealed
store per product, the same unlock log, the same REGISTRATION.md requirement".

data/holdout.py seals MES's holdout 2 and is not changed here: its seal refusal pins the chunk
paths to MES.v.0. This module is the same procedure for any other root, built from
data.holdout's own primitives (cipher, manifest write, log append, log pin and plaintext removal,
interrupted-seal completion), so the order and the proofs are identical:
prove the round trip in memory -> write the blob ("xb", fsync) -> prove it again from disk ->
append the manifest record -> log SEALED -> pin the log -> only then remove the plaintext.

Per product (``step2_holdout_paths``):
- sealed store  data/sealed/<ROOT>_holdout_v2/raw/range=<s>_<e>.dbn.zst.sealed
- manifest      docs/holdout2/<ROOT>_HOLDOUT2_MANIFEST.json (bytes and sha256s only)
- unlock log    docs/HOLDOUT_UNLOCK_LOG.md (the same append-only log as MES's two holdouts)
- REGISTRATION.md, the phrase and the cipher: data.holdout's.
Nothing here decrypts for reading; the unlock ceremony stays data.holdout's (never called here).
"""

from __future__ import annotations

import os
import secrets
from datetime import UTC, datetime
from pathlib import Path

from data import holdout as ho
from data.adapter import OHLCV_1M, raw_path
from data.config import DATA_ROOT, REPO_ROOT, VENDOR_ROOT
from data.research_bars import HOLDOUT2_RAW_CHUNKS

SEALED_BASE = DATA_ROOT / "sealed"
MANIFEST_DIR = REPO_ROOT / "docs" / "holdout2"
MANIFEST_SUFFIX = "_HOLDOUT2_MANIFEST.json"
DECLARATION = ("docs/STAGE_E_DESIGN.md D4 and D11.4 (holdout-2 per product, sealed on arrival); "
               "reports/stage_e2b_task4_purchase_worker.md (data/pull_step2.py)")


def continuous(root: str) -> str:
    return f"{root}.v.0"


def step2_holdout_paths(root: str, *, sealed_base: Path = SEALED_BASE,
                        manifest_dir: Path = MANIFEST_DIR,
                        unlock_log: Path = ho.HOLDOUT2_PATHS.unlock_log,
                        registration: Path = ho.HOLDOUT2_PATHS.registration,
                        vendor_root: Path = VENDOR_ROOT,
                        store_parquet: Path | None = None) -> ho.HoldoutPaths:
    """The product's own holdout-2 store. MES is refused: its store is data.holdout's."""
    if root == "MES":
        raise ValueError("MES's holdout 2 is data.holdout.HOLDOUT2_PATHS (Stage D.1f); the step "
                         "2 path never seals MES")
    if not root or not root.replace("6", "").isalnum() or root != root.upper():
        raise ValueError(f"{root!r} is not a product root")
    return ho.HoldoutPaths(
        sealed_root=sealed_base / f"{root}_holdout_v2",
        manifest=manifest_dir / f"{root}{MANIFEST_SUFFIX}",
        unlock_log=unlock_log, registration=registration,
        research_parquet=_store_parquet(root) if store_parquet is None else store_parquet,
        holdout_id=2, vendor_root=vendor_root)


def _store_parquet(root: str) -> Path:
    """The product's step 2 bar store, which ``verify`` checks for rows after 2024-02-29."""
    from data.step2_store import step2_parquet_path  # lazy: the store imports this module

    return step2_parquet_path(root)


def chunk_paths(root: str, paths: ho.HoldoutPaths) -> list[Path]:
    """Where the product's 13 holdout-2 chunks land when bought, oldest first."""
    return [raw_path(continuous(root), OHLCV_1M, s, e, paths.vendor_root)
            for s, e in HOLDOUT2_RAW_CHUNKS]


def _new_manifest(root: str) -> dict:
    return {**ho._new_holdout2_manifest(), "product": root, "continuous": continuous(root),
            "declaration": DECLARATION}


def _refuse_seal(root: str, raw: Path, paths: ho.HoldoutPaths, manifest: dict | None) -> None:
    """data.holdout._refuse_holdout2_seal with the product's own chunk paths. Every refusal
    happens before a byte is read, written or removed."""
    if paths.holdout_id != 2:
        raise ValueError("a step 2 seal needs holdout-2 paths (holdout_id=2)")
    if manifest is not None and manifest.get("product") != root:
        raise ValueError(f"{paths.manifest.name} belongs to {manifest.get('product')!r}, "
                         f"not {root!r}")
    chunk = ho._chunk_of(raw)
    if chunk not in HOLDOUT2_RAW_CHUNKS:
        raise ValueError(f"{raw.name} is not one of the 13 holdout-2 chunks; it is never sealed")
    expected = chunk_paths(root, paths)[HOLDOUT2_RAW_CHUNKS.index(chunk)]
    if raw.resolve() != expected.resolve():
        raise ValueError(f"{raw} is not where the step 2 path stores {root}'s {raw.name} "
                         f"({expected})")
    if manifest is not None and any(raw.resolve() in ho._record_paths(r)
                                    for r in manifest["raw_files"]):
        raise FileExistsError(f"{raw.name} is already in {paths.manifest.name}: sealed once only")
    nxt = ho.next_holdout2_chunk(paths)
    if chunk != nxt:
        raise ho.SealIntegrityError(f"out of order: {root} {raw.name} arrived but the next chunk "
                                    f"to seal is {nxt} (oldest first)")
    if manifest is not None and not ho._unlock_log_intact(manifest, paths):
        raise ho.SealIntegrityError("the unlock log no longer matches its pinned prefix: "
                                    "refusing to re-pin a rewritten history")
    sealed_path = paths.sealed_root / "raw" / (raw.name + ".sealed")
    if sealed_path.exists():
        raise FileExistsError(f"{sealed_path} exists but {raw.name} is not in the manifest: an "
                              "earlier seal was interrupted. Inspect and remove the orphan by "
                              "hand, then re-run.")
    if not raw.is_file():
        raise FileNotFoundError(f"{raw} does not exist: nothing to seal")


def seal_chunk(root: str, raw: Path, paths: ho.HoldoutPaths, *, note: str = "") -> dict:
    """Seal one of ``root``'s holdout-2 chunks the moment it arrives: data.holdout's
    seal_holdout2_chunk, step for step, for the product's own store. Nothing is decoded."""
    raw = Path(raw)
    manifest = ho.load_manifest(paths) if paths.manifest.exists() else None
    _refuse_seal(root, raw, paths, manifest)
    create = manifest is None
    manifest = _new_manifest(root) if create else manifest
    salt = bytes.fromhex(manifest["salt_hex"])

    data = raw.read_bytes()
    sha_plain = ho.sha256_bytes(data)
    blob = ho.seal_bytes(data, ho.ACKNOWLEDGEMENT, salt, secrets.token_bytes(ho.NONCE_BYTES))
    ho.open_sealed(blob, ho.ACKNOWLEDGEMENT, salt, sha_plain)  # raises on mismatch
    rel = Path("raw") / (raw.name + ".sealed")
    sealed_path = paths.sealed_root / rel
    sealed_path.parent.mkdir(parents=True, exist_ok=True)
    with sealed_path.open("xb") as fh:
        fh.write(blob)
        fh.flush()
        os.fsync(fh.fileno())
    ho._fsync_dir(sealed_path.parent)
    on_disk = sealed_path.read_bytes()
    if ho.sha256_bytes(on_disk) != ho.sha256_bytes(blob):
        raise ho.SealIntegrityError(f"sealed copy of {root} {raw.name} did not persist intact")
    ho.open_sealed(on_disk, ho.ACKNOWLEDGEMENT, salt, sha_plain)  # the proof licensing removal

    record = {"original_path": str(raw), "original_relpath": ho._relpath_in_repo(raw),
              "sealed_relpath": str(rel), "bytes": len(data), "sha256_plaintext": sha_plain,
              "sha256_sealed": ho.sha256_bytes(blob)}
    manifest = {**manifest, "raw_files": [*manifest["raw_files"], record]}
    ho._write_manifest(paths.manifest, manifest, create=create)
    ho._append_log(paths, f"{datetime.now(UTC).isoformat()} SEALED {ho.HOLDOUT2_LABEL} {root} "
                          f"raw chunk {raw.name}", [
        f"product {root} ({continuous(root)}), chunk {len(manifest['raw_files'])} of "
        f"{len(HOLDOUT2_RAW_CHUNKS)}, sealed on arrival in the download call, oldest first",
        f"plaintext sha256 {sha_plain}; sealed sha256 {record['sha256_sealed']}",
        f"manifest {paths.manifest.name} sha256: {ho.sha256_file(paths.manifest)}",
        "the sealed copy on disk decrypted back to the plaintext sha256 before removal",
        *([note] if note else []),
    ])
    ho._pin_log_and_remove(raw, paths, manifest)
    return record


def complete_interrupted_seal(raw: Path, paths: ho.HoldoutPaths) -> dict:
    """data.holdout's own completion (generic in its paths): removes the plaintext of a chunk
    already recorded in the product's manifest, only under the normal path's proof."""
    return ho.complete_interrupted_seal(raw, paths)


def is_sealed(path: Path, paths: ho.HoldoutPaths) -> bool:
    return ho.is_sealed_raw(path, paths)


def next_chunk(paths: ho.HoldoutPaths) -> tuple[str, str] | None:
    return ho.next_holdout2_chunk(paths)


def verify(root: str, paths: ho.HoldoutPaths) -> dict:
    """Checksums only (data.holdout._verify_holdout2 with the product's chunk paths). Before the
    first chunk is sealed the state is "not_yet_sealed" and all_ok is False."""
    manifest = ho.load_manifest(paths) if paths.manifest.exists() else None
    records = manifest["raw_files"] if manifest else []
    raw_files = {}
    for record in records:
        sealed = paths.sealed_root / record["sealed_relpath"]
        raw_files[Path(record["original_path"]).name] = {
            "sealed_ok": sealed.exists() and ho.sha256_file(sealed) == record["sha256_sealed"],
            "plaintext_absent": not any(p.exists() or ho.partial_path(p).exists()
                                        for p in ho._record_paths(record)),
        }
    done = ho._sealed_chunks(manifest) if manifest else []
    unsealed = [p for p, c in zip(chunk_paths(root, paths), HOLDOUT2_RAW_CHUNKS, strict=True)
                if c not in done]
    report: dict = {
        "holdout": ho.HOLDOUT2_LABEL, "product": root,
        "product_matches": manifest is None or manifest.get("product") == root,
        "state": ("not_yet_sealed" if not done else
                  "sealed" if len(done) == len(HOLDOUT2_RAW_CHUNKS) else "partially_sealed"),
        "chunks_expected": len(HOLDOUT2_RAW_CHUNKS), "chunks_sealed": len(done),
        "sealed_in_order": done == list(HOLDOUT2_RAW_CHUNKS[:len(done)]),
        "raw_files": raw_files,
        "unsealed_plaintext_present": [p.name for p in unsealed
                                       if p.exists() or ho.partial_path(p).exists()],
        "unlock_log_ok": ho._unlock_log_intact(manifest or {}, paths),
        "store_has_no_embargo_or_holdout2_rows": ho._confirmation_clean(paths),
        "unlocks_logged": ho.prior_unlocks(paths),
    }
    report["all_ok"] = bool(
        report["state"] == "sealed" and report["sealed_in_order"] and report["unlock_log_ok"]
        and report["product_matches"] and not report["unsealed_plaintext_present"]
        and report["store_has_no_embargo_or_holdout2_rows"] is not False
        and all(v["sealed_ok"] and v["plaintext_absent"] for v in raw_files.values()))
    return report


def verify_all(base: ho.HoldoutPaths) -> dict:
    """``verify`` of every per-product store that exists beside ``base`` (MES's holdout 2):
    manifests in <base.manifest's dir>/holdout2/, sealed stores beside base.sealed_root, the same
    unlock log. Used by ``python -m data.holdout status``. A manifest whose name is not a product
    root is reported not ok (fail-closed), never skipped."""
    manifest_dir = base.manifest.parent / MANIFEST_DIR.name
    if not manifest_dir.is_dir():
        return {}
    out: dict[str, dict] = {}
    for manifest in sorted(manifest_dir.glob(f"*{MANIFEST_SUFFIX}")):
        root = manifest.name.removesuffix(MANIFEST_SUFFIX)
        try:
            paths = step2_holdout_paths(root, sealed_base=base.sealed_root.parent,
                                        manifest_dir=manifest_dir, unlock_log=base.unlock_log,
                                        registration=base.registration,
                                        vendor_root=base.vendor_root)
        except ValueError as exc:
            out[root] = {"all_ok": False, "error": str(exc)}
            continue
        out[root] = verify(root, paths)
    return out
