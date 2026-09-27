"""Resumable JSONL ledgers and the model hash chain (M7.6, M8).

One ledger file per (challenger, horizon) under ``<out_dir>/ledger/``. Each line is one fit
(a configuration on a CPCV split, or a refit on blocks 1-5), keyed by ``key``; a key already in
the ledger is skipped on restart. Every record carries the fitted model's sha256, the machine
that ran the fit, the harness manifest sha256 that preflight returned, and ``prev_sha256``, the
sha256 of the previous line, so the file is a hash chain: ``verify_chain`` raises on any edited,
dropped or reordered line.

Model hashes are reproducible on one machine (fixed seeds, frozen thread counts, deterministic
LightGBM and torch settings) but need not match across machines. ``check_refit`` therefore
refuses a different hash for the same key only when the machine is the same; a fit from another
machine is recorded with its own machine id and never compared. ``verify_model_file`` refuses a
saved model whose bytes no longer hash to the recorded value (the test run's refusal).
"""

from __future__ import annotations

import hashlib
import json
import platform
import socket
import sys
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

GENESIS = "0" * 64


class HashChainError(RuntimeError):
    """A ledger line, a model file or a refit disagrees with the recorded hash chain."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(obj: dict) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")


def machine_id() -> dict[str, str]:
    """Who ran a fit: host, OS and CPU architecture (and the GPU when torch reports one)."""
    ident = {"host": socket.gethostname(), "os": sys.platform, "arch": platform.machine(),
             "python": platform.python_version()}
    try:
        import torch

        if torch.cuda.is_available():
            ident["gpu"] = torch.cuda.get_device_name(0)
    except ImportError:  # torch is pinned in uv.lock; this only guards odd environments
        ident["gpu"] = "torch not importable"
    return ident


@dataclass(frozen=True)
class Ledger:
    path: Path

    def records(self) -> Iterator[dict]:
        if not self.path.exists():
            return
        with self.path.open(encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    yield json.loads(line)

    def keys(self) -> set[str]:
        return {r["key"] for r in self.records()}

    def get(self, key: str) -> dict | None:
        found = [r for r in self.records() if r["key"] == key]
        return found[-1] if found else None

    def last_sha(self) -> str:
        last = GENESIS
        for r in self.records():
            last = r["record_sha256"]
        return last

    def append(self, record: dict) -> dict:
        if "key" not in record:
            raise ValueError("a ledger record needs a key")
        if record["key"] in self.keys():
            raise HashChainError(f"{record['key']} is already in {self.path.name}")
        body = {**record, "prev_sha256": self.last_sha()}
        body["record_sha256"] = sha256_bytes(canonical(body))
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(body, sort_keys=True, default=str) + "\n")
        return body


def verify_chain(ledger: Ledger) -> int:
    """Number of records; raises HashChainError on a broken chain."""
    prev = GENESIS
    n = 0
    for r in ledger.records():
        body = {k: v for k, v in r.items() if k != "record_sha256"}
        if r.get("prev_sha256") != prev:
            raise HashChainError(f"{ledger.path.name}: {r.get('key')} does not follow {prev[:12]}")
        if sha256_bytes(canonical(body)) != r.get("record_sha256"):
            raise HashChainError(f"{ledger.path.name}: {r.get('key')} was edited")
        prev = r["record_sha256"]
        n += 1
    return n


def check_refit(recorded: dict, model_sha256: str, machine: dict[str, str]) -> None:
    """Same key, same machine: the model hash must match (M7.6)."""
    if recorded.get("machine") == machine and recorded.get("model_sha256") != model_sha256:
        raise HashChainError(f"{recorded['key']}: refit hash {model_sha256[:12]} differs from "
                             f"the recorded {str(recorded.get('model_sha256'))[:12]} on the same "
                             "machine")


def verify_model_file(path: Path, expected_sha256: str) -> bytes:
    data = Path(path).read_bytes()
    got = sha256_bytes(data)
    if got != expected_sha256:
        raise HashChainError(f"REFUSED: {Path(path).name} hashes to {got[:12]}, the manifest "
                             f"records {expected_sha256[:12]}")
    return data
