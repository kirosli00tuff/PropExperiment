"""Half-open ``[start, end)`` nanosecond windows.

Ported from MLCryptoEngine ``data/recorder/gaps.py::merge_windows``
(read-only port, 2026-09-16). Overlapping windows are unioned, never summed:
a Friday close overlapping that day's own halt must not be counted twice.
"""

from __future__ import annotations

from bisect import bisect_right
from collections.abc import Iterable, Sequence


def merge_windows(windows: Iterable[tuple[int, int]]) -> list[tuple[int, int]]:
    """Union half-open windows; touching and duplicate windows collapse."""
    ordered = sorted((start, end) for start, end in windows if end > start)
    merged: list[tuple[int, int]] = []
    for start, end in ordered:
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged


def contains(merged: Sequence[tuple[int, int]], ts_ns: int) -> bool:
    """Membership in an already-merged, sorted window list (O(log n))."""
    idx = bisect_right(merged, (ts_ns, 2**63)) - 1
    return idx >= 0 and merged[idx][0] <= ts_ns < merged[idx][1]
