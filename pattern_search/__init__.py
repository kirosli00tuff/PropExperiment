"""Stage E.20 Part C: the ML route's net pipeline on 17 roots (search, screen; backward test
pieces). The rule is reports/stage_e20_plan.md; the build record is
reports/stage_e20_briefs/search_build.md. ``python -m pattern_search check | run | report``.

Every module composes the frozen ml_route_v2 code (reports/stage_e12_ml_v2_freeze.json) without
editing it. Importing any pattern_search module imports the read guard (F3, plan section 3) first.
"""

from pattern_search import guard as guard  # noqa: F401  (F3: every search process imports it)
