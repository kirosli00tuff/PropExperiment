"""Synthetic NQ-path bars for the h6_rod tests (no real data is read here; never a store, never
the GEX CSV). Prices are integer MNQ/NQ ticks of 0.25; the flag columns come from rules/sessions.py
for MNQ, as the Stage E synthetic frames do (tests/_stage_e_synthetic.py)."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from datetime import UTC, date, datetime, time, timedelta
from types import MappingProxyType
from zoneinfo import ZoneInfo

import pandas as pd

CT = ZoneInfo("America/Chicago")
NS = 1_000_000_000
TICK = 0.25
BASE_TICKS = 60_000  # 15000.00 index points


def ts_ns(day: date, hh: int, mm: int) -> int:
    return int(datetime.combine(day, time(hh, mm), tzinfo=CT).astimezone(UTC).timestamp()) * NS


def day_frame(day: date, *, start: tuple[int, int] = (14, 0), end: tuple[int, int] = (15, 20),
              close_ticks: Mapping[tuple[int, int], int] | None = None,
              base_ticks: int = BASE_TICKS, skip: Sequence[tuple[int, int]] = (),
              instrument_id: int = 4242, iid_at: Mapping[tuple[int, int], int] | None = None,
              open_ticks: Mapping[tuple[int, int], int] | None = None) -> list[dict]:
    """One CT day segment [start, end) of trade date ``day``. Each bar's open equals the previous
    bar's close (base_ticks before the first); ``close_ticks`` sets a bar's close at (hh, mm) and
    the price carries forward; ``open_ticks`` overrides a bar's open; ``skip`` drops bars (the
    price path still moves)."""
    from rules import sessions

    rows = []
    price = base_ticks
    t0 = datetime.combine(day, time(*start), tzinfo=CT)
    n = (end[0] * 60 + end[1]) - (start[0] * 60 + start[1])
    for k in range(n):
        local = t0 + timedelta(minutes=k)
        key = (local.hour, local.minute)
        o = (open_ticks or {}).get(key, price)
        c = (close_ticks or {}).get(key, price)
        price = c
        if key in skip:
            continue
        state = sessions.session_state("MNQ", local.astimezone(UTC))
        rows.append({
            "ts_event": int(local.astimezone(UTC).timestamp()) * NS,
            "open": o * TICK, "high": max(o, c) * TICK, "low": min(o, c) * TICK,
            "close": c * TICK, "volume": 10,
            "instrument_id": (iid_at or {}).get(key, instrument_id), "raw_symbol": "NQM2",
            "trade_date": day.isoformat(), "in_flatten_window": bool(state.must_be_flat),
            "in_no_new_positions_window": bool(not state.can_open), "early_halt_ct": "",
            "in_scheduled_closure": False, "is_roll_session": False, "gap_before_minutes": 0,
            "vendor_degraded_day": False,
        })
    return rows


def frame(days: Sequence[date], per_day: Callable[[date], dict] | None = None) -> pd.DataFrame:
    """Bars over ``days``; ``per_day(day)`` returns day_frame keyword arguments."""
    rows: list[dict] = []
    for d in days:
        rows += day_frame(d, **(per_day(d) if per_day else {}))
    return pd.DataFrame(rows).sort_values("ts_event", kind="stable").reset_index(drop=True)


def no_releases() -> object:
    from screening.stage_e_rules import ReleaseCalendar

    return ReleaseCalendar(MappingProxyType({}), (), date(2019, 5, 1), date(2026, 6, 19),
                           "0" * 64, "test")


RUN_DAYS = (date(2020, 5, 29), *[date(2020, 6, d) for d in (1, 2, 3, 4, 5, 8, 9, 10, 11, 12)])


def run_bars() -> pd.DataFrame:
    """Eleven synthetic trade dates (2020-05-29 is the engine lead-in)."""
    rows: list[dict] = []
    price = 40_000
    for i, d in enumerate(RUN_DAYS):
        move = 8 if i % 3 else -6
        rows += day_frame(d, base_ticks=price, close_ticks={(14, 29): price + move,
                                                             (14, 45): price + 2 * move})
        price += 2 * move
    return pd.DataFrame(rows).sort_values("ts_event", kind="stable").reset_index(drop=True)


def make_run_setup(tmp: object, set_constant: Callable[[object, str, object], None]) -> dict:
    """Temporary store bytes, GEX CSV, freeze manifest and registry, the lead's constants set
    through ``set_constant`` (monkeypatch.setattr in-process, setattr in a subprocess), and test
    hooks with an injected loader. Nothing of the repository's data is opened."""
    import hashlib
    import json
    from pathlib import Path

    from h6_rod import constants as K
    from h6_rod import preflight as pf
    from h6_rod import run
    from screening.trial_registry import init_registry

    def sha(p: Path) -> str:
        return hashlib.sha256(Path(p).read_bytes()).hexdigest()

    tmp = Path(str(tmp))
    run._import_dependencies()  # the v2 modules H6 runs, loaded before the manifest lists them
    store = tmp / "store.parquet"
    store.write_bytes(b"synthetic store bytes")
    gex = tmp / "gex.csv"
    gex.write_text("date,price,dix,gex\n2020-05-29,1,0.4,-5\n2020-06-01,1,0.4,3\n"
                   "2020-06-02,1,0.4,-1\n2020-06-04,1,0.4,-2\n2024-03-01,junk,junk,junk\n",
                   encoding="utf-8")
    for name, value in (("T3_REGISTERED", True), ("ENGINE_LEAD_IN_DATES", 1),
                        ("REGISTRY_LABEL", "E20H6"),
                        ("TEST_IDS", {"T1": "E20H6-T1", "T2": "E20H6-T2", "T3": "E20H6-T3"}),
                        ("NQ_STORE_SHA256", sha(store)), ("GEX_CSV_SHA256", sha(gex))):
        set_constant(K, name, value)
    freeze = tmp / "freeze.json"
    freeze.write_text(json.dumps(pf.manifest_body(pf.required_files(("T1", "T2", "T3"), gex))))
    registry = tmp / "registry.jsonl"
    init_registry(registry)
    paths = run.RunPaths(store, store, gex, freeze, tmp / "RUN_ONCE.json", tmp / "result.json",
                         tmp / "result.md", registry)
    bars = run_bars()
    hooks = run.Hooks(preflight=lambda s: s, validate_store=lambda p: {"synthetic": True},
                      load_leg=lambda p: (bars, frozenset(), {"synthetic": True}),
                      releases=no_releases)
    return {"paths": paths, "hooks": hooks, "freeze_sha": sha(freeze), "tmp": tmp}


__all__ = ["BASE_TICKS", "CT", "NS", "RUN_DAYS", "TICK", "day_frame", "frame", "make_run_setup",
           "no_releases", "run_bars", "ts_ns"]
