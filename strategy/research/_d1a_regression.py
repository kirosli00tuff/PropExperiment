"""Stage D.1a, Task 4: re-run Stage D.1's 23 logged trials through the shared runner.

Tooling, not a hypothesis. No new trial is run: the trial list is imported from
``_lead_accounting.TRIALS`` unchanged. Three checks, reported, never tuned toward an
expected answer:

1. SAME NUMBERS. On fold 0's train dates and on the 289-day train union, every
   trial's n / p / R / T / net must equal ``reports/stage_d1_accounting.json`` exactly.
   The runner's canonical EngineConfig equals the one the D.1 lead used, and the
   engine's market-order path is unchanged, so any difference is a regression.
2. SAME VERDICTS. The raw zero-edge robust verdict must equal the one Stage D.1
   logged (transcribed below from its progress.md table), and no trial may pass the
   composite (zero-edge AND drift) verdict.
3. DRIFT CATCHES THE FOUR. The four unconditional longs Stage D.1 flagged as
   drift-driven must fail the DRIFT benchmark itself, not merely the zero-edge null.
   The same holds on all 8 folds' train windows, as a supplementary check.

    uv run python -m strategy.research._d1a_regression

Writes reports/stage_d1a_regression.json. Train dates only (the runner refuses others).
"""

from __future__ import annotations

import json
import multiprocessing as mp
from pathlib import Path

from screening.runner import (
    _research_frame,
    fold_train_window,
    screen_candidate,
    train_union_window,
)
from strategy.research._lead_accounting import TRIALS

D1_ACCOUNTING = Path("reports/stage_d1_accounting.json")
OUTPUT_PATH = Path("reports/stage_d1a_regression.json")
DRIFT_FLAGGED = ("A-H1 european-open overnight drift", "A-H2 rth close window (buy)",
                 "A-H4 eth leg", "A-H4 rth leg")

# Robust verdicts exactly as Stage D.1's progress.md Task 3 table logged them:
# (fold 0 train, 289-day train union). "unmeasurable (no wins)" is "unmeasurable" here.
D1_ROBUST = {
    "A-H1 european-open overnight drift": ("fail", "fail"),
    "A-H2 rth close window (buy)": ("fail", "fail"),
    "A-H2 rth close window (sell)": ("fail", "fail"),
    "A-H3 weekend effect": ("below_grid", "fail"),
    "A-H4 eth leg": ("fail", "fail"),
    "A-H4 rth leg": ("fail", "fail"),
    "B-H1 opening-range breakout (hold 5)": ("below_grid", "fail"),
    "B-H1 opening-range breakout (hold 75)": ("fail", "fail"),
    "B-H2 prior-day stop cascade": ("fail", "fail"),
    "B-H3 breakout leg": ("fail", "fail"),
    "B-H3 fade leg": ("fail", "fail"),
    "B-H4 narrow-range breakout": ("fail", "fail"),
    "C-H1 magnitude-conditioned reversal": ("below_grid", "below_grid"),
    "C-H2 post-spike exhaustion fade": ("below_grid", "below_grid"),
    "C-H3 close-location-value reversal": ("below_grid", "below_grid"),
    "D-H1 trailing-vol regime gate": ("fail", "fail"),
    "D-H2 inverse-vol sizing": ("fail", "fail"),
    "D-H3 range-compression gate": ("below_grid", "below_grid"),
    "D-H4 overnight gap fade": ("below_grid", "below_grid"),
    "E-H1 scheduled macro drift": ("below_grid", "below_grid"),
    "E-H2 post-release momentum": ("fail", "fail"),
    "E-H3 quarterly witching short": ("unmeasurable", "below_grid"),
    "E-H4 turn-of-month long": ("fail", "fail"),
}
NUMERIC_FIELDS = ("n_trips", "win_probability", "win_loss_ratio", "trades_per_day",
                  "net_pnl_usd")


def _window(name: str):
    return train_union_window() if name == "train_union" else fold_train_window(
        int(name.removeprefix("fold").removesuffix("_train")))


def _run(job: tuple[int, str]) -> dict:
    index, window_name = job
    label, factory = TRIALS[index]
    try:
        report = screen_candidate(label, factory, _window(window_name))
    except Exception as exc:  # recorded, never swallowed
        return {"index": index, "label": label, "window": window_name, "error": repr(exc)}
    return {"index": index, **report.to_dict()}


def _compare_numbers(run: dict, logged: dict) -> list[str]:
    ours = {"n_trips": run["n_trips"], "win_probability": run["zero_edge"]["win_probability"],
            "win_loss_ratio": run["zero_edge"]["win_loss_ratio"],
            "trades_per_day": run["trades_per_day"], "net_pnl_usd": run["net_pnl_usd"]}
    return [f"{k}: runner {ours[k]!r} vs D.1 {logged[k]!r}" for k in NUMERIC_FIELDS
            if ours[k] != logged[k]]


def main() -> None:
    _research_frame()  # load once in the parent; forked workers inherit it
    d1 = json.loads(D1_ACCOUNTING.read_text())
    logged = {(r["label"], r["window"]): r for r in d1["fold0_rerun"] + d1["train_union_run"]}
    flagged_idx = [i for i, (label, _) in enumerate(TRIALS) if label in DRIFT_FLAGGED]
    jobs = [(i, w) for w in ("fold0_train", "train_union") for i in range(len(TRIALS))]
    jobs += [(i, f"fold{k}_train") for k in range(1, 8) for i in flagged_idx]
    with mp.get_context("fork").Pool(processes=12) as pool:
        runs = pool.map(_run, jobs, chunksize=1)

    problems = [f"{r['label']}/{r['window']}: {r['error']}" for r in runs if "error" in r]
    for r in (r for r in runs if "error" not in r):
        key = (r["label"], r["window"])
        if key in logged:
            problems += [f"{key}: {m}" for m in _compare_numbers(r, logged[key])]
            want = D1_ROBUST[r["label"]][0 if r["window"] == "fold0_train" else 1]
            if r["zero_edge"]["robust"] != want:
                problems.append(f"{key}: robust {r['zero_edge']['robust']} vs D.1 {want}")
        if r["verdict"] != "fail":
            problems.append(f"{key}: composite verdict {r['verdict']} (D.1: nothing passed)")
        if r["label"] in DRIFT_FLAGGED and r["drift_verdict"] != "fail":
            problems.append(f"{key}: flagged drift trial PASSED the drift benchmark")

    out = {"n_trials": len(TRIALS), "n_runs": len(runs), "problems": problems,
           "drift_flagged": list(DRIFT_FLAGGED),
           "runs": [{k: v for k, v in r.items() if k != "caveats"} for r in runs]}
    OUTPUT_PATH.write_text(json.dumps(out, indent=1, default=str) + "\n")
    print(f"wrote {OUTPUT_PATH}: {len(runs)} runs, {len(problems)} problems")
    for p in problems:
        print("PROBLEM:", p)


if __name__ == "__main__":
    main()
