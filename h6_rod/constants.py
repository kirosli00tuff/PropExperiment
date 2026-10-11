"""Every literal of test H6 (reports/stage_e20_prereg_H6.md; docs/prompts/STAGE_E.20.md F2, F3, F5).

Nothing here is read from data. Three values are the lead's to set before the freeze, and every
entry point refuses while any of them is None (h6_rod.preflight.lead_settings):
- ``T3_REGISTERED``: True or False, from prereg section 7 (the NQ reader's GEX terms ruling);
- ``GEX_CSV_SHA256``: the GEX CSV's sha256 (only read when T3 is registered);
- ``ENGINE_LEAD_IN_DATES``: 0 or 1, an open item of the build (reports/stage_e20_briefs/
  h6_build.md, stop item S3): whether each engine run starts with the trade date before its
  window's first date as a no-entry lead-in that gives the engine its D9.7 prior-settlement
  reference (1), or starts on the window's first date (0, whose entry the engine then refuses
  as engine_price_limit_reference_unavailable).
The registry label and ids are the prereg's (section 8). screening.trial_registry refuses them as
written (stop item S1); h6_rod.preflight.registry_names_valid makes every entry point refuse until
the lead fixes the text and these two constants.
"""

from __future__ import annotations

from datetime import date, time
from types import MappingProxyType

# ------------------------------------------------------------------ data (prereg section 2) ----
PRICE_ROOT = "NQ"  # the price path
VEHICLE = "MNQ"  # the traded vehicle, one lot (F5)
QUANTITY = 1
NQ_STORE_REL = ("data/processed_step2/NQ/"
                "ohlcv-1m_NQ_v_0_2019-05-06_2024-02-29_step2.parquet")
NQ_STORE_SHA256 = "08fae13f8747883944888f4e7a3dd695c974707df2af59a22ef9036816be30aa"
STORE_FIRST = date(2019, 5, 6)  # data.stage_e_bars.STEP2_FIRST_TRADE_DATE
STORE_LAST = date(2024, 2, 29)

# ------------------------------------------------------------------ windows (section 2) ----
VERDICT_FIRST = date(2020, 6, 1)
VERDICT_LAST = date(2024, 2, 29)
OVERLAP_FIRST = date(2019, 5, 6)  # descriptive only, never in the verdict
OVERLAP_LAST = date(2020, 5, 29)
FORBIDDEN_FROM = date(2024, 3, 1)  # no bar dated on or after it (F2, F3, section 9)
T2_WARMUP_TRADE_DATES = 60  # the 60 equity trade dates before VERDICT_FIRST
T2_LOOKBACK_ELIGIBLE = 60  # the median over the 60 most recent eligible dates before d

# ------------------------------------------------------------------ clock (section 3) ----
NORMAL_CLOSE_CT = time(15, 0)  # C on a normal day; checked against the frozen day_session_ct
SIGNAL_BAR_BEFORE_C_MIN = 31  # P(C-30): the bar opening at C-31 (also the entry decision bar)
PRIOR_BAR_BEFORE_C_MIN = 1  # P(prior C): the bar opening at the previous trade date's C-1
EXIT_BEFORE_C_MIN = 2  # the exit: the first present bar opening at or after C-2

# ------------------------------------------------------------------ reason codes (section 3) ----
# Eligibility, in the order the text lists them; the first that applies is recorded.
REASON_MISSING_SIGNAL_BAR = "missing_signal_bar"
REASON_MISSING_PRIOR_BAR = "missing_prior_bar"
REASON_INSTRUMENT_CHANGE = "instrument_change"
REASON_ZERO_SIGNAL = "zero_signal"
ELIGIBILITY_REASONS = (REASON_MISSING_SIGNAL_BAR, REASON_MISSING_PRIOR_BAR,
                       REASON_INSTRUMENT_CHANGE, REASON_ZERO_SIGNAL)
REASON_T2_WARMUP = "t2_warmup"  # section 2: fewer than 60 eligible dates in the allowed range
REASON_T2_NOT_ABOVE = "t2_not_above_median"  # |r_ROD| <= the median (section 3: strictly >)
REASON_GEX_MISSING = "gex_missing"  # section 3: no GEX row for the previous trade date
REASON_GEX_NOT_NEGATIVE = "gex_not_negative"  # GEX >= 0 (section 3: strictly negative)

# ------------------------------------------------------------------ statistic and bar (4, 5) ----
HOLM_ALPHA = 0.025
COST_MULTIPLE = 1.5  # mean gross per trade >= 1.5 x mean c
SHARPE_BAR = 0.5
ANNUALIZATION_DAYS = 252
MIN_TRADES = MappingProxyType({"T1": 100, "T2": 100, "T3": 30})
STRESS_SLIPPAGE_MULTIPLE = 1.5  # section 6, descriptive
BP_PER_UNIT = 10_000
B_TEST_HORIZON = "C-30..C-2"  # the label passed to gate0._b_test (no effect on t or p)
PASS, FAIL, STOPPED = "PASS", "FAIL", "STOPPED"
YEAR_BUCKETS = (  # section 6's per-year results, verdict window
    ("2020-06..12", date(2020, 6, 1), date(2020, 12, 31)),
    ("2021", date(2021, 1, 1), date(2021, 12, 31)),
    ("2022", date(2022, 1, 1), date(2022, 12, 31)),
    ("2023", date(2023, 1, 1), date(2023, 12, 31)),
    ("2024-01..02", date(2024, 1, 1), date(2024, 2, 29)),
)

# ------------------------------------------------------------------ registration (section 8) ----
# lead ruling S1: the registry allows no hyphen in a label (prompt names E20-H6, E20-H6-T1..T3)
REGISTRY_LABEL = "E20H6"
TEST_IDS = MappingProxyType({"T1": "E20H6-T1", "T2": "E20H6-T2", "T3": "E20H6-T3"})
T3_REGISTERED: bool | None = True  # lead: GEX source cleared (prereg section 7)

# ------------------------------------------------------------------ the engine (stop item S3) ----
# lead ruling S3: one prior trade date seeds the D9.7 reference; no entry on it
ENGINE_LEAD_IN_DATES: int | None = 1

# ------------------------------------------------------------------ GEX (T3 only) ----
GEX_CSV_REL = "reports/stage_e14_briefs/gex/DIX.csv"
# E.14 copy (prereg section 7)
GEX_CSV_SHA256: str | None = "51bef9ea5ee13af2f72b14f4198de57eeb865a36c1d3e244a3f64b3603e9ce62"
GEX_HEADER = ("date", "price", "dix", "gex")

# ------------------------------------------------------------------ run discipline ----
HARNESS_SHA256 = "ece91ae8e6993ad3c64412d30cc0b6ff6a4af07a15a6956ce9f2927f7ea70d32"  # harness v12
PREREG_REL = "reports/stage_e20_prereg_H6.md"
FREEZE_MANIFEST_REL = "reports/stage_e20_h6_freeze.json"
FREEZE_SCHEMA = "stage_e20_h6_freeze/1"
MARKER_REL = "reports/stage_e20_H6_RUN_ONCE.json"
MARKER_SCHEMA = "stage_e20_h6_run_once/1"
RESULT_JSON_REL = "reports/stage_e20_H6_result.json"
RESULT_MD_REL = "reports/stage_e20_H6_result.md"
RESULT_SCHEMA = "stage_e20_h6_result/1"
CODE_PACKAGE = "h6_rod"
RC_OK, RC_ERROR, RC_REFUSED = 0, 1, 2


def registered_tests() -> tuple[str, ...]:
    """("T1", "T2") or ("T1", "T2", "T3"); refuses while T3_REGISTERED is None."""
    if T3_REGISTERED is None:
        raise ValueError("T3_REGISTERED is None: the lead sets True or False before the freeze "
                         "(prereg section 7)")
    return ("T1", "T2", "T3") if T3_REGISTERED else ("T1", "T2")
