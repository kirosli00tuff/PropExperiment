"""Print a JSON file's skeleton: keys, types, list lengths; strings truncated. Usage: skel.py FILE [depth] [path.to.node]"""
import json, sys
def sk(x, d, maxd, ind, maxkeys=12):
    p = "  " * ind
    if isinstance(x, dict):
        ks = list(x)
        print(f"{p}{{dict {len(ks)}}}")
        if d >= maxd: print(p + "  keys: " + ", ".join(ks[:30])[:300]); return
        for k in ks[:maxkeys]:
            v = x[k]
            if isinstance(v, (dict, list)):
                print(f"{p}  {k}:"); sk(v, d + 1, maxd, ind + 2)
            else:
                print(f"{p}  {k}: {repr(v)[:110]}")
        if len(ks) > maxkeys: print(f"{p}  ... +{len(ks)-maxkeys} keys: " + ", ".join(ks[maxkeys:maxkeys+40])[:400])
    elif isinstance(x, list):
        print(f"{p}[list {len(x)}]")
        if x and d < maxd:
            sk(x[0], d + 1, maxd, ind + 1)
    else:
        print(f"{p}{repr(x)[:110]}")
doc = json.load(open(sys.argv[1]))
maxd = int(sys.argv[2]) if len(sys.argv) > 2 else 2
if len(sys.argv) > 3:
    for k in sys.argv[3].split("."):
        doc = doc[int(k)] if isinstance(doc, list) else doc[k]
sk(doc, 0, maxd, 0)
