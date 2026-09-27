"""The two challengers behind one interface for ml_route.train (fit, predict, usable rows).

LgbmAdapter: the design matrix (F1-F17 plus one-hot F18 per product with rows and F19 per
cluster) is built once per row table.
LstmAdapter: per product 5-minute bars (a second read of the step 2 store, same allowlist), the
per-row sequence index for each lookback, and the static inputs (F1-F17 and the F19 one-hot).
Its usable rows are the complete rows whose 72-step sequence is fully defined (the 24-step
sequence is its suffix), so all four LSTM configurations of a horizon score the same rows
(reading in the worker report). For training, ``adapter_for`` takes the device and the batch
size from the route's LSTM machine record (ml_route.lstm_machine, review NOTE-5 and NOTE-11):
CUDA is required (no silent CPU fallback, V7), the record is written before the first LSTM fit
with M8's A-1 batch on that card, and every later fit refuses unless the card holds the recorded
batch with 0.5 GB free and the fit uses that batch. ``PROBES_PATH`` is E.2b's probe file (the
manifest records it).
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

from data.config import REPO_ROOT
from ml_route.constants import CLUSTER_IDS
from ml_route.inputs import RouteInputMissing, RouteInputs

PROBES_PATH = REPO_ROOT / "reports" / "stage_e2b_ml_probes.json"


class LgbmAdapter:
    challenger = "lgbm"
    device = "cpu"  # LightGBM runs on the CPU (M3, M8); recorded in every fit record

    def __init__(self) -> None:
        from ml_route import lgbm

        self.m = lgbm
        self.design: np.ndarray | None = None
        self.names: list[str] = []

    def grid(self) -> list[dict]:
        return self.m.grid()

    def config_id(self, config: dict) -> str:
        return self.m.config_id(config)

    def attach(self, table) -> None:  # noqa: ANN001 - RowTable
        products = sorted(set(table.product.astype(str)))
        self.design, self.names = self.m.design_matrix(table.X, table.product, table.cluster,
                                                       products)

    def usable_rows(self, table, horizon: str) -> np.ndarray:  # noqa: ANN001
        return table.complete_mask(horizon)

    def fit(self, table, rows: np.ndarray, config: dict, horizon: str):  # noqa: ANN001, ANN201
        return self.m.fit(self.design[rows], table.y[horizon][rows], self.names, config)

    def predict(self, model, table, rows: np.ndarray, config: dict) -> np.ndarray:  # noqa: ANN001
        return self.m.predict(model, self.design[rows])


class LstmAdapter:
    challenger = "lstm"

    def __init__(self, store_root: Path | None, inputs: RouteInputs, batch_size: int,
                 device: str, five_min: dict | None = None, machine: dict | None = None
                 ) -> None:
        """``batch_size`` and ``device`` are explicit (no fallback); for training they come from
        the route's LSTM machine record (``machine``), see ``adapter_for``."""
        from ml_route import lstm

        self.m = lstm
        self.store_root = store_root
        self.inputs = inputs
        self.five_min = five_min
        self.machine = machine
        if machine is not None and device != "cuda":
            raise RouteInputMissing(f"REFUSED: an LSTM training fit on {device!r}; V7 plans no "
                                    "CPU fallback")
        self.device = device
        self.batch_size = int(batch_size)
        self.index: dict[int, tuple[np.ndarray, np.ndarray]] = {}

    def grid(self) -> list[dict]:
        return self.m.grid()

    def config_id(self, config: dict) -> str:
        return self.m.config_id(config)

    def attach(self, table) -> None:  # noqa: ANN001
        from ml_route.lstm_data import sequence_index, steps_defined

        if self.five_min is None:
            self.five_min = five_minute_store(self.store_root, self.inputs)
        self.products = sorted(set(table.product.astype(str)))
        self.code = np.searchsorted(self.products, table.product.astype(str)).astype(np.int64)
        onehot_k = np.stack([(table.cluster.astype(str) == k) for k in CLUSTER_IDS], axis=1)
        self.static = np.hstack([table.X, onehot_k]).astype(np.float32)
        self.sigma = table.sigma
        self.defined = np.zeros(len(table), dtype=bool)
        for lookback in (24, 72):
            end = np.full(len(table), -1, dtype=np.int64)
            length = np.zeros(len(table), dtype=np.int64)
            for p in self.products:
                rows = np.flatnonzero(table.product.astype(str) == p)
                idx = sequence_index(self.five_min[p], table.day[rows], table.t_ns[rows], lookback)
                end[rows], length[rows] = idx.end, idx.length
                if lookback == 72:
                    self.defined[rows] = steps_defined(self.five_min[p], idx)
            self.index[lookback] = (end, length)

    def usable_rows(self, table, horizon: str) -> np.ndarray:  # noqa: ANN001
        return table.complete_mask(horizon) & self.defined

    def batch_fn(self, rows_global: np.ndarray, lookback: int):  # noqa: ANN201
        from ml_route.lstm_data import SequenceIndex, gather

        end, length = self.index[lookback]

        def fn(r: np.ndarray):  # noqa: ANN202
            g = rows_global[r]
            seq = np.zeros((len(g), lookback, 3), dtype=np.float32)
            lens = np.zeros(len(g), dtype=np.int64)
            codes = self.code[g]
            for c in np.unique(codes):
                sel = np.flatnonzero(codes == c)
                fb = self.five_min[self.products[int(c)]]
                s, ln = gather(fb, SequenceIndex(end, length), g[sel], self.sigma, lookback)
                seq[sel], lens[sel] = s, ln
            return seq, lens, codes, self.static[g]

        return fn

    def fit(self, table, rows: np.ndarray, config: dict, horizon: str):  # noqa: ANN001, ANN201
        if self.machine is not None:
            from ml_route.lstm_machine import check_fit_batch

            check_fit_batch(self.machine, self.batch_size)
        fn = self.batch_fn(rows, int(config["lookback"]))
        return self.m.fit(len(rows), fn, table.y[horizon][rows], len(self.products),
                          self.static.shape[1], config, self.batch_size, self.device)

    def predict(self, model, table, rows: np.ndarray, config: dict) -> np.ndarray:  # noqa: ANN001
        fn = self.batch_fn(rows, int(config["lookback"]))
        return self.m.predict(model, len(rows), fn, self.batch_size, self.device)


def five_minute_store(store_root: Path, inputs: RouteInputs) -> dict:
    from ml_route.dataset import bars_from_store, pinned_store_sha256
    from ml_route.lstm_data import five_minute_bars
    from ml_route.store import read_product_bars

    out = {}
    for root in inputs.traded():
        pb = read_product_bars(store_root, root, inputs.s_x[root],
                               expected_sha256=pinned_store_sha256(inputs, root))
        out[root] = five_minute_bars(bars_from_store(pb),
                                     inputs.products[root].vehicle_ticks_per_vendor_unit)
    return out


def adapter_for(challenger: str, store_root: Path, inputs: RouteInputs,  # noqa: ANN201
                route_dir: Path, harness_sha256: str):
    """The training adapter. The LSTM's device and batch come from the route's machine record,
    written before its first fit (ml_route.lstm_machine); no CUDA is refused by name."""
    if challenger == "lgbm":
        return LgbmAdapter()
    if challenger == "lstm":
        from ml_route.lstm_machine import ensure_lstm_machine

        machine = ensure_lstm_machine(Path(route_dir), harness_sha256)
        return LstmAdapter(Path(store_root), inputs, batch_size=int(machine["batch_size"]),
                           device="cuda", machine=machine)
    raise ValueError(f"unknown challenger {challenger!r}")
