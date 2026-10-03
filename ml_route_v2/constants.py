"""Constants of ML route v2 (docs/STAGE_E_ML_V2_DESIGN.md, DRAFT, Stage E.11).

Every value here is a literal from the v2 design draft (section given beside it). None is read from
an argument or an environment variable. The draft is not frozen: the freeze session applies the
user's decisions (V2.12) by editing this file, and its freeze manifest then hashes it.
"""

from __future__ import annotations

from datetime import date, time
from types import MappingProxyType

# ---- V2.1 windows (v1 M1 kept) -----------------------------------------------------------
EARLIEST_S_X = date(2019, 5, 6)
TRAIN_LAST = date(2024, 2, 29)
FORBIDDEN_FROM = date(2024, 3, 1)  # embargo, holdout-2 and everything later: never in a fit
HOLDOUT_2 = (date(2024, 4, 1), date(2025, 3, 31))
RESEARCH_WINDOW = (date(2025, 4, 1), date(2026, 6, 19))

# ---- V2.1 universe: exposure vehicle -> (cluster, price-path root) -------------------------
UNIVERSE = MappingProxyType({
    "MNQ": ("K1", "NQ"), "M2K": ("K1", "RTY"), "MYM": ("K1", "YM"),
    "ZT": ("K2", "ZT"), "ZF": ("K2", "ZF"), "ZN": ("K2", "ZN"), "TN": ("K2", "TN"),
    "ZB": ("K2", "ZB"), "UB": ("K2", "UB"),
    "6E": ("K3", "6E"), "6A": ("K3", "6A"), "6B": ("K3", "6B"), "6C": ("K3", "6C"),
    "6J": ("K3", "6J"), "6S": ("K3", "6S"), "6N": ("K3", "6N"),
    "MCL": ("K4", "CL"), "NG": ("K4", "NG"),
    "MGC": ("K5", "GC"), "MHG": ("K5", "HG"),
    "ZC": ("K6", "ZC"), "ZW": ("K6", "ZW"), "ZS": ("K6", "ZS"), "ZM": ("K6", "ZM"),
    "ZL": ("K6", "ZL"), "HE": ("K6", "HE"), "LE": ("K6", "LE"),
    "MBT": ("K7", "MBT"),
})
CLUSTERS = ("K1", "K2", "K3", "K4", "K5", "K6", "K7")
# G17 cross-product leads (price-path roots), plus MES as a signal-only root (V2.3)
CLUSTER_LEADS = MappingProxyType({"K1": "NQ", "K2": "ZN", "K3": "6E", "K4": "CL", "K5": "GC",
                                  "K6": "ZC", "K7": "MBT"})
SIGNAL_ONLY_ROOTS = ("MES",)

# ---- V2.2 decision clock -----------------------------------------------------------------
DECISION_STEP_MIN = 30
FIRST_DECISION_OFFSET_MIN = 30  # t1 = O_X + 30 min
N_DECISION_TIMES = 3
HORIZONS = ("h60", "h120", "hF")  # 60 min, 120 min, to the forced flatten
HORIZON_MINUTES = MappingProxyType({"h60": 60, "h120": 120, "hF": None})
LONGEST_FIXED_HORIZON_MIN = 120  # t3 is the latest O_X + 30k with t3 + 120 <= F_X
MAX_ENTRIES_PER_PRODUCT_DAY = 3
# The table the rule must reproduce (CT), pinned by a test (V2.2)
DECISION_TIMES_CT = MappingProxyType({
    "equity": (time(9, 0), time(11, 0), time(13, 0)),
    "crypto": (time(9, 0), time(11, 0), time(13, 0)),
    "rates": (time(7, 50), time(10, 20), time(12, 50)),
    "fx": (time(7, 50), time(10, 20), time(12, 50)),
    "energy": (time(8, 30), time(10, 30), time(13, 0)),
    "gold": (time(7, 50), time(10, 20), time(12, 50)),
    "copper": (time(7, 40), time(10, 10), time(12, 40)),
    "grains": (time(9, 0), time(10, 0), time(11, 0)),
    "livestock": (time(9, 0), time(10, 0), time(11, 0)),
})
C_SIGMA_TAU = 0.10  # V2.2 c/sigma filter

# ---- V2.4 normalization ------------------------------------------------------------------
Z_WINDOW_DATES = 250
Z_MIN_DATES = 60
Z_CLIP = 5.0
SIGMA_D_DATES = 20  # sigma_X,d (v1 ML-A06)

# ---- V2.2b Gate 0 (parameters fixed at freeze) ----------------------------------------------
GATE0_COST_MULTIPLE = 1.5
GATE0_T_MIN = 3.0
GATE0_FAMILY_ALPHA = 0.05
GATE0_TOP_FRACTION = 0.20
GATE0_MIN_TRADES = 30
GATE0_HOLM_INCLUDES_FAMILY_A = True
GATE0_RIDGE_LAMBDA = 0.1

# ---- V2.6 models -------------------------------------------------------------------------
SEED = 20261003
RIDGE_LAMBDAS = (0.01, 0.1, 1.0)  # alpha = lambda x n_train
LGBM_DEPTHS = (2, 3)
LGBM_FIXED = MappingProxyType({
    "objective": "regression", "min_data_in_leaf": 2000, "lambda_l2": 100.0,
    "learning_rate": 0.02, "num_boost_round": 300, "feature_fraction": 0.7,
    "bagging_fraction": 0.7, "bagging_freq": 1, "deterministic": True, "force_col_wise": True,
    "num_threads": 8, "verbosity": -1,
})

# ---- V2.7 decision layer -----------------------------------------------------------------
COST_GATE_KS = (1.5, 2.0, 3.0)  # trade iff |r_hat| - c > k c (literal F7 reading)
N_CONFIGURATIONS = (len(RIDGE_LAMBDAS) + len(LGBM_DEPTHS)) * len(COST_GATE_KS) * len(HORIZONS)
# V2.7: 'net' = literal F7 (|r_hat| - c > k c); 'gross' = |r_hat| > k c;
# the user decides (V2.12 item 1)
COST_GATE_READING = "net"

# ---- V2.8 sizing, portfolio, kill switches -------------------------------------------------
DAILY_SIGMA_FRACTION = 0.10  # sigma_target = 0.10 x D_open
TRADE_LOSS_FRACTION = 0.25  # n x (L + c) x tick value <= 0.25 x D_now
RISK_SPLIT_M = 3  # b = sigma_target / sqrt(m)
# n_risk 0 -> 1 when one contract's h-sigma $ <= 2 b (D2's band upper end)
RISK_ROUND_UP_RATIO = 2.0
LOSS_QUANTILE = 0.99  # L(p,h)
MAX_OPEN_POSITIONS = 3
MAX_OPEN_PER_CLUSTER = 1
PER_PRODUCT_LOT_EQUIVALENTS = 1.0  # D9.5
PORTFOLIO_TIER_MARGIN_LOTS = 0.1  # portfolio <= tier max - 0.1 lot
KS1_DAILY_LOSS_FRACTION = 0.30  # of D_open
KS2_HALF_SIZE_BELOW = 0.50  # of MLL
KS2_SIZE_MULTIPLIER = 0.5
KS2B_HALT_BELOW = 0.25  # of MLL
KS3_LOSING_DATES = 5
KS4_WINDOW_DATES = 40
KS4_SE_MULTIPLE = 3.0
KS5_STALE_ENTRY_MIN = 2
KS5_STALE_FLATTEN_MIN = 5
# V2.8 (design review D-08a): each contract beyond D2's q_c pays one extra tick per side
BEYOND_QC_EXTRA_TICKS_PER_SIDE = 1.0

# ---- V2.9 evaluation ---------------------------------------------------------------------
N_BLOCKS = 6
N_TEST_BLOCKS = 2  # outer CPCV: 15 splits, 5 paths
EMBARGO_DATES = 1
MIN_TRADES = 30  # V18, V21
PBO_BLOCKS = 16
N_PROGRAM_AT_DRAFT = 198  # cumulative N after E.9 (E.10 screened nothing, V21); freeze re-reads it
VERDICT_T_MIN = 3.0
VERDICT_DSR_MIN = 0.95
VERDICT_PBO_MAX = 0.5
VERDICT_SHARPE_MIN = 1.5
LEAKAGE_ALARM_SHARPE = 4.0
VERDICT_RUIN_MAX = 0.10
RESEARCH_T_MIN = 1.0
HOLM_K = 10  # V21
PAYOUT_PATHS = 10_000
PAYOUT_HORIZON_DATES = 252
PAYOUT_BLOCK_MEAN = 10
N_COPIED_ACCOUNTS = 5  # one draw (F11)
# V2.0 table "/month (21 d)"; monthly payouts = path total / (252/21) (Task 4)
TRADE_DATES_PER_MONTH = 21
# V2.9: a new Combine's delay after a breach, open; the freeze fills it (Task 4)
PAYOUT_RESET_DELAY_DATES = 0
# V2.9 payout policy: keep D >= 0.5 x MLL after a payout (KS2 threshold), lead ruling 2026-10-03
PAYOUT_KEEP_D_FRAC = 0.5
COST_SENSITIVITY_SLIPPAGE_MULTIPLE = 1.5  # V2.9 (design review D-08b): OOS at 1.5 x slippage

# ---- V2.3 generic feature literals (Task 2, SignalCoder) -----------------------------------
G_RETURN_MINUTES = (30, 60, 120)  # V2.3 G1-G3: returns over the last 30, 60 and 120 minutes
G6_RV_MINUTES = 60  # V2.3 G6: realized volatility of one-minute returns over the last 60 minutes
G_BASE_DATES = 20  # V2.3 G6 ("over its 20-date mean") and G10 (v1 F10's 20-date median)
G9_MEDIAN_DATES = 120  # V2.3 G9: sigma_X,d over its trailing 120-date median
G10_VOLUME_MINUTES = 30  # V2.3 G10: log volume ratio over the last 30 minutes
G16_MONTH_END_DATES = 2  # V2.3 G16: the last two trade dates of the month
G17_RETURN_MINUTES = 60  # V2.3 G17: the 60-minute return of each other cluster's lead
G17_LOG_RETURN_SCALE = 1e4  # V2.3 G17 unit: log return in basis points (Task 2 reading SG-1)
