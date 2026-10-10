"""Stage E.18 Step 3: the dry check of C1b's amended C10 (Fable E.17 F-1), before the freeze.

The amended check (c1_replication.c1b.c10_check) runs on E.12's FROZEN reference counts (the pinned model JSON's
c10_reference, computed on E.12's 2019-2024 training panel) against the C10 counts of a SYNTHETIC world that mimics the
2010-2019 listing state of every leg: NG, NQ, ZN, 6E, GC and ZC present as synthetic bars (tests._c1_fixtures,
ml_route_v2.synthetic), CL and MBT absent as C1's C7 sentinel frames (one bar after the window). Then each non-exempt
leg in turn is replaced by the same sentinel. No 2010-2019 bar is read: the bars are synthetic, the calendars and
release tables are the pinned official ones (no prices), the reference is E.12's.

    uv run python reports/stage_e18_briefs/dry_check.py --calendars real --out reports/stage_e18_dry_check.json
    uv run python reports/stage_e18_briefs/dry_check.py --calendars synthetic --out <scratch>/smoke.json  (mechanics)

Expected (written before the run, in reports/stage_e18_STATE.md): all legs present -> C1b's check returns [] and C1's
frozen check returns g17_mbt (h60), (hF) (E.17's contradiction); each non-exempt leg removed -> C1b's check returns
exactly that leg's g17 feature for both horizons. Exit 0 iff every expectation holds.
"""

from __future__ import annotations

import argparse
import dataclasses
import gc
import hashlib
import json
import sys
import tempfile
from datetime import date
from pathlib import Path
from types import MappingProxyType

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

MODEL = REPO / "reports" / "stage_e14_c1_model.json"
MODEL_SHA = "c6075306ddfd70cb22a2b32f8017ae41ba6050778e6cb66568d00b94585421e6"
CAL_HASHES = REPO / "reports" / "stage_e17_c1_calendar_hashes.json"
CAL_HASHES_SHA = "d5e48579"  # prefix recorded in E.17's return; the full sha256 is written to the output
FIRST, LAST = date(2010, 6, 7), date(2011, 9, 30)  # a sub-window: warm-up plus about nine months of rows
SEED = 11


def sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def now() -> str:
    from ml_route_v2.phase1._io import now_local

    return now_local()


def counts_for(world, signals):  # noqa: ANN001, ANN201
    from c1_replication import evaluate as ev
    from c1_replication.world import replication_panel

    panel = replication_panel(world, signals)
    counts = ev.c10_counts(panel)
    del panel
    gc.collect()
    return counts


def main(argv=None) -> int:  # noqa: ANN001
    from c1_replication import c1b
    from c1_replication import evaluate as ev
    from c1_replication.constants import (
        E12_GATE0_LIST,
        E12_GATE0_LIST_SHA256,
        LEG_ROOTS,
        STORE_ROOTS,
        WINDOW_FIRST,
        WINDOW_LAST,
    )
    from c1_replication.context import hist_tables
    from c1_replication.exclusions import c12_exclusions
    from c1_replication.guards import pinned_file
    from c1_replication.world import build_world, sentinel_frame
    from compute.platform import lower_priority
    from tests._c1_fixtures import synthetic_leg, vol_ticks_table, write_inputs

    p = argparse.ArgumentParser()
    p.add_argument("--calendars", choices=("real", "synthetic"), required=True)
    p.add_argument("--out", required=True)
    args = p.parse_args(argv)
    lower_priority()
    started = now()
    model = json.loads(pinned_file(MODEL, MODEL_SHA, "model JSON"))
    reference = model["c10_reference"]
    signals = tuple(json.loads(pinned_file(E12_GATE0_LIST, E12_GATE0_LIST_SHA256, "E.12 Gate 0 list"))
                    ["covered_signals"])
    if args.calendars == "real":
        cal_path = CAL_HASHES
        if not sha(cal_path).startswith(CAL_HASHES_SHA):
            print("REFUSED: the calendar hashes file is not E.17's", file=sys.stderr)
            return 2
    else:
        cal_path = write_inputs(Path(tempfile.mkdtemp(prefix="e18_dry_cal_"))).hashes
    vol_ticks_table()
    cal = ev.load_calendars(cal_path, WINDOW_FIRST, WINDOW_LAST)
    c12 = c12_exclusions(cal["calendars"], tuple(cal["releases"].unsourced), first=FIRST, last=LAST)
    cases = {}
    with hist_tables(cal["tables"]):
        world = build_world(lambda r: synthetic_leg(r, FIRST, LAST, seed=SEED), cal["releases"].calendar,
                            c12.excluded_dates(), first=FIRST, last=LAST)
        cases["all_legs_present"] = counts_for(world, signals)
        for leg in LEG_ROOTS:
            removed = dataclasses.replace(
                world, bars=MappingProxyType({**world.bars, leg: sentinel_frame()}),
                blackout=MappingProxyType({**world.blackout, leg: frozenset()}))
            cases[f"{leg}_removed"] = counts_for(removed, signals)
    live = {h: sorted(s for s, n in reference[h]["applicable"].items() if n > 0) for h in reference}
    results, ok = {}, True
    for name, counts in cases.items():
        got_c1b = c1b.c10_check(counts, reference)
        got_c1 = ev.c10_check(counts, reference)
        if name == "all_legs_present":
            want = []
            want_c1 = ["g17_mbt (h60)", "g17_mbt (hF)"]
        else:
            leg = name.split("_")[0].lower()
            want = [f"g17_{leg} (h60)", f"g17_{leg} (hF)"]
            want_c1 = sorted(want + ["g17_mbt (h60)", "g17_mbt (hF)"])
        good = got_c1b == want and sorted(got_c1) == sorted(want_c1)
        ok &= good
        results[name] = {
            "c1b_check": got_c1b, "c1b_expected": want, "c1_frozen_check": got_c1,
            "c1_expected": want_c1, "as_expected": good,
            "ng_ok_rows": {h: counts[h]["ng_ok_rows"] for h in counts},
            "live_in_e12_zero_here": {h: [s for s in live[h] if counts[h]["applicable"].get(s, 0) == 0]
                                      for h in counts},
            "applicable_live_in_e12": {h: {s: counts[h]["applicable"][s] for s in live[h]} for h in counts}}
    out = {"schema": "stage_e18_dry_check/1", "calendars": args.calendars, "ok": ok,
           "window": [FIRST.isoformat(), LAST.isoformat()], "seed": SEED,
           "store_roots_synthetic": list(STORE_ROOTS), "sentinel_roots": ["CL", "MBT"],
           "exempt": sorted(c1b.C10_EXEMPT),
           "inputs": {"model": {"path": str(MODEL.relative_to(REPO)), "sha256": MODEL_SHA},
                      "gate0_list": {"path": str(E12_GATE0_LIST.relative_to(REPO)),
                                     "sha256": E12_GATE0_LIST_SHA256},
                      "calendar_hashes": {"path": str(cal_path), "sha256": sha(cal_path)},
                      "c1b_py_sha256": sha(REPO / "c1_replication" / "c1b.py"),
                      "evaluate_py_sha256": sha(REPO / "c1_replication" / "evaluate.py")},
           "c12": {"excluded_in_subwindow": len(c12.excluded), "candidates": c12.n_candidates},
           "e12_live_signals": live, "cases": results, "started_local": started, "finished_local": now()}
    Path(args.out).write_text(json.dumps(out, indent=1) + "\n")
    for name, r in results.items():
        print(f"{name}: c1b {r['c1b_check']} (expected {r['c1b_expected']}); C1 frozen {r['c1_frozen_check']}; "
              f"ok rows {r['ng_ok_rows']}; {'AS EXPECTED' if r['as_expected'] else 'NOT AS EXPECTED'}")
    print(f"dry check {'PASS' if ok else 'FAIL'}; written {args.out} sha256 {sha(Path(args.out))}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
