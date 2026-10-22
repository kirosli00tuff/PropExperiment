"""Summarise CFTC disaggregated futures-only COT shares of open interest for COMEX metals.
Shares = (long+short [+2*spread]) / (2*OI) per category, weekly, then mean/min/max over a window."""
import csv, sys, statistics as st
from pathlib import Path
W = Path(__file__).resolve().parent / "cot"
MK = {"HG": "COPPER- #1 - COMMODITY EXCHANGE INC.", "GC": "GOLD - COMMODITY EXCHANGE INC.",
      "MGC": "MICRO GOLD - COMMODITY EXCHANGE INC.", "SI": "SILVER - COMMODITY EXCHANGE INC.",
      "MHG": "MICRO COPPER - COMMODITY EXCHANGE INC.", "SIL": "MICRO SILVER - COMMODITY EXCHANGE INC."}
WINDOWS = {"2022-11..2023-10": ("2022-11-01", "2023-10-31", ["2022", "2023"]),
           "latest52w": (None, None, ["2025", "2026"])}
def rows(years):
    for y in years:
        with open(W / y / "f_year.txt", newline="") as f:
            for r in csv.DictReader(f):
                yield r
def num(r, k): return float(r[k].strip() or 0)
def share(r):
    oi = num(r, "Open_Interest_All")
    pm = num(r, "Prod_Merc_Positions_Long_All") + num(r, "Prod_Merc_Positions_Short_All")
    sw = num(r, "Swap_Positions_Long_All") + num(r, "Swap__Positions_Short_All") + 2 * num(r, "Swap__Positions_Spread_All")
    mm = num(r, "M_Money_Positions_Long_All") + num(r, "M_Money_Positions_Short_All") + 2 * num(r, "M_Money_Positions_Spread_All")
    ot = num(r, "Other_Rept_Positions_Long_All") + num(r, "Other_Rept_Positions_Short_All") + 2 * num(r, "Other_Rept_Positions_Spread_All")
    nr = num(r, "NonRept_Positions_Long_All") + num(r, "NonRept_Positions_Short_All")
    d = 2 * oi
    return oi, {"prod_merc": pm / d, "swap": sw / d, "m_money": mm / d, "other_rept": ot / d, "nonrept": nr / d}
for wname, (lo, hi, yrs) in WINDOWS.items():
    data = list(rows(yrs))
    for code, name in MK.items():
        sel = sorted([r for r in data if r["Market_and_Exchange_Names"].strip() == name],
                     key=lambda r: r["Report_Date_as_YYYY-MM-DD"])
        if wname == "latest52w":
            sel = sel[-52:]
        else:
            sel = [r for r in sel if lo <= r["Report_Date_as_YYYY-MM-DD"] <= hi]
        if not sel:
            print(wname, code, "no rows"); continue
        ois, shs = zip(*[share(r) for r in sel])
        out = f"{wname} {code} n={len(sel)} {sel[0]['Report_Date_as_YYYY-MM-DD']}..{sel[-1]['Report_Date_as_YYYY-MM-DD']} OI_mean={st.mean(ois):.0f} OI_median={st.median(ois):.0f}"
        for k in shs[0]:
            v = [s[k] for s in shs]
            out += f" {k}={100*st.mean(v):.1f}%[{100*min(v):.1f},{100*max(v):.1f}]"
        print(out)
