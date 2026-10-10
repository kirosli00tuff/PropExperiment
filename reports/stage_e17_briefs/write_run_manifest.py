"""Stage E.17 step 12: write the base-rule run manifest (schema stage_e16_run_manifest/1, base_rules/README.md "E.17
commands" item 2), once, before any H run. Hashes only; no bar is read.

For each of the 27 test products (base_rules.constants.PRODUCTS):
- "ext2010": {"path", "sha256", "plan"} of its 2010-2019 store under its FIXED plan (base_rules.constants.HIST_PLAN_OF:
  "ext2010" for NG NQ ZN 6E GC ZC, "ext2010h" for the 21 others), taken from the build summary
  reports/hist/bars_<ROOT>_<plan>.json (its "parquet" entry; its last window trade date must be 2019-04-30) and
  checked against the file on disk; null when the root is on the fallback list (--fallback, A5), which then runs on
  2019-05-06..2024-02-29;
- "step2": {"path", "sha256"} of its E.12 step 2 store, from reports/step2/bars_<ROOT>.json's "parquet" entry
  (E.12's store summaries; window 2019-05-06..2024-02-29), checked against the file on disk.
A root not on the fallback list must have its hist summary and file. Writes --out once (refused if it exists) and
prints its sha256. base_rules.run's preflight re-checks every path, plan, window and booking before its marker.

Usage (repo root): PYTHONPATH=. uv run python reports/stage_e17_briefs/write_run_manifest.py \
    --fallback <fallback json> --out reports/stage_e17_run_manifest.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def parquet_entry(summary: Path, last: str, first: str | None = None) -> dict[str, str]:
    doc = json.loads(summary.read_bytes())
    pq = doc["parquet"]
    got = sha(Path(pq["path"]))
    if got != pq["sha256"]:
        raise SystemExit(f"{summary}: the parquet on disk ({got[:12]}...) differs from the summary's sha256")
    window = list(doc.get("window_trade_dates") or [None, None])
    if window[1] != last or (first is not None and window[0] != first):
        raise SystemExit(f"{summary}: window {window} does not end {last} (start {first})")
    return {"path": pq["path"], "sha256": pq["sha256"]}


def main() -> int:
    from base_rules import constants as K

    ap = argparse.ArgumentParser()
    ap.add_argument("--fallback", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    fallback = json.loads(Path(a.fallback).read_bytes())["roots"]
    unknown = sorted(set(fallback) - set(K.PRODUCTS))
    if unknown:
        raise SystemExit(f"fallback roots not among the 27 products: {unknown}")
    stores, counts = {}, {"ext2010": 0, "ext2010h": 0, "fallback": 0}
    for root in K.PRODUCTS:
        plan = K.HIST_PLAN_OF[root]
        ext = None
        if root in fallback:
            counts["fallback"] += 1
        else:
            summary = Path(f"reports/hist/bars_{root}_{plan}.json")
            if not summary.is_file():
                raise SystemExit(f"{root}: not on the fallback list but {summary} is missing")
            ext = {**parquet_entry(summary, str(K.HIST_LAST)), "plan": plan}
            counts[plan] += 1
        step2 = parquet_entry(Path(f"reports/step2/bars_{root}.json"), str(K.WINDOW_LAST), str(K.STEP2_FIRST))
        stores[root] = {"ext2010": ext, "step2": step2}
    doc = {"schema": K.RUN_MANIFEST_SCHEMA, "stores": stores}
    raw = (json.dumps(doc, indent=1, sort_keys=True) + "\n").encode()
    with Path(a.out).open("xb") as fh:
        fh.write(raw)
    print(f"{a.out} sha256 {hashlib.sha256(raw).hexdigest()} {counts}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
