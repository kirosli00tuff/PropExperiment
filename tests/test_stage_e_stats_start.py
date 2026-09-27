"""Known-answer tests for the Stage E D4 start rule (screening/stage_e_stats_start.py).

The D.1f result (reports/stage_d1f_step5_start_rule.json: V_ref 1763, S = 2020-02-03, 0.15 ->
2020-01-02, 0.40 -> 2020-03-02) is reproduced from its recorded monthly medians and first dates.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest

from screening import stage_e_stats_start as st

REPO = Path(__file__).resolve().parents[1]
D1F_START = REPO / "reports" / "stage_d1f_step5_start_rule.json"


@pytest.fixture(scope="module")
def d1f() -> dict:
    return json.loads(D1F_START.read_text(encoding="utf-8"))["start_rule"]


def _first_dates(d1f_rule: dict) -> dict[str, date]:
    return {m: date.fromisoformat(v) for m, v in d1f_rule["extension_first_trade_dates"].items()}


def test_reproduces_the_d1f_mes_start_rule(d1f) -> None:
    result = st.start_rule(
        "MES", d1f["reference_monthly_medians"], d1f["extension_monthly_medians"], _first_dates(d1f)
    )
    assert result.v_ref == d1f["v_ref"] == 1763.0
    assert result.binding.fraction == 0.25
    assert result.binding.threshold == d1f["binding"]["threshold"]
    assert result.binding.m_star == "2020-02"
    assert result.s_x == date(2020, 2, 3) == date.fromisoformat(d1f["S"])
    assert result.empty_window is False
    sens = {s.fraction: s for s in result.sensitivity}
    for recorded in d1f["sensitivity"]:
        ours = sens[recorded["fraction"]]
        assert ours.threshold == pytest.approx(recorded["threshold"])
        assert ours.m_star == recorded["m_star"]
        assert ours.s.isoformat() == recorded["s"]


def test_constants_are_the_frozen_text() -> None:
    assert st.REFERENCE_MONTHS[0] == "2025-04" and st.REFERENCE_MONTHS[-1] == "2026-05"
    assert len(st.REFERENCE_MONTHS) == 14
    assert st.EXTENSION_MONTHS[0] == "2019-05" and st.EXTENSION_MONTHS[-1] == "2024-02"
    assert len(st.EXTENSION_MONTHS) == 58
    assert st.BINDING_FRACTION == 0.25 and st.SENSITIVITY_FRACTIONS == (0.15, 0.40)
    assert date(2019, 5, 6) == st.EARLIEST_START


def _flat(value: float) -> dict[str, float]:
    return {m: value for m in st.REFERENCE_MONTHS}


def _all_first_dates() -> dict[str, date]:
    out = {}
    for m in st.EXTENSION_MONTHS:
        y, mo = int(m[:4]), int(m[5:])
        out[m] = date(2019, 5, 6) if m == "2019-05" else date(y, mo, 2)
    return out


def test_month_exactly_at_the_threshold_qualifies() -> None:
    ext = {m: 25.0 for m in st.EXTENSION_MONTHS}  # 0.25 x 100 = 25.0 exactly
    result = st.start_rule("X", _flat(100.0), ext, _all_first_dates())
    assert result.binding.m_star == "2019-05"
    assert result.s_x == date(2019, 5, 6)


def test_a_failing_month_moves_the_start_after_it() -> None:
    ext = {m: 50.0 for m in st.EXTENSION_MONTHS}
    ext["2021-07"] = 24.99
    result = st.start_rule("X", _flat(100.0), ext, _all_first_dates())
    assert result.binding.m_star == "2021-08"
    assert result.s_x == date(2021, 8, 2)
    # 0.15 x 100 = 15: 24.99 qualifies there, so the descriptive start is the earliest month
    assert result.sensitivity[0].m_star == "2019-05"
    # 0.40 x 100 = 40: same as binding
    assert result.sensitivity[1].m_star == "2021-08"


def test_last_month_failing_empties_the_window() -> None:
    ext = {m: 50.0 for m in st.EXTENSION_MONTHS}
    ext["2024-02"] = 10.0
    result = st.start_rule("X", _flat(100.0), ext, _all_first_dates())
    assert result.binding.m_star is None and result.s_x is None and result.empty_window is True


def test_a_month_without_bars_cannot_qualify() -> None:
    ext: dict[str, float | None] = {m: 50.0 for m in st.EXTENSION_MONTHS}
    ext["2022-03"] = None
    del ext["2020-06"]
    result = st.start_rule("X", _flat(100.0), ext, _all_first_dates())
    assert result.binding.m_star == "2022-04"


def test_short_history_product_starts_at_its_listing() -> None:
    # a micro listed in 2021-05: no bars before, so no month before can qualify
    ext = {m: 40.0 for m in st.EXTENSION_MONTHS if m >= "2021-05"}
    first = {m: d for m, d in _all_first_dates().items() if m >= "2021-05"}
    result = st.start_rule("MBT", _flat(100.0), ext, first)
    assert result.s_x == date(2021, 5, 2)


def test_v_ref_is_the_median_of_the_fourteen_monthly_medians() -> None:
    ref = {m: float(i) for i, m in enumerate(st.REFERENCE_MONTHS)}  # 0..13, median 6.5
    ext = {m: 10.0 for m in st.EXTENSION_MONTHS}
    result = st.start_rule("X", ref, ext, _all_first_dates())
    assert result.v_ref == 6.5
    assert result.binding.threshold == pytest.approx(1.625)


@pytest.mark.parametrize(
    "mutate,message",
    [
        (lambda r, e: r.pop("2025-09"), "missing"),
        (lambda r, e: r.update({"2026-06": 5.0}), "outside"),
        (lambda r, e: e.update({"2024-03": 50.0}), "outside"),
        (lambda r, e: e.update({"2019-04": 50.0}), "outside"),
        (lambda r, e: r.update({"2025-04": float("nan")}), "finite"),
        (lambda r, e: e.update({"2020-01": -1.0}), "finite"),
        (lambda r, e: r.update({"2025-04": None}), "finite"),
    ],
)
def test_input_refusals(mutate, message) -> None:
    ref = _flat(100.0)
    ext: dict = {m: 50.0 for m in st.EXTENSION_MONTHS}
    mutate(ref, ext)
    with pytest.raises(ValueError, match=message):
        st.start_rule("X", ref, ext, _all_first_dates())


def test_zero_reference_volume_is_refused() -> None:
    ext = {m: 50.0 for m in st.EXTENSION_MONTHS}
    with pytest.raises(ValueError, match="V_ref = 0"):
        st.start_rule("X", _flat(0.0), ext, _all_first_dates())


def test_first_date_rules() -> None:
    ext = {m: 50.0 for m in st.EXTENSION_MONTHS}
    early = _all_first_dates()
    early["2019-05"] = date(2019, 5, 1)
    with pytest.raises(ValueError, match="2019-05-06"):
        st.start_rule("X", _flat(100.0), ext, early)
    wrong_month = _all_first_dates()
    wrong_month["2020-01"] = date(2020, 2, 3)
    with pytest.raises(ValueError, match="not in its month"):
        st.start_rule("X", _flat(100.0), ext, wrong_month)
    missing = _all_first_dates()
    del missing["2019-05"]
    with pytest.raises(ValueError, match="no trade date with bars"):
        st.start_rule("X", _flat(100.0), ext, missing)


def test_first_trade_dates_by_month_applies_the_earliest_start() -> None:
    days = [date(2019, 5, 1), date(2019, 5, 3), date(2019, 5, 7), date(2019, 5, 6),
            date(2019, 6, 3), date(2024, 2, 29), date(2019, 4, 30)]
    out = st.first_trade_dates_by_month(days)
    assert out == {"2019-05": date(2019, 5, 6), "2019-06": date(2019, 6, 3),
                   "2024-02": date(2024, 2, 29)}
    with pytest.raises(ValueError, match="2024-02-29"):
        st.first_trade_dates_by_month([date(2024, 3, 1)])
