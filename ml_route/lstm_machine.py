"""The LSTM challenger's machine and batch size, recorded before its first fit (review NOTE-5 and
NOTE-11; V7, V10-2, M8's A-1).

V7 runs the LSTM on a CUDA card with no CPU fallback; V10-2 records the machine chosen before the
first fit. So, for training (``ml_route.train fit --challenger lstm``):
- ``require_cuda()``: no CUDA device is refused by name (``LstmMachineRefused``); only
  ``ml_route.probes`` may run the LSTM on the CPU (the E.2b prompt's failure path).
- ``ensure_lstm_machine(route_dir, harness_sha256)``: before the FIRST LSTM fit of the route, runs
  M8's A-1 ladder (``ml_route.probes.a1_step``: 512, 256, 128, 64, the first batch that leaves at
  least 0.5 GB of the card free) on this card and writes ONE record, ``lstm_machine.json`` in the
  route directory, write-once: the host, the GPU name, the card's total VRAM, the A-1 steps and
  the planned batch size. A ladder that fits no batch is refused ("stop to the user", A-1).
  Every LATER fit re-measures A-1 at the recorded batch on the card it runs on and refuses unless
  that card holds it with at least 0.5 GB free; ``check_fit_batch`` refuses a fit whose batch
  size is not the recorded one.
- The card's total VRAM is nvidia-smi's ``memory.total``; on the planned RTX 3050 Laptop GPU
  that is 4096 MiB, M8's "4 GB" (reading R-M1, in the worker report).
The record goes into the route manifest (ml_route.manifest) and the device into every fit record
(ml_route.train).
"""

from __future__ import annotations

import json
import socket
from datetime import UTC, datetime
from pathlib import Path

from ml_route.constants import LSTM_BATCH_LADDER, VRAM_MIN_FREE_GB
from ml_route.inputs import RouteInputMissing

MACHINE_FILE = "lstm_machine.json"
SCHEMA = "ml_route_lstm_machine/1"


class LstmMachineRefused(RouteInputMissing):
    """The LSTM cannot be fitted on this machine as frozen (V7, V10-2, A-1); the case is named."""


def _cuda_available() -> bool:
    import torch

    return bool(torch.cuda.is_available())


def require_cuda() -> None:
    if not _cuda_available():
        raise LstmMachineRefused(
            "REFUSED: torch.cuda.is_available() is False; V7 runs the LSTM on a CUDA card with "
            "no CPU fallback (only ml_route.probes may run it on the CPU)")


def card() -> dict:
    """This machine's host and card: GPU name and total VRAM (nvidia-smi)."""
    import torch

    from ml_route.probes import _nvidia_smi_gpu

    smi = _nvidia_smi_gpu()
    if "total_mib" not in smi:
        raise LstmMachineRefused(f"REFUSED: nvidia-smi cannot report the card: {smi}")
    return {"host": socket.gethostname(), "gpu_name": torch.cuda.get_device_name(0),
            "total_vram_mib": float(smi["total_mib"])}


def a1_step(batch: int, total_mib: float) -> dict:
    from ml_route.lstm import set_determinism
    from ml_route.probes import a1_step as measure

    set_determinism()
    return measure(batch, "cuda", total_mib)


def plan_batch(total_mib: float) -> tuple[int | None, list[dict]]:
    """M8's A-1 ladder on this card: the first batch that leaves 0.5 GB free, and every step."""
    steps = []
    for batch in LSTM_BATCH_LADDER:
        step = a1_step(batch, total_mib)
        steps.append(step)
        if step["leaves_0_5gb_free"]:
            return batch, steps
    return None, steps


def ensure_lstm_machine(route_dir: Path, harness_sha256: str) -> dict:
    """The route's LSTM machine record, written before the first fit and checked by every later
    one (see the module docstring). Returns the record plus this fit's card and A-1 check."""
    require_cuda()
    here = card()
    path = Path(route_dir) / MACHINE_FILE
    if not path.exists():
        batch, steps = plan_batch(here["total_vram_mib"])
        if batch is None:
            raise LstmMachineRefused(
                "REFUSED: M8's A-1 ladder found no batch size that leaves 0.5 GB of the card "
                f"free ({[s['batch'] for s in steps]}); stop to the user")
        record = {"schema": SCHEMA, **here, "batch_size": batch, "a1_steps": steps,
                  "a1_rule": "M8 / A-1: 512 -> 256 -> 128 -> 64, the first batch that leaves "
                             f"at least {VRAM_MIN_FREE_GB} GB of the card free",
                  "harness_sha256": harness_sha256,
                  "recorded_utc": datetime.now(UTC).isoformat(timespec="seconds")}
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("x", encoding="utf-8") as fh:
            fh.write(json.dumps(record, indent=1, sort_keys=True) + "\n")
        return {**record, "this_fit": {**here, "a1_check": steps[-1]}}
    record = json.loads(path.read_text(encoding="utf-8"))
    if record.get("schema") != SCHEMA or not isinstance(record.get("batch_size"), int):
        raise LstmMachineRefused(f"REFUSED: {path} is not an LSTM machine record")
    check = a1_step(int(record["batch_size"]), here["total_vram_mib"])
    if not check["leaves_0_5gb_free"]:
        raise LstmMachineRefused(
            f"REFUSED: this card ({here['gpu_name']} on {here['host']}) does not hold the "
            f"recorded batch {record['batch_size']} with {VRAM_MIN_FREE_GB} GB free by the A-1 "
            f"measure (free {check['free_of_4gb_mib']} MiB of {here['total_vram_mib']:.0f})")
    return {**record, "this_fit": {**here, "a1_check": check}}


def check_fit_batch(record: dict, batch_size: int) -> None:
    if batch_size != record["batch_size"]:
        raise LstmMachineRefused(f"REFUSED: an LSTM fit with batch {batch_size}; the route's "
                                 f"machine record plans {record['batch_size']} (A-1)")


def read_machine_record(route_dir: Path) -> dict | None:
    path = Path(route_dir) / MACHINE_FILE
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


__all__ = ["LstmMachineRefused", "MACHINE_FILE", "card", "check_fit_batch",
           "ensure_lstm_machine", "plan_batch", "read_machine_record", "require_cuda"]
