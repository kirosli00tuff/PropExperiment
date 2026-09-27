"""M5 steps 2-5 (surrogates, candidates, pre-test, ranking, rule JSON), the route manifest, the
frozen inputs, and the entry points' preflight refusal (00_common.md)."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import numpy as np
import pytest

from ml_route.constants import FEATURES_DISTILLABLE
from ml_route.surrogate import (
    Leaf,
    RuleRows,
    candidate_sign,
    fit_surrogate,
    keep_per_cluster,
    leaves,
    pretest,
    render_entry,
    rule_json,
    rule_result,
)

NS_MIN = 60_000_000_000


class TestSurrogate:
    def test_depth_two_tree_leaves_and_conditions(self) -> None:
        rng = np.random.default_rng(0)
        X = rng.standard_normal((4000, 17))
        pred = np.where(X[:, 2] > 0.3, 1.0, -1.0) + np.where(X[:, 5] > 0, 0.2, 0.0)
        tree = fit_surrogate(X, pred)
        ls = leaves(tree)
        assert len(ls) == 4 and [leaf.order for leaf in ls] == [0, 1, 2, 3]
        root_feature, root_op, root_cut = ls[0].conditions[0]
        assert root_feature == "F3_ret30" and root_op == "<=" and abs(root_cut - 0.3) < 0.05
        assert ls[-1].conditions[0][:2] == ("F3_ret30", ">")
        assert all(len(leaf.conditions) == 2 for leaf in ls)
        assert type(root_cut) is float  # unrounded float64 threshold

    def test_candidate_thresholds_are_per_side_at_one_and_a_half(self) -> None:
        assert candidate_sign(0.051, 0.1) == 1 and candidate_sign(0.05, 0.1) == 0
        assert candidate_sign(-0.251, 0.1) == -1 and candidate_sign(-0.25, 0.1) == 0

    def _rows(self) -> RuleRows:
        n = 60
        X = np.zeros((n, 17))
        X[:, 0] = np.tile([1.0, -1.0], n // 2)
        day = np.repeat(np.arange(n // 2), 2).astype("datetime64[D]")
        t = day.astype("datetime64[ns]").astype(np.int64) + np.tile([0, 60], n // 2) * NS_MIN
        return RuleRows(np.array(["A"] * n, dtype=object), day, t, t + 30 * NS_MIN, X,
                        np.full(n, 0.5), np.full(n, 0.1))

    def test_rule_result_and_pretest(self) -> None:
        rows = self._rows()
        res = rule_result(rows, (("F1_ret5", ">", 0.0),), 1)
        assert res.trades == 30 and res.net_pnl == pytest.approx(30 * (0.5 - 0.05))
        assert res.per_trade_date == pytest.approx(res.net_pnl / 30)
        ok, reasons = pretest(res, res)
        assert ok and not reasons
        short = rule_result(rows, (("F1_ret5", ">", 0.0),), -1)
        ok, reasons = pretest(short, res)
        assert not ok and any("not positive" in r for r in reasons)
        few = rule_result(RuleRows(*(getattr(rows, f)[:20] for f in RuleRows.__dataclass_fields__)),
                          (("F1_ret5", ">", 0.0),), 1)
        assert any("< 30" in r for r in pretest(few, res)[1])

    def test_ranking_keeps_two_per_cluster_with_the_tie_order(self) -> None:
        def r(cluster, per, n_cond, h, ch, leaf):  # noqa: ANN001, ANN202
            return {"cluster": cluster, "pretest": {"block6_per_trade_date": per},
                    "conditions": [0] * n_cond, "horizon": h, "challenger": ch,
                    "leaf_order": leaf, "id": f"{cluster}{per}{n_cond}{h}{ch}{leaf}"}

        rules = [r("K1", 0.1, 2, "h30", "lgbm", 0), r("K1", 0.1, 1, "h30", "lstm", 3),
                 r("K1", 0.1, 1, "hF", "lstm", 1), r("K1", 0.2, 2, "h30", "lstm", 2),
                 r("K2", 0.1, 2, "h120", "lstm", 0), r("K2", 0.1, 2, "h120", "lgbm", 1)]
        kept = keep_per_cluster(rules)
        assert [k["id"] for k in kept] == ["K10.22h30lstm2", "K10.11hFlstm1",
                                           "K20.12h120lgbm1", "K20.12h120lstm0"]

    def test_rule_json_is_hashed_and_rendered_verbatim(self) -> None:
        from ml_route.rule_wrapper import RuleIntegrityError, rule_spec_from_json

        leaf = Leaf(1, 3, (("F3_ret30", "<=", 0.30000000000000004), ("F9_range", ">", 1.25)),
                    0.12)
        rule = rule_json("K2", "lgbm", "h120", leaf, 1, 0.1, ["ZN", "TN"], "ZN",
                         {"model_sha256": "m" * 64}, {"block6_per_trade_date": 0.01})
        spec = rule_spec_from_json(rule)
        assert spec.conditions[0][2] == 0.30000000000000004 and spec.sign == 1
        text = render_entry(rule)
        assert "0.30000000000000004" in text and rule["rule_sha256"] in text
        with pytest.raises(RuleIntegrityError):
            rule_spec_from_json({**rule, "sign": -1})


class TestInputs:
    def test_products_vehicles_and_units(self) -> None:
        from ml_route.inputs import load_products

        p = load_products()
        assert len(p) == 31
        assert sorted(r for r, s in p.items() if s.vehicle is None) == ["HO", "RB", "SI"]
        assert p["NQ"].vehicle == "MNQ" and p["CL"].vehicle == "MCL" and p["GC"].vehicle == "MGC"
        assert p["ZC"].vehicle_ticks_per_vendor_unit == pytest.approx(4.0)  # cents, 0.25 c tick
        assert p["NQ"].vehicle_ticks_per_vendor_unit == pytest.approx(4.0)
        assert not any(s.cpi_no_open for s in p.values())  # every CPI mini trades via a micro

    def test_changed_frozen_table_is_refused(self, tmp_path: Path) -> None:
        from ml_route.inputs import VEHICLES_PATH, FrozenInputMismatch, load_products

        copy = tmp_path / "v.json"
        copy.write_bytes(VEHICLES_PATH.read_bytes() + b" ")
        with pytest.raises(FrozenInputMismatch):
            load_products(copy)

    def test_session_times_known_values(self) -> None:
        from ml_route.inputs import day_times

        dt = day_times("ZC", "grains", date(2021, 6, 7))
        assert dt.open_ns == 1623072600 * 10**9  # 08:30 CT
        assert (dt.close_ns - dt.open_ns) // NS_MIN == 285  # 13:15 CT
        assert (dt.flatten_ns - dt.open_ns) // NS_MIN == 288  # 13:18 CT
        assert day_times("NQ", "equity", date(2023, 11, 24)).early_halt
        assert day_times("NQ", "equity", date(2021, 6, 5)) is None  # a Saturday

    def test_unwired_inputs_refuse_by_name(self, tmp_path: Path) -> None:
        # A root without reports/stage_e2b_release_calendar.json or stage_e_start_rule_*.json,
        # so the refusals hold after the frozen files land in the repository (lead, OC-P note).
        from ml_route.inputs import RouteInputMissing, load_route_inputs, load_start_dates

        with pytest.raises(RouteInputMissing, match="release calendar"):
            load_route_inputs(repo_root=tmp_path)
        with pytest.raises(RouteInputMissing, match="S_X"):
            load_start_dates(repo_root=tmp_path)


class TestEntryPreflight:
    @pytest.fixture()
    def calls(self, monkeypatch: pytest.MonkeyPatch) -> list[str]:
        import ml_route.inputs as inputs_mod
        import screening.harness_freeze as hf

        seen: list[str] = []

        def refuse(expected: str, root=None) -> str:  # noqa: ANN001
            seen.append("preflight")
            raise hf.HarnessFreezeError("tree differs from the frozen harness")

        def loader():  # noqa: ANN202
            seen.append("inputs")
            raise AssertionError("inputs were read before the preflight")

        monkeypatch.setattr(hf, "preflight", refuse)
        monkeypatch.setattr(inputs_mod, "load_route_inputs", loader)
        return seen

    def test_fit_refuses_when_preflight_raises(self, calls, tmp_path: Path) -> None:
        from ml_route.train import main
        from screening.harness_freeze import HarnessFreezeError

        with pytest.raises(HarnessFreezeError):
            main(["fit", "--challenger", "lgbm", "--horizon", "h30", "--store-root",
                  str(tmp_path), "--out-dir", str(tmp_path / "o"), "--harness-sha256", "a" * 64])
        assert calls == ["preflight"] and not (tmp_path / "o").exists()

    def test_finalize_refuses_when_preflight_raises(self, calls, tmp_path: Path) -> None:
        from ml_route.train import main
        from screening.harness_freeze import HarnessFreezeError

        with pytest.raises(HarnessFreezeError):
            main(["finalize", "--out-dir", str(tmp_path), "--harness-sha256", "a" * 64])
        assert calls == ["preflight"]

    def test_harness_hash_is_a_required_flag(self, tmp_path: Path) -> None:
        from ml_route.train import main

        with pytest.raises(SystemExit):
            main(["fit", "--challenger", "lgbm", "--horizon", "h30", "--store-root",
                  str(tmp_path), "--out-dir", str(tmp_path)])

    def test_real_preflight_refuses_a_wrong_hash(self, tmp_path: Path) -> None:
        from ml_route.train import main
        from screening.harness_freeze import HarnessFreezeError

        with pytest.raises(HarnessFreezeError):
            main(["finalize", "--out-dir", str(tmp_path), "--harness-sha256", "0" * 64])


class TestManifest:
    def _candidates(self, out: Path, harness: str) -> None:
        from ml_route.surrogate import Leaf

        (out / "candidates").mkdir(parents=True)
        for ch in ("lgbm", "lstm"):
            for h in ("h30", "h120", "hF"):
                leaf = Leaf(0, 1, (("F1_ret5", ">", 0.5),), 0.2)
                rule = rule_json("K2", ch, h, leaf, 1, 0.1, ["ZN"], "ZN", {"model_sha256": "m"},
                                 {"block6_per_trade_date": 0.1 if h == "hF" else 0.05})
                (out / "candidates" / f"{ch}_{h}.json").write_text(json.dumps({
                    "harness_sha256": harness, "selected": {"x": 1}, "model_sha256": "m" * 64,
                    "model_file": "f.bin", "surrogates": [{"cluster": "K2", "tree": {"v": 1}}],
                    "candidates": [rule], "survivors": [rule]}), encoding="utf-8")

    def _inputs(self):  # noqa: ANN202
        from ml_route.synthetic import synthetic_events, synthetic_inputs

        ev = synthetic_events(["ZN"], date(2019, 5, 6), date(2019, 6, 1), 1)
        return synthetic_inputs({"ZN": date(2019, 5, 6)}, ev)

    def test_finalize_writes_rules_and_the_manifest(self, tmp_path: Path) -> None:
        from ml_route.blocks import cut_blocks
        from ml_route.ledger import Ledger
        from ml_route.manifest import finalize_route

        harness = "d" * 64
        self._candidates(tmp_path, harness)
        Ledger(tmp_path / "ledger" / "lgbm_h30.jsonl").append(
            {"key": "k", "model_sha256": "e" * 64, "machine": {"host": "x"}})
        days = [date(2020, 1, 6 + i) for i in range(12)]
        sha = finalize_route(tmp_path, harness, self._inputs(), cut_blocks(days))
        man = json.loads((tmp_path / "route_manifest.json").read_text(encoding="utf-8"))
        assert man["harness_sha256"] == harness and len(man["blocks"]["blocks"]) == 6
        assert man["trial_counts"]["configurations"] == {"lgbm": 24, "lstm": 12, "total": 36}
        assert man["trial_counts"]["kept_rules"] == 2 == len(man["rules"])
        assert [r["horizon"] for r in man["rules"]] == ["hF", "hF"]
        assert man["fits"][0]["model_sha256"] == "e" * 64 and man["s_x"] == {"ZN": "2019-05-06"}
        assert man["lstm_batch_size"] == 512 and len(sha) == 64
        assert len(list((tmp_path / "rules").glob("*.json"))) == 2

    def test_missing_candidates_or_other_harness_refused(self, tmp_path: Path) -> None:
        from ml_route.blocks import cut_blocks
        from ml_route.manifest import ManifestError, finalize_route

        days = [date(2020, 1, 6 + i) for i in range(12)]
        with pytest.raises(ManifestError, match="missing"):
            finalize_route(tmp_path, "d" * 64, self._inputs(), cut_blocks(days))
        self._candidates(tmp_path, "d" * 64)
        with pytest.raises(ManifestError, match="another harness"):
            finalize_route(tmp_path, "f" * 64, self._inputs(), cut_blocks(days))


def test_feature_list_for_surrogates_is_f1_to_f17() -> None:
    assert len(FEATURES_DISTILLABLE) == 17 and FEATURES_DISTILLABLE[-1] == "F17_vol_state"
