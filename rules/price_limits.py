"""Price-limit proximity rule (design D9.7) with per-product CME limit tables, Stage E, $50K XFA.

Topstep's rule (help.topstep.com/en/articles/8284225, May 29, 2026): "Stop trading above:
Settlement × (1 + Price Limit% − 2%)"; "Stop trading below: Settlement × (1 − Price Limit% + 2%)";
"Price limits are calculated from the previous day’s settlement price." For a limit set in price
units, Price Limit% = limit amount / prior settlement (D9.7). Encoded (D9.7): no entry, and an
immediate exit, while the price is at or beyond either stop level. That exit fills at the next
bar's open, is exempt from the event-minute fill guard (D9.5a) and pays the event-window cost
(D8). Locked markets (review R-08): an exit that must trade against a lock (a long at limit-down,
a short at limit-up) is not filled until a later bar trades through the limit price, and the trip
is flagged (``locked_exit_fill``).

Limit kinds (reports/stage_e2a_price_limits.json has every source with verbatim quotes):
- HARD_DAILY (ZC, ZW, ZS, ZM, ZL, HE, LE): a fixed amount in exchange price units around the
  prior settlement, up and down, all hours. Grain limits reset for the first trade date of May
  and November; Live Cattle on the first trading day in June; Lean Hogs in September. Only the
  initial limit is encoded: an expanded limit (the day after a limit close) is wider, so the
  initial limit is the stricter reading (flag R-L2).
- EQUITY_BANDS (NQ, MNQ, RTY, M2K, YM, MYM, and the ES/MES leg): around the prior fixing price
  (VWAP 14:59:30-15:00:00 CT): up and down ``eth_pct`` from 17:00 to 08:30 CT and from 15:00 CT
  on; down only 7% from 08:30 CT until ``rth_7pct_until`` (14:25 CT from November 2019), then down
  only 20% until 15:00 CT. The 7% and 13% RTH levels are halts after which the next level
  applies; the first level is kept for the whole window (stricter, flag R-L3).
- DCB_ONLY (rates, FX, energy, metals, MBT): CME has no daily lock limit, only dynamic circuit
  breakers (a variant of the prior settlement, applied to a rolling 60-minute window; a breach
  halts trading for about two minutes). Topstep's rule names a "price lock limit"; a DCB never
  locks. Two readings are encoded (``DcbReading``). The default is NO_LOCK_LIMIT (lead ruling
  L-13, 2026-09-25 06:58 PDT): these products have no price lock limit, so the 2% rule does not
  apply. The alternative, VARIANT_AS_LIMIT, treats the DCB variant as a daily limit around the
  prior settlement; under it a variant below 2% of price leaves no tradable band, so ZT (0.75
  point), ZF (1.50) and ZN (2.00) could not be traded at all. Hard-limit products (grains,
  livestock, equity) are unaffected by the switch.
Periods: ``sourced`` (CME publications on both sides), ``bracketed`` (the change date lies
between two observations and no CME-stated date was found: the narrower limit is encoded),
``carried`` (after the last observation, unverified), ``pending`` (no CME source: the lookup
raises ``LimitPending``). Every period of the research window 2025-04-01..2026-06-19 is sourced,
bracketed or carried; none is pending.

Prior settlement: Databento's statistics schema was not bought, so D9.7's proxy applies: the
volume-weighted price of the one-minute bars in the product's settlement window
(``settlement_window_ct``; CME's Daily Settlement Time Details), computed by
``settlement_proxy`` from bars the caller passes. This module reads no data.

All prices are in vendor units (Databento): ZC, ZW, ZS, ZL, HE and LE in cents, the rest in the
exchange's units; limit amounts are stored in exchange units and scaled by the product's
``vendor_price_factor``.
"""

from __future__ import annotations

import importlib
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from enum import Enum
from zoneinfo import ZoneInfo

from data.cme_calendar import HolidayKind
from rules.products import Price, product, to_decimal
from rules.sessions import GroupHolidays, default_holidays
from rules.xfa_rules import Refusal

CT = ZoneInfo("America/Chicago")
D = Decimal
TOPSTEP_BUFFER = D("0.02")  # "Price Limit% − 2%"


class LimitKind(Enum):
    HARD_DAILY = "hard_daily"
    EQUITY_BANDS = "equity_bands"
    DCB_ONLY = "dcb_only"


class DcbReading(Enum):
    NO_LOCK_LIMIT = "no_lock_limit"  # literal: no price lock limit, the rule does not apply
    VARIANT_AS_LIMIT = "variant_as_limit"  # conservative: the DCB variant as a daily limit


# Lead ruling L-13 (2026-09-25 06:58 PDT): a DCB is a temporary halt that never locks the
# market, so DCB-only products have no "price lock limit" and the 2% rule does not apply.
DCB_READING_DEFAULT = DcbReading.NO_LOCK_LIMIT


class LimitPending(LookupError):
    """No CME source for this product and date: the rule cannot be evaluated."""


@dataclass(frozen=True)
class LimitPeriod:
    start: date
    end: date  # inclusive
    kind: LimitKind
    status: str  # sourced | bracketed | carried | pending
    n_observations: int
    sources: tuple[str, ...]  # ids in reports/stage_e2a_price_limits.json
    amount: Decimal | None = None  # HARD_DAILY, exchange price units
    eth_pct: int | None = None  # EQUITY_BANDS
    rth_7pct_until: time | None = None  # EQUITY_BANDS
    dcb_kind: str | None = None  # DCB_ONLY: "pct" or "points"
    dcb_value: Decimal | None = None


def _d(s: str) -> date:
    return date.fromisoformat(s)


def _hard(a: str, b: str, amount: Decimal | None, status: str, n: int,
          sources: tuple[str, ...]) -> LimitPeriod:
    return LimitPeriod(_d(a), _d(b), LimitKind.HARD_DAILY, status, n, sources, amount=amount)


def _eq(a: str, b: str, eth: int, rth_until: str, status: str, n: int,
        sources: tuple[str, ...]) -> LimitPeriod:
    return LimitPeriod(_d(a), _d(b), LimitKind.EQUITY_BANDS, status, n, sources, eth_pct=eth,
                       rth_7pct_until=time.fromisoformat(rth_until))


def _dcb(a: str, b: str, kind: str | None, value: Decimal | None, status: str, n: int,
         sources: tuple[str, ...]) -> LimitPeriod:
    return LimitPeriod(_d(a), _d(b), LimitKind.DCB_ONLY, status, n, sources, dcb_kind=kind,
                       dcb_value=value)


# Generated from reports/stage_e2a_price_limits.json (scratch builder build_price_limits.py);
# tests/test_e2a_rules.py asserts this table equals the JSON's periods.
LIMITS: dict[str, tuple[LimitPeriod, ...]] = {
    'ZC': (
        _hard("2019-05-01", "2021-05-02", D("0.25"), "sourced", 49,
             ("pl_20190408215002", "pl_20210411030219",)),
        _hard("2021-05-03", "2021-10-31", D("0.40"), "sourced", 10,
             ("cme_grain_faq", "pl_20210519160902", "pl_20211005224651",)),
        _hard("2021-11-01", "2022-05-01", D("0.35"), "sourced", 13,
             ("cme_grain_faq", "pl_20211203073758", "pl_20220324054144",)),
        _hard("2022-05-02", "2022-10-31", D("0.50"), "sourced", 8,
             ("cme_grain_faq", "pl_20220521112448", "pl_20221008031710",)),
        _hard("2022-11-01", "2023-10-31", D("0.45"), "sourced", 11,
             ("cme_grain_faq", "pl_20230323140643", "pl_20230707204329",)),
        _hard("2023-11-01", "2024-04-30", D("0.35"), "sourced", 7,
             ("cme_grain_faq", "pl_20230928165949", "pl_20240413052451",)),
        _hard("2024-05-01", "2025-04-30", D("0.30"), "sourced", 31,
             ("cme_grain_faq", "pl_20240519144823", "pl_20250428093001",)),
        _hard("2025-05-01", "2025-11-02", D("0.35"), "sourced", 21,
             ("cme_grain_faq", "pl_20250513061945", "pl_20251018123959",)),
        _hard("2025-11-03", "2026-06-19", D("0.30"), "sourced", 13,
             ("cme_grain_faq", "pl_20251112101804", "pl_20260907145625",)),
    ),
    'ZW': (
        _hard("2019-05-01", "2020-04-30", D("0.35"), "sourced", 18,
             ("pl_20190408215002", "pl_20200422053715",)),
        _hard("2020-05-01", "2021-05-02", D("0.40"), "sourced", 32,
             ("cme_grain_faq", "pl_20200531052856", "pl_20210411030219",)),
        _hard("2021-05-03", "2021-10-31", D("0.45"), "sourced", 12,
             ("cme_grain_faq", "pl_20210519160902", "pl_20211005224651",)),
        _hard("2021-11-01", "2022-01-28", D("0.50"), "sourced", 7,
             ("cme_grain_faq", "pl_20211203073758", "pl_20220128182742",)),
        _hard("2022-01-29", "2022-03-06", D("0.50"), "bracketed", 1,
             ("cme_grain_faq", "pl_20220307144843",)),
        _hard("2022-03-07", "2022-05-01", D("0.85"), "sourced", 4,
             ("pl_20220307144843", "pl_20220324054144",)),
        _hard("2022-05-02", "2022-10-31", D("0.70"), "sourced", 8,
             ("cme_grain_faq", "pl_20220521112448", "pl_20221008031710",)),
        _hard("2022-11-01", "2023-04-30", D("0.65"), "sourced", 7,
             ("cme_grain_faq", "pl_20230323140643", "pl_20230326155246",)),
        _hard("2023-05-01", "2023-10-31", D("0.60"), "sourced", 4,
             ("cme_grain_faq", "pl_20230523200617", "pl_20230707204329",)),
        _hard("2023-11-01", "2024-04-30", D("0.50"), "sourced", 7,
             ("cme_grain_faq", "pl_20230928165949", "pl_20240413052451",)),
        _hard("2024-05-01", "2025-11-02", D("0.40"), "sourced", 52,
             ("cme_grain_faq", "pl_20240519144823", "pl_20251018123959",)),
        _hard("2025-11-03", "2026-04-30", D("0.35"), "sourced", 10,
             ("cme_grain_faq", "pl_20251112101804", "pl_20260418140621",)),
        _hard("2026-05-01", "2026-06-19", D("0.45"), "sourced", 3,
             ("cme_grain_faq", "pl_20260516231307", "pl_20260907145625",)),
    ),
    'ZS': (
        _hard("2019-05-01", "2019-10-31", D("0.65"), "sourced", 4,
             ("cme_grain_faq", "pl_20190509132638", "pl_20190921105213",)),
        _hard("2019-11-01", "2020-11-01", D("0.60"), "sourced", 26,
             ("cme_grain_faq", "pl_20191108140542", "pl_20201005092639",)),
        _hard("2020-11-02", "2021-05-02", D("0.70"), "sourced", 18,
             ("cme_grain_faq", "pl_20201028173809", "pl_20210411030219",)),
        _hard("2021-05-03", "2021-10-31", D("1.00"), "sourced", 10,
             ("cme_grain_faq", "pl_20210519160902", "pl_20211005224651",)),
        _hard("2021-11-01", "2022-05-01", D("0.90"), "sourced", 13,
             ("cme_grain_faq", "pl_20211203073758", "pl_20220324054144",)),
        _hard("2022-05-02", "2022-10-31", D("1.15"), "sourced", 8,
             ("cme_grain_faq", "pl_20220521112448", "pl_20221008031710",)),
        _hard("2022-11-01", "2023-04-30", D("1.00"), "sourced", 7,
             ("cme_grain_faq", "pl_20230323140643", "pl_20230326155246",)),
        _hard("2023-05-01", "2023-10-31", D("1.05"), "sourced", 4,
             ("cme_grain_faq", "pl_20230523200617", "pl_20230707204329",)),
        _hard("2023-11-01", "2024-04-30", D("0.95"), "sourced", 7,
             ("cme_grain_faq", "pl_20230928165949", "pl_20240413052451",)),
        _hard("2024-05-01", "2024-10-31", D("0.85"), "sourced", 12,
             ("cme_grain_faq", "pl_20240519144823", "pl_20241007192846",)),
        _hard("2024-11-01", "2025-04-30", D("0.70"), "sourced", 19,
             ("cme_grain_faq", "pl_20241106132409", "pl_20250428093001",)),
        _hard("2025-05-01", "2025-11-02", D("0.75"), "sourced", 20,
             ("cme_grain_faq", "pl_20250513061945", "pl_20251018123959",)),
        _hard("2025-11-03", "2026-04-30", D("0.70"), "sourced", 10,
             ("cme_grain_faq", "pl_20251112101804", "pl_20260418140621",)),
        _hard("2026-05-01", "2026-06-19", D("0.85"), "sourced", 3,
             ("cme_grain_faq", "pl_20260516231307", "pl_20260907145625",)),
    ),
    'ZM': (
        _hard("2019-05-01", "2020-11-01", D("20.00"), "sourced", 31,
             ("pl_20190408215002", "pl_20201005092639",)),
        _hard("2020-11-02", "2021-05-02", D("25.00"), "sourced", 18,
             ("cme_grain_faq", "pl_20201028173809", "pl_20210411030219",)),
        _hard("2021-05-03", "2021-10-31", D("30.00"), "sourced", 10,
             ("cme_grain_faq", "pl_20210519160902", "pl_20211005224651",)),
        _hard("2021-11-01", "2022-05-01", D("25.00"), "sourced", 13,
             ("cme_grain_faq", "pl_20211203073758", "pl_20220324054144",)),
        _hard("2022-05-02", "2023-10-31", D("30.00"), "sourced", 19,
             ("cme_grain_faq", "pl_20220521112448", "pl_20230707204329",)),
        _hard("2023-11-01", "2024-10-31", D("25.00"), "sourced", 19,
             ("cme_grain_faq", "pl_20230928165949", "pl_20241007192846",)),
        _hard("2024-11-01", "2026-06-19", D("20.00"), "sourced", 52,
             ("cme_grain_faq", "pl_20241106132409", "pl_20260907145625",)),
    ),
    'ZL': (
        _hard("2019-05-01", "2020-11-01", D("0.020"), "sourced", 31,
             ("pl_20190408215002", "pl_20201005092639",)),
        _hard("2020-11-02", "2021-05-02", D("0.025"), "sourced", 18,
             ("cme_grain_faq", "pl_20201028173809", "pl_20210411030219",)),
        _hard("2021-05-03", "2021-10-31", D("0.035"), "sourced", 10,
             ("cme_grain_faq", "pl_20210519160902", "pl_20211005224651",)),
        _hard("2021-11-01", "2022-05-01", D("0.040"), "sourced", 13,
             ("cme_grain_faq", "pl_20211203073758", "pl_20220324054144",)),
        _hard("2022-05-02", "2022-10-31", D("0.050"), "sourced", 8,
             ("cme_grain_faq", "pl_20220521112448", "pl_20221008031710",)),
        _hard("2022-11-01", "2023-04-30", D("0.045"), "sourced", 7,
             ("cme_grain_faq", "pl_20230323140643", "pl_20230326155246",)),
        _hard("2023-05-01", "2024-04-30", D("0.040"), "sourced", 11,
             ("cme_grain_faq", "pl_20230523200617", "pl_20240413052451",)),
        _hard("2024-05-01", "2024-10-31", D("0.035"), "sourced", 12,
             ("cme_grain_faq", "pl_20240519144823", "pl_20241007192846",)),
        _hard("2024-11-01", "2025-11-02", D("0.030"), "sourced", 39,
             ("cme_grain_faq", "pl_20241106132409", "pl_20251018123959",)),
        _hard("2025-11-03", "2026-04-30", D("0.035"), "sourced", 10,
             ("cme_grain_faq", "pl_20251112101804", "pl_20260418140621",)),
        _hard("2026-05-01", "2026-06-19", D("0.045"), "sourced", 3,
             ("cme_grain_faq", "pl_20260516231307", "pl_20260907145625",)),
    ),
    'LE': (
        _hard("2019-05-01", "2020-10-04", D("0.03"), "sourced", 25,
             ("pl_20190408215002", "pl_20201005092639",)),
        _hard("2020-10-05", "2021-05-31", D("0.04"), "sourced", 21,
             ("cme_livestock_notices", "pl_20201028173809", "pl_20210526094607",)),
        _hard("2021-06-01", "2022-05-31", D("0.05"), "sourced", 23,
             ("cme_livestock_notices", "pl_20210615145720", "pl_20220521112448",)),
        _hard("2022-06-01", "2023-05-31", D("0.0575"), "sourced", 15,
             ("cme_livestock_notices", "pl_20220625225942", "pl_20230523200617",)),
        _hard("2023-06-01", "2024-06-02", D("0.0675"), "sourced", 12,
             ("cme_livestock_notices", "pl_20230531231343", "pl_20240520085408",)),
        _hard("2024-06-03", "2024-10-08", D("0.0750"), "sourced", 10,
             ("cme_livestock_notices", "pl_20240616110534", "pl_20241007192846",)),
        _hard("2024-10-09", "2024-11-05", D("0.0650"), "bracketed", 1,
             ("cme_livestock_notices", "pl_20241106132409",)),
        _hard("2024-11-06", "2025-06-01", D("0.0650"), "sourced", 23,
             ("pl_20241106132409", "pl_20250527172431",)),
        _hard("2025-06-02", "2026-05-18", D("0.0725"), "sourced", 24,
             ("cme_livestock_notices", "pl_20250604005334", "pl_20260516231307",)),
        _hard("2026-05-19", "2026-06-19", D("0.0725"), "bracketed", 1,
             ("cme_livestock_notices", "pl_20260820062901",)),
    ),
    'HE': (
        _hard("2019-05-01", "2020-04-01", D("0.03"), "sourced", 13,
             ("pl_20190408215002", "pl_20200401165707",)),
        _hard("2020-04-02", "2020-04-21", D("0.03"), "bracketed", 2,
             ("pl_20200401165707", "pl_20200422053715",)),
        _hard("2020-04-22", "2020-08-19", D("0.0375"), "sourced", 9,
             ("pl_20200422053715", "pl_20200819160616",)),
        _hard("2020-08-20", "2020-09-21", D("0.03"), "bracketed", 2,
             ("pl_20200819160616", "pl_20200922013357",)),
        _hard("2020-09-22", "2021-08-31", D("0.03"), "sourced", 32,
             ("pl_20200922013357", "pl_20210731164704",)),
        _hard("2021-09-01", "2023-08-31", D("0.0475"), "sourced", 33,
             ("cme_livestock_notices", "pl_20210918003230", "pl_20230707204329",)),
        _hard("2023-09-01", "2024-09-03", D("0.0375"), "sourced", 14,
             ("cme_livestock_notices", "pl_20230928165949", "pl_20240901090928",)),
        _hard("2024-09-04", "2024-09-12", D("0.0375"), "bracketed", 1,
             ("cme_livestock_notices", "pl_20240913105737",)),
        _hard("2024-09-13", "2025-08-29", D("0.0400"), "sourced", 37,
             ("pl_20240913105737", "pl_20250829060023",)),
        _hard("2025-08-30", "2025-09-01", D("0.0400"), "bracketed", 2,
             ("pl_20250829060023", "pl_20250830034814",)),
        _hard("2025-09-02", "2026-06-19", D("0.0475"), "sourced", 20,
             ("pl_20250830034814", "pl_20260820062901",)),
    ),
    'NQ': (
        _eq("2019-05-01", "2019-09-23", 5, "15:00", "sourced", 5,
             ("pl_20190408215002", "pl_20190921105213",)),
        _eq("2019-09-24", "2019-11-07", 5, "15:00", "bracketed", 2,
             ("pl_20190921105213", "pl_20191108140542",)),
        _eq("2019-11-08", "2020-09-30", 5, "14:25", "sourced", 26,
             ("pl_20191108140542", "pl_20201005092639",)),
        _eq("2020-10-01", "2020-11-01", 5, "14:25", "bracketed", 2,
             ("pl_20201005092639", "pl_20201028173809",)),
        _eq("2020-11-02", "2026-06-19", 7, "14:25", "sourced", 135,
             ("pl_20201028173809", "pl_20260907145625",)),
    ),
    'MNQ': (
        _eq("2019-05-01", "2019-09-23", 5, "15:00", "sourced", 5,
             ("pl_20190408215002", "pl_20190921105213",)),
        _eq("2019-09-24", "2019-11-07", 5, "15:00", "bracketed", 2,
             ("pl_20190921105213", "pl_20191108140542",)),
        _eq("2019-11-08", "2020-09-30", 5, "14:25", "sourced", 26,
             ("pl_20191108140542", "pl_20201005092639",)),
        _eq("2020-10-01", "2020-11-01", 5, "14:25", "bracketed", 2,
             ("pl_20201005092639", "pl_20201028173809",)),
        _eq("2020-11-02", "2026-06-19", 7, "14:25", "sourced", 135,
             ("pl_20201028173809", "pl_20260907145625",)),
    ),
    'RTY': (
        _eq("2019-05-01", "2019-09-23", 5, "15:00", "sourced", 5,
             ("pl_20190408215002", "pl_20190921105213",)),
        _eq("2019-09-24", "2019-11-07", 5, "15:00", "bracketed", 2,
             ("pl_20190921105213", "pl_20191108140542",)),
        _eq("2019-11-08", "2020-09-30", 5, "14:25", "sourced", 26,
             ("pl_20191108140542", "pl_20201005092639",)),
        _eq("2020-10-01", "2020-11-01", 5, "14:25", "bracketed", 2,
             ("pl_20201005092639", "pl_20201028173809",)),
        _eq("2020-11-02", "2026-06-19", 7, "14:25", "sourced", 135,
             ("pl_20201028173809", "pl_20260907145625",)),
    ),
    'M2K': (
        _eq("2019-05-01", "2019-09-23", 5, "15:00", "sourced", 5,
             ("pl_20190408215002", "pl_20190921105213",)),
        _eq("2019-09-24", "2019-11-07", 5, "15:00", "bracketed", 2,
             ("pl_20190921105213", "pl_20191108140542",)),
        _eq("2019-11-08", "2020-09-30", 5, "14:25", "sourced", 26,
             ("pl_20191108140542", "pl_20201005092639",)),
        _eq("2020-10-01", "2020-11-01", 5, "14:25", "bracketed", 2,
             ("pl_20201005092639", "pl_20201028173809",)),
        _eq("2020-11-02", "2026-06-19", 7, "14:25", "sourced", 135,
             ("pl_20201028173809", "pl_20260907145625",)),
    ),
    'YM': (
        _eq("2019-05-01", "2019-09-23", 5, "15:00", "sourced", 5,
             ("pl_20190408215002", "pl_20190921105213",)),
        _eq("2019-09-24", "2019-11-07", 5, "15:00", "bracketed", 2,
             ("pl_20190921105213", "pl_20191108140542",)),
        _eq("2019-11-08", "2020-09-30", 5, "14:25", "sourced", 26,
             ("pl_20191108140542", "pl_20201005092639",)),
        _eq("2020-10-01", "2020-11-01", 5, "14:25", "bracketed", 2,
             ("pl_20201005092639", "pl_20201028173809",)),
        _eq("2020-11-02", "2026-06-19", 7, "14:25", "sourced", 135,
             ("pl_20201028173809", "pl_20260907145625",)),
    ),
    'MYM': (
        _eq("2019-05-01", "2019-09-23", 5, "15:00", "sourced", 5,
             ("pl_20190408215002", "pl_20190921105213",)),
        _eq("2019-09-24", "2019-11-07", 5, "15:00", "bracketed", 2,
             ("pl_20190921105213", "pl_20191108140542",)),
        _eq("2019-11-08", "2020-09-30", 5, "14:25", "sourced", 26,
             ("pl_20191108140542", "pl_20201005092639",)),
        _eq("2020-10-01", "2020-11-01", 5, "14:25", "bracketed", 2,
             ("pl_20201005092639", "pl_20201028173809",)),
        _eq("2020-11-02", "2026-06-19", 7, "14:25", "sourced", 135,
             ("pl_20201028173809", "pl_20260907145625",)),
    ),
    'ES': (
        _eq("2019-05-01", "2019-09-23", 5, "15:00", "sourced", 5,
             ("pl_20190408215002", "pl_20190921105213",)),
        _eq("2019-09-24", "2019-11-07", 5, "15:00", "bracketed", 2,
             ("pl_20190921105213", "pl_20191108140542",)),
        _eq("2019-11-08", "2020-09-30", 5, "14:25", "sourced", 26,
             ("pl_20191108140542", "pl_20201005092639",)),
        _eq("2020-10-01", "2020-11-01", 5, "14:25", "bracketed", 2,
             ("pl_20201005092639", "pl_20201028173809",)),
        _eq("2020-11-02", "2026-06-19", 7, "14:25", "sourced", 135,
             ("pl_20201028173809", "pl_20260907145625",)),
    ),
    'MES': (
        _eq("2019-05-01", "2019-09-23", 5, "15:00", "sourced", 5,
             ("pl_20190408215002", "pl_20190921105213",)),
        _eq("2019-09-24", "2019-11-07", 5, "15:00", "bracketed", 2,
             ("pl_20190921105213", "pl_20191108140542",)),
        _eq("2019-11-08", "2020-09-30", 5, "14:25", "sourced", 26,
             ("pl_20191108140542", "pl_20201005092639",)),
        _eq("2020-10-01", "2020-11-01", 5, "14:25", "bracketed", 2,
             ("pl_20201005092639", "pl_20201028173809",)),
        _eq("2020-11-02", "2026-06-19", 7, "14:25", "sourced", 135,
             ("pl_20201028173809", "pl_20260907145625",)),
    ),
    'ZT': (
        _dcb("2019-05-01", "2020-10-09", None, None, "pending", 0,
             ()),
        _dcb("2020-10-10", "2026-06-19", "points", D("0.75"), "sourced", 15,
             ("pl_20260516231307", "spfl_20260310032723",)),
    ),
    'ZF': (
        _dcb("2019-05-01", "2020-10-09", None, None, "pending", 0,
             ()),
        _dcb("2020-10-10", "2026-06-19", "points", D("1.50"), "sourced", 15,
             ("pl_20260516231307", "spfl_20260310032723",)),
    ),
    'ZN': (
        _dcb("2019-05-01", "2020-10-09", None, None, "pending", 0,
             ()),
        _dcb("2020-10-10", "2026-06-19", "points", D("2.00"), "sourced", 15,
             ("pl_20260516231307", "spfl_20260310032723",)),
    ),
    'TN': (
        _dcb("2019-05-01", "2020-10-09", None, None, "pending", 0,
             ()),
        _dcb("2020-10-10", "2026-06-19", "points", D("3.00"), "sourced", 15,
             ("pl_20260516231307", "spfl_20260310032723",)),
    ),
    'ZB': (
        _dcb("2019-05-01", "2020-10-09", None, None, "pending", 0,
             ()),
        _dcb("2020-10-10", "2026-06-19", "points", D("4.50"), "sourced", 15,
             ("pl_20260516231307", "spfl_20260310032723",)),
    ),
    'UB': (
        _dcb("2019-05-01", "2020-10-09", None, None, "pending", 0,
             ()),
        _dcb("2020-10-10", "2026-06-19", "points", D("8.00"), "sourced", 15,
             ("pl_20260516231307", "spfl_20260310032723",)),
    ),
    '6E': (
        _dcb("2019-05-01", "2022-01-23", None, None, "pending", 0,
             ()),
        _dcb("2022-01-24", "2026-03-10", "pct", D("4"), "sourced", 10,
             ("spfl_20220124234130", "spfl_20260310032723",)),
        _dcb("2026-03-11", "2026-06-19", "pct", D("4"), "carried", 1,
             ("spfl_20260310032723",)),
    ),
    'M6E': (
        _dcb("2019-05-01", "2022-01-23", None, None, "pending", 0,
             ()),
        _dcb("2022-01-24", "2026-03-10", "pct", D("4"), "sourced", 10,
             ("spfl_20220124234130", "spfl_20260310032723",)),
        _dcb("2026-03-11", "2026-06-19", "pct", D("4"), "carried", 1,
             ("spfl_20260310032723",)),
    ),
    'E7': (
        _dcb("2019-05-01", "2022-01-23", None, None, "pending", 0,
             ()),
        _dcb("2022-01-24", "2026-03-10", "pct", D("4"), "sourced", 10,
             ("spfl_20220124234130", "spfl_20260310032723",)),
        _dcb("2026-03-11", "2026-06-19", "pct", D("4"), "carried", 1,
             ("spfl_20260310032723",)),
    ),
    '6A': (
        _dcb("2019-05-01", "2022-01-23", None, None, "pending", 0,
             ()),
        _dcb("2022-01-24", "2026-03-10", "pct", D("4"), "sourced", 10,
             ("spfl_20220124234130", "spfl_20260310032723",)),
        _dcb("2026-03-11", "2026-06-19", "pct", D("4"), "carried", 1,
             ("spfl_20260310032723",)),
    ),
    'M6A': (
        _dcb("2019-05-01", "2022-01-23", None, None, "pending", 0,
             ()),
        _dcb("2022-01-24", "2026-03-10", "pct", D("4"), "sourced", 10,
             ("spfl_20220124234130", "spfl_20260310032723",)),
        _dcb("2026-03-11", "2026-06-19", "pct", D("4"), "carried", 1,
             ("spfl_20260310032723",)),
    ),
    '6B': (
        _dcb("2019-05-01", "2022-01-23", None, None, "pending", 0,
             ()),
        _dcb("2022-01-24", "2026-03-10", "pct", D("4"), "sourced", 10,
             ("spfl_20220124234130", "spfl_20260310032723",)),
        _dcb("2026-03-11", "2026-06-19", "pct", D("4"), "carried", 1,
             ("spfl_20260310032723",)),
    ),
    'M6B': (
        _dcb("2019-05-01", "2022-01-23", None, None, "pending", 0,
             ()),
        _dcb("2022-01-24", "2026-03-10", "pct", D("4"), "sourced", 10,
             ("spfl_20220124234130", "spfl_20260310032723",)),
        _dcb("2026-03-11", "2026-06-19", "pct", D("4"), "carried", 1,
             ("spfl_20260310032723",)),
    ),
    '6C': (
        _dcb("2019-05-01", "2022-01-23", None, None, "pending", 0,
             ()),
        _dcb("2022-01-24", "2026-03-10", "pct", D("4"), "sourced", 10,
             ("spfl_20220124234130", "spfl_20260310032723",)),
        _dcb("2026-03-11", "2026-06-19", "pct", D("4"), "carried", 1,
             ("spfl_20260310032723",)),
    ),
    '6J': (
        _dcb("2019-05-01", "2022-01-23", None, None, "pending", 0,
             ()),
        _dcb("2022-01-24", "2026-03-10", "pct", D("4"), "sourced", 10,
             ("spfl_20220124234130", "spfl_20260310032723",)),
        _dcb("2026-03-11", "2026-06-19", "pct", D("4"), "carried", 1,
             ("spfl_20260310032723",)),
    ),
    '6S': (
        _dcb("2019-05-01", "2022-01-23", None, None, "pending", 0,
             ()),
        _dcb("2022-01-24", "2026-03-10", "pct", D("4"), "sourced", 10,
             ("spfl_20220124234130", "spfl_20260310032723",)),
        _dcb("2026-03-11", "2026-06-19", "pct", D("4"), "carried", 1,
             ("spfl_20260310032723",)),
    ),
    '6N': (
        _dcb("2019-05-01", "2022-01-23", None, None, "pending", 0,
             ()),
        _dcb("2022-01-24", "2026-03-10", "pct", D("4"), "sourced", 10,
             ("spfl_20220124234130", "spfl_20260310032723",)),
        _dcb("2026-03-11", "2026-06-19", "pct", D("4"), "carried", 1,
             ("spfl_20260310032723",)),
    ),
    'CL': (
        _dcb("2019-05-01", "2019-07-17", None, None, "pending", 0,
             ()),
        _dcb("2019-07-18", "2020-03-18", "pct", D("7"), "sourced", 1,
             ("spfl_20190718234942",)),
        _dcb("2020-03-19", "2021-07-24", "pct", D("15"), "sourced", 5,
             ("pl_20200325160849", "spfl_20210724172159",)),
        _dcb("2021-07-25", "2022-01-23", "pct", D("10"), "bracketed", 2,
             ("pl_20200325160849", "spfl_20220124234130",)),
        _dcb("2022-01-24", "2026-03-10", "pct", D("10"), "sourced", 10,
             ("spfl_20220124234130", "spfl_20260310032723",)),
        _dcb("2026-03-11", "2026-06-19", "pct", D("10"), "carried", 1,
             ("spfl_20260310032723",)),
    ),
    'MCL': (
        _dcb("2019-05-01", "2019-07-17", None, None, "pending", 0,
             ()),
        _dcb("2019-07-18", "2020-03-18", "pct", D("7"), "sourced", 1,
             ("spfl_20190718234942",)),
        _dcb("2020-03-19", "2021-07-24", "pct", D("15"), "sourced", 5,
             ("pl_20200325160849", "spfl_20210724172159",)),
        _dcb("2021-07-25", "2022-01-23", "pct", D("10"), "bracketed", 2,
             ("pl_20200325160849", "spfl_20220124234130",)),
        _dcb("2022-01-24", "2026-03-10", "pct", D("10"), "sourced", 10,
             ("spfl_20220124234130", "spfl_20260310032723",)),
        _dcb("2026-03-11", "2026-06-19", "pct", D("10"), "carried", 1,
             ("spfl_20260310032723",)),
    ),
    'QM': (
        _dcb("2019-05-01", "2019-07-17", None, None, "pending", 0,
             ()),
        _dcb("2019-07-18", "2020-03-18", "pct", D("7"), "sourced", 1,
             ("spfl_20190718234942",)),
        _dcb("2020-03-19", "2021-07-24", "pct", D("15"), "sourced", 5,
             ("pl_20200325160849", "spfl_20210724172159",)),
        _dcb("2021-07-25", "2022-01-23", "pct", D("10"), "bracketed", 2,
             ("pl_20200325160849", "spfl_20220124234130",)),
        _dcb("2022-01-24", "2026-03-10", "pct", D("10"), "sourced", 10,
             ("spfl_20220124234130", "spfl_20260310032723",)),
        _dcb("2026-03-11", "2026-06-19", "pct", D("10"), "carried", 1,
             ("spfl_20260310032723",)),
    ),
    'NG': (
        _dcb("2019-05-01", "2019-07-17", None, None, "pending", 0,
             ()),
        _dcb("2019-07-18", "2021-07-24", "pct", D("7"), "sourced", 5,
             ("spfl_20190718234942", "spfl_20210724172159",)),
        _dcb("2021-07-25", "2022-01-23", "pct", D("7"), "bracketed", 2,
             ("spfl_20210724172159", "spfl_20220124234130",)),
        _dcb("2022-01-24", "2026-03-10", "pct", D("10"), "sourced", 10,
             ("spfl_20220124234130", "spfl_20260310032723",)),
        _dcb("2026-03-11", "2026-06-19", "pct", D("10"), "carried", 1,
             ("spfl_20260310032723",)),
    ),
    'MNG': (
        _dcb("2019-05-01", "2019-07-17", None, None, "pending", 0,
             ()),
        _dcb("2019-07-18", "2021-07-24", "pct", D("7"), "sourced", 5,
             ("spfl_20190718234942", "spfl_20210724172159",)),
        _dcb("2021-07-25", "2022-01-23", "pct", D("7"), "bracketed", 2,
             ("spfl_20210724172159", "spfl_20220124234130",)),
        _dcb("2022-01-24", "2026-03-10", "pct", D("10"), "sourced", 10,
             ("spfl_20220124234130", "spfl_20260310032723",)),
        _dcb("2026-03-11", "2026-06-19", "pct", D("10"), "carried", 1,
             ("spfl_20260310032723",)),
    ),
    'QG': (
        _dcb("2019-05-01", "2019-07-17", None, None, "pending", 0,
             ()),
        _dcb("2019-07-18", "2021-07-24", "pct", D("7"), "sourced", 5,
             ("spfl_20190718234942", "spfl_20210724172159",)),
        _dcb("2021-07-25", "2022-01-23", "pct", D("7"), "bracketed", 2,
             ("spfl_20210724172159", "spfl_20220124234130",)),
        _dcb("2022-01-24", "2026-03-10", "pct", D("10"), "sourced", 10,
             ("spfl_20220124234130", "spfl_20260310032723",)),
        _dcb("2026-03-11", "2026-06-19", "pct", D("10"), "carried", 1,
             ("spfl_20260310032723",)),
    ),
    'RB': (
        _dcb("2019-05-01", "2019-07-17", None, None, "pending", 0,
             ()),
        _dcb("2019-07-18", "2020-03-12", "pct", D("7"), "sourced", 1,
             ("spfl_20190718234942",)),
        _dcb("2020-03-13", "2021-07-24", "pct", D("15"), "sourced", 5,
             ("pl_20200325160849", "spfl_20210724172159",)),
        _dcb("2021-07-25", "2022-01-23", "pct", D("10"), "bracketed", 2,
             ("pl_20200325160849", "spfl_20220124234130",)),
        _dcb("2022-01-24", "2026-03-10", "pct", D("10"), "sourced", 10,
             ("spfl_20220124234130", "spfl_20260310032723",)),
        _dcb("2026-03-11", "2026-06-19", "pct", D("10"), "carried", 1,
             ("spfl_20260310032723",)),
    ),
    'HO': (
        _dcb("2019-05-01", "2019-07-17", None, None, "pending", 0,
             ()),
        _dcb("2019-07-18", "2020-03-12", "pct", D("7"), "sourced", 1,
             ("spfl_20190718234942",)),
        _dcb("2020-03-13", "2021-07-24", "pct", D("15"), "sourced", 5,
             ("pl_20200325160849", "spfl_20210724172159",)),
        _dcb("2021-07-25", "2022-01-23", "pct", D("10"), "bracketed", 2,
             ("pl_20200325160849", "spfl_20220124234130",)),
        _dcb("2022-01-24", "2026-03-10", "pct", D("10"), "sourced", 10,
             ("spfl_20220124234130", "spfl_20260310032723",)),
        _dcb("2026-03-11", "2026-06-19", "pct", D("10"), "carried", 1,
             ("spfl_20260310032723",)),
    ),
    'GC': (
        _dcb("2019-05-01", "2019-07-17", None, None, "pending", 0,
             ()),
        _dcb("2019-07-18", "2019-07-18", "pct", D("5"), "sourced", 1,
             ("spfl_20190718234942",)),
        _dcb("2019-07-19", "2020-06-17", "pct", D("5"), "bracketed", 2,
             ("spfl_20190718234942", "spfl_20200618002851",)),
        _dcb("2020-06-18", "2026-03-10", "pct", D("10"), "sourced", 14,
             ("spfl_20200618002851", "spfl_20260310032723",)),
        _dcb("2026-03-11", "2026-06-19", "pct", D("10"), "carried", 1,
             ("spfl_20260310032723",)),
    ),
    'MGC': (
        _dcb("2019-05-01", "2019-07-17", None, None, "pending", 0,
             ()),
        _dcb("2019-07-18", "2019-07-18", "pct", D("5"), "sourced", 1,
             ("spfl_20190718234942",)),
        _dcb("2019-07-19", "2020-06-17", "pct", D("5"), "bracketed", 2,
             ("spfl_20190718234942", "spfl_20200618002851",)),
        _dcb("2020-06-18", "2026-03-10", "pct", D("10"), "sourced", 14,
             ("spfl_20200618002851", "spfl_20260310032723",)),
        _dcb("2026-03-11", "2026-06-19", "pct", D("10"), "carried", 1,
             ("spfl_20260310032723",)),
    ),
    'SI': (
        _dcb("2019-05-01", "2019-07-17", None, None, "pending", 0,
             ()),
        _dcb("2019-07-18", "2019-07-18", "pct", D("5"), "sourced", 1,
             ("spfl_20190718234942",)),
        _dcb("2019-07-19", "2020-06-17", "pct", D("5"), "bracketed", 2,
             ("spfl_20190718234942", "spfl_20200618002851",)),
        _dcb("2020-06-18", "2026-03-10", "pct", D("10"), "sourced", 14,
             ("spfl_20200618002851", "spfl_20260310032723",)),
        _dcb("2026-03-11", "2026-06-19", "pct", D("10"), "carried", 1,
             ("spfl_20260310032723",)),
    ),
    'SIL': (
        _dcb("2019-05-01", "2019-07-17", None, None, "pending", 0,
             ()),
        _dcb("2019-07-18", "2019-07-18", "pct", D("5"), "sourced", 1,
             ("spfl_20190718234942",)),
        _dcb("2019-07-19", "2020-06-17", "pct", D("5"), "bracketed", 2,
             ("spfl_20190718234942", "spfl_20200618002851",)),
        _dcb("2020-06-18", "2026-03-10", "pct", D("10"), "sourced", 14,
             ("spfl_20200618002851", "spfl_20260310032723",)),
        _dcb("2026-03-11", "2026-06-19", "pct", D("10"), "carried", 1,
             ("spfl_20260310032723",)),
    ),
    'HG': (
        _dcb("2019-05-01", "2019-07-17", None, None, "pending", 0,
             ()),
        _dcb("2019-07-18", "2019-07-18", "pct", D("5"), "sourced", 1,
             ("spfl_20190718234942",)),
        _dcb("2019-07-19", "2020-06-17", "pct", D("5"), "bracketed", 2,
             ("spfl_20190718234942", "spfl_20200618002851",)),
        _dcb("2020-06-18", "2026-03-10", "pct", D("10"), "sourced", 14,
             ("spfl_20200618002851", "spfl_20260310032723",)),
        _dcb("2026-03-11", "2026-06-19", "pct", D("10"), "carried", 1,
             ("spfl_20260310032723",)),
    ),
    'MHG': (
        _dcb("2019-05-01", "2019-07-17", None, None, "pending", 0,
             ()),
        _dcb("2019-07-18", "2019-07-18", "pct", D("5"), "sourced", 1,
             ("spfl_20190718234942",)),
        _dcb("2019-07-19", "2020-06-17", "pct", D("5"), "bracketed", 2,
             ("spfl_20190718234942", "spfl_20200618002851",)),
        _dcb("2020-06-18", "2026-03-10", "pct", D("10"), "sourced", 14,
             ("spfl_20200618002851", "spfl_20260310032723",)),
        _dcb("2026-03-11", "2026-06-19", "pct", D("10"), "carried", 1,
             ("spfl_20260310032723",)),
    ),
    'MBT': (
        _dcb("2021-05-03", "2026-06-19", "pct", D("10"), "sourced", 16,
             ("pl_20260516231307", "spfl_20260310032723",)),
    ),
}
TABLE_WINDOW = (date(2019, 5, 1), date(2026, 6, 19))
HARD_LIMIT_PRODUCTS: frozenset[str] = frozenset(
    r for r, ps in LIMITS.items() if ps[0].kind is not LimitKind.DCB_ONLY)


def limit_period(root: str, trade_date: date) -> LimitPeriod:
    """The limit period in force on ``trade_date``; raises LimitPending when unsourced."""
    periods = LIMITS.get(root)
    if periods is None:
        raise KeyError(f"{root!r} has no price-limit table")
    for p in periods:
        if p.start <= trade_date <= p.end:
            if p.status == "pending":
                raise LimitPending(f"{root} {trade_date}: no CME source for the limit "
                                   f"({p.start}..{p.end}, pending)")
            return p
    raise LimitPending(f"{root} {trade_date}: outside the table "
                       f"({periods[0].start}..{periods[-1].end})")


# --------------------------------------------------------- settlement window ----
@dataclass(frozen=True)
class Window:
    start_ct: time
    end_ct: time  # exclusive
    source: str


_WIKI = "cme_wiki_settlement_times"
_EQUITY_FIXING = Window(time(14, 59, 30), time(15, 0), "pl_* (equity fixing price, VWAP "
                        "14:59:30-15:00:00 CT)")
SETTLEMENT_WINDOW_CT: dict[str, Window] = {
    "equity": _EQUITY_FIXING,  # the limit reference is the fixing price (CME price-limit page)
    "rates": Window(time(13, 59, 30), time(14, 0), _WIKI + " Treasuries"),
    "fx": Window(time(13, 59, 30), time(14, 0), _WIKI + " FX"),
    "energy": Window(time(13, 28), time(13, 30), _WIKI + " Energy Products (14:28-14:30 ET)"),
    "gold": Window(time(12, 29), time(12, 30), _WIKI + " Gold (13:29-13:30 ET)"),
    "silver": Window(time(12, 24), time(12, 25), _WIKI + " Silver (13:24-13:25 ET)"),
    "copper": Window(time(11, 59), time(12, 0), _WIKI + " Copper (12:59-13:00 ET)"),
    "grains": Window(time(13, 14), time(13, 15), _WIKI + " Grains/Oilseeds"),
    "livestock": Window(time(12, 59, 30), time(13, 0), _WIKI + " Livestock"),
    "crypto": Window(time(14, 59), time(15, 0), _WIKI + " Bitcoin"),
}


def _window_key(root: str) -> str:
    p = product(root)
    return p.subgroup if p.group == "metals" else p.group


def _early_settlement(group: str, day: date) -> time | None:
    """A CME-published early settlement time from the group module, where it has one (rates)."""
    mod = importlib.import_module(f"data.calendars.{group}") if group != "equity" else None
    table = getattr(mod, "EARLY_SETTLEMENT_CT", {}) if mod is not None else {}
    return table.get(day)


def _dt(t: time, delta: timedelta) -> time:
    return (datetime.combine(date(2000, 1, 3), t) + delta).time()


def settlement_window_ct(root: str, trade_date: date,
                         holidays: GroupHolidays | None = None) -> Window:
    """The CT window whose bars give the settlement proxy of ``trade_date``.

    Regular days: CME's settlement period for the product (equity: the fixing-price window).
    A CME-published early settlement time (rates' EARLY_SETTLEMENT_CT): the regular length
    ending there. An early halt at or before the regular window's end: the regular length ending
    at the halt, i.e. the last traded minute(s) (a proxy reading, R-P3: CME moves settlement on
    early-close days to times that differ by group)."""
    key = _window_key(root)
    reg = SETTLEMENT_WINDOW_CT[key]
    length = datetime.combine(date(2000, 1, 3), reg.end_ct) - datetime.combine(
        date(2000, 1, 3), reg.start_ct)
    group = product(root).group
    early = _early_settlement(group, trade_date)
    if early is not None and early < reg.end_ct:
        return Window(_dt(early, -length), early, f"data.calendars.{group}.EARLY_SETTLEMENT_CT")
    cal = (holidays if holidays is not None else default_holidays())[group]
    hol = cal.get(trade_date)
    if hol is not None and hol.kind is HolidayKind.FULL_CLOSURE:
        raise ValueError(f"{root}: {trade_date} is a full closure; no settlement")
    if hol is not None and hol.halt_ct is not None and hol.halt_ct <= reg.end_ct:
        return Window(_dt(hol.halt_ct, -length), hol.halt_ct,
                      f"early halt {hol.halt_ct:%H:%M} ({hol.name}); proxy reading R-P3")
    return reg


def settlement_window_utc(root: str, trade_date: date,
                          holidays: GroupHolidays | None = None) -> tuple[datetime, datetime]:
    w = settlement_window_ct(root, trade_date, holidays)
    start = datetime.combine(trade_date, w.start_ct, tzinfo=CT)
    end = datetime.combine(trade_date, w.end_ct, tzinfo=CT)
    return start.astimezone(ZoneInfo("UTC")), end.astimezone(ZoneInfo("UTC"))


@dataclass(frozen=True)
class BarPrint:
    """One one-minute bar for the settlement proxy: start instant, close, volume."""

    start: datetime
    close: Price
    volume: int


@dataclass(frozen=True)
class SettlementProxy:
    value: Decimal
    method: str  # "vwap_close" | "last_close_before_window_end"
    bars_used: int


def settlement_proxy(bars: Iterable[BarPrint], window_start: datetime,
                     window_end: datetime) -> SettlementProxy | None:
    """D9.7's proxy: the volume-weighted close of the one-minute bars whose minute overlaps
    [window_start, window_end). With no volume in the window, the last close of a bar starting
    before window_end (a flagged fallback, R-P2). None when no bar precedes window_end."""
    if window_start.tzinfo is None or window_end.tzinfo is None:
        raise ValueError("window instants must be timezone-aware")
    lo = window_start.replace(second=0, microsecond=0)
    num, den, used = D(0), 0, 0
    last: tuple[datetime, Decimal] | None = None
    for b in bars:
        if b.start.tzinfo is None:
            raise ValueError("bar instants must be timezone-aware")
        if b.start >= window_end:
            continue
        close = to_decimal(b.close)
        if last is None or b.start > last[0]:
            last = (b.start, close)
        if b.start >= lo and b.volume > 0:
            num += close * b.volume
            den += b.volume
            used += 1
    if den > 0:
        return SettlementProxy(num / den, "vwap_close", used)
    if last is None:
        return None
    return SettlementProxy(last[1], "last_close_before_window_end", 0)


# -------------------------------------------------------------- the band ----
@dataclass(frozen=True)
class Band:
    """Price Limit% up and down (fractions; None = no limit on that side) around the prior
    settlement, as Topstep's formula uses them."""

    root: str
    kind: LimitKind
    up: Decimal | None  # Price Limit% as a fraction of the prior settlement
    down: Decimal | None
    reading: str
    period: LimitPeriod | None
    up_amount: Decimal | None = None  # the limit in vendor price units (exact for price units)
    down_amount: Decimal | None = None


def _equity_sides(period: LimitPeriod, ts: datetime) -> tuple[Decimal | None, Decimal | None, str]:
    t = ts.astimezone(CT).time()
    assert period.eth_pct is not None and period.rth_7pct_until is not None
    eth = D(period.eth_pct) / 100
    if time(8, 30) <= t < period.rth_7pct_until:
        return None, D("0.07"), "RTH: 7% down only"
    if period.rth_7pct_until <= t < time(15, 0):
        return None, D("0.20"), "RTH late: 20% down only"
    return eth, eth, f"ETH: {period.eth_pct}% up and down"


def limit_band(root: str, trade_date: date, ts: datetime, prior_settlement: Price,
               reading: DcbReading = DCB_READING_DEFAULT) -> Band:
    if ts.tzinfo is None:
        raise ValueError("timestamp must be timezone-aware")
    s = to_decimal(prior_settlement)
    if s <= 0:
        raise ValueError(f"{root}: prior settlement {s} must be positive")
    if root not in LIMITS:
        raise KeyError(f"{root!r} has no price-limit table")
    if LIMITS[root][0].kind is LimitKind.DCB_ONLY and reading is DcbReading.NO_LOCK_LIMIT:
        return Band(root, LimitKind.DCB_ONLY, None, None, "DCB only: no lock limit", None)
    period = limit_period(root, trade_date)
    factor = product(root).vendor_price_factor
    if period.kind is LimitKind.HARD_DAILY:
        assert period.amount is not None
        amt = period.amount * factor
        return Band(root, period.kind, amt / s, amt / s, f"hard limit {period.amount}", period,
                    amt, amt)
    if period.kind is LimitKind.EQUITY_BANDS:
        up, down, why = _equity_sides(period, ts)
        return Band(root, period.kind, up, down, why, period,
                    None if up is None else s * up, None if down is None else s * down)
    assert period.dcb_value is not None
    amt = s * period.dcb_value / 100 if period.dcb_kind == "pct" else period.dcb_value * factor
    return Band(root, period.kind, amt / s, amt / s, f"DCB variant {period.dcb_value} "
                f"{period.dcb_kind} as a limit (alternative reading)", period, amt, amt)


@dataclass(frozen=True)
class StopLevels:
    upper: Decimal | None  # stop trading at or above
    lower: Decimal | None  # stop trading at or below
    band: Band


def stop_levels(band: Band, prior_settlement: Price) -> StopLevels:
    """Topstep: S x (1 + PL% - 2%) above, S x (1 - PL% + 2%) below, computed as
    S + amount - 2% x S so a limit in price units stays exact."""
    s = to_decimal(prior_settlement)
    buffer = s * TOPSTEP_BUFFER
    upper = None if band.up_amount is None else s + band.up_amount - buffer
    lower = None if band.down_amount is None else s - band.down_amount + buffer
    return StopLevels(upper, lower, band)


def limit_prices(band: Band, prior_settlement: Price) -> tuple[Decimal | None, Decimal | None]:
    """The limit prices themselves, S x (1 + PL%) and S x (1 - PL%), for the lock rule."""
    s = to_decimal(prior_settlement)
    up = None if band.up_amount is None else s + band.up_amount
    down = None if band.down_amount is None else s - band.down_amount
    return up, down


def beyond_stop(price: Price, levels: StopLevels) -> str | None:
    """"above" / "below" when the price is at or beyond a stop level, else None. A band narrower
    than 2% makes both true at once; "above" is then returned first."""
    p = to_decimal(price)
    if levels.upper is not None and p >= levels.upper:
        return "above"
    if levels.lower is not None and p <= levels.lower:
        return "below"
    return None


def check_price_limit_entry(root: str, trade_date: date, ts: datetime, prior_settlement: Price,
                            price: Price, reading: DcbReading = DCB_READING_DEFAULT
                            ) -> Refusal | None:
    """D9.7: no entry while the price is at or beyond either stop level."""
    band = limit_band(root, trade_date, ts, prior_settlement, reading)
    levels = stop_levels(band, prior_settlement)
    side = beyond_stop(price, levels)
    if side is None:
        return None
    return Refusal(
        "price_limit_zone_no_entry",
        f"{root} {to_decimal(price)} is {side} the stop level "
        f"({levels.upper if side == 'above' else levels.lower}) = S {to_decimal(prior_settlement)}"
        f" x (1 {'+' if side == 'above' else '-'} PL% {'-' if side == 'above' else '+'} 2%); "
        f"{band.reading}",
    )


@dataclass(frozen=True)
class PriceLimitExit:
    """The forced D9.7 exit: fills at the next bar's open, exempt from the event-minute fill
    guard, event-window cost; subject to the locked-market rule."""

    root: str
    side: str
    quantity: int
    fill: str = "next_bar_open"
    fill_guard_exempt: bool = True
    cost: str = "event_window"
    reason: str = ""


def required_price_limit_exit(root: str, trade_date: date, ts: datetime, position: int,
                              prior_settlement: Price, price: Price,
                              reading: DcbReading = DCB_READING_DEFAULT
                              ) -> PriceLimitExit | None:
    if position == 0:
        return None
    band = limit_band(root, trade_date, ts, prior_settlement, reading)
    levels = stop_levels(band, prior_settlement)
    side = beyond_stop(price, levels)
    if side is None:
        return None
    return PriceLimitExit(root, "sell" if position > 0 else "buy", abs(position),
                          reason=f"{to_decimal(price)} {side} stop level; {band.reading}")


# -------------------------------------------------------- locked markets ----
@dataclass(frozen=True)
class Bar:
    open: Price
    high: Price
    low: Price
    close: Price


@dataclass(frozen=True)
class LockedFill:
    index: int | None  # index into ``bars`` of the fill bar; None = still locked at the end
    price: Decimal | None
    flagged: bool  # True when at least one bar was skipped as locked (R-08)
    bars_waited: int


def locked_exit_fill(side: str, limit_up: Price | None, limit_down: Price | None,
                     bars: Sequence[Bar], tolerance: Price = 0) -> LockedFill:
    """R-08. ``bars[0]`` is the bar whose open would fill the exit. A sell (long exit) is
    blocked while the bar shows the market locked at limit-down (high <= limit_down +
    tolerance); a buy (short exit) while locked at limit-up (low >= limit_up - tolerance). The
    exit fills at the open of the first bar that trades through the limit price. A side with no
    limit (None) cannot lock. ``tolerance`` (vendor units) widens the lock test for a proxy
    settlement that may sit a few ticks off CME's (default 0; flag R-P1). ``limit_prices``
    gives (limit_up, limit_down)."""
    if side not in ("buy", "sell"):
        raise ValueError(f"side {side!r} is not buy or sell")
    if not bars:
        return LockedFill(None, None, False, 0)
    limit_price = limit_down if side == "sell" else limit_up
    if limit_price is None:
        return LockedFill(0, to_decimal(bars[0].open), False, 0)
    lim, tol = to_decimal(limit_price), to_decimal(tolerance)
    for i, bar in enumerate(bars):
        hi, lo = to_decimal(bar.high), to_decimal(bar.low)
        locked = hi <= lim + tol if side == "sell" else lo >= lim - tol
        if not locked:
            return LockedFill(i, to_decimal(bar.open), i > 0, i)
    return LockedFill(None, None, True, len(bars))
