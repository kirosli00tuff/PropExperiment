"""Tests for screening.build_release_calendar (Stage E.2b, lead rulings OC-J and OC-N).

Synthetic sources and saved pages under tmp_path drive the refusals; the frozen inputs
(F6.4, vehicles, liquidity, catalog, the names extraction) are the repository's own. The
integration tests at the end run on the real source files and are skipped when the git-ignored
saved pages are absent.
"""

from __future__ import annotations

import copy
import dataclasses
import json
import os
import stat
from datetime import UTC, date, datetime, time
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

from data.config import REPO_ROOT
from rules.products import PRODUCTS
from screening import build_release_calendar as b
from screening.stage_e_rules import release_calendar_from_dict

NY = ZoneInfo("America/New_York")
PAGES_DIR = "data/vendor/release_pages/test"
REAL_PAGES = (REPO_ROOT / "data" / "vendor" / "release_pages").is_dir()


# ------------------------------------------------------------------ fixtures ----
@pytest.fixture(scope="module")
def real_inputs() -> b.BuildInputs:
    return b.load_inputs(REPO_ROOT)


def _utc(day: str, hhmm: str) -> str:
    local = datetime.combine(date.fromisoformat(day), time.fromisoformat(hhmm), tzinfo=NY)
    return local.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _entry(code: str, day: str, hhmm: str, note: str = "", **extra: object) -> dict:
    return {"id": f"{code}-{day}", "release": code, "release_name": f"{code} name",
            "reference_period": "synthetic", "date": day, "time_local": hhmm,
            "tz": "America/New_York", "instant_utc": _utc(day, hhmm),
            "url": f"https://example.test/{code}", "fetched_url": f"https://example.test/{code}",
            "quote": f"{code} released on {day} at {hhmm} ET",
            "saved_path": f"{PAGES_DIR}/{code}.txt", "fetched_pdt": "2026-09-26T15:00:00-0700",
            "note": note, **extra}


def _table(codes: list[str], entries: list[dict], cancellations: list[dict]) -> dict:
    table = {c: {y: {"expected": 0, "found": 0, "unverified": 0, "cancelled": 0, "moved": 0}
                 for y in b.YEARS} for c in codes}
    for e in entries:
        row = table[e["release"]][e["date"][:4]]
        row["expected"] += 1
        row["unverified" if b.UNVERIFIED_MARK in e["note"] else "found"] += 1
    for c in cancellations:
        row = table[c["release"]][c["originally_scheduled"][:4]]
        row["expected"] += 1
        row["cancelled"] += 1
    return table


# code -> (date, local time, extra fields)
_SYNTH = {
    "NFP": ("2020-01-10", "08:30", {}), "CPI": ("2020-01-14", "08:30", {}),
    "FOMC": ("2020-01-29", "14:00", {}), "WPSR": ("2020-01-08", "10:30", {}),
    "NGS": ("2020-01-09", "10:30", {"note": "[unverified] standing Thursday rule"}),
    "CROP": ("2020-01-10", "12:00", {}), "CROP_ANNUAL": ("2020-01-10", "12:00", {}),
    "WASDE": ("2020-01-10", "12:00", {}), "PPI": ("2020-01-15", "08:30", {}),
    "ISM_SERVICES": ("2020-01-07", "10:00", {}), "G17": ("2020-01-17", "09:15", {}),
    "API_WSB": ("2020-01-07", "16:30", {"evidence_kind": "announced_schedule"}),
    "CROP_PROGRESS": ("2020-04-06", "16:00", {}), "TREASURY_AUCTION": ("2020-01-07", "13:00", {}),
}
_CANCEL = {"release": "PPI", "reference_period": "October 2025",
           "originally_scheduled": "2025-11-14 08:30 America/New_York", "reason": "lapse",
           "evidence": [{"saved_path": f"{PAGES_DIR}/PPI.txt", "quote": "PPI October 2025 not "
                         "published", "found": True}]}


def _synthetic_sources(page_root: Path) -> dict[str, dict]:
    pages = page_root / PAGES_DIR
    pages.mkdir(parents=True, exist_ok=True)
    sources: dict[str, dict] = {}
    for name in b.SOURCES:
        codes = [c for c, s in b.RELEASE_SOURCE.items() if s == name]
        entries = []
        for code in codes:
            day, hhmm, extra = _SYNTH[code]
            e = _entry(code, day, hhmm, **extra)
            entries.append(e)
            text = f"Header line\n  {e['quote'].replace(' at ', '  at\n ')}\nFooter"
            if code == "PPI":
                text += "\nPPI October 2025 not published"
            (pages / f"{code}.txt").write_text(text, encoding="utf-8")
        cancels = [copy.deepcopy(_CANCEL)] if name == "named" else []
        sources[name] = {"coverage": {"first": b.COVERAGE_FIRST, "last": b.COVERAGE_LAST},
                         "entries": entries, "cancellations": cancels, "moves": [],
                         "coverage_table": _table(codes, entries, cancels)}
    return sources


@pytest.fixture()
def synth(tmp_path: Path, real_inputs: b.BuildInputs) -> b.BuildInputs:
    return dataclasses.replace(real_inputs, sources=_synthetic_sources(tmp_path),
                               source_logs={n: "final log" for n in b.SOURCES})


def _with_entry(inputs: b.BuildInputs, name: str, code: str, **changes: object) -> b.BuildInputs:
    sources = copy.deepcopy(dict(inputs.sources))
    for e in sources[name]["entries"]:
        if e["release"] == code:
            e.update(changes)
    return dataclasses.replace(inputs, sources=sources)


# ------------------------------------------------------------ frozen inputs ----
def test_frozen_inputs_are_pinned_to_their_recorded_sha256(tmp_path: Path) -> None:
    (tmp_path / "reports").mkdir()
    for rel in (b.FREEZE_MANIFEST, b.FACTS_PATH, b.LIQUIDITY_PATH):
        (tmp_path / rel).write_bytes((REPO_ROOT / rel).read_bytes())
    (tmp_path / b.LIQUIDITY_PATH).write_bytes((REPO_ROOT / b.LIQUIDITY_PATH).read_bytes() + b" ")
    with pytest.raises(b.CalendarBuildRefused, match="stage_e0_liquidity.json: sha256"):
        b.load_inputs(tmp_path)
    manifest = json.loads((REPO_ROOT / b.FREEZE_MANIFEST).read_text(encoding="utf-8"))
    del manifest["files"][b.CATALOG_PATH]
    (tmp_path / b.FREEZE_MANIFEST).write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(b.CalendarBuildRefused, match="records no sha256"):
        b.load_inputs(tmp_path)


# -------------------------------------------------------------------- F6.4 ----
def test_f6_4_quote_parses_into_its_five_rows_verbatim() -> None:
    rows = b.parse_f6_4(b.F6_4_QUOTE)
    assert [r.name for r in rows] == list(b.F6_4_CODES)
    assert len(rows[0].listed) == 28 and rows[0].listed[0] == "ES" and rows[0].listed[-1] == "MET"
    assert rows[1].listed is None  # FOMC Statement: "All products"
    assert rows[2].listed == ("CL", "QM", "MCL", "RB")
    assert rows[2].time_text == "9:30 AM / 10:00 AM*"
    assert rows[4].codes == ("CROP", "CROP_ANNUAL")


def test_f6_4_parse_refuses_text_it_cannot_tile() -> None:
    with pytest.raises(b.CalendarBuildRefused, match="unparsed"):
        b.parse_f6_4("Stray words. " + b.F6_4_QUOTE)
    with pytest.raises(b.CalendarBuildRefused, match="unparsed"):
        b.parse_f6_4(b.F6_4_QUOTE + " trailing")


def test_frozen_facts_file_carries_the_encoded_f6_4(real_inputs: b.BuildInputs) -> None:
    assert len(b.check_f6_4(real_inputs.facts)) == 5


def test_f6_4_check_refuses_an_altered_quote_or_a_missing_micro_note(
        real_inputs: b.BuildInputs) -> None:
    facts = copy.deepcopy(dict(real_inputs.facts))
    fact = next(f for f in facts["facts"] if f["id"] == "F6.4")
    fact["quote"] = fact["quote"].replace("NG, QG", "NG")
    with pytest.raises(b.CalendarBuildRefused, match="quote differs"):
        b.check_f6_4(facts)
    fact["quote"] = b.F6_4_QUOTE
    fact["note"] = "*Pending abbreviated trading hours."
    with pytest.raises(b.CalendarBuildRefused, match="Micro contracts"):
        b.check_f6_4(facts)


def test_micro_siblings_come_from_the_product_table() -> None:
    assert b.micro_siblings("NQ") == ("MNQ",)
    assert b.micro_siblings("ES") == ("MES",)
    assert b.micro_siblings("SI") == ("SIL",)  # Micro Silver counts as a micro
    assert b.micro_siblings("CL") == ("MCL",)  # QM is an E-mini, not a micro
    assert b.micro_siblings("NG") == ("MNG",)
    assert b.micro_siblings("6E") == ("M6E",)  # E7 is an E-mini
    assert b.micro_siblings("6C") == ()
    assert b.micro_siblings("MNQ") == ()
    assert b.micro_siblings("NKD") == ()  # not in the product table


# ---------------------------------------------------------- universe, words ----
def test_product_universe_splits_on_the_product_table(real_inputs: b.BuildInputs) -> None:
    inside, outside = b.product_universe(real_inputs.vehicles, real_inputs.liquidity)
    assert set(inside) == set(PRODUCTS) - {"MES"}
    assert outside == ("6M", "MET", "NKD", "PL")


@pytest.mark.parametrize(("word", "roots"), [
    ("crude", ("CL", "MCL")), ("gas", ("NG",)), ("gold", ("GC", "MGC")), ("silver", ("SI",)),
    ("EUR", ("6E",)), ("ZT", ("ZT",)), ("HE", ("HE",)), ("Nasdaq-100", ("MNQ", "NQ")),
    ("RBOB", ("RB",)), ("bitcoin", ("MBT",))])
def test_exposure_words_map_to_vehicle_and_price_path(real_inputs: b.BuildInputs, word: str,
                                                      roots: tuple[str, ...]) -> None:
    exposure = b.exposure_of_word(word, real_inputs.vehicles)
    assert b.exposure_roots(real_inputs.vehicles)[exposure] == roots


def test_an_unknown_exposure_word_is_refused(real_inputs: b.BuildInputs) -> None:
    with pytest.raises(b.CalendarBuildRefused, match="platinum"):
        b.exposure_of_word("platinum", real_inputs.vehicles)


def test_names_extraction_matches_the_frozen_catalog(real_inputs: b.BuildInputs) -> None:
    b.check_names_against_catalog(real_inputs.names, real_inputs.catalog, real_inputs.vehicles)
    names = copy.deepcopy(dict(real_inputs.names))
    names["members"][0]["read_products"] = ["gold"]
    with pytest.raises(b.CalendarBuildRefused, match="differs from the catalog"):
        b.check_names_against_catalog(names, real_inputs.catalog, real_inputs.vehicles)


def test_a_member_named_release_without_a_ruling_is_refused(real_inputs: b.BuildInputs) -> None:
    names = copy.deepcopy(dict(real_inputs.names))
    names["members"][0]["release_name_verbatim"] = "Beige Book"
    with pytest.raises(b.CalendarBuildRefused, match="Beige Book"):
        b.member_named(names, real_inputs.vehicles)


def test_excluded_fixes_and_auctions_add_no_products(real_inputs: b.BuildInputs) -> None:
    named = b.member_named(real_inputs.names, real_inputs.vehicles)
    assert set(named.excluded) == b.EXCLUDED_BY_RULING
    assert set(named.roots) <= set(b.RELEASE_SOURCE)


def test_release_products_follow_ruling_oc_n(real_inputs: b.BuildInputs) -> None:
    rows = b.check_f6_4(real_inputs.facts)
    inside, outside = b.product_universe(real_inputs.vehicles, real_inputs.liquidity)
    named = b.member_named(real_inputs.names, real_inputs.vehicles)
    p = {c: set(x.products) for c, x in b.release_products(rows, inside, outside, named).items()}
    assert p["FOMC"] == set(PRODUCTS)  # all products, MES as ES's micro sibling
    assert {"MES", "MNQ", "M2K", "MYM", "MGC", "SIL", "MHG", "M6B", "E7"} <= p["NFP"]
    assert not {"NKD", "GE", "6M", "MET"} & p["NFP"]
    assert p["CPI"] == {"GC", "HG", "MBT", "MGC", "MHG", "MNQ", "NQ", "SI"}
    assert p["PPI"] == {"MBT"} and p["CROP_PROGRESS"] == {"ZC"}
    assert p["TREASURY_AUCTION"] == {"ZT", "ZF", "ZN", "TN", "ZB", "UB"}
    assert {"CL", "QM", "MCL", "RB", "6C", "HO", "NG"} == p["WPSR"]  # 6C: K8-oilcad-01
    assert p["CROP"] == p["CROP_ANNUAL"] == p["WASDE"] == {"ZC", "ZS", "ZW", "ZM", "ZL", "HE",
                                                          "LE"}


# ------------------------------------------------------- synthetic assemble ----
def test_synthetic_build_keeps_unverified_and_announced_and_flags_cpi(
        synth: b.BuildInputs, tmp_path: Path) -> None:
    cal = b.assemble(synth, tmp_path)
    v = cal["verification"]
    assert v["entries"] == len(b.RELEASE_SOURCE)
    assert v["quotes_ok"] == v["quotes_checked"] == v["instants_ok"] == len(b.RELEASE_SOURCE)
    assert v["unverified"] == {"total": 1, "by_release": {"NGS": 1}}
    assert v["announced_schedule"] == {"total": 1, "by_release": {"API_WSB": 1}}
    assert v["evidence_quotes_ok"] == 1 and v["cancelled"] == {"PPI": 1}
    assert [e["id"] for e in cal["releases"] if e["cpi"]] == ["CPI-2020-01-14"]
    ngs = next(e for e in cal["releases"] if e["release"] == "NGS")
    assert ngs["evidence"] == "unverified" and ngs["products"] and "[unverified]" in ngs["note"]
    assert cal["releases"] == sorted(cal["releases"], key=lambda e: (e["instant_utc"], e["id"]))


def test_shared_instants_list_both_ids_and_the_loader_deduplicates(
        synth: b.BuildInputs, tmp_path: Path) -> None:
    cal = b.assemble(synth, tmp_path)
    groups = {g["instant_utc"]: g["ids"] for g in cal["shared_instants"]}
    noon = _utc("2020-01-10", "12:00")
    assert sorted(groups[noon]) == ["CROP-2020-01-10", "CROP_ANNUAL-2020-01-10",
                                    "WASDE-2020-01-10"]
    loaded = release_calendar_from_dict(cal, "sha", "test")
    zc = loaded.by_root["ZC"]
    assert len(zc) == len(set(zc)) and len([x for x in zc if x == _ns(noon)]) == 1
    assert len(loaded.cpi) == 1 and loaded.cpi[0] == datetime(2020, 1, 14, 13, 30, tzinfo=UTC)


def _ns(text: str) -> int:
    return int(datetime.fromisoformat(text.replace("Z", "+00:00")).timestamp()) * 10**9


def test_a_quote_absent_from_its_page_refuses(synth: b.BuildInputs, tmp_path: Path) -> None:
    bad = _with_entry(synth, "macro", "CPI", quote="CPI released on another day")
    with pytest.raises(b.CalendarBuildRefused, match="CPI-2020-01-14: quote not in"):
        b.assemble(bad, tmp_path)


def test_an_instant_that_is_not_date_time_tz_refuses(synth: b.BuildInputs, tmp_path: Path) -> None:
    bad = _with_entry(synth, "macro", "NFP", instant_utc="2020-01-10T12:30:00Z")
    with pytest.raises(b.CalendarBuildRefused, match="NFP-2020-01-10: instant"):
        b.assemble(bad, tmp_path)


def test_instant_matching_rejects_a_dst_gap_and_a_non_z_format() -> None:
    gap = _entry("NFP", "2020-03-08", "02:30", instant_utc="2020-03-08T07:30:00Z")
    assert not b.instant_matches(gap)
    assert not b.instant_matches(_entry("NFP", "2020-01-10", "08:30",
                                        instant_utc="2020-01-10T13:30:00+00:00"))
    assert b.instant_matches(_entry("NFP", "2020-07-02", "08:30"))


def _with_table(inputs: b.BuildInputs, name: str, code: str, year: str, **changes: int
                ) -> b.BuildInputs:
    sources = copy.deepcopy(dict(inputs.sources))
    sources[name]["coverage_table"][code][year].update(changes)
    return dataclasses.replace(inputs, sources=sources)


def test_an_expected_release_neither_found_unverified_nor_cancelled_refuses(
        synth: b.BuildInputs, tmp_path: Path) -> None:
    bad = _with_table(synth, "macro", "FOMC", "2021", expected=1)
    with pytest.raises(b.CalendarBuildRefused, match="FOMC 2021 expects 1 releases"):
        b.assemble(bad, tmp_path)


def test_a_coverage_table_the_entries_do_not_reproduce_refuses(
        synth: b.BuildInputs, tmp_path: Path) -> None:
    bad = _with_table(synth, "commodity", "WPSR", "2021", expected=1, found=1)
    with pytest.raises(b.CalendarBuildRefused, match="WPSR 2021 table"):
        b.assemble(bad, tmp_path)


def test_a_draft_source_log_refuses(synth: b.BuildInputs, tmp_path: Path) -> None:
    bad = dataclasses.replace(synth, source_logs={**synth.source_logs,
                                                  "commodity": "x\nSTATUS: DRAFT\n"})
    with pytest.raises(b.CalendarBuildRefused, match="source commodity: its log"):
        b.assemble(bad, tmp_path)


def test_a_source_with_a_different_coverage_window_refuses(synth: b.BuildInputs,
                                                           tmp_path: Path) -> None:
    sources = copy.deepcopy(dict(synth.sources))
    sources["named"]["coverage"] = {"first": "2019-06-01", "last": b.COVERAGE_LAST}
    with pytest.raises(b.CalendarBuildRefused, match="source named: coverage"):
        b.assemble(dataclasses.replace(synth, sources=sources), tmp_path)


def test_a_release_in_the_wrong_source_refuses(synth: b.BuildInputs, tmp_path: Path) -> None:
    sources = copy.deepcopy(dict(synth.sources))
    moved = sources["named"]["entries"].pop()
    sources["macro"]["entries"].append(moved)
    sources["macro"]["coverage_table"][moved["release"]] = \
        sources["named"]["coverage_table"].pop(moved["release"])
    with pytest.raises(b.CalendarBuildRefused, match="not one the lead assigned"):
        b.assemble(dataclasses.replace(synth, sources=sources), tmp_path)


def test_a_release_of_the_lead_list_without_entries_refuses(synth: b.BuildInputs,
                                                            tmp_path: Path) -> None:
    sources = copy.deepcopy(dict(synth.sources))
    sources["named"]["entries"] = [e for e in sources["named"]["entries"]
                                   if e["release"] != "G17"]
    del sources["named"]["coverage_table"]["G17"]
    with pytest.raises(b.CalendarBuildRefused, match=r"\['G17'\] of the lead's list"):
        b.assemble(dataclasses.replace(synth, sources=sources), tmp_path)


def test_duplicate_ids_and_dates_outside_the_coverage_refuse(synth: b.BuildInputs,
                                                             tmp_path: Path) -> None:
    dup = _with_entry(synth, "named", "PPI", id="CPI-2020-01-14")
    with pytest.raises(b.CalendarBuildRefused, match="appears twice"):
        b.assemble(dup, tmp_path)
    sources = copy.deepcopy(dict(synth.sources))
    late = _entry("CPI", "2026-06-22", "08:30")
    sources["macro"]["entries"].append(late)
    sources["macro"]["coverage_table"] = _table(["NFP", "CPI", "FOMC"],
                                                sources["macro"]["entries"], [])
    (tmp_path / PAGES_DIR / "CPI.txt").write_text(late["quote"] + "\n" + _SYNTH_QUOTE("CPI"),
                                                  encoding="utf-8")
    with pytest.raises(b.CalendarBuildRefused, match="outside the coverage"):
        b.assemble(dataclasses.replace(synth, sources=sources), tmp_path)


def _SYNTH_QUOTE(code: str) -> str:  # noqa: N802
    day, hhmm, _ = _SYNTH[code]
    return f"{code} released on {day} at {hhmm} ET"


def test_a_cancellation_evidence_quote_absent_from_its_page_refuses(
        synth: b.BuildInputs, tmp_path: Path) -> None:
    sources = copy.deepcopy(dict(synth.sources))
    sources["named"]["cancellations"][0]["evidence"][0]["quote"] = "PPI was published"
    with pytest.raises(b.CalendarBuildRefused, match="evidence quote"):
        b.assemble(dataclasses.replace(synth, sources=sources), tmp_path)


def test_a_saved_path_leaving_the_repository_refuses(synth: b.BuildInputs,
                                                     tmp_path: Path) -> None:
    bad = _with_entry(synth, "macro", "FOMC", saved_path="../outside.txt")
    with pytest.raises(b.CalendarBuildRefused, match="not a relative path"):
        b.assemble(bad, tmp_path)


def test_an_unknown_evidence_kind_refuses() -> None:
    with pytest.raises(b.CalendarBuildRefused, match="unknown evidence_kind"):
        b.evidence_of({"id": "X", "note": "", "evidence_kind": "rumour"})


def test_vehicle_and_price_path_with_different_instants_refuse(
        real_inputs: b.BuildInputs) -> None:
    entries = [{"instant_utc": "2020-01-10T13:30:00Z", "products": ["MNQ"]}]
    with pytest.raises(b.CalendarBuildRefused, match="Nasdaq-100"):
        b.check_vehicle_parity(entries, real_inputs.vehicles)


# ------------------------------------------------------------------ writing ----
def test_write_once_is_read_only_and_refuses_to_overwrite(tmp_path: Path) -> None:
    path = tmp_path / "calendar.json"
    b.write_once(path, "{}\n")
    assert not os.access(path, os.W_OK) or not (path.stat().st_mode & stat.S_IWUSR)
    with pytest.raises(b.CalendarBuildRefused, match="written once"):
        b.write_once(path, "{}\n")
    assert path.read_text(encoding="utf-8") == "{}\n"


def test_build_writes_once_check_reproduces_and_a_second_build_refuses(
        synth: b.BuildInputs, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr(b, "load_inputs", lambda root: synth)
    (tmp_path / "reports").mkdir()
    assert b.main([], repo_root=tmp_path) == 0
    written = tmp_path / b.OUT_JSON
    raw = json.loads(written.read_text(encoding="utf-8"))
    assert raw["schema"] == "stage_e_release_calendar/1"
    assert (tmp_path / b.OUT_MD).read_text(encoding="utf-8").startswith("# Stage E.2b release")
    assert b.main(["--check"], repo_root=tmp_path) == 0
    assert "CHECK identical" in capsys.readouterr().out
    assert b.main([], repo_root=tmp_path) == 2  # refuses to overwrite
    assert "never overwritten" in capsys.readouterr().err


def test_main_reports_a_refusal_and_writes_nothing(synth: b.BuildInputs, tmp_path: Path,
                                                   monkeypatch: pytest.MonkeyPatch) -> None:
    bad = dataclasses.replace(synth, source_logs={**synth.source_logs, "named": "STATUS: DRAFT"})
    monkeypatch.setattr(b, "load_inputs", lambda root: bad)
    (tmp_path / "reports").mkdir()
    assert b.main([], repo_root=tmp_path) == 2
    assert not (tmp_path / b.OUT_JSON).exists() and not (tmp_path / b.OUT_MD).exists()


# ------------------------------------------------------ real source files ----
@pytest.mark.skipif(not REAL_PAGES, reason="saved release pages (git-ignored) are absent")
def test_real_sources_build_and_both_consumers_read_them(tmp_path: Path) -> None:
    from ml_route.inputs import event_calendar_from_release, load_products

    result = b.build(REPO_ROOT, write=False)
    v = result.calendar["verification"]
    assert v["entries"] == 2609 and v["by_source"] == {"macro": 227, "commodity": 921,
                                                       "named": 1461}
    assert v["quotes_ok"] == v["quotes_checked"] == v["instants_ok"] == 2609
    assert v["unverified"]["by_release"] == {"NGS": 365}
    assert v["announced_schedule"]["by_release"] == {"API_WSB": 372}
    loaded = release_calendar_from_dict(json.loads(result.json_text), result.sha256, "test")
    assert set(loaded.by_root) == set(PRODUCTS) and len(loaded.cpi) == 85
    assert (loaded.first, loaded.last) == (date(2019, 5, 1), date(2026, 6, 21))
    events = event_calendar_from_release(loaded, load_products())
    assert events.of("NQ").tolist() == list(loaded.by_root["MNQ"])  # vehicle list, same instants


@pytest.mark.skipif(not (REPO_ROOT / b.OUT_JSON).is_file(), reason="calendar not written yet")
def test_the_written_calendar_loads_through_both_consumers() -> None:
    from ml_route.inputs import load_event_calendar
    from screening.stage_e_rules import load_release_calendar

    cal = load_release_calendar()
    assert cal.covers([date(2019, 5, 6), date(2026, 6, 19)]) and len(cal.cpi) == 85
    events = load_event_calendar()
    events.require_coverage(date(2019, 5, 6), date(2024, 2, 29), "the training window")
    assert events.sha256 == cal.sha256
