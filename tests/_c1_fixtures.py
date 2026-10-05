"""Synthetic inputs for test C1's evaluation tests. Nothing here is market data or a sourced
calendar: every payload is marked SYNTHETIC.

- ``calendar_payload(group)``: an e14_hist_calendar/1 payload for each of the six hist groups
  (sessions shaped like CME's, a few SYNTHETIC holidays, every year "covered").
- ``release_payload()``: an e14_release_calendar/1 payload with weekly NGS (Thursday 10:30 ET),
  weekly WPSR (Wednesday 10:30 ET) and FOMC rows (14:00 ET) over the coverage.
- ``write_inputs(base)``: the six calendars, the release file and the energy full sessions on
  disk, with the calendar-hashes JSON evaluate reads (``Inputs``).
- ``synthetic_leg(root, first, last, seed, plants)``: a LegFrame of frozen synthetic bars
  (ml_route_v2.synthetic._root_bars) on the hist calendar; call it inside the C1 context.
- ``ridge_model(feature_cols, weights)``: a frozen-format ridge FittedModel with chosen
  coefficients (models._ridge_payload's layout).
"""

from __future__ import annotations

import copy
import hashlib
import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import numpy as np

SOURCE = "synthetic-test-fixture"
ET = ZoneInfo("America/New_York")
SESSIONS = {
    "equity": ([(-1, "17:00", 0, "16:00")], {"*": ["08:30", "15:00"]}),
    "rates": ([(-1, "17:00", 0, "16:00")], {"*": ["07:20", "14:00"]}),
    "fx": ([(-1, "17:00", 0, "16:00")], {"*": ["07:20", "14:00"]}),
    "energy": ([(-1, "17:00", 0, "16:00")], {"*": ["08:00", "13:30"]}),
    "metals": ([(-1, "17:00", 0, "16:00")], {"*": ["07:20", "12:30"]}),
    "grains": ([(-1, "19:00", 0, "07:45"), (0, "08:30", 0, "13:20")], {"*": ["08:30", "13:15"]}),
}
PRODUCTS = {"equity": ["NQ", "ES"], "rates": ["ZN"], "fx": ["6E"],
            "energy": ["NG", "CL"], "metals": ["GC"], "grains": ["ZC"]}
# SYNTHETIC entries (not CME's schedule): (day, name, kind, halt_ct, evidence)
COMMON = [("2010-07-05", "Independence Day (synthetic)", "full_closure", None, "cme"),
          ("2010-11-25", "Thanksgiving (synthetic)", "full_closure", None, "cme"),
          ("2010-12-24", "Christmas (synthetic)", "full_closure", None, "cme"),
          ("2011-01-17", "MLK (synthetic)", "early_halt", "12:00", "cme")]
EXTRA = {"equity": [("2010-11-26", "Thanksgiving Friday (synthetic)", "early_halt", "12:15",
                     "cme"),
                    ("2011-07-04", "Independence Day (synthetic)", "full_closure", None, "cme")],
         "energy": [("2010-11-26", "Thanksgiving Friday (synthetic)", "early_halt", "12:45",
                     "cme"),
                    ("2011-07-04", "Independence Day (synthetic)", "full_closure", None, "cme")]}
GROUPS = ("equity", "rates", "fx", "energy", "metals", "grains")
CAL_SCHEMA_HASHES = "stage_e14_c1_calendar_hashes/1"


def sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def calendar_payload(group: str, *, entries: Sequence[tuple] | None = None,
                     unsourced: Sequence[tuple[str, str]] = ()) -> dict[str, Any]:
    segments, day_session = SESSIONS[group]
    rows = list(COMMON) + list(EXTRA.get(group, [])) if entries is None else list(entries)
    out = []
    for day, name, kind, halt, evidence in sorted(rows):
        out.append({"day": day, "name": name, "kind": kind, "halt_ct": halt,
                    "evidence": evidence, "time_evidence": "n/a" if kind == "full_closure"
                    else "cme", "source": SOURCE, "status_quote": "SYNTHETIC",
                    "time_quote": None, "note": "SYNTHETIC"})
    return {
        "schema": "e14_hist_calendar/1", "group": group, "products": PRODUCTS[group],
        "cme_row_labels": ["SYNTHETIC"], "coverage": {"first": "2010-06-01", "last": "2019-05-31"},
        "sessions": [{"valid_from": "2010-06-01", "valid_to": None,
                      "segments": [{"start_offset_days": a, "start_ct": b, "end_offset_days": c,
                                    "end_ct": d} for a, b, c, d in segments],
                      "day_session_ct": day_session, "source": SOURCE, "evidence": "cme",
                      "note": "SYNTHETIC"}],
        "entries": out, "no_entry_findings": [],
        "year_coverage": [{"year": y, "documents": [SOURCE], "complete_exception_list": True,
                           "unscheduled_check": "SYNTHETIC", "evidence": "cme"}
                          for y in range(2010, 2020)],
        "unsourced": [{"day": d, "reason": r} for d, r in unsourced],
        "sources": {SOURCE: {"url": None, "capture": None, "fetched_utc": None,
                             "saved_file": None, "sha256": None,
                             "title": "SYNTHETIC TEST FIXTURE, not a sourced calendar"}},
        "counts": {},
    }


def _instant(day: date, hh: int, mm: int) -> str:
    local = datetime.combine(day, time(hh, mm), tzinfo=ET)
    return local.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _row(kind: str, day: date, hh: int, mm: int, evidence: str = "official",
         **extra: Any) -> dict[str, Any]:  # noqa: ANN401
    return {"id": f"{kind}-{day.isoformat()}", "release": kind, "release_name": kind,
            "date": day.isoformat(), "time_local": f"{hh:02d}:{mm:02d}",
            "tz": "America/New_York", "instant_utc": _instant(day, hh, mm),
            "products": ["NG"], "cpi": False, "evidence": evidence,
            "source": {"id": SOURCE}, **extra}


def release_payload(*, unverified: Sequence[str] = (), drops: Sequence[str] = (),
                    unsourced: Sequence[str] = ()) -> dict[str, Any]:
    first, last = date(2010, 6, 1), date(2019, 5, 31)
    rows = []
    d = first
    while d <= last:
        if d.weekday() == 3:  # Thursday NGS
            rows.append(_row("NGS", d, 10, 30, "unverified" if d.isoformat() in unverified
                             else "official", drop_actual_differs=d.isoformat() in drops))
        if d.weekday() == 2:  # Wednesday WPSR, and FOMC every sixth Wednesday
            rows.append(_row("WPSR", d, 10, 30))
            if (d - first).days % 42 < 7:
                rows.append(_row("FOMC", d, 14, 0))
        d += timedelta(days=1)
    rows.append(_row("NFP", date(2011, 1, 7), 8, 30))  # not on NG's D8 list: ignored
    return {"schema": "e14_release_calendar/1",
            "coverage": {"first": first.isoformat(), "last": last.isoformat()},
            "releases": rows, "cancellations": [],
            "unsourced": [{"date": u, "release": "NGS", "reason": "SYNTHETIC"}
                          for u in unsourced],
            "sources": {SOURCE: {"title": "SYNTHETIC"}}, "counts": {}}


@dataclass(frozen=True)
class Inputs:
    base: Path
    hashes: Path
    calendar_dir: Path
    releases: Path
    full_sessions: Path


def write_inputs(base: Path, *, calendars: Mapping[str, dict] | None = None,
                 releases: dict | None = None) -> Inputs:
    from c1_replication.tables import full_sessions_rule
    from data.hist_calendar import parse_hist_calendar

    base.mkdir(parents=True, exist_ok=True)
    cal_dir = base / "hist2010"
    cal_dir.mkdir(exist_ok=True)
    rec: dict[str, Any] = {"schema": CAL_SCHEMA_HASHES, "calendars": {}}
    for g in GROUPS:
        payload = (calendars or {}).get(g) or calendar_payload(g)
        path = cal_dir / f"{g}.json"
        path.write_text(json.dumps(payload, indent=1))
        rec["calendars"][g] = {"path": str(path), "sha256": sha(path)}
    rel = base / "releases.json"
    rel.write_text(json.dumps(releases or release_payload()))
    rec["releases"] = {"path": str(rel), "sha256": sha(rel)}
    energy_path = cal_dir / "energy.json"
    energy = parse_hist_calendar(energy_path.read_bytes(), "energy", energy_path)
    rng = (date(2010, 6, 1), date(2019, 5, 31))
    full = base / "energy_full_sessions.json"
    full.write_text(json.dumps({"rule": "SYNTHETIC", "source_sha256": energy.file_sha256,
                                "range": {"first": rng[0].isoformat(),
                                          "last": rng[1].isoformat()},
                                "ENERGY_FULL_SESSIONS": list(full_sessions_rule(energy, *rng))}))
    rec["energy_full_sessions"] = {"path": str(full), "sha256": sha(full)}
    hashes = base / "calendar_hashes.json"
    hashes.write_text(json.dumps(rec, indent=1))
    return Inputs(base, hashes, cal_dir, rel, full)


_VOL: dict[str, float] = {}


def vol_ticks_table() -> dict[str, float]:
    """The frozen synthetic step sd per store root; computed OUTSIDE the C1 context (it reads
    the real metals calendar's sub-group map, which a hist calendar does not carry)."""
    from c1_replication.constants import STORE_ROOTS
    from c1_replication.context import is_active
    from ml_route_v2.synthetic import default_vol_ticks

    if not _VOL:
        if is_active():
            raise RuntimeError("call vol_ticks_table() before entering the C1 context")
        _VOL.update({r: float(default_vol_ticks(r)) for r in STORE_ROOTS})
    return dict(_VOL)


def synthetic_leg(root: str, first: date, last: date, *, seed: int,
                  plants: Sequence[Mapping[str, Any]] = ()) -> Any:  # noqa: ANN401
    """Frozen synthetic bars on the hist calendar (inside the C1 context) as a LegFrame;
    vol_ticks_table() must have run before the context."""
    from data.stage_e_bars import LegFrame
    from ml_route_v2.synthetic import _root_bars, synthetic_blackout

    frame = _root_bars(root, first, last, seed=seed, vol_ticks=_VOL[root],
                       plants=list(plants), vehicles=("NG",), compact=False)
    frame["in_scheduled_closure"] = False
    frame["vendor_degraded_day"] = False
    days = tuple(sorted({date.fromisoformat(d) for d in frame["trade_date"].astype(str)}))
    return LegFrame(root, "hist:ext2010", f"synthetic/{root}", "0" * 64, frame, days, (),
                    synthetic_blackout(root, first, last))


def ridge_model(feature_cols: Sequence[str], weights: Mapping[str, float],
                intercept: float = 0.0) -> Any:  # noqa: ANN401
    from ml_route_v2.configs import ridge_spec
    from ml_route_v2.models import FittedModel, _sha256

    coef = np.array([float(weights.get(c, 0.0)) for c in feature_cols], dtype="<f8")
    payload = (np.asarray([len(feature_cols)], dtype="<i8").tobytes() + coef.tobytes()
               + np.asarray([intercept], dtype="<f8").tobytes())
    return FittedModel(ridge_spec(0.1), _sha256(payload), payload)


def deep(doc: dict) -> dict:
    return copy.deepcopy(doc)


def write_model(base: Path, feature_cols: Sequence[str], signals: Sequence[str],
                fitted: Mapping[str, Any], q: Mapping[str, float],
                c10_reference: Mapping[str, Any] | None = None) -> tuple[Path, str, Path]:
    """A model JSON in q_m1's schema plus its payload files: (path, sha256, model dir)."""
    from c1_replication.constants import MODEL_SCHEMA
    from c1_replication.q_m1 import feature_cols_sha256, payload_name

    model_dir = base / "models"
    model_dir.mkdir(parents=True, exist_ok=True)
    m1 = {}
    for h, m in fitted.items():
        (model_dir / payload_name(h)).write_bytes(m.payload)
        m1[h] = {"spec": m.spec.as_dict(), "payload_sha256": m.sha256}
    ref = c10_reference or {h: {"ng_ok_rows": 1, "applicable": {s: 0 for s in signals}}
                            for h in fitted}
    doc = {"schema": MODEL_SCHEMA, "feature_cols": list(feature_cols),
           "feature_cols_sha256": feature_cols_sha256(feature_cols), "signals": list(signals),
           "m1": m1, "q": {h: {"q": float(v), "q_repr": repr(float(v))} for h, v in q.items()},
           "c10_reference": ref}
    path = base / "model.json"
    path.write_text(json.dumps(doc))
    return path, sha(path), model_dir
