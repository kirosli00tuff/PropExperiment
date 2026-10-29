"""Stage E.33c D3 figure from fig/fig_data.json (written by run_dstats.py).

matplotlib is not in the project environment; run with the system interpreter, isolated:
    nice -n 10 python3 -I plot_dstats.py <fig_data.json> <out.png>
"""
from __future__ import annotations

import json
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

LINE_STYLE = {"SR0": ("#6b6b6b", "--", "SR0 = E[max SR] at N 838"), "G3": ("#b8860b", "-.", "G3 (DSR > 0.95)"),
              "binding": ("#b22222", "-", "binding max(G3, G4)")}


def bins(lo: float, hi: float, w: float) -> list:
    n = int(round((hi - lo) / w))
    return [lo + k * w for k in range(n + 1)]


def main(src: str, out: str) -> int:
    d = json.loads(open(src).read())
    real, null, maxima = d["real_sharpe"], d["null_sharpe"], d["null_seed_maxima"]
    n_real_const = sum(1 for v in d["real_constant"] if v)
    lines = d["lines"]
    b = bins(-0.34, 0.24, 0.01)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8.4), gridspec_kw={"height_ratios": [3, 1.4]})
    ax1.hist(null, bins=b, weights=[1 / len(null)] * len(null), histtype="stepfilled", alpha=0.35,
             color="#4c72b0", label=f"null per-configuration SR_d (B5: 20 seeds x 20 configs, n = {len(null)}; "
                                    f"{d['null_n_constant']} no-trade at 0)")
    ax1.hist(real, bins=b, weights=[1 / len(real)] * len(real), histtype="step", linewidth=1.8, color="#222222",
             label=f"real OOF SR_d (E.33, n = {len(real)}; {n_real_const} no-trade at 0)")
    for k, (col, ls, lab) in LINE_STYLE.items():
        ax1.axvline(lines[k], color=col, linestyle=ls, linewidth=1.4, label=f"{lab}: {lines[k]:.4f}")
        ax2.axvline(lines[k], color=col, linestyle=ls, linewidth=1.4)
    ax1.axvline(max(real), color="#222222", linestyle=":", linewidth=1.2, label=f"real max {max(real):.4f}")
    ax1.set_ylabel("share of configurations per 0.01 bin")
    ax1.set_title("E.33 OOF daily Sharpe (796 dates, Topstep market, L = 1 s) beside the B5 null")
    ax1.legend(fontsize=7.5, loc="upper left")
    ax1.set_xlim(b[0], b[-1])
    ax2.hist(maxima, bins=b, histtype="stepfilled", alpha=0.5, color="#4c72b0",
             label="null per-seed maxima over 20 configurations (20 seeds); not the null of the max over 300")
    ax2.axvline(max(real), color="#222222", linestyle=":", linewidth=1.2, label="real max over 300")
    ax2.axvline(d["e_max_300_report"], color="#4c72b0", linestyle="--", linewidth=1.2,
                label=f"report: E[max over 300] = {d['e_max_300_report']:.4f} (zero-edge null, independent, SD sigma_c,df)")
    ax2.set_xlim(b[0], b[-1])
    ax2.set_xlabel("daily Sharpe SR_d = mean / population SD")
    ax2.set_ylabel("seeds")
    ax2.yaxis.get_major_locator().set_params(integer=True)
    ax2.legend(fontsize=7.5, loc="upper left")
    fig.tight_layout()
    fig.savefig(out, dpi=130)
    print(f"wrote {out}: real {len(real)}, null {len(null)}, maxima {len(maxima)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
