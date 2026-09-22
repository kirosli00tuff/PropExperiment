"""Stage D.1d Task 3: screen the seven re-tests (RT1-RT7) through the shared runner.

    uv run python -m strategy.research.g_timeframe._run_retests

Each re-test runs on fold 0's train window (the D.1 screening window) and on the 289-day
train union (the accounting window), exactly as every prior trial did. Folds 1-7 run only
for a re-test whose fold-0 composite verdict passes (declaration section 2). Every result
is written, survivors and non-survivors alike, next to the original trial's D.1 figures
on the same window (``reports/stage_d1_accounting.json``), so the resolution-effect read
is a comparison of like with like.

Writes reports/stage_d1d_retests.json. Train dates only (the runner refuses others).
"""

from __future__ import annotations

import hashlib
import json
import multiprocessing as mp
from pathlib import Path

from screening.runner import (
    _research_frame,
    fold_train_window,
    screen_candidate,
    train_union_window,
)
from strategy.research.g_timeframe.retests import RETESTS

DECLARATION = Path("reports/stage_d1d_timeframe_declaration.md")
D1_ACCOUNTING = Path("reports/stage_d1_accounting.json")
OUTPUT_PATH = Path("reports/stage_d1d_retests.json")
WINDOWS = ("fold0_train", "train_union")
N_FOLDS = 8


def _window(name: str):
    if name == "train_union":
        return train_union_window()
    return fold_train_window(int(name.removeprefix("fold").removesuffix("_train")))


def _run(job: tuple[int, str]) -> dict:
    index, window = job
    label, original, factory = RETESTS[index]
    try:
        report = screen_candidate(label, factory, _window(window))
    except Exception as exc:  # recorded, never swallowed: main() refuses to summarise
        return {"index": index, "label": label, "window": window, "error": repr(exc)}
    return {"index": index, "label": label, "original": original, "window": window,
            "report": report.to_dict()}


def _originals() -> dict[tuple[str, str], dict]:
    logged = json.loads(D1_ACCOUNTING.read_text())
    rows = {}
    for key, window in (("fold0_rerun", "fold0_train"), ("train_union_run", "train_union")):
        for row in logged[key]:
            rows[(row["label"], window)] = row
    return rows


def _comparison(run: dict, original: dict | None) -> dict:
    report = run["report"]
    n = report["n_trips"]
    out = {"retest": {"n_trips": n, "trades_per_day": report["trades_per_day"],
                      "p": report["zero_edge"]["win_probability"],
                      "R": report["zero_edge"]["win_loss_ratio"],
                      "net_usd": report["net_pnl_usd"],
                      "net_per_trip_usd": report["net_pnl_usd"] / n if n else None,
                      "robust": report["zero_edge"]["robust"],
                      "drift_verdict": report["drift_verdict"], "verdict": report["verdict"],
                      "reasons": report["reasons"]}}
    if original is not None:
        m = original["n_trips"]
        out["original"] = {"n_trips": m, "trades_per_day": original["trades_per_day"],
                           "p": original["win_probability"], "R": original["win_loss_ratio"],
                           "net_usd": original["net_pnl_usd"],
                           "net_per_trip_usd": original["net_pnl_usd"] / m if m else None}
    out["resolution_effect"] = (
        "supported: the re-test passes the composite where the original failed"
        if report["verdict"] == "pass" else
        "not supported: the composite still fails (direction of change reported only)")
    return out


def main() -> None:
    _research_frame()  # load once in the parent; forked workers inherit the cache
    jobs = [(i, w) for i in range(len(RETESTS)) for w in WINDOWS]
    with mp.get_context("fork").Pool(processes=min(12, len(jobs))) as pool:
        results = pool.map(_run, jobs, chunksize=1)
    errors = [r for r in results if "error" in r]
    if errors:
        raise SystemExit("runs errored: " + "; ".join(f"{r['label']}/{r['window']}: {r['error']}"
                                                      for r in errors))
    passers = sorted({r["index"] for r in results
                      if r["window"] == "fold0_train" and r["report"]["verdict"] == "pass"})
    extension = []
    if passers:
        jobs = [(i, f"fold{k}_train") for i in passers for k in range(1, N_FOLDS)]
        with mp.get_context("fork").Pool(processes=min(12, len(jobs))) as pool:
            extension = pool.map(_run, jobs, chunksize=1)
    originals = _originals()
    out = {
        "meta": {"declaration_sha256": hashlib.sha256(DECLARATION.read_bytes()).hexdigest(),
                 "n_retests": len(RETESTS), "windows": list(WINDOWS),
                 "fold_extension_run_for": [RETESTS[i][0] for i in passers]},
        "runs": results + extension,
        "comparison": [{"label": r["label"], "original_label": r["original"],
                        "window": r["window"],
                        **_comparison(r, originals.get((r["original"], r["window"])))}
                       for r in results],
        "fold0_survivors": [RETESTS[i][0] for i in passers],
    }
    OUTPUT_PATH.write_text(json.dumps(out, indent=1, default=str) + "\n")
    print(f"wrote {OUTPUT_PATH}; fold-0 survivors: {len(passers)}")
    for c in out["comparison"]:
        r = c["retest"]
        print(f"  {c['label']} [{c['window']}]: n={r['n_trips']} p={r['p']:.3f} R={r['R']:.3f} "
              f"net=${r['net_usd']:,.2f} verdict={r['verdict']}")


if __name__ == "__main__":
    main()
