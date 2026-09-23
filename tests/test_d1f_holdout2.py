"""Stage D.1f holdout 2: sealed on arrival (reports/stage_d1f_confirmation_list.md 1.2, 5.2).

Synthetic chunks only. Every test that seals, pulls or unlocks points data.holdout's
DEFAULT_PATHS and HOLDOUT2_PATHS at a repo laid out under pytest's tmp_path, uses a stub
vendor client and the D.1f gate on tmp ledgers, and runs with ``databento`` blocked in
sys.modules, so neither the vendor package nor the network can be reached. The real sealed
stores, manifests, unlock log and ledger are only ever read (the last class), never written.

The stub client mirrors the audited databento 0.82.0 path fetch_range uses:
``timeseries.get_range(path=...)`` opens ``path`` with "x+b" and streams the response there
and nowhere else (databento/common/http.py ``_stream``); the package has no disk cache and no
tempfile use. TestVendorAudit pins that finding to the installed version.
"""

from __future__ import annotations

import dataclasses
import importlib.metadata
import json
import os
import re
import secrets
import stat
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from data import adapter, pull_mes
from data import holdout as ho
from data.adapter import MES_CONTINUOUS, OHLCV_1M, raw_path
from data.config import (
    D1F_REQUEST_CAP_USD,
    D1F_SESSION_CAP_USD,
    PROCESSED_ROOT,
    REPO_ROOT,
    STAGE_D1F_SESSION_ID,
    VENDOR_ROOT,
)
from data.research_bars import (
    CONFIRMATION_RAW_CHUNKS,
    CONFIRMATION_SERIES_PATH,
    HOLDOUT2_RAW_CHUNKS,
    RESEARCH_PARQUET_NAME,
)
from data.spend_gate import BudgetRefusedError, SpendGate, read_entries

REASON = "Stage D.2 pre-registered read of holdout 2 for candidate X"
REGISTRATION = (
    "# Stage D.2 pre-registration\n\n"
    "metric: mean daily net P&L per micro over the holdout-2 trade dates.\n"
    "threshold: mean > $0 and a one-sided t-statistic of at least 1.28.\n"
    "decision: if the threshold is met, proceed to the Stage E practice-account forward test; "
    "otherwise abandon the candidate and return to Stage D.1 research.\n"
)
H2_NAMES = [f"range={s}_{e}.dbn.zst" for s, e in HOLDOUT2_RAW_CHUNKS]
# Where a vendor client could keep a cache. databento 0.82.0 keeps none (TestVendorAudit).
CLIENT_CACHE_CANDIDATES = (
    Path.home() / ".cache" / "databento",
    Path.home() / ".databento",
    Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / "databento",
)


@dataclasses.dataclass(frozen=True)
class World:
    root: Path
    vendor: Path
    h1: ho.HoldoutPaths
    h2: ho.HoldoutPaths
    gate: pull_mes.RequestCappedGate
    ledger: Path
    access: Path
    log: list[str]


class StubClient:
    """Quotes every request at ``usd`` (or ``prices``), writes random bytes to ``path`` with
    "x+b" exactly like databento's _stream, and records what it wrote. Nothing else is written.
    ``observe`` (holdout-2 paths) records, at each download, how many chunks were sealed."""

    def __init__(self, usd: float = 0.10, prices: dict | None = None,
                 observe: ho.HoldoutPaths | None = None) -> None:
        self.usd, self.prices, self.observe = usd, prices or {}, observe
        self.quotes: list[tuple[str, str]] = []
        self.requests: list[tuple[str, str]] = []
        self.writes: dict[tuple[str, str], dict] = {}
        self.sealed_before: list[int] = []
        self.metadata = SimpleNamespace(get_cost=self._cost, get_billable_size=lambda **_: 10**7)
        self.timeseries = SimpleNamespace(get_range=self._get_range)

    def _cost(self, **kw) -> float:
        self.quotes.append((kw["start"], kw["end"]))
        return self.prices.get((kw["start"], kw["end"]), self.usd)

    def _get_range(self, *, dataset, symbols, schema, stype_in, start, end, path) -> None:
        assert (dataset, symbols, schema, stype_in) == (
            "GLBX.MDP3", ["MES.v.0"], "ohlcv-1m", "continuous")
        if self.observe is not None:
            m = self.observe.manifest
            self.sealed_before.append(
                len(json.loads(m.read_text())["raw_files"]) if m.exists() else 0)
        payload = secrets.token_bytes(4096 + 37 * len(self.writes))  # unique size and content
        with open(path, "x+b") as fh:
            fh.write(payload)
        self.requests.append((start, end))
        self.writes[(start, end)] = {"path": Path(path), "bytes": len(payload),
                                     "sha256": ho.sha256_bytes(payload)}


@pytest.fixture(autouse=True)
def no_vendor_package(monkeypatch) -> None:
    """``import databento`` fails for the whole test; the record-byte check reads the size."""
    monkeypatch.setitem(sys.modules, "databento", None)
    monkeypatch.setattr(adapter, "delivered_record_bytes", lambda path: Path(path).stat().st_size)


@pytest.fixture
def world(tmp_path: Path, monkeypatch) -> World:
    root = tmp_path / "repo"
    docs = root / "docs"
    vendor = root / "data" / "vendor" / "databento"
    h1 = ho.HoldoutPaths(
        sealed_root=root / "data" / "sealed" / "MES_holdout_v1",
        manifest=docs / "HOLDOUT_MANIFEST.json", unlock_log=docs / "HOLDOUT_UNLOCK_LOG.md",
        registration=root / "REGISTRATION.md",
        research_parquet=root / "data" / "processed" / "MES" / "research.parquet")
    h2 = dataclasses.replace(
        h1, sealed_root=root / "data" / "sealed" / "MES_holdout_v2",
        manifest=docs / "HOLDOUT2_MANIFEST.json",
        research_parquet=root / "data" / "processed" / "MES" / "confirmation.parquet",
        holdout_id=2, vendor_root=vendor)
    monkeypatch.setattr(ho, "DEFAULT_PATHS", h1)
    monkeypatch.setattr(ho, "HOLDOUT2_PATHS", h2)
    monkeypatch.setattr(pull_mes, "d1f_freeze_check", lambda: ([], "0" * 64))  # review F2
    external = root / "external_ledger.jsonl"
    external.parent.mkdir(parents=True)
    external.write_text("")
    ledger, access = root / "ledger" / "spend.jsonl", docs / "ACCESS.md"
    gate = pull_mes.d1f_gate(ledger_path=ledger, external_ledger_paths=(external,),
                             access_doc_path=access)
    return World(root, vendor, h1, h2, gate, ledger, access, [])


def _pull(world: World, client: StubClient, gate: SpendGate | None = None) -> list[dict]:
    return pull_mes.pull_d1f(client, gate or world.gate, root=world.vendor, log=world.log.append)


def _target(world: World, chunk: tuple[str, str]) -> Path:
    return raw_path(MES_CONTINUOUS, OHLCV_1M, chunk[0], chunk[1], world.vendor)


def _gate(world: World, **caps) -> pull_mes.RequestCappedGate:
    return pull_mes.d1f_gate(ledger_path=world.gate.ledger_path,
                             external_ledger_paths=world.gate.external_ledger_paths,
                             access_doc_path=world.access, **caps)


def _files_holding(roots: list[Path], wanted: dict[str, int]) -> dict[str, set[Path]]:
    """sha256 -> regular files under ``roots`` whose CONTENT hashes to it. Names are ignored;
    only files of a wanted size are hashed, and FIFOs, sockets and symlinks are skipped."""
    sizes, found = set(wanted.values()), {}
    for root in roots:
        if not root.is_dir():
            continue
        for dirpath, _dirs, names in os.walk(root, onerror=lambda _e: None):
            for name in names:
                path = Path(dirpath, name)
                try:
                    st = path.lstat()
                    if not stat.S_ISREG(st.st_mode) or st.st_size not in sizes:
                        continue
                    digest = ho.sha256_bytes(path.read_bytes())
                except OSError:
                    continue
                if digest in wanted:
                    found.setdefault(digest, set()).add(path.resolve())
    return found


def _list_in_manifest(paths: ho.HoldoutPaths, targets: list[Path]) -> None:
    """A hand-made manifest that lists ``targets`` as sealed raw files."""
    paths.manifest.parent.mkdir(parents=True, exist_ok=True)
    paths.manifest.write_text(json.dumps({"raw_files": [
        {"original_path": str(t), "original_relpath": None, "sealed_relpath": "raw/x",
         "bytes": 1, "sha256_plaintext": "0", "sha256_sealed": "0"} for t in targets]}))


def _seal_holdout1(world: World) -> pd.DataFrame:
    """A small synthetic holdout 1 in the same tmp repo (same unlock log and registration)."""
    frame = pd.DataFrame([{"ts_event": 1_781_000_000_000_000_000 + k * 60_000_000_000,
                           "close": 6000.0 + k * 0.25, "trade_date": d} for k, d in
                          enumerate(["2026-06-18", "2026-06-19", "2026-06-22", "2026-06-23"])])
    full = world.root / "data" / "processed" / "MES" / "full.parquet"
    full.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(pa.Table.from_pandas(frame, preserve_index=False), full)
    raw = world.root / "h1raw" / "range=2026-06-01_2026-07-01.dbn.zst"
    raw.parent.mkdir(parents=True)
    raw.write_bytes(b"june" * 100)
    ho.seal_holdout(full, [raw], world.h1, remove_plaintext=True)
    return frame


def _place(world: World, chunk: tuple[str, str], payload: bytes | None = None) -> Path:
    target = _target(world, chunk)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(payload if payload is not None else secrets.token_bytes(999))
    return target


class TestChunkPlan:
    def test_71_chunks_oldest_first_58_confirmation_then_13_holdout2(self) -> None:
        chunks = pull_mes.d1f_chunks()
        assert len(chunks) == 71 and chunks == sorted(chunks)
        assert chunks[0] == ("2019-05-01", "2019-06-01")
        assert chunks[-1] == ("2025-03-01", "2025-04-01")  # ends where the existing raw begins
        assert chunks[:58] == list(CONFIRMATION_RAW_CHUNKS)
        assert chunks[58:] == list(HOLDOUT2_RAW_CHUNKS) and len(HOLDOUT2_RAW_CHUNKS) == 13
        assert HOLDOUT2_RAW_CHUNKS[0] == ("2024-03-01", "2024-04-01")

    def test_the_default_gate_is_the_d1f_session_with_both_caps(self) -> None:
        gate = pull_mes.d1f_gate()  # constructing it reads and writes nothing
        assert gate.session_id == STAGE_D1F_SESSION_ID
        assert gate.session_cap_usd == D1F_SESSION_CAP_USD
        assert gate.request_cap_usd == D1F_REQUEST_CAP_USD


class TestSealOnArrival:
    def test_buys_all_71_oldest_first_and_seals_exactly_the_13(self, world) -> None:
        client = StubClient()
        done = _pull(world, client)
        assert client.requests == pull_mes.d1f_chunks() == client.quotes
        sealed = "bought and SEALED as holdout 2"
        assert [d["action"] for d in done] == ["bought"] * 58 + [sealed] * 13
        for chunk in CONFIRMATION_RAW_CHUNKS:  # the 58 stay plaintext, read-only, never sealed
            target = _target(world, chunk)
            assert ho.sha256_file(target) == client.writes[chunk]["sha256"]
            assert not target.stat().st_mode & 0o222
            assert not ho.is_sealed_raw(target)
        manifest = ho.load_manifest(world.h2)
        assert [Path(r["original_path"]).name for r in manifest["raw_files"]] == H2_NAMES
        headings = [ln for ln in world.h2.unlock_log.read_text().splitlines()
                    if ln.startswith("## ")]
        assert [h.split(" SEALED holdout 2 raw chunk ")[1] for h in headings] == H2_NAMES

    def test_each_chunk_is_sealed_before_the_next_is_requested(self, world) -> None:
        client = StubClient(observe=world.h2)
        _pull(world, client)
        # At download i the manifest already lists every holdout-2 chunk bought before it.
        assert client.sealed_before == [max(0, i - 58) for i in range(71)]

    def test_i_no_plaintext_of_a_sealed_chunk_survives_anywhere(self, world) -> None:
        client = StubClient()
        _pull(world, client)
        sealed = {client.writes[c]["sha256"]: client.writes[c]["bytes"]
                  for c in HOLDOUT2_RAW_CHUNKS}
        kept = {client.writes[c]["sha256"]: client.writes[c]["bytes"]
                for c in CONFIRMATION_RAW_CHUNKS}
        roots = [world.root, Path("/tmp"), Path(tempfile.gettempdir()), REPO_ROOT,
                 *CLIENT_CACHE_CANDIDATES]
        found = _files_holding(roots, {**sealed, **kept})
        assert not {sha for sha in found if sha in sealed}, "sealed plaintext survived"
        # Positive control: the same scan finds each of the 58 unsealed chunks, by content only.
        assert {sha: paths for sha, paths in found.items() if sha in kept} == {
            client.writes[c]["sha256"]: {_target(world, c).resolve()}
            for c in CONFIRMATION_RAW_CHUNKS}
        # The client wrote only fetch_range's in-flight names, and none of them is left.
        for chunk, write in client.writes.items():
            assert write["path"] == ho.partial_path(_target(world, chunk))
            assert not write["path"].exists()

    def test_ii_the_manifest_lists_13_records_with_both_sha256s_and_nothing_else(
            self, world) -> None:
        client = StubClient()
        _pull(world, client)
        manifest = ho.load_manifest(world.h2)
        records = manifest["raw_files"]
        assert len(records) == 13
        for record, chunk in zip(records, HOLDOUT2_RAW_CHUNKS, strict=True):
            assert set(record) == {"original_path", "original_relpath", "sealed_relpath",
                                   "bytes", "sha256_plaintext", "sha256_sealed"}
            assert record["sha256_plaintext"] == client.writes[chunk]["sha256"]
            assert record["bytes"] == client.writes[chunk]["bytes"]
            blob = world.h2.sealed_root / record["sealed_relpath"]
            assert ho.sha256_file(blob) == record["sha256_sealed"] != record["sha256_plaintext"]
        assert manifest["expected_raw_chunks"] == H2_NAMES
        assert manifest["unlock_log_at_seal"] == {
            "bytes": world.h2.unlock_log.stat().st_size,
            "sha256": ho.sha256_file(world.h2.unlock_log)}
        text = world.h2.manifest.read_text()
        assert "rows" not in text and "trade_dates" not in text and "close" not in text

    def test_iii_verify_seal_reports_all_ok_with_plaintext_absent_for_all_13(self, world) -> None:
        _pull(world, StubClient())
        report = ho.verify_seal(world.h2)
        assert report["all_ok"] and report["state"] == "sealed" and report["unlock_log_ok"]
        assert report["chunks_sealed"] == 13 and report["sealed_in_order"]
        assert sorted(report["raw_files"]) == sorted(H2_NAMES)
        assert all(v == {"sealed_ok": True, "plaintext_absent": True}
                   for v in report["raw_files"].values())
        assert report["unlocks_logged"] == 0 and report["unsealed_plaintext_present"] == []

    def test_v_status_reports_both_holdouts(self, world, capsys) -> None:
        _seal_holdout1(world)
        assert ho.main(["data.holdout", "status"]) == 0
        before = json.loads(capsys.readouterr().out)
        assert before["all_ok"] and before["unlocks_logged"] == 0  # holdout 1, unchanged keys
        assert {"holdout_blob_ok", "research_parquet_ok", "raw_files", "unlock_log_ok",
                "research_has_no_holdout_rows"} <= set(before)
        assert before["holdout_2"]["state"] == "not_yet_sealed"
        assert not before["holdout_2"]["all_ok"]
        _pull(world, StubClient())
        assert ho.main(["data.holdout", "status"]) == 0
        after = json.loads(capsys.readouterr().out)
        assert after["all_ok"] and after["unlocks_logged"] == 0
        assert after["holdout_2"]["all_ok"] and after["holdout_2"]["chunks_sealed"] == 13
        assert after["holdout_2"]["unlocks_logged"] == 0

    def test_the_cli_pulls_into_the_holdout2_vendor_root(self, world, monkeypatch,
                                                          capsys) -> None:
        client = StubClient()
        monkeypatch.setitem(sys.modules, "databento", SimpleNamespace(Historical=lambda _k: client))
        monkeypatch.setattr(pull_mes, "require_databento_key", lambda: "stub-key")
        monkeypatch.setattr(pull_mes, "d1f_gate", lambda: world.gate)
        monkeypatch.setattr(sys, "argv", ["pull_mes", "--d1f-quote-only"])
        assert pull_mes.main() == 0 and client.requests == [] and len(client.quotes) == 71
        assert not any(e["event"] == "commit" for e in read_entries(world.ledger))
        monkeypatch.setattr(sys, "argv", ["pull_mes", "--d1f-pull"])
        assert pull_mes.main() == 0 and client.requests == pull_mes.d1f_chunks()
        assert "holdout 2: sealed, 13 chunks, all_ok True" in capsys.readouterr().out


class TestPullRefusals:
    def test_a_rerun_buys_nothing(self, world) -> None:
        _pull(world, StubClient())
        commits = sum(e["event"] == "commit" for e in read_entries(world.ledger))
        again = StubClient()
        done = _pull(world, again)
        assert again.requests == [] and again.quotes == []
        assert sum(e["event"] == "commit" for e in read_entries(world.ledger)) == commits == 71
        assert {d["action"] for d in done[58:]} == {"skipped: sealed as holdout 2, never re-bought"}
        assert {d["action"] for d in done[:58]} == {"skipped: already on disk, never re-bought"}

    def test_a_chunk_listed_in_the_holdout1_manifest_is_never_bought(self, world) -> None:
        first = CONFIRMATION_RAW_CHUNKS[0]
        _list_in_manifest(world.h1, [_target(world, first)])
        client = StubClient()
        done = _pull(world, client)
        assert first not in client.requests and len(client.requests) == 70
        assert done[0]["action"] == "skipped: sealed as holdout 1, never re-bought"

    def test_an_out_of_order_holdout2_chunk_is_refused_before_it_is_bought(self, world) -> None:
        _list_in_manifest(world.h1, [_target(world, HOLDOUT2_RAW_CHUNKS[0])])  # 2024-03 skipped
        client = StubClient()
        with pytest.raises(ho.SealIntegrityError, match="out of order"):
            _pull(world, client)
        assert client.requests == list(CONFIRMATION_RAW_CHUNKS)  # 2024-04 was never requested

    def test_sealed_holdout2_ranges_are_refused_by_every_download_path(self, world) -> None:
        _pull(world, StubClient())
        target = _target(world, HOLDOUT2_RAW_CHUNKS[4])
        assert ho.is_sealed_raw(target)  # the default checks both manifests (A.1, builder)
        with pytest.raises(adapter.RawFileExistsError, match="sealed holdout store"):
            adapter._refuse_existing(target)
        assert ho.request_touches_sealed_window("2024-06-15", "2024-07-15")  # any schema/range
        assert not ho.request_touches_sealed_window("2024-02-01", "2024-03-01")
        assert not ho.request_touches_sealed_window("2025-04-01", "2025-05-01")

        class NoClient:
            def __getattr__(self, name):
                raise AssertionError("refused before the client or gate is touched")

        params = pull_mes._d1f_params("2024-06-15", "2024-07-15")
        with pytest.raises(adapter.RawFileExistsError):
            adapter.fetch_range(NoClient(), NoClient(), params, root=world.vendor)

    @pytest.mark.parametrize(("price", "refused"), [(10.00, False), (10.01, True)])
    def test_the_per_request_cap(self, world, price, refused) -> None:
        third = CONFIRMATION_RAW_CHUNKS[2]
        client = StubClient(prices={third: price})
        gate = _gate(world, session_cap_usd=100.0)  # the session cap cannot be what refuses
        if not refused:
            _pull(world, client, gate)
            assert third in client.requests
            return
        with pytest.raises(BudgetRefusedError, match="per-request cap"):
            _pull(world, client, gate)
        assert client.requests == list(CONFIRMATION_RAW_CHUNKS[:2])
        entries = read_entries(world.ledger)
        assert [e["event"] for e in entries if e["date"] == f"{third[0]}..{third[1]}"] == [
            "quote", "refused"]
        assert "per-request cap" in world.access.read_text()

    def test_the_d1f_session_cap_stops_the_pull(self, world) -> None:
        client = StubClient(usd=0.50)  # 20 chunks reach the $10 cap exactly; the 21st is refused
        with pytest.raises(BudgetRefusedError, match="session cap"):
            _pull(world, client)
        assert client.requests == list(CONFIRMATION_RAW_CHUNKS[:20])

    def test_a_gate_without_the_request_cap_or_a_foreign_vendor_root_is_refused(
            self, world) -> None:
        client = StubClient()
        plain = SpendGate(STAGE_D1F_SESSION_ID, ledger_path=world.ledger,
                          external_ledger_paths=world.gate.external_ledger_paths)
        with pytest.raises(TypeError, match="per-request cap"):
            _pull(world, client, plain)
        with pytest.raises(ValueError, match="holdout 2 seals chunks under"):
            pull_mes.pull_d1f(client, world.gate, root=world.root / "elsewhere")
        assert client.quotes == [] and client.requests == []

    def test_the_a1_pull_refuses_a_chunk_listed_in_the_holdout2_manifest(
            self, world, monkeypatch) -> None:
        a1_root = world.root / "a1vendor"
        listed = ("2025-05-01", "2025-06-01")
        _list_in_manifest(world.h2, [raw_path(MES_CONTINUOUS, OHLCV_1M, *listed, a1_root)])
        fetched = []
        client = SimpleNamespace(metadata=SimpleNamespace(get_dataset_range=lambda **_: "stub"))
        monkeypatch.setitem(sys.modules, "databento", SimpleNamespace(Historical=lambda _k: client))
        monkeypatch.setattr(pull_mes, "require_databento_key", lambda: "stub-key")
        monkeypatch.setattr(pull_mes, "SpendGate", lambda sid: _gate(world))
        monkeypatch.setattr(pull_mes, "raw_path",
                            lambda sym, schema, s, e: raw_path(sym, schema, s, e, a1_root))
        monkeypatch.setattr(pull_mes, "fetch_range", lambda gate, client, params, note: (
            fetched.append((params.start, params.end)) or Path(params.start)))
        monkeypatch.setattr(sys, "argv", ["pull_mes", "--pull"])
        assert pull_mes.main() == 0
        h1_start, h1_end = ho.sealed_window_utc_dates()
        expected = [c for c in reversed(pull_mes.monthly_chunks(pull_mes.WINDOW_START,
                                                                pull_mes.WINDOW_END))
                    if c != listed and not (c[0] < h1_end and c[1] > h1_start)]
        assert fetched == expected and len(fetched) == 13  # 18 chunks - 4 sealed - 1 listed


class TestSealingFailures:
    def test_a_sealing_failure_stops_the_pull_keeps_the_plaintext_and_resumes(
            self, world, monkeypatch) -> None:
        real, calls = ho.seal_bytes, []

        def corrupt_third(plaintext, *args):
            calls.append(1)
            blob = real(plaintext, *args)
            return blob[:-1] + bytes([blob[-1] ^ 1]) if len(calls) == 3 else blob

        monkeypatch.setattr(ho, "seal_bytes", corrupt_third)
        client = StubClient()
        with pytest.raises(ho.SealIntegrityError):
            _pull(world, client)
        failed = HOLDOUT2_RAW_CHUNKS[2]
        assert client.requests[-1] == failed  # nothing after the failed chunk was requested
        assert len(ho.load_manifest(world.h2)["raw_files"]) == 2
        assert ho.sha256_file(_target(world, failed)) == client.writes[failed]["sha256"]
        assert not (world.h2.sealed_root / "raw" / (H2_NAMES[2] + ".sealed")).exists()

        monkeypatch.setattr(ho, "seal_bytes", real)
        resumed = StubClient()
        done = _pull(world, resumed)
        assert resumed.requests == list(HOLDOUT2_RAW_CHUNKS[3:])  # the failed one not re-bought
        assert done[60]["action"].startswith("SEALED as holdout 2 on resume")
        record = ho.load_manifest(world.h2)["raw_files"][2]
        assert record["sha256_plaintext"] == client.writes[failed]["sha256"]
        assert ho.verify_seal(world.h2)["all_ok"]
        assert "sealed on resume" in world.h2.unlock_log.read_text()

    def test_a_crash_before_the_manifest_leaves_the_plaintext_and_blocks_a_rerun(
            self, world, monkeypatch) -> None:
        real = ho._write_manifest

        def no_disk(*_a, **_k):
            raise OSError("disk full")

        monkeypatch.setattr(ho, "_write_manifest", no_disk)
        client = StubClient()
        with pytest.raises(OSError, match="disk full"):
            _pull(world, client)
        first = HOLDOUT2_RAW_CHUNKS[0]
        assert client.requests[-1] == first and not world.h2.manifest.exists()
        assert ho.sha256_file(_target(world, first)) == client.writes[first]["sha256"]
        monkeypatch.setattr(ho, "_write_manifest", real)
        again = StubClient()
        with pytest.raises(FileExistsError, match="interrupted"):  # the orphan blob
            _pull(world, again)
        assert again.requests == [] and _target(world, first).exists()

    def test_plaintext_of_a_sealed_chunk_on_disk_stops_the_pull(self, world) -> None:
        _pull(world, StubClient())
        _place(world, HOLDOUT2_RAW_CHUNKS[0])
        again = StubClient()
        with pytest.raises(ho.SealIntegrityError, match="interrupted"):
            _pull(world, again)
        assert again.requests == []
        report = ho.verify_seal(world.h2)
        assert not report["all_ok"] and not report["raw_files"][H2_NAMES[0]]["plaintext_absent"]


def _crash_at_unlink(monkeypatch, target: Path) -> None:
    """The first unlink of ``target`` fails, as a crash between the log pin and the plaintext
    removal would leave it; every other unlink (and every later one) is the real one."""
    real, armed = Path.unlink, [True]

    def unlink(self, missing_ok=False):
        if armed[0] and self == target:
            armed[0] = False
            raise OSError("power cut before the plaintext removal")
        return real(self, missing_ok=missing_ok)

    monkeypatch.setattr(Path, "unlink", unlink)


def _interrupted_seal(world: World, monkeypatch) -> tuple[Path, bytes]:
    """Holdout-2 chunk 1 cut off after its manifest record, SEALED entry and log pin, with its
    plaintext still on disk (the D2 state)."""
    payload = secrets.token_bytes(777)
    target = _place(world, HOLDOUT2_RAW_CHUNKS[0], payload)
    _crash_at_unlink(monkeypatch, target)
    with pytest.raises(OSError, match="power cut"):
        ho.seal_holdout2_chunk(target, world.h2)
    assert ho.is_sealed_raw(target, world.h2) and target.read_bytes() == payload
    assert ho.load_manifest(world.h2)["unlock_log_at_seal"]["bytes"] == (
        world.h2.unlock_log.stat().st_size)
    return target, payload


class TestResume:
    """D1: a chunk found on disk gets the record-byte check before it is sealed on resume. D2: a
    seal cut off after its manifest record is finished by complete_interrupted_seal."""

    def test_d1_a_chunk_found_on_disk_is_record_byte_checked_before_it_is_sealed(
            self, world, monkeypatch) -> None:
        first = HOLDOUT2_RAW_CHUNKS[0]

        def stop_between_link_and_settle(path):
            if Path(path).name == H2_NAMES[0]:
                raise RuntimeError("interrupted between fetch_range's link and its settle")
            return Path(path).stat().st_size

        monkeypatch.setattr(adapter, "delivered_record_bytes", stop_between_link_and_settle)
        client = StubClient()
        with pytest.raises(RuntimeError, match="interrupted"):
            _pull(world, client)
        target = _target(world, first)
        assert client.requests[-1] == first and target.exists()
        assert not world.h2.manifest.exists()  # downloaded, never checked, never sealed

        checks: list[tuple[Path, bool, bool]] = []

        def recording(path):
            path = Path(path)
            checks.append((path, path.exists(), ho.is_sealed_raw(path, world.h2)))
            return path.stat().st_size

        monkeypatch.setattr(adapter, "delivered_record_bytes", recording)
        resumed = StubClient()
        done = _pull(world, resumed)
        assert resumed.requests == list(HOLDOUT2_RAW_CHUNKS[1:])  # the chunk on disk: not re-bought
        assert checks[0] == (target, True, False)  # the one decode, on disk, BEFORE the seal
        assert len(checks) == 13  # the resumed chunk, then fetch_range's check of the other 12
        assert done[58]["action"] == (
            "SEALED as holdout 2 on resume (already downloaded, not re-bought)")
        log = world.h2.unlock_log.read_text()
        entry = log.split(f"SEALED holdout 2 raw chunk {H2_NAMES[0]}")[1].split("\n## ")[0]
        size = client.writes[first]["bytes"]
        assert f"record-byte check run on resume: {size:,} delivered record bytes" in entry
        assert ho.load_manifest(world.h2)["raw_files"][0]["bytes"] == size
        assert ho.verify_seal(world.h2)["all_ok"]

    def test_d1_an_out_of_order_chunk_on_disk_is_refused_before_its_decode(
            self, world, monkeypatch) -> None:
        _list_in_manifest(world.h1, [_target(world, HOLDOUT2_RAW_CHUNKS[0])])  # 2024-03 skipped
        april = _place(world, HOLDOUT2_RAW_CHUNKS[1], b"april")
        decoded: list[Path] = []
        monkeypatch.setattr(adapter, "delivered_record_bytes",
                            lambda path: decoded.append(Path(path)) or Path(path).stat().st_size)
        with pytest.raises(ho.SealIntegrityError, match="out of order"):
            _pull(world, StubClient())
        assert april not in decoded and april.read_bytes() == b"april"
        assert not world.h2.manifest.exists()

    @pytest.mark.parametrize("crash", ["before_the_log_pin", "before_the_removal"])
    def test_d2_a_seal_cut_off_after_its_manifest_record_is_finished_on_resume(
            self, world, monkeypatch, crash) -> None:
        first, target = HOLDOUT2_RAW_CHUNKS[0], _target(world, HOLDOUT2_RAW_CHUNKS[0])
        if crash == "before_the_log_pin":  # after the manifest record and the SEALED entry
            real, armed = ho._pin_log_and_remove, [True]

            def power_cut(*args, **kwargs):
                if armed[0]:
                    armed[0] = False
                    raise OSError("power cut before the log pin")
                return real(*args, **kwargs)

            monkeypatch.setattr(ho, "_pin_log_and_remove", power_cut)
        else:  # after the log pin, at the plaintext removal
            _crash_at_unlink(monkeypatch, target)
        client = StubClient()
        with pytest.raises(OSError, match="power cut"):
            _pull(world, client)
        assert client.requests[-1] == first and ho.is_sealed_raw(target, world.h2)
        assert ho.sha256_file(target) == client.writes[first]["sha256"]  # plaintext still there
        assert not ho.verify_seal(world.h2)["raw_files"][H2_NAMES[0]]["plaintext_absent"]

        resumed = StubClient()  # the crash hooks are spent: from here every call is the real one
        done = _pull(world, resumed)
        assert resumed.requests == list(HOLDOUT2_RAW_CHUNKS[1:])
        assert done[58]["action"] == "plaintext of an interrupted holdout-2 seal removed on resume"
        assert not target.exists() and not ho.partial_path(target).exists()
        log = world.h2.unlock_log.read_text()
        assert log.count(f"RESUMED holdout 2 raw chunk {H2_NAMES[0]}") == 1
        assert log.count("plaintext removed on resume") == 1
        record = ho.load_manifest(world.h2)["raw_files"][0]
        assert record["sha256_plaintext"] == client.writes[first]["sha256"]
        report = ho.verify_seal(world.h2)
        assert report["all_ok"] and report["unlocks_logged"] == 0

    def test_d2_complete_interrupted_seal_logs_repins_and_then_removes(
            self, world, monkeypatch) -> None:
        target, payload = _interrupted_seal(world, monkeypatch)
        before = world.h2.unlock_log.read_text()
        record = ho.complete_interrupted_seal(target, world.h2)
        assert record["sha256_plaintext"] == ho.sha256_bytes(payload)
        assert not target.exists() and not ho.partial_path(target).exists()
        log = world.h2.unlock_log.read_text()
        assert log.startswith(before)  # appended, nothing rewritten
        added = log[len(before):]
        assert added.startswith("\n## ") and added.count("\n## ") == 1
        heading = added.splitlines()[1]
        assert heading.endswith(f" RESUMED holdout 2 raw chunk {H2_NAMES[0]}")
        assert " UNLOCK " not in heading and "- plaintext removed on resume: " in added
        assert ho.load_manifest(world.h2)["unlock_log_at_seal"] == {
            "bytes": world.h2.unlock_log.stat().st_size,
            "sha256": ho.sha256_file(world.h2.unlock_log)}  # re-pinned after the new entry
        assert ho.verify_seal(world.h2)["raw_files"][H2_NAMES[0]] == {
            "sealed_ok": True, "plaintext_absent": True}
        assert ho.prior_unlocks(world.h2) == 0 and ho.prior_unlocks(world.h1) == 0

    @pytest.mark.parametrize(("breakage", "error", "match"), [
        ("tampered_blob", ho.SealIntegrityError, "does not match the manifest"),
        ("wrong_salt", ho.SealIntegrityError, "decrypted bytes do not match"),
        ("rewritten_log", ho.SealIntegrityError, "pinned prefix"),
        ("foreign_plaintext", ho.SealIntegrityError, "not the sealed plaintext"),
        ("missing_blob", FileNotFoundError, "No such file"),
        ("not_in_the_manifest", ValueError, "not a sealed holdout 2 chunk"),
    ])
    def test_d2_a_failed_proof_raises_and_removes_nothing(
            self, world, monkeypatch, breakage, error, match) -> None:
        target, payload = _interrupted_seal(world, monkeypatch)
        record = ho.load_manifest(world.h2)["raw_files"][0]
        blob = world.h2.sealed_root / record["sealed_relpath"]
        if breakage == "tampered_blob":
            data = blob.read_bytes()
            blob.write_bytes(data[:-1] + bytes([data[-1] ^ 1]))
        elif breakage == "wrong_salt":
            manifest = ho.load_manifest(world.h2)
            world.h2.manifest.write_text(json.dumps({**manifest, "salt_hex": "00" * 16}))
        elif breakage == "rewritten_log":
            log = world.h2.unlock_log
            log.write_text(log.read_text().replace("SEALED", "sealed"))
        elif breakage == "foreign_plaintext":
            target.chmod(0o644)
            payload = secrets.token_bytes(777)
            target.write_bytes(payload)
        elif breakage == "missing_blob":
            blob.unlink()
        else:
            target = _place(world, HOLDOUT2_RAW_CHUNKS[1], b"april")
            payload = b"april"
        manifest_before = world.h2.manifest.read_bytes()
        log_before = world.h2.unlock_log.read_bytes()
        with pytest.raises(error, match=match):
            ho.complete_interrupted_seal(target, world.h2)
        assert target.read_bytes() == payload  # nothing removed
        assert world.h2.manifest.read_bytes() == manifest_before  # nothing re-pinned
        assert world.h2.unlock_log.read_bytes() == log_before  # nothing logged


class TestCliFailure:
    @pytest.mark.parametrize(("failure", "name"), [("seal_integrity", "SealIntegrityError"),
                                                   ("disk_full", "OSError")])
    def test_n7_a_sealing_failure_prints_a_clear_message_and_exits_non_zero(
            self, world, monkeypatch, capsys, failure, name) -> None:
        client = StubClient()
        monkeypatch.setitem(sys.modules, "databento", SimpleNamespace(Historical=lambda _k: client))
        monkeypatch.setattr(pull_mes, "require_databento_key", lambda: "stub-key")
        monkeypatch.setattr(pull_mes, "d1f_gate", lambda: world.gate)
        if failure == "seal_integrity":
            real = ho.seal_bytes

            def corrupt(plaintext, *args):
                blob = real(plaintext, *args)
                return blob[:-1] + bytes([blob[-1] ^ 1])

            monkeypatch.setattr(ho, "seal_bytes", corrupt)
        else:
            def no_disk(*_a, **_k):
                raise OSError("disk full")

            monkeypatch.setattr(ho, "_write_manifest", no_disk)
        monkeypatch.setattr(sys, "argv", ["pull_mes", "--d1f-pull"])
        assert pull_mes.main() == 1
        err = capsys.readouterr().err
        assert f"PULL STOPPED — {name}: " in err and "fail-closed" in err
        assert "python -m data.holdout status" in err
        first = HOLDOUT2_RAW_CHUNKS[0]  # the pull stopped at the first holdout-2 chunk
        assert client.requests == [*CONFIRMATION_RAW_CHUNKS, first]
        assert ho.sha256_file(_target(world, first)) == client.writes[first]["sha256"]


class TestSealChunkRefusals:
    def test_only_the_13_holdout2_chunks_at_the_adapter_path_are_sealed(self, world) -> None:
        feb = _place(world, CONFIRMATION_RAW_CHUNKS[-1])
        with pytest.raises(ValueError, match="not one of the 13"):
            ho.seal_holdout2_chunk(feb, world.h2)
        stray = world.root / "elsewhere" / H2_NAMES[0]
        stray.parent.mkdir()
        stray.write_bytes(b"x")
        with pytest.raises(ValueError, match="not where the adapter stores"):
            ho.seal_holdout2_chunk(stray, world.h2)
        with pytest.raises(ValueError, match="holdout-2 paths"):
            ho.seal_holdout2_chunk(_place(world, HOLDOUT2_RAW_CHUNKS[0]), world.h1)
        assert feb.exists() and stray.exists() and not world.h2.manifest.exists()

    def test_out_of_order_and_already_sealed_are_refused_before_any_write(self, world) -> None:
        april = _place(world, HOLDOUT2_RAW_CHUNKS[1], b"april")
        with pytest.raises(ho.SealIntegrityError, match="out of order"):
            ho.seal_holdout2_chunk(april, world.h2)
        assert april.read_bytes() == b"april" and not world.h2.sealed_root.exists()
        assert not world.h2.manifest.exists() and not world.h2.unlock_log.exists()
        march = _place(world, HOLDOUT2_RAW_CHUNKS[0], b"march")
        ho.partial_path(march).write_bytes(b"stale in-flight copy")
        ho.seal_holdout2_chunk(march, world.h2)
        assert not march.exists() and not ho.partial_path(march).exists()
        _place(world, HOLDOUT2_RAW_CHUNKS[0], b"march")
        with pytest.raises(FileExistsError, match="sealed once only"):
            ho.seal_holdout2_chunk(march, world.h2)

    def test_removal_waits_for_the_proof_from_disk(self, world, monkeypatch) -> None:
        real, calls = ho.open_sealed, []

        def disk_copy_fails(blob, *args):  # call 1 is the in-memory proof, call 2 from disk
            calls.append(1)
            if len(calls) == 2:
                raise ho.SealIntegrityError("the disk copy does not decrypt")
            return real(blob, *args)

        monkeypatch.setattr(ho, "open_sealed", disk_copy_fails)
        march = _place(world, HOLDOUT2_RAW_CHUNKS[0], b"march")
        with pytest.raises(ho.SealIntegrityError, match="disk copy"):
            ho.seal_holdout2_chunk(march, world.h2)
        assert march.read_bytes() == b"march" and len(calls) == 2
        assert not world.h2.manifest.exists() and not world.h2.unlock_log.exists()

    def test_a_rewritten_unlock_log_blocks_the_next_seal(self, world) -> None:
        ho.seal_holdout2_chunk(_place(world, HOLDOUT2_RAW_CHUNKS[0]), world.h2)
        log = world.h2.unlock_log
        log.write_text(log.read_text().replace("SEALED", "sealed"))
        april = _place(world, HOLDOUT2_RAW_CHUNKS[1], b"april")
        with pytest.raises(ho.SealIntegrityError, match="pinned prefix"):
            ho.seal_holdout2_chunk(april, world.h2)
        assert april.read_bytes() == b"april"

    def test_not_yet_sealed_is_an_explicit_state_not_a_crash(self, world) -> None:
        report = ho.verify_seal(world.h2)
        assert report["state"] == "not_yet_sealed" and not report["all_ok"]
        assert report["chunks_sealed"] == 0 and report["raw_files"] == {}
        assert report["unlocks_logged"] == 0 and report["unsealed_plaintext_present"] == []
        assert not ho.request_touches_holdout2("2024-01-01", "2026-01-01")
        _place(world, HOLDOUT2_RAW_CHUNKS[5])  # a holdout-2 chunk bought but never sealed
        assert ho.verify_seal(world.h2)["unsealed_plaintext_present"] == [H2_NAMES[5]]

    @pytest.mark.parametrize(("last", "clean"), [("2024-02-29", True), ("2024-03-01", False)])
    def test_a_confirmation_parquet_holding_a_later_date_fails_verification(
            self, world, last, clean) -> None:
        _pull(world, StubClient())
        world.h2.research_parquet.parent.mkdir(parents=True, exist_ok=True)
        pq.write_table(pa.table({"trade_date": ["2019-05-06", last]}), world.h2.research_parquet)
        report = ho.verify_seal(world.h2)
        assert report["confirmation_has_no_holdout2_rows"] is clean
        assert report["all_ok"] is clean


L3 = r"(stage\s+)?d\.2(\s+holdout\s+2)?"  # list 1.2 L-3, verbatim


class TestCeremony:
    # Lead ruling N2: the holdout-2 stage argument must NAME "holdout 2" (1.2); a bare "d.2" or
    # "Stage D.2" is refused for holdout 2. Every accepted string still fullmatches L-3.
    @pytest.mark.parametrize(("stage", "ok"), [
        ("d.2 holdout 2", True), ("D.2 Holdout 2", True), ("stage d.2 holdout 2", True),
        ("STAGE D.2 HOLDOUT 2", True), ("d.2  holdout\t2", True), ("Stage\tD.2 holdout  2", True),
        ("d.2", False), ("D.2", False), ("Stage D.2", False), ("stage d.2", False),
        ("D.1", False), ("d.21", False), ("d.2.1", False), ("d.2 holdout 1", False),
        ("d.2 holdout 2 extra", False), ("holdout 2", False), (" d.2 holdout 2", False),
        ("d.2 holdout 2 ", False), ("d.2holdout 2", False), ("stage d.2 holdout", False),
        ("d.2 holdout 22", False), ("Stage D.2 holdout 2\n## forged UNLOCK", False),
    ])
    def test_the_holdout2_stage_must_name_holdout_2(self, world, stage, ok) -> None:
        world.h2.registration.parent.mkdir(parents=True, exist_ok=True)
        world.h2.registration.write_text(REGISTRATION)
        call = (stage, REASON, ho.ACKNOWLEDGEMENT, 0, world.h2)
        if ok:
            assert re.fullmatch(L3, stage, re.IGNORECASE)  # within the frozen L-3 regex
            assert ho._refuse_unless_ceremony(*call) == ho.sha256_file(world.h2.registration)
        else:
            with pytest.raises(ho.HoldoutLockedError, match="not Stage D.2"):
                ho._refuse_unless_ceremony(*call)

    def test_the_holdout2_pattern_accepts_only_l3_strings_that_name_holdout_2(self) -> None:
        assert ho.STAGE_PATTERNS[2] == r"(stage\s+)?d\.2\s+holdout\s+2"
        assert ho.STAGE_PATTERNS[1] == r"\s*(stage\s+)?d\.2\s*"  # holdout 1: Stage C's, unchanged
        for stage in ("d.2", "Stage D.2"):  # in L-3, but they do not name holdout 2
            assert re.fullmatch(L3, stage, re.IGNORECASE)
            assert not re.fullmatch(ho.STAGE_PATTERNS[2], stage, re.IGNORECASE)

    def test_a_bare_d2_unseals_nothing_from_holdout2_and_logs_nothing(self, world) -> None:
        _pull(world, StubClient())
        world.h2.registration.write_text(REGISTRATION)
        before, target = world.h2.unlock_log.read_text(), _target(world, HOLDOUT2_RAW_CHUNKS[0])
        for stage in ("d.2", "Stage D.2"):
            with pytest.raises(ho.HoldoutLockedError, match="not Stage D.2"):
                ho.unseal_raw_file(target, stage=stage, reason=REASON,
                                   acknowledgement=ho.ACKNOWLEDGEMENT, paths=world.h2)
        assert world.h2.unlock_log.read_text() == before and not target.exists()
        assert ho.prior_unlocks(world.h2) == 0

    def test_holdout1_keeps_its_own_stage_pattern(self, world) -> None:
        world.h1.registration.parent.mkdir(parents=True, exist_ok=True)
        world.h1.registration.write_text(REGISTRATION)
        ho._refuse_unless_ceremony(" Stage D.2 ", REASON, ho.ACKNOWLEDGEMENT, 0, world.h1)
        with pytest.raises(ho.HoldoutLockedError, match="not Stage D.2"):
            ho._refuse_unless_ceremony("d.2 holdout 2", REASON, ho.ACKNOWLEDGEMENT, 0, world.h1)

    def test_a_full_synthetic_unseal_round_trip(self, world) -> None:
        client = StubClient()
        _pull(world, client)
        world.h2.registration.write_text(REGISTRATION)
        for k, chunk in enumerate(HOLDOUT2_RAW_CHUNKS):
            restored = ho.unseal_raw_file(_target(world, chunk), stage="stage d.2 holdout 2",
                                          reason=REASON, acknowledgement=ho.ACKNOWLEDGEMENT,
                                          prior_unlocks_acknowledged=k, paths=world.h2)
            assert ho.sha256_file(restored) == client.writes[chunk]["sha256"]
            assert not restored.stat().st_mode & 0o222
        log = world.h2.unlock_log.read_text()
        assert log.count("UNLOCK holdout 2 raw file (stage d.2 holdout 2)") == 13
        assert ho.sha256_file(world.h2.registration) in log
        assert ho.prior_unlocks(world.h2) == 13 and ho.prior_unlocks(world.h1) == 0
        report = ho.verify_seal(world.h2)
        assert report["unlocks_logged"] == 13 and not report["all_ok"]
        assert not any(v["plaintext_absent"] for v in report["raw_files"].values())

    @pytest.mark.parametrize(("kwargs", "match"), [
        ({"acknowledgement": "I accept"}, "acknowledgement"),
        ({"stage": "D.1"}, "not Stage D.2"),
        ({"prior_unlocks_acknowledged": 1}, "prior unlock"),
        ({"reason": "because"}, "real reason"),
        ({"registration": ""}, "pre-registered bar"),
    ])
    def test_refusals_restore_nothing_and_log_nothing(self, world, kwargs, match) -> None:
        _pull(world, StubClient())
        world.h2.registration.write_text(kwargs.get("registration", REGISTRATION))
        before, target = world.h2.unlock_log.read_text(), _target(world, HOLDOUT2_RAW_CHUNKS[0])
        call = {"stage": "d.2 holdout 2", "reason": REASON,
                "acknowledgement": ho.ACKNOWLEDGEMENT, "prior_unlocks_acknowledged": 0} | {
                    k: v for k, v in kwargs.items() if k != "registration"}
        with pytest.raises(ho.HoldoutLockedError, match=match):
            ho.unseal_raw_file(target, paths=world.h2, **call)
        assert world.h2.unlock_log.read_text() == before and not target.exists()

    def test_unlocks_are_counted_per_holdout(self, world) -> None:
        frame = _seal_holdout1(world)
        _pull(world, StubClient())
        world.h1.registration.write_text(REGISTRATION)
        common = {"reason": REASON, "acknowledgement": ho.ACKNOWLEDGEMENT}
        ho.unseal_raw_file(_target(world, HOLDOUT2_RAW_CHUNKS[0]), stage="Stage D.2 holdout 2",
                           paths=world.h2, **common)
        assert (ho.prior_unlocks(world.h1), ho.prior_unlocks(world.h2)) == (0, 1)
        rows = ho.unlock_holdout(stage="D.2", paths=world.h1, **common)  # 0 still right for 1
        assert rows.equals(frame.iloc[2:].reset_index(drop=True))
        assert (ho.prior_unlocks(world.h1), ho.prior_unlocks(world.h2)) == (1, 1)
        with pytest.raises(ho.HoldoutLockedError, match="1 prior unlock"):
            ho.unseal_raw_file(_target(world, HOLDOUT2_RAW_CHUNKS[1]), stage="d.2 holdout 2",
                               paths=world.h2, **common)
        ho.unseal_raw_file(_target(world, HOLDOUT2_RAW_CHUNKS[1]), stage="d.2 holdout 2",
                           prior_unlocks_acknowledged=1, paths=world.h2, **common)
        assert (ho.prior_unlocks(world.h1), ho.prior_unlocks(world.h2)) == (1, 2)
        assert ho.verify_seal(world.h1)["all_ok"]  # holdout 1's log pin survived all of it

    def test_holdout1_only_entry_points_refuse_holdout2_paths(self, world) -> None:
        with pytest.raises(ValueError, match="no bars blob"):
            ho.unlock_holdout(stage="d.2", reason=REASON, acknowledgement=ho.ACKNOWLEDGEMENT,
                              paths=world.h2)
        with pytest.raises(ValueError, match="holdout 1's migration"):
            ho.seal_holdout(world.root / "x.parquet", [], world.h2, remove_plaintext=False)
        assert not world.h2.unlock_log.exists()


class TestHoldout1Unchanged:
    def test_the_two_path_sets(self) -> None:
        assert ho.HoldoutPaths(
            sealed_root=REPO_ROOT / "data" / "sealed" / "MES_holdout_v1",
            manifest=REPO_ROOT / "docs" / "HOLDOUT_MANIFEST.json",
            unlock_log=REPO_ROOT / "docs" / "HOLDOUT_UNLOCK_LOG.md",
            registration=REPO_ROOT / "REGISTRATION.md",
            research_parquet=PROCESSED_ROOT / "MES" / RESEARCH_PARQUET_NAME) == ho.DEFAULT_PATHS
        assert ho.DEFAULT_PATHS.holdout_id == 1
        h2 = ho.HOLDOUT2_PATHS
        assert h2.sealed_root == REPO_ROOT / "data" / "sealed" / "MES_holdout_v2"
        assert h2.manifest == REPO_ROOT / "docs" / "HOLDOUT2_MANIFEST.json"
        assert (h2.unlock_log, h2.registration) == (ho.DEFAULT_PATHS.unlock_log,
                                                    ho.DEFAULT_PATHS.registration)
        assert (h2.holdout_id, h2.vendor_root) == (2, VENDOR_ROOT)
        assert h2.research_parquet == CONFIRMATION_SERIES_PATH

    def test_holdout1_status_is_unaffected_by_an_unsealed_holdout2(self, world) -> None:
        _seal_holdout1(world)
        report = ho.status_report()
        assert report["all_ok"] and report["unlocks_logged"] == 0
        assert report["holdout_2"]["state"] == "not_yet_sealed"
        assert {k: v for k, v in report.items() if k != "holdout_2"} == ho.verify_seal()

    def test_holdout1_verifies_after_holdout2_is_sealed_into_the_same_log(self, world) -> None:
        _seal_holdout1(world)
        _pull(world, StubClient())
        report = ho.verify_seal(world.h1)
        assert report["all_ok"] and report["unlock_log_ok"] and report["unlocks_logged"] == 0


class TestRolls:
    def _client(self, extra: list[dict] | None = None) -> SimpleNamespace:
        calls: list[dict] = []
        intervals = [{"d0": "2019-04-01", "d1": "2019-06-14", "s": "7849"},
                     {"d0": "2019-06-14", "d1": "2024-03-01", "s": "9001"}, *(extra or [])]

        def resolve(**kw):
            calls.append(kw)
            if kw["stype_out"] == "instrument_id":
                return {"result": {kw["symbols"][0]: intervals}}
            return {"result": {"7849": [{"d0": "2019-04-01", "d1": "2019-06-14", "s": "MESM9"}],
                               "9001": [{"d0": "2019-06-14", "d1": "2024-03-01", "s": "MESU9"}]}}

        return SimpleNamespace(symbology=SimpleNamespace(resolve=resolve), calls=calls)

    def test_rolls_are_resolved_over_2019_04_01_to_2024_03_01_only(self, world) -> None:
        client, log = self._client(), []
        out = pull_mes.resolve_d1f_rolls(client, root=world.vendor, log=log.append)
        assert {(c["start_date"], c["end_date"]) for c in client.calls} == {
            ("2019-04-01", "2024-03-01")}
        assert [r.date for r in out["MES.v.0"]] == ["2019-06-14"]
        stored = world.vendor / "rolls" / "MES_v_0_2019-04-01_2024-03-01.jsonl"
        assert [r.to_raw_symbol for r in adapter.read_rolls(stored)] == ["MESU9"]
        text = stored.read_text()
        pull_mes.resolve_d1f_rolls(client, root=world.vendor, log=log.append)
        assert stored.read_text() == text and any("REFUSED" in line for line in log)

    def test_a_boundary_past_the_confirmation_window_is_refused(self, world) -> None:
        client = self._client([{"d0": "2024-03-15", "d1": "2024-06-01", "s": "9100"}])
        with pytest.raises(ValueError, match="outside 2019-04-01..2024-03-01"):
            pull_mes.resolve_d1f_rolls(client, root=world.vendor, log=lambda _m: None)
        assert not (world.vendor / "rolls").exists()


class TestVendorAudit:
    """Pins where the installed vendor client writes a download (read as text, not imported)."""

    def test_databento_writes_get_range_to_path_only_and_keeps_no_cache(self) -> None:
        try:
            dist = importlib.metadata.distribution("databento")
        except importlib.metadata.PackageNotFoundError:
            pytest.skip("databento is not installed")
        assert dist.version in ("0.82.0",), (
            f"databento {dist.version} is not the audited 0.82.0: re-audit where "
            "timeseries.get_range writes before trusting seal-on-arrival")
        package = Path(dist.locate_file("databento"))
        assert 'writer = open(path, "x+b")' in (package / "common" / "http.py").read_text()
        sources = "\n".join(p.read_text() for p in package.rglob("*.py"))
        for marker in ("tempfile", "mkstemp", "NamedTemporaryFile", "gettempdir", "diskcache"):
            assert marker not in sources, marker


class TestRealStores:
    """Read-only checks of the repo's own holdout-2 state. Nothing is written or decrypted."""

    def test_real_holdout2_is_not_yet_sealed_or_verifies(self) -> None:
        report = ho.verify_seal(ho.HOLDOUT2_PATHS)
        if not ho.HOLDOUT2_PATHS.manifest.exists():
            assert report["state"] == "not_yet_sealed" and report["chunks_sealed"] == 0
            assert report["unsealed_plaintext_present"] == []
            assert not ho.HOLDOUT2_PATHS.sealed_root.exists()
        else:
            assert report["all_ok"], report
