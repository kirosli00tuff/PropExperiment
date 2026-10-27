"""Print only the minimum requested start string (full timestamp) per (schema, symbols, event) for ZM/ZS/ZL
mbo, mbp-1, tbbo and definition lines. No other field is printed."""
import json, re
P = re.compile(r"^(ZM|ZS|ZL)([.\-_ ]|$)")
m = {}
for line in open("ledger/databento_spend.jsonl"):
    d = json.loads(line); r = d["request"]
    syms = r["symbols"] if isinstance(r["symbols"], list) else [r["symbols"]]
    if r.get("schema") not in ("mbo", "mbp-1", "tbbo", "definition"): continue
    if not any(P.match(str(s)) for s in syms): continue
    k = (r["schema"], ",".join(sorted(map(str, syms))), d["event"]); s = str(r["start"])
    m[k] = min(m.get(k, s), s)
for k in sorted(m): print(k, m[k])
