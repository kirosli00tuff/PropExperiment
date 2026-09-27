"""M3 challenger 2: one small pooled LSTM (PyTorch) with the product embedding (ML-A12).

Model: embedding(products with rows, 4) -> one-layer LSTM (3 inputs per 5-minute step, hidden
16 or 32) -> dropout 0.2 on the final hidden state (a one-layer nn.LSTM's own dropout argument
acts only between layers, so it is applied here; reading in the worker report) -> one linear
layer on [final hidden state, product embedding, static features (F1-F17 and the F19 cluster
one-hot)] -> the normalized net target. MSE loss, Adam at 1e-3, 8 epochs, no early stopping, no
gradient clipping, no weight decay; rows shuffled each epoch by a torch.Generator seeded
20260924; torch.manual_seed(20260924) before the weights are made; deterministic algorithms with
CUBLAS_WORKSPACE_CONFIG=:4096:8 and cuDNN deterministic. Padded steps are masked by packing, so
they never reach the final hidden state (equivalent to left padding with a mask).

A model's identity is the sha256 of ``serialize(state_dict)``: a JSON header (names, dtypes,
shapes, in state_dict order) followed by the raw little-endian tensor bytes. The same bytes are
the saved model file, so the file hash is the model hash (M7.6). No pickle is involved.
"""

from __future__ import annotations

import json
import os
from collections.abc import Callable
from itertools import product as cartesian

import numpy as np

from ml_route.constants import (
    CUBLAS_WORKSPACE_CONFIG,
    LSTM_FIXED,
    LSTM_GRID_AXES,
    SEED,
    TORCH_CPU_THREADS,
)
from ml_route.ledger import sha256_bytes

N_STEP_INPUTS = 3


def grid() -> list[dict]:
    names = [a for a, _ in LSTM_GRID_AXES]
    return [dict(zip(names, vals, strict=True))
            for vals in cartesian(*(v for _, v in LSTM_GRID_AXES))]


def config_id(config: dict) -> str:
    return f"lstm_h{config['hidden']}_lb{config['lookback']}"


def set_determinism() -> None:
    """ML-A12's deterministic settings; call before the first CUDA call of the process."""
    os.environ["CUBLAS_WORKSPACE_CONFIG"] = CUBLAS_WORKSPACE_CONFIG
    import torch

    torch.use_deterministic_algorithms(True)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    torch.set_num_threads(TORCH_CPU_THREADS)


def build_model(n_products: int, n_static: int, hidden: int):  # noqa: ANN201
    import torch
    from torch import nn

    class RouteLSTM(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.embed = nn.Embedding(n_products, int(LSTM_FIXED["embedding_dim"]))
            self.lstm = nn.LSTM(N_STEP_INPUTS, hidden, num_layers=int(LSTM_FIXED["layers"]),
                                batch_first=True)
            self.drop = nn.Dropout(float(LSTM_FIXED["dropout"]))
            self.out = nn.Linear(hidden + int(LSTM_FIXED["embedding_dim"]) + n_static, 1)

        def forward(self, seq, lengths, product, static):  # noqa: ANN001, ANN202
            packed = nn.utils.rnn.pack_padded_sequence(seq, lengths.cpu(), batch_first=True,
                                                       enforce_sorted=False)
            _, (h_n, _) = self.lstm(packed)
            h = self.drop(h_n[-1])
            z = torch.cat([h, self.embed(product), static], dim=1)
            return self.out(z).squeeze(1)

    torch.manual_seed(SEED)
    return RouteLSTM()


def serialize(state_dict) -> bytes:  # noqa: ANN001
    header, blobs = [], []
    for name, tensor in state_dict.items():
        arr = tensor.detach().cpu().contiguous().numpy()
        arr = arr.astype(arr.dtype.newbyteorder("<"), copy=False)
        header.append({"name": name, "dtype": str(arr.dtype), "shape": list(arr.shape)})
        blobs.append(arr.tobytes(order="C"))
    head = json.dumps(header, separators=(",", ":")).encode("utf-8")
    return len(head).to_bytes(8, "little") + head + b"".join(blobs)


def deserialize(data: bytes) -> dict:
    import torch

    n = int.from_bytes(data[:8], "little")
    header = json.loads(data[8:8 + n].decode("utf-8"))
    offset = 8 + n
    out = {}
    for h in header:
        dtype = np.dtype(h["dtype"])
        count = int(np.prod(h["shape"])) if h["shape"] else 1
        arr = np.frombuffer(data, dtype=dtype, count=count, offset=offset).reshape(h["shape"])
        offset += count * dtype.itemsize
        out[h["name"]] = torch.from_numpy(arr.copy())
    return out


BatchFn = Callable[[np.ndarray], tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]]


def fit(n_rows: int, batch_fn: BatchFn, y: np.ndarray, n_products: int, n_static: int,
        config: dict, batch_size: int, device: str,
        on_epoch: Callable[[int, float], None] | None = None) -> tuple[object, bytes, str]:
    """Train on rows 0..n_rows-1 of the caller's arrays for M3's 8 epochs. ``batch_fn(rows)``
    returns (sequences, lengths, product codes, static features) for those rows. Returns
    (model, bytes, sha256)."""
    return _train(n_rows, batch_fn, y, n_products, n_static, config, batch_size, device,
                  int(LSTM_FIXED["epochs"]), on_epoch)


def _train(n_rows: int, batch_fn: BatchFn, y: np.ndarray, n_products: int, n_static: int,
           config: dict, batch_size: int, device: str, n_epochs: int,
           on_epoch: Callable[[int, float], None] | None) -> tuple[object, bytes, str]:
    """``fit`` with an explicit epoch count: only the timed probe (one epoch) calls it."""
    import torch

    set_determinism()
    model = build_model(n_products, n_static, int(config["hidden"])).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=float(LSTM_FIXED["lr"]))
    loss_fn = torch.nn.MSELoss()
    gen = torch.Generator().manual_seed(SEED)
    target = torch.as_tensor(np.asarray(y, dtype=np.float32))
    for epoch in range(n_epochs):
        model.train()
        order = torch.randperm(n_rows, generator=gen).numpy()
        total = 0.0
        for lo in range(0, n_rows, batch_size):
            rows = order[lo:lo + batch_size]
            seq, lengths, prod, static = batch_fn(rows)
            pred = model(torch.as_tensor(seq, device=device), torch.as_tensor(lengths),
                         torch.as_tensor(prod, device=device),
                         torch.as_tensor(static, device=device))
            loss = loss_fn(pred, target[rows].to(device))
            opt.zero_grad(set_to_none=True)
            loss.backward()
            opt.step()
            total += float(loss.detach()) * len(rows)
        if on_epoch is not None:
            on_epoch(epoch, total / max(n_rows, 1))
    data = serialize(model.state_dict())
    return model, data, sha256_bytes(data)


def predict(model, n_rows: int, batch_fn: BatchFn, batch_size: int, device: str) -> np.ndarray:  # noqa: ANN001
    import torch

    model.eval()
    out = np.empty(n_rows, dtype=np.float64)
    with torch.no_grad():
        for lo in range(0, n_rows, batch_size):
            rows = np.arange(lo, min(lo + batch_size, n_rows))
            seq, lengths, prod, static = batch_fn(rows)
            pred = model(torch.as_tensor(seq, device=device), torch.as_tensor(lengths),
                         torch.as_tensor(prod, device=device),
                         torch.as_tensor(static, device=device))
            out[lo:lo + len(rows)] = pred.detach().cpu().numpy()
    return out
