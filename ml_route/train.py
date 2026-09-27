"""E.ML-train's entry points (M5 steps 1-4, M7, M8). Real data only through the step 2 store.

    uv run python -m ml_route.train fit --challenger lgbm --horizon h30 \
        --store-root data/processed_step2 --out-dir <dir> --harness-sha256 <sha256>
    uv run python -m ml_route.train finalize --out-dir <dir> --harness-sha256 <sha256>

Every entry calls ``screening.harness_freeze.preflight(expected)`` FIRST, before any input or bar is
read, and writes the returned manifest sha256 into every ledger record, candidate file and the
route manifest. No flag or environment variable skips it. Frozen values (grids, seeds, threads,
windows, blocks, costs, S_X, the release calendar, the LSTM batch size) come from frozen files and
module constants; ``load_route_inputs`` refuses while S_X and the release calendar are unwired.
Every ledger record carries the fit's device ("cpu" for LightGBM, "cuda" for the LSTM, which
refuses by name without CUDA and runs with its route machine record's batch; review NOTE-5 and
NOTE-11, ml_route.lstm_machine).

``fit`` (one challenger, one horizon): M7.3's 10 CPCV splits for each configuration (resumable:
a key already in the ledger is skipped), ML-A01's scores, selection with ML-A10's ties, the refit
on blocks 1-5, then per cluster the surrogate, its candidate leaves, the block-6 pre-test, and a
candidates file. ``finalize``: M5 step 4 across the six candidate files, the rule JSON files and
the route manifest (ml_route.manifest).
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import numpy as np

HORIZON_CHOICES = ("h30", "h120", "hF")
CHALLENGER_CHOICES = ("lgbm", "lstm")


def _preflight(expected: str) -> str:
    from screening.harness_freeze import preflight

    return preflight(expected)


def _prepare_process() -> None:
    from compute.platform import apply_thread_limits, lower_priority

    lower_priority()
    apply_thread_limits(1)  # BLAS/OpenMP outside the learner's own thread count (M8)


@dataclass(frozen=True)
class FitContext:
    challenger: str
    horizon: str
    out_dir: Path
    harness_sha256: str


def _ledger_path(ctx: FitContext) -> Path:
    return ctx.out_dir / "ledger" / f"{ctx.challenger}_{ctx.horizon}.jsonl"


def _window_record(table, rows: np.ndarray) -> dict:  # noqa: ANN001 - RowTable
    days = table.day[rows]
    return {"rows": int(len(rows)), "first": str(days.min()) if len(rows) else None,
            "last": str(days.max()) if len(rows) else None,
            "row_index_sha256": _row_index_sha(table, rows)}


def _row_index_sha(table, rows: np.ndarray) -> str:  # noqa: ANN001
    from ml_route.ledger import sha256_bytes

    names = "|".join(table.product[rows].astype(str)).encode("utf-8")
    return sha256_bytes(table.t_ns[rows].astype("<i8").tobytes() + names)


def run_fit(ctx: FitContext, table, adapter, cut, inputs,  # noqa: ANN001, C901, PLR0915
            log: Callable[[str], None] = print) -> dict:
    """M5 steps 1-3 for one challenger and horizon on a built row table."""
    from ml_route.blocks import assert_fold, cpcv_splits, split_masks
    from ml_route.ledger import Ledger, check_refit, machine_id, verify_chain
    from ml_route.selection import configuration_score, portfolio_daily, select, split_score
    from ml_route.store import assert_window

    ledger = Ledger(_ledger_path(ctx))
    verify_chain(ledger)
    done = ledger.keys()
    machine = machine_id()
    usable = adapter.usable_rows(table, ctx.horizon)
    block = np.array([cut.block_of(d.astype(object)) for d in table.day])
    in15 = usable & (block <= 5)
    splits = cpcv_splits(cut)
    scored: list[tuple[dict, float]] = []
    for config in adapter.grid():
        cid = adapter.config_id(config)
        scores = []
        for split in splits:
            key = f"{cid}|{split.label()}"
            if key in done:
                scores.append(float(ledger.get(key)["score"]))
                continue
            rows15 = np.flatnonzero(in15)
            tr, va, purged = split_masks(split, table.day[rows15].astype(object),
                                         table.t_ns[rows15], table.exit_ns[ctx.horizon][rows15])
            assert_fold(split, table.day[rows15].astype(object), table.t_ns[rows15],
                        table.exit_ns[ctx.horizon][rows15], tr, va)
            train_rows, val_rows = rows15[tr], rows15[va]
            for root in np.unique(table.product[train_rows]):
                sel = train_rows[table.product[train_rows] == root]
                assert_window(str(root), inputs.s_x[str(root)], table.day[sel], key)
            t0 = time.perf_counter()
            model, _, sha = adapter.fit(table, train_rows, config, ctx.horizon)
            pred = adapter.predict(model, table, val_rows, config)
            y, c = table.y[ctx.horizon][val_rows], table.cost[ctx.horizon][val_rows]
            s = split_score(table.product[val_rows], table.day[val_rows], table.t_ns[val_rows],
                            table.exit_ns[ctx.horizon][val_rows], y, c, pred)
            from ml_route.selection import (
                one_open_position,
                positions_from_predictions,
                trade_pnl,
            )

            pos = one_open_position(table.product[val_rows], table.t_ns[val_rows],
                                    table.exit_ns[ctx.horizon][val_rows],
                                    positions_from_predictions(pred, c))
            daily = portfolio_daily(table.product[val_rows], table.day[val_rows],
                                    trade_pnl(y, c, pos, 1.0))
            ledger.append({"key": key, "challenger": ctx.challenger, "horizon": ctx.horizon,
                           "config": config, "split": split.label(), "score": s.score,
                           "n_dates": s.n_dates, "n_trades": s.n_trades, "purged_rows": purged,
                           "train": _window_record(table, train_rows),
                           "validation": _window_record(table, val_rows),
                           "daily_pnl": [[str(d), float(v)] for d, v in daily.items()],
                           "model_sha256": sha, "machine": machine,
                           "device": adapter.device, "harness_sha256": ctx.harness_sha256,
                           "seconds": round(time.perf_counter() - t0, 2)})
            scores.append(s.score)
            log(f"{key}: score {s.score:.5f} ({time.perf_counter() - t0:.1f} s)")
        scored.append((config, configuration_score(scores)))
    chosen = select(ctx.challenger, scored)
    cid = adapter.config_id(chosen)
    refit_rows = np.flatnonzero(in15)
    for root in np.unique(table.product[refit_rows]):
        sel = refit_rows[table.product[refit_rows] == root]
        assert_window(str(root), inputs.s_x[str(root)], table.day[sel], "refit")
    model, data, sha = adapter.fit(table, refit_rows, chosen, ctx.horizon)
    key = f"{cid}|refit"
    prior = ledger.get(key)
    if prior is not None:
        check_refit(prior, sha, machine)
    else:
        ledger.append({"key": key, "challenger": ctx.challenger, "horizon": ctx.horizon,
                       "config": chosen, "split": "refit_blocks_1_5",
                       "train": _window_record(table, refit_rows), "model_sha256": sha,
                       "machine": machine, "device": adapter.device,
                       "harness_sha256": ctx.harness_sha256})
    model_path = ctx.out_dir / "models" / f"{ctx.challenger}_{ctx.horizon}_{cid}_refit.bin"
    model_path.parent.mkdir(parents=True, exist_ok=True)
    if not model_path.exists():
        model_path.write_bytes(data)
    return {"selected": chosen, "config_id": cid, "scores": {adapter.config_id(c): s
                                                               for c, s in scored},
            "model_sha256": sha, "model_file": model_path.name, "model": model,
            "usable": usable, "block": block}


def run_distil(ctx: FitContext, table, adapter, fit_out: dict, inputs) -> dict:  # noqa: ANN001
    """M5 steps 2-3 for the selected model: surrogates, candidates, block-6 pre-test."""
    from ml_route.constants import CLUSTER_IDS, CLUSTERS, COST_STRESS, LEAD_OF_CLUSTER
    from ml_route.store import assert_window
    from ml_route.surrogate import (
        RuleRows,
        candidate_sign,
        condition_mask,
        fit_surrogate,
        leaves,
        pretest,
        rule_json,
        rule_result,
    )

    usable, block = fit_out["usable"], fit_out["block"]
    out = {"challenger": ctx.challenger, "horizon": ctx.horizon, "surrogates": [],
           "candidates": [], "survivors": [], "harness_sha256": ctx.harness_sha256}
    for k in CLUSTER_IDS:
        members = [p for p in CLUSTERS[k] if p in inputs.traded()]
        in_k = usable & np.isin(table.product.astype(str), members)
        r15, r6 = np.flatnonzero(in_k & (block <= 5)), np.flatnonzero(in_k & (block == 6))
        if len(r15) == 0:
            continue
        for rows, step in ((r15, f"distil {k} blocks 1-5"), (r6, f"pretest {k} block 6")):
            for root in np.unique(table.product[rows]):
                sel = rows[table.product[rows] == root]
                assert_window(str(root), inputs.s_x[str(root)], table.day[sel], step)
        pred15 = adapter.predict(fit_out["model"], table, r15, fit_out["selected"])
        tree = fit_surrogate(table.X[r15], pred15)
        lead_vehicle = inputs.products[LEAD_OF_CLUSTER[k]].vehicle
        if lead_vehicle is None:
            from ml_route.inputs import RouteInputMissing

            raise RouteInputMissing(f"{k}: the lead exposure has no vehicle; ML-A15's ADV "
                                    "fallback needs D1's table, not wired")
        exposures = [inputs.products[p].vehicle for p in members]
        out["surrogates"].append({"cluster": k, "n_rows": int(len(r15)),
                                  "tree": _tree_record(tree)})

        def rows_of(r: np.ndarray) -> RuleRows:
            return RuleRows(table.product[r], table.day[r], table.t_ns[r],
                            table.exit_ns[ctx.horizon][r], table.X[r], table.y[ctx.horizon][r],
                            table.cost[ctx.horizon][r])

        for leaf in leaves(tree):
            in_leaf = condition_mask(table.X[r15], leaf.conditions)
            c_bar = float(table.cost[ctx.horizon][r15][in_leaf].mean())
            sign = candidate_sign(leaf.mu, c_bar)
            if sign == 0:
                continue
            res6 = rule_result(rows_of(r6), leaf.conditions, sign, COST_STRESS)
            res15 = rule_result(rows_of(r15), leaf.conditions, sign, COST_STRESS)
            ok, reasons = pretest(res6, res15)
            rule = rule_json(k, ctx.challenger, ctx.horizon, leaf, sign, c_bar, exposures,
                             lead_vehicle,
                             {"model_sha256": fit_out["model_sha256"],
                              "config": fit_out["selected"],
                              "surrogate_sha256": _tree_sha(tree),
                              "harness_sha256": ctx.harness_sha256},
                             {"block6_net_pnl": res6.net_pnl, "block6_trades": res6.trades,
                              "block6_dates": res6.dates,
                              "block6_per_trade_date": res6.per_trade_date,
                              "blocks15_net_pnl": res15.net_pnl, "passed": ok,
                              "reasons": reasons})
            out["candidates"].append(rule)
            if ok:
                out["survivors"].append(rule)
    return out


def _tree_record(tree) -> dict:  # noqa: ANN001
    t = tree.tree_
    return {"feature": t.feature.tolist(), "threshold": [float(x) for x in t.threshold],
            "children_left": t.children_left.tolist(),
            "children_right": t.children_right.tolist(),
            "value": [float(v) for v in t.value.ravel()],
            "n_node_samples": t.n_node_samples.tolist()}


def _tree_sha(tree) -> str:  # noqa: ANN001
    from ml_route.ledger import canonical, sha256_bytes

    return sha256_bytes(canonical(_tree_record(tree)))


def save_row_index(path: Path, table) -> str:  # noqa: ANN001 - RowTable
    """The saved row index M7.4 asserts on: (product, trade date, t) of every row."""
    from ml_route.ledger import sha256_bytes

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as fh:
        np.savez(fh, product=table.product.astype(str), day=table.day.astype("datetime64[D]"),
                 t_ns=table.t_ns.astype(np.int64))
    return sha256_bytes(path.read_bytes())


def cmd_fit(args: argparse.Namespace) -> int:
    harness = _preflight(args.harness_sha256)  # FIRST: before any input or bar is read
    _prepare_process()
    from ml_route.adapters import adapter_for
    from ml_route.blocks import frozen_block_cut
    from ml_route.dataset import build_dataset
    from ml_route.inputs import load_route_inputs

    inputs = load_route_inputs()
    cut = frozen_block_cut()
    ctx = FitContext(args.challenger, args.horizon, Path(args.out_dir), harness)
    adapter = adapter_for(args.challenger, args.store_root, inputs, ctx.out_dir, harness)
    table = build_dataset(Path(args.store_root), inputs)
    index_sha = save_row_index(ctx.out_dir / f"row_index_{args.challenger}_{args.horizon}.npz",
                               table)
    adapter.attach(table)
    fit_out = run_fit(ctx, table, adapter, cut, inputs)
    distil = run_distil(ctx, table, adapter, fit_out, inputs)
    distil.update({"selected": fit_out["selected"], "model_sha256": fit_out["model_sha256"],
                   "model_file": fit_out["model_file"], "scores": fit_out["scores"],
                   "row_counts": table.counts, "row_index_sha256": index_sha,
                   "step2_store_sha256": dict(sorted(table.store_sha256.items()))})
    path = ctx.out_dir / "candidates" / f"{ctx.challenger}_{ctx.horizon}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(distil, indent=1, sort_keys=True, default=str) + "\n",
                    encoding="utf-8")
    return 0


def cmd_finalize(args: argparse.Namespace) -> int:
    harness = _preflight(args.harness_sha256)
    from ml_route.manifest import finalize_route

    finalize_route(Path(args.out_dir), harness)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    fit = sub.add_parser("fit")
    fit.add_argument("--challenger", choices=CHALLENGER_CHOICES, required=True)
    fit.add_argument("--horizon", choices=HORIZON_CHOICES, required=True)
    fit.add_argument("--store-root", type=Path, required=True)
    fit.add_argument("--out-dir", type=Path, required=True)
    fit.add_argument("--harness-sha256", required=True)
    fin = sub.add_parser("finalize")
    fin.add_argument("--out-dir", type=Path, required=True)
    fin.add_argument("--harness-sha256", required=True)
    args = parser.parse_args(argv)
    return cmd_fit(args) if args.cmd == "fit" else cmd_finalize(args)


if __name__ == "__main__":
    sys.exit(main())
