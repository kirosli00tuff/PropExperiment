"""forward.report (E.22, ForwardRunnerCoder): the 6-monthly descriptive look. Synthetic only."""

from __future__ import annotations

from datetime import date, timedelta

import pytest

from forward.evaluate import max_drawdown
from forward.report import LookNotDue, flag_counts, render_markdown, six_month_look, turnover

START = date(2026, 11, 2)


def recs_until(end: date):
    out, d, k = [], START, 0
    while d <= end:
        if d.weekday() < 5:
            k += 1
            out.append(
                {
                    "date": d.isoformat(),
                    "net_pnl": 10.0 if k % 3 else -25.0,
                    "gross_pnl": 12.0,
                    "costs": {"fills": 1.5, "rolls": 0.5, "total": 2.0},
                    "fills": [{"qty": 2 if k % 2 else -1}],
                    "rolls": [],
                    "flags": ["missing:AAA"] if k % 50 == 0 else [],
                }
            )
        d += timedelta(days=1)
    return out


def test_look_is_refused_until_its_period_closes():
    with pytest.raises(LookNotDue):
        six_month_look(recs_until(date(2027, 4, 30)), 1)
    with pytest.raises(ValueError):
        six_month_look(recs_until(date(2027, 5, 3)), 7)


def test_look_one_figures_have_no_p_value_and_say_nothing_changes():
    look = six_month_look(recs_until(date(2027, 5, 3)), 1, capital=25_000.0)
    fig = look["period_figures"]
    assert look["period"] == ["2026-11-02", "2027-05-02"]
    assert fig["n_days"] == len([r for r in recs_until(date(2027, 5, 1))])
    assert fig == look["cumulative_figures"]
    banned = {"p_one_sided", "nw_t", "nw_se", "pass", "p_value", "t"}
    assert not banned & set(fig)
    assert fig["cost_total_usd"] == pytest.approx(2.0 * fig["n_days"])
    assert fig["cost_pct_capital"] == pytest.approx(100 * 2.0 * fig["n_days"] / 25_000)
    text = render_markdown(look)
    assert "this look changes nothing" in text.lower()
    assert "No p-value" in text


def test_second_look_splits_period_and_cumulative():
    look = six_month_look(recs_until(date(2027, 11, 2)), 2)
    assert look["period"] == ["2027-05-02", "2027-11-02"]
    assert (
        look["cumulative_figures"]["n_days"]
        == look["period_figures"]["n_days"]
        + six_month_look(recs_until(date(2027, 11, 2)), 1)["period_figures"]["n_days"]
    )


def test_max_drawdown_hand_examples():
    assert max_drawdown(["a", "b", "c", "d"], [1.0, -3.0, 1.0, 2.0]) == {
        "max_drawdown_usd": 3.0,
        "peak_date": "a",
        "trough_date": "b",
    }
    assert max_drawdown(["a", "b"], [-2.0, 1.0]) == {
        "max_drawdown_usd": 2.0,
        "peak_date": None,
        "trough_date": "a",
    }


def test_turnover_counts_fill_sides_and_both_roll_legs():
    rows = [
        {"fills": [{"qty": 2}, {"qty": -3}], "rolls": [{"qty": 2}]},
        {"fills": [], "rolls": [{"qty": -1}]},
    ]
    t = turnover(rows)
    assert t["contracts_traded_fills"] == 5 and t["contracts_traded_rolls"] == 6
    assert t["round_turns"] == 5.5
    assert t["round_turns_per_year"] == pytest.approx(5.5 / (2 / 252))


def test_flag_counts_by_kind():
    rows = [
        {"flags": ["missing:AAA", "order_expired:AAA", "missing:BBB"]},
        {"flags": ["missing_day"]},
        {"flags": []},
    ]
    assert flag_counts(rows) == {"missing": 2, "missing_day": 1, "order_expired": 1}
