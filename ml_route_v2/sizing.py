"""Position size of one v2 trade (docs/STAGE_E_ML_V2_DESIGN.md V2.8, "Sizing (F8)").

- sigma_target = DAILY_SIGMA_FRACTION x D_open; the per-trade budget b = sigma_target / sqrt(m),
  m = RISK_SPLIT_M; KS2's multiplier scales the budget.
- n_risk = floor(b x multiplier / (sigma(p,h) x tick value)). Rounding band (lead amendment, V2.8):
  if n_risk is 0 but one contract's h-sigma in dollars is at most RISK_ROUND_UP_RATIO x b x
  multiplier, n_risk = 1.
- n_loss = floor(TRADE_LOSS_FRACTION x D_now / ((L(p,h) + c) x tick value)).
- n = min(n_risk, n_loss, the product cap, the capacity left); 0 means no trade. The caller folds
  D9.12's CPI cap into ``product_cap``.
- Daily risk budget (design review D-03): the trade date starts with the variance budget
  sigma_target^2 = (DAILY_SIGMA_FRACTION x D_open)^2 (``daily_variance_budget``). Each accepted
  trade consumes (n x sigma(p,h) x tick value)^2 (``budget_use``). With ``budget_var`` (the
  remaining budget) the size is also at most the largest n whose use fits it,
  floor(sqrt(remaining) / (sigma(p,h) x tick value)) (``budget_contracts``); a spent budget gives
  0, so no entry. The budget is not scaled by KS2's multiplier (the ruling: "the day starts with
  sigma_target^2"); the multiplier scales b only. Consequence: the rounding band can lift a trade
  only up to one contract's sigma$ <= sigma_target = sqrt(m) x b, below the band's 2 b.
- Cost beyond D2's size (design review D-08a): ``excess_cost_ticks`` is the per-contract round-trip
  surcharge 2 x BEYOND_QC_EXTRA_TICKS_PER_SIDE x (n - q_c)^+ / n ticks (one extra tick per side for
  each contract beyond the vehicle's q_c), shared by the fixed-D metric and payout re-sizing.

Every caller (portfolio.accept_trades, simulate.PortfolioMember, payout_sim.run_path) takes this
arithmetic from here; payout_sim's vectorized copy repeats the same operations in the same order.

The floors take a 1e-9 guard against float noise (a ratio that is 3 in exact arithmetic must not
floor to 2); it never lifts a ratio short of an integer by more than that.
"""

from __future__ import annotations

from math import floor, isfinite, sqrt

from ml_route_v2.constants import (
    BEYOND_QC_EXTRA_TICKS_PER_SIDE,
    DAILY_SIGMA_FRACTION,
    RISK_ROUND_UP_RATIO,
    RISK_SPLIT_M,
    TRADE_LOSS_FRACTION,
)

FLOOR_GUARD = 1e-9  # float-noise guard of the floors (see the module docstring)


def _floor(x: float) -> int:
    return floor(x + FLOOR_GUARD)


def _check(name: str, value: float, *, positive: bool) -> None:
    if not isfinite(value) or (value <= 0 if positive else value < 0):
        raise ValueError(f"sizing_bad_input: {name} = {value!r} must be finite and "
                         f"{'> 0' if positive else '>= 0'}")


def risk_budget_usd(d_open: float) -> float:
    """b = 0.10 x D_open / sqrt(3): the per-trade dollar sigma budget (before KS2)."""
    return DAILY_SIGMA_FRACTION * d_open / sqrt(RISK_SPLIT_M)


def daily_variance_budget(d_open: float) -> float:
    """sigma_target^2 = (0.10 x D_open)^2, in $^2: the trade date's starting risk budget (D-03)."""
    return (DAILY_SIGMA_FRACTION * d_open) ** 2


def budget_use(n: int, sigma_ticks: float, tick_value_usd: float) -> float:
    """(n x sigma(p,h) x tick value)^2: the variance one accepted trade of n contracts consumes."""
    return (n * (sigma_ticks * tick_value_usd)) ** 2


def budget_contracts(remaining_var: float, sigma_ticks: float, tick_value_usd: float) -> int:
    """The largest n with (n x sigma$)^2 <= remaining_var; 0 once the budget is spent."""
    if not isfinite(remaining_var):
        raise ValueError(f"sizing_bad_input: budget_var = {remaining_var!r} must be finite")
    return _floor(sqrt(max(remaining_var, 0.0)) / (sigma_ticks * tick_value_usd))


def excess_cost_ticks(n: int, q_c: int | None) -> float:
    """Round-trip surcharge per contract for the contracts beyond q_c (design review D-08a):
    2 x extra ticks per side x (n - q_c)^+ / n. 0.0 when q_c is None (unknown) or n < 1."""
    if q_c is None or n < 1:
        return 0.0
    return 2.0 * BEYOND_QC_EXTRA_TICKS_PER_SIDE * max(n - q_c, 0) / n


def contracts(*, d_open: float, d_now: float, sigma_ticks: float, loss_ticks: float,
              cost_ticks: float, tick_value_usd: float, product_cap: int,
              capacity_contracts: int, multiplier: float = 1.0,
              budget_var: float | None = None) -> int:
    """V2.8's contract count; 0 means no trade. ``budget_var``: the trade date's remaining
    variance budget (D-03); None leaves the budget out (single-trade use)."""
    _check("sigma_ticks", sigma_ticks, positive=True)
    _check("tick_value_usd", tick_value_usd, positive=True)
    _check("loss_ticks", loss_ticks, positive=False)
    _check("cost_ticks", cost_ticks, positive=False)
    _check("multiplier", multiplier, positive=False)
    if not (isfinite(d_open) and isfinite(d_now)):
        raise ValueError(f"sizing_bad_input: D_open {d_open!r} / D_now {d_now!r} not finite")
    if loss_ticks + cost_ticks <= 0:
        raise ValueError("sizing_bad_input: loss_ticks + cost_ticks must be > 0")
    if d_open <= 0 or d_now <= 0 or multiplier == 0 or product_cap < 1 or capacity_contracts < 1:
        return 0
    budget = risk_budget_usd(d_open) * multiplier
    one_sigma_usd = sigma_ticks * tick_value_usd
    n_risk = _floor(budget / one_sigma_usd)
    if n_risk == 0 and one_sigma_usd <= RISK_ROUND_UP_RATIO * budget:
        n_risk = 1  # the rounding band (lead amendment to V2.8)
    n_loss = _floor(TRADE_LOSS_FRACTION * d_now / ((loss_ticks + cost_ticks) * tick_value_usd))
    n = max(0, min(n_risk, n_loss, int(product_cap), int(capacity_contracts)))
    if budget_var is not None:
        n = min(n, budget_contracts(budget_var, sigma_ticks, tick_value_usd))
    return n


__all__ = [
    "FLOOR_GUARD", "budget_contracts", "budget_use", "contracts", "daily_variance_budget",
    "excess_cost_ticks", "risk_budget_usd",
]
