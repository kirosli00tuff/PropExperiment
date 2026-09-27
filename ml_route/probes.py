"""M8's timed probes on synthetic data of the real size (Stage E.2b Task 2). No market data.

    uv run python -m ml_route.probes lgbm  --out reports/stage_e2b_ml_probes.json
    uv run python -m ml_route.probes lstm  --out reports/stage_e2b_ml_probes.json

- lgbm: one CPCV split of a 450,000-row synthetic table (31 products, 7 clusters, the real design
  matrix: F1-F17 plus the one-hot F18 and F19), the largest and the smallest tree configuration,
  8 threads, each timed for fit + validation prediction + ML-A01 score.
- lstm: M8's A-1 batch-size rule (the largest configuration, 32 hidden units, lookback 72, one
  forward and backward pass on synthetic inputs of the frozen shapes at 512, then 256, 128, 64
  while less than 0.5 GB of the 4 GB stays free; peak = torch.cuda.max_memory_reserved() plus
  the process's CUDA context, read as nvidia-smi's per-process figure minus
  torch.cuda.memory_reserved() at the same moment), then one epoch of the largest configuration at
  the chosen batch on the split's training rows, and the projected full-run time.
Peak RAM is measured outside the process (``/usr/bin/time -v`` on Linux), so this module stays
cross-platform; the caller passes the figure in with ``--record-ram``.
Results merge into the JSON file under their probe name.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np

from compute.platform import apply_thread_limits, lower_priority
from ml_route.constants import (
    CLUSTER_IDS,
    CPCV_BLOCKS,
    LGBM_THREADS,
    LSTM_BATCH_LADDER,
    LSTM_FIXED,
    N_BLOCKS,
    VRAM_MIN_FREE_GB,
    VRAM_TOTAL_GB,
)

N_ROWS = 450_000
N_PRODUCTS = 31
N_DATES = 1248  # the training calendar's n (ML-A03)
N_CONTINUOUS = 17
N_STATIC_LSTM = 17 + len(CLUSTER_IDS)
PROBE_SEED = 20260926
TREE_FITS_PER_CONFIG = 11
LSTM_FITS_PER_CONFIG = 11
PT = ZoneInfo("America/Vancouver")


def _now() -> str:
    return datetime.now(UTC).astimezone(PT).strftime("%Y-%m-%d %H:%M:%S %Z")


def synthetic_table(seed: int = PROBE_SEED) -> dict[str, np.ndarray]:
    rng = np.random.default_rng(seed)
    day = np.sort(rng.integers(0, N_DATES, size=N_ROWS))
    product = rng.integers(0, N_PRODUCTS, size=N_ROWS)
    cluster = product % len(CLUSTER_IDS)
    X = rng.standard_normal((N_ROWS, N_CONTINUOUS))
    y = 0.05 * X[:, 0] + rng.standard_normal(N_ROWS)
    slot = rng.integers(0, 13, N_ROWS)
    t_ns = day.astype(np.int64) * 86_400_000_000_000 + slot * 1_800_000_000_000
    return {"day": day, "product": product, "cluster": cluster, "X": X, "y": y, "t_ns": t_ns,
            "exit_ns": t_ns + 1_800_000_000_000, "cost": np.full(N_ROWS, 0.05)}


def one_split(day: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Split (1, 2) of the CPCV (test blocks 1 and 2), with the one-date embargo after block 2."""
    size = N_DATES // N_BLOCKS
    block = np.minimum(day // size, N_BLOCKS - 1) + 1
    val = (block == 1) | (block == 2)
    embargo = day == 2 * size  # the first date of block 3
    train = np.isin(block, [b for b in CPCV_BLOCKS if b not in (1, 2)]) & ~embargo
    return train, val


def probe_lgbm() -> dict:
    from ml_route import lgbm
    from ml_route.selection import split_score

    tab = synthetic_table()
    onehot_p = np.eye(N_PRODUCTS)[tab["product"]]
    onehot_k = np.eye(len(CLUSTER_IDS))[tab["cluster"]]
    X = np.hstack([tab["X"], onehot_p, onehot_k])
    names = ([f"F{i + 1}" for i in range(N_CONTINUOUS)] + [f"F18_{i}" for i in range(N_PRODUCTS)]
             + [f"F19_{k}" for k in CLUSTER_IDS])
    train, val = one_split(tab["day"])
    out = {"rows_total": N_ROWS, "rows_train": int(train.sum()), "rows_validation": int(val.sum()),
           "design_columns": X.shape[1], "threads": LGBM_THREADS, "configs": {}}
    for config in (lgbm.grid()[-4], lgbm.grid()[3]):  # (31, 500, *) largest; (7, 2000, 10) smallest
        config = dict(config)
        t0 = time.perf_counter()
        booster, _, sha = lgbm.fit(X[train], tab["y"][train], names, config)
        t_fit = time.perf_counter() - t0
        pred = lgbm.predict(booster, X[val])
        score = split_score(tab["product"][val], tab["day"][val], tab["t_ns"][val],
                            tab["exit_ns"][val], tab["y"][val], tab["cost"][val], pred)
        t_all = time.perf_counter() - t0
        out["configs"][lgbm.config_id(config)] = {
            "fit_seconds": round(t_fit, 2), "fit_predict_score_seconds": round(t_all, 2),
            "model_sha256": sha, "score": score.score}
    big = max(v["fit_predict_score_seconds"] for v in out["configs"].values())
    small = min(v["fit_predict_score_seconds"] for v in out["configs"].values())
    refit_factor = 5 / 3  # a refit trains on blocks 1-5, about 5/3 of a split's training rows
    per_cfg = lambda s: 10 * s + refit_factor * s  # noqa: E731
    out["projection"] = {
        "rule": "24 configurations x (10 splits + 1 refit); half the configurations at 31 leaves "
                "(timed: largest), half at 7 (timed: smallest); refit = 5/3 of a split fit",
        "hours_estimate": round(3 * 4 * (per_cfg(big) + per_cfg(small)) / 3600, 2),
        "hours_upper_all_largest": round(24 * per_cfg(big) / 3600, 2)}
    return out


def _nvidia_smi_process_mib(pid: int) -> float | None:
    try:
        res = subprocess.run(["nvidia-smi", "--query-compute-apps=pid,used_memory",
                              "--format=csv,noheader,nounits"], capture_output=True, text=True,
                             check=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    for line in res.stdout.splitlines():
        parts = [p.strip() for p in line.split(",")]
        if len(parts) == 2 and parts[0] == str(pid):
            return float(parts[1])
    return None


def _nvidia_smi_gpu() -> dict:
    try:
        res = subprocess.run(["nvidia-smi", "--query-gpu=name,driver_version,memory.total,"
                              "memory.used,memory.free", "--format=csv,noheader,nounits"],
                             capture_output=True, text=True, check=True, timeout=30)
    except (OSError, subprocess.SubprocessError) as exc:
        return {"error": repr(exc)}
    name, driver, total, used, free = [p.strip() for p in res.stdout.splitlines()[0].split(",")]
    return {"name": name, "driver": driver, "total_mib": float(total), "used_mib": float(used),
            "free_mib": float(free)}


def a1_step(batch: int, device: str, total_mib: float = VRAM_TOTAL_GB * 1024) -> dict:
    """One step of M8's A-1 measure at ``batch``: the largest configuration (32 hidden units,
    lookback 72), one forward and backward pass on synthetic inputs of the frozen shapes; peak =
    torch.cuda.max_memory_reserved() plus the process's CUDA context (nvidia-smi's per-process
    figure minus torch.cuda.memory_reserved() at the same moment); free = ``total_mib`` - peak,
    which must leave at least 0.5 GB. Also used by ml_route.lstm_machine (review NOTE-11)."""
    import os

    import torch

    from ml_route.lstm import build_model

    lookback, hidden = 72, 32
    need_free_mib = VRAM_MIN_FREE_GB * 1024
    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()
    model = build_model(N_PRODUCTS, N_STATIC_LSTM, hidden).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=float(LSTM_FIXED["lr"]))
    g = torch.Generator().manual_seed(PROBE_SEED)
    seq = torch.randn(batch, lookback, 3, generator=g).to(device)
    lengths = torch.full((batch,), lookback, dtype=torch.int64)
    prod = torch.randint(0, N_PRODUCTS, (batch,), generator=g).to(device)
    static = torch.randn(batch, N_STATIC_LSTM, generator=g).to(device)
    target = torch.randn(batch, generator=g).to(device)
    loss = torch.nn.functional.mse_loss(model(seq, lengths, prod, static), target)
    opt.zero_grad()
    loss.backward()
    opt.step()
    torch.cuda.synchronize()
    peak_reserved = torch.cuda.max_memory_reserved() / 2**20
    now_reserved = torch.cuda.memory_reserved() / 2**20
    per_process = _nvidia_smi_process_mib(os.getpid())
    context = None if per_process is None else per_process - now_reserved
    peak = None if context is None else peak_reserved + context
    free = None if peak is None else total_mib - peak
    ok = free is not None and free >= need_free_mib
    del model, opt, seq, prod, static, target, loss
    return {"batch": batch, "max_memory_reserved_mib": round(peak_reserved, 1),
            "memory_reserved_now_mib": round(now_reserved, 1),
            "nvidia_smi_process_mib": per_process,
            "cuda_context_mib": None if context is None else round(context, 1),
            "peak_mib": None if peak is None else round(peak, 1),
            "free_of_4gb_mib": None if free is None else round(free, 1),
            "leaves_0_5gb_free": ok}


def batch_probe(device: str, total_mib: float = VRAM_TOTAL_GB * 1024) -> dict:
    """M8's A-1 rule on synthetic inputs of the frozen shapes: 512, then 256, 128, 64 while less
    than 0.5 GB of the card stays free (``total_mib``: the 4 GB of M8 by default)."""
    from ml_route.lstm import set_determinism

    set_determinism()
    steps = []
    chosen = None
    for batch in LSTM_BATCH_LADDER:
        step = a1_step(batch, device, total_mib)
        steps.append(step)
        if step["leaves_0_5gb_free"]:
            chosen = batch
            break
    return {"rule": "M8 / A-1: largest configuration (32 hidden, lookback 72), one forward and "
                    "backward pass; halve 512 -> 256 -> 128 -> 64 while less than 0.5 GB of the "
                    "4 GB stays free", "steps": steps, "batch_size": chosen,
            "stop_to_user": chosen is None}


def probe_lstm() -> dict:
    import torch

    from ml_route import lstm

    gpu = torch.cuda.is_available()
    device = "cuda" if gpu else "cpu"
    out = {"device": device, "gpu": _nvidia_smi_gpu(), "torch": torch.__version__,
           "cuda_runtime": torch.version.cuda, "cudnn": torch.backends.cudnn.version(),
           "arch_list": torch.cuda.get_arch_list() if gpu else []}
    if not gpu:
        out["gpu_unavailable_reason"] = "torch.cuda.is_available() is False"
        batch = int(LSTM_FIXED["planned_batch"])
    else:
        out["batch_probe"] = batch_probe(device)
        batch = out["batch_probe"]["batch_size"]
        if batch is None:
            return out
    rng = np.random.default_rng(PROBE_SEED)
    tab = synthetic_table()
    train, _ = one_split(tab["day"])
    rows = np.flatnonzero(train)
    n = len(rows)
    lookback = 72
    steps5 = rng.standard_normal((n + lookback, 3)).astype(np.float32)
    lengths_all = rng.integers(1, lookback + 1, size=n)
    static = np.hstack([tab["X"][rows], np.eye(len(CLUSTER_IDS))[tab["cluster"][rows]]]
                       ).astype(np.float32)
    prod = tab["product"][rows].astype(np.int64)

    def batch_fn(r: np.ndarray):  # noqa: ANN202 - the same gather shape as lstm_data.gather
        idx = r[:, None] + np.arange(lookback)[None, :]
        seq = steps5[idx]
        ln = lengths_all[r]
        seq[np.arange(lookback)[None, :] >= ln[:, None]] = 0.0
        return seq, ln, prod[r], static[r]

    if gpu:
        torch.cuda.reset_peak_memory_stats()
    epochs = []
    t0 = time.perf_counter()
    cfg = {"hidden": 32, "lookback": lookback}
    _, _, sha = lstm._train(n, batch_fn, tab["y"][rows], N_PRODUCTS, N_STATIC_LSTM, cfg, batch,
                            device, 1, lambda e, loss: epochs.append(round(loss, 4)))
    t_epoch = time.perf_counter() - t0
    out["epoch_probe"] = {"config": cfg, "rows": n, "batch_size": batch,
                          "epoch_seconds": round(t_epoch, 2), "loss": epochs,
                          "model_sha256": sha}
    if gpu:
        out["epoch_probe"]["max_memory_reserved_mib"] = round(
            torch.cuda.max_memory_reserved() / 2**20, 1)
    fits = 10 + 5 / 3  # 10 split fits + 1 refit on about 5/3 of a split's rows
    lb24 = 24 / 72  # the lookback-24 configurations run about a third of the steps
    per_cfg_big = fits * int(LSTM_FIXED["epochs"]) * t_epoch
    out["projection"] = {
        "rule": "12 configurations x 11 fits x 8 epochs; timed: one epoch of the largest "
                "configuration; lookback-24 configurations scaled by 24/72 (a guess)",
        "hours_estimate": round(3 * 2 * (per_cfg_big + lb24 * per_cfg_big) / 3600, 2),
        "hours_upper_all_largest": round(12 * per_cfg_big / 3600, 2)}
    return out


def merge(path: Path, name: str, result: dict) -> None:
    data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    data.setdefault("probes", {})[name] = {**result, "recorded_pdt": _now()}
    path.write_text(json.dumps(data, indent=2, sort_keys=True, default=str) + "\n",
                    encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("probe", choices=("lgbm", "lstm", "versions", "ram"))
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--record-ram", nargs=2, metavar=("PROBE", "MAX_RSS_KB"))
    args = parser.parse_args(argv)
    lower_priority()
    apply_thread_limits(1)  # BLAS/OpenMP outside the learner's own count (M8)
    if args.probe == "ram":
        name, kb = args.record_ram
        data = json.loads(args.out.read_text(encoding="utf-8"))
        data["probes"][name]["peak_ram_mib"] = round(int(kb) / 1024, 1)
        args.out.write_text(json.dumps(data, indent=2, sort_keys=True, default=str) + "\n",
                            encoding="utf-8")
        return 0
    if args.probe == "versions":
        import lightgbm
        import sklearn
        import torch

        merge(args.out, "versions", {"lightgbm": lightgbm.__version__, "torch": torch.__version__,
                                     "cuda_runtime": torch.version.cuda,
                                     "cudnn": torch.backends.cudnn.version(),
                                     "arch_list": torch.cuda.get_arch_list(),
                                     "sklearn": sklearn.__version__,
                                     "python": sys.version.split()[0], "gpu": _nvidia_smi_gpu()})
        return 0
    result = probe_lgbm() if args.probe == "lgbm" else probe_lstm()
    merge(args.out, args.probe, result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
