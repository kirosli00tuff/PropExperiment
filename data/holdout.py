"""Sealed holdout: a structural barrier around the Stage D.2 slice (Stage C, Task 6).

    uv run python -m data.holdout status    # both holdouts: checksums only, decrypts nothing
    uv run python -m data.holdout seal      # one-time migration (already run 2026-09-17)

The holdout (trade dates >= ``data.splits.HOLDOUT_START``) does not exist as a readable file
anywhere in the repo tree. What exists:
- ``data/processed/MES/..._research.parquet``: research + embargo rows only, and read-only.
- ``data/sealed/MES_holdout_v1/holdout_bars.sealed``: the holdout rows, encrypted.
- ``data/sealed/MES_holdout_v1/raw/...sealed``: every paid raw DBN file that overlaps the
  holdout, encrypted too, so "just rebuild from raw" is not a way around the seal.
- ``docs/HOLDOUT_MANIFEST.json`` (committed): sha256 of every sealed and plaintext blob,
  row counts, date range, cipher parameters. No prices and no price statistics.
- ``docs/HOLDOUT_UNLOCK_LOG.md`` (committed): append-only. Every seal and every unlock.

Reading the holdout is a ceremony, not a file read. ``unlock_holdout`` refuses unless ALL of
these hold:
1. ``acknowledgement`` equals ``ACKNOWLEDGEMENT`` exactly. The phrase is also the key
   material, so a guess cannot decrypt anything;
2. ``stage`` names Stage D.2;
3. ``REGISTRATION.md`` exists and is not empty: the pre-registered bar comes first. Its
   sha256 goes into the log, so the bar cannot be edited after the read unnoticed;
4. the sealed blob's sha256 still matches the manifest (tamper check);
5. ``prior_unlocks_acknowledged`` equals the number of unlocks already logged. A second
   read is possible, but it has to admit the holdout is already spent.
Only after the log entry has been written and flushed is anything decrypted. If the log
cannot be written, nothing is read.

Threat model, stated honestly: this stops accidents and convenience, not a determined
adversary. The phrase is written right here, so anyone can call the unlock. They cannot do
it silently or by accident, and they cannot do it without first writing a registration.
Known residual: MLCryptoEngine (another repo) still holds plaintext MES tick and book files
for 2026-07-15 and 2026-07-31, the Stage A.1 cost-calibration days, which fall inside this
holdout. They are outside this repo's control and are named in the manifest and the report.

Paid raw data is never lost: a raw file's plaintext is removed only after its sealed copy
decrypts back to the identical sha256. ``unseal_raw_file`` restores it, through the same
ceremony. ``is_sealed_raw`` lets the data puller refuse to buy a sealed range again.

Holdout 2 (Stage D.1f, reports/stage_d1f_confirmation_list.md section 1.2): trade dates
2024-04-01..2025-03-31, held as the 13 whole raw monthly chunks 2024-03..2025-03 and nothing
else (no bars blob). ``HOLDOUT2_PATHS`` is its HoldoutPaths: its own sealed store and manifest,
the SAME append-only unlock log, the same REGISTRATION.md, phrase and cipher.
``seal_holdout2_chunk`` seals one chunk the moment the D.1f puller has downloaded it (oldest
first) and removes the plaintext only after the sealed copy on disk decrypts back to it. The
manifest holds bytes and sha256s per chunk: no row counts, no dates, no prices. Its ceremony
takes the stage ``(stage )d.2 holdout 2``; unlocks are logged as "UNLOCK holdout 2 ..." and
counted per holdout, so holdout 1's count keeps its meaning. ``status`` reports both.
``complete_interrupted_seal`` finishes a seal cut off after its manifest record.
"""

from __future__ import annotations

import hashlib
import io
import json
import os
import re
import secrets
import stat
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from data.config import DATA_ROOT, PROCESSED_ROOT, REPO_ROOT, VENDOR_ROOT
from data.research_bars import (
    CONFIRMATION_LAST_TRADE_DATE,
    CONFIRMATION_SERIES_PATH,
    HOLDOUT2_END,
    HOLDOUT2_RAW_CHUNKS,
    HOLDOUT2_START,
    RESEARCH_PARQUET_NAME,
)
from data.splits import DATA_LAST_TRADE_DATE, HOLDOUT_START

ACKNOWLEDGEMENT = (
    "I am running Stage D.2 against the bar pre-registered in REGISTRATION.md, "
    "and I accept that reading the sealed holdout spends it."
)
MAGIC = b"PROPEXP-SEALED-1\n"
NONCE_BYTES = 16
KDF_ITERATIONS = 200_000
CIPHER = "PBKDF2-HMAC-SHA256(acknowledgement, salt) -> key; SHAKE-256(key || nonce) keystream XOR"
ORIGINAL_FULL_PARQUET_NAME = "ohlcv-1m_MES_v_0_2025-04-01_2026-09-16.parquet"
MIN_REASON_CHARS = 20
MIN_REGISTRATION_CHARS = 200
REGISTRATION_REQUIRED_WORDS = ("metric", "threshold", "decision")
HOLDOUT2_LABEL = "holdout 2"
# The ceremony's stage argument, per holdout (fullmatch, case-insensitive). Holdout 1's: Stage C's,
# unchanged. Holdout 2's: list 1.2 L-3 with "holdout 2" required (lead ruling N2); fullmatches L-3.
STAGE_PATTERNS = {1: r"\s*(stage\s+)?d\.2\s*", 2: r"(stage\s+)?d\.2\s+holdout\s+2"}
_HOLDOUT2_UNLOCK_MARK = f" UNLOCK {HOLDOUT2_LABEL} "
_CHUNK_NAME = re.compile(r"range=(\d{4}-\d{2}-\d{2})_(\d{4}-\d{2}-\d{2})\.dbn\.zst")


class HoldoutLockedError(PermissionError):
    """The unlock ceremony was not satisfied. Nothing was decrypted."""


class SealIntegrityError(RuntimeError):
    """A sealed blob no longer matches its manifest checksum."""


@dataclass(frozen=True)
class HoldoutPaths:
    sealed_root: Path
    manifest: Path
    unlock_log: Path
    registration: Path
    research_parquet: Path  # holdout 2: the confirmation parquet, checked for holdout-2 dates
    holdout_id: int = 1  # which holdout these paths guard: 1 (Stage C) or 2 (Stage D.1f)
    vendor_root: Path = VENDOR_ROOT  # holdout 2: where its raw chunks land before sealing

    @property
    def holdout_blob(self) -> Path:
        return self.sealed_root / "holdout_bars.sealed"


DEFAULT_PATHS = HoldoutPaths(
    sealed_root=DATA_ROOT / "sealed" / "MES_holdout_v1",
    manifest=REPO_ROOT / "docs" / "HOLDOUT_MANIFEST.json",
    unlock_log=REPO_ROOT / "docs" / "HOLDOUT_UNLOCK_LOG.md",
    registration=REPO_ROOT / "REGISTRATION.md",
    research_parquet=PROCESSED_ROOT / "MES" / RESEARCH_PARQUET_NAME,
)

HOLDOUT2_PATHS = HoldoutPaths(
    sealed_root=DATA_ROOT / "sealed" / "MES_holdout_v2",
    manifest=REPO_ROOT / "docs" / "HOLDOUT2_MANIFEST.json",
    unlock_log=REPO_ROOT / "docs" / "HOLDOUT_UNLOCK_LOG.md",  # the same append-only log
    registration=REPO_ROOT / "REGISTRATION.md",  # the same pre-registration requirement
    research_parquet=CONFIRMATION_SERIES_PATH,
    holdout_id=2,
)


# ------------------------------------------------------------------ cipher ----
def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(Path(path).read_bytes())


def _keystream_xor(data: bytes, acknowledgement: str, salt: bytes, nonce: bytes) -> bytes:
    key = hashlib.pbkdf2_hmac("sha256", acknowledgement.encode(), salt, KDF_ITERATIONS)
    stream = hashlib.shake_256(key + nonce).digest(len(data))
    return (np.frombuffer(data, np.uint8) ^ np.frombuffer(stream, np.uint8)).tobytes()


def seal_bytes(plaintext: bytes, acknowledgement: str, salt: bytes, nonce: bytes) -> bytes:
    if len(nonce) != NONCE_BYTES:
        raise ValueError(f"nonce must be {NONCE_BYTES} bytes")
    return MAGIC + nonce + _keystream_xor(plaintext, acknowledgement, salt, nonce)


def open_sealed(blob: bytes, acknowledgement: str, salt: bytes, expected_sha256: str) -> bytes:
    """Decrypt and verify. A wrong phrase yields garbage, which the checksum rejects."""
    if not blob.startswith(MAGIC):
        raise SealIntegrityError("not a sealed blob")
    nonce = blob[len(MAGIC):len(MAGIC) + NONCE_BYTES]
    plaintext = _keystream_xor(blob[len(MAGIC) + NONCE_BYTES:], acknowledgement, salt, nonce)
    if sha256_bytes(plaintext) != expected_sha256:
        raise SealIntegrityError("decrypted bytes do not match the manifest checksum")
    return plaintext


# ------------------------------------------------------------------ splitting ----
def split_research_holdout(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """(rows before HOLDOUT_START, rows on/after it), by CME trade date. Pure."""
    held = frame["trade_date"].astype(str) >= HOLDOUT_START.isoformat()
    return frame.loc[~held].reset_index(drop=True), frame.loc[held].reset_index(drop=True)


def _parquet_bytes(table: pa.Table) -> bytes:
    sink = io.BytesIO()
    pq.write_table(table, sink)
    return sink.getvalue()


def sealed_window_utc_dates() -> tuple[str, str]:
    """[start, end) UTC dates that can hold a sealed bar. The first holdout session opens 17:00 CT
    the calendar day before HOLDOUT_START; the last sealed trade date is the data's last one."""
    start = (pd.Timestamp(HOLDOUT_START) - pd.Timedelta(days=1)).date().isoformat()
    end = (pd.Timestamp(DATA_LAST_TRADE_DATE) + pd.Timedelta(days=1)).date().isoformat()
    return start, end


def request_touches_sealed_window(start: str, end: str) -> bool:
    """True if a vendor request for [start, end) (UTC dates, end exclusive) could return sealed
    bars. Data AFTER the sealed window (Stage E forward data) is not blocked. Holdout-2 chunks
    count once sealed, so no schema of an already sealed holdout-2 range is bought again."""
    sealed_start, sealed_end = sealed_window_utc_dates()
    return (start < sealed_end and end > sealed_start) or request_touches_holdout2(start, end)


def request_touches_holdout2(start: str, end: str, paths: HoldoutPaths | None = None) -> bool:
    """True if [start, end) overlaps a chunk already sealed as holdout 2. The next unsealed chunk
    is not blocked, which is what lets the D.1f puller buy and seal them one at a time."""
    paths = paths or HOLDOUT2_PATHS
    if not paths.manifest.exists():
        return False
    return any(start < e and end > s for s, e in _sealed_chunks(load_manifest(paths)))


def raw_files_overlapping_holdout(raw_paths: Sequence[Path]) -> list[Path]:
    """Monthly raw chunks named range=<start>_<end> (end exclusive, UTC dates) that can hold
    any bar of the holdout. The first holdout session opens 17:00 CT on the calendar day
    before HOLDOUT_START, so any chunk ending after that day is included (a day of margin)."""
    first_session_day = (pd.Timestamp(HOLDOUT_START) - pd.Timedelta(days=1)).date().isoformat()
    out = []
    for path in raw_paths:
        _, end = Path(path).name.removeprefix("range=").removesuffix(".dbn.zst").split("_")
        if end > first_session_day:
            out.append(Path(path))
    return out


# ------------------------------------------------------------------ logging ----
def _append_log(paths: HoldoutPaths, heading: str, lines: Sequence[str]) -> None:
    paths.unlock_log.parent.mkdir(parents=True, exist_ok=True)
    new = not paths.unlock_log.exists()
    with paths.unlock_log.open("a") as fh:
        if new:
            fh.write("# Holdout unlock log\n\nAppend-only. `data/holdout.py` writes each entry "
                     "BEFORE any sealed byte is decrypted. Do not edit or delete entries.\n")
        fh.write(f"\n## {heading}\n\n" + "".join(f"- {line}\n" for line in lines))
        fh.flush()
        os.fsync(fh.fileno())


def prior_unlocks(paths: HoldoutPaths | None = None) -> int:
    """Unlocks already logged FOR THIS HOLDOUT. Holdout-2 headings read "UNLOCK holdout 2 ...";
    every other UNLOCK heading is holdout 1's, so its count means what it always meant."""
    paths = paths or DEFAULT_PATHS
    if not paths.unlock_log.exists():
        return 0
    unlocks = [line for line in paths.unlock_log.read_text().splitlines()
               if line.startswith("## ") and " UNLOCK " in line]
    return sum(1 for line in unlocks
               if (_HOLDOUT2_UNLOCK_MARK in line) == (paths.holdout_id == 2))


def load_manifest(paths: HoldoutPaths | None = None) -> dict:
    paths = paths or DEFAULT_PATHS
    if not paths.manifest.exists():
        raise SealIntegrityError(f"no holdout manifest at {paths.manifest}")
    return json.loads(paths.manifest.read_text())


def _relpath_in_repo(path: Path) -> str | None:
    """Repo-relative spelling, or None for a path outside the repo (tests, other machines)."""
    try:
        return str(Path(path).resolve().relative_to(REPO_ROOT))
    except ValueError:
        return None


def _record_paths(record: dict) -> set[Path]:
    """Both spellings of a sealed file's original location: repo-relative (portable) and the
    absolute path recorded when it was sealed (provenance, valid only on that machine)."""
    out = {Path(record["original_path"])}
    if record.get("original_relpath"):
        out.add(REPO_ROOT / record["original_relpath"])
    return {p.resolve() for p in out}


def is_sealed_raw(path: Path, paths: HoldoutPaths | None = None) -> bool:
    """True if ``path`` is a raw vendor file held in the sealed store (never re-buy it). With no
    ``paths``, BOTH holdouts' manifests are checked (list 1.2 L-1), so every caller that relies
    on the default (the adapter's refuse-existing, the A.1 puller, the bar builder) refuses a
    sealed holdout-2 chunk too."""
    if paths is None:
        return any(is_sealed_raw(path, p) for p in (DEFAULT_PATHS, HOLDOUT2_PATHS))
    if not paths.manifest.exists():
        return False
    target = Path(path).resolve()
    return any(target in _record_paths(r) for r in load_manifest(paths).get("raw_files", []))


def _refuse_unless_ceremony(stage: str, reason: str, acknowledgement: str,
                            prior_unlocks_acknowledged: int, paths: HoldoutPaths) -> str:
    """Raise HoldoutLockedError unless every condition holds; return the registration sha256."""
    if acknowledgement != ACKNOWLEDGEMENT:
        raise HoldoutLockedError("acknowledgement does not match data.holdout.ACKNOWLEDGEMENT")
    if not re.fullmatch(STAGE_PATTERNS[paths.holdout_id], stage, re.IGNORECASE):
        raise HoldoutLockedError(f"stage {stage!r} is not Stage D.2, the holdout's only consumer"
                                 f" (it must fullmatch {STAGE_PATTERNS[paths.holdout_id]!r})")
    if any("\n" in text or "#" in text for text in (stage, reason)):
        raise HoldoutLockedError("stage and reason go into the log's markdown headings: no "
                                 "newlines or '#' characters")
    if len(reason.strip()) < MIN_REASON_CHARS:
        raise HoldoutLockedError(f"state a real reason (>= {MIN_REASON_CHARS} characters); "
                                 "it goes in the log")
    registration = paths.registration.read_text() if paths.registration.exists() else ""
    missing_words = [w for w in REGISTRATION_REQUIRED_WORDS if w not in registration.lower()]
    if len(registration.strip()) < MIN_REGISTRATION_CHARS or missing_words:
        raise HoldoutLockedError(
            f"{paths.registration.name} is not a pre-registered bar: it needs at least "
            f"{MIN_REGISTRATION_CHARS} characters and must state each of "
            f"{REGISTRATION_REQUIRED_WORDS} (missing: {missing_words or 'none'}). Write the bar "
            "BEFORE reading the holdout; its sha256 goes into the log.")
    already = prior_unlocks(paths)
    if prior_unlocks_acknowledged != already:
        raise HoldoutLockedError(f"the log shows {already} prior unlock(s); pass "
                                 f"prior_unlocks_acknowledged={already} to confirm you know")
    return sha256_file(paths.registration)


# ------------------------------------------------------------------ unlock ----
def unlock_holdout(*, stage: str, reason: str, acknowledgement: str,
                   prior_unlocks_acknowledged: int = 0,
                   paths: HoldoutPaths | None = None) -> pd.DataFrame:
    """The ONLY way to read holdout bars. Logs first, then decrypts and verifies."""
    paths = paths or DEFAULT_PATHS
    if paths.holdout_id != 1:
        raise ValueError(f"{HOLDOUT2_LABEL} has no bars blob, only sealed raw chunks: restore "
                         "them with unseal_raw_file through the same ceremony")
    registration_sha = _refuse_unless_ceremony(stage, reason, acknowledgement,
                                               prior_unlocks_acknowledged, paths)
    manifest = load_manifest(paths)
    entry = manifest["holdout"]
    blob = paths.holdout_blob.read_bytes()
    if sha256_bytes(blob) != entry["sha256_sealed"]:
        raise SealIntegrityError("sealed holdout blob does not match the manifest")
    _append_log(paths, f"{datetime.now(UTC).isoformat()} UNLOCK holdout bars ({stage})", [
        f"reason: {reason.strip()}",
        f"registration: {paths.registration.name} sha256 {registration_sha}",
        f"manifest sha256: {sha256_file(paths.manifest)}",
        f"prior unlocks acknowledged: {prior_unlocks_acknowledged}",
        f"rows: {entry['rows']}, trade dates {entry['first_trade_date']}.."
        f"{entry['last_trade_date']}",
    ])
    plaintext = open_sealed(blob, acknowledgement, bytes.fromhex(manifest["salt_hex"]),
                            entry["sha256_plaintext"])
    return pq.read_table(io.BytesIO(plaintext)).to_pandas()


def unseal_raw_file(original_path: Path, *, stage: str, reason: str, acknowledgement: str,
                    prior_unlocks_acknowledged: int = 0,
                    paths: HoldoutPaths | None = None) -> Path:
    """Restore one paid raw file to its original path (read-only), through the same ceremony."""
    paths = paths or DEFAULT_PATHS
    registration_sha = _refuse_unless_ceremony(stage, reason, acknowledgement,
                                               prior_unlocks_acknowledged, paths)
    manifest = load_manifest(paths)
    target = Path(original_path).resolve()
    record = next((r for r in manifest["raw_files"] if target in _record_paths(r)), None)
    if record is None:
        raise KeyError(f"{original_path} is not in the sealed raw store")
    if target.exists():
        raise FileExistsError(f"{target} already exists; raw files are never overwritten")
    blob = (paths.sealed_root / record["sealed_relpath"]).read_bytes()
    if sha256_bytes(blob) != record["sha256_sealed"]:
        raise SealIntegrityError(f"sealed raw blob for {target.name} does not match the manifest")
    label = f"{HOLDOUT2_LABEL} " if paths.holdout_id == 2 else ""
    _append_log(paths, f"{datetime.now(UTC).isoformat()} UNLOCK {label}raw file ({stage})", [
        f"reason: {reason.strip()}", f"file: {target.name}",
        f"registration: {paths.registration.name} sha256 {registration_sha}",
        f"prior unlocks acknowledged: {prior_unlocks_acknowledged}",
    ])
    plaintext = open_sealed(blob, acknowledgement, bytes.fromhex(manifest["salt_hex"]),
                            record["sha256_plaintext"])
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("xb") as fh:
        fh.write(plaintext)
    target.chmod(stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
    return target


# ------------------------------------------------------------------ verify ----
def _unlock_log_intact(manifest: dict, paths: HoldoutPaths) -> bool:
    """The log is append-only: its first ``bytes_at_seal`` bytes must still hash to what they
    hashed to at seal time. Catches a deleted, truncated or rewritten history, which would
    otherwise reset the prior-unlock count to zero."""
    recorded = manifest.get("unlock_log_at_seal")
    if not recorded:
        return paths.unlock_log.exists()
    if not paths.unlock_log.exists():
        return False
    head = paths.unlock_log.read_bytes()[:recorded["bytes"]]
    return len(head) == recorded["bytes"] and sha256_bytes(head) == recorded["sha256"]


def verify_seal(paths: HoldoutPaths | None = None) -> dict:
    """Checksums only. Decrypts nothing and writes no log entry."""
    paths = paths or DEFAULT_PATHS
    if paths.holdout_id == 2:
        return _verify_holdout2(paths)
    manifest = load_manifest(paths)
    report: dict = {
        "holdout_blob_ok": paths.holdout_blob.exists()
        and sha256_file(paths.holdout_blob) == manifest["holdout"]["sha256_sealed"],
        "research_parquet_ok": paths.research_parquet.exists()
        and sha256_file(paths.research_parquet) == manifest["research"]["sha256"],
        "raw_files": {},
    }
    for record in manifest["raw_files"]:
        sealed = paths.sealed_root / record["sealed_relpath"]
        report["raw_files"][Path(record["original_path"]).name] = {
            "sealed_ok": sealed.exists() and sha256_file(sealed) == record["sha256_sealed"],
            "plaintext_absent": not any(p.exists() for p in _record_paths(record)),
        }
    report["unlock_log_ok"] = _unlock_log_intact(manifest, paths)
    last = ""
    if paths.research_parquet.exists():
        dates = pq.read_table(paths.research_parquet, columns=["trade_date"]).column("trade_date")
        last = max(dates.to_pylist(), default="")
    report["research_has_no_holdout_rows"] = bool(last) and last < HOLDOUT_START.isoformat()
    report["unlocks_logged"] = prior_unlocks(paths)
    report["all_ok"] = bool(report["holdout_blob_ok"] and report["research_parquet_ok"]
                            and report["research_has_no_holdout_rows"] and report["unlock_log_ok"]
                            and all(v["sealed_ok"] and v["plaintext_absent"]
                                    for v in report["raw_files"].values()))
    return report


# ------------------------------------------------------------------ seal (one-time) ----
def seal_holdout(full_parquet: Path, raw_paths: Sequence[Path],
                 paths: HoldoutPaths | None = None, *, remove_plaintext: bool) -> dict:
    """One-time migration. Every removal happens only after a verified round trip."""
    paths = paths or DEFAULT_PATHS
    if paths.holdout_id != 1:
        raise ValueError("seal_holdout is holdout 1's migration; see seal_holdout2_chunk")
    if paths.manifest.exists():
        raise FileExistsError(f"{paths.manifest} exists: the holdout is already sealed")
    table = pq.read_table(full_parquet)
    frame = table.to_pandas()
    research, holdout = split_research_holdout(frame)
    if holdout.empty:
        raise ValueError("no holdout rows found; refusing to write an empty seal")
    salt, nonce = secrets.token_bytes(16), secrets.token_bytes(NONCE_BYTES)
    metadata = table.schema.metadata or {}

    research_table = pa.Table.from_pandas(research, preserve_index=False).replace_schema_metadata(
        {**metadata, b"propexperiment_holdout": json.dumps(
            {"sealed": True, "holdout_start_trade_date": HOLDOUT_START.isoformat()}).encode()})
    holdout_bytes = _parquet_bytes(
        pa.Table.from_pandas(holdout, preserve_index=False).replace_schema_metadata(metadata))
    blob = seal_bytes(holdout_bytes, ACKNOWLEDGEMENT, salt, nonce)

    # Reconstruction proof BEFORE anything is written or removed.
    reopened = pq.read_table(io.BytesIO(
        open_sealed(blob, ACKNOWLEDGEMENT, salt, sha256_bytes(holdout_bytes)))).to_pandas()
    if not pd.concat([research, reopened], ignore_index=True).equals(frame.reset_index(drop=True)):
        raise SealIntegrityError("research + sealed holdout does not reproduce the full series")

    paths.sealed_root.mkdir(parents=True, exist_ok=True)
    with paths.holdout_blob.open("xb") as fh:
        fh.write(blob)
    paths.research_parquet.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(research_table, paths.research_parquet)
    paths.research_parquet.chmod(stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
    if not pq.read_table(paths.research_parquet).to_pandas().equals(research):
        raise SealIntegrityError("research parquet did not persist intact")

    raw_records = []
    for raw in raw_files_overlapping_holdout(raw_paths):
        data = raw.read_bytes()
        raw_blob = seal_bytes(data, ACKNOWLEDGEMENT, salt, secrets.token_bytes(NONCE_BYTES))
        open_sealed(raw_blob, ACKNOWLEDGEMENT, salt, sha256_bytes(data))  # raises on mismatch
        rel = Path("raw") / (raw.name + ".sealed")
        sealed_path = paths.sealed_root / rel
        sealed_path.parent.mkdir(parents=True, exist_ok=True)
        with sealed_path.open("xb") as fh:
            fh.write(raw_blob)
        if sha256_file(sealed_path) != sha256_bytes(raw_blob):
            raise SealIntegrityError(f"sealed copy of {raw.name} did not persist intact")
        raw_records.append({"original_path": str(raw),
                            "original_relpath": _relpath_in_repo(raw),
                            "sealed_relpath": str(rel),
                            "bytes": len(data), "sha256_plaintext": sha256_bytes(data),
                            "sha256_sealed": sha256_bytes(raw_blob)})

    manifest = {
        "created_utc": datetime.now(UTC).isoformat(),
        "holdout_start_trade_date": HOLDOUT_START.isoformat(),
        "cipher": CIPHER, "kdf_iterations": KDF_ITERATIONS, "salt_hex": salt.hex(),
        "acknowledgement_sha256": sha256_bytes(ACKNOWLEDGEMENT.encode()),
        "original_full_parquet": {"name": Path(full_parquet).name,
                                  "sha256": sha256_file(full_parquet), "rows": len(frame)},
        "research": {"path": str(paths.research_parquet), "sha256":
                     sha256_file(paths.research_parquet), "rows": len(research),
                     "first_trade_date": str(research["trade_date"].min()),
                     "last_trade_date": str(research["trade_date"].max())},
        "holdout": {"sealed_file": paths.holdout_blob.name,
                    "sha256_sealed": sha256_bytes(blob),
                    "sha256_plaintext": sha256_bytes(holdout_bytes), "rows": len(holdout),
                    "trade_dates": int(holdout["trade_date"].nunique()),
                    "first_trade_date": str(holdout["trade_date"].min()),
                    "last_trade_date": str(holdout["trade_date"].max())},
        "raw_files": raw_records,
        "residual_exposure": [
            "MLCryptoEngine (another repo) holds plaintext MES trades and mbp-10 files for "
            "2026-07-15 and 2026-07-31 (Stage A.1 cost-calibration and tick cross-check days), "
            "inside the holdout period; this repo does not control them.",
            "reports/bar_validation_summary.json and reports/tick_crosscheck_summary.json predate "
            "the seal and describe data structure (gaps, holidays, tick-match counts) over the "
            "whole window, not returns.",
        ],
    }
    paths.manifest.parent.mkdir(parents=True, exist_ok=True)
    with paths.manifest.open("x") as fh:
        json.dump(manifest, fh, indent=1)
    log_entry = [
        f"holdout trade dates {manifest['holdout']['first_trade_date']}.."
        f"{manifest['holdout']['last_trade_date']} ({manifest['holdout']['rows']} bars)",
        "sealed raw files: " + ", ".join(Path(r["original_path"]).name for r in raw_records),
        f"manifest sha256: {sha256_file(paths.manifest)}",
    ]
    _append_log(paths, f"{manifest['created_utc']} SEALED", log_entry)
    # Pin the log's sealed prefix so a later deletion or rewrite is detectable.
    manifest["unlock_log_at_seal"] = {"bytes": paths.unlock_log.stat().st_size,
                                      "sha256": sha256_file(paths.unlock_log)}
    paths.manifest.write_text(json.dumps(manifest, indent=1))

    if remove_plaintext:
        for record in raw_records:
            sealed = paths.sealed_root / record["sealed_relpath"]
            open_sealed(sealed.read_bytes(), ACKNOWLEDGEMENT, salt, record["sha256_plaintext"])
            Path(record["original_path"]).unlink()
        Path(full_parquet).unlink()
    return manifest


# ------------------------------------------------------------------ holdout 2 ----
def _chunk_of(path: Path) -> tuple[str, str]:
    """(start, end) of a raw monthly chunk named range=<start>_<end>.dbn.zst."""
    match = _CHUNK_NAME.fullmatch(Path(path).name)
    if match is None:
        raise ValueError(f"{Path(path).name} is not a raw chunk name range=<start>_<end>.dbn.zst")
    return match.group(1), match.group(2)


def partial_path(path: Path) -> Path:
    """The in-flight name data.adapter.fetch_range downloads to before linking the target."""
    return path.with_name(path.name + ".partial")


def _sealed_chunks(manifest: dict) -> list[tuple[str, str]]:
    return [_chunk_of(Path(r["original_path"])) for r in manifest.get("raw_files", [])]


def holdout2_raw_paths(paths: HoldoutPaths | None = None) -> list[Path]:
    """Where the 13 holdout-2 chunks land when bought (the adapter's raw_path), oldest first."""
    from data.adapter import MES_CONTINUOUS, OHLCV_1M, raw_path  # lazy: adapter imports us lazily

    paths = paths or HOLDOUT2_PATHS
    return [raw_path(MES_CONTINUOUS, OHLCV_1M, s, e, paths.vendor_root)
            for s, e in HOLDOUT2_RAW_CHUNKS]


def next_holdout2_chunk(paths: HoldoutPaths | None = None) -> tuple[str, str] | None:
    """The only holdout-2 chunk that may be sealed next (oldest first), or None when all are."""
    paths = paths or HOLDOUT2_PATHS
    done = _sealed_chunks(load_manifest(paths)) if paths.manifest.exists() else []
    if done != list(HOLDOUT2_RAW_CHUNKS[:len(done)]):
        raise SealIntegrityError(f"{paths.manifest.name} lists chunks out of order: {done}")
    return HOLDOUT2_RAW_CHUNKS[len(done)] if len(done) < len(HOLDOUT2_RAW_CHUNKS) else None


def _fsync_dir(directory: Path) -> None:
    fd = os.open(directory, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _write_manifest(path: Path, manifest: dict, *, create: bool) -> None:
    """Durable manifest write: temp file + fsync, then link (create: never replaces an existing
    manifest) or atomic replace (update)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.unlink(missing_ok=True)
    with tmp.open("x") as fh:
        json.dump(manifest, fh, indent=1)
        fh.flush()
        os.fsync(fh.fileno())
    if create:
        os.link(tmp, path)
        tmp.unlink()
    else:
        os.replace(tmp, path)
    _fsync_dir(path.parent)


def _new_holdout2_manifest() -> dict:
    return {
        "holdout": HOLDOUT2_LABEL, "created_utc": datetime.now(UTC).isoformat(),
        "declaration": "reports/stage_d1f_confirmation_list.md section 1.2",
        "holdout_start_trade_date": HOLDOUT2_START.isoformat(),
        "holdout_end_trade_date": HOLDOUT2_END.isoformat(),
        "cipher": CIPHER, "kdf_iterations": KDF_ITERATIONS,
        "salt_hex": secrets.token_bytes(16).hex(),
        "acknowledgement_sha256": sha256_bytes(ACKNOWLEDGEMENT.encode()),
        "expected_raw_chunks": [f"range={s}_{e}.dbn.zst" for s, e in HOLDOUT2_RAW_CHUNKS],
        "raw_files": [],
    }


def _refuse_holdout2_seal(raw: Path, paths: HoldoutPaths, manifest: dict | None) -> None:
    """Every refusal happens before a byte is read, written or removed."""
    if paths.holdout_id != 2:
        raise ValueError("seal_holdout2_chunk needs holdout-2 paths (holdout_id=2)")
    chunk = _chunk_of(raw)
    if chunk not in HOLDOUT2_RAW_CHUNKS:
        raise ValueError(f"{raw.name} is not one of the 13 holdout-2 chunks; it is never sealed")
    expected = holdout2_raw_paths(paths)[HOLDOUT2_RAW_CHUNKS.index(chunk)]
    if raw.resolve() != expected.resolve():
        raise ValueError(f"{raw} is not where the adapter stores {raw.name} ({expected})")
    if manifest is not None and any(raw.resolve() in _record_paths(r)
                                    for r in manifest["raw_files"]):
        raise FileExistsError(f"{raw.name} is already in {paths.manifest.name}: sealed once only")
    if chunk != next_holdout2_chunk(paths):
        raise SealIntegrityError(f"out of order: {raw.name} arrived but the next chunk to seal "
                                 f"is {next_holdout2_chunk(paths)} (oldest first)")
    if manifest is not None and not _unlock_log_intact(manifest, paths):
        raise SealIntegrityError("the unlock log no longer matches its pinned prefix: refusing "
                                 "to re-pin a rewritten history")
    sealed_path = paths.sealed_root / "raw" / (raw.name + ".sealed")
    if sealed_path.exists():
        raise FileExistsError(f"{sealed_path} exists but {raw.name} is not in the manifest: an "
                              "earlier seal was interrupted. The plaintext is kept; inspect and "
                              "remove the orphan by hand, then re-run.")
    if not raw.is_file():
        raise FileNotFoundError(f"{raw} does not exist: nothing to seal")


def seal_holdout2_chunk(raw: Path, paths: HoldoutPaths | None = None, *, note: str = "") -> dict:
    """Seal one holdout-2 raw chunk the moment it arrives. Nothing is decoded: the bytes are
    encrypted as they are. Order: prove the round trip in memory, write the blob ("xb", fsync),
    prove it again from disk, append the manifest record, log SEALED, pin the log, and only then
    remove the plaintext (and any stale in-flight copy). Any failure raises before removal."""
    paths, raw = paths or HOLDOUT2_PATHS, Path(raw)
    manifest = load_manifest(paths) if paths.manifest.exists() else None
    _refuse_holdout2_seal(raw, paths, manifest)
    create = manifest is None
    manifest = _new_holdout2_manifest() if create else manifest
    salt = bytes.fromhex(manifest["salt_hex"])

    data = raw.read_bytes()
    sha_plain = sha256_bytes(data)
    blob = seal_bytes(data, ACKNOWLEDGEMENT, salt, secrets.token_bytes(NONCE_BYTES))
    open_sealed(blob, ACKNOWLEDGEMENT, salt, sha_plain)  # raises on mismatch; nothing written
    rel = Path("raw") / (raw.name + ".sealed")
    sealed_path = paths.sealed_root / rel
    sealed_path.parent.mkdir(parents=True, exist_ok=True)
    with sealed_path.open("xb") as fh:
        fh.write(blob)
        fh.flush()
        os.fsync(fh.fileno())
    _fsync_dir(sealed_path.parent)
    on_disk = sealed_path.read_bytes()
    if sha256_bytes(on_disk) != sha256_bytes(blob):
        raise SealIntegrityError(f"sealed copy of {raw.name} did not persist intact")
    open_sealed(on_disk, ACKNOWLEDGEMENT, salt, sha_plain)  # the proof that licenses removal

    record = {"original_path": str(raw), "original_relpath": _relpath_in_repo(raw),
              "sealed_relpath": str(rel), "bytes": len(data), "sha256_plaintext": sha_plain,
              "sha256_sealed": sha256_bytes(blob)}
    manifest = {**manifest, "raw_files": [*manifest["raw_files"], record]}
    _write_manifest(paths.manifest, manifest, create=create)
    _append_log(paths, f"{datetime.now(UTC).isoformat()} SEALED {HOLDOUT2_LABEL} raw chunk "
                       f"{raw.name}", [
        f"chunk {len(manifest['raw_files'])} of {len(HOLDOUT2_RAW_CHUNKS)}, sealed on arrival, "
        "oldest first",
        f"plaintext sha256 {sha_plain}; sealed sha256 {record['sha256_sealed']}",
        f"manifest sha256: {sha256_file(paths.manifest)}",
        "the sealed copy on disk decrypted back to the plaintext sha256 before removal",
        *([note] if note else []),
    ])
    _pin_log_and_remove(raw, paths, manifest)
    return record


def _pin_log_and_remove(raw: Path, paths: HoldoutPaths, manifest: dict) -> None:
    """Pin the log's prefix in the manifest, then remove the plaintext. Callers prove first."""
    pin = {"bytes": paths.unlock_log.stat().st_size, "sha256": sha256_file(paths.unlock_log)}
    _write_manifest(paths.manifest, {**manifest, "unlock_log_at_seal": pin}, create=False)
    for path in (raw, partial_path(raw)):
        path.unlink(missing_ok=True)
    _fsync_dir(raw.parent)
    if raw.exists() or partial_path(raw).exists():
        raise SealIntegrityError(f"plaintext of {raw.name} survived removal")


def complete_interrupted_seal(raw: Path, paths: HoldoutPaths | None = None) -> dict:
    """Finish a holdout-2 seal that stopped after its manifest record. The normal path's proof
    licenses removal (blob sha256 as recorded, decrypts to the recorded plaintext sha256, and
    the file removed is that plaintext); then log, re-pin, remove. A failure removes nothing."""
    paths, raw = paths or HOLDOUT2_PATHS, Path(raw)
    manifest = load_manifest(paths)
    record = next((r for r in manifest["raw_files"] if raw.resolve() in _record_paths(r)), None)
    if paths.holdout_id != 2 or record is None:
        raise ValueError(f"{raw.name} is not a sealed {HOLDOUT2_LABEL} chunk: nothing to finish")
    if not _unlock_log_intact(manifest, paths):
        raise SealIntegrityError("the unlock log no longer matches its pinned prefix: refusing "
                                 "to re-pin a rewritten history")
    blob = (paths.sealed_root / record["sealed_relpath"]).read_bytes()
    if sha256_bytes(blob) != record["sha256_sealed"]:
        raise SealIntegrityError(f"sealed blob of {raw.name} does not match the manifest")
    open_sealed(blob, ACKNOWLEDGEMENT, bytes.fromhex(manifest["salt_hex"]),
                record["sha256_plaintext"])  # raises unless it decrypts to the recorded bytes
    if raw.exists() and sha256_file(raw) != record["sha256_plaintext"]:
        raise SealIntegrityError(f"{raw.name} is sealed but the file at its path is not the "
                                 "sealed plaintext, so not what an interrupted seal leaves: kept")
    _append_log(paths, f"{datetime.now(UTC).isoformat()} RESUMED {HOLDOUT2_LABEL} raw chunk "
                       f"{raw.name}", ["plaintext removed on resume: sealed sha256 "
                       "{sha256_sealed} decrypted back to {sha256_plaintext}".format(**record)])
    _pin_log_and_remove(raw, paths, manifest)
    return record


def _confirmation_clean(paths: HoldoutPaths) -> bool | None:
    """None if the confirmation parquet is not built; else True iff no trade date after
    CONFIRMATION_LAST_TRADE_DATE (so no embargo, holdout-2 or mined date) is in it."""
    if not paths.research_parquet.exists():
        return None
    try:
        dates = pq.read_table(paths.research_parquet, columns=["trade_date"]).column("trade_date")
    except (KeyError, ValueError, pa.ArrowException):
        return False  # cannot be verified, so it is not clean
    last = max((str(d)[:10] for d in dates.to_pylist()), default="")
    return last <= CONFIRMATION_LAST_TRADE_DATE.isoformat()


def _verify_holdout2(paths: HoldoutPaths) -> dict:
    """Holdout 2's verify_seal. Before the first chunk is sealed (all of the D.1f build) it
    reports state "not_yet_sealed" and all_ok False rather than failing."""
    manifest = load_manifest(paths) if paths.manifest.exists() else None
    records = manifest["raw_files"] if manifest else []
    raw_files = {}
    for record in records:
        sealed = paths.sealed_root / record["sealed_relpath"]
        raw_files[Path(record["original_path"]).name] = {
            "sealed_ok": sealed.exists() and sha256_file(sealed) == record["sha256_sealed"],
            "plaintext_absent": not any(p.exists() or partial_path(p).exists()
                                        for p in _record_paths(record)),
        }
    done = _sealed_chunks(manifest) if manifest else []
    unsealed = [p for p, c in zip(holdout2_raw_paths(paths), HOLDOUT2_RAW_CHUNKS, strict=True)
                if c not in done]
    report: dict = {
        "holdout": HOLDOUT2_LABEL,
        "state": ("not_yet_sealed" if not done else
                  "sealed" if len(done) == len(HOLDOUT2_RAW_CHUNKS) else "partially_sealed"),
        "chunks_expected": len(HOLDOUT2_RAW_CHUNKS), "chunks_sealed": len(done),
        "sealed_in_order": done == list(HOLDOUT2_RAW_CHUNKS[:len(done)]),
        "raw_files": raw_files,
        "unsealed_plaintext_present": [p.name for p in unsealed
                                       if p.exists() or partial_path(p).exists()],
        "unlock_log_ok": _unlock_log_intact(manifest or {}, paths),
        "confirmation_has_no_holdout2_rows": _confirmation_clean(paths),
        "unlocks_logged": prior_unlocks(paths),
    }
    report["all_ok"] = bool(
        report["state"] == "sealed" and report["sealed_in_order"] and report["unlock_log_ok"]
        and not report["unsealed_plaintext_present"]
        and report["confirmation_has_no_holdout2_rows"] is not False
        and all(v["sealed_ok"] and v["plaintext_absent"] for v in raw_files.values()))
    return report


def status_report() -> dict:
    """Holdout 1's report with its keys unchanged at the top level (so existing callers and the
    session-start check read the same fields), plus a ``holdout_2`` section."""
    return {**verify_seal(DEFAULT_PATHS), "holdout_2": verify_seal(HOLDOUT2_PATHS)}


def main(argv: Sequence[str]) -> int:
    command = argv[1] if len(argv) > 1 else "status"
    if command == "status":
        print(json.dumps(status_report(), indent=1))
        return 0
    if command == "seal":
        from data.adapter import MES_CONTINUOUS, OHLCV_1M, raw_path
        from data.pull_mes import WINDOW_END, WINDOW_START, monthly_chunks

        full = PROCESSED_ROOT / "MES" / ORIGINAL_FULL_PARQUET_NAME
        raws = [raw_path(MES_CONTINUOUS, OHLCV_1M, s, e, VENDOR_ROOT)
                for s, e in monthly_chunks(WINDOW_START, WINDOW_END)]
        manifest = seal_holdout(full, raws, remove_plaintext=True)
        print(json.dumps({k: manifest[k] for k in ("research", "holdout")}, indent=1))
        print(json.dumps(verify_seal(), indent=1))
        return 0
    print("usage: python -m data.holdout [status|seal]")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
