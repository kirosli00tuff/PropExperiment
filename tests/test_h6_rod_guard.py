"""h6_rod.guard (F3, prereg section 9): every planted case raises. No store is opened: the path
check refuses before anything is opened, and the audit hook refuses at the open call itself (in a
subprocess, so this test process never carries the irreversible hook)."""

from __future__ import annotations

import subprocess
import sys
from datetime import date

import pandas as pd
import pytest

from h6_rod import guard
from h6_rod.guard import GuardRefusal
from tests._h6_rod_synth import day_frame, ts_ns


def _repo():
    from data.config import REPO_ROOT

    return REPO_ROOT


def _planted() -> dict[str, object]:
    from data import holdout as ho
    from data.config import REPO_ROOT

    return {
        "hist": REPO_ROOT / "data/processed_hist/ext2010/NQ/x.parquet",
        "sealed": REPO_ROOT / "data/sealed/anything.sealed",
        "holdout1_blob": ho.DEFAULT_PATHS.holdout_blob,
        "holdout2_root": ho.HOLDOUT2_PATHS.sealed_root / "raw" / "x.sealed",
        "mes_research": ho.DEFAULT_PATHS.research_parquet,
        "mes_confirmation": ho.HOLDOUT2_PATHS.research_parquet,
        "other_root_step2": REPO_ROOT / "data/processed_step2/ES/x_step2.parquet",
        "other_root_research": REPO_ROOT / "data/processed/NQ/x_research.parquet",
        "vendor_raw": REPO_ROOT / "data/vendor/databento/x.dbn.zst",
    }


# ------------------------------------------------------------------ (a) the path check ----
@pytest.mark.parametrize("case", list(_planted()))
def test_the_store_path_check_refuses_every_forbidden_path(case: str) -> None:
    with pytest.raises(GuardRefusal, match="H6 guard"):
        guard.check_store_path(_planted()[case])


def test_the_path_check_names_the_forbidden_class() -> None:
    planted = _planted()
    assert "processed_hist" in guard.refusal_reason(planted["hist"])
    assert "sealed or holdout" in guard.refusal_reason(planted["sealed"])
    assert "sealed or holdout" in guard.refusal_reason(planted["mes_confirmation"])
    assert "another store" in guard.refusal_reason(planted["other_root_step2"])


def test_a_path_outside_every_store_root_is_still_not_the_nq_store(tmp_path) -> None:
    with pytest.raises(GuardRefusal, match="not the NQ step 2 store"):
        guard.check_store_path(tmp_path / "copy_of_nq.parquet")


def test_only_the_nq_step2_file_passes_and_nothing_is_opened() -> None:
    nq = guard.nq_store_path()
    assert nq.as_posix().endswith(
        "data/processed_step2/NQ/ohlcv-1m_NQ_v_0_2019-05-06_2024-02-29_step2.parquet")
    assert guard.check_store_path(nq) == nq
    assert guard.refusal_reason(nq) is None


def test_a_symlink_to_a_forbidden_store_is_refused(tmp_path) -> None:
    link = tmp_path / "nq.parquet"
    link.symlink_to(_planted()["sealed"])
    with pytest.raises(GuardRefusal):
        guard.check_store_path(link)
    assert guard.refusal_reason(link) is not None


# ------------------------------------------------------------------ (b) the audit hook ----
def test_audit_decision_refuses_opens_of_forbidden_prefixes() -> None:
    prefixes = guard.forbidden_prefixes()
    allowed = str(guard.nq_store_path())
    for path in _planted().values():
        assert guard.audit_decision("open", (str(path), "r", 0), allowed=allowed,
                                    prefixes=prefixes) is not None
        assert guard.audit_decision("os.open", (str(path), "r", 0), allowed=allowed,
                                    prefixes=prefixes) is not None
    assert guard.audit_decision("open", (allowed, "rb", 0), allowed=allowed,
                                prefixes=prefixes) is None
    assert guard.audit_decision("open", (str(_repo() / "pyproject.toml"), "r", 0),
                                allowed=allowed, prefixes=prefixes) is None
    assert guard.audit_decision("open", (3, "r", 0), allowed=allowed, prefixes=prefixes) is None
    assert guard.audit_decision("exec", ("x",), allowed=allowed, prefixes=prefixes) is None


_HOOK_SCRIPT = """
import io, os, sys
from h6_rod import guard
assert guard.install_audit_hook() and not guard.install_audit_hook()
with open(os.path.join({repo!r}, "pyproject.toml")) as fh:
    fh.read(1)
refused = []
for path in {paths!r}:
    for opener in (lambda p: open(p, "rb"), lambda p: os.open(p, os.O_RDONLY),
                   lambda p: io.open_code(p)):
        try:
            opener(path)
        except guard.GuardRefusal as exc:
            refused.append("H6 guard" in str(exc))
        except OSError:
            refused.append(False)
print("REFUSED", sum(refused), len(refused))
"""


def test_the_audit_hook_refuses_python_level_opens_in_a_cli_like_process() -> None:
    paths = [str(p) for p in _planted().values()]
    script = _HOOK_SCRIPT.format(repo=str(_repo()), paths=paths)
    proc = subprocess.run([sys.executable, "-c", script], cwd=_repo(), capture_output=True,
                          text=True, timeout=120, check=False)
    assert proc.returncode == 0, proc.stderr[-2000:]
    n = 3 * len(paths)
    assert f"REFUSED {n} {n}" in proc.stdout


# ------------------------------------------------------------------ (c) the bars ----
def _frame(day: date) -> pd.DataFrame:
    return pd.DataFrame(day_frame(day, start=(14, 0), end=(14, 5)))


def test_bars_dated_before_march_2024_pass() -> None:
    guard.check_bars(_frame(date(2024, 2, 29)))
    guard.check_trade_dates([date(2024, 2, 29), "2024-02-28"])


def test_a_bar_with_trade_date_march_1_2024_raises() -> None:
    bars = _frame(date(2024, 2, 29))
    bars.loc[bars.index[-1], "trade_date"] = "2024-03-01"
    with pytest.raises(GuardRefusal, match="2024-03-01"):
        guard.check_bars(bars)
    with pytest.raises(GuardRefusal):
        guard.check_trade_dates([date(2024, 3, 1)])


def test_a_bar_opening_on_or_after_march_1_2024_utc_raises_whatever_its_label() -> None:
    bars = _frame(date(2024, 2, 29))
    bars.loc[bars.index[-1], "ts_event"] = ts_ns(date(2024, 2, 29), 18, 0)  # 00:00 UTC Mar 1
    with pytest.raises(GuardRefusal, match="00:00 UTC"):
        guard.check_bars(bars)


def test_the_guard_is_imported_by_every_h6_rod_module() -> None:
    import h6_rod

    assert h6_rod.guard is guard
