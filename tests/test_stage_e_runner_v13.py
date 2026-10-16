"""Harness v13 (Stage E.22 Part A) on the generalized runner, synthetic data only:
N1 a declared price path in the confirmation window and the supply count (MGC on GC's bars, the
micro's tick value and costs), N3 MES as a confirmation leg (D.1f's store under the research root,
S = 2020-02-03, its splices in the blackout union), N4 declared not-run members, R1 the run-once
marker, R2 the dry run."""

from __future__ import annotations

import hashlib
import json
import os
import stat
from dataclasses import replace
from datetime import date, timedelta
from pathlib import Path
from types import MappingProxyType

import pytest

import screening.stage_e_runner as runner
from data import stage_e_bars as sb
from data.step2_store import step2_parquet_path
from screening import harness_freeze, stage_e_freeze
from screening import stage_e_start_dates as sd
from screening.stage_e_freeze import MemberDecl, write_cluster_freeze
from screening.stage_e_frozen import leg_inputs
from screening.stage_e_rules import ReleaseCalendar
from strategy.stage_e.interface import LegSpec
from tests._stage_e_synthetic import (
    MEMBER_SOURCE,
    install_member_package,
    product_frame,
    ts_ns,
    write_parquet,
)
from tests.test_stage_e_start_dates import consistent_entry

HARNESS = "a" * 64
BASE = 15000  # GC/MGC price in ticks (0.10): 1,500.0


def _weekdays(first: date, n: int) -> tuple[date, ...]:
    out, d = [], first
    while len(out) < n:
        if d.weekday() < 5:
            out.append(d)
        d += timedelta(days=1)
    return tuple(out)


RESEARCH_DAYS = _weekdays(date(2025, 6, 2), 8)
CONF_DAYS = _weekdays(date(2023, 6, 5), 8)
MES_ERA = _weekdays(date(2020, 1, 27), 15)  # 2020-01-27 .. 2020-02-14


def _install(tmp: Path, monkeypatch, root: str, signals: tuple[str, ...] = (),
             name: str = "synth") -> str:
    """The synthetic member trading ``root`` (entry 9:10, exit 9:40), with trading windows for
    ``signals`` too."""
    module = install_member_package(tmp, monkeypatch, name=name)
    source = MEMBER_SOURCE.format(entry=(9, 10), exit=(9, 40), early=False)
    source = source.replace('ROOT = "ZN"', f'ROOT = "{root}"\nSIGNALS = {signals!r}')
    source = source.replace("default_factory=lambda: {ROOT:", "default_factory=lambda: {**{s: ("
                            "TradingInterval(time(9, 0), time(10, 0)),) for s in SIGNALS}, ROOT:")
    (tmp / "strategy" / "members" / "k1" / f"{name}.py").write_text(source, encoding="utf-8")
    return module


@pytest.fixture
def repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """A synthetic repository: frozen K1 members, research stores, a release calendar, the
    runner's loaders pointed at tmp_path; ``members`` = [(label, legs)]."""
    def build(members: list[tuple[str, tuple[LegSpec, ...]]], *, signals=("MES",)):
        decls = []
        research = tmp_path / "research"
        shas = {}
        for i, (label, legs) in enumerate(members, start=1):
            traded = next(leg.root for leg in legs if leg.traded)
            module = _install(tmp_path, monkeypatch, traded, signals, name=f"m{i}")
            decls.append(MemberDecl(label, i, module, "make_member", legs))
            for leg in legs:
                path = sb.research_parquet_path(leg.root, research)
                if not path.exists():
                    write_parquet(product_frame(leg.root, RESEARCH_DAYS, 3, start=(9, 0),
                                                end=(10, 0), base_ticks=BASE), path,
                                  {"rolls": []})
                shas[leg.root] = hashlib.sha256(path.read_bytes()).hexdigest()
        write_cluster_freeze("K1", decls, root=tmp_path)
        monkeypatch.setattr(runner, "load_cluster_freeze",
                            lambda c: stage_e_freeze.load_cluster_freeze(c, root=tmp_path))
        monkeypatch.setattr(runner, "verify_cluster_code",
                            lambda f: stage_e_freeze.verify_cluster_code(f, root=tmp_path))
        monkeypatch.setattr(runner, "_legs_inputs", lambda legs: {
            leg.root: replace(leg_inputs(leg.root, traded=leg.traded),
                              research_parquet_sha256=shas[leg.root]) for leg in legs})
        monkeypatch.setattr(runner, "load_release_calendar", lambda: ReleaseCalendar(
            MappingProxyType({}), (), date(2019, 5, 1), date(2026, 6, 19), "c" * 64, "test"))
        monkeypatch.setattr(harness_freeze, "preflight", lambda expected: expected)
        return {"research_root": research, "step2_root": tmp_path / "step2",
                "out_dir": tmp_path / "out"}
    return build


def _store(root: str, days, base: Path, rolls=(), extra_rows=()) -> str:
    """A step 2 store of ``root`` (9:00-10:00 CT bars); a 1-tick rise at 9:30 each day."""
    path = step2_parquet_path(root, base)
    step = {(d, 9 * 60 + 30): (BASE + 1,) * 4 for d in days} | {
        (d, 9 * 60): (BASE,) * 4 for d in days}  # back to BASE at each day's first bar
    frame = product_frame(root, days, 5, start=(9, 0), end=(10, 0), base_ticks=BASE,
                          vol_ticks=0.0, path_ticks=step)
    write_parquet(frame, path, {"rolls": [{"ts_ns": ns} for ns in rolls]})
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _start_files(tmp: Path, monkeypatch, **sets: dict[str, tuple[str | None, str]]) -> None:
    """sets: SET -> {root: (s_x, step2_sha256)}; the runner's loader pointed at tmp."""
    for set_id, products in sets.items():
        doc = {"schema": sd.SCHEMA, "set": set_id, "inputs": [], "harness_sha256": HARNESS,
               "created_pdt": "2026-10-16T01:00:00-07:00",
               "products": {r: consistent_entry(s, root=r, step2_sha256=sha)
                            for r, (s, sha) in products.items()}}
        path = tmp / "reports" / f"stage_e_start_rule_{set_id}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(doc), encoding="utf-8")
    monkeypatch.setattr(runner, "_start_dates", lambda roots, allow_empty=False:
                        sd.start_dates_for(roots, root=tmp, allow_empty=allow_empty))


MGC = ("K1-mgc-01 MGC", (LegSpec("MGC", True),))


def _conf(paths: dict, label: str = MGC[0]) -> dict:
    return runner.screen_member("K1", label, None, None, "confirmation",
                                harness_sha256=HARNESS, **paths)


# ======================================================= N1: price path ====
def test_n1_a_mapped_vehicle_runs_on_the_path_store_with_the_path_s_x_and_its_own_ticks(
        repo, tmp_path, monkeypatch) -> None:
    paths = repo([MGC])
    gc_sha = _store("GC", CONF_DAYS, paths["step2_root"])
    _start_files(tmp_path, monkeypatch, K5={"MGC": (None, "e" * 64)},  # K5 keeps MGC null
                 K8={"GC": (CONF_DAYS[1].isoformat(), gc_sha)})
    rec = _conf(paths)  # the pinned declaration of the repository: MGC -> GC
    assert rec["status"] == "run" and rec["price_path"] == {"MGC": "GC"}
    assert rec["price_path_declaration"] == {"path": "reports/stage_e22_price_paths.json",
                                             "sha256": sd.PRICE_PATHS_SHA256}
    assert rec["s_x"] == {"MGC": CONF_DAYS[1].isoformat()}  # the path's S_X, keyed by MGC
    assert set(rec["start_rule"]) == {"GC"} and rec["start_rule"]["GC"]["step2_sha256"] == gc_sha
    assert rec["bars"]["MGC"]["path"] == step2_parquet_path("GC", Path("x")).name
    assert rec["bars"]["MGC"]["sha256"] == gc_sha
    assert rec["window_dates"]["first"] == CONF_DAYS[1] and rec["series"]["vehicle"] == "MGC"
    trips = json.loads((paths["out_dir"] / "K1_K1-mgc-01_MGC_confirmation_trips.json")
                       .read_text(encoding="utf-8"))["trips"]
    assert trips and {t["gross_cents"] for t in trips} == {100}  # 1 GC tick at MGC's $1.00
    mgc = leg_inputs("MGC", traded=True)
    assert mgc.tick_value_cents == 100 and sb.product("GC").tick_value_usd == 10  # not GC's $10


def test_n1_the_supply_count_uses_the_path_root_and_the_research_window_does_not(
        repo, tmp_path, monkeypatch) -> None:
    from screening import stage_e_stats as st

    paths = repo([MGC])
    gc_sha = _store("GC", CONF_DAYS, paths["step2_root"])
    _start_files(tmp_path, monkeypatch, K5={"MGC": (None, "e" * 64)},
                 K8={"GC": (CONF_DAYS[2].isoformat(), gc_sha)})
    seen = []
    monkeypatch.setattr(st, "power_check", lambda s, c, o, supply: seen.append(supply) or "ok")
    rec = runner.screen_member("K1", MGC[0], None, None, "research", harness_sha256=HARNESS,
                               **paths)
    assert seen == [len(CONF_DAYS) - 2]
    assert rec["power"]["price_path"] == {"MGC": "GC"} and "GC" in rec["power"]["start_rule"]
    assert rec["bars"]["MGC"]["path"] == sb.research_parquet_path("MGC", Path("x")).name
    assert "price_path" not in rec and "s_x" not in rec  # the screened series: MGC's own bars


def test_n1_an_unmapped_micro_still_reads_its_own_empty_window(repo, tmp_path,
                                                               monkeypatch) -> None:
    paths = repo([MGC])
    _start_files(tmp_path, monkeypatch, K5={"MGC": (None, "e" * 64)})
    monkeypatch.setattr(runner, "_price_paths", lambda: sd.PricePaths(
        MappingProxyType({}), "reports/stage_e22_price_paths.json", "9" * 64))
    with pytest.raises(runner.StartWindowEmpty, match="MGC"):
        _conf(paths)


def test_n1_a_declaration_that_is_not_the_pinned_file_refuses_the_run(repo, tmp_path,
                                                                     monkeypatch) -> None:
    paths = repo([MGC])
    gc_sha = _store("GC", CONF_DAYS, paths["step2_root"])
    _start_files(tmp_path, monkeypatch, K8={"GC": (CONF_DAYS[1].isoformat(), gc_sha)})
    monkeypatch.setattr(sd, "price_paths", lambda: sd.load_price_paths(
        sd.REPO_ROOT, expected_sha256="0" * 64))  # the repository's file is not this pin
    with pytest.raises(runner.PricePathInvalid, match="not the pinned"):
        _conf(paths)
    rec = runner.screen_member("K1", MGC[0], None, None, "research", harness_sha256=HARNESS,
                               **paths)
    assert rec["power"]["status"] == "not_run"  # research: recorded by name, never guessed
    assert rec["power"]["reason"].startswith("PricePathInvalid")


# ================================================ N3: MES as a signal leg ====
def _mes_store(research: Path, days, rolls) -> str:
    """D.1f's MES layout under the research root, with one 16:59 CT closure print labelled with
    the session it follows (re-booked by the rulings below)."""
    frame = product_frame("MES", days, 9, start=(9, 0), end=(10, 0), base_ticks=10000)
    row = frame.iloc[[-1]].copy()
    row["ts_event"], row["trade_date"] = ts_ns(days[-2], 16, 59), days[-2].isoformat()
    frame = (__import__("pandas").concat([frame, row], ignore_index=True)
             .sort_values("ts_event").reset_index(drop=True))
    path = sb.mes_confirmation_path(research)
    write_parquet(frame, path, {"rolls": [{"ts_ns": ns} for ns in rolls]})
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _mes_rulings(tmp: Path, store_sha: str, day: date, booked: date, monkeypatch) -> None:
    ns = ts_ns(day, 16, 59)
    path = tmp / "mes_rulings.json"
    path.write_text(json.dumps({"schema": sb.MES_CLOSURE_RULINGS_SCHEMA, "ruling": "test",
                                "store": {"sha256": store_sha}, "entries": [
                                    {"root": "MES", "ts_event_ns": ns, "ct": sb._ct_str(ns),
                                     "store_label": day.isoformat(),
                                     "trade_date": booked.isoformat(),
                                     "ruling": "rebook_and_flag"}]}), encoding="utf-8")
    monkeypatch.setattr(sb, "MES_CLOSURE_RULINGS_PATH", path)
    monkeypatch.setattr(sb, "MES_CLOSURE_RULINGS_SHA256",
                        hashlib.sha256(path.read_bytes()).hexdigest())


FLIGHT = ("K1-flight-01 MGC", (LegSpec("MGC", True), LegSpec("MES", False)))


def test_n3_an_mes_signal_leg_starts_at_2020_02_03_and_its_blackout_joins_the_union(
        repo, tmp_path, monkeypatch) -> None:
    paths = repo([FLIGHT])
    gc_sha = _store("GC", MES_ERA, paths["step2_root"])
    splice = date(2020, 2, 12)  # MES's own roll: blackout 2020-02-10, 02-11, 02-12
    mes_sha = _mes_store(paths["research_root"], MES_ERA, [ts_ns(splice, 9, 0)])
    _mes_rulings(tmp_path, mes_sha, MES_ERA[-2], MES_ERA[-1], monkeypatch)
    _start_files(tmp_path, monkeypatch, K8={"GC": (MES_ERA[0].isoformat(), gc_sha),
                                            "MES": ("2020-02-03", mes_sha)})
    rec = _conf(paths, FLIGHT[0])
    assert rec["status"] == "run" and rec["s_x"] == {"MGC": MES_ERA[0].isoformat(),
                                                     "MES": "2020-02-03"}
    assert rec["window_dates"]["first"] == date(2020, 2, 3)
    blackout = {date(2020, 2, 10), date(2020, 2, 11), date(2020, 2, 12)}
    window = [d for d in MES_ERA if d >= date(2020, 2, 3) and d not in blackout]
    assert rec["window_dates"]["n"] == len(window)
    assert rec["bars"]["MES"]["path"] == sb.MES_CONFIRMATION_NAME
    assert rec["bars"]["MES"]["sha256"] == mes_sha and rec["bars"]["MES"]["closure_bars"] == 1
    assert rec["price_path"] == {"MGC": "GC"}
    supply, meta = runner.confirmation_supply_days(FLIGHT[1], paths["step2_root"],
                                                   paths["research_root"])
    assert supply == len(window) and meta["price_path"] == {"MGC": "GC"}


def test_n3_mes_without_the_research_root_or_with_another_store_refuses(
        repo, tmp_path, monkeypatch) -> None:
    paths = repo([FLIGHT])
    gc_sha = _store("GC", MES_ERA, paths["step2_root"])
    mes_sha = _mes_store(paths["research_root"], MES_ERA, [])
    _mes_rulings(tmp_path, mes_sha, MES_ERA[-2], MES_ERA[-1], monkeypatch)
    _start_files(tmp_path, monkeypatch, K8={"GC": (MES_ERA[0].isoformat(), gc_sha),
                                            "MES": ("2020-02-03", "f" * 64)})
    with pytest.raises(sb.ParquetHashMismatch):
        _conf(paths, FLIGHT[0])
    with pytest.raises(sb.ConfirmationStoreMissing, match="research root"):
        runner.confirmation_supply_days(FLIGHT[1], paths["step2_root"])


# ===================================================== N4: declared not run ====
WK = ("K1-wk-01 MNQ", (LegSpec("MNQ", True), LegSpec("MBT", False)))
ZN = ("K1-zn-01 ZN", (LegSpec("ZN", True),))


def _declaration(tmp: Path, members: dict) -> Path:
    path = tmp / "untestable.json"
    path.write_text(json.dumps({"schema": runner.UNTESTABLE_SCHEMA, "cluster": "K1",
                                "members": members}), encoding="utf-8")
    return path


def _zn_ready(paths: dict, tmp: Path, monkeypatch) -> None:
    zn_sha = _store("ZN", CONF_DAYS, paths["step2_root"])
    _start_files(tmp, monkeypatch, K2={"ZN": (CONF_DAYS[0].isoformat(), zn_sha)})


def test_n4_a_declared_member_gets_a_not_run_record_and_the_cluster_continues(
        repo, tmp_path, monkeypatch) -> None:
    paths = repo([WK, ZN], signals=("MBT",))
    _zn_ready(paths, tmp_path, monkeypatch)
    decl = _declaration(tmp_path, {WK[0]: {
        "label": "untestable on owned data", "missing_leg": "MBT",
        "reason": "BTC full-size history for the MBT signal path is not owned"}})
    out = runner.screen_cluster("K1", "confirmation", harness_sha256=HARNESS, **paths,
                                untestable=decl)
    assert out["members"] == [WK[0], ZN[0]] and list(out["not_run_members"]) == [WK[0]]
    rec = json.loads((paths["out_dir"] / "K1_K1-wk-01_MNQ_confirmation.json")
                     .read_text(encoding="utf-8"))
    assert rec["status"] == "not_run" and rec["series"] is None and rec["power"] is None
    assert rec["labels"] == ["untestable on owned data"] and rec["missing_leg"] == "MBT"
    assert rec["not_run_declaration"]["sha256"] == hashlib.sha256(decl.read_bytes()).hexdigest()
    assert rec["harness_sha256"] == HARNESS and rec["ordinal"] == 1 and "s_x" not in rec
    zn = json.loads((paths["out_dir"] / "K1_K1-zn-01_ZN_confirmation.json")
                    .read_text(encoding="utf-8"))
    assert zn["status"] == "run"


def test_n4_an_undeclared_refusal_still_aborts_the_cluster(repo, tmp_path, monkeypatch) -> None:
    paths = repo([WK, ZN], signals=("MBT",))
    _zn_ready(paths, tmp_path, monkeypatch)
    with pytest.raises(runner.StartRuleMissing, match="NQ"):  # MNQ -> NQ has no entry here
        runner.screen_cluster("K1", "confirmation", harness_sha256=HARNESS, **paths)
    assert not (paths["out_dir"] / "K1_confirmation_cluster.json").exists()


@pytest.mark.parametrize(("spec", "match"), [
    ({"label": "untestable on owned data", "missing_leg": "BTC", "reason": "x"}, "frozen legs"),
    ({"label": "untestable", "missing_leg": "MBT", "reason": "x"}, "is not one of"),
    ({"label": "untestable on owned data", "missing_leg": "MBT", "reason": " "}, "reason"),
    ({"label": "inconclusive by design", "reason": "n_b > supply"}, "exactly"),
])
def test_n4_a_bad_declaration_is_refused(repo, tmp_path, spec: dict, match: str) -> None:
    paths = repo([WK, ZN], signals=("MBT",))
    with pytest.raises(runner.RunnerRefusal, match=match):
        runner.screen_cluster("K1", "confirmation", harness_sha256=HARNESS, **paths,
                              untestable=_declaration(tmp_path, {WK[0]: spec}))
    with pytest.raises(runner.RunnerRefusal, match="confirmation window only"):
        runner.screen_cluster("K1", "research", harness_sha256=HARNESS, **paths,
                              untestable=_declaration(tmp_path, {WK[0]: {
                                  "label": "inconclusive by design", "missing_leg": None,
                                  "reason": "n_b > supply"}}))


# ================================================== R1: the run-once marker ====
def _once(paths: dict, tmp: Path, **kw) -> dict:
    return runner.run_confirmation_once("K1", harness_sha256=HARNESS, **paths,
                                        marker=tmp / "RUN_ONCE.json", **kw)


def test_r1_the_marker_is_written_read_only_before_any_bar_is_read(repo, tmp_path,
                                                                   monkeypatch) -> None:
    paths = repo([ZN])
    _zn_ready(paths, tmp_path, monkeypatch)
    lst = _write_list(tmp_path, [_list_trial(1, ZN[0], "ZN")], {"ZN": CONF_DAYS[0]})
    marker = tmp_path / "RUN_ONCE.json"
    real = runner._load_frames

    def frames_after_marker(*a, **k):  # noqa: ANN002, ANN003, ANN202
        assert marker.exists(), "a bar was read before the run-once marker"
        return real(*a, **k)

    monkeypatch.setattr(runner, "_load_frames", frames_after_marker)
    out = _once(paths, tmp_path, list_path=lst)
    assert out["members"] == [ZN[0]]
    body = json.loads(marker.read_text(encoding="utf-8"))
    assert stat.S_IMODE(os.stat(marker).st_mode) == 0o444
    assert body["cluster"] == "K1" and body["harness_sha256"] == HARNESS
    assert body["members"] == 1 and body["list"]["sha256"] == hashlib.sha256(
        lst.read_bytes()).hexdigest()
    assert body["cluster_freeze_sha256"] and body["created_utc"]
    with pytest.raises(runner.RunOnceRefusal, match="exists"):
        _once(paths, tmp_path)


def test_r1_a_present_marker_refuses_before_the_preflight(repo, tmp_path, monkeypatch) -> None:
    paths = repo([ZN])
    (tmp_path / "RUN_ONCE.json").write_text("{}", encoding="utf-8")
    monkeypatch.setattr(harness_freeze, "preflight", lambda e: pytest.fail("preflight ran"))
    with pytest.raises(runner.RunOnceRefusal, match="exists"):
        _once(paths, tmp_path)


def test_r1_a_resolution_refusal_writes_no_marker(repo, tmp_path, monkeypatch) -> None:
    paths = repo([ZN])
    zn_sha = _store("ZN", CONF_DAYS, paths["step2_root"])
    _start_files(tmp_path, monkeypatch, K2={"ZN": (CONF_DAYS[0].isoformat(), "0" * 64)})
    with pytest.raises(sb.ParquetHashMismatch):  # the store is not the start rule's
        _once(paths, tmp_path)
    assert not (tmp_path / "RUN_ONCE.json").exists() and zn_sha


def test_r1_an_exception_after_the_marker_writes_stopped_beside_it(repo, tmp_path,
                                                                   monkeypatch) -> None:
    paths = repo([ZN])
    _zn_ready(paths, tmp_path, monkeypatch)

    def boom(*a, **k):  # noqa: ANN002, ANN003, ANN202
        raise RuntimeError("planted engine failure")

    monkeypatch.setattr(runner, "run_engine", boom)
    with pytest.raises(RuntimeError, match="planted"):
        _once(paths, tmp_path)
    stopped = runner.stopped_path(tmp_path / "RUN_ONCE.json")
    assert stopped.name == "RUN_ONCE_STOPPED.json" and (tmp_path / "RUN_ONCE.json").exists()
    body = json.loads(stopped.read_text(encoding="utf-8"))
    assert body["status"] == "STOPPED" and "planted engine failure" in body["error"]


def test_r1_a_list_for_another_cluster_or_harness_refuses(repo, tmp_path, monkeypatch) -> None:
    paths = repo([ZN])
    _zn_ready(paths, tmp_path, monkeypatch)
    lst = tmp_path / "K1_list.json"
    lst.write_text(json.dumps({"cluster": "K3", "harness_sha256": HARNESS}), encoding="utf-8")
    with pytest.raises(runner.RunOnceRefusal, match="K3"):
        _once(paths, tmp_path, list_path=lst)
    assert not (tmp_path / "RUN_ONCE.json").exists()


# ========================================================= R2: the dry run ====
def test_r2_the_dry_run_resolves_counts_supply_and_writes_nothing(repo, tmp_path, monkeypatch,
                                                                  capsys) -> None:
    paths = repo([MGC, WK, ZN], signals=("MBT",))
    gc_sha = _store("GC", CONF_DAYS, paths["step2_root"])
    zn_sha = _store("ZN", CONF_DAYS, paths["step2_root"])
    _start_files(tmp_path, monkeypatch, K8={"GC": (CONF_DAYS[1].isoformat(), gc_sha)},
                 K2={"ZN": (CONF_DAYS[0].isoformat(), zn_sha)})
    decl = _declaration(tmp_path, {WK[0]: {"label": "untestable on owned data",
                                           "missing_leg": "MBT", "reason": "BTC not owned"}})
    monkeypatch.setattr(runner, "run_engine", lambda *a, **k: pytest.fail("the engine ran"))
    monkeypatch.setattr(runner, "load_confirmation_leg", lambda *a, **k: pytest.fail("bars"))
    rc = runner.main(["--harness-sha256", HARNESS, "--cluster", "K1", "--all", "--window",
                      "confirmation", "--research-root", str(paths["research_root"]),
                      "--step2-root", str(paths["step2_root"]), "--out-dir",
                      str(paths["out_dir"]), "--dry-run", "--untestable", str(decl)])
    lines = capsys.readouterr().out.splitlines()
    assert rc == 0 and not paths["out_dir"].exists()
    assert "path MGC->GC" in lines[0] and f"supply {len(CONF_DAYS) - 1} days" in lines[0]
    assert "not run (untestable on owned data)" in lines[1]
    assert f"supply {len(CONF_DAYS)} days" in lines[2] and "nothing written" in lines[3]


def test_r2_the_v13_flags_need_all_and_the_confirmation_window(capsys) -> None:
    base = ["--harness-sha256", HARNESS, "--cluster", "K1", "--research-root", "r",
            "--step2-root", "s", "--out-dir", "o"]
    for extra in (["--member", "x", "--window", "confirmation", "--dry-run"],
                  ["--all", "--window", "research", "--run-once-marker", "m"],
                  ["--all", "--window", "confirmation", "--list", "l"],
                  ["--all", "--window", "confirmation", "--dry-run", "--run-once-marker", "m"]):
        with pytest.raises(SystemExit) as exc:
            runner.main(base + extra)
        assert exc.value.code == 2


# ========================================== review fixes (SF-1, SF-2, N-4, N-11) ====
def _list_trial(ordinal: int, member: str, vehicle: str, *, tier: str = "A", run: bool = True,
                labels: tuple[str, ...] = ()) -> dict:
    from screening.stage_e_stats_units import frozen_epsilon

    eps = frozen_epsilon(vehicle)
    return {"ordinal": ordinal, "member": member, "vehicle": vehicle, "q_c": eps.q_c,
            "eps_ticks": eps.eps_ticks, "eps_usd_per_day_at_q": eps.eps_usd_per_day_at_q,
            "tier": tier, "run": run, "labels": list(labels), "bootstrap_seed": 20260923 + ordinal,
            "power": None}


def _write_list(tmp: Path, trials: list[dict], starts: dict, **over) -> Path:
    payload = {"schema": "stage_e_confirmation_list/1", "cluster": "K1", "harness_sha256": HARNESS,
               "cluster_freeze_sha256": "cd" * 32, "k_holm": 5, "program_n": 533,
               "bootstrap": {"seed_base": 20260923, "resamples": 10000, "mean_block": 5.0,
                             "ucb_quantile": 0.95},
               "start_dates": {r: d.isoformat() for r, d in starts.items()}, "trials": trials,
               **over}
    path = tmp / "K1_list.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


@pytest.mark.parametrize("planted", ["K1_K1-zn-01_ZN_confirmation.json",
                                     "K1_K1-zn-01_ZN_confirmation_trips.json",
                                     "K1_confirmation_cluster.json"])
def test_sf1_a_used_out_dir_refuses_before_the_marker_and_in_the_dry_run(
        repo, tmp_path, monkeypatch, planted: str) -> None:
    paths = repo([ZN])
    _zn_ready(paths, tmp_path, monkeypatch)
    paths["out_dir"].mkdir(parents=True)
    (paths["out_dir"] / planted).write_text("{}", encoding="utf-8")
    with pytest.raises(runner.RunnerRefusal, match="written once"):
        _once(paths, tmp_path)
    assert not (tmp_path / "RUN_ONCE.json").exists()
    with pytest.raises(runner.RunnerRefusal, match=planted.replace(".", r"\.")):
        runner.dry_run("K1", harness_sha256=HARNESS, research_root=paths["research_root"],
                       step2_root=paths["step2_root"], out_dir=paths["out_dir"])
    (paths["out_dir"] / planted).unlink()
    (paths["out_dir"] / "K2_K2-x_confirmation.json").write_text("{}", encoding="utf-8")
    assert _once(paths, tmp_path)["members"] == [ZN[0]]  # another cluster's file is not ours


def _sf2_world(repo, tmp_path, monkeypatch) -> tuple[dict, Path]:
    paths = repo([WK, ZN], signals=("MBT",))
    _zn_ready(paths, tmp_path, monkeypatch)
    decl = _declaration(tmp_path, {WK[0]: {"label": "untestable on owned data",
                                           "missing_leg": "MBT", "reason": "BTC not owned"}})
    return paths, decl


def _sf2_trials() -> list[dict]:
    return [_list_trial(1, WK[0], "MNQ", run=False, labels=("untestable on owned data",)),
            _list_trial(2, ZN[0], "ZN", tier="B")]


def test_sf2_a_list_that_agrees_with_the_plan_is_sealed_into_the_marker(
        repo, tmp_path, monkeypatch) -> None:
    paths, decl = _sf2_world(repo, tmp_path, monkeypatch)
    lst = _write_list(tmp_path, _sf2_trials(), {"ZN": CONF_DAYS[0]})
    out = _once(paths, tmp_path, list_path=lst, untestable=decl)
    assert out["not_run_members"] == {WK[0]: "BTC not owned"}
    body = json.loads((tmp_path / "RUN_ONCE.json").read_text(encoding="utf-8"))
    assert body["list"]["sha256"] == hashlib.sha256(lst.read_bytes()).hexdigest()


@pytest.mark.parametrize("mutate", ["parse", "missing_member", "ordinal", "extra_member",
                                    "undeclared_not_run", "declared_but_run", "start_date",
                                    "start_missing"])
def test_sf2_a_list_the_plan_contradicts_refuses_and_writes_no_marker(
        repo, tmp_path, monkeypatch, mutate: str) -> None:
    paths, decl = _sf2_world(repo, tmp_path, monkeypatch)
    trials, starts, over = _sf2_trials(), {"ZN": CONF_DAYS[0]}, {}
    untestable, match = decl, "differ from the frozen members"
    if mutate == "parse":
        over, match = {"k_holm": 0}, "verdict would refuse"
    elif mutate == "missing_member":
        trials = trials[1:]
    elif mutate == "ordinal":
        trials[1] = {**_list_trial(3, ZN[0], "ZN", tier="B")}
    elif mutate == "extra_member":
        trials.append(_list_trial(3, "K1-zz-01 ZN", "ZN", tier="B"))
    elif mutate == "undeclared_not_run":  # ZN listed run: false, not in the declaration
        trials[1] = _list_trial(2, ZN[0], "ZN", tier="B", run=False,
                                labels=("inconclusive by design",))
        match = "not the declared not-run members"
    elif mutate == "declared_but_run":
        trials[0] = _list_trial(1, WK[0], "MNQ", tier="B")
        match = "not the declared not-run members"
    elif mutate == "start_date":
        starts, match = {"ZN": CONF_DAYS[1]}, r"start_dates\[ZN\]"
    else:
        starts, match = {"MNQ": CONF_DAYS[0]}, r"start_dates\[ZN\] None"
    lst = _write_list(tmp_path, trials, starts, **over)
    with pytest.raises(runner.RunOnceRefusal, match=match):
        _once(paths, tmp_path, list_path=lst, untestable=untestable)
    assert not (tmp_path / "RUN_ONCE.json").exists()


def test_n4_the_marker_branch_prints_the_summary(repo, tmp_path, monkeypatch, capsys) -> None:
    paths = repo([ZN])
    _zn_ready(paths, tmp_path, monkeypatch)
    rc = runner.main(["--harness-sha256", HARNESS, "--cluster", "K1", "--all", "--window",
                      "confirmation", "--research-root", str(paths["research_root"]),
                      "--step2-root", str(paths["step2_root"]), "--out-dir",
                      str(paths["out_dir"]), "--run-once-marker", str(tmp_path / "M.json")])
    assert rc == 0 and capsys.readouterr().out.splitlines()[0] == (
        "K1 confirmation: 1 members, 0 refused")


def test_n11_a_failed_stopped_write_keeps_the_original_exception(repo, tmp_path,
                                                                 monkeypatch) -> None:
    paths = repo([ZN])
    _zn_ready(paths, tmp_path, monkeypatch)

    def boom(*a, **k):  # noqa: ANN002, ANN003, ANN202
        raise RuntimeError("planted engine failure")

    monkeypatch.setattr(runner, "run_engine", boom)
    monkeypatch.setattr(runner, "stopped_path", lambda m: tmp_path / "missing_dir" / "S.json")
    with pytest.raises(RuntimeError, match="planted engine failure"):
        _once(paths, tmp_path)
    assert (tmp_path / "RUN_ONCE.json").exists()
