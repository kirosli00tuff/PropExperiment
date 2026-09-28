"""Stage E.2b Task 4: data/pull_step2.py (the step 2 purchase path) and data/step2_seal.py.

Fake clients only: no network, no DATABENTO_API_KEY. Every ledger, ACCESS doc, vendor root,
sealed store, manifest, unlock log and report lives under tmp_path; the real ledger and the
real holdout manifests are checked untouched. Downloaded files are synthetic DBN files.
"""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from data import adapter, config
from data import holdout as ho
from data import pull_step2 as ps
from data import step2_seal as seal
from data import trade_date_guard as tdg
from data.spend_gate import BudgetRefusedError, read_entries
from screening import harness_freeze
from tests.test_pull_universe import (
    FakeMetadata,
    FakeTimeseries,
    RecordingNamespace,
    e0_like_price,
)

HARNESS = "ab" * 32
ZN_SUBPLAN = slice(56, 61)  # 2024-01, 2024-02 (kept), 2024-03, 2024-04, 2024-05 (sealed)


# ------------------------------------------------------------- helpers ----
def _lines(path: Path) -> int:
    return len(path.read_text(encoding="utf-8").splitlines()) if path.is_file() else 0


def real_state() -> tuple[int, int, int, bool]:
    manifest, log = ho.HOLDOUT2_PATHS.manifest, ho.HOLDOUT2_PATHS.unlock_log
    return (_lines(config.LEDGER_PATH), manifest.stat().st_size if manifest.exists() else 0,
            log.stat().st_size if log.exists() else 0, seal.MANIFEST_DIR.exists())


def gate(tmp_path: Path, **caps: float) -> Any:
    kwargs = {"session_cap_usd": 50.0, "request_cap_usd": 3.0, **caps}
    return ps.step2_gate(ledger_path=tmp_path / "ledger.jsonl",
                         access_doc_path=tmp_path / "ACCESS.md", **kwargs)


def paths_for(tmp_path: Path) -> Any:
    def make(root: str) -> ho.HoldoutPaths:
        return seal.step2_holdout_paths(
            root, sealed_base=tmp_path / "sealed", manifest_dir=tmp_path / "docs" / "holdout2",
            unlock_log=tmp_path / "docs" / "UNLOCK_LOG.md", registration=tmp_path / "REG.md",
            vendor_root=tmp_path / "v", store_parquet=tmp_path / "store" / f"{root}.parquet")
    return make


def buy_client(**timeseries: Any) -> SimpleNamespace:
    downloads: list[dict[str, Any]] = []
    return SimpleNamespace(metadata=FakeMetadata(), timeseries=FakeTimeseries(downloads,
                                                                              **timeseries),
                           batch=RecordingNamespace([]), downloads=downloads)


def quote_client(price: Any = e0_like_price) -> SimpleNamespace:
    hits: list[str] = []
    return SimpleNamespace(metadata=FakeMetadata(price=price),
                           timeseries=RecordingNamespace(hits), batch=RecordingNamespace(hits),
                           billable_hits=hits)


@pytest.fixture
def preflight_ok(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    seen: list[str] = []

    def fake(expected: str, root: Path = config.REPO_ROOT) -> str:
        seen.append(expected)
        return expected

    monkeypatch.setattr(harness_freeze, "preflight", fake)
    return seen


def set_caps(monkeypatch: pytest.MonkeyPatch, session: float, request: float) -> None:
    """The active step 2 caps as step2_gate reads them (data/config.py STEP2_*_CAP_USD)."""
    monkeypatch.setattr(ps, "STEP2_SESSION_CAP_USD", session)
    monkeypatch.setattr(ps, "STEP2_REQUEST_CAP_USD", request)


def run(tmp_path: Path, client: Any, plan: list[ps.Chunk], g: Any = None) -> list[dict]:
    _, done = ps.run_buy(client, g or gate(tmp_path), plan, expected_harness_sha256=HARNESS,
                         vendor_root=tmp_path / "v", seal_paths=paths_for(tmp_path),
                         reports_base=tmp_path / "reports", log=lambda m: None)
    return done


# ----------------------------------------------------------------- plan ----
def test_the_step2_plan_is_71_monthly_chunks_oldest_first_58_kept_then_13_sealed() -> None:
    plan = ps.plan_step2(["ZN", "MBT"])
    zn = [c for c in plan if c.root == "ZN"]
    assert len(plan) == 71 + 48 and len(zn) == 71  # MBT from its first priced month (OC-R)
    assert [(c.params.start, c.params.end) for c in zn][:2] == [
        ("2019-05-01", "2019-06-01"), ("2019-06-01", "2019-07-01")]
    assert [c.sealing for c in zn] == [False] * 58 + [True] * 13
    assert (zn[57].params.start, zn[57].params.end) == ("2024-02-01", "2024-03-01")
    assert (zn[58].params.start, zn[70].params.end) == ("2024-03-01", "2025-04-01")
    assert zn[0].params.as_kwargs() == {"dataset": "GLBX.MDP3", "symbols": ["ZN.v.0"],
                                        "schema": "ohlcv-1m", "stype_in": "continuous",
                                        "start": "2019-05-01", "end": "2019-06-01"}
    assert [c.root for c in plan] == ["ZN"] * 71 + ["MBT"] * 48  # root by root


def test_the_ml_route_is_m1s_31_contracts_and_clusters_come_from_the_vehicle_table() -> None:
    assert ps.ML_ROUTE_ROOTS == (
        "NQ", "RTY", "YM", "ZT", "ZF", "ZN", "TN", "ZB", "UB", "6E", "6A", "6B", "6C", "6J",
        "6S", "6N", "CL", "NG", "RB", "HO", "GC", "SI", "HG", "ZC", "ZW", "ZS", "ZM", "ZL",
        "HE", "LE", "MBT")
    vehicles = ps.cluster_vehicles()
    assert vehicles["K1"] == ("MNQ", "M2K", "MYM") and vehicles["K4"] == ("MCL", "NG")
    assert vehicles["K7"] == () and sum(len(v) for v in vehicles.values()) == 22  # set (b)
    assert ps.roots_for(True, None) == ps.ML_ROUTE_ROOTS
    assert ps.roots_for(False, "K5") == ("MGC", "MHG")
    with pytest.raises(ps.Step2Error, match="exactly one"):
        ps.roots_for(True, "K1")


def test_late_listed_contracts_start_at_their_first_priced_month_oc_r() -> None:
    assert ps.FIRST_PRICED_MONTH == {"MBT": "2021-04-01", "MCL": "2021-06-01",
                                     "MHG": "2022-04-01"}
    for root, first, n in (("MBT", "2021-04-01", 48), ("MCL", "2021-06-01", 46),
                           ("MHG", "2022-04-01", 36)):
        plan = ps.plan_step2([root])
        assert plan[0].params.start == first and len(plan) == n
        assert [c.sealing for c in plan][-13:] == [True] * 13  # every holdout-2 chunk still
        assert len(ps.unsealed_chunks(root)) == n - 13
    assert ps.plan_step2(["ZN"])[0].params.start == "2019-05-01"


@pytest.mark.parametrize("root,month", [("MBT", "2021-03-01"), ("MCL", "2019-05-01"),
                                        ("MHG", "2022-03-01")])
def test_a_month_before_listing_is_refused_by_name_before_any_call(
        tmp_path: Path, preflight_ok: list[str], root: str, month: str) -> None:
    start, end = next(c for c in ps.STEP2_CHUNKS if c[0] == month)
    early = ps.chunk_for(root, start, end)
    with pytest.raises(ps.Step2BeforeListing, match="first vendor-priceable month"):
        ps.check_chunk(early)
    client = buy_client()
    with pytest.raises(ps.Step2BeforeListing):
        run(tmp_path, client, [early])
    with pytest.raises(ps.Step2BeforeListing):
        ps.run_quote_only(quote_client(), gate(tmp_path), [early], log=lambda m: None)
    assert client.metadata.calls == [] and read_entries(tmp_path / "ledger.jsonl") == []


def test_mng_with_a_pricing_gap_is_refused_for_step2_by_name() -> None:
    with pytest.raises(ps.Step2RefusedRoot, match="gap 2020-01..2023-09"):
        ps.plan_step2(["MNG"])


def test_the_cluster_purchase_mode_buys_traded_vehicles_and_member_legs(tmp_path: Path) -> None:
    roots = ps.cluster_roots()
    assert roots["K2"] == ("ZT", "ZF", "ZN", "TN", "ZB", "UB")  # undersized ZT, ZF traded (R10)
    assert roots["K3"] == ("6E", "6A", "6B", "6C", "6J", "6S", "6N")
    assert roots["K7"] == ("MBT",) and roots["K6"][0] == "ZC"
    assert roots["K8"] == ("MGC", "6C", "MNQ", "MCL", "MBT")  # legs only; MES excluded
    assert ps.roots_for(False, "K8") == roots["K8"] and ps.roots_for(False, "K7") == ("MBT",)
    assert "MES" not in {r for rs in roots.values() for r in rs}
    assert len({r for rs in roots.values() for r in rs}) == 28
    thin = tmp_path / "vehicles.json"
    thin.write_text(json.dumps({"exposures": [
        {"exposure": "gold", "cluster": "K5", "status": "chosen", "vehicle": "MGC"}]}),
        encoding="utf-8")
    with pytest.raises(ps.Step2Error, match="nothing to buy"):
        ps.roots_for(False, "K1", thin)
    with pytest.raises(ps.Step2Error, match="leg exposure 'CAD'"):
        ps.roots_for(False, "K8", thin)


def test_quote_set_b2_prices_each_leg_root_once_and_totals_k8(tmp_path: Path) -> None:
    client = quote_client()
    ledger = tmp_path / "ledger.jsonl"
    out_json, out_md = tmp_path / "q.json", tmp_path / "q.md"
    rc = ps.main(["--quote-only", "--set", "clusters-legs"], key_loader=lambda: "k",
                 gate_factory=lambda: ps.step2_gate(ledger_path=ledger,
                                                    access_doc_path=tmp_path / "A.md"),
                 client_factory=lambda key: client, quotes_json=out_json, quotes_md=out_md,
                 log=lambda m: None)
    section = json.loads(out_json.read_text(encoding="utf-8"))["sets"]["clusters-legs"]
    unique = {r for rs in ps.cluster_roots().values() for r in rs}
    assert rc == 0 and section["contracts"] == 28 and section["complete"]
    assert len(read_entries(ledger)) == sum(len(ps.step2_chunks(r)) for r in unique)
    k8 = section["per_cluster"]["K8"]
    assert k8["contracts"] == ["MGC", "6C", "MNQ", "MCL", "MBT"]
    assert k8["usd"] == pytest.approx(sum(section["per_contract"][r]["usd"]
                                          for r in k8["contracts"]))
    assert "(b2)" in out_md.read_text(encoding="utf-8")


@pytest.mark.parametrize("root", ["MES", "PL", "ES", "NKD", "6M", "MET", "ZZ", "zn"])
def test_refused_roots_raise_before_any_plan(root: str) -> None:
    with pytest.raises(ps.Step2RefusedRoot):
        ps.plan_step2(["ZN", root])


def test_check_chunk_refuses_windows_outside_the_71_and_a_wrong_sealing_flag(
        monkeypatch: pytest.MonkeyPatch) -> None:
    # Holdout-1 side: MBT's June 2026 chunk is no step 2 chunk (and the guard books it to 06-22).
    with pytest.raises(ps.Step2ChunkError, match="not one of the 71"):
        ps.check_chunk(ps.chunk_for("MBT", "2026-06-01", "2026-06-21"))
    with pytest.raises(tdg.HoldoutTradeDateRefused, match="holdout-1"):
        tdg.refuse_holdout_bookings("MBT", "2026-06-01", "2026-06-21", sealing=True)
    with pytest.raises(ps.Step2ChunkError, match="not one of the 71"):
        ps.check_chunk(ps.chunk_for("ZN", "2024-03-01", "2024-03-15"))
    sealed = ps.chunk_for("ZN", "2024-03-01", "2024-04-01")
    with pytest.raises(ps.Step2ChunkError, match="sealing flag"):
        ps.check_chunk(ps.Chunk("ZN", sealed.params, sealing=False))
    mbp = ps.Chunk("ZN", ps.RequestParams("GLBX.MDP3", ("ZN.v.0",), "mbp-1", "continuous",
                                          "2019-05-01", "2019-06-01"), False)
    with pytest.raises(ps.Step2ChunkError, match="not a step 2 request"):
        ps.check_chunk(mbp)

    # The trade-date guard is wired in with the chunk's sealing flag.
    seen: list[bool] = []

    def refuse(root: str, start: str, end: str, *, sealing: bool = False) -> None:
        seen.append(sealing)
        raise tdg.HoldoutTradeDateRefused("planted")

    monkeypatch.setattr(tdg, "refuse_holdout_bookings", refuse)
    with pytest.raises(ps.Step2TradeDateError, match="planted"):
        ps.check_chunk(sealed)
    assert seen == [True]


# ----------------------------------------------------------- quote-only ----
def test_quote_only_issues_no_billable_request_and_ledgers_zero_lines_on_acct2(
        tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    # Arrange
    before = real_state()
    client = quote_client()
    ledger = tmp_path / "ledger.jsonl"
    ledger.write_text(json.dumps({"session_id": "stage-E.1-2026-09-24", "event": "commit",
                                  "usd": 103.48, "account": "acct-2",
                                  "request": {"x": 1}}) + "\n", encoding="utf-8")
    out_json, out_md = tmp_path / "q.json", tmp_path / "q.md"

    # Act
    rc = ps.main(["--quote-only", "--set", "ml-route"], key_loader=lambda: "SECRET-KEY-XYZ",
                 gate_factory=lambda: ps.step2_gate(ledger_path=ledger,
                                                    access_doc_path=tmp_path / "A.md"),
                 client_factory=lambda key: client, quotes_json=out_json, quotes_md=out_md,
                 log=lambda m: None)

    # Assert: nothing billable touched; every new line a $0.00 quote on acct-2 under the active
    # step 2 purchase policy's session id (data/config.py; Stage E.5 on, stage-E.5-2026-09-27).
    assert rc == 0 and client.billable_hits == []
    with pytest.raises(RuntimeError, match="forbidden"):
        client.timeseries.get_range(dataset="GLBX.MDP3")
    new = read_entries(ledger)[1:]
    assert len(new) == 30 * 71 + 48  # MBT from 2021-04 (OC-R): no pre-listing month requested
    assert {(e["event"], e["usd"], e["account"], e["session_id"]) for e in new} == {
        ("quote", 0.0, "acct-2", config.STEP2_PURCHASE_SESSION_ID)}
    payload = json.loads(out_json.read_text(encoding="utf-8"))
    section = payload["sets"]["ml-route"]
    assert section["contracts"] == 31 and section["chunks"] == 2178 and section["complete"]
    assert section["first_priced_month"] == {"MBT": "2021-04-01"}
    assert payload["account"]["spent_usd"] == pytest.approx(103.48)
    assert payload["account"]["cap_headroom_usd"] == pytest.approx(21.52)
    assert (payload["session_cap_usd"], payload["request_cap_usd"]) == (
        ps.STEP2_SESSION_CAP_USD, ps.STEP2_REQUEST_CAP_USD)  # the active caps, whatever they are
    total = section["total_usd"]
    assert total == pytest.approx(sum(r["usd"] for r in section["per_contract"].values()))
    assert total == pytest.approx(sum(c["usd"] for c in section["per_cluster"].values()))
    assert section["topup_usd_at_quote"] == pytest.approx(round(max(0, total - 21.52), 2))
    assert set(section["per_cluster"]) == set(ps.CLUSTERS)
    md = out_md.read_text(encoding="utf-8")
    assert "31 contracts, 2178 chunks" in md and "| MBT | K7 |" in md
    out = capsys.readouterr()
    assert "SECRET-KEY-XYZ" not in out.out + out.err + md + out_json.read_text(encoding="utf-8")
    assert real_state() == before


def test_quote_failures_mark_the_set_incomplete_and_retry_quotes_only_the_failed(
        tmp_path: Path) -> None:
    # Arrange: three ZN months fail on the first pass (a transient vendor problem).
    failing = {"2020-01-01", "2020-02-01", "2020-03-01"}

    def price(kw: dict[str, Any]) -> float:
        if kw["symbols"] == ["ZN.v.0"] and kw["start"] in failing:
            raise ValueError("HTTP 500 planted")
        return e0_like_price(kw)

    ledger = tmp_path / "ledger.jsonl"
    g = ps.step2_gate(ledger_path=ledger, access_doc_path=tmp_path / "A.md")
    groups = {"K7": ("MBT",), "K2": ("ZN",)}
    plan = ps.plan_step2(["MBT", "ZN"])

    # Act
    ps.run_quote_only(quote_client(price), g, plan, log=lambda m: None)
    first = ps.summarize_set("x", groups, ps.quotes_from_ledger(plan, read_entries(ledger),
                                                                g.session_id),
                             ps.account_position(g))
    retry_client = quote_client()
    ps.run_quote_only(retry_client, g, plan, log=lambda m: None, retry_failed=True)
    second = ps.summarize_set("x", groups, ps.quotes_from_ledger(plan, read_entries(ledger),
                                                                 g.session_id),
                              ps.account_position(g))

    # Assert
    assert not first["complete"] and first["chunks_failed"] == 3
    assert first["per_cluster"]["K2"]["complete"] is False and first["per_cluster"]["K7"][
        "complete"]
    assert len(retry_client.metadata.calls) == 2 * 3  # get_cost + billable size, failed only
    assert second["complete"] and second["chunks_quoted"] == 48 + 71


# ----------------------------------------------------------------- buy ----
def test_the_buy_refuses_when_the_harness_preflight_raises(tmp_path: Path,
                                                           monkeypatch: pytest.MonkeyPatch
                                                           ) -> None:
    def refuse(expected: str, root: Path = config.REPO_ROOT) -> str:
        raise harness_freeze.HarnessFreezeError("planted: manifest mismatch")

    monkeypatch.setattr(harness_freeze, "preflight", refuse)
    client = buy_client()
    plan = ps.plan_step2(["ZN"])[ZN_SUBPLAN]
    with pytest.raises(harness_freeze.HarnessFreezeError, match="planted"):
        run(tmp_path, client, plan)
    called: list[str] = []
    rc = ps.main(["--buy", "--ml-route", "--harness-sha256", HARNESS],
                 key_loader=lambda: called.append("key") or "k",
                 gate_factory=lambda: gate(tmp_path),
                 client_factory=lambda k: called.append("client"), log=lambda m: None)
    assert rc == ps.RC_REFUSED and called == []
    assert client.metadata.calls == [] and client.downloads == []
    assert read_entries(tmp_path / "ledger.jsonl") == []


def test_the_buy_refuses_to_start_with_the_active_zero_caps(
        tmp_path: Path, preflight_ok: list[str], monkeypatch: pytest.MonkeyPatch) -> None:
    set_caps(monkeypatch, 0.0, 0.0)  # R-A2-2: the config's cap values are not pinned
    client = buy_client()
    zero = ps.step2_gate(ledger_path=tmp_path / "ledger.jsonl",
                         access_doc_path=tmp_path / "ACCESS.md")
    assert (zero.session_cap_usd, zero.request_cap_usd, zero.account_id) == (0.0, 0.0, "acct-2")
    assert zero.account_cap_usd == config.ACCOUNT_2_CAP_USD
    with pytest.raises(ps.Step2CapError, match="sets its own caps in data/config.py"):
        run(tmp_path, client, ps.plan_step2(["ZN"])[ZN_SUBPLAN], zero)
    assert preflight_ok == [HARNESS]  # the preflight ran first
    rc = ps.main(["--buy", "--cluster", "K2", "--harness-sha256", HARNESS],
                 key_loader=lambda: pytest.fail("key loaded"), gate_factory=lambda: zero,
                 client_factory=lambda k: pytest.fail("client built"), log=lambda m: None)
    assert rc == ps.RC_REFUSED
    assert client.metadata.calls == [] and read_entries(tmp_path / "ledger.jsonl") == []


def test_main_buy_requires_the_harness_sha256(tmp_path: Path) -> None:
    rc = ps.main(["--buy", "--ml-route"], key_loader=lambda: pytest.fail("key"),
                 gate_factory=lambda: gate(tmp_path), log=lambda m: None)
    assert rc == ps.RC_REFUSED


def test_buy_seals_each_holdout_chunk_after_its_byte_check_before_the_next_request(
        tmp_path: Path, preflight_ok: list[str], monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange: record the order of downloads, byte checks and seals.
    before = real_state()
    events: list[str] = []
    make = paths_for(tmp_path)
    zn_paths = make("ZN")

    def on_call(kw: dict[str, Any]) -> None:
        sealed = [Path(r["original_path"]).name for r in
                  (ho.load_manifest(zn_paths)["raw_files"] if zn_paths.manifest.exists() else [])]
        plain = [p.name for p in seal.chunk_paths("ZN", zn_paths) if p.exists()]
        events.append(f"download {kw['start']} sealed={len(sealed)} plaintext={plain}")

    real_check, real_seal = adapter.delivered_record_bytes, seal.seal_chunk
    monkeypatch.setattr(adapter, "delivered_record_bytes",
                        lambda p: events.append(f"check {Path(p).name}") or real_check(p))
    monkeypatch.setattr(seal, "seal_chunk", lambda r, raw, p, note="": events.append(
        f"seal {Path(raw).name}") or real_seal(r, raw, p, note=note))
    client = buy_client(on_call=on_call)
    plan = ps.plan_step2(["ZN"])[ZN_SUBPLAN]

    # Act
    done = run(tmp_path, client, plan)

    # Assert: order, ledger, seals, no plaintext of a sealed range, manifests.
    assert [e.split()[0] for e in events] == ["download", "check"] * 2 + [
        "download", "check", "seal"] * 3
    assert events[4] == "download 2024-03-01 sealed=0 plaintext=[]"
    assert events[7] == "download 2024-04-01 sealed=1 plaintext=[]"
    assert events[10] == "download 2024-05-01 sealed=2 plaintext=[]"
    assert [d["action"].split()[0] for d in done] == ["bought", "bought"] + ["bought"] * 3
    entries = read_entries(tmp_path / "ledger.jsonl")
    assert [e["event"] for e in entries] == ["quote", "commit", "settle"] * 5
    assert {e["account"] for e in entries} == {"acct-2"}
    assert {e["session_id"] for e in entries} == {config.STEP2_PURCHASE_SESSION_ID}
    report = seal.verify("ZN", zn_paths)
    assert report["chunks_sealed"] == 3 and report["sealed_in_order"]
    assert report["unsealed_plaintext_present"] == [] and report["unlock_log_ok"]
    assert all(v["sealed_ok"] and v["plaintext_absent"] for v in report["raw_files"].values())
    assert not any(p.exists() for p in seal.chunk_paths("ZN", zn_paths))
    manifest = json.loads((tmp_path / "reports" / "purchase_ZN.json").read_text("utf-8"))
    assert [f["name"] for f in manifest["files"]] == ["range=2024-01-01_2024-02-01.dbn.zst",
                                                      "range=2024-02-01_2024-03-01.dbn.zst"]
    assert all(len(f["sha256"]) == 64 and f["record_count"] > 0 for f in manifest["files"])
    assert len(manifest["sealed_chunks"]) == 3 and manifest["harness_sha256"] == HARNESS
    log = (tmp_path / "docs" / "UNLOCK_LOG.md").read_text(encoding="utf-8")
    assert log.count("SEALED holdout 2 ZN raw chunk") == 3 and " UNLOCK " not in log
    assert real_state() == before


def test_a_download_failing_mid_chunk_leaves_no_plaintext(tmp_path: Path,
                                                          preflight_ok: list[str]) -> None:
    client = buy_client(fail=ConnectionError("dropped mid-transfer"))
    chunk = ps.plan_step2(["ZN"])[58]  # 2024-03, sealing
    with pytest.raises(ps.DownloadError, match="dropped"):
        run(tmp_path, client, [chunk])
    target = ps.target_path(chunk.params, tmp_path / "v")
    assert not target.exists() and not target.with_name(target.name + ".partial").exists()
    assert [e["event"] for e in read_entries(tmp_path / "ledger.jsonl")] == ["quote", "commit"]


@pytest.mark.parametrize("stage", ["byte_check", "seal"])
def test_a_failure_after_the_download_purges_the_holdout_plaintext(
        tmp_path: Path, preflight_ok: list[str], monkeypatch: pytest.MonkeyPatch,
        stage: str) -> None:
    def boom(*a: Any, **k: Any) -> Any:
        raise OSError(f"planted {stage} failure")

    if stage == "byte_check":
        monkeypatch.setattr(adapter, "delivered_record_bytes", boom)
    else:
        monkeypatch.setattr(ho, "open_sealed", boom)
    chunk = ps.plan_step2(["ZN"])[58]
    with pytest.raises((ps.DeliveryCheckError, OSError)):
        run(tmp_path, buy_client(), [chunk])
    target = ps.target_path(chunk.params, tmp_path / "v")
    assert not target.exists() and not target.with_name(target.name + ".partial").exists()
    assert not paths_for(tmp_path)("ZN").manifest.exists()


def test_a_delivery_above_the_quote_is_settled_pro_rata_sealed_and_stops(
        tmp_path: Path, preflight_ok: list[str]) -> None:
    chunk = ps.plan_step2(["ZN"])[58]
    with pytest.raises(ps.DeliveryCheckError, match="settled pro rata and sealed"):
        run(tmp_path, buy_client(extra_records=10), [chunk])
    settle = read_entries(tmp_path / "ledger.jsonl")[-1]
    assert settle["event"] == "settle" and settle["actual_usd"] > settle["quoted_usd"]
    assert seal.verify("ZN", paths_for(tmp_path)("ZN"))["chunks_sealed"] == 1
    assert not ps.target_path(chunk.params, tmp_path / "v").exists()


def test_the_account_cap_on_acct2_refuses_and_acct1_spend_does_not_count(
        tmp_path: Path, preflight_ok: list[str]) -> None:
    # Arrange: acct-1 spend is not acct-2's; acct-2 already at $124.99 of its $125.00 cap.
    ledger = tmp_path / "ledger.jsonl"
    ledger.write_text(json.dumps({"session_id": "old", "event": "commit", "usd": 110.0,
                                  "account": "acct-1", "request": {"a": 1}}) + "\n",
                      encoding="utf-8")
    chunk = ps.plan_step2(["ZN"])[0]
    run(tmp_path, buy_client(), [chunk])  # acct-1's $110 does not block acct-2
    with ledger.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({"session_id": "old", "event": "commit", "usd": 124.99,
                             "account": "acct-2", "request": {"b": 1}}) + "\n")

    # Act / Assert
    with pytest.raises(BudgetRefusedError, match="account cap acct-2"):
        run(tmp_path, buy_client(), [ps.plan_step2(["ZN"])[1]])
    assert read_entries(ledger)[-1]["event"] == "refused"
    with pytest.raises(BudgetRefusedError, match="per-request cap"):
        run(tmp_path, buy_client(), [ps.plan_step2(["ZN"])[2]],
            gate(tmp_path, request_cap_usd=0.01))


def test_resume_skips_settled_and_sealed_chunks_without_quoting_them(
        tmp_path: Path, preflight_ok: list[str]) -> None:
    plan = ps.plan_step2(["ZN"])[ZN_SUBPLAN]
    run(tmp_path, buy_client(), plan)
    again = buy_client()
    done = run(tmp_path, again, plan)
    assert again.metadata.calls == [] and again.downloads == []
    assert [d["action"].split(":")[0] for d in done] == ["skipped"] * 2 + ["skipped"] * 3


def test_resume_across_sessions_accepts_another_sessions_settle(tmp_path: Path,
                                                                preflight_ok: list[str]) -> None:
    chunk = ps.plan_step2(["ZN"])[0]
    run(tmp_path, buy_client(), [chunk])
    later = ps.LockedQuoteGate("stage-E.3-K2", session_cap_usd=5.0, request_cap_usd=3.0,
                               account="acct-2", ledger_path=tmp_path / "ledger.jsonl",
                               access_doc_path=tmp_path / "A.md")
    again = buy_client()
    assert run(tmp_path, again, [chunk], later)[0]["action"].startswith("skipped")
    assert again.metadata.calls == []


def test_resume_seals_a_downloaded_holdout_chunk_and_finishes_an_interrupted_seal(
        tmp_path: Path, preflight_ok: list[str], monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange: chunk 2024-03 on disk unsealed (cut off between link and seal).
    make = paths_for(tmp_path)
    chunk = ps.plan_step2(["ZN"])[58]
    target = ps.target_path(chunk.params, tmp_path / "v")
    target.parent.mkdir(parents=True)
    FakeTimeseries([]).get_range(path=target, **chunk.params.as_kwargs())

    # Act 1
    done = run(tmp_path, buy_client(), [chunk])

    # Assert 1: sealed without a new purchase
    assert done[0]["action"].startswith("SEALED as holdout 2 on resume")
    assert not target.exists() and seal.verify("ZN", make("ZN"))["chunks_sealed"] == 1

    # Arrange 2: the next chunk's seal stops after its manifest record (plaintext left).
    nxt = ps.plan_step2(["ZN"])[59]
    monkeypatch.setattr(ho, "_pin_log_and_remove",
                        lambda raw, paths, manifest: (_ for _ in ()).throw(OSError("cut")))
    with pytest.raises(OSError, match="cut"):
        run(tmp_path, buy_client(), [nxt])
    monkeypatch.undo()
    monkeypatch.setattr(harness_freeze, "preflight", lambda e, root=None: e)
    nxt_target = ps.target_path(nxt.params, tmp_path / "v")
    assert not nxt_target.exists()  # purged on failure: no plaintext kept
    assert seal.is_sealed(nxt_target, make("ZN"))

    # Act 2: resume sees it sealed and bought; nothing is re-bought.
    again = buy_client()
    done = run(tmp_path, again, [nxt])
    assert done[0]["action"].startswith("skipped: sealed") and again.downloads == []


def test_resume_finishes_a_seal_whose_plaintext_is_still_on_disk(
        tmp_path: Path, preflight_ok: list[str]) -> None:
    make = paths_for(tmp_path)
    chunk = ps.plan_step2(["ZN"])[58]
    run(tmp_path, buy_client(), [chunk])
    target = ps.target_path(chunk.params, tmp_path / "v")
    blob_record = ho.load_manifest(make("ZN"))["raw_files"][0]
    sealed_blob = make("ZN").sealed_root / blob_record["sealed_relpath"]
    plain = ho.open_sealed(sealed_blob.read_bytes(), ho.ACKNOWLEDGEMENT,
                           bytes.fromhex(ho.load_manifest(make("ZN"))["salt_hex"]),
                           blob_record["sha256_plaintext"])
    target.write_bytes(plain)  # what a seal cut off after its manifest record leaves
    done = run(tmp_path, buy_client(), [chunk])
    assert done[0]["action"] == "plaintext of an interrupted seal removed on resume"
    assert not target.exists()


def test_resume_names_a_kept_file_without_a_settled_line(tmp_path: Path,
                                                         preflight_ok: list[str]) -> None:
    chunk = ps.plan_step2(["ZN"])[0]
    target = ps.target_path(chunk.params, tmp_path / "v")
    target.parent.mkdir(parents=True)
    target.write_bytes(b"stray")
    with pytest.raises(ps.ResumeStateError, match="without a settled ledger line"):
        run(tmp_path, buy_client(), [chunk])
    assert target.read_bytes() == b"stray"  # nothing deleted


def test_a_holdout_chunk_out_of_order_is_refused_before_any_buy(tmp_path: Path,
                                                                preflight_ok: list[str]) -> None:
    client = buy_client()
    with pytest.raises(ps.ResumeStateError, match="out of order"):
        run(tmp_path, client, [ps.plan_step2(["ZN"])[59]])  # 2024-04 before 2024-03
    assert client.metadata.calls == [] and client.downloads == []


# ------------------------------------------------------------ seal store ----
def test_step2_seal_refuses_mes_a_foreign_manifest_and_a_wrong_path(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="MES"):
        seal.step2_holdout_paths("MES")
    make = paths_for(tmp_path)
    raw = seal.chunk_paths("ZN", make("ZN"))[0]
    raw.parent.mkdir(parents=True)
    raw.write_bytes(b"x" * 100)
    elsewhere = tmp_path / "elsewhere" / raw.name
    elsewhere.parent.mkdir()
    elsewhere.write_bytes(b"x")
    with pytest.raises(ValueError, match="not where the step 2 path stores"):
        seal.seal_chunk("ZN", elsewhere, make("ZN"))
    seal.seal_chunk("ZN", raw, make("ZN"))
    foreign = make("ZN")
    with pytest.raises(ValueError, match="belongs to 'ZN'"):
        seal._refuse_seal("ZB", seal.chunk_paths("ZB", foreign)[1], foreign,
                          ho.load_manifest(foreign))
    assert ps.status(["ZT"])["ZT"] == {"state": "not_bought"}


# ------------------------------------------- data.holdout status (Q2) ----
def _beside(tmp_path: Path) -> ho.HoldoutPaths:
    """MES's holdout-2 paths moved under tmp_path, laid out as in the repo (docs/, sealed/)."""
    return ho.HoldoutPaths(sealed_root=tmp_path / "sealed" / "MES_holdout_v2",
                           manifest=tmp_path / "docs" / "HOLDOUT2_MANIFEST.json",
                           unlock_log=tmp_path / "docs" / "UNLOCK_LOG.md",
                           registration=tmp_path / "REG.md",
                           research_parquet=tmp_path / "mes.parquet", holdout_id=2,
                           vendor_root=tmp_path / "v")


def _stub_status(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(ho, "HOLDOUT2_PATHS", _beside(tmp_path))
    monkeypatch.setattr(ho, "verify_seal", lambda paths=None: {
        "all_ok": True, "unlocks_logged": 0, "state": "stub"})


def test_status_products_are_empty_and_all_ok_unchanged_with_no_product_store(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _stub_status(monkeypatch, tmp_path)
    report = ho.status_report()
    assert report["holdout_2"]["products"] == {} and report["all_ok"] is True
    assert {k: v for k, v in report.items() if k != "holdout_2"} == ho.verify_seal()


def test_status_folds_every_product_store_into_the_top_level_all_ok(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange: ZN's store beside MES's (paths_for uses the same tmp layout).
    _stub_status(monkeypatch, tmp_path)
    zn = paths_for(tmp_path)("ZN")
    raws = seal.chunk_paths("ZN", zn)
    raws[0].parent.mkdir(parents=True)
    raws[0].write_bytes(b"chunk 0")
    seal.seal_chunk("ZN", raws[0], zn)

    # Act / Assert: partially sealed -> not ok, and the top-level all_ok turns False.
    report = ho.status_report()
    assert report["holdout_2"]["products"]["ZN"]["state"] == "partially_sealed"
    assert report["all_ok"] is False and report["holdout_2"]["all_ok"] is True
    for raw in raws[1:]:
        raw.write_bytes(b"chunk " + raw.name.encode())
        seal.seal_chunk("ZN", raw, zn)
    report = ho.status_report()
    assert report["holdout_2"]["products"]["ZN"]["all_ok"] is True and report["all_ok"] is True
    (tmp_path / "docs" / "holdout2" / f"zz{seal.MANIFEST_SUFFIX}").write_text("{}", "utf-8")
    report = ho.status_report()  # a manifest that names no product root: not ok, not skipped
    assert report["holdout_2"]["products"]["zz"]["all_ok"] is False and not report["all_ok"]


def test_the_product_stores_sit_beside_mes_holdout2_in_the_repo() -> None:
    assert ho.HOLDOUT2_PATHS.manifest.parent / seal.MANIFEST_DIR.name == seal.MANIFEST_DIR
    assert ho.HOLDOUT2_PATHS.sealed_root.parent == seal.SEALED_BASE
    assert ho.status_report()["holdout_2"]["products"] == seal.verify_all(ho.HOLDOUT2_PATHS)


# ------------------------------------------------ Stage E.5: the active policy ----
# Lead ruling R-A2-2: the E.5 caps are set in Task B1 (a data/config.py edit only), so these tests
# pin behavior and hold at 0.00 and at any positive caps; none pins the config's cap values.
E5_SESSION = "stage-E.5-2026-09-27"
CAP_CASES = [(0.0, 0.0), (21.52, 3.00)]


@pytest.mark.parametrize("caps", CAP_CASES)
def test_the_step2_gate_is_the_e5_session_on_acct2_and_reads_the_active_caps(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caps: tuple[float, float]) -> None:
    # Arrange: the active names point at the E.5 block (the session id does not change in B1).
    assert config.STAGE_E5_SESSION_ID == E5_SESSION == config.STEP2_PURCHASE_SESSION_ID
    assert (config.STEP2_SESSION_CAP_USD, config.STEP2_REQUEST_CAP_USD) == (
        config.E5_SESSION_CAP_USD, config.E5_REQUEST_CAP_USD)
    assert (ps.STEP2_SESSION_CAP_USD, ps.STEP2_REQUEST_CAP_USD) == (
        config.STEP2_SESSION_CAP_USD, config.STEP2_REQUEST_CAP_USD)
    assert config.STAGE_E2B_SESSION_ID == "stage-E.2b-2026-09-26"  # the E.2b block is kept
    set_caps(monkeypatch, *caps)

    # Act: the gate as the CLI builds it (no cap override)
    g = ps.step2_gate(ledger_path=tmp_path / "ledger.jsonl", access_doc_path=tmp_path / "A.md")

    # Assert
    assert (g.session_id, g.account_id) == (E5_SESSION, "acct-2")
    assert (g.session_cap_usd, g.request_cap_usd) == caps
    assert g.account_cap_usd == config.ACCOUNT_2_CAP_USD
    if caps == (0.0, 0.0):
        with pytest.raises(ps.Step2CapError, match=E5_SESSION):
            ps.require_buy_caps(g)
    else:  # positive caps pass the start check: nothing here depends on 0.00
        ps.require_buy_caps(g)


def test_the_buy_refuses_before_any_vendor_call_at_zero_caps(
        tmp_path: Path, preflight_ok: list[str], monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange
    set_caps(monkeypatch, 0.0, 0.0)
    ledger = tmp_path / "ledger.jsonl"

    # Act
    rc = ps.main(["--buy", "--cluster", "K4", "--harness-sha256", HARNESS],
                 key_loader=lambda: pytest.fail("key loaded"),
                 gate_factory=lambda: ps.step2_gate(ledger_path=ledger,
                                                    access_doc_path=tmp_path / "A.md"),
                 client_factory=lambda k: pytest.fail("client built"), log=lambda m: None)

    # Assert: refused after the preflight, before any key, client or ledger line.
    assert rc == ps.RC_REFUSED and preflight_ok == [HARNESS]
    assert read_entries(ledger) == []


@pytest.mark.parametrize("caps", CAP_CASES)
def test_quote_only_ledgers_only_zero_lines_under_the_e5_session(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caps: tuple[float, float]) -> None:
    # Arrange
    before = real_state()
    set_caps(monkeypatch, *caps)
    ledger = tmp_path / "ledger.jsonl"
    client = quote_client()

    # Act
    rc = ps.main(["--quote-only", "--set", "ml-route"], key_loader=lambda: "k",
                 gate_factory=lambda: ps.step2_gate(ledger_path=ledger,
                                                    access_doc_path=tmp_path / "A.md"),
                 client_factory=lambda key: client, quotes_json=tmp_path / "q.json",
                 quotes_md=tmp_path / "q.md", log=lambda m: None)

    # Assert: whatever the caps, only $0.00 quote lines on acct-2 under the E.5 session id.
    entries = read_entries(ledger)
    assert rc == 0 and client.billable_hits == [] and entries
    assert {(e["event"], e["usd"], e["account"], e["session_id"]) for e in entries} == {
        ("quote", 0.0, "acct-2", E5_SESSION)}
    payload = json.loads((tmp_path / "q.json").read_text(encoding="utf-8"))
    assert payload["session_id"] == E5_SESSION
    assert (payload["session_cap_usd"], payload["request_cap_usd"]) == caps
    assert real_state() == before
