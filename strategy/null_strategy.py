"""NullStrategy: explicitly a non-strategy used to exercise the harness.

It emits nothing: ``on_bar`` always returns the empty tuple, regardless of the
bar or account it is handed. It is a fixture, not a trading idea, and any
non-zero P&L it shows in a backtest is a harness defect (a fill, a cost, or a
position appearing from nowhere), never a signal to investigate in the
strategy layer.
"""

from __future__ import annotations

from dataclasses import dataclass

from strategy.interface import AccountView, Bar


@dataclass(frozen=True)
class NullStrategy:
    """A strategy that never trades. Used to prove the engine is inert on its own."""

    name: str = "null"

    def on_bar(self, bar: Bar, account: AccountView) -> tuple[()]:
        return ()
