"""Hypothesis screening: the shared runner every research session uses (Stage D.1a).

Use ``screen_candidate``. Read docs/SCREENING.md first; it is the whole contract.
"""

from screening.runner import (
    ScreeningReport,
    ScreeningWindow,
    fold_train_window,
    screen_candidate,
    train_union_window,
)

__all__ = ["ScreeningReport", "ScreeningWindow", "fold_train_window", "screen_candidate",
           "train_union_window"]
