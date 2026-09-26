"""Fixed inputs of the Stage E per-product cost model (design D8; Stage E.2a Task 8).

Everything here is read from frozen Stage E.0 / E.1 reports or stated by D8 itself; nothing is
estimated. The calibration (``sim.calibrate_costs``) and the loader (``sim.product_costs``) both
take their commission and tick tables from this module, so the two cannot disagree.

- Commission: Topstep's published round-turn total per product (commission, exchange and NFA
  fees), reports/stage_e0_topstep_facts.json fact F3.7, with the CME exchange-fee increase
  effective the 2026-10-01 trading day (fact F3.6: MCL and MNG +$0.10 per side) applied now,
  as D8 says: MCL $1.72, MNG $1.92.
- Tick size and tick value: reports/stage_e0_liquidity.json (``tick_size``, ``tick_value_usd``,
  each with its CME contract-spec source).
- Vendor price units: Databento GLBX.MDP3 prices are fixed-point 1e-9 in the exchange's display
  units. Six products are displayed in US cents (the grains ZC, ZW, ZS, ZL and livestock HE, LE),
  so their tick in vendor units is 100 x the E.0 tick in USD. This factor is DECLARED here and
  VERIFIED on the data by the calibration (every quoted price on the vendor tick grid, and a
  one-tick quoted spread observed), never inferred from it.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from pathlib import Path

from data.config import REPO_ROOT

TOPSTEP_FACTS = REPO_ROOT / "reports" / "stage_e0_topstep_facts.json"
LIQUIDITY_JSON = REPO_ROOT / "reports" / "stage_e0_liquidity.json"
PURCHASE_MANIFEST = REPO_ROOT / "reports" / "stage_e1_purchase.json"

# D8: the five dates fixed at 20:10 PDT on 2026-09-23 (full CME trade dates).
SAMPLE_DATES: tuple[date, ...] = (
    date(2025, 5, 14), date(2025, 8, 13), date(2025, 11, 12), date(2026, 2, 11), date(2026, 4, 15),
)
BUCKET_MINUTES = 30  # D8: 30-minute CT buckets aligned to the clock
MIN_DATES_WITH_QUOTES = 3  # D8: a bucket quoted on fewer than 3 of the 5 dates takes the fallback
PRICE_SCALE = 1_000_000_000  # Databento fixed-point prices

# F3.6: "Exchange fee increase starting the October 1, 2026 trading day ... MCL: $0.50 to $0.60 per
# side ($1.20 round turn). MNG: $0.60 to $0.70 per side ($1.40 round turn). That's $0.10 more per
# side." D8 applies it now: +$0.20 per round turn.
FEE_INCREASE_2026_10_01_RT: dict[str, Decimal] = {"MCL": Decimal("0.20"), "MNG": Decimal("0.20")}

# Products whose Databento prices are in US cents (declared; verified on the data).
VENDOR_PRICE_FACTOR: dict[str, int] = {p: 100 for p in ("ZC", "ZW", "ZS", "ZL", "HE", "LE")}


class CostInputError(ValueError):
    """A frozen input does not say what the cost model needs; never guessed."""


def parse_commission_quote(quote: str) -> dict[str, Decimal]:
    """F3.7's quote ``"ES $3.78; MES $1.22; ..."`` -> {root: round-turn USD}."""
    out: dict[str, Decimal] = {}
    for item in quote.split(";"):
        match = re.fullmatch(r"\s*([0-9A-Z]+)\s+\$(\d+\.\d{2})\s*", item)
        if match is None:
            raise CostInputError(f"F3.7 item {item!r} is not '<ROOT> $<x.xx>'")
        root, usd = match.group(1), Decimal(match.group(2))
        if root in out:
            raise CostInputError(f"F3.7 lists {root} twice")
        out[root] = usd
    return out


def _fact(facts: list[dict], fact_id: str) -> dict:
    found = [f for f in facts if f.get("id") == fact_id]
    if len(found) != 1:
        raise CostInputError(f"{len(found)} facts with id {fact_id}")
    return found[0]


def load_commissions(path: Path = TOPSTEP_FACTS) -> dict[str, Decimal]:
    """Round-turn commission (USD) per root: F3.7 plus the F3.6 increase (D8)."""
    facts = json.loads(Path(path).read_text())["facts"]
    table = parse_commission_quote(_fact(facts, "F3.7")["quote"])
    notice = _fact(facts, "F3.6")["quote"]
    for root, bump in FEE_INCREASE_2026_10_01_RT.items():
        if f"{root}:" not in notice:
            raise CostInputError(f"F3.6 does not name {root}")
        table[root] = table[root] + bump
    return table


def parse_tick(text: str) -> Decimal:
    """The numeric tick of an E.0 ``tick_size`` string: its leading decimal, or the decimal in
    parentheses when it leads with a fraction ("1/2 of 1/32 (0.015625)")."""
    lead = re.match(r"^\s*(\d+(?:\.\d+)?)(?=\s|$)", text)
    if lead:
        return Decimal(lead.group(1))
    inner = re.search(r"\((\d+(?:\.\d+)?)\)", text)
    if inner:
        return Decimal(inner.group(1))
    raise CostInputError(f"no numeric tick in {text!r}")


@dataclass(frozen=True)
class TickSpec:
    root: str
    tick_size: Decimal  # exchange units (E.0)
    tick_value_usd: Decimal
    vendor_factor: int  # vendor price units per exchange unit
    source_text: str

    @property
    def vendor_tick(self) -> Decimal:
        return self.tick_size * self.vendor_factor

    @property
    def vendor_tick_fixed(self) -> int:
        value = self.vendor_tick * PRICE_SCALE
        if value != value.to_integral_value() or value <= 0:
            raise CostInputError(f"{self.root}: tick {self.vendor_tick} is not whole 1e-9 units")
        return int(value)


def load_ticks(path: Path = LIQUIDITY_JSON) -> dict[str, TickSpec]:
    rows = json.loads(Path(path).read_text())["products"]
    out: dict[str, TickSpec] = {}
    for row in rows:
        root = row["symbol"]
        out[root] = TickSpec(
            root=root, tick_size=parse_tick(str(row["tick_size"])),
            tick_value_usd=Decimal(str(row["tick_value_usd"])),
            vendor_factor=VENDOR_PRICE_FACTOR.get(root, 1), source_text=str(row["tick_size"]))
    return out


def mbp1_files(manifest: Path = PURCHASE_MANIFEST) -> dict[str, list[dict]]:
    """root -> the product's mbp-1 manifest rows, in request order."""
    rows = json.loads(Path(manifest).read_text())["files"]
    out: dict[str, list[dict]] = {}
    for row in rows:
        if row["schema"] == "mbp-1":
            out.setdefault(row["product"], []).append(row)
    return {k: sorted(v, key=lambda r: r["request_start"]) for k, v in out.items()}
