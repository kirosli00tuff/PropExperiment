"""Harness v10 (Stage E.14): data.pull_hist, the es2011 and ext2010 plans, and the --plan hand-off
in data.pull_step2.

Fake clients only: no network, no key (the key loader returns an obviously fake value that is
checked never to reach any output). Every ledger, ACCESS doc, vendor root, manifest, registry and
quotes file lives under tmp_path; the real spend ledger and trial registry are checked untouched.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable, Iterator
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from data import config
from data import pull_hist as ph
from data import pull_step2 as ps
from data.spend_gate import read_entries
from screening import harness_freeze
from screening import trial_registry as tr
from tests.test_pull_universe import (
    FakeMetadata,
    FakeTimeseries,
    RecordingNamespace,
    e0_like_price,
)

HARNESS = "cd" * 32
FAKE_KEY = "fake-v10-key-not-real"
E14 = "stage-E.14-2026-10-05"


# ------------------------------------------------------------- helpers ----
@pytest.fixture(autouse=True, scope="module")
def real_files_untouched() -> Iterator[None]:
    paths = (config.LEDGER_PATH, tr.REGISTRY_PATH, config.ACCESS_DOC_PATH)
    before = [p.read_bytes() if p.is_file() else None for p in paths]
    yield
    assert [p.read_bytes() if p.is_file() else None for p in paths] == before


@pytest.fixture
def preflight_ok(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    seen: list[str] = []
    monkeypatch.setattr(harness_freeze, "preflight",
                        lambda expected, root=None: seen.append(expected) or expected)
    return seen


def never(what: str) -> Callable[..., Any]:
    def fail(*args: Any, **kwargs: Any) -> Any:
        pytest.fail(f"{what} was called")
    return fail


def registry_with(tmp_path: Path, *tests: str) -> Path:
    path = tmp_path / "registry.jsonl"
    tr.init_registry(path)
    for test in tests:
        freeze = tmp_path / f"freeze_{test}.md"
        freeze.write_text(f"frozen {test}\n", encoding="utf-8")
        tr.register(test, [f"{test}-T1", f"{test}-T2"], freeze,
                    hashlib.sha256(freeze.read_bytes()).hexdigest(), HARNESS, path=path)
    return path


def gate_kwargs(tmp_path: Path) -> dict[str, Any]:
    return {"ledger_path": tmp_path / "ledger.jsonl", "access_doc_path": tmp_path / "A.md"}


class ConditionMetadata(FakeMetadata):
    def get_dataset_condition(self, **kwargs: Any) -> list[dict[str, str]]:
        self.calls.append(("get_dataset_condition", kwargs))
        return [{"date": kwargs["start_date"], "condition": "available"}]


class FakeSymbology:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    def resolve(self, **kwargs: Any) -> dict[str, Any]:
        self.calls.append(kwargs)
        sym = kwargs["symbols"][0]
        return {"result": {sym: [{"d0": kwargs["start_date"], "d1": kwargs["end_date"],
                                  "s": "4242"}]}}


def buy_client(**timeseries: Any) -> SimpleNamespace:
    downloads: list[dict[str, Any]] = []
    return SimpleNamespace(metadata=ConditionMetadata(),
                           timeseries=FakeTimeseries(downloads, **timeseries),
                           batch=RecordingNamespace([]), symbology=FakeSymbology(),
                           downloads=downloads)


def quote_client(price: Any = e0_like_price) -> SimpleNamespace:
    hits: list[str] = []
    return SimpleNamespace(metadata=FakeMetadata(price=price), timeseries=RecordingNamespace(hits),
                           batch=RecordingNamespace(hits), billable_hits=hits)


def buy(tmp_path: Path, client: Any, items: list[ph.HistChunk], *, cap: float = 18.0,
        registry: Path | None = None) -> tuple[str, list[dict[str, str]]]:
    gate = ph.buy_gate(ph.PLAN_ES2011, config.ACCOUNT_2_ID, session_cap_usd=cap,
                       **gate_kwargs(tmp_path))
    return ph.run_hist_buy(client, gate, ph.ES2011, items, expected_harness_sha256=HARNESS,
                           account=config.ACCOUNT_2_ID,
                           registry_path=registry or registry_with(tmp_path, "C2"),
                           vendor_root=tmp_path / "v", reports_base=tmp_path / "reports",
                           rolls_dir=tmp_path / "rolls", condition_dir=tmp_path / "cond",
                           log=lambda m: None)


# ------------------------------------------------------------------ plans ----
def test_es2011_is_the_96_monthly_es_chunks_2011_05_to_2019_04() -> None:
    plan = ph.ES2011
    assert plan.roots == ("ES",) and len(plan.chunks) == 96
    assert plan.chunks[0] == ("2011-05-01", "2011-06-01")
    assert plan.chunks[-1] == ("2019-04-01", "2019-05-01")
    assert (str(plan.first_trade_date), str(plan.last_trade_date)) == ("2011-05-02",
                                                                       "2019-04-30")
    assert plan.test_ids == ("C2-T1", "C2-T2")
    assert len(ph.plan_chunks(plan)) == 96


def test_ext2010_is_the_june_2010_partial_chunk_then_106_months_per_root() -> None:
    plan = ph.EXT2010
    assert plan.roots == ("NG", "NQ", "ZN", "6E", "GC", "ZC") and len(plan.chunks) == 107
    assert plan.chunks[:2] == (("2010-06-06", "2010-07-01"), ("2010-07-01", "2010-08-01"))
    assert plan.chunks[-1] == ("2019-04-01", "2019-05-01")
    assert (str(plan.first_trade_date), str(plan.last_trade_date)) == ("2010-06-07",
                                                                       "2019-04-30")
    items = ph.plan_chunks(plan)
    assert len(items) == 642 and items[0].params.symbols == ("NG.v.0",)
    assert plan.test_ids == ("C1-T1", "C1-T2")


@pytest.mark.parametrize("plan,root,start,end,match", [
    ("es2011", "ES", "2019-05-01", "2019-06-01", "not one of"),
    ("es2011", "ES", "2011-04-01", "2011-05-01", "not one of"),
    ("es2011", "ES", "2011-05-02", "2011-06-01", "not one of"),
    ("es2011", "MES", "2011-05-01", "2011-06-01", "not a root"),
    ("es2011", "NQ", "2011-05-01", "2011-06-01", "not a root"),
    ("ext2010", "ES", "2011-05-01", "2011-06-01", "not a root"),
    ("ext2010", "NG", "2010-06-01", "2010-07-01", "not one of"),
    ("ext2010", "CL", "2010-07-01", "2010-08-01", "not a root"),
])
def test_any_chunk_or_root_outside_the_plan_is_refused(plan: str, root: str, start: str,
                                                       end: str, match: str) -> None:
    item = ph.HistChunk(plan, root, ph._params(root, start, end))
    with pytest.raises(ph.HistPlanError, match=match):
        ph.check_hist_chunk(item, ph.get_plan(plan))


def test_a_wrong_request_or_another_plans_chunk_or_type_is_refused() -> None:
    good = ph.plan_chunks(ph.ES2011)[0]
    wrong_schema = ph.HistChunk("es2011", "ES", ph.RequestParams(
        "GLBX.MDP3", ("ES.v.0",), "mbp-1", "continuous", "2011-05-01", "2011-06-01"))
    with pytest.raises(ph.HistPlanError, match="not a es2011 request"):
        ph.check_hist_chunk(wrong_schema, ph.ES2011)
    with pytest.raises(ph.HistPlanError, match="plan 'es2011', not 'ext2010'"):
        ph.check_hist_chunk(good, ph.EXT2010)
    step2 = ps.chunk_for("NQ", "2019-05-01", "2019-06-01")
    with pytest.raises(ph.HistPlanError, match="only a HistChunk"):
        ph.check_hist_chunk(step2, ph.EXT2010)
    with pytest.raises(ps.Step2QuoteOnlyChunk):
        ps.check_chunk(good)  # the step 2 buy path never takes a hist chunk
    with pytest.raises(ps.Step2RefusedRoot):
        ps.chunk_for("ES", "2019-05-01", "2019-06-01")  # nor ES


def test_no_hist_chunk_reaches_the_step2_window_or_a_holdout() -> None:
    for plan in ph.PLANS.values():
        assert all(e <= "2019-05-01" for _, e in plan.chunks)
        assert str(plan.data_end) == ps.STEP2_CHUNKS[0][0]


def test_manifests_and_metadata_paths_are_plan_specific(tmp_path: Path) -> None:
    assert ph.purchase_manifest_path("NG", "ext2010") == (
        config.REPO_ROOT / "reports" / "hist" / "purchase_NG_ext2010.json")
    assert ph.purchase_manifest_path("NG", "ext2010") != ps.manifest_path("NG")
    assert ph.symbology_cache_path("NG", ph.EXT2010).name == \
        "NG_v_0_2010-06-06_2019-05-01_symbology.json"
    assert ph.condition_path(ph.ES2011).name == "GLBX.MDP3_2011-05-01_2019-05-01.json"


def test_the_buy_gates_use_each_plans_session_and_caps() -> None:
    es = ph.buy_gate(ph.PLAN_ES2011)
    ext = ph.buy_gate(ph.PLAN_EXT2010)
    assert (es.session_id, es.session_cap_usd, es.request_cap_usd) == (E14, 0.0, 3.0)
    assert (ext.session_id, ext.session_cap_usd) == ("stage-E.14-ext2010", 0.0)
    assert es.account_id == ext.account_id == config.ACCOUNT_2_ID
    assert ph.quote_gate().session_id == E14


# ------------------------------------------------------------- quote-only ----
def test_quote_only_ledgers_zero_lines_under_e14_on_acct2_and_writes_the_summary(
        tmp_path: Path) -> None:
    # Arrange
    client = quote_client()
    out = tmp_path / "q" / "stage_e14_quotes.json"
    logs: list[str] = []

    # Act
    rc = ph.main(["--quote-only", "--plan", "es2011", "--quotes-out", str(out)],
                 key_loader=lambda account: FAKE_KEY,
                 quote_gate_factory=lambda account: ph.quote_gate(account,
                                                                  **gate_kwargs(tmp_path)),
                 buy_gate_factory=never("buy gate"), client_factory=lambda key: client,
                 log=logs.append)

    # Assert
    assert rc == 0 and client.billable_hits == []
    lines = read_entries(tmp_path / "ledger.jsonl")
    assert len(lines) == 96 and {(e["event"], e["session_id"], e["account"], e["usd"])
                                 for e in lines} == {("quote", E14, "acct-2", 0.0)}
    payload = json.loads(out.read_text(encoding="utf-8"))
    section = payload["sets"]["plan:es2011"]
    assert section["chunks"] == 96 and section["complete"] and section["per_root"]["ES"][
        "quoted"] == 96
    assert section["total_usd_x_1_03"] == pytest.approx(section["total_usd"] * 1.03)
    assert section["account"]["headroom_usd"] == pytest.approx(config.ACCOUNT_2_CAP_USD)
    assert out.with_suffix(".md").is_file()
    assert FAKE_KEY not in out.read_text(encoding="utf-8") + "".join(logs)


def test_quote_failures_leave_the_plan_incomplete_and_retry_quotes_only_the_failed(
        tmp_path: Path) -> None:
    # Arrange: every 2014 chunk fails once
    failed = {"on": True}

    def price(kwargs: dict[str, Any]) -> float:
        if failed["on"] and kwargs["start"].startswith("2014"):
            raise RuntimeError("unpriceable")
        return e0_like_price(kwargs)

    out = tmp_path / "quotes.json"
    args = ["--quote-only", "--plan", "es2011", "--quotes-out", str(out)]
    kw = {"key_loader": lambda account: FAKE_KEY, "log": lambda m: None,
          "quote_gate_factory": lambda account: ph.quote_gate(account, **gate_kwargs(tmp_path))}

    # Act
    first = ph.main(args, client_factory=lambda key: quote_client(price), **kw)
    failed["on"] = False
    second_client = quote_client(price)
    second = ph.main([*args, "--retry-failed"], client_factory=lambda key: second_client, **kw)

    # Assert
    assert (first, second) == (ph.RC_STOPPED, 0)
    assert len(second_client.metadata.calls) == 2 * 12  # cost and size for 12 months only
    assert json.loads(out.read_text(encoding="utf-8"))["sets"]["plan:es2011"]["complete"]


def test_quote_only_refuses_a_missing_or_e2b_quotes_path_and_a_harness_sha(tmp_path: Path) -> None:
    kw = {"key_loader": never("key loader"), "client_factory": never("client"),
          "log": lambda m: None}
    assert ph.main(["--quote-only", "--plan", "es2011"], **kw) == ph.RC_REFUSED
    assert ph.main(["--quote-only", "--plan", "es2011", "--quotes-out",
                    str(ps.QUOTES_JSON)], **kw) == ph.RC_REFUSED
    assert ph.main(["--quote-only", "--plan", "es2011", "--quotes-out", str(tmp_path / "q.json"),
                    "--harness-sha256", HARNESS], **kw) == ph.RC_REFUSED


# ------------------------------------------------------------- buy refusals ----
def _main_buy(tmp_path: Path, argv: list[str], *, cap: float | None = None,
              registry: Path | None = None) -> int:
    def factory(plan: str, account: str) -> Any:
        extra = {} if cap is None else {"session_cap_usd": cap}
        if account == config.ACCOUNT_1_ID:
            external = tmp_path / "external.jsonl"
            external.touch()
            extra["external_ledger_paths"] = (external,)
        return ph.buy_gate(plan, account, **gate_kwargs(tmp_path), **extra)

    return ph.main(argv, key_loader=never("key loader"), buy_gate_factory=factory,
                   quote_gate_factory=never("quote gate"), client_factory=never("client"),
                   registry_path=registry or registry_with(tmp_path, "C2"),
                   vendor_root=tmp_path / "v", reports_base=tmp_path / "reports",
                   log=lambda m: None)


BUY_ES = ["--buy", "--plan", "es2011", "--account", "acct-2", "--harness-sha256", HARNESS]


def test_the_es2011_buy_refuses_to_start_while_the_e14_cap_is_zero(
        tmp_path: Path, preflight_ok: list[str]) -> None:
    assert config.E14_SESSION_CAP_USD == 0.0
    assert _main_buy(tmp_path, BUY_ES) == ph.RC_REFUSED
    assert preflight_ok == [HARNESS]  # the preflight ran first


def test_the_ext2010_buy_stays_refused_at_a_zero_cap_and_without_c1s_registration(
        tmp_path: Path, preflight_ok: list[str]) -> None:
    argv = ["--buy", "--plan", "ext2010", "--account", "acct-2", "--harness-sha256", HARNESS]
    assert config.E14_EXT2010_SESSION_CAP_USD == 0.0
    assert _main_buy(tmp_path, argv) == ph.RC_REFUSED
    assert _main_buy(tmp_path, argv, cap=70.0, registry=registry_with(tmp_path / "a", "C2")) \
        == ph.RC_REFUSED


@pytest.mark.parametrize("argv", [
    ["--buy", "--plan", "es2011", "--account", "acct-1", "--harness-sha256", HARNESS],
    ["--buy", "--plan", "es2011", "--harness-sha256", HARNESS],
    ["--buy", "--plan", "es2011", "--account", "acct-2"],
    [*BUY_ES, "--quotes-out", "x.json"],
])
def test_a_buy_on_acct1_or_without_its_arguments_is_refused(
        tmp_path: Path, preflight_ok: list[str], argv: list[str]) -> None:
    assert _main_buy(tmp_path, argv, cap=18.0) == ph.RC_REFUSED


def test_the_buy_refuses_without_c2s_registration(tmp_path: Path,
                                                  preflight_ok: list[str]) -> None:
    empty = tmp_path / "r" / "registry.jsonl"
    tr.init_registry(empty)
    assert _main_buy(tmp_path, BUY_ES, cap=18.0, registry=empty) == ph.RC_REFUSED
    assert _main_buy(tmp_path, BUY_ES, cap=18.0,
                     registry=registry_with(tmp_path / "c1", "C1")) == ph.RC_REFUSED


def test_the_buy_refuses_a_session_cap_above_the_accounts_headroom(
        tmp_path: Path, preflight_ok: list[str]) -> None:
    assert _main_buy(tmp_path, BUY_ES, cap=config.ACCOUNT_2_CAP_USD + 0.01) == ph.RC_REFUSED


def test_the_buy_refuses_when_the_harness_preflight_raises(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def refuse(expected: str, root: Path | None = None) -> str:
        raise harness_freeze.HarnessFreezeError("tree differs")

    monkeypatch.setattr(harness_freeze, "preflight", refuse)
    assert _main_buy(tmp_path, BUY_ES, cap=18.0) == ph.RC_REFUSED


# ------------------------------------------------------------- buy flow ----
def test_the_buy_quotes_commits_downloads_settles_and_records_each_chunk(
        tmp_path: Path, preflight_ok: list[str]) -> None:
    # Arrange
    client = buy_client()
    items = ph.plan_chunks(ph.ES2011)

    # Act
    harness, done = buy(tmp_path, client, items)

    # Assert
    assert harness == HARNESS and len(done) == 96 and len(client.downloads) == 96
    lines = read_entries(tmp_path / "ledger.jsonl")
    assert {e["session_id"] for e in lines} == {E14} and {e["account"] for e in lines} == {
        "acct-2"}
    assert sum(e["event"] == "commit" for e in lines) == 96 == sum(
        e["event"] == "settle" for e in lines)
    manifest = json.loads((tmp_path / "reports" / "purchase_ES_es2011.json").read_text())
    assert manifest["plan"] == "es2011" and manifest["product"] == "ES"
    assert len(manifest["files"]) == 96 and manifest["harness_sha256"] == HARNESS
    assert all(f["billed_over_quote_ratio"] == 1.0 for f in manifest["files"])
    assert not (tmp_path / "reports" / "purchase_ES.json").exists()
    assert ph.symbology_cache_path("ES", ph.ES2011, tmp_path / "rolls").is_file()
    assert ph.condition_path(ph.ES2011, tmp_path / "cond").is_file()
    assert client.symbology.calls[0]["start_date"] == "2011-05-01"


def test_a_resumed_buy_skips_settled_chunks_without_quoting_them(
        tmp_path: Path, preflight_ok: list[str]) -> None:
    items = ph.plan_chunks(ph.ES2011)[:3]
    registry = registry_with(tmp_path, "C2")
    buy(tmp_path, buy_client(), items, registry=registry)
    again = buy_client()
    _, done = buy(tmp_path, again, items, registry=registry)
    assert again.downloads == [] and again.metadata.calls == []
    assert {d["action"] for d in done} == {"skipped: already bought and settled"}


def test_a_foreign_file_at_a_target_is_refused_before_any_vendor_call(
        tmp_path: Path, preflight_ok: list[str]) -> None:
    items = ph.plan_chunks(ph.ES2011)[:3]
    target = ph.target_path(items[2].params, tmp_path / "v")
    target.parent.mkdir(parents=True)
    target.write_bytes(b"not ours")
    client = buy_client()
    with pytest.raises(ph.ResumeStateError, match="without a settled"):
        buy(tmp_path, client, items)
    assert client.downloads == [] and client.metadata.calls == []


def test_an_owned_raw_file_overlapping_a_chunk_is_refused_before_any_vendor_call(
        tmp_path: Path, preflight_ok: list[str]) -> None:
    items = ph.plan_chunks(ph.ES2011)[:3]
    other = ph.target_path(items[0].params, tmp_path / "v").with_name(
        "range=2011-05-15_2011-06-15.dbn.zst")
    other.parent.mkdir(parents=True)
    other.write_bytes(b"owned")
    client = buy_client()
    with pytest.raises(ph.ResumeStateError, match="overlaps"):
        buy(tmp_path, client, items)
    assert client.downloads == [] and client.metadata.calls == []


def test_billed_above_its_quote_by_more_than_3pct_stops_before_the_next_chunk(
        tmp_path: Path, preflight_ok: list[str]) -> None:
    # Arrange: about 720 records quoted per chunk; 100 extra = about 14% above the quote
    client = buy_client(extra_records=100)
    items = ph.plan_chunks(ph.ES2011)[:3]

    # Act
    with pytest.raises(ph.DeliveryCheckError, match="MORE THAN 3%"):
        buy(tmp_path, client, items)

    # Assert
    assert len(client.downloads) == 1
    manifest = json.loads((tmp_path / "reports" / "purchase_ES_es2011.json").read_text())
    (row,) = manifest["files"]
    assert row["billed_above_quote"] and row["billed_over_quote_ratio"] > 1.03
    settle = [e for e in read_entries(tmp_path / "ledger.jsonl") if e["event"] == "settle"]
    assert len(settle) == 1 and settle[0]["actual_usd"] > settle[0]["quoted_usd"]


def test_billed_above_its_quote_by_at_most_3pct_is_recorded_and_the_run_continues(
        tmp_path: Path, preflight_ok: list[str]) -> None:
    client = buy_client(extra_records=2)  # about 0.3% above
    items = ph.plan_chunks(ph.ES2011)[:3]
    _, done = buy(tmp_path, client, items)
    assert len(client.downloads) == 3 and all("above the quote" in d["action"] for d in done)
    manifest = json.loads((tmp_path / "reports" / "purchase_ES_es2011.json").read_text())
    assert all(1.0 < f["billed_over_quote_ratio"] <= 1.03 for f in manifest["files"])


def test_a_failed_metadata_fetch_is_named_and_a_rerun_fetches_it(
        tmp_path: Path, preflight_ok: list[str]) -> None:
    # Arrange
    items = ph.plan_chunks(ph.ES2011)[:2]
    registry = registry_with(tmp_path, "C2")
    client = buy_client()

    def down(**kwargs: Any) -> Any:
        raise RuntimeError("symbology unavailable")

    client.symbology.resolve = down

    # Act / Assert
    with pytest.raises(ph.HistPlanError, match="metadata fetch failed"):
        buy(tmp_path, client, items, registry=registry)
    again = buy_client()
    buy(tmp_path, again, items, registry=registry)
    assert again.downloads == [] and len(again.symbology.calls) == 2  # two resolve calls
    assert ph.symbology_cache_path("ES", ph.ES2011, tmp_path / "rolls").is_file()


def test_a_manifest_of_another_plan_or_root_is_refused(tmp_path: Path,
                                                       preflight_ok: list[str]) -> None:
    path = tmp_path / "reports" / "purchase_ES_es2011.json"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps({"product": "ES", "plan": "ext2010", "files": []}))
    with pytest.raises(ph.HistPlanError, match="not ES es2011"):
        buy(tmp_path, buy_client(), ph.plan_chunks(ph.ES2011)[:1])


# ------------------------------------------------------- pull_step2 --plan ----
def test_pull_step2_hands_a_plan_run_to_pull_hist(monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange
    seen: list[tuple[list[str], dict[str, Any]]] = []
    monkeypatch.setattr(ph, "main", lambda argv, **kw: seen.append((argv, kw)) or 0)
    argv = ["--quote-only", "--plan", "es2011", "--quotes-out", "x.json"]

    # Act
    rc = ps.main(argv, key_loader=never("key"), gate_factory=never("step 2 gate"),
                 client_factory=never("client"), log=lambda m: None)

    # Assert
    assert rc == 0 and seen[0][0] == argv
    assert set(seen[0][1]) == {"key_loader", "client_factory", "log"}


@pytest.mark.parametrize("extra", [["--roots", "NG"], ["--set", "ml-v2"], ["--training-window"],
                                   ["--extension-2010"], ["--holdout2-only"]])
def test_pull_step2_refuses_step2_options_with_a_plan(monkeypatch: pytest.MonkeyPatch,
                                                      extra: list[str]) -> None:
    monkeypatch.setattr(ph, "main", never("pull_hist.main"))
    rc = ps.main(["--quote-only", "--plan", "ext2010", *extra], key_loader=never("key"),
                 gate_factory=never("gate"), client_factory=never("client"), log=lambda m: None)
    assert rc == ps.RC_REFUSED
