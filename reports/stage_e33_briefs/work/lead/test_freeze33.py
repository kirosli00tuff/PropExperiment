"""Tests of freeze33.py (E.33 B7 pipeline freeze list).

  uv run python -m pytest -q reports/stage_e33_briefs/work/lead/test_freeze33.py

Unit tests run on temporary trees; the integration tests measure the real pipeline (a child interpreter imports
pipeline/*.py and runs the four read-only probes, about 10 s each build) and read no market data.
"""
from __future__ import annotations

import ast
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import freeze33 as fz  # noqa: E402

ENV = {"python": "3.12.13", "numpy": "2.5.3", "pandas": "3.0.5", "pyarrow": "25.0.1", "scikit-learn": "1.9.1",
       "lightgbm": "4.7.0", "scipy": "1.18.1"}


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _tree(tmp: Path, files: dict[str, bytes]) -> dict[str, str]:
    for name, data in files.items():
        (tmp / name).parent.mkdir(parents=True, exist_ok=True)
        (tmp / name).write_bytes(data)
    return {name: _sha(data) for name, data in files.items()}


# ----------------------------------------------------------------------------------------------- format
def test_render_parse_round_trip_keeps_sections_and_sorts_paths():
    sections = {"pipeline": {"b/z.py": "1" * 64, "a/y.csv": "2" * 64},
                "verification evidence": {"t/test_x.py": "3" * 64}, "freeze tools": {}}
    text = fz.render(ENV, sections)
    env, parsed = fz.parse(text)
    assert env == ENV
    assert parsed["pipeline"] == sections["pipeline"]
    assert parsed["verification evidence"] == sections["verification evidence"]
    assert parsed["freeze tools"] == {}
    body = [ln for ln in text.splitlines() if not ln.startswith("#")]
    assert body == [f"{'2' * 64}  a/y.csv", f"{'1' * 64}  b/z.py", f"{'3' * 64}  t/test_x.py"]


def test_parse_rejects_malformed_and_duplicate_lines():
    with pytest.raises(ValueError, match="not a freeze-list line"):
        fz.parse("# section pipeline: x\nabc  path\n")
    with pytest.raises(ValueError, match="duplicate"):
        fz.parse(f"# section pipeline: x\n{'a' * 64}  p\n{'b' * 64}  p\n")
    with pytest.raises(ValueError, match="not a freeze-list line"):
        fz.parse(f"{'a' * 64}  p\n")  # a hash line before any section


def test_render_refuses_a_path_sha256sum_cannot_carry():
    with pytest.raises(ValueError, match="not representable"):
        fz.render(ENV, {"pipeline": {"bad\nname": "0" * 64}})


@pytest.mark.skipif(shutil.which("sha256sum") is None, reason="sha256sum not installed")
def test_rendered_file_checks_with_sha256sum(tmp_path):
    digests = _tree(tmp_path, {"a.py": b"x = 1\n", "d/b.json": b"{}\n"})
    (tmp_path / "list.sha256").write_text(fz.render(ENV, {"pipeline": digests}))
    run = subprocess.run(["sha256sum", "-c", "list.sha256"], cwd=tmp_path, capture_output=True, text=True)
    assert run.returncode == 0, run.stdout + run.stderr


# ----------------------------------------------------------------------------------------------- verify
def test_verify_lines_reports_changed_missing_and_environment(tmp_path):
    digests = _tree(tmp_path, {"a.py": b"a\n", "b.csv": b"b\n", "t/test_a.py": b"t\n"})
    text = fz.render(ENV, {"pipeline": {"a.py": digests["a.py"], "b.csv": digests["b.csv"]},
                           "verification evidence": {"t/test_a.py": digests["t/test_a.py"]}})
    assert fz.verify_lines(text, tmp_path, ENV) == []

    (tmp_path / "a.py").write_bytes(b"a = 2\n")
    (tmp_path / "t/test_a.py").unlink()
    diffs = fz.verify_lines(text, tmp_path, dict(ENV, numpy="9.9.9"))

    assert "CHANGED pipeline: a.py" in diffs
    assert "MISSING verification evidence: t/test_a.py" in diffs
    assert "ENV numpy: frozen 2.5.3, now 9.9.9" in diffs
    assert not any("b.csv" in d for d in diffs)


# ----------------------------------------------------------------------------------------------- check-proofs
def _proof_repo(tmp: Path) -> tuple[Path, Path, dict[str, str]]:
    pipe, p7 = tmp / "pipe", tmp / "p7"
    files = {"pipe/search33.py": b"import run_search33\nimport helper33\nimport numpy\n",
             "pipe/run_search33.py": b"import search33\n", "pipe/helper33.py": b"X = 1\n",
             "pipe/select33.py": b"Y = 2\n", "p7/p7_final.py": b"Z = 3\n", "uv.lock": b"lock\n"}
    return pipe, p7, _tree(tmp, files)


def _engine_sha(digests: dict[str, str], names: list[str]) -> str:
    """search33._pipeline_sha: name + NUL + raw digest over the sorted closure."""
    h = hashlib.sha256()
    for n in sorted(names):
        h.update(f"{n}.py".encode() + b"\0" + bytes.fromhex(digests[f"pipe/{n}.py"]))
    return h.hexdigest()


def test_proof_lines_pass_when_manifest_and_list_agree(tmp_path):
    pipe, p7, d = _proof_repo(tmp_path)
    text = fz.render(ENV, {"pipeline": d})
    manifest = {"code_sha256": {"search33.py": d["pipe/search33.py"], "select33.py": d["pipe/select33.py"],
                                "p7_final.py": d["p7/p7_final.py"]},
                "versions": {"python": "3.12.13", "numpy": "2.5.3", "pandas": "3.0.5", "pyarrow": "25.0.1",
                             "sklearn": "1.9.1", "lightgbm": "4.7.0", "scipy": "1.18.1", "uv_lock_sha256": d["uv.lock"]},
                "engine_pipeline_sha": _engine_sha(d, ["search33", "run_search33", "helper33"])}

    lines, fails = fz.proof_lines(text, manifest, tmp_path, pipe, p7)

    assert fails == [], lines
    assert any("p7_final.py -> p7/p7_final.py" in ln for ln in lines)


def test_proof_lines_report_each_kind_of_difference(tmp_path):
    pipe, p7, d = _proof_repo(tmp_path)
    text = fz.render(dict(ENV, lightgbm="4.6.0"), {"pipeline": d})
    manifest = {"code_sha256": {"search33.py": "0" * 64, "gone33.py": "1" * 64},
                "versions": {"python": "3.12.13", "numpy": "2.5.3", "pandas": "3.0.5", "pyarrow": "25.0.1",
                             "sklearn": "1.9.1", "lightgbm": "4.7.0", "scipy": "1.18.1", "uv_lock_sha256": "2" * 64},
                "engine_pipeline_sha": "3" * 64}

    _lines, fails = fz.proof_lines(text, manifest, tmp_path, pipe, p7)

    assert "manifest file search33.py: pipe/search33.py" in fails
    assert "manifest file gone33.py: missing" in fails
    assert "uv.lock" in fails and "env lightgbm" in fails and "engine_pipeline_sha" in fails


def test_unpinned_evidence_accepts_a_pinned_sha_or_an_old_clean_file_only():
    from datetime import datetime
    start = datetime(2026, 10, 28, 2, 36, tzinfo=fz.PT)
    before, after = datetime(2026, 10, 1, tzinfo=fz.PT), datetime(2026, 10, 28, 9, 0, tzinfo=fz.PT)
    pinned = {"pipe/guard33.py": f'X_SHA256 = "{"a" * 64}"'}
    assert fz.unpinned_evidence("a" * 64, after, start, "untracked", pinned)[0]
    assert fz.unpinned_evidence("b" * 64, before, start, "same as HEAD", pinned)[0]
    assert not fz.unpinned_evidence("b" * 64, after, start, "same as HEAD", pinned)[0]
    assert not fz.unpinned_evidence("b" * 64, before, start, "differs from HEAD", pinned)[0]
    assert not fz.unpinned_evidence("b" * 64, before, start, "untracked", pinned)[0]


# ----------------------------------------------------------------------------------------------- AST helpers
def test_static_import_targets_include_function_level_and_from_imports():
    tree = ast.parse("import a.b\nfrom c import d, e\ndef f():\n    import g\n    from .h import i\n")
    got = {name for name, _line in fz.static_import_targets(tree, "pkg")}
    assert {"a.b", "c", "c.d", "c.e", "g", "pkg.h", "pkg.h.i"} <= got


def test_dynamic_import_resolves_fstrings_from_literal_call_sites_only():
    lib = ast.parse("import importlib\ndef load(group):\n    name = f'data.calendars.{group}'\n"
                    "    return importlib.import_module(name)\n")
    caller = ast.parse("from lib import load\ndef grains():\n    return load('grains')\n")
    targets, unresolved, patterns = fz.dynamic_import_targets({"lib.py": lib, "caller.py": caller})
    assert [t for t, _ in targets] == ["data.calendars.grains"] and unresolved == [] and patterns == []

    other = ast.parse("def any_group(g):\n    return load(g)\n")
    targets, unresolved, patterns = fz.dynamic_import_targets({"lib.py": lib, "caller.py": caller,
                                                               "other.py": other})
    assert targets == [] and unresolved == []  # a non-literal call site: every module of the package
    assert [p for p, _ in patterns] == ["data.calendars.*"]

    opaque = ast.parse("import importlib\ndef f(x):\n    return importlib.import_module(x + 'y')\n")
    assert len(fz.dynamic_import_targets({"o.py": opaque})[1]) == 1  # neither literal nor pattern: reported


def test_safe_path_expr_allows_path_arithmetic_and_refuses_other_calls():
    ok = [ast.parse(s, mode="eval").body for s in ("str(P7_DIR)", "Path(__file__).resolve().parents[1] / 'x'")]
    bad = [ast.parse(s, mode="eval").body for s in ("os.system('x')", "open('f').read()", "str(f())")]
    assert all(fz.safe_path_expr(e) for e in ok)
    assert not any(fz.safe_path_expr(e) for e in bad)


def test_data_literals_skip_docstrings_and_turn_fstrings_into_patterns():
    tree = ast.parse('"""doc mentions x.json"""\nA = "cfg/a.json"\ndef f(d):\n    return f"{d}.parquet"\n')
    assert fz.data_literals(tree) == [(2, "cfg/a.json"), (4, "*.parquet")]


def test_top_level_names_skip_function_bodies():
    tree = ast.parse("A = 1\nif True:\n    B: int = 2\nfor _p in ():\n    pass\ndef f():\n    C = 3\n")
    assert fz.top_level_names(tree) == {"A", "B"}


def test_in_repo_excludes_the_environment_and_never_covers_sealed_and_credentials():
    repo = fz.REPO
    assert fz.in_repo(repo / "data" / "session.py")
    assert not fz.in_repo(repo / ".venv" / "lib" / "python3.12" / "site-packages" / "numpy" / "__init__.py")
    assert not fz.in_repo("/usr/lib/python3/x.py")
    assert fz.never("data/sealed/SOY_test_v1/x.sealed") and fz.never(".env") and fz.never("sub/.env")
    assert not fz.never("data/calendars/grains.py")


# ----------------------------------------------------------------------------------------------- assembly rules
def _measurement(**over) -> dict:
    m = {"loaded": {}, "opens": [], "constants": [], "literals": [], "sys_path_added": [], "unresolved_imports": [],
         "unresolved_dynamic": [], "libraries": [], "errors": [], "harness_unfollowed": [], "harness_dynamic": []}
    m.update(over)
    return m


def test_assemble_constant_rules_owned_harness_state_refused_never():
    owned_file = fz.rel(fz.PIPE / "cal33.py")
    target = str(fz.REPO / "reports" / "stage_e28_briefs" / "A0_contract_stats.md")
    registry = str(fz.REPO / "ledger" / "trial_registrations.jsonl")
    m = _measurement(constants=[
        {"owner": "cal33.SOME_FILE", "file": owned_file, "path": target, "kind": "file", "refused": None},
        {"owner": "data.config.ACCESS_DOC_PATH", "file": "data/config.py", "path": str(fz.REPO / "docs/ACCESS.md"),
         "kind": "file", "refused": None},
        {"owner": "data.research_bars.X", "file": "data/research_bars.py", "path": str(fz.REPO / "pyproject.toml"),
         "kind": "file", "refused": "REFUSED (P1.2 soy test window): test"},
        {"owner": "screening.trial_registry.REGISTRY_PATH", "file": "screening/trial_registry.py", "path": registry,
         "kind": "file", "refused": None},
        {"owner": "data.config.ENV_FILE", "file": "data/config.py", "path": str(fz.REPO / ".env"), "kind": "file",
         "refused": None}])

    sections, rows, problems, _warnings = fz.assemble(m)

    assert any(p.startswith("unclassified path constant cal33.SOME_FILE") for p in problems)
    assert "reports/stage_e28_briefs/A0_contract_stats.md" not in sections["pipeline"]
    assert "docs/ACCESS.md" in sections["pipeline"]                       # harness constant: hashed (lead, item 2)
    assert any(r[0] == "guard-refused" and r[1] == "pyproject.toml" for r in rows)
    assert any(r[0] == "state" and r[1] == "ledger/trial_registrations.jsonl" for r in rows)
    assert "ledger/trial_registrations.jsonl" not in sections["pipeline"]
    assert any(r[0] == "never" and r[1] == ".env" for r in rows) and ".env" not in sections["pipeline"]


def test_assemble_hashes_probe_reads_lists_writes_and_refuses_never_paths():
    read = str(fz.REPO / "reports" / "stage_e31_briefs" / "research" / "usda_releases.csv")
    written = str(fz.REPO / "reports" / "stage_e33_briefs" / "work" / "B5_proofs.md")
    m = _measurement(opens=[["probe p", read, "r"], ["probe p", written, "w"],
                            ["probe p", str(fz.REPO / ".env"), "r"]])

    sections, rows, problems, _warnings = fz.assemble(m)

    assert sections["pipeline"]["reports/stage_e31_briefs/research/usda_releases.csv"] == fz.sha256_file(Path(read))
    assert any(r[0] == "written" and r[1].endswith("B5_proofs.md") for r in rows)
    assert any(".env was opened" in p for p in problems)
    assert ".env" not in sections["pipeline"]


# ----------------------------------------------------------------------------------------------- derived inputs
def test_inputs_manifest_round_trip_verify_and_resume(tmp_path):
    a, b = tmp_path / "a.npy", tmp_path / "b.DONE"
    a.write_bytes(b"a" * 1000)
    b.write_bytes(b"{}")
    hashed = fz.hash_files([str(a), str(b)], jobs=2)
    text = fz.render_inputs(hashed)
    man = tmp_path / "inputs.sha256"
    man.write_text(text)

    assert fz.is_inputs_manifest(man) and "# files 2, bytes 1002" in text
    assert fz.parse(text)[1]["derived inputs"] == {str(a): _sha(b"a" * 1000), str(b): _sha(b"{}")}
    assert fz.verify_inputs(text, jobs=2) == []
    b.write_bytes(b"{1}")
    a.unlink()
    assert fz.verify_inputs(text, jobs=1) == [f"MISSING input: {a}", f"CHANGED input: {b}"]


def test_hash_files_resumes_from_its_cache_and_caps_the_processes(tmp_path, monkeypatch):
    a, b = tmp_path / "a", tmp_path / "b"
    a.write_bytes(b"one")
    b.write_bytes(b"two")
    st = a.stat()
    cache = tmp_path / "cache.tsv"
    cache.write_text(f"{st.st_size}\t{st.st_mtime_ns}\t{'f' * 64}\t{a}\n")  # a finished in an earlier run
    seen = {}

    class Pool:
        def __init__(self, max_workers, initializer):
            seen["workers"] = max_workers

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def map(self, fn, items, chunksize):
            return map(fn, items)

    import concurrent.futures
    monkeypatch.setattr(concurrent.futures, "ProcessPoolExecutor", Pool)
    hashed = fz.hash_files([str(a), str(b)], jobs=8, cache=cache)

    assert hashed[str(a)] == (3, "f" * 64)          # taken from the cache, not re-read
    assert hashed[str(b)] == (3, _sha(b"two"))
    assert seen["workers"] == fz.MAX_HASH_JOBS == 2  # --jobs 8 is capped
    assert cache.read_text().count("\n") == 2       # b appended for the next resume


def test_derived_problems_stop_on_missing_or_refused_inputs():
    assert fz.derived_problems([]) == ["no derived inputs enumerated"]
    probs = fz.derived_problems([{"path": "/x", "exists": False, "refused": None},
                                 {"path": "/y", "exists": True, "refused": "REFUSED (P1.2 ...)"}])
    assert probs == ["derived input missing: /x", "derived input refused by guard33: /y: REFUSED (P1.2 ...)"]


# ----------------------------------------------------------------------------------------------- the real pipeline
@pytest.fixture(scope="module")
def real_build():
    m = fz.measure(fz.pipeline_modules(), with_derived=True)
    sections, rows, problems, warnings = fz.assemble(m)
    text = fz.render(m["versions"], sections)
    return {"text": text, "rows": rows, "problems": problems, "warnings": warnings, "m": m,
            "sections": fz.parse(text)[1], "env": fz.parse(text)[0]}


SF2_FILES = (  # PipelineReview SF2 and prompt B7 / P0.2 / P5
    "screening/stage_e_verdict.py", "funnel/multiple_comparisons.py",
    "reports/stage_e32_briefs/protocol/p7_final.py", "reports/stage_e32_briefs/protocol/p7_thresholds.py",
    "reports/stage_e31_briefs/work/pilot/measure31.py", "reports/stage_e31_briefs/work/pilot/measure31_core.py",
    "reports/stage_e31_briefs/work/pilot/mbo_book31.py", "data/calendars/grains.py", "data/calendars/__init__.py",
    "data/calendars/hist2010/grains.json", "reports/stage_e31_briefs/research/usda_releases.csv",
    "reports/stage_e31_briefs/research/usda_releases_ext.csv", "reports/stage_e28_briefs/A3_econ.json",
    "reports/stage_e28_briefs/A2_firm_topstep.json", "screening/trial_registry.py", "uv.lock", "pyproject.toml",
    "reports/stage_e32_discovery_protocol.md", "reports/stage_e33_protocol_readings.md")


LEAD_ITEM2_FILES = (  # harness lazy imports, the dynamic calendar import, harness path constants (lead, item 2)
    "data/holdout.py", "data/adapter.py", "data/pull_mes.py", "data/step2_seal.py", "data/calendars/crypto.py",
    "data/calendars/equity.py", "reports/power_gate.json", "docs/HOLDOUT_MANIFEST.json",
    "reports/stage_e2a_epsilon.json", "data/calendars/hist2010/equity.json", "sim/slippage_calibration.json")


def test_real_build_has_no_problems_and_covers_sf2_and_the_lead_items(real_build):
    assert real_build["problems"] == []
    pipeline = real_build["sections"]["pipeline"]
    assert [f for f in SF2_FILES if f not in pipeline] == []
    assert [f for f in LEAD_ITEM2_FILES if f not in pipeline] == []
    assert all(fz.rel(p) in pipeline for p in fz.PIPE.glob("*.py"))
    refused = {r[1] for r in real_build["rows"] if r[0] == "guard-refused"}
    assert "data/processed/MES/ohlcv-1m_MES_v_0_2019-05-01_2024-02-29_confirmation.parquet" in refused
    assert not refused & set(pipeline)


def test_real_documents_section(real_build):
    docs = real_build["sections"]["documents"]
    readings = sorted(fz.WORK.glob("*_readings.md")) + sorted(fz.IMPLB.glob("*_readings.md"))
    assert readings and all(fz.rel(p) in docs for p in readings)
    assert all(fz.rel(p) in docs for p in fz.DOCUMENT_FILES)
    assert not any(p in real_build["sections"]["verification evidence"] for p in docs)


def test_real_derived_inputs_cover_every_loader_file_and_pass_the_guard(real_build):
    derived = real_build["m"]["derived"]
    assert fz.derived_problems(derived) == []
    paths = [d["path"] for d in derived]
    assert all(not fz.in_repo(p) for p in paths)
    hows = [h for d in derived for h in d["how"]]
    assert sum(h.startswith("data33.zm_path") for h in hows) == 816
    assert sum(h.startswith("data33.mbp1_path(ZS") for h in hows) == 816
    assert sum(h.startswith("data33.mbp1_path(ZL") for h in hows) == 816
    assert sum("E.31 ZM month markers" in h for h in hows) == 39
    assert any(p.endswith("/split/Z4/definitions_all.npy") for p in paths)
    assert not any("/features/" in p or "/labels/" in p for p in paths)  # outputs keyed by code hash


def test_real_build_sections_are_disjoint_and_exclude_environment_sealed_and_outputs(real_build):
    s = real_build["sections"]
    pipeline, evidence, tools = s["pipeline"], s["verification evidence"], s["freeze tools"]
    assert not (set(pipeline) & set(evidence)) and not (set(pipeline) & set(tools))
    assert not any(p.startswith(("reports/stage_e33_briefs/work/implB/", "reports/stage_e33_briefs/work/pipeline/tests"))
                   for p in pipeline)
    assert any(p.startswith("reports/stage_e33_briefs/work/implB/") for p in evidence)
    assert any(p.startswith("reports/stage_e33_briefs/work/pipeline/tests/") for p in evidence)
    every = [p for sec in s.values() for p in sec]
    assert not any(p.startswith((".venv/", "data/sealed/", ".git/")) or Path(p).name == ".env" for p in every)
    assert "reports/stage_e33_briefs/work/B5_proofs.md" not in pipeline
    assert "ledger/trial_registrations.jsonl" not in pipeline  # registry state changes at C1


def test_real_build_header_and_determinism(real_build):
    assert real_build["env"] == fz.env_versions()
    assert set(real_build["env"]) == {"python"} | {h for h, _ in fz.LIBRARIES}
    assert fz.verify_lines(real_build["text"]) == []
    again, _rows, problems, _w, _m = fz.build_text()
    assert problems == [] and again == real_build["text"]


def test_engine_sha_from_list_equals_search33_pipeline_sha(real_build):
    code = ("import sys; sys.path.insert(0, %r); import search33; print(search33.PIPELINE_SHA)" % str(fz.PIPE))
    run = subprocess.run([sys.executable, "-I", "-B", "-c", code], cwd=fz.REPO, capture_output=True, text=True,
                         timeout=300)
    assert run.returncode == 0, run.stderr[-2000:]
    assert fz.engine_sha_from_list(real_build["sections"]["pipeline"]) == run.stdout.split()[-1]


@pytest.mark.skipif(not fz.PROOF_MANIFEST.exists(), reason="proof run manifest not on this machine")
def test_every_proof_manifest_file_resolves_to_a_pipeline_line(real_build):
    manifest = json.loads(fz.PROOF_MANIFEST.read_text())
    lines, _fails = fz.proof_lines(real_build["text"], manifest)
    unresolved = [ln for ln in lines if "not in the pipeline section" in ln]
    assert unresolved == []
    assert real_build["sections"]["pipeline"]["uv.lock"] == manifest["versions"]["uv_lock_sha256"]  # P5
