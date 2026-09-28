"""Stage E.7 Task 3 audit (MemberAuditor-K1-FableXHigh): the auditor's own checks that the coders'
tests do not make, on synthetic bars through the real engine (the test kits' bar builders) and with
exact-rational oracles for the three members' integer arithmetic.

Read-only on the repository. No bar file is read; no runner; no freeze. Prints one line per check.
Run: PYTHONPYCACHEPREFIX=<fresh dir> uv run python reports/stage_e7_briefs/audit_k1/auditor_scenarios.py
"""

from __future__ import annotations

import random
from datetime import date, time
from decimal import Decimal
from fractions import Fraction

from strategy.members.k1 import cp3, vwap, vxnband
from strategy.members.k1 import _event_common as common
from tests import test_k1_members_ports as pk
from tests.test_k1_members_vxnband import (
    D0, D1, ID, Day, at, bars, call, fills, hm, intents, ns_at, run, trips,
)

random.seed(20260928)
FAILS: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    print(f"{'ok  ' if ok else 'FAIL'} {name} {detail}")
    if not ok:
        FAILS.append(name)


# ---------------------------------------------------------------- exact-arithmetic oracles ----
def oracle_breach(close: int, prev: int, v: Fraction) -> str | None:
    w = Fraction(prev) * v / 1600
    if Fraction(close) > prev + w:
        return "sell"
    if Fraction(close) < prev - w:
        return "buy"
    return None


bad = 0
for _ in range(20000):
    prev = random.randint(60_000, 200_000)
    v = Decimal(random.randint(500, 6000)) / Decimal(100)  # 5.00 .. 60.00
    if random.random() < 0.3:
        v = v + Decimal(random.randint(0, 999999)) / Decimal(1_000_000)
    n, m = v.as_integer_ratio()
    vf = Fraction(n, m)
    # closes near the band edges and at random
    w = Fraction(prev) * vf / 1600
    edges = [prev + int(w), prev + int(w) + 1, prev - int(w), prev - int(w) - 1,
             random.randint(prev - 3000, prev + 3000)]
    for close in edges:
        if vxnband.breach_side(close, prev, v) != oracle_breach(close, prev, vf):
            bad += 1
check("vxnband.breach_side equals the Fraction oracle on 100k random cases", bad == 0, f"bad={bad}")


def oracle_clv(high: int, low: int, close: int) -> str | None:
    if high - low <= 0:
        return None
    clv = Fraction(close - low, high - low)
    if clv >= Fraction(4, 5):
        return "buy"
    if clv <= Fraction(1, 5):
        return "sell"
    return None


bad = 0
for _ in range(50000):
    low = random.randint(0, 100000)
    span = random.randint(0, 400)
    close = low + random.randint(-5, span + 5)
    if cp3.clv_side(cp3.DailyBar(D0, low + span, low, close, ID)) != oracle_clv(low + span, low, close):
        bad += 1
check("cp3.clv_side equals the Fraction oracle on 50k random cases", bad == 0, f"bad={bad}")


def oracle_vwap_sign(hlc_vol: list[tuple[int, int, int, int]]) -> list[int]:
    """s after each bar from exact rational VWAP of TP; tie keeps the sign; no volume: no update."""
    out, s, num, den = [], 0, Fraction(0), Fraction(0)
    for h, lo, c, vol in hlc_vol:
        num += Fraction(h + lo + c, 3) * vol
        den += vol
        if den == 0:
            out.append(s)
            continue
        vwap_ = num / den
        if Fraction(c) > vwap_:
            s = 1
        elif Fraction(c) < vwap_:
            s = -1
        out.append(s)
    return out


bad = 0
for _ in range(3000):
    n = random.randint(1, 12)
    seq = []
    for _b in range(n):
        c = random.randint(-30, 30)
        h = c + random.randint(0, 6)
        lo = c - random.randint(0, 6)
        vol = random.choice([0, 0, 1, 3, 10, 250])
        seq.append((h, lo, c, vol))
    member = vwap.make_mnq()
    day = Day(D1, start=hm(8, 30), end=hm(8, 30) + n,
              closes={hm(8, 30) + i: seq[i][2] for i in range(n)},
              highs={hm(8, 30) + i: seq[i][0] for i in range(n)},
              lows={hm(8, 30) + i: seq[i][1] for i in range(n)},
              volumes={hm(8, 30) + i: seq[i][3] for i in range(n)})
    got = []
    for bar in bars([day]):
        call(member, bar, position=0, pending=1)  # pending: nothing is sent
        got.append(member._s)
    # the kit's H and L span O = C and the offsets: recompute the true H/L the bar carries
    true = []
    for bar in bars([day]):
        tick = common.leg_facts().tick
        true.append((common.to_ticks(bar.high, tick), common.to_ticks(bar.low, tick),
                     common.to_ticks(bar.close, tick), bar.volume))
    if got != oracle_vwap_sign(true):
        bad += 1
check("vwap sign sequence equals the Fraction VWAP oracle on 3k random days", bad == 0, f"bad={bad}")

# ---------------------------------------------------------------- vxnband scenarios ----
import pytest  # noqa: E402  (monkeypatch outside pytest)

mp = pytest.MonkeyPatch()
V_IN = "10.000000"


def use(table: dict[date, str]) -> None:
    mp.setattr(vxnband, "_VXN", {d: Decimal(v) for d, v in table.items()})


# S1: entry on the 14:28 bar; 14:58 and 14:59 missing: the exit goes on the 15:00 bar (fill 15:01)
use({D0: V_IN})
days = [Day(D0), Day(D1, closes={hm(14, 28): 2000, hm(14, 29): 0},
                      skip=frozenset({hm(14, 58), hm(14, 59)}))]
res = run(vxnband.make_mnq(), days)
check("S1 vxnband missing 14:58/14:59 -> exit on 15:00, fill 15:01",
      trips(res) == ([(at(D1, "14:28"), "sell", True), (at(D1, "15:00"), "buy", True)],
                     [(at(D1, "14:29"), "sell", "strategy"), (at(D1, "15:01"), "buy", "strategy")]),
      str(trips(res)))

# S2: an instrument change AFTER the breach (during the hold) changes nothing in the member
use({D0: V_IN})
days = [Day(D0), Day(D1, closes={hm(9, 0): 2000, hm(9, 1): 0}, ids={hm(9, 10): 778})]
member = vxnband.make_mnq()
got = []
for bar in bars(days):
    pos = -1 if (bar.trade_date == D1 and ns_at(D1, hm(9, 1)) <= bar.ts_event_ns <= ns_at(D1, hm(9, 30))) else 0
    items = call(member, bar, position=pos)
    if items:
        got.append((bar.ts_event_ns, [i.side for i in items]))
check("S2 vxnband id change during the hold: entry 09:00, exit 09:30 only",
      got == [(ns_at(D1, hm(9, 0)), ["sell"]), (ns_at(D1, hm(9, 30)), ["buy"])], str(got))

# S3: the real table across Good Friday 2025: d = 04-21 uses the 04-17 row (no 04-18 row exists)
mp.undo()
v_0417 = dict(vxnband.VXN_CLOSE).get("2025-04-17")
check("S3 vxn_for(2025-04-21) is the 2025-04-17 close",
      vxnband.vxn_for(date(2025, 4, 21)) == Decimal(v_0417) and "2025-04-18" not in dict(vxnband.VXN_CLOSE),
      f"{vxnband.vxn_for(date(2025, 4, 21))} vs {v_0417}")

# S4: V is never a later date's close: for every table date, vxn_for(d) is the row of a date < d
mp.undo()
bad = 0
rows = dict(vxnband.VXN_CLOSE)
for iso in common.EQUITY_TRADE_DATES:
    d = date.fromisoformat(iso)
    v = vxnband.vxn_for(d)
    p = common.PREVIOUS_TRADE_DATE.get(d)
    if v is not None and not (p is not None and p < d and Decimal(rows[p.isoformat()]) == v):
        bad += 1
check("S4 V(d) is always the row of the EC-CAL trade date before d (all 1846 dates)", bad == 0, f"bad={bad}")

# S5: vxnband regime edge through the engine with V = 20 exactly and 30 exactly
for v, expect in (("20.000000", False), ("30.000000", True), ("19.999999", True), ("29.999999", False)):
    mp.setattr(vxnband, "_VXN", {D0: Decimal(v)})
    res = run(vxnband.make_mnq(), [Day(D0), Day(D1, closes={hm(9, 0): 5000, hm(9, 1): 0})])
    check(f"S5 vxnband regime V={v} trades={expect}", (len(fills(res)) == 2) == expect)
mp.undo()

# ---------------------------------------------------------------- vwap scenarios ----
UP, DOWN = 40, -40
# S6: entry intent on 14:56 (fill 14:57 = k), 14:58 missing: the final exit goes on 14:59 (k + 2)
res = run(vwap.make_mnq(), [Day(D0), Day(D1, closes={hm(14, 56): UP}, skip=frozenset({hm(14, 58)}))])
check("S6 vwap 14:56 entry, 14:58 missing -> final exit 14:59, fill 15:00",
      intents(res) == [(at(D1, "14:56"), "buy", True), (at(D1, "14:59"), "sell", True)]
      and fills(res) == [(at(D1, "14:57"), "buy", "strategy"), (at(D1, "15:00"), "sell", "strategy")],
      str((intents(res), fills(res))))

# S7: the reversal pair on bar k + 1 is accepted by the engine's D9.3b (decision = fill + 120 s)
res = run(vwap.make_mnq(), [Day(D0), Day(D1, closes={hm(9, 0): UP, hm(9, 1): DOWN})])
recs = [(r.accepted, r.refusal.reason if r.refusal else None) for r in res.events(__import__("screening.stage_e_engine", fromlist=["IntentRecord"]).IntentRecord)]
check("S7 vwap reversal on k+1: every intent accepted (no engine_min_hold)",
      all(a for a, _ in recs) and len(recs) >= 3, str(recs[:4]))

# S8: 20 entries via reversals: the 21st opposite signal exits to flat, no engine_entry_cap ever
def alternating(first: int, count: int, step: int = 2) -> dict[int, int]:
    return {first + step * i: (UP if i % 2 == 0 else DOWN) for i in range(count)}


res = run(vwap.make_mnq(), [Day(D0), Day(D1, closes=alternating(hm(9, 0), 30))])
recs = res.events(__import__("screening.stage_e_engine", fromlist=["IntentRecord"]).IntentRecord)
n_entry = sum(1 for r in recs if r.accepted) - 20  # 20 entries + 20 exits = 40 accepted
check("S8 vwap cap: 40 accepted intents (20 entries, 20 exits), none refused, ends flat",
      len(recs) == 40 and all(r.accepted for r in recs) and res.events(
          __import__("screening.stage_e_engine", fromlist=["Fill"]).Fill)[-1].position_after == 0,
      f"intents={len(recs)} refused={[r.refusal.reason for r in recs if not r.accepted][:2]}")

# S9: the 09:01 bar is missing, so the 09:00 entry fills at the 09:02 open (k = 09:02, the bar at
# whose call the position is first seen); the 09:02 flip waits for the hold; on 09:03 the exit
# goes, and because the missing 09:01 bar is a gap (K1-L-07) there is NO new leg: the member exits
# to flat and sends nothing more that day (no final exit either: flat)
res = run(vwap.make_mnq(), [Day(D0), Day(D1, closes={hm(9, 0): UP, hm(9, 2): DOWN},
                                          skip=frozenset({hm(9, 1)}))])
check("S9 vwap gap at 09:01: fill 09:02 (k), flip on 09:02 waits, 09:03 exit to flat, no new leg, nothing after",
      intents(res) == [(at(D1, "09:00"), "buy", True), (at(D1, "09:03"), "sell", True)]
      and fills(res) == [(at(D1, "09:02"), "buy", "strategy"), (at(D1, "09:04"), "sell", "strategy")],
      str((intents(res), fills(res))))

# ---------------------------------------------------------------- ports: q_c on every leg ----
for module in (pk.cp1, pk.cp2, pk.cp3):
    for root in pk.ROOTS:
        m = pk.make(module, root)
        check(f"{module.MEMBER_ID} {root} q_c from the frozen table = {pk.Q_C[root]}",
              m._leg.q == pk.Q_C[root] and m.name == f"{module.MEMBER_ID} {root}")

# S10: cp1 with 14:29 present but a position still open from an engine-deferred fill? (cannot be);
# instead: cp1 entry refused by the engine on a roll-blackout date sends exactly one intent
from screening.stage_e_frozen import leg_inputs  # noqa: E402
from screening.stage_e_rules import StageERules  # noqa: E402

blackout_rules = StageERules({"MNQ": leg_inputs("MNQ", traded=True)}, frozenset({pk.MON, pk.TUE}),
                             frozenset({pk.TUE}), pk.NO_RELEASES)
res = pk.run(pk.make(pk.cp1, "MNQ"), [pk.cp1_day()], rules=blackout_rules)
check("S10 cp1 on a roll-blackout date: one refused intent, no resend",
      pk.intents(res) == [(pk.TUE, "14:29", False, "engine_roll_blackout")], str(pk.intents(res)))

print("\nFAILS:", FAILS if FAILS else "none")
