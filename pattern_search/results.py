"""Result files of the search: reports/stage_e20_search.json (schema "stage_e20_search_result/1"),
reports/stage_e20_search.md and the tables under reports/stage_e20_search/, written atomically."""

from __future__ import annotations

import json
import math
import os
from datetime import date, datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from pattern_search import guard  # noqa: F401  (F3)


def _default(obj: Any) -> Any:
    if isinstance(obj, (date, datetime, pd.Timestamp)):
        return obj.isoformat()
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return None if not math.isfinite(float(obj)) else float(obj)
    if isinstance(obj, np.bool_):
        return bool(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, pd.DataFrame):
        return json.loads(obj.to_json(orient="records", date_format="iso"))
    if isinstance(obj, pd.Series):
        return json.loads(obj.to_json(date_format="iso"))
    if isinstance(obj, (set, frozenset, tuple)):
        return list(obj)
    return str(obj)


def _clean(obj: Any) -> Any:
    """NaN and infinities become null (strict JSON)."""
    if isinstance(obj, float):
        return obj if math.isfinite(obj) else None
    if isinstance(obj, dict):
        return {str(k): _clean(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_clean(v) for v in obj]
    return obj


def write_atomic(path: Path, raw: bytes) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    with tmp.open("wb") as fh:
        fh.write(raw)
        fh.flush()
        os.fsync(fh.fileno())
    tmp.replace(path)
    return path


def to_json_bytes(doc: dict[str, Any]) -> bytes:
    text = json.dumps(_clean(json.loads(json.dumps(doc, default=_default))), indent=1,
                      allow_nan=False)
    return (text + "\n").encode()


def write_json(path: Path, doc: dict[str, Any]) -> Path:
    return write_atomic(path, to_json_bytes(doc))


def write_csv(path: Path, frame: pd.DataFrame) -> Path:
    return write_atomic(path, frame.to_csv(index=True).encode())


def _fmt(x: Any, nd: int = 3) -> str:
    if x is None:
        return "n/a"
    if isinstance(x, float):
        return "n/a" if not math.isfinite(x) else f"{x:.{nd}f}"
    return str(x)


def summary_md(doc: dict[str, Any]) -> str:
    sc = doc.get("screen") or {}
    items = sc.get("items") or {}
    lines = ["# Stage E.20 Part C search: result", "",
             f"Written {doc.get('written_local')} (PDT). World: {doc.get('world_source')}. "
             f"Freeze manifest sha256 {str(doc.get('freeze_sha256'))[:12]}...", "",
             f"## SCREEN: {sc.get('verdict')}", ""]
    if sc.get("reason"):
        lines += [f"Reason: {sc['reason']}", ""]
    if items:
        lines += ["| Item | Value | Bar | Passes |", "|---|---|---|---|"]
        for name, it in items.items():
            lines.append(f"| {name} | {_fmt(it.get('value', it.get('config_id')))} | "
                         f"{it.get('bar', 'a configuration')} | {it.get('passes')} |")
        lines.append("")
    if sc.get("leakage_alarm"):
        lines += ["Leakage alarm: annualized Sharpe above 4.0. The screen fails as written; the "
                  "independent FableLeakageAudit runs for the record (plan 9 item 3).", ""]
    rep = doc.get("reported") or {}
    dsr = rep.get("dsr") or {}
    fin = (rep.get("oos") or {}).get("final") or {}
    lines += ["## Reported, not gating", "",
              f"- DSR at N = {dsr.get('n_trials')}: {_fmt(dsr.get('deflated_sharpe_ratio'))} "
              f"(status {dsr.get('status')})",
              f"- Final configuration: {fin.get('config_id')} ({fin.get('registry_id')})",
              f"- t4 share of its CPCV OOS net P&L: {_fmt(fin.get('t4_share'))}; r_ROD share: "
              f"{_fmt(fin.get('rod_share'))} (P&L fitted "
              f"{_fmt(fin.get('pnl_total_15_splits_usd'), 2)}"
              f", rod zeroed {_fmt(fin.get('pnl_rod_zeroed_15_splits_usd'), 2)})",
              f"- Ruin probability: {rep.get('ruin', {}).get('status')}",
              f"- Per-configuration table: {doc.get('tables', {}).get('configs')}",
              f"- Per-product round trips: {doc.get('tables', {}).get('round_trips')}", ""]
    lines += ["## Stages", "", "| Stage | Status | Wall s | Peak RSS MB |", "|---|---|---|---|"]
    for st in doc.get("stages", []):
        lines.append(f"| {st['name']} | {st['status']} | {_fmt(st['wall_s'], 1)} | "
                     f"{_fmt(st.get('peak_rss_mb'), 0)} |")
    return "\n".join(lines) + "\n"


__all__ = ["summary_md", "to_json_bytes", "write_atomic", "write_csv", "write_json"]
