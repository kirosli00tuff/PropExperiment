import csv, hashlib, re, sys, datetime as dt
from collections import Counter, defaultdict
files = ["reports/stage_e31_briefs/research/usda_releases.csv", "reports/stage_e31_briefs/research/usda_releases_ext.csv"]
REPORTS = {"USDA WASDE","NASS Crop Production","NASS Crop Production Annual","NASS Grain Stocks","NASS Prospective Plantings","NASS Acreage","NOPA Monthly Crush (not USDA)"}
cnt = Counter(); nopa_months = defaultdict(int); invalid = 0; comments = 0; mins = {}; maxs = {}
for f in files:
    b = open(f,'rb').read(); print(f, hashlib.sha256(b).hexdigest(), len(b))
    lines = [l for l in b.decode().splitlines()]
    comments += sum(1 for l in lines if l.startswith('#'))
    rows = list(csv.DictReader(l for l in lines if not l.startswith('#')))
    print(" header:", list(rows[0].keys()))
    for r in rows:
        try: d = dt.date.fromisoformat(r['date']); assert re.fullmatch(r'\d{4}-\d{2}-\d{2}', r['date'])
        except Exception: invalid += 1; continue
        mins[f]=min(mins.get(f,d),d); maxs[f]=max(maxs.get(f,d),d)
        if r['time_et']=='12:00' and r['report'] in REPORTS:
            cnt[r['report']] += 1
            if r['report'].startswith('NOPA'): nopa_months[d.strftime('%Y-%m')] += 1
print("comments", comments, "invalid-date rows", invalid)
print("date ranges", {k:(str(v),str(maxs[k])) for k,v in mins.items()})
for k in sorted(cnt): print(f"  {k}: {cnt[k]}")
months = []
y,m = 2020,12
while (y,m) <= (2024,2):
    months.append(f"{y}-{m:02d}"); m += 1
    if m==13: y+=1; m=1
print("months in window", len(months))
print("months with no NOPA row:", [mo for mo in months if nopa_months.get(mo,0)==0])
print("months with >1 NOPA row:", [mo for mo in months if nopa_months.get(mo,0)>1])
print("NOPA rows outside window:", [mo for mo in nopa_months if mo not in months])
