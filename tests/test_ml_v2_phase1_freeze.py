"""Stage E.12 Task 1b: the v2 freeze check (ml_route_v2/phase1/freeze.py) and the CLI's two gates
(harness preflight, then the freeze) that run before anything is read or written."""

from __future__ import annotations

import hashlib
import json

import pytest

from ml_route_v2.phase1 import cli
from ml_route_v2.phase1.freeze import FreezeError, verify_v2_freeze
from tests.test_ml_v2_phase1_support import write_freeze

FILES = {"ml_route_v2/a.py": b"A = 1\n", "docs/design.md": b"# FROZEN\n"}


def test_good_manifest_verifies(tmp_path) -> None:
    path, sha = write_freeze(tmp_path, FILES)
    doc = verify_v2_freeze(path, sha, root=tmp_path)
    assert doc["schema"] == "ml_v2_freeze/1" and len(doc["files"]) == 2


def test_wrong_sha_is_refused(tmp_path) -> None:
    path, sha = write_freeze(tmp_path, FILES)
    with pytest.raises(FreezeError, match="not the expected"):
        verify_v2_freeze(path, "0" * 64, root=tmp_path)
    with pytest.raises(FreezeError, match="not a sha256"):
        verify_v2_freeze(path, sha[:63], root=tmp_path)


def test_tampered_or_missing_file_is_refused(tmp_path) -> None:
    path, sha = write_freeze(tmp_path, FILES)
    (tmp_path / "ml_route_v2/a.py").write_bytes(b"A = 2\n")
    with pytest.raises(FreezeError, match="a.py: sha256 differs"):
        verify_v2_freeze(path, sha, root=tmp_path)
    (tmp_path / "docs/design.md").unlink()
    with pytest.raises(FreezeError, match="design.md: missing"):
        verify_v2_freeze(path, sha, root=tmp_path)


def _manifest(tmp_path, doc) -> tuple:
    raw = json.dumps(doc).encode()
    path = tmp_path / "m.json"
    path.write_bytes(raw)
    return path, hashlib.sha256(raw).hexdigest()


@pytest.mark.parametrize("doc, message", [
    ({"schema": "other", "files": []}, "schema"),
    ({"schema": "ml_v2_freeze/1", "files": []}, "no files"),
    ({"schema": "ml_v2_freeze/1",
      "files": [{"path": "/etc/passwd", "sha256": "0" * 64, "bytes": 1}]}, "repository-relative"),
    ({"schema": "ml_v2_freeze/1",
      "files": [{"path": "../x", "sha256": "0" * 64, "bytes": 1}]}, "repository-relative"),
    ({"schema": "ml_v2_freeze/1", "files": [{"path": "x"}]}, "malformed"),
    # review F-8: a superset of two keys without "bytes" is malformed, not a KeyError
    ({"schema": "ml_v2_freeze/1",
      "files": [{"path": "x", "sha256": "0" * 64, "foo": 1}]}, "malformed"),
])
def test_malformed_manifest_is_refused(tmp_path, doc, message) -> None:
    path, sha = _manifest(tmp_path, doc)
    with pytest.raises(FreezeError, match=message):
        verify_v2_freeze(path, sha, root=tmp_path)


def _canonical(monkeypatch, tmp_path) -> None:
    """The CLI's canonical paths pointed at tmp_path (review F-2: no path flag exists)."""
    monkeypatch.setattr(cli, "FREEZE_ROOT", tmp_path / "frozen")
    monkeypatch.setattr(cli, "REPORTS_DIR", tmp_path / "reports")
    monkeypatch.setattr(cli, "LEDGER_PATH", tmp_path / "ledger.jsonl")
    monkeypatch.setattr(cli, "STATE_DIR", tmp_path / "state")


def test_cli_refuses_before_reading_anything_when_a_gate_fails(tmp_path, monkeypatch) -> None:
    from screening import harness_freeze

    _path, sha = write_freeze(tmp_path / "frozen", FILES)
    _canonical(monkeypatch, tmp_path)

    def refuse(_sha: str) -> str:
        raise harness_freeze.HarnessFreezeError("preflight refused")

    monkeypatch.setattr(harness_freeze, "preflight", refuse)
    with pytest.raises(harness_freeze.HarnessFreezeError):
        cli.main(["build", "--harness-sha256", "a" * 64, "--freeze-sha256", sha])
    monkeypatch.setattr(harness_freeze, "preflight", lambda s: s)
    with pytest.raises(FreezeError):
        cli.main(["build", "--harness-sha256", "a" * 64, "--freeze-sha256", "f" * 64])
    assert not (tmp_path / "state").exists() and not (tmp_path / "reports").exists()


def test_cli_verifies_the_canonical_manifest_only(tmp_path, monkeypatch) -> None:
    from screening import harness_freeze

    _canonical(monkeypatch, tmp_path)
    monkeypatch.setattr(harness_freeze, "preflight", lambda s: s)
    _path, sha = write_freeze(tmp_path / "elsewhere", FILES)  # a valid manifest, not canonical
    with pytest.raises(FreezeError, match="does not exist"):
        cli.main(["register", "--harness-sha256", "a" * 64, "--freeze-sha256", sha])


def test_cli_requires_both_shas_and_names_no_path() -> None:
    with pytest.raises(SystemExit):
        cli.main(["build"])
    assert cli.STATE_DIR.name == "propexp_e12_phase1" and ".cache" in cli.STATE_DIR.parts
    assert cli.LEDGER_PATH.parts[-2:] == ("ledger", "ml_v2_config_ledger.jsonl")
    assert cli.REPORTS_DIR.name == "reports" and cli.REPORTS_DIR.parent == cli.FREEZE_ROOT
