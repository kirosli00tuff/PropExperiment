import json, sys
d = json.load(open('reports/stage_e28_briefs/A1_grains.json'))
fields = sys.argv[1].split(',')
codes = sys.argv[2].split(',') if len(sys.argv) > 2 else None
width = int(sys.argv[3]) if len(sys.argv) > 3 else 400
for i, e in enumerate(d):
    c = e['candidate']
    if codes and c not in codes:
        continue
    for f in fields:
        v = e.get(f)
        if v is None:
            print(f"[{i}] {c}.{f}: MISSING"); continue
        s = json.dumps(v, ensure_ascii=False)
        print(f"[{i}] {c}.{f}: {s[:width]}")
