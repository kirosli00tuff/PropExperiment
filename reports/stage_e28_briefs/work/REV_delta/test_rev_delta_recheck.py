"""DeltaReviewer re-check (E.28b round 2): the RD-01..RD-03 fixes hold, plus probes for new holes.
Fake clients, tmp ledgers, no network. Every test asserts the SAFE behaviour (a pass = fixed)."""
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

MIN = ["--first-trade-date", "2024-01-12"]


@pytest.fixture
def env(tmp_path):
    return Env(tmp_path)


def _quote(env, argv, usd=10.0):
    client, _ = fake_client(usd=usd)
    return env.run(["--quote", *argv], client=client)


@pytest.mark.parametrize("mode", ["--plan", "--quote", "--buy", "--span-search"])
@pytest.mark.parametrize("root", ["QG", "qm", "CL", "MCL"])
def test_other_roots_refused_before_any_key_in_every_mode(env, mode, root):
    extra = ["--approved-usd", "10"] if mode == "--buy" else []
    argv = [mode, "--root", root, *(MIN if mode != "--span-search" else ["--first-listed",
                                                                         "2010-06-06"]), *extra]
    assert env.run(argv) == pc.RC_REFUSED
    assert env.keys == [] and env.built == [] and env.lines() == []


@pytest.mark.parametrize("end", ["2024-02-29", "2024-02-29T21:59:59Z", "2023-12-01",
                                 "2024-02-29T22:00:00.000Z"])
@pytest.mark.parametrize("mode", ["--quote", "--buy"])
def test_any_other_end_refused(env, mode, end):
    extra = ["--approved-usd", "10"] if mode == "--buy" else []
    assert env.run([mode, "--root", "QM", *MIN, "--end", end, *extra]) == pc.RC_REFUSED
    assert env.keys == [] and env.lines() == []


def test_second_purchase_refused_after_a_settled_first(env):
    assert _quote(env, ["--root", "QM", *MIN]) == pc.RC_OK
    client, _ = fake_client(usd=10.0, root="QM")
    assert env.run(["--buy", "--root", "QM", *MIN, "--approved-usd", "10"],
                   client=client) == pc.RC_OK
    other = ["--root", "QM", "--first-trade-date", "2023-12-01"]
    assert _quote(env, other) == pc.RC_OK          # quotes stay allowed (free)
    n = len(env.lines())
    client, calls = fake_client(usd=10.0, root="QM")
    assert env.run(["--buy", *other, "--approved-usd", "10"], client=client) == pc.RC_REFUSED
    assert calls["get_range"] == [] and len(env.lines()) == n


def test_orphan_commit_of_another_request_in_another_session_blocks_the_buy(env):
    env.seed(ts="2026-10-21T00:00:00+00:00", account="acct-3", event="commit", usd=5.0,
             session_id="stage-E.28-pilot-other", request={"symbols": ["QM.v.0"]})
    assert _quote(env, ["--root", "QM", *MIN]) == pc.RC_OK
    client, calls = fake_client(usd=10.0, root="QM")
    assert env.run(["--buy", "--root", "QM", *MIN, "--approved-usd", "10"],
                   client=client) == pc.RC_REFUSED
    assert calls["get_range"] == []


def _es_file(tmp, d):
    rows = session_tape(d, pc.calendar_for("ES"))
    start, end = pc.start_bound(d), f"{d.isoformat()}T22:00:00Z"
    return write_dbn(pilot_file(tmp, "ES", start, end), rows, root="ES",
                     start_ns=pc.bound_ns(start), end_ns=pc.bound_ns(end),
                     intervals=[(date(2023, 11, 1), date(2024, 3, 1), "111")])


def test_verify_requires_a_record_and_checks_every_file(tmp_path):
    d1, d2 = date(2023, 11, 14), date(2023, 11, 15)
    a, b = _es_file(tmp_path / "a", d1), _es_file(tmp_path / "b", d2)
    out = tmp_path / "m.json"
    assert verify.main(["--root", "ES", "--dbn", str(a), "--out", str(out)]) == pc.RC_REFUSED
    from data.pull_universe import file_sha256
    rec = tmp_path / "r.json"
    rec.write_text(json.dumps({"sha256": file_sha256(a)}))
    assert verify.main(["--root", "ES", "--dbn", str(a), "--out", str(out),
                        "--purchase-record", str(rec)]) == 0
    assert verify.main(["--root", "ES", "--dbn", str(a), str(b), "--out", str(out),
                        "--purchase-record", str(rec)]) == 1
    rec.write_text(json.dumps({"sha256": file_sha256(a).upper()}))
    assert verify.main(["--root", "ES", "--dbn", str(a), "--out", str(out),
                        "--purchase-record", str(rec)]) == pc.RC_REFUSED


def test_verify_refuses_a_qm_folder_file_under_another_root(tmp_path):
    path = pilot_file(tmp_path, "QM", pc.start_bound(date(2024, 1, 12)), pc.CUTOFF_BOUND)
    assert pc.file_name_refusals(path, "QG") and not pc.file_name_refusals(path, "QM")
