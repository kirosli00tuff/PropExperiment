"""A3 helper: print a firm JSON section flattened (value | note | quote prefix), no market data."""
import json
import sys

def walk(x, p, qlen):
    if isinstance(x, dict):
        if "value" in x and ("quote" in x or "source_file" in x):
            q = (x.get("quote") or "")
            q = q if isinstance(q, str) else json.dumps(q)
            print(f"{p} = {json.dumps(x['value'])[:200]} | {str(x.get('unit') or '')[:40]} | "
                  f"{(x.get('note') or '')[:220]} | Q: {q[:qlen]}")
            return
        for k, v in x.items():
            walk(v, f"{p}.{k}", qlen)
    elif isinstance(x, list):
        for i, v in enumerate(x):
            walk(v, f"{p}[{i}]", qlen)
    else:
        print(f"{p} = {json.dumps(x)[:200]}")

firm, sections, qlen = sys.argv[1], sys.argv[2].split(","), int(sys.argv[3]) if len(sys.argv) > 3 else 0
d = json.load(open(f"reports/stage_e28_briefs/A2_firm_{firm}.json"))
for s in sections:
    walk(d.get(s), s, qlen)
