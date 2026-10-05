"""A synthetic E.12-like phase-1 state for test C1's q_m1 tests. Nothing here is market data.

``make_state(base)`` builds, in a temp dir, what E.12's phase-1 steps left on disk, with the
frozen code itself: a panel (tests.test_ml_v2_cpcv.make_panel's synthetic frame, held in a real
ml_route_v2.panel.Panel; ``make_pipeline_state``: the frozen synthetic pipeline's panel,
synthetic_universe -> build_world_panel -> _filter, with every real signal column) saved as the
two stage files under the current constants fingerprint
(pipeline._save, the format load_build reads), phase1_build.json, Gate 0's family B run by the
frozen gate0.gate0_b_trades (it fits the 45 OOF splits ONCE and writes them and gate0B_meta.json),
an E.12-shaped Gate 0 report and list (the NG h60 and hF rows from that run), a registered ledger
and the state manifest.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

from c1_replication.constants import STATE_MANIFEST_SCHEMA
from ml_route_v2.configs import ConfigLedger
from ml_route_v2.fingerprint import constants_fingerprint
from ml_route_v2.gate0 import _b_test, family_b_id, gate0_b_trades
from ml_route_v2.panel import Panel
from ml_route_v2.phase1.build import _input_fingerprint
from ml_route_v2.pipeline import _save
from tests.test_ml_v2_cpcv import make_panel

ROOTS = ("NG", "MNQ", "ZN")
HORIZONS = ("h60", "h120", "hF")


@dataclass(frozen=True)
class SyntheticState:
    state: Path
    manifest: Path
    ledger: Path
    report: Path
    report_sha: str
    listed: Path
    listed_sha: str
    panel: Panel
    admissible: tuple[tuple[str, str], ...]
    calendar: tuple[date, ...]


def sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def synthetic_panel(seed: int = 7, n_dates: int = 150) -> Panel:
    fp = make_panel(n_dates=n_dates, roots=ROOTS, n_signals=3, seed=seed, edge=0.3,
                    first=date(2019, 5, 6))
    frame = fp.frame.copy()
    ng = frame["root"].to_numpy(object) == "NG"
    # s2 never applies on NG rows (a signal "not live" on NG, for the C10 reference counts)
    frame.loc[ng, "app_s2"] = 0.0
    frame.loc[ng, "z_s2"] = 0.0
    return Panel(frame, tuple(fp.feature_cols), tuple(fp.signal_names), tuple(fp.horizons),
                 np.asarray(fp.avail_max_ts_ns), {})


def write_manifest(state: Path, path: Path) -> Path:
    files = {p.relative_to(state).as_posix(): {"bytes": p.stat().st_size, "sha256": sha(p)}
             for p in sorted(state.rglob("*")) if p.is_file()}
    path.write_text(json.dumps({"schema": STATE_MANIFEST_SCHEMA, "files": files}, indent=1))
    return path


def make_state(base: Path, *, seed: int = 7) -> SyntheticState:
    """A state from tests.test_ml_v2_cpcv.make_panel's synthetic frame (fast)."""
    panel = synthetic_panel(seed)
    calendar = tuple(sorted(set(pd.to_datetime(panel.frame["trade_date"]).dt.date)))
    adm = tuple((r, h) for r in sorted(ROOTS) for h in HORIZONS)
    return _write_state(base, panel, calendar, ROOTS,
                        {"c_sigma": None, "risk": None, "admissible": adm})


def make_pipeline_state(base: Path, *, seed: int = 4) -> SyntheticState:
    """A state from the frozen synthetic pipeline: synthetic_universe(("NG",)) ->
    pipeline.build_world_panel (every signal of the registry, real feature columns) ->
    pipeline._filter (the c/sigma admissible pairs), as phase1's build stages."""
    from ml_route_v2.pipeline import _filter, build_world_panel
    from ml_route_v2.synthetic import synthetic_universe

    world = synthetic_universe(("NG",), date(2021, 3, 1), date(2021, 7, 30), seed=seed,
                               eager_frames=False)
    panel = build_world_panel(world)
    return _write_state(base, panel, tuple(world.calendar), ("NG",), _filter(panel))


def _write_state(base: Path, panel: Panel, calendar: tuple, vehicles: tuple,
                 filt: dict) -> SyntheticState:
    state = base / "state"
    adm = tuple(tuple(map(str, p)) for p in filt["admissible"])
    inputs = {"synthetic": True}
    out = {"panel": panel, "calendar": calendar, "vehicles": vehicles, "requested": vehicles,
           "inputs": inputs, "input_fingerprint": _input_fingerprint(panel, inputs)}
    const = constants_fingerprint()
    _save(state / "stages" / "phase1_panel.pkl", {"constants": const, "out": out})
    _save(state / "stages" / "phase1_filter.pkl", {"constants": const, "out": filt})
    (state / "phase1_build.json").write_text(json.dumps({"synthetic": True}))
    ledger = base / "ml_ledger.jsonl"
    trades = gate0_b_trades(panel, ledger=ConfigLedger(ledger), state_dir=state / "gate0",
                            admissible=adm, calendar=list(calendar))
    rows = []
    for h in ("h60", "hF"):
        tid = family_b_id("NG", h)
        sub = trades.loc[trades["test_id"] == tid]
        t = _b_test(tid, "NG", h, sub, int(sub["n_pair_rows"].iloc[0]))
        rows.append({"test_id": tid, "family": "B", "root": "NG", "horizon": h,
                     "n_trades": t.n_trades, "n_dates": t.n_dates, "n_obs": t.n_obs,
                     "mean": t.mean, "mean_gross_ticks": t.mean, "t": t.t, "t_B": t.t,
                     "p": t.p, "cost_ticks": t.cost_ticks})
    listed = base / "gate0_list.json"
    listed.write_text(json.dumps({"covered_signals": list(panel.signal_names),
                                  "admissible_pairs": [list(p) for p in adm]}))
    meta = json.loads((state / "gate0" / "gate0B_meta.json").read_text())
    report = base / "gate0_report.json"
    report.write_text(json.dumps({
        "tests": rows, "list_sha256": sha(listed),
        "fingerprints": {"constants": const, "inputs": out["input_fingerprint"],
                         "gate0_b_state": meta["fingerprint"]}}))
    manifest = write_manifest(state, base / "state_manifest.json")
    return SyntheticState(state, manifest, ledger, report, sha(report), listed, sha(listed),
                          panel, adm, calendar)


def rewrite_report(st: SyntheticState, edit: dict) -> tuple[Path, str]:
    """The report with ``edit`` = {horizon: {key: value}} applied to the NG rows."""
    doc = json.loads(st.report.read_text())
    for row in doc["tests"]:
        row.update(edit.get(row["horizon"], {}))
    path = st.report.with_name("gate0_report_edited.json")
    path.write_text(json.dumps(doc))
    return path, sha(path)
