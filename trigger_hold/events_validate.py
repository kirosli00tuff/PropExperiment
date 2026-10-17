"""W_cf validation of the trigger extraction (lead_spec section 6; TriggerCoder brief item 4).

For one trigger, two runs of the same frozen member on 2019-05-06..2024-02-29 (from the declared
S_X where one exists):
- adapter: trigger_hold.events.extract(trigger, "W_cf") (base_rules.store bars);
- harness: the Stage E runner's own path, records not written: screening.stage_e_runner's
  _legs_inputs, _load_frames ("confirmation": the start rule's S_X, the price path, the step 2
  store pinned by the start rule's sha256), member_window, member_coverage, _run_member. A member
  whose store root no start rule lists (K2's rates: its confirmation never ran) is loaded by the
  harness's loader data.stage_e_bars.load_confirmation_leg from 2019-05-06 with the E.17 run
  manifest's sha256 for the store, the start W_cf declares.
Only entry events are taken from the harness's EngineResult (trigger_hold.events.entries_of);
its P&L is dropped unread. The two event lists are compared on (d0, tau, side); the frames the
engine received are compared column by column (equal or not; no value is written).
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import numpy as np

from base_rules import constants as BK
from data.stage_e_bars import BAR_COLUMNS, STEP2, LegFrame, load_confirmation_leg
from screening import harness_freeze
from screening import stage_e_runner as R
from screening.stage_e_align import member_coverage, member_window
from screening.stage_e_freeze import load_cluster_freeze, resolve_member, verify_cluster_code
from screening.stage_e_frozen import sha256_file
from screening.stage_e_rules import load_release_calendar
from screening.stage_e_runner import StartRuleMissing
from trigger_hold import constants as TC
from trigger_hold import events as EV
from trigger_hold import events_bars as EB
from trigger_hold import events_members as EM

RESEARCH_ROOT = Path("data/processed")  # passed as confirm_run.sh passes it; read for MES only
STEP2_ROOT = Path("data/processed_step2")


def _harness_frames(legs: Any, inputs: Any) -> tuple[dict[str, LegFrame], str]:
    try:
        frames, extra = R._load_frames(legs, inputs, R.CONFIRMATION_WINDOW, RESEARCH_ROOT,
                                       STEP2_ROOT)
        return frames, f"harness _load_frames, S_X {extra.get('s_x')}"
    except StartRuleMissing:
        pass
    store_roots, _ = R._store_roots(legs)
    man = EB.manifest()
    frames = {}
    for leg in legs:
        src = store_roots[leg.root]
        ref = man.stores[src]["step2"]
        frames[leg.root] = load_confirmation_leg(
            leg.root, STEP2_ROOT, TC.W_CF_FIRST, expected_sha256=ref.sha256,
            path_root=R._source(leg.root, store_roots), research_root=RESEARCH_ROOT)
    return frames, "harness load_confirmation_leg from 2019-05-06 (no start rule), E.17 sha256"


def harness_entries(trigger_id: str) -> dict[str, Any]:
    harness_freeze.preflight(EV.HARNESS_SHA256)
    spec = EM.spec_for(trigger_id)
    freeze = load_cluster_freeze(spec.cluster)
    verify_cluster_code(freeze)
    decl, factory = resolve_member(freeze, spec.label, None)
    legs = decl.legs
    inputs = R._legs_inputs(legs)
    releases = load_release_calendar()
    frames, how = _harness_frames(legs, inputs)
    mw = member_window(frames, STEP2)
    member = factory()
    coverage = member_coverage(frames, mw.dates, getattr(member, "trading_windows", {}))
    result = R._run_member(member, legs, inputs, frames, mw.dates, mw.blackout_union, releases)
    capture = EV.entries_of(result, frames)
    del result  # P&L dropped unread
    return {"capture": capture, "frames": frames, "how": how, "window": mw,
            "coverage": {r: [c.present, c.expected, c.passes] for r, c in coverage.items()}}


def frames_equal(a: Mapping[str, LegFrame], b: Mapping[str, LegFrame]) -> dict[str, Any]:
    """Per leg and column: do the two frames hold the same values (True/False only)."""
    out: dict[str, Any] = {}
    for root in sorted(set(a) | set(b)):
        if root not in a or root not in b:
            out[root] = "leg missing on one side"
            continue
        fa, fb = a[root].frame, b[root].frame
        if len(fa) != len(fb):
            out[root] = {"rows_equal": False, "rows": [len(fa), len(fb)]}
            continue
        cols = {}
        for c in BAR_COLUMNS:
            xa, xb = fa[c].to_numpy(), fb[c].to_numpy()
            if xa.dtype.kind in "fiub" and xb.dtype.kind in "fiub":
                cols[c] = bool(np.array_equal(xa, xb))
            else:
                cols[c] = bool(np.array_equal(xa.astype(str), xb.astype(str)))
        out[root] = {"rows_equal": True, "rows": len(fa), "columns_equal": cols,
                     "trade_dates_equal": a[root].trade_dates == b[root].trade_dates,
                     "blackout_equal": a[root].roll_blackout == b[root].roll_blackout}
    return out


def _rows(events: Any) -> list[list[Any]]:
    return [[d.isoformat(), int(t), int(s)] for d, t, s in events]


H6_RESULT = Path("reports/stage_e20_H6_result.json")


def e20_h6_entries(path: Path = H6_RESULT) -> dict[str, list[tuple[str, int, int]]]:
    """E.20's own H6 T1 runs (verdict 2020-06..2024-02, overlap 2019-05..2020-05): each trade's
    trade date, side and entry fill instant only; no other field of a trade is read."""
    from datetime import datetime

    body = json.loads((BK.repo_path(path)).read_text(encoding="utf-8"))
    out = {}
    for part in ("overlap", "tests"):
        rows = []
        for t in body[part]["T1"]["trades"]:
            when = datetime.fromisoformat(str(t["entry_fill_utc"]).replace("Z", "+00:00"))
            ns = int(when.timestamp()) * 1_000_000_000
            rows.append((str(t["trade_date"]), ns, 1 if t["side"] in ("buy", 1, "long") else -1))
        out[part] = sorted(rows)
    return out


def validate_h6() -> dict[str, Any]:
    from trigger_hold.events_h6 import extract_h6

    record, meta = extract_h6(EB.W_CF)
    adapter = {(r["d0"], int(r["tau_ns"]), int(r["side"])) for r in record["events"]}
    e20 = e20_h6_entries()
    harness = set(e20["overlap"]) | set(e20["tests"])
    a_day = {(d, s) for d, _, s in adapter}
    h_day = {(d, s) for d, _, s in harness}
    diffs = [{"in": "adapter only", "event": [d, s]} for d, s in sorted(a_day - h_day)]
    diffs += [{"in": "E.20 only", "event": [d, s]} for d, s in sorted(h_day - a_day)]
    tau_vs_fill = sum(1 for e in adapter if e in harness)
    return {"schema": EV.VALIDATION_SCHEMA, "trigger_id": record["trigger_id"],
            "window": EB.W_CF, "identical": adapter == harness,
            "same_d0_and_side": a_day == h_day,
            "tau_equals_e20_entry_fill_instant": tau_vs_fill,
            "adapter": {"n": len(adapter), "first": meta["first"], "last": meta["last"],
                        "counts": record["counts"]},
            "harness": {"n": len(harness), "how": "E.20 records reports/stage_e20_H6_result.json "
                        "(overlap.T1 and tests.T1 trades: trade_date, side, entry_fill_utc)",
                        "n_overlap": len(e20["overlap"]), "n_verdict": len(e20["tests"]),
                        "sha256": sha256_file(BK.repo_path(H6_RESULT))},
            "differences": diffs, "inputs": record["inputs"]}


def validate(trigger_id: str) -> dict[str, Any]:
    from trigger_hold.events_h6 import is_h6

    if is_h6(trigger_id):
        return validate_h6()
    record, meta = EV.extract(trigger_id, EB.W_CF)
    adapter = {(r["d0"], int(r["tau_ns"]), int(r["side"])) for r in record["events"]}
    h = harness_entries(trigger_id)
    harness = {(d.isoformat(), t, s) for d, t, s in h["capture"].events}
    adapter_frames = _adapter_frames(trigger_id, meta)
    diffs = [{"in": "adapter only", "event": list(e)} for e in sorted(adapter - harness)]
    diffs += [{"in": "harness only", "event": list(e)} for e in sorted(harness - adapter)]
    by_day_a = {(d, s) for d, _, s in adapter}
    by_day_h = {(d, s) for d, _, s in harness}
    return {"schema": EV.VALIDATION_SCHEMA, "trigger_id": record["trigger_id"],
            "window": EB.W_CF, "identical": adapter == harness,
            "same_d0_and_side": by_day_a == by_day_h,
            "adapter": {"n": len(adapter), "first": meta["first"], "last": meta["last"],
                        "bounds_source": meta["bounds_source"], "counts": record["counts"]},
            "harness": {"n": len(harness), "how": h["how"], "counts": dict(h["capture"].counts),
                        "window_dates": len(h["window"].dates),
                        "first": h["window"].dates[0].isoformat(),
                        "last": h["window"].dates[-1].isoformat(), "coverage": h["coverage"]},
            "frames_equal": frames_equal(adapter_frames, h["frames"]),
            "differences": diffs, "inputs": record["inputs"]}


def _adapter_frames(trigger_id: str, meta: Mapping[str, Any]) -> dict[str, LegFrame]:
    from datetime import date

    spec = EM.spec_for(trigger_id)
    legs = EM.resolve(spec)[0].legs
    first, last = date.fromisoformat(meta["first"]), date.fromisoformat(meta["last"])
    man = EB.manifest()
    cals = EB.load_calendars_for([leg.root for leg in legs])
    return {leg.root: EB.load_leg(leg.root, EB.W_CF, first, last, run_manifest=man,
                                  calendars=cals).leg for leg in legs}


__all__ = ["frames_equal", "harness_entries", "validate"]
