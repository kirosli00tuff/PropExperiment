"""RandomBaseline: explicitly a NON-strategy used to exercise engine mechanics.

It is an unconditional coin flip used only to exercise engine mechanics end to
end; it reads no price, volume or flag, so it cannot have an edge; it is not a
trading idea. ``on_bar`` reads ONLY ``bar.ts_event_ns`` (and, indirectly,
``bar.decision_ts_utc`` via ``market_intent``, which stamps every intent with
it) plus ``account.position_micros`` and ``account.pending_signed_micros``. It
never looks at open/high/low/close/volume, any calendar flag, ``early_halt_ct``,
``gap_before_minutes``, ``raw_symbol`` or ``instrument_id`` — the leakage suite
(``tests/test_leakage_canaries.py``) relies on that blindness to prove the
harness itself does not smuggle information into a strategy.

Randomness is stateless and deterministic: ``coin_uniforms`` hashes
``(seed, ts_event_ns)`` with BLAKE2b and slices the digest into two uniforms in
``[0, 1)``. Same seed and same bar timestamps always produce the same
decisions; nothing is drawn from a stream, so replays and parallel runs agree
bit for bit.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

from rules.xfa_rules import OrderIntent, Refusal
from strategy.interface import AccountView, Bar, market_intent

_TWO_POW_64 = 2**64


def coin_uniforms(seed: int, ts_event_ns: int) -> tuple[float, float]:
    """Two independent-looking uniforms in [0, 1), deterministic in (seed, ts_event_ns)."""
    digest = hashlib.blake2b(f"{seed}:{ts_event_ns}".encode(), digest_size=16).digest()
    u1 = int.from_bytes(digest[:8], "big") / _TWO_POW_64
    u2 = int.from_bytes(digest[8:], "big") / _TWO_POW_64
    return u1, u2


@dataclass(frozen=True)
class RandomBaseline:
    """Unconditional coin-flip entries/exits. See module docstring: not a strategy."""

    seed: int
    entry_probability: float = 1 / 30
    exit_probability: float = 1 / 15
    quantity_micros: int = 1
    name: str = "random_baseline"

    def __post_init__(self) -> None:
        if isinstance(self.seed, bool) or not isinstance(self.seed, int):
            raise ValueError(f"seed {self.seed!r} must be an int")
        if not (0 < self.entry_probability <= 1):
            raise ValueError(
                f"entry_probability {self.entry_probability!r} must be in (0, 1]"
            )
        if not (0 < self.exit_probability <= 1):
            raise ValueError(
                f"exit_probability {self.exit_probability!r} must be in (0, 1]"
            )
        bad_quantity = (
            isinstance(self.quantity_micros, bool)
            or not isinstance(self.quantity_micros, int)
            or self.quantity_micros <= 0
        )
        if bad_quantity:
            raise ValueError(
                f"quantity_micros {self.quantity_micros!r} must be a positive int"
            )

    def on_bar(self, bar: Bar, account: AccountView) -> tuple[OrderIntent | Refusal, ...]:
        u_act, u_side = coin_uniforms(self.seed, bar.ts_event_ns)
        if account.pending_signed_micros != 0:
            return ()
        exposure = account.position_micros
        if exposure == 0:
            if u_act < self.entry_probability:
                side = "buy" if u_side < 0.5 else "sell"
                return (market_intent(bar, side, self.quantity_micros),)
            return ()
        if u_act < self.exit_probability:
            side = "sell" if exposure > 0 else "buy"
            return (market_intent(bar, side, abs(exposure)),)
        return ()
