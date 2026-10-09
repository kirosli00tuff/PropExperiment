"""base_rules statistics, power, inputs, costs and constants (synthetic and frozen files only)."""

from __future__ import annotations

import math
from datetime import date

import numpy as np
import pytest

from base_rules import constants as K
from base_rules.auctions import auctions_from_rows
from base_rules.costs import build_release_rules, combine_rows
from base_rules.inputs import (
    InputError,
    settlement_from_dict,
    window_starts_from_quotes,
    windows_from_dict,
)
from base_rules.power import analytic_power, simulate_pass
from base_rules.stats import holm, newey_west_se, unit_stats, verdict, year_table
from tests._base_rules_fixtures import settlement_payload


# ------------------------------------------------------------------ statistics ----
def test_holm_steps_down_and_stops_at_the_first_non_rejection() -> None:
    got = holm({"H1": 0.009, "H2": 0.012, "H3": 0.02, "H4": 0.5, "H5": None})
    assert got == {"H1": True, "H2": True, "H3": False, "H4": False, "H5": False}
    assert holm({"a": 0.011, "b": 0.001}) == {"a": True, "b": True}
    assert holm({"a": 0.051, "b": 0.001}) == {"a": False, "b": True}


def test_newey_west_with_no_lag_is_the_population_standard_error() -> None:
    x = np.random.default_rng(1).normal(0, 1, 500)
    assert newey_west_se(x, 0) == pytest.approx(x.std() / math.sqrt(len(x)))


def test_the_one_sided_p_is_the_larger_of_t_and_newey_west() -> None:
    x = np.cumsum(np.random.default_rng(2).normal(0.0, 1.0, 400)) * 0.01 + 0.05
    s = unit_stats(list(x), 5)
    assert s["p"] == max(s["p_t"], s["p_nw"])
    assert s["t"] == pytest.approx(x.mean() / (x.std(ddof=1) / math.sqrt(len(x))))


def test_year_stability_needs_two_thirds_of_three_or_more_qualifying_years() -> None:
    def series(spec):  # noqa: ANN001, ANN202
        return [(date(y, 1, 1 + k), v) for y, n, v in spec for k in range(n)]

    assert year_table(series([(2011, 10, 1), (2012, 10, 1), (2013, 10, -1)]), 10)["passes"]
    assert not year_table(series([(2011, 10, 1), (2012, 10, -1), (2013, 10, -1)]), 10)["passes"]
    assert not year_table(series([(2011, 10, 1), (2012, 10, 1), (2013, 9, 1)]), 10)["passes"]
    assert year_table(series([(2011, 6, 1), (2012, 6, 1), (2013, 6, 1)]), 6)["passes"]


def test_the_verdict_needs_every_bar() -> None:
    def st(p, mean, n, years):  # noqa: ANN001, ANN202
        return {K.BASE: {"p": p, "mean": mean, "n": n, "year_stability": {"passes": years}}}

    v = verdict({"H1": st(0.001, 1.0, 100, True), "H2": st(0.001, 1.0, 20, True),
                 "H3": st(0.001, -1.0, 100, True), "H4": st(0.001, 1.0, 100, False),
                 "H5": st(0.2, 1.0, 100, True)})["tests"]
    assert [t for t, r in v.items() if r["pass"]] == ["H1"]


# ------------------------------------------------------------------ power ----
def test_simulated_power_matches_the_analytic_t_power_without_the_year_bar() -> None:
    per_year = {str(y): 250 for y in range(2011, 2024)}
    row = simulate_pass("H1", per_year, 0.8, n_sim=600)
    for a in ("0.01", "0.05"):
        assert row["sim_p_and_mean_only"][a] == pytest.approx(row["analytic_t_power"][a],
                                                              abs=0.08)
    assert simulate_pass("H1", per_year, 0.8, n_sim=600) == row  # fixed seed
    assert analytic_power(3000, 0.05, 0.05) > analytic_power(3000, 0.05, 0.01)


# ------------------------------------------------------------------ inputs ----
def test_the_settlement_table_must_tile_the_window_with_known_grades() -> None:
    raw = settlement_payload()
    assert settlement_from_dict(raw, "x", "t").settle_minute("NQ", date(2015, 1, 5)) == 900
    gap = settlement_payload(overrides={"NQ": [
        {"from": "2010-06-07", "to": "2015-01-01", "minute_ct": "15:15", "grade": "primary",
         "lead_grade": "primary"},
        {"from": "2015-01-03", "to": "2024-02-29", "minute_ct": "15:00", "grade": "primary",
         "lead_grade": "primary"}]})
    with pytest.raises(InputError, match="gap or overlap"):
        settlement_from_dict(gap, "x", "t")
    bad = settlement_payload(overrides={"NQ": [
        {"from": "2010-06-07", "to": "2024-02-29", "minute_ct": "15:00", "grade": "primary"}]})
    with pytest.raises(InputError, match="lead_grade"):
        settlement_from_dict(bad, "x", "t")


def test_the_h1_h4_grade_is_the_lead_grade_and_null_minutes_are_not_listed() -> None:
    raw = settlement_payload(overrides={"LE": [
        {"from": "2010-06-07", "to": "2014-12-14", "minute_ct": "13:00", "grade": "primary",
         "lead_grade": "weak"},
        {"from": "2014-12-15", "to": "2024-02-29", "minute_ct": "13:00", "grade": "weak",
         "lead_grade": "primary"}],
        "TN": [{"from": "2010-06-07", "to": "2016-01-10", "minute_ct": None, "grade": "primary",
                "lead_grade": "primary"},
               {"from": "2016-01-11", "to": "2024-02-29", "minute_ct": "14:00",
                "grade": "primary", "lead_grade": "primary"}]},
        opens={"LE": [{"from": "2010-06-07", "to": "2014-10-26", "minute_ct": "09:05"},
                      {"from": "2014-10-27", "to": "2016-02-28", "minute_ct": "08:00",
                       "first_business_day_of_week_minute_ct": "09:05"},
                      {"from": "2016-02-29", "to": "2024-02-29", "minute_ct": "08:30"}]})
    st = settlement_from_dict(raw, "x", "t")
    assert not st.sourced("LE", date(2012, 5, 1)) and st.sourced("LE", date(2015, 5, 1))
    assert not st.listed("TN", date(2015, 5, 1)) and st.listed("TN", date(2016, 1, 11))
    assert st.open_minute("LE", date(2015, 3, 2), True) == 545
    assert st.open_minute("LE", date(2015, 3, 3), False) == 480


def test_window_starts_follow_u2_from_the_quote_record() -> None:
    got = window_starts_from_quotes()
    for p in K.PRODUCTS:
        assert got[p].replace(day=1) == K.WINDOW_START[p].replace(day=1), p
    raw = {"schema": K.WINDOWS_SCHEMA, "fallback_window": ["2019-05-06", "2024-02-29"],
           "products": {p: {"window_start_on_or_after": str(K.WINDOW_START[p]),
                            "window_end": "2024-02-29"} for p in K.PRODUCTS}}
    assert windows_from_dict(raw, "w") == dict(K.WINDOW_START)


def test_ec_auc_rows_keep_the_four_tenors_and_apply_e0_where_the_fields_exist() -> None:
    def row(i, tenor, **kw):  # noqa: ANN001, ANN202
        return {"id": f"TREASURY_AUCTION-2012-01-{i:02d}-{tenor}", "release": "TREASURY_AUCTION",
                "date": f"2012-01-{i:02d}", "instant_utc": "2012-01-10T18:00:00Z", **kw}

    rows = [row(3, "10Y"), row(4, "7Y"), row(5, "2Y", security_type="Note", floating_rate="No",
                                           inflation_index_security="No",
                                           announcemt_date="2012-01-05",
                                           original_security_term="2-Year"),
            row(6, "5Y", security_type="Note", floating_rate="Yes", inflation_index_security="No",
                announcemt_date="2012-01-01", original_security_term="5-Year"),
            {"id": "NFP-x", "release": "NFP", "date": "2012-01-06"}]
    got, dropped = auctions_from_rows(rows, "t")
    assert [(a.tenor, a.root) for a in got] == [("10Y", "ZN")]
    assert dropped == {"tenor not 2Y, 5Y, 10Y or 30Y": 1,
                       "announced on or after the auction date": 1,
                       "floating or inflation-indexed": 1}


def test_frozen_auction_rows_take_their_announcement_date_from_the_announcements_file(
        tmp_path) -> None:
    import json

    from base_rules.auctions import load_announcements

    row = {"id": "TREASURY_AUCTION-2020-05-12-10Y", "release": "TREASURY_AUCTION",
           "date": "2020-05-12", "instant_utc": "2020-05-12T17:00:00Z"}
    ann = {row["id"]: {"id": row["id"], "auction_date": "2020-05-12", "tenor": "10Y",
                       "announcemt_date": "2020-05-06", "security_type": "Note",
                       "floating_rate": "No", "inflation_index_security": "No",
                       "original_security_term": "10-Year"}}
    got, _ = auctions_from_rows([row], "t", announcements=ann)
    assert got[0].announced == date(2020, 5, 6) and got[0].root == "ZN"
    got, _ = auctions_from_rows([row], "t")
    assert got[0].announced is None  # no date on file: H3 excludes it ("no announcement date")
    with pytest.raises(InputError, match="tenor"):
        auctions_from_rows([row], "t", announcements={row["id"]: {**ann[row["id"]],
                                                                  "tenor": "2Y"}})
    path = tmp_path / "a.json"
    path.write_text(json.dumps({"schema": "wrong", "rows": []}))
    with pytest.raises(InputError, match="schema"):
        load_announcements(path)
    path.write_text(json.dumps({"schema": K.ANNOUNCEMENTS_SCHEMA, "rows": list(ann.values())}))
    assert load_announcements(path)[0][row["id"]]["announcemt_date"] == "2020-05-06"


# ------------------------------------------------------------------ costs ----
def test_a_hist_row_without_an_instant_takes_every_clock_time_of_its_type() -> None:
    frozen = [{"id": "W1", "release": "WPSR", "date": "2020-01-08",
               "instant_utc": "2020-01-08T15:30:00Z", "products": ["CL"]}]
    hist = [{"id": "W0", "release": "WPSR", "date": "2012-11-01", "instant_utc": None,
             "products": ["CL"]},
            {"id": "W2", "release": "WPSR", "date": "2012-11-08",
             "instant_utc": "2012-11-08T16:00:00Z", "products": ["CL"]}]
    rows, rec = combine_rows(frozen, hist, [])
    assert rec["expanded_no_instant"] == ["W0"]
    assert sorted(r["instant_utc"] for r in rows if r["id"].startswith("W0@")) == [
        "2012-11-01T14:30:00Z", "2012-11-01T15:00:00Z"]


def test_a_touching_type_without_2010_2019_rows_gets_the_conservative_fallback() -> None:
    from datetime import time

    from data.session import ct_ns

    rules = build_release_rules(touching={"CROP_PROGRESS": ["ZC"], "FOMC": ["CL"]},
                                auctions_path=None)
    assert "CROP_PROGRESS" not in rules.hist_types and "FOMC" in rules.hist_types
    assert rules.fallback["ZC"] == (15 * 60, 16 * 60)  # 16:00 ET and one 17:00 ET row
    t = ct_ns(date(2014, 6, 2), time(15, 1))
    assert rules.guard("ZC", t) and rules.event("ZC", t)
    assert not rules.guard("ZC", ct_ns(date(2014, 6, 2), time(15, 2)))
    assert rules.event("ZC", ct_ns(date(2014, 6, 2), time(15, 29)))
    assert not rules.event("ZC", ct_ns(date(2020, 6, 2), time(15, 31)))
    fomc = ct_ns(date(2015, 3, 18), time(13, 0))  # an E.14 FOMC row, 14:00 ET
    assert rules.guard("CL", fomc) and rules.guard("MCL", fomc)


# ------------------------------------------------------------------ constants ----
def test_vehicles_are_e12s_and_share_the_price_path_tick_grid() -> None:
    from ml_route_v2.constants import UNIVERSE
    from rules.products import product

    assert {path: v for v, (_c, path) in UNIVERSE.items() if v != "MBT"} == dict(K.VEHICLE_OF)
    for p, v in K.VEHICLE_OF.items():
        assert product(p).vendor_tick_fixed == product(v).vendor_tick_fixed, p
    assert len(K.PRODUCTS) == 27 and "MBT" not in K.PRODUCTS
