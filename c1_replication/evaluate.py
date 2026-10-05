"""Test C1, part 2: the single replication run (a later session, under the freeze, once).

    python -m c1_replication.evaluate --harness-sha256 <sha> \
        --freeze reports/stage_e14_prereg_C1.md --freeze-sha256 <sha> \
        --model reports/stage_e14_c1_model.json --model-sha256 <sha> --model-dir <dir> \
        --store-hashes <json> --calendar-hashes <json> --out reports/stage_e14_c1_result.json

Preconditions (``preconditions``; each refused with NOTHING written, no bar read, exit 2):
the harness preflight; neither the run-once marker reports/stage_e14_c1_RUN_ONCE.json nor --out
exists; the freeze file's sha256; the trial registry holds C1-T1 and C1-T2 registered together
under that freeze sha256; the v2 freeze (every ml_route_v2 file is E.12's); E.12's Gate 0 list
(its covered signals are the panel's signals); the model JSON (pinned sha256; its q, M1 payload
sha256s, feature_cols and signals) and each M1 payload file in --model-dir; the expected
feature_cols (derived from the signals as panel.build_panel derives them) equal the model's (C11);
the six ext2010 stores exist and hash to --store-hashes; the six hist calendars, the release file
and the energy full sessions hash to --calendar-hashes and parse (c1_replication.tables); ruling
C12's share of unsourced dates (calendars only, c1_replication.exclusions) is at most 2%; the
decision clock on every NG candidate date is the frozen energy clock (08:30, 10:30, 13:00 CT) and
NG's day session in every hist energy SessionSpec is D6's.

Then the marker is written, BEFORE any bar is read. From there every stop gives verdict STOPPED
with its reason, written to --out (a stop closes the registered attempt; it is never rerun):
1. World and panel inside c1_replication.context.hist_tables: the six legs through
   data.hist_bars.load_hist_leg (pinned sha256, the pinned hist calendar), c1_replication.world;
   pipeline.build_world_panel(world, check_grid=False, signals=E.12's covered signals) (NG rows
   only, per-product causal z-scores as normalize.py does).
2. Guards: C11, the panel's feature_cols equal the model's (names and order); C10, per covered
   signal and horizon the count of NG ok rows where it applies (counts only), stop if a signal
   with a non-zero E.12 reference count applies on no row.
3. Trades per test (T1 = NG h60, T2 = NG hF): r_hat = models.predict(M1_h, X) on the ok rows of
   h; trade sign(r_hat) iff |r_hat| >= q_h, one contract; g = side x y_gross_h; cost =
   cost_long_h or cost_short_h by side (all V2.2 exclusions applied by the frozen clock and
   targets).
4. Statistic (gate0._b_test, the frozen code): per-date mean, t_B, one-sided p with n_dates - 1
   df, mean cost of the sides taken. A test passes iff mean g >= 1.5 x c AND p <= 0.025 AND
   n_trades >= 30 (all inclusive; a NaN never passes). PASS iff T1 or T2 passes, else FAIL.
5. --out: the verdict first, then the descriptive outputs (C14: the 1.5x slippage case,
   commission + 1.5 x the slippage part, as portfolio._trade_cost_ticks; C15: the share of rows at
   or above q, the long/short split, trades per year), every input hash, the patch record and
   trades_sha256. No price is written.
"""

from __future__ import annotations

import argparse
import gc
import hashlib
import json
import math
import sys
from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from c1_replication.constants import (
    ALPHA_ONE_SIDED,
    COST_MULTIPLE,
    E12_GATE0_LIST,
    E12_GATE0_LIST_SHA256,
    FAIL,
    FREEZE_PATH,
    HORIZON_OF,
    MARKER_PATH,
    MARKER_SCHEMA,
    MIN_TRADES,
    MODEL_SCHEMA,
    PASS,
    PLAN,
    RC_REFUSED,
    RESULT_SCHEMA,
    STOPPED,
    STORE_ROOTS,
    TEST,
    TEST_IDS,
    V2_FREEZE_MANIFEST,
    V2_FREEZE_SHA256,
    VEHICLE,
    WINDOW_FIRST,
    WINDOW_LAST,
)
from c1_replication.guards import C1Refused, C1Stop, file_sha256, pinned_file, verify_v2

CALENDAR_HASHES_SCHEMA = "stage_e14_c1_calendar_hashes/1"
STORE_HASHES_SCHEMA = "stage_e14_c1_store_hashes/1"
HIST_GROUPS = ("equity", "rates", "fx", "energy", "metals", "grains")
_HEX = frozenset("0123456789abcdef")


class C1GuardStop(C1Stop):
    """A guard after the marker (C10, C11): the attempt is closed with verdict STOPPED."""

    def __init__(self, message: str, record: Mapping[str, Any] | None = None) -> None:
        super().__init__(message)
        self.record = dict(record or {})


def _is_sha(value: Any) -> bool:  # noqa: ANN401
    return isinstance(value, str) and len(value) == 64 and set(value) <= _HEX


def _now() -> str:
    from ml_route_v2.phase1._io import now_local

    return now_local()


def _rel(path: Path) -> str:
    from data.config import REPO_ROOT

    p = Path(path).resolve()
    return str(p.relative_to(REPO_ROOT)) if p.is_relative_to(REPO_ROOT) else str(p)


def _abs(path: str) -> Path:
    from data.config import REPO_ROOT

    p = Path(path)
    return p if p.is_absolute() else REPO_ROOT / p


# ------------------------------------------------------------------ inputs ----
@dataclass(frozen=True)
class RunInputs:
    harness_sha256: str
    freeze_sha256: str
    model: Path
    model_sha256: str
    model_dir: Path
    store_hashes: Path
    calendar_hashes: Path
    out: Path
    freeze_path: Path = FREEZE_PATH
    marker_path: Path = MARKER_PATH
    registry_path: Path | None = None  # None: screening.trial_registry.REGISTRY_PATH
    hist_root: Path | None = None  # None: data.config.HIST_ROOT
    gate0_list: tuple[Path, str] = (E12_GATE0_LIST, E12_GATE0_LIST_SHA256)
    v2_freeze: tuple[Path, str] = (V2_FREEZE_MANIFEST, V2_FREEZE_SHA256)
    first: date = WINDOW_FIRST
    last: date = WINDOW_LAST


@dataclass(frozen=True)
class Prepared:
    records: dict[str, Any]
    tables: Any  # context.HistTables
    releases: Any  # tables.HistReleases
    c12: Any  # exclusions.C12Result
    calendars: Mapping[str, Any]
    models: Mapping[str, Any]  # h -> models.FittedModel
    q: Mapping[str, float]
    feature_cols: tuple[str, ...]
    signals: tuple[str, ...]
    c10_reference: Mapping[str, Any]
    stores: Mapping[str, str]  # root -> sha256


def expected_feature_cols(signals: Sequence[str]) -> tuple[str, ...]:
    """panel.build_panel's feature_cols for ``signals`` (z_, varying app_, then identifiers)."""
    from ml_route_v2.constants import CLUSTERS, UNIVERSE
    from ml_route_v2.signals import ALWAYS_APPLICABLE

    return (tuple(f"z_{s}" for s in signals)
            + tuple(f"app_{s}" for s in signals if s not in ALWAYS_APPLICABLE)
            + tuple(f"id_root_{v}" for v in UNIVERSE) + tuple(f"id_cluster_{k}" for k in CLUSTERS))


def load_model(path: Path, sha: str, model_dir: Path, signals: Sequence[str]
               ) -> tuple[dict, dict, dict]:
    """(model JSON, h -> FittedModel, h -> q) with every hash checked."""
    from c1_replication.q_m1 import feature_cols_sha256, payload_name
    from ml_route_v2.configs import ridge_spec
    from ml_route_v2.constants import GATE0_RIDGE_LAMBDA
    from ml_route_v2.models import FittedModel, _sha256

    doc = json.loads(pinned_file(path, sha, "model JSON"))
    if doc.get("schema") != MODEL_SCHEMA:
        raise C1Refused(f"{Path(path).name}: schema is not {MODEL_SCHEMA!r}")
    cols = doc.get("feature_cols")
    if not isinstance(cols, list) or feature_cols_sha256(cols) != doc.get("feature_cols_sha256"):
        raise C1Refused("the model JSON's feature_cols do not hash to its feature_cols_sha256")
    if list(doc.get("signals", [])) != list(signals):
        raise C1Refused("the model JSON's signals are not E.12's covered signals")
    spec = ridge_spec(GATE0_RIDGE_LAMBDA)
    fitted, q = {}, {}
    for tid in TEST_IDS:
        h = HORIZON_OF[tid]
        m = doc.get("m1", {}).get(h, {})
        if m.get("spec") != spec.as_dict() or not _is_sha(m.get("payload_sha256")):
            raise C1Refused(f"the model JSON's M1 {h} is not the frozen ridge spec with a sha256")
        payload = pinned_file(Path(model_dir) / payload_name(h), m["payload_sha256"],
                              f"M1 {h} payload")
        fitted[h] = FittedModel(spec, _sha256(payload), payload)
        rec = doc.get("q", {}).get(h, {})
        value = rec.get("q")
        if not (isinstance(value, float) and math.isfinite(value) and value > 0
                and rec.get("q_repr") == repr(value)):
            raise C1Refused(f"the model JSON's q {h} is not a positive float with its repr")
        q[h] = value
    return doc, fitted, q


def load_store_hashes(path: Path) -> dict[str, str]:
    doc = json.loads(Path(path).read_bytes())
    stores = doc.get("stores") if isinstance(doc, dict) else None
    if not isinstance(doc, dict) or doc.get("schema") != STORE_HASHES_SCHEMA or \
            doc.get("plan") != PLAN or not isinstance(stores, dict):
        raise C1Refused(f"{Path(path).name}: not a {STORE_HASHES_SCHEMA} file of plan {PLAN}")
    if sorted(stores) != sorted(STORE_ROOTS) or not all(_is_sha(v) for v in stores.values()):
        raise C1Refused(f"{Path(path).name}: needs a sha256 for exactly {list(STORE_ROOTS)}")
    return {r: str(stores[r]) for r in STORE_ROOTS}


def check_stores(stores: Mapping[str, str], hist_root: Path) -> dict[str, Any]:
    from data.hist_store import hist_parquet_path

    out = {}
    for root, want in stores.items():
        path = hist_parquet_path(root, PLAN, hist_root)
        if not path.is_file():
            raise C1Refused(f"store {path} does not exist")
        got = file_sha256(path)
        if got != want:
            raise C1Refused(f"store {path.name}: sha256 {got[:12]}... is not {want[:12]}...")
        out[root] = {"path": _rel(path), "sha256": got}
    return out


def load_calendars(path: Path, first: date, last: date) -> dict[str, Any]:
    """The six hist calendars, the release tables and the energy full sessions (pinned)."""
    from c1_replication.context import HistTables
    from c1_replication.tables import (
        TableError,
        h1_rows,
        h1_unsettled,
        load_full_sessions,
        load_releases,
        read_pinned,
    )
    from data.hist_calendar import parse_hist_calendar

    doc = json.loads(Path(path).read_bytes())
    if not isinstance(doc, dict) or doc.get("schema") != CALENDAR_HASHES_SCHEMA:
        raise C1Refused(f"{Path(path).name}: schema is not {CALENDAR_HASHES_SCHEMA!r}")
    try:
        cals = {}
        for g in HIST_GROUPS:
            rec = doc["calendars"][g]
            p = _abs(rec["path"])
            cals[g] = parse_hist_calendar(read_pinned(p, rec["sha256"], f"{g} calendar"), g, p)
        rel = load_releases(_abs(doc["releases"]["path"]), doc["releases"]["sha256"])
        full = load_full_sessions(_abs(doc["energy_full_sessions"]["path"]),
                                  doc["energy_full_sessions"]["sha256"], cals["energy"])
        rows = h1_rows(cals["equity"])
    except (KeyError, TypeError, TableError, ValueError, RuntimeError) as exc:
        raise C1Refused(f"calendar inputs refused: {type(exc).__name__}: {exc}") from exc
    if rel.calendar.first > first or rel.calendar.last < last:
        raise C1Refused(f"the release calendar covers {rel.calendar.first}..{rel.calendar.last}, "
                        f"not the window {first}..{last}")
    tables = HistTables(cals, rows, rel.ngs_table, full)
    return {"calendars": cals, "releases": rel, "tables": tables,
            "record": {"hashes_file": {"path": str(path), "sha256": file_sha256(path)},
                       "calendars": {g: c.record() for g, c in cals.items()},
                       "releases": rel.record(),
                       "energy_full_sessions": {**doc["energy_full_sessions"], "n": len(full)},
                       "topstep_h1_rows": len(rows),
                       "topstep_h1_unsettled": [d.isoformat()
                                                for d in h1_unsettled(cals["equity"])]}}


def clock_check(c12: Any, calendars: Mapping[str, Any]) -> dict[str, Any]:  # noqa: ANN401
    """The frozen energy clock on every NG candidate date (inside the context), and NG's day
    session in each hist energy SessionSpec equal to D6's."""
    from ml_route_v2.clock import decision_rows, minutes_after_midnight_ct
    from ml_route_v2.constants import DECISION_TIMES_CT
    from ml_route_v2.signals._daily import session_minutes

    o, c = session_minutes(VEHICLE)
    for spec in calendars["energy"].sessions:
        table = spec.day_session_ct
        pair = table.get(VEHICLE) or table.get("*")
        if pair is None or (pair[0].hour * 60 + pair[0].minute,
                            pair[1].hour * 60 + pair[1].minute) != (o, c):
            raise C1Refused(f"the hist energy session from {spec.valid_from} gives NG's day "
                            f"session {pair}, not D6's ({o // 60:02d}:{o % 60:02d}-"
                            f"{c // 60:02d}:{c % 60:02d} CT)")
    energy = calendars["energy"]
    days = [d for d in c12.candidates if d not in c12.excluded and energy.is_trade_date(d)]
    rows = decision_rows((VEHICLE,), {VEHICLE: days})
    want = {t.hour * 60 + t.minute for t in DECISION_TIMES_CT["energy"]}
    got = set(minutes_after_midnight_ct(rows["decision_ts_ns"].to_numpy()).tolist())
    per_day = rows.groupby("trade_date").size()
    if got != want or (per_day != len(want)).any():
        raise C1Refused(f"the decision clock on NG's dates is not the frozen energy clock "
                        f"{sorted(want)} (got {sorted(got)})")
    return {"dates": len(days), "dates_with_rows": int(len(per_day)),
            "dates_without_rows": len(days) - int(len(per_day)), "rows": int(len(rows))}


def preconditions(inp: RunInputs, preflight: Callable[[str], str]) -> Prepared:
    """Every check before the marker (module docstring). Raises C1Refused."""
    from c1_replication.context import hist_tables, patch_record
    from c1_replication.exclusions import c12_exclusions
    from data.config import HIST_ROOT
    from screening import trial_registry

    harness = preflight(inp.harness_sha256)
    if Path(inp.marker_path).exists() or Path(inp.out).exists():
        raise C1Refused(f"C1 runs once: "
                        f"{Path(inp.marker_path if Path(inp.marker_path).exists() else inp.out)}"
                        " exists")
    pinned_file(inp.freeze_path, inp.freeze_sha256, "freeze")
    registry = Path(inp.registry_path or trial_registry.REGISTRY_PATH)
    try:
        entry = trial_registry.require_registered(TEST_IDS, test=TEST,
                                                  freeze_sha256=inp.freeze_sha256, path=registry)
    except trial_registry.TrialRegistryError as exc:
        raise C1Refused(str(exc)) from exc
    v2 = verify_v2(*inp.v2_freeze)
    signals = tuple(json.loads(pinned_file(*inp.gate0_list, "E.12 Gate 0 list"))
                    ["covered_signals"])
    model_doc, fitted, q = load_model(inp.model, inp.model_sha256, inp.model_dir, signals)
    cols = tuple(model_doc["feature_cols"])
    if expected_feature_cols(signals) != cols:
        raise C1Refused("C11: the feature_cols the signals give are not the model's")
    stores = load_store_hashes(inp.store_hashes)
    store_rec = check_stores(stores, Path(inp.hist_root or HIST_ROOT))
    cal = load_calendars(inp.calendar_hashes, inp.first, inp.last)
    c12 = c12_exclusions(cal["calendars"], tuple(cal["releases"].unsourced),
                         first=inp.first, last=inp.last)
    if c12.stops:
        raise C1Refused(f"C12 STOP: {len(c12.excluded)} of {c12.n_candidates} NG dates "
                        f"({c12.share:.4%}) are unsourced, above {c12.max_share:.0%}")
    with hist_tables(cal["tables"]):
        clock = clock_check(c12, cal["calendars"])
    records = {
        "harness_sha256": harness,
        "freeze": {"path": _rel(inp.freeze_path), "sha256": inp.freeze_sha256},
        "registry": {"path": _rel(registry), "entry_id": entry["entry_id"],
                     "n_before": entry["n_before"], "n_after": entry["n_after"]},
        "v2_freeze": v2,
        "gate0_list": {"path": _rel(inp.gate0_list[0]), "sha256": inp.gate0_list[1]},
        "model": {"path": _rel(inp.model), "sha256": inp.model_sha256,
                  "m1_payload_sha256": {h: m.sha256 for h, m in fitted.items()},
                  "q": {h: model_doc["q"][h]["q_repr"] for h in q},
                  "feature_cols_sha256": model_doc["feature_cols_sha256"]},
        "stores": store_rec, "store_hashes_file": {"path": str(inp.store_hashes),
                                                   "sha256": file_sha256(inp.store_hashes)},
        "calendar_inputs": cal["record"], "c12": c12.record(), "clock": clock,
        "patches": patch_record(cal["tables"]),
        "window": [inp.first.isoformat(), inp.last.isoformat()],
        "code_sha256": _code_hashes(),
    }
    return Prepared(records, cal["tables"], cal["releases"], c12, cal["calendars"], fitted, q,
                    cols, signals, model_doc["c10_reference"], stores)


def _code_hashes() -> dict[str, str]:
    from c1_replication.q_m1 import code_hashes

    return code_hashes()


# ------------------------------------------------------------------ the evaluation ----
def c10_counts(panel: Any) -> dict[str, Any]:  # noqa: ANN401
    from c1_replication.q_m1 import c10_reference

    return c10_reference(panel)


def c10_check(counts: Mapping[str, Any], reference: Mapping[str, Any]) -> list[str]:
    """Signals live on NG rows in E.12 (reference count > 0) that apply on no row now."""
    dead = []
    for tid in TEST_IDS:
        h = HORIZON_OF[tid]
        ref, got = reference[h]["applicable"], counts[h]["applicable"]
        dead += [f"{s} ({h})" for s, n in ref.items() if n > 0 and got.get(s, 0) == 0]
    return dead


def trade_frame(panel: Any, h: str, model: Any, q: float, test_id: str  # noqa: ANN401
                ) -> tuple[pd.DataFrame, int]:
    """(the test's trades in gate0_b_trades' columns, the NG ok rows at h)."""
    from ml_route_v2.cpcv import horizon_data
    from ml_route_v2.models import predict

    data = horizon_data(panel, h, None)
    if (data.rows["root"].to_numpy(object) != VEHICLE).any():
        raise C1GuardStop("C8: the panel holds rows of another vehicle than NG")
    r_hat = predict(model, data.X)
    side = np.sign(r_hat).astype(np.int8)
    idx = np.flatnonzero((np.abs(r_hat) >= q) & (side != 0))
    rows = data.rows.iloc[idx]
    s = side[idx]
    cost = np.where(s > 0, rows[f"cost_long_{h}"].to_numpy(np.float64),
                    rows[f"cost_short_{h}"].to_numpy(np.float64))
    frame = pd.DataFrame({
        "test_id": test_id, "root": VEHICLE, "horizon": h, "trade_date": data.days[idx],
        "decision_ts_ns": data.t_ns[idx], "r_hat": r_hat[idx], "side": s,
        "g_ticks": s * rows[f"y_gross_{h}"].to_numpy(np.float64), "cost_ticks": cost,
        "n_pair_rows": int(len(r_hat))})
    return frame, int(len(r_hat))


def passes(mean: float, cost: float, p: float, n: int) -> bool:
    return bool(math.isfinite(mean) and math.isfinite(cost) and mean >= COST_MULTIPLE * cost
                and math.isfinite(p) and p <= ALPHA_ONE_SIDED and n >= MIN_TRADES)


def stat_block(test: Any) -> dict[str, Any]:  # noqa: ANN401
    ok = passes(test.mean, test.cost_ticks, test.p, int(test.n_trades or 0))
    return {"horizon": test.horizon, "n_trades": test.n_trades, "n_dates": test.n_dates,
            "n_rows": test.n_obs, "mean_gross_ticks": test.mean, "cost_ticks": test.cost_ticks,
            "bar_ticks": COST_MULTIPLE * test.cost_ticks, "t_B": test.t, "p_one_sided": test.p,
            "criteria": {"mean_ge_1_5c": bool(math.isfinite(test.mean) and test.mean
                                              >= COST_MULTIPLE * test.cost_ticks),
                         "p_le_0_025": bool(math.isfinite(test.p) and test.p <= ALPHA_ONE_SIDED),
                         "n_ge_30": bool((test.n_trades or 0) >= MIN_TRADES)},
            "decision": PASS if ok else FAIL}


def verdict_of(blocks: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    passing = [t for t in TEST_IDS if blocks[t]["decision"] == PASS]
    return {"verdict": PASS if passing else FAIL, "passing_tests": passing,
            "verdict_rule": "PASS iff T1 (NG h60) or T2 (NG hF) passes; a test passes iff mean "
                            "g >= 1.5 x c AND one-sided p <= 0.025 AND n_trades >= 30"}


def descriptive(trades: Mapping[str, pd.DataFrame], n_rows: Mapping[str, int]) -> dict[str, Any]:
    from ml_route_v2.constants import COST_SENSITIVITY_SLIPPAGE_MULTIPLE
    from ml_route_v2.portfolio import vehicle_facts

    comm = float(vehicle_facts(VEHICLE).commission_rt_ticks)
    out = {}
    for tid, tr in trades.items():
        g = tr["g_ticks"].to_numpy(np.float64)
        c = tr["cost_ticks"].to_numpy(np.float64)
        c15 = comm + COST_SENSITIVITY_SLIPPAGE_MULTIPLE * (c - comm)
        side = tr["side"].to_numpy()
        years = Counter(pd.to_datetime(tr["trade_date"]).dt.year.astype(int).tolist())
        mean_c15 = float(c15.mean()) if len(c15) else float("nan")
        out[tid] = {
            "c14_slippage_1_5x": {
                "commission_rt_ticks": comm, "mean_cost_ticks": mean_c15,
                "bar_ticks": COST_MULTIPLE * mean_c15,
                "mean_ge_bar": bool(len(g) and float(g.mean()) >= COST_MULTIPLE * mean_c15)},
            "c15": {"share_of_rows_at_or_above_q": (len(tr) / n_rows[tid]) if n_rows[tid]
                    else None, "n_rows": n_rows[tid],
                    "long": {"n": int((side > 0).sum()),
                             "mean_gross_ticks": float(g[side > 0].mean()) if (side > 0).any()
                             else None},
                    "short": {"n": int((side < 0).sum()),
                              "mean_gross_ticks": float(g[side < 0].mean()) if (side < 0).any()
                              else None},
                    "trades_per_year": {str(y): n for y, n in sorted(years.items())}}}
    return out


def trades_sha256(trades: Mapping[str, pd.DataFrame]) -> str:
    rows = []
    for tid in TEST_IDS:
        tr = trades.get(tid)
        if tr is None:
            continue
        for d, t, s, g, c in zip(pd.to_datetime(tr["trade_date"]).dt.date.astype(str),
                                 tr["decision_ts_ns"].astype(np.int64), tr["side"].astype(int),
                                 tr["g_ticks"].astype(float), tr["cost_ticks"].astype(float),
                                 strict=True):
            rows.append([tid, d, int(t), int(s), repr(float(g)), repr(float(c))])
    return hashlib.sha256(json.dumps(rows, separators=(",", ":")).encode()).hexdigest()


def default_leg_loader(hist_root: Path | None) -> Callable[..., Any]:
    from data.config import HIST_ROOT
    from data.hist_bars import load_hist_leg

    def load(root: str, *, expected_sha256: str, calendar: Any) -> Any:  # noqa: ANN401
        return load_hist_leg(root, PLAN, expected_sha256=expected_sha256,
                             hist_root=Path(hist_root or HIST_ROOT), calendar=calendar)

    return load


def evaluate(prep: Prepared, inp: RunInputs, leg_loader: Callable[..., Any] | None = None,
             partial: dict[str, Any] | None = None,
             log: Callable[[str], None] = print) -> dict[str, Any]:
    """Steps 1-5 of the module docstring. ``partial`` collects the guard counts as they are
    computed (written with a STOPPED result)."""
    from c1_replication.context import hist_tables
    from c1_replication.world import build_world, replication_panel
    from data.group_session import group_of
    from ml_route_v2.gate0 import _b_test

    partial = {} if partial is None else partial
    loader = leg_loader or default_leg_loader(inp.hist_root)
    with hist_tables(prep.tables):
        world = build_world(
            lambda r: loader(r, expected_sha256=prep.stores[r],
                             calendar=prep.calendars[group_of(r)]),
            prep.releases.calendar, prep.c12.excluded_dates(), first=inp.first, last=inp.last)
        partial["world"] = {"roots": dict(world.roots), "calendar_dates": len(world.calendar),
                            "excluded_dates": len(world.excluded)}
        panel = replication_panel(world, prep.signals)
        del world
        gc.collect()
    partial["panel_counts"] = {k: int(v) for k, v in dict(panel.counts).items()}
    if tuple(panel.feature_cols) != tuple(prep.feature_cols):
        raise C1GuardStop("C11: the replication panel's feature_cols are not E.12's")
    counts = c10_counts(panel)
    partial["c10"] = counts
    for tid in TEST_IDS:  # C10: counts of NG ok rows where each signal applies (no values)
        h = HORIZON_OF[tid]
        log(f"C10 {h}: NG ok rows {counts[h]['ng_ok_rows']}; applicable rows per signal "
            + ", ".join(f"{s} {n}" for s, n in counts[h]["applicable"].items()))
    dead = c10_check(counts, prep.c10_reference)
    if dead:
        raise C1GuardStop(f"C10: features live in E.12 apply on no NG row: {dead[:5]}"
                          f"{' ...' if len(dead) > 5 else ''} ({len(dead)})")
    trades, blocks, n_rows = {}, {}, {}
    for tid in TEST_IDS:
        h = HORIZON_OF[tid]
        trades[tid], n_rows[tid] = trade_frame(panel, h, prep.models[h], prep.q[h], tid)
        blocks[tid] = stat_block(_b_test(tid, VEHICLE, h, trades[tid], n_rows[tid]))
    verdict = verdict_of(blocks)
    return {**verdict, "tests": blocks, "descriptive": descriptive(trades, n_rows),
            "trades_sha256": trades_sha256(trades),
            "guards": {"C11": "feature_cols equal E.12's", "C10": counts}}


def _write_new(path: Path, payload: Mapping[str, Any]) -> str:
    from ml_route_v2.phase1._io import clean

    data = (json.dumps(clean(payload), indent=1, allow_nan=False) + "\n").encode()
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with Path(path).open("xb") as fh:  # never over an existing file
        fh.write(data)
    return hashlib.sha256(data).hexdigest()


def run(inp: RunInputs, *, preflight: Callable[[str], str] | None = None,
        leg_loader: Callable[..., Any] | None = None,
        log: Callable[[str], None] = print) -> dict[str, Any]:
    """The one evaluation: C1Refused before the marker; afterwards always a written result."""
    from screening import harness_freeze

    prep = preconditions(inp, preflight or harness_freeze.preflight)
    started = _now()
    _write_new(inp.marker_path, {"schema": MARKER_SCHEMA, "test": TEST,
                                 "started_local": started, "out": _rel(inp.out),
                                 "inputs": prep.records})
    log(f"C1 marker written at {started}; the evaluation runs once from here")
    partial: dict[str, Any] = {}
    try:
        result = evaluate(prep, inp, leg_loader, partial, log)
    except C1GuardStop as exc:
        result = {"verdict": STOPPED, "stop_reason": str(exc),
                  "guards": {"C10": partial.get("c10")}}
    except Exception as exc:  # noqa: BLE001 - every stop after the marker is the verdict
        result = {"verdict": STOPPED, "stop_reason": f"{type(exc).__name__}: {exc}",
                  "guards": {"C10": partial.get("c10")}}
    head = {"schema": RESULT_SCHEMA, "test": TEST, "test_ids": list(TEST_IDS),
            "verdict": result.pop("verdict")}
    payload = {**head, **result, "world": partial.get("world"),
               "panel_counts": partial.get("panel_counts"), "inputs": prep.records,
               "started_local": started, "finished_local": _now()}
    sha = _write_new(inp.out, payload)
    log(f"C1 verdict {payload['verdict']}" + (f" ({payload['stop_reason']})"
                                              if payload.get("stop_reason") else ""))
    for tid, b in (payload.get("tests") or {}).items():
        log(f"  {tid} {b['horizon']}: {b['decision']}; n_trades {b['n_trades']}, mean "
            f"{b['mean_gross_ticks']!r} ticks, bar {b['bar_ticks']!r}, t_B {b['t_B']!r}, "
            f"p {b['p_one_sided']!r}")
    for tid, d in (payload.get("descriptive") or {}).items():
        c15 = d["c15"]
        log(f"  descriptive {tid}: share at or above q {c15['share_of_rows_at_or_above_q']!r}, "
            f"long {c15['long']['n']}, short {c15['short']['n']}, 1.5x slippage bar met "
            f"{d['c14_slippage_1_5x']['mean_ge_bar']}")
    log(f"  written {inp.out} sha256 {sha}")
    return payload


# ------------------------------------------------------------------ CLI ----
def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="python -m c1_replication.evaluate")
    p.add_argument("--harness-sha256", required=True)
    p.add_argument("--freeze", default=str(FREEZE_PATH))
    p.add_argument("--freeze-sha256", required=True)
    p.add_argument("--model", required=True)
    p.add_argument("--model-sha256", required=True)
    p.add_argument("--model-dir", required=True)
    p.add_argument("--store-hashes", required=True)
    p.add_argument("--calendar-hashes", required=True)
    p.add_argument("--out", required=True)
    return p


def main(argv: Sequence[str] | None = None, *,
         preflight: Callable[[str], str] | None = None) -> int:
    from compute.platform import lower_priority
    from screening import harness_freeze

    args = _parser().parse_args(argv)
    lower_priority()
    inp = RunInputs(args.harness_sha256, args.freeze_sha256, Path(args.model), args.model_sha256,
                    Path(args.model_dir).expanduser(), Path(args.store_hashes),
                    Path(args.calendar_hashes), Path(args.out), freeze_path=Path(args.freeze))
    try:
        payload = run(inp, preflight=preflight)
    except (C1Refused, harness_freeze.HarnessFreezeError, OSError, json.JSONDecodeError) as exc:
        print(f"REFUSED, nothing written, the evaluation has not run ({type(exc).__name__}): "
              f"{exc}", file=sys.stderr)
        return RC_REFUSED
    return 0 if payload["verdict"] in (PASS, FAIL) else 1


if __name__ == "__main__":
    sys.exit(main())
