"""The study universe (lead_spec_B.md S1, S3.6, S6): each modelled micro on its owned E.21 price
path, its multiplier, tick and cost basis, every figure with its source.

Units (study): the price of a path is in the contract's own price units (rules.products tick_size,
e.g. USD per bushel for ZC, index points for NQ). A micro's dollar P&L per contract is
``multiplier x dP``. The yield micros (2YY, 10Y, 30Y) run on a proxy yield series in basis points
(S3.6): multiplier 10 USD per bp.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType

T28 = "E.13 T-28 (AMP contract specifications, reports/stage_e13_briefs/pages/TrendCarry/amp_contract_specs.txt)"
D8_FROZEN = "base_rules.costs.vehicle_cost (frozen D8 table reports/stage_e2a_costs.json), settlement bucket, base case"
COSTS_JSON = "reports/stage_e2a_costs.json commission_rt_usd (source F3.7/F3.6 of reports/stage_e0_topstep_facts.json)"
UNSOURCED_COMM = ("UNSOURCED for this micro: no Topstep/D8 commission; declared the largest frozen micro "
                  "round turn (MGC/MNG $1.92, reports/stage_e2a_costs.json)")


@dataclass(frozen=True)
class Micro:
    code: str  # the micro's trading class
    exposure: str
    root: str  # owned price path (E.21 root)
    multiplier: float  # USD per 1.0 of the study price unit (bp for the yield proxies)
    tick: float  # the micro's tick in study price units
    tick_value: float  # USD per tick
    spec_source: str
    cost_basis: str  # "frozen" (base_rules D8 vehicle) or "extension" (commission + 1 tick)
    commission_rt: float  # USD per round turn (extension) or the frozen vehicle's figure
    commission_source: str
    yield_proxy: bool = False
    duration: float | None = None  # declared modified duration (S3.6), yield proxies only


MICROS: tuple[Micro, ...] = (
    Micro("MNQ", "Nasdaq-100", "NQ", 2.0, 0.25, 0.50, T28 + ": '$2 x Nasdaq-100 Index', '0.25 / $0.50'",
          "frozen", 1.22, COSTS_JSON),
    Micro("M2K", "Russell 2000", "RTY", 5.0, 0.10, 0.50, T28 + ": '$5 x Russell 2000 Index', '0.10 / $0.50'",
          "frozen", 1.22, COSTS_JSON),
    Micro("MGC", "Gold", "GC", 10.0, 0.10, 1.00, T28 + ": '10 oz', '0.10/$1.00'",
          "frozen", 1.92, COSTS_JSON),
    Micro("MCL", "WTI crude", "CL", 100.0, 0.01, 1.00, T28 + ": '100 barrels', '0.01 / $1.00'",
          "frozen", 1.72, COSTS_JSON),
    Micro("MNG", "Henry Hub gas", "NG", 1000.0, 0.001, 1.00, T28 + ": '1,000 MMBtu', '0.001 / $1.00'",
          "extension", 1.92, COSTS_JSON + " (MNG 1.92 incl. the 2026-10-01 fee increase, D8)"),
    Micro("M6E", "EUR/USD", "6E", 12500.0, 0.0001, 1.25, T28 + ": '12,500 EUR', '0.0001 / $1.25'",
          "extension", 1.00, COSTS_JSON),
    Micro("2YY", "2-year yield", "ZT", 10.0, 0.1, 1.00, T28 + ": '$10.00 DV01', '1/10 of 1bp / $1.00'",
          "extension", 1.92, UNSOURCED_COMM, True, 1.9),
    Micro("10Y", "10-year yield", "ZN", 10.0, 0.1, 1.00, T28 + ": '$10.00 DV01', '1/10 of 1bp / $1.00' (AMP code 10YY)",
          "extension", 1.92, UNSOURCED_COMM, True, 6.5),
    Micro("30Y", "30-year yield", "ZB", 10.0, 0.1, 1.00, T28 + ": '$10.00 DV01', '1/10 of 1bp / $1.00' (AMP code 30YY)",
          "extension", 1.92, UNSOURCED_COMM, True, 15.0),
    Micro("MZC", "Corn", "ZC", 500.0, 0.005, 2.50, T28 + ": '500 bushels', '0.0050 / $2.50'",
          "extension", 1.92, UNSOURCED_COMM),
    Micro("MZS", "Soybeans", "ZS", 500.0, 0.005, 2.50, T28 + ": '500 bushels', '0.0050 / $2.50'",
          "extension", 1.92, UNSOURCED_COMM),
    Micro("MZL", "Soybean oil", "ZL", 6000.0, 0.0002, 1.20, T28 + ": '6,000 lbs', '0.02 / $1.20' (cents/lb)",
          "extension", 1.92, UNSOURCED_COMM),
)
BY_CODE = MappingProxyType({m.code: m for m in MICROS})
ROOTS = tuple(m.root for m in MICROS)
YIELD_CODES = tuple(m.code for m in MICROS if m.yield_proxy)
DURATION_NOTE = "declared approximation, UNSOURCED (lead_spec_B S3.6)"

# Optional sensitivity (S5): micro Ultra 10-year / Ultra bond on the TN / UB paths, price-quoted.
SENSITIVITY: tuple[Micro, ...] = (
    Micro("MTN", "Ultra 10-year (micro)", "TN", 100.0, 0.015625 / 2, 1.5625,
          T28 + ": '$10K Note', '1/2 of 1/32 / $1.5625'", "extension", 1.92, UNSOURCED_COMM),
    Micro("MWN", "Ultra bond (micro)", "UB", 100.0, 0.03125, 3.125,
          T28 + ": '$10K bond', '1/32 / $3.125' (AMP code MWNA)", "extension", 1.92, UNSOURCED_COMM),
)

NOT_MODELLED = MappingProxyType({
    "SIL": "no owned silver path (SI not owned)",
    "MHG": "only owned path HG/MHG step 2 2019-05..2024-02, never read by E.21; Part A K5 confirmation data",
    "M6A": "only owned path 6A step 2, never read by E.21; Part A K3 confirmation data",
    "M6B": "only owned path 6B step 2, never read by E.21; Part A K3 confirmation data",
    "MCD": "only owned path 6C step 2, never read by E.21; Part A K3 confirmation data",
    "MJY": "only owned path 6J step 2, never read by E.21; Part A K3 confirmation data",
    "MZW": "only owned path ZW step 2, never read by E.21; Part A K6 confirmation data",
    "MZM": "only owned path ZM step 2, never read by E.21; Part A K6 confirmation data",
    "MES": "no owned 2010-2024 path (only MES's Stage D 2019-2024 store, a Part A leg)",
})


def per_side_extension_cents(m: Micro, slippage_ticks: float = 1.0) -> float:
    """S6 'D8 extension': commission per side + ``slippage_ticks`` ticks of slippage, cents."""
    return 100.0 * (m.commission_rt / 2.0 + slippage_ticks * m.tick_value)


__all__ = ["BY_CODE", "DURATION_NOTE", "MICROS", "Micro", "NOT_MODELLED", "ROOTS", "SENSITIVITY",
           "YIELD_CODES", "per_side_extension_cents"]
