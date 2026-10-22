"""A1_grains: CFTC disaggregated COT (futures only) shares for grain markets.
Prints the market names that match grain keywords, then mean shares over two windows."""
import zipfile, csv, io, sys, statistics as st
P = '/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e28_briefs/pages/A1_grains/'
rows = []
for y in (2022, 2023, 2025, 2026):
    z = zipfile.ZipFile(P + f'cftc_fut_disagg_txt_{y}.zip')
    name = z.namelist()[0]
    r = csv.DictReader(io.TextIOWrapper(z.open(name), encoding='latin-1'))
    for d in r:
        rows.append(d)
keys = rows[0].keys()
def k(sub):
    return [c for c in keys if sub.lower() in c.lower()]
NAME = 'Market_and_Exchange_Names'; DATE = 'Report_Date_as_YYYY-MM-DD'; CODE = 'CFTC_Contract_Market_Code'
if sys.argv[1:] == ['names']:
    seen = {}
    for d in rows:
        n = d[NAME]
        if any(w in n.upper() for w in ('CORN', 'SOYBEAN', 'WHEAT')):
            seen.setdefault((d[CODE].strip(), n.strip()), 0); seen[(d[CODE].strip(), n.strip())] += 1
    for (c, n), v in sorted(seen.items()):
        print(c, '|', n, '|', v)
    sys.exit()
cols = dict(oi='Open_Interest_All', pm_l='Prod_Merc_Positions_Long_All', pm_s='Prod_Merc_Positions_Short_All',
            sd_l='Swap_Positions_Long_All', sd_s='Swap__Positions_Short_All', mm_l='M_Money_Positions_Long_All',
            mm_s='M_Money_Positions_Short_All', or_l='Other_Rept_Positions_Long_All', or_s='Other_Rept_Positions_Short_All',
            nr_l='NonRept_Positions_Long_All', nr_s='NonRept_Positions_Short_All', sd_sp='Swap__Positions_Spread_All', mm_sp='M_Money_Positions_Spread_All', or_sp='Other_Rept_Positions_Spread_All')
for c in cols.values():
    if c not in keys:
        print('MISSING COL', c, k(c.split('_')[0])); sys.exit(1)
codes = sys.argv[1].split(',')
windows = {'2022-11-01..2023-10-31': ('2022-11-01', '2023-10-31'), 'latest_52wk': None}
for code in codes:
    sel = [d for d in rows if d[CODE].strip() == code]
    dates = sorted({d[DATE] for d in sel})
    last = dates[-1]
    import datetime as dt
    l = dt.date.fromisoformat(last); start = (l - dt.timedelta(days=364)).isoformat()
    windows['latest_52wk'] = (start, last)
    for wn, (a, b) in windows.items():
        w = [d for d in sel if a <= d[DATE] <= b]
        if not w:
            print(code, wn, 'no rows'); continue
        f = lambda d, c: float(d[cols[c]])
        def share(c1, c2, sp=None):
            return st.mean((f(d, c1) + f(d, c2) + (2 * f(d, sp) if sp else 0)) / (2 * f(d, 'oi')) for d in w)
        print(f"{code} | {w[0][NAME].strip()} | {wn} actual {min(d[DATE] for d in w)}..{max(d[DATE] for d in w)} n={len(w)} | "
              f"meanOI={st.mean(f(d,'oi') for d in w):.0f} | ProdMerc={share('pm_l','pm_s'):.3f} Swap={share('sd_l','sd_s','sd_sp'):.3f} "
              f"MM={share('mm_l','mm_s','mm_sp'):.3f} OtherRept={share('or_l','or_s','or_sp'):.3f} NonRept={share('nr_l','nr_s'):.3f}")
