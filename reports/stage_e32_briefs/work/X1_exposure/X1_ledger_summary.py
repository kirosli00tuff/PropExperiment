import json, collections, re, sys
ROOTS = ("ZM", "ZS", "ZL")
g = collections.defaultdict(lambda: [0, "9999", "0000", collections.Counter()])
for l in open("ledger/databento_spend.jsonl"):
    d = json.loads(l)
    r = d["request"]
    syms = r["symbols"] if isinstance(r["symbols"], list) else [r["symbols"]]
    hit = [s for s in syms if re.match(r"^(ZM|ZS|ZL)[.\-_ ]", str(s)) or str(s) in ROOTS]
    if not hit:
        continue
    key = (r["dataset"], r["schema"], ",".join(sorted(set(str(s) for s in syms)))[:60], d["event"])
    # group by dataset, schema, symbols, event; range min start / max end
    e = g[key]
    e[0] += 1
    e[1] = min(e[1], str(r["start"])[:10]); e[2] = max(e[2], str(r["end"])[:10])
for k in sorted(g):
    v = g[k]
    print(" | ".join(k), "| n=%d | min_start=%s | max_end=%s" % (v[0], v[1], v[2]))

print("--- union of committed ranges (ohlcv-1m, mbp-1, mbo, definition) per symbol set")
import datetime as dt
u = collections.defaultdict(list)
for l in open("ledger/databento_spend.jsonl"):
    d = json.loads(l)
    if d["event"] != "commit":
        continue
    r = d["request"]
    syms = r["symbols"] if isinstance(r["symbols"], list) else [r["symbols"]]
    if not any(str(s)[:2] in ROOTS for s in syms):
        continue
    u[(r["schema"], ",".join(sorted(set(str(s) for s in syms)))[:60])].append((str(r["start"])[:10], str(r["end"])[:10]))
for k, rs in sorted(u.items()):
    rs.sort()
    merged = []
    for a, b in rs:
        if merged and a <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], b)
        else:
            merged.append([a, b])
    print(k, len(rs), merged)
