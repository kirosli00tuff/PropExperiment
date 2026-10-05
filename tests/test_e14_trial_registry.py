"""Harness v10 (Stage E.14): screening.trial_registry, the append-only trial registry.

Every test uses a registry under tmp_path. The real ledger/trial_registrations.jsonl is never
appended to: a module fixture checks its bytes before and after.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterator
from pathlib import Path

import pytest

from screening import trial_registry as tr

HARNESS = "ab" * 32


@pytest.fixture(autouse=True, scope="module")
def real_registry_untouched() -> Iterator[None]:
    before = tr.REGISTRY_PATH.read_bytes() if tr.REGISTRY_PATH.is_file() else None
    yield
    after = tr.REGISTRY_PATH.read_bytes() if tr.REGISTRY_PATH.is_file() else None
    assert before == after, "a test touched the real trial registry"


@pytest.fixture
def registry(tmp_path: Path) -> Path:
    path = tmp_path / "ledger" / "trial_registrations.jsonl"
    tr.init_registry(path, time_local="2026-10-05T01:00:00-07:00")
    return path


@pytest.fixture
def freeze(tmp_path: Path) -> tuple[Path, str]:
    path = tmp_path / "stage_e14_prereg_C2.md"
    path.write_text("# frozen C2\n", encoding="utf-8")
    return path, hashlib.sha256(path.read_bytes()).hexdigest()


def register_c2(registry: Path, freeze: tuple[Path, str], **kwargs: object) -> dict:
    return tr.register("C2", ["C2-T1", "C2-T2"], freeze[0], freeze[1], HARNESS, path=registry,
                       **kwargs)


def test_the_baseline_is_n_471_citing_e12_and_is_written_once(registry: Path) -> None:
    # Act
    entries = tr.read_registry(registry)

    # Assert
    assert len(entries) == 1 and entries[0]["entry_id"] == "baseline"
    assert entries[0]["n_after"] == 471 == tr.current_n(registry)
    assert entries[0]["source"] == "reports/E.12_RETURN.md:561"
    assert "New program N = 198 + 273 = 471" in entries[0]["note"]
    with pytest.raises(tr.TrialRegistryError, match="written once"):
        tr.init_registry(registry)


def test_the_baseline_quote_is_in_the_cited_return() -> None:
    line = (tr.REPO_ROOT / "reports" / "E.12_RETURN.md").read_text(
        encoding="utf-8").splitlines()[560]
    assert tr.BASELINE_QUOTE in line


def test_registering_c2_adds_two_and_appends_one_line(registry: Path,
                                                      freeze: tuple[Path, str]) -> None:
    # Arrange
    before = registry.read_bytes()
    seen: list[str] = []

    # Act
    entry = register_c2(registry, freeze, preflight=lambda sha: seen.append(sha) or sha)

    # Assert
    assert seen == [HARNESS]
    assert (entry["n_before"], entry["n_after"]) == (471, 473) and tr.current_n(registry) == 473
    assert registry.read_bytes().startswith(before)  # append-only
    assert len(registry.read_text(encoding="utf-8").splitlines()) == 2
    assert entry["freeze_sha256"] == freeze[1] and entry["harness_sha256"] == HARNESS
    assert entry["time_local"].endswith(("-07:00", "-08:00"))
    got = tr.require_registered(["C2-T1", "C2-T2"], test="C2", freeze_sha256=freeze[1],
                                path=registry)
    assert got["entry_id"] == entry["entry_id"]


def test_a_duplicate_test_or_id_is_refused_and_nothing_is_appended(
        registry: Path, freeze: tuple[Path, str]) -> None:
    register_c2(registry, freeze)
    size = registry.stat().st_size
    with pytest.raises(tr.TrialRegistryError, match="already registered"):
        register_c2(registry, freeze)
    with pytest.raises(tr.TrialRegistryError, match="already registered"):
        tr.register("C2", ["C2-T3"], freeze[0], freeze[1], HARNESS, path=registry)
    assert registry.stat().st_size == size


def test_a_freeze_whose_bytes_differ_is_refused(registry: Path, freeze: tuple[Path, str]) -> None:
    with pytest.raises(tr.TrialRegistryError, match="sha256"):
        tr.register("C2", ["C2-T1", "C2-T2"], freeze[0], "0" * 64, HARNESS, path=registry)
    with pytest.raises(tr.TrialRegistryError, match="does not exist"):
        tr.register("C2", ["C2-T1"], freeze[0].with_name("missing.md"), freeze[1], HARNESS,
                    path=registry)
    assert tr.current_n(registry) == 471


@pytest.mark.parametrize("test,ids,match", [
    ("C2", [], "distinct"), ("C2", ["C2-T1", "C2-T1"], "distinct"), ("C2", ["C1-T1"], "form"),
    ("c2", ["c2-T1"], "label"), ("C2", ["C2T1"], "form")])
def test_malformed_test_ids_are_refused(registry: Path, freeze: tuple[Path, str], test: str,
                                        ids: list[str], match: str) -> None:
    with pytest.raises(tr.TrialRegistryError, match=match):
        tr.register(test, ids, freeze[0], freeze[1], HARNESS, path=registry)


def test_a_failing_preflight_stops_the_registration(registry: Path,
                                                    freeze: tuple[Path, str]) -> None:
    def refuse(sha: str) -> str:
        raise RuntimeError("harness differs")

    with pytest.raises(RuntimeError, match="harness differs"):
        register_c2(registry, freeze, preflight=refuse)
    assert tr.current_n(registry) == 471


def test_require_registered_refuses_missing_ids_another_test_or_another_freeze(
        registry: Path, freeze: tuple[Path, str]) -> None:
    with pytest.raises(tr.TrialRegistryError, match="not registered"):
        tr.require_registered(["C2-T1", "C2-T2"], path=registry)
    register_c2(registry, freeze)
    with pytest.raises(tr.TrialRegistryError, match="not registered"):
        tr.require_registered(["C1-T1", "C1-T2"], test="C1", path=registry)
    with pytest.raises(tr.TrialRegistryError, match="under test"):
        tr.require_registered(["C2-T1"], test="C1", path=registry)
    with pytest.raises(tr.TrialRegistryError, match="freeze sha256"):
        tr.require_registered(["C2-T1", "C2-T2"], freeze_sha256="1" * 64, path=registry)


@pytest.mark.parametrize("mutate,match", [
    (lambda lines: lines[:0], "empty"),
    (lambda lines: [lines[0].replace('"n_after": 471', '"n_after": 470')], "baseline"),
    (lambda lines: [lines[0], lines[1].replace('"n_before": 471', '"n_before": 470')], "chain"),
    (lambda lines: [lines[0], lines[1], lines[1]], "chain"),
    (lambda lines: [lines[0], lines[1], lines[1].replace('"n_after": 473', '"n_after": 475')
                    .replace('"n_before": 471', '"n_before": 473')], "repeats"),
    (lambda lines: [lines[0], "{not json"], "not JSON"),
    (lambda lines: [lines[0], ""], "blank"),
])
def test_a_malformed_registry_is_refused(registry: Path, freeze: tuple[Path, str], mutate,
                                         match: str) -> None:
    # Arrange
    register_c2(registry, freeze)
    lines = registry.read_text(encoding="utf-8").splitlines()
    registry.write_text("".join(f"{x}\n" for x in mutate(lines)), encoding="utf-8")

    # Act / Assert
    with pytest.raises(tr.TrialRegistryError, match=match):
        tr.read_registry(registry)


def test_the_cli_registers_with_the_preflight_and_reports_status(
        registry: Path, freeze: tuple[Path, str], capsys: pytest.CaptureFixture[str]) -> None:
    # Act
    rc = tr.main(["register", "--test", "C2", "--ids", "C2-T1", "C2-T2", "--freeze",
                  str(freeze[0]), "--freeze-sha256", freeze[1], "--harness-sha256", HARNESS],
                 path=registry, preflight=lambda sha: sha)
    again = tr.main(["register", "--test", "C2", "--ids", "C2-T1", "C2-T2", "--freeze",
                     str(freeze[0]), "--freeze-sha256", freeze[1], "--harness-sha256", HARNESS],
                    path=registry, preflight=lambda sha: sha)
    status = tr.main(["status"], path=registry)

    # Assert
    out = capsys.readouterr()
    assert (rc, again, status) == (0, tr.RC_REFUSED, 0)
    assert "N 471 -> 473" in out.out and "REFUSED" in out.err and "N = 473" in out.out
    assert json.loads(registry.read_text(encoding="utf-8").splitlines()[1])["test"] == "C2"


def test_the_committed_registry_holds_only_the_baseline_until_the_lead_registers() -> None:
    entries = tr.read_registry(tr.REGISTRY_PATH)
    assert entries[0]["entry_id"] == "baseline" and entries[0]["n_after"] == 471
