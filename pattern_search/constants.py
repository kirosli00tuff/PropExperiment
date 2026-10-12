"""Every literal of the Stage E.20 Part C search (reports/stage_e20_plan.md; docs/prompts/
STAGE_E.20.md F1, F2, F3, F6, F7, F9). Nothing here is read from data.

The frozen v2 values (the grid, the clock, the normalization, the CPCV settings, the screen's
statistics) are not repeated here: pattern_search calls the frozen ml_route_v2 code, which reads
its own hashed constants. Only the plan's additions and the run discipline live in this file.
"""

from __future__ import annotations

from datetime import date
from types import MappingProxyType

# ------------------------------------------------------------------ universe (plan 1, F1) ----
# Vehicle -> price-path root, in the plan's cluster order (K1..K6); every key is a
# ml_route_v2.constants.UNIVERSE vehicle with that price path (checked by world.check_universe).
VEHICLE_PATHS = MappingProxyType({
    "MNQ": "NQ", "M2K": "RTY",
    "ZT": "ZT", "ZF": "ZF", "ZN": "ZN", "TN": "TN", "ZB": "ZB", "UB": "UB",
    "6E": "6E",
    "MCL": "CL", "NG": "NG",
    "MGC": "GC",
    "ZC": "ZC", "ZS": "ZS", "ZL": "ZL", "HE": "HE", "LE": "LE",
})
VEHICLES = tuple(VEHICLE_PATHS)
PATH_ROOTS = tuple(VEHICLE_PATHS.values())
N_VEHICLES = 17

# ------------------------------------------------------------------ windows (plan 2, F2) ----
SEARCH_FIRST = date(2019, 5, 6)  # the step 2 stores' first trade date (EARLIEST_S_X)
SEARCH_LAST = date(2024, 2, 29)  # TRAIN_LAST
FORBIDDEN_FROM = date(2024, 3, 1)  # no bar dated on or after it (F2, F3)
# E.12's recorded S_X per price path (reports/stage_e12_phase1_bars.json "roots" -> "s_x");
# the D4 rule is never rerun (plan 2). world.recorded_starts reads the file and checks it.
S_X_SOURCE_REL = "reports/stage_e12_phase1_bars.json"
STORE_MANIFEST_REL = "reports/stage_e17_run_manifest.json"  # "stores" -> root -> "step2"
STEP2_SUMMARIES_REL = "reports/step2"  # bars_<ROOT>.json: the degraded-day record
RELEASE_CALENDAR_REL = "reports/stage_e2b_release_calendar.json"
FROZEN_TABLES_REL = ("reports/stage_e2a_costs.json", "reports/stage_e2a_vehicle_sizes.json",
                     "reports/stage_e2a_vehicles.json", "reports/stage_e2a_epsilon.json")
EXPECTED_S_X = MappingProxyType({  # plan 2's statement of the recorded values, cross-checked
    **{p: date(2019, 5, 6) for p in PATH_ROOTS}, "ZF": date(2020, 10, 1),
    "ZT": date(2021, 10, 1)})

# ------------------------------------------------------------------ clock (plan 4) ----
T4_INDEX = 4
T4_MINUTES_BEFORE_F = 60  # t4 = F_X - 60 min (F6 addition 1)

# ------------------------------------------------------------------ features (plan 5) ----
KEPT_SIGNALS = (  # plan 5.1, in REGISTRY order (equal to the plan's listing order)
    "cp1_ret", "cp2_range", "cp2_brk", "cp3_clv",
    "k1_vwap_dist",
    "k2_auction_mto", "k2_auction_msince", "k2_monthend_msince",
    "k4_eiafade_move", "k4_ngpre_mto", "k4_ngpre_msince", "k4_ovr_ret", "k4_ovr_pct",
    "k5_ovr_ret", "k5_ovr_pct",
    "g01_ret30", "g02_ret60", "g03_ret120", "g04_ret_day", "g05_gap", "g06_rv60", "g07_range",
    "g08_prev_ret", "g09_vol_state", "g10_logvol30", "g11_t_index", "g12_dow",
    "g16_month_end",
    "g17_nq", "g17_zn", "g17_6e", "g17_cl", "g17_gc", "g17_zc",
)
N_KEPT = 34
ROD_RET = "rod_ret"
ROD_ABSRATIO = "rod_absratio"
ROD_SIGNALS = (ROD_RET, ROD_ABSRATIO)  # plan 5.2
ACCEPTED_PART_A = ()  # plan 5.3: none accepted
FEATURE_NAMES = (*KEPT_SIGNALS, *ROD_SIGNALS, *ACCEPTED_PART_A)  # 36
ROD_MEDIAN_DATES = 60  # rod_absratio: the median over the previous 60 eligible row dates
UNAVAILABLE_ROOTS = MappingProxyType({"MES": "not loaded in E.20 (plan 6: MES is never opened)"})

# ------------------------------------------------------------------ the grid (plan 7, F9) ----
N_CONFIGS = 45
REGISTRY_LABEL = "E20S"  # the registry allows no hyphen in a label (plan 7, as E20H6)
CONFIG_IDS = tuple(f"{REGISTRY_LABEL}-{n:02d}" for n in range(1, N_CONFIGS + 1))

# ------------------------------------------------------------------ screen (plan 9, F7) ----
SCREEN_MEDIAN_T_MIN = 2.0  # item 1: >= 2.0
SCREEN_PBO_MAX = 0.5  # item 2: < 0.5
SCREEN_SHARPE_MIN = 0.5  # item 3: >= 0.5
SCREEN_SHARPE_MAX = 4.0  # item 3: <= 4.0; above is a leakage alarm (fails as written)
N_TRIALS_BEFORE = 483  # the registry's N after H6 (plan 11)
N_TOTAL_AT_SCREEN = 528  # 483 + 45: the DSR's N, passed explicitly (plan 9)
MIN_ROUND_TRIPS_PER_PRODUCT = 30  # V2.9 criterion 6 (reported, flagged)
SLIPPAGE_STRESS = 1.5  # the 1.5 x slippage re-pricing (reported)
PASS, FAIL = "PASS", "FAIL"

# ------------------------------------------------------------------ run discipline ----
HARNESS_SHA256 = "ece91ae8e6993ad3c64412d30cc0b6ff6a4af07a15a6956ce9f2927f7ea70d32"  # harness v12
V2_FREEZE_REL = "reports/stage_e12_ml_v2_freeze.json"
V2_FREEZE_SHA256 = "a647cd06c8f71f9549c0afa1c740bc32bad05e8f83ed57c87642a1586a0cad5b"
PLAN_REL = "reports/stage_e20_plan.md"
FREEZE_MANIFEST_REL = "reports/stage_e20_search_freeze.json"
FREEZE_SCHEMA = "stage_e20_search_freeze/1"
CODE_PACKAGE = "pattern_search"
TEST_GLOB = "test_pattern_search*.py"
TEST_HELPERS = ("tests/_pattern_search_synth.py",)
STATE_DIR_NAME = ".cache/propexp_e20_search"  # under the home directory, never E.12's
REPORTS_SUBDIR_REL = "reports/stage_e20_search"
RESULT_JSON_REL = "reports/stage_e20_search.json"
RESULT_MD_REL = "reports/stage_e20_search.md"
RESULT_SCHEMA = "stage_e20_search_result/1"
RC_OK, RC_ERROR, RC_REFUSED = 0, 1, 2

# ------------------------------------------------------------------ backward (plan 2, 3) ----
B1_LABEL = "E20B1"
B1_TEST_ID = "E20B1-T1"
B1_MARKER_REL = "reports/stage_e20_B1_RUN_ONCE.json"


def config_ids() -> dict[str, str]:
    """{registry id E20S-nn: frozen config_id} with E20S-nn = configs.CONFIGS[nn - 1] (plan 7)."""
    from ml_route_v2.configs import CONFIGS

    if len(CONFIGS) != N_CONFIGS:
        raise ValueError(f"the frozen grid has {len(CONFIGS)} configurations, not {N_CONFIGS}")
    return {rid: c.config_id for rid, c in zip(CONFIG_IDS, CONFIGS, strict=True)}
