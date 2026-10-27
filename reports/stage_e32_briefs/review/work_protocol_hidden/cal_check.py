"""Parse E.31's two release calendars as P3.6 rule 3 would; report ambiguities (no market data)."""
import csv, collections, io, sys
R = "reports/stage_e31_briefs/research/"
def load(name):
    txt = open(R + name).read().splitlines()
    txt = [l for l in txt if not l.startswith("#")]
    return list(csv.DictReader(io.StringIO("\n".join(txt))))
main, ext = load("usda_releases.csv"), load("usda_releases_ext.csv")
print("main rows", len(main), "ext rows", len(ext), "ext cols", list(ext[0].keys()))
c = collections.Counter((r["report"], r["time_et"]) for r in ext)
for k, v in sorted(c.items()): print(" ext", v, k)
nor = [r for r in ext + main if r["date"].endswith("NORELEASE")]
print("NORELEASE rows", len(nor), collections.Counter((r["report"], r["time_et"]) for r in nor))
six = ("USDA WASDE", "NASS Crop Production", "NASS Crop Production Annual", "NASS Grain Stocks",
       "NASS Prospective Plantings", "NASS Acreage", "NOPA Monthly Crush (not USDA)")
allrows = main + ext
blank = [(r["date"], r["report"], r["time_et"], r["evidence"]) for r in allrows if r["report"] in six and r["time_et"] != "12:00"]
print("six-report rows whose time is not 12:00:", len(blank)); [print("  ", b) for b in blank]
nopa_months = collections.defaultdict(list)
for r in allrows:
    if r["report"].startswith("NOPA") and not r["date"].endswith("NORELEASE"):
        nopa_months[r["date"][:7]].append((r["date"], r["time_et"]))
months = [f"{y}-{m:02d}" for y in range(2020, 2025) for m in range(1, 13)]
months = [m for m in months if "2020-12" <= m <= "2024-02"]
missing = [m for m in months if m not in nopa_months]
print("months 2020-12..2024-02:", len(months), "with a NOPA row:", len(nopa_months), "without:", len(missing))
print("months without NOPA row:", missing)
multi = {m: v for m, v in nopa_months.items() if len(v) > 1}
print("months with >1 NOPA row:", multi)
grades = collections.Counter(r["evidence"] for r in allrows if r["report"] in six)
print("evidence grades among six-report rows:", dict(grades))
dup = collections.Counter((r["date"], r["report"]) for r in allrows if r["report"] in six)
print("duplicate (date, report) rows:", [k for k, v in dup.items() if v > 1][:5])
