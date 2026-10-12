"""The search's read guard (reports/stage_e20_plan.md section 3; F3): every planted case raises.
The audit hook is irreversible, so its test runs in a subprocess. Nothing here opens a store:
every planted path is refused before an open, and the hook test plants paths that do not exist."""

from __future__ import annotations

import subprocess
import sys
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from pattern_search import constants as K
from pattern_search import guard
from pattern_search import world as W


def _repo() -> Path:
    from data.config import REPO_ROOT

    return Path(REPO_ROOT)


def _planted() -> dict[str, Path]:
    from data.config import HIST_ROOT, PROCESSED_ROOT, STEP2_ROOT, VENDOR_ROOT
    from data.holdout import DEFAULT_PATHS, HOLDOUT2_PATHS
    from data.step2_seal import SEALED_BASE

    return {
        "processed_hist ext2010": Path(HIST_ROOT) / "ext2010" / "NQ" / "planted_absent.parquet",
        "processed_hist ext2010h": Path(HIST_ROOT) / "ext2010h" / "ZT" / "planted_absent.parquet",
        "sealed": Path(SEALED_BASE) / "planted_absent.sealed",
        "holdout 1 blob": Path(DEFAULT_PATHS.holdout_blob),
        "holdout 2 blob": Path(HOLDOUT2_PATHS.holdout_blob),
        "holdout 1 research parquet": Path(DEFAULT_PATHS.research_parquet),
        "holdout 2 confirmation parquet": Path(HOLDOUT2_PATHS.research_parquet),
        "MES research store": Path(PROCESSED_ROOT) / "MES" / "planted_absent.parquet",
        "MES step 2 store": Path(STEP2_ROOT) / "MES" / "planted_absent.parquet",
        "research store of a search root": Path(PROCESSED_ROOT) / "NQ" / "planted.parquet",
        "another root's step 2 store": guard.step2_store_path("ES"),
        "an outside root's store (6J)": guard.step2_store_path("6J"),
        "a vendor chunk": Path(VENDOR_ROOT) / "planted_absent.dbn.zst",
        "another file in a search root's step 2 directory":
            Path(STEP2_ROOT) / "NQ" / "planted_other.parquet",
    }


@pytest.mark.parametrize("case", sorted(_planted()))
def test_every_planted_forbidden_path_is_refused(case: str) -> None:
    with pytest.raises(guard.GuardRefusal, match="E.20 search guard"):
        guard.check_store_path(_planted()[case])


def test_the_refusal_names_the_forbidden_class() -> None:
    p = _planted()
    assert guard.refusal_reason(p["processed_hist ext2010"]) == guard.REASON_HIST
    assert guard.refusal_reason(p["sealed"]) == guard.REASON_HOLDOUT
    assert guard.refusal_reason(p["holdout 2 confirmation parquet"]) == guard.REASON_HOLDOUT
    assert guard.refusal_reason(p["MES research store"]) == guard.REASON_PROCESSED
    assert guard.refusal_reason(p["another root's step 2 store"]) == guard.REASON_OTHER
    assert guard.refusal_reason(p["a vendor chunk"]) == guard.REASON_OTHER


def test_the_17_search_stores_pass_and_nothing_is_opened() -> None:
    allowed = guard.search_store_paths()
    assert len(allowed) == 17 and sorted(allowed.values()) == sorted(K.PATH_ROOTS)
    for root in K.PATH_ROOTS:
        path = guard.step2_store_path(root)
        assert guard.check_store_path(path) == path
        assert path.name == f"ohlcv-1m_{root}_v_0_2019-05-06_2024-02-29_step2.parquet"


def test_a_symlink_to_a_forbidden_store_is_refused(tmp_path) -> None:
    link = tmp_path / "innocent.parquet"
    link.symlink_to(_planted()["processed_hist ext2010"])
    with pytest.raises(guard.GuardRefusal, match="processed_hist"):
        guard.check_store_path(link)


def test_a_path_outside_every_store_root_is_still_not_a_search_store(tmp_path) -> None:
    with pytest.raises(guard.GuardRefusal, match="not one of the 17"):
        guard.check_store_path(tmp_path / "x.parquet")


def _b1_registry(tmp: Path) -> Path:
    from pattern_search import preflight as pf
    from screening.trial_registry import init_registry, register

    reg = tmp / "registry.jsonl"
    init_registry(reg)
    f = tmp / "b1_freeze.json"
    f.write_text("{}")
    register(K.B1_LABEL, [K.B1_TEST_ID], f, pf.sha256_file(f), "0" * 64, path=reg)
    return reg


def test_processed_hist_is_refused_before_registration_after_it_and_with_a_marker(tmp_path
                                                                                  ) -> None:
    """Plan 3: before E20-B1's registration, after it without the marker, and (Step 6: the B1
    code is not built) even with both, every processed_hist path is refused."""
    hist = _planted()["processed_hist ext2010"]
    with pytest.raises(guard.GuardRefusal, match="processed_hist"):
        guard.check_store_path(hist)  # before any registration
    _b1_registry(tmp_path)
    with pytest.raises(guard.GuardRefusal, match="processed_hist"):
        guard.check_store_path(hist)  # registered, no marker
    (tmp_path / "stage_e20_B1_RUN_ONCE.json").write_text("{}")
    with pytest.raises(guard.GuardRefusal, match="processed_hist"):
        guard.check_store_path(hist)  # registered and marked: still refused in Step 6
    assert guard.backward_permitted() is False


def test_audit_decision_refuses_opens_of_forbidden_prefixes() -> None:
    prefixes = guard.forbidden_prefixes()
    allowed = guard.search_store_paths()
    for path in _planted().values():
        why = guard.audit_decision("open", (str(path), "rb", 0), allowed=allowed,
                                   prefixes=prefixes)
        assert why is not None and "audit hook" in why
    store = str(guard.step2_store_path("NQ"))
    assert guard.audit_decision("open", (store, "rb", 0), allowed=allowed,
                                prefixes=prefixes) is None
    assert guard.audit_decision("open", (3, "rb", 0), allowed=allowed, prefixes=prefixes) is None
    assert guard.audit_decision("exec", ("x",), allowed=allowed, prefixes=prefixes) is None


_HOOK_SCRIPT = """
import io, os, sys
sys.path.insert(0, {repo!r})
from pattern_search import guard
assert guard.install_audit_hook() is True
assert guard.install_audit_hook() is False
refused = []
for path in {paths!r}:
    for opener in (lambda p: open(p, "rb"), lambda p: os.open(p, os.O_RDONLY),
                   lambda p: io.open_code(p)):
        try:
            opener(path)
        except guard.GuardRefusal as exc:
            refused.append("E.20 search guard" in str(exc))
        except OSError:
            refused.append(False)
print("REFUSED", sum(refused), len(refused))
"""


def test_the_audit_hook_refuses_python_level_opens_in_a_cli_like_process() -> None:
    paths = [str(p) for k, p in _planted().items() if "planted" in p.name or "6J" in k
             or "ES" in str(p)]
    paths = [p for p in paths if not Path(p).exists()]
    assert len(paths) >= 6
    script = _HOOK_SCRIPT.format(repo=str(_repo()), paths=paths)
    proc = subprocess.run([sys.executable, "-c", script], cwd=_repo(), capture_output=True,
                          text=True, timeout=120, check=False)
    assert proc.returncode == 0, proc.stderr[-2000:]
    n = 3 * len(paths)
    assert f"REFUSED {n} {n}" in proc.stdout


# ------------------------------------------------------------------ (c) the bars ----
def _bars(day: str, ts_ns: int) -> pd.DataFrame:
    return pd.DataFrame({"ts_event": np.asarray([ts_ns], dtype=np.int64),
                         "trade_date": pd.Categorical([day])})


def test_bars_dated_before_march_2024_pass() -> None:
    ts = int(pd.Timestamp("2024-02-29 20:00", tz="UTC").value)
    guard.check_bars(_bars("2024-02-29", ts))


def test_a_bar_with_trade_date_march_1_2024_raises() -> None:
    ts = int(pd.Timestamp("2024-02-29 20:00", tz="UTC").value)
    with pytest.raises(guard.GuardRefusal, match="2024-03-01"):
        guard.check_bars(_bars("2024-03-01", ts))


def test_a_bar_opening_on_or_after_march_1_2024_utc_raises_whatever_its_label() -> None:
    ts = int(pd.Timestamp("2024-03-01 00:00", tz="UTC").value)
    with pytest.raises(guard.GuardRefusal, match="00:00 UTC"):
        guard.check_bars(_bars("2024-02-29", ts))


def test_a_world_reaching_march_2024_is_refused_by_the_frame_check() -> None:
    ts = int(pd.Timestamp("2024-03-01 15:00", tz="UTC").value)
    with pytest.raises(guard.GuardRefusal):
        guard.check_frames({"NQ": _bars("2024-03-01", ts)})


# ------------------------------------------------------------------ the loader wrapper ----
def test_the_loader_wrapper_refuses_before_the_frozen_loader_runs(monkeypatch, tmp_path) -> None:
    from data.config import HIST_ROOT

    def boom(*a, **k):  # the frozen loader must never be reached
        raise AssertionError("load_root was called")

    monkeypatch.setattr("ml_route_v2.phase1.world.load_root", boom)
    rec = {"s_x": date(2019, 5, 6), "store_sha256": "0" * 64}
    with pytest.raises(guard.GuardRefusal, match="not one of the 17 price paths"):
        W.load_search_root("ES", rec, step2_root=tmp_path, summaries_root=tmp_path, repo=tmp_path)
    with pytest.raises(guard.GuardRefusal, match="processed_hist"):
        W.load_search_root("NQ", rec, step2_root=Path(HIST_ROOT) / "ext2010",
                           summaries_root=tmp_path, repo=tmp_path)


def test_a_store_hash_is_refused_for_a_forbidden_path() -> None:
    from pattern_search import preflight as pf

    with pytest.raises(guard.GuardRefusal, match="refused to hash"):
        pf.guarded_sha256(_planted()["processed_hist ext2010"])


def test_every_pattern_search_module_imports_the_guard_first() -> None:
    script = ("import sys\nimport pattern_search.constants\n"
              "print('GUARD', 'pattern_search.guard' in sys.modules)")
    proc = subprocess.run([sys.executable, "-c", script], cwd=_repo(), capture_output=True,
                          text=True, timeout=120, check=False)
    assert "GUARD True" in proc.stdout, proc.stderr[-1000:]
    pkg = _repo() / "pattern_search"
    for f in sorted(pkg.glob("*.py")):
        if f.name in ("__init__.py", "__main__.py", "constants.py", "guard.py"):
            continue
        text = f.read_text()
        assert "from pattern_search import guard" in text or \
            "from pattern_search import constants as K, guard" in text or \
            "import guard" in text or "from pattern_search.run import main" in text, f.name
