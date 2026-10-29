"""Lead ruling LR-Q6p (session 3, 2026-10-29): Q6's daily payout-qualification threshold is the lowest over the payout
paths the firm offers on the modelled plan. Topstep offers the Consistency Path (3 traded days, best day <= 40%, no
per-day minimum) beside the Standard Path (5 winning days of $150+), so Topstep members get 0. Reads the DossierWriter's
unrated file, writes a patched copy; the original stays for the $150 sensitivity."""
import json
from pathlib import Path

B = Path(__file__).resolve().parents[2]
src, dst = B / "R2_combinations_unrated.json", B / "R2_combinations_unrated_q6p.json"
d = json.loads(src.read_text())
n = 0
for c in d["combinations"]:
    if c["venue"] != "topstep":
        continue
    for m in c["members"]:
        if m.get("payout_threshold_usd") != 0:
            m["payout_threshold_usd_standard_path"] = m.get("payout_threshold_usd")
            m["payout_threshold_usd"] = 0
            m["payout_threshold_note"] = "LR-Q6p: Topstep Consistency Path has no per-day minimum (Standard Path $150 beside)"
            n += 1
d["lead_patch"] = {"ruling": "LR-Q6p", "script": "work/R2/patch_q6p_lead.py", "members_patched": n}
dst.write_text(json.dumps(d, indent=1, ensure_ascii=False))
print("patched", n, "topstep members ->", dst.name)
