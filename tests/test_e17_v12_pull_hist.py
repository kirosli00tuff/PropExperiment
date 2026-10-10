"""Harness v12 (Stage E.17): data.pull_hist plan "ext2010h" (reports/stage_e16_handoff.md step 8)
and the --roots option (E.17 amendment A4).

Fake clients only: no network, no key (the key loader returns an obviously fake value). Every
ledger, ACCESS doc, vendor root, manifest, registry and quotes file lives under tmp_path; the real
spend ledger, trial registry and ACCESS doc are checked untouched.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable, Iterator
from datetime import date
from pathlib import Path
from typing import Any

import pytest

from base_rules import constants as K
from base_rules import hist_plan as HP
from data import config
from data import hist_store as hs
from data import pull_hist as ph
from data import pull_step2 as ps
from data.pull_mes import monthly_chunks
from data.spend_gate import read_entries
from screening import harness_freeze
from screening import trial_registry as tr
from tests.test_e14_pull_hist import buy_client, gate_kwargs, never, quote_client
from tests.test_pull_universe import e0_like_price

HARNESS = "ab" * 32
FAKE_KEY = "fake-v12-key-not-real"
E14 = "stage-E.14-2026-10-05"
E17 = "stage-E.17-ext2010h"
E16_IDS = ("E16-H1", "E16-H2", "E16-H3", "E16-H4", "E16-H5")
WINDOWS = config.REPO_ROOT / "reports" / "stage_e16_windows.json"
LATE = {"HE": 22, "RTY": 23, "TN": 40}


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


def windows() -> dict[str, Any]:
    return json.loads(WINDOWS.read_text(encoding="utf-8"))


def registry_e16(tmp_path: Path, ids: tuple[str, ...] = E16_IDS, test: str = "E16") -> Path:
    path = tmp_path / "registry.jsonl"
    tr.init_registry(path)
    freeze = tmp_path / f"freeze_{test}.md"
    freeze.write_text(f"frozen {test}\n", encoding="utf-8")
    tr.register(test, list(ids), freeze, hashlib.sha256(freeze.read_bytes()).hexdigest(),
                HARNESS, path=path)
    return path


def buy_argv(*roots: str, plan: str = "ext2010h") -> list[str]:
    extra = ["--roots", *roots] if roots else []
    return ["--buy", "--plan", plan, "--account", "acct-2", "--harness-sha256", HARNESS, *extra]


def main_buy(tmp_path: Path, argv: list[str], *, registry: Path, cap: float | None = None,
             client: Any = None, logs: list[str] | None = None) -> int:
    def factory(plan: str, account: str) -> Any:
        extra = {} if cap is None else {"session_cap_usd": cap}
        return ph.buy_gate(plan, account, **gate_kwargs(tmp_path), **extra)

    return ph.main(argv, key_loader=never("key loader") if client is None else (
        lambda account: FAKE_KEY), buy_gate_factory=factory,
        quote_gate_factory=never("v10 quote gate"), plan_quote_gate_factory=never("quote gate"),
        client_factory=never("client") if client is None else (lambda key: client),
        registry_path=registry, vendor_root=tmp_path / "v", reports_base=tmp_path / "reports",
        rolls_dir=tmp_path / "rolls", condition_dir=tmp_path / "cond",
        log=(lambda m: None) if logs is None else logs.append)


def main_quote(tmp_path: Path, argv: list[str], client: Any,
               factory: Callable[..., Any] | None = None) -> int:
    def default(plan: str, account: str) -> Any:
        return ph.plan_quote_gate(plan, account, **gate_kwargs(tmp_path))

    return ph.main(argv, key_loader=lambda account: FAKE_KEY,
                   quote_gate_factory=never("v10 quote gate"),
                   plan_quote_gate_factory=factory or default, buy_gate_factory=never("buy gate"),
                   client_factory=lambda key: client, log=lambda m: None)


# ------------------------------------------------------------------ the plan ----
def test_ext2010h_holds_the_21_roots_of_the_windows_file_in_its_order() -> None:
    # Arrange
    w = windows()

    # Act
    plan = ph.get_plan("ext2010h")

    # Assert
    assert plan is ph.EXT2010H and plan.name == ph.PLAN_EXT2010H == K.PLAN_EXT
    assert plan.roots == tuple(w["purchase_21_roots"]["roots"])
    assert plan.test == "E16" and plan.test_ids == E16_IDS
    assert set(plan.roots) == {p for p in K.PRODUCTS if K.HIST_PLAN_OF[p] == "ext2010h"}
    assert not set(plan.roots) & set(ph.EXT2010.roots)
    assert "ext2010h" in ph.PLANS and ph.HIST_PLAN_NAMES == ("es2011", "ext2010", "ext2010h")


def test_ext2010h_is_1993_distinct_chunks_18_x_106_tn_40_rty_23_he_22() -> None:
    items = ph.plan_chunks(ph.EXT2010H)
    counts = {r: len(ph.EXT2010H.chunks_of(r)) for r in ph.EXT2010H.roots}
    assert len(items) == 1993 == windows()["purchase_21_roots"]["chunks"]
    assert len({i.key for i in items}) == 1993
    assert {r: n for r, n in counts.items() if n != 106} == LATE
    assert sum(n == 106 for n in counts.values()) == 18
    assert [i.root for i in items] == [r for r in ph.EXT2010H.roots for _ in range(counts[r])]


@pytest.mark.parametrize("root", ph.EXT2010H.roots)
def test_each_roots_chunks_run_monthly_from_its_u2_start_month_through_2019_04(root: str) -> None:
    # Arrange
    row = windows()["products"][root]
    start = date.fromisoformat(f"{row['start_month']}-01")

    # Act
    chunks = ph.EXT2010H.chunks_of(root)
    items = ph.plan_chunks(ph.EXT2010H, (root,))

    # Assert
    assert chunks == tuple(monthly_chunks(start, date(2019, 5, 1)))
    assert len(chunks) == int(row["chunks_2010_to_2019_04"])
    assert chunks[0][0] == f"{row['start_month']}-01" == row["window_start_on_or_after"]
    assert chunks[-1] == ("2019-04-01", "2019-05-01")
    assert {i.params.symbols for i in items} == {(f"{root}.v.0",)}
    assert [(i.params.start, i.params.end) for i in items] == list(chunks)


def test_ext2010h_store_dates_and_data_window() -> None:
    plan = ph.EXT2010H
    assert (plan.first_trade_date, plan.last_trade_date) == (date(2010, 7, 1), date(2019, 4, 30))
    assert (plan.data_start, plan.data_end) == (date(2010, 7, 1), date(2019, 5, 1))
    assert plan.chunks == tuple(monthly_chunks(date(2010, 7, 1), date(2019, 5, 1)))
    assert plan.first_trade_date == K.DEFAULT_START and plan.last_trade_date == K.HIST_LAST
    assert HP.default_resolver("ext2010h") == HP.PlanWindow("ext2010h", date(2010, 7, 1),
                                                            date(2019, 4, 30))


def test_base_rules_check_name_accepts_every_ext2010h_store_name(tmp_path: Path) -> None:
    for root in ph.EXT2010H.roots:
        path = hs.hist_parquet_path(root, "ext2010h", tmp_path)
        assert path.name == f"ohlcv-1m_{root}_v_0_2010-07-01_2019-04-30_ext2010h.parquet"
        assert path.parent == tmp_path / "ext2010h" / root
        assert HP.check_name(root, "ext2010h", path) == (date(2010, 7, 1), date(2019, 4, 30))
    assert hs.expected_names("TN", ph.EXT2010H)[0] == "range=2016-01-01_2016-02-01.dbn.zst"
    assert len(hs.expected_names("HE", ph.EXT2010H)) == 22


def test_es2011_and_ext2010_are_unchanged() -> None:
    es, ext = ph.ES2011, ph.EXT2010
    assert es.chunks == tuple(monthly_chunks(date(2011, 5, 1), date(2019, 5, 1)))
    assert ext.chunks == (("2010-06-06", "2010-07-01"),
                          *monthly_chunks(date(2010, 7, 1), date(2019, 5, 1)))
    for plan in (es, ext):
        assert plan.root_chunks == ()
        assert all(plan.chunks_of(r) == plan.chunks for r in plan.roots)
        v10_keys = [ph.HistChunk(plan.name, r, ph._params(r, s, e)).key
                    for r in plan.roots for s, e in plan.chunks]
        assert [i.key for i in ph.plan_chunks(plan)] == v10_keys
    assert (es.test, es.test_ids, es.roots) == ("C2", ("C2-T1", "C2-T2"), ("ES",))
    assert (ext.first_trade_date, ext.data_start) == (date(2010, 6, 7), date(2010, 6, 6))
    assert ph.buy_policy("es2011") == (E14, config.E14_SESSION_CAP_USD, 3.0)
    assert ph.buy_policy("ext2010") == ("stage-E.14-ext2010", config.E14_EXT2010_SESSION_CAP_USD,
                                        3.0)
    assert ph.quote_gate().session_id == E14
    assert ph.quote_session_id("es2011") == ph.quote_session_id("ext2010") == E14


# ------------------------------------------------------------- session and config ----
def test_ext2010h_quotes_and_buys_under_its_own_session() -> None:
    assert config.STAGE_E17_EXT2010H_SESSION_ID == E17
    assert ph.quote_session_id("ext2010h") == E17
    assert ph.buy_policy("ext2010h") == (E17, config.E17_EXT2010H_SESSION_CAP_USD,
                                         config.E14_REQUEST_CAP_USD)
    gate = ph.plan_quote_gate("ext2010h")
    assert (gate.session_id, gate.account_id) == (E17, config.ACCOUNT_2_ID)
    assert ph.buy_gate("ext2010h").session_id == E17
    assert E17 not in {config.STAGE_E14_SESSION_ID, config.STAGE_E14_EXT2010_SESSION_ID}
    with pytest.raises(ph.HistPlanError, match="unknown hist plan"):
        ph.quote_session_id("ext2011")


def test_the_v12_config_block_holds_the_placeholder_cap() -> None:
    # The lead replaced 0.00 with the fresh quote's cap before the commit (rulings V12-R3)
    assert config.E17_EXT2010H_SESSION_CAP_USD == 65.82
    assert config.E14_REQUEST_CAP_USD == 3.00
    source = Path(config.__file__).read_text(encoding="utf-8")
    assert source.index("\nHIST_ROOT =") < source.index("\nSTAGE_E17_EXT2010H_SESSION_ID =") \
        < source.index("\nDATABENTO_KEY_ENV_BY_ACCOUNT")


# ------------------------------------------------------------- check_hist_chunk ----
@pytest.mark.parametrize("root,start,end,match", [
    ("6A", "2010-06-01", "2010-07-01", "not one of plan ext2010h's 106 6A chunks"),
    ("6A", "2010-06-06", "2010-07-01", "not one of"),  # ext2010's partial chunk
    ("TN", "2015-12-01", "2016-01-01", "not one of plan ext2010h's 40 TN chunks 2016-01-01"),
    ("TN", "2010-07-01", "2010-08-01", "not one of"),  # another root's month, not TN's
    ("RTY", "2017-05-01", "2017-06-01", "not one of plan ext2010h's 23 RTY chunks"),
    ("HE", "2017-06-01", "2017-07-01", "not one of plan ext2010h's 22 HE chunks"),
    ("6A", "2019-05-01", "2019-06-01", "not one of"),  # past 2019-05-01
    ("ZT", "2019-04-01", "2019-05-02", "not one of"),  # past 2019-05-01
    ("6A", "2010-07-01", "2010-07-15", "not one of"),  # not a monthly chunk
    ("NG", "2010-07-01", "2010-08-01", "not a root"),  # a C1 root
    ("ES", "2011-05-01", "2011-06-01", "not a root"),
    ("MES", "2019-04-01", "2019-05-01", "not a root"),
])
def test_any_chunk_outside_its_own_roots_list_is_refused(root: str, start: str, end: str,
                                                         match: str) -> None:
    item = ph.HistChunk("ext2010h", root, ph._params(root, start, end))
    with pytest.raises(ph.HistPlanError, match=match):
        ph.check_hist_chunk(item, ph.EXT2010H)


def test_each_roots_own_first_and_last_chunks_pass() -> None:
    for root, first in (("6A", "2010-07-01"), ("TN", "2016-01-01"), ("RTY", "2017-06-01"),
                        ("HE", "2017-07-01")):
        nxt = ph.EXT2010H.chunks_of(root)[0][1]
        ph.check_hist_chunk(ph.HistChunk("ext2010h", root, ph._params(root, first, nxt)),
                            ph.EXT2010H)
        ph.check_hist_chunk(ph.HistChunk("ext2010h", root, ph._params(
            root, "2019-04-01", "2019-05-01")), ph.EXT2010H)


def test_another_plans_chunk_a_wrong_request_or_type_is_refused() -> None:
    ng = ph.plan_chunks(ph.EXT2010, ("NG",))[1]
    with pytest.raises(ph.HistPlanError, match="plan 'ext2010', not 'ext2010h'"):
        ph.check_hist_chunk(ng, ph.EXT2010H)
    mine = ph.plan_chunks(ph.EXT2010H, ("6A",))[0]
    with pytest.raises(ph.HistPlanError, match="plan 'ext2010h', not 'ext2010'"):
        ph.check_hist_chunk(mine, ph.EXT2010)
    with pytest.raises(ph.HistPlanError, match="plan 'ext2010h', not 'es2011'"):
        ph.check_hist_chunk(mine, ph.ES2011)
    swapped = ph.HistChunk("ext2010h", "6A", ph._params("6B", "2010-07-01", "2010-08-01"))
    with pytest.raises(ph.HistPlanError, match="not a ext2010h request"):
        ph.check_hist_chunk(swapped, ph.EXT2010H)
    with pytest.raises(ph.HistPlanError, match="only a HistChunk"):
        ph.check_hist_chunk(ps.chunk_for("NQ", "2019-05-01", "2019-06-01"), ph.EXT2010H)
    with pytest.raises(ps.Step2QuoteOnlyChunk):
        ps.check_chunk(mine)  # the step 2 buy path never takes a hist chunk
    with pytest.raises(ph.HistPlanError, match="not a root of plan ext2010h"):
        ph.plan_chunks(ph.EXT2010H, ("NG",))


# ------------------------------------------------------------------ --roots ----
def test_select_roots_restricts_ext2010h_in_the_order_given() -> None:
    assert ph.select_roots(ph.EXT2010H, None) is None
    chosen = ph.select_roots(ph.EXT2010H, ["ZT", "ZF", "ZB", "HE"])
    items = ph.plan_chunks(ph.EXT2010H, chosen)
    assert chosen == ("ZT", "ZF", "ZB", "HE")
    assert len(items) == 3 * 106 + 22
    assert list(dict.fromkeys(i.root for i in items)) == ["ZT", "ZF", "ZB", "HE"]


@pytest.mark.parametrize("plan,roots,match", [
    ("ext2010h", ["NG"], "not root"),
    ("ext2010h", ["6A", "ES"], "not root"),
    ("ext2010h", ["6A", "6A"], "more than once"),
    ("ext2010h", [], "at least one"),
    ("ext2010", ["NG"], "is for plan ext2010h only"),
    ("ext2010", ["NG", "NQ", "ZN", "6E", "GC", "ZC"], "is for plan ext2010h only"),
    ("es2011", ["ES"], "is for plan ext2010h only"),
])
def test_select_roots_refusals(plan: str, roots: list[str], match: str) -> None:
    with pytest.raises(ph.HistPlanError, match=match):
        ph.select_roots(ph.get_plan(plan), roots)


@pytest.mark.parametrize("argv", [
    ["--quote-only", "--plan", "ext2010", "--quotes-out", "q.json", "--roots", "NG"],
    ["--quote-only", "--plan", "es2011", "--quotes-out", "q.json", "--roots", "ES"],
    ["--quote-only", "--plan", "ext2010h", "--quotes-out", "q.json", "--roots", "NG"],
    ["--quote-only", "--plan", "ext2010h", "--quotes-out", "q.json", "--roots", "HE", "HE"],
    buy_argv("NG", plan="ext2010"),
    buy_argv("ES", plan="es2011"),
    buy_argv("6A", "CL", "NQ"),
    buy_argv("ZT", "ZT"),
])
def test_cli_roots_refusals_happen_before_any_gate_preflight_key_or_client(
        argv: list[str], monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(harness_freeze, "preflight", never("harness preflight"))
    rc = ph.main(argv, key_loader=never("key loader"), quote_gate_factory=never("quote gate"),
                 plan_quote_gate_factory=never("quote gate"), buy_gate_factory=never("buy gate"),
                 client_factory=never("client"), log=never("log"))
    assert rc == ph.RC_REFUSED


def test_cli_an_empty_roots_list_is_refused_by_the_parser() -> None:
    with pytest.raises(SystemExit) as exc:
        ph.main(buy_argv() + ["--roots"], key_loader=never("key loader"),
                buy_gate_factory=never("buy gate"), client_factory=never("client"))
    assert exc.value.code == ph.RC_REFUSED


# ------------------------------------------------------------------ quote ----
def test_an_ext2010h_quote_ledgers_only_new_session_lines_and_ignores_older_sessions(
        tmp_path: Path) -> None:
    # Arrange: an E.14-session quote line for HE's first chunk, priced far off, already ledgered
    he = ph.plan_chunks(ph.EXT2010H, ("HE",))
    old = ph.quote_gate(config.ACCOUNT_2_ID, **gate_kwargs(tmp_path))
    ph.run_hist_quotes(quote_client(lambda kw: 99.0), old, ph.EXT2010H, he[:1],
                       log=lambda m: None)
    out = tmp_path / "q" / "quotes_ext2010h.json"
    client = quote_client()

    # Act
    rc = main_quote(tmp_path, ["--quote-only", "--plan", "ext2010h", "--quotes-out", str(out),
                               "--roots", "HE", "RTY"], client)

    # Assert
    assert rc == 0 and client.billable_hits == []
    lines = read_entries(tmp_path / "ledger.jsonl")
    new = lines[1:]
    assert len(new) == 45 and {(e["event"], e["session_id"], e["account"], e["usd"])
                               for e in new} == {("quote", E17, "acct-2", 0.0)}
    assert {tuple(e["request"]["symbols"]) for e in new} == {("HE.v.0",), ("RTY.v.0",)}
    payload = json.loads(out.read_text(encoding="utf-8"))
    section = payload["sets"]["plan:ext2010h"]
    assert payload["session_id"] == E17 and section["roots"] == ["HE", "RTY"]
    assert section["chunks"] == 45 and section["complete"]
    assert section["per_root"]["HE"]["usd"] == pytest.approx(
        sum(e0_like_price(c.params.as_kwargs()) for c in he))
    assert section["per_root"]["HE"]["largest_chunk_usd"] < 1.0  # the E.14 line is not read
    assert FAKE_KEY not in out.read_text(encoding="utf-8")


def test_an_ext2010h_quote_of_the_whole_plan_covers_all_1993_chunks(tmp_path: Path) -> None:
    out = tmp_path / "quotes.json"
    rc = main_quote(tmp_path, ["--quote-only", "--plan", "ext2010h", "--quotes-out", str(out)],
                    quote_client())
    lines = read_entries(tmp_path / "ledger.jsonl")
    section = json.loads(out.read_text(encoding="utf-8"))["sets"]["plan:ext2010h"]
    assert rc == 0 and len(lines) == 1993 and {e["session_id"] for e in lines} == {E17}
    assert section["chunks"] == 1993 and section["roots"] == list(ph.EXT2010H.roots)
    assert section["chunk_range"] == ["2010-07-01", "2019-05-01"]
    assert section["store_trade_dates"] == ["2010-07-01", "2019-04-30"]
    assert {r: row["chunks"] for r, row in section["per_root"].items() if row["chunks"] != 106} \
        == LATE


def test_an_ext2010h_quote_through_a_gate_of_another_session_is_refused(tmp_path: Path) -> None:
    def e14_gate(plan: str, account: str) -> Any:
        return ph.quote_gate(account, **gate_kwargs(tmp_path))

    rc = main_quote(tmp_path, ["--quote-only", "--plan", "ext2010h", "--quotes-out",
                               str(tmp_path / "q.json"), "--roots", "HE"],
                    never("client"), factory=e14_gate)
    assert rc == ph.RC_REFUSED and not (tmp_path / "ledger.jsonl").exists()


def test_a_v10_quote_still_uses_the_v10_quote_gate_only(tmp_path: Path) -> None:
    client = quote_client()
    rc = ph.main(["--quote-only", "--plan", "es2011", "--quotes-out", str(tmp_path / "q.json")],
                 key_loader=lambda account: FAKE_KEY,
                 quote_gate_factory=lambda account: ph.quote_gate(account,
                                                                  **gate_kwargs(tmp_path)),
                 plan_quote_gate_factory=never("plan quote gate"),
                 buy_gate_factory=never("buy gate"), client_factory=lambda key: client,
                 log=lambda m: None)
    assert rc == 0 and {e["session_id"] for e in read_entries(tmp_path / "ledger.jsonl")} == {E14}


# ------------------------------------------------------------------ buy ----
def test_the_ext2010h_buy_refuses_at_a_zero_cap_even_when_registered(
        tmp_path: Path, preflight_ok: list[str]) -> None:
    registry = registry_e16(tmp_path)
    assert main_buy(tmp_path, buy_argv("HE"), registry=registry, cap=0.0) == ph.RC_REFUSED
    assert preflight_ok == [HARNESS]  # the preflight ran first


def test_an_ext2010h_buy_without_roots_is_refused_before_the_preflight(
        tmp_path: Path, preflight_ok: list[str]) -> None:
    # Review F-1 (E.17): a buy of ext2010h must name the lead's selection with --roots.
    registry = registry_e16(tmp_path)
    assert main_buy(tmp_path, buy_argv(), registry=registry, cap=10.0) == ph.RC_REFUSED
    assert preflight_ok == []  # refused by the argument check, before any gate or vendor call


def test_the_ext2010h_buy_refuses_at_the_configured_placeholder_cap(
        tmp_path: Path, preflight_ok: list[str]) -> None:
    if config.E17_EXT2010H_SESSION_CAP_USD != 0.0:
        pytest.skip("the lead has set the v12 cap; the zero-cap refusal is tested above")
    assert main_buy(tmp_path, buy_argv("HE"), registry=registry_e16(tmp_path)) == ph.RC_REFUSED


@pytest.mark.parametrize("make", [
    lambda p: (tr.init_registry(p / "registry.jsonl"), p / "registry.jsonl")[1],
    lambda p: registry_e16(p, ("E16-H1", "E16-H2", "E16-H3", "E16-H4")),  # H5 missing
    lambda p: registry_e16(p, ("C2-T1", "C2-T2"), test="C2"),
])
def test_the_ext2010h_buy_refuses_without_e16_h1_to_h5_registered(
        tmp_path: Path, preflight_ok: list[str], make: Callable[[Path], Path]) -> None:
    assert main_buy(tmp_path, buy_argv("HE"), registry=make(tmp_path), cap=10.0) \
        == ph.RC_REFUSED


def test_a_two_root_buy_buys_exactly_those_roots_chunks(tmp_path: Path,
                                                        preflight_ok: list[str]) -> None:
    # Arrange
    client = buy_client()
    logs: list[str] = []

    # Act
    rc = main_buy(tmp_path, buy_argv("HE", "RTY"), registry=registry_e16(tmp_path), cap=10.0,
                  client=client, logs=logs)

    # Assert: 22 + 23 chunks, nothing of any other root
    assert rc == 0 and len(client.downloads) == 45
    assert {tuple(d["symbols"]) for d in client.downloads} == {("HE.v.0",), ("RTY.v.0",)}
    assert [(d["start"], d["end"]) for d in client.downloads] == [
        *ph.EXT2010H.chunks_of("HE"), *ph.EXT2010H.chunks_of("RTY")]
    lines = read_entries(tmp_path / "ledger.jsonl")
    assert {e["session_id"] for e in lines} == {E17} and {e["account"] for e in lines} == {
        "acct-2"}
    assert sum(e["event"] == "commit" for e in lines) == 45 == sum(
        e["event"] == "settle" for e in lines)
    assert sorted(p.name for p in (tmp_path / "reports").iterdir()) == [
        "purchase_HE_ext2010h.json", "purchase_RTY_ext2010h.json"]
    he = json.loads((tmp_path / "reports" / "purchase_HE_ext2010h.json").read_text())
    assert (he["plan"], he["test"], len(he["files"])) == ("ext2010h", "E16", 22)
    assert he["files"][0]["request_start"] == "2017-07-01"
    raw_dirs = tmp_path / "v" / "GLBX.MDP3" / "ohlcv-1m"
    assert sorted(p.name for p in raw_dirs.iterdir()) == ["HE_v_0", "RTY_v_0"]
    assert [p.name for p in (tmp_path / "v").iterdir()] == ["GLBX.MDP3"]
    resolved = [c["symbols"] for c in client.symbology.calls if c["stype_in"] == "continuous"]
    assert resolved == [["HE.v.0"], ["RTY.v.0"]]
    assert {(c["start_date"], c["end_date"]) for c in client.symbology.calls} == {
        ("2010-07-01", "2019-05-01")}
    assert sorted(p.name for p in (tmp_path / "rolls").iterdir()) == [
        "HE_v_0_2010-07-01_2019-05-01_symbology.json",
        "RTY_v_0_2010-07-01_2019-05-01_symbology.json"]
    assert ph.condition_path(ph.EXT2010H, tmp_path / "cond").name == \
        "GLBX.MDP3_2010-07-01_2019-05-01.json"
    assert ph.condition_path(ph.EXT2010H, tmp_path / "cond").is_file()
    assert any("--roots: 2 of plan ext2010h's 21 roots" in m for m in logs)
    assert FAKE_KEY not in "".join(logs)
