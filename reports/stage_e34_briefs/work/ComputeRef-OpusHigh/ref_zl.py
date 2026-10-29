"""E.34 ComputeRef: P10 compute-stop reference R_ZL as a guess range (arithmetic only, no data read).

Anchors are E.33's wall times from reports/stage_e33c_briefs/ref_v03.json (times only) and
reports/E.33c_RETURN.md 3.3. Usage: nice -n 10 python3 -I ref_zl.py <repo> <out.json>
"""
import itertools
import json
import os
import sys
from pathlib import Path

os.nice(10)

# ---- E.33 anchors (ref_v03.json keys) ----
N1, N5 = 23, 59                      # S1 and S5 feature counts (project_ref_v03.py N_FEATURES)
P_B, P_L, P_G = 4, 8, 2             # E.33 process counts (project_ref_v03.py; protocol 0.3 P5)

# ---- ZL grid (brief) ----
LABELS = 5
GRID = {"LOGIT": 6, "LGBM": 4}
FOLDS = 6

# ---- labelled assumptions: low / central / high ----
PHI = {"low": 0.83, "central": 0.98, "high": 1.08}     # A3 label mix (drop FH05)
KAPPA = {"low": 0.6, "central": 1.0, "high": 2.0}      # A4 data regime ZL vs ZM
ETA = {"low": 1.00, "central": 1.06, "high": 1.15}     # A5 parallel efficiency + reruns
BUILD = {"low": 460.0, "central": 1200.0, "high": 3580.0}  # A6 feature build wall, s
# A2 feature counts: C, F09 crush, F09 prop, F10 book
COUNTS = {"low": (13, 8, 9, 12), "central": (14, 8, 9, 12), "high": (15, 10, 10, 12)}


def anchors(ref: dict) -> dict:
    psm = ref["per_set_model"]
    out = {}
    for m in ("LOGIT", "LGBM"):
        s5 = psm[f"S5 {m}"]
        t5 = s5["measured_s"] / s5["measured_folds"]
        rho = ref["rho"][m]
        a = (N5 * rho - N1) / (1.0 - rho)    # affine t ~ (a + n) through (23, rho t5) and (59, t5)
        out[m] = {"t5_mean_s": t5, "rho": rho, "a_affine": a, "t1_mean_s": rho * t5}
    return out


def t_fold(anc: dict, n: int, form: str) -> float:
    t5, rho, a = anc["t5_mean_s"], anc["rho"], anc["a_affine"]
    if form == "affine":
        return t5 * (a + n) / (a + N5)
    if form == "lin_S5":
        return t5 * n / N5
    if form == "lin_S1":                      # E.33c's projection rule (t_S5 x rho x n / 23)
        return t5 * rho * n / N1
    raise ValueError(form)


def sets(counts: tuple) -> dict:
    c, fc, fp, fb = counts
    return {"S_crush": c + fc, "S_prop": c + fp, "S_book": c + fb, "S_pool": c + fc + fp + fb}


def fit_sum(anc: dict, ns: dict, pick: str) -> dict:
    """Sum of fold seconds per family over 4 sets; pick = affine | min | max over model forms."""
    res = {}
    for m in ("LOGIT", "LGBM"):
        nf = GRID[m] * LABELS * FOLDS
        tot = 0.0
        for n in ns.values():
            vals = [t_fold(anc[m], n, f) for f in ("affine", "lin_S5", "lin_S1")]
            t = {"affine": vals[0], "min": min(vals), "max": max(vals)}[pick]
            tot += nf * t
        res[m] = tot
    return res


def r_zl(anc, counts, phi, kappa, eta, build, pick, p_l=P_L, p_g=P_G):
    s = fit_sum(anc, sets(counts), pick)
    logit = eta * kappa * phi * s["LOGIT"] / p_l
    lgbm = eta * kappa * phi * s["LGBM"] / p_g
    return {"build_s": build, "logit_wall_s": logit, "lgbm_wall_s": lgbm, "R_s": build + logit + lgbm,
            "fold_cpu_s": {k: kappa * phi * v for k, v in s.items()}}


def main(repo: Path, out: Path) -> None:
    ref = json.loads((repo / "reports/stage_e33c_briefs/ref_v03.json").read_text())
    anc = anchors(ref)
    pick = {"low": "min", "central": "affine", "high": "max"}
    scen = {}
    for k in ("low", "central", "high"):
        r = r_zl(anc, COUNTS[k], PHI[k], KAPPA[k], ETA[k], BUILD[k], pick[k])
        r["stop_3x_s"] = 3 * r["R_s"]
        r["R_h"], r["stop_3x_h"] = r["R_s"] / 3600, r["stop_3x_s"] / 3600
        r["sets"] = sets(COUNTS[k])
        scen[k] = r
    # one-at-a-time sensitivity around central
    base = dict(counts=COUNTS["central"], phi=PHI["central"], kappa=KAPPA["central"], eta=ETA["central"],
                build=BUILD["central"], pick="affine")
    sens = {}
    for name, grid in (("counts", COUNTS), ("phi", PHI), ("kappa", KAPPA), ("eta", ETA), ("build", BUILD),
                       ("pick", {"low": "min", "high": "max"})):
        for lvl in ("low", "high"):
            kw = dict(base)
            kw[name] = grid[lvl]
            sens[f"{name}_{lvl}"] = round(r_zl(anc, **kw)["R_s"], 1)
    # overnight-profile variant: 14 single-thread LOGIT processes (LGBM 2 x 7 threads, assume no LGBM gain)
    night = {k: round(r_zl(anc, COUNTS[k], PHI[k], KAPPA[k], ETA[k], BUILD[k], pick[k], p_l=14)["R_s"], 1)
             for k in ("low", "central", "high")}
    # reduced-process variant if memory forces P_L = 5 (high memory case)
    pl5 = {k: round(r_zl(anc, COUNTS[k], PHI[k], KAPPA[k], ETA[k], BUILD[k], pick[k], p_l=5)["R_s"], 1)
           for k in ("low", "central", "high")}
    # linear coefficients (affine form, central phi/kappa/eta): R = B + K0 + K1 * sum_s n_s
    coef = {}
    for m, p in (("LOGIT", P_L), ("LGBM", P_G)):
        nf = GRID[m] * LABELS * FOLDS
        g = ETA["central"] * KAPPA["central"] * PHI["central"] * nf * anc[m]["t5_mean_s"] / (anc[m]["a_affine"] + N5) / p
        coef[m] = {"per_feature_in_sum_s": g, "intercept_s": 4 * anc[m]["a_affine"] * g}
    # per-fold central times by set
    per_fold = {s: {m: round(t_fold(anc[m], n, "affine"), 2) for m in anc} for s, n in sets(COUNTS["central"]).items()}
    # E.33 check: fits efficiency eta measured
    meas_fits = ref["measured_at_0.2_stop_s"]["fits_net_s"] + 7272.6        # E.33c_RETURN 3.3
    proj_fits = ref["R_0.3_s"] - ref["B_s"]
    e33 = {"fits_measured_s": meas_fits, "fits_projected_s": round(proj_fits, 1),
           "eta_measured": round(meas_fits / proj_fits, 4),
           "build_measured_over_B": round(ref["measured_at_0.2_stop_s"]["build_s"] / ref["B_s"], 4),
           "R_0.3_s": ref["R_0.3_s"], "measured_total_s": 14047.4}
    # affine model replayed on E.33 (sanity: should reproduce E.33's sum_fold_s within the label-cell caveat)
    e33_replay = {}
    for m in ("LOGIT", "LGBM"):
        nf = {"LOGIT": 216, "LGBM": 144}[m]
        e33_replay[m] = {f: round(sum(nf * t_fold(anc[m], n, f) for n in (23, 26, 27, 28, 59)), 1)
                         for f in ("affine", "lin_S1")}
        e33_replay[m]["ref_v03_sum_fold_s"] = ref["sum_fold_s"][m]
    res = {"anchors": anc, "scenarios": scen, "sensitivity_R_s": sens, "overnight_PL14_R_s": night,
           "PL5_R_s": pl5, "linear_coef": coef, "per_fold_central_s": per_fold, "e33_check": e33,
           "e33_replay_sum_fold_s": e33_replay,
           "assumptions": {"PHI": PHI, "KAPPA": KAPPA, "ETA": ETA, "BUILD": BUILD, "COUNTS": COUNTS}}
    out.write_text(json.dumps(res, indent=1, default=float) + "\n")
    for k, r in scen.items():
        print(k, r["sets"], "R", round(r["R_s"]), "s", round(r["R_h"], 2), "h; 3x", round(r["stop_3x_s"]),
              "s", round(r["stop_3x_h"], 2), "h; parts", round(r["build_s"]), round(r["logit_wall_s"]),
              round(r["lgbm_wall_s"]))
    print("sens", sens)
    print("night", night, "pl5", pl5)
    print("coef", {m: {k: round(v, 3) for k, v in c.items()} for m, c in coef.items()})
    print("per_fold", per_fold)
    print("e33", e33)
    print("replay", e33_replay)
    print("anchors", {m: {k: round(v, 4) for k, v in a.items()} for m, a in anc.items()})


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
