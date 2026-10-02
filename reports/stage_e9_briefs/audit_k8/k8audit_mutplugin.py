"""Auditor's pytest plugin: install a mutated K8 module under its real module name before any test
imports it. Nothing under strategy/ or tests/ is modified; the mutated source lives under
reports/stage_e9_briefs/audit_k8/mutants/. With K8_MUT_MODULE unset the plugin does nothing."""

from __future__ import annotations

import importlib
import importlib.util
import os
import sys


def pytest_configure(config) -> None:  # noqa: ANN001
    mod_name = os.environ.get("K8_MUT_MODULE")
    if not mod_name:
        return
    src_path = os.environ["K8_MUT_SOURCE"]
    real_path = os.environ["K8_MUT_REALPATH"]
    pkg_name, child = mod_name.rsplit(".", 1)
    parent = importlib.import_module(pkg_name)
    with open(src_path, encoding="utf-8") as fh:
        src = fh.read()
    spec = importlib.util.spec_from_file_location(mod_name, real_path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = mod
    exec(compile(src, real_path, "exec"), mod.__dict__)  # noqa: S102
    setattr(parent, child, mod)
    sys.stderr.write(f"[k8audit] installed mutant {src_path} as {mod_name}\n")
