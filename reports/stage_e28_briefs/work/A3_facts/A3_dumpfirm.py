"""A3 helper: compact dump of A2 firm JSON sections (value + note, truncated)."""
import json, sys
f = sys.argv[1]; secs = sys.argv[2].split(','); W = int(sys.argv[3]) if len(sys.argv) > 3 else 220
d = json.load(open(f))
def show(path, v):
    if isinstance(v, dict) and 'value' in v:
        print(f"{path}: V={json.dumps(v.get('value'))[:W]} | Q={str(v.get('quote'))[:W]} | N={str(v.get('note'))[:W]}")
    elif isinstance(v, dict):
        for k, x in v.items(): show(path + '.' + k, x)
    else:
        print(f"{path}: {json.dumps(v)[:W]}")
for s in secs:
    if s in d: show(s, d[s])
