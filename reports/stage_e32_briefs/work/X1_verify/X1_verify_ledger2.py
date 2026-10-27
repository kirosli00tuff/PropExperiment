"""Counts only: lines without a 'request' object, and lines whose top-level 'symbol' or 'schema'
field (older format) names ZM/ZS/ZL, grouped by (event, top-level schema, top-level symbol)
with min/max top-level 'date'. Prints no other value."""
import json, collections, re
P = re.compile(r"^(ZM|ZS|ZL)([.\-_ ]|$)")
noreq = 0; c = collections.defaultdict(lambda: [0, "9999", "0000"])
for line in open("ledger/databento_spend.jsonl"):
    d = json.loads(line)
    if not d.get("request"):
        noreq += 1
    sym = str(d.get("symbol"))
    if P.match(sym):
        k = (d.get("event"), d.get("schema"), sym[:30], bool(d.get("request")))
        v = c[k]; v[0] += 1; dt = str(d.get("date"))[:10]; v[1] = min(v[1], dt); v[2] = max(v[2], dt)
print("lines without request:", noreq)
for k, v in sorted(c.items(), key=str):
    print(k, v)
