import json, sys, os, subprocess
# usage: merge.py SECTION ratings.json   (SECTION in codes|pairs|firms); ratings = {label: {crit: R}}
OUT = '/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e32b_briefs/F4_blind_ratings_masked.json'
sec, src = sys.argv[1], sys.argv[2]
new = json.load(open(src))
if os.path.exists(OUT):
    out = json.load(open(OUT))
else:
    out = {"rater": "BlindScorer2-OpusXHigh", "generated_pdt": "", "codes": {}, "pairs": {}, "firms": {}}
for lab, crits in new.items():
    for c, r in crits.items():
        assert set(r) <= {"value", "unknown", "reason", "unverified"}, (lab, c, r)
        assert isinstance(r["unknown"], bool) and isinstance(r["reason"], str) and isinstance(r["value"], (int, float)), (lab, c)
        out[sec].setdefault(lab, {})[c] = r
out["generated_pdt"] = subprocess.check_output(['date', '+%Y-%m-%d %H:%M %Z'], env={'TZ': 'America/Vancouver'}).decode().strip()
tmp = OUT + '.tmp'
json.dump(out, open(tmp, 'w'), indent=1, ensure_ascii=False)
os.replace(tmp, OUT)
print('merged', sec, len(new), 'labels; section now', len(out[sec]), 'labels; time', out["generated_pdt"])
