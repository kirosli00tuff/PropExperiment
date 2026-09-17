"""Stage B Task 3 runner: the zero-edge funnel baseline, both payout paths.

    uv run python -m funnel.run_null_baseline

Writes reports/funnel_null_baseline.json (everything) and
reports/funnel_null_baseline.md (tables; prose sections are added by hand).

Design, fixed before any run:
- Headline sizing: the integer micro count whose daily sd is closest to 25% of the
  $2,000 MLL, using the research-slice RTH sd from the null generator's calibration.
  At $283.62 per micro that is round(500 / 283.62) = 2 micros (daily sd ~$567).
- Headline activity: one round turn per day (the cheapest zero-edge trader).
- Sample size: nested ladder 1k..64k with the stability rule in ``funnel.simulator``.
  Reported headline numbers use the largest N; the ladder shows where they settled.
- Sensitivity (not headline): micros {1,2,3,5} x round turns/day {1,2,4}, and bootstrap mean
  block {1,5,21} days. The power gate's critical value is the MOST FAVORABLE null over
  this grid (conservative).
"""

from __future__ import annotations

import json
import time
from datetime import UTC, datetime

import numpy as np

from funnel.null_generator import NullDayGenerator, calibration_summary, load_null_generator
from funnel.simulator import (
    FeeSchedule,
    FunnelConfig,
    RunResult,
    monthly_net_usd,
    run_many,
    stability_ladder,
    summarize,
)
from rules.xfa_rules import XFA_50K, PayoutPath
from sim.fill_model import COMMISSION_PER_SIDE_CENTS_PER_MICRO

BASE_SEED = 20_260_917
LADDER = (1_000, 2_000, 4_000, 8_000, 16_000, 32_000, 64_000)
SENSITIVITY_MICROS = (1, 2, 3, 5)
# Added after the first run showed null income still RISING at 5 micros (the funnel caps losses
# at fees while payouts harvest upside): extend until past the XFA's initial 20-micro cap.
EXTENDED_MICROS = (6, 7, 8, 10, 15, 20, 30)
SENSITIVITY_SEGMENTS = (1, 2, 4)
SENSITIVITY_RUNS = 32_000
BLOCK_LENGTHS = (1.0, 5.0, 21.0)
TARGET_DAILY_SD_SHARE_OF_MLL = 0.25
PATHS = (PayoutPath.STANDARD, PayoutPath.CONSISTENCY)
JSON_PATH = "reports/funnel_null_baseline.json"
MD_PATH = "reports/funnel_null_baseline.md"


def headline_micros(sd_usd_per_micro: float) -> int:
    target = TARGET_DAILY_SD_SHARE_OF_MLL * XFA_50K.mll_cents / 100
    return max(1, round(target / sd_usd_per_micro))


def net_quantile(results: list[RunResult], cfg: FunnelConfig, q: float) -> float:
    return float(np.quantile(monthly_net_usd(results, cfg.horizon_days), q))


def compact(results: list[RunResult], cfg: FunnelConfig) -> dict:
    summary = summarize(results, cfg)
    inc = summary["monthly_income_usd"]
    return {
        "runs": summary["runs"],
        "pass_rate_per_attempt": summary["combine"]["pass_rate_per_attempt"],
        "pass_rate_per_resolved_attempt": summary["combine"]["pass_rate_per_resolved_attempt"],
        "p_first_payout_within_12m": summary["first_payout"]["p_within_horizon"],
        "months_to_first_payout_p50_given_payout":
            summary["first_payout"]["months_to_first_payout_given_payout"].get("p50"),
        "monthly_gross_mean": inc["gross_payouts"]["mean"],
        "monthly_net_mean": inc["net_of_fees"]["mean"],
        "monthly_net_p50": inc["net_of_fees"]["p50"],
        "monthly_net_p80": net_quantile(results, cfg, 0.80),
        "monthly_net_p90": net_quantile(results, cfg, 0.90),
        "monthly_net_p95": net_quantile(results, cfg, 0.95),
        "p_net_positive": inc["net_of_fees"]["p_positive"],
        "mean_xfa_breaches": summary["xfa"]["mean_breaches_per_run"],
        "p_same_day_multi_breach": summary["blowups"]["p_run_has_same_day_multi_breach"],
        "share_multi_given_2plus_live": summary["blowups"]["share_multi_account_given_2plus_live"],
    }


def full_summary(results: list[RunResult], cfg: FunnelConfig) -> dict:
    summary = summarize(results, cfg)
    summary["monthly_income_usd"]["net_of_fees"]["p80"] = net_quantile(results, cfg, 0.80)
    summary["monthly_income_usd"]["net_of_fees"]["p95"] = net_quantile(results, cfg, 0.95)
    return summary


def main() -> None:
    started = time.perf_counter()
    generators: dict[int, NullDayGenerator] = {t: load_null_generator(t) for t in (1, 2, 4)}
    calibration = {t: calibration_summary(g.table) for t, g in generators.items()}
    sd = calibration[1]["rth_session_move_sd_usd_per_micro"]
    micros = headline_micros(sd)
    out: dict = {
        "generated_utc": datetime.now(UTC).isoformat(),
        "base_seed": BASE_SEED,
        "calibration": calibration,
        "fees": FeeSchedule().as_dict(),
        "commission_per_side_cents_per_micro": COMMISSION_PER_SIDE_CENTS_PER_MICRO,
        "sizing": {
            "rule": "integer micros whose daily RTH sd is closest to 25% of the $2,000 MLL",
            "sd_usd_per_micro": sd,
            "headline_micros": micros,
            "headline_daily_sd_usd": round(micros * sd, 2),
        },
        "headline_segments_per_day": 1,
        "horizon_trading_days": 252,
        "headline": {}, "independent_counterfactual": {}, "sensitivity": [],
        "block_length_sensitivity": [],
    }

    for path in PATHS:
        cfg = FunnelConfig(path, micros)
        results = run_many(cfg, generators[1], LADDER[-1], BASE_SEED)
        out["headline"][path.value] = {"summary": full_summary(results, cfg),
                                       "stability": stability_ladder(results, cfg, LADDER)}
        ind_cfg = FunnelConfig(path, micros, correlated=False)
        ind = run_many(ind_cfg, generators[1], LADDER[-1], BASE_SEED)
        out["independent_counterfactual"][path.value] = {"summary": full_summary(ind, ind_cfg)}
        elapsed = time.perf_counter() - started
        print(f"{path.value}: headline + counterfactual done ({elapsed:.0f}s)")

        for m in SENSITIVITY_MICROS:
            for t in SENSITIVITY_SEGMENTS:
                s_cfg = FunnelConfig(path, m)
                s_res = run_many(s_cfg, generators[t], SENSITIVITY_RUNS, BASE_SEED)
                out["sensitivity"].append({"path": path.value, "micros": m,
                                           "segments_per_day": t, **compact(s_res, s_cfg)})
        for block in BLOCK_LENGTHS:
            b_cfg = FunnelConfig(path, micros)
            b_res = run_many(b_cfg, NullDayGenerator(generators[1].table, block),
                             SENSITIVITY_RUNS, BASE_SEED)
            out["block_length_sensitivity"].append({"path": path.value, "mean_block_days": block,
                                                    **compact(b_res, b_cfg)})
        print(f"{path.value}: sensitivity done ({time.perf_counter() - started:.0f}s)")

    out["null_critical_values_monthly_net_usd"] = critical_values(out["sensitivity"])
    out["runtime_seconds"] = round(time.perf_counter() - started, 1)
    with open(JSON_PATH, "w") as fh:
        json.dump(out, fh, indent=1)
    with open(MD_PATH, "w") as fh:
        fh.write(render_markdown(out))
    print(f"wrote {JSON_PATH} and {MD_PATH} in {out['runtime_seconds']}s")


def critical_values(sensitivity: list[dict]) -> dict:
    """Most favorable null per path: the max over the sensitivity grid of each upper quantile."""
    out: dict = {}
    for path in PATHS:
        rows = [r for r in sensitivity if r["path"] == path.value]
        out[path.value] = {}
        for key in ("monthly_net_p80", "monthly_net_p90", "monthly_net_p95"):
            best = max(rows, key=lambda r, k=key: r[k])
            out[path.value][key] = {"value": best[key], "micros": best["micros"],
                                    "segments_per_day": best["segments_per_day"]}
    return out


def _usd(x: float | None) -> str:
    if x is None:
        return "—"
    return f"-${-x:,.0f}" if round(x) < 0 else f"${x:,.0f}"


def _pct(x: float | None) -> str:
    return "—" if x is None else f"{100 * x:.1f}%"


def _headline_table(h: dict) -> list[str]:
    lines = ["| Metric | Standard path | Consistency path |", "|---|---|---|"]
    ttfp = "months_to_first_payout_given_payout"
    rows = [
        ("Runs", lambda s: f"{s['runs']:,}"),
        ("Combine pass rate per attempt", lambda s: _pct(s["combine"]["pass_rate_per_attempt"])),
        ("Combine pass rate per resolved attempt",
         lambda s: _pct(s["combine"]["pass_rate_per_resolved_attempt"])),
        ("Runs passing ≥1 Combine in 12 months",
         lambda s: _pct(s["combine"]["p_run_passes_at_least_once"])),
        ("Combine attempts per run (mean)",
         lambda s: f"{s['combine']['mean_attempts_per_run']:.1f}"),
        ("P(first payout within 12 months)",
         lambda s: _pct(s["first_payout"]["p_within_horizon"])),
        ("Months to first payout, p10 / p50 / p90 (given a payout)",
         lambda s: " / ".join(f"{s['first_payout'][ttfp][q]:.1f}" for q in ("p10", "p50", "p90"))),
        ("Monthly gross payouts, mean",
         lambda s: _usd(s["monthly_income_usd"]["gross_payouts"]["mean"])),
        ("Monthly fees, mean", lambda s: _usd(s["monthly_income_usd"]["mean_fees_per_month"])),
    ]
    for q in ("mean", "p10", "p25", "p50", "p75", "p80", "p90", "p95"):
        rows.append((f"Monthly net income, {q}",
                     lambda s, q=q: _usd(s["monthly_income_usd"]["net_of_fees"][q])))
    rows += [
        ("P(net income > 0)", lambda s: _pct(s["monthly_income_usd"]["net_of_fees"]["p_positive"])),
        ("XFAs activated per run (mean)", lambda s: f"{s['xfa']['mean_activated_per_run']:.2f}"),
        ("XFA payouts per run (mean)", lambda s: f"{s['xfa']['mean_payouts_per_run']:.2f}"),
        ("XFA breaches per run (mean)", lambda s: f"{s['xfa']['mean_breaches_per_run']:.2f}"),
        ("Runs ever reaching 5 live XFAs", lambda s: _pct(s["xfa"]["p_run_reaches_5_live"])),
    ]
    for label, fn in rows:
        lines.append(f"| {label} | {fn(h['standard'])} | {fn(h['consistency'])} |")
    return lines


def _correlation_table(h: dict, ind: dict) -> list[str]:
    lines = ["| Metric | Standard (correlated) | Standard (independent) | "
             "Consistency (correlated) | Consistency (independent) |", "|---|---|---|---|---|"]
    hist = "breached_count_histogram_given_2plus_live"
    rows = [
        ("Breach days with ≥2 live XFAs",
         lambda s: f"{s['blowups']['days_with_2plus_live_and_a_breach']:,}"),
        ("…share where ≥2 XFAs breached the same day",
         lambda s: _pct(s["blowups"]["share_multi_account_given_2plus_live"])),
        ("…share where every live XFA breached",
         lambda s: _pct(s["blowups"]["share_all_live_breached_given_2plus_live"])),
        ("Runs with a same-day multi-XFA breach",
         lambda s: _pct(s["blowups"]["p_run_has_same_day_multi_breach"])),
        ("Monthly net income, mean",
         lambda s: _usd(s["monthly_income_usd"]["net_of_fees"]["mean"])),
        ("Monthly net income, p80", lambda s: _usd(s["monthly_income_usd"]["net_of_fees"]["p80"])),
    ]
    rows += [(f"Breach days (≥2 live) with exactly {k} breached",
              lambda s, k=k: f"{s['blowups'][hist][k]:,}") for k in ("1", "2", "3", "4", "5")]
    for label, fn in rows:
        lines.append(f"| {label} | {fn(h['standard'])} | {fn(ind['standard'])} | "
                     f"{fn(h['consistency'])} | {fn(ind['consistency'])} |")
    return lines


def _stability_table(st: dict) -> list[str]:
    lines = ["| N | pass rate/attempt | P(payout ≤12m) | P(multi-breach run) | net mean | "
             "net median | net p80 | stable vs next |", "|---|---|---|---|---|---|---|---|"]
    for r in st["ladder"]:
        m = r["metrics"]

        def cell(name: str, fmt, m=m) -> str:  # noqa: ANN001
            return f"{fmt(m[name]['estimate'])} ± {fmt(1.96 * m[name]['mc_se'])}"

        stable = "—" if "stable" not in r else ("yes" if r["stable"] else "no")
        lines.append(
            f"| {r['n']:,} | {cell('pass_rate_per_attempt', _pct)} | "
            f"{cell('p_first_payout_within_horizon', _pct)} | "
            f"{cell('p_same_day_multi_xfa_breach', _pct)} | {cell('monthly_net_usd_mean', _usd)} | "
            f"{cell('monthly_net_usd_median', _usd)} | {cell('monthly_net_usd_p80', _usd)} | "
            f"{stable} |")
    return lines


def render_markdown(out: dict) -> str:
    h = {p: out["headline"][p]["summary"] for p in ("standard", "consistency")}
    ind = {p: out["independent_counterfactual"][p]["summary"] for p in ("standard", "consistency")}
    lines = [
        "# Funnel null baseline (Stage B, Task 3)", "",
        f"Generated {out['generated_utc']} · seed {out['base_seed']} · "
        f"`uv run python -m funnel.run_null_baseline` · machine-readable: `{JSON_PATH}`", "",
        "<!-- PROSE:SUMMARY -->", "",
        f"## Headline: zero-edge trader, {out['sizing']['headline_micros']} micros, "
        "1 round turn/day, 12 months (252 trading days)", "",
        *_headline_table(h), "",
        "## Correlated blowups across the XFA cluster", "",
        "Counted on days when ≥2 XFAs were live at the open and at least one breached. "
        "'Independent' is the counterfactual where every account draws its own market.", "",
        *_correlation_table(h, ind), "",
        "<!-- PROSE:CORRELATION -->", "",
        "## Sample-size stability", "",
    ]
    for p in ("standard", "consistency"):
        st = out["headline"][p]["stability"]
        crit = st["criterion"]
        stable = "not reached" if st["stable_n"] is None else f"{st['stable_n']:,}"
        lines += [f"**{p.title()} path:** stable at N = {stable}. Rule: `{crit['rule']}`; rate "
                  f"tolerance ±{100 * crit['rate_tol']:.0f} pp, USD tolerance "
                  f"max(${crit['usd_tol_abs']:.0f}, {100 * crit['usd_tol_rel']:.0f}%). "
                  "Cells are estimate ± 1.96 × Monte Carlo SE.", "",
                  *_stability_table(st), ""]
    lines += [f"## Sensitivity: size × round turns per day (correlated, {SENSITIVITY_RUNS:,} runs)",
              "", "| Path | Micros | RT/day | Pass/attempt | P(payout ≤12m) | Net mean | Net p50 | "
              "Net p80 | Net p90 | P(net>0) | XFA breaches/run |",
              "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in out["sensitivity"]:
        lines.append(
            f"| {r['path']} | {r['micros']} | {r['segments_per_day']} | "
            f"{_pct(r['pass_rate_per_attempt'])} | {_pct(r['p_first_payout_within_12m'])} | "
            f"{_usd(r['monthly_net_mean'])} | {_usd(r['monthly_net_p50'])} | "
            f"{_usd(r['monthly_net_p80'])} | {_usd(r['monthly_net_p90'])} | "
            f"{_pct(r['p_net_positive'])} | {r['mean_xfa_breaches']:.2f} |")
    lines += ["", "## Sensitivity: bootstrap mean block length (headline size)", "",
              "| Path | Mean block (days) | Pass/attempt | P(payout ≤12m) | Net mean | Net p80 | "
              "P(multi-breach run) |", "|---|---|---|---|---|---|---|"]
    for r in out["block_length_sensitivity"]:
        lines.append(
            f"| {r['path']} | {r['mean_block_days']:.0f} | {_pct(r['pass_rate_per_attempt'])} | "
            f"{_pct(r['p_first_payout_within_12m'])} | {_usd(r['monthly_net_mean'])} | "
            f"{_usd(r['monthly_net_p80'])} | {_pct(r['p_same_day_multi_breach'])} |")
    lines += ["", "## Most favorable null (critical values used by the power gate)", "",
              "| Path | Quantile | Monthly net | at micros | RT/day |", "|---|---|---|---|---|"]
    for p, qs in out["null_critical_values_monthly_net_usd"].items():
        for k, v in qs.items():
            lines.append(f"| {p} | {k.replace('monthly_net_', '')} | {_usd(v['value'])} | "
                         f"{v['micros']} | {v['segments_per_day']} |")
    lines += ["", "<!-- PROSE:ASSUMPTIONS -->", ""]
    return "\n".join(lines)


def extend_sizes() -> None:
    """Append EXTENDED_MICROS rows to an existing baseline JSON and recompute critical values."""
    started = time.perf_counter()
    with open(JSON_PATH) as fh:
        out = json.load(fh)
    # Only 1 round turn/day for the extended sizes: null income falls with activity (more
    # cost, same zero edge), so the most favorable null — the only thing these rows are for —
    # is always at T=1. The 1/2/3/5-micro rows already cover T=2 and T=4.
    extended_segments = (1,)
    generators = {t: load_null_generator(t) for t in extended_segments}
    have = {(r["path"], r["micros"], r["segments_per_day"]) for r in out["sensitivity"]}
    for path in PATHS:
        for m in EXTENDED_MICROS:
            for t in extended_segments:
                if (path.value, m, t) in have:
                    continue
                cfg = FunnelConfig(path, m)
                res = run_many(cfg, generators[t], SENSITIVITY_RUNS, BASE_SEED)
                out["sensitivity"].append({"path": path.value, "micros": m,
                                           "segments_per_day": t, **compact(res, cfg)})
            print(f"{path.value} micros={m} done ({time.perf_counter() - started:.0f}s)")
    out["sensitivity"].sort(key=lambda r: (r["path"], r["micros"], r["segments_per_day"]))
    out["null_critical_values_monthly_net_usd"] = critical_values(out["sensitivity"])
    out["extended_sizes"] = {"micros": EXTENDED_MICROS, "generated_utc":
                             datetime.now(UTC).isoformat(),
                             "runtime_seconds": round(time.perf_counter() - started, 1)}
    with open(JSON_PATH, "w") as fh:
        json.dump(out, fh, indent=1)
    print(f"extended {JSON_PATH} in {out['extended_sizes']['runtime_seconds']}s")


if __name__ == "__main__":
    import sys

    extend_sizes() if "--extend-sizes" in sys.argv else main()
