"""The result files of one run: <out>/<test>_result.json (series, statistics, exclusions, tables)
and <out>/<test>_units.jsonl (one row per unit candidate: fills, gross, costs, sigma, status)."""

from __future__ import annotations

import json
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any

from base_rules import constants as K
from base_rules.common import RunOutput
from base_rules.h5 import Component
from base_rules.stats import stats_for_test


def result_path(out_dir: Path, test: str) -> Path:
    return Path(out_dir) / f"{test}_result.json"


def units_path(out_dir: Path, test: str) -> Path:
    return Path(out_dir) / f"{test}_units.jsonl"


def per_year_product(rows: list[dict]) -> dict[str, dict[str, int]]:
    out: dict[str, dict[str, int]] = {}
    for r in rows:
        if r.get("status") != "traded":
            continue
        y = r["date"][:4]
        out.setdefault(r["key"], {}).setdefault(y, 0)
        out[r["key"]][y] += 1
    return out


def to_record(out: RunOutput, header: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": K.RESULT_SCHEMA, **header, "test": out.test,
        "stats": stats_for_test(out.test, out.units),
        "series": {c: [[str(d), v] for d, v in s] for c, s in out.units.items()},
        "component": {c: {str(d): v for d, v in sorted(s.items())} for c, s in out.daily.items()},
        "grid_dates": sorted(str(d) for d in out.grid),
        "exclusions": dict(sorted(Counter(out.counters).items())),
        "per_product": {k: dict(v) for k, v in sorted(out.per_product.items())},
        "traded_units_per_key_and_year": per_year_product(out.rows),
        "notes": out.notes,
    }


def write(out: RunOutput, out_dir: Path, header: dict[str, Any]) -> Path:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    with units_path(out_dir, out.test).open("w", encoding="utf-8") as fh:
        for row in out.rows:
            fh.write(json.dumps(row, default=str) + "\n")
    path = result_path(out_dir, out.test)
    path.write_text(json.dumps(to_record(out, header), indent=1, default=str) + "\n",
                    encoding="utf-8")
    return path


def component_from_record(rec: dict) -> Component:
    daily = {c: {date.fromisoformat(d): float(v) for d, v in rec["component"][c].items()}
             for c in K.COST_CASES}
    return Component(rec["test"], daily, frozenset(date.fromisoformat(d)
                                                   for d in rec["grid_dates"]))


__all__ = ["component_from_record", "result_path", "to_record", "units_path", "write"]
