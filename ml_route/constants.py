"""Frozen constants of the Stage E ML route (docs/STAGE_E_ML_DESIGN.md, frozen by Stage E.2a).

Every value here is a literal from the frozen design (M1 to M8, with the E.2a rulings in its
brackets). None of them is read from an argument or an environment variable; a session that wants
a different value must change this file, which the harness manifest (M7.8) hashes.
"""

from __future__ import annotations

from datetime import date
from types import MappingProxyType

# ---- M1: the partition -------------------------------------------------------------------
EARLIEST_S_X = date(2019, 5, 6)  # D4: the earliest possible S_X
TRAIN_LAST = date(2024, 2, 29)  # the training window ends here (M1)
FORBIDDEN_FROM = date(2024, 3, 1)  # March 2024 embargo, holdout-2 and everything later (M7.4)
EMBARGO_MONTH = (date(2024, 3, 1), date(2024, 3, 31))
HOLDOUT_2 = (date(2024, 4, 1), date(2025, 3, 31))
RESEARCH_WINDOW = (date(2025, 4, 1), date(2026, 6, 19))

# ---- M2 / ML-A07: the 31 price-path contracts, clusters and F16 leads -----------------------
CLUSTERS: MappingProxyType[str, tuple[str, ...]] = MappingProxyType({
    "K1": ("NQ", "RTY", "YM"),
    "K2": ("ZT", "ZF", "ZN", "TN", "ZB", "UB"),
    "K3": ("6E", "6A", "6B", "6C", "6J", "6S", "6N"),
    "K4": ("CL", "NG", "RB", "HO"),
    "K5": ("GC", "SI", "HG"),
    "K6": ("ZC", "ZW", "ZS", "ZM", "ZL", "HE", "LE"),
    "K7": ("MBT",),
})
CLUSTER_IDS: tuple[str, ...] = tuple(CLUSTERS)
PRICE_PATH_CONTRACTS: tuple[str, ...] = tuple(p for ps in CLUSTERS.values() for p in ps)
CLUSTER_OF: MappingProxyType[str, str] = MappingProxyType(
    {p: k for k, ps in CLUSTERS.items() for p in ps})
LEAD_OF_CLUSTER: MappingProxyType[str, str] = MappingProxyType({
    "K1": "NQ", "K2": "ZN", "K3": "6E", "K4": "CL", "K5": "GC", "K6": "ZC", "K7": "MBT"})

# ---- M3: challengers and grids --------------------------------------------------------------
SEED = 20260924
HORIZONS: tuple[str, ...] = ("h30", "h120", "hF")  # 30 min, 120 min, to the flatten F_X
HORIZON_MINUTES: MappingProxyType[str, int | None] = MappingProxyType(
    {"h30": 30, "h120": 120, "hF": None})
LGBM_THREADS = 8  # M3 (V7: inside the overnight profile's 14-thread limit; the value stays 8)
LGBM_GRID_AXES = (("num_leaves", (7, 31)), ("min_data_in_leaf", (500, 2000)),
                  ("lambda_l2", (1.0, 10.0)))
LGBM_FIXED: MappingProxyType[str, object] = MappingProxyType({
    "objective": "regression",  # L2
    "learning_rate": 0.03,
    "num_boost_round": 400,  # no early stopping
    "feature_fraction": 0.8,
    "bagging_fraction": 0.8,
    "bagging_freq": 1,
    "max_depth": -1,
    "deterministic": True,
    "force_col_wise": True,  # ML-A26
    "num_threads": LGBM_THREADS,
    "seed": SEED,
    "bagging_seed": SEED,
    "feature_fraction_seed": SEED,
    "data_random_seed": SEED,
    "verbosity": -1,
})
LSTM_GRID_AXES = (("hidden", (16, 32)), ("lookback", (24, 72)))
LSTM_FIXED: MappingProxyType[str, object] = MappingProxyType({
    "layers": 1,
    "dropout": 0.2,
    "lr": 1e-3,  # Adam
    "epochs": 8,  # no early stopping
    "embedding_dim": 4,  # ML-A12
    "planned_batch": 512,  # M3; M8's A-1 rule may lower it to 256, 128 or 64
})
LSTM_BATCH_LADDER: tuple[int, ...] = (512, 256, 128, 64)  # M8 / A-1
VRAM_TOTAL_GB = 4.0  # the RTX 3050 Laptop GPU (M8)
VRAM_MIN_FREE_GB = 0.5  # M8
CUBLAS_WORKSPACE_CONFIG = ":4096:8"  # ML-A12
FIVE_MIN = 5  # the LSTM's clock-aligned bars (ML-A12)
TORCH_CPU_THREADS = 4  # harness constant (not a design value): the LSTM job's CPU threads for
# batch preparation, inside the 6-per-job limit of the E.2b rules

# ---- M4: decision times, features ------------------------------------------------------------
DECISION_SPACING_MIN = 30
MAX_DECISIONS_PER_DAY = 13
SIGMA_LOOKBACK_DATES = 20  # sigma_X,d and F10
F17_MEDIAN_DATES = 120
RETURN_LOOKBACKS_MIN: tuple[int, ...] = (5, 15, 30, 60, 120)  # F1-F5
LEAD_RETURN_MIN = 30  # F16
EVENT_GUARD_MIN = 2  # D9.5a
EVENT_COST_WINDOW_MIN = 30  # D8
MIN_HOLD_MIN = 2  # D9.3
FEATURES_DISTILLABLE: tuple[str, ...] = (
    "F1_ret5", "F2_ret15", "F3_ret30", "F4_ret60", "F5_ret120", "F6_ret_day", "F7_gap",
    "F8_clv_prev", "F9_range", "F10_logvol", "F11_min_since_open", "F12_dow",
    "F13_min_to_release", "F14_min_since_release", "F15_release_day", "F16_lead_ret30",
    "F17_vol_state")

# ---- M5: distillation ------------------------------------------------------------------------
N_BLOCKS = 6
CPCV_BLOCKS = (1, 2, 3, 4, 5)
CPCV_TEST_BLOCKS = 2  # 10 splits
PRETEST_BLOCK = 6
COST_STRESS = 1.5  # M4 / M5
SURROGATE_MAX_DEPTH = 2
SURROGATE_MIN_LEAF = 0.02
PRETEST_MIN_TRADES = 30
MAX_RULES_PER_CLUSTER = 2

# ---- Frozen E.2a tables (full sha256, as recorded in reports/stage_e2b_briefs/task1a_runner.md) --
COSTS_SHA256 = "f4360bb77272d0335485a9e01c0f6fc6ab99c47d52e640d95f9cd0397296df14"
VEHICLES_SHA256 = "1f1cafee4330961799f33d5493e640897cfa79827be98597dbaba23292e29913"
