"""Stage E.30: QM.FUT + CL.FUT ohlcv-1d (parent) on acct-2. Request: reports/stage_e30_request.md.

    uv run python reports/stage_e30_briefs/qm_pull.py quote
    uv run python reports/stage_e30_briefs/qm_pull.py buy --end <the end the quote recorded>

``quote`` makes the free get_dataset_range call and one logged quote (no spend). ``buy`` re-quotes
the identical request, refuses unless the quote is <= USD 1.00 and <= acct-2's headroom, then
commit -> download (.partial, link, read-only) -> record-byte check -> settle -> sha256 manifest,
as data.pull_hist does for one chunk. No key is printed or written.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from data import adapter  # noqa: E402
from data.config import DATASET, VENDOR_ROOT, require_databento_key  # noqa: E402
from data.pull_mes import RequestCappedGate  # noqa: E402
from data.pull_universe import download  # noqa: E402
from data.spend_gate import RequestParams  # noqa: E402

SESSION_ID = "stage-E.30-2026-10-21"
ACCOUNT = "acct-2"
CAP_USD = 1.00
SCHEMA = "ohlcv-1d"
SYMBOLS = ("QM.FUT", "CL.FUT")
START = "2023-01-01"
OUT_DIR = VENDOR_ROOT / DATASET / SCHEMA / "QM_CL_parent"
BRIEFS = REPO / "reports" / "stage_e30_briefs"
NOTE = "Stage E.30 QM volume check (V47)"


def log(msg: str) -> None:
    stamp = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
    print(f"[{stamp}] {msg}", flush=True)


def make_gate() -> RequestCappedGate:
    return RequestCappedGate(SESSION_ID, request_cap_usd=CAP_USD, session_cap_usd=CAP_USD,
                             account=ACCOUNT)


def make_client():  # noqa: ANN201
    import databento  # lazy

    return databento.Historical(require_databento_key(account=ACCOUNT))


def params_for(end: str) -> RequestParams:
    return RequestParams(dataset=DATASET, symbols=SYMBOLS, schema=SCHEMA, stype_in="parent",
                         start=START, end=end)


def ohlcv_1d_end(client) -> tuple[str, dict]:  # noqa: ANN001
    rng = client.metadata.get_dataset_range(dataset=DATASET)
    per_schema = (rng.get("schema") or {}).get(SCHEMA) or {}
    return str(per_schema.get("end") or rng["end"]), rng


def headroom(gate: RequestCappedGate) -> float:
    return gate.account_cap_usd - gate.account_spent_usd()


def cmd_quote() -> int:
    gate = make_gate()
    client = make_client()
    end, rng = ohlcv_1d_end(client)
    log(f"get_dataset_range: ohlcv-1d end {end}")
    params = params_for(end)
    quote = gate.quote(client, params)
    room = headroom(gate)
    out = {"ts_utc": datetime.now(UTC).isoformat(), "session_id": SESSION_ID, "account": ACCOUNT,
           "dataset_range": rng, "request": params.as_kwargs(),
           "quoted_usd": None if quote is None else quote.usd,
           "billable_bytes": None if quote is None else quote.billable_bytes,
           "acct2_headroom_usd": room, "cap_usd": CAP_USD,
           "buy_allowed": quote is not None and quote.usd <= CAP_USD and quote.usd <= room}
    (BRIEFS / "quote.json").write_text(json.dumps(out, indent=2) + "\n")
    log(f"quote: {out['quoted_usd']} USD, billable {out['billable_bytes']} bytes, "
        f"headroom {room:.6f}, buy_allowed {out['buy_allowed']}")
    return 0 if quote is not None else 1


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def cmd_buy(end: str) -> int:
    gate = make_gate()
    client = make_client()
    params = params_for(end)
    target = OUT_DIR / f"glbx-mdp3-{SCHEMA}-QM.FUT_CL.FUT-parent-{START}_{end[:10]}.dbn.zst"
    if target.exists():
        log(f"REFUSED: {target} already exists; nothing bought")
        return 2
    quote = gate.quote(client, params)
    if quote is None:
        log("REFUSED: quote failed; nothing bought")
        return 2
    room = headroom(gate)
    log(f"fresh quote {quote.usd} USD (billable {quote.billable_bytes}); headroom {room:.6f}")
    if quote.usd > CAP_USD or quote.usd > room:
        log(f"REFUSED: quote above USD {CAP_USD:.2f} or above headroom; nothing bought")
        return 3
    gate.authorize(params, quote)  # session, request and account caps; raises on refusal
    gate.commit(quote, note=NOTE)
    log("committed; downloading")
    download(client, params, target)
    delivered = adapter.delivered_record_bytes(target)
    ratio = delivered / quote.billable_bytes if quote.billable_bytes > 0 else float("inf")
    actual = quote.usd * ratio if ratio > 1.0 and quote.billable_bytes > 0 else quote.usd
    gate.settle(quote, actual_usd=actual, note=(
        f"{NOTE}: delivered uncompressed record bytes {delivered:,} vs quoted billable "
        f"{quote.billable_bytes:,}" + (" — DELIVERED EXCEEDS QUOTE" if ratio > 1.0 else "")))
    manifest = {"ts_utc": datetime.now(UTC).isoformat(), "session_id": SESSION_ID,
                "account": ACCOUNT, "request": params.as_kwargs(),
                "file": target.name, "path": str(target.resolve()),
                "bytes": target.stat().st_size, "sha256": sha256_of(target),
                "quoted_usd": quote.usd, "settled_usd": actual,
                "quoted_billable_bytes": quote.billable_bytes,
                "delivered_record_bytes": delivered}
    (OUT_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    (BRIEFS / "purchase_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    log(f"settled {actual} USD; delivered/billable {ratio:.4f}; sha256 {manifest['sha256']}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("quote")
    b = sub.add_parser("buy")
    b.add_argument("--end", required=True, help="the end string quote.json recorded")
    args = ap.parse_args()
    return cmd_quote() if args.cmd == "quote" else cmd_buy(args.end)


if __name__ == "__main__":
    raise SystemExit(main())
