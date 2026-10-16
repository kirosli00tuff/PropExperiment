"""forward.sources (E.22, ForwardRunnerCoder). Synthetic data only."""

from __future__ import annotations

from datetime import date

import pytest

from forward.sources import (
    CsvSettlementSource,
    InMemorySettlementSource,
    Missing,
    SettlementSource,
    SourceError,
    normalize_day,
)

HEADER = "trade_date,instrument,contract_id,settlement\n"


def _csv(tmp_path, body: str, name: str = "s.csv"):
    path = tmp_path / name
    path.write_text(body, encoding="utf-8")
    return path


def test_csv_source_reads_several_contracts_per_instrument(tmp_path):
    path = _csv(
        tmp_path,
        "# manual entry\n"
        + HEADER
        + "2026-11-02,MNQ,MNQZ26,21034.25\n2026-11-02,MCL,MCLF27,71.42\n"
        "2026-11-02,MCL,MCLG27,71.10\n2026-11-03,MNQ,MNQZ26,21100\n",
    )
    src = CsvSettlementSource(path, instruments=["MNQ", "MCL"])
    assert isinstance(src, SettlementSource)
    day = src.settlements(date(2026, 11, 2))
    assert day == {"MCL": {"MCLF27": 71.42, "MCLG27": 71.10}, "MNQ": {"MNQZ26": 21034.25}}
    assert src.settlements(date(2026, 11, 3)) == {"MNQ": {"MNQZ26": 21100.0}}


def test_csv_date_without_rows_is_missing(tmp_path):
    src = CsvSettlementSource(_csv(tmp_path, HEADER + "2026-11-02,MNQ,MNQZ26,1\n"))
    assert isinstance(src.settlements(date(2026, 11, 4)), Missing)


def test_csv_sees_rows_appended_between_calls(tmp_path):
    path = _csv(tmp_path, HEADER + "2026-11-02,MNQ,MNQZ26,1\n")
    src = CsvSettlementSource(path)
    assert isinstance(src.settlements(date(2026, 11, 3)), Missing)
    with open(path, "a", encoding="utf-8") as fh:
        fh.write("2026-11-03,MNQ,MNQZ26,2\n")
    assert src.settlements(date(2026, 11, 3)) == {"MNQ": {"MNQZ26": 2.0}}


@pytest.mark.parametrize(
    "row",
    [
        "2026-11-02,MNQ,MNQZ26,abc\n",
        "2026-11-02,MNQ,MNQZ26,nan\n",
        "2026-11-02,MNQ,MNQZ26,inf\n",
        "2026-13-02,MNQ,MNQZ26,1\n",
        "2026-11-02,MNQ,MNQ-Z26,1\n",
        "2026-11-02,mnq,MNQZ26,1\n",
        "2026-11-02,MNQ,MNQZ26\n",
        "2026-11-02,XXX,XXXZ26,1\n",
    ],
)
def test_csv_bad_rows_are_errors(tmp_path, row):
    src = CsvSettlementSource(_csv(tmp_path, HEADER + row), instruments=["MNQ"])
    with pytest.raises(SourceError):
        src.settlements(date(2026, 11, 2))


def test_csv_duplicate_rows_are_errors_not_last_wins(tmp_path):
    src = CsvSettlementSource(
        _csv(tmp_path, HEADER + "2026-11-02,MNQ,MNQZ26,1\n2026-11-02,MNQ,MNQZ26,2\n")
    )
    with pytest.raises(SourceError, match="duplicate"):
        src.settlements(date(2026, 11, 2))


def test_csv_header_is_required(tmp_path):
    src = CsvSettlementSource(_csv(tmp_path, "date,inst,cid,px\n2026-11-02,MNQ,MNQZ26,1\n"))
    with pytest.raises(SourceError, match="header"):
        src.settlements(date(2026, 11, 2))


def test_normalize_accepts_the_single_contract_tuple_form():
    assert normalize_day({"MNQ": ("MNQZ26", 100)}) == {"MNQ": {"MNQZ26": 100.0}}
    assert isinstance(normalize_day({}), Missing)
    with pytest.raises(SourceError):
        normalize_day({"MNQ": ("MNQZ26", True)})
    with pytest.raises(SourceError):
        normalize_day([("MNQ", 1.0)])


def test_in_memory_source_returns_copies_and_missing():
    d = date(2026, 11, 2)
    src = InMemorySettlementSource(
        {d: {"MNQ": {"MNQZ26": 1.0}}, date(2026, 11, 3): Missing("holiday test")}
    )
    first = src.settlements(d)
    first["MNQ"]["MNQZ26"] = 99.0
    assert src.settlements(d) == {"MNQ": {"MNQZ26": 1.0}}
    assert src.settlements(date(2026, 11, 3)) == Missing("holiday test")
    assert isinstance(src.settlements(date(2026, 11, 4)), Missing)
