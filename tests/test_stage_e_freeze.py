"""The per-cluster member code freeze (screening/stage_e_freeze.py): written once before any
member runs; the runner refuses a changed, unlisted or missing member file, an undeclared label,
a factory other than the declared one, and legs other than the declared ones."""

from __future__ import annotations

import os
import stat
from pathlib import Path

import pytest

from screening.stage_e_freeze import (
    ClusterFreezeError,
    MemberDecl,
    freeze_path,
    load_cluster_freeze,
    members_dir,
    resolve_member,
    verify_cluster_code,
    write_cluster_freeze,
)
from strategy.stage_e.interface import LegSpec
from tests._stage_e_synthetic import install_member_package

LEGS = (LegSpec("ZN", True),)


def _decl(module: str, label: str = "K1-test-01 ZN", ordinal: int = 1,
          factory: str = "make_member") -> MemberDecl:
    return MemberDecl(label, ordinal, module, factory, LEGS)


def test_a_freeze_is_written_once_read_only_and_loads_back(tmp_path: Path, monkeypatch) -> None:
    module = install_member_package(tmp_path, monkeypatch)
    sha = write_cluster_freeze("K1", [_decl(module)], root=tmp_path)
    path = tmp_path / freeze_path("K1")
    assert path.is_file() and not os.stat(path).st_mode & stat.S_IWUSR
    freeze = load_cluster_freeze("K1", root=tmp_path)
    assert freeze.sha256 == sha and freeze.member("K1-test-01 ZN").legs == LEGS
    assert set(freeze.files) == {"strategy/members/__init__.py", "strategy/members/k1/__init__.py",
                                 "strategy/members/k1/synth.py"}
    with pytest.raises(ClusterFreezeError, match="written once"):
        write_cluster_freeze("K1", [_decl(module)], root=tmp_path)
    verify_cluster_code(freeze, root=tmp_path)
    decl, factory = resolve_member(freeze, "K1-test-01 ZN")
    assert decl.ordinal == 1 and factory().name == "synthetic"


def test_a_changed_member_file_is_refused(tmp_path: Path, monkeypatch) -> None:
    module = install_member_package(tmp_path, monkeypatch)
    write_cluster_freeze("K1", [_decl(module)], root=tmp_path)
    target = tmp_path / "strategy/members/k1/synth.py"
    target.write_text(target.read_text(encoding="utf-8") + "# edited\n", encoding="utf-8")
    with pytest.raises(ClusterFreezeError, match="differs from the frozen"):
        verify_cluster_code(load_cluster_freeze("K1", root=tmp_path), root=tmp_path)


def test_an_unlisted_or_missing_member_file_is_refused(tmp_path: Path, monkeypatch) -> None:
    module = install_member_package(tmp_path, monkeypatch)
    write_cluster_freeze("K1", [_decl(module)], root=tmp_path)
    freeze = load_cluster_freeze("K1", root=tmp_path)
    extra = tmp_path / "strategy/members/k1/helper.py"
    extra.write_text("X = 1\n", encoding="utf-8")
    with pytest.raises(ClusterFreezeError, match="not in the freeze"):
        verify_cluster_code(freeze, root=tmp_path)
    extra.unlink()
    (tmp_path / "strategy/members/k1/synth.py").unlink()
    with pytest.raises(ClusterFreezeError, match="missing"):
        verify_cluster_code(freeze, root=tmp_path)


def test_an_undeclared_label_or_another_factory_is_refused(tmp_path: Path, monkeypatch) -> None:
    module = install_member_package(tmp_path, monkeypatch)
    write_cluster_freeze("K1", [_decl(module)], root=tmp_path)
    freeze = load_cluster_freeze("K1", root=tmp_path)
    with pytest.raises(ClusterFreezeError, match="not in the freeze"):
        resolve_member(freeze, "K1-other-01 ZN")
    import importlib

    other = importlib.import_module(module).other_factory
    with pytest.raises(ClusterFreezeError, match="is not"):
        resolve_member(freeze, "K1-test-01 ZN", other)


def test_bad_declarations_are_refused_before_anything_is_written(tmp_path: Path,
                                                                  monkeypatch) -> None:
    module = install_member_package(tmp_path, monkeypatch)
    with pytest.raises(ClusterFreezeError, match="K1..K8"):
        write_cluster_freeze("K9", [_decl(module)], root=tmp_path)
    with pytest.raises(ClusterFreezeError, match="unique"):
        write_cluster_freeze("K1", [_decl(module), _decl(module)], root=tmp_path)
    with pytest.raises(ClusterFreezeError, match="is not under"):
        write_cluster_freeze("K1", [_decl("strategy.research.x")], root=tmp_path)
    with pytest.raises(ClusterFreezeError, match="traded leg"):
        write_cluster_freeze("K1", [MemberDecl("L", 1, module, "make_member",
                                               (LegSpec("MES", False),))], root=tmp_path)
    assert not (tmp_path / freeze_path("K1")).exists()


def test_member_code_lives_outside_the_harness_directory() -> None:
    from screening.harness_freeze import HARNESS_DIRS

    assert members_dir("K3").as_posix() == "strategy/members/k3"
    assert not any(members_dir("K3").as_posix().startswith(d + "/") or
                   members_dir("K3").as_posix() == d for d in HARNESS_DIRS)


def test_a_cluster_without_a_freeze_file_is_refused(tmp_path: Path) -> None:
    with pytest.raises(ClusterFreezeError, match="has not been frozen"):
        load_cluster_freeze("K2", root=tmp_path)


# ------------------------------------------------------------------ F-1 ----
EXPLOIT = ("import screening.stage_e_runner as runner\n"
           "runner.MEAN_HOLD_MIN_MINUTES = 0.0\n")


def test_f1_exploit_a_patching_members_init_is_refused_and_never_runs(tmp_path: Path,
                                                                      monkeypatch) -> None:
    """Review F-1 reproduced: strategy/members/__init__.py that patches a runner constant. The
    freeze refuses it (the init must be empty); planted after the freeze, verify and resolve
    refuse it before anything is imported, so the constant keeps its value."""
    import screening.stage_e_runner as runner

    module = install_member_package(tmp_path, monkeypatch)
    init = tmp_path / "strategy/members/__init__.py"
    init.write_text(EXPLOIT, encoding="utf-8")
    with pytest.raises(ClusterFreezeError, match="must be empty"):
        write_cluster_freeze("K1", [_decl(module)], root=tmp_path)
    init.write_text("", encoding="utf-8")
    write_cluster_freeze("K1", [_decl(module)], root=tmp_path)
    freeze = load_cluster_freeze("K1", root=tmp_path)
    assert "strategy/members/__init__.py" in freeze.files
    init.write_text(EXPLOIT, encoding="utf-8")
    with pytest.raises(ClusterFreezeError, match="must be empty"):
        verify_cluster_code(freeze)
    with pytest.raises(ClusterFreezeError, match="must be empty"):
        resolve_member(freeze, "K1-test-01 ZN")
    assert runner.MEAN_HOLD_MIN_MINUTES == 10.0


def test_f1_exploit_a_member_module_that_patches_the_runner_is_refused(tmp_path: Path,
                                                                        monkeypatch) -> None:
    import screening.stage_e_runner as runner

    module = install_member_package(tmp_path, monkeypatch)
    target = tmp_path / "strategy/members/k1/synth.py"
    target.write_text(EXPLOIT + target.read_text(encoding="utf-8"), encoding="utf-8")
    with pytest.raises(ClusterFreezeError, match="import_not_allowed.*assigns_imported"):
        write_cluster_freeze("K1", [_decl(module)], root=tmp_path)
    assert runner.MEAN_HOLD_MIN_MINUTES == 10.0


def test_f1_a_freeze_written_before_the_fix_is_refused(tmp_path: Path, monkeypatch) -> None:
    import json

    module = install_member_package(tmp_path, monkeypatch)
    write_cluster_freeze("K1", [_decl(module)], root=tmp_path)
    path = tmp_path / freeze_path("K1")
    doc = json.loads(path.read_text(encoding="utf-8"))
    del doc["files"]["strategy/members/__init__.py"]
    os.chmod(path, 0o644)
    path.write_text(json.dumps(doc), encoding="utf-8")
    with pytest.raises(ClusterFreezeError, match="does not hash"):
        load_cluster_freeze("K1", root=tmp_path)


def test_f1_the_allowlist_accepts_the_template_and_the_synthetic_member() -> None:
    from data.config import REPO_ROOT
    from screening.stage_e_freeze import check_member_source
    from tests._stage_e_synthetic import MEMBER_SOURCE

    template = (REPO_ROOT / "strategy/stage_e/_template.py").read_text(encoding="utf-8")
    assert check_member_source("strategy/members/k1/cp2.py", template, "K1") == []
    member = MEMBER_SOURCE.format(entry=(9, 10), exit=(9, 40), early=False)
    assert check_member_source("strategy/members/k1/synth.py", member, "K1") == []
    own = "from strategy.members.k1 import helper\nfrom . import other\nimport numpy as np\n"
    assert check_member_source("strategy/members/k1/m.py", own, "K1") == []


BANNED = [
    ("import os", "import_not_allowed"),
    ("import importlib", "import_not_allowed"),
    ("from pathlib import Path", "import_not_allowed"),
    ("import numpy.f2py", "import_not_allowed"),
    ("import rules.sessions", "import_not_allowed"),
    ("from rules import sessions", "import_not_allowed"),
    ("import screening.stage_e_runner", "import_not_allowed"),
    ("from strategy.members.k2 import x", "import_not_allowed"),
    ("from .. import k2", "import_not_allowed"),
    ("from numpy import *", "star_import"),
    ("x = open('f')", "banned_name"),
    ("exec('1')", "banned_name"),
    ("eval('1')", "banned_name"),
    ("compile('1', 'f', 'exec')", "banned_name"),
    ("__import__('os')", "banned_name"),
    ("g = globals()", "banned_name"),
    ("setattr(a, 'b', 1)", "banned_name"),
    ("delattr(a, 'b')", "banned_name"),
    ("getattr(a, 'b')", "banned_name"),
    ("b = __builtins__", "banned_name"),
    ("import numpy as np\nnp.sys", "banned_name"),
    ("from math import sqrt as open", "banned_name"),
    ("s = ().__class__.__base__.__subclasses__()", "dunder_attribute"),
    ("import numpy as np\nnp.load('f.npy')", "file_io"),
    ("def f(a):\n    a.tofile('x')", "file_io"),
    ("import rules.products as p\np.PRODUCTS = {}", "assigns_imported"),
    ("from rules.products import PRODUCTS\nPRODUCTS['ZN'] = None", "assigns_imported"),
    ("from rules.products import PRODUCTS\ndel PRODUCTS['ZN']", "assigns_imported"),
    ("import math\nmath.pi += 1", "assigns_imported"),
    ("from rules.products import PRODUCTS\nPRODUCTS.update({})", "mutating_call_on_imported"),
    ("from screening.stage_e_frozen import load_frozen_tables\nload_frozen_tables.cache_clear()",
     "mutating_call_on_imported"),
]


@pytest.mark.parametrize(("source", "rule"), BANNED)
def test_f1_each_banned_form_is_refused_with_file_line_and_rule(source: str, rule: str) -> None:
    from screening.stage_e_freeze import check_member_source

    problems = check_member_source("strategy/members/k1/m.py", source, "K1")
    assert any(p.startswith("strategy/members/k1/m.py:") and f": {rule}: " in p
               for p in problems), problems


def test_f1_an_importable_non_source_file_is_refused(tmp_path: Path, monkeypatch) -> None:
    module = install_member_package(tmp_path, monkeypatch)
    (tmp_path / "strategy/members/k1/evil.pyc").write_bytes(b"\x00")
    with pytest.raises(ClusterFreezeError, match="non-source"):
        write_cluster_freeze("K1", [_decl(module)], root=tmp_path)


def test_f1_resolve_refuses_when_python_would_import_another_file(tmp_path: Path,
                                                                   monkeypatch) -> None:
    import strategy

    module = install_member_package(tmp_path / "a", monkeypatch)
    write_cluster_freeze("K1", [_decl(module)], root=tmp_path / "a")
    freeze = load_cluster_freeze("K1", root=tmp_path / "a")
    install_member_package(tmp_path / "b", monkeypatch)  # now first on strategy.__path__
    assert str(tmp_path / "b" / "strategy") == strategy.__path__[0]
    with pytest.raises(ClusterFreezeError, match="not the checked files"):
        resolve_member(freeze, "K1-test-01 ZN")
