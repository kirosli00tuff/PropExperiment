"""pilot_pull.py: every refusal (with a client that must never be built), quote, buy, resume,
and the span search. Fake clients only; tmp ledgers; no network."""

import json
import stat
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace

import pilot_common as pc
import pilot_pull as pp
import pytest
from b_helpers import S, write_dbn

from data.quote_universe import ForbiddenNamespace

DAY = "2023-11-14"
START = "2023-11-13T22:00:00Z"
ROOT = pc.PILOT_ROOT  # "QM": the frozen spec's one contract (RD-01); other roots are refused
BASE = ["--root", ROOT, "--first-trade-date", DAY]


class Tripwire:
    """A client stand-in: any use fails the test."""

    def __getattr__(self, name):
        raise AssertionError(f"client.{name} used")


class Env:
    def __init__(self, tmp: Path) -> None:
        self.tmp = tmp
        self.ledger = tmp / "ledger" / "spend.jsonl"
        self.access = tmp / "ACCESS.md"
        self.vendor = tmp / "vendor"
        self.vendor.mkdir()
        self.runs = tmp / "runs"
        self.keys: list[str] = []
        self.built: list[str] = []
        self.client = None
        self.logs: list[str] = []

    def key_loader(self, account=None):
        self.keys.append(account)
        return "fake-key-not-real"

    def tripwire_factory(self, key):
        self.built.append(key)
        return Tripwire()

    def run(self, argv, client=None, now=None):
        factory = self.tripwire_factory if client is None else self._factory(client)
        return pp.main(argv, key_loader=self.key_loader, client_factory=factory,
                       ledger_path=self.ledger, access_doc_path=self.access,
                       vendor_root=self.vendor, runs_dir=self.runs,
                       now=now or (lambda: datetime.now(UTC)), log=self.logs.append,
                       sleep=lambda s: None)

    def _factory(self, client):
        def build(key):
            self.built.append(key)
            return client
        return build

    def lines(self):
        if not self.ledger.is_file():
            return []
        return [json.loads(x) for x in self.ledger.read_text().splitlines() if x.strip()]

    def seed(self, **entry):
        self.ledger.parent.mkdir(parents=True, exist_ok=True)
        with self.ledger.open("a") as fh:
            fh.write(json.dumps(entry) + "\n")

    def target(self, start=START, end=pc.CUTOFF_BOUND):
        from data.pull_universe import target_path

        return target_path(pc.pilot_params(ROOT, start, end), self.vendor)


@pytest.fixture
def env(tmp_path):
    return Env(tmp_path)


def fake_client(usd=10.0, billable=160, fail_download=False, cost=None, root=ROOT):
    calls = {"get_range": [], "cost": [], "condition": [], "resolve": []}

    def get_cost(**kw):
        calls["cost"].append(kw)
        return cost(kw) if cost else usd

    def get_range(path, **kw):
        calls["get_range"].append(kw)
        if fail_download:
            Path(path).write_bytes(b"partial")
            raise RuntimeError("connection reset")
        write_dbn(Path(path), [{"t": 1_700_000_000 * S, "bid": 100, "ask": 101, "bsz": 1,
                                "asz": 1}] * 2, root=root, start_ns=1_699_000_000 * S,
                  end_ns=pc.bound_ns(pc.CUTOFF_BOUND),
                  intervals=[(date(2023, 11, 1), date(2024, 3, 1), "111")])

    def resolve(**kw):
        calls["resolve"].append(kw)
        return {"result": {pc.symbol_for(root): [{"d0": "2019-05-06", "d1": "2024-03-01",
                                                  "s": "111"}]}}

    client = SimpleNamespace(
        metadata=SimpleNamespace(get_cost=get_cost, get_billable_size=lambda **kw: billable,
                                 get_dataset_condition=lambda **kw: calls["condition"].append(kw)
                                 or [{"date": "2023-11-14", "condition": "available"}]),
        timeseries=SimpleNamespace(get_range=get_range),
        symbology=SimpleNamespace(resolve=resolve), batch=None)
    return client, calls


# ------------------------------------------------------------------ refusals ----
REFUSED = [
    (["--account", "acct-2"], "acct-3"),
    (["--account", "acct-1"], "acct-3"),
    (["--schema", "mbp-10"], "schema"),
    (["--schema", "tbbo"], "schema"),
    (["--dataset", "XNAS.ITCH"], "dataset"),
    (["--symbol", "NQ.v.0"], "symbols"),
    (["--symbol", "ES.c.0"], "symbols"),
    (["--stype-in", "raw_symbol"], "stype_in"),
    (["--end", "2024-03-02"], "after 2024-02-29T22:00:00Z"),
    (["--end", "2024-03-01"], "after 2024-02-29T22:00:00Z"),          # RS-01: the old bound
    (["--end", "2024-02-29T22:00:01Z"], "after 2024-02-29T22:00:00Z"),
    (["--end", "2024-02-29T23:00:00Z"], "after 2024-02-29T22:00:00Z"),
    (["--session-id", "stage-E.17-ext2010h"], "session id"),
]


@pytest.mark.parametrize("mode", ["--plan", "--quote", "--buy"])
@pytest.mark.parametrize(("extra", "reason"), REFUSED)
def test_refusals_never_touch_key_or_client(env, capsys, mode, extra, reason):
    rc = env.run([mode, *BASE, "--approved-usd", "50", *extra])
    assert rc == pc.RC_REFUSED
    assert reason in capsys.readouterr().err
    assert env.keys == [] and env.built == [] and env.lines() == []


@pytest.mark.parametrize(("window", "reason"), [
    (["--start", "2025-05-01", "--end", "2025-05-02"], "research window"),
    (["--start", "2024-04-01", "--end", "2024-04-02"], "embargo and holdout 2"),
    (["--start", "2024-02-20", "--end", "2024-03-05"], "embargo and holdout 2"),
    (["--start", "2026-07-01", "--end", "2026-07-02"], "holdout 1"),
    (["--start", "2010-01-04", "--end", "2010-02-01"], "first date"),
    (["--start", "2023-11-1", "--end", pc.CUTOFF_BOUND], "request bound"),
    (["--start", "2023-11-01T00:00:00+00:00", "--end", pc.CUTOFF_BOUND], "request bound"),
    (["--start", "2024-02-01", "--end", "2024-01-01"], "inverted"),
])
def test_window_refusals(env, capsys, window, reason):
    rc = env.run(["--quote", "--root", ROOT, *window])
    assert rc == pc.RC_REFUSED
    assert reason in capsys.readouterr().err
    assert env.keys == [] and env.built == []


def test_unknown_root_is_refused(env, capsys):
    assert env.run(["--quote", "--root", "XYZ", "--first-trade-date", DAY]) == pc.RC_REFUSED
    assert "no CME group calendar" in capsys.readouterr().err and env.built == []


def test_research_window_guard_names_each_window():
    params = pc.pilot_params(ROOT, "2024-02-01", "2026-07-01")
    reasons = " | ".join(pc.request_refusals(params, ROOT))
    for word in ("after 2024-02-29T22:00:00Z", "embargo and holdout 2", "research window",
                 "holdout 1"):
        assert word in reasons


def test_span_search_refusals(env, capsys):
    assert env.run(["--span-search", "--root", ROOT, "--target-usd", "50", "--schema",
                    "mbp-10"]) == pc.RC_REFUSED
    assert env.run(["--span-search", "--root", ROOT, "--target-usd", "50", "--account",
                    "acct-2"]) == pc.RC_REFUSED
    assert env.run(["--span-search", "--root", ROOT, "--target-usd", "500"]) == pc.RC_REFUSED
    # RS-08: the target may not exceed B - max(3.00, 0.03 B): 121.25 at B = 125.00
    assert env.run(["--span-search", "--root", ROOT, "--target-usd", "121.26"]) == pc.RC_REFUSED
    assert env.run(["--span-search", "--root", ROOT, "--balance-usd", "50", "--target-usd",
                    "47.01"]) == pc.RC_REFUSED
    assert env.run(["--span-search", "--root", ROOT, "--balance-usd", "126"]) == pc.RC_REFUSED
    assert env.run(["--span-search", "--root", ROOT, "--balance-usd", "0"]) == pc.RC_REFUSED
    assert env.run(["--span-search", "--root", ROOT, "--end", "2024-03-01"]) == pc.RC_REFUSED
    assert env.keys == [] and env.built == []


# ------------------------------------------------------------------ plan and quote ----
def test_plan_makes_no_call(env, capsys):
    rc = env.run(["--plan", *BASE])
    assert rc == pc.RC_OK and env.keys == [] and env.built == []
    plan = json.loads(capsys.readouterr().out)
    assert plan["request"] == {"dataset": "GLBX.MDP3", "symbols": ["QM.v.0"],
                               "schema": "mbp-1", "stype_in": "continuous", "start": START,
                               "end": "2024-02-29T22:00:00Z"}
    assert plan["target"].endswith("GLBX.MDP3/mbp-1/QM_v_0/"
                                   "range=2023-11-13T220000Z_2024-02-29T220000Z.dbn.zst")
    assert plan["covers_minimum_span"] and plan["spend_target_usd"] == 121.25
    assert plan["first_whole_trade_date"] == DAY and plan["start_aligned_to_whole_trade_date"]
    assert plan["position"]["account"] == "acct-3" and plan["vendor_calls"] == 0


def test_quote_ledgers_one_priced_line_on_acct3_with_billables_guarded(env):
    client, calls = fake_client(usd=12.5)
    rc = env.run(["--quote", *BASE, "--out", str(env.tmp / "q.json")], client=client)
    assert rc == pc.RC_OK
    (line,) = env.lines()
    assert (line["event"], line["account"], line["session_id"]) == ("quote", "acct-3",
                                                                    pc.QUOTE_SESSION_ID)
    assert line["usd"] == 0.0 and line["quoted_usd"] == 12.5
    assert line["request"]["schema"] == "mbp-1" and line["request"]["start"] == START
    assert isinstance(client.timeseries, ForbiddenNamespace)
    assert isinstance(client.batch, ForbiddenNamespace)
    assert calls["get_range"] == [] and len(calls["cost"]) == 1
    assert json.loads((env.tmp / "q.json").read_text())["quoted_usd"] == 12.5
    assert env.keys == ["acct-3"]


# ------------------------------------------------------------------ buy ----
def quote_then(env, usd=10.0, **kw):
    client, calls = fake_client(usd=usd, **kw)
    assert env.run(["--quote", *BASE], client=client) == pc.RC_OK
    return client, calls


def test_buy_happy_path_then_idempotent(env):
    quote_then(env)
    client, calls = fake_client()
    rc = env.run(["--buy", *BASE, "--approved-usd", "10"], client=client)
    assert rc == pc.RC_OK
    events = [e["event"] for e in env.lines()]
    assert events == ["quote", "commit", "settle"]
    commit, settle = env.lines()[1:]
    assert commit["usd"] == 10.0 and commit["account"] == "acct-3"
    assert settle["usd"] == 0.0 and settle["actual_usd"] == 10.0  # 160 bytes delivered = quoted
    target = env.target()
    assert target.is_file() and not (target.parent / (target.name + ".partial")).exists()
    assert not target.stat().st_mode & stat.S_IWUSR
    assert calls["get_range"] == [{"dataset": "GLBX.MDP3", "symbols": ["QM.v.0"],
                                   "schema": "mbp-1", "stype_in": "continuous",
                                   "start": START, "end": "2024-02-29T22:00:00Z"}]
    record = json.loads(next(env.runs.glob("purchase_QM_*.json")).read_text())
    assert record["billing"]["settled_usd"] == 10.0 and len(record["sha256"]) == 64
    assert list(env.runs.glob("condition_*.json"))
    assert isinstance(client.batch, ForbiddenNamespace)
    built = len(env.built)
    assert env.run(["--buy", *BASE, "--approved-usd", "10"]) == pc.RC_OK  # tripwire client
    assert len(env.built) == built and len(env.lines()) == 3


def test_buy_without_a_quote_is_refused(env, capsys):
    assert env.run(["--buy", *BASE, "--approved-usd", "10"]) == pc.RC_REFUSED
    assert "run --quote first" in capsys.readouterr().err and env.built == []


def test_buy_refuses_quote_older_than_the_sessions_fresh_quote(env, capsys):
    quote_then(env)
    other, _ = fake_client()
    assert env.run(["--quote", "--root", ROOT, "--first-trade-date", "2023-12-01"],
                   client=other) == pc.RC_OK
    built = len(env.built)
    assert env.run(["--buy", *BASE, "--approved-usd", "10"]) == pc.RC_REFUSED
    assert "newest quote is for another request" in capsys.readouterr().err
    assert len(env.built) == built


def test_buy_refuses_stale_quote(env, capsys):
    quote_then(env)
    later = lambda: datetime.now(UTC) + timedelta(hours=25)  # noqa: E731
    assert env.run(["--buy", *BASE, "--approved-usd", "10"], now=later) == pc.RC_REFUSED
    assert "quote again" in capsys.readouterr().err


def test_buy_refuses_quote_above_approved(env, capsys):
    quote_then(env, usd=30.0)
    assert env.run(["--buy", *BASE, "--approved-usd", "29.99"]) == pc.RC_REFUSED
    assert "--approved-usd" in capsys.readouterr().err


def test_buy_refuses_failed_newest_quote(env, capsys):
    client, _ = fake_client(cost=lambda kw: (_ for _ in ()).throw(RuntimeError("down")))
    assert env.run(["--quote", *BASE], client=client) == pc.RC_STOPPED
    assert env.run(["--buy", *BASE, "--approved-usd", "10"]) == pc.RC_REFUSED
    assert "newest quote failed" in capsys.readouterr().err


def test_buy_refused_by_acct3_cap(env, capsys):
    # One purchase only (RD-01), so the account cap can bind only on the same request: an
    # orphan commit of THIS request (another session, no settle, no file) of 100.00 plus a
    # retry quoted at 30.00 exceeds acct-3's 125.00 (the session cap alone would allow it)
    request = pc.pilot_params(ROOT, START).as_kwargs()
    env.seed(ts=datetime.now(UTC).isoformat(), event="commit", session_id="stage-E.28-old",
             account="acct-3", usd=100.0, request=request)
    quote_then(env, usd=30.0)
    built = len(env.built)
    assert env.run(["--buy", *BASE, "--approved-usd", "30", "--retry-download"]) == \
        pc.RC_REFUSED
    assert "account cap acct-3" in capsys.readouterr().err
    assert len(env.built) == built
    assert env.lines()[-1]["event"] == "refused" and env.access.is_file()
    assert not env.target().exists()


@pytest.mark.parametrize("earlier", [
    {"session_id": "stage-E.28-old", "request": {"dataset": "GLBX.MDP3"}},      # no full request
    {"session_id": pc.QUOTE_SESSION_ID,                                            # QM, other span
     "request": pc.pilot_params(pc.PILOT_ROOT, "2023-11-14T22:00:00Z").as_kwargs()},
    {"session_id": pc.QUOTE_SESSION_ID,                                            # another root
     "request": {**pc.pilot_params(pc.PILOT_ROOT, START).as_kwargs(), "symbols": ["QG.v.0"]}},
])
def test_buy_refused_when_acct3_already_holds_another_purchase(env, capsys, earlier):
    # RD-01: one purchase only on acct-3; any commit of another request blocks the buy before
    # any vendor call, and nothing is ledgered by the refusal
    env.seed(ts=datetime.now(UTC).isoformat(), event="commit", account="acct-3", usd=5.0,
             **earlier)
    quote_then(env, usd=10.0)
    n_lines, built = len(env.lines()), len(env.built)
    client, calls = fake_client()
    assert env.run(["--buy", *BASE, "--approved-usd", "10"], client=client) == pc.RC_REFUSED
    err = capsys.readouterr().err
    assert "one purchase only" in err and "RD-01" in err
    assert calls["get_range"] == [] and len(env.built) == built
    assert len(env.lines()) == n_lines and not env.target().exists()


def test_second_buy_of_another_qm_span_after_a_settled_purchase_is_refused(env, capsys):
    quote_then(env)
    client, _ = fake_client()
    assert env.run(["--buy", *BASE, "--approved-usd", "10"], client=client) == pc.RC_OK
    other = ["--root", ROOT, "--first-trade-date", "2023-11-15"]
    client, _ = fake_client()
    assert env.run(["--quote", *other], client=client) == pc.RC_OK  # a quote is free
    client, calls = fake_client()
    assert env.run(["--buy", *other, "--approved-usd", "10"], client=client) == pc.RC_REFUSED
    assert "one purchase only" in capsys.readouterr().err and calls["get_range"] == []
    assert [e["event"] for e in env.lines()].count("commit") == 1
    # the first purchase itself still resumes as "already bought" (same request)
    assert env.run(["--buy", *BASE, "--approved-usd", "10"]) == pc.RC_OK


@pytest.mark.parametrize("mode", ["--plan", "--quote", "--buy", "--span-search"])
@pytest.mark.parametrize("root", ["QG", "CL", "ES"])
def test_every_mode_refuses_a_root_other_than_qm(env, capsys, mode, root):
    # RD-01: the frozen spec (section 0) fixes the contract at QM
    when = (["--first-listed", "2019-05-06"] if mode == "--span-search"
            else ["--first-trade-date", "2024-01-12"])
    rc = env.run([mode, "--root", root, *when, "--approved-usd", "10"])
    assert rc == pc.RC_REFUSED
    err = capsys.readouterr().err
    assert f"root '{root}' refused" in err and "QM" in err
    assert env.keys == [] and env.built == [] and env.lines() == []


@pytest.mark.parametrize("mode", ["--plan", "--quote", "--buy"])
@pytest.mark.parametrize("end", ["2023-12-01", "2024-02-29", "2024-02-29T21:59:59Z",
                                 "2024-02-01T00:00:00Z"])
def test_every_mode_refuses_an_end_before_the_cutoff(env, capsys, mode, end):
    # RD-02: the end is exactly 2024-02-29T22:00:00Z, so a bought span always holds the whole
    # minimum span [2024-01-12, 2024-02-29T22:00Z) once the start passes RS-07
    rc = env.run([mode, "--root", ROOT, "--first-trade-date", "2023-11-14", "--end", end,
                  "--approved-usd", "10"])
    assert rc == pc.RC_REFUSED
    err = capsys.readouterr().err
    assert f"end {end} refused" in err and "RD-02" in err
    assert env.keys == [] and env.built == [] and env.lines() == []


def test_pilot_refusals_pin_root_and_end_but_request_refusals_stay_generic():
    start = pc.start_bound(date(2024, 1, 12))
    assert pc.pilot_refusals(pc.pilot_params("QM", start), "QM") == []
    assert pc.request_refusals(pc.pilot_params("ES", start), "ES") == []
    assert any("RD-01" in r for r in pc.pilot_refusals(pc.pilot_params("ES", start), "ES"))
    early = pc.pilot_params("QM", start, "2024-02-28T22:00:00Z")
    assert pc.request_refusals(early, "QM") == []
    assert any("RD-02" in r for r in pc.pilot_refusals(early, "QM"))


def test_buy_refused_by_session_cap(env, capsys):
    quote_then(env, usd=30.0)
    assert env.run(["--buy", *BASE, "--approved-usd", "30", "--session-cap-usd", "20"]) \
        == pc.RC_REFUSED
    assert "session cap" in capsys.readouterr().err


def test_buy_session_cap_above_account_cap_is_refused(env, capsys):
    quote_then(env)
    assert env.run(["--buy", *BASE, "--approved-usd", "10", "--session-cap-usd", "126"]) \
        == pc.RC_REFUSED


def test_download_failure_stops_keeps_commit_and_leaves_no_file(env, capsys):
    quote_then(env)
    client, _ = fake_client(fail_download=True)
    assert env.run(["--buy", *BASE, "--approved-usd", "10"], client=client) == pc.RC_STOPPED
    target = env.target()
    assert not target.exists() and not (target.parent / (target.name + ".partial")).exists()
    assert [e["event"] for e in env.lines()] == ["quote", "commit"]
    # rerun: the open commit with no file is refused unless --retry-download
    assert env.run(["--buy", *BASE, "--approved-usd", "10"]) == pc.RC_REFUSED
    assert "--retry-download" in capsys.readouterr().err
    # --retry-download still needs a quote newer than that commit
    assert env.run(["--buy", *BASE, "--approved-usd", "10", "--retry-download"]) == \
        pc.RC_REFUSED
    assert "commit follows" in capsys.readouterr().err
    quote_then(env)
    good, calls = fake_client()
    assert env.run(["--buy", *BASE, "--approved-usd", "10", "--retry-download"],
                   client=good) == pc.RC_OK
    assert [e["event"] for e in env.lines()] == ["quote", "commit", "quote", "commit",
                                                 "settle"]
    n = len(env.lines())  # idempotent after the retry: the orphan commit is not settled again
    assert env.run(["--buy", *BASE, "--approved-usd", "10"]) == pc.RC_OK
    assert len(env.lines()) == n


def test_resume_settles_a_completed_download_without_downloading(env):
    quote_then(env)
    lines = env.lines()
    env.seed(**{**lines[0], "event": "commit", "usd": 10.0, "ts": datetime.now(UTC).isoformat()})
    target = env.target()
    _, calls = fake_client()
    write_dbn(target, [{"t": 1_700_000_000 * S, "bid": 100, "ask": 101, "bsz": 1, "asz": 1}] * 2,
              root=ROOT, start_ns=1_699_000_000 * S, end_ns=pc.bound_ns(pc.CUTOFF_BOUND),
              intervals=[(date(2023, 11, 1), date(2024, 3, 1), "111")])
    built = len(env.built)
    assert env.run(["--buy", *BASE, "--approved-usd", "10"]) == pc.RC_OK
    assert len(env.built) == built  # no client: nothing downloaded again
    assert [e["event"] for e in env.lines()] == ["quote", "commit", "settle"]


def test_foreign_file_at_target_is_refused(env, capsys):
    quote_then(env)
    target = env.target()
    target.parent.mkdir(parents=True)
    target.write_bytes(b"not ours")
    assert env.run(["--buy", *BASE, "--approved-usd", "10"]) == pc.RC_REFUSED
    assert "foreign or unfinished" in capsys.readouterr().err
    assert target.read_bytes() == b"not ours"


def test_overlapping_file_in_folder_is_refused(env, capsys):
    quote_then(env)
    other = env.target("2023-12-01", "2024-01-01")
    other.parent.mkdir(parents=True)
    other.write_bytes(b"x")
    assert env.run(["--buy", *BASE, "--approved-usd", "10"]) == pc.RC_REFUSED
    assert "overlap" in capsys.readouterr().err


def test_research_window_file_in_folder_does_not_block(env):
    quote_then(env)
    research = env.target("2025-05-13", "2025-05-14")
    research.parent.mkdir(parents=True)
    research.write_bytes(b"x")
    client, _ = fake_client()
    assert env.run(["--buy", *BASE, "--approved-usd", "10"], client=client) == pc.RC_OK
    assert research.read_bytes() == b"x"


# ------------------------------------------------------------------ span search ----
def test_span_search_small_hand_example():
    days = [date(2024, 2, 1) + timedelta(days=k) for k in range(10)]
    cost = {d: (10 - k) * 3.0 for k, d in enumerate(days)}  # 30, 27, ..., 3
    calls = []

    def quote(d):
        calls.append(d)
        return cost[d]

    # target 12: (10 - k) x 3 <= 12 -> k >= 6 -> days[6]
    out = pp.span_search(days, quote, 12.0)
    assert out["first_trade_date"] == days[6].isoformat() and out["cost_usd"] == 12.0
    assert out["next_earlier"] == {"first_trade_date": days[5].isoformat(), "usd": 15.0}
    assert out["trade_dates_in_span"] == 4 and out["costs_monotone"]
    assert len(calls) <= 2 + 4 and len(set(calls)) == len(calls)


def test_span_search_bounds_and_infeasible():
    days = [date(2024, 2, 1) + timedelta(days=k) for k in range(10)]
    cost = {d: (10 - k) * 3.0 for k, d in enumerate(days)}
    wide = pp.span_search(days, cost.get, 1000.0)
    assert wide["first_trade_date"] == days[0].isoformat() and wide["limited_by_lower_bound"]
    assert len(wide["quotes"]) == 2
    none = pp.span_search(days, cost.get, 2.0)
    assert not none["feasible"]
    bumpy = {**cost, days[4]: 2.0}  # a later start (days[9], 3.0) costs more than days[4]
    out = pp.span_search(days, bumpy.get, 12.0)
    assert out["first_trade_date"] == days[4].isoformat() and not out["costs_monotone"]


def _per_day_cost(cal, rate=1.25):
    def cost(kw):
        start = pc.bound_ns(kw["start"])
        n = sum(1 for d in pp.span_candidates(cal, date(2019, 5, 1))
                if pc.bound_ns(pc.start_bound(d)) >= start)
        return rate * n
    return cost


def test_span_search_cli_finds_the_hand_computed_start_and_never_buys(env, capsys):
    cal = pc.calendar_for(ROOT)
    client, calls = fake_client(cost=_per_day_cost(cal))
    rc = env.run(["--span-search", "--root", ROOT, "--target-usd", "50", "--first-listed",
                  "2023-06-01", "--out", str(env.tmp / "span.json")], client=client)
    assert rc == pc.RC_OK
    days = pp.span_candidates(cal, date(2023, 6, 2))  # trade dates to 2024-02-29
    # 50 / 1.25 = 40 trade dates to 02-29 (linear scan, not the bisection): 35 from the
    # minimum span's 01-12 (Jan 12-31: 14; Feb: 21) plus 01-11, 10, 09, 08, 05 -> 2024-01-05
    expected = next(d for d in days if 1.25 * sum(1 for x in days if x >= d) <= 50)
    assert expected == date(2024, 1, 5)
    out = json.loads((env.tmp / "span.json").read_text())
    assert out["first_trade_date"] == expected.isoformat() and out["cost_usd"] == 50.0
    assert out["trade_dates_in_span"] == 40 and out["end"] == pc.CUTOFF_BOUND
    assert out["start"] == pc.start_bound(expected) and not out["bought"]
    assert calls["get_range"] == [] and isinstance(client.timeseries, ForbiddenNamespace)
    lines = env.lines()
    assert len(lines) == len(out["quotes"]) == len(calls["cost"])
    assert {(e["event"], e["account"], e["session_id"]) for e in lines} == \
        {("quote", "acct-3", pc.SPAN_SESSION_ID)}


def test_span_search_never_starts_before_first_listed(env):
    cal = pc.calendar_for(ROOT)
    client, calls = fake_client(cost=_per_day_cost(cal))
    rc = env.run(["--span-search", "--root", ROOT, "--first-listed", "2023-12-20", "--out",
                  str(env.tmp / "s.json")], client=client)  # default TARGET 121.25
    assert rc == pc.RC_OK
    out = json.loads((env.tmp / "s.json").read_text())
    # 2023-12-20's start bound (12-19 16:00 CT) precedes the listing: the first whole trade
    # date is 2023-12-21; trade dates to 02-29: Dec 21, 22, 26-29 (6) + Jan 22 + Feb 21 = 49,
    # costing 61.25 <= 121.25
    assert out["first_trade_date"] == "2023-12-21" and out["limited_by_lower_bound"]
    assert out["trade_dates_in_span"] == 49 and out["cost_usd"] == pytest.approx(61.25)
    assert out["target_usd"] == 121.25 and out["balance_usd"] == 125.0


def test_span_search_never_proposes_a_start_after_the_minimum_span(env, capsys):
    cal = pc.calendar_for(ROOT)
    client, calls = fake_client(cost=_per_day_cost(cal))
    # TARGET 30 < the minimum span's 35 trade dates (2024-01-12..02-29 on the QM calendar)
    # x 1.25 = 43.75: buy nothing, one quote
    rc = env.run(["--span-search", "--root", ROOT, "--target-usd", "30", "--first-listed",
                  "2023-06-01", "--out", str(env.tmp / "s.json")], client=client)
    assert rc == pc.RC_STOPPED
    out = json.loads((env.tmp / "s.json").read_text())
    assert not out["feasible"] and "buy nothing" in out["reason"]
    assert [q["first_trade_date"] for q in out["quotes"]] == ["2024-01-12"]
    assert out["quotes"][0]["usd"] == pytest.approx(43.75)
    # listed after 2024-01-12: the minimum span cannot exist
    rc = env.run(["--span-search", "--root", ROOT, "--first-listed", "2024-02-01"],
                 client=client)
    assert rc == pc.RC_STOPPED and "minimum span cannot be bought" in capsys.readouterr().err
    assert calls["get_range"] == []


def test_span_search_uses_free_symbology_when_first_listed_not_given(env):
    cal = pc.calendar_for(ROOT)
    client, calls = fake_client(cost=_per_day_cost(cal))
    rc = env.run(["--span-search", "--root", ROOT, "--target-usd", "50", "--out",
                  str(env.tmp / "s.json")], client=client)
    assert rc == pc.RC_OK and len(calls["resolve"]) == 1
    assert json.loads((env.tmp / "s.json").read_text())["first_listed"] == "2019-05-06"


def test_span_search_stops_when_a_quote_fails(env, capsys):
    client, _ = fake_client(cost=lambda kw: (_ for _ in ()).throw(RuntimeError("down")))
    rc = env.run(["--span-search", "--root", ROOT, "--target-usd", "30", "--first-listed",
                  "2023-06-01"], client=client)
    assert rc == pc.RC_STOPPED and "nothing was bought" in capsys.readouterr().err


# ------------------------------------------------------------------ RS-07, RS-08 ----
@pytest.mark.parametrize("when", [["--first-trade-date", "2024-01-15"],  # next trade date
                                  ["--first-trade-date", "2024-01-18"],  # the QG bound
                                  ["--first-trade-date", "2024-02-26"],
                                  ["--start", "2024-01-12"],             # 00:00Z: 01-12 partial
                                  ["--start", "2024-01-11T22:00:01Z"]])
def test_buy_refuses_a_start_later_than_the_minimum_span(env, capsys, when):
    rc = env.run(["--buy", "--root", ROOT, *when, "--approved-usd", "10"])
    assert rc == pc.RC_REFUSED and "minimum span" in capsys.readouterr().err
    assert env.keys == [] and env.built == [] and env.lines() == []


def test_minimum_span_start_itself_passes_the_span_check(env, capsys):
    # frozen spec section 6 (RS-07, corrected for QM): first trade date no later than 2024-01-12
    assert date(2024, 1, 12) == pc.MIN_SPAN_FIRST_TRADE_DATE
    assert pc.start_bound(date(2024, 1, 12)) == "2024-01-11T22:00:00Z"
    for when in (["--first-trade-date", "2024-01-12"], ["--start", "2024-01-11T22:00:00Z"],
                 ["--first-trade-date", "2024-01-11"]):
        rc = env.run(["--buy", "--root", ROOT, *when, "--approved-usd", "10"])
        assert rc == pc.RC_REFUSED and "run --quote first" in capsys.readouterr().err


def test_quote_of_a_short_span_warns_that_the_buy_will_refuse(env):
    client, _ = fake_client()
    assert env.run(["--quote", "--root", ROOT, "--first-trade-date", "2024-02-01"],
                   client=client) == pc.RC_OK
    assert any("WARNING: --buy will refuse" in m for m in env.logs)


@pytest.mark.parametrize(("balance", "target"), [(125.0, 121.25), (100.0, 97.0), (50.0, 47.0),
                                                 (100.01, 97.0), (200.0, 194.0)])
def test_margin_target_by_hand(balance, target):
    # B - max(3.00, 0.03 B), down to the cent: 125 - 3.75; 100 - 3.00; 50 - 3.00;
    # 100.01 - 3.0003 = 97.0097 -> 97.00; 200 - 6.00
    assert pc.margin_target(balance) == target


def test_buy_refuses_a_quote_above_the_spend_target(env, capsys):
    quote_then(env, usd=122.0)
    assert env.run(["--buy", *BASE, "--approved-usd", "122"]) == pc.RC_REFUSED
    assert "spend target $121.25" in capsys.readouterr().err
    quote_then(env, usd=98.0)
    assert env.run(["--buy", *BASE, "--approved-usd", "98", "--balance-usd", "100"]) == \
        pc.RC_REFUSED
    assert "spend target $97.00" in capsys.readouterr().err
    assert env.built.count("fake-key-not-real") == 2  # only the two --quote runs built one


def test_buy_is_approved_for_exactly_the_fresh_quote(env, capsys):
    quote_then(env, usd=10.0)
    assert env.run(["--buy", *BASE, "--approved-usd", "10.5"]) == pc.RC_REFUSED
    assert "exactly that quote" in capsys.readouterr().err
    client, _ = fake_client()
    assert env.run(["--buy", *BASE, "--approved-usd", "10.009"], client=client) == pc.RC_OK
