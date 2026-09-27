"""Stage E.2b Task 6: the harness-freeze preflight refuses any change to the frozen harness."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from data.config import REPO_ROOT
from screening import harness_freeze as hf


def _tiny_root(tmp_path: Path) -> tuple[Path, str]:
    """A synthetic repo: two harness files and a manifest listing both; returns (root, sha256)."""
    (tmp_path / "screening").mkdir()
    (tmp_path / "screening" / "a.py").write_bytes(b"X = 1\n")
    (tmp_path / "reports").mkdir()
    (tmp_path / "reports" / "table.json").write_bytes(b'{"k": 2}\n')
    files = {rel: {"sha256": hf.sha256_file(tmp_path / rel), "bytes": (tmp_path / rel).stat().st_size}
             for rel in ("screening/a.py", "reports/table.json")}
    raw = (json.dumps({"stage": "test", "files": files}) + "\n").encode("utf-8")
    (tmp_path / hf.MANIFEST_PATH).write_bytes(raw)
    return tmp_path, hf.sha256_bytes(raw)


def test_preflight_passes_on_the_frozen_tree_and_returns_the_manifest_sha(tmp_path: Path) -> None:
    root, digest = _tiny_root(tmp_path)
    assert hf.preflight(digest, root) == digest


def test_preflight_refuses_a_one_byte_change_to_a_listed_file(tmp_path: Path) -> None:
    root, digest = _tiny_root(tmp_path)
    (root / "screening" / "a.py").write_bytes(b"X = 2\n")  # same length, one byte differs
    with pytest.raises(hf.HarnessFreezeError, match="screening/a.py: sha256"):
        hf.preflight(digest, root)


def test_preflight_refuses_a_one_byte_change_to_a_frozen_table(tmp_path: Path) -> None:
    root, digest = _tiny_root(tmp_path)
    (root / "reports" / "table.json").write_bytes(b'{"k": 3}\n')
    with pytest.raises(hf.HarnessFreezeError, match="reports/table.json"):
        hf.preflight(digest, root)


def test_preflight_refuses_a_missing_listed_file(tmp_path: Path) -> None:
    root, digest = _tiny_root(tmp_path)
    (root / "reports" / "table.json").unlink()
    with pytest.raises(hf.HarnessFreezeError, match="reports/table.json: missing"):
        hf.preflight(digest, root)


def test_preflight_refuses_an_unlisted_module_in_a_harness_directory(tmp_path: Path) -> None:
    root, digest = _tiny_root(tmp_path)
    (root / "screening" / "sneaky.py").write_bytes(b"Y = 1\n")
    with pytest.raises(hf.HarnessFreezeError, match="screening/sneaky.py: not listed"):
        hf.preflight(digest, root)


def test_preflight_refuses_a_rebuilt_manifest_without_the_expected_sha(tmp_path: Path) -> None:
    root, digest = _tiny_root(tmp_path)
    (root / "screening" / "a.py").write_bytes(b"X = 2\n")
    manifest = json.loads((root / hf.MANIFEST_PATH).read_text(encoding="utf-8"))
    manifest["files"]["screening/a.py"]["sha256"] = hf.sha256_file(root / "screening" / "a.py")
    (root / hf.MANIFEST_PATH).write_text(json.dumps(manifest) + "\n", encoding="utf-8")
    with pytest.raises(hf.HarnessFreezeError, match="is not the expected"):
        hf.preflight(digest, root)  # the session prompt's hash, not the rebuilt one


def test_preflight_refuses_a_missing_manifest_and_a_malformed_expected_hash(tmp_path: Path) -> None:
    with pytest.raises(hf.HarnessFreezeError, match="is missing"):
        hf.preflight("0" * 64, tmp_path)
    (tmp_path / "r").mkdir()
    root, _ = _tiny_root(tmp_path / "r")
    with pytest.raises(hf.HarnessFreezeError, match="is not a sha256"):
        hf.preflight("not-a-hash", root)


def test_the_builder_excludes_data_and_bytecode_and_includes_the_import_closure() -> None:
    cats = hf.manifest_categories(REPO_ROOT)
    assert hf.MANIFEST_PATH not in cats
    assert not any(hf._in_data_subdir(rel) or rel.endswith(".pyc") for rel in cats)
    assert cats["strategy/interface.py"] == "import_closure"
    assert cats["screening/harness_freeze.py"] == "harness_code"
    assert cats["reports/stage_e2a_epsilon.json"] == "frozen_input"
    assert cats["docs/STAGE_E_ML_DESIGN.md"] == "earlier_freeze"
    assert "docs/HOLDOUT_UNLOCK_LOG.md" not in cats and "ledger/databento_spend.jsonl" not in cats


def test_the_real_tree_matches_the_committed_manifest_when_it_exists() -> None:
    if not (REPO_ROOT / hf.MANIFEST_PATH).is_file():
        pytest.skip("the harness manifest is not built yet")
    problems, _ = hf.check(REPO_ROOT)
    assert problems == []


def test_data_subdirectories_are_neither_listed_nor_scanned(tmp_path: Path) -> None:
    root, digest = _tiny_root(tmp_path)
    (root / "data" / "vendor" / "pages").mkdir(parents=True)
    (root / "data" / "vendor" / "pages" / "fetch.py").write_bytes(b"Z = 1\n")
    assert hf.preflight(digest, root) == digest
    (root / "data" / "loader.py").write_bytes(b"W = 1\n")  # data/ code outside them is scanned
    with pytest.raises(hf.HarnessFreezeError, match="data/loader.py: not listed"):
        hf.preflight(digest, root)


# ---------------------------------------------------------------- review F-1 and F-2 (Task 8)
def _compile_to(src_text: str, pyc: Path, source_path: Path, mode: str) -> None:
    import py_compile

    stand_in = pyc.parent / "_stand_in.py"
    stand_in.write_text(src_text, encoding="utf-8")
    py_compile.compile(str(stand_in), cfile=str(pyc), dfile=str(source_path), doraise=True,
                       invalidation_mode=py_compile.PycInvalidationMode[mode])
    stand_in.unlink()


def _pyc_path(source: Path) -> Path:
    import importlib.util

    return Path(importlib.util.cache_from_source(str(source)))


def test_member_code_outside_the_cluster_packages_is_refused(tmp_path: Path) -> None:
    root, digest = _tiny_root(tmp_path)
    (root / "strategy" / "members" / "k1").mkdir(parents=True)
    (root / "strategy" / "members" / "k1" / "cp2.py").write_bytes(b"A = 1\n")  # cluster freeze's job
    assert hf.preflight(digest, root) == digest
    (root / "strategy" / "members" / "__init__.py").write_bytes(b"import screening\n")
    with pytest.raises(hf.HarnessFreezeError, match="strategy/members/__init__.py: member code"):
        hf.preflight(digest, root)


def test_an_unchecked_hash_pyc_beside_an_unchanged_source_is_refused(tmp_path: Path) -> None:
    root, digest = _tiny_root(tmp_path)
    source = root / "screening" / "a.py"
    pyc = _pyc_path(source)
    pyc.parent.mkdir()
    _compile_to("X = 9\n", pyc, source, "UNCHECKED_HASH")  # the review's E3 exploit
    with pytest.raises(hf.HarnessFreezeError, match="unchecked hash-based bytecode"):
        hf.preflight(digest, root)


def test_a_timestamp_pyc_forged_to_match_its_source_is_refused(tmp_path: Path) -> None:
    import struct

    root, digest = _tiny_root(tmp_path)
    source = root / "screening" / "a.py"
    pyc = _pyc_path(source)
    pyc.parent.mkdir()
    _compile_to("X = 9\n", pyc, source, "TIMESTAMP")  # same length as the real "X = 1\n"
    data = bytearray(pyc.read_bytes())
    stat = source.stat()
    data[8:16] = struct.pack("<II", int(stat.st_mtime) & 0xFFFFFFFF, stat.st_size & 0xFFFFFFFF)
    pyc.write_bytes(bytes(data))  # Python would now trust it without reading the source
    with pytest.raises(hf.HarnessFreezeError, match="bytecode differs from its source"):
        hf.preflight(digest, root)


def test_honest_and_stale_bytecode_pass(tmp_path: Path) -> None:
    root, digest = _tiny_root(tmp_path)
    source = root / "screening" / "a.py"
    pyc = _pyc_path(source)
    pyc.parent.mkdir()
    _compile_to(source.read_text(encoding="utf-8"), pyc, source, "CHECKED_HASH")
    assert hf.preflight(digest, root) == digest
    import os

    _compile_to("X = 9\n", pyc, source, "TIMESTAMP")
    os.utime(source, (1_000_000, 1_000_000))  # header mtime now differs: Python recompiles
    assert hf.preflight(digest, root) == digest


@pytest.mark.parametrize("name", ["a.cpython-312-x86_64-linux-gnu.so", "a.pyd", "a.pyc"])
def test_a_binary_module_or_loose_pyc_in_a_harness_directory_is_refused(tmp_path: Path,
                                                                        name: str) -> None:
    root, digest = _tiny_root(tmp_path)
    (root / "screening" / name).write_bytes(b"\x7fELF")
    with pytest.raises(hf.HarnessFreezeError, match="unlisted binary module or loose bytecode"):
        hf.preflight(digest, root)
