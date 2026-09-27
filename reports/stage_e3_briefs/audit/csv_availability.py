"""Auditor: EC-AUC availability guard and T_a from the saved FiscalData CSV vs _releases.py (counts only)."""
import sys; sys.path.insert(0, ".")
import csv
from datetime import date, datetime
from strategy.members.k2._releases import TREASURY_AUCTIONS
TM = {"2-Year": "2Y", "5-Year": "5Y", "10-Year": "10Y", "30-Year": "30Y"}
p = "data/vendor/release_pages/treasury/auctions_query_notes_bonds_20190501_20260621.csv"
recs = list(csv.DictReader(open(p, newline="")))
keep, sameday, lags, times = {}, [], [], set()
for r in recs:
    if r["security_type"] not in ("Note", "Bond") or r["floating_rate"] != "No" or r["inflation_index_security"] != "No": continue
    if r["original_security_term"] not in TM: continue
    ad, an = date.fromisoformat(r["auction_date"]), date.fromisoformat(r["announcemt_date"])
    if not date(2019, 5, 6) <= ad <= date(2019+7, 6, 19): continue
    if not an < ad: sameday.append((r["auction_date"], TM[r["original_security_term"]], r["closing_time_comp"])); continue
    lags.append((ad - an).days); times.add(r["closing_time_comp"])
    et = datetime.strptime(r["closing_time_comp"].strip(), "%I:%M %p")
    ta = f"{et.hour - 1:02d}:{et.minute:02d}"
    keep[(r["auction_date"], TM[r["original_security_term"]])] = ta
csvset = {(d, t, ta) for (d, t), ta in keep.items()}
print("retained", len(keep), "same-day excluded", sameday, "min lag", min(lags), "closing times seen", sorted(times))
print("csv set == TREASURY_AUCTIONS:", csvset == set(TREASURY_AUCTIONS), "diff", sorted(csvset ^ set(TREASURY_AUCTIONS))[:6])
