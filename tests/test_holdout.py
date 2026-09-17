"""Sealed holdout (Stage C, Task 6): the barrier, the ceremony, and the paid-data safety.

Every lifecycle test runs on synthetic files in tmp_path, never on the real store. The last
class checks the real store only if the migration has run (skipped otherwise), and it decrypts
nothing.
"""

from __future__ import annotations

import stat
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from data import adapter
from data import holdout as ho
from data.research_bars import (
    RESEARCH_PARQUET_NAME,
    RESEARCH_SERIES_PATH,
    HoldoutLeakError,
    assert_no_holdout_rows,
)
from data.splits import HOLDOUT_START

# Trade dates straddling HOLDOUT_START (2026-06-22): three before, three from it on.
DATES = ["2026-06-12", "2026-06-18", "2026-06-19", "2026-06-22", "2026-06-23", "2026-06-24"]
REASON = "Stage D.2 pre-registered holdout evaluation of candidate X"
# The unlock gate wants a real pre-registration: >= 200 characters naming the metric, the
# threshold and the decision rule.
REGISTRATION = (
    "# Stage D.2 pre-registration\n\n"
    "metric: mean daily net P&L per micro over the 62 complete holdout trade dates.\n"
    "threshold: mean > $0 and a one-sided t-statistic of at least 1.28.\n"
    "decision: if the threshold is met, proceed to the Stage E practice-account forward test; "
    "otherwise abandon the candidate and return to Stage D.1 research.\n"
)


def _frame() -> pd.DataFrame:
    return pd.DataFrame([{"ts_event": 1_781_000_000_000_000_000 + k * 60_000_000_000,
                          "close": 6000.0 + k * 0.25, "trade_date": d}
                         for k, d in enumerate(DATES)])


def _paths(tmp: Path) -> ho.HoldoutPaths:
    return ho.HoldoutPaths(sealed_root=tmp / "sealed", manifest=tmp / "docs" / "MANIFEST.json",
                           unlock_log=tmp / "docs" / "UNLOCK_LOG.md",
                           registration=tmp / "REGISTRATION.md",
                           research_parquet=tmp / "processed" / "research.parquet")


def _raw(tmp: Path, name: str, payload: bytes) -> Path:
    path = tmp / "vendor" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    path.chmod(stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)  # like real raw files
    return path


@pytest.fixture
def sealed(tmp_path: Path) -> tuple[ho.HoldoutPaths, dict, list[Path], pd.DataFrame]:
    paths = _paths(tmp_path)
    frame = _frame()
    full = tmp_path / "processed" / "full.parquet"
    full.parent.mkdir(parents=True)
    pq.write_table(pa.Table.from_pandas(frame, preserve_index=False)
                   .replace_schema_metadata({b"propexperiment": b'{"rolls": []}'}), full)
    raws = [
        _raw(tmp_path, "range=2026-05-01_2026-06-01.dbn.zst", b"may-bytes"),  # research only
        _raw(tmp_path, "range=2026-06-01_2026-07-01.dbn.zst", b"june-bytes" * 50),  # holdout
        _raw(tmp_path, "range=2026-09-01_2026-09-16.dbn.zst", b"sept-bytes" * 30),  # holdout
    ]
    manifest = ho.seal_holdout(full, raws, paths, remove_plaintext=True)
    return paths, manifest, raws, frame


class TestSplitAndOverlap:
    def test_split_is_by_trade_date_at_holdout_start(self) -> None:
        research, held = ho.split_research_holdout(_frame())
        # DATES: 3 before 2026-06-22, 3 on/after it.
        assert list(research["trade_date"]) == DATES[:3]
        assert list(held["trade_date"]) == DATES[3:]
        assert HOLDOUT_START.isoformat() == "2026-06-22"

    @pytest.mark.parametrize(("name", "expected"), [
        ("range=2026-05-01_2026-06-01.dbn.zst", False),  # ends before the first session
        ("range=2026-06-01_2026-06-21.dbn.zst", False),  # ends 06-21 00:00 UTC; session opens 22:00
        ("range=2026-06-01_2026-06-22.dbn.zst", True),  # holds 06-21 22:00 UTC onward
        ("range=2026-06-01_2026-07-01.dbn.zst", True),
        ("range=2026-09-01_2026-09-16.dbn.zst", True),
    ])
    def test_raw_overlap_rule(self, name: str, expected: bool) -> None:
        assert (ho.raw_files_overlapping_holdout([Path(name)]) == [Path(name)]) is expected


class TestCipher:
    SALT, NONCE = b"s" * 16, b"n" * 16

    def test_round_trip_and_wrong_phrase(self) -> None:
        blob = ho.seal_bytes(b"holdout bytes", ho.ACKNOWLEDGEMENT, self.SALT, self.NONCE)
        assert b"holdout bytes" not in blob
        sha = ho.sha256_bytes(b"holdout bytes")
        assert ho.open_sealed(blob, ho.ACKNOWLEDGEMENT, self.SALT, sha) == b"holdout bytes"
        with pytest.raises(ho.SealIntegrityError):
            ho.open_sealed(blob, ho.ACKNOWLEDGEMENT + " ", self.SALT, sha)

    def test_tamper_and_format_are_detected(self) -> None:
        payload = b"abc" * 100
        blob = bytearray(ho.seal_bytes(payload, ho.ACKNOWLEDGEMENT, self.SALT, self.NONCE))
        blob[-1] ^= 0xFF
        with pytest.raises(ho.SealIntegrityError):
            ho.open_sealed(bytes(blob), ho.ACKNOWLEDGEMENT, self.SALT, ho.sha256_bytes(payload))
        with pytest.raises(ho.SealIntegrityError, match="not a sealed blob"):
            ho.open_sealed(b"PAR1....", ho.ACKNOWLEDGEMENT, self.SALT, "0")
        with pytest.raises(ValueError):
            ho.seal_bytes(b"x", ho.ACKNOWLEDGEMENT, self.SALT, b"short")


class TestSealMigration:
    def test_plaintext_holdout_is_gone_everywhere(self, sealed, tmp_path: Path) -> None:
        paths, manifest, raws, _ = sealed
        assert not (tmp_path / "processed" / "full.parquet").exists()
        assert raws[0].exists()  # May holds no holdout bar: untouched
        assert not raws[1].exists() and not raws[2].exists()
        research = pq.read_table(paths.research_parquet).to_pandas()
        assert list(research["trade_date"]) == DATES[:3]
        assert not (paths.research_parquet.stat().st_mode & 0o222), "research file is read-only"
        assert manifest["holdout"]["rows"] == 3 and manifest["research"]["rows"] == 3
        assert b"trade_date" not in paths.holdout_blob.read_bytes()  # not a readable parquet
        with pytest.raises(Exception):  # noqa: B017 — any parquet error proves unreadability
            pq.read_table(paths.holdout_blob)

    def test_manifest_log_and_verify(self, sealed) -> None:
        paths, manifest, raws, _ = sealed
        assert [Path(r["original_path"]).name for r in manifest["raw_files"]] == [
            raws[1].name, raws[2].name]
        assert "SEALED" in paths.unlock_log.read_text()
        assert ho.prior_unlocks(paths) == 0
        report = ho.verify_seal(paths)
        assert report["all_ok"] and report["research_has_no_holdout_rows"]
        assert ho.is_sealed_raw(raws[1], paths) and not ho.is_sealed_raw(raws[0], paths)

    def test_manifest_contains_no_prices(self, sealed) -> None:
        paths, *_ = sealed
        text = paths.manifest.read_text()
        assert "6000" not in text and "close" not in text

    def test_sealing_twice_is_refused(self, sealed, tmp_path: Path) -> None:
        paths, *_ = sealed
        with pytest.raises(FileExistsError):
            ho.seal_holdout(tmp_path / "whatever.parquet", [], paths, remove_plaintext=False)


class TestUnlockCeremony:
    @pytest.mark.parametrize(("kwargs", "match"), [
        ({"acknowledgement": "I accept"}, "acknowledgement"),
        ({"stage": "D.1"}, "not Stage D.2"),
        ({"stage": "D.21"}, "not Stage D.2"),
        ({"stage": "D.2.1"}, "not Stage D.2"),
        ({"stage": "D.2\n## forged UNLOCK"}, "not Stage D.2"),
        ({"reason": REASON + "\n## forged UNLOCK heading"}, "no newlines"),
        ({"reason": REASON + " #1"}, "no newlines"),
        ({"reason": "because"}, "real reason"),
        ({"prior_unlocks_acknowledged": 1}, "prior unlock"),
    ])
    def test_refusals_decrypt_nothing_and_log_nothing(self, sealed, kwargs, match) -> None:
        paths, *_ = sealed
        paths.registration.write_text(REGISTRATION)
        before = paths.unlock_log.read_text()
        call = {"stage": "Stage D.2", "reason": REASON, "acknowledgement": ho.ACKNOWLEDGEMENT,
                "prior_unlocks_acknowledged": 0} | kwargs
        with pytest.raises(ho.HoldoutLockedError, match=match):
            ho.unlock_holdout(paths=paths, **call)
        assert paths.unlock_log.read_text() == before

    @pytest.mark.parametrize("registration", [
        None, "", "   \n", "TBD",
        "x" * 300,  # long enough, but states no metric/threshold/decision
        REGISTRATION.replace("threshold", "bar"),  # a required word missing
    ])
    def test_registration_must_be_a_real_pre_registration(self, sealed, registration) -> None:
        paths, *_ = sealed
        if registration is not None:
            paths.registration.write_text(registration)
        with pytest.raises(ho.HoldoutLockedError, match="pre-registered bar"):
            ho.unlock_holdout(stage="D.2", reason=REASON, acknowledgement=ho.ACKNOWLEDGEMENT,
                              paths=paths)

    def test_unlock_logs_first_then_returns_exact_rows(self, sealed) -> None:
        paths, _, _, frame = sealed
        paths.registration.write_text(REGISTRATION)
        rows = ho.unlock_holdout(stage="Stage D.2", reason=REASON,
                                 acknowledgement=ho.ACKNOWLEDGEMENT, paths=paths)
        assert rows.equals(frame.iloc[3:].reset_index(drop=True))
        log = paths.unlock_log.read_text()
        assert "UNLOCK holdout bars (Stage D.2)" in log and REASON in log
        assert ho.sha256_file(paths.registration) in log
        assert ho.prior_unlocks(paths) == 1
        with pytest.raises(ho.HoldoutLockedError, match="1 prior unlock"):
            ho.unlock_holdout(stage="D.2", reason=REASON, acknowledgement=ho.ACKNOWLEDGEMENT,
                              paths=paths)
        ho.unlock_holdout(stage="D.2", reason=REASON, acknowledgement=ho.ACKNOWLEDGEMENT,
                          prior_unlocks_acknowledged=1, paths=paths)
        assert ho.prior_unlocks(paths) == 2

    def test_tampered_blob_is_refused_before_logging(self, sealed) -> None:
        paths, *_ = sealed
        paths.registration.write_text(REGISTRATION)
        blob = bytearray(paths.holdout_blob.read_bytes())
        blob[-1] ^= 0x01
        paths.holdout_blob.write_bytes(bytes(blob))
        before = paths.unlock_log.read_text()
        with pytest.raises(ho.SealIntegrityError):
            ho.unlock_holdout(stage="D.2", reason=REASON, acknowledgement=ho.ACKNOWLEDGEMENT,
                              paths=paths)
        assert paths.unlock_log.read_text() == before
        assert not ho.verify_seal(paths)["all_ok"]


class TestPaidRawSafety:
    def test_unseal_restores_identical_read_only_bytes(self, sealed) -> None:
        paths, _, raws, _ = sealed
        paths.registration.write_text(REGISTRATION)
        restored = ho.unseal_raw_file(raws[1], stage="D.2", reason=REASON,
                                      acknowledgement=ho.ACKNOWLEDGEMENT, paths=paths)
        assert restored.read_bytes() == b"june-bytes" * 50
        assert not (restored.stat().st_mode & 0o222)
        with pytest.raises(FileExistsError):
            ho.unseal_raw_file(raws[1], stage="D.2", reason=REASON,
                               acknowledgement=ho.ACKNOWLEDGEMENT,
                               prior_unlocks_acknowledged=1, paths=paths)
        with pytest.raises(KeyError):
            ho.unseal_raw_file(raws[0], stage="D.2", reason=REASON,
                               acknowledgement=ho.ACKNOWLEDGEMENT,
                               prior_unlocks_acknowledged=1, paths=paths)

    def test_adapter_refuses_to_rebuy_a_sealed_range(self, sealed, monkeypatch) -> None:
        paths, _, raws, _ = sealed
        monkeypatch.setattr(ho, "DEFAULT_PATHS", paths)
        with pytest.raises(adapter.RawFileExistsError, match="sealed holdout store"):
            adapter._refuse_existing(raws[1])
        adapter._refuse_existing(raws[0].with_name("range=2026-01-01_2026-02-01.dbn.zst"))


class TestSealedWindowAndLogPin:
    def test_a_request_overlapping_the_sealed_window_is_refused_before_any_quote(self) -> None:
        # The sealed window runs from the first holdout session (opens 2026-06-21 17:00 CT) to
        # the day after the last sealed trade date (2026-09-17).
        assert ho.sealed_window_utc_dates() == ("2026-06-21", "2026-09-17")
        assert ho.request_touches_sealed_window("2026-09-01", "2026-10-01")  # straddles the end
        assert ho.request_touches_sealed_window("2026-06-01", "2026-07-01")
        assert not ho.request_touches_sealed_window("2026-05-01", "2026-06-01")  # ends before
        assert not ho.request_touches_sealed_window("2026-09-17", "2026-10-01")  # Stage E data

    def test_fetch_range_refuses_a_sealed_window_request(self, tmp_path: Path) -> None:
        from data.spend_gate import RequestParams

        class NoClient:
            def __getattr__(self, name):  # any use at all is a failure
                raise AssertionError("the request must be refused before the client is touched")

        params = RequestParams("GLBX.MDP3", ("MES.v.0",), "ohlcv-1m", "continuous",
                               "2026-09-01", "2026-10-01")
        with pytest.raises(adapter.RawFileExistsError, match="sealed holdout window"):
            adapter.fetch_range(NoClient(), NoClient(), params, root=tmp_path)

    def test_deleting_or_rewriting_the_unlock_log_fails_verification(self, sealed) -> None:
        paths, *_ = sealed
        assert ho.verify_seal(paths)["unlock_log_ok"]
        original = paths.unlock_log.read_text()
        paths.unlock_log.unlink()
        assert not ho.verify_seal(paths)["all_ok"]  # a missing log is not "ok"
        paths.unlock_log.write_text(original.replace("SEALED", "sealed"))
        assert not ho.verify_seal(paths)["unlock_log_ok"]  # rewritten history
        paths.unlock_log.write_text(original)
        assert ho.verify_seal(paths)["all_ok"]

    def test_manifest_records_a_repo_relative_path_when_the_file_is_inside_the_repo(self) -> None:
        # Fixture files live in tmp_path (outside the repo), so their relpath is None; the real
        # manifest's raw files are inside the repo and carry one.
        assert ho._relpath_in_repo(Path("/nowhere/else/x.dbn.zst")) is None
        if ho.DEFAULT_PATHS.manifest.exists():
            records = ho.load_manifest()["raw_files"]
            assert all(r.get("original_relpath", "").startswith("data/vendor") for r in records)


class TestResearchLoaderGuard:
    def test_holdout_row_in_a_research_path_raises(self) -> None:
        with pytest.raises(HoldoutLeakError):
            assert_no_holdout_rows(pd.DataFrame({"trade_date": ["2026-06-19", "2026-06-22"]}))
        assert_no_holdout_rows(pd.DataFrame({"trade_date": ["2026-06-19"]}))

    def test_paths_agree(self) -> None:
        assert RESEARCH_SERIES_PATH.name == RESEARCH_PARQUET_NAME
        assert ho.DEFAULT_PATHS.research_parquet == RESEARCH_SERIES_PATH


@pytest.mark.skipif(not ho.DEFAULT_PATHS.manifest.exists(), reason="holdout not sealed here")
class TestRealStore:
    def test_real_seal_verifies_without_decrypting(self) -> None:
        report = ho.verify_seal()
        assert report["all_ok"], report

    def test_no_plaintext_parquet_under_data_holds_a_holdout_date(self) -> None:
        root = Path(ho.DATA_ROOT)
        for parquet in root.rglob("*.parquet"):
            dates = pq.read_table(parquet, columns=["trade_date"]).column("trade_date").to_pylist()
            assert max(dates, default="") < HOLDOUT_START.isoformat(), parquet
        assert not (root / "processed" / "MES" / ho.ORIGINAL_FULL_PARQUET_NAME).exists()
