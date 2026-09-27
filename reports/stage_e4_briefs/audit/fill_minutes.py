"""Task 6 item 4 detail: classify every fill-minute deviation (D9.5a guard, later bar, engine close) and the Tier A
trial's unverifiable-date sensitivity. Read-only; uses the runner's trip lists and the frozen tables only."""
from __future__ import annotations
import json, math
from collections import Counter, defaultdict
from datetime import datetime, UTC
from pathlib import Path
from zoneinfo import ZoneInfo
from strategy.members.k4._releases import NGS, WPSR, NGS_UNVERIFIED_IN_WINDOW
CT = ZoneInfo("America/Chicago"); OUT = Path("reports/stage_e4_k4_screen"); NS_MIN = 60_000_000_000
cal = json.loads(Path("reports/stage_e2b_release_calendar.json").read_text())
rel = defaultdict(list)
for r in cal["releases"]:
    inst = int(datetime.fromisoformat(r["instant_utc"].replace("Z", "+00:00")).timestamp()) * 10**9
    for root in r["products"]: rel[root].append((inst, r["release"]))
def ct(ns): return datetime.fromtimestamp(ns / 1e9, tz=UTC).astimezone(CT)
def mod(ns): t = ct(ns); return t.hour * 60 + t.minute
def cm(s): h, m = s.split(":"); return int(h) * 60 + int(m)
def fmt(m): return f"{m // 60:02d}:{m % 60:02d}"
def guard(root, nominal_ns, actual_ns):
    """D9.5a: the nominal fill lies in [release, release + 2 min) of a release concerning root and the actual fill is at release + 2."""
    for inst, name in rel[root]:
        if inst <= nominal_ns < inst + 2 * NS_MIN and actual_ns == inst + 2 * NS_MIN: return name
    return None
wpsr = {d: t for d, t, _, _ in WPSR}; ngs = dict(NGS)
def nominal(label, x):
    mid = label.split()[0]; d = x["trade_date"]; o = mod(x["open_ts_ns"])
    if mid == "K4-cp1-01": return cm("13:00"), cm("13:29")
    if mid == "K4-cp3-01": return cm("08:01"), cm("13:29")
    if mid == "K4-ngpre-01": t = cm(ngs[d]); return t - 90, t + 30
    if mid == "K4-apipre-01": return cm("07:30"), cm("09:29")
    if mid == "K4-eiafade-01": return cm(wpsr[d]) + 15, cm("13:29")
    if mid == "K4-eiamom-01": return cm("14:30"), cm("14:59")
    if mid == "K4-cp2-01": return (o if cm("08:16") <= o <= cm("13:30") else None), (o + 75)
    if mid == "K4-ovr-01":
        t = o - o % 60 if o % 60 <= 2 and cm("09:00") <= o - o % 60 <= cm("13:00") else None
        return t, (None if t is None else t + 59)
totals = Counter()
for p in sorted(OUT.glob("K4_*_research_trips.json")):
    tl = json.loads(p.read_text()); label = tl["member"]; root = tl["trips"][0]["root"]
    kinds = Counter(); detail = []
    for x in tl["trips"]:
        o, c = mod(x["open_ts_ns"]), mod(x["close_ts_ns"]); eo, ec = nominal(label, x)
        day0 = x["open_ts_ns"] - o * NS_MIN
        notes = []
        if eo is None: notes.append(f"entry {fmt(o)} not a rule minute")
        elif o != eo:
            g = guard(root, day0 + eo * NS_MIN, x["open_ts_ns"])
            notes.append(f"entry {fmt(o)} vs {fmt(eo)}: " + (f"D9.5a guard ({g})" if g else "later bar (nominal bar missing; unverifiable without bars)"))
        if x["close_reason"] != "strategy": notes.append(f"engine close {x['close_reason']} at {fmt(c)} (nominal {fmt(ec) if ec else '?'})")
        elif ec is not None and c != ec:
            g = guard(root, day0 + ec * NS_MIN, x["close_ts_ns"])
            if label.startswith("K4-cp2") and not g:
                notes.append(f"exit {fmt(c)} vs {fmt(ec)}: +{c - ec} present-bar count (missing bar in the hold; unverifiable without bars)")
            else:
                notes.append(f"exit {fmt(c)} vs {fmt(ec)}: " + (f"D9.5a guard ({g})" if g else "later bar (nominal bar missing; unverifiable without bars)"))
        if notes: detail.append((x["trade_date"], "; ".join(notes)))
        for n in notes:
            k = "D9.5a" if "D9.5a" in n else ("engine close: " + x["close_reason"] if "engine close" in n else "later bar / missing bar")
            kinds[k] += 1
        if not notes: kinds["exact"] += 1
    print(f"{label:18s} {len(tl['trips']):3d} trips: {dict(kinds)}")
    for d in detail: print("   ", d)
    totals.update(kinds)
print("TOTAL", dict(totals))
# Tier A sensitivity: the three unverifiable NGS dates
tl = json.loads((OUT / "K4_K4-ngpre-01_NG_research_trips.json").read_text()); rec = json.loads((OUT / "K4_K4-ngpre-01_NG_research.json").read_text())
traded = {x["trade_date"]: x for x in tl["trips"]}
print("ngpre NG unverifiable NGS dates:", [(d, d in traded, traded[d]["net_cents"] if d in traded else None) for d in NGS_UNVERIFIED_IN_WINDOW])
vals, dates = rec["series"]["values"], rec["series"]["dates"]
def scr(vs):
    n = len(vs); m = math.fsum(vs) / n; sd = math.sqrt(math.fsum((v - m) ** 2 for v in vs) / n); t = m / (sd / math.sqrt(n)); return round(m, 4), round(t, 4), bool(m > 0 and t >= 1)
print("  screen as run:", scr(vals))
print("  unverifiable days zeroed:", scr([0.0 if d in NGS_UNVERIFIED_IN_WINDOW else v for d, v in zip(dates, vals)]))
print("  unverifiable days dropped:", scr([v for d, v in zip(dates, vals) if d not in NGS_UNVERIFIED_IN_WINDOW]))
print("  D9.5a-deferred days (09:32 entries) zeroed:", scr([0.0 if d in ("2025-06-18", "2025-11-26", "2025-12-31") else v for d, v in zip(dates, vals)]))
wins = sorted(((v, d) for d, v in zip(dates, vals) if v != 0), reverse=True)
print("  top 3 days:", wins[:3], "bottom 3:", wins[-3:], "positive days:", sum(1 for v in vals if v > 0), "negative:", sum(1 for v in vals if v < 0))
print("  screen without the best day:", scr([v for d, v in zip(dates, vals) if d != wins[0][1]]))
