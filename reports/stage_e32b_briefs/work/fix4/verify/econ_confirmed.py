"""FixVerifier (F4): RV1 S3 and N2. Scan econ32b.json for every search record with confirmed != true (all blocks,
nested E_dir.<h> included), print the recorded values, the E and rank of the affected pairs in score32b_out.json, and
compare with the 8 input_checks entries. Also sha256 of econ32b.json and the ranking file's hash statements."""
import hashlib
import json
import re
from pathlib import Path

B = Path(__file__).resolve().parents[3]
econ_p = B / "econ32b.json"
print("econ32b.json sha256:", hashlib.sha256(econ_p.read_bytes()).hexdigest())
econ = json.loads(econ_p.read_text())
unc = []
n_search = 0
for key, blocks in sorted(econ["pairs"].items()):
    for name, blk in blocks.items():
        if name == "inputs" or not isinstance(blk, dict):
            continue
        subs = [(name, blk)] if "search" in blk else [(f"{name}.{h}", s) for h, s in blk.items()
                                                      if isinstance(s, dict) and "search" in s]
        for nm, b in subs:
            for sname, rec in (b.get("search") or {}).items():
                n_search += 1
                if rec.get("confirmed") is not True:
                    unc.append((key, nm, sname, rec.get("confirmed"), b.get(sname), rec.get("k_bisection"),
                                len(rec.get("violations") or []), rec.get("n_checked"),
                                (rec.get("violations") or [None])[0]))
print("search records:", n_search, "; unconfirmed:", len(unc))
for u in unc:
    print("  ", u)
edir_unc = [u for u in unc if u[1].startswith("E_dir")]
print("unconfirmed in E_dir blocks:", len(edir_unc))
# values and E for bulenox CL / NG
out = json.loads((B / "score32b_out.json").read_text())
pairs = out["primary"]["pairs"] if "pairs" in out["primary"] else out["primary"]["ranked"]
for k in ("bulenox|CL", "bulenox|NG"):
    for bn in ("primary", "spread1"):
        b = econ["pairs"][k][bn]
        print(k, bn, "mu*_mkt", b["mu_star_mkt"], "mu10K_mkt", b["mu10K_mkt"], "c_mkt", b.get("c_mkt_ticks"))
    row = next(r for r in pairs if f"{r['firm']}|{r['code']}" == k)
    print("   score row: E", row.get("E"), "rank", row.get("rank"), "S", row.get("S"), "block", row.get("econ_block"))
ic = [c for c in out["input_checks"] if "confirmed" in c]
print("input_checks mentioning confirmed:", len(ic), "of", len(out["input_checks"]))
for c in ic:
    print("  ", c[:170])
# E.28 regression values
reg = B / "work/econ/REGRESSION.md"
if reg.exists():
    for l in reg.read_text().splitlines():
        if "bulenox|CL" in l or "bulenox|NG" in l:
            print("REGRESSION.md:", l[:200])
# hashes named in the ranking file
rk = (B.parent / "stage_e32b_ranking.md").read_text()
for h in ("e5673466", "0567890e", "05678907", "ee74c6a0", "70809d50"):
    print(f"ranking.md mentions {h}: {rk.count(h)}")
print("score32b_out.json inputs econ:", out["inputs"].get("econ32b.json") or [v for k, v in out["inputs"].items() if "econ" in k])
