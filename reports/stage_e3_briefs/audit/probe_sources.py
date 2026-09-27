"""Auditor probe: structure of the frozen release calendar and the rates calendar (counts only)."""
import hashlib, json, sys
from collections import Counter
p = "reports/stage_e2b_release_calendar.json"
raw = open(p, "rb").read()
print("release calendar sha256", hashlib.sha256(raw).hexdigest())
d = json.loads(raw)
print("top keys", sorted(d.keys()))
rel = d["releases"]
print("n releases", len(rel))
print("entry keys", sorted(rel[0].keys()))
kinds = Counter(r["id"].rsplit("-", 1)[0].split("-")[0] for r in rel)
print("id prefixes", dict(kinds.most_common(12)))
ex = [r for r in rel if r["id"].startswith("TREASURY_AUCTION")][:2]
print("auction examples", ex)
ex = [r for r in rel if r["id"].startswith("FOMC")][:1]
print("fomc example", ex)
ex = [r for r in rel if r["id"].startswith("ISM")][:1]
print("ism example", ex)
print("rates.py sha256", hashlib.sha256(open("data/calendars/rates.py","rb").read()).hexdigest())
from data.group_session import load_group_calendar
cal = load_group_calendar("rates")
print("calendar type", type(cal).__name__, [a for a in dir(cal) if not a.startswith("_")][:30])
