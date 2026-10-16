"""The rule's constants with their sources (lead_spec_B.md S3, S4, S6, S8) and the builder of
forward/config_f1.json (E22-F1's frozen constants; written from the study, frozen by the lead).

CS = reports/stage_e22_briefs/carver_sources.md (CarverReader, 2026-10-16), whose IDs (C-DEF,
C-VOL, C-EWMAC, C-ROB, C-DM, P-NOV21, ...) name saved files under
reports/stage_e22_briefs/carver_pages/ with sha256s.
"""

from __future__ import annotations

import copy
from collections.abc import Mapping, Sequence
from typing import Any

from microbook.universe import MICROS, Micro, per_side_extension_cents

SPEEDS = ((8, 32), (16, 64), (32, 128), (64, 256))
SCALARS_PRODUCTION = {"8/32": 5.949404365193165, "16/64": 4.104172020369661,
                      "32/128": 2.786994330124792, "64/256": 1.9093945630747895}
SCALARS_BOOK = {"8/32": 5.3, "16/64": 3.75, "32/128": 2.65, "64/256": 1.87}


def v(value: Any, source: str) -> dict:
    return {"value": value, "source": source}


BASE: dict[str, Any] = {
    "ewmac": {
        "speeds": v([list(s) for s in SPEEDS],
                    "lead_spec_B S3.2; CS A2 (C-CH15:28-63 'Lfast: 8 Lslow: 32' ... 'Lfast: 64 Lslow: 256')"),
        "ewma_definition": v("pandas ewm(span=L, min_periods=1).mean()",
                             "CS A1 (C-EWMAC:120-124 'fast_ewma = price.ewm(span=Lfast, min_periods=1).mean()')"),
        "scalars": v(dict(SCALARS_PRODUCTION),
                     "lead ruling S8 B-R1; CS A6b (C-ROB:364-368 'momentum8: 5.949404365193165', "
                     "'momentum16: 4.104172020369661', 'momentum32: 2.786994330124792', "
                     "'momentum64: 1.9093945630747895')"),
        "denominator": v("the mixed daily price-difference vol (key 'vol')",
                         "lead ruling S8 B-R2; CS A3, A5 (C-DEF:112-119 'func: \"sysquant.estimators.vol.mixed_vol_calc\"')"),
    },
    "forecast_cap": v(20.0, "lead_spec_B S3.2-3; CS A8 (C-DEF:141 'forecast_cap: 20.0')"),
    "average_abs_forecast": v(10.0, "CS A7 (C-DEF:143 'average_absolute_forecast: 10.0')"),
    "vol": {
        "recent_span": v(35, "CS A5, A12 (C-DEF:116 'days: 35'; C-VOL:188 'ewm(adjust=True, span=days, min_periods=min_periods).std()')"),
        "min_periods": v(10, "CS A5 (C-DEF:117 'min_periods: 10')"),
        "slow_vol_years": v(10, "CS A12b (C-DEF:118 'slow_vol_years: 10')"),
        "business_days_per_year": v(256.0, "CS A12c (C-DATE:26 'BUSINESS_DAYS_IN_YEAR = 256.0'); slow span = years x 256 (C-VOL:170)"),
        "proportion_of_slow_vol": v(0.3, "lead_spec_B S3.4; CS A12b (C-DEF:119 'proportion_of_slow_vol: 0.3')"),
        "vol_abs_min": v(1e-10, "CS A12d (C-DEF:120 'vol_abs_min: 0.0000000001')"),
        "annualisation": v(16.0, "CS A12c (sqrt(256), C-DATE:27 'ROOT_BDAYS_INYEAR = BUSINESS_DAYS_IN_YEAR**0.5')"),
        "dollar_vol_definition": v("multiplier x 16 x daily price-difference vol",
                                   "lead ruling (coordinator message 2026-10-16): sigma_% := sigma(dP)/P"),
    },
    "vol_target": v(0.20, "lead_spec_B S3.5 (tau = 0.20, the stage prompt)"),
    "fdm": {
        "value": None, "correlation": None,
        "weights": v([0.25, 0.25, 0.25, 0.25], "lead_spec_B S3.3 (equal weight)"),
        "dm_max": v(2.5, "CS A9 (C-DM:76 'dm_max: float = 2.5')"),
        "floor_at_zero": v(True, "CS A9b (C-DEF:162 'floor_at_zero: True')"),
        "estimate": v("Pearson correlation of the four scaled, capped forecasts, weekly (W-FRI last), pooled "
                      "(stacked) over the 12 instruments' live dates 2010-07..2024-02, full span",
                      "lead_spec_B S3.3; weekly frequency from CS A9b (C-DEF:155 'frequency: \"W\"')"),
    },
    "idm": {
        "value": None, "correlation": None, "instruments": None,
        "dm_max": v(2.5, "CS A10 (C-DEF:253 'dm_max: 2.5')"),
        "floor_at_zero": v(True, "CS A10b (C-DEF:247 'floor_at_zero: True')"),
        "estimate": v("Pearson correlation of weekly (W-FRI sum) instrument subsystem returns (unrounded "
                      "position F/10 / annual $ vol, filled at the next settlement), pairwise complete, full span; "
                      "dates with fewer live instruments use the live sub-matrix",
                      "lead_spec_B S3.5; weekly frequency and subsystem returns from CS A10b (C-DEF:240, C-PORT:415)"),
    },
    "warmup_diffs": v(256, "MicroBookCoder choice (microbook/README.md): an instrument is live once 256 daily "
                           "differences exist (the slowest EWMAC span); not a Carver figure"),
    "simple_rounding": {
        "buffer_size": v(0.10, "lead ruling S8 B-R3; CS A13 (C-DEF:297 'buffer_size: 0.10'; P-NOV21 'a simple 10% of average position')"),
        "trade_to_edge": v(True, "CS A13 (C-DEF:298 'buffer_trade_to_edge: True'), A13b (C-ABS:197-208)"),
        "rounding": v("half away from zero", "lead ruling S8 B-R3 (posts silent; pysystemtrade rounds half to even)"),
    },
    "greedy": {
        "used_by_e22_f1": v(False, "lead ruling R-B7: E22-F1 rounds with 'simple_rounding'; the greedy is the "
                                   "study's comparison method only"),
        "shadow_cost": v(250.0, "lead ruling S8 B-R4; CS B.1 step 5 (P-NOV21 .txt:136-141 'Shadow cost 250')"),
        "te_buffer": v(0.0125, "lead ruling S8 B-R4; CS B.1 step 7 (P-NOV21 .txt:140-141 'Buffer size 0.0125'); not rescaled to tau 20%"),
        "start": v("zero", "CS B.1 step 4 (P-OCT21, P-NOV21 .txt:73 'the algo always starts at zero')"),
        "direction": v("sign of the unrounded optimum; sign(0) = +1", "CS B.1 step 4; B.2 (C-GEN:142-157 sign(0) = 1.0)"),
        "trade_rounding": v("half away from zero", "lead ruling S8 B-R3 (P-NOV21: 'And then round them, obviously.')"),
        "all_zero_result": v("accepted (no fallback to prior)", "MicroBookCoder choice: the post has no fallback; C-OPT:164-170's error fallback is code-only (CS B.3 D7)"),
        "cost_per_contract": v("the per-side cost of section 'costs' (USD, base case), undeflated",
                               "lead ruling S8 B-R4 (no end-of-sample look-ahead); the backtest charges the same undeflated cost"),
        "correlation": {
            "returns": v("percentage returns dP/P of the held contract (yield micros: yield changes)",
                         "CS B.2 (C-PORT:1117 get_daily_percentage_returns); yields per the lead's sigma ruling"),
            "return_days": v(7, "lead ruling S8 B-R5; CS B.2 (C-DEF:313 'frequency: \"7D\"'), windows ending on the decision date"),
            "ew_span": v(75, "lead ruling S8 B-R5; CS B.2 (C-DEF 'ew_lookback: 75', a pandas span, C-EXPC:151-152)"),
            "min_periods": v(10, "lead ruling S8 B-R5; CS B.2 (C-DEF 'min_periods: 10')"),
            "years": v(5, "lead ruling S8 B-R5; CS B.2 (C-DEF 'rollyears: 5', date_method rolling)"),
            "clip": v(0.99, "lead ruling S8 B-R5; CS B.2 (C-DEF 'clip: 0.99')"),
            "offdiag": v(0.0, "lead ruling S8 B-R5; CS B.2 (C-DEF 'offdiag: 0.0')"),
            "floor_at_zero": v(False, "CS B.1 step 3 (P-JUN21 .txt:70 'We don't floor_at_zero'); C-DEF 'floor_at_zero: False'"),
            "shrinkage": v(0.5, "lead ruling R-B6 (2026-10-16): P-NOV21 .txt:153 states shrinking ('What eventually "
                                "came to the rescue ... was shrinking the correlation matrix') without a value, so B-R5 "
                                "takes the code's 0.5 toward a zero off-diagonal (C-STAGE:285-286, C-CORR:95)"),
            "reestimate": v("every decision date", "MicroBookCoder choice (code re-estimates weekly in backtests; "
                                                    "P-JUN21 'will need to be done every day in production')"),
        },
        "volatility": v("annual $ vol per contract (key 'vol')", "CS B.2 (stdev = annualised mixed vol, C-PORT:1263)"),
    },
    "fills": v("orders from data through settle(t) fill at settle(t+1), the instrument's next settlement",
               "lead_spec_B S3.7"),
}


QUOTE_UNITS = {
    "MNQ": "Nasdaq-100 index points", "M2K": "Russell 2000 index points",
    "MGC": "USD per troy ounce", "MCL": "USD per barrel", "MNG": "USD per MMBtu",
    "M6E": "USD per EUR", "2YY": "yield in percent", "10Y": "yield in percent",
    "30Y": "yield in percent",
    "MZC": "USD per bushel (CME quotes cents: enter cents / 100)",
    "MZS": "USD per bushel (CME quotes cents: enter cents / 100)",
    "MZL": "USD per pound (CME quotes cents: enter cents / 100)",
}


def forward_instruments(cost_rows: Mapping[str, Mapping[str, float]]) -> dict[str, dict]:
    """The FORWARD instruments (lead ruling (2)): each micro on its own settlement series; the
    yield micros trade their own yield-quoted contracts (price = yield in percent, $1,000 per
    1.000, $10 per bp, tick 0.001 = $1)."""
    out = {}
    for m in MICROS:
        row = cost_rows[m.code]
        if m.yield_proxy:
            spec = {"multiplier": 1000.0, "tick": 0.001, "tick_value": 1.0,
                    "price_units": "yield in percent", "yield_quoted": True,
                    "spec_source": m.spec_source + "; price = yield in %, $1,000 per 1.000 (lead ruling (2))"}
        else:
            spec = {"multiplier": m.multiplier, "tick": m.tick, "tick_value": m.tick_value,
                    "price_units": "contract price", "yield_quoted": False,
                    "spec_source": m.spec_source}
        out[m.code] = {**spec, "exposure": m.exposure, "quote_units": QUOTE_UNITS[m.code],
                       "cost_per_side_usd": row["per_side_usd"],
                       "cost_source": row["source"],
                       "commission_rt_usd": m.commission_rt,
                       "commission_source": m.commission_source,
                       "study_path": m.root + (" (yield proxy, D " + str(m.duration) + ")" if m.yield_proxy else "")}
    return out


def build_config(*, fdm: float | None, fdm_corr: Sequence[Sequence[float]] | None,
                 idm: float | None, idm_corr: Sequence[Sequence[float]] | None,
                 idm_codes: Sequence[str] | None, cost_rows: Mapping[str, Mapping[str, float]],
                 scalars: Mapping[str, float] | None = None, capital: float = 25_000.0,
                 study_note: str = "") -> dict[str, Any]:
    cfg = copy.deepcopy(BASE)
    if scalars is not None:
        cfg["ewmac"]["scalars"]["value"] = dict(scalars)
    cfg["fdm"]["value"] = fdm
    cfg["fdm"]["correlation"] = None if fdm_corr is None else [list(map(float, r)) for r in fdm_corr]
    cfg["idm"]["value"] = idm
    cfg["idm"]["correlation"] = None if idm_corr is None else [list(map(float, r)) for r in idm_corr]
    cfg["idm"]["instruments"] = None if idm_codes is None else list(idm_codes)
    return {
        "schema": "stage_e22_f1_config/1",
        "status": ("DRAFT written by MicroBookCoder (microbook.run study) from the design study; the lead "
                   "reviews and freezes it (E22-F1)"),
        "test_id": "E22-F1",
        "capital_usd": v(capital, "reports/stage_e22_prereg_F1.md (draft) title: '$25,000'"),
        "rounding_method": v("simple", "lead ruling R-B7 (2026-10-16): E22-F1 uses Carver's rounded-and-buffered "
                                       "baseline (key 'simple_rounding'); the greedy code and its parameters (key "
                                       "'greedy') stay in forward/core.py and are NOT used by E22-F1"),
        "instruments_order": [m.code for m in MICROS],
        "instruments": forward_instruments(cost_rows),
        **cfg,
        "study_note": study_note,
    }


def build_tables(config: Mapping[str, Any]) -> dict[str, Any]:
    """forward.runner's --tables JSON (forward/README.md): multipliers in the settlement CSV's quote
    units and per-side costs (USD), from the same instrument table as config_f1.json; the runner
    reads only "multipliers" and "cost_per_side"."""
    inst = config["instruments"]
    codes = list(config["instruments_order"])
    return {
        "schema": "stage_e22_f1_tables/1",
        "status": ("DRAFT written by MicroBookCoder (microbook.run study); the lead freezes it with "
                   "config_f1.json (E22-F1)"),
        "multipliers": {c: float(inst[c]["multiplier"]) for c in codes},
        "cost_per_side": {c: float(inst[c]["cost_per_side_usd"]) for c in codes},
        "quote_units": {c: inst[c]["quote_units"] for c in codes},
        "sources": {c: {"multiplier": inst[c]["spec_source"], "cost_per_side": inst[c]["cost_source"]}
                    for c in codes},
    }


def extension_cost_row(m: Micro) -> dict[str, float | str]:
    return {"per_side_usd": per_side_extension_cents(m) / 100.0,
            "source": (f"S6 D8 extension: commission ${m.commission_rt:.2f} RT / 2 ({m.commission_source}) "
                       f"+ 1 tick ${m.tick_value:.2f} per side (FLAGGED: not a frozen D8 table)")}


__all__ = ["BASE", "QUOTE_UNITS", "SCALARS_BOOK", "SCALARS_PRODUCTION", "SPEEDS", "build_config", "build_tables",
           "extension_cost_row", "forward_instruments", "v"]
