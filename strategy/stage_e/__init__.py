"""Stage E member contract and template (Stage E.2b Task 1).

- strategy/stage_e/interface.py: the member contract (LegSpec, MinuteView, MemberAccountView,
  LegIntent, TradingInterval, leg_market_intent, leg_limit_intent).
- strategy/stage_e/_template.py: a worked member to copy.

This package is harness code (frozen by reports/stage_e2b_harness_freeze.json). A cluster's
members are written under strategy/members/<k#>/ (never here: the harness preflight refuses any
unlisted *.py in this directory) and frozen with screening.stage_e_freeze before they are run.
"""
