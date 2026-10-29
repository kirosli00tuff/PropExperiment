import json, sys
p = sys.argv[1]
d = json.load(open(p))
print("TOPTYPE", type(d).__name__)
if isinstance(d, dict):
    for k, v in d.items():
        if isinstance(v, (dict, list)):
            print("KEY", k, type(v).__name__, len(v))
        else:
            s = str(v)
            print("KEY", k, type(v).__name__, len(s))
