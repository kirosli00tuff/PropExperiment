"""The two r_ROD features (reports/stage_e20_plan.md section 5.2) on synthetic bars: values computed
by hand from the bar frames, the early-halt, missing-bar, warm-up and zero-median cases,
availability at or before t, the causality canary and attach_rod's build_panel rules."""

from __future__ import annotations

from datetime import date, datetime, timedelta

import numpy as np
import pandas as pd
import pytest

from pattern_search import constants as K
from pattern_search.features import _rod_absratio, attach_rod, rod_frame, rod_z
from pattern_search.panel import context
from tests._pattern_search_synth import panel_small, rows_small, world_small

NS_MIN = 60_000_000_000
CT = "America/Chicago"


def _cal(vehicle: str):  # noqa: ANN202
    from data.calendars import GROUP_OF_PRODUCT
    from ml_route.inputs import _group_calendar

    return _group_calendar(GROUP_OF_PRODUCT[vehicle])


def _prev(vehicle: str, day: date) -> date | None:
    from data.group_session import previous_trade_date

    return previous_trade_date(_cal(vehicle), day)


def _close_ct(vehicle: str) -> str:
    from screening.stage_e_frozen import load_frozen_tables

    return load_frozen_tables().day_session_ct[vehicle][1].strftime("%H:%M")


def _bar_close(frame: pd.DataFrame, ts_ns: int, day: date) -> float:
    hit = frame.loc[(frame["ts_event"].to_numpy(np.int64) == ts_ns)
                    & (frame["trade_date"].astype(str).to_numpy() == day.isoformat())]
    return float(hit["close"].iloc[0]) if len(hit) else float("nan")


def _hand_rod_ret(w, row: pd.Series) -> tuple[float, bool]:  # noqa: ANN001
    """(value, applicable) of rod_ret on one row, from the bar frame alone."""
    v, path = row["root"], row["path_root"]
    day = pd.Timestamp(row["trade_date"]).date()
    frame = w.bars[path]
    p_t = _bar_close(frame, int(row["decision_ts_ns"]) - NS_MIN, day)
    prev = _prev(v, day)
    if prev is None:
        return float("nan"), True
    if _cal(v).early_halt_ct(prev) is not None:
        return 0.0, False
    c_ct = datetime.combine(prev, datetime.strptime(_close_ct(v), "%H:%M").time())
    c1 = int(pd.Timestamp(c_ct - timedelta(minutes=1)).tz_localize(CT).tz_convert("UTC").value)
    p_c = _bar_close(frame, c1, prev)
    return p_t / p_c - 1.0, True


@pytest.fixture(scope="module")
def rod() -> tuple[pd.DataFrame, pd.DataFrame]:
    w, rows = world_small(), rows_small()
    return rows, rod_frame(context(w, rows))


def test_rod_ret_equals_the_hand_computed_value_on_sampled_rows(rod) -> None:
    rows, frame = rod
    w = world_small()
    rng = np.random.default_rng(3)
    picks = []
    for v in K.VEHICLES:
        for k in (1, 2, 3, 4):
            idx = np.flatnonzero((rows["root"] == v).to_numpy() & (rows["t_index"] == k).to_numpy())
            picks += rng.choice(idx, size=2, replace=False).tolist()
    for i in picks:
        want, app = _hand_rod_ret(w, rows.iloc[i])
        got_app = frame["app_rod_ret"].iloc[i] > 0
        got = frame["raw_rod_ret"].iloc[i]
        assert got_app == app, (i, rows.iloc[i].to_dict())
        if app and np.isfinite(want):
            assert got == pytest.approx(want, rel=0, abs=1e-12), rows.iloc[i].to_dict()
        elif app:
            assert np.isnan(got)
    assert len(picks) == 17 * 4 * 2


def test_after_an_early_halt_date_both_features_are_not_applicable(rod) -> None:
    rows, frame = rod
    halted = np.array([_cal(v).early_halt_ct(_prev(v, pd.Timestamp(d).date()) or date(1970, 1, 1))
                       is not None for v, d in zip(rows["root"], rows["trade_date"], strict=True)])
    assert halted.sum() >= 4  # Good Friday 2021-04-02 and Memorial Day 2021-05-31 are in the window
    for n in K.ROD_SIGNALS:
        assert (frame[f"app_{n}"].to_numpy()[halted] == 0).all()
        assert (frame[f"raw_{n}"].to_numpy()[halted] == 0).all()
    assert (frame["app_rod_ret"].to_numpy()[~halted] == 1).all()


def test_a_missing_prior_close_bar_or_signal_bar_makes_the_value_missing() -> None:
    w, rows = world_small(), rows_small()
    v, path = "MNQ", "NQ"
    sel = rows.loc[(rows["root"] == v) & (rows["t_index"] == 2)]
    target = sel.iloc[80]
    day = pd.Timestamp(target["trade_date"]).date()
    prev = _prev(v, day)
    c_ct = datetime.combine(prev, datetime.strptime(_close_ct(v), "%H:%M").time())
    c1 = int(pd.Timestamp(c_ct - timedelta(minutes=1)).tz_localize(CT).tz_convert("UTC").value)
    other = sel.iloc[90]
    sig_bar = int(other["decision_ts_ns"]) - NS_MIN
    bars = dict(w.bars)
    nq = bars[path]
    bars[path] = nq.loc[~nq["ts_event"].isin([c1, sig_bar])].reset_index(drop=True)
    import dataclasses

    frame = rod_frame(context(dataclasses.replace(w, bars=bars), rows))
    for i in (target.name, other.name):
        assert frame.loc[i, "app_rod_ret"] == 1.0
        assert np.isnan(frame.loc[i, "raw_rod_ret"])
        assert frame.loc[i, "avail_rod_ret"] == -1
        assert np.isnan(frame.loc[i, "raw_rod_absratio"])
    # every t_index of the target's date loses the prior close (it is a per-date input)
    same_day = rows.index[(rows["root"] == v) & (rows["trade_date"] == target["trade_date"])]
    assert np.isnan(frame.loc[same_day, "raw_rod_ret"]).all()


def test_rod_absratio_warms_up_over_60_eligible_dates_then_equals_the_hand_median(rod) -> None:
    rows, frame = rod
    for v, k in (("MNQ", 1), ("ZC", 4), ("6E", 3), ("HE", 2)):
        sel = rows.index[(rows["root"] == v) & (rows["t_index"] == k)]
        order = rows.loc[sel].sort_values("trade_date").index
        r = frame.loc[order, "raw_rod_ret"].to_numpy()
        app = frame.loc[order, "app_rod_ret"].to_numpy() > 0
        elig = app & np.isfinite(r)
        ratio = frame.loc[order, "raw_rod_absratio"].to_numpy()
        pos = np.flatnonzero(elig)
        assert len(pos) > K.ROD_MEDIAN_DATES + 5
        assert np.isnan(ratio[pos[:K.ROD_MEDIAN_DATES]]).all()
        for j in range(K.ROD_MEDIAN_DATES, len(pos)):
            med = np.median(np.abs(r[pos[j - K.ROD_MEDIAN_DATES:j]]))
            assert ratio[pos[j]] == pytest.approx(abs(r[pos[j]]) / med, rel=1e-12)


def _fake_ctx(values: np.ndarray, apps: np.ndarray):  # noqa: ANN202
    from ml_route_v2.clock import ROW_COLUMNS
    from ml_route_v2.signals import SignalContext

    n = len(values)
    days = pd.bdate_range("2021-01-04", periods=n)
    t = (days + pd.Timedelta(hours=15)).tz_localize("UTC").asi8
    rows = pd.DataFrame({"root": "MNQ", "path_root": "NQ", "cluster": "K1", "group": "equity",
                         "trade_date": days.astype("datetime64[ns]"), "t_index": np.int8(1),
                         "decision_ts_ns": t, "flatten_ts_ns": t + 60 * NS_MIN},
                        columns=list(ROW_COLUMNS))
    ctx = SignalContext(rows, {}, None, pd.Series(1.0, index=rows.index))
    ret = pd.DataFrame({"value": np.where(apps, values, 0.0), "applicable": apps.astype(float),
                        "avail_ts_ns": np.where(apps & np.isfinite(values), t, -1)},
                       index=rows.index)
    return ctx, ret, t


def test_rod_absratio_hand_values_and_a_zero_median_is_not_applicable() -> None:
    vals = np.r_[np.linspace(-0.01, 0.01, 60), 0.02, np.nan, 0.005]
    apps = np.ones(len(vals), dtype=bool)
    apps[-2] = True  # applicable but missing: stays out of the window
    ctx, ret, t = _fake_ctx(vals, apps)
    out = _rod_absratio(ctx, ret)
    med60 = np.median(np.abs(vals[:60]))
    assert np.isnan(out["value"].iloc[:60]).all() and (out["applicable"].iloc[:60] == 1).all()
    assert out["value"].iloc[60] == pytest.approx(0.02 / med60)
    assert np.isnan(out["value"].iloc[61]) and out["avail_ts_ns"].iloc[61] == -1
    med_next = np.median(np.abs(np.r_[vals[1:60], 0.02]))  # the missing row is skipped
    assert out["value"].iloc[62] == pytest.approx(0.005 / med_next)
    assert (out["avail_ts_ns"].to_numpy()[[60, 62]] == t[[60, 62]]).all()
    zeros = np.r_[np.zeros(60), 0.01]
    ctx, ret, _ = _fake_ctx(zeros, np.ones(61, dtype=bool))
    out = _rod_absratio(ctx, ret)
    assert out["applicable"].iloc[60] == 0 and out["value"].iloc[60] == 0
    na = np.ones(61, dtype=bool)
    na[60] = False
    ctx, ret, _ = _fake_ctx(np.r_[np.linspace(0.001, 0.01, 60), 0.0], na)
    out = _rod_absratio(ctx, ret)
    assert out["applicable"].iloc[60] == 0  # not applicable when rod_ret is not applicable


def test_every_present_value_is_available_at_its_decision_time(rod) -> None:
    rows, frame = rod
    t = rows["decision_ts_ns"].to_numpy(np.int64)
    for n in K.ROD_SIGNALS:
        raw = frame[f"raw_{n}"].to_numpy()
        avail = frame[f"avail_{n}"].to_numpy(np.int64)
        present = np.isfinite(raw) & (frame[f"app_{n}"].to_numpy() > 0)
        assert present.sum() > 1000
        assert (avail[present] <= t[present]).all() and (avail[present] == t[present]).all()


def test_assert_causal_passes_on_the_rod_frame_and_catches_a_planted_late_value(rod) -> None:
    from ml_route_v2.signals import CausalityError, assert_causal

    rows, frame = rod
    assert_causal(frame, rows)
    late = frame.copy()
    i = int(np.flatnonzero(np.isfinite(late["raw_rod_ret"].to_numpy())
                           & (late["app_rod_ret"].to_numpy() > 0))[100])
    late.iloc[i, late.columns.get_loc("avail_rod_ret")] = int(rows["decision_ts_ns"].iloc[i]) + 1
    with pytest.raises(CausalityError, match="rod_ret"):
        assert_causal(late, rows)


def test_attach_rod_applies_build_panels_rules() -> None:
    from ml_route_v2.normalize import zscore_causal

    panel = panel_small()
    w, rows = world_small(), rows_small()
    frame = rod_frame(context(w, rows))
    raw, app, z = rod_z(frame, rows)
    masked = pd.DataFrame(np.where(app, raw, np.nan), index=rows.index, columns=list(K.ROD_SIGNALS))
    zz = zscore_causal(masked, rows, list(K.ROD_SIGNALS))
    idx = panel.frame.index
    for n in K.ROD_SIGNALS:
        a = panel.frame[f"app_{n}"].to_numpy()
        zc = panel.frame[f"z_{n}"].to_numpy()
        assert set(np.unique(a)) <= {0.0, 1.0}
        assert (zc[a == 0] == 0).all()
        np.testing.assert_allclose(zc[a == 1], zz.loc[idx, n].to_numpy()[a == 1], rtol=0, atol=0)
        assert np.isfinite(zc).all()
    assert tuple(panel.feature_cols[-4:]) == ("z_rod_ret", "z_rod_absratio", "app_rod_ret",
                                              "app_rod_absratio")


def test_attach_rod_drops_a_row_whose_applicable_value_is_missing() -> None:
    import dataclasses

    from ml_route_v2.panel import build_panel
    from ml_route_v2.targets import build_targets

    w, rows = world_small(), rows_small()
    ctx = context(w, rows)
    tg = build_targets(rows, w.bars, releases=w.releases, costs=w.costs)
    base = build_panel(ctx, tg, mode="train", signals=K.KEPT_SIGNALS)
    frame = rod_frame(ctx)
    victim = base.frame.index[-5]
    planted = frame.copy()
    planted.loc[victim, "raw_rod_ret"] = np.nan
    planted.loc[victim, "avail_rod_ret"] = -1
    out = attach_rod(base, ctx, planted)
    assert victim not in out.frame.index
    assert out.counts["rows_dropped_rod"] >= 1
    ok = attach_rod(base, ctx, frame)
    assert victim in ok.frame.index
    assert dataclasses.is_dataclass(ok) and len(ok.frame) == len(ok.avail_max_ts_ns)
