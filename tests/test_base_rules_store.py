"""base_rules.store: the 2010-2024 splice loader on synthetic stores in the hist (fixed plan per
root, F-01) and step 2 layouts (the frozen read-only writer, the frozen booking checks): the
boundary, the splices, the plan rules, the preflight and the refusals (sha256, holdout, embargo,
research, sealed, MES, dates after 2024-02-29, a date in both)."""

from __future__ import annotations

from datetime import UTC, date, datetime
from pathlib import Path

import pytest

from base_rules import constants as K
from base_rules import hist_plan as HP
from base_rules import store as S
from data.group_session import load_group_calendar
from data.hist_calendar import load_hist_group_calendar
from data.stage_e_bars import HoldoutRowRefused, ParquetHashMismatch
from tests._base_rules_fixtures import ns, store_frame, store_rows, write_store

HIST_DAYS = [date(2019, 4, d) for d in (24, 25, 26, 29, 30)]
STEP2_DAYS = [date(2019, 5, d) for d in (6, 7, 8, 9, 10)]
SPLICE = int(datetime(2019, 4, 26, tzinfo=UTC).timestamp()) * 10**9  # 19:00 CT on 04-25
STUB = HP.PlanWindow(K.PLAN_EXT, date(2010, 6, 7), date(2019, 4, 30))


def stub(plan: str) -> HP.PlanWindow:
    return STUB if plan == K.PLAN_EXT else HP.default_resolver(plan)


@pytest.fixture(scope="module")
def cals():  # noqa: ANN201
    return {S.EXT2010: load_hist_group_calendar("rates"), S.STEP2_ERA: load_group_calendar("rates")}


def _write(tmp: Path, cals, *, root: str = "ZN", step2_days=STEP2_DAYS,  # noqa: ANN001, ANN202
           meta_plan: str | None = None, rng: list | None = None, first: date = K.PROMPT_FIRST):
    plan = K.HIST_PLAN_OF[root]
    hist_rows = store_rows(root, cals[S.EXT2010], HIST_DAYS, [14 * 60, 14 * 60 + 1],
                           lambda t: "M9" if t < SPLICE else "U9", lambda t: 8000 + t % 7)
    hist_meta = {"plan": meta_plan or plan,
                 "hist_calendar": {"sha256": cals[S.EXT2010].file_sha256},
                 "trade_date_range": rng or [str(HIST_DAYS[0]), str(HIST_DAYS[-1])],
                 "rolls": [{"ts_ns": SPLICE, "from_raw_symbol": "M9", "to_raw_symbol": "U9"}]}
    h = write_store(tmp, root, S.EXT2010, store_frame(root, hist_rows), hist_meta, plan, first)
    s_rows = store_rows(root, cals[S.STEP2_ERA], step2_days, [14 * 60], lambda t: "U9",
                        lambda t: 8100)
    s = write_store(tmp, root, S.STEP2_ERA, store_frame(root, s_rows), {"rolls": []})
    return {S.EXT2010: S.StoreRef(*h, plan), S.STEP2_ERA: S.StoreRef(*s)}


def test_the_two_stores_splice_at_the_boundary_with_their_rolls_exposed(tmp_path, cals) -> None:
    refs = _write(tmp_path, cals)
    assert refs[S.EXT2010].plan == "ext2010"  # C1's plan for ZN
    bars = S.load_product("ZN", refs, cals)
    days = sorted({date.fromordinal(int(x)) for x in bars.td})
    assert days == HIST_DAYS + STEP2_DAYS  # 2019-05-01..05-03 in neither store
    assert [s.trade_date for s in bars.splices] == [date(2019, 4, 26)]
    assert bars.blackout == frozenset({date(2019, 4, 24), date(2019, 4, 25), date(2019, 4, 26)})
    i = bars.bar(date(2019, 4, 25), 14 * 60)
    j = bars.bar(date(2019, 4, 26), 14 * 60)
    assert bars.contract(i) == "M9" and bars.contract(j) == "U9"
    assert bars.bar(date(2019, 5, 6), 14 * 60 + 1) is None  # no forward fill
    assert bars.last_before(SPLICE) == i + 1 and bars.first_at_or_after(SPLICE) == j
    assert [r["era"] for r in bars.records] == ["ext2010", "step2"]
    assert bars.high_t is not None and bars.volume is not None and bars.no_new is not None


def test_a_second_plan_name_loads_through_the_plan_resolver(tmp_path, cals) -> None:
    refs = _write(tmp_path, cals, root="ZB")
    assert refs[S.EXT2010].plan == K.PLAN_EXT
    assert refs[S.EXT2010].path.parent.parent.name == K.PLAN_EXT
    assert S.preflight("ZB", refs, cals, stub)[0]["plan"] == K.PLAN_EXT
    bars = S.load_product("ZB", refs, cals, stub)
    assert sorted({date.fromordinal(int(x)) for x in bars.td})[0] == HIST_DAYS[0]
    with pytest.raises(Exception, match="ext2010h"):  # harness v10 has no such plan
        S.preflight("ZB", refs, cals)


def test_the_manifest_refuses_a_plan_other_than_the_roots_fixed_one() -> None:
    entry = {"path": "/a", "sha256": "a" * 64}
    raw = {"schema": K.RUN_MANIFEST_SCHEMA, "stores": {"ZB": {
        "ext2010": {**entry, "plan": "ext2010"}, "step2": entry}}}
    with pytest.raises(HP.PlanRefused, match="fixed plan"):
        S.manifest_from_dict(raw, "x", "m")
    raw["stores"]["ZB"]["ext2010"]["plan"] = K.PLAN_EXT
    assert S.manifest_from_dict(raw, "x", "m").stores["ZB"]["ext2010"].plan == K.PLAN_EXT
    del raw["stores"]["ZB"]["ext2010"]["plan"]
    with pytest.raises(HP.PlanRefused):
        S.manifest_from_dict(raw, "x", "m")


def test_metadata_plan_trade_range_and_name_window_must_agree(tmp_path, cals) -> None:
    bad_meta = _write(tmp_path / "a", cals, root="ZB", meta_plan="ext2010")
    with pytest.raises(HP.PlanRefused, match="metadata plan"):
        S.preflight("ZB", bad_meta, cals, stub)
    bad_rng = _write(tmp_path / "b", cals, root="ZB", rng=["2010-06-01", "2019-04-30"])
    with pytest.raises(HP.PlanRefused, match="trade_date_range"):
        S.preflight("ZB", bad_rng, cals, stub)
    other = _write(tmp_path / "c", cals, root="ZB", first=date(2010, 6, 6))
    with pytest.raises(HP.PlanRefused, match="spans"):  # the resolver's window is 06-07
        S.preflight("ZB", other, cals, stub)
    late = _write(tmp_path / "d", cals, root="ZB", first=date(2010, 7, 2))
    with pytest.raises(HP.PlanRefused, match="trade dates"):  # after ZB's window start
        S.preflight("ZB", late, cals, stub)


def test_the_hist_name_and_directories_follow_the_plan(tmp_path) -> None:
    good = tmp_path / K.PLAN_EXT / "ZB" / HP.expected_name("ZB", K.PLAN_EXT, date(2010, 6, 7),
                                                          K.HIST_LAST)
    assert HP.check_name("ZB", K.PLAN_EXT, good) == (date(2010, 6, 7), K.HIST_LAST)
    with pytest.raises(HP.PlanRefused, match="under"):
        HP.check_name("ZB", K.PLAN_EXT, tmp_path / "x" / "ZB" / good.name)
    with pytest.raises(HP.PlanRefused):
        HP.check_name("ZB", K.PLAN_EXT, good.with_name(good.name.replace("2019-04-30",
                                                                          "2019-05-31")))


def test_a_fallback_product_reads_the_step2_store_only(tmp_path, cals) -> None:
    refs = _write(tmp_path, cals)
    bars = S.load_product("ZN", {S.EXT2010: None, S.STEP2_ERA: refs[S.STEP2_ERA]}, cals)
    assert min(int(x) for x in bars.td) == STEP2_DAYS[0].toordinal()


def test_the_preflight_checks_every_store_input_without_reading_a_row(tmp_path, cals) -> None:
    refs = _write(tmp_path, cals)
    got = S.preflight("ZN", refs, cals)
    assert [r["era"] for r in got] == ["ext2010", "step2"] and got[0]["splices"] == 1
    with pytest.raises(ParquetHashMismatch):
        S.preflight("ZN", {**refs, S.STEP2_ERA: S.StoreRef(refs[S.STEP2_ERA].path, "0" * 64)},
                    cals)
    with pytest.raises(S.StoreRefused, match="step 2"):
        S.preflight("ZN", {S.EXT2010: refs[S.EXT2010], S.STEP2_ERA: None}, cals)


def test_a_sha256_mismatch_is_refused_before_any_row(tmp_path, cals) -> None:
    refs = _write(tmp_path, cals)
    bad = {**refs, S.STEP2_ERA: S.StoreRef(refs[S.STEP2_ERA].path, "0" * 64)}
    with pytest.raises(ParquetHashMismatch):
        S.load_product("ZN", bad, cals)


def test_rows_booked_after_2024_02_29_are_refused(tmp_path, cals) -> None:
    refs = _write(tmp_path, cals, step2_days=[date(2024, 2, 29), date(2024, 3, 1)])
    with pytest.raises(HoldoutRowRefused):
        S.load_product("ZN", refs, cals)


@pytest.mark.parametrize("path,match", [
    ("sealed/ZN/" + S.step2_name("ZN"), "sealed"),
    ("x/ZN/ohlcv-1m_ZN_v_0_2025-04-01_2026-06-19_research.parquet", "research"),
    ("x/ZN/ohlcv-1m_ZN_v_0_2024-03-01_2025-03-31_step2.parquet", "layout"),
    ("x/ZN/ohlcv-1m_ZN_v_0_2024-03-01_2024-03-31_embargo.parquet", "layout"),
    ("x/NQ/" + S.step2_name("ZN"), "layout"),
])
def test_paths_outside_the_two_layouts_are_refused(tmp_path, path, match) -> None:
    with pytest.raises(S.StoreRefused, match=match):
        S.refuse_path("ZN", S.STEP2_ERA, tmp_path / path)


def test_the_research_base_and_mes_are_refused() -> None:
    from data.config import PROCESSED_ROOT

    with pytest.raises(S.StoreRefused, match="research"):
        S.refuse_path("ZN", S.STEP2_ERA, PROCESSED_ROOT / "ZN" / S.step2_name("ZN"))
    with pytest.raises(S.StoreRefused, match="MES"):
        S.refuse_path("MES", S.STEP2_ERA, Path("/x/MES/a.parquet"))


def test_a_trade_date_in_both_stores_is_refused(tmp_path, cals, monkeypatch) -> None:
    refs = _write(tmp_path, cals)
    real = S.read_era

    def overlapping(root, era, ref, cal, resolver=HP.default_resolver):  # noqa: ANN001, ANN202
        frame, rec = real(root, era, ref, cal, resolver)
        if era == S.STEP2_ERA:
            frame["_td"] = date(2019, 4, 30).toordinal()
            frame["ts_event"] = frame["ts_event"] + 10**15
        return frame, rec

    monkeypatch.setattr(S, "read_era", overlapping)
    with pytest.raises(S.StoreRefused, match="both stores"):
        S.load_product("ZN", refs, cals)


def test_the_run_manifest_needs_a_step2_store_and_its_hash(tmp_path) -> None:
    with pytest.raises(S.StoreRefused, match="step 2"):
        S.manifest_from_dict({"schema": "stage_e16_run_manifest/1",
                              "stores": {"ZN": {"ext2010": None}}}, "x", "m")
    m = S.manifest_from_dict({"schema": "stage_e16_run_manifest/1", "stores": {"ZN": {
        "ext2010": None, "step2": {"path": "/a", "sha256": "a" * 64}}}}, "x", "m")
    assert m.fallback("ZN")
    with pytest.raises(ValueError):
        S.manifest_from_dict({"schema": "stage_e16_run_manifest/1", "stores": {"ZN": {
            "step2": {"path": "/a", "sha256": "short"}}}}, "x", "m")


def test_bar_lookup_is_by_ct_wall_clock_and_trade_date(tmp_path, cals) -> None:
    bars = S.load_product("ZN", _write(tmp_path, cals), cals)
    i = bars.bar(date(2019, 5, 7), 14 * 60)
    assert int(bars.ts[i]) == ns(date(2019, 5, 7), 14 * 60)
