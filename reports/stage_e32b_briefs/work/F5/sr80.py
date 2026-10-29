"""E.32b F5: SR80, the true daily Sharpe that passes a gate with probability 0.80 (no data read).

    uv run python reports/stage_e32b_briefs/work/F5/sr80.py [--out PATH]

Spec section 7 (reports/stage_e32b_ranking_spec.md, frozen): SR80 from E.32 protocol P7.2 as implemented in
reports/stage_e32_briefs/protocol/p7_final.py (read-only), with the DSR at N = 838, discovery T = 796 (G3 alone and
the binding G3 + G4) and test T = 870.

Two implementations, compared:
- A: p7_final's own functions, imported as a black box (bytecode writing switched off so nothing is written into
  the E.32 folder). p7_final's report(300) is also regenerated and compared byte for byte with the frozen
  p7_final_budget300.md on disk, and its printed values are parsed from that text.
- B: an independent re-implementation from the DSR definition (Bailey and Lopez de Prado; Mertens' standard error)
  using only statistics.NormalDist.

Primary SR80 convention (p7_final's "80%-power true daily Sharpe"): SR80 = bar + z_0.80 se(bar, T). The exact root of
p7_final's power(s, bar, T) = 0.80 (standard error at s rather than at the bar) is reported beside it.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import subprocess
import sys
from pathlib import Path
from statistics import NormalDist

REPO = Path(__file__).resolve().parents[4]
SPEC = REPO / "reports" / "stage_e32b_ranking_spec.md"
FROZEN_SPEC_SHA256 = "09ebe6970fcf027009152fa81a414360a015d535b095138cdf65cf1a4eb58635"
P7_DIR = REPO / "reports" / "stage_e32_briefs" / "protocol"
P7_FROZEN_MD = P7_DIR / "p7_final_budget300.md"
DEFAULT_OUT = Path(__file__).resolve().parent / "SR80.json"

N_TRIALS = 838          # spec 9.2
N_PRIOR_EXPECTED = 538  # E.32 protocol: N after E.33 = 538 + budget
BUDGET = N_TRIALS - N_PRIOR_EXPECTED
T_DISC = 796            # spec 9.2 (E.33's out-of-fold count)
T_TEST = 870            # spec 9.2 (E.32's test count)
POWER = 0.80
DSR_LEVEL = 0.95
T_STAT_BAR = 3.0
EULER_GAMMA = 0.5772156649015329
CROSS_CHECK_TOL = 1e-7  # A versus B; Acklam's inverse normal in funnel/ is accurate to about 1e-9
Z = NormalDist()


class SpecHashError(RuntimeError):
    """The frozen spec on disk does not match its recorded hash."""


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require_frozen_spec(path: Path = SPEC) -> str:
    digest = sha256_of(path)
    if digest != FROZEN_SPEC_SHA256:
        raise SpecHashError(f"spec sha256 {digest} != frozen {FROZEN_SPEC_SHA256}; refusing to run")
    return digest


# ---------------------------------------------------------------- B: independent re-implementation

def se_b(sr: float, t: int) -> float:
    """Mertens' standard error of a daily Sharpe, normal moments (skew 0, kurtosis 3)."""
    return math.sqrt((1.0 + 0.5 * sr * sr) / (t - 1))


def expected_max_b(n: int, variance: float) -> float:
    if n == 1:
        return 0.0
    term = ((1 - EULER_GAMMA) * Z.inv_cdf(1 - 1 / n)
            + EULER_GAMMA * Z.inv_cdf(1 - 1 / (n * math.e)))
    return math.sqrt(variance) * term


def _bisect(f, lo: float, hi: float, iters: int = 200) -> float:
    """Smallest x in [lo, hi] with f(x) >= 0 for an increasing f."""
    if f(lo) >= 0:
        return lo
    if f(hi) < 0:
        raise ValueError("root not bracketed")
    for _ in range(iters):
        mid = (lo + hi) / 2
        if f(mid) >= 0:
            hi = mid
        else:
            lo = mid
    return hi


def dsr_required_b(n: int, t: int, level: float = DSR_LEVEL) -> float:
    """Smallest observed daily Sharpe with DSR >= level at N = n, V = 1/(t - 1), normal moments."""
    sr0 = expected_max_b(n, 1 / (t - 1))
    z = Z.inv_cdf(level)
    return _bisect(lambda s: (s - sr0) * math.sqrt(t - 1) / math.sqrt(1 + 0.5 * s * s) - z, 0.0, 1.0)


def g4_b(b_test: float, t_disc: int) -> float:
    """Smallest discovery Sharpe whose one-SE lower bound reaches b_test."""
    return _bisect(lambda s: s - se_b(s, t_disc) - b_test, 0.0, 1.0)


def sr80_closed(bar: float, t: int, se) -> float:
    return bar + Z.inv_cdf(POWER) * se(bar, t)


def sr80_exact(bar: float, t: int, se) -> float:
    return _bisect(lambda s: (s - bar) / se(s, t) - Z.inv_cdf(POWER), bar, bar + 1.0)


def thresholds_b() -> dict:
    g3 = dsr_required_b(N_TRIALS, T_DISC)
    t_bar = T_STAT_BAR / math.sqrt(T_TEST)
    dsr_test = dsr_required_b(N_TRIALS, T_TEST)
    b_test = max(t_bar, dsr_test)
    g4 = g4_b(b_test, T_DISC)
    return {"SR0_disc": expected_max_b(N_TRIALS, 1 / (T_DISC - 1)),
            "SR0_test": expected_max_b(N_TRIALS, 1 / (T_TEST - 1)),
            "G3": g3, "t_bar_test": t_bar, "DSR_test": dsr_test, "b_test": b_test, "G4": g4,
            "G3_G4_binding": max(g3, g4)}


def sr80_set(th: dict, se) -> dict:
    bars = {"disc_G3": (th["G3"], T_DISC), "disc_G3G4": (th["G3_G4_binding"], T_DISC),
            "test": (th["b_test"], T_TEST)}
    return {"closed": {k: sr80_closed(b, t, se) for k, (b, t) in bars.items()},
            "exact": {k: sr80_exact(b, t, se) for k, (b, t) in bars.items()},
            "bars": {k: {"bar": b, "T": t} for k, (b, t) in bars.items()}}


# ---------------------------------------------------------------- A: p7_final imported (read-only)

def load_p7():
    sys.dont_write_bytecode = True  # never write into the E.32 folder
    for p in (str(REPO), str(P7_DIR)):
        if p not in sys.path:
            sys.path.insert(0, p)
    import p7_final  # noqa: PLC0415
    return p7_final


def thresholds_a(p7) -> dict:
    n = p7.N_PRIOR + BUDGET
    t_disc = p7.trade_dates(*p7.DISCOVERY) - p7.BURN_IN
    t_test = p7.trade_dates(*p7.TEST_MBO) - p7.BURN_IN
    v_d, v_t = 1 / (t_disc - 1), 1 / (t_test - 1)
    g3 = p7.required_sharpe(n, t_disc, v_d, 0.0, 3.0)
    t_bar = 3.0 / math.sqrt(t_test)
    dsr_test = p7.required_sharpe(n, t_test, v_t, 0.0, 3.0)
    b_test = max(t_bar, dsr_test)
    g4 = p7.g4_threshold(b_test, t_disc)
    return {"N": n, "T_disc": t_disc, "T_test": t_test,
            "SR0_disc": p7.expected_max_sharpe(n, v_d), "SR0_test": p7.expected_max_sharpe(n, v_t),
            "G3": g3, "t_bar_test": t_bar, "DSR_test": dsr_test, "b_test": b_test, "G4": g4,
            "G3_G4_binding": max(g3, g4)}


PRINTED_PATTERNS = {
    "SR0_disc": r"SR0 = ([0-9.]+) daily",
    "G3": r"SR_d needed, normal moments: ([0-9.]+) daily",
    "t_bar_test": r"daily t > 3\.0: ([0-9.]+)",
    "DSR_test": r"V = 1/\(T_test - 1\), normal moments: ([0-9.]+)",
    "b_test": r"b_test = max = ([0-9.]+)",
    "G4": r"G4 threshold on discovery SR_d: ([0-9.]+)",
    "G3_G4_binding": r"binding selection threshold max\(G3, G4\) = ([0-9.]+)",
    "SR80_test": r"80%-power true daily Sharpe at b_test: ([0-9.]+?)\.?\)",
}


def parse_printed(text: str) -> dict:
    out = {}
    for key, pat in PRINTED_PATTERNS.items():
        m = re.search(pat, text)
        out[key] = float(m.group(1)) if m else None
    return out


# ---------------------------------------------------------------- assembly

def pdt_now() -> str:
    return subprocess.run(["date", "+%Y-%m-%d %H:%M:%S %Z"], capture_output=True, text=True,
                          env={"TZ": "America/Vancouver"}, check=True).stdout.strip()


def build() -> dict:
    spec_sha = require_frozen_spec()
    th_b = thresholds_b()
    sr_b = sr80_set(th_b, se_b)
    p7 = load_p7()
    th_a = thresholds_a(p7)
    sr_a = sr80_set(th_a, p7.se_sharpe)
    regenerated = p7.report(BUDGET)
    on_disk = P7_FROZEN_MD.read_text()
    printed = parse_printed(on_disk)
    power_at = {k: p7.power(sr_a["closed"][k], sr_a["bars"][k]["bar"], sr_a["bars"][k]["T"])
                for k in sr_a["closed"]}
    diffs = {f"thresholds.{k}": abs(th_a[k] - th_b[k]) for k in th_b}
    diffs.update({f"SR80.{form}.{k}": abs(sr_a[form][k] - sr_b[form][k])
                  for form in ("closed", "exact") for k in sr_a[form]})
    printed_vs = {k: {"printed": v, "recomputed": (sr_a["closed"]["test"] if k == "SR80_test" else th_a[k]),
                      "agrees_at_4dp": v is not None and abs(
                          round(sr_a["closed"]["test"] if k == "SR80_test" else th_a[k], 4) - v) < 1e-9}
                  for k, v in printed.items()}
    checks = {
        "N_equals_838": th_a["N"] == N_TRIALS,
        "T_disc_equals_796": th_a["T_disc"] == T_DISC,
        "T_test_equals_870": th_a["T_test"] == T_TEST,
        "A_vs_B_max_abs_diff_below_tol": max(diffs.values()) < CROSS_CHECK_TOL,
        "p7_report_regenerated_equals_disk": regenerated == on_disk,
        "printed_values_agree_at_4dp": all(v["agrees_at_4dp"] for v in printed_vs.values()),
    }
    if not all(checks.values()):
        raise RuntimeError(f"SR80 cross-check failed: {checks}")
    return {
        "spec_sha256": spec_sha,
        "generated_pdt": pdt_now(),
        "generated_by": "reports/stage_e32b_briefs/work/F5/sr80.py",
        "inputs": {"N": N_TRIALS, "N_prior": th_a["N"] - BUDGET, "budget": BUDGET, "T_disc": T_DISC,
                   "T_test": T_TEST, "power": POWER, "dsr_level": DSR_LEVEL, "t_stat_bar": T_STAT_BAR,
                   "V_disc": 1 / (T_DISC - 1), "V_test": 1 / (T_TEST - 1),
                   "moments": "normal (skewness 0, kurtosis 3)",
                   "source": "reports/stage_e32_briefs/protocol/p7_final.py (read-only, imported)"},
        "formula": {
            "se": ("se(s, T) = sqrt((1 - g3 s + (g4 - 1)/4 s^2) / (T - 1)) = sqrt((1 + s^2/2) / (T - 1)) "
                   "at normal moments"),
            "SR0": "E[max SR] = sqrt(V) [(1 - gamma) Phi^-1(1 - 1/N) + gamma Phi^-1(1 - 1/(N e))], V = 1/(T - 1)",
            "G3": "smallest s with Phi((s - SR0) sqrt(T_disc - 1) / sqrt(1 + s^2/2)) >= 0.95 (N = 838, T = 796)",
            "b_test": "max(3.0 / sqrt(T_test), smallest s with DSR >= 0.95 at N = 838, T = 870)",
            "G4": "smallest s with s - se(s, T_disc) >= b_test",
            "G3_G4_binding": "max(G3, G4)",
            "SR80": "bar + Phi^-1(0.80) se(bar, T): p7_final's '80%-power true daily Sharpe' (s80 in report())",
            "SR80_exact": "root of p7_final.power(s, bar, T) = Phi((s - bar) / se(s, T)) = 0.80",
            "bars": "disc_G3: G3 at T = 796; disc_G3G4: max(G3, G4) at T = 796; test: b_test at T = 870",
        },
        "thresholds": {k: th_a[k] for k in th_b},
        "SR80": sr_a["closed"],
        "SR80_exact_root": sr_a["exact"],
        "power_at_SR80_by_p7_power": power_at,
        "bars": sr_a["bars"],
        "cross_check": {
            "method_A": "p7_final.py functions imported (required_sharpe, expected_max_sharpe, se_sharpe, "
                        "g4_threshold, power, trade_dates), sys.dont_write_bytecode set",
            "method_B": "independent re-implementation in this file with statistics.NormalDist only",
            "max_abs_diff_A_vs_B": max(diffs.values()),
            "tolerance": CROSS_CHECK_TOL,
            "p7_frozen_output": "reports/stage_e32_briefs/protocol/p7_final_budget300.md",
            "p7_frozen_output_sha256": sha256_of(P7_FROZEN_MD),
            "printed_vs_recomputed": printed_vs,
            "checks": checks,
            "pass": True,
        },
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args(argv[1:])
    result = build()
    args.out.write_text(json.dumps(result, indent=2) + "\n")
    s = result["SR80"]
    print(f"SR80 disc_G3 {s['disc_G3']:.4f} disc_G3G4 {s['disc_G3G4']:.4f} test {s['test']:.4f}; "
          f"cross-check pass, max |A - B| {result['cross_check']['max_abs_diff_A_vs_B']:.2e}; wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
