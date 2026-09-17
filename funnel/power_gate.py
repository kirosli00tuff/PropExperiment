"""Power gate: which assumed strategy qualities beat the zero-edge funnel (Stage B, Task 4).

    uv run python -m funnel.power_gate      # needs reports/funnel_null_baseline.json

Stage D.1 screens a candidate with ``screen(...)`` before spending research time on it.

Test, stated (per payout path, per grid point q, per confidence level c):
- Outcome X = a run's 12-month net income per month (gross payouts - fees), at the
  headline sizing (2 micros per trade).
- HEADLINE critical value k_c = the c-quantile of the MATCHED null: a zero-edge trader at
  the SAME size and the SAME round turns per day as the grid point. The question is
  "does this edge beat luck at the same size and activity?".
- ROBUST critical value = the c-quantile of the MOST FAVORABLE null over every size and
  activity in the baseline's sensitivity grid (1-30 micros x 1/2/4 round turns). Why this is
  a separate, stricter column rather than the headline: the null baseline showed a zero-edge
  trader's funnel income RISING with size. The Combine/XFA caps losses at fees while payouts
  harvest upside, so volatility is worth money on its own. Comparing a 2-micro strategy
  against a trader rewarded for sizing up conflates edge with leverage. The robust column is
  still reported, because it answers "is this better than simply gambling bigger?".
- Power(q) = P(X_q > k_c), estimated from N Monte Carlo runs. The verdict uses the lower
  95% Monte Carlo bound so simulation noise cannot manufacture a pass:
  PASS if power - 1.96*se >= 0.80; MARGINAL if power >= 0.80 but the bound is below;
  FAIL otherwise.
- Every grid point's sorted net-income samples are saved to reports/power_gate_samples.npz,
  so verdicts can be recomputed for any other critical value without re-simulating.

Why c = 80% is the headline (with 90% and 95% also reported): this is a screen that
runs BEFORE research time is spent. Wrongly discarding a real edge is expensive at this
stage, while a false pass is caught later by walk-forward folds, the sealed holdout
(Stage D.2) and the forward test (Stage E). So alpha = 0.20 with the conventional 80%
power. The stricter 90%/95% columns are for anyone who wants a tighter screen. A
strategy that fails even at 80% is not worth the funnel's fees.

All grid points share one base seed (common random numbers), so neighbouring cells
differ by their quality, not by simulation luck.
"""

from __future__ import annotations

import csv
import json
import math
import time
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

from funnel.null_generator import NullDayGenerator, load_null_generator
from funnel.quality_generator import QualityDayGenerator, QualityParams, expected_edge_ticks
from funnel.simulator import CostBook, FunnelConfig, monthly_net_usd, run_many, summarize
from rules.xfa_rules import PayoutPath
from sim.costs import load_slippage_table

NULL_BASELINE_JSON = Path("reports/funnel_null_baseline.json")
POWER_GATE_JSON = Path("reports/power_gate.json")
POWER_GATE_CSV = Path("reports/power_gate.csv")
POWER_GATE_MD = Path("reports/power_gate.md")
POWER_GATE_SAMPLES = Path("reports/power_gate_samples.npz")

GRID_WIN_PROBABILITY = (0.40, 0.45, 0.50, 0.55, 0.60)
GRID_WIN_LOSS_RATIO = (0.75, 1.0, 1.5, 2.0)
GRID_SEGMENTS_PER_DAY = (1, 2, 4)
CONFIDENCE_LEVELS = (0.80, 0.90, 0.95)
HEADLINE_CONFIDENCE = 0.80
REQUIRED_POWER = 0.80
MIN_RUNS_PER_POINT = 8_000
BASE_SEED = 20_260_917
Z95 = 1.96


def sample_key(path: str, segments_per_day: int, win_probability: float,
               win_loss_ratio: float) -> str:
    """Key of a grid point's sorted net-income samples in POWER_GATE_SAMPLES."""
    return f"{path}|T{segments_per_day}|p{win_probability}|R{win_loss_ratio}"


def verdict(power: float, n: int) -> tuple[str, float, float]:
    se = math.sqrt(max(power * (1.0 - power), 0.0) / n)
    lower = power - Z95 * se
    if lower >= REQUIRED_POWER:
        return "pass", se, lower
    if power >= REQUIRED_POWER:
        return "marginal", se, lower
    return "fail", se, lower


def p_beats(samples: np.ndarray, null_sorted: np.ndarray) -> float:
    """P(X > Y) for independent X ~ samples, Y ~ null (ties count half)."""
    below = np.searchsorted(null_sorted, samples, side="left")
    at_or_below = np.searchsorted(null_sorted, samples, side="right")
    return float(np.mean((below + at_or_below) / 2.0) / len(null_sorted))


def critical_value(baseline: dict, path: str, confidence: float) -> float:
    """ROBUST critical value: the most favorable null over all sizes and activities."""
    key = f"monthly_net_p{round(confidence * 100)}"
    return float(baseline["null_critical_values_monthly_net_usd"][path][key]["value"])


def matched_critical_value(baseline: dict, path: str, confidence: float, micros: int,
                           segments_per_day: int) -> float:
    """HEADLINE critical value: the null at the same size and round turns per day."""
    key = f"monthly_net_p{round(confidence * 100)}"
    for row in baseline["sensitivity"]:
        if (row["path"] == path and row["micros"] == micros
                and row["segments_per_day"] == segments_per_day):
            return float(row[key])
    raise KeyError(f"no null sensitivity row for {path} micros={micros} T={segments_per_day}")


def runs_per_point(baseline: dict) -> int:
    """8,000 runs per grid point. The null needed N=16,000 to pin its QUANTILES (critical values)
    to +/-2%; a grid point only needs a binomial proportion (power), whose 95% half-width at
    N=8,000 is <= 1.96*sqrt(0.25/8000) = 1.1 pp. Because the verdict uses the Monte Carlo LOWER
    bound, a smaller N can only turn a pass into "marginal", never manufacture a pass."""
    stable = [baseline["headline"][p]["stability"]["stable_n"] for p in ("standard", "consistency")]
    if any(s is None for s in stable):
        raise ValueError("null baseline did not stabilise; rerun it with a longer ladder first")
    return MIN_RUNS_PER_POINT


def mean_round_turn_cost_usd_per_micro(generator: NullDayGenerator, micros: int) -> float:
    book = CostBook(load_slippage_table(), "mean")
    table = generator.table
    total = sum(book.side_cents(int(a), micros) + book.side_cents(int(b), micros)
                for a, b in zip(table.entry_minute_ct.ravel(), table.exit_minute_ct.ravel(),
                                strict=True))
    return total / table.entry_minute_ct.size / micros / 100.0


def evaluate_point(
    path: PayoutPath, params: QualityParams, segments: int, micros: int, n: int,
    generators: dict[int, NullDayGenerator], baseline: dict, null_sorted: np.ndarray,
) -> dict:
    table = generators[segments].table
    cfg = FunnelConfig(path, micros)
    results = run_many(cfg, QualityDayGenerator(table, params), n, BASE_SEED)
    net = monthly_net_usd(results, cfg.horizon_days)
    summary = summarize(results, cfg)
    edge_ticks = expected_edge_ticks(params, table)
    row = {
        "path": path.value,
        "win_probability": params.win_probability,
        "win_loss_ratio": params.win_loss_ratio,
        "segments_per_day": segments,
        "micros": micros,
        "runs": n,
        "breakeven_win_probability": params.breakeven_win_probability,
        "expected_gross_edge_ticks_per_trade_per_micro": edge_ticks,
        "expected_gross_edge_usd_per_trade_per_micro": edge_ticks * 1.25,
        "pass_rate_per_attempt": summary["combine"]["pass_rate_per_attempt"],
        "p_first_payout_within_12m": summary["first_payout"]["p_within_horizon"],
        "monthly_net_mean": float(net.mean()),
        "monthly_net_p10": float(np.quantile(net, 0.10)),
        "monthly_net_p50": float(np.quantile(net, 0.50)),
        "monthly_net_p90": float(np.quantile(net, 0.90)),
        "p_beats_random_null_trader": p_beats(net, null_sorted),
        "mean_xfa_breaches": summary["xfa"]["mean_breaches_per_run"],
        "p_run_reaches_5_live": summary["xfa"]["p_run_reaches_5_live"],
        "p_same_day_multi_breach": summary["blowups"]["p_run_has_same_day_multi_breach"],
    }
    for c in CONFIDENCE_LEVELS:
        for prefix, k in (("", matched_critical_value(baseline, path.value, c, micros, segments)),
                          ("robust_", critical_value(baseline, path.value, c))):
            power = float(np.mean(net > k))
            label, se, lower = verdict(power, n)
            tag = f"{prefix}c{round(c * 100)}"
            row |= {f"{tag}_critical_value": k, f"{tag}_power": power, f"{tag}_power_se": se,
                    f"{tag}_power_lower95": lower, f"{tag}_verdict": label}
    row["_net_samples"] = np.sort(net)
    return row


def main() -> None:
    started = time.perf_counter()
    baseline = json.loads(NULL_BASELINE_JSON.read_text())
    micros = int(baseline["sizing"]["headline_micros"])
    n = runs_per_point(baseline)
    generators = {t: load_null_generator(t) for t in GRID_SEGMENTS_PER_DAY}
    rows: list[dict] = []
    for path in (PayoutPath.STANDARD, PayoutPath.CONSISTENCY):
        null_cfg = FunnelConfig(path, micros)
        null_net = np.sort(monthly_net_usd(run_many(null_cfg, generators[1], n, BASE_SEED + 1),
                                           null_cfg.horizon_days))
        for t in GRID_SEGMENTS_PER_DAY:
            for p in GRID_WIN_PROBABILITY:
                for r in GRID_WIN_LOSS_RATIO:
                    rows.append(evaluate_point(path, QualityParams(p, r), t, micros, n,
                                               generators, baseline, null_net))
            print(f"{path.value} T={t} done ({time.perf_counter() - started:.0f}s)")
    samples = {sample_key(r["path"], r["segments_per_day"], r["win_probability"],
                          r["win_loss_ratio"]): r.pop("_net_samples") for r in rows}
    np.savez_compressed(POWER_GATE_SAMPLES, **samples)
    costs = {t: mean_round_turn_cost_usd_per_micro(g, micros) for t, g in generators.items()}
    out = {
        "generated_utc": datetime.now(UTC).isoformat(),
        "null_baseline_generated_utc": baseline["generated_utc"],
        "base_seed": BASE_SEED,
        "runs_per_point": n,
        "headline_micros": micros,
        "headline_confidence": HEADLINE_CONFIDENCE,
        "required_power": REQUIRED_POWER,
        "verdict_rule": "pass if power - 1.96*se >= 0.80; marginal if power >= 0.80; else fail",
        "robust_critical_values_monthly_net_usd": baseline["null_critical_values_monthly_net_usd"],
        "matched_critical_values_monthly_net_usd": {
            path: {f"T{t}": {f"c{round(c * 100)}":
                             matched_critical_value(baseline, path, c, micros, t)
                             for c in CONFIDENCE_LEVELS} for t in GRID_SEGMENTS_PER_DAY}
            for path in ("standard", "consistency")},
        "samples_file": str(POWER_GATE_SAMPLES),
        "mean_round_turn_cost_usd_per_micro_by_segments": costs,
        "grid": {"win_probability": GRID_WIN_PROBABILITY, "win_loss_ratio": GRID_WIN_LOSS_RATIO,
                 "segments_per_day": GRID_SEGMENTS_PER_DAY},
        "rows": rows,
        "runtime_seconds": round(time.perf_counter() - started, 1),
    }
    POWER_GATE_JSON.write_text(json.dumps(out, indent=1))
    with POWER_GATE_CSV.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    POWER_GATE_MD.write_text(render_markdown(out))
    print(f"wrote power gate reports in {out['runtime_seconds']}s")


# ------------------------------------------------------------ consumer API ----
def screen(
    path: str,
    win_probability: float,
    win_loss_ratio: float,
    segments_per_day: int,
    confidence: float = HEADLINE_CONFIDENCE,
    gate_json: Path = POWER_GATE_JSON,
    robust: bool = False,
) -> dict:
    """Conservative lookup for a candidate's estimated quality.

    Uses the grid point with the largest win probability <= the estimate and the largest
    win/loss ratio <= the estimate, at exactly ``segments_per_day``. Estimates below the
    grid return verdict "below_grid" (treat as fail). ``robust=True`` reads the verdict against
    the most favorable null instead of the matched one.
    """
    gate = json.loads(Path(gate_json).read_text())
    if segments_per_day not in gate["grid"]["segments_per_day"]:
        raise ValueError(f"segments_per_day must be one of {gate['grid']['segments_per_day']}")
    tag = ("robust_" if robust else "") + f"c{round(confidence * 100)}"
    ps = [p for p in gate["grid"]["win_probability"] if p <= win_probability + 1e-12]
    rs = [r for r in gate["grid"]["win_loss_ratio"] if r <= win_loss_ratio + 1e-12]
    if not ps or not rs:
        return {"verdict": "below_grid", "grid_point": None}
    for row in gate["rows"]:
        if (row["path"] == path and row["segments_per_day"] == segments_per_day
                and row["win_probability"] == max(ps) and row["win_loss_ratio"] == max(rs)):
            return {"verdict": row[f"{tag}_verdict"], "power": row[f"{tag}_power"],
                    "power_lower95": row[f"{tag}_power_lower95"], "grid_point": row}
    raise KeyError(f"no grid row for path={path!r}")


# ---------------------------------------------------------------- report ----
_SYMBOL = {"pass": "PASS", "marginal": "marg", "fail": "fail"}


def _usd(x: float) -> str:
    return f"-${-x:,.0f}" if round(x) < 0 else f"${x:,.0f}"


def render_markdown(out: dict) -> str:
    lines = [
        "# Power gate (Stage B, Task 4)", "",
        f"Generated {out['generated_utc']} · `uv run python -m funnel.power_gate` · "
        f"{out['runs_per_point']:,} runs per grid point · {out['headline_micros']} micros · "
        "structured data: `reports/power_gate.json`, `reports/power_gate.csv`; lookup: "
        "`funnel.power_gate.screen(...)`", "",
        "<!-- PROSE:SUMMARY -->", "",
        f"Verdict rule: {out['verdict_rule']}.", "",
        "Headline critical values: the MATCHED null (zero edge, same size, same round turns/day), "
        "monthly net income quantile:", "",
        "| Path | RT/day | c = 80% | c = 90% | c = 95% |", "|---|---|---|---|---|",
    ]
    for p, by_t in out["matched_critical_values_monthly_net_usd"].items():
        for t, qs in by_t.items():
            lines.append(f"| {p} | {t[1:]} | " + " | ".join(_usd(qs[k]) for k in
                                                            ("c80", "c90", "c95")) + " |")
    lines += ["", "Robust critical values: the MOST FAVORABLE null over every size and activity "
              "(a zero-edge trader who picks the best size to gamble with):", "",
              "| Path | c = 80% | c = 90% | c = 95% | at micros / RT per day |",
              "|---|---|---|---|---|"]
    for p, qs in out["robust_critical_values_monthly_net_usd"].items():
        vals = " | ".join(_usd(qs[k]["value"]) for k in
                          ("monthly_net_p80", "monthly_net_p90", "monthly_net_p95"))
        at = qs["monthly_net_p80"]
        lines.append(f"| {p} | {vals} | {at['micros']} / {at['segments_per_day']} |")
    lines += ["", "Mean round-turn cost per micro (commission + modelled slippage, lower bound): " +
              ", ".join(f"{t} RT/day ${c:.2f}" for t, c in
                        out["mean_round_turn_cost_usd_per_micro_by_segments"].items()), ""]
    panels = [(f"c{round(c * 100)}", f"## Headline (matched null), confidence {round(c * 100)}%")
              for c in CONFIDENCE_LEVELS]
    panels.append(("robust_c80", "## Robust (most favorable null), confidence 80%"))
    for tag, heading in panels:
        lines += [heading, ""]
        for path in ("standard", "consistency"):
            for t in out["grid"]["segments_per_day"]:
                lines += [f"**{path.title()} path, {t} round turn(s)/day**: cell = verdict "
                          "(power); rows = win probability, columns = avg win / avg loss", "",
                          "| p \\ R | " + " | ".join(f"{r:g}" for r in
                                                     out["grid"]["win_loss_ratio"]) + " |",
                          "|---|" + "---|" * len(out["grid"]["win_loss_ratio"])]
                for p in out["grid"]["win_probability"]:
                    cells = []
                    for r in out["grid"]["win_loss_ratio"]:
                        row = next(x for x in out["rows"] if x["path"] == path
                                   and x["segments_per_day"] == t and x["win_probability"] == p
                                   and x["win_loss_ratio"] == r)
                        cells.append(f"{_SYMBOL[row[f'{tag}_verdict']]} "
                                     f"({100 * row[f'{tag}_power']:.0f}%)")
                    lines.append(f"| {p:.2f} | " + " | ".join(cells) + " |")
                lines.append("")
    lines += ["## Economics behind the cells (80%)", "",
              "| Path | RT/day | p | R | gross edge $/trade/micro | net mean $/mo | net p50 | "
              "P(payout ≤12m) | P(beat random null) | power (matched) | verdict (matched) | "
              "verdict (robust) |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for row in out["rows"]:
        lines.append(
            f"| {row['path']} | {row['segments_per_day']} | {row['win_probability']:.2f} | "
            f"{row['win_loss_ratio']:g} | "
            f"{row['expected_gross_edge_usd_per_trade_per_micro']:.2f} | "
            f"{_usd(row['monthly_net_mean'])} | {_usd(row['monthly_net_p50'])} | "
            f"{100 * row['p_first_payout_within_12m']:.0f}% | "
            f"{100 * row['p_beats_random_null_trader']:.0f}% | {100 * row['c80_power']:.1f}% | "
            f"{row['c80_verdict']} | {row['robust_c80_verdict']} |")
    lines += ["", "<!-- PROSE:ASSUMPTIONS -->", ""]
    return "\n".join(lines)


if __name__ == "__main__":
    main()
