"""Stage E.24 A1 proof (b): E.23's discovery books replayed through mdio.bounded in a scratch
directory. TEST MODE: no run-once marker, no result under reports/, nothing under ledger/; the
only files written are under --out (refused unless it is a fresh directory under /tmp/claude-1000/).
This re-reads E.23's own, already-read W_ext window (ext2010 stores of NQ, ZN, ZF, ZB only).

    nice -n 10 uv run python reports/stage_e24_briefs/loader/replay_e23.py \
        --out <scratch>/loader_replay

1. The E.23 freeze is verified (trigger_hold.freeze_manifest.verify, read-only: every frozen code,
   test and input file by sha256) with the sha256 recorded in discovery_result.json.
2. The context exactly as trigger_hold.run.preconditions builds it for discovery
   (context_from_freeze, e21_starts, ctx.last = W_EXT_LAST), then bound at ctx.last by
   mdio.bounded.bound_context; the unbounded context's loader is replaced by one that raises.
   base_rules.store.preflight is NOT run (it would hash the step 2 stores).
3. Pass A: trigger_hold.evaluate.discovery (frozen) on the bounded context, n_trials as recorded;
   every value compared with reports/stage_e23_runs/discovery/discovery_result.json (floats to
   the last bit).
4. Pass B: mdio.trigger_books.read_root_books per root; its records compared with pass A's; the
   per-unit and per-fill files written to --out/books/per_root/<ROOT>.json.
5. Pass C: per root, base_rules.store.load_product on the ext2010 store alone versus
   mdio.bounded.load_product_bounded on both stores at 2019-04-30, field by field.
6. --out/replay_compare.json: values compared, mismatches, the max loaded trade date per store,
   and sha256 of E.23's result, marker and the trial registry before and after.
"""

from __future__ import annotations

import argparse
import gc
import hashlib
import json
import math
import os
import struct
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))

from base_rules import hist_plan as HP  # noqa: E402
from base_rules.context import context_from_freeze  # noqa: E402
from base_rules.store import EXT2010, STEP2_ERA, load_manifest, load_product  # noqa: E402
from mdio.book_files import write_per_root  # noqa: E402
from mdio.bounded import bound_context, load_product_bounded  # noqa: E402
from mdio.trigger_books import read_root_books  # noqa: E402
from multiday.run import e21_starts  # noqa: E402
from trigger_hold import constants as K  # noqa: E402
from trigger_hold import freeze_manifest as FM  # noqa: E402
from trigger_hold.config import load_config  # noqa: E402
from trigger_hold.evaluate import discovery  # noqa: E402

DISC = REPO / "reports/stage_e23_runs/discovery/discovery_result.json"
FREEZE = REPO / "reports/stage_e23_freeze.json"
WATCHED = ("reports/stage_e23_runs/discovery/discovery_result.json",
           "reports/stage_e23_RUN_ONCE_discovery.json",
           "reports/stage_e23_RUN_ONCE_confirmation.json",
           "ledger/trial_registrations.jsonl")
ARRAYS = ("ts", "open_t", "close_t", "sym", "usable", "td", "high_t", "low_t", "volume",
          "no_new")


def now() -> str:
    return datetime.now(ZoneInfo("America/Vancouver")).isoformat(timespec="seconds")


def sha(p: Path) -> str | None:
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None


def watched() -> dict:
    return {rel: sha(REPO / rel) for rel in WATCHED}


class Compare:
    """Leaf-by-leaf comparison; floats equal only bit for bit (NaN equals NaN)."""

    def __init__(self) -> None:
        self.n = 0
        self.mismatches: list[dict] = []

    def leaf(self, a: object, b: object, where: str) -> None:
        self.n += 1
        if isinstance(a, float) or isinstance(b, float):
            ok = isinstance(a, float) and isinstance(b, float) and (
                (math.isnan(a) and math.isnan(b)) or struct.pack("<d", a) == struct.pack("<d", b))
        else:
            ok = type(a) is type(b) and a == b
        if not ok:
            self.mismatches.append({"path": where, "replay": a, "recorded": b})

    def walk(self, a: object, b: object, where: str = "") -> None:
        if isinstance(b, dict):
            if not isinstance(a, dict):
                self.mismatches.append({"path": where, "replay": type(a).__name__,
                                        "recorded": "dict"})
                return
            for k in sorted(set(a) | set(b)):
                if k not in a or k not in b:
                    self.mismatches.append({"path": f"{where}/{k}", "replay": k in a,
                                            "recorded": k in b, "what": "key present"})
                    continue
                self.walk(a[k], b[k], f"{where}/{k}")
        elif isinstance(b, list):
            if not isinstance(a, list) or len(a) != len(b):
                self.mismatches.append({"path": where, "what": "list length",
                                        "replay": len(a) if isinstance(a, list) else None,
                                        "recorded": len(b)})
                return
            for i, (x, y) in enumerate(zip(a, b, strict=True)):
                self.walk(x, y, f"{where}[{i}]")
        else:
            self.leaf(a, b, where)


def rt(obj: object) -> object:
    """The JSON round trip the E.23 writer applied (json.dumps(..., default=str))."""
    return json.loads(json.dumps(obj, default=str))


def refuse_unbounded(root: str):  # noqa: ANN201
    raise RuntimeError(f"an unbounded load of {root} was attempted (replay invariant)")


def bars_equal(a, b) -> list[str]:  # noqa: ANN001
    bad = [n for n in ARRAYS if getattr(a, n).dtype != getattr(b, n).dtype
           or not np.array_equal(getattr(a, n), getattr(b, n))]
    bad += [n for n in ("root", "symbols", "splices", "blackout", "records")
            if getattr(a, n) != getattr(b, n)]
    return bad


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = Path(a.out).resolve()
    if not str(out).startswith("/tmp/claude-1000/") or out.is_relative_to(REPO):
        print(f"REFUSED: --out {out} is not a scratch directory under /tmp/claude-1000/")
        return 2
    if out.exists() and any(out.iterdir()):
        print(f"REFUSED: --out {out} is not empty")
        return 2
    out.mkdir(parents=True, exist_ok=True)
    os.nice(10)
    before = watched()
    t0 = now()
    disc = json.loads(DISC.read_text())
    freeze = FM.verify(FREEZE, disc["freeze_sha256"])
    inputs = freeze["inputs"]
    cfg = load_config(Path(inputs["config"]["path"]))
    power = json.loads(Path(inputs["power"]["path"]).read_text())
    manifest = load_manifest(Path(inputs["run_manifest"]["path"]),
                             inputs["run_manifest"]["sha256"])
    ctx0 = context_from_freeze({"inputs": inputs}, manifest, HP.default_resolver)
    ctx0.starts = e21_starts(dict(ctx0.starts))
    ctx0.last = K.W_EXT_LAST
    ctx, loader = bound_context(ctx0, manifest)
    ctx0.load_bars = refuse_unbounded
    trend_dir = Path(freeze["trend_dir"])
    print(f"{now()} freeze verified; roots {cfg.roots}; bound {loader.bound}", flush=True)

    # Pass A: the frozen discovery on the bounded context.
    res = discovery(ctx, cfg, power, disc["n_trials"], trend_dir=trend_dir)
    (out / "discovery_replay.json").write_text(json.dumps(res, indent=1, default=str) + "\n")
    res_rt = rt(res)
    cmp_a = Compare()
    cmp_a.walk(res_rt, {k: disc[k] for k in disc if k in res_rt}, "")
    not_compared = sorted(set(disc) - set(res_rt))
    header = {"freeze_sha256": disc["freeze_sha256"] == sha(FREEZE),
              "manifest_sha256": disc["manifest_sha256"] == manifest.sha256}
    print(f"{now()} pass A: {cmp_a.n} values, {len(cmp_a.mismatches)} mismatches", flush=True)

    # Pass B: the per-unit and per-fill files; records equal pass A's.
    cmp_b = Compare()
    books = {}
    for root in cfg.roots:
        ths = [th for th in cfg.rows if th.root == root
               and res["trigger_holds"][th.id].get("status") == "read"]
        if not ths:
            continue
        got, rec = read_root_books(ctx, root, ths, K.W_EXT, trend_dir=trend_dir)
        cmp_b.walk(rt(got), {th.id: res_rt["trigger_holds"][th.id] for th in ths}, f"/{root}")
        if rec is None:
            books[root] = {"written": None}
            continue
        path = write_per_root(out / "books", rec)
        books[root] = {"written": str(path), "sha256": sha(path),
                       "units": {i: len(u) for i, u in rec["units"].items()},
                       "fills": {i: len(f) for i, f in rec["fills"].items()},
                       "holdings": {i: len(h) for i, h in rec["holdings"].items()},
                       "last_fill_date": max((f["date"] for fs in rec["fills"].values()
                                              for f in fs), default=None)}
        del got, rec
        gc.collect()
    print(f"{now()} pass B: {cmp_b.n} values, {len(cmp_b.mismatches)} mismatches", flush=True)

    # Pass C: the bounded bars equal load_product on the ext2010 store alone.
    pass_c, c_loads = {}, []
    for root in cfg.roots:
        refs = manifest.stores[root]
        g = ctx.cal(root)
        eras = {EXT2010: g.hist, STEP2_ERA: g.frozen}
        ref_pb = load_product(root, {EXT2010: refs[EXT2010], STEP2_ERA: None}, eras)
        got_pb, loads = load_product_bounded(root, refs, eras, K.W_EXT_LAST)
        c_loads += loads
        pass_c[root] = {"fields_differing": bars_equal(ref_pb, got_pb), "rows": len(got_pb.ts),
                        "max_trade_date": str(datetime.fromordinal(int(got_pb.td.max())).date())}
        del ref_pb, got_pb
        gc.collect()
    print(f"{now()} pass C: {pass_c}", flush=True)

    stores: dict[str, dict] = {}
    for ld in (*loader.loads, *c_loads):
        s = stores.setdefault(ld.path, {"era": ld.era, "root": ld.root, "loads": 0,
                                        "skipped_every_time": True, "max_trade_date": None,
                                        "rows_kept": set(), "rows_decoded": set(),
                                        "row_groups_read": set(), "row_groups_total": set()})
        s["loads"] += 1
        s["skipped_every_time"] &= ld.skipped
        if ld.max_trade_date and (s["max_trade_date"] is None
                                  or ld.max_trade_date > s["max_trade_date"]):
            s["max_trade_date"] = ld.max_trade_date
        s["rows_kept"].add(ld.rows_kept)
        s["rows_decoded"].add(ld.rows_decoded)
        s["row_groups_read"].add(tuple(ld.row_groups_read))
        s["row_groups_total"].add(ld.row_groups_total)
    for s in stores.values():
        for k in ("rows_kept", "rows_decoded", "row_groups_total"):
            s[k] = sorted(s[k])
        s["row_groups_read"] = sorted(list(x) for x in s["row_groups_read"])
    overall = max((s["max_trade_date"] for s in stores.values() if s["max_trade_date"]),
                  default=None)
    after = watched()
    summary = {
        "schema": "stage_e24_loader_replay/1", "started_local": t0, "finished_local": now(),
        "bound": str(loader.bound), "roots": cfg.roots, "n_trials_used": disc["n_trials"],
        "header_checks": header, "recorded_keys_not_compared": not_compared,
        "pass_a_discovery": {"values_compared": cmp_a.n, "mismatches": cmp_a.mismatches},
        "pass_b_book_files": {"values_compared": cmp_b.n, "mismatches": cmp_b.mismatches,
                              "files": books},
        "pass_c_bars": pass_c,
        "values_compared_total": cmp_a.n + cmp_b.n,
        "mismatches_total": len(cmp_a.mismatches) + len(cmp_b.mismatches),
        "max_loaded_trade_date_per_store": stores,
        "max_loaded_trade_date_overall": overall,
        "nothing_after_bound_loaded": overall is not None and overall <= str(K.W_EXT_LAST),
        "watched_sha256_before": before, "watched_sha256_after": after,
        "watched_unchanged": before == after}
    (out / "replay_compare.json").write_text(json.dumps(summary, indent=1, default=str) + "\n")
    ok = (summary["mismatches_total"] == 0 and summary["nothing_after_bound_loaded"]
          and summary["watched_unchanged"] and all(header.values())
          and not any(v["fields_differing"] for v in pass_c.values()))
    print(f"{now()} replay {'OK' if ok else 'MISMATCH'}: {summary['values_compared_total']} "
          f"values, {summary['mismatches_total']} mismatches, max loaded {overall}", flush=True)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
