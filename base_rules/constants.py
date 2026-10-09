"""Every parameter of Stage E.16's base-rule tests H1..H5 (reports/stage_e16_briefs/lead_spec.md).

Each value names its source: the stage prompt (docs/prompts/STAGE_E.16.md), the lead's spec
(sections 0-6, the user rulings U1-U3), or a frozen file. Paths are relative to the repository
root; the pinned sha256s are filled by the freeze (Task 4) in reports/stage_e16_freeze.json, never
here, so the code that is hashed into the freeze does not change when the freeze is written.
"""

from __future__ import annotations

from datetime import date, time
from fractions import Fraction
from pathlib import Path
from types import MappingProxyType

from data.calendars import GROUP_OF_PRODUCT
from data.config import REPO_ROOT

# ------------------------------------------------------------------ the tests ----
TESTS = ("H1", "H2", "H3", "H4", "H5")
REGISTRY_TEST = "E16"  # ruling R-B4: the trial-registry label, fixed (no run-time override)
TEST_IDS = MappingProxyType({t: f"{REGISTRY_TEST}-{t}" for t in TESTS})
INTRADAY_TESTS = ("H1", "H4")
MULTIDAY_TESTS = ("H2", "H3")

# ------------------------------------------------------------------ universe (E.12, D2) ----
# The 27 price paths of E.12 (MBT excluded, prompt "Universe"); vehicle per path, as
# ml_route_v2.constants.UNIVERSE (a test pins the equality).
PRODUCTS = ("NQ", "RTY", "YM", "ZT", "ZF", "ZN", "TN", "ZB", "UB", "6E", "6A", "6B", "6C", "6J",
            "6S", "6N", "CL", "NG", "GC", "HG", "ZC", "ZW", "ZS", "ZM", "ZL", "HE", "LE")
VEHICLE_OF = MappingProxyType({p: {"NQ": "MNQ", "YM": "MYM", "RTY": "M2K", "CL": "MCL",
                                   "GC": "MGC", "HG": "MHG"}.get(p, p) for p in PRODUCTS})
GROUP_OF = MappingProxyType({p: GROUP_OF_PRODUCT[p] for p in PRODUCTS})
HIST_GROUPS_FROZEN = ("equity", "rates", "fx", "energy", "metals", "grains")
LIVESTOCK = "livestock"

# ------------------------------------------------------------------ windows (prompt, U2) ----
PROMPT_FIRST = date(2010, 6, 7)
WINDOW_LAST = date(2024, 2, 29)
DEFAULT_START = date(2010, 7, 1)  # 24 products: 2010-01..2010-06 unpriced
# U2: the first trade date ON OR AFTER these (reports/stage_e16_windows.json, the run's input)
START_EXCEPTIONS = MappingProxyType({"RTY": date(2017, 6, 1), "TN": date(2016, 1, 1),
                                     "HE": date(2017, 7, 1)})
WINDOW_START = MappingProxyType({p: START_EXCEPTIONS.get(p, DEFAULT_START) for p in PRODUCTS})
FALLBACK_FIRST = date(2019, 5, 6)  # prompt "Fallback, fixed now"
HIST_LAST = date(2019, 4, 30)  # the ext2010 stores' last trade date (data.pull_hist.EXT2010)
HIST_FIRST_MIN = date(2010, 6, 6)  # F-01: a hist store's named first trade date is on or after
# F-01 (lead ruling): the 2010-2019 store plan of each root is fixed. C1's frozen plan "ext2010"
# holds its six roots; the 21 others are bought by E.17 under plan "ext2010h".
PLAN_C1, PLAN_EXT = "ext2010", "ext2010h"
C1_ROOTS = ("NG", "NQ", "ZN", "6E", "GC", "ZC")
HIST_PLAN_OF = MappingProxyType({p: PLAN_C1 if p in C1_ROOTS else PLAN_EXT for p in PRODUCTS})
STEP2_FIRST = date(2019, 5, 6)  # the E.12 step 2 stores' first trade date (data.step2_store)
FROZEN_CAL_FIRST = date(2019, 5, 1)  # the 2019-on group calendars take over from this date
QUOTE_RECORD = "reports/stage_e12_quotes_ext2010.json"
QUOTE_SET = "ml-v2+extension-2010"

# ------------------------------------------------------------------ risk scaling (spec 3) ----
SIGMA_WINDOW = 20  # trailing g values
WARMUP_UNITS = 20  # first eligible units per product (leg, tenor): computed for g, never traded
H5_SIGMA_WINDOW = 60
H5_WARMUP = 60

# ------------------------------------------------------------------ statistics (spec 5) ----
NW_LAGS = MappingProxyType({"H1": 5, "H2": 1, "H3": 3, "H4": 5, "H5": 5})
YEAR_MIN_UNITS = MappingProxyType({"H1": 10, "H2": 6, "H3": 10, "H4": 10, "H5": 10})  # U3b
YEAR_POSITIVE_SHARE = Fraction(2, 3)
YEAR_MIN_QUALIFYING = 3  # fewer qualifying years: the criterion FAILS (not vacuous)
HOLM_ALPHA = 0.05
MIN_UNITS = 30
EXPECTED_N_AT_RUN = 478  # spec 5: "expected 478 if C1 registers first" (reported, never assumed)

# ------------------------------------------------------------------ costs (spec 1, U3a) ----
BASE, STRESS, SLIP150 = "base", "stress", "slip150"
COST_CASES = (BASE, STRESS, SLIP150)
STRESS_EXTRA_TICKS = 1  # per side, every fill
SLIPPAGE_MULTIPLE = Fraction(3, 2)  # the prompt's 1.5 x slippage case, commission unchanged
EVENT_MINUTES = 30  # D8 [release, release + 30 min)
GUARD_MINUTES = 2  # D9.5a [release, release + 2 min)

# ------------------------------------------------------------------ the rules (spec 4) ----
H1_WINDOW_MIN = 30  # entry S - 30, signal close of S - 31, exit S
TOPSTEP_FLATTEN_CT = time(15, 8)  # S > 15:08 CT product-dates are counted for the lead
H2_EQUITY, H2_BOND = "NQ", "ZN"
H2_LEGS = (H2_EQUITY, H2_BOND)
H2_D5_FROM_END = 5  # the month's fifth-last trading day
H3_TENOR_ROOT = MappingProxyType({"2Y": "ZT", "5Y": "ZF", "10Y": "ZN", "30Y": "ZB"})
H3_TENOR_TERM = MappingProxyType({"2Y": "2-Year", "5Y": "5-Year", "10Y": "10-Year",
                                  "30Y": "30-Year"})
H3_BEFORE = 3  # short at t - 3
H3_AFTER = 5  # exit at t + 5
AUCTION_RELEASE = "TREASURY_AUCTION"
H5_COMPONENTS = ("H1", "H2", "H3", "H4")

# ------------------------------------------------------------------ settlement table ----
SETTLEMENT_SCHEMA = "stage_e16_settlement/1"
SETTLEMENT_GRADES = ("primary", "secondary", "weak", "unsourced")
LEAD_GRADES = ("primary", "secondary", "weak", "none")  # settle periods' "lead_grade"
SETTLEMENT_GRADES_OK = ("primary", "secondary")  # H1/H4 need a LEAD grade in these (d and d - 1)
# The lead's prior (prompt "Common definitions"): used ONLY for the provisional calendar-only
# counts when Task 1's table is not on disk; never by a runner.
PRIOR_SETTLE_CT = MappingProxyType({
    "equity": time(15, 0), "rates": time(14, 0), "fx": time(14, 0), "energy": time(13, 30),
    "gold": time(12, 30), "copper": time(12, 0), "grains": time(13, 15), "livestock": time(13, 0)})
SUBGROUP = MappingProxyType({"GC": "gold", "HG": "copper"})

# ------------------------------------------------------------------ input paths ----
SETTLEMENT_PATH = Path("reports/stage_e16_settlement.json")
WINDOWS_PATH = Path("reports/stage_e16_windows.json")
WINDOWS_SCHEMA = "stage_e16_windows/1"
ECAUC_HIST_PATH = Path("reports/stage_e16_calendars/ec_auc_2010_2019.json")
# F-04: the announcement dates of the frozen 2019-05..2024-02 TREASURY_AUCTION rows
ANNOUNCEMENTS_PATH = Path("reports/stage_e16_calendars/ec_auc_announcements_2019_2024.json")
ANNOUNCEMENTS_SCHEMA = "stage_e16_ec_auc_announcements/1"
LIVESTOCK_HIST_PATH = Path("reports/stage_e16_calendars/hist2010_livestock.json")
RELEASE_FROZEN_PATH = Path("reports/stage_e2b_release_calendar.json")  # D8, from 2019-05
RELEASE_HIST_PATH = Path("reports/stage_e14_cal_releases.json")  # FOMC, NGS, WPSR 2010-2019
HIST_CALENDAR_DIR = Path("data/calendars/hist2010")
FREEZE_PATH = Path("reports/stage_e16_freeze.json")
OUT_DIR = Path("reports/stage_e17_runs")
REGISTRY_PATH = Path("ledger/trial_registrations.jsonl")
FREEZE_SCHEMA = "stage_e16_freeze/1"
RUN_MANIFEST_SCHEMA = "stage_e16_run_manifest/1"
RESULT_SCHEMA = "stage_e16_base_rules_result/1"
MARKER_SCHEMA = "stage_e16_base_rules_run_once/1"
VERDICT_SCHEMA = "stage_e16_base_rules_verdict/1"
CODE_DIR = Path(__file__).resolve().parent
RC_OK, RC_STOPPED, RC_REFUSED = 0, 1, 2


def repo_path(rel: Path | str) -> Path:
    """An input path: absolute as given, else under the repository root."""
    p = Path(rel)
    return p if p.is_absolute() else REPO_ROOT / p


__all__ = [n for n in dir() if n.isupper()] + ["repo_path"]
