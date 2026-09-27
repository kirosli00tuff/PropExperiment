"""Auditor Task 6 item 4 follow-up: replay K2-predrift-01 ZN and ZB through the runner's own functions
(determinism), then a wrapped replay that observes what the member saw on the untraded ISM dates. No
repository file is modified; the wrapper only records and delegates. Prints per-date facts."""
import sys, json; sys.path.insert(0, ".")
from datetime import datetime, UTC, date
from decimal import Decimal
from pathlib import Path
from zoneinfo import ZoneInfo
from screening import harness_freeze
from screening.stage_e_freeze import load_cluster_freeze, verify_cluster_code, resolve_member
from screening.stage_e_runner import (_legs_inputs, _load_frames, _run_member, extract_trips, _series,
                                      RESEARCH_WINDOW, RESEARCH)
from screening.stage_e_align import member_window
from screening.stage_e_rules import load_release_calendar
from screening.stage_e_engine import IntentRecord, Fill
from rules.products import product
CT = ZoneInfo("America/Chicago")
HARNESS = "cf939270f0a00be74aa29a43f0c7de964256411a9cdcebc36f22fd3bdc021a45"
DATES = {"ZN": ["2025-07-03", "2026-05-05", "2026-06-03"], "ZB": ["2025-07-03", "2025-08-05", "2026-05-05", "2026-06-03"]}
def ct(ns): return datetime.fromtimestamp(ns / 1e9, tz=UTC).astimezone(CT)
def ticks(price, tick): return int(round(Decimal(repr(price)) / tick))

class Observer:
    """Delegates every call to the real member; records the bars at 08:30 and 08:49 CT on the dates of interest."""
    def __init__(self, inner, root, days):
        self._inner, self.root, self._days = inner, root, set(days)
        self.name, self.legs, self.trading_windows = inner.name, inner.legs, inner.trading_windows
        self.seen = {}
    def on_minute(self, view, account):
        bar = view.bar(self.root)
        items = self._inner.on_minute(view, account)
        if bar is not None:
            t = ct(bar.ts_event_ns); key = (t.date().isoformat(), t.strftime("%H:%M"))
            if key[0] in self._days and key[1] in ("08:30", "08:49"):
                self.seen[key] = {"trade_date": str(bar.trade_date), "instrument_id": bar.instrument_id,
                                  "early_halt_ct": None if bar.early_halt_ct is None else str(bar.early_halt_ct),
                                  "open": bar.open, "close": bar.close, "position": account.position(self.root),
                                  "pending": account.pending.get(self.root, 0), "items": [repr(i) for i in items],
                                  "member_start_ticks": getattr(self._inner, "_start_ticks", None),
                                  "member_entry_done": getattr(self._inner, "_entry_done", None)}
        return items

print("preflight", harness_freeze.preflight(HARNESS)[:16])
freeze = load_cluster_freeze("K2"); verify_cluster_code(freeze)
releases = load_release_calendar()
out = {}
for root in ("ZN", "ZB"):
    label = f"K2-predrift-01 {root}"
    decl, factory = resolve_member(freeze, label, None)
    legs = decl.legs; inputs = _legs_inputs(legs)
    frames, _ = _load_frames(legs, inputs, RESEARCH_WINDOW, Path("data/processed"), Path("data/processed_step2"))
    mw = member_window(frames, RESEARCH)
    rec = json.load(open(f"reports/stage_e3_k2_screen/K2_{label.replace(' ', '_')}_research.json"))
    # 1. plain replay: determinism
    plain = _run_member(factory(), legs, inputs, frames, mw.dates, mw.blackout_union, releases)
    s_plain = _series(label, legs, inputs, extract_trips(plain), mw.dates)
    eq_plain = list(s_plain.values) == rec["series"]["values"] and [d.isoformat() for d in s_plain.dates] == rec["series"]["dates"] and dict(plain.counters) == rec["engine"]["counters"]
    # 2. wrapped replay: observe
    inner = factory(); obs = Observer(inner, root, DATES[root])
    wrapped = _run_member(obs, legs, inputs, frames, mw.dates, mw.blackout_union, releases)
    s_wr = _series(label, legs, inputs, extract_trips(wrapped), mw.dates)
    eq_wr = list(s_wr.values) == rec["series"]["values"] and dict(wrapped.counters) == rec["engine"]["counters"]
    print(f"{label}: plain replay equals record {eq_plain}; wrapped replay equals record {eq_wr}; n_trips {s_plain.n_trips}/{s_wr.n_trips} (record {rec['series']['n_trips']}); bar sha equal {frames[root].sha256 == rec['bars'][root]['sha256']}")
    tick = product(root).vendor_tick
    intents = [(ct(r.decision_ts_ns - 60_000_000_000).isoformat(timespec='minutes'), r.accepted, None if r.refusal is None else r.refusal.reason)
               for r in wrapped.events(IntentRecord) if ct(r.decision_ts_ns).date().isoformat() in DATES[root]]
    fills = [(ct(f.fill_ts_ns).isoformat(timespec='minutes'), f.side, f.reason) for f in wrapped.events(Fill) if ct(f.fill_ts_ns).date().isoformat() in DATES[root]]
    ism = getattr(inner, "_events", frozenset())
    for day in DATES[root]:
        b30 = obs.seen.get((day, "08:30")); b49 = obs.seen.get((day, "08:49"))
        in_window = day in rec["series"]["dates"]; is_event = date.fromisoformat(day) in ism
        s = None if not (b30 and b49) else ticks(b49["close"], tick) - ticks(b30["open"], tick)
        if not is_event: cause = "not an ISM date in the member's table"
        elif not in_window: cause = "date not in the window"
        elif b30 is None or b49 is None: cause = "missing bar (" + ("08:30 " if b30 is None else "") + ("08:49" if b49 is None else "") + ")"
        elif b49["early_halt_ct"] is not None: cause = "early halt"
        elif b30["instrument_id"] != b49["instrument_id"]: cause = "instrument guard"
        elif s == 0: cause = "s = 0"
        elif b49["items"]: cause = "intent emitted: " + ("engine refusal" if any(i[0].startswith(day) and not i[1] for i in intents) else "accepted?")
        else: cause = "member defect: s != 0 and no intent"
        row = {"date": day, "in_window": in_window, "ism_event": is_event, "bar_0830": b30, "bar_0849": b49, "s_ticks": s,
               "intents": [i for i in intents if i[0].startswith(day)], "fills": [f for f in fills if f[0].startswith(day)], "cause": cause}
        out[f"{root} {day}"] = row
        short = lambda b: None if b is None else (b["instrument_id"], b["early_halt_ct"], b["open"], b["close"], b["items"])
        print(f"  {root} {day}: window {in_window}, ISM {is_event}, 08:30 {short(b30)}, 08:49 {short(b49)}, s {s}, intents {row['intents']}, fills {row['fills']}, cause: {cause}")
    out[f"{root} determinism"] = {"plain_equals_record": eq_plain, "wrapped_equals_record": eq_wr}
json.dump(out, open("reports/stage_e3_briefs/audit/predrift_followup.json", "w"), indent=1, default=str)
print("done")
