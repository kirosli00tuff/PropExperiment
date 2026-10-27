"""Release-calendar schema check (reference data, not market data): report strings, times, anomalous rows."""
import csv, collections, io
SIX = {'USDA WASDE', 'NASS Crop Production', 'NASS Crop Production Annual', 'NASS Grain Stocks',
       'NASS Prospective Plantings', 'NASS Acreage', 'NOPA Monthly Crush (not USDA)'}
for f in ["usda_releases.csv", "usda_releases_ext.csv"]:
    p = f"reports/stage_e31_briefs/research/{f}"
    lines = open(p).read().splitlines()
    body = [l for l in lines if not l.startswith('#')]
    print("==", f, "comment lines:", len(lines) - len(body))
    rows = list(csv.DictReader(io.StringIO("\n".join(body))))
    print("  rows", len(rows), "reports:", dict(collections.Counter(x['report'] for x in rows)))
    print("  six-report rows by time:", dict(collections.Counter((x['report'], x['time_et']) for x in rows if x['report'] in SIX)))
    for x in rows:
        if x['report'] in SIX and x['time_et'] != '12:00':
            print("  ODD:", x['date'], repr(x['time_et']), x['report'], '|', x['evidence'][:80])
    months = sorted(set(x['date'][:7] for x in rows if x['report'] in SIX))
    print("  six-report months:", len(months), months[0], "..", months[-1])
