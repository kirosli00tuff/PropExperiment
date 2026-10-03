"""XFA account parameters of ML route v2 (docs/STAGE_E_ML_V2_DESIGN.md V2.0, V2.8, V2.9).

``AccountSpec`` holds, in dollars, what the sizing (V2.8), the portfolio caps (V2.8) and the payout
simulator (V2.9) need about one Express Funded Account. Two instances:

- ``ACCOUNT_50K`` is derived from rules.xfa_rules.XFA_50K (cents to dollars, the same values) plus
  the facts file's DLL ($1,000, F12.2c), the DLL doubling of the payout caps (F12.2b) and the 90/10
  split (F9.1). The frozen engine encodes this account and no other.
- ``ACCOUNT_150K`` carries the 150K figures of facts F12.2a-c, the MLL ($4,500, V22, confirmed at
  the Stage E.12 freeze) and the 150K scaling plan read from Topstep's page image at the freeze
  (reports/stage_e12_topstep_150k.md; V23 item 12).

Fields beyond the interfaces file's list (reported to the lead): ``starting_balance_usd``,
``mll_lock_usd`` and ``post_payout_floor_usd``, which the trailing floor and the post-payout reset
need (xfa_rules XfaRules.starting_balance_cents, mll_lock_cents, post_payout_mll_floor_cents).
"""

from __future__ import annotations

from dataclasses import dataclass

from rules import xfa_rules as xr
from rules.products import TENTHS_PER_LOT

PATH_TYPES = ("standard", "consistency")


@dataclass(frozen=True)
class AccountSpec:
    """One XFA's parameters in dollars (sources in the instances' comments)."""

    name: str
    mll_usd: float  # trailing maximum loss limit distance
    dll_usd: float  # optional daily loss limit (chosen at Combine purchase)
    standard_cap_usd: float  # per-request payout cap, Standard path, no DLL
    consistency_cap_usd: float  # per-request payout cap, Consistency path, no DLL
    dll_cap_multiplier: float  # the caps' multiplier when the DLL was added
    balance_ceiling_frac: float  # a request is at most this share of the balance
    min_payout_usd: float
    split: float  # the trader's share of a payout
    standard_min_days: int
    standard_winning_day_usd: float
    consistency_min_days: int
    consistency_largest_frac: float  # largest winning day / window net profit, inclusive
    base_lots: float  # scaling plan below the first tier
    scaling_tiers: tuple[tuple[float, bool, float], ...]  # (threshold $, inclusive, max lots)
    starting_balance_usd: float = 0.0
    mll_lock_usd: float = 0.0  # the floor trails up to this balance, then locks
    post_payout_floor_usd: float = 0.0  # the floor after any payout ("regardless of where it was")

    def __post_init__(self) -> None:
        if not (self.mll_usd > 0 and self.dll_usd > 0):
            raise ValueError(f"{self.name}: account_bad_limits (MLL {self.mll_usd}, "
                             f"DLL {self.dll_usd} must be > 0)")
        if not (0 < self.split <= 1 and 0 < self.balance_ceiling_frac <= 1):
            raise ValueError(f"{self.name}: account_bad_fraction (split {self.split}, ceiling "
                             f"{self.balance_ceiling_frac})")
        for threshold, inclusive, lots in self.scaling_tiers:
            if not (isinstance(inclusive, bool) and lots > 0 and threshold >= 0):
                raise ValueError(f"{self.name}: account_bad_tier {(threshold, inclusive, lots)}")


def _usd(cents: int) -> float:
    return cents / 100


def _tiers_from_xfa(rules: xr.XfaRules) -> tuple[tuple[float, bool, float], ...]:
    return tuple((_usd(t.threshold_cents), t.inclusive, float(t.max_minis))
                 for t in rules.scaling_tiers)


_X = xr.XFA_50K

ACCOUNT_50K = AccountSpec(
    name="50K",
    mll_usd=_usd(_X.mll_cents),  # $2,000: xfa_rules XFA_50K.mll_cents
    dll_usd=1_000.0,  # facts F12.2c: "$50K Account: $1,000"
    standard_cap_usd=_usd(_X.standard.per_request_cap_cents),  # $2,000: XFA_50K, facts F12.2a
    consistency_cap_usd=_usd(_X.consistency.per_request_cap_cents),  # $3,000: XFA_50K, F12.2a
    dll_cap_multiplier=2.0,  # facts F12.2b: $2,000 -> $4,000 and $3,000 -> $6,000 with a DLL
    balance_ceiling_frac=_X.payout_balance_ceiling_bps / xr.BPS,  # 50%: XFA_50K
    min_payout_usd=_usd(_X.min_payout_cents),  # $125: XFA_50K.min_payout_cents
    split=0.9,  # facts F9.1: "Profit split 90/10"
    standard_min_days=_X.standard.min_days,  # 5: XFA_50K.standard
    standard_winning_day_usd=_usd(_X.standard.winning_day_min_net_cents or 0),  # $150: XFA_50K
    consistency_min_days=_X.consistency.min_days,  # 3: XFA_50K.consistency
    consistency_largest_frac=(_X.consistency.largest_day_max_bps or 0) / xr.BPS,  # 40%: XFA_50K
    base_lots=float(_X.base_max_minis),  # 2 lots: XFA_50K.base_max_minis
    scaling_tiers=_tiers_from_xfa(_X),  # 3 lots at >= $1,500, 5 lots above $2,000: XFA_50K
    starting_balance_usd=_usd(_X.starting_balance_cents),  # $0: XFA_50K
    mll_lock_usd=_usd(_X.mll_lock_cents),  # $0: XFA_50K.mll_lock_cents
    post_payout_floor_usd=_usd(_X.post_payout_mll_floor_cents),  # $0: XFA_50K
)

ACCOUNT_150K = AccountSpec(
    name="150K",
    # V22 (user): MLL $4,500, confirmed at the freeze (V23 item 12): "$150K | $4,500"
    # (reports/stage_e12_topstep_150k.md row 1, help.topstep.com/en/articles/8284204).
    mll_usd=4_500.0,
    dll_usd=3_000.0,  # facts F12.2c: "$150K Account: $3,000"
    standard_cap_usd=5_000.0,  # facts F12.2a: "$150K | $5,000 | $6,000"
    consistency_cap_usd=6_000.0,  # facts F12.2a
    dll_cap_multiplier=2.0,  # facts F12.2b: "$150K | Standard | $5,000 | $10,000" (and $12,000)
    balance_ceiling_frac=0.5,  # facts F12.2a: "50% of your account balance up to the cap"
    # Not account-size specific in the facts (F9.1 states one $150 winning-day rule and one 40%
    # target for XFA); the $125 minimum is xfa_rules' 50K figure, assumed to hold at 150K.
    min_payout_usd=_usd(_X.min_payout_cents),
    split=0.9,  # facts F9.1
    standard_min_days=5,  # facts F9.1: "5 winning days of $150+"
    standard_winning_day_usd=150.0,  # facts F9.1
    consistency_min_days=3,  # facts F9.1: "3 days traded, 40% consistency target"
    consistency_largest_frac=0.4,  # facts F9.1, F9.2
    # The 150K scaling plan, read from Topstep's page image at the freeze (V23 item 12;
    # reports/stage_e12_topstep_150k.md section 2, help.topstep.com/en/articles/8284223, image
    # "XFA charts - hc.png" fetched 2026-10-03): "Below $1,500 | 3 Lots", "$1,500 - $2,000 | 4",
    # "$2,000 - $3,000 | 5", "$3,000 - $4,500 | 10", "Above $4,500 | 15". The page does not say
    # which tier a balance exactly on $2,000, $3,000 or $4,500 is in: the lower one is taken (the
    # conservative reading), and $1,500 opens the 4-lot tier, as XFA_50K's ">= $1,500" encodes
    # the same label (E.12 lead ruling).
    base_lots=3.0,
    scaling_tiers=((1_500.0, True, 4.0), (2_000.0, False, 5.0), (3_000.0, False, 10.0),
                   (4_500.0, False, 15.0)),
    # The XFA structure of xfa_rules (start $0, lock at $0, post-payout floor $0), assumed for 150K.
    starting_balance_usd=0.0,
    mll_lock_usd=0.0,
    post_payout_floor_usd=0.0,
)


def tier_max_lots(account: AccountSpec, prior_close_balance_usd: float) -> float:
    """The scaling plan's maximum position (lots) at the prior session's closing balance
    (xfa_rules.max_position_micros semantics: each tier met in order raises the limit)."""
    lots = account.base_lots
    for threshold, inclusive, tier_lots in account.scaling_tiers:
        above = prior_close_balance_usd > threshold
        at = inclusive and prior_close_balance_usd == threshold
        if above or at:
            lots = tier_lots
    return lots


def tier_max_tenths(account: AccountSpec, prior_close_balance_usd: float) -> int:
    """``tier_max_lots`` in tenths of a lot (the unit of rules.constraints)."""
    return round(tier_max_lots(account, prior_close_balance_usd) * TENTHS_PER_LOT)


def payout_cap_usd(account: AccountSpec, path_type: str, dll: bool) -> float:
    """The per-request cap of a path, doubled when the DLL was added (facts F12.2b)."""
    if path_type not in PATH_TYPES:
        raise ValueError(f"unknown_path_type {path_type!r}; expected one of {PATH_TYPES}")
    cap = account.standard_cap_usd if path_type == "standard" else account.consistency_cap_usd
    return cap * account.dll_cap_multiplier if dll else cap


def trail_floor(account: AccountSpec, prev_floor_usd: float, eod_balance_usd: float) -> float:
    """End-of-day trailing floor (xfa_rules.trail_mll_floor): up only, capped at the lock."""
    return max(prev_floor_usd, min(eod_balance_usd - account.mll_usd, account.mll_lock_usd))


__all__ = [
    "ACCOUNT_150K", "ACCOUNT_50K", "PATH_TYPES", "AccountSpec", "payout_cap_usd",
    "tier_max_lots", "tier_max_tenths", "trail_floor",
]
