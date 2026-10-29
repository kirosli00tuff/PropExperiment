"""Protocol 0.3 compute reference for registration r009-E33 (V53): the method of the amended P5 bullet, in code.

Inputs, wall times only (no outcome, fit statistic or iteration count is read):
  - reports/stage_e33_briefs/work/logs/search_real.log: the 'fold k done <s> s' lines of the 0.2 run;
  - ledger/trial_registrations.jsonl: the 300 ids of r009-E33;
  - reports/stage_e33_briefs/work/logs/p5_builder_probe_e33b.log: the 3 builder probe times (P5, unchanged);
  - reports/stage_e33_briefs/work/logs/p10_stop.json: the 0.2 run's measured parts at its stop.
Method (protocol 0.3, P5 "Probe and compute stop"):
  R = B + sum_LOGIT(t_f) / P_L + sum_LGBM(t_f) / P_G over all 1,800 folds, where t_f is the fold's measured seconds if
  it finished before the 0.2 stop, else t_S5(label, grid, fold) * rho_m * n_set / n_S1, with rho_m the ratio
  sum(t_S1) / sum(t_S5) over the (label, grid, fold) cells finished in both S1 and S5 (per model family m).
Usage: python3 -I project_ref_v03.py <repo> <out.json> [<haiku fold_times_real.csv> for a cross-check]
"""
import csv
import hashlib
import json
import re
import sys
from pathlib import Path

N_FEATURES = {"S1": 23, "S2": 26, "S3": 27, "S4": 28, "S5": 59}  # search33.SETS (P4: C 15 + F1 8, F2 11, F3 12, F4 13)
P_B, P_L, P_G = 4, 8, 2          # 0.2 process counts (STATE P5 PROJECTION block), unchanged
N_OOF = 796
STOP_FACTOR = 3.0
DONE_RE = re.compile(r"^\d{4}-\d\d-\d\d \d\d:\d\d:\d\d,\d{3} INFO (E33-\w+) fold (\d) done ([\d.]+) s$")
START_RE = re.compile(r"^\d{4}-\d\d-\d\d \d\d:\d\d:\d\d,\d{3} INFO start (E33-\w+) fold (\d) ")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parts(cid: str) -> tuple:
    s, label, grid = cid[4:6], cid[6:9], cid[9:]
    return s, label, grid, "LOGIT" if grid.startswith("L") else "LGBM"


def main(repo: Path, out: Path, csv_check: Path | None) -> None:
    log = repo / "reports/stage_e33_briefs/work/logs/search_real.log"
    reg = repo / "ledger/trial_registrations.jsonl"
    bprobe = repo / "reports/stage_e33_briefs/work/logs/p5_builder_probe_e33b.log"
    stop = repo / "reports/stage_e33_briefs/work/logs/p10_stop.json"
    ids = next(json.loads(ln)["test_ids"] for ln in reg.read_text().splitlines()
               if ln.strip() and json.loads(ln).get("entry_id") == "r009-E33")
    assert len(ids) == len(set(ids)) == 300
    done, started = {}, set()
    for ln in log.read_text().splitlines():
        m = DONE_RE.match(ln)
        if m:
            key = (m.group(1), int(m.group(2)))
            assert key not in done, key
            done[key] = float(m.group(3))
        m = START_RE.match(ln)
        if m:
            started.add((m.group(1), int(m.group(2))))
    assert set(done) <= started
    cut = sorted(started - set(done))
    t_s5 = {(parts(c)[1], parts(c)[2], k): v for (c, k), v in done.items() if parts(c)[0] == "S5"}
    assert len(t_s5) == 360, len(t_s5)  # every S5 fold finished before the stop
    num = {"LOGIT": 0.0, "LGBM": 0.0}
    den = {"LOGIT": 0.0, "LGBM": 0.0}
    ncell = {"LOGIT": 0, "LGBM": 0}
    for (c, k), v in done.items():
        s, label, grid, m = parts(c)
        if s == "S1":
            num[m] += v
            den[m] += t_s5[(label, grid, k)]
            ncell[m] += 1
    rho = {m: num[m] / den[m] for m in num}
    tot = {"LOGIT": 0.0, "LGBM": 0.0}
    rem = {"LOGIT": 0.0, "LGBM": 0.0}
    per_set = {}
    for c in ids:
        s, label, grid, m = parts(c)
        for k in range(1, 7):
            if (c, k) in done:
                t, kind = done[(c, k)], "measured"
            else:
                t, kind = t_s5[(label, grid, k)] * rho[m] * N_FEATURES[s] / N_FEATURES["S1"], "projected"
                rem[m] += t
            tot[m] += t
            row = per_set.setdefault(f"{s} {m}", {"measured_folds": 0, "projected_folds": 0,
                                                  "measured_s": 0.0, "projected_s": 0.0})
            row[f"{kind}_folds"] += 1
            row[f"{kind}_s"] += t
    probe = [json.loads(ln)["wall_s"] for ln in bprobe.read_text().splitlines() if ln.startswith("{")]
    assert len(probe) == 3
    b_part = N_OOF * (sum(probe) / 3) / P_B
    ref = b_part + tot["LOGIT"] / P_L + tot["LGBM"] / P_G
    rem_wall = rem["LOGIT"] / P_L + rem["LGBM"] / P_G
    st = json.loads(stop.read_text())
    so_far = st["build_s"] + st["fits_net_s"]
    old_formula_real = b_part + 1080 * done[("E33-S5F15L100E", 6)] / P_L + 720 * done[("E33-S5F15G3050", 6)] / P_G
    res = {
        "inputs_sha256": {str(p.relative_to(repo)): sha256(p) for p in (log, reg, bprobe, stop)},
        "script_sha256": sha256(Path(__file__)),
        "folds": {"done_before_stop": len(done), "cut_by_stop": len(cut), "not_started": 1800 - len(started),
                  "projected": 1800 - len(done)},
        "cut_folds": [f"{c} fold {k}" for c, k in cut],
        "rho": {m: round(rho[m], 6) for m in rho}, "rho_cells": ncell,
        "rho_sums_s": {m: {"S1": round(num[m], 1), "S5_same_cells": round(den[m], 1)} for m in num},
        "builder_probe_s": probe, "B_s": round(b_part, 2),
        "sum_fold_s": {m: round(v, 1) for m, v in tot.items()},
        "sum_projected_fold_s": {m: round(v, 1) for m, v in rem.items()},
        "per_set_model": {k: {kk: (round(vv, 1) if isinstance(vv, float) else vv) for kk, vv in v.items()}
                          for k, v in sorted(per_set.items())},
        "R_0.3_s": round(ref, 1), "stop_at_s": round(STOP_FACTOR * ref, 1),
        "remaining_projected_wall_s": round(rem_wall, 1),
        "measured_at_0.2_stop_s": {"build_s": st["build_s"], "fits_net_s": st["fits_net_s"], "sum": round(so_far, 1)},
        "allowance_for_resumed_run_s": round(STOP_FACTOR * ref - so_far, 1),
        "info_0.2_formula_with_real_fold6_s": round(old_formula_real, 1),
    }
    if csv_check is not None:
        with open(csv_check, newline="") as fh:
            rows = list(csv.DictReader(fh))
        hk = {(r["config_id"], int(r["fold"])): float(r["seconds"]) for r in rows if r["status"] == "done"}
        hcut = sorted((r["config_id"], int(r["fold"])) for r in rows if r["status"] == "cut")
        res["haiku_csv_check"] = {"csv_sha256": sha256(csv_check), "done_equal": hk == done, "cut_equal": hcut == cut,
                                  "n_done": len(hk), "n_cut": len(hcut)}
    out.write_text(json.dumps(res, indent=1) + "\n")
    for k in ("folds", "rho", "rho_cells", "B_s", "sum_fold_s", "sum_projected_fold_s", "R_0.3_s", "stop_at_s",
              "remaining_projected_wall_s", "measured_at_0.2_stop_s", "allowance_for_resumed_run_s",
              "info_0.2_formula_with_real_fold6_s", "haiku_csv_check"):
        if k in res:
            print(k, json.dumps(res[k]))


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]) if len(sys.argv) > 3 else None)
