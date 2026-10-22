"""A3 helper: print compact value/unit/window/note of A1 fields (truncated)."""
import json, sys
f = sys.argv[1]; fields = sys.argv[2].split(',') if len(sys.argv) > 2 and sys.argv[2] else None
W = int(sys.argv[3]) if len(sys.argv) > 3 else 160
rows = json.load(open(f))
for r in rows:
    c = r.get('candidate') or r.get('code')
    print('#####', c)
    for k, v in r.items():
        if fields and k not in fields: continue
        if isinstance(v, dict) and 'value' in v:
            s = f"{k}: V={json.dumps(v.get('value'))[:W]} | U={str(v.get('unit'))[:40]} | W={str(v.get('window'))[:40]} | N={str(v.get('note'))[:W]}"
        else:
            s = f"{k}: {json.dumps(v)[:W]}"
        print(s)
