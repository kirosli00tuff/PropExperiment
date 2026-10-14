"""multiday.run and multiday.freeze_manifest end to end in the TEST MODE on synthetic stores (the
step 2 layout, the frozen read-only writer, the frozen bookings), synthetic calendars, settlement,
windows, release rows, an H2 result and a temporary registry: the pre-marker refusals
(unregistered, wrong freeze sha256, a changed file, an existing output, fixed paths outside the
test mode), the run-once marker and a second run refused."""

from __future__ import annotations

import hashlib
import json
import shutil
from datetime import UTC, date, datetime
from pathlib import Path

import numpy as np
import pytest

from base_rules import constants as BK
from base_rules.counts import in_session
from base_rules.store import step2_name
from multiday import constants as K
from multiday import freeze_manifest as FM
from multiday.run import main
from screening.trial_registry import current_n, init_registry, register
from tests._base_rules_fixtures import (
    hist_payload,
    settlement_payload,
    store_frame,
    store_rows,
    write_store,
)
from tests.test_multiday_world import all_cals, ctx_for

LAST = date(2021, 12, 31)  # bars end here (the window runs on; later months hold nothing)


def _sha(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def _write(path: Path, obj) -> Path:  # noqa: ANN001
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj))
    return path


def _rolls(days: list[date]) -> list[int]:
    out = []
    for y in range(2019, 2022):
        for m in (3, 6, 9, 12):
            mondays = [d for d in days if d.year == y and d.month == m and d.weekday() == 0]
            if len(mondays) >= 2:
                d = mondays[1]
                out.append(int(datetime(d.year, d.month, d.day, tzinfo=UTC).timestamp()) * 10**9)
    return out


@pytest.fixture(scope="module")
def world(tmp_path_factory):  # noqa: ANN001, ANN201
    tmp = tmp_path_factory.mktemp("e21")
    inputs: dict[str, str] = {}
    for g in BK.HIST_GROUPS_FROZEN:
        inputs[f"hist_calendar_{g}"] = str(_write(tmp / "hist2010" / f"{g}.json",
                                                  hist_payload(g)))
    inputs["livestock_hist"] = str(_write(tmp / "livestock.json", hist_payload("livestock")))
    inputs["settlement"] = str(_write(tmp / "settlement.json", settlement_payload()))
    inputs["windows"] = str(_write(tmp / "windows.json", {
        "schema": BK.WINDOWS_SCHEMA, "fallback_window": [str(BK.FALLBACK_FIRST),
                                                         str(BK.WINDOW_LAST)],
        "products": {p: {"window_start_on_or_after": "2010-07-01",
                         "window_end": str(BK.WINDOW_LAST)} for p in BK.PRODUCTS}}))
    inputs["release_frozen"] = str(_write(tmp / "rel_frozen.json", {"releases": []}))
    inputs["release_hist"] = str(_write(tmp / "rel_hist.json", {"releases": []}))
    inputs["ecauc_hist"] = str(_write(tmp / "ecauc.json", {"rows": []}))
    inputs["ecauc_announcements"] = str(_write(tmp / "ann.json", {
        "schema": BK.ANNOUNCEMENTS_SCHEMA, "rows": []}))
    inputs["quote_record"] = str(_write(tmp / "quotes.json", {"synthetic": True}))
    cals = all_cals()
    ctx = ctx_for(cals, {}, starts={r: BK.FALLBACK_FIRST for r in K.ROOTS})
    stores = {}
    for k, root in enumerate(K.ROOTS):
        cal = cals[BK.GROUP_OF[root]]
        days = [d for d in cal.trade_dates() if BK.FALLBACK_FIRST <= d <= LAST]
        s = int(ctx.settlement.settle_minute(root, days[0]))
        rolls = _rolls(days)
        rng = np.random.default_rng(100 + k)
        level, prices = 50_000.0, {}
        keep = []
        for d in days:
            level *= float(np.exp(0.0004 * (1 if k % 2 else -1) + 0.008 * rng.standard_normal()))
            for m in (s - 1, s):
                if in_session(ctx, root, d, m):
                    keep.append((d, m))
            prices[d] = int(level)
        rows = []
        for d, m in keep:
            rows += store_rows(root, cal.frozen, [d], [m],
                               lambda t, r=rolls: f"C{sum(1 for x in r if t >= x)}",
                               lambda t, p=prices[d]: p)
        meta = {"rolls": [{"ts_ns": t, "from_raw_symbol": f"C{j}", "to_raw_symbol": f"C{j + 1}"}
                          for j, t in enumerate(rolls)]}
        path, sha = write_store(tmp / "stores", root, "step2", store_frame(root, rows), meta)
        assert path.name == step2_name(root)
        stores[root] = {"step2": {"path": str(path), "sha256": sha}}
    for p in BK.PRODUCTS:  # the E.17 manifest lists all 27 roots; E.21 reads only its 17
        stores.setdefault(p, stores["NQ"])
    inputs["run_manifest"] = str(_write(tmp / "run_manifest.json", {
        "schema": BK.RUN_MANIFEST_SCHEMA, "stores": stores}))
    h2_days = [d for d in cals["equity"].trade_dates() if BK.FALLBACK_FIRST <= d <= LAST][::3]
    inputs["h2_result"] = str(_write(tmp / "H2_result.json", {
        "status": "complete", "test": "H2",
        "component": {c: {str(d): 0.01 * ((j % 7) - 3) for j, d in enumerate(h2_days)}
                      for c in BK.COST_CASES}, "grid_dates": [str(d) for d in h2_days]}))
    spec = tmp / "lead_spec.md"
    shutil.copy(K.repo_path(K.SPEC_PATH), spec)
    inputs["spec"] = str(spec)
    inputs["prereg"] = str(_write(tmp / "prereg.md", {"prereg": "synthetic"}))
    return {"tmp": tmp, "inputs": inputs}


@pytest.fixture()
def setup(world, tmp_path):  # noqa: ANN001, ANN201
    inputs = dict(world["inputs"])
    prereg = tmp_path / "prereg.md"
    prereg.write_text("synthetic prereg\n")
    inputs["prereg"] = str(prereg)
    paths = _write(tmp_path / "input_paths.json", inputs)
    freeze = FM.build(tmp_path / "freeze.json", FM.resolve_inputs(inputs))
    registry = tmp_path / "trial_registrations.jsonl"
    init_registry(registry, time_local="2026-10-14T00:00:00-07:00")
    return {"freeze": freeze, "sha": _sha(freeze), "registry": registry, "paths": paths,
            "out": tmp_path / "runs", "marker": tmp_path / "RUN_ONCE.json", "tmp": tmp_path,
            "prereg": prereg}


def _register(s, sha: str | None = None, label: str = "E21") -> None:  # noqa: ANN001
    register(label, [f"{label}-{t}" for t in K.TESTS], s["freeze"], sha or s["sha"], "a" * 64,
             path=s["registry"], time_local="2026-10-14T00:00:00-07:00")


def _args(s, *, sha: str | None = None) -> list[str]:  # noqa: ANN001
    return ["evaluate", "--freeze", str(s["freeze"]), "--freeze-sha256", sha or s["sha"],
            "--out-dir", str(s["out"]), "--marker", str(s["marker"]),
            "--registry", str(s["registry"]), "--input-paths", str(s["paths"])]


def test_an_unregistered_run_is_refused_and_nothing_is_written(setup) -> None:
    assert main(_args(setup)) == K.RC_REFUSED
    assert not setup["marker"].exists() and not setup["out"].exists()


def test_a_registration_under_another_label_is_refused(setup) -> None:
    _register(setup, label="E99")
    assert main(_args(setup)) == K.RC_REFUSED and not setup["marker"].exists()


def test_a_wrong_freeze_sha256_is_refused(setup) -> None:
    _register(setup)
    assert main(_args(setup, sha="0" * 64)) == K.RC_REFUSED
    assert not setup["marker"].exists()


def test_a_changed_frozen_file_is_refused(setup) -> None:
    _register(setup)
    setup["prereg"].write_text("changed after the freeze\n")
    assert main(_args(setup)) == K.RC_REFUSED and not setup["marker"].exists()
    with pytest.raises(FM.FreezeRefused, match="missing or changed"):
        FM.verify(setup["freeze"], setup["sha"],
                  input_overrides=json.loads(setup["paths"].read_text()))


def test_an_existing_output_is_refused(setup) -> None:
    _register(setup)
    setup["out"].mkdir()
    (setup["out"] / "T1_result.json").write_text("{}")
    assert main(_args(setup)) == K.RC_REFUSED and not setup["marker"].exists()


def test_fixed_paths_outside_the_test_mode(setup) -> None:
    _register(setup)
    args = [a for a in _args(setup)]
    i = args.index("--input-paths")
    del args[i:i + 2]
    assert main(args) == K.RC_REFUSED and not setup["marker"].exists()


def test_the_freeze_lists_code_tests_base_rules_and_every_input(setup) -> None:
    body = json.loads(setup["freeze"].read_text())
    paths = {e["path"] for e in body["files"]}
    assert "multiday/run.py" in paths and "base_rules/h2.py" in paths
    assert {"multiday/README.md", "screening/trial_registry.py"} <= paths  # FR-7
    assert any(p.startswith("tests/test_multiday_") for p in paths)
    assert set(body["inputs"]) == set(FM.input_roles())
    assert FM.build is not None
    with pytest.raises(FileExistsError):
        FM.build(setup["freeze"], FM.resolve_inputs(json.loads(setup["paths"].read_text())))


def test_the_run_writes_its_marker_once_and_a_second_run_is_refused(setup) -> None:
    _register(setup)
    assert main(_args(setup)) == K.RC_OK
    marker = json.loads(setup["marker"].read_text())
    assert marker["schema"] == K.MARKER_SCHEMA and marker["freeze_sha256"] == setup["sha"]
    assert len(marker["preflight"]) == len(K.ROOTS)
    out = setup["out"]
    for t in K.TESTS:
        rec = json.loads((out / f"{t}_result.json").read_text())
        assert rec["status"] == "complete" and rec["test_id"] == f"E21-{t}"
        assert set(rec["series"]) == set(BK.COST_CASES) and rec["stats"]["base"]["n"] > 100
        assert rec["sharpe_ci95_base"]["draws"] == K.BOOT_DRAWS
    v = json.loads((out / "verdict.json").read_text())
    assert set(v["tests"]) == set(K.TESTS) and v["holm_alpha"] == 0.025
    assert v["n_trials_at_verdict"] == current_n(setup["registry"])  # baseline + 4
    assert (out / "summary.md").is_file()
    roots = sorted(p.stem for p in (out / "per_root").glob("*.json"))
    assert roots == sorted(K.ROOTS)
    row = json.loads((out / "per_root" / "NQ.json").read_text())
    assert row["holdings"]["T1"] and row["fills"]["T1"] and row["per_contract_daily_dollars"]
    kinds = {f["kind"] for f in row["fills"]["T1"]}
    assert {"rebalance", "roll_out", "roll_in"} <= kinds
    t1 = json.loads((out / "T1_result.json").read_text())
    assert t1["fills_by_kind"]["roll_out"]["fills"] == t1["fills_by_kind"]["roll_in"]["fills"]
    assert main(_args(setup)) == K.RC_REFUSED  # run once
