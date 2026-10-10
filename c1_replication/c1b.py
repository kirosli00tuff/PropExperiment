"""Test C1b (Stage E.18): test C1's single evaluation, re-registered with guard C10's one clause
(reports/stage_e18_prereg_C1b.md, "THE ONE FIX"; DECISIONS V31).

    python -m c1_replication.c1b --harness-sha256 <sha> \
        --freeze reports/stage_e18_prereg_C1b.md --freeze-sha256 <sha> \
        --model reports/stage_e14_c1_model.json --model-sha256 <sha> --model-dir <dir> \
        --store-hashes <json> --calendar-hashes <json> --out reports/stage_e18_c1b_result.json

Every C1 file is unchanged (C1's closed attempt stays reproducible from its frozen code). This
module runs the frozen c1_replication.evaluate.run inside ``c1b_profile()``, which swaps the
evaluate attributes C1b changes while the run lasts and puts every original back on exit (also on
an exception), as c1_replication.context.hist_tables does for the frozen modules (``SWAPS``):
1. TEST "C1b", TEST_IDS ("C1b-T1", "C1b-T2"), HORIZON_OF (T1 = NG h60, T2 = NG hF): the new
   registration (the trial registry must hold both ids together under C1b's freeze sha256).
2. c10_check: C1's rule, called unchanged, on every signal except ``C10_EXEMPT`` (freeze section
   3 as amended): a signal whose leg section 2 already makes "not applicable" on every NG row of
   the test window. The list is fixed from listing dates and section 2, never from a count of
   the test window.
3. preconditions: C1's, called unchanged; the C1b record (ids, the exempt list) is added to the
   records the marker and the result carry, so the rule in force is on disk before any bar.
The freeze and the marker are RunInputs fields (``FREEZE_PATH``, ``MARKER_PATH``). Everything
else is C1's code: the model, q, the calendars, C12, the clock, the world, the panel, C11, the
trades, the statistic, the pass bar, the verdict, the descriptive outputs, the exit codes. The
frozen log lines keep C1's wording ("C1 marker written", "C1 verdict").
"""

from __future__ import annotations

import dataclasses
import json
import sys
from collections.abc import Callable, Iterator, Mapping, Sequence
from contextlib import contextmanager
from pathlib import Path
from types import MappingProxyType
from typing import Any

from c1_replication import evaluate as ev
from c1_replication.constants import FAIL, PASS, RC_REFUSED
from c1_replication.guards import C1Refused
from data.config import REPO_ROOT

TEST = "C1b"  # the trial registry's label
TEST_IDS = ("C1b-T1", "C1b-T2")  # freeze section 5: T1 = NG h60, T2 = NG hF
HORIZON_OF = MappingProxyType({"C1b-T1": "h60", "C1b-T2": "hF"})
FREEZE_PATH = REPO_ROOT / "reports" / "stage_e18_prereg_C1b.md"
MARKER_PATH = REPO_ROOT / "reports" / "stage_e18_c1b_RUN_ONCE.json"
# Freeze section 3, C10 as amended: exempt signals and why (listing dates and section 2 only).
C10_EXEMPT = MappingProxyType({
    "g17_mbt": "leg MBT, no contract listed on any date of 2010-06-07..2019-04-30 (CME Micro "
               "Bitcoin futures launched 2021-05-03; CME Bitcoin futures BTC from the trade date "
               "2017-12-18); section 2: 'MBT is not listed (n/a by design)'",
    "g17_cl": "leg CL, NG's own cluster lead (K4), which G17 never applies on its own cluster's "
              "rows; section 2: 'CL is never live on NG rows'; its E.12 reference is 0, so C1's "
              "rule never reached it",
})
SWAPS = ("TEST", "TEST_IDS", "HORIZON_OF", "c10_check", "preconditions")

_C1_C10_CHECK = ev.c10_check
_C1_PRECONDITIONS = ev.preconditions
_C1_TEST = ev.TEST


def c10_check(counts: Mapping[str, Any], reference: Mapping[str, Any]) -> list[str]:
    """C1's c10_check on the reference less the C10_EXEMPT signals: every other signal live on
    NG rows in E.12 (reference count > 0) that applies on no row stops the run, as in C1."""
    kept = {h: {**ref, "applicable": {s: n for s, n in ref["applicable"].items()
                                      if s not in C10_EXEMPT}}
            for h, ref in reference.items()}
    return _C1_C10_CHECK(counts, kept)


def record() -> dict[str, Any]:
    return {"test": TEST, "test_ids": list(TEST_IDS), "freeze": "reports/stage_e18_prereg_C1b.md",
            "c10_exempt": dict(C10_EXEMPT),
            "c1_closed": "C1 (r001-C1) stopped at C10 in Stage E.17; "
                         "reports/stage_e14_c1_result.json"}


def _preconditions(inp: ev.RunInputs, preflight: Callable[[str], str]) -> ev.Prepared:
    prep = _C1_PRECONDITIONS(inp, preflight)
    return dataclasses.replace(prep, records={**prep.records, "c1b": record()})


@contextmanager
def c1b_profile() -> Iterator[dict[str, Any]]:
    """SWAPS set to C1b's values while the block runs (module docstring); no nesting."""
    if ev.TEST != _C1_TEST:
        raise C1Refused("the C1b profile is already active (no nesting)")
    values = {"TEST": TEST, "TEST_IDS": TEST_IDS, "HORIZON_OF": HORIZON_OF,
              "c10_check": c10_check, "preconditions": _preconditions}
    saved: dict[str, Any] = {}
    try:
        for name in SWAPS:
            saved[name] = getattr(ev, name)
            setattr(ev, name, values[name])
        yield values
    finally:
        for name in reversed(SWAPS):
            if name in saved:
                setattr(ev, name, saved[name])


def run(inp: ev.RunInputs, *, preflight: Callable[[str], str] | None = None,
        leg_loader: Callable[..., Any] | None = None,
        log: Callable[[str], None] = print) -> dict[str, Any]:
    """The one C1b evaluation: evaluate.run under c1b_profile()."""
    with c1b_profile():
        return ev.run(inp, preflight=preflight, leg_loader=leg_loader, log=log)


def main(argv: Sequence[str] | None = None, *,
         preflight: Callable[[str], str] | None = None) -> int:
    from compute.platform import lower_priority
    from screening import harness_freeze

    parser = ev._parser()
    parser.prog = "python -m c1_replication.c1b"
    parser.set_defaults(freeze=str(FREEZE_PATH))
    args = parser.parse_args(argv)
    lower_priority()
    inp = ev.RunInputs(args.harness_sha256, args.freeze_sha256, Path(args.model),
                       args.model_sha256, Path(args.model_dir).expanduser(),
                       Path(args.store_hashes), Path(args.calendar_hashes), Path(args.out),
                       freeze_path=Path(args.freeze), marker_path=MARKER_PATH)
    try:
        payload = run(inp, preflight=preflight)
    except (C1Refused, harness_freeze.HarnessFreezeError, OSError, json.JSONDecodeError) as exc:
        print(f"REFUSED, nothing written, the evaluation has not run ({type(exc).__name__}): "
              f"{exc}", file=sys.stderr)
        return RC_REFUSED
    return 0 if payload["verdict"] in (PASS, FAIL) else 1


if __name__ == "__main__":
    sys.exit(main())
