"""Every statistic entering the H1-H5 verdicts, from the series rebuilt by recompute_series.py and
recompute_h5.py: n, mean, sd, t, Newey-West t (frozen lags), p_t, p_nw, p = max, year stability,
Holm at 0.05 over the five base-case p's, each pass bar, DSR at N read from the registry.
Writes recompute.json. Nothing here reads a result file's statistics or verdict.json."""
from __future__ import annotations

import json
import sys

import numpy as np

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from vv_common import (CASES, HOLM_ALPHA, MIN_N, OUT, REPO, TESTS, describe, dsr_table, holm,  # noqa: E402
                       write_json)


def registry_n() -> int:
    with open(REPO / "ledger/trial_registrations.jsonl", encoding="utf-8") as handle:
        entries = [json.loads(l) for l in handle if l.strip()]
    return int(entries[-1]["n_after"])


def load_series(test: str) -> dict:
    with open(OUT / f"series_{test}.json", encoding="utf-8") as handle:
        return json.load(handle)


def h5_descriptives(series: dict) -> dict:
    """Descriptive only (never a verdict input): how much of H5's base sd the extreme dates carry."""
    out = {}
    for case in CASES:
        xs = np.asarray(series[case]["values"])
        dates = series[case]["dates"]
        order = np.argsort(-np.abs(xs))
        top = [(dates[i], float(xs[i])) for i in order[:10]]
        rec = {"top10_abs": top}
        for k in (1, 5, 10, 30):
            keep = np.ones(len(xs), bool)
            keep[order[:k]] = False
            sub = xs[keep]
            rec[f"without_top{k}"] = {"n": int(len(sub)), "mean": float(sub.mean()),
                                     "sd": float(sub.std(ddof=1)),
                                     "t": float(sub.mean() / (sub.std(ddof=1) / np.sqrt(len(sub))))}
        out[case] = rec
    return out


def main() -> None:
    n_trials = registry_n()
    series = {t: load_series(t) for t in TESTS}
    stats = {t: {c: describe(t, series[t][c]["dates"], np.asarray(series[t][c]["values"]))
                 for c in CASES} for t in TESTS}
    base_p = {t: stats[t]["base"]["p"] for t in TESTS}
    holm_out = holm(base_p, HOLM_ALPHA)
    pass_bar = {}
    for t in TESTS:
        s = stats[t]["base"]
        steps = {"holm_rejects": holm_out["rejected"][t], "mean_positive": s["mean"] > 0,
                 "n_at_least_30": s["n"] >= MIN_N, "year_stability": s["year_stability"]["pass"]}
        pass_bar[t] = {**steps, "pass": all(steps.values())}
    dsr = {c: dsr_table({t: np.asarray(series[t][c]["values"]) for t in TESTS}, n_trials)
           for c in CASES}
    stress_survives = {t: {"mean_positive": stats[t]["stress"]["mean"] > 0,
                           "p": stats[t]["stress"]["p"]} for t in TESTS}
    out = {"n_trials_from_registry": n_trials, "stats": stats, "holm_base": holm_out,
           "pass_bar": pass_bar, "dsr_at_N": dsr, "stress_case_descriptive": stress_survives,
           "h5_descriptive": h5_descriptives(series["H5"])}
    write_json(OUT / "recompute.json", out)
    for t in TESTS:
        for c in CASES:
            s = stats[t][c]
            print(f"{t} {c:7s} n={s['n']} mean={s['mean']:.5f} sd={s['sd']:.5f} t={s['t']:.3f} "
                  f"t_nw={s['t_nw']:.3f} p_t={s['p_t']:.3g} p_nw={s['p_nw']:.3g} p={s['p']:.3g} "
                  f"years q/pos={s['year_stability']['qualifying_years']}/"
                  f"{s['year_stability']['positive_years']} ys={s['year_stability']['pass']}")
    print("Holm:", [(st["test"], f"{st['p']:.3g}", f"{st['threshold']:.4f}", st["reject"])
                    for st in holm_out["steps"]])
    print("pass bar:", {t: pass_bar[t]["pass"] for t in TESTS})
    print("DSR base:", {t: (None if dsr["base"]["dsr"][t]["dsr"] is None
                            else round(dsr["base"]["dsr"][t]["dsr"], 4)) for t in TESTS},
          "sharpe var", dsr["base"]["sharpe_variance"], "E[max SR]",
          dsr["base"]["expected_max_sharpe_under_null"], "N", n_trials)
    print("H5 descriptive sd without top-k (base):",
          {k: round(v["sd"], 3) for k, v in out["h5_descriptive"]["base"].items() if k != "top10_abs"})


if __name__ == "__main__":
    main()
