"""The Stage E start-date builder and the one shared S_X loader (screening/stage_e_start_dates.py;
design D4, NULL_CRITERIA 4.1, lead ruling OC-K), on synthetic stores only.

What is proved: the day session per product (D6's (O_X, C_X) for every root, lead ruling OC-S);
the day-session monthly medians (CT clock minutes [start, end), keyed by trade-date month, bars
present); the builder reads ts_event, volume and trade_date only and applies the stores' trade-date
refusals; D.1f's recorded MES medians give D.1f's S = 2020-02-03 (and 0.15 / 0.40) end to end
through synthetic stores; MES as a leg comes from D.1f's pinned record; the set's roots (clusters:
frozen vehicles and every frozen leg; ML: the 31 price-path contracts); the file is written once,
read-only, preflight first; the loader merges every per-set file, refuses a root on which two
files differ in S_X, V_ref or any monthly median (ruling Q-4), refuses invalid files, and names a
missing or empty-window root with the runner's StartRuleMissing.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import shutil
import stat
from dataclasses import replace
from datetime import date, datetime, time, timedelta
from pathlib import Path
from types import MappingProxyType
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import pytest

import screening.stage_e_start_dates as sd
from data.config import REPO_ROOT
from data.group_session import load_group_calendar
from data.stage_e_bars import (
    ConfirmationStoreMissing,
    HoldoutRowRefused,
    ParquetHashMismatch,
    book_trade_dates,
)
from rules.products import product
from screening import harness_freeze
from screening.harness_freeze import HarnessFreezeError
from screening.stage_e_frozen import load_frozen_tables
from screening.stage_e_runner import (
    RunnerRefusal,
    StartRuleConflict,
    StartRuleInconsistent,
    StartRuleInvalid,
    StartRuleMissing,
    StartWindowEmpty,
)

CT = ZoneInfo("America/Chicago")
NS = 1_000_000_000
HARNESS = "b" * 64
D1F_RECORD = REPO_ROOT / "reports" / "stage_d1f_step5_start_rule.json"
D1F = json.loads(D1F_RECORD.read_text(encoding="utf-8"))["start_rule"]
BIG = 10_000_000  # the volume of bars outside the day session: it would dominate any median


# ------------------------------------------------------------------ helpers ----
def _ns(day: date, minute: int) -> int:
    local = datetime.combine(day, time(minute // 60, minute % 60), tzinfo=CT)
    return int(local.timestamp()) * NS


def _frame(root: str, rows: list[tuple[date, int, int]]) -> pd.DataFrame:
    """Bars (day, CT minute of day, volume), labelled with the group calendar's own trade date;
    price columns are present so that reading them would be possible (and is checked not to be)."""
    ts = np.array([_ns(d, m) for d, m, _ in rows], dtype=np.int64)
    booked = book_trade_dates(load_group_calendar(product(root).group), ts)
    assert all(b is not None for b in booked)
    order = np.argsort(ts, kind="stable")
    return pd.DataFrame({
        "ts_event": ts[order],
        "open": 1.0, "high": 1.0, "low": 1.0, "close": 1.0,
        "volume": np.array([v for _, _, v in rows], dtype=np.int64)[order],
        "trade_date": [booked[i].isoformat() for i in order],
    })


def _write(frame: pd.DataFrame, path: Path) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_parquet(path, index=False)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _inside(day: date, median: float) -> list[tuple[date, int, int]]:
    """60 day-session bars (08:30-08:59 and 11:00-11:29 CT) whose median volume is ``median``."""
    minutes = [8 * 60 + 30 + k for k in range(30)] + [11 * 60 + k for k in range(30)]
    lo, hi = math.floor(median), math.ceil(median)
    return [(day, m, lo if i % 2 == 0 else hi) for i, m in enumerate(minutes)]


def _outside(day: date) -> list[tuple[date, int, int]]:
    """90 pre-open bars (07:00-08:29 CT) of huge volume: outside every equity day session."""
    return [(day, 7 * 60 + k, BIG) for k in range(90)]


def _reference_day(month: str) -> date:
    """The first Wednesday on or after the 8th of the month (a regular equity trade date)."""
    d = date(int(month[:4]), int(month[5:]), 8)
    while d.weekday() != 2:
        d += timedelta(days=1)
    return d


def _d1f_stores(tmp: Path, root: str = "MNQ") -> tuple[Path, Path, str]:
    """Synthetic research and step 2 stores whose equity day-session monthly medians are D.1f's
    recorded MES medians; 2020-02's first trade date carries pre-open bars only (any session
    counts for the first date), its day-session bars are on the next trade date."""
    research_rows: list[tuple[date, int, int]] = []
    for month, value in D1F["reference_monthly_medians"].items():
        day = _reference_day(month)
        research_rows += _inside(day, value) + _outside(day)
    june = date(2026, 6, 10)  # a research date outside the 14 reference months, never counted
    research_rows += [(june, 9 * 60 + k, BIG) for k in range(60)]
    step2_rows: list[tuple[date, int, int]] = []
    for month, value in D1F["extension_monthly_medians"].items():
        first = date.fromisoformat(D1F["extension_first_trade_dates"][month])
        if month == "2020-02":
            step2_rows += _outside(first) + _inside(first + timedelta(days=1), value)
        else:
            step2_rows += _outside(first) + _inside(first, value)
    research = tmp / "research" / root / "r.parquet"
    step2 = tmp / "step2" / root / "s.parquet"
    sha = _write(_frame(root, research_rows), research)
    _write(_frame(root, step2_rows), step2)
    return research, step2, sha


def consistent_entry(s_x: str | None, *, root: str = "ZN", v_ref: float = 100.0,
                     overrides: dict | None = None, step2_sha256: str = "a" * 64) -> dict:
    """A start-rule entry that follows from its own medians (D4's rule re-run): every reference
    month at v_ref; extension months from s_x's month on at v_ref, earlier ones at v_ref / 10
    (below 0.15 v_ref), so S_X = s_x at 0.25, 0.15 and 0.40 alike; s_x None: no month
    qualifies. ``overrides`` replaces extension medians before the rule runs."""
    from screening.stage_e_stats_start import EXTENSION_MONTHS, REFERENCE_MONTHS

    m_star = None if s_x is None else s_x[:7]
    reference = {m: v_ref for m in REFERENCE_MONTHS}
    extension = {m: v_ref if m_star is not None and m >= m_star else v_ref / 10
                 for m in EXTENSION_MONTHS} | (overrides or {})
    first = {m: date(int(m[:4]), int(m[5:]), 6 if m == "2019-05" else 1)
             for m in EXTENSION_MONTHS}
    if s_x is not None:
        first[m_star] = date.fromisoformat(s_x)
    return sd.entry_from_medians(root, reference, extension, first,
                                 window=(time(7, 20), time(14, 0)), source="test",
                                 step2_sha256=step2_sha256)


def _doc(set_id: str, products: dict) -> dict:
    """``products``: root -> s_x (a consistent entry is built) or a ready entry dict."""
    return {"schema": sd.SCHEMA, "set": set_id,
            "products": {r: v if isinstance(v, dict) else consistent_entry(v, root=r)
                         for r, v in products.items()},
            "inputs": [], "harness_sha256": HARNESS, "created_pdt": "2026-09-26T15:00:00-07:00"}


def _put(root: Path, set_id: str, products: dict) -> Path:
    path = root / "reports" / f"stage_e_start_rule_{set_id}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.chmod(0o644)
    path.write_text(json.dumps(_doc(set_id, products)), encoding="utf-8")
    return path


def _tables_with(**shas: str):
    tables = load_frozen_tables()
    return replace(tables, research_parquet_sha256=MappingProxyType(
        dict(tables.research_parquet_sha256) | shas))


# ---------------------------------------------------------------- day session ----
@pytest.mark.parametrize("root, window", [
    ("MNQ", ("08:30", "15:00")), ("NQ", ("08:30", "15:00")), ("MBT", ("08:30", "15:00")),
    ("ZN", ("07:20", "14:00")), ("6E", ("07:20", "14:00")), ("CL", ("08:00", "13:30")),
    ("MCL", ("08:00", "13:30")), ("GC", ("07:20", "12:30")), ("MGC", ("07:20", "12:30")),
    ("SI", ("07:20", "12:25")), ("SIL", ("07:20", "12:25")), ("HG", ("07:10", "12:00")),
    ("MHG", ("07:10", "12:00")), ("ZC", ("08:30", "13:15")), ("ZL", ("08:30", "13:15")),
    ("HE", ("08:30", "13:00")), ("LE", ("08:30", "13:00")), ("MES", ("08:30", "15:00")),
])
def test_the_day_session_is_d6s_o_x_to_c_x_for_every_root(root, window) -> None:
    start, end = sd.day_session_window(root)
    assert (start.strftime("%H:%M"), end.strftime("%H:%M")) == window


def test_no_contract_e2a_recorded_is_refused_and_each_gets_its_recorded_o_x_c_x() -> None:
    table = load_frozen_tables().day_session_ct
    assert len(table) == 45  # every contract of reports/stage_e2a_vehicle_sizes.json
    assert {r: sd.day_session_window(r) for r in table} == dict(table)


@pytest.mark.parametrize("root", ["ES", "NKD", "MET", "6M", "BTC"])
def test_a_root_without_an_e2a_record_or_product_entry_is_refused(root) -> None:
    with pytest.raises(sd.StartDatesRefusal, match=root):
        sd.day_session_window(root)


def test_monthly_medians_count_ct_minutes_start_inclusive_end_exclusive() -> None:
    day = date(2025, 6, 11)
    rows = [(day, 8 * 60 + 29, BIG), (day, 8 * 60 + 30, 5), (day, 14 * 60 + 59, 7),
            (day, 15 * 60, BIG), (date(2025, 7, 9), 12 * 60, 3)]
    frame = _frame("MNQ", rows)
    got = sd.day_session_monthly_medians(frame, (time(8, 30), time(15, 0)))
    assert got == {"2025-06": 6.0, "2025-07": 3.0}


def test_monthly_medians_are_keyed_by_trade_date_not_calendar_date() -> None:
    frame = pd.DataFrame({"ts_event": [_ns(date(2021, 5, 31), 9 * 60)], "volume": [4],
                          "trade_date": ["2021-06-01"]})  # a booked-forward holiday session
    assert sd.day_session_monthly_medians(frame, (time(8, 30), time(15, 0))) == {"2021-06": 4.0}


# ------------------------------------------------------------- the builder ----
def test_d1fs_mes_medians_give_d1fs_start_dates_through_synthetic_stores(tmp_path) -> None:
    research, step2, sha = _d1f_stores(tmp_path)
    got = sd.product_start_rule("MNQ", research_path=research, step2_path=step2,
                                research_sha256=sha, window=(time(8, 30), time(15, 0)))
    e = got.entry
    assert e["v_ref"] == D1F["v_ref"] == 1763.0
    assert (e["s_x"], e["s_x_015"], e["s_x_040"]) == ("2020-02-03", "2020-01-02", "2020-03-02")
    assert e["m_star"] == {"0.25": "2020-02", "0.15": "2020-01", "0.40": "2020-03"}
    assert e["monthly_medians"] == D1F["reference_monthly_medians"] | D1F[
        "extension_monthly_medians"]
    assert e["first_trade_dates"] == D1F["extension_first_trade_dates"]
    assert e["day_session_ct"] == ["08:30", "15:00"] and e["source"] == "computed"
    assert e["step2_sha256"] == hashlib.sha256(step2.read_bytes()).hexdigest()
    assert [p for p, _ in got.inputs] == [research.as_posix(), step2.as_posix()]
    assert got.inputs[0][1] == sha


def test_the_builder_reads_timestamps_volume_and_trade_date_only(tmp_path, monkeypatch) -> None:
    research, step2, sha = _d1f_stores(tmp_path)
    seen: list[tuple[str, ...]] = []
    real = pd.read_parquet

    def spy(path, *args, columns=None, **kw):  # noqa: ANN001, ANN202
        seen.append(tuple(columns or ()))
        return real(path, *args, columns=columns, **kw)

    monkeypatch.setattr(sd.pd, "read_parquet", spy)
    sd.product_start_rule("MNQ", research_path=research, step2_path=step2, research_sha256=sha,
                          window=(time(8, 30), time(15, 0)))
    assert seen == [("ts_event", "volume", "trade_date")] * 2


def test_a_research_store_that_is_not_e2as_file_is_refused(tmp_path) -> None:
    research, step2, _ = _d1f_stores(tmp_path)
    with pytest.raises(ParquetHashMismatch):
        sd.product_start_rule("MNQ", research_path=research, step2_path=step2,
                              research_sha256="0" * 64, window=(time(8, 30), time(15, 0)))


def test_a_missing_step2_store_is_refused_by_name(tmp_path) -> None:
    research, _, sha = _d1f_stores(tmp_path)
    with pytest.raises(ConfirmationStoreMissing):
        sd.product_start_rule("MNQ", research_path=research, step2_path=tmp_path / "none.parquet",
                              research_sha256=sha, window=(time(8, 30), time(15, 0)))


def test_a_holdout_row_in_either_store_refuses_the_product(tmp_path) -> None:
    research, step2, sha = _d1f_stores(tmp_path)
    bad = pd.concat([pd.read_parquet(step2),
                     _frame("MNQ", [(date(2024, 3, 5), 9 * 60, 1)])], ignore_index=True)
    _write(bad, step2)  # an embargo (March 2024) row in the step 2 store
    with pytest.raises(HoldoutRowRefused, match="embargo"):
        sd.product_start_rule("MNQ", research_path=research, step2_path=step2,
                              research_sha256=sha, window=(time(8, 30), time(15, 0)))
    leak = pd.concat([pd.read_parquet(research),
                      _frame("MNQ", [(date(2024, 6, 5), 9 * 60, 1)])], ignore_index=True)
    sha2 = _write(leak, research)  # a holdout-2 row in the research store
    _d1f_stores(tmp_path / "again")
    with pytest.raises(HoldoutRowRefused, match="holdout-2"):
        sd.product_start_rule("MNQ", research_path=research,
                              step2_path=tmp_path / "again" / "step2" / "MNQ" / "s.parquet",
                              research_sha256=sha2, window=(time(8, 30), time(15, 0)))


def test_a_missing_reference_month_is_refused_naming_the_product(tmp_path) -> None:
    research, step2, _ = _d1f_stores(tmp_path)
    frame = pd.read_parquet(research)
    sha = _write(frame[~frame["trade_date"].str.startswith("2025-09")], research)
    with pytest.raises(sd.StartDatesRefusal, match="MNQ.*2025-09"):
        sd.product_start_rule("MNQ", research_path=research, step2_path=step2,
                              research_sha256=sha, window=(time(8, 30), time(15, 0)))


def test_no_qualifying_month_gives_an_empty_window_not_a_date(tmp_path) -> None:
    rows = []
    for month in D1F["reference_monthly_medians"]:
        rows += _inside(_reference_day(month), 1000.0)
    research = tmp_path / "r.parquet"
    sha = _write(_frame("ZN", [(d, m + 20, v) for d, m, v in rows]), research)  # 07:50.. CT
    step2 = tmp_path / "s.parquet"
    _write(_frame("ZN", [(date(2024, 2, 1), 9 * 60, 10), (date(2024, 2, 2), 9 * 60, 10)]), step2)
    got = sd.product_start_rule("ZN", research_path=research, step2_path=step2,
                                research_sha256=sha, window=(time(7, 20), time(14, 0)))
    assert got.entry["s_x"] is None and got.entry["m_star"]["0.25"] is None
    assert got.entry["monthly_medians"]["2024-02"] == 10.0


def test_mes_as_a_leg_comes_from_d1fs_pinned_record(tmp_path) -> None:
    got = sd.mes_from_d1f(REPO_ROOT)
    e = got.entry
    assert (e["s_x"], e["s_x_015"], e["s_x_040"]) == ("2020-02-03", "2020-01-02", "2020-03-02")
    assert e["v_ref"] == 1763.0 and e["source"].startswith("D.1f record")
    assert e["step2_sha256"] == (  # D.1f's MES confirmation parquet, the store S came from
        "82e256b4a7418e68fbab5e5e0d961908f7160eaac5b7ba8f05f71896f36296b8")
    assert got.inputs == (("reports/stage_d1f_step5_start_rule.json", sd.D1F_RECORD_SHA256),)
    fake = tmp_path / "reports" / "stage_d1f_step5_start_rule.json"
    fake.parent.mkdir(parents=True)
    fake.write_text(D1F_RECORD.read_text(encoding="utf-8").replace("2020-02-03", "2020-02-04"),
                    encoding="utf-8")
    with pytest.raises(sd.StartDatesRefusal, match="sha256"):
        sd.mes_from_d1f(tmp_path)


# ----------------------------------------------------------------- set roots ----
def test_the_ml_set_is_the_31_price_path_contracts() -> None:
    from ml_route.constants import PRICE_PATH_CONTRACTS

    roots, inputs = sd.set_roots("ML")
    assert roots == tuple(sorted(PRICE_PATH_CONTRACTS)) and len(roots) == 31
    assert inputs == ()


def test_a_cluster_set_is_its_frozen_vehicles_and_every_leg_its_members_read(
        tmp_path, monkeypatch) -> None:
    from screening.stage_e_freeze import MemberDecl, write_cluster_freeze
    from strategy.stage_e.interface import LegSpec
    from tests._stage_e_synthetic import install_member_package

    module = install_member_package(tmp_path, monkeypatch, cluster="k2")
    sha = write_cluster_freeze("K2", [MemberDecl("K2-a", 1, module, "make_member",
                                                 (LegSpec("ZN", True), LegSpec("MES", False)))],
                               root=tmp_path)
    roots, inputs = sd.set_roots("K2", root=tmp_path)
    assert roots == ("MES", "TN", "UB", "ZB", "ZF", "ZN", "ZT")
    assert inputs == (("reports/stage_e_k2_member_freeze.json", sha),)


def test_a_cluster_without_a_member_freeze_and_an_unknown_set_are_refused(tmp_path) -> None:
    from screening.stage_e_freeze import ClusterFreezeError

    with pytest.raises(ClusterFreezeError, match="does not exist"):
        sd.set_roots("K5", root=tmp_path)
    with pytest.raises(sd.StartDatesRefusal, match="K9"):
        sd.set_roots("K9", root=tmp_path)


# ------------------------------------------------------ the set file (entry) ----
@pytest.fixture
def one_set(tmp_path, monkeypatch):
    """A repository with D.1f's record and synthetic MNQ stores; the set is (MES, MNQ)."""
    research, step2, sha = _d1f_stores(tmp_path)
    (tmp_path / "reports").mkdir(exist_ok=True)
    shutil.copyfile(D1F_RECORD, tmp_path / "reports" / D1F_RECORD.name)
    monkeypatch.setattr(sd, "_frozen_tables", lambda: _tables_with(MNQ=sha))
    monkeypatch.setattr(sd, "set_roots", lambda s, root=REPO_ROOT, tables=None: (
        ("MES", "MNQ"), (("reports/x.json", "f" * 64),)))
    monkeypatch.setattr(sd, "research_parquet_path", lambda r, base: research)
    monkeypatch.setattr(sd, "step2_parquet_path", lambda r, base: step2)
    monkeypatch.setattr(harness_freeze, "preflight", lambda expected: expected)
    return tmp_path


def test_run_set_writes_the_file_once_read_only_and_the_loader_reads_it(one_set) -> None:
    path = sd.run_set("K1", harness_sha256=HARNESS, research_root=one_set,
                      step2_root=one_set, root=one_set)
    assert path == one_set / "reports" / "stage_e_start_rule_K1.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    assert doc["schema"] == "stage_e_start_rule/2" and doc["set"] == "K1"
    assert doc["harness_sha256"] == HARNESS and doc["created_pdt"].endswith(("-07:00", "-08:00"))
    assert "OC-S" in doc["day_session"] and doc["day_session"].startswith("D6 (O_X, C_X)")
    assert set(doc["products"]) == {"MES", "MNQ"}
    assert {k for k in doc["products"]["MNQ"]} >= {"s_x", "s_x_015", "s_x_040", "v_ref",
                                                   "monthly_medians"}
    assert {i["path"] for i in doc["inputs"]} >= {"reports/x.json",
                                                  "reports/stage_d1f_step5_start_rule.json"}
    assert not os.stat(path).st_mode & (stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH)
    assert sd.load_start_dates(one_set) == {"MES": date(2020, 2, 3), "MNQ": date(2020, 2, 3)}
    with pytest.raises(sd.StartDatesRefusal, match="already exists"):
        sd.run_set("K1", harness_sha256=HARNESS, research_root=one_set, step2_root=one_set,
                   root=one_set)


def test_the_entry_refuses_when_preflight_raises_before_reading_anything(one_set, monkeypatch
                                                                         ) -> None:
    def refuse(expected: str) -> str:
        raise HarnessFreezeError("Stage E harness preflight refused: planted")

    monkeypatch.setattr(harness_freeze, "preflight", refuse)
    monkeypatch.setattr(sd, "set_roots", lambda *a, **k: pytest.fail("read the set"))
    monkeypatch.setattr(sd, "_read_columns", lambda *a, **k: pytest.fail("read a store"))
    with pytest.raises(HarnessFreezeError, match="planted"):
        sd.run_set("K1", harness_sha256=HARNESS, research_root=one_set, step2_root=one_set,
                   root=one_set)
    assert not (one_set / "reports" / "stage_e_start_rule_K1.json").exists()


def test_refused_roots_refuse_the_whole_set_before_any_bar_is_read(one_set,
                                                                   monkeypatch) -> None:
    monkeypatch.setattr(sd, "set_roots", lambda s, root=REPO_ROOT, tables=None: (
        ("ES", "MNQ", "NKD"), ()))
    monkeypatch.setattr(sd, "_read_columns", lambda *a, **k: pytest.fail("read a store"))
    with pytest.raises(sd.StartDatesRefusal, match="2 root.*refused whole.*ES: .*NKD: "):
        sd.build_set("K5", harness_sha256=HARNESS, research_root=one_set,
                     step2_root=one_set, root=one_set)


def test_the_cli_requires_the_hash_and_a_set_and_calls_the_preflight_first(monkeypatch) -> None:
    with pytest.raises(SystemExit):
        sd.main(["--set", "K1"])
    with pytest.raises(SystemExit):
        sd.main(["--harness-sha256", HARNESS])
    seen = []

    def refuse(expected: str) -> str:
        seen.append(expected)
        raise HarnessFreezeError("refused")

    monkeypatch.setattr(harness_freeze, "preflight", refuse)
    monkeypatch.setattr("compute.platform.lower_priority", lambda: None)
    with pytest.raises(HarnessFreezeError):
        sd.main(["--harness-sha256", HARNESS, "--set", "ML"])
    assert seen == [HARNESS]


# ---------------------------------------------------------------- the loader ----
def test_no_file_means_every_root_is_missing_by_the_runners_class(tmp_path) -> None:
    assert dict(sd.load_start_dates(tmp_path)) == {}
    with pytest.raises(StartRuleMissing, match="no frozen S_X for ZN"):
        sd.start_date("ZN", tmp_path)


def test_the_loader_merges_every_set_file_and_records_where_each_date_came_from(tmp_path) -> None:
    k2 = _put(tmp_path, "K2", {"ZN": "2019-05-06", "ZB": "2019-06-03"})
    ml = _put(tmp_path, "ML", {"ZN": "2019-05-06", "NQ": "2019-05-06"})
    assert dict(sd.load_start_dates(tmp_path)) == {
        "NQ": date(2019, 5, 6), "ZB": date(2019, 6, 3), "ZN": date(2019, 5, 6)}
    assert sd.start_date("ZB", tmp_path) == date(2019, 6, 3)
    dates, provenance = sd.start_dates_for(("ZN", "ZB"), tmp_path)
    assert dates == {"ZN": date(2019, 5, 6), "ZB": date(2019, 6, 3)}
    sha = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (k2, ml)}
    assert provenance["ZN"] == {"s_x": "2019-05-06", "step2_sha256": "a" * 64, "files": [
        {"path": "reports/stage_e_start_rule_K2.json", "sha256": sha[k2.name]},
        {"path": "reports/stage_e_start_rule_ML.json", "sha256": sha[ml.name]}]}


def test_two_files_giving_one_root_different_dates_are_refused(tmp_path) -> None:
    _put(tmp_path, "K2", {"ZN": "2019-05-06"})
    _put(tmp_path, "ML", {"ZN": "2019-06-03"})
    with pytest.raises(StartRuleConflict, match=r"ZN.*\['s_x', .*K2.*ML"):
        sd.load_start_dates(tmp_path)
    with pytest.raises(RunnerRefusal):
        sd.start_date("NQ", tmp_path)


def test_two_files_agreeing_on_s_x_but_not_on_v_ref_a_median_or_the_store_are_refused(
        tmp_path) -> None:
    _put(tmp_path, "K2", {"ZN": consistent_entry("2019-06-01")})
    _put(tmp_path, "ML", {"ZN": consistent_entry("2019-06-01", v_ref=100.5)})
    with pytest.raises(StartRuleConflict, match=r"ZN.*'v_ref'"):
        sd.load_start_dates(tmp_path)
    _put(tmp_path, "ML", {"ZN": consistent_entry("2019-06-01", overrides={"2019-05": 3.0})})
    with pytest.raises(StartRuleConflict, match=r"ZN.*\['monthly_medians'\]"):
        sd.start_date("ZN", tmp_path)
    _put(tmp_path, "ML", {"ZN": consistent_entry("2019-06-01", step2_sha256="b" * 64)})
    with pytest.raises(StartRuleConflict, match=r"ZN.*\['step2_sha256'\]"):
        sd.start_date("ZN", tmp_path)
    _put(tmp_path, "ML", {"ZN": consistent_entry("2019-06-01")})
    assert sd.start_date("ZN", tmp_path) == date(2019, 6, 1)  # identical: accepted


# --------------------------- review F-3 (a): an entry must follow from its own data ----
def test_e1_an_s_x_that_contradicts_its_own_medians_is_refused(tmp_path) -> None:
    """The review's E1: medians giving S_X = 2019-05-06, s_x written as 2023-06-15."""
    entry = consistent_entry("2019-05-06")
    assert entry["s_x"] == "2019-05-06"
    doctored = entry | {"s_x": "2023-06-15"}
    with pytest.raises(StartRuleInconsistent, match=r"ZN: \['s_x'\] do not follow"):
        sd.write_start_rule(_doc("K2", {"ZN": doctored}), root=tmp_path)
    assert not (tmp_path / "reports" / "stage_e_start_rule_K2.json").exists()
    _put(tmp_path, "K2", {"ZN": doctored})  # written by hand, around the writer
    with pytest.raises(StartRuleInconsistent, match="2023-06-15"):
        sd.start_dates_for(("ZN",), tmp_path)
    with pytest.raises(StartRuleInvalid):  # an inconsistent file is an invalid one
        sd.start_date("ZN", tmp_path)


@pytest.mark.parametrize("field, value", [
    ("v_ref", 99.0), ("s_x_015", "2019-06-01"), ("s_x_040", None),
    ("m_star", {"0.25": "2019-05", "0.15": "2019-05", "0.40": "2019-06"}),
])
def test_a_recorded_v_ref_sensitivity_date_or_m_star_that_does_not_re_run_is_refused(
        tmp_path, field, value) -> None:
    _put(tmp_path, "K2", {"ZN": consistent_entry("2019-05-06") | {field: value}})
    with pytest.raises(StartRuleInconsistent, match=rf"\['{field}'\] do not follow"):
        sd.load_start_dates(tmp_path)


def test_medians_that_cannot_re_run_the_rule_are_refused(tmp_path) -> None:
    entry = consistent_entry("2019-05-06")
    medians = {m: v for m, v in entry["monthly_medians"].items() if m != "2025-09"}
    _put(tmp_path, "K2", {"ZN": entry | {"monthly_medians": medians}})
    with pytest.raises(StartRuleInconsistent, match="2025-09"):
        sd.load_start_dates(tmp_path)


def test_each_entry_keeps_the_step2_store_sha256_it_was_computed_from(tmp_path) -> None:
    _put(tmp_path, "K2", {"ZN": consistent_entry("2019-06-01", step2_sha256="c" * 64)})
    _, provenance = sd.start_dates_for(("ZN",), tmp_path)
    assert provenance["ZN"]["step2_sha256"] == "c" * 64
    assert sd.load_start_entries(tmp_path)["ZN"].step2_sha256 == "c" * 64


def test_an_empty_window_is_named_and_is_still_a_start_rule_missing(tmp_path) -> None:
    _put(tmp_path, "K7", {"MBT": None})
    assert dict(sd.load_start_dates(tmp_path)) == {}
    with pytest.raises(StartWindowEmpty, match="MBT.*empty"):
        sd.start_date("MBT", tmp_path)
    assert issubclass(StartWindowEmpty, StartRuleMissing)
    with pytest.raises(StartWindowEmpty):
        sd.start_dates_for(("MBT",), tmp_path)


def test_allow_empty_leaves_an_empty_window_out_of_the_dates_but_keeps_its_provenance(
        tmp_path) -> None:
    _put(tmp_path, "K7", {"MBT": None})
    _put(tmp_path, "K2", {"ZN": "2019-05-06"})
    dates, provenance = sd.start_dates_for(("MBT", "ZN"), tmp_path, allow_empty=True)
    assert dates == {"ZN": date(2019, 5, 6)}
    assert provenance["MBT"]["s_x"] is None
    assert provenance["MBT"]["files"][0]["path"] == "reports/stage_e_start_rule_K7.json"
    with pytest.raises(StartRuleMissing, match="NQ"):  # a missing root still refuses
        sd.start_dates_for(("NQ",), tmp_path, allow_empty=True)


def test_start_dates_for_names_every_missing_root(tmp_path) -> None:
    _put(tmp_path, "K2", {"ZN": "2019-05-06"})
    with pytest.raises(StartRuleMissing, match=r"\['MES', 'ZB'\]"):
        sd.start_dates_for(("ZN", "MES", "ZB"), tmp_path)


@pytest.mark.parametrize("mutate, match", [
    (lambda d: d | {"schema": "stage_e_start_rule/1"}, "schema"),
    (lambda d: d | {"set": "K3"}, "set"),
    (lambda d: d | {"products": {}}, "no products"),
    (lambda d: d | {"products": {"ZN": {"s_x": "2024-03-01"}}}, "outside"),
    (lambda d: d | {"products": {"ZN": {"s_x": "2019-5-6"}}}, "ZN"),
    (lambda d: d | {"products": {"ZN": {"v_ref": 1.0}}}, "s_x"),
    (lambda d: d | {"products": {"ZN": {"s_x": None, "monthly_medians": {}}}}, "v_ref"),
    (lambda d: d | {"products": {"ZN": {"s_x": None, "v_ref": 0, "monthly_medians": {}}}},
     "v_ref"),
    (lambda d: d | {"products": {"ZN": {"s_x": None, "v_ref": True, "monthly_medians": {}}}},
     "v_ref"),
    (lambda d: d | {"products": {"ZN": {"s_x": None, "v_ref": 1.0}}}, "monthly_medians"),
    (lambda d: d | {"products": {"ZN": {"s_x": None, "v_ref": 1.0,
                                         "monthly_medians": {"2019-5": 1.0}}}}, "2019-5"),
    (lambda d: d | {"products": {"ZN": {"s_x": None, "v_ref": 1.0,
                                         "monthly_medians": {"2019-05": -1.0}}}}, "2019-05"),
    (lambda d: d | {"products": {"ZN": {"s_x": None, "v_ref": 1.0,
                                         "monthly_medians": {"2024-03": 1.0}}}}, "2024-03"),
    (lambda d: d | {"products": {"ZN": {k: v for k, v in consistent_entry(None).items()
                                         if k != "first_trade_dates"}}}, "first_trade_dates"),
    (lambda d: d | {"products": {"ZN": consistent_entry(None) | {"step2_sha256": None}}},
     "step2_sha256"),
])
def test_an_invalid_file_is_refused_by_name(tmp_path, mutate, match) -> None:
    path = tmp_path / "reports" / "stage_e_start_rule_K2.json"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(mutate(_doc("K2", {"ZN": "2019-05-06"}))), encoding="utf-8")
    with pytest.raises(StartRuleInvalid, match=match):
        sd.load_start_dates(tmp_path)


def test_a_file_whose_name_is_not_a_set_or_is_not_json_is_refused(tmp_path) -> None:
    stray = _put(tmp_path, "K2", {"ZN": "2019-05-06"})
    stray.rename(stray.with_name("stage_e_start_rule_K2_copy.json"))
    with pytest.raises(StartRuleInvalid, match="K2_copy"):
        sd.load_start_dates(tmp_path)
    stray.with_name("stage_e_start_rule_K2_copy.json").unlink()
    stray.write_text("{not json", encoding="utf-8")
    with pytest.raises(StartRuleInvalid, match="JSON"):
        sd.load_start_dates(tmp_path)


def test_the_writer_refuses_a_document_the_loader_would_refuse(tmp_path) -> None:
    with pytest.raises(StartRuleInvalid, match="schema"):
        sd.write_start_rule(_doc("K2", {"ZN": "2019-05-06"}) | {"schema": "x"}, root=tmp_path)
    assert not (tmp_path / "reports" / "stage_e_start_rule_K2.json").exists()
