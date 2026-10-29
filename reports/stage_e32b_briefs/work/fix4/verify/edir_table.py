"""FixVerifier (F4) item 6: every cell of the scope file's section-4 E_dir table against econ32b.json, and the lead's
reading (m10K lowest at 30 and rising in 15/15; above cap at 120 for 4 and at 240 for 14; m* lower at 240 than at 30
in 8/15; 9 zero cells; no unconfirmed E_dir search)."""
import json
import math
import re
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

B = Path(__file__).resolve().parents[3]
econ = json.loads((B / "econ32b.json").read_text())["pairs"]
scope = (B.parent / "stage_e32b_holding_scope.md").read_text().splitlines()
start = next(i for i, l in enumerate(scope) if l.startswith("## 4. Economics by horizon"))
rows = [l for l in scope[start:start + 45] if re.match(r"^\| [a-z]+\|[A-Z0-9]+ \|", l)]
print("table rows:", len(rows))


def r2(x):
    return str(Decimal(str(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def r3(x):
    return str(Decimal(str(x)).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP))


def block(pair, h):
    p = econ[pair]
    return p["E_dir60"] if h == 60 else p["E_dir"][str(h)]


def above(b, key):
    """True when the search found no grid point: above_cap flag (either key spelling) or a null value."""
    ac = b.get("above_cap") or {}
    short = key.replace("_mkt", "")
    return bool(ac.get(key) or ac.get(short)) or b.get(key) is None


def cell_expected(b, with_cap):
    mu = "u (>cap)" if above(b, "mu_star_mkt") else r2(b["mu_star_mkt"])
    m10 = "u (>cap)" if above(b, "mu10K_mkt") else r2(b["mu10K_mkt"])
    ms = "u" if above(b, "mu_star_mkt") else r3(b["m_star"])
    mk = "u" if above(b, "mu10K_mkt") else r3(b["m10K"])
    parts = [mu, m10, ms, mk] + ([str(int(b["grid_cap"]))] if with_cap else [])
    return " / ".join(parts)


bad = 0
pairs_in_table = []
for l in rows:
    cells = [c.strip() for c in l.strip().strip("|").split("|")]
    # the pair cell itself contains a '|' so re-split carefully
    m = re.match(r"^\| ([a-z]+\|[A-Z0-9]+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \|$", l.strip())
    pair, tcol, e60, e30, e120, e240 = [g.strip() for g in m.groups()]
    pairs_in_table.append(pair)
    T = "/".join(str(block(pair, h)["T"]) for h in (30, 60, 120, 240))
    exp = {"T": T, "E_dir60": cell_expected(block(pair, 60), True), "E_dir30": cell_expected(block(pair, 30), False),
           "E_dir120": cell_expected(block(pair, 120), False), "E_dir240": cell_expected(block(pair, 240), False)}
    got = {"T": tcol, "E_dir60": e60, "E_dir30": e30, "E_dir120": e120, "E_dir240": e240}
    for k in exp:
        if exp[k] != got[k]:
            bad += 1
            print(f"MISMATCH {pair} {k}: table '{got[k]}' vs econ '{exp[k]}'")
print("cells checked:", len(rows) * 5, "; mismatches:", bad)
print("above_cap sample:", block("mffu|MYM", 60).get("above_cap"))

# the lead's reading
top15 = pairs_in_table
inf = math.inf
low30 = rising = cap120 = cap240 = lower240 = zeros = 0
for p in top15:
    vals = {}
    for h in (30, 60, 120, 240):
        b = block(p, h)
        vals[h] = inf if above(b, "mu10K_mkt") else b["m10K"]
        if b["mu_star_mkt"] == 0:
            zeros += 1
    if vals[30] == min(vals.values()) and all(vals[30] < vals[h] for h in (60, 120, 240)):
        low30 += 1
    if vals[30] <= vals[60] <= vals[120] <= vals[240]:
        rising += 1
    cap120 += vals[120] == inf
    cap240 += vals[240] == inf
    ms30, ms240 = block(p, 30)["m_star"], block(p, 240)["m_star"]
    lower240 += ms240 < ms30
print(f"m10K lowest at 30 (strict): {low30}/15 ; non-decreasing 30<=60<=120<=240: {rising}/15")
print(f"mu10K above cap at 120: {cap120} ; at 240: {cap240} ; which not at 240:",
      [p for p in top15 if not above(block(p, 240), "mu10K_mkt")])
print("above_cap record sample (mffu|MYM E_dir60):", block("mffu|MYM", 60).get("above_cap"), "mu10K_mkt =",
      block("mffu|MYM", 60).get("mu10K_mkt"))
print(f"m* lower at 240 than at 30: {lower240}/15 ; zero mu*_mkt cells: {zeros}")
zc = [(p, h) for p in top15 for h in (30, 60, 120, 240) if block(p, h)["mu_star_mkt"] == 0]
print("zero cells:", zc)
mym = [above(block("mffu|MYM", h), "mu10K_mkt") for h in (30, 60, 120, 240)]
print("mffu|MYM mu10K above cap by h 30/60/120/240:", mym)
unc = [(p, h, s) for p in top15 for h in (30, 60, 120, 240) for s, rec in block(p, h)["search"].items()
       if rec.get("confirmed") is not True]
print("unconfirmed E_dir searches among the 15:", unc)
# cap formula check: cap = max(4, ceil(0.30 sigma_60))
capbad = [(p, block(p, 60)["grid_cap"], max(4, math.ceil(0.30 * block(p, 60)["sigma60"]))) for p in top15
          if block(p, 60)["grid_cap"] != max(4, math.ceil(0.30 * block(p, 60)["sigma60"]))]
print("cap formula mismatches:", capbad)
