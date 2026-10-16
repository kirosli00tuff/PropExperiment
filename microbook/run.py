"""The micro book CLI (lead_spec_B.md S5).

    nice -n 10 uv run python -m microbook.run load [--roots NQ RTY ...]   (bars -> cache, one root at a time)
    nice -n 10 uv run python -m microbook.run study                       (the S5 tables from the cache)
    uv run python -m microbook.run margins                                (adds the margin columns from
                                                                           reports/stage_e22_briefs/ibkr_margins.json)

Outputs: reports/stage_e22_microbook/ (cache/, books/ per capital and method, resumable),
reports/stage_e22_microbook.md and .json. Nothing is read from data/processed/, no sealed store,
nothing dated after 2024-02-29 (base_rules' loader refuses it; microbook.data checks the paths).
"""

from __future__ import annotations

import argparse
import gc
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from base_rules import constants as BK

OUT_DIR = Path("reports/stage_e22_microbook")
CACHE_DIR = OUT_DIR / "cache"
REPORT_MD = Path("reports/stage_e22_microbook.md")
REPORT_JSON = Path("reports/stage_e22_microbook.json")
MARGINS_JSON = Path("reports/stage_e22_briefs/ibkr_margins.json")


def now_local() -> str:
    return datetime.now(ZoneInfo("America/Vancouver")).isoformat(timespec="seconds")


def cmd_load(roots: list[str]) -> int:
    from microbook.data import build_context, load_root_cached
    from microbook.universe import ROOTS

    roots = roots or list(ROOTS)
    ctx_manifest = None
    cache = BK.repo_path(CACHE_DIR)
    for root in roots:
        pq_path = cache / f"{root}.parquet"
        if pq_path.is_file() and (cache / f"{root}.json").is_file():
            print(f"{now_local()} {root}: cached")
            continue
        if ctx_manifest is None:
            ctx_manifest = build_context()
        frame, meta = load_root_cached(root, cache, ctx_manifest)
        print(f"{now_local()} {root}: {len(frame)} marks {meta['first']}..{meta['last']} "
              f"{json.dumps(meta['counters'])}", flush=True)
        del frame
        gc.collect()
    return 0


def cmd_study(args: argparse.Namespace) -> int:
    from microbook.study import run_study

    run_study(out_dir=BK.repo_path(OUT_DIR), cache_dir=BK.repo_path(CACHE_DIR),
              report_md=BK.repo_path(REPORT_MD), report_json=BK.repo_path(REPORT_JSON),
              margins_json=BK.repo_path(MARGINS_JSON), with_sensitivity=not args.no_sensitivity)
    return 0


def cmd_margins(_args: argparse.Namespace) -> int:
    """Re-render the tables with the margin columns from ``MARGINS_JSON``: the study reruns
    from the cache and the saved books (no bar is read, no book is recomputed)."""
    from microbook.study import run_study

    if not BK.repo_path(MARGINS_JSON).is_file():
        print(f"{MARGINS_JSON} not found: margin columns stay 'margin not sourced'")
        return 2
    run_study(out_dir=BK.repo_path(OUT_DIR), cache_dir=BK.repo_path(CACHE_DIR),
              report_md=BK.repo_path(REPORT_MD), report_json=BK.repo_path(REPORT_JSON),
              margins_json=BK.repo_path(MARGINS_JSON))
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="microbook.run")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p_load = sub.add_parser("load")
    p_load.add_argument("--roots", nargs="*", default=[])
    p_study = sub.add_parser("study")
    p_study.add_argument("--no-sensitivity", action="store_true")
    sub.add_parser("margins")
    a = ap.parse_args(argv)
    if os.nice(0) < 10:
        os.nice(10 - os.nice(0))
    if a.cmd == "load":
        return cmd_load(a.roots)
    if a.cmd == "study":
        return cmd_study(a)
    return cmd_margins(a)


if __name__ == "__main__":
    sys.exit(main())
