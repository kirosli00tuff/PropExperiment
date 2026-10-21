"""Stage E.26 T1.4/T1.6: a short read through each data path by the existing loaders, in their
row-free check mode (no bar value, no outcome read).

- data/processed_step2 and data/processed_hist: base_rules.store.preflight, the "every INPUT check
  of a product's stores that needs no row" path microbook.data.load_root_cached runs before it reads
  bars, for every root in E.21's run manifest (sha256 against the manifest, store metadata, rolls
  booked on the calendar). Context from microbook.data.build_context (E.21's freeze inputs).
- data/vendor/databento: data.adapter.raw_path for the first MES chunk, the DBN header metadata only
  (dataset, schema, symbols, start, end), and data.holdout.is_sealed_raw on it (False expected).
- data/sealed: covered by `python -m data.holdout status` in checks.sh (sha256 of every blob).
Run before and after the move; the two JSON outputs must be equal apart from "paths_resolved".
Usage: PYTHONPATH=. uv run python reports/stage_e26_briefs/loader_reads.py <out.json>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import databento as db

from base_rules.store import EXT2010, STEP2_ERA, preflight
from data.adapter import raw_path
from data.config import HIST_ROOT, STEP2_ROOT, VENDOR_ROOT
from data.holdout import is_sealed_raw
from microbook.data import build_context


def main(out: str) -> int:
    report: dict = {"preflight": {}, "errors": [],
                    "paths_resolved": {str(p): str(p.resolve()) for p in (VENDOR_ROOT, STEP2_ROOT, HIST_ROOT)}}
    ctx, manifest = build_context()
    for root in sorted(manifest.stores):
        try:
            cals = ctx.cal(root)
            report["preflight"][root] = preflight(root, manifest.stores[root],
                                                  {EXT2010: cals.hist, STEP2_ERA: cals.frozen})
        except Exception as exc:  # recorded, compared before/after
            report["errors"].append(f"{root}: {type(exc).__name__}: {exc}")
    dbn = raw_path("MES.v.0", "ohlcv-1m", "2019-05-01", "2019-06-01")
    meta = db.DBNStore.from_file(dbn).metadata
    report["dbn_header"] = {"path": str(dbn), "dataset": meta.dataset, "schema": str(meta.schema),
                            "symbols": list(meta.symbols), "start": int(meta.start), "end": int(meta.end),
                            "is_sealed_raw": is_sealed_raw(dbn)}
    Path(out).write_text(json.dumps(report, indent=1, default=str) + "\n")
    stores = sum(len(v) for v in report["preflight"].values())
    print("roots", len(report["preflight"]), "stores", stores, "errors", len(report["errors"]),
          "dbn", report["dbn_header"]["schema"], report["dbn_header"]["symbols"])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
