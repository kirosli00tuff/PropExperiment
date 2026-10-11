"""Result writing: canonical JSON (NaN -> null, +-inf -> "inf"/"-inf", dates and numpy scalars to
Python), atomic writes, and the short Markdown summary of the result."""

from __future__ import annotations

import json
import math
import os
from collections.abc import Mapping
from datetime import date, datetime
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np


def clean(value: Any) -> Any:  # noqa: ANN401 - any JSON-able tree
    if isinstance(value, Mapping):
        return {str(k): clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        items = sorted(value) if isinstance(value, (set, frozenset)) else value
        return [clean(v) for v in items]
    if isinstance(value, (bool, np.bool_)):
        return bool(value)
    if isinstance(value, (int, np.integer)):
        return int(value)
    if isinstance(value, Fraction):
        return clean(float(value))
    if isinstance(value, (float, np.floating)):
        f = float(value)
        if math.isnan(f):
            return None
        if math.isinf(f):
            return "inf" if f > 0 else "-inf"
        return f
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value


def write_atomic(path: Path, data: bytes) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    with tmp.open("wb") as fh:
        fh.write(data)
        fh.flush()
        os.fsync(fh.fileno())
    tmp.replace(path)


def write_json(path: Path, doc: Any) -> None:  # noqa: ANN401
    write_atomic(path, (json.dumps(clean(doc), indent=1, sort_keys=True, allow_nan=False)
                        + "\n").encode())


def _f(x: Any, nd: int = 3) -> str:  # noqa: ANN401
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "n/a"
    return f"{x:.{nd}f}" if isinstance(x, float) else str(x)


def summary_md(doc: Mapping[str, Any]) -> str:
    """The result's short human summary (the JSON is the record)."""
    lines = [f"# Stage E.20 H6 result ({doc.get('written_local', '')})", "",
             f"Registration {doc.get('registration', {}).get('entry_id')}; freeze "
             f"{str(doc.get('freeze', {}).get('sha256', ''))[:12]}...; harness "
             f"{str(doc.get('harness_sha256', ''))[:12]}...", "",
             "## Verdict window 2020-06-01..2024-02-29", "",
             "| test | verdict | trades | t_B | p | Holm | mean gross | 1.5 x mean c | "
             "Sharpe |", "|---|---|---|---|---|---|---|---|---|"]
    holm = doc.get("holm", {}).get("rejected", {})
    for test, rec in doc.get("tests", {}).items():
        if rec.get("status") == "STOPPED":
            lines.append(f"| {test} | STOPPED | | | | | | | |")
            continue
        lines.append(
            f"| {test} | {rec['pass_bar']['verdict']} | {rec['n_trades']} | {_f(rec['t_b'])} | "
            f"{_f(rec['p_one_sided'], 4)} | {holm.get(test)} | {_f(rec['mean_gross_ticks'])} | "
            f"{_f(1.5 * rec['mean_cost_ticks'])} | {_f(rec['annualized_net_sharpe'])} |")
    lines += ["", "## Overlap 2019-05-06..2020-05-29 (descriptive, never in the verdict)", "",
              "| test | trades | t_B | mean net ticks | Sharpe |", "|---|---|---|---|---|"]
    for test, rec in doc.get("overlap", {}).items():
        if rec.get("status") == "STOPPED":
            lines.append(f"| {test} | STOPPED | | | |")
            continue
        lines.append(f"| {test} | {rec['n_trades']} | {_f(rec['t_b'])} | "
                     f"{_f(rec['mean_net_ticks'])} | {_f(rec['annualized_net_sharpe'])} |")
    lines += ["", "Every number is in the JSON beside this file (per-trade rows, exclusions, "
              "refusals, exit types, MLL breaches, per-year and stress blocks).", ""]
    return "\n".join(lines)


__all__ = ["clean", "summary_md", "write_atomic", "write_json"]
