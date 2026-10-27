"""M2_lead_lag extra worked examples (re-spawned instance). No market data read.
Inputs: E.32 brief standard numbers, contract specs, labelled assumptions."""
import json, math, os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "M2_examples2.json")
r = {}
HURDLE = 1.59  # ticks, stage_e28_ranking.md line 130 (topstep ZM mu*_mkt)
s1m = {"ZM": 3.15, "ZS": 3.11, "ZL": 5.52}
s1s = {k: v / math.sqrt(60) for k, v in s1m.items()}  # random-walk scaling (assumption)
r["sigma_1s_ticks"] = {k: round(v, 4) for k, v in s1s.items()}
# (b) pure-shift lead-lag model: ZS leads ZM by theta seconds; predictable ZM move left after latency L
tab = []
for rho in (0.3, 0.6, 1.0):
    for th in (0.2, 0.5, 1.0, 2.0):
        for L in (0.3, 1.0):
            left = max(th - L, 0.0)
            sd = rho * s1s["ZM"] * math.sqrt(left)
            tab.append({"rho": rho, "theta_s": th, "L_s": L, "sd_pred_ticks": round(sd, 4),
                        "k_sigma_to_clear_hurdle": (round(HURDLE / sd, 2) if sd > 0 else None)})
r["b_shift_model"] = tab
r["b_zs_1s_move_needed_sigma"] = round(1.57 / s1s["ZS"], 3)
# (a) Epps attenuation of a 1-min regression hedge ratio (from M2_examples.json MC, rho_true 0.6)
r["a_epps_atten"] = {"1min": round(0.5457 / 0.6, 4), "5min": round(0.583 / 0.6, 4), "15s": round(0.4106 / 0.6, 4)}
# (e)/(f) VECM shares under physical and median vectors, same hypothetical alpha (per minute)
alpha = (-0.02, 0.05, 0.06)
for name, b in (("physical", (1.0, -0.11, -0.22)), ("median", (1.0, -0.11, -0.19))):
    ba = sum(x * y for x, y in zip(b, alpha))
    shares = [x * y / ba for x, y in zip(b, alpha)]
    r[f"e_{name}"] = {"beta": b, "alpha_hyp": alpha, "beta_alpha": round(ba, 6),
                      "hl_z_min": round(math.log(2) / -math.log(1 + ba), 3),
                      "shares": [round(s, 4) for s in shares],
                      "zm_ticks_alone_per_1c": round(1 / -b[2], 4),
                      "zm_ticks_total_per_1c": round(alpha[2] / -ba, 4)}
# deterministic check by iteration for the median vector
b = (1.0, -0.11, -0.19); P = [1.0, 0.0, 0.0]
for _ in range(5000):
    z = sum(x * y for x, y in zip(b, P)); P = [p + a * z for p, a in zip(P, alpha)]
r["e_median"]["sim_moves"] = [round(P[0] - 1.0, 4), round(P[1], 4), round(P[2], 4)]
# same 1 cent on the physical crush, read through the median vector (ZS-only shock)
# a ZS move of +1 cent changes both residuals by +1 cent; a ZM move of -x ticks changes physical by 0.22x and median by 0.19x
r["f_unit_note"] = {"zm_shock_1c_physical_ticks": round(1 / 0.22, 4),
                    "same_shock_median_residual_c": round(0.19 / 0.22, 4)}
# (f) break-even ZM adjustment share s* = hurdle*bM/(D*(1-2^-m)); and gross at s=1
be = {}
for bM in (0.22, 0.19):
    for D in (0.5, 1.0, 2.0, 3.0):
        for m in (1, 2, 3):
            frac = 1 - 2 ** (-m)
            be[f"bM{bM}_D{D}_m{m}"] = {"s_star": round(HURDLE * bM / (D * frac), 4),
                                       "gross_if_s1": round(D * frac / bM, 3)}
r["f_breakeven"] = be
# Hansen-type check: half-life CI at n=290 is asymmetric; repeat with n=60
for n, ph in ((60, 0.95 - (1 + 3 * 0.95) / 60), (290, 0.95 - (1 + 3 * 0.95) / 290)):
    se = math.sqrt((1 - ph ** 2) / n); lo, hi = ph - 1.96 * se, ph + 1.96 * se
    hl = lambda p: math.log(2) / -math.log(p)
    r[f"d_ci_n{n}"] = {"phi_hat": round(ph, 5), "se": round(se, 5), "lo": round(lo, 5), "hi": round(hi, 5),
                       "hl_lo": round(hl(lo), 3), "hl_hi": (round(hl(hi), 3) if hi < 1 else "inf")}
# bias-corrected phi (Kendall inversion): phi_c = (n*phi_hat + 1)/(n - 3)
for n in (60, 290):
    ph = r[f"d_ci_n{n}"]["phi_hat"]; pc = (n * ph + 1) / (n - 3)
    r[f"d_ci_n{n}"]["phi_kendall_corrected"] = round(pc, 5)
with open(OUT, "w") as fh:
    json.dump(r, fh, indent=1)
print("ok")
