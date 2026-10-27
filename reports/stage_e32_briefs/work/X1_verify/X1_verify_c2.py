"""Compare X1 Table C2 rows (X1_exposure.md lines 245-279) with stats31.md lines 1398-1434 cell by cell.
Prints only mismatching cells and counts."""
x1 = open("reports/stage_e32_briefs/X1_exposure.md").read().splitlines()[244:279]
st = [l for l in open("reports/stage_e31_briefs/work/pilot/runs/stats31.md").read().splitlines()[1396:1434] if l.startswith("|") and not l.startswith("|---") and not l.startswith("| family")]
cells = lambda l: [c.strip() for c in l.strip().strip("|").split("|")]
print("x1 rows", len(x1), "stats rows", len(st))
mism = 0; rows_ok = 0
for a, b in zip(x1, st):
    ca, cb = cells(a), cells(b)
    bad = [(i, ca[i], cb[i]) for i in range(min(len(ca), len(cb))) if ca[i] != cb[i]]
    if len(ca) != len(cb): bad.append(("ncols", len(ca), len(cb)))
    if bad:
        mism += 1; print("ROW", ca[0], ca[1], bad[:4])
    else:
        rows_ok += 1
print("rows identical", rows_ok, "rows differing", mism)
