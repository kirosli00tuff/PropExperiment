"""DeltaReviewer adversarial tests (Stage E.28b, step S2). Fake clients, tmp ledgers, no network.

Each test named DOCUMENTS_* asserts the code's CURRENT behaviour; a pass confirms the hole the
docstring names (R_delta.md finding). Each test named CHECK_* asserts a property the frozen spec
needs; a pass means the property holds. Nothing here edits B_pilot/.

Run from the repo root:
  nice -n 10 uv run pytest -q reports/stage_e28_briefs/work/REV_delta/test_rev_delta_adversarial.py \
      -p no:cacheprovider -rf
"""

import json
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
PILOT = HERE.parent / "B_pilot"
for entry in (str(PILOT.parents[3]), str(PILOT), str(PILOT / "tests")):
    if entry not in sys.path:
        sys.path.insert(0, entry)

import pilot_common as pc  # noqa: E402
import pytest  # noqa: E402
import verify  # noqa: E402
from b_helpers import pilot_file, session_tape, write_dbn  # noqa: E402
from test_b_pull import Env, fake_client  # noqa: E402

QM_MIN = "2024-01-12"


@pytest.fixture
def env(tmp_path):
    return Env(tmp_path)


def _quote(env, argv, usd=10.0):
    client, _ = fake_client(usd=usd)
    assert env.run(["--quote", *argv], client=client) == pc.RC_OK


# ------------------------------------------------------------------ RD: second contract ----
@pytest.mark.parametrize("root", ["QG", "CL", "ES"])
def test_DOCUMENTS_buy_of_a_root_other_than_QM_is_not_refused(env, root):
    """RD finding: the frozen spec fixes ROOT = QM (symbol QM.v.0), but pilot_pull.py accepts any
    root with a group calendar. A --buy --root QG (the v1 top pair) passes every refusal and
    downloads QG.v.0 mbp-1, using QM's minimum-span constant."""
    argv = ["--root", root, "--first-trade-date", QM_MIN]
    _quote(env, argv)
    client, calls = fake_client(usd=10.0)
    rc = env.run(["--buy", *argv, "--approved-usd", "10"], client=client)
    assert rc == pc.RC_OK
    assert calls["get_range"][0]["symbols"] == [f"{root}.v.0"]


def test_DOCUMENTS_a_second_contract_can_be_bought_after_the_first(env):
    """RD finding: after one settled purchase on acct-3, a second purchase of another root is
    accepted while acct-3's headroom allows it (only the 125.00 cap stands in the way)."""
    first = ["--root", "QM", "--first-trade-date", QM_MIN]
    _quote(env, first)
    client, _ = fake_client(usd=10.0)
    assert env.run(["--buy", *first, "--approved-usd", "10"], client=client) == pc.RC_OK
    second = ["--root", "QG", "--first-trade-date", QM_MIN]
    _quote(env, second)
    client, calls = fake_client(usd=10.0)
    assert env.run(["--buy", *second, "--approved-usd", "10"], client=client) == pc.RC_OK
    assert calls["get_range"][0]["symbols"] == ["QG.v.0"]
    commits = [e for e in env.lines() if e["event"] == "commit"]
    assert len(commits) == 2 and {c["account"] for c in commits} == {"acct-3"}


# ------------------------------------------------------------------ RD: end bound ----
def test_DOCUMENTS_buy_with_an_end_before_the_cutoff_passes_the_minimum_span_check(env):
    """RD finding: min_span_refusal checks the start only. With --end earlier than
    2024-02-29T22:00:00Z the buy downloads a span that does not hold the minimum span
    [2024-01-12, 2024-02-29T22:00Z) (spec sections 0 and 6 fix the end)."""
    argv = ["--root", "QM", "--first-trade-date", "2023-11-14", "--end", "2023-12-01"]
    _quote(env, argv)
    client, calls = fake_client(usd=10.0)
    rc = env.run(["--buy", *argv, "--approved-usd", "10"], client=client)
    assert rc == pc.RC_OK
    assert calls["get_range"][0]["end"] == "2023-12-01"
    assert pc.min_span_refusal(pc.start_bound(date(2023, 11, 14))) is None


def test_CHECK_span_search_refuses_any_other_end(env, capsys):
    rc = env.run(["--span-search", "--root", "QM", "--end", "2024-02-01", "--first-listed",
                  "2010-06-06"])
    assert rc == pc.RC_REFUSED and env.built == []


# ------------------------------------------------------------------ QM parameters ----
def test_CHECK_qm_minimum_span_request_is_admissible_and_exact():
    start = pc.start_bound(date(2024, 1, 12))
    assert start == "2024-01-11T22:00:00Z"
    params = pc.pilot_params("QM", start)
    assert params.end == "2024-02-29T22:00:00Z" and params.symbols == ("QM.v.0",)
    assert pc.request_refusals(params, "QM") == []
    assert pc.min_span_refusal(start) is None
    assert pc.min_span_refusal(pc.start_bound(date(2024, 1, 15))) is not None
    assert pc.min_span_refusal("2024-01-11T22:00:01Z") is not None


@pytest.mark.parametrize("balance,target", [(125.0, 121.25), (100.0, 97.0), (50.0, 47.0),
                                            (110.0, 106.7), (99.99, 96.99)])
def test_CHECK_margin_target(balance, target):
    assert pc.margin_target(balance) == target
    # a 3% overrun of a quote equal to TARGET still fits the balance
    assert target * 1.03 <= balance + 1e-9


# ------------------------------------------------------------------ RD: verify.py ----
def _es_file(tmp, start, end, days):
    cal = pc.calendar_for("ES")
    rows = []
    for d in days:
        rows += session_tape(d, cal)
    path = pilot_file(tmp, "ES", start, end)
    return write_dbn(path, rows, root="ES", start_ns=pc.bound_ns(start), end_ns=pc.bound_ns(end),
                     intervals=[(date(2023, 11, 1), date(2024, 3, 1), "111")])


def test_DOCUMENTS_verify_exits_0_without_a_purchase_record(tmp_path):
    """RD finding (author's open question 3): no --purchase-record, no sha256 check, exit 0."""
    d = date(2023, 11, 14)
    path = _es_file(tmp_path, pc.start_bound(d), "2023-11-14T22:00:00Z", [d])
    out = tmp_path / "m.json"
    assert verify.main(["--root", "ES", "--dbn", str(path), "--out", str(out)]) == 0
    names = [c["name"] for c in json.loads(out.read_text())["files"][0]["checks"]]
    assert "sha256_matches_purchase_record" not in names


def test_DOCUMENTS_verify_with_two_files_skips_the_sha_check_silently(tmp_path):
    """RD finding: with two --dbn files the purchase record's sha256 is ignored (no check
    written), so a wrong record still gives exit 0."""
    d1, d2 = date(2023, 11, 14), date(2023, 11, 15)
    a = _es_file(tmp_path / "a", pc.start_bound(d1), "2023-11-14T22:00:00Z", [d1])
    b = _es_file(tmp_path / "b", pc.start_bound(d2), "2023-11-15T22:00:00Z", [d2])
    rec = tmp_path / "purchase.json"
    rec.write_text(json.dumps({"sha256": "0" * 64}))
    out = tmp_path / "m.json"
    rc = verify.main(["--root", "ES", "--dbn", str(a), str(b), "--out", str(out),
                      "--purchase-record", str(rec)])
    assert rc == 0
    names = {c["name"] for f in json.loads(out.read_text())["files"] for c in f["checks"]}
    assert "sha256_matches_purchase_record" not in names


def test_CHECK_verify_with_a_wrong_purchase_record_fails(tmp_path):
    d = date(2023, 11, 14)
    path = _es_file(tmp_path, pc.start_bound(d), "2023-11-14T22:00:00Z", [d])
    rec = tmp_path / "purchase.json"
    rec.write_text(json.dumps({"sha256": "0" * 64}))
    out = tmp_path / "m.json"
    assert verify.main(["--root", "ES", "--dbn", str(path), "--out", str(out),
                        "--purchase-record", str(rec)]) == 1
