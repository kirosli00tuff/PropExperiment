"""The runtime probe (Stage E.16 Task 3): SYNTHETIC stores at full 2010-2024 scale, the five runners
end to end through the E.17 command line, wall time and peak RSS per test. No market data.

    uv run python -m base_rules.probe build --dir ~/.cache/propexp_e16_probe --settlement ... \
        --windows ... --ecauc ... --livestock <file>
    uv run python -m base_rules.probe run --dir ~/.cache/propexp_e16_probe   (each test under
        /usr/bin/time -v, H5 last)
    uv run python -m base_rules.probe clean --dir ~/.cache/propexp_e16_probe

``build`` writes, one product at a time (memory), each product's ext2010 store (trade dates
2010-06-07..2019-04-30) and step 2 store (2019-05-06..2024-02-29) in the real layouts with the
frozen read-only writer: one-minute bars over every open interval of the product's calendars (the
real hist calendars, the real 2019-on calendars, the livestock file given), a tick random walk,
quarterly-or-cycle rolls at 00:00 UTC of estimated splice dates; then a run manifest, a probe
freeze manifest (the real settlement, windows and EC-AUC inputs, the given livestock calendar, this
code) and a temporary trial registry holding the five ids. Nothing is written under the repo.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time as _time
from datetime import UTC, date, datetime
from pathlib import Path

import numpy as np
import pandas as pd

from base_rules import constants as K
from base_rules import guards as G
from base_rules import hist_plan as HP
from base_rules.calendars import GroupCalendars, load_hist
from base_rules.context import empty_release_rules, make_context
from base_rules.counts import estimated_splices
from base_rules.inputs import load_settlement, load_windows
from base_rules.store import EXT2010, STEP2_ERA, step2_name
from data.group_session import load_group_calendar, open_intervals
from data.stage_e_bars import book_trade_dates
from rules.products import PRICE_SCALE, product

NS_MIN = 60_000_000_000
ERA_DATES = {EXT2010: (K.PROMPT_FIRST, K.HIST_LAST), STEP2_ERA: (K.STEP2_FIRST, K.WINDOW_LAST)}


def _minutes(cal, first: date, last: date) -> np.ndarray:  # noqa: ANN001
    opened = open_intervals(cal, first, last)
    parts = [np.arange(lo, hi, NS_MIN, dtype=np.int64)
             for lo, hi in zip(opened.starts.tolist(), opened.ends.tolist(), strict=True)]
    return np.concatenate(parts) if parts else np.zeros(0, dtype=np.int64)


def era_frame(root: str, cal, era: str, splices_ns: list[int], seed: int  # noqa: ANN001
              ) -> pd.DataFrame:
    first, last = ERA_DATES[era]
    ts = _minutes(cal, first, last)
    booked = book_trade_dates(cal, ts)
    unsourced = getattr(cal, "unsourced", frozenset())
    keep = np.array([d is not None and first <= d <= last and d not in unsourced
                     for d in booked], dtype=bool)
    ts = ts[keep]
    labels = pd.Categorical([str(d) for d, k in zip(booked, keep, strict=True) if k])
    rng = np.random.default_rng(seed)
    steps = rng.integers(-2, 3, size=len(ts)).astype(np.int64)
    close = 200_000 + np.cumsum(steps)
    open_ = np.concatenate([[close[0]], close[:-1]]) if len(close) else close
    tick = product(root).vendor_tick_fixed / PRICE_SCALE
    contract = np.searchsorted(np.array(sorted(splices_ns), dtype=np.int64), ts, side="right")
    sym = pd.Categorical.from_codes(contract, [f"{root}R{k}" for k in range(len(splices_ns) + 1)])
    return pd.DataFrame({
        "ts_event": ts, "open": open_ * tick, "high": np.maximum(open_, close) * tick,
        "low": np.minimum(open_, close) * tick, "close": close * tick,
        "volume": np.ones(len(ts), dtype=np.int64), "instrument_id": contract.astype(np.int64),
        "raw_symbol": sym, "trade_date": labels, "in_flatten_window": False,
        "in_no_new_positions_window": False, "early_halt_ct": "", "in_scheduled_closure": False,
        "is_roll_session": False, "gap_before_minutes": 0, "vendor_degraded_day": False})


def build(a: argparse.Namespace) -> int:
    from data.build_mes_bars import _write_read_only_parquet

    base = Path(a.dir).expanduser()
    base.mkdir(parents=True, exist_ok=True)
    livestock = Path(a.livestock)
    cals = {g: GroupCalendars(g, load_hist(g, livestock_path=livestock), load_group_calendar(g))
            for g in sorted(set(K.GROUP_OF.values()))}
    st, windows = load_settlement(Path(a.settlement)), load_windows(Path(a.windows))
    ctx = make_context(cals, st, windows, lambda p: None, (), empty_release_rules())
    stores, t0 = {}, _time.time()
    for k, p in enumerate(K.PRODUCTS):
        g = cals[K.GROUP_OF[p]]
        splices = [int(datetime(d.year, d.month, d.day, tzinfo=UTC).timestamp()) * 10**9
                   for d in estimated_splices(ctx, p)]
        refs = {}
        cut = int(datetime(2019, 5, 1, tzinfo=UTC).timestamp()) * 10**9  # each roll in one store
        first = int(datetime(2010, 6, 7, tzinfo=UTC).timestamp()) * 10**9
        plan = K.HIST_PLAN_OF[p]
        for era, cal in ((EXT2010, g.hist), (STEP2_ERA, g.frozen)):
            out = (base / "stores" / plan / p / HP.expected_name(p, plan, *ERA_DATES[era])
                   if era == EXT2010 else base / "stores" / "step2" / p / step2_name(p))
            rolls = [{"ts_ns": s, "date": str(datetime.fromtimestamp(s / 1e9, UTC).date())}
                     for s in splices if (first < s < cut if era == EXT2010 else s >= cut)]
            if not out.exists():
                frame = era_frame(p, cal, era, splices, seed=1000 + k)
                meta = {"plan": plan if era == EXT2010 else "step2", "rolls": rolls,
                        "hist_calendar": {"sha256": getattr(cal, "file_sha256", None)},
                        "trade_date_range": [str(frame["trade_date"].astype(str).min()),
                                             str(frame["trade_date"].astype(str).max())],
                        "note": "SYNTHETIC probe store (Stage E.16 Task 3)"}
                _write_read_only_parquet(frame, out, meta)
                del frame
            refs[era] = {"path": str(out), "sha256": G.sha256_file(out),
                         **({"plan": plan} if era == EXT2010 else {})}
        stores[p] = refs
        print(f"{p}: built ({_time.time() - t0:.0f} s)", flush=True)
    manifest = base / "run_manifest.json"
    manifest.write_text(json.dumps({"schema": K.RUN_MANIFEST_SCHEMA, "stores": stores}, indent=1))
    inputs = {**{r: str(K.repo_path(p)) for r, p in G.INPUT_ROLES.items()},
              "settlement": str(Path(a.settlement).resolve()),
              "windows": str(Path(a.windows).resolve()), "ecauc_hist": str(Path(a.ecauc).resolve()),
              "livestock_hist": str(Path(a.livestock).resolve()),
              "ecauc_announcements": str(Path(a.announcements).resolve())}
    stub = {K.PLAN_EXT: [str(d) for d in ERA_DATES[EXT2010]]}  # harness v10 has no ext2010h
    (base / "input_paths.json").write_text(json.dumps({**inputs, "plan_windows": stub}, indent=1))
    print(f"built in {_time.time() - t0:.0f} s -> {base}")
    return 0


def write_freeze(base: Path) -> Path:
    """A probe freeze in the lead's format (this code and the inputs) and a fresh temporary
    registry holding the five ids: written at every ``run``, never under the repo."""
    from screening.trial_registry import init_registry, register

    inputs = {k: v for k, v in json.loads((base / "input_paths.json").read_text()).items()
              if k in G.INPUT_ROLES}
    fpath = base / "freeze_probe.json"
    fpath.write_text(json.dumps(G.manifest_body([*G.code_files(),
                                                 *(Path(p) for p in inputs.values())]), indent=1))
    registry = base / "registry.jsonl"
    registry.unlink(missing_ok=True)
    init_registry(registry)
    register(K.REGISTRY_TEST, list(K.TEST_IDS.values()), fpath, G.sha256_file(fpath), "a" * 64,
             path=registry, note="SYNTHETIC probe registry, never the ledger")
    return fpath


def _time_v(cmd: list[str], log: Path) -> dict:
    t0 = _time.time()
    with log.open("w") as fh:
        rc = subprocess.run(["/usr/bin/time", "-v", "nice", "-n", "10", *cmd], stdout=fh,
                            stderr=subprocess.STDOUT, check=False,
                            env={**os.environ, "OMP_NUM_THREADS": "4"}).returncode
    text = log.read_text()
    rss = re.search(r"Maximum resident set size \(kbytes\): (\d+)", text)
    wall = re.search(r"Elapsed \(wall clock\) time \(h:mm:ss or m:ss\): ([\d:.]+)", text)
    return {"rc": rc, "wall_clock": wall.group(1) if wall else None,
            "wall_s_measured": round(_time.time() - t0, 1),
            "peak_rss_mb": round(int(rss.group(1)) / 1024, 1) if rss else None}


def run(a: argparse.Namespace) -> int:
    base = Path(a.dir).expanduser()
    fpath, manifest = write_freeze(base), base / "run_manifest.json"
    out = {}
    for test in K.TESTS:
        cmd = [sys.executable, "-m", "base_rules.run", "run", "--test", test,
               "--freeze", str(fpath), "--freeze-sha256", G.sha256_file(fpath),
               "--out-dir", str(base / "runs"), "--registry", str(base / "registry.jsonl"),
               "--input-paths", str(base / "input_paths.json")]
        if test != "H5":
            cmd += ["--manifest", str(manifest), "--manifest-sha256", G.sha256_file(manifest)]
        out[test] = _time_v(cmd, base / f"time_{test}.log")
        res = json.loads((base / "runs" / f"{test}_result.json").read_text())
        out[test]["status"] = res.get("status")
        out[test]["n_units_base"] = (res.get("stats") or {}).get("base", {}).get("n")
        out[test]["exclusions"] = res.get("exclusions")
        out[test]["error"] = res.get("error")
        print(test, {k: v for k, v in out[test].items() if k != "exclusions"}, flush=True)
    (base / "probe_result.json").write_text(json.dumps(out, indent=1, default=str))
    return 0


def clean(a: argparse.Namespace) -> int:
    base = Path(a.dir).expanduser()
    for p in base.rglob("*"):
        if p.is_file():
            p.chmod(0o644)
    shutil.rmtree(base / "stores", ignore_errors=True)
    print(f"stores removed under {base}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="base_rules.probe")
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    for name in ("--dir", "--settlement", "--windows", "--ecauc", "--announcements",
                 "--livestock"):
        b.add_argument(name, required=True)
    for name in ("run", "clean"):
        sub.add_parser(name).add_argument("--dir", required=True)
    a = ap.parse_args(argv)
    return {"build": build, "run": run, "clean": clean}[a.cmd](a)


if __name__ == "__main__":
    raise SystemExit(main())
