"""forward/etf_bars.py: the ETF bar interface E22-F2's runner consumes (Stage E.24 Part C)."""

from __future__ import annotations

import hashlib
import math
from datetime import date, datetime

import pytest

from forward import sources
from forward.etf_bars import (
    CsvEtfSource,
    EtfBar,
    EtfBarError,
    EtfBarSource,
    EtfDayRow,
    InMemoryEtfSource,
    Missing,
    NotReady,
    SourceUnavailable,
    dump_etf_warmup,
    etf_history_sha256,
    load_etf_warmup,
    normalize_etf_day,
)

D1, D2, D3 = date(2026, 11, 2), date(2026, 11, 3), date(2026, 11, 4)


def _rows():
    return [
        EtfDayRow(D1, {"QQQ": EtfBar(500.0), "BIL": EtfBar(91.5)}),
        EtfDayRow(D2, {"QQQ": EtfBar(505.0, 0.01, D1), "BIL": EtfBar(91.51, 0.0001, D1)}),
        EtfDayRow(D3, {"QQQ": EtfBar(500.0, -0.0099, D2), "BIL": EtfBar(91.52, 0.0001, D2)}),
    ]


# --- EtfBar validation ---------------------------------------------------------------------


def test_bar_accepts_valid_values_and_normalises_to_float():
    bar = EtfBar(500, 0, D1)
    assert bar.close == 500.0 and isinstance(bar.close, float)
    assert bar.ret == 0.0 and isinstance(bar.ret, float)
    assert EtfBar(1.5).ret is None and EtfBar(1.5).prev_date is None


@pytest.mark.parametrize(
    "close, ret, prev",
    [
        (0.0, None, None),
        (-1.0, None, None),
        (math.nan, None, None),
        (math.inf, None, None),
        (True, None, None),
        ("abc", None, None),
        (10.0, -1.0, D1),
        (10.0, -1.5, D1),
        (10.0, math.nan, D1),
        (10.0, 0.01, None),
        (10.0, None, D1),
        (10.0, 0.01, datetime(2026, 11, 2, 16, 0)),
    ],
)
def test_bar_rejects_invalid_values(close, ret, prev):
    with pytest.raises(EtfBarError):
        EtfBar(close, ret, prev)


def test_bar_is_frozen():
    bar = EtfBar(10.0)
    with pytest.raises(AttributeError):
        bar.close = 11.0  # type: ignore[misc]


def test_errors_are_value_errors_and_missing_is_the_forward_sources_class():
    assert issubclass(EtfBarError, sources.SourceError)
    assert issubclass(EtfBarError, ValueError)
    assert Missing is sources.Missing
    assert issubclass(NotReady, SourceUnavailable)
    assert not issubclass(SourceUnavailable, ValueError)


# --- day normalisation ---------------------------------------------------------------------


def test_normalize_day_sorts_copies_and_checks_prev_date():
    raw = {"QQQ": EtfBar(1.0, 0.0, D1), "BIL": {"close": 2.0, "ret": None, "prev_date": None}}
    day = normalize_etf_day(raw, D2)
    assert list(day) == ["BIL", "QQQ"]
    assert day["BIL"] == EtfBar(2.0)
    with pytest.raises(EtfBarError, match="not before"):
        normalize_etf_day({"QQQ": EtfBar(1.0, 0.0, D2)}, D2)
    with pytest.raises(EtfBarError, match="bad symbol"):
        normalize_etf_day({"qqq": EtfBar(1.0)}, D2)
    assert isinstance(normalize_etf_day({}, D2), Missing)
    m = Missing("halted")
    assert normalize_etf_day(m, D2) is m


# --- warm-up JSONL -------------------------------------------------------------------------


def test_warmup_round_trip_and_sha256_equals_file_hash(tmp_path):
    path = tmp_path / "warm.jsonl"
    digest = dump_etf_warmup(_rows(), path)
    assert digest == hashlib.sha256(path.read_bytes()).hexdigest()
    assert digest == etf_history_sha256(_rows())
    loaded = load_etf_warmup(path)
    assert [r.date for r in loaded] == [D1, D2, D3]
    assert loaded[1].bars["QQQ"] == EtfBar(505.0, 0.01, D1)
    assert etf_history_sha256(loaded) == digest
    first = path.read_text().splitlines()[0]
    assert first == (
        '{"bars":{"BIL":{"close":91.5,"prev_date":null,"ret":null},'
        '"QQQ":{"close":500.0,"prev_date":null,"ret":null}},"date":"2026-11-02"}'
    )


def test_warmup_dump_refuses_to_overwrite(tmp_path):
    path = tmp_path / "warm.jsonl"
    dump_etf_warmup(_rows(), path)
    with pytest.raises(FileExistsError):
        dump_etf_warmup(_rows(), path)


def test_warmup_accepts_date_bars_tuples():
    rows = [(r.date, dict(r.bars)) for r in _rows()]
    assert etf_history_sha256(rows) == etf_history_sha256(_rows())


def test_warmup_rejects_unordered_rows():
    rows = _rows()
    with pytest.raises(EtfBarError, match="strictly ascending"):
        etf_history_sha256([rows[0], rows[2], rows[1]])
    with pytest.raises(EtfBarError, match="strictly ascending"):
        etf_history_sha256([rows[0], rows[0]])


def test_warmup_rejects_a_broken_prev_date_chain():
    bad = [
        EtfDayRow(D1, {"QQQ": EtfBar(500.0)}),
        EtfDayRow(D2, {"QQQ": EtfBar(505.0, 0.01, date(2026, 10, 30))}),
    ]
    with pytest.raises(EtfBarError, match="previous row"):
        etf_history_sha256(bad)
    late_none = [EtfDayRow(D1, {"QQQ": EtfBar(500.0)}), EtfDayRow(D2, {"QQQ": EtfBar(505.0)})]
    with pytest.raises(EtfBarError, match="previous row"):
        etf_history_sha256(late_none)


def test_warmup_allows_a_symbol_gap_measured_from_its_last_row():
    rows = [
        EtfDayRow(D1, {"QQQ": EtfBar(500.0), "USO": EtfBar(70.0)}),
        EtfDayRow(D2, {"QQQ": EtfBar(505.0, 0.01, D1)}),
        EtfDayRow(D3, {"QQQ": EtfBar(500.0, -0.0099, D2), "USO": EtfBar(71.4, 0.02, D1)}),
    ]
    assert len(etf_history_sha256(rows)) == 64


def test_load_warmup_rejects_bad_lines(tmp_path):
    path = tmp_path / "bad.jsonl"
    path.write_text('{"date": "2026-11-02", "bars": {"QQQ": {"close": 1.0}}}\n')
    with pytest.raises(EtfBarError, match="exactly close, ret, prev_date"):
        load_etf_warmup(path)
    path.write_text("not json\n")
    with pytest.raises(EtfBarError, match="not JSON"):
        load_etf_warmup(path)
    path.write_text('{"date": "2026-11-02", "bars": {}}\n')
    with pytest.raises(EtfBarError, match="at least one bar"):
        load_etf_warmup(path)


# --- sources -------------------------------------------------------------------------------


def test_in_memory_source_returns_copies_missing_and_raises_unavailable():
    src = InMemoryEtfSource(
        {D1: {"QQQ": EtfBar(500.0)}, D2: Missing("halted"), D3: SourceUnavailable("timeout")}
    )
    assert isinstance(src, EtfBarSource)
    day = src.bars(D1)
    assert day == {"QQQ": EtfBar(500.0)}
    day["BIL"] = EtfBar(1.0)  # type: ignore[index]
    assert "BIL" not in src.bars(D1)
    assert src.bars(D2) == Missing("halted")
    with pytest.raises(SourceUnavailable, match="timeout"):
        src.bars(D3)
    assert isinstance(src.bars(date(2026, 11, 5)), Missing)


CSV_OK = """# manual entry
trade_date,symbol,close,ret,prev_date
2026-11-02,QQQ,500.0,,
2026-11-03,QQQ,505.0,0.01,2026-11-02
2026-11-03,BIL,91.51,0.0001,2026-11-02
"""


def test_csv_source_reads_rows(tmp_path):
    path = tmp_path / "etf.csv"
    path.write_text(CSV_OK)
    src = CsvEtfSource(path, symbols=["QQQ", "BIL"])
    assert isinstance(src, EtfBarSource)
    assert src.bars(D1) == {"QQQ": EtfBar(500.0)}
    assert src.bars(D2) == {"BIL": EtfBar(91.51, 0.0001, D1), "QQQ": EtfBar(505.0, 0.01, D1)}
    assert isinstance(src.bars(D3), Missing)


@pytest.mark.parametrize(
    "body, match",
    [
        (CSV_OK + "2026-11-03,QQQ,506.0,0.01,2026-11-02\n", "duplicate"),
        (CSV_OK + "2026-11-04,XLE,80.0,,\n", "not in the universe"),
        (CSV_OK + "2026-11-04,QQQ,500.0,0.01,\n", "both be set"),
        (CSV_OK + "2026-11-04,QQQ,-5,,\n", "close must be > 0"),
        (CSV_OK + "2026-11-04,QQQ,500.0,0.01,2026-11-04\n", "not before"),
        (CSV_OK + "2026-11-04,QQQ,500.0\n", "expected 5 fields"),
        ("trade_date,instrument,close,ret,prev_date\n", "header must be"),
        ("# only a comment\n", "no header row"),
    ],
)
def test_csv_source_rejects_malformed_files(tmp_path, body, match):
    path = tmp_path / "etf.csv"
    path.write_text(body)
    with pytest.raises(EtfBarError, match=match):
        CsvEtfSource(path, symbols=["QQQ", "BIL"]).bars(D1)
