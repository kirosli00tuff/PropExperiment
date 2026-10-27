"""X1_verify ledger summary: prints counts by (dataset, schema, symbols, event) and requested
date ranges only. Never prints any other field value (no keys, no costs, no ids).
Also prints the sorted set of field NAMES (not values) seen at top level and in 'request',
and a broad match count (any symbol containing ZM/ZS/ZL anywhere) to check X1's filter."""
import json, collections, re
PATH = "ledger/databento_spend.jsonl"
STRICT = re.compile(r"^(ZM|ZS|ZL)([.\-_ ]|$)")
BROAD = re.compile(r"(ZM|ZS|ZL)")
top_names, req_names = set(), set()
grp = collections.defaultdict(lambda: [0, "9999", "0000"])
broad_only = collections.Counter()
commits = collections.defaultdict(list)
sealed_start, sealed_end = "2017-05-01", "2020-11-30"
in_window = collections.Counter()
nlines = 0
for line in open(PATH):
    nlines += 1
    d = json.loads(line)
    top_names.update(d.keys())
    r = d.get("request", {}) or {}
    req_names.update(r.keys())
    syms = r.get("symbols")
    syms = syms if isinstance(syms, list) else [syms]
    syms = [str(s) for s in syms]
    strict = any(STRICT.match(s) for s in syms)
    broad = any(BROAD.search(s) for s in syms)
    if broad and not strict:
        broad_only[(r.get("schema"), ",".join(sorted(set(syms)))[:60], d.get("event"))] += 1
    if not strict:
        continue
    s0, e0 = str(r.get("start"))[:10], str(r.get("end"))[:10]
    k = (r.get("dataset"), r.get("schema"), ",".join(sorted(set(syms)))[:60], d.get("event"))
    g = grp[k]; g[0] += 1; g[1] = min(g[1], s0); g[2] = max(g[2], e0)
    # any requested range that intersects the sealed window [2017-05-01, 2020-11-30] by date
    if s0 <= sealed_end and e0 >= sealed_start:
        in_window[k] += 1
    if d.get("event") == "commit":
        commits[(r.get("schema"), ",".join(sorted(set(syms)))[:60])].append((s0, e0))
print("lines", nlines)
print("top-level field names:", sorted(top_names))
print("request field names:", sorted(req_names))
for k in sorted(grp, key=str):
    v = grp[k]
    print(" | ".join(map(str, k)), "| n=%d | min_start=%s | max_end=%s" % tuple(v))
print("--- broad-only matches (symbol contains ZM/ZS/ZL but not as root prefix):", sum(broad_only.values()))
for k, n in sorted(broad_only.items(), key=str):
    print("  ", k, n)
print("--- lines whose requested range intersects 2017-05-01..2020-11-30 (by date), per group")
for k, n in sorted(in_window.items(), key=str):
    print("  ", " | ".join(map(str, k)), n)
print("--- merged committed ranges")
for k, rs in sorted(commits.items(), key=str):
    rs.sort(); m = []
    for a, b in rs:
        if m and a <= m[-1][1]:
            m[-1][1] = max(m[-1][1], b)
        else:
            m.append([a, b])
    print(k, len(rs), m)
