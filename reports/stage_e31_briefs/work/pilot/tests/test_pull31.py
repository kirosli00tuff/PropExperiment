"""pull31.py, verify31.py and pilot31_common.py on synthetic inputs only.

A fake Databento client (no network, no key: the key loader is a stub that records calls), tmp
ledgers, tmp vendor and runs folders, synthetic DBN files (mbo, mbp-1, definition). Run with
    uv run pytest -q -p no:cacheprovider reports/stage_e31_briefs/work/pilot/tests/test_pull31.py
"""

import json
import os
import stat
import sys
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace

import pytest

PILOT = Path(__file__).resolve().parents[1]
if str(PILOT) not in sys.path:
    sys.path.insert(0, str(PILOT))

import pilot31_common as pc  # noqa: E402
import pull31 as pp  # noqa: E402
import verify31 as vf  # noqa: E402

from data.quote_universe import ForbiddenNamespace  # noqa: E402
from data.spend_gate import RequestParams  # noqa: E402

S = pc.NS
H = 3600 * S
N_PER_SYMBOL = 3
COST = {"mbo": 30.0, "mbp-1": 5.0, "definition": 1.0}  # USD per request; 41.00 per month
VOLUME_LINES = [
    {"ts": "2026-10-22T14:58:55.990161+00:00", "event": "commit", "session_id": pc.VOLUME_SESSION,
     "account": "acct-3", "usd": 0.72502180934, "request": pc.VOLUME_REQUEST,
     "quoted_usd": 0.72502180934, "billable_bytes": 1},
    {"ts": "2026-10-22T15:00:06.053807+00:00", "event": "settle", "session_id": pc.VOLUME_SESSION,
     "account": "acct-3", "usd": 0.0, "request": pc.VOLUME_REQUEST,
     "quoted_usd": 0.72502180934, "billable_bytes": 1},
]


# ------------------------------------------------------------------ synthetic DBN ----
F_SNAP = 32 | 8 | 128  # F_SNAPSHOT | F_BAD_TS_RECV | F_LAST: an empty book's snapshot
RECV_DELAY = 1000  # ns: ts_recv = ts_event + 1 us for ordinary records
BASE_OFFSET = 17 * 60 * S  # base records sit 17 min after the hour (never on a midnight)
TAIL_BEFORE_END = 10 * S  # the tail record: 10 s before the month's last DAY session end


def _record(schema: str, iid: int, t: int, k: int, *, recv: int | None = None,
            kind: str = "base"):
    import databento_dbn as dbn

    recv = t + RECV_DELAY if recv is None else recv
    if schema == "mbo":
        if kind == "snap":
            return dbn.MBOMsg(1, iid, t, 0, 2**63 - 1, 0, dbn.Action.CLEAR, dbn.Side.NONE, recv,
                              flags=F_SNAP, sequence=0)
        return dbn.MBOMsg(1, iid, t, 1000 + k, 350 * 10**9, 1, dbn.Action.ADD, dbn.Side.BID,
                          recv, flags=0, sequence=k + 1)
    if schema == "mbp-1":
        level = dbn.BidAskPair(bid_px=1200 * 10**9, ask_px=1201 * 10**9, bid_sz=1, ask_sz=1,
                               bid_ct=1, ask_ct=1)
        return dbn.MBP1Msg(1, iid, t, 1200 * 10**9, 1, dbn.Action.ADD, dbn.Side.BID, 0,
                           recv, flags=0, sequence=k + 1, levels=level)
    return dbn.InstrumentDefMsg(1, iid, t, recv, 10**8, 10**9, f"SYM{iid}", "ZM", "FUT",
                                dbn.InstrumentClass.FUTURE, dbn.SecurityUpdateAction.ADD)


def record_size(schema: str) -> int:
    return len(bytes(_record(schema, 1, 1, 0)))


def item_of(kw: dict) -> pc.Planned:
    params = RequestParams(kw["dataset"], tuple(kw["symbols"]), kw["schema"], kw["stype_in"],
                           kw["start"], kw["end"])
    return pc.Planned(pc.series_of(params), pc.month_of_end(kw["end"]), params)


def default_mappings(kw: dict) -> dict[str, list[tuple[date, date, int]]]:
    """Each symbol -> one instrument (100, 101, ...) over the whole request. A parent request
    is keyed by a child raw symbol (ZM.FUT -> ZMH4), as the real Z4 headers are."""
    d0, d1 = pc.parse_utc(kw["start"]).date(), pc.parse_utc(kw["end"]).date() + timedelta(days=1)
    key = (lambda s: s.split(".")[0] + "H4") if kw["stype_in"] == "parent" else (lambda s: s)
    return {key(sym): [(d0, d1, 100 + n)] for n, sym in enumerate(kw["symbols"])}


def encode_dbn(path: Path, kw: dict, records: list, mappings: dict | None = None) -> Path:
    """A zstd DBN v3 file whose header is the request ``kw``, holding ``records``."""
    import databento_dbn as dbn
    import zstandard

    schema = {"mbo": dbn.Schema.MBO, "mbp-1": dbn.Schema.MBP_1,
              "definition": dbn.Schema.DEFINITION}[kw["schema"]]
    stype = {"continuous": dbn.SType.CONTINUOUS, "parent": dbn.SType.PARENT}[kw["stype_in"]]
    maps = default_mappings(kw) if mappings is None else mappings
    meta = dbn.Metadata(kw["dataset"], pc.bound_ns(kw["start"]), stype, dbn.SType.INSTRUMENT_ID,
                        schema, symbols=list(kw["symbols"]), partial=[], not_found=[],
                        mappings=[SimpleNamespace(raw_symbol=sym, intervals=[
                            SimpleNamespace(start_date=a, end_date=b, symbol=str(iid))
                            for a, b, iid in rows]) for sym, rows in maps.items()],
                        end=pc.bound_ns(kw["end"]))
    raw = bytes(meta.encode()) + b"".join(bytes(r) for r in records)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(zstandard.ZstdCompressor().compress(raw))
    return path


def synthetic_records(kw: dict, *, late: bool = False, early: bool = False,
                      after_cutoff: bool = False, drop_snapshot: tuple | None = None,
                      short_tail: bool = False, early_event: bool = False) -> list:
    """N_PER_SYMBOL base records per symbol; for mbo, an empty-book snapshot (R, F_SNAPSHOT,
    ts_recv 00:00Z) per weekday midnight and mapped instrument; for mbo and mbp-1, one tail
    record 10 s before the month's last DAY session end (a day earlier with short_tail).
    late/early/after_cutoff move the last or first record (the byte count is unchanged);
    drop_snapshot = (UTC date, instrument_id) leaves that snapshot out."""
    import verify31

    start_ns, end_ns = pc.bound_ns(kw["start"]), pc.bound_ns(kw["end"])
    ids = [100 + n for n in range(len(kw["symbols"]))]
    events = [[start_ns + (k + 1) * H + BASE_OFFSET, None, iid, "base"]
              for k, iid in enumerate(i for i in ids for _ in range(N_PER_SYMBOL))]
    if kw["schema"] == "mbo":
        for mid in verify31.weekday_midnights(start_ns, end_ns):
            day = datetime.fromtimestamp(mid // S, UTC).date()
            events += [[mid, mid, iid, "snap"] for iid in ids if drop_snapshot != (day, iid)]
    if kw["schema"] in ("mbo", "mbp-1"):
        tail = verify31.last_day_session_end_ns(item_of(kw))[1] - TAIL_BEFORE_END
        events.append([tail - (24 * H if short_tail else 0), None, ids[0], "base"])
    events.sort(key=lambda e: e[1] if e[1] is not None else e[0] + RECV_DELAY)
    if late:
        events[-1][:2] = [end_ns, None]
    if early:
        events[0][:2] = [start_ns - S, None]
    if early_event:  # ts_event before the start, ts_recv inside (a snapshot's resting order)
        events[0][:2] = [start_ns - S, start_ns + S]
    if after_cutoff:
        events[-1][:2] = [int(pc.NO_RECORD_FROM_UTC.timestamp()) * S, None]
    return [_record(kw["schema"], iid, t, k, recv=recv, kind=kind)
            for k, (t, recv, iid, kind) in enumerate(events)]


def write_dbn(path: Path, kw: dict, **flags) -> Path:
    return encode_dbn(path, kw, synthetic_records(kw, **flags))


def synthetic_bytes(kw: dict, **flags) -> int:
    return sum(len(bytes(r)) for r in synthetic_records(kw, **flags))


# ------------------------------------------------------------------ fakes ----
class Tripwire:
    """A client stand-in: any use fails the test."""

    def __getattr__(self, name):
        raise AssertionError(f"client.{name} used")


class FakeClient:
    def __init__(self, cost=None, billable_scale=1.0, fail_download=False, special=None):
        self.cost = cost or (lambda kw: COST[kw["schema"]])
        self.scale = 1.0
        self.billable_scale = billable_scale
        self.fail_download = fail_download
        self.special = special or {}  # request key -> write_dbn flags
        self.calls = {"cost": [], "get_range": [], "condition": []}
        self.last = None

    def fresh(self):
        """A new client facade per build (a real run builds one client per process; the
        guards are installed on that object), sharing this fake's state and call log."""
        self.last = SimpleNamespace(
            metadata=SimpleNamespace(get_cost=self._get_cost, get_billable_size=self._billable,
                                     get_dataset_condition=self._condition),
            timeseries=SimpleNamespace(get_range=self._get_range), batch=None)
        return self.last

    def _get_cost(self, **kw):
        self.calls["cost"].append(kw)
        return round(self.cost(kw) * self.scale, 9)

    def _billable(self, **kw):
        from data.quote_universe import request_key

        n = synthetic_bytes(kw, **self.special.get(request_key(kw), {}))
        return int(n * self.billable_scale)

    def _condition(self, **kw):
        self.calls["condition"].append(kw)
        return [{"date": "2024-02-01", "condition": "available"}]

    def _get_range(self, path, **kw):
        self.calls["get_range"].append(kw)
        if self.fail_download:
            Path(path).write_bytes(b"partial")
            raise RuntimeError("connection reset")
        from data.quote_universe import request_key

        write_dbn(Path(path), kw, **self.special.get(request_key(kw), {}))


class Env:
    def __init__(self, tmp: Path) -> None:
        self.ledger = tmp / "ledger" / "spend.jsonl"
        self.access = tmp / "ACCESS.md"
        self.vendor = tmp / "vendor"
        self.vendor.mkdir()
        self.runs = tmp / "runs"
        self.keys: list[str] = []
        self.built: list[str] = []
        self.logs: list[str] = []
        self.seed(*VOLUME_LINES)

    def key_loader(self, account=None):
        self.keys.append(account)
        return "fake-key-not-real"

    def run(self, argv, client=None, now=None):
        def factory(key):
            self.built.append(key)
            if client is None:
                return Tripwire()
            return client.fresh() if isinstance(client, FakeClient) else client

        return pp.main(argv, key_loader=self.key_loader, client_factory=factory,
                       ledger_path=self.ledger, access_doc_path=self.access,
                       vendor_root=self.vendor, runs_dir=self.runs,
                       now=now or (lambda: datetime.now(UTC)), log=self.logs.append,
                       sleep=lambda s: None)

    def verify(self, *extra):
        return vf.main(["--months", "2", *extra], vendor_root=self.vendor, runs_dir=self.runs)

    def lines(self, session=None, event=None):
        rows = [json.loads(x) for x in self.ledger.read_text().splitlines() if x.strip()]
        return [r for r in rows if (session is None or r.get("session_id") == session)
                and (event is None or r.get("event") == event)]

    def seed(self, *entries):
        self.ledger.parent.mkdir(parents=True, exist_ok=True)
        with self.ledger.open("a") as fh:
            for e in entries:
                fh.write(json.dumps(e) + "\n")

    def quote31(self):
        return json.loads((self.runs / "quote31.json").read_text())


@pytest.fixture
def env(tmp_path):
    return Env(tmp_path)


def quoted(env, months=2, client=None):
    client = client or FakeClient()
    assert env.run(["--quote", "--months", str(months)], client) == 0
    return client, env.quote31()["sum_usd"]


def buy(env, client, approved, months=2, now=None):
    return env.run(["--buy", "--months", str(months), "--approved-usd", str(approved)],
                   client, now)


# ------------------------------------------------------------------ months ----
def test_month_bounds_follow_chicago_dst_and_end_exactly_at_the_cutoff():
    assert pc.month_bounds(date(2023, 10, 1)) == ("2023-09-30T21:00:00Z", "2023-10-31T21:00:00Z")
    assert pc.month_bounds(date(2023, 11, 1)) == ("2023-10-31T21:00:00Z", "2023-11-30T22:00:00Z")
    assert pc.month_bounds(date(2023, 3, 1)) == ("2023-02-28T22:00:00Z", "2023-03-31T21:00:00Z")
    assert pc.month_bounds(date(2024, 2, 1)) == ("2024-01-31T22:00:00Z", "2024-02-29T22:00:00Z")
    assert pc.month_bounds(pc.LAST_MONTH)[1] == pc.CUTOFF_BOUND == "2024-02-29T22:00:00Z"
    assert pc.month_bounds(date(2019, 6, 1))[0] == "2019-05-31T21:00:00Z"


def test_months_back_and_buy_order():
    assert pc.months_back(2) == [date(2024, 2, 1), date(2024, 1, 1)]
    assert pc.n_available_months() == 57 and pc.span_months()[-1] == date(2019, 6, 1)
    order = [i.label for i in pc.plan(2)]
    assert order == ["Z1 2024-02", "Z1 2024-01", "Z2 2024-02", "Z2 2024-01", "Z3 2024-02",
                     "Z3 2024-01", "Z4 2024-02", "Z4 2024-01"]
    item = pc.plan(1)[0]
    assert item.params.symbols == ("ZM.v.0", "ZM.v.1") and item.params.schema == "mbo"
    assert pc.target_path(item, Path("/v")) == Path(
        "/v/GLBX.MDP3/mbo/Z1_ZM_v_0-ZM_v_1/range=2024-01-31T220000Z_2024-02-29T220000Z.dbn.zst")
    for bad in (0, -1, 58):
        with pytest.raises(pc.PilotRefused):
            pc.months_back(bad)


# ------------------------------------------------------------------ guards ----
GOOD = pc.request_for(pc.SERIES[0], date(2024, 2, 1))
G = GOOD.as_kwargs()


def _p(**over):
    kw = {**G, **over}
    return RequestParams(kw["dataset"], tuple(kw["symbols"]), kw["schema"], kw["stype_in"],
                         kw["start"], kw["end"])


FORBIDDEN = [
    (_p(dataset="XNAS.ITCH"), "dataset"),
    (_p(symbols=["ZC.v.0", "ZC.v.1"]), "root(s)"),
    (_p(symbols=["ES.v.0"], schema="mbp-1"), "root(s)"),
    (_p(schema="mbp-10"), "not one of the four pilot series"),
    (_p(schema="mbp-1"), "not one of the four pilot series"),
    (_p(symbols=["ZM.v.0"]), "not one of the four pilot series"),
    (_p(symbols=["ZM.v.1", "ZM.v.0"]), "not one of the four pilot series"),
    (_p(symbols=["ZM.v.0", "ZM.v.1", "ZM.v.2"]), "not one of the four pilot series"),
    (_p(stype_in="raw_symbol"), "not one of the four pilot series"),
    (_p(stype_in="parent", symbols=["ZM.FUT"]), "not one of the four pilot series"),
    (_p(end="2024-02-29T22:00:01Z"), "after 2024-02-29T22:00:00Z"),
    (_p(end="2024-03-01"), "after 2024-02-29T22:00:00Z"),
    (_p(end="2024-02-29T21:00:00Z"), "not the month rule's window"),
    (_p(start="2024-01-31T21:00:00Z"), "not the month rule's window"),
    (_p(start="2024-02-01", end="2024-02-29T22:00:00Z"), "not the month rule's window"),
    (_p(start=pc.month_bounds(date(2024, 3, 1))[0], end=pc.month_bounds(date(2024, 3, 1))[1]),
     "after 2024-02"),
    (_p(start=pc.month_bounds(date(2019, 5, 1))[0], end=pc.month_bounds(date(2019, 5, 1))[1]),
     "before 2019-06"),
    (_p(start="2024-13-31T22:00:00Z"), "unparseable"),
    (_p(start="2024-01-31T22:00:00+00:00"), "not canonical"),
    (_p(start="2024-01-31T22:00Z"), "not canonical"),
    (_p(start=pc.month_bounds(date(2025, 6, 1))[0], end=pc.month_bounds(date(2025, 6, 1))[1]),
     "research window"),
]


@pytest.mark.parametrize("params,reason", FORBIDDEN)
def test_request_guard_refuses_each_forbidden_input(params, reason):
    reasons = pc.request_refusals(params)
    assert any(reason in r for r in reasons), reasons
    with pytest.raises(pc.PilotRefused):
        pc.check_request(params)


def test_every_planned_request_passes_the_guard():
    assert all(not pc.request_refusals(i.params) for i in pc.span_order(pc.span_months()))


@pytest.mark.parametrize("account", ["acct-1", "acct-2", "acct-4", ""])
@pytest.mark.parametrize("mode", [["--plan", "--months", "2"], ["--span-search"],
                                  ["--quote", "--months", "2"],
                                  ["--buy", "--months", "2", "--approved-usd", "82"]])
def test_every_mode_refuses_another_account_before_the_key(env, capsys, mode, account):
    assert env.run([*mode, "--account", account]) == pc.RC_REFUSED
    assert env.keys == [] and env.built == []
    assert "acct-3" in capsys.readouterr().err


@pytest.mark.parametrize("argv", [["--plan", "--months", "58"], ["--plan", "--months", "0"],
                                  ["--quote", "--months", "1"], ["--quote"],
                                  ["--buy", "--months", "1", "--approved-usd", "41"],
                                  ["--buy", "--months", "2"]])
def test_month_count_and_missing_arguments_refused_before_the_key(env, argv):
    assert env.run(argv) == pc.RC_REFUSED
    assert env.keys == [] and env.built == []


@pytest.mark.parametrize("mode", [["--quote", "--months", "2"],
                                  ["--buy", "--months", "2", "--approved-usd", "82"],
                                  ["--span-search"]])
def test_a_request_off_the_month_rule_stops_every_mode_before_any_call(env, monkeypatch, mode):
    real = pc.request_for

    def shifted(series, month):
        p = real(series, month)
        return RequestParams(p.dataset, p.symbols, p.schema, p.stype_in, p.start,
                             pc.iso_z(pc.parse_utc(p.end) + timedelta(hours=1)))

    monkeypatch.setattr(pc, "request_for", shifted)
    assert env.run(mode) == pc.RC_REFUSED
    assert env.keys == [] and env.built == []


def test_spend_target_by_hand():
    assert pc.floor_cent(122.27497819066) == 122.27
    assert pc.spend_target(VOLUME_LINES)["target_usd"] == 122.27
    assert pc.spend_target([])["target_usd"] == 122.27  # rule 123.00, capped at the spec
    extra = {"account": "acct-3", "session_id": "other", "usd": 10.0, "event": "commit"}
    assert pc.spend_target([*VOLUME_LINES, extra])["target_usd"] == 112.27
    own = {**extra, "session_id": pc.PILOT_SESSION, "usd": 50.0}
    assert pc.spend_target([*VOLUME_LINES, own])["target_usd"] == 122.27
    acct2 = {**extra, "account": "acct-2"}
    assert pc.spend_target([*VOLUME_LINES, acct2])["target_usd"] == 122.27


# ------------------------------------------------------------------ plan ----
def test_plan_makes_no_call_and_reports_target_and_position(env, capsys):
    assert env.run(["--plan", "--months", "2"]) == 0
    assert env.keys == [] and env.built == []
    out = json.loads(capsys.readouterr().out)
    assert out["n_requests"] == 8 and out["vendor_calls"] == 0
    assert out["spend"]["target_usd"] == 122.27
    assert out["position"]["account_committed_usd"] == pytest.approx(0.72502180934)
    assert out["requests"][0]["target"].endswith(
        "mbo/Z1_ZM_v_0-ZM_v_1/range=2024-01-31T220000Z_2024-02-29T220000Z.dbn.zst")
    assert out["other_acct3_commits"] == []


# ------------------------------------------------------------------ span search ----
def _months(n):
    return pc.months_back(n)


def _fixed(costs):
    def quote_month(month):
        usd = costs[pc.months_back(len(costs)).index(month)]
        return [{"quoted_usd": usd}]
    return quote_month


@pytest.mark.parametrize("costs,k,over,buy_it", [
    ([50.0, 40.0, 40.0, 1.0], 2, "2023-12", True),   # 50, 90, 130 > 122.27
    ([60.0, 62.27, 0.01], 2, "2023-12", True),       # 122.27 is at most TARGET
    ([100.0, 30.0, 1.0], 1, "2024-01", False),       # k = 1 < 2: buy nothing
    ([130.0, 1.0], 0, "2024-02", False),             # the last month alone is over
])
def test_span_search_stopping_rule(costs, k, over, buy_it):
    result = pp.span_search(_months(len(costs)), _fixed(costs), 122.27, lambda m: None)
    assert (result["k"], result["first_month_over_target"], result["buy"]) == (k, over, buy_it)
    assert result["cost_usd"] == pytest.approx(sum(costs[:k]))
    assert len(result["rows"]) == k + 1 and not result["limited_by_lower_bound"]


def test_span_search_limited_by_the_lower_bound_and_a_failed_quote():
    result = pp.span_search(_months(3), _fixed([1.0, 1.0, 1.0]), 122.27, lambda m: None)
    assert result["k"] == 3 and result["limited_by_lower_bound"] and result["buy"]

    def failing(month):
        if month == date(2024, 1, 1):
            raise pp.SpanSearchError("quote failed")
        return [{"quoted_usd": 1.0}]

    result = pp.span_search(_months(3), failing, 122.27, lambda m: None)
    assert not result["complete"] and result["k"] is None and result["k_before_error"] == 1
    assert not result["buy"]


def test_span_search_cli_quotes_all_four_series_per_month_and_never_buys(env):
    client = FakeClient()  # 41.00 per month: 41, 82, 123 > 122.27 -> k = 2
    assert env.run(["--span-search"], client) == 0
    span = json.loads((env.runs / "span31.json").read_text())
    assert span["k"] == 2 and span["months"] == ["2024-02", "2024-01"]
    assert span["first_month_over_target"] == "2023-12" and span["bought"] is False
    assert [r["cumulative_usd"] for r in span["rows"]] == pytest.approx([41.0, 82.0, 123.0])
    assert all(len(r["quotes"]) == 4 for r in span["rows"])
    quotes = env.lines(pc.SPAN_SESSION, "quote")
    assert len(quotes) == 12 and all(q["usd"] == 0.0 and q["account"] == "acct-3"
                                     for q in quotes)
    assert env.lines(event="commit") == env.lines(pc.VOLUME_SESSION, "commit")
    assert isinstance(client.last.timeseries, ForbiddenNamespace)
    assert client.calls["get_range"] == []
    assert env.keys == ["acct-3"]
    assert (env.runs / "condition31_2024-01_2024-02.json").is_file()


def test_span_search_cli_buys_nothing_when_k_is_below_two(env):
    client = FakeClient(cost=lambda kw: 30.0 if kw["schema"] == "mbo" else 20.0)  # 90/month
    assert env.run(["--span-search"], client) == pc.RC_STOPPED
    span = json.loads((env.runs / "span31.json").read_text())
    assert span["k"] == 1 and span["buy"] is False
    assert client.calls["get_range"] == []


def test_span_search_cli_stops_on_a_failed_quote(env):
    def cost(kw):
        if kw["start"].startswith("2023-12-31"):
            raise RuntimeError("boom")
        return COST[kw["schema"]] / 10
    assert env.run(["--span-search"], FakeClient(cost=cost)) == pc.RC_STOPPED
    span = json.loads((env.runs / "span31.json").read_text())
    assert not span["complete"] and span["k"] is None


# ------------------------------------------------------------------ quote ----
def test_quote_writes_every_request_and_the_sum_with_billables_guarded(env):
    client, total = quoted(env)
    q = env.quote31()
    assert q["complete"] and q["within_target"] and len(q["requests"]) == 8
    assert total == pytest.approx(82.0)
    assert len(env.lines(pc.PILOT_SESSION, "quote")) == 8
    assert isinstance(client.last.timeseries, ForbiddenNamespace)
    assert isinstance(client.last.batch, ForbiddenNamespace)


def test_quote_above_target_stops_and_the_buy_refuses(env, capsys):
    client = FakeClient(cost=lambda kw: 61.2 if kw["schema"] == "mbo" else 0.01)
    assert env.run(["--quote", "--months", "2"], client) == pc.RC_STOPPED
    assert env.quote31()["sum_usd"] == pytest.approx(122.46)
    assert buy(env, client, 122.46) == pc.RC_REFUSED
    assert "TARGET" in capsys.readouterr().err and client.calls["get_range"] == []


# ------------------------------------------------------------------ buy ----
def test_buy_happy_path_order_files_records_and_idempotent_rerun(env):
    client, total = quoted(env)
    assert buy(env, client, total) == 0
    commits = env.lines(pc.PILOT_SESSION, "commit")
    assert [f"{c['schema']} {c['request']['start'][:7]}" for c in commits] == [
        "mbo 2024-01", "mbo 2023-12", "mbp-1 2024-01", "mbp-1 2023-12", "mbp-1 2024-01",
        "mbp-1 2023-12", "definition 2024-01", "definition 2023-12"]
    assert [c["request"]["symbols"][0] for c in commits][2:6] == ["ZS.v.0"] * 2 + ["ZL.v.0"] * 2
    assert len(env.lines(pc.PILOT_SESSION, "settle")) == 8
    assert len(env.lines(pc.PILOT_SESSION, "quote")) == 16  # quote31 + one re-quote each
    for item in pc.plan(2):
        target = pc.target_path(item, env.vendor)
        assert target.is_file() and not target.stat().st_mode & stat.S_IWUSR
        assert not target.with_name(target.name + ".partial").exists()
        rec = json.loads((env.runs / pc.record_name(item)).read_text())
        assert rec["settled"]["billed_over_quote_ratio"] == pytest.approx(1.0)
        assert rec["request"] == item.params.as_kwargs() and len(rec["sha256"]) == 64
    assert (env.runs / "condition31_2024-01_2024-02.json").is_file()
    keys = list(env.keys)
    assert buy(env, Tripwire(), total) == 0  # resume: everything settled, nothing called
    assert env.keys == keys
    assert len(env.lines(pc.PILOT_SESSION, "commit")) == 8


def test_buy_without_quote31_is_refused(env, capsys):
    assert buy(env, FakeClient(), 82.0) == pc.RC_REFUSED
    assert "quote31.json" in capsys.readouterr().err and env.keys == []


def test_buy_refuses_stale_quotes(env, capsys):
    client, total = quoted(env)
    later = datetime.now(UTC) + timedelta(hours=25)
    assert buy(env, client, total, now=lambda: later) == pc.RC_REFUSED
    assert "old" in capsys.readouterr().err and client.calls["get_range"] == []
    assert env.keys == ["acct-3"]  # only the --quote run read the key


def test_buy_refuses_quotes_of_another_plan(env, capsys):
    client, total = quoted(env, months=2)
    assert buy(env, client, total, months=3) == pc.RC_REFUSED
    err = capsys.readouterr().err
    assert "not this plan's" in err and "months" in err


def test_buy_refuses_a_quote31_file_that_disagrees_with_the_ledger(env, capsys):
    client, total = quoted(env)
    q = env.quote31()
    q["requests"][0]["quoted_usd"] = 20.0
    q["sum_usd"] = round(total - 10.0, 9)
    (env.runs / "quote31.json").write_text(json.dumps(q))
    assert buy(env, client, q["sum_usd"]) == pc.RC_REFUSED
    assert "no matching quote line in the ledger" in capsys.readouterr().err


@pytest.mark.parametrize("delta", [0.01, 0.02, -0.001, -5.0])
def test_buy_is_approved_for_exactly_the_quoted_sum(env, capsys, delta):
    client, total = quoted(env)
    assert buy(env, client, round(total + delta, 6)) == pc.RC_REFUSED
    assert "--approved-usd" in capsys.readouterr().err and client.calls["get_range"] == []


def test_buy_accepts_an_approval_inside_the_cent(env):
    client, total = quoted(env)
    assert buy(env, client, round(total + 0.009, 6)) == 0


def test_buy_stops_when_a_requote_is_more_than_one_percent_above(env, capsys):
    client, total = quoted(env)
    client.scale = 1.0101
    assert buy(env, client, total) == pc.RC_STOPPED
    assert "re-quote" in capsys.readouterr().err
    assert env.lines(pc.PILOT_SESSION, "commit") == [] and client.calls["get_range"] == []


def test_buy_accepts_a_requote_within_one_percent(env):
    client, total = quoted(env)
    client.scale = 1.0099
    assert buy(env, client, total) == 0
    assert len(env.lines(pc.PILOT_SESSION, "settle")) == 8


def test_buy_refuses_when_acct3_holds_another_commit(env, capsys):
    client, total = quoted(env)
    env.seed({"ts": "2026-10-22T16:00:00+00:00", "event": "commit", "session_id": "stage-E.28-x",
              "account": "acct-3", "usd": 1.0, "request": GOOD.as_kwargs()})
    assert buy(env, client, total) == pc.RC_REFUSED
    assert "other than Part 1's volume request" in capsys.readouterr().err


def test_buy_refuses_a_pilot_commit_outside_this_plan(env, capsys):
    client, total = quoted(env)
    other = pc.request_for(pc.SERIES[0], date(2023, 12, 1)).as_kwargs()  # month 3: not in k=2
    env.seed({"ts": "2026-10-22T16:00:00+00:00", "event": "commit",
              "session_id": pc.PILOT_SESSION, "account": "acct-3", "usd": 1.0, "request": other})
    assert buy(env, client, total) == pc.RC_REFUSED


def test_session_cap_target_stops_the_buy(env, capsys):
    client, total = quoted(env)
    env.seed({"ts": "2026-10-22T16:00:00+00:00", "event": "settle",
              "session_id": pc.PILOT_SESSION, "account": "acct-3", "usd": 100.0,
              "request": pc.request_for(pc.SERIES[0], date(2023, 12, 1)).as_kwargs()})
    # a stray +100 settle delta in the pilot session, on a request outside this plan
    assert buy(env, client, total) == pc.RC_STOPPED
    assert "session cap" in capsys.readouterr().err
    assert client.calls["get_range"] == []


# ------------------------------------------------------------------ resume ----
def test_download_failure_keeps_the_commit_then_the_rerun_is_refused(env, capsys):
    client, total = quoted(env)
    client.fail_download = True
    assert buy(env, client, total) == pc.RC_STOPPED
    first = pc.plan(2)[0]
    target = pc.target_path(first, env.vendor)
    assert not target.exists() and not target.with_name(target.name + ".partial").exists()
    assert len(env.lines(pc.PILOT_SESSION, "commit")) == 1
    keys = list(env.keys)
    client.fail_download = False
    assert buy(env, client, total) == pc.RC_REFUSED
    err = capsys.readouterr().err
    assert "open commit" in err and "--retry-download --series Z1 --month 2024-02" in err
    assert env.keys == keys and len(client.calls["get_range"]) == 1


def test_a_file_with_an_open_commit_is_settled_without_a_new_download(env):
    client, total = quoted(env)
    first = pc.plan(2)[0]
    target = pc.target_path(first, env.vendor)
    write_dbn(target, first.params.as_kwargs())
    target.chmod(0o444)
    q = env.quote31()["requests"][0]
    env.seed({"ts": "2026-10-22T16:00:00+00:00", "event": "commit",
              "session_id": pc.PILOT_SESSION, "account": "acct-3", "usd": q["quoted_usd"],
              "request": q["request"], "quoted_usd": q["quoted_usd"],
              "billable_bytes": q["billable_bytes"]})
    assert buy(env, client, total) == 0
    assert first.params.as_kwargs() not in client.calls["get_range"]
    assert len(client.calls["get_range"]) == 7
    assert json.loads((env.runs / pc.record_name(first)).read_text())["quote31_usd"] == 30.0


def test_a_missing_purchase_record_is_rebuilt_from_the_ledger(env):
    client, total = quoted(env)
    assert buy(env, client, total) == 0
    first = pc.plan(2)[0]
    original = json.loads((env.runs / pc.record_name(first)).read_text())
    (env.runs / pc.record_name(first)).unlink()
    assert buy(env, Tripwire(), total) == 0
    rec = json.loads((env.runs / pc.record_name(first)).read_text())
    assert rec["rebuilt_from_ledger"] is True and len(rec["sha256"]) == 64
    assert rec["settled"]["delivered_record_bytes"] == \
        original["settled"]["delivered_record_bytes"] == 49 * 56  # from the settle note
    assert rec["session_id"] == pc.PILOT_SESSION and rec["retry_of_commit"] is None
    assert env.verify() == 0


@pytest.mark.parametrize("case", ["partial", "foreign", "overlap"])
def test_resume_refuses_stray_files_and_deletes_nothing(env, capsys, case):
    client, total = quoted(env)
    first = pc.plan(2)[0]
    target = pc.target_path(first, env.vendor)
    target.parent.mkdir(parents=True)
    if case == "partial":
        stray = target.with_name(target.name + ".partial")
    elif case == "foreign":
        stray = target
    else:
        stray = target.parent / "range=2024-02-01_2024-02-15.dbn.zst"
    stray.write_bytes(b"x")
    assert buy(env, client, total) == pc.RC_REFUSED
    assert stray.read_bytes() == b"x" and client.calls["get_range"] == []
    assert env.lines(pc.PILOT_SESSION, "commit") == []


def test_billing_more_than_three_percent_above_stops_the_remaining_buys(env, capsys):
    client = FakeClient(billable_scale=0.9)  # delivered = billable / 0.9: 11% above
    client, total = quoted(env, client=client)
    assert buy(env, client, total) == pc.RC_STOPPED
    assert "more than 3%" in capsys.readouterr().err
    settles = env.lines(pc.PILOT_SESSION, "settle")
    assert len(settles) == 1 and settles[0]["actual_usd"] > settles[0]["quoted_usd"]
    rec = json.loads((env.runs / pc.record_name(pc.plan(2)[0])).read_text())
    assert rec["settled"]["billed_above_quote"] is True
    assert len(client.calls["get_range"]) == 1


# ------------------------------------------------------------------ verify ----
def test_verify_passes_on_a_clean_purchase_and_writes_both_manifests(env, capsys):
    client, total = quoted(env)
    assert buy(env, client, total) == 0
    assert env.verify() == 0
    manifest = json.loads((env.runs / "manifest31.json").read_text())
    assert manifest["n_verified"] == 8 and manifest["missing"] == []
    f = manifest["files"][0]  # Z1 2024-02: 6 base, 21 weekdays x 2 snapshots, 1 tail
    assert f["records_by_rtype"] == {"160": 49} and f["records_by_instrument_id"] == {
        "100": 25, "101": 24}
    assert f["header"]["symbols"] == ["ZM.v.0", "ZM.v.1"] and f["header"]["version"] == 3
    assert f["delivered_record_bytes"] == 49 * 56
    assert manifest["files"][-1]["records_by_rtype"] == {"19": 9}
    names = {c["name"] for c in f["checks"]}
    assert {"record_bytes_match_purchase_record", "delivered_bytes_equal_quoted_billable",
            "z1_weekday_midnight_snapshot_per_mapped_instrument",
            "ts_event_max_reaches_last_day_session"} <= names
    z4 = {c["name"] for c in manifest["files"][-1]["checks"]}
    assert "ts_event_max_reaches_last_day_session" not in z4
    assert "z1_weekday_midnight_snapshot_per_mapped_instrument" not in z4
    for series in pc.SERIES:
        folder = env.vendor / "GLBX.MDP3" / series.schema / pc.series_dir_name(series)
        assert json.loads((folder / "manifest.json").read_text()) == manifest
        (folder / "manifest.json").unlink()
    assert env.verify("--no-side-manifests") == 0
    assert not any(env.vendor.rglob("manifest.json"))


def _buy_with(env, special_for):
    from data.quote_universe import request_key

    special = {request_key(i.params.as_kwargs()): flags for i, flags in special_for.items()}
    client, total = quoted(env, client=FakeClient(special=special))
    assert buy(env, client, total) == 0


def _failed(name):
    manifest = json.loads(Path(name).read_text())
    return {(f["series"], f["month"], c["name"]) for f in manifest["files"] for c in f["checks"]
            if not c["passed"]}


def test_verify_flags_a_record_at_the_request_end(env):
    jan = pc.plan(2)[1]  # Z1 2024-01
    _buy_with(env, {jan: {"late": True}})
    assert env.verify() == pc.RC_REFUSED
    assert _failed(env.runs / "manifest31.json") == {
        ("Z1", "2024-01", "no_record_at_or_after_request_end")}


def test_verify_flags_a_record_on_or_after_2024_03_01(env):
    feb = pc.plan(2)[2]  # Z2 2024-02
    _buy_with(env, {feb: {"after_cutoff": True}})
    assert env.verify() == pc.RC_REFUSED
    assert _failed(env.runs / "manifest31.json") == {
        ("Z2", "2024-02", "no_record_at_or_after_request_end"),
        ("Z2", "2024-02", vf.CUTOFF_CHECK)}


def test_verify_lists_a_record_before_the_start_as_a_quality_finding(env):
    _buy_with(env, {pc.plan(2)[6]: {"early": True}})
    assert env.verify() == pc.RC_QUALITY
    assert _failed(env.runs / "manifest31.json") == {
        ("Z4", "2024-02", "no_record_before_request_start")}


def test_verify_fails_on_a_sha256_mismatch_and_on_missing_purchases(env):
    client, total = quoted(env)
    assert buy(env, client, total) == 0
    first = pc.plan(2)[0]
    path = env.runs / pc.record_name(first)
    rec = json.loads(path.read_text())
    path.write_text(json.dumps({**rec, "sha256": "0" * 64}))
    assert env.verify() == pc.RC_REFUSED
    path.unlink()
    assert env.verify() == pc.RC_REFUSED  # Z1 2024-02 has no purchase record
    assert env.verify("--allow-missing") == 0


def test_verify_refuses_when_nothing_was_purchased(env, capsys):
    assert env.verify() == pc.RC_REFUSED
    assert "no purchase31" in capsys.readouterr().err


def test_verify_counts_weekday_midnights_and_the_last_day_session():
    feb, jan = pc.plan(2)[0].params, pc.plan(2)[1].params
    assert len(vf.weekday_midnights(pc.bound_ns(feb.start), pc.bound_ns(feb.end))) == 21
    assert len(vf.weekday_midnights(pc.bound_ns(jan.start), pc.bound_ns(jan.end))) == 23
    assert vf.weekday_midnights(pc.bound_ns("2024-01-06T00:00:00Z"),
                                pc.bound_ns("2024-01-08T00:00:00Z")) == []  # Sat, Sun
    last, end = vf.last_day_session_end_ns(pc.plan(2)[0])
    assert (last, pc.iso_ns(end)) == (date(2024, 2, 29), "2024-02-29T19:20:00.000000000Z")
    dec = pc.Planned(pc.SERIES[1], date(2023, 12, 1),
                     pc.request_for(pc.SERIES[1], date(2023, 12, 1)))
    last, end = vf.last_day_session_end_ns(dec)  # 12-30/31 are a weekend: Friday 12-29
    assert (last, pc.iso_ns(end)) == (date(2023, 12, 29), "2023-12-29T19:20:00.000000000Z")


def test_mapped_on_follows_start_inclusive_end_exclusive():
    hdr = {"mappings": {"ZM.v.0": [{"start_date": "2024-01-01", "end_date": "2024-01-10",
                                    "symbol": "7"},
                                   {"start_date": "2024-01-10", "end_date": "2024-02-01",
                                    "symbol": "8"}],
                        "ZM.v.1": [{"start_date": "2024-01-01", "end_date": "2024-02-01",
                                    "symbol": " "}]}}
    assert vf.mapped_on(hdr, date(2024, 1, 9)) == {"ZM.v.0": [7], "ZM.v.1": []}
    assert vf.mapped_on(hdr, date(2024, 1, 10)) == {"ZM.v.0": [8], "ZM.v.1": []}


def test_verify_flags_a_purchase_record_whose_delivered_bytes_differ(env):
    client, total = quoted(env)
    assert buy(env, client, total) == 0
    path = env.runs / pc.record_name(pc.plan(2)[3])  # Z2 2024-01
    rec = json.loads(path.read_text())
    rec["settled"]["delivered_record_bytes"] += 80
    path.write_text(json.dumps(rec))
    assert env.verify() == pc.RC_REFUSED
    assert _failed(env.runs / "manifest31.json") == {
        ("Z2", "2024-01", "record_bytes_match_purchase_record")}


@pytest.mark.parametrize("scale,code,severity", [(1.02, pc.RC_REFUSED, "hard"),
                                                 (0.99, pc.RC_QUALITY, "quality")])
def test_verify_compares_delivered_with_the_quoted_billable_bytes(env, scale, code, severity):
    client, total = quoted(env, client=FakeClient(billable_scale=scale))
    assert buy(env, client, total) == 0  # 0.99: delivered ~1% above, settled pro rata
    assert env.verify() == code
    manifest = json.loads((env.runs / "manifest31.json").read_text())
    bad = [c for f in manifest["files"] for c in f["checks"] if not c["passed"]]
    assert {c["name"] for c in bad} == {"delivered_bytes_equal_quoted_billable"}
    assert len(bad) == 8
    # Lead ruling 2026-10-23: below the billable bytes is hard for Z1-Z3 and quality for Z4.
    for f in manifest["files"]:
        sev = {c["severity"] for c in f["checks"] if not c["passed"]}
        want = "quality" if severity == "quality" or f["series"] == "Z4" else "hard"
        assert sev == {want}, (f["series"], sev)
    diffs = [c["detail"]["delivered_minus_billable"] for c in bad]
    assert all(d < 0 for d in diffs) if scale > 1 else all(d > 0 for d in diffs)


def test_verify_lists_a_missing_weekday_snapshot_as_a_quality_finding(env):
    _buy_with(env, {pc.plan(2)[0]: {"drop_snapshot": (date(2024, 2, 14), 101)}})
    assert env.verify() == pc.RC_QUALITY
    assert _failed(env.runs / "manifest31.json") == {
        ("Z1", "2024-02", "z1_weekday_midnight_snapshot_per_mapped_instrument")}
    manifest = json.loads((env.runs / "manifest31.json").read_text())
    check = next(c for c in manifest["files"][0]["checks"] if not c["passed"])
    assert check["detail"]["n_missing"] == 1 and check["detail"]["cells"] == 42
    assert check["detail"]["missing"][0]["midnight"].startswith("2024-02-14T00:00:00")
    assert check["detail"]["missing"][0]["instrument_id"] == 101


def test_verify_lists_a_file_that_stops_before_the_last_day_session(env):
    _buy_with(env, {pc.plan(2)[5]: {"short_tail": True}})  # Z3 2024-01
    assert env.verify() == pc.RC_QUALITY
    assert _failed(env.runs / "manifest31.json") == {
        ("Z3", "2024-01", "ts_event_max_reaches_last_day_session")}


# ------------------------------------------------------------------ ledger rules ----
def test_spend_target_and_other_commits_know_the_retry_session():
    plan_key = pc.plan(2)[0].key
    retry_commit = {"ts": "t", "event": "commit", "session_id": pc.RETRY_SESSION,
                    "account": "acct-3", "usd": 1.5, "request": pc.plan(2)[0].params.as_kwargs()}
    entries = [*VOLUME_LINES, retry_commit]
    assert pc.spend_target(entries)["target_usd"] == 122.27  # retry spend is not "outside"
    assert pc.other_commits(entries, {plan_key}) == []
    assert len(pc.other_commits(entries, set())) == 1  # a retry of a non-plan request counts
    assert pc.retry_cap_usd(0.72502180934 + 30.0) == pytest.approx(94.27497819066)


@pytest.mark.parametrize("label", ["2024-1", "24-01", "2024-13", "2024/01", "", None])
def test_parse_month_refuses_anything_but_yyyy_mm(label):
    with pytest.raises(pc.PilotRefused):
        pc.parse_month(label)


# ------------------------------------------------------------------ retry ----
def retry(env, client, series="Z1", month="2024-02"):
    return env.run(["--retry-download", "--series", series, "--month", month], client)


def _fail_first(env, cost=None):
    client, total = quoted(env, client=FakeClient(cost=cost))
    client.fail_download = True
    assert buy(env, client, total) == pc.RC_STOPPED
    client.fail_download = False
    return client, total


def test_retry_rebuys_one_failed_download_then_buy_resumes_and_verify_passes(env):
    client, total = _fail_first(env)
    failed = env.lines(pc.PILOT_SESSION, "commit")[0]
    assert retry(env, client) == 0
    lines = env.lines(pc.RETRY_SESSION)
    assert [x["event"] for x in lines] == ["quote", "commit", "settle"]
    assert lines[1]["usd"] == 30.0 and "RETRY of the failed commit" in lines[1]["note"]
    assert len(env.lines(pc.PILOT_SESSION, "commit")) == 1  # the failed commit stays open
    assert env.lines(pc.PILOT_SESSION, "settle") == []
    first = pc.plan(2)[0]
    target = pc.target_path(first, env.vendor)
    assert target.is_file() and not target.stat().st_mode & stat.S_IWUSR
    rec = json.loads((env.runs / pc.record_name(first)).read_text())
    assert rec["session_id"] == pc.RETRY_SESSION and rec["retry_of_commit"]["ts"] == failed["ts"]
    assert rec["position_after"]["session_cap_usd"] == pytest.approx(125.0 - 0.72502180934 - 30)
    assert any("cap $94.274978" in x for x in env.logs)
    assert buy(env, client, total) == 0  # the rest; the retried request is done
    assert len(env.lines(pc.PILOT_SESSION, "commit")) == 8
    assert len(env.lines(pc.PILOT_SESSION, "settle")) == 7
    assert client.calls["get_range"][1] == first.params.as_kwargs()  # the retry's download
    assert env.verify() == 0
    assert buy(env, Tripwire(), total) == 0  # idempotent: nothing called


def test_retry_record_is_rebuilt_from_the_retry_session(env):
    client, total = _fail_first(env)
    assert retry(env, client) == 0
    first = pc.plan(2)[0]
    (env.runs / pc.record_name(first)).unlink()
    assert buy(env, client, total) == 0
    rec = json.loads((env.runs / pc.record_name(first)).read_text())
    assert rec["rebuilt_from_ledger"] is True and rec["session_id"] == pc.RETRY_SESSION
    assert rec["settled"]["delivered_record_bytes"] == 49 * 56


def test_a_retried_file_with_an_open_retry_commit_is_settled_in_the_retry_session(env):
    client, total = _fail_first(env)
    first = pc.plan(2)[0]
    q = env.lines(pc.PILOT_SESSION, "commit")[0]
    target = write_dbn(pc.target_path(first, env.vendor), first.params.as_kwargs())
    target.chmod(0o444)
    env.seed({**q, "ts": "2026-10-22T17:00:00+00:00", "session_id": pc.RETRY_SESSION})
    assert buy(env, client, total) == 0
    settles = env.lines(pc.RETRY_SESSION, "settle")
    assert len(settles) == 1 and settles[0]["request"] == first.params.as_kwargs()
    assert len(env.lines(pc.PILOT_SESSION, "settle")) == 7
    assert first.params.as_kwargs() not in client.calls["get_range"][1:]


def test_a_failed_retry_stops_and_a_second_retry_is_refused(env, capsys):
    client, total = _fail_first(env)
    client.fail_download = True
    assert retry(env, client) == pc.RC_STOPPED
    assert "second failure" in capsys.readouterr().err
    assert len(env.lines(pc.RETRY_SESSION, "commit")) == 1
    client.fail_download = False
    keys = list(env.keys)
    assert retry(env, client) == pc.RC_REFUSED
    assert "already retried once" in capsys.readouterr().err
    assert buy(env, client, total) == pc.RC_REFUSED
    assert "second failure" in capsys.readouterr().err
    assert env.keys == keys and len(env.lines(pc.RETRY_SESSION, "commit")) == 1


RETRY_ARGS = {"bad_series": ("Z9", "2024-02"), "bad_month": ("Z1", "2024-2"),
              "late_month": ("Z1", "2024-03")}


@pytest.mark.parametrize("case", ["no_commit", "settled", "file", "partial", "overlap",
                                  "foreign_commit", *RETRY_ARGS])
def test_retry_is_refused_before_the_key(env, capsys, case):
    if case == "no_commit":
        quoted(env)
    elif case == "settled":
        client, total = quoted(env)
        assert buy(env, client, total) == 0
    else:
        _fail_first(env)
    target = pc.target_path(pc.plan(2)[0], env.vendor)
    if case == "file":
        target.write_bytes(b"x")
    elif case == "partial":
        target.with_name(target.name + ".partial").write_bytes(b"x")
    elif case == "overlap":
        (target.parent / "range=2024-02-01_2024-02-15.dbn.zst").write_bytes(b"x")
    elif case == "foreign_commit":
        env.seed({"ts": "2026-10-22T16:00:00+00:00", "event": "commit",
                  "session_id": "stage-E.28-x", "account": "acct-3", "usd": 1.0,
                  "request": GOOD.as_kwargs()})
    keys = list(env.keys)
    assert retry(env, Tripwire(), *RETRY_ARGS.get(case, ("Z1", "2024-02"))) == pc.RC_REFUSED
    assert "REFUSED before any vendor call" in capsys.readouterr().err
    assert env.keys == keys and env.lines(pc.RETRY_SESSION) == []


def test_retry_respects_the_retry_session_cap(env, capsys):
    client, _ = _fail_first(env, cost=lambda kw: 60.0 if kw["schema"] == "mbo" else 0.01)
    env.seed({"ts": "2026-10-22T16:30:00+00:00", "event": "settle",
              "session_id": pc.PILOT_SESSION, "account": "acct-3", "usd": 10.0,
              "request": pc.plan(2)[7].params.as_kwargs()})  # +10 USD counted on acct-3
    assert retry(env, client) == pc.RC_STOPPED  # cap 125 - 70.725 = 54.275 < 60
    assert "session cap" in capsys.readouterr().err
    assert [x["event"] for x in env.lines(pc.RETRY_SESSION)] == ["quote", "refused"]
    assert len(client.calls["get_range"]) == 1


def test_retry_stops_when_its_quote_is_more_than_one_percent_above_the_failed_commit(
        env, capsys):
    client, _ = _fail_first(env)
    client.scale = 1.0101
    assert retry(env, client) == pc.RC_STOPPED
    assert "retry quote" in capsys.readouterr().err
    assert env.lines(pc.RETRY_SESSION, "commit") == []


def test_series_and_month_belong_to_the_retry_only(env, capsys):
    assert env.run(["--plan", "--months", "2", "--series", "Z1"]) == pc.RC_REFUSED
    assert "--retry-download only" in capsys.readouterr().err


# ------------------------------------------------------------------ lock ----
def _hold_lock(env):
    import fcntl

    env.runs.mkdir(parents=True, exist_ok=True)
    fh = (env.runs / pc.LOCK_FILE).open("a+")
    fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    fh.seek(0)
    fh.truncate()
    fh.write("pid 1 --buy since test\n")
    fh.flush()
    return fh


@pytest.mark.parametrize("mode", ["buy", "retry"])
def test_a_held_lock_refuses_buy_and_retry_before_the_ledger_and_the_key(env, capsys, mode):
    client, total = _fail_first(env) if mode == "retry" else quoted(env)
    keys, n_lines = list(env.keys), len(env.lines())
    fh = _hold_lock(env)
    try:
        code = buy(env, client, total) if mode == "buy" else retry(env, client)
    finally:
        fh.close()
    assert code == pc.RC_REFUSED
    err = capsys.readouterr().err
    assert "held by another" in err and "pid 1 --buy since test" in err
    assert env.keys == keys and len(env.lines()) == n_lines
    assert (buy(env, client, total) if mode == "buy" else retry(env, client)) == 0
    assert (env.runs / pc.LOCK_FILE).read_text().startswith(f"pid {os.getpid()} --")


def _hdr(keys, symbol="7"):
    return {"mappings": {k: [{"start_date": "2024-01-31", "end_date": "2024-03-01",
                              "symbol": symbol}] for k in keys}}


def test_parent_mappings_are_keyed_by_child_raw_symbols():
    z4 = pc.SERIES_BY_NAME["Z4"]
    real = ["ZMH4", "ZM:BF K5-N5-Q5", "ZSX6-ZSN7", "ZL:CF N4Q4U4V4"]
    assert vf.mapping_refusals(_hdr(real), z4) == []
    assert vf.mapping_refusals(_hdr(["ZMH4", "ZSX6"]), z4) == [
        "no symbology mapping for ['ZL.FUT']"]
    assert vf.mapping_refusals(_hdr([*real, "ZCH4"]), z4) == [
        "mapping keys outside ['ZM', 'ZS', 'ZL']: ['ZCH4']"]
    assert vf.mapping_refusals(_hdr(real, symbol=" "), z4) == [
        "no symbology mapping for ['ZM.FUT', 'ZS.FUT', 'ZL.FUT']"]
    z1 = pc.SERIES_BY_NAME["Z1"]  # continuous: the requested symbols are the keys
    assert vf.mapping_refusals(_hdr(["ZM.v.0", "ZM.v.1"]), z1) == []
    assert vf.mapping_refusals(_hdr(["ZM.v.0", "ZMH4"]), z1) == [
        "no symbology mapping for ['ZM.v.1']"]


def test_an_old_ts_event_with_ts_recv_inside_the_request_is_only_counted(env):
    _buy_with(env, {pc.plan(2)[0]: {"early_event": True}, pc.plan(2)[6]: {"early_event": True}})
    assert env.verify() == 0
    manifest = json.loads((env.runs / "manifest31.json").read_text())
    for f in (manifest["files"][0], manifest["files"][6]):
        info = next(c for c in f["checks"] if c["name"] == "ts_event_before_request_start_counted")
        assert info["detail"]["records_ts_event_only_before_start"] == 1
        early = next(c for c in f["checks"] if c["name"] == "no_record_before_request_start")
        assert early["passed"] and early["detail"]["records_ts_recv_before_start"] == 0


def test_partial_parent_combos_are_listed_but_other_partials_are_findings():
    z4, z1 = _item_from(pc.SERIES_BY_NAME["Z4"]), _item_from(pc.SERIES_BY_NAME["Z1"])
    combos = ["ZM:BF K5-N5-Q5", "ZL:CF N4Q4U4V4"]
    got = vf.partial_checks({"partial": combos}, z4)
    assert [(c["name"], c["severity"], c["passed"]) for c in got] == [
        ("metadata_partial_empty", "quality", True),
        ("metadata_partial_parent_combos_listed", "info", True)]
    got = vf.partial_checks({"partial": [*combos, "ZMH4"]}, z4)
    assert not got[0]["passed"] and got[0]["detail"] == ["ZMH4"]
    got = vf.partial_checks({"partial": ["ZM.v.1"]}, z1)
    assert len(got) == 1 and not got[0]["passed"]
    assert vf.partial_checks({"partial": []}, z1)[0]["passed"]


def _item_from(series):
    return pc.Planned(series, date(2024, 2, 1), pc.request_for(series, date(2024, 2, 1)))
