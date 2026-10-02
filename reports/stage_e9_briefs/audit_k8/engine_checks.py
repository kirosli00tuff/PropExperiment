"""Auditor's own engine-level checks with the REAL frozen release calendar (the coders' engine
tests all use NO_RELEASES): C6 skip vs the engine's D9.5a deferral on synthetic bars (items 6, 9,
10). Reuses the coders' synthetic-bar kits read-only (tests/test_k8_members_*.py). No bar file."""

from __future__ import annotations

import os

os.nice(10)

import sys  # noqa: E402
from datetime import date  # noqa: E402
from pathlib import Path  # noqa: E402

REPO = Path("/home/kiros-li/Documents/GitHub/PropExperiment")
sys.path.insert(0, str(REPO))

import pandas as pd  # noqa: E402

from screening.stage_e_engine import Cancel, Fill, IntentRecord, run_engine  # noqa: E402
from screening.stage_e_frozen import leg_inputs  # noqa: E402
from screening.stage_e_rules import StageERules, load_release_calendar  # noqa: E402
from strategy.members.k8 import flight, wkndbtc  # noqa: E402
from strategy.members.k8.flight import reference_dates  # noqa: E402
from tests import test_k8_members_flight as FK  # noqa: E402
from tests import test_k8_members_flight_engine as FE  # noqa: E402
from tests import test_k8_members_oilcad as OK  # noqa: E402
from tests import test_k8_members_wkndbtc as WK  # noqa: E402

REL = load_release_calendar()


def real_rules(member, window, blackout=()):  # noqa: ANN001
    return StageERules({leg.root: leg_inputs(leg.root, traded=leg.traded) for leg in member.legs},
                       frozenset(window), frozenset(blackout), REL)


def show(tag: str, res) -> None:  # noqa: ANN001
    fl = [(OK.ct(f.fill_ts_ns).strftime("%a %H:%M"), f.root, f.side, f.qty, f.reason)
          for f in res.events(Fill)]
    it = [(OK.ct(r.decision_ts_ns - 60 * OK.NS).strftime("%a %H:%M"), r.root,
           None if r.refusal is None else r.refusal.reason) for r in res.events(IntentRecord)]
    ca = [(OK.ct(c.ts_ns).strftime("%a %H:%M") if hasattr(c, "ts_ns") else "?", c.reason)
          for c in res.events(Cancel)]
    counters = {k: v for k, v in res.counters.items() if "guard" in k or "defer" in k
                or "skip" in k or "refus" in k}
    print(f"[{tag}] fills {fl}")
    print(f"[{tag}] intents {it}")
    print(f"[{tag}] cancels {ca} counters {counters}")


# ---- oilcad: WPSR date, triggers at 09:30 (guarded fill) and 09:35 (not guarded)
day = OK.WPSR_DAY
window = (*OK.refs_of(day), day)
bars = OK.oil_bars(day, {"09:30": 2, "09:35": 2})
res = OK.engine(OK.mk(), bars, real_rules(OK.mk(), window))
show("oilcad WPSR 09:30 skip, 09:35 enters", res)
assert not any("fill_guard_deferral" in k for k in res.counters), res.counters

# ---- oilcad: FOMC date, trigger at 13:00 (guarded) and 13:05
day = OK.FOMC_DAY
window = (*OK.refs_of(day), day)
bars = OK.oil_bars(day, {"13:00": 2, "13:05": 2})
res = OK.engine(OK.mk(), bars, real_rules(OK.mk(), window))
show("oilcad FOMC 13:00 skip, 13:05 enters", res)
assert not any("fill_guard_deferral" in k for k in res.counters), res.counters

# ---- oilcad: the dropped WPSR row 2026-05-28 11:00 CT (R-1b-1): skipped by the member
day = OK.DROPPED_WPSR_DAY
window = (*OK.refs_of(day), day)
bars = OK.oil_bars(day, {"11:00": 2, "11:05": 2})
res = OK.engine(OK.mk(), bars, real_rules(OK.mk(), window))
show("oilcad 2026-05-28 11:00 skip (R-1b-1), 11:05 enters", res)

# ---- oilcad: the logged edge (K8-L-08): a trigger at 09:25 whose 6C bars 09:25..09:29 are
# missing; the fill is pushed to 09:30 (guarded) and the ENGINE defers it to 09:32
day = OK.WPSR_DAY
window = (*OK.refs_of(day), day)
bars = OK.oil_bars(day, {"09:25": 2}, cad_skip=range(OK.hm(9, 25), OK.hm(9, 30)))
res = OK.engine(OK.mk(), bars, real_rules(OK.mk(), window))
show("oilcad EDGE: 09:25 trigger, 6C 09:25-09:29 missing -> engine defers into the guard", res)

# ---- flight: FOMC date, dips at k = 54 (t = 13:00, guarded) and k = 55 (13:05)
FOMC = FK.FOMC
refs = reference_dates(FOMC)
assert len(refs) == 20
mes_bars = []
for i, ref in enumerate(refs):
    dip = {10: FK.DIPS[i]} if i < len(FK.DIPS) else {}
    mes_bars += [(ref, FK.BLOCK_BARS[j], c, FK.MES_ID) for j, c in enumerate(FK.dip_path(dip))]
dips = {FK.end_bar(54): FK.B - 5, FK.end_bar(55): FK.B - 10}  # r_54 = -5/B, r_55 = -5/(B-5)
mes_bars += [(FOMC, m, dips.get(m, FK.B), FK.MES_ID) for m in range(FK.hm(8, 29), FK.hm(14, 55))]
mgc_bars = [(FOMC, m, FK.G, FK.MGC_ID) for m in range(FK.hm(8, 30), FK.hm(15, 11))]
frames = {"MGC": FE._rows("MGC", mgc_bars), "MES": FE._rows("MES", mes_bars)}
for factory in (flight.make_h30, flight.make_heod):
    m = factory()
    res = run_engine(frames, m, FE.LEGS, real_rules(m, (*refs, FOMC)))
    print(f"[flight {m.variant} FOMC] fills {FE.fills(res)} intents {FE.intents(res)} "
          f"guard counters {[k for k in res.counters if 'guard' in k]}")
    assert not any("fill_guard_deferral" in k for k in res.counters), res.counters

# ---- wkndbtc: a plain week with the real calendar (no MNQ row at Sunday 18:00)
bars = WK.week(WK.MON)
member = wkndbtc.make_mnq()
days = sorted({b.trade_date for _, b in bars})
res = OK.engine(member, bars, real_rules(member, days))
show("wkndbtc plain week", res)
assert not any("fill_guard_deferral" in k for k in res.counters), res.counters

# ---- cross-leg timing: every bar the member is shown opens at the view minute (closed at the
# decision time); the fill minute is strictly after the signal bar's open
class Spy:
    def __init__(self, inner):  # noqa: ANN001
        self.inner, self.name, self.legs, self.trading_windows = inner, inner.name, inner.legs, inner.trading_windows
        self.bad = 0
        self.views = 0

    def on_minute(self, view, account):  # noqa: ANN001
        self.views += 1
        for b in view.bars.values():
            if b is not None and b.ts_event_ns != view.ts_event_ns:
                self.bad += 1
        return self.inner.on_minute(view, account)


spy = Spy(OK.mk())
day = OK.PLAIN_DAY
bars = OK.oil_bars(day, {"09:05": 2})
res = OK.engine(spy, bars, real_rules(spy, (*OK.refs_of(day), day)))
fl = [(OK.ct(f.fill_ts_ns).strftime("%H:%M"), f.side) for f in res.events(Fill)]
print(f"[timing] views {spy.views} bars not opening at the view minute {spy.bad}; fills {fl}")
assert spy.bad == 0
print("ENGINE CHECKS DONE")
