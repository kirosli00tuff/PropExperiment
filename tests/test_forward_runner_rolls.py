"""forward.rolls and forward/rolls_f1.json (E.22, ForwardRunnerCoder). Synthetic dates only."""

from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

import pytest

from forward import rolls as R

ROOT = Path(__file__).resolve().parents[1]
UNIVERSE = ("MNQ", "M2K", "MGC", "MCL", "MNG", "M6E", "2YY", "10Y", "30Y", "MZC", "MZS", "MZL")


def _doc(**overrides):
    entry = {
        "root": "AAA",
        "cycle": "HMUZ",
        "cycle_source": "test",
        "anchor": {"kind": "nth_weekday", "weekday": 4, "nth": 3, "month_offset": 0},
        "n_bdays": 6,
    }
    entry.update(overrides)
    return {"status": R.CHECK_FLAG, "instruments": {"AAA": entry}}


def test_declared_file_covers_the_universe_and_carries_the_check_flag():
    raw = json.loads(R.DEFAULT_ROLLS_PATH.read_text(encoding="utf-8"))
    specs = R.load_rolls()
    assert set(specs) == set(UNIVERSE)
    assert R.CHECK_FLAG in raw["status"]
    for name, entry in raw["instruments"].items():
        assert entry["cycle_source"].startswith("F46"), name
        assert any(R.CHECK_FLAG in f for f in entry["flags"]), name
        assert entry["anchor_source"], name


def test_cited_saved_pages_exist_and_contain_the_quoted_cycles():
    raw = json.loads(R.DEFAULT_ROLLS_PATH.read_text(encoding="utf-8"))
    text = re.sub(
        r"\s+",
        " ",
        (ROOT / "reports/stage_e13_briefs/pages/TrendCarry/amp_contract_specs.txt").read_text(
            encoding="utf-8"
        ),
    )
    normalised = re.sub(r"\s*\|\s*", " | ", text)
    for name, entry in raw["instruments"].items():
        quote = entry["cycle_source"].split("'")[1]
        assert " | ".join(c.strip() for c in quote.split("|")) in normalised, name
        cycle_cell = quote.split("|")[4].strip()
        if cycle_cell != "All":
            assert set(cycle_cell.split(",")) == set(entry["cycle"]), name
        else:
            assert entry["cycle"] == "FGHJKMNQUVXZ", name


def test_no_cmegroup_url_is_fetched_directly():
    raw = json.loads(R.DEFAULT_ROLLS_PATH.read_text(encoding="utf-8"))
    for key, src in raw["sources"].items():
        url = src.get("url", "")
        assert not url.startswith("https://www.cmegroup.com"), key
        assert not url.startswith("http://www.cmegroup.com"), key


def test_bdays_before_skips_weekends():
    assert R.bdays_before(date(2026, 12, 18), 6) == date(2026, 12, 10)
    assert R.bdays_before(date(2026, 12, 1), 1) == date(2026, 11, 30)
    assert R.bdays_before(date(2026, 11, 30), 1) == date(2026, 11, 27)  # Monday -> Friday


def test_equity_style_roll_date_and_active_contract_switch():
    spec = R.parse_rolls(_doc())["AAA"]
    assert R.anchor_date(spec.anchor, 2026, 12) == date(2026, 12, 18)
    assert R.roll_date(spec, 2026, 12) == date(2026, 12, 10)
    assert R.active_contract(spec, date(2026, 12, 9)) == "AAAZ26"
    assert R.active_contract(spec, date(2026, 12, 10)) == "AAAH27"
    assert not R.is_roll_due(spec, "AAAZ26", date(2026, 12, 9))
    assert R.is_roll_due(spec, "AAAZ26", date(2026, 12, 10))
    assert R.expiry_guard(spec, "AAAZ26") == date(2026, 12, 18)


def test_prior_month_calendar_anchor_like_mcl():
    spec = R.load_rolls()["MCL"]
    # F27 rolls 10 weekdays before 2026-12-25 (a Friday): 2026-12-11.
    assert R.roll_date(spec, 2027, 1) == date(2026, 12, 11)
    assert R.active_contract(spec, date(2026, 12, 10)) == "MCLF27"
    assert R.active_contract(spec, date(2026, 12, 11)) == "MCLG27"


def test_every_declared_instrument_has_one_roll_per_listed_month():
    specs = R.load_rolls()
    for name, spec in specs.items():
        rows = R.roll_schedule(spec, date(2027, 1, 1), date(2027, 12, 31))
        assert len(rows) == len(spec.months), name
        assert all(r["roll_date"] < r["anchor_date"] for r in rows), name
        assert all(date.fromisoformat(r["roll_date"]).weekday() < 5 for r in rows), name


def test_contract_id_round_trip_and_refusals():
    spec = R.load_rolls()["10Y"]
    assert R.contract_id(spec, 2027, 3) == "10YH27"
    assert R.parse_contract(spec, "10YH27") == (2027, 3)
    with pytest.raises(ValueError):
        R.parse_contract(spec, "30YH27")
    with pytest.raises(ValueError):
        R.parse_contract(spec, "10YF27")  # January is not in the HMUZ cycle
    with pytest.raises(ValueError):
        R.contract_id(spec, 2027, 1)


@pytest.mark.parametrize(
    "bad",
    [
        {"cycle": "HMUA"},
        {"cycle": "HHMU"},
        {"n_bdays": 0},
        {"root": "aa"},
        {"anchor": {"kind": "eom", "month_offset": 0}},
        {"anchor": {"kind": "calendar_day", "day": 31, "month_offset": 0}},
        {"anchor": {"kind": "nth_weekday", "weekday": 5, "nth": 3, "month_offset": 0}},
        {"cycle_source": ""},
    ],
)
def test_malformed_roll_entries_are_refused(bad):
    with pytest.raises(R.RollConfigError):
        R.parse_rolls(_doc(**bad))


def test_status_flag_is_required():
    doc = _doc()
    doc["status"] = "checked"
    with pytest.raises(R.RollConfigError):
        R.parse_rolls(doc)


def test_forward_runner_modules_have_no_network_or_vendor_code():
    banned = re.compile(
        r"^\s*(import|from)\s+(requests|urllib|http|socket|databento|aiohttp|httpx)\b", re.M
    )
    for name in ("runner", "ledger", "sources", "rolls", "evaluate", "report", "history"):
        source = (ROOT / "forward" / f"{name}.py").read_text(encoding="utf-8")
        assert not banned.search(source), name
        assert "cmegroup" not in source, name
