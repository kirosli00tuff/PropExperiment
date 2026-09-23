"""Stage D.1f: the preflight's refusals, the freeze anchors and the pre-purchase freeze check.

Moved here from tests/test_d1f_confirmation.py (the hash, git-anchor, build-summary and
holdout refusals) and extended for the adversarial review's fixes
(reports/stage_d1f_adversarial_review.md):
- F1: the runner takes the declared manifest sha256 and refuses any other; the two E-H
  post-amendment hashes are literals, so the reviewer's re-freeze scenario now refuses;
- F2: the D.1f quote / rolls / pull CLI and the confirmation build CLI run the file-hash checks
  first; the build records the manifest sha256 and the runner refuses a build made under
  another manifest;
- F3: strategy/research is a regular package, and an unlisted *.py under any pinned directory
  refuses;
- F4: the git anchor covers every file the manifest lists, checked in a real temp git repo.
SYNTHETIC ONLY: a miniature repository under tmp_path; the real repository is read only for
the literals and the package check. No vendor call, no bar is read.
"""

from __future__ import annotations

import json
import os
import subprocess
from argparse import Namespace
from pathlib import Path
from types import MappingProxyType

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

import data.build_mes_bars as bmb
import data.pull_mes as pull_mes
import strategy.research._d1f_confirmation as conf
import strategy.research._d1f_preflight as pf
from data.config import REPO_ROOT
from strategy.research._d1f_freeze import build_manifest

CLEAN = {"all_ok": True, "unlocks_logged": 0,
         "holdout_2": {"state": "sealed", "all_ok": True, "unlocks_logged": 0}}


def _git_ok(shown: bytes = b""):
    """A git stub: every listed path tracked and clean; ``show`` returns ``shown``."""
    def git(_root: Path, *args: str) -> subprocess.CompletedProcess:
        out = shown if args[0] == "show" else b""
        if args[0] == "ls-files":
            out = b"\0".join(a.encode() for a in args[args.index("--") + 1:])
        return subprocess.CompletedProcess(args, 0, stdout=out, stderr=b"")
    return git


CME_OLD = ('x = 1\n    # ---- 2025\n    _closure(date(2025, 1, 1), "New Year"),\n'
           '    _closure(date(2026, 12, 25), "Christmas Day"),\n')


def _refreeze(root: Path) -> str:
    """What the freeze script does: hash the CURRENT listed files and record each E-H module's
    CURRENT hash as its post-amendment hash. Returns the new manifest's sha256."""
    manifest = json.loads((root / pf.MANIFEST_PATH).read_text())
    manifest["files"] = {p: pf.sha256_file(root / p) for p in sorted(manifest["files"])}
    for rel in pf.EH_AMENDED:
        manifest["declared_amendments"][rel]["post_amendment_sha256"] = manifest["files"][rel]
    (root / pf.MANIFEST_PATH).write_text(json.dumps(manifest))
    return pf.sha256_file(root / pf.MANIFEST_PATH)


@pytest.fixture
def fake_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A miniature repository that passes every hash check."""
    files = {"a.py": "print('a')\n", pf.EH_AMENDED[0]: "h1 amended\n",
             pf.EH_AMENDED[1]: "h2 amended\n", "strategy/research/_d1f_confirmation.py": "#\n",
             "screening/runner.py": "runner\n", pf.CME_CALENDAR: CME_OLD + "# 2019 entries\n"}
    for rel, text in files.items():
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / rel).write_text(text)
    pre = {p: pf.sha256_bytes(f"{p} before\n".encode()) for p in pf.EH_AMENDED}
    lines = ["# list", "## 0. Provenance", f"- a.py  {pf.sha256_file(tmp_path / 'a.py')}",
             *(f"- {p}  {pre[p]} (pre-amendment hash)" for p in pf.EH_AMENDED),
             f"- {pf.CME_CALENDAR} (2025-2026 entries)  {pf.sha256_bytes(CME_OLD.encode())}",
             "## 1. Data", "- b.py  " + "0" * 64]
    (tmp_path / "reports").mkdir(exist_ok=True)
    (tmp_path / pf.LIST_PATH).write_text("\n".join(lines) + "\n")
    list_sha = pf.sha256_file(tmp_path / pf.LIST_PATH)
    (tmp_path / "docs").mkdir(exist_ok=True)
    (tmp_path / pf.CRITERIA_PATH).write_text(f"criteria embedding {list_sha}\n")
    (tmp_path / pf.DECLARATION_HASHES_PATH).write_text(json.dumps({
        pf.LIST_PATH: list_sha, pf.CRITERIA_PATH: pf.sha256_file(tmp_path / pf.CRITERIA_PATH)}))
    frozen = [*files, pf.LIST_PATH, pf.CRITERIA_PATH, pf.DECLARATION_HASHES_PATH]
    manifest = {"files": {p: pf.sha256_file(tmp_path / p) for p in sorted(frozen)},
                "declared_amendments": {p: {"pre_amendment_sha256": pre[p],
                                            "post_amendment_sha256":
                                                pf.sha256_file(tmp_path / p)}
                                        for p in pf.EH_AMENDED}}
    manifest["file_count"] = len(manifest["files"])
    (tmp_path / pf.MANIFEST_PATH).write_text(json.dumps(manifest))
    monkeypatch.setattr(pf, "N_SECTION0_ENTRIES", 4)
    # The fake E-H modules' hashes stand in for the declared literals (review F1).
    monkeypatch.setattr(pf, "EH_POST_AMENDMENT_SHA256", MappingProxyType(
        {p: pf.sha256_file(tmp_path / p) for p in pf.EH_AMENDED}))
    return tmp_path


def _git(root: Path, *args: str) -> str:
    env = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1",
           "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.invalid",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.invalid"}
    done = subprocess.run(["git", "-C", str(root), "-c", "core.hooksPath=/dev/null",
                           "-c", "commit.gpgsign=false", *args],
                          capture_output=True, check=True, env=env)
    return done.stdout.decode().strip()


def _commit_all(root: Path, message: str) -> None:
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", message)


@pytest.fixture
def git_root(fake_root: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """The fake repository as a REAL git repository: an anchor commit holding the calendar as
    section 0 pins it, then the freeze commit holding the manifest and every file it lists."""
    final = (fake_root / pf.CME_CALENDAR).read_text()
    _git(fake_root, "init", "-q")
    (fake_root / pf.CME_CALENDAR).write_text(CME_OLD)
    _git(fake_root, "add", pf.CME_CALENDAR)
    _git(fake_root, "commit", "-q", "-m", "anchor")
    monkeypatch.setattr(pf, "CME_ANCHOR_COMMIT", _git(fake_root, "rev-parse", "HEAD"))
    (fake_root / pf.CME_CALENDAR).write_text(final)
    _commit_all(fake_root, "freeze")
    return fake_root


# ================================================================ hash checks ====
def test_the_fake_repository_passes_every_hash_check(fake_root: Path) -> None:
    problems, sha = pf.hash_checks(fake_root, _git_ok(CME_OLD.encode()))
    assert problems == [] and sha == pf.sha256_file(fake_root / pf.MANIFEST_PATH)


def test_the_real_git_repository_passes_every_hash_check(git_root: Path) -> None:
    problems, sha = pf.hash_checks(git_root)
    assert problems == [] and sha == pf.sha256_file(git_root / pf.MANIFEST_PATH)


@pytest.mark.parametrize(("rel", "words"), [
    ("a.py", "section 0 file changed: a.py"),
    ("screening/runner.py", "manifest file changed: screening/runner.py"),
    ("strategy/research/_d1f_confirmation.py", "manifest file changed: strategy/research/_d1f_"),
    (pf.CRITERIA_PATH, "docs/NULL_CRITERIA.md: sha256"),
    (pf.EH_AMENDED[0], f"section 0 file changed: {pf.EH_AMENDED[0]}"),
])
def test_a_tampered_file_refuses(fake_root: Path, rel: str, words: str) -> None:
    with (fake_root / rel).open("a") as fh:
        fh.write("tampered\n")
    problems, _ = pf.hash_checks(fake_root, _git_ok(CME_OLD.encode()))
    assert any(words in p for p in problems), problems


def test_a_tampered_list_or_manifest_refuses(fake_root: Path) -> None:
    (fake_root / "strategy/research/_d1f_extra.py").write_text("#\n")
    problems, _ = pf.hash_checks(fake_root, _git_ok(CME_OLD.encode()))
    assert any("_d1f_extra.py is not in the freeze manifest" in p for p in problems)
    manifest = json.loads((fake_root / pf.MANIFEST_PATH).read_text())
    manifest["files"]["a.py"] = "f" * 64
    (fake_root / pf.MANIFEST_PATH).write_text(json.dumps(manifest))
    problems, _ = pf.hash_checks(fake_root, _git_ok(CME_OLD.encode()))
    assert any("manifest file changed: a.py" in p for p in problems)
    text = (fake_root / pf.LIST_PATH).read_text().replace("## 1. Data", "## 1. Data (edited)")
    (fake_root / pf.LIST_PATH).write_text(text)
    problems, _ = pf.hash_checks(fake_root, _git_ok(CME_OLD.encode()))
    assert any("stage_d1f_confirmation_list.md: sha256" in p for p in problems)


def test_the_cme_calendar_is_checked_on_its_2025_2026_block_only(fake_root: Path) -> None:
    pinned = pf.sha256_bytes(CME_OLD.encode())
    assert pf.check_cme_calendar(fake_root, pinned, _git_ok(CME_OLD.encode())) == []
    wrong_anchor = CME_OLD.replace("x = 1", "x = 2").encode()
    assert "does not hash" in pf.check_cme_calendar(fake_root, pinned, _git_ok(wrong_anchor))[0]
    (fake_root / pf.CME_CALENDAR).write_text(CME_OLD.replace("New Year", "New Years") + "#\n")
    assert "2025-2026 entries changed" in pf.check_cme_calendar(
        fake_root, pinned, _git_ok(CME_OLD.encode()))[0]


def test_the_real_cme_calendar_block_matches_commit_9cbd815() -> None:
    entry = next(e for e in pf.parse_section0((REPO_ROOT / pf.LIST_PATH).read_text())
                 if e.path == pf.CME_CALENDAR)
    assert pf.check_cme_calendar(REPO_ROOT, entry.sha256) == []


# ======================================================= F1: declared anchors ====
def test_the_declared_eh_literals_are_the_real_modules_hashes() -> None:
    assert dict(pf.EH_POST_AMENDMENT_SHA256) == {
        "strategy/research/e_calendar_event/h1_scheduled_macro_drift.py":
            "f28529f058e9a6cc63d1030f6e08ce1b78e7c11c7f89ad64aa583468e1eb7a35",
        "strategy/research/e_calendar_event/h2_post_release_momentum.py":
            "7183d9bda56b36b9089b05b9ee02cbd9609392f29d88f14ca005fb6bb341aeca"}
    for rel, declared in pf.EH_POST_AMENDMENT_SHA256.items():
        assert pf.sha256_file(REPO_ROOT / rel) == declared


def test_the_freeze_script_refuses_eh_modules_off_the_declared_literals(monkeypatch) -> None:
    monkeypatch.setattr(pf, "EH_POST_AMENDMENT_SHA256",
                        MappingProxyType({p: "0" * 64 for p in pf.EH_AMENDED}))
    with pytest.raises(ValueError, match="refusing to freeze"):
        build_manifest(REPO_ROOT)


def test_the_reviewers_refreeze_of_an_eh_module_now_refuses(git_root: Path) -> None:
    # review/demo_refreeze.py: edit a harness file AND the E-H1 module, re-run the freeze,
    # commit. Before the fix every check passed; the declared literal now refuses.
    (git_root / "screening/runner.py").write_text("runner\nEDITED AFTER THE FREEZE\n")
    (git_root / pf.EH_AMENDED[0]).write_text("h1 amended\nEDITED AGAIN AFTER THE FREEZE\n")
    _refreeze(git_root)
    _commit_all(git_root, "re-freeze")
    problems, _ = pf.hash_checks(git_root)
    assert any(f"{pf.EH_AMENDED[0]}: the manifest's hash is not the declared" in p
               for p in problems), problems
    assert f"section 0 file changed: {pf.EH_AMENDED[0]}" in problems


def _build_files(tmp_path: Path, summary: dict, meta: dict) -> tuple[Path, Path]:
    s, p = tmp_path / "build.json", tmp_path / "c.parquet"
    s.write_text(json.dumps(summary))
    table = pa.table({"x": [1]}).replace_schema_metadata(
        {b"propexperiment": json.dumps(meta).encode()})
    pq.write_table(table, p)
    return s, p


def _passing_build(tmp_path: Path, manifest_sha: str) -> tuple[Path, Path]:
    comparison = {"identical": True}
    return _build_files(
        tmp_path, {"manifest_sha256": manifest_sha, "stop_for_lead_decision": False,
                   "calendar_validation_step4b": {"passed": True},
                   "degraded_dates_comparison": comparison},
        {"manifest_sha256": manifest_sha, "stop_for_lead_decision": False,
         "calendar_validation_step4b_passed": True, "degraded_dates_comparison": comparison})


def test_the_reviewers_refreeze_of_a_harness_file_refuses_at_the_runner(
        git_root: Path, tmp_path: Path, monkeypatch, capsys) -> None:
    declared = pf.sha256_file(git_root / pf.MANIFEST_PATH)
    (git_root / "screening/runner.py").write_text("runner\nEDITED AFTER THE FREEZE\n")
    refrozen = _refreeze(git_root)
    _commit_all(git_root, "re-freeze")
    assert pf.hash_checks(git_root) == ([], refrozen) and refrozen != declared  # as before
    summary, parquet = _passing_build(tmp_path, refrozen)
    monkeypatch.setattr(conf, "preflight", lambda: pf.preflight(
        git_root, summary_path=summary, parquet_path=parquet, holdout_status=lambda: CLEAN))
    assert conf.run_step("preflight", 1, declared) == conf.RC_REFUSED
    assert f"is not the declared {declared}" in capsys.readouterr().out
    assert conf.run_step("preflight", 1, refrozen) == 0  # only the declared value refused


def test_the_runner_requires_a_declared_manifest_sha256(capsys) -> None:
    for argv in (["--step", "preflight"], ["--step", "5", "--manifest-sha256", "abc"],
                 ["--step", "5", "--manifest-sha256", "A" * 64]):
        with pytest.raises(SystemExit):
            conf.main(argv)
    assert "manifest-sha256" in capsys.readouterr().err


def test_every_step_refuses_a_manifest_other_than_the_declared_one(monkeypatch) -> None:
    seen = pf.Preflight(True, (), "b" * 64, {})
    monkeypatch.setattr(conf, "preflight", lambda: seen)
    monkeypatch.setattr(conf, "_refuse_if_decided", lambda: pytest.fail("a step ran"))
    for step in ("preflight", "5", "6", "7", "8"):
        assert conf.run_step(step, 1, "a" * 64) == conf.RC_REFUSED
    assert conf.declared_manifest_problems(seen, "b" * 64) == []
    assert conf.main(["--step", "all", "--manifest-sha256", "a" * 64]) == conf.RC_REFUSED


def test_the_runner_refuses_in_the_build_session(capsys) -> None:
    before = {p: p.exists() for p in (conf.START_RULE_PATH, *conf.STEP8_OUTPUTS)}
    declared = ["--manifest-sha256", "0" * 64]
    assert conf.main(["--step", "preflight", *declared]) == conf.RC_REFUSED
    assert conf.main(["--step", "all", *declared]) == conf.RC_REFUSED
    assert "REFUSED" in capsys.readouterr().out
    assert {p: p.exists() for p in before} == before


# ============================================== F2: the build and the pull ====
def test_build_summary_flags_refuse_and_a_degraded_difference_is_only_logged(
        tmp_path: Path) -> None:
    sha = "c" * 64
    comparison = {"identical": False, "added_since_declaration": ["2021-01-05"]}
    good = {"manifest_sha256": sha, "stop_for_lead_decision": False,
            "calendar_validation_step4b": {"passed": True},
            "degraded_dates_comparison": comparison}
    meta = {"manifest_sha256": sha, "stop_for_lead_decision": False,
            "calendar_validation_step4b_passed": True, "degraded_dates_comparison": comparison}
    problems, record = pf.check_build(*_build_files(tmp_path, good, meta), manifest_sha256=sha)
    assert problems == [] and record["degraded_dates_differ_from_declaration"] is True
    assert record["manifest_sha256_of_the_build"] == sha
    cases = (({**good, "stop_for_lead_decision": True}, meta, "stop for the lead"),
             ({**good, "calendar_validation_step4b": {"passed": False}}, meta, "step 4b"),
             ({k: v for k, v in good.items() if k != "degraded_dates_comparison"}, meta,
              "comparison is missing"),
             (good, {**meta, "stop_for_lead_decision": True}, "metadata"),
             ({**good, "manifest_sha256": "d" * 64}, meta, "ran under freeze manifest"),
             ({k: v for k, v in good.items() if k != "manifest_sha256"}, meta,
              "ran under freeze manifest None"),
             (good, {**meta, "manifest_sha256": "d" * 64}, "metadata manifest_sha256"))
    for summary, parquet_meta, words in cases:
        problems, _ = pf.check_build(*_build_files(tmp_path, summary, parquet_meta),
                                     manifest_sha256=sha)
        assert any(words in p for p in problems), (words, problems)
    problems, _ = pf.check_build(*_build_files(tmp_path, good, meta), manifest_sha256=None)
    assert any("ran under freeze manifest" in p for p in problems)
    assert "summary missing" in pf.check_build(tmp_path / "none.json", tmp_path / "c.parquet",
                                               manifest_sha256=sha)[0][0]


class _NoVendor:
    """A Databento client that fails the test on any use."""

    def __getattr__(self, name: str) -> object:
        raise AssertionError(f"a vendor call was attempted: {name}")


D1F_MODES = ({"d1f_rolls": True, "d1f_quote_only": False, "d1f_pull": False},
             {"d1f_rolls": False, "d1f_quote_only": True, "d1f_pull": False},
             {"d1f_rolls": False, "d1f_quote_only": False, "d1f_pull": True})


def test_the_d1f_pull_cli_refuses_before_any_vendor_call(git_root: Path, monkeypatch) -> None:
    monkeypatch.setattr(pull_mes, "REPO_ROOT", git_root)
    monkeypatch.setattr(pull_mes, "d1f_gate", lambda: pytest.fail("the gate was reached"))
    with (git_root / "screening/runner.py").open("a") as fh:
        fh.write("typed in during the pull\n")
    problems, _ = pull_mes.d1f_freeze_check()
    assert any("manifest file changed: screening/runner.py" in p for p in problems)
    assert any("screening/runner.py has uncommitted changes" in p for p in problems)
    for mode in D1F_MODES:
        assert pull_mes.main_d1f(_NoVendor(), Namespace(**mode)) == pull_mes.RC_FREEZE_REFUSED


def test_the_d1f_pull_cli_proceeds_when_the_freeze_matches(git_root: Path, monkeypatch,
                                                           capsys) -> None:
    monkeypatch.setattr(pull_mes, "REPO_ROOT", git_root)
    called: list = []
    monkeypatch.setattr(pull_mes, "resolve_d1f_rolls", lambda client: called.append(client))
    client = _NoVendor()
    assert pull_mes.main_d1f(client, Namespace(**D1F_MODES[0])) == 0 and called == [client]
    sha = pf.sha256_file(git_root / pf.MANIFEST_PATH)
    assert f"manifest sha256 {sha}" in capsys.readouterr().out


def test_the_confirmation_build_cli_checks_the_freeze_first(git_root: Path, monkeypatch) -> None:
    monkeypatch.setattr(pull_mes, "REPO_ROOT", git_root)  # d1f_freeze_check's root
    built: list = []
    monkeypatch.setattr(bmb, "build_confirmation", lambda **kw: built.append(kw) or 0)
    assert bmb.cli(["--confirmation"]) == 0
    assert built == [{"manifest_sha256": pf.sha256_file(git_root / pf.MANIFEST_PATH)}]
    (git_root / "a.py").write_text("print('b')\n")
    assert bmb.cli(["--confirmation"]) == bmb.RC_FREEZE_REFUSED and len(built) == 1


# ======================================================== F3: unlisted *.py ====
def test_strategy_research_is_a_regular_package_with_an_empty_init() -> None:
    import strategy.research

    init = REPO_ROOT / "strategy/research/__init__.py"
    assert init.is_file() and init.read_bytes() == b""
    assert Path(strategy.research.__file__) == init


@pytest.mark.parametrize("rel", ["strategy/research/__init__.py", "strategy/other/new.py",
                                 "data/new.py", "data/sub/deep.py", "screening/new.py",
                                 "sim/new.py", "funnel/new.py", "rules/new.py"])
def test_an_unlisted_py_under_any_pinned_directory_refuses(fake_root: Path, rel: str) -> None:
    (fake_root / rel).parent.mkdir(parents=True, exist_ok=True)
    (fake_root / rel).write_text("VALUE = 999  # runs on import, unpinned\n")
    problems, _ = pf.hash_checks(fake_root, _git_ok(CME_OLD.encode()))
    assert f"{rel} is not in the freeze manifest" in problems


def test_a_py_outside_the_pinned_directories_or_a_cache_is_not_refused(fake_root: Path) -> None:
    for rel in ("tests/test_new.py", "scratch.py", "strategy/research/__pycache__/x.py"):
        (fake_root / rel).parent.mkdir(parents=True, exist_ok=True)
        (fake_root / rel).write_text("#\n")
    assert pf.hash_checks(fake_root, _git_ok(CME_OLD.encode()))[0] == []


# =========================================== F4: git anchor over every file ====
def test_the_git_anchor_covers_every_listed_file(git_root: Path) -> None:
    manifest = json.loads((git_root / pf.MANIFEST_PATH).read_text())
    assert pf.check_git_anchor(git_root, manifest) == []
    (git_root / "screening/runner.py").write_text("runner\nedited\n")
    problems = pf.check_git_anchor(git_root, manifest)
    assert problems == ["screening/runner.py has uncommitted changes in git (M)"]
    _git(git_root, "checkout", "--", "screening/runner.py")
    _git(git_root, "rm", "-q", "--cached", "a.py")
    _git(git_root, "commit", "-q", "-m", "a.py left out of the freeze commit")
    problems = pf.check_git_anchor(git_root, manifest)
    assert "a.py is not tracked in git (the user's freeze commit anchors it)" in problems
    assert any(p.startswith("a.py has uncommitted changes") for p in problems)  # untracked
    (git_root / pf.MANIFEST_PATH).write_text("{}")
    assert any(p.startswith(f"{pf.MANIFEST_PATH} has uncommitted changes")
               for p in pf.check_git_anchor(git_root, manifest))


def test_the_manifest_must_be_committed(fake_root: Path) -> None:
    def failing(_root: Path, *args: str) -> subprocess.CompletedProcess:
        return subprocess.CompletedProcess(args, 128, stdout=b"", stderr=b"not a git repo")

    assert "git ls-files / status failed" in pf.check_git_anchor(fake_root, None, failing)[0]

    def no_git(*_a: object) -> subprocess.CompletedProcess:
        raise FileNotFoundError("git")

    assert "git unavailable" in pf.check_git_anchor(fake_root, None, no_git)[0]


# ================================================================ holdouts ====
def test_holdouts_must_be_clean() -> None:
    assert pf.check_holdouts(lambda: CLEAN)[0] == []
    assert pf.check_holdouts(lambda: {**CLEAN, "unlocks_logged": 1})[0]
    unsealed = {**CLEAN, "holdout_2": {"state": "not_yet_sealed", "all_ok": False,
                                       "unlocks_logged": 0}}
    assert "holdout-2" in pf.check_holdouts(lambda: unsealed)[0][0]


def test_steps_refuse_out_of_order_and_outputs_are_never_overwritten(tmp_path: Path) -> None:
    with pytest.raises(conf.StepRefused, match="has not run"):
        conf.read_step(tmp_path / "missing.json", "sha", "step 5")
    target = tmp_path / "out.json"
    sha = conf.write_once(target, {"manifest_sha256": "abc", "x": float("nan")})
    assert sha == pf.sha256_file(target) and json.loads(target.read_text())["x"] is None
    with pytest.raises(conf.StepRefused, match="never re-run"):
        conf.write_once(target, {"manifest_sha256": "abc"})
    with pytest.raises(conf.StepRefused, match="another freeze manifest"):
        conf.read_step(target, "other", "step 5")
