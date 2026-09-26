"""Per-product contract table for the Stage E rules engine (design D9.5, D9.6, D8, D11.1).

The 45 admissible contracts of design D1 (after U2) plus the MES/ES leg, for the $50K XFA only.
Every value is a module constant with its source, as rules/xfa_rules.py binds its limits: nothing
upstream can pass a looser table. rules/xfa_rules.py is not changed and MES keeps its own engine;
the MES row here repeats its constants (tests assert equality).

Sources (field -> source):
- tick size and tick value: reports/stage_e0_liquidity.json (CME contract specifications, fetched
  by E.0 with ``tick_quote`` and ``tick_source_url`` per product). Exchange price units.
- vendor price factor: Databento quotes ZC, ZW, ZS, ZL, HE and LE in US cents, so their tick in
  vendor price units is 100 x the exchange tick (the lead's late note of 2026-09-25 02:00 PDT;
  BarsCoder's grid-scale probe, reports/stage_e2a_bars.md). Every other product: factor 1.
- commission (round turn, commission + exchange + NFA fees): Topstep's table, facts F3.7, plus
  the CME increase effective the 2026-10-01 trading day (F3.6: MCL and MNG +$0.10 per side),
  applied now as design D8 says: MCL $1.72, MNG $1.92.
- lot-equivalent weight: design D9.6 ("minis 1, micros 0.1, SIL 0.2, MBT 1, MET 1"), from
  Topstep's Scaling Plan article (F5.2, F5.4). Weights are held in tenths of a lot so every sum
  is exact integer arithmetic.
- volatility caps: design D9.11, the 50K figures of Topstep's Risk Adjustments article (F12.1c).

Readings (reported in reports/stage_e2a_rules.md, never silent):
- QM, QG, E7: Topstep publishes no weighting for them by name (facts F12.4, not_published). They
  are E-mini contracts, so D9.6's "minis 1" applies, as the K4 catalog already reads it; the
  conservative reading (the larger weight) gives the same answer. Weight 1.
- M6E, M6A, M6B: named "Micro" by Topstep's product list and absent from its exception table
  (F12.4); D9.6's "micros 0.1" applies (Topstep's generic "1 Mini = 10 Micro contracts").
- SI and HG: Topstep's 50K volatility cap is 0 at its discretion (F12.1c). D9.11 encodes only
  SIL, MHG, MCL, MGC, CL, QM, RB, HO and GC; SI and HG keep the D9.5 cap of 1 and carry the
  flag ``may_be_suspended`` (the lead's answer Q-1 to VehicleCoder, reports/stage_e2a_STATE.md).
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum

from data.calendars import GROUP_OF_PRODUCT

PRICE_SCALE = 1_000_000_000  # Databento fixed-point prices: 1e-9 units
TENTHS_PER_LOT = 10  # lot-equivalents are held in tenths
MEMBER_CAP_TENTHS = 10  # D9.5: every member is at most 1 lot-equivalent


class ContractType(Enum):
    MINI = "mini"  # full-size and E-mini contracts
    MICRO = "micro"
    SIL = "sil"  # Micro Silver: "5:1 ratio vs. Silver (SI); counts as 2 of any other micro"
    MBT = "mbt"  # Micro Bitcoin: "Capped at mini-equivalent lot sizes"


LOT_WEIGHT_TENTHS: dict[ContractType, int] = {
    ContractType.MINI: 10,
    ContractType.MICRO: 1,
    ContractType.SIL: 2,
    ContractType.MBT: 10,
}

SOURCE_TICK = "reports/stage_e0_liquidity.json (CME contract specifications via E.0)"
SOURCE_VENDOR = "lead late note 2026-09-25 02:00 PDT; stage_e2a_bars.md grid-scale probe"
SOURCE_COMMISSION = "reports/stage_e0_topstep_facts.json F3.7 (help.topstep.com, article 8284213)"
SOURCE_COMMISSION_F36 = SOURCE_COMMISSION + " + F3.6 (CME increase from 2026-10-01, D8)"
SOURCE_WEIGHT = "design D9.6 (Topstep Scaling Plan, facts F5.2 and F5.4)"
SOURCE_WEIGHT_READING = "reading: not named by Topstep (F12.4); design D9.6 category applied"
SOURCE_GROUP = "data/calendars/__init__.py GROUP_OF_PRODUCT"


@dataclass(frozen=True)
class Product:
    """One contract. Prices in ``tick_size`` are exchange units (E.0); bars arrive in vendor
    units, ``vendor_price_factor`` x exchange units."""

    root: str
    group: str
    subgroup: str  # settlement and D6 sub-table key (gold / silver / copper for metals)
    exposure: str
    contract_type: ContractType
    tick_size: Decimal
    tick_value_usd: Decimal
    multiplier_usd: Decimal  # USD per 1.0 exchange price unit; tick_value = tick x multiplier
    vendor_price_factor: int
    commission_rt_cents: int
    admissible: bool  # False: the MES/ES leg (design D1.5)
    weight_source: str
    commission_source: str
    tick_source: str = SOURCE_TICK

    @property
    def lot_weight_tenths(self) -> int:
        return LOT_WEIGHT_TENTHS[self.contract_type]

    @property
    def vendor_tick(self) -> Decimal:
        return self.tick_size * self.vendor_price_factor

    @property
    def vendor_tick_fixed(self) -> int:
        """The tick in Databento fixed-point vendor units (1e-9)."""
        value = self.vendor_tick * PRICE_SCALE
        if value != value.to_integral_value():
            raise ValueError(f"{self.root}: vendor tick {self.vendor_tick} is not whole 1e-9 units")
        return int(value)


def _p(
    root: str,
    exposure: str,
    ctype: ContractType,
    tick: str,
    tick_value: str,
    multiplier: str,
    commission_cents: int,
    *,
    subgroup: str | None = None,
    factor: int = 1,
    admissible: bool = True,
    weight_source: str = SOURCE_WEIGHT,
    commission_source: str = SOURCE_COMMISSION,
) -> Product:
    group = GROUP_OF_PRODUCT[root]
    return Product(
        root=root,
        group=group,
        subgroup=subgroup or group,
        exposure=exposure,
        contract_type=ctype,
        tick_size=Decimal(tick),
        tick_value_usd=Decimal(tick_value),
        multiplier_usd=Decimal(multiplier),
        vendor_price_factor=factor,
        commission_rt_cents=commission_cents,
        admissible=admissible,
        weight_source=weight_source,
        commission_source=commission_source,
    )


MINI, MICRO = ContractType.MINI, ContractType.MICRO
_WR, _F36 = SOURCE_WEIGHT_READING, SOURCE_COMMISSION_F36
_CENTS = 100  # vendor factor of the cent-quoted products

PRODUCTS: dict[str, Product] = {
    p.root: p
    for p in (
        # ---- equity index (K1); ES and MES are legs only (D1.5)
        _p("NQ", "nasdaq100", MINI, "0.25", "5.00", "20", 378),
        _p("MNQ", "nasdaq100", MICRO, "0.25", "0.50", "2", 122),
        _p("RTY", "russell2000", MINI, "0.10", "5.00", "50", 378),
        _p("M2K", "russell2000", MICRO, "0.10", "0.50", "5", 122),
        _p("YM", "dow", MINI, "1.00", "5.00", "5", 378),
        _p("MYM", "dow", MICRO, "1.00", "0.50", "0.5", 122),
        _p("ES", "sp500", MINI, "0.25", "12.50", "50", 378, admissible=False),
        _p("MES", "sp500", MICRO, "0.25", "1.25", "5", 122, admissible=False),
        # ---- rates (K2)
        _p("ZT", "ust2y", MINI, "0.00390625", "7.8125", "2000", 232),
        _p("ZF", "ust5y", MINI, "0.0078125", "7.8125", "1000", 232),
        _p("ZN", "ust10y", MINI, "0.015625", "15.625", "1000", 262),
        _p("TN", "ustultra10y", MINI, "0.015625", "15.625", "1000", 262),
        _p("ZB", "ustbond", MINI, "0.03125", "31.25", "1000", 276),
        _p("UB", "ustultrabond", MINI, "0.03125", "31.25", "1000", 292),
        # ---- FX (K3)
        _p("6E", "eur", MINI, "0.00005", "6.25", "125000", 422),
        _p("M6E", "eur", MICRO, "0.0001", "1.25", "12500", 100, weight_source=_WR),
        _p("E7", "eur", MINI, "0.0001", "6.25", "62500", 272, weight_source=_WR),
        _p("6A", "aud", MINI, "0.00005", "5.00", "100000", 422),
        _p("M6A", "aud", MICRO, "0.0001", "1.00", "10000", 100, weight_source=_WR),
        _p("6B", "gbp", MINI, "0.0001", "6.25", "62500", 422),
        _p("M6B", "gbp", MICRO, "0.0001", "0.625", "6250", 100, weight_source=_WR),
        _p("6C", "cad", MINI, "0.00005", "5.00", "100000", 422),
        _p("6J", "jpy", MINI, "0.0000005", "6.25", "12500000", 422),
        _p("6S", "chf", MINI, "0.00005", "6.25", "125000", 422),
        _p("6N", "nzd", MINI, "0.00005", "5.00", "100000", 422),
        # ---- energy (K4)
        _p("CL", "wti", MINI, "0.01", "10.00", "1000", 402),
        _p("MCL", "wti", MICRO, "0.01", "1.00", "100", 172, commission_source=_F36),
        _p("QM", "wti", MINI, "0.025", "12.50", "500", 342, weight_source=_WR),
        _p("NG", "henryhub", MINI, "0.001", "10.00", "10000", 422),
        _p("MNG", "henryhub", MICRO, "0.001", "1.00", "1000", 192, commission_source=_F36),
        _p("QG", "henryhub", MINI, "0.005", "12.50", "2500", 202, weight_source=_WR),
        _p("RB", "rbob", MINI, "0.0001", "4.20", "42000", 402),
        _p("HO", "ulsd", MINI, "0.0001", "4.20", "42000", 402),
        # ---- metals (K5)
        _p("GC", "gold", MINI, "0.10", "10.00", "100", 432, subgroup="gold"),
        _p("MGC", "gold", MICRO, "0.10", "1.00", "10", 192, subgroup="gold"),
        _p("SI", "silver", MINI, "0.005", "25.00", "5000", 432, subgroup="silver"),
        _p("SIL", "silver", ContractType.SIL, "0.005", "5.00", "1000", 272, subgroup="silver"),
        _p("HG", "copper", MINI, "0.0005", "12.50", "25000", 432, subgroup="copper"),
        _p("MHG", "copper", MICRO, "0.0005", "1.25", "2500", 192, subgroup="copper"),
        # ---- grains (K6); ZC, ZW, ZS, ZL quoted in cents by the vendor
        _p("ZC", "corn", MINI, "0.0025", "12.50", "5000", 528, factor=_CENTS),
        _p("ZW", "wheat", MINI, "0.0025", "12.50", "5000", 528, factor=_CENTS),
        _p("ZS", "soybeans", MINI, "0.0025", "12.50", "5000", 528, factor=_CENTS),
        _p("ZM", "soymeal", MINI, "0.10", "10.00", "100", 528),
        _p("ZL", "soyoil", MINI, "0.0001", "6.00", "60000", 528, factor=_CENTS),
        # ---- livestock (K6); quoted in cents by the vendor
        _p("HE", "leanhogs", MINI, "0.00025", "10.00", "40000", 522, factor=_CENTS),
        _p("LE", "livecattle", MINI, "0.00025", "10.00", "40000", 522, factor=_CENTS),
        # ---- crypto (K7)
        _p("MBT", "bitcoin", ContractType.MBT, "5.00", "0.50", "0.1", 282),
    )
}

ADMISSIBLE: tuple[str, ...] = tuple(r for r, p in PRODUCTS.items() if p.admissible)

# Design D9.11 (Topstep Risk Adjustments, F12.1c, 50K figures), applied at all times.
VOLATILITY_CAP_50K: dict[str, int] = {
    "SIL": 2, "MHG": 2, "MCL": 10, "MGC": 10, "CL": 1, "QM": 1, "RB": 1, "HO": 1, "GC": 1,
}
# Topstep's 50K figure is 0 at its discretion; not in D9.11's encoded list (flag only).
MAY_BE_SUSPENDED: frozenset[str] = frozenset({"SI", "HG"})


class UnknownProduct(KeyError):
    pass


def product(root: str) -> Product:
    try:
        return PRODUCTS[root]
    except KeyError:
        raise UnknownProduct(f"{root!r} is not in the Stage E product table") from None


def member_cap_contracts(root: str) -> int:
    """D9.5 and D9.11: floor(1 lot / weight), then the 50K volatility cap."""
    p = product(root)
    cap = MEMBER_CAP_TENTHS // p.lot_weight_tenths
    return min(cap, VOLATILITY_CAP_50K.get(root, cap))


# ------------------------------------------------------------ price units ----
Price = int | float | str | Decimal


def to_decimal(price: Price) -> Decimal:
    """A vendor-unit price as an exact Decimal (a float goes through its shortest repr).
    Raw Databento fixed-point integers go through ``from_fixed`` first."""
    if isinstance(price, bool):
        raise TypeError("price must be a number, not a bool")
    if isinstance(price, Decimal):
        return price
    if isinstance(price, int):
        return Decimal(price)
    return Decimal(str(price))


def from_fixed(raw: int) -> Decimal:
    """A Databento 1e-9 fixed-point price as a Decimal in vendor units."""
    return Decimal(raw) / PRICE_SCALE


def price_to_ticks(root: str, price: Price) -> int:
    """Vendor price -> whole ticks of the vendor-unit tick; refuses an off-grid price."""
    tick = product(root).vendor_tick
    ticks = to_decimal(price) / tick
    whole = ticks.to_integral_value()
    if abs(ticks - whole) > Decimal("1e-6"):
        raise ValueError(f"{root} price {price} is not on the {tick} vendor-unit grid")
    return int(whole)


def ticks_between(root: str, from_price: Price, to_price: Price) -> int:
    """Signed ticks from ``from_price`` to ``to_price`` (vendor units)."""
    return price_to_ticks(root, to_price) - price_to_ticks(root, from_price)


def pnl_usd(root: str, ticks: int, contracts: int) -> Decimal:
    """Exact USD for ``ticks`` on ``contracts`` (signed): ticks x contracts x tick value. Some
    tick values have fractions of a cent (ZT, ZF $7.8125; M6B $0.625), so this is a Decimal."""
    return Decimal(ticks) * Decimal(contracts) * product(root).tick_value_usd


def commission_usd(root: str, contracts: int) -> Decimal:
    """Round-turn commission and fees for ``contracts`` contracts."""
    return Decimal(product(root).commission_rt_cents) * abs(contracts) / 100
