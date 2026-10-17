"""Every parameter of Stage E.23's trigger-hold books (reports/stage_e23_briefs/lead_spec.md,
sections cited). E.21's frozen values are imported from multiday.constants, never copied."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from types import MappingProxyType

from multiday import constants as MK

# ------------------------------------------------------------------ registry (section 8) ----
REGISTRY_TEST = "E23"
N_BEFORE = 533  # P2.5: N 533 -> 533 + K

# ------------------------------------------------------------------ universe, windows (0, 1) ----
ROOTS = MK.ROOTS
HOLDS = (5, 20)  # P2.1: h in {5, 20} mark dates
W_EXT, W_CF = "W_ext", "W_cf"
WINDOW_NAMES = (W_EXT, W_CF)
W_EXT_FIRST = date(2011, 7, 27)  # the first date of the E.21 T1/T2 series
W_EXT_LAST = MK.HIST_LAST  # 2019-04-30
W_CF_FIRST = MK.STEP2_FIRST  # 2019-05-06
W_CF_LAST = MK.WINDOW_LAST  # 2024-02-29
DIRECTIONS = (1, -1)  # m: +1 the member's side, -1 the opposite side (section 2)

# ------------------------------------------------------------------ sizing (section 3) ----
TARGET_VOL = MK.TARGET_VOL  # 0.40, the E.21 T1 per-root formula, no divisor

# ------------------------------------------------------------------ costs (section 0) ----
BASE = MK.BASE
STRESS = MK.STRESS  # E.23's stress (commission + 2 x one-side slippage), NOT base_rules' +1 tick
CASES = (BASE, STRESS)
STRESS_SLIPPAGE_MULTIPLE = 2

# ------------------------------------------------------------------ statistics (4, 7) ----
SHARPE_ANNUALIZATION = 252
HOLM_ALPHA = 0.05  # one-sided, step-down
T_BAR = 2.0  # alpha t_NW >= 2.0
SHARPE_BAR = 0.3  # base net Sharpe >= 0.3
MAX_SURVIVORS = 4
DSR_MIN = 0.95
PBO_MAX = 0.5
PBO_BLOCKS = 8

# ------------------------------------------------------------------ power (section 5) ----
POWER_TRUE_SHARPE = 0.5
POWER_MIN = 0.2
MIN_NONOVERLAP = 30

# ------------------------------------------------------------------ verdicts (section 7) ----
PASS, NULL = "PASS", "NULL"
INCONCLUSIVE = "INCONCLUSIVE BY DESIGN"
UNCONFIRMABLE = "UNCONFIRMABLE ON OWNED DATA"

# ------------------------------------------------------------------ paths and schemas ----
SPEC_PATH = Path("reports/stage_e23_briefs/lead_spec.md")
PREREG_PATH = Path("reports/stage_e23_prereg.md")
CONFIG_PATH = Path("reports/stage_e23_registration.json")
POWER_PATH = Path("reports/stage_e23_power.json")
FREEZE_PATH = Path("reports/stage_e23_freeze.json")
EVENTS_DIR = Path("reports/stage_e23_events")
TREND_DIR = Path("reports/stage_e23_trend_per_root")
RUNS_DIR = Path("reports/stage_e23_runs")
OUT_DIRS = MappingProxyType({"discovery": RUNS_DIR / "discovery",
                             "confirmation": RUNS_DIR / "confirmation"})
MARKERS = MappingProxyType({"discovery": Path("reports/stage_e23_RUN_ONCE_discovery.json"),
                            "confirmation": Path("reports/stage_e23_RUN_ONCE_confirmation.json")})
E21_RESULTS = MappingProxyType({"T1": Path("reports/stage_e21_runs/T1_result.json"),
                                "T2": Path("reports/stage_e21_runs/T2_result.json"),
                                "T3": Path("reports/stage_e21_runs/T3_result.json")})
E21_FREEZE_PATH = MK.FREEZE_PATH
RUN_MANIFEST_PATH = MK.RUN_MANIFEST_PATH
REGISTRY_PATH = MK.REGISTRY_PATH
CODE_DIR = Path(__file__).resolve().parent
TEST_GLOB = "tests/test_trigger_hold_*.py"
CONFIG_SCHEMA = "stage_e23_registration/1"
FREEZE_SCHEMA = "stage_e23_freeze/1"
TREND_SCHEMA = "stage_e23_trend_per_root/1"
POWER_SCHEMA = "stage_e23_power/1"
MARKER_SCHEMA = "stage_e23_run_once/1"
RESULT_SCHEMA = "stage_e23_result/1"
TREND_CHECK_TOL = 1e-12
RC_OK, RC_STOPPED, RC_REFUSED = MK.RC_OK, MK.RC_STOPPED, MK.RC_REFUSED

repo_path = MK.repo_path

__all__ = [n for n in dir() if n.isupper()] + ["repo_path"]
