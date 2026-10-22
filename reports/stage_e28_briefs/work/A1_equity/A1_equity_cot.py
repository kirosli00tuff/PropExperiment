"""A1_equity: CFTC Traders in Financial Futures (futures only) shares for equity-index candidates.

Window 2022-11-01..2023-10-31 only; rows dated 2023-11-01 or later are dropped before any value is used.
Usage: python3 -I A1_equity_cot.py names   -> list market names matching equity patterns (window rows only)
       python3 -I A1_equity_cot.py stats   -> per-market mean shares of open interest over the window
"""
import csv
import re
import sys
from statistics import mean

BASE = '/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e28_briefs/pages/A1_equity'
FILES = [f'{BASE}/cot22/FinFutYY.txt', f'{BASE}/cot23/FinFutYY.txt']
LO, HI = '2022-11-01', '2023-10-31'
PAT = re.compile(r'NASDAQ|DJIA|DOW|RUSSELL', re.I)
GROUPS = ['Dealer', 'Asset_Mgr', 'Lev_Money', 'Other_Rept', 'NonRept']


def rows():
    for path in FILES:
        with open(path, newline='', encoding='utf-8', errors='replace') as fh:
            for r in csv.DictReader(fh):
                d = r.get('Report_Date_as_YYYY-MM-DD', '').strip()
                if not (LO <= d <= HI):
                    continue
                yield r


def num(r, k):
    v = r.get(k, '').strip()
    return float(v) if v not in ('', '.') else 0.0


def main(mode):
    if mode == 'names':
        seen = {}
        for r in rows():
            n = r['Market_and_Exchange_Names'].strip()
            if PAT.search(n):
                key = (n, r['CFTC_Contract_Market_Code'].strip())
                seen[key] = seen.get(key, 0) + 1
        for (n, c), k in sorted(seen.items()):
            print(f'{c}\t{k} reports\t{n}')
        return
    by = {}
    for r in rows():
        n = r['Market_and_Exchange_Names'].strip()
        if not PAT.search(n):
            continue
        oi = num(r, 'Open_Interest_All')
        if oi <= 0:
            continue
        rec = {'oi': oi}
        for g in GROUPS:
            lo = num(r, f'{g}_Positions_Long_All')
            sh = num(r, f'{g}_Positions_Short_All')
            sp = num(r, f'{g}_Positions_Spread_All') if g not in ('NonRept',) else 0.0
            # share of total reportable+nonreportable long-plus-short positions (each side sums to OI)
            rec[g] = (lo + sh + 2 * sp) / (2 * oi)
        rec['tr'] = num(r, 'Traders_Tot_All')
        by.setdefault((r['CFTC_Contract_Market_Code'].strip(), n), []).append((r['Report_Date_as_YYYY-MM-DD'], rec))
    print('code\tmarket\tn_reports\tfirst\tlast\tmean_OI\t' + '\t'.join(f'{g}_share' for g in GROUPS) + '\tmean_traders')
    for (c, n), lst in sorted(by.items()):
        lst.sort()
        recs = [x[1] for x in lst]
        vals = '\t'.join(f"{mean(x[g] for x in recs):.3f}" for g in GROUPS)
        print(f"{c}\t{n}\t{len(recs)}\t{lst[0][0]}\t{lst[-1][0]}\t{mean(x['oi'] for x in recs):.0f}\t{vals}\t"
              f"{mean(x['tr'] for x in recs):.0f}")


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'names')
