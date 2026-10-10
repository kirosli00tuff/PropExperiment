"""Paths, spend caps, and credential loading for the offline data lane.

Each Databento account has its own key, read from the environment or from this repo's
``.env``: ``DATABENTO_API_KEY1`` for acct-1, ``DATABENTO_API_KEY2`` for acct-2, chosen by
``ACTIVE_ACCOUNT`` unless the caller names the account (Stage E.11, V19; the old single
``DATABENTO_API_KEY`` is no longer read). This mirrors MLCryptoEngine's pattern of a
git-ignored ``.env`` read through one config function. A key is never
hardcoded, logged, or written anywhere. This module holds NO TopstepX
credential of any kind and must never grow one in Stage A.1.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType

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

# Stage E.0 spend policy (set by the E.0 lead on the stage prompt's instruction, 2026-09-23):
# quotes only.
# $0.00 caps, so the gate refuses any billable request by construction.
STAGE_E0_SESSION_ID = "stage-E.0-2026-09-23"
E0_SESSION_CAP_USD = 0.00
E0_REQUEST_CAP_USD = 0.00


# Databento account registry (Stage E.1, 2026-09-24). Spend is capped PER ACCOUNT: a gate
# sums only the ledger lines of its own account and applies that account's cap. Every ledger
# line the gate writes from now on carries an "account" field; a line without one predates
# the registry and belongs to acct-1 (LEGACY_ACCOUNT_ID). An account id not listed here fails
# closed (data.spend_gate.UnknownAccountError).
@dataclass(frozen=True, slots=True)
class DatabentoAccount:
    account_id: str
    cap_usd: float
    # Other ledgers drawing on the same account, read-only and REQUIRED: a missing one closes
    # the gate. Empty means this repo's ledger is the account's only spend record.
    external_ledger_paths: tuple[Path, ...]
    description: str


ACCOUNT_1_ID = "acct-1"
ACCOUNT_2_ID = "acct-2"
LEGACY_ACCOUNT_ID = ACCOUNT_1_ID  # ledger lines with no "account" field
# acct-2's cumulative cap (V19, V23 item 19; raised in Stage E.12, harness v8). Was 125.00, the
# credit acct-2 opened with (U5). Arithmetic from the ledger: acct-2's cumulative spend
# data.spend_gate.account_committed_usd(read_entries(LEDGER_PATH), "acct-2") = 124.673761
# (ledger/databento_spend.jsonl at 2026-10-03 07:52 PDT: 17,400 lines, sha256
# 0b5466c4366ca9eaba7e10525545631c83e97c1184a7e745d5ed8ad47a9fe957; recomputed by the v8
# worker from the same file: 124.673761487003) + the user's $125.00 top-up of 2026-10-02 (V19)
# = 249.673761, rounded DOWN to the cent so the cap never exceeds the funds: 249.67.
# Harness v11 (Stage E.17, 2026-10-09; V27, V30 as amended; C1's freeze section 11): acct-2's ledger
# spend 231.599730 (ledger/databento_spend.jsonl, 29,040 lines before E.17's quote) + C1's fresh
# ext2010 quote $57.742330 x 1.03 = $59.474600 (the sum of the quote run's own 642 ledger lines,
# 18:54-19:07 PDT; reports/stage_e17_briefs/fresh_quote_c1.json) = 291.074330, rounded UP to the cent.
ACCOUNT_2_CAP_USD = 291.08

ACCOUNTS: MappingProxyType[str, DatabentoAccount] = MappingProxyType({
    ACCOUNT_1_ID: DatabentoAccount(
        ACCOUNT_1_ID, SHARED_ACCOUNT_CAP_USD, EXTERNAL_LEDGER_PATHS,
        "the old account, shared with the archived MLCryptoEngine (its ledger is read)",
    ),
    ACCOUNT_2_ID: DatabentoAccount(
        ACCOUNT_2_ID, ACCOUNT_2_CAP_USD, (),
        "the Stage E.1 account, used by this repo only (no external ledger)",
    ),
})
ACTIVE_ACCOUNT = ACCOUNT_2_ID

# Stage E.1 spend policy (stage prompt, 2026-09-24): Stage E step 1 purchase on ACTIVE_ACCOUNT.
STAGE_E1_SESSION_ID = "stage-E.1-2026-09-24"
E1_REQUEST_CAP_USD = 3.00  # never raised: a request quoted above it is split in time instead
# The E.1 lead sets E1_SESSION_CAP_USD in Task 6 from the fresh quote-only run (quote total
# + 10%, never above E1_SESSION_CAP_MAX_USD) before any purchase. 0.00 means the gate
# refuses every billable request until then, and `python -m data.pull_universe --buy`
# refuses to start.
# Set by the E.1 lead at 18:38 PDT 2026-09-24 from the fresh --quote-only total $103.161113
# (reports/stage_e1_quote_summary.json): 103.161113 x 1.10 = 113.477 -> $113.48, under the $120.00 ceiling.
E1_SESSION_CAP_USD = 113.48
E1_SESSION_CAP_MAX_USD = 120.00

# Stage E.2b spend policy (stage prompt, 2026-09-26): quotes only, the E.0 pattern. The step 2
# quote run (data.pull_step2 --quote-only) ledgers $0.00 quote lines on ACTIVE_ACCOUNT under this
# session id; with both caps at $0.00 the gate refuses every billable request, and
# `python -m data.pull_step2 --buy` refuses to start. A later step 2 purchase session sets its own
# session id and caps in a new block; nothing here is raised in E.2b.
STAGE_E2B_SESSION_ID = "stage-E.2b-2026-09-26"
E2B_SESSION_CAP_USD = 0.00
E2B_REQUEST_CAP_USD = 0.00
# The step 2 bar store (data.step2_store): its own base, separate from the research store
# (lead ruling 2026-09-26, M7.4 and the V10 separate data roots). Git-ignored.
STEP2_ROOT = DATA_ROOT / "processed_step2"

# Stage E.5 spend policy (stage prompt, 2026-09-27): the step 2 purchase of K4 and K5 on
# ACTIVE_ACCOUNT (acct-2). The E.5 lead sets both caps in Task B1 from the fresh quote before any
# purchase; 0.00 means the gate refuses every billable request until then, and
# `python -m data.pull_step2 --buy` refuses to start.
# Set by the E.5 lead at 18:12 PDT 2026-09-27 from the fresh --quote-only run (set clusters-legs, 1905
# chunks, 0 failed; reports/stage_e5_step2_quotes.json): K4 (MCL, NG) $11.455464 + K5 (MGC, MHG)
# $9.741104 = $21.196568; x 1.10 = $23.316225, above acct-2's headroom $125.00 - $103.477194 =
# $21.522806, so the session cap is the headroom in whole cents, $21.52 (never above it). Request cap:
# D13's $3.00 per request (the largest chunk quoted is $0.1157). ACCOUNT_2_CAP_USD is not raised.
STAGE_E5_SESSION_ID = "stage-E.5-2026-09-27"
E5_SESSION_CAP_USD = 21.52
E5_REQUEST_CAP_USD = 3.00

# Stage E.12 spend policy (stage prompt docs/prompts/STAGE_E.12.md, V23 item 19, 2026-10-03): the
# phase-1 purchase of ML route v2's training-window price paths through data.pull_step2, acct-1
# first up to its headroom under SHARED_ACCOUNT_CAP_USD, then acct-2 up to its headroom under
# ACCOUNT_2_CAP_USD; each run names its account (--account). The session id is shared by both
# accounts' gates, so the session cap bounds the two accounts together.
# The E.12 lead sets E12_SESSION_CAP_USD from the fresh quote-only run before the v8 manifest: the
# selected subset's quote total x 1.03, never above the combined headroom of the two accounts.
# 0.00 means the gate refuses every billable request until then, and
# `python -m data.pull_step2 --buy` refuses to start. Request cap: D13's $3.00 per request.
STAGE_E12_SESSION_ID = "stage-E.12-2026-10-03"
# Set by the E.12 lead at 10:02 PDT 2026-10-03 from the fresh --quote-only run (set ml-v2, training
# window, 1,601 chunks, 0 failed; reports/stage_e12_quotes_phase1.json, $139.340240 for 28 price
# paths) and the frozen subset rule (reports/stage_e12_ranking.json: all 28 exposures, NG owned at
# $0): subset total $133.723742 (acct-1 $26.797773, acct-2 $106.925969) x 1.03 = $137.735454, in
# whole cents $137.73, under the combined headroom $28.407753 + $124.996239 = $153.403992.
E12_SESSION_CAP_USD = 137.73
E12_REQUEST_CAP_USD = 3.00
# V23 item 4: phase 1 buys the training window only, ending with range=2024-02-01_2024-03-01.
# While True, `python -m data.pull_step2 --buy` without --training-window is refused before any
# vendor call, and --training-window refuses every chunk starting on or after 2024-03-01.
STEP2_TRAINING_WINDOW_ONLY = True

# The active step 2 purchase policy: the three names data.pull_step2.step2_gate reads. A later
# purchase session adds its own block above and repoints these three (a config-only edit, as the
# E.2b design intended); the blocks of earlier sessions stay as they were. Stage E.12 on: the
# E.12 block (Stage E.5 to E.11: the E.5 block).
STEP2_PURCHASE_SESSION_ID = STAGE_E12_SESSION_ID
STEP2_SESSION_CAP_USD = E12_SESSION_CAP_USD
STEP2_REQUEST_CAP_USD = E12_REQUEST_CAP_USD

# Stage E.14 spend policy (stage prompt docs/prompts/STAGE_E.14.md, V25, V26, 2026-10-05; harness
# v10). Read by data.pull_hist only: the step 2 active policy above stays on the E.12 block, and
# ACCOUNT_2_CAP_USD stays 249.67 (V26: the acct-2 top-up did not go through).
# Test C2 buys ES.v.0 2011-05..2019-04 (data.pull_hist plan "es2011") on acct-2 only. The E.14 lead
# sets E14_SESSION_CAP_USD from the fresh `--quote-only --plan es2011` total x 1.03, in whole
# cents, never above acct-2's headroom ($18.070270, E.12_RETURN.md:572; the E.14 prompt's
# Guardrails: "never above acct-2's remaining headroom ($18.07)"), before the v10 manifest. 0.00
# means the gate refuses every billable request and `--buy --plan es2011` refuses to start.
STAGE_E14_SESSION_ID = "stage-E.14-2026-10-05"
# Stays 0.00 (E.14 lead, 01:34 PDT 2026-10-05): the fresh --quote-only --plan es2011 run (01:29-01:32
# PDT, 96 of 96 chunks, 0 failed; reports/stage_e14_quotes_es2011.json) quoted $10.109048 (x 1.03 =
# $10.412319, which would fit acct-2's $18.070270), but test C2 stopped before its freeze and
# registration on its power rule (prereg C2 section 7: 135 eligible GEX < 0 dates, under 200;
# reports/stage_e14_gex.md). No ES is bought in E.14; a later harness sets this cap only if the user
# runs C2 under a new decision.
E14_SESSION_CAP_USD = 0.00
E14_REQUEST_CAP_USD = 3.00  # D13's per-request cap (docs/STAGE_E_DESIGN.md D13), as E.5 and E.12
# Test C1 (plan "ext2010": NG, NQ, ZN, 6E, GC, ZC, 2010-06-06..2019-05-01) is quoted only in E.14;
# its $0.00 quote lines go under STAGE_E14_SESSION_ID. Its buy runs under its own session id, so
# C2's ES spend never counts against C1's session cap, and is refused while this cap is 0.00
# (V26: C1 stops frozen, awaiting funds). A later harness may raise only this cap and
# ACCOUNT_2_CAP_USD (C1's freeze says so).
STAGE_E14_EXT2010_SESSION_ID = "stage-E.14-ext2010"
# Harness v11 (Stage E.17): C1's fresh ext2010 quote $57.742330 x 1.03 = $59.474600, rounded DOWN to
# the cent; never above $60.00 (V27) nor E.17's $124.00 budget (V30 as amended).
E14_EXT2010_SESSION_CAP_USD = 59.47
# The only account an E.14 plan buys on: acct-1's $1.609980 of headroom fits no root
# (E.12_RETURN.md:572; reports/stage_e13_ng_replication_draft.md section 8).
E14_BUY_ACCOUNT = ACCOUNT_2_ID
# The hist bar stores (data.hist_store, plans es2011 and ext2010): their own base, separate from
# the research and step 2 stores (the V10 separate data roots). Git-ignored.
HIST_ROOT = DATA_ROOT / "processed_hist"

# One Databento key per account (Stage E.11, V19): .env holds DATABENTO_API_KEY1 and
# DATABENTO_API_KEY2 only. require_databento_key reads the variable of the account it is asked
# for (ACTIVE_ACCOUNT by default). The old single DATABENTO_API_KEY is not read, not even as a
# fallback. Every account in ACCOUNTS has exactly one entry here.
DATABENTO_KEY_ENV_BY_ACCOUNT: MappingProxyType[str, str] = MappingProxyType({
    ACCOUNT_1_ID: "DATABENTO_API_KEY1",
    ACCOUNT_2_ID: "DATABENTO_API_KEY2",
})
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


def require_databento_key(env_file: Path = ENV_FILE, account: str | None = None) -> str:
    """The Databento key of ``account`` (``ACTIVE_ACCOUNT`` when None), or a clear failure.

    The account's variable is read from the environment, else from ``env_file``; a blank
    environment value does not shadow the file. The key comes back stripped of surrounding
    whitespace (E.11 review C-10(b), harness v8). An account with no registered variable, and a
    variable that is missing, empty or whitespace-only, raise MissingSecretError naming the
    account and the variable, never a value.
    """
    account_id = ACTIVE_ACCOUNT if account is None else account
    name = DATABENTO_KEY_ENV_BY_ACCOUNT.get(account_id)
    if name is None:
        raise MissingSecretError(
            f"no Databento key variable is registered for account {account_id!r} "
            f"(known accounts: {', '.join(DATABENTO_KEY_ENV_BY_ACCOUNT)})"
        )
    key = os.environ.get(name, "")
    if not key.strip():
        key = _read_env_file(env_file).get(name, "")
    if not key.strip():
        raise MissingSecretError(
            f"{name} (the Databento key of account {account_id}) is not set, or is empty, "
            f"in the environment or {env_file.name}"
        )
    return key.strip()
