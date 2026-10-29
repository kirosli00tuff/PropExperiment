"""FixVerifier (F4) items 4-6 arithmetic: EQ3 K_eff and q, member thresholds, YM/MNQ/RTY/ZL e80, the two-member pool,
the priors' products, the S5 range over the 15 pairs, base rates from R1_closed_lines.json, ETH/MBT notional."""
import json
import math
from pathlib import Path

B = Path(__file__).resolve().parents[3]
f5 = json.loads((B / "F5_holding.json").read_text())
sr = json.loads((B / "work/F5/SR80.json").read_text())
print("SR80.json keys:", list(sr.keys()))
print("SR80 block:", json.dumps(sr.get("SR80"))[:500])
SR80 = sr["SR80"]["test"] if isinstance(sr.get("SR80"), dict) else sr["SR80_test"]
print("SR80_test", SR80)
rows = {k: v["rows"]["30"] for k, v in f5["pairs"].items()}
sig = {k.split("|")[1]: rows[k]["sigma"] for k in rows if k.startswith("topstep|")}
print("topstep sigma_30:", {k: round(v, 4) for k, v in sig.items()})
K_eff3 = 3 * 870 / (1 + 2 * 0.5)
q3 = SR80 * math.sqrt(870 / K_eff3)
print(f"K_eff(3, rho .5) = {K_eff3:.1f} ; q = {q3:.5f}")
for code in ("YM", "MNQ", "RTY"):
    print(f"  {code}: pooled e80 = q x sigma_30 = {q3 * sig[code]:.3f} ticks ; single e80 = {SR80 * sig[code]:.3f} ; "
          f"F5 e80_test {rows['topstep|' + code]['e80_test']:.3f}")
K_eff2 = 2 * 870 / (1 + 0.5)
q2 = SR80 * math.sqrt(870 / K_eff2)
print(f"K_eff(2, rho .5) = {K_eff2:.1f} ; q = {q2:.5f} ; Q5 band: {'<=0.20 -> 2' if q2 <= 0.20 else 'other'}")
# 273-date pool: K = 2 x 273 = 546 -> K_eff 364
print(f"two members on 273 dates: K_total 546, K_eff {546 / 1.5:.0f}")
# RTY figures
r = rows["topstep|RTY"]
print(f"RTY: sigma_30 {r['sigma']:.2f}, c_f/sigma {r['g_be'] / r['sigma']:.4f}, n_cap {r['n_cap']}, e80_test {r['e80_test']:.2f}, "
      f"gross_detect_test {r['gross_detect_test']:.2f}")
z = rows["topstep|ZL"]
print(f"ZL: sigma_30 {z['sigma']:.2f}, c_f {z['g_be']:.2f}, c_f/sigma {z['g_be'] / z['sigma']:.4f}, n_cap {z['n_cap']}, "
      f"e80_test {z['e80_test']:.2f}, gross {z['gross_detect_test']:.2f} = {z['gross_detect_test'] / z['sigma']:.3f} sigma")
y = rows["topstep|YM"]
print(f"YM: c_f {y['g_be']:.3f}, sigma {y['sigma']:.4f}, e80 single {SR80 * y['sigma']:.3f}")
# S5 range: gross_detect_test at 30 over the 15 pairs
g30 = {k: v["gross_detect_test"] for k, v in rows.items()}
lo, hi = min(g30, key=g30.get), max(g30, key=g30.get)
print(f"S5: gross_detect_test at 30: min {g30[lo]:.3f} ({lo}) max {g30[hi]:.3f} ({hi})")
# band members: min over in_band rows
gb = [(k, h, rw["gross_detect_test"]) for k, v in f5["pairs"].items() for h, rw in v["rows"].items() if rw.get("in_band")]
print(f"band members: gross min {min(gb, key=lambda t: t[2])} max {max(gb, key=lambda t: t[2])}")
e80b = [(k, h, rw["e80_test"]) for k, v in f5["pairs"].items() for h, rw in v["rows"].items() if rw.get("in_band")]
print(f"band members: e80 min {min(e80b, key=lambda t: t[2])} max {max(e80b, key=lambda t: t[2])}")
# priors
print(f"priors: 0.04 x 0.49 = {0.04 * 0.49:.4f}; 0.05 x 0.49 = {0.05 * 0.49:.4f}; 1-(1-a)(1-b) = {1 - (1 - 0.0196) * (1 - 0.0245):.4f}")
print(f"Laplace: 1/25 = {1 / 25:.3f}; 1/19 = {1 / 19:.4f}")
# base rates from R1
r1 = json.loads((B / "R1_closed_lines.json").read_text())
lines = r1["lines"]
print("R1 lines:", len(lines), "; keys:", list(lines[0].keys())[:30])
for ln in lines:
    print("  ", ln.get("id"), "trials", ln.get("n_trials"), "| outcome:", str(ln.get("outcome") or ln.get("result") or ln.get("status"))[:60],
          "| registered:", ln.get("registered") if "registered" in ln else ln.get("registration"))
# crypto notional
f4 = json.loads((B / "F4_facts_unmasked.json").read_text())["codes"]
eth, mbt = f4["ETH"], f4["MBT"]
print(f"ETH ADV {eth['adv']['value']} x mult {eth['multiplier']} = {eth['adv']['value'] * eth['multiplier']:,.0f} ETH/day; "
      f"MBT ADV {mbt['adv']['value']} x {mbt['multiplier']} = {mbt['adv']['value'] * mbt['multiplier']:,.1f} BTC/day; ratio "
      f"{eth['adv']['value'] * eth['multiplier'] / (mbt['adv']['value'] * mbt['multiplier']):,.0f}")
