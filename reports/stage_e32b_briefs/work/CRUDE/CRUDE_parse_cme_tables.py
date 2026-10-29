"""CRUDE_parse_cme_tables.py: print WTI column of Tables 3 and 4 of the saved CME Q1-2023 Asia-hours whitepaper text."""
import re, sys
lines = open(sys.argv[1]).read().splitlines()
def table(start_pat, stop_pat):
    i = next(k for k, l in enumerate(lines) if start_pat in l)
    toks = []
    for l in lines[i + 1:]:
        if stop_pat and stop_pat in l:
            break
        toks.append(l.strip())
    rows, cur = {}, None
    for t in toks:
        if re.fullmatch(r"\d{1,2}:00", t):
            cur = t; rows[cur] = []
        elif cur and re.fullmatch(r"-?\d+(\.\d+)?", t):
            rows[cur].append(float(t))
        elif cur and t and not re.fullmatch(r"-?\d+(\.\d+)?", t) and len(rows) >= 24:
            break
    return rows
for name, a, b in [("spread_ticks", "Table 3. Average of best bid/ask spread", "Table 4"), ("touch_lots", "Table 4. Average of best bid/ask quantity", None)]:
    r = table(a, b)
    print(name, len(r), "hours:", " ".join(f"{h}={v[0]}" for h, v in r.items() if v))
