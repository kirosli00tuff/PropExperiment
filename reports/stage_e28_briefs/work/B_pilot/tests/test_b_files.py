"""verify.py and measure.py end to end on small synthetic DBN files (no real data)."""

import json
from datetime import UTC, date, datetime

import measure
import pilot_common as pc
import pytest
import verify
from b_helpers import S, pilot_file, session_tape, write_dbn

from data.pull_universe import file_sha256

D1, D2 = date(2023, 11, 14), date(2023, 11, 15)
START = pc.start_bound(D1)              # 2023-11-13T22:00:00Z
END = "2023-11-15T22:00:00Z"           # 16:00 CST on 2023-11-15
ONE_ID = [(date(2023, 11, 1), date(2024, 3, 1), "111")]


def make_file(tmp, rows=None, intervals=ONE_ID, start=START, end=END):
    cal = pc.calendar_for("ES")
    if rows is None:
        rows = []
        for day in (D1, D2):
            rows += session_tape(day, cal)
    path = pilot_file(tmp, "ES", start, end)
    return write_dbn(path, rows, root="ES", start_ns=pc.bound_ns(start),
                     end_ns=pc.bound_ns(end), intervals=intervals)


def run_measure(path, out, *extra, tick="0.25", workers="1"):
    logs = []
    rc = measure.main(["--root", "ES", "--tick", tick, "--fee-side", "0.5", "--sim-rule",
                       "trade_through_only", "--dbn", str(path), "--out-dir", str(out),
                       "--workers", workers, "--chunk-records", "1000", *extra],
                      log=logs.append)
    return rc, logs


def purchase_record(tmp, sha):
    """A purchase record as pilot_pull.py writes it (only the sha256 is read by verify.py)."""
    rec = tmp / "purchase_record.json"
    rec.write_text(json.dumps({"root": "ES", "sha256": sha}))
    return rec


def run_verify(paths, out, *extra, sha=None):
    """verify.main with a purchase record holding ``sha`` (default: the first file's sha256)."""
    paths = [paths] if not isinstance(paths, list) else paths
    rec = purchase_record(out.parent, sha or file_sha256(paths[0]))
    return verify.main(["--root", "ES", "--dbn", *map(str, paths), "--out", str(out),
                        "--purchase-record", str(rec), *extra])


def test_verify_clean_file(tmp_path):
    path = make_file(tmp_path)
    out = tmp_path / "manifest.json"
    rc = run_verify(path, out, "--tick", "0.25")
    assert rc == 0
    manifest = json.loads(out.read_text())
    (f,) = manifest["files"]
    assert all(c["passed"] for c in f["checks"])
    assert f["trade_dates_with_records"] == ["2023-11-14", "2023-11-15"]
    assert f["records_by_rtype"] == {"1": f["records"]}
    assert set(f["records_by_action"]) == {"A", "T"}
    for row in f["days"]:
        assert row["instrument_ids_mapped"] == ["111"] and row["instrument_ids_records"] == ["111"]
        assert row["main_max_gap_s"] <= 30.0 and row["excluded_by_other_rules"] == []
    assert len(f["sha256"]) == 64 and out.with_suffix(".md").is_file()
    sha = next(c for c in f["checks"] if c["name"] == "sha256_matches_purchase_record")
    assert sha["severity"] == "hard" and sha["passed"] and sha["detail"] == f["sha256"]


CUTOFF_OPEN = datetime(2024, 2, 29, 23, 0, tzinfo=UTC)  # 17:00 CST: trade date 03-01 opens
MAINT_HOUR = "records_in_maintenance_hour_2024-02-29T22-23Z"


def _cutoff_checks(tmp_path, *late_moments):
    cal = pc.calendar_for("ES")
    rows = session_tape(date(2024, 2, 29), cal)
    for moment in late_moments:
        late = pc.ns_of(moment)
        rows.append({"t": late, "recv": late, "bid": 100, "ask": 101, "bsz": 1, "asz": 1})
    path = make_file(tmp_path, rows=rows, start=pc.start_bound(date(2024, 2, 29)),
                     end=pc.CUTOFF_BOUND)
    out = tmp_path / "m.json"
    rc = run_verify(path, out)
    return rc, {c["name"]: c for c in json.loads(out.read_text())["files"][0]["checks"]}


def test_cutoff_constants_match_the_frozen_spec():
    # spec section 0 / RS-01: request end 2024-02-29T22:00:00Z exclusive (16:00 CST, the end of
    # trade date 02-29); verify: no ts_event at or after 23:00Z (the 17:00 CST open of 03-01)
    end, open_ns = pc.CUTOFF_BOUND, pc.CUTOFF_OPEN_NS
    assert end == "2024-02-29T22:00:00Z"
    assert open_ns == pc.ns_of(CUTOFF_OPEN)
    assert verify.CUTOFF_CHECK == \
        "no_record_at_or_after_2024-02-29T23:00Z_open_of_trade_date_2024-03-01"


@pytest.mark.parametrize("late", [CUTOFF_OPEN,                                   # exactly 23:00Z
                                  datetime(2024, 3, 1, 7, 0, tzinfo=UTC)])       # 01:00 CST 03-01
def test_verify_fails_on_a_record_at_or_after_the_open_of_trade_date_0301(tmp_path, late):
    rc, checks = _cutoff_checks(tmp_path, late)
    assert rc == 1
    assert not checks[verify.CUTOFF_CHECK]["passed"]
    assert checks[verify.CUTOFF_CHECK]["detail"] == 1
    assert checks[MAINT_HOUR]["detail"] == 0


def test_records_in_the_maintenance_hour_before_0301_open_are_info_only(tmp_path):
    # [22:00Z, 23:00Z) on 02-29: after the request end but before trade date 03-01 opens
    rc, checks = _cutoff_checks(tmp_path, datetime(2024, 2, 29, 22, 0, tzinfo=UTC),
                                datetime(2024, 2, 29, 22, 59, 59, tzinfo=UTC))
    assert checks[verify.CUTOFF_CHECK]["passed"] and checks[verify.CUTOFF_CHECK]["detail"] == 0
    assert checks[MAINT_HOUR]["severity"] == "info" and checks[MAINT_HOUR]["passed"]
    assert checks[MAINT_HOUR]["detail"] == 2
    assert rc == 0


def test_verify_and_measure_handle_a_main_gap(tmp_path):
    cal = pc.calendar_for("ES")
    gap_lo = pc.ns_of(datetime(2023, 11, 15, 16, 0, tzinfo=UTC))
    rows = session_tape(D1, cal) + [r for r in session_tape(D2, cal)
                                    if not gap_lo <= r["t"] < gap_lo + 120 * S]
    path = make_file(tmp_path, rows=rows)
    out = tmp_path / "m.json"
    assert run_verify(path, out) == 3
    check = next(c for c in json.loads(out.read_text())["files"][0]["checks"]
                 if c["name"] == "main_session_gap_le_60s")
    assert check["detail"]["dates_otherwise_included_with_gap_gt_60s"] == ["2023-11-15"]
    rc, _ = run_measure(path, tmp_path / "res")
    assert rc == 0
    res = json.loads((tmp_path / "res" / "results.json").read_text())
    assert res["days"]["included"] == ["2023-11-14"]
    assert res["days"]["excluded"]["2023-11-15"] == [pc.EXCL_GAP]


def test_measure_end_to_end_resume_and_fingerprint(tmp_path):
    path = make_file(tmp_path)
    out = tmp_path / "res"
    rc, logs = run_measure(path, out)
    assert rc == 0
    res = json.loads((out / "results.json").read_text())
    assert res["days"]["included"] == ["2023-11-14", "2023-11-15"]
    cell = res["results"]["spec"]["T|MAIN"]
    # 2 dates x 76 MAIN grid times x 2 sides; spread is 1 tick so no I order is placed
    assert cell["pooled"]["placements"] == 304
    assert cell["buy"]["placements"] == cell["sell"]["placements"] == 152
    assert res["results"]["spec"]["I|MAIN"]["pooled"]["placements"] == 0
    assert res["data_checks_included_days"]["skipped_placements"]["I|MAIN|buy|spread_lt_2_ticks"] \
        == 152
    assert res["results"]["spec"]["T|OVERNIGHT"]["pooled"]["placements"] == 2 * 194 * 2
    assert set(res["results"]) == {"spec", "trade_through_only"}
    md = (out / "results.md").read_text()
    assert "### Cell T|MAIN (rule spec)" in md and "trade_through_only" in md
    days = sorted(p.name for p in (out / "days").glob("*.json"))
    assert days == ["2023-11-14.json", "2023-11-15.json"]
    rc, logs = run_measure(path, out)  # resume: nothing left to measure
    assert rc == 0 and any("0 to measure" in m for m in logs)
    rc, _ = run_measure(path, out, tick="0.125")  # a different fingerprint is refused
    assert rc == 2


def test_measure_reports_the_second_fee_without_a_new_phase_1(tmp_path):
    # spec section 0 (QM): FEE_SIDE 0.1368 and the conservative 0.296; fees are phase 2 only
    path = make_file(tmp_path)
    out = tmp_path / "res"
    assert run_measure(path, out)[0] == 0
    rc, logs = run_measure(path, out, "--fee-side", "0.1368", "--fee-side-alt", "0.296",
                           "0.296", "--aggregate-only")
    assert rc == 0
    res = json.loads((out / "results.json").read_text())
    assert res["parameters"]["fee_side_ticks"] == 0.1368
    assert res["parameters"]["fee_side_alt_ticks"] == [0.296]
    pooled = res["results"]["spec"]["T|MAIN"]["pooled"]
    # the synthetic tape has no fill (the by-hand values are in test_b_stats): the alt keys are
    # present with no value, and VPO is 0 (placements, no fill) at either fee
    assert pooled["placements"] == 304 and pooled["fills"] == 0
    for h in ("1", "10", "60"):
        for variant in ("markouts", "markouts_nodrop"):
            assert pooled[variant][h]["mean_net_alt"]["0.296"]["value"] is None
    assert pooled["vpo_alt"]["0.296"] and set(pooled["vpo_alt"]["0.296"]) == {"10", "60"}
    assert pooled["vpo_alt"]["0.296"]["60"]["value"] == 0.0
    assert pooled["vpo_nodrop_alt"]["0.296"]["60"]["value"] == 0.0
    assert "also at 0.296 ticks" in (out / "results.md").read_text()
    assert run_measure(path, out, "--fee-side-alt", "-0.1", "--aggregate-only")[0] == 2


def test_measure_two_workers_match_one(tmp_path):
    path = make_file(tmp_path)
    rc1, _ = run_measure(path, tmp_path / "one", workers="1")
    rc2, _ = run_measure(path, tmp_path / "two", workers="2")
    assert rc1 == rc2 == 0
    r1 = json.loads((tmp_path / "one" / "results.json").read_text())["results"]
    r2 = json.loads((tmp_path / "two" / "results.json").read_text())["results"]
    assert r1 == r2


def test_measure_excludes_roll_day(tmp_path):
    intervals = [(date(2023, 11, 1), date(2023, 11, 15), "111"),
                 (date(2023, 11, 15), date(2024, 3, 1), "222")]
    path = make_file(tmp_path, intervals=intervals)
    rc, _ = run_measure(path, tmp_path / "res")
    assert rc == 0
    res = json.loads((tmp_path / "res" / "results.json").read_text())
    # 2023-11-15's trade date opens 11-14 23:00Z, before the 00:00Z change: two instruments
    assert res["days"]["excluded"] == {"2023-11-15": [pc.EXCL_ROLL]}
    assert res["days"]["included"] == ["2023-11-14"]


def test_measure_refuses_research_window_file_unread(tmp_path, capsys):
    bad = pilot_file(tmp_path, "ES", "2025-05-13", "2025-05-14")
    bad.parent.mkdir(parents=True)
    bad.write_bytes(b"not a dbn file: must never be opened")
    rc, _ = run_measure(bad, tmp_path / "res")
    assert rc == 2 and "refused unread" in capsys.readouterr().err
    assert verify.main(["--root", "ES", "--dbn", str(bad), "--out", str(tmp_path / "m.json"),
                        "--purchase-record", str(purchase_record(tmp_path, "0" * 64))]) == 2


def test_measure_refuses_wrong_header(tmp_path, capsys):
    path = make_file(tmp_path)
    other = pilot_file(tmp_path / "x", "ES", START, END)
    write_dbn(other, [], root="ES", start_ns=pc.bound_ns(START), end_ns=pc.bound_ns(END),
              intervals=ONE_ID, schema="ohlcv-1m")
    rc, _ = run_measure(other, tmp_path / "res")
    assert rc == 2 and "metadata schema" in capsys.readouterr().err
    assert path.is_file()


@pytest.mark.parametrize("workers", ["0", "5"])
def test_measure_worker_bounds(tmp_path, workers):
    path = make_file(tmp_path)
    rc, _ = run_measure(path, tmp_path / "res", workers=workers)
    assert rc == 2


# ------------------------------------------------------------------ RD-03 ----
def test_verify_refuses_to_run_without_a_purchase_record(tmp_path, capsys):
    path = make_file(tmp_path)
    out = tmp_path / "m.json"
    assert verify.main(["--root", "ES", "--dbn", str(path), "--out", str(out)]) == 2
    assert "--purchase-record is required" in capsys.readouterr().err and not out.exists()


@pytest.mark.parametrize("content", ['{"root": "ES"}', '{"sha256": "abc"}', "[]", "not json"])
def test_verify_refuses_a_record_without_a_sha256(tmp_path, content):
    path = make_file(tmp_path)
    rec = tmp_path / "rec.json"
    rec.write_text(content)
    out = tmp_path / "m.json"
    assert verify.main(["--root", "ES", "--dbn", str(path), "--out", str(out),
                        "--purchase-record", str(rec)]) == 2
    assert not out.exists()


def test_verify_fails_when_the_sha256_differs_from_the_record(tmp_path):
    out = tmp_path / "m.json"
    assert run_verify(make_file(tmp_path), out, sha="0" * 64) == 1
    (f,) = json.loads(out.read_text())["files"]
    check = next(c for c in f["checks"] if c["name"] == "sha256_matches_purchase_record")
    assert not check["passed"]


def test_verify_checks_every_file_against_the_record(tmp_path):
    # RD-03: with two files, each gets the hard sha256 check; the record (one purchase, one
    # file) matches the first only, so the run fails: never silently skipped
    a = make_file(tmp_path / "a", rows=session_tape(D1, pc.calendar_for("ES")),
                  start=pc.start_bound(D1), end="2023-11-14T22:00:00Z")
    b = make_file(tmp_path / "b", rows=session_tape(D2, pc.calendar_for("ES")),
                  start=pc.start_bound(D2), end="2023-11-15T22:00:00Z")
    out = tmp_path / "m.json"
    assert run_verify([a, b], out) == 1
    files = json.loads(out.read_text())["files"]
    shas = [next(c for c in f["checks"] if c["name"] == "sha256_matches_purchase_record")
            for f in files]
    assert [c["passed"] for c in shas] == [True, False]
    assert run_verify([a, b], tmp_path / "m2.json", sha=file_sha256(b)) == 1
