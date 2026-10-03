"""ml_route_v2.signals: registry coverage, causality of every signal, hand-checked values.

Synthetic data only (ml_route_v2.signals.synthetic_bars on the real group calendars and the
members' real literal tables). The causality tests are parametrized over REGISTRY:
- avail: every present value is available at or before its row's decision time;
- perturbation: every bar not closed by a cut time t* (ts_event > t* - 60 s), on EVERY root (a
  superset of the roots a signal reads), is replaced by random values and 20% of them are
  removed; values, flags and availability of all rows with decision_ts_ns <= t* are unchanged;
- roots_read: a spy on ctx.bars shows a signal reads no root outside its roots_read.
"""

from __future__ import annotations

import dataclasses
import json
from collections.abc import Iterator, Mapping
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

import ml_route_v2.signals as sigmod
from ml_route_v2.clock import decision_rows, trade_dates_of
from ml_route_v2.constants import SEED, SIGNAL_ONLY_ROOTS, UNIVERSE
from ml_route_v2.signals import (
    ALWAYS_APPLICABLE,
    EXCLUDED,
    FAMILY_SIGNALS,
    REGISTRY,
    CausalityError,
    SignalContext,
    SignalSpec,
    assert_causal,
    compute_signals,
)
from ml_route_v2.signals._core import ct_ns, epoch_day, per_unit
from ml_route_v2.signals.synthetic_bars import session_bars, synthetic_releases
from ml_route_v2.targets import sigma_d

FIRST, LAST = date(2021, 9, 1), date(2021, 11, 12)
NS_MIN = 60_000_000_000
PATHS = tuple(sorted({p for _k, p in UNIVERSE.values()} | set(SIGNAL_ONLY_ROOTS)))
INVENTORY = Path(__file__).resolve().parents[1] / "reports/stage_e11_briefs/member_inventory.json"
# Signals that cannot carry a value in a 52-date random-walk world: no exact limit move ever
# happens (K6-limitcont), and G9 needs 20 + 120 dates of history.
VACUOUS_HERE = {"k6_limitcont_dir", "g09_vol_state"}


def _world(drop: float = 0.002) -> tuple[dict, pd.DataFrame, object]:
    bars = {p: session_bars(p, FIRST, LAST, seed=SEED + i, drop=drop)
            for i, p in enumerate(PATHS)}
    rows = decision_rows(tuple(UNIVERSE), {v: trade_dates_of(bars[p])
                                           for v, (_k, p) in UNIVERSE.items()})
    return bars, rows, synthetic_releases(FIRST, LAST, SEED)


def _ctx(bars: Mapping[str, pd.DataFrame], rows: pd.DataFrame, rel: object) -> SignalContext:
    return SignalContext(rows, bars, rel, sigma_d(rows, bars))


def _perturb(bars: Mapping[str, pd.DataFrame], roots: tuple[str, ...], cut_ns: int | None,
             seed: int, drop: float = 0.0) -> dict[str, pd.DataFrame]:
    """Random values on the bars not closed by ``cut_ns`` (all bars when None); with ``drop``,
    that share of those bars is also removed (presence after t must not matter either)."""
    rng = np.random.default_rng(seed)
    out = dict(bars)
    for r in roots:
        f = bars[r].copy()
        if drop and cut_ns is not None:
            late = f["ts_event"].to_numpy() > cut_ns - NS_MIN
            f = f[~(late & (rng.random(len(f)) < drop))].reset_index(drop=True)
        ts = f["ts_event"].to_numpy()
        m = np.ones(len(f), dtype=bool) if cut_ns is None else ts > cut_ns - NS_MIN
        k = int(m.sum())
        for c in ("open", "high", "low", "close"):
            col = f[c].to_numpy().copy()
            col[m] = col[m] * rng.uniform(0.5, 1.5, k)
            f[c] = col
        vol = f["volume"].to_numpy().copy()
        vol[m] = rng.integers(1, 1000, k).astype(vol.dtype)
        f["volume"] = vol
        out[r] = f
    return out


@pytest.fixture(scope="module")
def world() -> tuple[dict, pd.DataFrame, object]:
    return _world()


@pytest.fixture(scope="module")
def base(world: tuple) -> dict[str, pd.DataFrame]:
    ctx = _ctx(*world)
    return {name: spec.fn(ctx) for name, spec in REGISTRY.items()}


@pytest.fixture(scope="module")
def cuts(world: tuple) -> list[tuple[int, dict[str, pd.DataFrame]]]:
    bars, rows, rel = world
    t = np.sort(rows["decision_ts_ns"].unique())
    out = []
    for i, frac in enumerate((0.55, 0.8)):
        cut = int(t[int(frac * len(t))])
        ctx = _ctx(_perturb(bars, PATHS, cut, seed=SEED + 100 + i, drop=0.2), rows, rel)
        out.append((cut, {name: spec.fn(ctx) for name, spec in REGISTRY.items()}))
    return out


# ------------------------------------------------------------------- registry ----
def test_every_inventory_family_has_signals_or_a_reason() -> None:
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    ids = {r["member_ids"][0].split(" ")[0] for r in inventory}
    assert len(ids) == 54
    assert set(FAMILY_SIGNALS) == ids
    for fam, names in FAMILY_SIGNALS.items():
        if names:
            assert all(n in REGISTRY for n in names) and fam not in EXCLUDED
        else:
            assert EXCLUDED.get(fam, "").strip(), fam
    assert set(EXCLUDED) == {"K5-fomc-01", "K6-wasdepost-01"}  # K9 enters in E.12 (V23 item 8)
    assert FAMILY_SIGNALS["K9-anncday-01"] == ("k9_anncday",)


def test_specs_are_well_formed() -> None:
    names = list(REGISTRY)
    assert len(names) == len(set(names))
    for name, s in REGISTRY.items():
        assert s.name == name and s.kind in ("member", "generic", "flag", "id")
        assert set(s.roots_read) <= set(PATHS)
        if s.kind == "flag":
            assert not s.normalize
    generic = {s.family for s in REGISTRY.values() if s.kind != "member"}
    # the generic G1..G17 and K9's announcement-day flag (a member family, kind "flag": V23 item 8)
    assert generic == {f"G{i}" for i in range(1, 18)} | {"K9-anncday-01"}
    k9 = REGISTRY["k9_anncday"]
    assert (k9.family, k9.cluster, k9.kind, k9.normalize, k9.roots_read) == (
        "K9-anncday-01", "K9", "flag", False, ())


# ------------------------------------------------------------------ causality ----
@pytest.mark.parametrize("name", list(REGISTRY))
def test_values_available_by_t(name: str, base: dict, world: tuple) -> None:
    rows = world[1]
    f = base[name]
    t = rows["decision_ts_ns"].to_numpy()
    present = np.isfinite(f["value"].to_numpy())
    avail = f["avail_ts_ns"].to_numpy()
    assert not np.any(present & ((avail > t) | (avail < 0)))
    off = f["applicable"].to_numpy() == 0
    assert np.all(f["value"].to_numpy()[off] == 0)
    assert set(np.unique(f["applicable"])) <= {0.0, 1.0}


@pytest.mark.parametrize("name", list(REGISTRY))
def test_bars_not_closed_by_t_do_not_move_values(name: str, base: dict, cuts: list,
                                                 world: tuple) -> None:
    t = world[1]["decision_ts_ns"].to_numpy()
    for cut, frames in cuts:
        before = t <= cut
        a, b = base[name].loc[before], frames[name].loc[before]
        np.testing.assert_array_equal(a["applicable"].to_numpy(), b["applicable"].to_numpy())
        np.testing.assert_array_equal(a["value"].to_numpy(), b["value"].to_numpy())
        np.testing.assert_array_equal(a["avail_ts_ns"].to_numpy(), b["avail_ts_ns"].to_numpy())


def test_perturbation_is_not_vacuous(base: dict, cuts: list, world: tuple) -> None:
    t = world[1]["decision_ts_ns"].to_numpy()
    cut, frames = cuts[0]
    after = t > cut
    moved = sum(not np.array_equal(base[n]["value"].to_numpy()[after],
                                   frames[n]["value"].to_numpy()[after], equal_nan=True)
                for n in ("g01_ret30", "cp1_ret", "k4_ovr_ret", "k8_flight_ret"))
    assert moved == 4


class _Spy(dict):
    def __init__(self, data: Mapping[str, pd.DataFrame]) -> None:
        super().__init__(data)
        self.read: set[str] = set()

    def __getitem__(self, key: str) -> pd.DataFrame:
        self.read.add(key)
        return super().__getitem__(key)


@pytest.mark.parametrize("name", list(REGISTRY))
def test_a_signal_reads_only_its_roots(name: str, world: tuple) -> None:
    bars, rows, rel = world
    spy = _Spy(bars)
    ctx = SignalContext(rows, spy, rel, sigma_d(rows, bars))
    REGISTRY[name].fn(ctx)
    assert spy.read <= set(REGISTRY[name].roots_read)


# ------------------------------------------- V2.2 leg roll blackout (lead ruling 2026-10-03) ----
def _own_path_cases() -> list[tuple[str, str]]:
    """(signal, vehicle): every own_path_only spec on the rows of each vehicle whose path it lists
    (three sampled vehicles for the specs that list every path)."""
    sample = ("MNQ", "MCL", "ZS")
    out = []
    for name, s in REGISTRY.items():
        if not s.own_path_only:
            continue
        vs = [v for v, (_k, p) in UNIVERSE.items() if p in s.roots_read]
        out += [(name, v) for v in (sample if len(vs) == len(UNIVERSE) else vs)]
    return out


@pytest.mark.parametrize(("name", "vehicle"), _own_path_cases())
def test_own_path_only_specs_read_only_the_row_path(name: str, vehicle: str, world: tuple
                                                    ) -> None:
    """The declaration the leg rule relies on: on one vehicle's rows the signal reads that
    vehicle's price path and nothing else, so another root's roll date never concerns it."""
    bars, rows, rel = world
    sub = rows.loc[rows["root"] == vehicle]
    spy = _Spy(bars)
    REGISTRY[name].fn(SignalContext(sub, spy, rel, sigma_d(sub, bars)))
    assert spy.read <= {UNIVERSE[vehicle][1]}


def test_a_cross_reading_member_is_not_declared_own_path(world: tuple) -> None:
    bars, rows, rel = world
    sub = rows.loc[rows["root"] == "ZS"]
    spy = _Spy(bars)
    REGISTRY["k6_crushgap_gap"].fn(SignalContext(sub, spy, rel, sigma_d(sub, bars)))
    assert {"ZM", "ZL"} <= spy.read
    assert not REGISTRY["k6_crushgap_gap"].own_path_only


def test_always_applicable_signals_never_read_another_root() -> None:
    for name in ALWAYS_APPLICABLE:
        spec = REGISTRY[name]
        assert spec.own_path_only or not spec.roots_read, name


def test_compute_signals_refuses_to_blank_an_always_applicable_signal(
        world: tuple, monkeypatch: pytest.MonkeyPatch) -> None:
    bars, rows, rel = world
    wrong = dataclasses.replace(REGISTRY["g04_ret_day"], own_path_only=False)
    monkeypatch.setattr(sigmod, "REGISTRY", {**REGISTRY, "g04_ret_day": wrong})
    day = pd.Timestamp(rows["trade_date"].iloc[len(rows) // 2]).date()
    ctx = SignalContext(rows, bars, rel, sigma_d(rows, bars), blackout={"CL": frozenset({day})})
    with pytest.raises(CausalityError, match="always-applicable"):
        compute_signals(ctx, ["g04_ret_day"])


def test_sigma_d_is_causal(world: tuple, cuts: list) -> None:
    bars, rows, rel = world
    cut = cuts[0][0]
    pert = _perturb(bars, PATHS, cut, seed=7)
    s0, s1 = sigma_d(rows, bars).to_numpy(), sigma_d(rows, pert).to_numpy()
    cut_day = pd.Timestamp(cut, tz="UTC").tz_convert("America/Chicago").normalize()
    same_or_before = rows["trade_date"].to_numpy() <= np.datetime64(cut_day.tz_localize(None))
    np.testing.assert_array_equal(s0[same_or_before], s1[same_or_before])


def test_assert_causal_raises_on_a_planted_late_signal(world: tuple) -> None:
    bars, rows, rel = world
    t = rows["decision_ts_ns"].to_numpy()
    frame = pd.DataFrame({"raw_x": np.ones(len(rows)), "app_x": np.ones(len(rows)),
                          "avail_x": t}, index=rows.index)
    assert_causal(frame, rows)
    late = frame.copy()
    late.loc[late.index[5], "avail_x"] = t[5] + 1
    with pytest.raises(CausalityError):
        assert_causal(late, rows)
    leaky = frame.copy()
    leaky.loc[leaky.index[3], "app_x"] = 0.0
    with pytest.raises(CausalityError):
        assert_causal(leaky, rows)


def test_compute_signals_refuses_a_planted_leak(world: tuple, monkeypatch: pytest.MonkeyPatch
                                                ) -> None:
    bars, rows, rel = world

    def peek(ctx: SignalContext) -> pd.DataFrame:
        t = ctx.rows["decision_ts_ns"].to_numpy()
        return pd.DataFrame({"value": np.ones(len(t)), "applicable": np.ones(len(t)),
                             "avail_ts_ns": t + 60 * NS_MIN}, index=ctx.rows.index)

    planted = SignalSpec("planted", "X", None, "generic", "test", (), True, peek)
    monkeypatch.setattr(sigmod, "REGISTRY", {**REGISTRY, "planted": planted})
    with pytest.raises(CausalityError):
        compute_signals(_ctx(bars, rows, rel), ["planted"])


def test_compute_signals_layout_and_determinism(world: tuple) -> None:
    names = ["g01_ret30", "k2_fomc_mto", "k8_oilcad_z"]
    a = compute_signals(_ctx(*world), names)
    b = compute_signals(_ctx(*_world()), names)
    assert list(a.columns) == [f"{p}_{n}" for n in names for p in ("raw", "app", "avail")]
    pd.testing.assert_frame_equal(a, b)


@pytest.mark.parametrize("name", [n for n in REGISTRY if n not in VACUOUS_HERE])
def test_signal_carries_values(name: str, base: dict) -> None:
    f = base[name]
    on = (f["applicable"].to_numpy() > 0) & np.isfinite(f["value"].to_numpy())
    assert on.any(), name


# --------------------------------------------------------------- hand checks ----
def _bar(frame: pd.DataFrame, day: date, hh: int, mm: int, offset: int = 0) -> pd.Series:
    ns = int(ct_ns(np.array([epoch_day(day)]), hh * 60 + mm, day_offset=offset)[0])
    hit = frame[frame["ts_event"] == ns]
    assert len(hit) == 1
    return hit.iloc[0]


def _row(rows: pd.DataFrame, root: str, day: date, k: int) -> int:
    sel = rows[(rows["root"] == root) & (rows["trade_date"] == pd.Timestamp(day))
               & (rows["t_index"] == k)]
    assert len(sel) == 1
    return int(np.flatnonzero(rows.index == sel.index[0])[0])


def _clean_world() -> tuple:
    return _world(drop=0.0)


@pytest.fixture(scope="module")
def clean() -> tuple[tuple, SignalContext]:
    w = _clean_world()
    return w, _ctx(*w)


def test_hand_predrift_and_fomc_minutes(clean: tuple) -> None:
    (bars, rows, _rel), ctx = clean
    day = date(2021, 10, 5)  # ISM Services in k2/_releases.ISM_SERVICES_DATES
    i = _row(rows, "ZN", day, 2)
    want = (_bar(bars["ZN"], day, 8, 49)["close"] - _bar(bars["ZN"], day, 8, 30)["open"]) \
        * per_unit("ZN")
    got = REGISTRY["k2_predrift_move"].fn(ctx)
    assert got["applicable"].iloc[i] == 1.0
    assert got["value"].iloc[i] == pytest.approx(want)
    assert got["applicable"].iloc[_row(rows, "ZN", day, 1)] == 0.0  # 07:50: not yet known
    fomc = REGISTRY["k2_fomc_mto"].fn(ctx)
    j = _row(rows, "ZT", date(2021, 9, 22), 3)  # 12:50, statement at 13:00
    assert fomc["value"].iloc[j] == pytest.approx(10.0)
    assert fomc["value"].iloc[_row(rows, "ZT", date(2021, 9, 22), 1)] == pytest.approx(310.0)
    assert fomc["applicable"].iloc[_row(rows, "ZT", date(2021, 9, 23), 1)] == 0.0


def test_hand_cp1_and_g01(clean: tuple) -> None:
    (bars, rows, _rel), ctx = clean
    day = date(2021, 10, 13)
    i = _row(rows, "MNQ", day, 1)
    want = (_bar(bars["NQ"], day, 8, 59)["close"] - _bar(bars["NQ"], day, 17, 0, -1)["open"]) \
        * per_unit("MNQ")
    assert REGISTRY["cp1_ret"].fn(ctx)["value"].iloc[i] == pytest.approx(want)
    j = _row(rows, "ZC", day, 2)  # 10:00: bars closing at 10:00 and 09:30
    sig = ctx.sigma_d.iloc[j]
    want = (_bar(bars["ZC"], day, 9, 59)["close"] - _bar(bars["ZC"], day, 9, 29)["close"]) \
        * per_unit("ZC") / sig
    assert REGISTRY["g01_ret30"].fn(ctx)["value"].iloc[j] == pytest.approx(want)
    he = REGISTRY["g01_ret30"].fn(ctx)
    k = _row(rows, "HE", day, 1)  # 09:00 - 31 min = 08:29: before the livestock session
    assert he["applicable"].iloc[k] == 0.0


def test_hand_mehedge_and_tkypost(clean: tuple) -> None:
    from strategy.members.k3._clocks import T_T
    from strategy.members.k3._mehedge_signal import MEHEDGE_R_EQ_6J

    (_bars, rows, _rel), ctx = clean
    me = date(2021, 9, 30)
    r_eq = {d: r for _m, d, r in MEHEDGE_R_EQ_6J}[me.isoformat()]
    i = _row(rows, "6J", me, 1)
    got = REGISTRY["k3_mehedge_req"].fn(ctx)
    assert got["applicable"].iloc[i] == 1.0 and got["value"].iloc[i] == pytest.approx(r_eq)
    day = date(2021, 10, 13)
    t_t = dict(T_T)[day.isoformat()]
    hh, mm = (int(x) for x in t_t.split(":"))
    inst = int(ct_ns(np.array([epoch_day(day)]), hh * 60 + mm, day_offset=-1)[0])
    j = _row(rows, "6J", day, 1)
    since = REGISTRY["k3_tkypost_msince"].fn(ctx)
    t = rows["decision_ts_ns"].iloc[j]
    assert since["value"].iloc[j] == pytest.approx((t - inst) / NS_MIN)


def test_hand_eiafade(clean: tuple) -> None:
    from strategy.members.k4.eiafade import make_mcl, release_minutes

    (bars, rows, _rel), ctx = clean
    rel = release_minutes(make_mcl().wpsr)
    day = min(d for d in rel if date(2021, 10, 1) <= d and rel[d] == 9 * 60 + 30)
    t_w = rel[day]
    c0 = _bar(bars["CL"], day, (t_w - 1) // 60, (t_w - 1) % 60)["close"]
    c14 = _bar(bars["CL"], day, (t_w + 14) // 60, (t_w + 14) % 60)["close"]
    i = _row(rows, "MCL", day, 2)  # 10:30 >= T_W + 15 for a 09:30 release
    got = REGISTRY["k4_eiafade_move"].fn(ctx)
    assert got["value"].iloc[i] == pytest.approx((c14 - c0) / c0)
    assert got["applicable"].iloc[_row(rows, "MCL", day, 1)] == 0.0


def test_excluded_reasons_name_their_evidence() -> None:
    assert "13:05" in EXCLUDED["K5-fomc-01"] and "12:50" in EXCLUDED["K5-fomc-01"]
    assert "11:15" in EXCLUDED["K6-wasdepost-01"] and "11:00" in EXCLUDED["K6-wasdepost-01"]
    assert "K9-anncday-01" not in EXCLUDED  # V23 item 8: the EC-K9 2019-2024 calendar


def _iter_member_names() -> Iterator[str]:
    for s in REGISTRY.values():
        if s.kind == "member":
            yield s.name


def test_member_signals_apply_only_to_their_cluster(base: dict, world: tuple) -> None:
    rows = world[1]
    cluster = rows["cluster"].to_numpy()
    for name in _iter_member_names():
        on = base[name]["applicable"].to_numpy() > 0
        own = REGISTRY[name].cluster
        if own in ("K8", None):
            continue  # cross-product members and the pooled ports apply beyond one cluster
        assert set(cluster[on]) <= {own}, name


def test_pooled_ports_cover_all_21_families_and_every_product(base: dict, world: tuple) -> None:
    from ml_route_v2.signals import ALWAYS_APPLICABLE

    ports = ("cp1_ret", "cp2_range", "cp2_brk", "cp3_clv")
    fams = {f: n for f, n in FAMILY_SIGNALS.items() if "-cp" in f}
    assert len(fams) == 21
    assert {f: n for f, n in fams.items() if "-cp1-" in f} == {
        f"K{i}-cp1-01": ("cp1_ret",) for i in range(1, 8)}
    assert all(n == ("cp2_range", "cp2_brk") for f, n in fams.items() if "-cp2-" in f)
    assert all(n == ("cp3_clv",) for f, n in fams.items() if "-cp3-" in f)
    assert not any(n.startswith(("k1_cp", "k7_cp")) for n in REGISTRY)
    roots = world[1]["root"].to_numpy()
    for name in ports:
        assert name in ALWAYS_APPLICABLE
        on = base[name]["applicable"].to_numpy() > 0
        assert on.all(), name  # known by t1 on every product's rows
        has = on & np.isfinite(base[name]["value"].to_numpy())
        assert set(roots[has]) == set(UNIVERSE), name


def test_hand_pooled_cp1_on_grain_and_livestock(clean: tuple) -> None:
    (bars, rows, _rel), ctx = clean
    day = date(2021, 10, 13)
    got = REGISTRY["cp1_ret"].fn(ctx)
    zc = bars["ZC"]
    ct = pd.to_datetime(zc["ts_event"], utc=True).dt.tz_convert("America/Chicago")
    first = zc[(zc["trade_date"] == day.isoformat())
               & (ct >= pd.Timestamp("2021-10-12 19:00", tz="America/Chicago"))].iloc[0]
    want = (_bar(zc, day, 8, 59)["close"] - first["open"]) * per_unit("ZC")
    assert got["value"].iloc[_row(rows, "ZC", day, 1)] == pytest.approx(want)
    he = bars["HE"]
    want = (_bar(he, day, 8, 59)["close"] - _bar(he, day, 8, 30)["open"]) * per_unit("HE")
    assert got["value"].iloc[_row(rows, "HE", day, 2)] == pytest.approx(want)


def test_hand_limitcont_planted_limit_close() -> None:
    from rules.products import product
    from strategy.members.k6._calendar import LIVESTOCK_TRADE_DATES
    from strategy.members.k6.limitcont import limit_ticks

    bars = {"HE": session_bars("HE", date(2021, 9, 1), date(2021, 10, 15), seed=5)}
    rows = decision_rows(("HE",), {"HE": trade_dates_of(bars["HE"])})
    d = date(2021, 10, 13)
    table = sorted(LIVESTOCK_TRADE_DATES)
    d1, d2 = (table[table.index(d) - k] for k in (1, 2))
    tick = float(product("HE").vendor_tick)
    frame = bars["HE"].copy()
    s2 = _bar(frame, d2, 12, 59)["close"]
    up = s2 + limit_ticks("HE", d1) * tick
    ns1 = int(ct_ns(np.array([epoch_day(d1)]), 12 * 60 + 59)[0])
    frame.loc[frame["ts_event"] == ns1, "close"] = up
    ctx = _ctx({"HE": frame}, rows, synthetic_releases(date(2021, 9, 1), date(2021, 10, 15), 1))
    got = REGISTRY["k6_limitcont_dir"].fn(ctx)
    on_d = (rows["trade_date"] == pd.Timestamp(d)).to_numpy()
    assert (got["applicable"].to_numpy()[on_d] == 1.0).all()
    assert (got["value"].to_numpy()[on_d] == 1.0).all()
    later = (rows["trade_date"] == pd.Timestamp(date(2021, 10, 14))).to_numpy()
    assert (got["applicable"].to_numpy()[later] == 0.0).all()  # d-1 of the 14th is no limit
    frame.loc[frame["ts_event"] == ns1, "close"] = s2 - limit_ticks("HE", d1) * tick
    down = REGISTRY["k6_limitcont_dir"].fn(_ctx({"HE": frame}, rows, ctx.releases))
    assert (down["value"].to_numpy()[on_d] == -1.0).all()
