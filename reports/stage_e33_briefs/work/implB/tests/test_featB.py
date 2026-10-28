"""Implementation B: hand-built known-answer tests, at least one per P4 feature, plus the G4 clip
list and G3 invalid handling. Synthetic day raws only (no market data, no outcomes)."""

from __future__ import annotations

import math
import sys
from datetime import date
from pathlib import Path

import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import calB  # noqa: E402
import dayB  # noqa: E402
import featB  # noqa: E402

D = date(2022, 2, 16)  # a Wednesday
P = 1_000_000_000
TICKS = (100_000_000, 250_000_000, 10_000_000)  # ZM 0.10 USD, ZS 0.25 c, ZL 0.01 c
BASE = (400 * P, 1400 * P, 60 * P)
TOL = dict(rtol=1e-12, atol=1e-12)


class AllZero(dict):
    def get(self, key, default=None):  # noqa: ANN001, ANN201
        return 0


@pytest.fixture(autouse=True)
def one_segment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(calB, "segment_ids", lambda: AllZero())


def flat(q):  # noqa: ANN001, ANN201
    return 0.0 * np.asarray(q, np.float64)


def alt(q):  # noqa: ANN001, ANN201
    return (np.asarray(q) % 2).astype(np.float64)


def lin(q):  # noqa: ANN001, ANN201
    return np.asarray(q, np.float64)


def _m2(f, k: int, q: np.ndarray) -> np.ndarray:  # noqa: ANN001
    return (2 * (BASE[k] + np.round(f(q) * TICKS[k]))).astype(np.int64)


def make_raw(d: date, fz=flat, fs=flat, fl=flat, **over) -> dict:  # noqa: ANN001
    """A synthetic day raw: mids are paths in ticks of the open-axis minute index q (q = 0 at
    08:35 on d); every other quantity a simple default unless overridden."""
    ax = calB.OpenAxis.of([calB.prev_trade_date(d), d])
    wall, pos, kint = ax.marks()
    keep = wall >= dayB.data33.window(d)[0]
    wall, pos = wall[keep], pos[keep]
    p0 = int(ax.pos(np.array([calB.ct(d, 8, 35)]))[0])
    qm = (pos - p0) // calB.MIN_NS
    g = calB.grid_ns(d)
    n = len(g)
    qi = np.arange(n)
    raw = {"date": d.isoformat(), "fronts": np.array([1, 2, 3]),
           "ticks": np.array(TICKS, np.int64), "grid": g, "grid_pos": ax.pos(g),
           "mark_wall": wall, "mark_pos": pos,
           "mark_day": np.array([ax.day[k].toordinal() for k in kint[keep]], np.int64)}
    for k, (inst, f) in enumerate((("zm", fz), ("zs", fs), ("zl", fl))):
        raw[f"mark_{inst}"], raw[f"mark_{inst}_ok"] = _m2(f, k, qm), np.ones(len(qm), bool)
        raw[f"g_{inst}"], raw[f"g_{inst}_ok"] = _m2(f, k, qi), np.ones(n, bool)
        for name, q in (("0830", -5), ("0835", 0), ("1315", 280)):
            raw[f"{inst}{name}"] = int(_m2(f, k, np.array([q]))[0])
            raw[f"{inst}{name}_ok"] = True
    ones = np.ones(n, np.int64)
    raw.update(g_zm_state_ok=np.ones(n, bool), g_bq=np.ones((n, 5), np.int64),
               g_aq=np.ones((n, 5), np.int64), g_bpx1=np.full(n, BASE[0]),
               g_apx1=np.full(n, BASE[0] + TICKS[0]), zs_present=True, zl_present=True,
               seas_q=np.ones((n, 2, 3), np.int64), seas_ok=np.ones(n, bool),
               lam60=np.ones(n), rp_hi=raw["g_zm"] + 2 * TICKS[0], rp_lo=raw["g_zm"],
               rp_ok=np.ones(n, bool), expiration=-1, release_clear=np.ones(n, bool))
    for key in ("v15_zm", "v15_zs", "v15_zl", "b5", "s5", "b15", "s15", "ca5", "cb5", "swb5",
                "sws5", "rfb15", "ofi_zm_1", "ofi_zm_5", "ofi_zm_15", "ofi_zs_1", "ofi_zs_5",
                "ofi_zl_1", "ofi_zl_5", *[f"iofi5_{m}" for m in range(1, 6)]):
        raw[key] = ones.copy()
    raw["rfa15"] = np.zeros(n, np.int64)
    for key in ("ofi_zm_1", "ofi_zm_5", "ofi_zm_15", "ofi_zs_1", "ofi_zs_5", "ofi_zl_1",
                "ofi_zl_5", *[f"iofi5_{m}" for m in range(1, 6)]):
        raw[f"{key}_ok"] = np.ones(n, bool)
    raw.update(over)
    return raw


def history(d: date = D, fz=alt, fs=alt, fl=alt, **over) -> list[dict]:  # noqa: ANN001
    return [make_raw(h, fz, fs, fl, **over) for h in calB.previous_dates(d, 21)]


def history_gv(d: date = D) -> list[dict]:
    """history() with alternating day levels of ZM, so the F4.7 gaps have a positive SD."""
    return [make_raw(h, lambda q, c=float(k % 2): alt(q) + c, alt, alt)
            for k, h in enumerate(calB.previous_dates(d, 21))]


def col(x: np.ndarray, name: str) -> np.ndarray:
    return x[:, featB.NAMES.index(name)]


def run(raw: dict, hist: list[dict], d: date = D) -> tuple[np.ndarray, dict]:
    return featB.features(d, raw, hist)


# ------------------------------------------------------------------ C ----
def test_c1_c2_time_of_day() -> None:
    x, _ = run(make_raw(D), history())
    assert col(x, "C_1")[139] == 0.5 and col(x, "C_2")[139] == 0.25
    assert col(x, "C_1")[0] == 0.0 and math.isclose(col(x, "C_1")[272], 272 / 278)


def test_c3_spread_cap_and_invalid() -> None:
    raw = make_raw(D)
    raw["g_apx1"] = raw["g_apx1"].copy()
    raw["g_apx1"][10] = BASE[0] + 3 * TICKS[0]
    raw["g_apx1"][11] = BASE[0] + 8 * TICKS[0]
    raw["g_zm_state_ok"] = raw["g_zm_state_ok"].copy()
    raw["g_zm_state_ok"][12] = False
    x, _ = run(raw, history())
    assert col(x, "C_3")[10] == 3.0 and col(x, "C_3")[11] == 5.0 and col(x, "C_3")[12] == 0.0
    assert col(x, "C_3")[13] == 1.0


def test_c4_touch_depth() -> None:
    raw = make_raw(D)
    raw["g_bq"][:, 0], raw["g_aq"][:, 0] = 4, 5
    x, _ = run(raw, history())
    assert np.allclose(col(x, "C_4"), math.log(10.0), **TOL)


def test_c5_volume_ratio_and_clip() -> None:
    raw = make_raw(D)
    raw["v15_zm"] = np.full(279, 9)
    raw["v15_zm"][1] = 10_000
    x, _ = run(raw, history(v15_zm=np.full(279, 4)))
    assert math.isclose(col(x, "C_5")[0], math.log(2.0), rel_tol=1e-12)
    assert col(x, "C_5")[1] == 5.0  # log(10001/5) = 7.6, clipped (G4)


def test_c6_log_sigma() -> None:
    x, st = run(make_raw(D), history())
    assert math.isclose(st["sigma_zm"], 1.0, rel_tol=1e-12)
    assert abs(col(x, "C_6")[0]) < 1e-12
    x, st = run(make_raw(D), history(fz=lambda q: 2 * alt(q)))
    assert math.isclose(col(x, "C_6")[5], math.log(2.0), rel_tol=1e-12)


def test_c6_sigma_needs_20_dates() -> None:
    x, st = run(make_raw(D), history()[-19:])
    assert st["sigma_zm"] is None and np.all(col(x, "C_6") == 0)


def test_c7_trade_dates_to_expiration() -> None:
    d = date(2022, 2, 15)
    raw = make_raw(d, expiration=calB.ct(date(2022, 3, 14), 12, 0))
    x, _ = run(raw, history(d), d)
    assert math.isclose(col(x, "C_7")[0], 18 / 60)  # 2022-02-21 is a full closure
    raw = make_raw(d, expiration=calB.ct(date(2022, 7, 14), 12, 0))
    assert col(run(raw, history(d), d)[0], "C_7")[0] == 1.0
    assert col(run(make_raw(d), history(d), d)[0], "C_7")[0] == 0.0  # no definition: invalid


def test_c8_c9_release_day() -> None:
    d = date(2022, 11, 9)  # USDA WASDE and NASS Crop Production at 12:00 ET
    assert calB.has_release(d) and not calB.has_release(date(2022, 11, 10))
    x, _ = run(make_raw(d), history(d), d)
    assert np.all(col(x, "C_8") == 1.0)
    assert col(x, "C_9")[174] == 0.0 and col(x, "C_9")[175] == 1.0  # 11:30 = i 175
    d2 = date(2022, 11, 15)  # NOPA rule date (no valid NOPA row in 2022-11)
    assert calB.has_release(d2)


def test_c10_monday_or_after_closure() -> None:
    assert calB.is_monday_or_after_closure(date(2022, 2, 14))
    assert calB.is_monday_or_after_closure(date(2022, 1, 18))  # after MLK 2022-01-17
    assert calB.is_monday_or_after_closure(date(2021, 11, 26))  # after Thanksgiving
    assert not calB.is_monday_or_after_closure(D)
    x, _ = run(make_raw(D), history())
    assert np.all(col(x, "C_10") == 0.0)


def test_c15_summer() -> None:
    d = date(2022, 6, 15)
    x, _ = run(make_raw(d), history(d), d)
    assert np.all(col(x, "C_15") == 1.0)
    assert np.all(col(run(make_raw(D), history())[0], "C_15") == 0.0)


# ------------------------------------------------------------------ F1 ----
def test_f1_1_f1_2_linear_crush() -> None:
    x, _ = run(make_raw(D, fz=lin), history())
    assert np.allclose(col(x, "F1_1"), 15.5 / math.sqrt(899 / 12), **TOL)
    assert np.allclose(col(x, "F1_2"), 60.5 / math.sqrt(14399 / 12), **TOL)
    assert np.all(col(x, "C_11") == 0.0)  # F1.3 (collinear history) and F1.7 (sd 0) invalid


def test_f1_4_kinked_path() -> None:
    kink = lambda q: np.minimum(np.asarray(q, np.float64), 10.0)  # noqa: E731
    x, _ = run(make_raw(D, fz=kink), history())

    def z(cur: float, win: list) -> float:
        w = np.array(win, np.float64)
        return (cur - w.mean()) / w.std()
    zt = z(10.0, [min(15 - j, 10) for j in range(1, 31)])
    zb = z(10.0, [min(10 - j, 10) for j in range(1, 31)])
    assert math.isclose(col(x, "F1_4")[15], zt - zb, rel_tol=1e-12)
    assert abs(col(x, "F1_4")[200]) < 1e-12  # flat window and current: sd 0 -> invalid


def test_f1_3_residual_z() -> None:
    def s_path(q):  # noqa: ANN001, ANN202
        return ((np.asarray(q) // 2) % 7).astype(np.float64)

    def l_path(q):  # noqa: ANN001, ANN202
        return ((np.asarray(q) // 2) % 5).astype(np.float64)

    def m_path(q):  # noqa: ANN001, ANN202  ZM = -420 + 0.5 ZS + 2 ZL +- 0.3 USD, in ZM ticks
        return 1.25 * s_path(q) + 0.2 * l_path(q) + np.where(np.asarray(q) % 2 == 0, 3.0, -3.0)
    clear = np.ones(279, bool)
    clear[278] = False  # keep the residual alternation orthogonal to the regressors
    hist = history(fz=m_path, fs=s_path, fl=l_path, release_clear=clear)
    fit = featB.fit_f13(D, hist)
    assert np.allclose(fit, (-420.0, 0.5, 2.0, 0.3), rtol=0, atol=1e-9)
    raw = make_raw(D, fz=lambda q: 6.0 + flat(q))
    x, _ = run(raw, hist)
    assert np.allclose(col(x, "F1_3"), 2.0, rtol=0, atol=1e-6)


def test_f1_3_needs_three_segment_dates(monkeypatch: pytest.MonkeyPatch) -> None:
    hist = history()
    seg = {date.fromisoformat(r["date"]): 1 for r in hist}
    for r in hist[-2:]:
        seg[date.fromisoformat(r["date"])] = 0
    seg[D] = 0
    monkeypatch.setattr(calB, "segment_ids", lambda: seg)
    assert featB.fit_f13(D, hist) is None


def test_f1_5_f1_6_volume_share() -> None:
    raw = make_raw(D, fz=lin, v15_zm=np.full(279, 3), v15_zs=np.full(279, 5),
                   v15_zl=np.full(279, 2))
    x, _ = run(raw, history())
    assert np.allclose(col(x, "F1_5"), 0.3, **TOL)
    assert np.allclose(col(x, "F1_6"), 0.3 * 15.5 / math.sqrt(899 / 12), **TOL)
    raw = make_raw(D, v15_zm=np.zeros(279), v15_zs=np.zeros(279), v15_zl=np.zeros(279))
    x, _ = run(raw, history())
    assert np.all(col(x, "F1_5") == 0) and np.all(col(x, "C_11") == 0)  # G3


def _gap_hist(d: date, last_level: float) -> tuple[list[dict], dict]:
    days = calB.previous_dates(d, 21)
    hist = [make_raw(h, fz=lambda q, c=float(k % 2): c + flat(q)) for k, h in enumerate(days)]
    raw = make_raw(d, fz=lambda q: last_level + flat(q))
    return hist, raw


def test_f1_7_f1_8_crush_gap() -> None:
    hist, raw = _gap_hist(D, 0.0)
    prev_level = 20 % 2  # days[20] is the previous trade date; its level is 0
    raw = make_raw(D, fz=lambda q: prev_level + 3.0 + flat(q))
    x, _ = run(raw, hist)
    assert np.allclose(col(x, "F1_7"), 3.0, **TOL)  # gaps +-1 (pstdev 1), own gap +3
    i = np.arange(273)
    assert np.allclose(col(x, "F1_8"), np.clip(3.0 * np.exp(-i / 30.0), -5, 5), **TOL)


# ------------------------------------------------------------------ F2 ----
def test_f2_1_to_f2_6_cross_returns() -> None:
    x, _ = run(make_raw(D, fs=lin, fl=lin), history())
    for n, k in enumerate((1, 5, 15)):
        assert np.allclose(col(x, f"F2_{1 + n}"), math.sqrt(k), **TOL)
        assert np.allclose(col(x, f"F2_{4 + n}"), math.sqrt(k), **TOL)


def test_f2_7_implied_meal_move() -> None:
    x, _ = run(make_raw(D, fs=lin), history())
    want = (5 * 0.25 / 2.2) / 0.10 / math.sqrt(5)
    assert np.allclose(col(x, "F2_7"), want, rtol=1e-12, atol=0)
    x, _ = run(make_raw(D, fz=lambda q: -lin(q)), history())
    assert np.allclose(col(x, "F2_7"), 5 / math.sqrt(5), **TOL)  # ZM falls 5 ticks


def test_f2_8_to_f2_11_ofi_ratios() -> None:
    hist = history(ofi_zs_1=np.full(279, -3), ofi_zs_5=np.full(279, 2),
                   ofi_zl_1=np.full(279, 4), ofi_zl_5=np.full(279, 1))
    raw = make_raw(D, ofi_zs_1=np.full(279, 6), ofi_zs_5=np.full(279, -1),
                   ofi_zl_1=np.full(279, 2), ofi_zl_5=np.full(279, 3))
    x, _ = run(raw, hist)
    assert np.allclose(col(x, "F2_8"), 2.0) and np.allclose(col(x, "F2_9"), -0.5)
    assert np.allclose(col(x, "F2_10"), 0.5) and np.allclose(col(x, "F2_11"), 3.0)
    raw["zs_present"] = False
    x, _ = run(raw, hist)
    assert np.all(col(x, "F2_8") == 0) and np.all(col(x, "C_12") == 0)  # G3


def test_f2_8_fd3b_invalid_window_and_reference() -> None:
    bad = np.ones(279, bool)
    bad[:100] = False
    hist = history(ofi_zs_1=np.where(bad, -3, 1000), ofi_zs_1_ok=bad)
    raw = make_raw(D, ofi_zs_1=np.full(279, 6))
    raw["ofi_zs_1_ok"] = raw["ofi_zs_1_ok"].copy()
    raw["ofi_zs_1_ok"][4] = False
    x, _ = run(raw, hist)
    assert np.allclose(col(x, "F2_8")[:4], 2.0)  # Obar over the computable marks only: 3
    assert col(x, "F2_8")[4] == 0 and col(x, "C_12")[4] == 0 and col(x, "C_12")[3] == 1


def test_f3_1_f3_4_fd3b_invalid_window() -> None:
    raw = make_raw(D)
    raw["ofi_zm_5_ok"] = raw["ofi_zm_5_ok"].copy()
    raw["ofi_zm_5_ok"][9] = False
    raw["iofi5_4_ok"] = raw["iofi5_4_ok"].copy()
    raw["iofi5_4_ok"][11] = False
    x, _ = run(raw, history())
    assert col(x, "F3_2")[9] == 0 and col(x, "F3_1")[9] == 1.0 and col(x, "C_13")[9] == 0
    assert col(x, "F3_4")[11] == 0 and col(x, "C_13")[11] == 0 and col(x, "F3_4")[10] != 0


# ------------------------------------------------------------------ F3 ----
def test_f3_1_to_f3_4_ofi_and_iofi() -> None:
    hist = history(ofi_zm_1=np.full(279, 2), ofi_zm_5=np.full(279, -4),
                   ofi_zm_15=np.full(279, 8))
    for r in hist:
        for m in range(5):
            r["g_bq"][:, m], r["g_aq"][:, m] = m + 1, m + 1
        r["g_zm_state_ok"][0] = False
        r["g_bq"][0, :] = 10_000  # an invalid book mark does not enter Dbar
    raw = make_raw(D, ofi_zm_1=np.full(279, 3), ofi_zm_5=np.full(279, 2),
                   ofi_zm_15=np.full(279, -4),
                   **{f"iofi5_{m}": np.full(279, 3) for m in range(1, 6)})
    x, _ = run(raw, hist)
    assert np.allclose(col(x, "F3_1"), 1.5) and np.allclose(col(x, "F3_2"), 0.5)
    assert np.allclose(col(x, "F3_3"), -0.5) and np.allclose(col(x, "F3_4"), 1.0)


def test_f3_5_f3_6_trade_imbalance() -> None:
    raw = make_raw(D, b5=np.full(279, 3), s5=np.full(279, 1), b15=np.zeros(279),
                   s15=np.zeros(279))
    x, _ = run(raw, history())
    assert np.allclose(col(x, "F3_5"), 0.5)
    assert np.all(col(x, "F3_6") == 0) and np.all(col(x, "C_13") == 0)  # B + S = 0: invalid


def test_f3_7_f3_8_seasoned_imbalance() -> None:
    q = np.ones((279, 2, 3), np.int64)
    q[:, 0, :] = [3, 1, 1]
    q[:, 1, :] = [1, 1, 2]
    raw = make_raw(D, seas_q=q)
    raw["seas_ok"][7] = False
    x, _ = run(raw, history())
    assert np.allclose(col(x, "F3_7")[:7], 0.5) and np.allclose(col(x, "F3_8")[:7], 1 / 9)
    assert col(x, "F3_7")[7] == 0 and col(x, "C_13")[7] == 0


def test_f3_9_cancel_ratio() -> None:
    x, _ = run(make_raw(D, ca5=np.full(279, 3), cb5=np.full(279, 1)), history())
    assert np.allclose(col(x, "F3_9"), 0.5)


def test_f3_10_f3_11_sweeps_and_refills() -> None:
    hist = history(swb5=np.full(279, 1), sws5=np.full(279, 1), rfb15=np.full(279, 3),
                   rfa15=np.full(279, 1))
    raw = make_raw(D, swb5=np.full(279, 4), sws5=np.full(279, 1), rfb15=np.full(279, 1),
                   rfa15=np.full(279, 4))
    x, _ = run(raw, hist)
    assert np.allclose(col(x, "F3_10"), 1.5) and np.allclose(col(x, "F3_11"), -1.5)


def test_f3_12_lambda_ratio() -> None:
    lam_h = np.full(279, 0.5)
    lam_h[:100] = np.nan  # invalid slopes do not enter the median
    raw = make_raw(D, lam60=np.full(279, 1.5))
    raw["lam60"][3] = np.nan
    x, _ = run(raw, history(lam60=lam_h))
    assert np.allclose(col(x, "F3_12")[:3], 3.0) and col(x, "F3_12")[3] == 0


# ------------------------------------------------------------------ F4 ----
def test_f4_1_to_f4_5_returns_and_clip() -> None:
    x, _ = run(make_raw(D, fz=lin), history())
    for n, k in enumerate((1, 5, 15, 30, 60)):
        assert np.allclose(col(x, f"F4_{1 + n}"), min(math.sqrt(k), 5.0), **TOL)


def test_f4_6_range_position() -> None:
    raw = make_raw(D)
    raw["rp_hi"] = raw["g_zm"] + 2 * 3 * TICKS[0]
    raw["rp_lo"] = raw["g_zm"] - 2 * 1 * TICKS[0]
    raw["rp_hi"][5] = raw["rp_lo"][5]
    x, _ = run(raw, history())
    assert np.allclose(col(x, "F4_6")[:5], 0.25) and col(x, "F4_6")[5] == 0.5


def test_f4_7_f4_8_zm_gap() -> None:
    hist, _ = _gap_hist(D, 0.0)
    raw = make_raw(D, fz=lambda q: 3.0 + flat(q))
    x, _ = run(raw, hist)
    assert np.allclose(col(x, "F4_7"), 3.0, **TOL)
    i = np.arange(273)
    assert np.allclose(col(x, "F4_8"), np.clip(3.0 * np.exp(-i / 30.0), -5, 5), **TOL)
    raw["fronts"] = np.array([9, 2, 3])  # a ZM front change between the two times: invalid
    x, _ = run(raw, hist)
    assert np.all(col(x, "F4_7") == 0) and np.all(col(x, "C_14") == 0)


def test_f4_9_f4_13_open_return() -> None:
    x, _ = run(make_raw(D, fz=lambda q: 0.1 * lin(q)), history())
    i = np.arange(273)
    want = np.where(i == 0, 0.0, 0.1 * i / np.sqrt(np.maximum(1, i)))
    assert np.allclose(col(x, "F4_9"), want, **TOL)
    assert col(x, "F4_13")[219] == 0.0 and math.isclose(col(x, "F4_13")[225], 1.5)


def test_f4_10_realised_vol() -> None:
    x, _ = run(make_raw(D, fz=alt), history())
    mean = 1 / 15
    assert np.allclose(col(x, "F4_10")[20:], math.sqrt(1 - mean ** 2), **TOL)


def test_f4_11_f4_12_burst() -> None:
    i0 = 40
    x, _ = run(make_raw(D, fz=lambda q: np.where(np.asarray(q) >= i0 - 4, 5.0, 0.0)),
               history())
    b = 5 / math.sqrt(2)
    assert math.isclose(col(x, "F4_11")[i0], b, rel_tol=1e-12)
    assert math.isclose(col(x, "F4_12")[i0], b * math.exp(-3 / 5), rel_tol=1e-12)
    assert col(x, "F4_11")[i0 + 20] == 0.0  # the burst left the 14 windows
    x, _ = run(make_raw(D, fz=lambda q: np.where(np.asarray(q) >= i0 - 4, 4.0, 0.0)),
               history_gv())
    assert col(x, "F4_11")[i0] == 0.0 and col(x, "C_14")[i0] == 1.0  # |B*| < 3: valid 0


# ------------------------------------------------------------------ G3, G4 ----
PROTOCOL_CLIPPED = (["C_5"] + [f"F1_{k}" for k in (1, 2, 3, 4)] + [f"F1_{k}" for k in (6, 7, 8)]
                    + [f"F2_{k}" for k in range(1, 12)] + [f"F3_{k}" for k in (1, 2, 3, 4)]
                    + [f"F3_{k}" for k in (10, 11, 12)] + [f"F4_{k}" for k in range(1, 6)]
                    + [f"F4_{k}" for k in range(7, 14)])


def test_g4_clip_list_is_the_protocol_list() -> None:
    assert sorted(featB.CLIPPED) == sorted(PROTOCOL_CLIPPED)
    assert len(featB.CLIPPED) == 38 and len(featB.NAMES) == 59
    unclipped = [n for n in featB.NAMES if n not in featB.CLIPPED]
    assert len(unclipped) == 21 and "F1_5" in unclipped and "F4_6" in unclipped


def test_g4_clipping_applies_to_every_listed_feature() -> None:
    big = make_raw(D, fz=lambda q: 50 * lin(q), fs=lambda q: 50 * lin(q),
                   fl=lambda q: -50 * lin(q), ofi_zm_1=np.full(279, 10 ** 6),
                   ofi_zs_1=np.full(279, 10 ** 6), swb5=np.full(279, 10 ** 6),
                   v15_zm=np.full(279, 10 ** 9))
    x, _ = run(big, history())
    assert np.abs(x[:, [featB.NAMES.index(n) for n in featB.CLIPPED]]).max() <= 5.0
    for n in ("F4_1", "F2_1", "F3_1", "F2_8", "F3_10", "C_5"):
        assert np.all(np.abs(col(x, n)[30:]) == 5.0), n


def test_g3_invalid_values_are_zero_and_flags() -> None:
    raw = make_raw(D, fz=lin)
    raw["g_zs_ok"] = raw["g_zs_ok"].copy()
    raw["g_zs_ok"][50] = False
    x, _ = run(raw, history_gv())
    assert col(x, "F2_1")[50] == 0 and col(x, "C_12")[50] == 0 and col(x, "C_12")[49] == 1
    assert col(x, "F1_1")[50] == 0 and col(x, "C_11")[50] == 0  # crush needs ZS too
    assert col(x, "C_14")[50] == 1  # F4 does not need ZS
    x, _ = run(make_raw(D, fz=lin), [])
    for flag in ("C_11", "C_12", "C_13", "C_14"):
        assert np.all(col(x, flag) == 0), flag  # no history: references undefined


def test_output_shape_and_dtype() -> None:
    x, st = run(make_raw(D), history())
    assert x.shape == (273, 59) and x.dtype == np.float64 and np.isfinite(x).all()
    assert set(st) == {"sigma_zm", "sigma_zs", "sigma_zl"}
