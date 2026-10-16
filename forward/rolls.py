"""Contract cycles and the declared roll rule of E22-F1's paper runner (ForwardRunnerCoder, E.22).

Each instrument holds one contract at a time, its "reference contract". The declared rule gives
every listed contract a roll date: ``n_bdays`` business days before an anchor date derived from
the contract month. Business days are Monday to Friday; exchange holidays are NOT modelled (a
declared approximation). The contract to hold on trade date d is the first listed contract whose
roll date is after d. The runner executes a due roll at the settlement of the first processed
trade date on or after the roll date at which both contracts have a settlement.

The rule file (forward/rolls_f1.json) is flagged "to be checked against the exchange's published
roll schedule before the clock starts". Nothing in this module fetches anything.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Any

MONTH_CODES = "FGHJKMNQUVXZ"
CODE_TO_MONTH = {code: i + 1 for i, code in enumerate(MONTH_CODES)}
DEFAULT_ROLLS_PATH = Path(__file__).with_name("rolls_f1.json")
ANCHOR_KINDS = ("nth_weekday", "calendar_day")
CHECK_FLAG = "to be checked against the exchange's published roll schedule before the clock starts"
MAX_ANCHOR_DAY = 28  # calendar_day anchors stay valid in every month
SEARCH_YEARS_BACK = 1
SEARCH_YEARS_AHEAD = 3


class RollConfigError(ValueError):
    """The roll file is malformed."""


@dataclass(frozen=True)
class Anchor:
    """The date the roll counts back from, relative to the contract month.

    kind "nth_weekday": the ``nth`` ``weekday`` (0 = Monday .. 4 = Friday) of the target month.
    kind "calendar_day": calendar day ``day`` of the target month.
    The target month is the contract month shifted by ``month_offset`` (0 = the contract month,
    -1 = the month before it).
    """

    kind: str
    month_offset: int
    weekday: int | None = None
    nth: int | None = None
    day: int | None = None


@dataclass(frozen=True)
class InstrumentRoll:
    instrument: str
    root: str
    months: tuple[int, ...]
    anchor: Anchor
    n_bdays: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "instrument": self.instrument,
            "root": self.root,
            "months": list(self.months),
            "anchor": asdict(self.anchor),
            "n_bdays": self.n_bdays,
        }


def shift_month(year: int, month: int, offset: int) -> tuple[int, int]:
    index = year * 12 + (month - 1) + offset
    return index // 12, index % 12 + 1


def anchor_date(anchor: Anchor, year: int, month: int) -> date:
    y, m = shift_month(year, month, anchor.month_offset)
    if anchor.kind == "calendar_day":
        return date(y, m, int(anchor.day))
    first = date(y, m, 1)
    lead = (int(anchor.weekday) - first.weekday()) % 7
    return first + timedelta(days=lead + 7 * (int(anchor.nth) - 1))


def bdays_before(day: date, n: int) -> date:
    """The n-th weekday strictly before ``day`` (exchange holidays not modelled)."""
    current, counted = day, 0
    while counted < n:
        current -= timedelta(days=1)
        if current.weekday() < 5:
            counted += 1
    return current


def roll_date(spec: InstrumentRoll, year: int, month: int) -> date:
    return bdays_before(anchor_date(spec.anchor, year, month), spec.n_bdays)


def contract_id(spec: InstrumentRoll, year: int, month: int) -> str:
    if month not in spec.months:
        raise ValueError(f"{spec.instrument}: month {month} is not in the declared cycle")
    return f"{spec.root}{MONTH_CODES[month - 1]}{year % 100:02d}"


def parse_contract(spec: InstrumentRoll, cid: str) -> tuple[int, int]:
    """(year, month) of a contract id such as MNQZ26.

    Refuses a foreign root, a malformed id or a month outside the cycle.
    """
    if not isinstance(cid, str) or not cid.startswith(spec.root) or len(cid) != len(spec.root) + 3:
        raise ValueError(f"{spec.instrument}: contract id {cid!r} does not match root {spec.root}")
    code, yy = cid[len(spec.root)], cid[len(spec.root) + 1 :]
    if code not in CODE_TO_MONTH or not yy.isdigit():
        raise ValueError(f"{spec.instrument}: contract id {cid!r} is malformed")
    month = CODE_TO_MONTH[code]
    if month not in spec.months:
        raise ValueError(f"{spec.instrument}: contract {cid} is outside the declared cycle")
    return 2000 + int(yy), month


def active_contract(spec: InstrumentRoll, day: date) -> str:
    """The contract the declared rule holds on ``day``: the first listed one rolling after it."""
    for year in range(day.year - SEARCH_YEARS_BACK, day.year + SEARCH_YEARS_AHEAD + 1):
        for month in spec.months:
            if roll_date(spec, year, month) > day:
                return contract_id(spec, year, month)
    raise RollConfigError(f"{spec.instrument}: no listed contract rolls after {day}")


def is_roll_due(spec: InstrumentRoll, held: str, day: date) -> bool:
    return roll_date(spec, *parse_contract(spec, held)) <= day


def expiry_guard(spec: InstrumentRoll, held: str) -> date:
    """The anchor date of the held contract; a roll still pending on or after it is overdue."""
    return anchor_date(spec.anchor, *parse_contract(spec, held))


def roll_schedule(spec: InstrumentRoll, start: date, end: date) -> list[dict[str, str]]:
    """Every listed contract whose roll date falls in [start, end], for the pre-clock check."""
    rows = []
    for year in range(start.year - SEARCH_YEARS_BACK, end.year + SEARCH_YEARS_AHEAD + 1):
        for month in spec.months:
            rd = roll_date(spec, year, month)
            if start <= rd <= end:
                rows.append(
                    {
                        "instrument": spec.instrument,
                        "contract": contract_id(spec, year, month),
                        "roll_date": rd.isoformat(),
                        "anchor_date": anchor_date(spec.anchor, year, month).isoformat(),
                    }
                )
    return sorted(rows, key=lambda r: r["roll_date"])


def _parse_cycle(name: str, cycle: Any) -> tuple[int, ...]:
    if not isinstance(cycle, str) or not cycle:
        raise RollConfigError(f"{name}: cycle must be a non-empty string of month codes")
    if any(c not in CODE_TO_MONTH for c in cycle) or len(set(cycle)) != len(cycle):
        raise RollConfigError(f"{name}: bad cycle {cycle!r}")
    return tuple(sorted(CODE_TO_MONTH[c] for c in cycle))


def _parse_anchor(name: str, raw: Any) -> Anchor:
    if not isinstance(raw, Mapping) or raw.get("kind") not in ANCHOR_KINDS:
        raise RollConfigError(f"{name}: anchor kind must be one of {ANCHOR_KINDS}")
    offset = raw.get("month_offset")
    if not isinstance(offset, int) or isinstance(offset, bool) or not -2 <= offset <= 0:
        raise RollConfigError(f"{name}: month_offset must be an int in [-2, 0]")
    if raw["kind"] == "calendar_day":
        day = raw.get("day")
        if not isinstance(day, int) or isinstance(day, bool) or not 1 <= day <= MAX_ANCHOR_DAY:
            raise RollConfigError(f"{name}: calendar_day needs day in [1, {MAX_ANCHOR_DAY}]")
        return Anchor("calendar_day", offset, day=day)
    weekday, nth = raw.get("weekday"), raw.get("nth")
    if not (
        isinstance(weekday, int) and 0 <= weekday <= 4 and isinstance(nth, int) and 1 <= nth <= 4
    ):
        raise RollConfigError(f"{name}: nth_weekday needs weekday in [0, 4] and nth in [1, 4]")
    return Anchor("nth_weekday", offset, weekday=weekday, nth=nth)


def _parse_instrument(name: str, raw: Any) -> InstrumentRoll:
    if not isinstance(raw, Mapping):
        raise RollConfigError(f"{name}: entry must be an object")
    root, n_bdays = raw.get("root"), raw.get("n_bdays")
    if not isinstance(root, str) or not root.isalnum() or not root.isupper():
        raise RollConfigError(f"{name}: root must be upper-case alphanumeric")
    if not isinstance(n_bdays, int) or isinstance(n_bdays, bool) or not 1 <= n_bdays <= 30:
        raise RollConfigError(f"{name}: n_bdays must be an int in [1, 30]")
    if not raw.get("cycle_source"):
        raise RollConfigError(f"{name}: cycle_source is required (cite, or say UNSOURCED)")
    return InstrumentRoll(
        name,
        root,
        _parse_cycle(name, raw.get("cycle")),
        _parse_anchor(name, raw.get("anchor")),
        n_bdays,
    )


def parse_rolls(doc: Mapping[str, Any]) -> dict[str, InstrumentRoll]:
    if CHECK_FLAG not in str(doc.get("status", "")):
        raise RollConfigError(f"roll file must carry the status flag: {CHECK_FLAG!r}")
    instruments = doc.get("instruments")
    if not isinstance(instruments, Mapping) or not instruments:
        raise RollConfigError("roll file has no instruments")
    return {name: _parse_instrument(name, raw) for name, raw in sorted(instruments.items())}


def load_rolls(path: Path | str = DEFAULT_ROLLS_PATH) -> dict[str, InstrumentRoll]:
    with open(path, encoding="utf-8") as fh:
        return parse_rolls(json.load(fh))


def rolls_fingerprint(specs: Mapping[str, InstrumentRoll]) -> str:
    body = json.dumps(
        [specs[k].as_dict() for k in sorted(specs)], sort_keys=True, separators=(",", ":")
    )
    return hashlib.sha256(body.encode("ascii")).hexdigest()
