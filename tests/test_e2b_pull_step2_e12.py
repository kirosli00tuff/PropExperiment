"""Harness v8 (Stage E.12 Task 4): data/pull_step2.py's --account, --roots, --training-window and
its interlock, the quote-only --holdout2-only and --extension-2010 plans, set ml-v2 and
--quotes-out.

Fake clients only: no network and no key (key loaders return an obviously fake value, which is
checked never to reach any output). Every ledger, acct-1 external ledger, ACCESS doc, vendor root,
report and quotes file lives under tmp_path; runs driven through main() check the real ledger
and holdout manifests untouched. The training-window interlock is tested with the config's value.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from data import config
from data import pull_step2 as ps
from data.spend_gate import UnknownAccountError, read_entries
from screening import harness_freeze
from tests.test_e2b_pull_step2 import HARNESS, buy_client, quote_client, real_state, set_caps
from tests.test_pull_universe import (
    FakeMetadata,
    FakeTimeseries,
    RecordingNamespace,
    e0_like_price,
)

FAKE_KEY = "fake-v8-key-not-real"
E12 = "stage-E.12-2026-10-03"


# ------------------------------------------------------------- helpers ----
@pytest.fixture
def preflight_ok(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    seen: list[str] = []

    def fake(expected: str, root: Path = config.REPO_ROOT) -> str:
        seen.append(expected)
        return expected

    monkeypatch.setattr(harness_freeze, "preflight", fake)
    return seen


def factory_for(tmp_path: Path, seen: list[str] | None = None, **caps: float
                ) -> Callable[..., Any]:
    """main()'s gate_factory: the step 2 gate on ``account`` with a tmp ledger; acct-1's
    external ledger is an empty tmp file. ``seen`` records each account asked for."""
    external = tmp_path / "external_ledger.jsonl"
    external.touch()

    def factory(account: str) -> Any:
        if seen is not None:
            seen.append(account)
        extra = {"external_ledger_paths": (external,)} if account == config.ACCOUNT_1_ID else {}
        return ps.step2_gate(account=account, ledger_path=tmp_path / "ledger.jsonl",
                             access_doc_path=tmp_path / "A.md", **extra, **caps)
    return factory


def never(what: str) -> Callable[..., Any]:
    def fail(*args: Any, **kwargs: Any) -> Any:
        pytest.fail(f"{what} was called")
    return fail


def chunk(root: str, start: str) -> ps.Chunk:
    s, e = next(c for c in ps.STEP2_CHUNKS if c[0] == start)
    return ps.chunk_for(root, s, e)


# ------------------------------------------------------ the 28 price paths ----
def test_the_v2_price_paths_are_the_ml_route_minus_rb_ho_si() -> None:
    # Act
    expected = tuple(r for r in ps.ML_ROUTE_ROOTS if r not in ("RB", "HO", "SI"))

    # Assert
    assert expected == ps.ML_V2_PRICE_PATHS and len(expected) == 28
    assert ps.quote_groups(ps.SET_ML_V2) == {
        "K1": ("NQ", "RTY", "YM"), "K2": ("ZT", "ZF", "ZN", "TN", "ZB", "UB"),
        "K3": ("6E", "6A", "6B", "6C", "6J", "6S", "6N"), "K4": ("CL", "NG"),
        "K5": ("GC", "HG"), "K6": ("ZC", "ZW", "ZS", "ZM", "ZL", "HE", "LE"), "K7": ("MBT",)}


def test_the_v2_price_paths_match_the_v2_universe_values() -> None:
    # Arrange: the harness never imports ml_route_v2; this test ties the literal to it.
    from ml_route_v2.constants import UNIVERSE

    # Act
    price_paths = tuple(path for _, path in UNIVERSE.values())

    # Assert
    assert set(price_paths) == set(ps.ML_V2_PRICE_PATHS) and len(price_paths) == 28


# --------------------------------------------------------------- --roots ----
def test_roots_parse_to_distinct_price_paths_in_order() -> None:
    assert ps.parse_roots("ZN,MBT") == ("ZN", "MBT")
    assert ps.parse_roots(" ZB , 6E ") == ("ZB", "6E")
    assert ps.parse_roots(",".join(ps.ML_V2_PRICE_PATHS)) == ps.ML_V2_PRICE_PATHS
    assert ps.groups_by_cluster(["ZN", "MBT", "NQ", "ZB"]) == {
        "K1": ("NQ",), "K2": ("ZN", "ZB"), "K7": ("MBT",)}


@pytest.mark.parametrize("text,match", [
    ("", "comma-separated"), ("ZN,", "comma-separated"), ("ZN,,ZB", "comma-separated"),
    ("ZN,ZN", "distinct"), ("RB", "28 v2 price paths"), ("SI", "28 v2 price paths"),
    ("MNQ", "28 v2 price paths"), ("MES", "28 v2 price paths"), ("zn", "28 v2 price paths")])
def test_roots_outside_the_price_paths_or_repeated_or_empty_are_refused(
        text: str, match: str) -> None:
    with pytest.raises(ps.Step2RefusedRoot, match=match):
        ps.parse_roots(text)


@pytest.mark.parametrize("mode", [
    ["--quote-only"], ["--buy", "--account", "acct-2", "--training-window",
                       "--harness-sha256", HARNESS]])
def test_main_refuses_bad_roots_before_any_vendor_call(
        tmp_path: Path, preflight_ok: list[str], mode: list[str]) -> None:
    # Act
    rc = ps.main([*mode, "--roots", "ZN,RB"], key_loader=never("key loader"),
                 gate_factory=never("gate factory"), client_factory=never("client factory"),
                 quotes_json=tmp_path / "q.json", log=lambda m: None)

    # Assert
    assert rc == ps.RC_REFUSED and preflight_ok == []
    assert not (tmp_path / "ledger.jsonl").exists()


# -------------------------------------------------------- --training-window ----
def test_the_training_window_plan_ends_with_2024_02_for_an_ordinary_root() -> None:
    # Act
    plan = ps.plan_step2(["ZN"], training_window=True)

    # Assert: the 58 unsealed chunks 2019-05..2024-02, none sealing
    assert len(plan) == 58 and not any(c.sealing for c in plan)
    assert (plan[0].params.start, plan[0].params.end) == ("2019-05-01", "2019-06-01")
    assert (plan[-1].params.start, plan[-1].params.end) == ps.LAST_TRAINING_CHUNK == (
        "2024-02-01", "2024-03-01")
    assert ps.training_window_chunks("ZN") == ps.unsealed_chunks("ZN")


def test_the_training_window_plan_for_mbt_runs_from_2021_04_to_2024_02() -> None:
    # Act
    plan = ps.plan_step2(["MBT"], training_window=True)

    # Assert: MBT from its first priced month (OC-R), 35 months
    assert len(plan) == 35
    assert plan[0].params.start == "2021-04-01" == ps.first_priced_month("MBT")
    assert (plan[-1].params.start, plan[-1].params.end) == ("2024-02-01", "2024-03-01")


@pytest.mark.parametrize("sealed", sorted(ps.SEALED_CHUNKS))
def test_the_training_window_refuses_every_chunk_from_2024_03_by_name(
        sealed: tuple[str, str]) -> None:
    # Arrange
    late = ps.chunk_for("ZN", *sealed)
    ps.check_chunk(late)  # a valid step 2 (sealing) chunk without the option

    # Act / Assert
    with pytest.raises(ps.Step2AfterTrainingWindow, match=f"range={sealed[0]}_{sealed[1]}"):
        ps.check_chunk(late, training_window=True)
    assert issubclass(ps.Step2AfterTrainingWindow, ps.Step2ChunkError)


def test_run_buy_under_the_training_window_refuses_a_2024_03_chunk_before_any_vendor_call(
        tmp_path: Path, preflight_ok: list[str]) -> None:
    # Arrange: a positive-cap gate on acct-2 and a plan whose second chunk is 2024-03
    client = buy_client()
    g = ps.step2_gate(ledger_path=tmp_path / "ledger.jsonl", access_doc_path=tmp_path / "A.md",
                      session_cap_usd=50.0, request_cap_usd=3.0)
    plan = [chunk("ZN", "2024-02-01"), chunk("ZN", "2024-03-01")]

    # Act / Assert
    with pytest.raises(ps.Step2AfterTrainingWindow, match="range=2024-03-01_2024-04-01"):
        ps.run_buy(client, g, plan, expected_harness_sha256=HARNESS, vendor_root=tmp_path / "v",
                   reports_base=tmp_path / "r", log=lambda m: None, account="acct-2",
                   training_window=True)
    assert preflight_ok == [HARNESS]
    assert client.metadata.calls == [] and client.downloads == []
    assert read_entries(tmp_path / "ledger.jsonl") == []


def test_quote_only_under_the_training_window_refuses_a_2024_03_chunk(tmp_path: Path) -> None:
    client = quote_client()
    g = ps.step2_gate(ledger_path=tmp_path / "ledger.jsonl", access_doc_path=tmp_path / "A.md")
    with pytest.raises(ps.Step2AfterTrainingWindow):
        ps.run_quote_only(client, g, [chunk("ZN", "2024-03-01")], log=lambda m: None,
                          training_window=True)
    assert client.metadata.calls == [] and read_entries(tmp_path / "ledger.jsonl") == []


# ------------------------------------------------------------ the interlock ----
def test_the_interlock_is_on_and_main_refuses_a_buy_without_the_training_window(
        tmp_path: Path, preflight_ok: list[str], capsys: pytest.CaptureFixture[str]) -> None:
    # Arrange: the config's value, not a patched one
    assert config.STEP2_TRAINING_WINDOW_ONLY is True is ps.STEP2_TRAINING_WINDOW_ONLY

    # Act
    rc = ps.main(["--buy", "--account", "acct-1", "--roots", "ZN", "--harness-sha256", HARNESS],
                 key_loader=never("key loader"), gate_factory=never("gate factory"),
                 client_factory=never("client factory"), log=lambda m: None)

    # Assert: refused before the gate, the preflight, the key and the client
    assert rc == ps.RC_REFUSED and preflight_ok == []
    assert "Step2TrainingWindowRequired" in capsys.readouterr().err


def test_run_buy_without_the_training_window_is_refused_while_the_interlock_is_on(
        tmp_path: Path, preflight_ok: list[str]) -> None:
    client = buy_client()
    g = ps.step2_gate(ledger_path=tmp_path / "ledger.jsonl", access_doc_path=tmp_path / "A.md",
                      session_cap_usd=50.0, request_cap_usd=3.0)
    with pytest.raises(ps.Step2TrainingWindowRequired, match="--training-window"):
        ps.run_buy(client, g, [chunk("ZN", "2019-05-01")], expected_harness_sha256=HARNESS,
                   vendor_root=tmp_path / "v", reports_base=tmp_path / "r", log=lambda m: None)
    assert client.metadata.calls == [] and client.downloads == []
    assert read_entries(tmp_path / "ledger.jsonl") == []


def test_the_interlock_reads_the_flag_so_a_later_phase_can_turn_it_off(
        monkeypatch: pytest.MonkeyPatch) -> None:
    ps.require_training_window(True)
    monkeypatch.setattr(ps, "STEP2_TRAINING_WINDOW_ONLY", False)
    ps.require_training_window(False)  # no refusal once the config flag is off


# --------------------------------------------------------------- --account ----
def test_buy_requires_an_account(tmp_path: Path, preflight_ok: list[str],
                                 capsys: pytest.CaptureFixture[str]) -> None:
    rc = ps.main(["--buy", "--roots", "ZN", "--training-window", "--harness-sha256", HARNESS],
                 key_loader=never("key loader"), gate_factory=never("gate factory"),
                 client_factory=never("client factory"), log=lambda m: None)
    assert rc == ps.RC_REFUSED and preflight_ok == []
    assert "--buy requires --account" in capsys.readouterr().err


def test_an_unregistered_account_is_refused_by_the_parser() -> None:
    with pytest.raises(SystemExit):
        ps.main(["--quote-only", "--set", "ml-v2", "--account", "acct-9"],
                key_loader=never("key loader"), gate_factory=never("gate factory"))


def test_require_buy_caps_accepts_any_registered_account_passed_explicitly(
        tmp_path: Path) -> None:
    # Arrange: positive caps on an acct-1 gate (its external ledger a tmp file)
    g = factory_for(tmp_path, session_cap_usd=5.0, request_cap_usd=3.0)(account="acct-1")

    # Act / Assert
    ps.require_buy_caps(g, "acct-1")
    with pytest.raises(UnknownAccountError, match="is not acct-2"):
        ps.require_buy_caps(g)  # no account named: ACTIVE_ACCOUNT, as before v8
    with pytest.raises(UnknownAccountError, match="is not acct-2"):
        ps.require_buy_caps(g, "acct-2")
    with pytest.raises(UnknownAccountError):
        ps.require_buy_caps(g, "acct-9")


def test_a_gate_factory_that_returns_another_accounts_gate_is_refused(tmp_path: Path) -> None:
    acct2 = factory_for(tmp_path)
    rc = ps.main(["--quote-only", "--set", "ml-v2", "--account", "acct-1"],
                 key_loader=never("key loader"), gate_factory=lambda account: acct2("acct-2"),
                 client_factory=never("client factory"), quotes_json=tmp_path / "q.json",
                 log=lambda m: None)
    assert rc == ps.RC_REFUSED


def test_buy_on_acct1_builds_the_gate_and_loads_the_key_of_acct1(
        tmp_path: Path, preflight_ok: list[str], monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str]) -> None:
    # Arrange: positive caps; the second chunk quotes above the $3.00 request cap, so the run
    # buys exactly one chunk (2019-05) and stops at the gate.
    before = real_state()
    set_caps(monkeypatch, 10.0, 3.0)
    seen: list[str] = []
    keys: list[dict[str, Any]] = []
    built: list[str] = []
    logged: list[str] = []
    downloads: list[dict[str, Any]] = []

    def price(kw: dict[str, Any]) -> float:
        return e0_like_price(kw) if kw["start"] == "2019-05-01" else 5.0

    client = SimpleNamespace(metadata=FakeMetadata(price=price),
                             timeseries=FakeTimeseries(downloads),
                             batch=RecordingNamespace([]), downloads=downloads)

    # Act
    rc = ps.main(["--buy", "--account", "acct-1", "--roots", "ZN", "--training-window",
                  "--harness-sha256", HARNESS],
                 key_loader=lambda **kw: keys.append(kw) or FAKE_KEY,
                 gate_factory=factory_for(tmp_path, seen),
                 client_factory=lambda key: built.append(key) or client,
                 vendor_root=tmp_path / "v", reports_base=tmp_path / "r", log=logged.append)

    # Assert
    assert rc == ps.RC_STOPPED and preflight_ok == [HARNESS, HARNESS]
    assert seen == ["acct-1"] and keys == [{"account": "acct-1"}] and built == [FAKE_KEY]
    assert [d["start"] for d in downloads] == ["2019-05-01"]
    entries = read_entries(tmp_path / "ledger.jsonl")
    assert {(e["account"], e["session_id"]) for e in entries} == {("acct-1", E12)}
    assert [e["event"] for e in entries] == ["quote", "commit", "settle", "quote", "refused"]
    assert "account acct-1" in logged[0]
    out = capsys.readouterr()
    assert FAKE_KEY not in "\n".join(logged) + out.out + out.err
    assert real_state() == before


def test_main_hands_run_buy_the_account_and_the_training_window_plan(
        tmp_path: Path, preflight_ok: list[str], monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange
    set_caps(monkeypatch, 10.0, 3.0)
    calls: list[dict[str, Any]] = []

    def fake_run_buy(client: Any, gate: Any, plan: list[ps.Chunk], **kw: Any) -> tuple:
        calls.append({"gate": gate.account_id, "plan": plan, **kw})
        return HARNESS, []

    monkeypatch.setattr(ps, "run_buy", fake_run_buy)

    # Act
    rc = ps.main(["--buy", "--account", "acct-2", "--roots", "ZN,MBT", "--training-window",
                  "--harness-sha256", HARNESS], key_loader=lambda **kw: FAKE_KEY,
                 gate_factory=factory_for(tmp_path), client_factory=lambda key: object(),
                 log=lambda m: None)

    # Assert
    assert rc == 0 and len(calls) == 1
    call = calls[0]
    assert (call["gate"], call["account"], call["training_window"]) == ("acct-2", "acct-2", True)
    assert len(call["plan"]) == 58 + 35
    assert max(c.params.start for c in call["plan"]) == "2024-02-01"
    assert not any(c.sealing for c in call["plan"])


# ------------------------------------------------------- quote-only plans ----
def test_the_holdout2_only_plan_is_13_sealed_chunks_per_root_and_a_separate_type() -> None:
    # Act
    plan, skipped = ps.plan_quote_only(["ZN", "MBT"], ps.PLAN_HOLDOUT2_ONLY)

    # Assert
    assert skipped == [] and len(plan) == 26
    assert all(type(q) is ps.QuoteOnlyChunk and q.sealing for q in plan)
    assert [(q.params.start, q.params.end) for q in plan[:13]] == sorted(ps.SEALED_CHUNKS)
    with pytest.raises(ps.Step2QuoteOnlyChunk):
        ps.check_chunk(plan[0])
    with pytest.raises(ps.Step2QuoteOnlyChunk):
        ps.validate_plan(plan, training_window=True)


def test_the_extension_plan_is_2010_01_to_2019_04_per_root_with_mbt_skipped_by_name() -> None:
    # Act
    plan, skipped = ps.plan_quote_only(["ZN", "MBT", "NQ"], ps.PLAN_EXTENSION_2010)

    # Assert
    assert skipped == ["MBT"] and len(plan) == 2 * 112
    zn = [q for q in plan if q.root == "ZN"]
    assert (zn[0].params.start, zn[0].params.end) == ("2010-01-01", "2010-02-01")
    assert (zn[-1].params.start, zn[-1].params.end) == ("2019-04-01", "2019-05-01")
    assert not any(q.sealing for q in plan)
    with pytest.raises(ps.Step2QuoteOnlyChunk):
        ps.check_chunk(plan[0])
    with pytest.raises(ps.Step2Error, match="nothing to quote"):
        ps.plan_quote_only(["MBT"], ps.PLAN_EXTENSION_2010)


def test_a_quote_only_item_outside_its_plan_is_refused() -> None:
    params = ps.chunk_for("ZN", "2019-05-01", "2019-06-01").params
    for kind in (ps.PLAN_HOLDOUT2_ONLY, ps.PLAN_EXTENSION_2010, "other"):
        with pytest.raises(ps.Step2QuoteOnlyChunk):
            ps.check_quote_only_chunk(ps.QuoteOnlyChunk("ZN", params, kind))


@pytest.mark.parametrize("kind", ["holdout2-only", "extension-2010"])
def test_run_buy_never_accepts_a_quote_only_plan(
        tmp_path: Path, preflight_ok: list[str], kind: str) -> None:
    # Arrange: past the caps and the interlock, so the plan check is what refuses
    plan, _ = ps.plan_quote_only(["ZN"], kind)
    client = buy_client()
    g = ps.step2_gate(ledger_path=tmp_path / "ledger.jsonl", access_doc_path=tmp_path / "A.md",
                      session_cap_usd=50.0, request_cap_usd=3.0)

    # Act / Assert
    with pytest.raises(ps.Step2QuoteOnlyChunk):
        ps.run_buy(client, g, plan, expected_harness_sha256=HARNESS, vendor_root=tmp_path / "v",
                   reports_base=tmp_path / "r", log=lambda m: None, account="acct-2",
                   training_window=True)
    assert client.metadata.calls == [] and client.downloads == []
    assert read_entries(tmp_path / "ledger.jsonl") == []


@pytest.mark.parametrize("option", ["--holdout2-only", "--extension-2010"])
def test_main_refuses_the_quote_only_plans_for_buy(
        tmp_path: Path, preflight_ok: list[str], option: str,
        capsys: pytest.CaptureFixture[str]) -> None:
    rc = ps.main(["--buy", "--account", "acct-2", "--roots", "ZN", option,
                  "--harness-sha256", HARNESS],
                 key_loader=never("key loader"), gate_factory=never("gate factory"),
                 client_factory=never("client factory"), log=lambda m: None)
    assert rc == ps.RC_REFUSED and preflight_ok == []
    assert "never bought" in capsys.readouterr().err


def test_holdout2_only_quotes_reach_only_gate_quote_and_report_both_accounts(
        tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    # Arrange: acct-2 already spent $124.67 in this ledger, acct-1 $9.47 here + $82.12 external
    before = real_state()
    ledger = tmp_path / "ledger.jsonl"
    ledger.write_text("".join(json.dumps(e) + "\n" for e in (
        {"session_id": "old", "event": "commit", "usd": 124.67, "account": "acct-2"},
        {"session_id": "old", "event": "commit", "usd": 9.47, "account": "acct-1"})),
        encoding="utf-8")
    factory = factory_for(tmp_path)
    (tmp_path / "external_ledger.jsonl").write_text(
        json.dumps({"usd": 82.12}) + "\n", encoding="utf-8")
    client = quote_client()
    out = tmp_path / "e12" / "quotes.json"
    keys: list[dict[str, Any]] = []

    # Act
    rc = ps.main(["--quote-only", "--set", "ml-v2", "--holdout2-only", "--quotes-out", str(out)],
                 key_loader=lambda **kw: keys.append(kw) or FAKE_KEY, gate_factory=factory,
                 client_factory=lambda key: client, quotes_json=tmp_path / "unused.json",
                 log=lambda m: None)

    # Assert: free metadata only, $0.00 quote lines on acct-2 (the default) under E.12
    assert rc == 0 and client.billable_hits == [] and keys == [{"account": "acct-2"}]
    with pytest.raises(RuntimeError, match="forbidden"):
        client.timeseries.get_range(dataset="GLBX.MDP3")
    new = read_entries(ledger)[2:]
    assert len(new) == 28 * 13
    assert {(e["event"], e["usd"], e["account"], e["session_id"]) for e in new} == {
        ("quote", 0.0, "acct-2", E12)}
    assert all(e["request"]["start"] >= "2024-03-01" for e in new)
    payload = json.loads(out.read_text(encoding="utf-8"))
    section = payload["sets"]["ml-v2+holdout2-only"]
    assert (section["contracts"], section["chunks"], section["complete"]) == (28, 364, True)
    assert section["total_usd"] == pytest.approx(sum(
        r["usd_sealed_2024_03_2025_03"] for r in section["per_contract"].values()))
    positions = payload["accounts"]["positions"]
    assert set(positions) == {"acct-1", "acct-2"}
    assert positions["acct-2"]["spent_usd"] == pytest.approx(124.67)
    assert positions["acct-2"]["account_cap_usd"] == config.ACCOUNT_2_CAP_USD
    assert positions["acct-2"]["cap_headroom_usd"] == pytest.approx(
        config.ACCOUNT_2_CAP_USD - 124.67)
    assert positions["acct-1"]["spent_usd"] == pytest.approx(9.47 + 82.12)
    assert positions["acct-1"]["cap_headroom_usd"] == pytest.approx(120.00 - 9.47 - 82.12)
    assert payload["accounts"]["combined_headroom_usd"] == pytest.approx(
        positions["acct-1"]["cap_headroom_usd"] + positions["acct-2"]["cap_headroom_usd"])
    md = out.with_suffix(".md").read_text(encoding="utf-8")
    assert md.startswith(f"# Step 2 quotes, session {E12}")
    assert "## ml-v2+holdout2-only" in md and "| acct-1 |" in md and "| acct-2 |" in md
    assert not (tmp_path / "unused.json").exists()
    captured = capsys.readouterr()
    assert FAKE_KEY not in captured.out + captured.err + md + out.read_text(encoding="utf-8")
    assert real_state() == before


def test_extension_quotes_skip_mbt_and_an_unpriceable_root_fails_its_quotes(
        tmp_path: Path) -> None:
    # Arrange: NQ has no 2010-2019 history at the (fake) vendor; ZN prices every month.
    def price(kw: dict[str, Any]) -> float:
        if kw["symbols"] == ["NQ.v.0"]:
            raise ValueError("422 symbology_invalid_request: None of the symbols could be "
                             "resolved")
        return e0_like_price(kw)

    client = quote_client(price)
    out = tmp_path / "x.json"

    # Act
    rc = ps.main(["--quote-only", "--roots", "ZN,MBT,NQ", "--extension-2010", "--account",
                  "acct-1", "--quotes-out", str(out)], key_loader=lambda **kw: FAKE_KEY,
                 gate_factory=factory_for(tmp_path), client_factory=lambda key: client,
                 log=lambda m: None)

    # Assert: incomplete (NQ failed), MBT never requested, nothing billable
    assert rc == ps.RC_STOPPED and client.billable_hits == []
    with pytest.raises(RuntimeError, match="forbidden"):
        client.timeseries.get_range(dataset="GLBX.MDP3")
    entries = read_entries(tmp_path / "ledger.jsonl")
    assert len(entries) == 2 * 112
    assert {(e["account"], e["session_id"]) for e in entries} == {("acct-1", E12)}
    assert not any(e["request"]["symbols"] == ["MBT.v.0"] for e in entries)
    payload = json.loads(out.read_text(encoding="utf-8"))
    section = payload["sets"]["roots:ZN,MBT,NQ+extension-2010"]
    assert section["skipped_roots"] == {"MBT": ps.EXTENSION_2010_SKIPPED["MBT"]}
    assert len(section["per_contract"]["NQ"]["failed"]) == 112 and not section["complete"]
    zn = section["per_contract"]["ZN"]
    assert zn["usd"] == pytest.approx(zn["usd_extension_2010_01_2019_04"]) and zn["usd"] > 0
    assert zn["usd_unsealed_2019_05_2024_02"] == 0.0
    assert payload["account"]["account"] == "acct-1"


def test_set_ml_v2_with_the_training_window_quotes_through_2024_02_only(tmp_path: Path) -> None:
    client = quote_client()
    out = tmp_path / "q.json"
    rc = ps.main(["--quote-only", "--set", "ml-v2", "--training-window"],
                 key_loader=lambda **kw: FAKE_KEY, gate_factory=factory_for(tmp_path),
                 client_factory=lambda key: client, quotes_json=out, log=lambda m: None)
    entries = read_entries(tmp_path / "ledger.jsonl")
    assert rc == 0 and len(entries) == 27 * 58 + 35
    assert max(e["request"]["start"] for e in entries) == "2024-02-01"
    section = json.loads(out.read_text(encoding="utf-8"))["sets"]["ml-v2+training-window"]
    assert section["chunks"] == 27 * 58 + 35 and section["complete"]
    assert all(r["usd_sealed_2024_03_2025_03"] == 0.0 for r in section["per_contract"].values())


# ------------------------------------------------------------ --quotes-out ----
def test_the_quotes_default_is_the_e12_file_and_the_md_goes_beside_it(tmp_path: Path) -> None:
    # Assert: the CLI default
    assert ps.QUOTES_OUT_DEFAULT == config.REPO_ROOT / "reports" / "stage_e12_quotes.json"
    assert ps.quote_paths(None, ps.QUOTES_OUT_DEFAULT) == (
        ps.QUOTES_OUT_DEFAULT, config.REPO_ROOT / "reports" / "stage_e12_quotes.md")
    assert ps.quote_paths(str(tmp_path / "a.json"), ps.QUOTES_OUT_DEFAULT) == (
        tmp_path / "a.json", tmp_path / "a.md")


@pytest.mark.parametrize("target", [ps.QUOTES_JSON, ps.QUOTES_JSON.with_suffix(".md")])
def test_e2b_quote_files_are_never_a_target(tmp_path: Path, target: Path) -> None:
    # Arrange
    before = {p: p.stat().st_mtime_ns for p in (ps.QUOTES_JSON, ps.QUOTES_MD) if p.exists()}

    # Act / Assert: as --quotes-out, and as main's quotes path
    with pytest.raises(ps.Step2Error, match="never overwritten|must name a .json"):
        ps.quote_paths(str(target), ps.QUOTES_OUT_DEFAULT)
    rc = ps.main(["--quote-only", "--set", "ml-v2", "--quotes-out", str(ps.QUOTES_JSON)],
                 key_loader=never("key loader"), gate_factory=never("gate factory"),
                 client_factory=never("client factory"), log=lambda m: None)
    assert rc == ps.RC_REFUSED
    with pytest.raises(ps.Step2Error, match="never overwritten"):
        ps.quote_paths(None, ps.QUOTES_JSON)
    with pytest.raises(ps.Step2Error, match="never overwritten"):
        ps.quote_paths(None, tmp_path / "q.json", ps.QUOTES_MD)
    after = {p: p.stat().st_mtime_ns for p in (ps.QUOTES_JSON, ps.QUOTES_MD) if p.exists()}
    assert after == before


def test_quotes_out_must_be_a_json_file_and_is_for_quote_only(
        tmp_path: Path, preflight_ok: list[str]) -> None:
    with pytest.raises(ps.Step2Error, match="must name a .json"):
        ps.quote_paths(str(tmp_path / "q.md"), ps.QUOTES_OUT_DEFAULT)
    rc = ps.main(["--buy", "--account", "acct-2", "--roots", "ZN", "--training-window",
                  "--quotes-out", str(tmp_path / "q.json"), "--harness-sha256", HARNESS],
                 key_loader=never("key loader"), gate_factory=never("gate factory"),
                 client_factory=never("client factory"), log=lambda m: None)
    assert rc == ps.RC_REFUSED and preflight_ok == []
