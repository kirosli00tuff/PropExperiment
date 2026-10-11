"""Stage E.20 test H6: rest-of-day to last-half-hour momentum on NQ at MNQ cost.

The rule is reports/stage_e20_prereg_H6.md (docs/prompts/STAGE_E.20.md F5); the build record is
reports/stage_e20_briefs/h6_build.md. ``python -m h6_rod check | register | evaluate``.

Importing any h6_rod module imports the read guard (F3, prereg section 9) first.
"""

from h6_rod import guard as guard  # noqa: F401  (F3: every H6 process imports the guard)
