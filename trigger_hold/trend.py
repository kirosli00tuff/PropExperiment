"""The per-root trend regressors v_T1(i, d), v_T2(i, d) (lead_spec section 0) and the E.21 T3
reproduction of the unit engine (the ONLY real-bar run of trigger_hold.book before the freeze).

reports/stage_e21_runs/per_root stores holdings and fills, not per-root daily series, so the
per-root E.21 T1 (TSMOM-12) and T2 (1/3/12 blend) BASE daily net values (capital units, the
S_M divisor included: their sum over roots is the E.21 series) are recomputed with the frozen
E.21 code exactly as multiday.evaluate does it (the E.21 freeze verified first; the E.21 context;
lock_rule; process_root; t12_orders; simulate_book), one root at a time, and written to
reports/stage_e23_trend_per_root/<ROOT>.json. The check: for every date of T1_result.json and
T2_result.json ``series.base``, |sum over roots - the published value| <= 1e-12 (and no per-root
value on a date outside the series); the result is written into every root's file.

T3 reproduction (NQ, RTY): T3's own units (multiday.signals.tom_units / book.tom_sigma, S_u)
through trigger_hold.book.unit_book with divisor_at = S_u of the unit's month, against the
frozen t3_orders + simulate_book per root, and their sum against T3_result.json series.base.

    nice -n 10 uv run python -m trigger_hold.trend [--out-dir ...] [--t3-out ...]
"""

from __future__ import annotations

import argparse
import contextlib
import gc
import json
import os
import sys
from collections import Counter
from collections.abc import Mapping
from datetime import date, datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from base_rules import guards as BG
from base_rules.common import load_or_exclude, lock_rule
from base_rules.context import context_from_freeze
from base_rules.store import load_manifest
from multiday import constants as MK
from multiday import freeze_manifest as MFM
from multiday.book import RootData, process_root, simulate_book, t3_orders, t12_orders
from multiday.run import e21_starts
from multiday.signals import divisor_su, divisor_table
from trigger_hold import constants as K
from trigger_hold.book import unit_book
from trigger_hold.units import Unit

E21_FREEZE_SHA256 = "0bb899e56729d84075f43d72ae7e4207a026a955f1b39b39b490330a2e03bb1e"
T3_REPRO_PATH = Path("reports/stage_e23_briefs/tmp_bookcoder/t3_reproduction.json")


def _now() -> str:
    return datetime.now(ZoneInfo("America/Vancouver")).isoformat(timespec="seconds")


def e21_context():  # noqa: ANN201
    freeze = MFM.verify(K.repo_path(K.E21_FREEZE_PATH), E21_FREEZE_SHA256)
    inputs = freeze["inputs"]
    manifest = load_manifest(Path(inputs["run_manifest"]["path"]),
                             inputs["run_manifest"]["sha256"])
    ctx = context_from_freeze({"inputs": inputs}, manifest)
    ctx.starts = e21_starts(dict(ctx.starts))
    return ctx


def _dated(values: Mapping[date, float]) -> dict[str, float]:
    return {str(d): float(v) for d, v in sorted(values.items())}


def root_record(rd: RootData, sm: Mapping, counters: Counter) -> dict[str, Any]:
    out: dict[str, Any] = {"schema": K.TREND_SCHEMA, "root": rd.root, "vehicle": rd.vehicle,
                           "written_local": _now(), "e21_freeze_sha256": E21_FREEZE_SHA256,
                           "unit": "capital units per day (E.21 per-root base net, S_M divisor "
                                   "included; the sum over roots is the E.21 series)"}
    for test in ("T1", "T2"):
        c: Counter = Counter()
        book = simulate_book(rd, t12_orders(rd, test, sm, c))
        out[f"v_{test}"] = _dated(book.net(MK.BASE))
        out[f"counters_{test}"] = dict(sorted((c + book.counters).items()))
    out["root_counters"] = dict(sorted(counters.items()))
    return out


def check_sum(out_dir: Path, test: str) -> dict[str, Any]:
    pub = json.loads(K.repo_path(K.E21_RESULTS[test]).read_text())["series"][MK.BASE]
    published = {date.fromisoformat(d): float(v) for d, v in pub}
    tot = dict.fromkeys(published, 0.0)
    off = 0
    roots = []
    for r in MK.ROOTS:
        p = out_dir / f"{r}.json"
        if not p.is_file():
            continue
        roots.append(r)
        for d, v in json.loads(p.read_text())[f"v_{test}"].items():
            day = date.fromisoformat(d)
            if day not in tot:
                off += 1
                continue
            tot[day] += v
    diffs = [abs(tot[d] - published[d]) for d in published]
    worst = max(diffs) if diffs else None
    return {"test": test, "published": BG.rel(K.repo_path(K.E21_RESULTS[test])),
            "published_sha256": BG.sha256_file(K.repo_path(K.E21_RESULTS[test])),
            "dates": len(published), "roots_summed": roots, "values_off_series": off,
            "max_abs_diff": worst, "tol": K.TREND_CHECK_TOL,
            "passed": bool(off == 0 and worst is not None and worst <= K.TREND_CHECK_TOL
                           and len(roots) == len(MK.ROOTS))}


def t3_reproduction(rds: Mapping[str, RootData]) -> dict[str, Any]:
    su = divisor_su({r: rds[r].tom for r in rds})
    out: dict[str, Any] = {"written_local": _now(), "roots": {}, "S_u_months": len(su)}
    mine_sum: dict[date, float] = {}
    for r, rd in rds.items():
        frozen = simulate_book(rd, t3_orders(rd, su, Counter()))
        units = [Unit(u.entry, u.exit, 1, "E21-T3", r, u.entry, 0) for u in rd.tom
                 if u.why is None]
        mine = unit_book(rd, units, divisor_at=lambda d: su[(d.year, d.month)])
        a, b = frozen.net(MK.BASE), mine.net(MK.BASE)
        days = set(a) | set(b)
        worst = max((abs(a.get(d, 0.0) - b.get(d, 0.0)) for d in days), default=0.0)
        out["roots"][r] = {"units": len(units), "frozen_fills": len(frozen.fills),
                           "unit_engine_fills": len(mine.fills), "dates": len(days),
                           "max_abs_diff_vs_frozen_t3": worst,
                           "passed": bool(worst <= K.TREND_CHECK_TOL
                                          and len(frozen.fills) == len(mine.fills))}
        for d, v in b.items():
            mine_sum[d] = mine_sum.get(d, 0.0) + v
    pub = json.loads(K.repo_path(K.E21_RESULTS["T3"]).read_text())["series"][MK.BASE]
    published = {date.fromisoformat(d): float(v) for d, v in pub}
    off = [d for d in mine_sum if d not in published]
    worst = max(abs(mine_sum.get(d, 0.0) - v) for d, v in published.items())
    out["sum_vs_published"] = {"published_sha256": BG.sha256_file(K.repo_path(
        K.E21_RESULTS["T3"])), "dates": len(published), "values_off_series": len(off),
        "max_abs_diff": worst, "passed": bool(not off and worst <= K.TREND_CHECK_TOL)}
    out["passed"] = bool(out["sum_vs_published"]["passed"]
                         and all(v["passed"] for v in out["roots"].values()))
    return out


def run(out_dir: Path, t3_out: Path) -> int:
    with contextlib.suppress(OSError):
        os.nice(10)
    ctx = e21_context()
    sm = divisor_table(ctx, MK.ROOTS)
    out_dir.mkdir(parents=True, exist_ok=True)
    rds3: dict[str, RootData] = {}
    need_t3 = not t3_out.is_file()
    for root in MK.ROOTS:
        done = (out_dir / f"{root}.json").is_file()
        if done and not (need_t3 and root in MK.T3_ROOTS):
            continue
        notes: dict = {}
        load_counts: Counter = Counter()
        bars = load_or_exclude(ctx, root, load_counts, notes)
        if bars is None:
            print(f"{root}: store refused {notes}", file=sys.stderr)
            return 1
        locks = lock_rule(ctx, bars)
        rd = process_root(ctx, bars, root, locks=locks, with_tom=root in MK.T3_ROOTS)
        del bars, locks
        gc.collect()
        if not done:
            rec = root_record(rd, sm, rd.counters)
            (out_dir / f"{root}.json").write_text(json.dumps(rec, indent=1) + "\n")
        if root in MK.T3_ROOTS:
            rds3[root] = rd
        print(f"{root}: done {_now()}", flush=True)
    if need_t3:
        rep = t3_reproduction({r: rds3[r] for r in MK.T3_ROOTS})
        t3_out.parent.mkdir(parents=True, exist_ok=True)
        t3_out.write_text(json.dumps(rep, indent=1, default=str) + "\n")
        print(f"T3 reproduction passed={rep['passed']}")
    checks = {t: check_sum(out_dir, t) for t in ("T1", "T2")}
    for root in MK.ROOTS:
        p = out_dir / f"{root}.json"
        rec = json.loads(p.read_text())
        rec["check"] = checks
        p.write_text(json.dumps(rec, indent=1) + "\n")
    print("check:", {t: (c["passed"], c["max_abs_diff"]) for t, c in checks.items()})
    return 0 if all(c["passed"] for c in checks.values()) else 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="trigger_hold.trend")
    ap.add_argument("--out-dir", default=str(K.repo_path(K.TREND_DIR)))
    ap.add_argument("--t3-out", default=str(K.repo_path(T3_REPRO_PATH)))
    a = ap.parse_args(argv)
    return run(Path(a.out_dir), Path(a.t3_out))


def load_trend(root: str, trend_dir: Path = K.TREND_DIR) -> dict[str, dict[date, float]]:
    """v_T1, v_T2 of one root from its trend file; refuses a file whose check did not pass."""
    rec = json.loads(K.repo_path(Path(trend_dir) / f"{root}.json").read_text())
    if rec.get("schema") != K.TREND_SCHEMA or not all(
            c.get("passed") for c in (rec.get("check") or {"x": {}}).values()):
        raise RuntimeError(f"{root}: the trend file is not a checked {K.TREND_SCHEMA}")
    return {t: {date.fromisoformat(d): float(v) for d, v in rec[f"v_{t}"].items()}
            for t in ("T1", "T2")}


if __name__ == "__main__":
    raise SystemExit(main())
