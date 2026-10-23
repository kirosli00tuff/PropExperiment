"""canary_check31.py on synthetic DBN files only (no network, no key, tmp folders).

    uv run pytest -q -p no:cacheprovider reports/stage_e31_briefs/work/pilot/tests/test_canary31.py
"""

import json
import sys
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import pytest

PILOT = Path(__file__).resolve().parents[1]
TESTS = Path(__file__).resolve().parent
for p in (PILOT, TESTS):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import canary_check31 as cc  # noqa: E402
import pilot31_common as pc  # noqa: E402
import test_pull31 as tp  # noqa: E402  (the synthetic DBN writer)
import verify31 as vf  # noqa: E402

from data.group_session import session_intervals, trade_dates_between  # noqa: E402

S = pc.NS
FEB = date(2024, 2, 1)
ROLL = date(2024, 2, 15)  # v.0 100 -> 101 and v.1 101 -> 102 from this UTC date
SNAP_R, SNAP_A = 32 | 8, 32 | 8 | 128  # F_SNAPSHOT | F_BAD_TS_RECV (| F_LAST)
DEF = {"ZM": (10**8, 10 * 10**9, 100 * 10**9), "ZS": (25 * 10**7, 125 * 10**8, 5000 * 10**9),
       "ZL": (10**7, 6 * 10**9, 60000 * 10**9)}  # tick, tick USD, contract size (1e-9)


def _item(name: str, month: date = FEB) -> pc.Planned:
    s = pc.SERIES_BY_NAME[name]
    return pc.Planned(s, month, pc.check_request(pc.request_for(s, month)))


def _mbo(iid, t, action, size=1, *, recv=None, flags=0, side=None, k=0):
    import databento_dbn as dbn

    act = {"R": dbn.Action.CLEAR, "A": dbn.Action.ADD, "T": dbn.Action.TRADE,
           "F": dbn.Action.FILL, "C": dbn.Action.CANCEL}[action]
    sd = side or (dbn.Side.NONE if action == "R" else dbn.Side.ASK)
    return dbn.MBOMsg(1, iid, t, 1000 + k, 350 * 10**9, size, act, sd,
                      t + 1000 if recv is None else recv, flags=flags, sequence=k)


def _ns(day: date, hour: int, minute: int = 0) -> int:
    return int(datetime(day.year, day.month, day.day, hour, minute, tzinfo=UTC).timestamp()) * S


# ------------------------------------------------------------------ builders ----
def z1_mappings(item: pc.Planned) -> dict:
    d0 = pc.parse_utc(item.params.start).date()
    d1 = pc.parse_utc(item.params.end).date() + timedelta(days=1)
    if not d0 < ROLL < d1:  # no roll inside this month
        return {"ZM.v.0": [(d0, d1, 100)], "ZM.v.1": [(d0, d1, 101)]}
    return {"ZM.v.0": [(d0, ROLL, 100), (ROLL, d1, 101)],
            "ZM.v.1": [(d0, ROLL, 101), (ROLL, d1, 102)]}


def write_z1(vendor: Path, item: pc.Planned, *, drop=None, trades=None) -> Path:
    """Snapshots (R then one A, F_LAST) per weekday midnight and mapped instrument, and trade
    groups on 2024-02-06 15:00Z, interleaved across instruments."""
    maps = z1_mappings(item)
    hdr = {"mappings": {s: [{"start_date": a.isoformat(), "end_date": b.isoformat(),
                             "symbol": str(i)} for a, b, i in rows] for s, rows in maps.items()}}
    recs = []
    start, end = pc.bound_ns(item.params.start), pc.bound_ns(item.params.end)
    for mid in vf.weekday_midnights(start, end):
        day = datetime.fromtimestamp(mid // S, UTC).date()
        for ids in vf.mapped_on(hdr, day).values():
            for iid in ids:
                if drop == (day, iid):
                    continue
                recs += [_mbo(iid, mid, "R", 0, recv=mid, flags=SNAP_R),
                         _mbo(iid, mid - 5 * S, "A", 4, recv=mid, flags=SNAP_A)]
    t = _ns(date(item.month.year, item.month.month, 6), 15)
    default =[(100, "T", 3), (101, "A", 2), (100, "F", 2), (100, "F", 1), (101, "T", 5),
               (101, "F", 5), (100, "C", 1)]
    for k, (iid, action, size) in enumerate(trades if trades is not None else default):
        recs.append(_mbo(iid, t + k, action, size, k=k))
    recs.sort(key=lambda r: r.ts_recv)
    path = pc.target_path(item, vendor)
    return tp.encode_dbn(path, item.params.as_kwargs(), recs, maps)


def write_daily(vendor: Path, item: pc.Planned, *, skip=None) -> Path:
    """One in-session record (09:00 CT) on each grains trade date of the month, and one record
    before the session (18:00 CT the evening before) on the first trade date."""
    import databento_dbn as dbn

    cal = pc.calendar_for(item.series.roots[0])
    days = trade_dates_between(cal, item.month, pc.last_day(item.month))
    level = dbn.BidAskPair(bid_px=1, ask_px=2, bid_sz=1, ask_sz=1, bid_ct=1, ask_ct=1)
    times = [session_intervals(cal, d)[-1][0] + 30 * 60 * S for d in days if d != skip]
    times.insert(0, session_intervals(cal, days[0])[0][0] - 3600 * S)
    recs = [dbn.MBP1Msg(1, 100, t, 1, 1, dbn.Action.ADD, dbn.Side.BID, 0, t + 1000, flags=0,
                        sequence=k, levels=level) for k, t in enumerate(times)]
    return tp.encode_dbn(pc.target_path(item, vendor), item.params.as_kwargs(), recs)


def write_z4(vendor: Path, item: pc.Planned, *, override=None) -> Path:
    import databento_dbn as dbn

    override = override or {}
    rows = [(100, "ZMG4", "ZM"), (101, "ZMH4", "ZM"), (102, "ZMK4", "ZM"),
            (200, "ZSH4", "ZS"), (300, "ZLH4", "ZL")]
    t = pc.bound_ns(item.params.start) + 2 * 3600 * S
    recs = []
    for iid, raw, root in rows:
        tick, amount, qty = override.get(root, {}).get("ticks", DEF[root])
        algo = override.get(root, {}).get("algo", dbn.MatchAlgorithm.CONFIGURABLE)
        recs.append(dbn.InstrumentDefMsg(
            1, iid, t, t + 1000, tick, 10**9, raw, root, "FUT", dbn.InstrumentClass.FUTURE,
            dbn.SecurityUpdateAction.ADD, match_algorithm=algo, unit_of_measure_qty=qty,
            min_price_increment_amount=amount))
    recs.append(dbn.InstrumentDefMsg(  # a spread: not an outright, never in the tick table
        1, 900, t, t + 1000, 5 * 10**7, 10**9, "ZMG4-ZMH4", "ZM", "FUT",
        dbn.InstrumentClass.FUTURE_SPREAD, dbn.SecurityUpdateAction.ADD,
        match_algorithm=dbn.MatchAlgorithm.FIFO))
    return tp.encode_dbn(pc.target_path(item, vendor), item.params.as_kwargs(), recs)


def write_month(vendor: Path, month: date = FEB, **over) -> None:
    write_z1(vendor, _item("Z1", month), **over.get("Z1", {}))
    write_daily(vendor, _item("Z2", month), **over.get("Z2", {}))
    write_daily(vendor, _item("Z3", month), **over.get("Z3", {}))
    write_z4(vendor, _item("Z4", month), **over.get("Z4", {}))


def run(tmp_path: Path, *argv: str) -> tuple[int, dict | None]:
    runs = tmp_path / "runs"
    code = cc.main(["--month", "2024-02", *argv], vendor_root=tmp_path / "vendor",
                   runs_dir=runs)
    path = runs / cc.JSON_FILE
    return code, json.loads(path.read_text()) if path.is_file() else None


# ------------------------------------------------------------------ tests ----
def test_clean_structure_holds_and_both_outputs_are_written(tmp_path):
    write_month(tmp_path / "vendor")
    code, rep = run(tmp_path)
    assert code == pc.RC_OK and rep["findings"] == [] and rep["exit_code"] == 0
    m = rep["months"]["2024-02"]
    z1 = m["Z1"]
    assert len(z1["snapshots"]) == 42 and all(r["snapshot_clears"] == 1 for r in z1["snapshots"])
    assert all(r["snapshot_adds"] == 1 and r["f_last"] for r in z1["snapshots"])
    roll = next(r for r in z1["mapping"] if r["date"] == ROLL.isoformat())
    before = next(r for r in z1["mapping"] if r["date"] == "2024-02-14")
    assert roll["ZM.v.0"] == [{"instrument_id": 101, "raw_symbol": "ZMH4"}]
    assert roll["ZM.v.1"] == [{"instrument_id": 102, "raw_symbol": "ZMK4"}]
    assert before["ZM.v.0"] == [{"instrument_id": 100, "raw_symbol": "ZMG4"}]
    cell = next(r for r in z1["snapshots"] if r["midnight"].startswith("2024-02-15")
                and r["symbol"] == "ZM.v.1")
    assert (cell["instrument_id"], cell["raw_symbol"]) == (102, "ZMK4")
    tf = z1["t_f"]
    assert (tf["n_T"], tf["n_F"], tf["T_F_sum_equal_size"], tf["T_without_F"],
            tf["T_F_sum_above_size"], tf["F_without_T"]) == (2, 3, 2, 0, 0, 0)
    roots = {s["root"]: s for s in m["Z4"]["roots"]}
    assert (roots["ZM"]["tick"], roots["ZM"]["price_unit"], roots["ZM"]["tick_usd"]) == \
        (0.1, "USD", 10.0)
    assert (roots["ZS"]["tick"], roots["ZS"]["price_unit"], roots["ZS"]["tick_usd"]) == \
        (0.25, "US cents", 12.5)
    assert (roots["ZL"]["tick"], roots["ZL"]["price_unit"], roots["ZL"]["tick_usd"]) == \
        (0.01, "US cents", 6.0)
    assert roots["ZM"]["outrights"] == ["ZMG4", "ZMH4", "ZMK4"]  # the spread is left out
    assert roots["ZM"]["match_algorithm"] == {"K": 3}
    cal = pc.calendar_for("ZS")
    days = trade_dates_between(cal, FEB, date(2024, 2, 29))
    z2 = m["Z2"]["per_trade_date"]
    assert [r["trade_date"] for r in z2] == [d.isoformat() for d in days]
    assert all(r["in_session"] == 1 for r in z2) and z2[0]["before_session"] == 1
    assert date(2024, 2, 19) not in days  # Presidents' Day: the calendar's closure
    md = (tmp_path / "runs" / cc.MD_FILE).read_text()
    assert "none: the structure holds" in md and "| 2024-02-15 | ZM.v.1 | 102 | ZMK4 | yes" in md


def test_a_missing_snapshot_after_the_roll_is_a_finding(tmp_path):
    write_month(tmp_path / "vendor", Z1={"drop": (ROLL, 102)})
    code, rep = run(tmp_path)
    assert code == pc.RC_QUALITY
    assert rep["findings"] == ["Z1 2024-02: no snapshot at 2024-02-15T00:00:00.000000000Z for "
                               "ZM.v.1 (instrument 102)"]
    assert "MISSING" in (tmp_path / "runs" / cc.MD_FILE).read_text()


@pytest.mark.parametrize("trades,field,n", [
    ([(100, "T", 3), (100, "A", 1), (100, "F", 3)], "T_without_F", 1),
    ([(100, "T", 3), (100, "F", 2), (100, "F", 2)], "T_F_sum_above_size", 1),
    ([(100, "A", 1), (100, "F", 2), (100, "F", 1)], "F_without_T", 2),
    ([(100, "F", 1), (100, "T", 2)], "F_without_T", 1),  # T last in the file: no F after it
])
def test_t_and_f_pairing_findings(tmp_path, trades, field, n):
    write_month(tmp_path / "vendor", Z1={"trades": trades})
    code, rep = run(tmp_path)
    tf = rep["months"]["2024-02"]["Z1"]["t_f"]
    assert code == pc.RC_QUALITY and tf[field] == n and rep["findings"]


def test_t_last_in_file_without_f_is_counted(tmp_path):
    write_month(tmp_path / "vendor", Z1={"trades": [(100, "T", 2)]})
    code, rep = run(tmp_path)
    tf = rep["months"]["2024-02"]["Z1"]["t_f"]
    assert code == pc.RC_QUALITY and tf["T_without_F"] == 1 and tf["examples"][0]["t_size"] == 2


@pytest.mark.parametrize("chunk", ["1", "2", "3", "1000000"])
def test_pairing_does_not_depend_on_chunk_boundaries(tmp_path, chunk):
    trades = [(100, "T", 3), (101, "A", 2), (100, "F", 2), (101, "T", 4), (100, "F", 1),
              (101, "F", 4), (102, "F", 1), (100, "T", 2), (100, "F", 3), (101, "T", 1)]
    write_month(tmp_path / "vendor", Z1={"trades": trades})
    code, rep = run(tmp_path, "--chunk-records", chunk)
    tf = rep["months"]["2024-02"]["Z1"]["t_f"]
    assert (tf["n_T"], tf["n_F"], tf["T_F_sum_equal_size"], tf["T_F_sum_above_size"],
            tf["T_without_F"], tf["F_without_T"]) == (4, 5, 2, 1, 1, 1)
    assert code == pc.RC_QUALITY


@pytest.mark.parametrize("override,expected", [
    ({"ZM": {"ticks": (5 * 10**7, 5 * 10**9, 100 * 10**9)}},
     ["ZM: min_price_increment 0.05, expected 0.1", "ZM: tick 0.05 x contract size 100"]),
    ({"ZL": {"ticks": (10**7, 6 * 10**9, 50000 * 10**9)}},
     ["ZL: unit_of_measure_qty [50000.0], expected 60000"]),
    ({"ZL": {"ticks": (2 * 10**7, 2**63 - 1, 2**63 - 1)}}, ["ZL: tick 0.02 x contract size"]),
])
def test_tick_findings(tmp_path, override, expected):
    write_month(tmp_path / "vendor", Z4={"override": override})
    code, rep = run(tmp_path)
    assert code == pc.RC_QUALITY and len(rep["findings"]) == len(expected)
    for want, got in zip(expected, rep["findings"], strict=True):
        assert got.startswith(f"Z4 2024-02: {want}")


def test_the_tick_amount_field_is_reported_as_found_not_checked(tmp_path):
    over = {r: {"ticks": (t, a, q)} for r, (t, a, q) in
            {"ZM": (10**8, 10**9, 100 * 10**9), "ZS": (25 * 10**7, 10**9, 5000 * 10**9),
             "ZL": (10**7, 6 * 10**7, 60000 * 10**9)}.items()}  # the real files' 1.0, 1.0, 0.06
    write_month(tmp_path / "vendor", Z4={"override": over})
    code, rep = run(tmp_path)
    roots = {s["root"]: s for s in rep["months"]["2024-02"]["Z4"]["roots"]}
    assert code == pc.RC_OK and rep["findings"] == []
    assert roots["ZL"]["min_price_increment_amount"] == {"0.06": 1}
    assert len(rep["notes"]) == 3 and rep["notes"][2].startswith(
        "Z4 2024-02: ZL min_price_increment_amount ['0.06'] as found (not checked")
    md = (tmp_path / "runs" / cc.MD_FILE).read_text()
    assert "## Notes (not findings)" in md and "ZM min_price_increment_amount ['1.0']" in md


@pytest.mark.parametrize("trades,per_t,runs", [
    ([(100, "T", 2), (100, "T", 1), (100, "F", 2), (100, "F", 1)],  # a sweep: T, T, F, F
     {"T_without_F": 1, "T_F_sum_above_size": 1},
     {"runs": 1, "runs_with_several_T": 1, "F_sum_equal_T_sum": 1}),
    ([(100, "T", 5), (100, "F", 5), (100, "F", 5)],  # an auction print: both sides filled
     {"T_F_sum_above_size": 1}, {"runs": 1, "F_sum_twice_T_sum": 1}),
])
def test_t_runs_are_info_only_beside_the_per_t_rule(tmp_path, trades, per_t, runs):
    write_month(tmp_path / "vendor", Z1={"trades": trades})
    code, rep = run(tmp_path)
    z1 = rep["months"]["2024-02"]["Z1"]
    assert code == pc.RC_QUALITY  # the per-T rule is what decides
    assert all(z1["t_f"][k] == v for k, v in per_t.items())
    assert {k: v for k, v in z1["t_runs_info"].items() if v} == runs
    assert "T runs (info only)" in (tmp_path / "runs" / cc.MD_FILE).read_text()


def test_clean_t_runs_info(tmp_path):
    write_month(tmp_path / "vendor")
    _, rep = run(tmp_path)
    info = rep["months"]["2024-02"]["Z1"]["t_runs_info"]
    assert {k: v for k, v in info.items() if v} == {"runs": 2, "F_sum_equal_T_sum": 2}


@pytest.mark.parametrize("chunk", ["1", "2", "5", "1000000"])
def test_t_runs_do_not_depend_on_chunk_boundaries(tmp_path, chunk):
    trades = [(100, "T", 2), (101, "A", 1), (100, "T", 1), (100, "F", 3), (101, "T", 4),
              (101, "F", 4), (101, "F", 4), (100, "T", 1), (100, "C", 1), (100, "T", 2),
              (100, "F", 1)]
    write_month(tmp_path / "vendor", Z1={"trades": trades})
    _, rep = run(tmp_path, "--chunk-records", chunk)
    info = rep["months"]["2024-02"]["Z1"]["t_runs_info"]
    assert {k: v for k, v in info.items() if v} == {
        "runs": 4, "runs_with_several_T": 1, "F_sum_equal_T_sum": 1, "F_sum_twice_T_sum": 1,
        "runs_without_F": 1, "F_sum_below_T_sum": 1}


def test_a_match_algorithm_other_than_k_is_a_finding(tmp_path):
    import databento_dbn as dbn

    write_month(tmp_path / "vendor", Z4={"override": {"ZS": {"algo": dbn.MatchAlgorithm.FIFO}}})
    code, rep = run(tmp_path)
    assert code == pc.RC_QUALITY
    assert rep["findings"] == ["Z4 2024-02: ZS: outright match_algorithm ['F'], expected K"]


def test_a_trade_date_with_no_record_is_a_finding(tmp_path):
    write_month(tmp_path / "vendor", Z3={"skip": date(2024, 2, 13)})
    code, rep = run(tmp_path)
    assert code == pc.RC_QUALITY
    assert rep["findings"] == ["Z3 2024-02: no in-session record on trade date 2024-02-13"]


def test_default_months_are_january_and_february_2024(tmp_path):
    write_month(tmp_path / "vendor")
    write_month(tmp_path / "vendor", date(2024, 1, 1))
    code = cc.main([], vendor_root=tmp_path / "vendor", runs_dir=tmp_path / "runs")
    rep = json.loads((tmp_path / "runs" / cc.JSON_FILE).read_text())
    assert sorted(rep["months"]) == ["2024-01", "2024-02"]
    jan = rep["months"]["2024-01"]["Z1"]
    assert len(jan["snapshots"]) == 46  # 23 weekdays (2024-01-01 included) x 2
    assert code == pc.RC_OK


@pytest.mark.parametrize("argv,why", [(["--month", "2024-03"], "after"),
                                      (["--month", "2024-1"], "YYYY-MM"),
                                      ([], "missing")])
def test_refusals_open_nothing(tmp_path, capsys, argv, why):
    write_z1(tmp_path / "vendor", _item("Z1"))  # Z2, Z3, Z4 missing for 2024-02
    code = cc.main(argv or ["--month", "2024-02"], vendor_root=tmp_path / "vendor",
                   runs_dir=tmp_path / "runs")
    assert code == pc.RC_REFUSED and why in capsys.readouterr().err
    assert not (tmp_path / "runs").exists()


def test_the_check_reads_no_price_field_of_book_records():
    source = Path(cc.__file__).read_text()
    for name in ('"price"', "'price'", "bid_px", "ask_px", "pretty_px", "_px_", ".price"):
        assert name not in source
