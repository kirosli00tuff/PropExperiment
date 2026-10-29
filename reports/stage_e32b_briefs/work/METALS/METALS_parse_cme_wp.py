"""Parse Tables 3 and 4 of the CME Asia-hours whitepaper (saved text) for Gold and Copper columns.
Columns: WTI, Natural Gas, Gold, Copper, Corn, Soybean. Corn/Soybean closed some hours (fewer values),
so only rows with >= 4 values are used and Gold, Copper are columns 3 and 4."""
import re, statistics, sys
t = open(sys.argv[1]).read().splitlines()
def table(start_pat, end_pat):
    s = next(i for i, l in enumerate(t) if start_pat in l)
    e = next(i for i in range(s + 1, len(t)) if end_pat in t[i])
    toks = [x.strip() for x in t[s + 1:e] if x.strip()]
    rows, cur = {}, None
    for x in toks:
        if re.fullmatch(r"\d{1,2}:00", x):
            cur = int(x.split(":")[0]); rows[cur] = []
        elif cur is not None and re.fullmatch(r"[\d,]+(\.\d+)?", x):
            rows[cur].append(float(x.replace(",", "")))
    return rows
for name, sp, ep in (("spread_ticks", "Table 3. Average of best bid/ask spread", "The average bid/ask order quantity"),
                     ("quantity_lots", "Table 4. Average of best bid/ask quantity", "CME Group flagship commodity")):
    rows = table(sp, ep)
    print(name, "hours parsed", len(rows), "row lengths", sorted({len(v) for v in rows.values()}))
    for col, idx in (("Gold", 2), ("Copper", 3)):
        vals = {h: v[idx] for h, v in rows.items() if len(v) >= 4}
        us = [vals[h] for h in (21, 22, 23, 0, 1) if h in vals]  # SGT 21:00-02:00 = ET 08:00-13:00 (winter)
        print(f"  {col}: all-hours mean {statistics.mean(vals.values()):.2f} median {statistics.median(vals.values()):.2f} "
              f"min {min(vals.values()):.2f} max {max(vals.values()):.2f}; SGT21-01 (ET 08-13) values {us} median {statistics.median(us):.2f}")
