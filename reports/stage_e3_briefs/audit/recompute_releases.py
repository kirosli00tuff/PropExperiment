"""Auditor recompute of TREASURY_AUCTIONS, FOMC_STATEMENT_DATES, ISM_SERVICES_DATES (counts/diffs only)."""
import sys; sys.path.insert(0, ".")
import csv, hashlib, json
from collections import Counter
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo
from strategy.members.k2._releases import TREASURY_AUCTIONS, FOMC_STATEMENT_DATES, ISM_SERVICES_DATES, DROPPED_AUCTIONS, RELEASE_CALENDAR_SHA256
CT, ET = ZoneInfo("America/Chicago"), ZoneInfo("America/New_York")
raw = open("reports/stage_e2b_release_calendar.json", "rb").read()
assert hashlib.sha256(raw).hexdigest() == RELEASE_CALENDAR_SHA256
rows = json.loads(raw)["releases"]
def loc(r, tz): return datetime.fromisoformat(r["instant_utc"].replace("Z", "+00:00")).astimezone(tz)
auc = set(); tenor_ct = Counter(); prod_ok = True
for r in rows:
    if r["release"] != "TREASURY_AUCTION": continue
    tenor = r["id"].rsplit("-", 1)[1]
    if tenor not in ("2Y", "5Y", "10Y", "30Y"): continue
    lt = loc(r, CT); et = loc(r, ET)
    assert r["tz"] == "America/New_York" and et.strftime("%H:%M") == r["time_local"], r["id"]
    assert (et.hour - lt.hour) == 1 and et.date() == lt.date() == date.fromisoformat(r["date"]), r["id"]
    auc.add((r["date"], tenor, lt.strftime("%H:%M"))); tenor_ct[tenor] += 1
    prod_ok &= set(r["products"]) >= {"ZT","ZF","ZN","TN","ZB","UB"}
print("auctions recomputed", len(auc), dict(tenor_ct), "products cover all six", prod_ok)
mine = auc - {(d, t, "DROP") for d, t, _ in DROPPED_AUCTIONS}
theirs = set(TREASURY_AUCTIONS)
print("auction set equal", mine == theirs, "only mine", sorted(mine - theirs)[:5], "only table", sorted(theirs - mine)[:5])
print("T_a values", Counter(t for _, _, t in TREASURY_AUCTIONS))
dates = [date.fromisoformat(d) for d, _, _ in TREASURY_AUCTIONS]
print("auction date range", min(dates), max(dates), "dup (date,tenor)", len(TREASURY_AUCTIONS) - len({(d, t) for d, t, _ in TREASURY_AUCTIONS}))
fomc_all = [r for r in rows if r["release"] == "FOMC"]
fomc = sorted(r["date"] for r in fomc_all if loc(r, CT).strftime("%H:%M") == "13:00")
print("FOMC rows", len(fomc_all), "at 13:00 CT", len(fomc), "equal", tuple(fomc) == tuple(FOMC_STATEMENT_DATES), "other times", Counter(loc(r, CT).strftime("%H:%M") for r in fomc_all))
print("FOMC range", fomc[0], fomc[-1], "products has all six", all(set(r["products"]) >= {"ZT","ZF","ZN","TN","ZB","UB"} for r in fomc_all))
ism_all = [r for r in rows if r["release"] == "ISM_SERVICES"]
ism = sorted(r["date"] for r in ism_all if loc(r, ET).strftime("%H:%M") == "10:00")
print("ISM rows", len(ism_all), "at 10:00 ET", len(ism), "equal", tuple(ism) == tuple(ISM_SERVICES_DATES), "products", Counter(tuple(sorted(r["products"])) for r in ism_all).most_common(2))
print("ISM range", ism[0], ism[-1])
# windows
def inwin(d, a, b): return a <= d <= b
R = (date(2025,4,1), date(2026,6,19)); C = (date(2019,5,6), date(2024,2,29))
for name, w in (("research", R), ("confirmation", C)):
    c = Counter(t for d, t, _ in TREASURY_AUCTIONS if inwin(date.fromisoformat(d), *w))
    c2y1030 = sum(1 for d, t, ta in TREASURY_AUCTIONS if t == "2Y" and ta == "10:30" and inwin(date.fromisoformat(d), *w))
    print(name, "auctions", dict(c), "2Y@10:30", c2y1030, "FOMC", sum(1 for d in FOMC_STATEMENT_DATES if inwin(date.fromisoformat(d), *w)), "ISM", sum(1 for d in ISM_SERVICES_DATES if inwin(date.fromisoformat(d), *w)))
# availability from the saved FiscalData CSV (announcement fields only)
p = "data/vendor/release_pages/treasury/auctions_query_notes_bonds_20190501_20260621.csv"
with open(p, newline="") as f: recs = list(csv.DictReader(f))
print("csv rows", len(recs), "fields", [k for k in recs[0].keys() if k in ("auction_date","security_type","security_term","original_security_term","floating_rate","inflation_index_security","announcemt_date","closing_time_comp","reopening")])
TM = {"2-Year": "2Y", "5-Year": "5Y", "10-Year": "10Y", "30-Year": "30Y"}
keep = {}; sameday = 0; lag = []
for r in recs:
    if r["security_type"] not in ("Note", "Bond") or r["floating_rate"] != "No" or r["inflation_index_security"] != "No": continue
    if r["original_security_term"] not in TM: continue
    ad, an = date.fromisoformat(r["auction_date"]), date.fromisoformat(r["announcemt_date"])
    if not inwin(ad, date(2019,5,6), date(2026,6,19)): continue
    if not an < ad: sameday += 1; continue
    lag.append((ad - an).days)
    hh, mm = r["closing_time_comp"].split(":")[:2]
    ta = f"{int(hh)-1:02d}:{mm}"
    keep[(r["auction_date"], TM[r["original_security_term"]])] = ta
print("csv retained", len(keep), "same-day excluded", sameday, "min lag days", min(lag))
csvset = {(d, t, ta) for (d, t), ta in keep.items()}
print("csv set == table", csvset == theirs, "only csv", sorted(csvset - theirs)[:5], "only table", sorted(theirs - csvset)[:5])
rk = [(r["auction_date"], r["security_term"], r["original_security_term"], r["reopening"]) for r in recs if r["auction_date"] in ("2019-11-05", "2026-01-26") and r["original_security_term"] in TM]
print("re-keyed", rk)
