"""Every parameter of Stage E.21's multi-day tests E21-T1..T4 in one place.

Source of each value: docs/prompts/STAGE_E.21.md (FIXED DESIGN F1-F8) and the lead's code-level
spec reports/stage_e21_briefs/lead_spec.md (sections cited). A Step 1 amendment (lead_spec
section A) is a one-line change here plus its test. Paths are relative to the repository root.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path
from types import MappingProxyType

from base_rules import constants as BK

# ------------------------------------------------------------------ the tests (F4, F7) ----
REGISTRY_TEST = "E21"  # the trial-registry label, fixed (no run-time override)
TESTS = ("T1", "T2", "T3", "T4")
TEST_IDS = MappingProxyType({t: f"{REGISTRY_TEST}-{t}" for t in TESTS})
EXPECTED_N_AFTER = 532  # F7: N 528 -> 532 (reported beside the registry's own N)

# ------------------------------------------------------------------ universe and windows (F1) ----
ROOTS = ("NG", "NQ", "ZN", "6E", "GC", "ZC", "ZT", "ZF", "ZB", "UB", "TN", "CL", "ZL", "ZS",
         "RTY", "HE", "LE")
T3_ROOTS = ("NQ", "RTY")
# Lead ruling Q1 (2026-10-14 03:48): a root's window, for EVERY purpose (marks, S_M, references,
# T3), starts ON OR AFTER the latest of the windows file's date, the R-S4 sourced-listing date
# (the settlement table's minute is null before it) and R-S3's LE start (LE's 2010-06-07..
# 2014-12-14 span is excluded for every test).
LISTING_FIRST = MappingProxyType({"RTY": date(2017, 7, 10), "TN": date(2016, 1, 11)})  # R-S4
LE_FIRST = MappingProxyType({"LE": date(2014, 12, 15)})  # R-S3
WINDOW_START_FLOOR = MappingProxyType({**LISTING_FIRST, **LE_FIRST})
WINDOW_LAST = BK.WINDOW_LAST  # 2024-02-29
HIST_LAST = BK.HIST_LAST  # 2019-04-30, the ext2010 stores' last trade date
STEP2_FIRST = BK.STEP2_FIRST  # 2019-05-06, the step 2 stores' first trade date

# ------------------------------------------------------------------ volatility (F3, spec 2) ----
EWMA_COM = 60  # centre of mass in trade dates: delta / (1 - delta) = 60
EWMA_DELTA = EWMA_COM / (EWMA_COM + 1.0)  # 60/61
ANNUALIZATION = 261  # sigma^2 = 261 x the EWMA variance of daily returns
SIGMA_WARMUP_RETURNS = 60  # sigma(i, d) defined once 60 defined daily returns precede d
TARGET_VOL = 0.40  # annual risk target per root

# ------------------------------------------------------------------ dates (spec 3, 5) ----
REBALANCE_LAST_DATES = 6  # d* is the latest eligible among the month's last 6 trade dates
REFERENCE_LAST_DATES = 6  # ref(i, M, k): the latest usable among month M - k's last 6
LOOKBACKS = (1, 3, 12)  # months (T2 blend; T1 uses 12)
T1_LOOKBACK = 12
DIVISOR_LOOKBACK = 12  # S_M counts roots whose e(i, M - 12) lies inside their window
TOM_ENTRY_FROM_END = 2  # T3 enters at MK(day -2): the month's second-to-last trade date
TOM_EXIT_DAY = 3  # T3 exits at MK(day +3): the third trade date of month M + 1
# lead_spec A12: T3's days -2, -1, +1, +2, +3 are numbered on T3 trading days = the equity group
# calendar's trade dates that are not NYSE full-day closures (rules in signals.nyse_closures)
NYSE_JUNETEENTH_FIRST_YEAR = 2022
NYSE_SPECIAL_CLOSURES = (date(2012, 10, 29), date(2012, 10, 30), date(2018, 12, 5))
# spec 7 and 4: the April 2019 rebalance sets every target to 0 (store boundary; the May 2019
# rebalance reopens); the February 2024 rebalance sets every target to 0 (window end).
FLAT_MONTHS = ((2019, 4), (2024, 2))

# ------------------------------------------------------------------ statistics (F6, spec 9) ----
NW_LAGS = MappingProxyType({"T1": 21, "T2": 21, "T3": 5, "T4": 21})
HOLM_ALPHA = 0.025  # family-wise, over the four tests
SHARPE_BAR = 0.3  # annualized net Sharpe >= 0.3
SHARPE_ANNUALIZATION = 252  # mean / sd x sqrt(252)
BOOT_BLOCK = 21  # circular moving-block bootstrap, block length in series dates
BOOT_DRAWS = 10_000
BOOT_SEED = 20261014  # a fresh numpy.random.default_rng(BOOT_SEED) per test
BOOT_CHUNK = 500  # draws per vectorized chunk (memory only; the draws do not depend on it)
BOOT_PERCENTILES = (2.5, 97.5)

# ------------------------------------------------------------------ T4 (spec 6) ----
T4_SIGMA_WINDOW = 60  # trailing grid dates, sample std (ddof 1), strictly before d
T4_WARMUP = 60
T4_COMPONENTS = ("T2", "T3", "H2")
H2_RESULT_SHA256 = "a661cebc2ac041866dec16210f6a8983661984d0acc815822a8c5b7908152dff"

# ------------------------------------------------------------------ costs (F5, spec 7) ----
COST_CASES = BK.COST_CASES  # base, stress (+1 vehicle tick per side), slip150 (1.5 x slippage)
BASE, STRESS, SLIP150 = BK.BASE, BK.STRESS, BK.SLIP150

# ------------------------------------------------------------------ paths and schemas ----
SPEC_PATH = Path("reports/stage_e21_briefs/lead_spec.md")
PREREG_PATH = Path("reports/stage_e21_prereg.md")
FREEZE_PATH = Path("reports/stage_e21_freeze.json")
RUN_MANIFEST_PATH = Path("reports/stage_e17_run_manifest.json")
H2_RESULT_PATH = Path("reports/stage_e17_runs/H2_result.json")
OUT_DIR = Path("reports/stage_e21_runs")
MARKER_PATH = Path("reports/stage_e21_RUN_ONCE.json")
REGISTRY_PATH = BK.REGISTRY_PATH
COUNTS_JSON = Path("reports/stage_e21_briefs/calendar_counts.json")
COUNTS_MD = Path("reports/stage_e21_briefs/calendar_counts.md")
CODE_DIR = Path(__file__).resolve().parent
TEST_GLOB = "tests/test_multiday_*.py"
FREEZE_SCHEMA = "stage_e21_freeze/1"
RESULT_SCHEMA = "stage_e21_multiday_result/1"
MARKER_SCHEMA = "stage_e21_run_once/1"
VERDICT_SCHEMA = "stage_e21_verdict/1"
PER_ROOT_SCHEMA = "stage_e21_per_root/1"
COUNTS_SCHEMA = "stage_e21_calendar_counts/1"
# the input roles of lead_spec section 0: base_rules' E.16 inputs plus the E.17 run manifest and
# H2's result (T4)
EXTRA_INPUT_ROLES = MappingProxyType({"run_manifest": RUN_MANIFEST_PATH,
                                      "h2_result": H2_RESULT_PATH})
RC_OK, RC_STOPPED, RC_REFUSED = BK.RC_OK, BK.RC_STOPPED, BK.RC_REFUSED

repo_path = BK.repo_path

__all__ = [n for n in dir() if n.isupper()] + ["repo_path"]
