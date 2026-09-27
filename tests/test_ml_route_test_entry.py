"""Stage E.2b G4 (MLTestCoder): the E.ML-test entry (python -m ml_route.test) on a synthetic
frozen route and a synthetic research store: the preflight comes first and its refusal stops the
entry; every hash of the frozen route is checked and a changed rule, model, ledger, manifest,
rendering or calendar is refused by name before any bar is read; the rules run through the Stage
E engine; the records and summary carry M6's trial accounting and the named not-computed items;
records are written once; M7.8's scope check."""

from __future__ import annotations

import hashlib
import json
import shutil
from dataclasses import replace
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pytest

from ml_route import freeze_scope, lgbm, lstm
from ml_route import test as entry
from ml_route.blocks import cpcv_splits, cut_blocks
from ml_route.constants import COSTS_SHA256, VEHICLES_SHA256
from ml_route.inputs import (
    RouteInputs,
    event_calendar_from_release,
    load_products,
    load_vehicle_costs,
)
from ml_route.ledger import HashChainError, Ledger, canonical, sha256_bytes
from ml_route.manifest import finalize_route
from ml_route.rule_wrapper import RuleIntegrityError
from ml_route.surrogate import Leaf, rule_json
from ml_route.synthetic import synthetic_bars
from screening import harness_freeze, stage_e_rules
from screening.harness_freeze import HarnessFreezeError
from screening.stage_e_rules import release_calendar_from_dict
from screening.stage_e_runner import RunnerRefusal
from strategy.stage_e.interface import LegSpec
from tests._stage_e_synthetic import write_parquet

HARNESS = "a" * 64
TRAIN_DAYS = [date(2020, 1, 1) + timedelta(days=i) for i in range(36)]
RESEARCH_FIRST, RESEARCH_LAST = date(2025, 4, 1), date(2025, 12, 31)
TREE = {"feature": [0, -2, -2], "threshold": [0.0, -2.0, -2.0]}
RULE_CONDITIONS = {"lgbm_h30": (("F1_ret5", ">", 0.0),),
                   "lstm_h30": (("F1_ret5", "<=", 0.0), ("F9_range", ">", 0.5))}
RULE_EXPOSURES = {"lgbm_h30": ["MNQ", "M2K"], "lstm_h30": ["MNQ"]}


def _calendar(sha: str = "c" * 64):  # noqa: ANN202
    products = load_products()
    universe = sorted({s.vehicle for s in products.values() if s.vehicle} | set(products))
    raw = {"schema": "stage_e_release_calendar/1",
           "coverage": {"first": "2019-05-01", "last": "2026-06-21"},
           "releases": [{"id": f"fomc{i}", "instant_utc": when, "products": universe,
                         "cpi": False, "source": "t"}
                        for i, when in enumerate(("2025-06-18T18:00:00Z",
                                                  "2025-10-29T18:00:00Z",
                                                  "2025-11-12T16:29:00Z"))]}
    return release_calendar_from_dict(raw, sha, "synthetic calendar")


def _ledgers(route: Path) -> None:
    splits = cpcv_splits(cut_blocks(TRAIN_DAYS))
    rng = np.random.default_rng(4)
    for ch, mod in (("lgbm", lgbm), ("lstm", lstm)):
        for h in ("h30", "h120", "hF"):
            ledger = Ledger(route / "ledger" / f"{ch}_{h}.jsonl")
            for cfg in mod.grid():
                cid = mod.config_id(cfg)
                for sp in splits:
                    pnl = [[d.isoformat(), float(rng.normal(0.0, 1.0))]
                           for d in sorted(sp.validation_dates)]
                    ledger.append({"key": f"{cid}|{sp.label()}", "challenger": ch, "horizon": h,
                                   "config": cfg, "split": sp.label(),
                                   "score": float(np.mean([v for _, v in pnl])),
                                   "daily_pnl": pnl, "model_sha256": "e" * 64,
                                   "machine": {"host": "t"}, "harness_sha256": HARNESS})
            cid = mod.config_id(mod.grid()[0])
            ledger.append({"key": f"{cid}|refit", "challenger": ch, "horizon": h,
                           "config": mod.grid()[0], "split": "refit_blocks_1_5",
                           "model_sha256": "f" * 64, "machine": {"host": "t"},
                           "harness_sha256": HARNESS})


def _candidates(route: Path) -> None:
    tree_sha = sha256_bytes(canonical(TREE))
    for ch, mod in (("lgbm", lgbm), ("lstm", lstm)):
        for h in ("h30", "h120", "hF"):
            cfg = mod.grid()[0]
            model_file = f"{ch}_{h}_{mod.config_id(cfg)}_refit.bin"
            data = f"model {ch} {h}".encode()
            (route / "models").mkdir(parents=True, exist_ok=True)
            (route / "models" / model_file).write_bytes(data)
            model_sha = sha256_bytes(data)
            rules = []
            key = f"{ch}_{h}"
            if key in RULE_CONDITIONS:
                leaf = Leaf(0, 1, RULE_CONDITIONS[key], 0.3)
                rules.append(rule_json(
                    "K1", ch, h, leaf, 1, 0.05, RULE_EXPOSURES[key], "MNQ",
                    {"model_sha256": model_sha, "config": cfg, "surrogate_sha256": tree_sha,
                     "harness_sha256": HARNESS},
                    {"block6_per_trade_date": 0.2 if ch == "lgbm" else 0.1, "passed": True}))
            (route / "candidates").mkdir(parents=True, exist_ok=True)
            (route / "candidates" / f"{key}.json").write_text(json.dumps({
                "harness_sha256": HARNESS, "selected": cfg, "model_sha256": model_sha,
                "model_file": model_file, "surrogates": [{"cluster": "K1", "tree": TREE}],
                "candidates": rules, "survivors": rules}), encoding="utf-8")


def build_route(route: Path) -> str:
    _ledgers(route)
    _candidates(route)
    products = load_products()
    events = event_calendar_from_release(_calendar(), products)
    inputs = RouteInputs(products, load_vehicle_costs(products), events,
                         {"NQ": date(2019, 5, 6)},
                         {"costs_sha256": COSTS_SHA256, "vehicles_sha256": VEHICLES_SHA256})
    return finalize_route(route, HARNESS, inputs, cut_blocks(TRAIN_DAYS))


def build_research(root: Path) -> dict[str, str]:
    from data.stage_e_bars import research_parquet_path

    nq = synthetic_bars("NQ", "equity", RESEARCH_FIRST, RESEARCH_LAST, 31, 0.25, 20000.0)
    rty = synthetic_bars("RTY", "equity", RESEARCH_FIRST, RESEARCH_LAST, 32, 0.1, 2000.0)
    frames = {"NQ": nq, "MNQ": nq.assign(raw_symbol="MNQZ5", instrument_id=np.uint32(9)),
              "RTY": rty, "M2K": rty.assign(raw_symbol="M2KZ5", instrument_id=np.uint32(8))}
    shas = {}
    for r, frame in frames.items():
        path = research_parquet_path(r, root)
        write_parquet(frame, path, {"rolls": []})
        shas[r] = hashlib.sha256(path.read_bytes()).hexdigest()
    return shas


def _patch(mp: pytest.MonkeyPatch, shas: dict[str, str], calendar=None) -> None:  # noqa: ANN001
    mp.setattr(harness_freeze, "preflight", lambda expected, root=None: expected)
    mp.setattr(freeze_scope, "check_harness_scope", lambda root=None: None)
    cal = calendar if calendar is not None else _calendar()
    mp.setattr(stage_e_rules, "load_release_calendar", lambda root=None: cal)
    real = entry._leg_inputs
    mp.setattr(entry, "_leg_inputs", lambda legs: {
        r: replace(li, research_parquet_sha256=shas[r]) for r, li in real(legs).items()})


@pytest.fixture(scope="module")
def ran(tmp_path_factory: pytest.TempPathFactory) -> dict:
    base = tmp_path_factory.mktemp("route")
    route, research, out = base / "route", base / "research", base / "out"
    manifest_sha = build_route(route)
    shas = build_research(research)
    mp = pytest.MonkeyPatch()
    try:
        _patch(mp, shas)
        summary = entry.run_test(route, manifest_sha, research, out, HARNESS)
    finally:
        mp.undo()
    return {"route": route, "research": research, "out": out, "manifest_sha": manifest_sha,
            "shas": shas, "summary": summary}


def _args(d: dict, out: Path | None = None, manifest_sha: str | None = None,
          route: Path | None = None) -> list[str]:
    return ["--route-dir", str(route or d["route"]),
            "--route-manifest-sha256", manifest_sha or d["manifest_sha"],
            "--research-root", str(d["research"]), "--out-dir", str(out or d["out"]),
            "--harness-sha256", HARNESS]


# ------------------------------------------------------------------ end to end ----
class TestEndToEnd:
    def test_both_rules_are_tested_and_counted_once_each(self, ran) -> None:
        s = ran["summary"]
        assert [r["status"] for r in s["rules"]] == ["run", "run"]
        acct = s["trial_accounting"]
        assert acct["program_trials_added"] == 2 and acct["not_tested"] == []
        assert acct["training_window_search"]["configurations"]["total"] == 36
        assert acct["training_window"]["n_configurations"] == 36
        assert s["harness_sha256"] == HARNESS and s["route_manifest_sha256"] == ran["manifest_sha"]

    def test_the_records_carry_the_series_hashes_and_training_figures(self, ran) -> None:
        records = sorted((ran["out"] / "rules").glob("*.json"))
        assert len(records) == 2
        for path in records:
            rec = json.loads(path.read_text(encoding="utf-8"))
            assert rec["harness_sha256"] == HARNESS and rec["status"] == "run"
            assert rec["primary_vehicle"] == "MNQ" and rec["exposures"][0]["vehicle"] == "MNQ"
            mnq = rec["exposures"][0]
            assert mnq["legs"] == [{"root": "MNQ", "traded": True},
                                   {"root": "NQ", "traded": False}]
            assert mnq["bars"]["MNQ"]["sha256"] == ran["shas"]["MNQ"]
            assert rec["series"]["unit"].startswith("net ticks per contract per day of the "
                                                    "primary vehicle MNQ")
            assert rec["series"]["n_trips"] > 5 and mnq["decisions"]["acted"] > 5
            assert set(rec["training_window"]["dsr"]) == {"configurations",
                                                          "implied_independent", "full_search"}
            assert mnq["window_dates"]["first"] == "2025-04-01"
            assert rec["statistics"]["daily_t"]["status"] == "computed"
            assert len(rec["series_m5_sigma"]["values"]) == len(rec["series"]["values"])
            for e in rec["exposures"]:
                assert [leg["traded"] for leg in e["legs"]].count(True) == 1  # OC-P

    def test_the_rule_series_is_m5s_mean_over_exposures_with_rows(self, ran) -> None:
        recs = [json.loads(p.read_text(encoding="utf-8"))
                for p in sorted((ran["out"] / "rules").glob("*.json"))]
        two = next(r for r in recs if len(r["exposures"]) == 2)
        one = next(r for r in recs if len(r["exposures"]) == 1)
        scale = {"MNQ": 1.0, "M2K": 3.0}  # q_c x $0.50 of each vehicle over MNQ's 1 x $0.50
        own = {e["vehicle"]: dict(zip(e["series_own_vehicle"]["dates"],
                                      e["series_own_vehicle"]["values"], strict=True))
               for e in two["exposures"]}
        rows = {e["vehicle"]: set(e["rows_dates"]) for e in two["exposures"]}
        window = sorted(set(own["MNQ"]) | set(own["M2K"]))
        assert two["series"]["dates"] == window  # every window date (RT-4 ruling)
        both = none = 0
        for d, got, n in zip(two["series"]["dates"], two["series"]["values"],
                             two["series"]["exposures_with_rows"], strict=True):
            with_rows = [v for v in ("MNQ", "M2K") if d in rows[v]]
            assert n == len(with_rows)
            want = (sum(own[v][d] * scale[v] for v in with_rows) / len(with_rows)
                    if with_rows else 0.0)
            assert got == pytest.approx(want, abs=1e-9)
            both += n == 2
            none += n == 0
        assert both > 20 and none > 100  # the F17 warm-up enters as zeros
        assert two["series"]["window_dates_without_rows"] == none
        assert two["series"]["window_dates"] == len(window)
        mnq = one["exposures"][0]
        own1 = dict(zip(mnq["series_own_vehicle"]["dates"], mnq["series_own_vehicle"]["values"],
                        strict=True))
        assert one["series"]["dates"] == mnq["series_own_vehicle"]["dates"]
        rows1 = set(mnq["rows_dates"])
        assert one["series"]["values"] == pytest.approx(
            [own1[d] if d in rows1 else 0.0 for d in one["series"]["dates"]], abs=1e-12)
        assert one["series"]["values"][0] == 0.0 and one["series"]["first_date_with_rows"] > (
            one["series"]["dates"][100])  # the warm-up dates are zeros, not left out

    def test_the_family_figures_and_the_named_open_items(self, ran) -> None:
        fam = ran["summary"]["route_family"]
        assert fam["pbo_research_window"]["n_strategies"] == 2
        rules = ran["summary"]["rules"]
        assert all(r["window_dates_without_rows"] > 100 for r in rules)
        assert "warm-up" in ran["summary"]["warm_up_finding"]
        assert fam["sharpe_variance_over_tested_rules"] >= 0.0
        for item in ("holm", "dsr_at_program_n", "composite_verdict", "nulls_per_exposure"):
            assert fam[item]["status"] == "not computed" and "question" in fam[item]["reason"]

    def test_a_second_run_is_refused(self, ran, monkeypatch) -> None:
        _patch(monkeypatch, ran["shas"])
        with pytest.raises(entry.RouteTestRefusal, match="not empty"):
            entry.main(_args(ran))


# ---------------------------------------------------------------- the preflight ----
def test_the_entry_refuses_when_preflight_raises_before_reading_anything(monkeypatch,
                                                                         tmp_path) -> None:
    def refuse(expected, root=None):  # noqa: ANN001, ANN202
        raise HarnessFreezeError("Stage E harness preflight refused: test")

    monkeypatch.setattr(harness_freeze, "preflight", refuse)
    monkeypatch.setattr(entry, "load_frozen_route",
                        lambda *a, **k: pytest.fail("the route was read before the preflight"))
    monkeypatch.setattr(freeze_scope, "check_harness_scope",
                        lambda root=None: pytest.fail("read before the preflight"))
    d = {"route": tmp_path / "r", "research": tmp_path / "x", "out": tmp_path / "o",
         "manifest_sha": "b" * 64}
    with pytest.raises(HarnessFreezeError):
        entry.main(_args(d))
    assert not (tmp_path / "o").exists()


def test_the_real_preflight_refuses_a_wrong_hash(tmp_path) -> None:
    d = {"route": tmp_path / "r", "research": tmp_path / "x", "out": tmp_path / "o",
         "manifest_sha": "b" * 64}
    with pytest.raises(HarnessFreezeError):
        entry.main(_args(d)[:-1] + ["0" * 64])


def test_every_argument_is_required(capsys) -> None:
    for drop in ("--harness-sha256", "--research-root", "--route-manifest-sha256"):
        args = ["--route-dir", "r", "--route-manifest-sha256", "b" * 64, "--research-root", "x",
                "--out-dir", "o", "--harness-sha256", HARNESS]
        i = args.index(drop)
        with pytest.raises(SystemExit):
            entry.main(args[:i] + args[i + 2:])
    assert "required" in capsys.readouterr().err


# ------------------------------------------------------- refusals of the frozen route ----
@pytest.fixture
def copy(ran, tmp_path, monkeypatch) -> dict:  # noqa: ANN001
    route = tmp_path / "route"
    shutil.copytree(ran["route"], route)
    _patch(monkeypatch, ran["shas"])
    monkeypatch.setattr(entry, "run_rule", lambda *a, **k: pytest.fail("a bar was read"))
    return {**ran, "route": route, "out": tmp_path / "out"}


def _rule_path(route: Path) -> Path:
    return sorted((route / "rules").glob("*.json"))[0]


class TestFrozenRouteRefusals:
    def test_a_changed_rule_is_refused_by_its_hash(self, copy) -> None:
        path = _rule_path(copy["route"])
        rule = json.loads(path.read_text(encoding="utf-8"))
        rule["conditions"][0]["cut"] = 0.25
        path.write_text(json.dumps(rule), encoding="utf-8")
        with pytest.raises(RuleIntegrityError):
            entry.main(_args(copy))

    def test_a_rehashed_changed_rule_is_refused_against_the_kept_rule(self, copy) -> None:
        path = _rule_path(copy["route"])
        rule = json.loads(path.read_text(encoding="utf-8"))
        rule["conditions"][0]["cut"] = 0.25
        body = {k: v for k, v in rule.items() if k != "rule_sha256"}
        rule["rule_sha256"] = sha256_bytes(canonical(body))
        path.write_text(json.dumps(rule), encoding="utf-8")
        with pytest.raises(entry.RouteTestRefusal, match="differs from the kept rule"):
            entry.main(_args(copy))

    def test_a_changed_model_file_is_refused(self, copy) -> None:
        model = sorted((copy["route"] / "models").glob("*.bin"))[0]
        model.write_bytes(b"another model")
        with pytest.raises(HashChainError, match="REFUSED"):
            entry.main(_args(copy))

    def test_an_edited_ledger_is_refused(self, copy) -> None:
        path = copy["route"] / "ledger" / "lgbm_h30.jsonl"
        lines = path.read_text(encoding="utf-8").splitlines()
        rec = json.loads(lines[3])
        rec["score"] = 42.0
        lines[3] = json.dumps(rec, sort_keys=True)
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        with pytest.raises(HashChainError):
            entry.main(_args(copy))

    def test_another_manifest_hash_is_refused(self, copy) -> None:
        with pytest.raises(entry.RouteTestRefusal, match="committed manifest"):
            entry.main(_args(copy, manifest_sha="d" * 64))

    def test_an_edited_manifest_body_is_refused(self, copy) -> None:
        path = copy["route"] / "route_manifest.json"
        man = json.loads(path.read_text(encoding="utf-8"))
        man["trial_counts"]["kept_rules"] = 1
        text = json.dumps(man, indent=1, sort_keys=True) + "\n"
        path.write_text(text, encoding="utf-8")
        new_sha = sha256_bytes(text.encode("utf-8"))
        with pytest.raises(entry.RouteTestRefusal, match="manifest_body_sha256"):
            entry.main(_args(copy, manifest_sha=new_sha))

    def test_another_harness_is_refused(self, copy) -> None:
        other = "9" * 64
        with pytest.raises(entry.RouteTestRefusal, match="frozen under harness"):
            entry.main(_args(copy)[:-1] + [other])

    def test_an_edited_rendering_or_an_extra_rule_file_is_refused(self, copy) -> None:
        md = copy["route"] / "rules" / "RULES.md"
        md.write_text(md.read_text(encoding="utf-8") + "\n", encoding="utf-8")
        with pytest.raises(entry.RouteTestRefusal, match="RULES.md"):
            entry.main(_args(copy))
        md.write_text(md.read_text(encoding="utf-8")[:-1], encoding="utf-8")
        (copy["route"] / "rules" / "extra.json").write_text("{}", encoding="utf-8")
        with pytest.raises(entry.RouteTestRefusal, match="extra.json"):
            entry.main(_args(copy))

    def test_an_edited_survivor_list_is_refused(self, copy) -> None:
        path = copy["route"] / "candidates" / "lstm_h30.json"
        cand = json.loads(path.read_text(encoding="utf-8"))
        cand["survivors"] = []
        path.write_text(json.dumps(cand), encoding="utf-8")
        with pytest.raises(entry.RouteTestRefusal, match="M5 step 4"):
            entry.main(_args(copy))

    def test_a_changed_surrogate_tree_is_refused(self, copy) -> None:
        path = copy["route"] / "candidates" / "lgbm_hF.json"
        cand = json.loads(path.read_text(encoding="utf-8"))
        cand["surrogates"][0]["tree"]["threshold"][0] = 0.5
        path.write_text(json.dumps(cand), encoding="utf-8")
        with pytest.raises(entry.RouteTestRefusal, match="surrogate trees"):
            entry.main(_args(copy))

    def test_another_release_calendar_is_refused(self, copy, monkeypatch) -> None:
        monkeypatch.setattr(stage_e_rules, "load_release_calendar",
                            lambda root=None: _calendar(sha="0" * 64))
        with pytest.raises(entry.RouteTestRefusal, match="event_calendar_sha256"):
            entry.main(_args(copy))


def test_k6_exposures_on_two_calendars_are_separate_runs_not_refused() -> None:
    from ml_route.stage_e_adapter import exposure_plans

    rule = rule_json("K6", "lgbm", "h30", Leaf(0, 1, (("F1_ret5", ">", 0.0),), 0.1), 1, 0.05,
                     ["ZC", "HE", "LE"], "ZC", {}, {})
    for plan in exposure_plans(rule, load_products()):
        got = entry._leg_inputs(plan.legs)
        assert [r for r, li in got.items() if li.costs is not None] == [plan.vehicle]


def test_a_run_with_two_traded_legs_is_refused() -> None:
    with pytest.raises(entry.RouteTestRefusal, match="exactly one traded leg"):
        entry._leg_inputs((LegSpec("ZC", True), LegSpec("HE", True)))


def test_the_rule_series_function_by_hand() -> None:
    d1, d2, d3 = date(2025, 11, 3), date(2025, 11, 4), date(2025, 11, 5)
    d0 = date(2025, 11, 2)
    dates, values = entry.rule_daily_series(
        [{d1: 2.0, d2: 4.0}, {d2: 1.0}], [{d1, d2}, {d2, d3}], [d3, d0, d1, d2])
    assert dates == [d0, d1, d2, d3]
    assert values == [0.0, 2.0, 2.5, 0.0]  # d0: no rows -> 0.0; d3: rows, no trade -> 0
    assert entry.rule_daily_series([], [], []) == ([], [])
    with pytest.raises(ValueError, match="outside the window"):
        entry.rule_daily_series([{}], [{d1}], [d2])


def test_the_write_once_rule_is_the_runners(tmp_path) -> None:
    entry._write_once({"a": 1}, tmp_path, "x")
    with pytest.raises(RunnerRefusal, match="written once"):
        entry._write_once({"a": 2}, tmp_path, "x")


# ------------------------------------------------------------------- M7.8 scope ----
class TestM78Scope:
    def test_every_named_item_exists_and_every_module_is_required(self) -> None:
        from data.config import REPO_ROOT

        req = set(freeze_scope.required_files())
        for _, files in freeze_scope.M78_ITEMS:
            for f in files:
                assert (REPO_ROOT / f).is_file(), f
                assert f in req
        assert {p.relative_to(REPO_ROOT).as_posix()
                for p in (REPO_ROOT / "ml_route").glob("*.py")} <= req
        assert "tests/test_ml_route_wrapper.py" in req and "tests/test_leakage_canaries.py" in req
        assert "tests/test_ml_route_test_entry.py" in req

    def test_the_check_names_what_the_manifest_leaves_out(self, tmp_path) -> None:
        (tmp_path / "ml_route").mkdir()
        (tmp_path / "ml_route" / "a.py").write_text("", encoding="utf-8")
        (tmp_path / "tests").mkdir()
        (tmp_path / "tests" / "test_ml_route_a.py").write_text("", encoding="utf-8")
        listed = {"ml_route/a.py": {"sha256": "x", "bytes": 0}}
        (tmp_path / "reports").mkdir()
        manifest = tmp_path / harness_freeze.MANIFEST_PATH
        manifest.write_text(json.dumps({"files": listed}), encoding="utf-8")
        with pytest.raises(freeze_scope.RouteScopeError, match="tests/test_ml_route_a.py"):
            freeze_scope.check_harness_scope(tmp_path)
        listed.update({f: {"sha256": "x", "bytes": 0} for f in
                       ("tests/test_ml_route_a.py", *freeze_scope.M7_EXTRA_TESTS)})
        manifest.write_text(json.dumps({"files": listed}), encoding="utf-8")
        freeze_scope.check_harness_scope(tmp_path)

    def test_a_missing_manifest_is_refused(self, tmp_path) -> None:
        with pytest.raises(freeze_scope.RouteScopeError, match="cannot be read"):
            freeze_scope.check_harness_scope(tmp_path)
