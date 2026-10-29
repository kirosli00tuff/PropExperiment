"""M2 F09-ZL worked arithmetic. No market data: inputs are the shared ZL facts (BRIEFS RULES) and
E.28/E.32 standard per-minute sigmas. Writes m2_examples.json beside this script's parent."""
import json, math
out = {}
B_L, B_M, B_S = 0.11, 0.22, 0.25          # c/bu of crush per one tick of ZL, ZM, ZS
CF = 2.38                                   # Topstep ZL round trip, ticks
SIG = {1: 5.52, 5: 12.05, 15: 20.37, 30: 28.10, 60: 38.21}   # ZL day-session sigma_h, ticks
out["zl_ticks_per_cent_crush"] = 1 / B_L
out["zl_ticks_per_zs_tick"] = B_S / B_L      # implied ZL move per ZS tick, meal fixed
out["zl_ticks_per_zm_tick"] = -B_M / B_L     # implied ZL move per ZM tick, beans fixed
# break-even share s_L* = CF * b_L / (D (1 - 2^-m)); m = inf means full reversion
be = {}
for D in (0.5, 1, 2, 3):
    for m in (1, 2, 3, "inf"):
        frac = 1.0 if m == "inf" else 1 - 2 ** (-m)
        be[f"D{D}_m{m}"] = round(CF * B_L / (D * frac), 4)
out["breakeven_sL"] = be
# gross at s_L = 1
out["gross_sL1_D1"] = {f"m{m}": round((1 / B_L) * (1 - 2 ** (-m)), 3) for m in (1, 2, 3)}
# time stop in half-lives for each hold h and a hypothetical HL
hl_tab = {}
for HL in (10, 20, 30, 60):
    for h in (15, 30, 60):
        m = h / HL
        hl_tab[f"HL{HL}_h{h}"] = {"m": round(m, 3), "frac": round(1 - 2 ** (-m), 4),
                                  "sL_star_D1": round(CF * B_L / (1 - 2 ** (-m)), 4)}
out["halflife_vs_hold"] = hl_tab
# OU half-life from AR(1) phi; and phi = 1 + beta'alpha example
out["hl_from_phi"] = {str(p): round(-math.log(2) / math.log(p), 3) for p in (0.90, 0.95, 0.97, 0.99)}
alpha = {"S": 0.02, "L": -0.05, "M": -0.06}   # hypothetical per minute, NOT estimates
# P = (S cents, nL, nM); beta'P = -S + 0.11 nL + 0.22 nM = C (crush, c/bu)
beta = {"S": -1.0, "L": B_L, "M": B_M}
ba = sum(beta[k] * alpha[k] for k in "SLM")
shares = {k: round(beta[k] * alpha[k] / ba, 4) for k in "SLM"}
out["vecm_hyp"] = {"beta_alpha": round(ba, 5), "phi": round(1 + ba, 5),
                   "HL_min": round(-math.log(2) / math.log(1 + ba), 3), "shares": shares,
                   "zl_ticks_per_cent_z": round(alpha["L"] / (-ba), 4)}
# iterate deterministic error correction from C0 = +1 c/bu
P = {"S": 0.0, "L": 0.0, "M": 0.0}; z = 1.0
for _ in range(20000):
    d = {k: alpha[k] * z for k in "SLM"}
    for k in "SLM":
        P[k] += d[k]
    z += sum(beta[k] * d[k] for k in "SLM")
out["vecm_hyp"]["iter_moves"] = {k: round(v, 4) for k, v in P.items()}
out["vecm_hyp"]["iter_final_z"] = z
# (b) worked: ZS +1 c/bu (4 ticks) in 15 min, ZM and ZL flat
gap = 1 / B_L
out["b_example"] = {"implied_zl_ticks": round(gap, 3), "gap_in_sigma15": round(gap / SIG[15], 4),
                    "f_needed_h30": round(CF / gap, 4)}
f = 0.5; net = f * gap - CF; sr = net / SIG[30]
out["b_example"]["f0.5_h30"] = {"gross": round(f * gap, 3), "net": round(net, 3),
                                "sharpe_trade": round(sr, 4), "trades_t3": round((3 / sr) ** 2)}
# 1-min leg scales in crush units and ZS 15-min move in implied ZL ticks
zs15 = 3.11 * math.sqrt(15)
out["zs_sigma15_ticks_rw"] = round(zs15, 3)
out["zs_sigma15_cents"] = round(zs15 * B_S, 3)
out["zs_1sigma15_implied_zl_ticks"] = round(zs15 * B_S / B_L, 3)
out["zs_1sigma15_implied_over_zl_sigma15"] = round(zs15 * B_S / B_L / SIG[15], 3)
# cost per sigma: ZM (E.28 mu*_mkt 1.59; sigma_30 by random-walk 3.15 sqrt 30) vs ZL
zm30 = 3.15 * math.sqrt(30)
out["cost_per_sigma"] = {"ZM": round(1.59 / zm30, 4), "ZM_sigma30_rw": round(zm30, 3),
                         "ZL": round(CF / SIG[30], 4)}
# bid-ask bounce in the implied-oil gap (half a tick per leg endpoint), ZL ticks
bs, bm, bl = 0.5 * B_S / B_L, 0.5 * B_M / B_L, 0.5
out["bounce_gap_sd_ticks"] = round(math.sqrt(bs**2 + bm**2 + bl**2), 3)
out["bounce_over_sigma5"] = round(math.sqrt(bs**2 + bm**2 + bl**2) / SIG[5], 4)
# spread sensitivity: S = 2.06 (GRAINS-35 snippet, unverified) instead of 1.0
cf2 = 2.06 + 0.5 + 0.88
out["cf_spread206"] = round(cf2, 2)
out["sL_star_D1_m1_spread206"] = round(cf2 * B_L / 0.5, 4)
json.dump(out, open(__file__.replace("scripts/m2_examples.py", "m2_examples.json"), "w"), indent=1)
print(json.dumps(out)[:3000])
