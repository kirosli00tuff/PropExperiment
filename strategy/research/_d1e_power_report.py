"""Stage D.1e Task 3: the markdown renderer for the power and sample-size run.

Split out of ``strategy/research/_d1e_power.py`` (the repo caps a file at 800
lines). The renderer reads the payload only, so it imports nothing from the
computation module; the few labels it needs travel in ``payload["meta"]``.
"""

from __future__ import annotations

from typing import Any

from strategy.research._d1e_calendar import (
    HOLDOUT2_END,
    HOLDOUT2_START,
    SUPPLY_END,
    SUPPLY_TOLERANCE,
)

# The two starts shown in section 5a-bis; the JSON carries every start.
RESOLUTION_STARTS = ("2019-05-06", "2021-01-04")


def _fmt(value: Any, digits: int = 2) -> str:
    if value is None:
        return "-"
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, int):
        return f"{value:,}"
    return f"{value:,.{digits}f}"


def render_markdown(payload: dict[str, Any]) -> str:
    meta = payload["meta"]
    eps = meta["eps_day"]
    descriptive_note = meta["descriptive_note"]
    lines: list[str] = []
    lines.append("# Stage D.1e Task 3: power and sample size for the class null")
    lines.append("")
    lines.append(
        f"Generated {meta['generated_utc']} - eps_day = {eps:g} net ticks per micro per day, "
        f"Holm family m = {meta['m']}, alpha_holm = {meta['alpha_holm']:.3e}, "
        f"z_a = {meta['z_a']:.6f}, z_b = {meta['z_b']:.6f}, z_95 = {meta['z_95']:.6f}."
    )
    lines.append(
        f"Bootstrap: mean block {meta['mean_block']:g}, K = {meta['K']}, "
        f"{meta['replications']:,} replications per length, seed base {meta['seed_base']}. "
        f"Runtime {meta['runtime_seconds']:.1f} s. VIF floor hits: {meta['floor_hits']}."
    )
    lines.append("")
    lines.append(
        "n_a = days to DETECT a true edge of eps_day with 80% power at the Holm-corrected "
        "one-sided level. n_b = days for the one-sided 95% UCB to fall below eps_day with "
        "80% probability when the true edge is zero. Holm's most stringent step (0.05/58) "
        "is used for every member, so every n_a is conservative."
    )
    lines.append("")
    lines.append(
        "Units: net ticks PER MICRO per day. Trial members are read as "
        "daily_net_ticks_per_micro, which divides each round trip by its own contract "
        "quantity (trip net / ($1.25 x trip_micros)). This corrects finding R-1 of "
        "reports/stage_d1e_adjudication.md: the earlier run divided daily dollars by $2.50, "
        "assuming 2 micros for every trial, which put every trial series at half scale and "
        "every trial sample size at a quarter of the right one. The Family H per-trade SD "
        "proxies were read off the same half-scale table and are corrected with it (200 "
        "ticks for H1-H5, 230 for H6). Statistic members are built from tick sums and were "
        "never affected."
    )
    lines.append("")
    lines.append(
        "Chosen figure: where the simulated and analytic sizes differ by more than 15%, the "
        "chosen figure is max(analytic, simulated). A simulated size BELOW the analytic one "
        "is not evidence that fewer days suffice - for a heavy-tailed member at short lengths "
        "the replicate's variance estimate is right-skewed, so the closed-form UCB "
        "under-covers there, and adopting the smaller figure would plan on an "
        "anti-conservative test. Where the simulation asks for MORE days it is used "
        "(sim_used_larger_*); where it asks for fewer it is recorded and ignored "
        "(sim_smaller_ignored_*). Both figures and the difference stay in every row."
    )
    lines.append("")
    lines.append(
        "Simulation SE: SE_hat = sqrt(gamma_0_hat(x) * VIF_boot(source) / n), with "
        "gamma_0_hat(x) the replicate's own sample variance (ddof = 1). A replicate's own "
        "lag-k autocovariance is already about (1-p)^k times the source's, so computing V_B "
        "from the replicate would attenuate the dependence term twice; the dependence factor "
        "therefore comes from the source, exactly as the analytic formula uses it."
    )
    lines.append("")

    lines.append("## 1. Supplied confirmation days (estimate, " + SUPPLY_TOLERANCE + ")")
    lines.append("")
    lines.append("| start S | weekday open dates | roll blackout | vendor degraded | days |")
    lines.append("|---|---|---|---|---|")
    for start, info in payload["supplied_days"].items():
        lines.append(
            f"| {start} | {info['weekday_open_dates']:,} | {info['roll_blackout_days']} | "
            f"{info['vendor_degraded_days']} | **{info['confirmation_days']:,}** |"
        )
    lines.append("")
    lines.append(
        f"All ranges end {SUPPLY_END}. Holdout-2 ({HOLDOUT2_START}..{HOLDOUT2_END}) supplies "
        f"**{payload['holdout2_days']:,}** trade dates by the same method."
    )
    lines.append("")

    lines.append("## 2. Per class: binding members, eps per trade, days supplied")
    lines.append("")
    header = (
        "| class | typical r (trades/day) | eps/trade | gross-equiv/trade | market cost | "
        "passive cost | binding n_a (member) | binding n_b (member) |"
    )
    lines.append(header)
    lines.append("|---|---|---|---|---|---|---|---|")
    for klass, summary in payload["classes"].items():
        lines.append(
            f"| {klass} | {_fmt(summary['typical_r'], 3)} | {_fmt(summary['eps_trade'])} | "
            f"{_fmt(summary['gross_equivalent_trade'])} | "
            f"{summary['cost_bar_market_ticks']:.2f} | "
            f"{summary['cost_bar_passive_ticks']:.2f} | {summary['binding_a']['days']:,} "
            f"({summary['binding_a']['id']}) | {summary['binding_b']['days']:,} "
            f"({summary['binding_b']['id']}) |"
        )
    lines.append("")
    starts = list(payload["supplied_days"])
    lines.append("### 2b. Days supplied at each start S against the binding n_b")
    lines.append("")
    lines.append("| class | binding n_b | " + " | ".join(starts) + " |")
    lines.append("|---" * (len(starts) + 2) + "|")
    for klass, summary in payload["classes"].items():
        cells = []
        for start in starts:
            days = summary["supplied_days"][start]
            ok = summary["null_power_achievable_at"][start]
            cells.append(f"{days:,} {'ok' if ok else 'short'}")
        lines.append(
            f"| {klass} | {summary['binding_b']['days']:,} | " + " | ".join(cells) + " |"
        )
    lines.append("")

    lines.append("## 3. Per member")
    lines.append("")
    lines.append(
        "| class | tier | member | kind | r | SD/day | lag1 | VIF_boot | eps/trade | "
        "n_a | n_b | n_a sim | n_b sim | diff a % | diff b % | chosen a | chosen b | flags |"
    )
    lines.append("|---" * 18 + "|")
    for row in payload["members"]:
        lines.append(
            f"| {row['class']} | {row['tier']} | {row['id']} | {row['kind']} | "
            f"{_fmt(row['r'], 3)} | {_fmt(row['sd_day'])} | {_fmt(row['lag1'], 3)} | "
            f"{_fmt(row['vif_boot'], 3)} | {_fmt(row['eps_trade'])} | "
            f"{row['n_a_analytic']:,} | {row['n_b_analytic']:,} | {_fmt(row['n_a_sim'], 1)} | "
            f"{_fmt(row['n_b_sim'], 1)} | {_fmt(row['diff_a_pct'], 1)} | "
            f"{_fmt(row['diff_b_pct'], 1)} | {row['chosen_a']:,} | {row['chosen_b']:,} | "
            f"{','.join(row['flags']) or '-'} |"
        )
    lines.append("")

    lines.append("## 4. Spot check: percentile bootstrap vs the closed-form SE")
    lines.append("")
    lines.append(
        "At each class's binding n_b, the same draws scored with a percentile UCB (95th "
        "percentile of an inner stationary bootstrap of the mean, B = 1,000, 200 replicates) "
        "instead of mean + 1.645 x SE. This is a check of the closed form against the "
        "percentile construction INSIDE THE BOOTSTRAP WORLD. The inner bootstrap resamples a "
        "replicate that has already been block-resampled once, so its dependence term is "
        "attenuated twice and the percentile column is biased UPWARD for an autocorrelated "
        "member. It is not a check of the absolute level of power_b, and it changes no figure."
    )
    lines.append("")
    lines.append("| class | member | n | closed-form power_b | percentile success |")
    lines.append("|---|---|---|---|---|")
    for klass, summary in payload["classes"].items():
        member_id = summary["binding_b"]["id"]
        row = next(r for r in payload["members"] if r["id"] == member_id)
        spot = row["spot_check"]
        if spot is None:
            lines.append(f"| {klass} | {member_id} | - | - | - (projected, not simulated) |")
        else:
            lines.append(
                f"| {klass} | {member_id} | {spot['n']:,} | "
                f"{spot['closed_form_power_b']:.3f} | {spot['percentile_success']:.3f} |"
            )
    lines.append("")

    lines.append(f"## 5. Descriptive extras ({descriptive_note})")
    lines.append("")
    lines.append(
        "### 5a. eps_min at each supplied-days count, for each class's binding n_b member"
    )
    lines.append("")
    per_start = " | ".join(f"{s} per day / per trade" for s in starts)
    lines.append("| class | member | " + per_start + " |")
    lines.append("|---" * (len(starts) + 2) + "|")
    for klass, summary in payload["classes"].items():
        member_id = summary["binding_b"]["id"]
        row = next(r for r in payload["members"] if r["id"] == member_id)
        cells = []
        for start in starts:
            entry = row["eps_min_at_supplied"][start]
            cells.append(f"{_fmt(entry['per_day'])} / {_fmt(entry['per_trade'])}")
        lines.append(f"| {klass} | {member_id} | " + " | ".join(cells) + " |")
    lines.append("")
    lines.append("### 5a-bis. eps_min per trade ACROSS each class, not only its binding member")
    lines.append("")
    resolution_starts = [s for s in RESOLUTION_STARTS if s in starts] or starts[:2]
    lines.append(
        "Smallest and largest per-trade eps_min over the class's measured members "
        "(C7: over its projected Family H rows - see the basis column)."
    )
    lines.append("")
    head = " | ".join(f"{s} min (member) | {s} max (member)" for s in resolution_starts)
    lines.append("| class | basis | members | " + head + " |")
    lines.append("|---" * (2 * len(resolution_starts) + 3) + "|")
    for klass, summary in payload["classes"].items():
        first = summary["resolution_range"][resolution_starts[0]]
        cells = []
        for start in resolution_starts:
            entry = summary["resolution_range"][start]
            for key in ("min_per_trade", "max_per_trade"):
                item = entry[key]
                cells.append(
                    "-" if item is None else f"{_fmt(item['value'])} ({item['member']})"
                )
        lines.append(
            f"| {klass} | {first['basis']} | {first['members']} | " + " | ".join(cells) + " |"
        )
    lines.append("")
    lines.append(
        f"### 5b. Days for a reference threshold of {meta['eps_ref_per_trade']:g} "
        "net tick per trade"
    )
    lines.append("")
    lines.append("| class | member | eps_day_ref | n_a_ref | n_b_ref |")
    lines.append("|---|---|---|---|---|")
    for klass, summary in payload["classes"].items():
        member_id = summary["binding_b"]["id"]
        row = next(r for r in payload["members"] if r["id"] == member_id)
        ref = row["eps_ref_days"]
        lines.append(
            f"| {klass} | {member_id} | {_fmt(ref['eps_day_ref'], 3)} | "
            f"{_fmt(ref['n_a'])} | {_fmt(ref['n_b'])} |"
        )
    lines.append("")
    lines.append("### 5c. n_b analytic sensitivity to eps_day, class binding members")
    lines.append("")
    eps_keys = [f"{e:g}" for e in meta["eps_sensitivity"]]
    lines.append("| class | member | " + " | ".join(eps_keys) + " |")
    lines.append("|---" * (len(eps_keys) + 2) + "|")
    for klass, summary in payload["classes"].items():
        member_id = summary["binding_b"]["id"]
        row = next(r for r in payload["members"] if r["id"] == member_id)
        cells = [f"{row['n_b_sensitivity'][k]:,}" for k in eps_keys]
        lines.append(f"| {klass} | {member_id} | " + " | ".join(cells) + " |")
    lines.append("")
    lines.append("## 6. Notes")
    lines.append("")
    for note in meta["notes"]:
        lines.append(f"- {note}")
    lines.append("")
    return "\n".join(lines)
