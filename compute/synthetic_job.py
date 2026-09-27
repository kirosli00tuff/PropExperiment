"""The compute backend's synthetic test job (Stage E.2b, V10). Reads no market data.

    python -m compute.synthetic_job --data-root DIR --out-dir DIR [--items N] [--sleep-s S] [--fail]

It lists the bar files under its data root and counts their trade dates (the files the backend
sent, synthetic in every test), then writes items/item_<i>.json one at a time, sleeping between
them, and skips items already written: a job interrupted on the far side resumes where it
stopped. Each item actually computed appends a line to computed.jsonl, so a test can prove that
no item was computed twice. summary.json records the process's priority and thread cap as the
job saw them. --fail exits 3 after the items (a failing job's results are still hashed).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

from compute.datarules import parquet_trade_dates
from compute.files import write_json_atomic
from compute.platform import THREAD_ENV_VARS, priority_label


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--items", type=int, default=3)
    parser.add_argument("--sleep-s", type=float, default=0.0)
    parser.add_argument("--fail", action="store_true")
    args = parser.parse_args(argv)
    files = sorted(p for p in args.data_root.rglob("*.parquet"))
    inputs = {}
    for path in files:
        days, _ = parquet_trade_dates(path)
        inputs[path.relative_to(args.data_root).as_posix()] = len(days)
    items = args.out_dir / "items"
    items.mkdir(parents=True, exist_ok=True)
    for i in range(args.items):
        target = items / f"item_{i}.json"
        if target.exists():
            continue
        time.sleep(args.sleep_s)
        write_json_atomic(target, {"item": i, "inputs": inputs})
        with (args.out_dir / "computed.jsonl").open("a", encoding="utf-8") as log:
            log.write(json.dumps({"item": i, "pid": os.getpid()}) + "\n")
    write_json_atomic(args.out_dir / "summary.json", {
        "items": args.items, "inputs": inputs, "priority": priority_label(),
        "threads": {name: os.environ.get(name) for name in THREAD_ENV_VARS},
    })
    print(f"synthetic job done: {args.items} items, {len(inputs)} input files", flush=True)
    return 3 if args.fail else 0


if __name__ == "__main__":
    sys.exit(main())
