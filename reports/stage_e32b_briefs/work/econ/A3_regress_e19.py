"""A3 regression: E.19's own funnel and return model, re-run without reading market data.

E.19's headline zero-edge 50K result (-$250 per cycle) used the 5-day block bootstrap of the E.12 training stores,
which run to 2024-02-29; the Stage E.28 reader rules forbid reading data dated 2023-11-01 or later, so that run
cannot be repeated here. This script instead

1. re-runs E.19's normal-tail twin of the same job (tail normal, 50K, zero edge k = 1, f = 0.25, DLL off, base
   rules), with E.19's grid code (prop_econ.grid.run_task), E.19's settings and seeds and E.19's rules file
   (the pre-E.26 copy, whose settings fingerprint equals E.19's), and checks every stored record field;
2. repeats it on the E.26-refreshed rules file (the record E.28 uses) and checks the simulated numbers agree;
3. reads E.19's stored headline record and prints the published -$250 figure for the citation.

The normal source needs only sigma_full per root, taken from reports/stage_e19_returns_summary.json; the E.19
bootstrap loader is replaced by a function that raises, so no store can be opened by accident.
Usage: uv run python reports/stage_e28_briefs/work/A3_econ/A3_regress_e19.py
"""

from __future__ import annotations

import json
import math
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import prop_econ.grid as grid
import prop_econ.returns as returns

REPO = Path(__file__).resolve().parents[4]
WORK = Path(__file__).resolve().parent
OUT = WORK / "e19_regress"
E19_RUNS = REPO / "reports" / "stage_e19_runs"
RULES_E19 = REPO / "reports" / "stage_e26_briefs" / "stage_e19_rules.before_e26.json"
RULES_NOW = REPO / "reports" / "stage_e19_rules.json"
SUMMARY = REPO / "reports" / "stage_e19_returns_summary.json"
JOB = grid.Job(grid.ShockConfig(tail="normal"), "50K", "zero_k1", 0.25, False, "base", "tail_normal")
HEADLINE_ID = "bootstrap-random-all-d8-continuous__50K__zero_k1__f0.25__dll0__base"
CHECK_KEYS = ("net", "net_ex_api", "net_p5", "net_p50", "net_p95", "p_no_payout", "p_reaches_xfa",
              "mean_purchases", "mean_fees_total", "mean_cycle_days", "mean_attempts", "mean_user_cash")


@dataclass(frozen=True)
class _SigmaOnly:
    """Stand-in for returns.PathShocks carrying only what the normal source reads."""

    root: str
    sigma_full_usd: float


def _forbid(*_a: object, **_k: object) -> None:
    raise RuntimeError("A3: reading the E.12 stores is forbidden (data dated 2023-11-01 or later)")


def stub_paths() -> tuple[_SigmaOnly, ...]:
    rows = {p["root"]: float(p["sigma_full_usd"]) for p in json.loads(SUMMARY.read_text())["paths"]}
    return tuple(_SigmaOnly(r, rows[r]) for r in returns.ROOTS)


def _records(doc: dict) -> dict[tuple, dict]:
    return {(r["path"], r["pricing"], r["b2f"]): r for r in doc["records"]}


def _flat(x: object) -> list[float]:
    if isinstance(x, dict):
        return [v for k in sorted(x) for v in _flat(x[k])]
    return [float(x)] if isinstance(x, (int, float)) and x is not None else []


def run(rules_path: Path, out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    done = grid.run_task([JOB], grid.Settings(), out_dir, rules_path=rules_path)
    doc = json.loads((out_dir / f"{JOB.id}.json").read_text())
    doc["_seconds"] = round(time.time() - t0, 2)
    doc["_ran"] = bool(done)
    return doc


def compare(new: dict, ref: dict) -> tuple[int, float]:
    """(number of compared numbers, max abs difference) over CHECK_KEYS of every record."""
    a, b = _records(new), _records(ref)
    if set(a) != set(b):
        raise AssertionError(f"record keys differ: {sorted(a)} vs {sorted(b)}")
    n, worst = 0, 0.0
    for key, rec in a.items():
        for k in CHECK_KEYS:
            va, vb = _flat(rec[k]), _flat(b[key][k])
            if len(va) != len(vb):
                raise AssertionError(f"{key} {k}: shape differs")
            for x, y in zip(va, vb, strict=True):
                n += 1
                worst = max(worst, abs(x - y))
    return n, worst


def main() -> int:
    os.nice(10)
    grid.load_paths = _forbid  # type: ignore[assignment]
    returns.load_paths = _forbid  # type: ignore[assignment]
    grid._PATHS = stub_paths()
    ref = json.loads((E19_RUNS / f"{JOB.id}.json").read_text())
    res = {}
    for tag, rules in (("e19_rules", RULES_E19), ("e26_refreshed_rules", RULES_NOW)):
        doc = run(rules, OUT / tag)
        n, worst = compare(doc, ref)
        std = _records(doc)[("standard", "standard", False)]
        res[tag] = {"fingerprint": doc["fingerprint"], "seconds": doc["_seconds"],
                    "compared_numbers": n, "max_abs_diff": worst,
                    "net_standard_standard": std["net"], "seeds": doc["seeds"]}
    head = json.loads((E19_RUNS / f"{HEADLINE_ID}.json").read_text())
    hstd = _records(head)[("standard", "standard", False)]
    res["e19_stored_normal_twin"] = {"fingerprint": ref["fingerprint"],
                                     "net_standard_standard": _records(ref)[
                                         ("standard", "standard", False)]["net"]}
    res["e19_published_headline_bootstrap"] = {"job": HEADLINE_ID, "fingerprint": head["fingerprint"],
                                               "net_standard_standard": hstd["net"],
                                               "rerun": "not possible (data rule)"}
    ok = all(res[t]["max_abs_diff"] == 0.0 for t in ("e19_rules", "e26_refreshed_rules"))
    ok &= res["e19_rules"]["fingerprint"] == ref["fingerprint"]
    ok &= math.isclose(hstd["net"]["mean"], -250.0, abs_tol=0.5)
    res["pass"] = bool(ok)
    (WORK / "A3_regress_e19.json").write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
