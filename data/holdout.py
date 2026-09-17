"""Sealed holdout: a structural barrier around the Stage D.2 slice (Stage C, Task 6).

    uv run python -m data.holdout status    # verify checksums; decrypts nothing, logs nothing
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
from data.research_bars import RESEARCH_PARQUET_NAME
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
    research_parquet: Path

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
    bars. Data AFTER the sealed window (Stage E forward data) is not blocked."""
    sealed_start, sealed_end = sealed_window_utc_dates()
    return start < sealed_end and end > sealed_start


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
    paths = paths or DEFAULT_PATHS
    if not paths.unlock_log.exists():
        return 0
    return sum(1 for line in paths.unlock_log.read_text().splitlines()
               if line.startswith("## ") and " UNLOCK " in line)


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
    """True if ``path`` is a raw vendor file held in the sealed store (never re-buy it)."""
    paths = paths or DEFAULT_PATHS
    if not paths.manifest.exists():
        return False
    target = Path(path).resolve()
    return any(target in _record_paths(r) for r in load_manifest(paths).get("raw_files", []))


def _refuse_unless_ceremony(stage: str, reason: str, acknowledgement: str,
                            prior_unlocks_acknowledged: int, paths: HoldoutPaths) -> str:
    """Raise HoldoutLockedError unless every condition holds; return the registration sha256."""
    if acknowledgement != ACKNOWLEDGEMENT:
        raise HoldoutLockedError("acknowledgement does not match data.holdout.ACKNOWLEDGEMENT")
    if not re.fullmatch(r"\s*(stage\s+)?d\.2\s*", stage, re.IGNORECASE):
        raise HoldoutLockedError(f"stage {stage!r} is not Stage D.2, the holdout's only consumer")
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
    _append_log(paths, f"{datetime.now(UTC).isoformat()} UNLOCK raw file ({stage})", [
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


def main(argv: Sequence[str]) -> int:
    command = argv[1] if len(argv) > 1 else "status"
    if command == "status":
        print(json.dumps(verify_seal(), indent=1))
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
