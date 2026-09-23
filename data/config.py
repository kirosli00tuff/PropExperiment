"""Paths, spend caps, and credential loading for the offline data lane.

The Databento key is read from the environment or from this repo's ``.env``
(``DATABENTO_API_KEY``), mirroring MLCryptoEngine's pattern of a
git-ignored ``.env`` read through one config function. It is never
hardcoded, logged, or written anywhere. This module holds NO TopstepX
credential of any kind and must never grow one in Stage A.1.
"""

from __future__ import annotations

import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = REPO_ROOT / "data"
VENDOR_ROOT = DATA_ROOT / "vendor" / "databento"
PROCESSED_ROOT = DATA_ROOT / "processed"
LEDGER_PATH = REPO_ROOT / "ledger" / "databento_spend.jsonl"
ACCESS_DOC_PATH = REPO_ROOT / "docs" / "ACCESS.md"
ENV_FILE = REPO_ROOT / ".env"

# Other ledgers drawing on the SAME Databento account. Read-only: this repo
# never writes to them. A missing external ledger closes the gate (fail
# closed) rather than being read as zero spend.
# Repointed by the Stage D.1f build lead (2026-09-23): the MLCryptoEngine repo moved to the
# archive drive, so the old sibling path (REPO_ROOT.parent / "MLCryptoEngine" / ...) no longer
# exists and the gate would fail closed on the D.1f purchase. This file is inside the D.1f
# harness-freeze manifest; the path is the one Stage D.1e read as "the relocated copy".
EXTERNAL_LEDGER_PATHS: tuple[Path, ...] = (
    Path("/mnt/large-storage/Archive/GitHub/MLCryptoEngine/data/vendor/spend_ledger.jsonl"),
)

# Stage A.1 spend policy (prompt, 2026-09-16): hard ceilings, not targets.
SESSION_CAP_USD = 15.00
SHARED_ACCOUNT_CAP_USD = 120.00
STAGE_A1_SESSION_ID = "stage-A.1-2026-09-16"

# Stage D.1f spend policy (set by the D.1f build lead on the stage prompt's instruction,
# 2026-09-23; frozen with the harness-freeze manifest). The caps cover the $7.59 history
# extension (reports/stage_d1e_quotes.json) and nothing more: the order-book purchase is
# Stage D.1g's separate decision and must not fit under them. Changing any value here means
# re-running strategy/research/_d1f_freeze.py before the freeze commit.
STAGE_D1F_SESSION_ID = "stage-D.1f-2026-09"
D1F_SESSION_CAP_USD = 10.00
D1F_REQUEST_CAP_USD = 10.00

DATABENTO_KEY_ENV = "DATABENTO_API_KEY"
DATASET = "GLBX.MDP3"


class MissingSecretError(RuntimeError):
    """A required credential is absent. Names the variable, never a value."""


def _read_env_file(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    out: dict[str, str] = {}
    for line in path.read_text().splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        name, value = stripped.split("=", 1)
        out[name.strip()] = value.strip().strip('"').strip("'")
    return out


def require_databento_key(env_file: Path = ENV_FILE) -> str:
    """The Databento key, or a clear failure naming the variable."""
    key = os.environ.get(DATABENTO_KEY_ENV) or _read_env_file(env_file).get(DATABENTO_KEY_ENV)
    if not key:
        raise MissingSecretError(
            f"{DATABENTO_KEY_ENV} is not set in the environment or {env_file.name}"
        )
    return key
