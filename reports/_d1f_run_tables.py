#!/usr/bin/env python3
"""Stage D.1f run tabulation.

Reads reports/stage_d1f_tier_a.json, reports/stage_d1f_tier_b.json and
reports/stage_d1f_decisions.json and writes reports/stage_d1f_run_tables.md
and reports/stage_d1f_run_tables.json. Every number is read from those three
JSON files by this script; nothing here is a hand-typed result. This script
tabulates only -- it draws no conclusions, ranks nothing, and adds no
interpretation beyond the arithmetic named in the brief (the descriptive
resolution formula).
"""
import json
import math
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS = os.path.join(REPO, "reports")

TIER_A_PATH = os.path.join(REPORTS, "stage_d1f_tier_a.json")
TIER_B_PATH = os.path.join(REPORTS, "stage_d1f_tier_b.json")
DECISIONS_PATH = os.path.join(REPORTS, "stage_d1f_decisions.json")
OUT_MD = os.path.join(REPORTS, "stage_d1f_run_tables.md")
OUT_JSON = os.path.join(REPORTS, "stage_d1f_run_tables.json")

RESOLUTION_CONST = 2.4865

CLASS_ORDER = ["C1", "C2", "C3", "C4", "C5", "C6", "C7"]


def load(path):
    with open(path, "r") as f:
        return json.load(f)


def fmt_ticks(x):
    if x is None:
        return ""
    return f"{x:.4f}"


def fmt_power(x):
    if x is None:
        return ""
    return f"{x:.4f}"


def fmt_p(x):
    if x is None:
        return ""
    if x != 0 and abs(x) < 1e-3:
        return f"{x:.3g}"
    return f"{x:.4f}"


def resolution(se_boot, activity_per_day):
    if se_boot is None or activity_per_day is None or activity_per_day == 0:
        return None
    return RESOLUTION_CONST * se_boot / activity_per_day


def main():
    tier_a = load(TIER_A_PATH)
    tier_b = load(TIER_B_PATH)
    decisions = load(DECISIONS_PATH)

    members_a = tier_a["members"]
    members_b = tier_b["members"]
    classes = decisions["classes"]
    family_decisions = decisions["family"]

    assert len(members_a) == 58, f"expected 58 Tier A members, got {len(members_a)}"
    assert len(members_b) == 43, f"expected 43 Tier B members, got {len(members_b)}"
    assert len(classes) == 7, f"expected 7 classes, got {len(classes)}"
    for c in CLASS_ORDER:
        assert c in classes, f"missing class {c}"

    out = {}

    # ---------------------------------------------------------------
    # T1: Tier A, 58 rows, grouped by class C1..C7, JSON member order
    # ---------------------------------------------------------------
    t1_rows = []
    for cls in CLASS_ORDER:
        for mid, rec in members_a.items():
            if rec.get("class") != cls:
                continue
            se_boot = rec.get("se_boot")
            act_per_day = rec.get("activity_per_day")
            res = resolution(se_boot, act_per_day)
            holm = rec.get("holm") or {}
            acct = rec.get("accounting") or {}
            per_trade = rec.get("per_trade") or {}
            null = rec.get("null") or {}
            row = {
                "id": mid,
                "class": rec.get("class"),
                "kind": rec.get("kind"),
                "n_days": rec.get("n_days"),
                "n_activity": rec.get("n_activity"),
                "activity_per_day": rec.get("activity_per_day"),
                "theta_hat": rec.get("theta_hat"),
                "ucb95": rec.get("ucb95"),
                "se_boot": se_boot,
                "achieved_power": null.get("achieved_power"),
                "p_one_sided": rec.get("p_one_sided"),
                "holm_rank": holm.get("rank"),
                "holm_threshold": holm.get("threshold"),
                "holm_reject": holm.get("reject"),
                "composite": rec.get("composite"),
                "t_stat": acct.get("t_stat"),
                "dsr_n58": acct.get("dsr_n58"),
                "status": rec.get("status"),
                "labels": list(rec.get("labels") or []),
                "theta_hat_per_trade": per_trade.get("theta_hat"),
                "ucb95_per_trade": per_trade.get("ucb95"),
                "resolution_per_trade": res,
            }
            t1_rows.append(row)
    out["t1_tier_a"] = t1_rows

    # ---------------------------------------------------------------
    # T2: Tier B, 43 rows, grouped by class, JSON member order
    # ---------------------------------------------------------------
    t2_rows = []
    for cls in CLASS_ORDER:
        for mid, rec in members_b.items():
            if rec.get("class") != cls:
                continue
            se_boot = rec.get("se_boot")
            act_per_day = rec.get("activity_per_day")
            res = resolution(se_boot, act_per_day)
            null = rec.get("null") or {}
            per_trade = rec.get("per_trade") or {}
            anomaly = rec.get("anomaly") or {}
            anomaly_bh = anomaly.get("bh") or {}
            reversal = rec.get("sign_reversal") or {}
            reversal_bh = reversal.get("bh") or {}
            row = {
                "id": mid,
                "class": rec.get("class"),
                "n_days": rec.get("n_days"),
                "n_events": rec.get("n_activity"),
                "events_per_day": rec.get("activity_per_day"),
                "theta_hat": rec.get("theta_hat"),
                "ucb95": rec.get("ucb95"),
                "se_boot": se_boot,
                "achieved_power": null.get("achieved_power"),
                "p_one_sided": rec.get("p_one_sided"),
                "anomaly_bh_reject": anomaly_bh.get("reject"),
                "net_edge_per_event": anomaly.get("net_edge_per_event"),
                "anomaly_flag": anomaly.get("flag"),
                "gross_per_event": reversal.get("gross_per_event"),
                "p_gross_below_0": reversal.get("p_one_sided_gross_below_0"),
                "reversal_bh_reject": reversal_bh.get("reject"),
                "reversal_flag": reversal.get("flag"),
                "status": rec.get("status"),
                "labels": list(rec.get("labels") or []),
                "ucb95_per_event": per_trade.get("ucb95"),
                "resolution_per_event": res,
            }
            t2_rows.append(row)
    out["t2_tier_b"] = t2_rows

    # ---------------------------------------------------------------
    # T3: classes
    # ---------------------------------------------------------------
    def member_lookup(mid):
        if mid in members_a:
            return "A", members_a[mid]
        if mid in members_b:
            return "B", members_b[mid]
        return None, None

    t3_rows = []
    for cls in CLASS_ORDER:
        info = classes[cls]
        mem_ids = info.get("members", [])
        n_a = sum(1 for m in mem_ids if m in members_a)
        n_b = sum(1 for m in mem_ids if m in members_b)
        res_candidates = []
        for mid in mem_ids:
            tier, rec = member_lookup(mid)
            if rec is None:
                continue
            act_per_day = rec.get("activity_per_day")
            if not act_per_day:
                continue
            se_boot = rec.get("se_boot")
            res = resolution(se_boot, act_per_day)
            if res is not None:
                res_candidates.append((res, mid))
        res_min = min(res_candidates, key=lambda t: t[0]) if res_candidates else None
        res_max = max(res_candidates, key=lambda t: t[0]) if res_candidates else None
        sf = info.get("statement_fields", {})
        row = {
            "class": cls,
            "verdict": info.get("verdict"),
            "n_members_tier_a": n_a,
            "n_members_tier_b": n_b,
            "n_members_total": len(mem_ids),
            "members_not_meeting_null": list(info.get("members_not_meeting_null", [])),
            "inconclusive_members": list(info.get("inconclusive", [])),
            "passing_members": list(info.get("passing_confirmation", [])),
            "class_frequency_trades_per_day": sf.get("class_frequency_trades_per_day"),
            "class_frequency_definition": sf.get("class_frequency_definition"),
            "epsilon_per_trade": sf.get("epsilon_per_trade"),
            "least_active_member": sf.get("least_active_member"),
            "largest_per_trade_ucb95": sf.get("largest_per_trade_ucb95"),
            "null_by_inactivity_members": list(sf.get("null_by_inactivity_members", [])),
            "label": sf.get("label"),
            "descriptive_resolution_min": {
                "value": res_min[0] if res_min else None,
                "member": res_min[1] if res_min else None,
            },
            "descriptive_resolution_max": {
                "value": res_max[0] if res_max else None,
                "member": res_max[1] if res_max else None,
            },
        }
        t3_rows.append(row)
    out["t3_classes"] = t3_rows

    # ---------------------------------------------------------------
    # T4: family accounting (from decisions.json "family")
    # ---------------------------------------------------------------
    fam = family_decisions
    dsr58 = fam.get("dsr_n58", {})
    dsr58_dsr = dsr58.get("dsr", {})
    dsr58_gt = sorted([mid for mid, v in dsr58_dsr.items() if v is not None and v > 0.95])
    dsr101 = fam.get("reported_dsr_n101", {})
    dsr101_dsr = dsr101.get("dsr", {})
    dsr101_gt = sorted([mid for mid, v in dsr101_dsr.items() if v is not None and v > 0.95])
    dsr186 = fam.get("reported_dsr_n186", {})
    dsr186_dsr = dsr186.get("dsr", {})
    dsr186_gt = sorted([mid for mid, v in dsr186_dsr.items() if v is not None and v > 0.95])

    out["t4_family"] = {
        "n_trials": fam.get("n_trials"),
        "dsr_n58": {
            "sharpe_variance": dsr58.get("sharpe_variance"),
            "expected_max_daily_sharpe_under_null": dsr58.get(
                "expected_max_daily_sharpe_under_null"
            ),
            "variance_over_n_members": dsr58.get("variance_over_n_members"),
            "n_trials": dsr58.get("n_trials"),
            "n_members_dsr_gt_0_95": len(dsr58_gt),
            "members_dsr_gt_0_95": dsr58_gt,
        },
        "pbo_n58": fam.get("pbo_n58"),
        "reported_dsr_n101": {
            "sharpe_variance": dsr101.get("sharpe_variance"),
            "expected_max_daily_sharpe_under_null": dsr101.get(
                "expected_max_daily_sharpe_under_null"
            ),
            "variance_over_n_members": dsr101.get("variance_over_n_members"),
            "n_trials": dsr101.get("n_trials"),
            "n_members_dsr_gt_0_95": len(dsr101_gt),
            "members_dsr_gt_0_95": dsr101_gt,
        },
        "reported_pbo_n101": fam.get("reported_pbo_n101"),
        "reported_dsr_n186": {
            "sharpe_variance": dsr186.get("sharpe_variance"),
            "expected_max_daily_sharpe_under_null": dsr186.get(
                "expected_max_daily_sharpe_under_null"
            ),
            "variance_over_n_members": dsr186.get("variance_over_n_members"),
            "n_trials": dsr186.get("n_trials"),
            "n_members_dsr_gt_0_95": len(dsr186_gt),
            "members_dsr_gt_0_95": dsr186_gt,
        },
        "holm": fam.get("holm"),
        "tier_b_bh": fam.get("tier_b_bh"),
        "window_n_days": fam.get("window_n_days"),
        "alignment": fam.get("alignment"),
    }

    # ---------------------------------------------------------------
    # T5: year slices, one row per member per calendar year
    # ---------------------------------------------------------------
    t5_rows = []
    for tier_label, members in (("A", members_a), ("B", members_b)):
        for mid, rec in members.items():
            ys = rec.get("year_slices") or {}
            for year in sorted(ys.keys()):
                yv = ys[year]
                t5_rows.append(
                    {
                        "id": mid,
                        "tier": tier_label,
                        "class": rec.get("class"),
                        "year": year,
                        "n_days": yv.get("n_days"),
                        "activity": yv.get("activity"),
                        "theta_hat": yv.get("theta_hat"),
                        "ucb95": yv.get("ucb95"),
                    }
                )
    out["t5_year_slices"] = t5_rows

    # ---------------------------------------------------------------
    # T6: counts
    # ---------------------------------------------------------------
    status_counts = {}
    label_counts = {}
    for tier_label, members in (("A", members_a), ("B", members_b)):
        for mid, rec in members.items():
            cls = rec.get("class")
            status = rec.get("status")
            key = (cls, tier_label, status)
            status_counts[key] = status_counts.get(key, 0) + 1
            for lab in rec.get("labels") or []:
                lkey = (tier_label, lab)
                label_counts[lkey] = label_counts.get(lkey, 0) + 1

    t6_status_rows = [
        {"class": cls, "tier": tier, "status": status, "count": count}
        for (cls, tier, status), count in sorted(status_counts.items())
    ]
    t6_label_rows = [
        {"tier": tier, "label": lab, "count": count}
        for (tier, lab), count in sorted(label_counts.items())
    ]
    out["t6_counts"] = {
        "by_class_tier_status": t6_status_rows,
        "by_label": t6_label_rows,
    }

    # ---------------------------------------------------------------
    # Write JSON
    # ---------------------------------------------------------------
    with open(OUT_JSON, "w") as f:
        json.dump(out, f, indent=2, sort_keys=False)

    # ---------------------------------------------------------------
    # Write Markdown
    # ---------------------------------------------------------------
    lines = []
    lines.append("# Stage D.1f run tables")
    lines.append("")
    lines.append(
        "Generated by reports/_d1f_run_tables.py from "
        "reports/stage_d1f_tier_a.json, reports/stage_d1f_tier_b.json and "
        "reports/stage_d1f_decisions.json. Ticks are net ticks per micro per "
        "day unless stated otherwise. No number here is hand-typed."
    )
    lines.append("")

    # T1
    lines.append("## T1: Tier A (58 rows, grouped by class)")
    lines.append("")
    header = [
        "id", "class", "kind", "n_days", "n_activity", "activity/day",
        "theta_hat", "UCB95", "SE_boot", "power", "p", "Holm rank",
        "Holm thresh", "Holm reject", "composite", "t", "DSR(N=58)",
        "status", "labels", "theta/trade", "UCB95/trade", "resolution/trade",
    ]
    lines.append("| " + " | ".join(header) + " |")
    lines.append("|" + "---|" * len(header))
    for r in t1_rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    str(r["id"]),
                    str(r["class"]),
                    str(r["kind"]),
                    str(r["n_days"]),
                    str(r["n_activity"]),
                    fmt_ticks(r["activity_per_day"]),
                    fmt_ticks(r["theta_hat"]),
                    fmt_ticks(r["ucb95"]),
                    fmt_ticks(r["se_boot"]),
                    fmt_power(r["achieved_power"]),
                    fmt_p(r["p_one_sided"]),
                    str(r["holm_rank"]),
                    fmt_p(r["holm_threshold"]),
                    str(r["holm_reject"]),
                    str(r["composite"]),
                    fmt_ticks(r["t_stat"]),
                    fmt_ticks(r["dsr_n58"]),
                    str(r["status"]),
                    ";".join(r["labels"]),
                    fmt_ticks(r["theta_hat_per_trade"]),
                    fmt_ticks(r["ucb95_per_trade"]),
                    fmt_ticks(r["resolution_per_trade"]),
                ]
            )
            + " |"
        )
    lines.append("")

    # T2
    lines.append("## T2: Tier B (43 rows, grouped by class)")
    lines.append("")
    header = [
        "id", "class", "n_days", "n_events", "events/day", "theta_hat",
        "UCB95", "SE_boot", "power", "p", "anomaly BH reject",
        "net edge/event", "anomaly flag", "gross/event", "p gross<0",
        "reversal BH reject", "reversal flag", "status", "labels",
        "UCB95/event", "resolution/event",
    ]
    lines.append("| " + " | ".join(header) + " |")
    lines.append("|" + "---|" * len(header))
    for r in t2_rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    str(r["id"]),
                    str(r["class"]),
                    str(r["n_days"]),
                    str(r["n_events"]),
                    fmt_ticks(r["events_per_day"]),
                    fmt_ticks(r["theta_hat"]),
                    fmt_ticks(r["ucb95"]),
                    fmt_ticks(r["se_boot"]),
                    fmt_power(r["achieved_power"]),
                    fmt_p(r["p_one_sided"]),
                    str(r["anomaly_bh_reject"]),
                    fmt_ticks(r["net_edge_per_event"]),
                    str(r["anomaly_flag"]),
                    fmt_ticks(r["gross_per_event"]),
                    fmt_p(r["p_gross_below_0"]),
                    str(r["reversal_bh_reject"]),
                    str(r["reversal_flag"]),
                    str(r["status"]),
                    ";".join(r["labels"]),
                    fmt_ticks(r["ucb95_per_event"]),
                    fmt_ticks(r["resolution_per_event"]),
                ]
            )
            + " |"
        )
    lines.append("")

    # T3
    lines.append("## T3: Classes C1..C7")
    lines.append("")
    for r in t3_rows:
        lines.append(f"### {r['class']}")
        lines.append("")
        lines.append(f"- verdict: {r['verdict']}")
        lines.append(
            f"- members: {r['n_members_total']} total "
            f"(Tier A {r['n_members_tier_a']}, Tier B {r['n_members_tier_b']})"
        )
        lines.append(
            f"- members not meeting the null ({len(r['members_not_meeting_null'])}): "
            f"{r['members_not_meeting_null']}"
        )
        lines.append(
            f"- inconclusive members ({len(r['inconclusive_members'])}): "
            f"{r['inconclusive_members']}"
        )
        lines.append(
            f"- passing members ({len(r['passing_members'])}): "
            f"{r['passing_members']}"
        )
        lines.append(
            f"- class frequency: {fmt_ticks(r['class_frequency_trades_per_day'])} "
            f"trades/day ({r['class_frequency_definition']})"
        )
        lines.append(f"- epsilon per trade: {fmt_ticks(r['epsilon_per_trade'])}")
        lines.append(f"- least active member: {r['least_active_member']}")
        lines.append(f"- largest per-trade UCB95: {r['largest_per_trade_ucb95']}")
        lines.append(
            f"- null-by-inactivity members ({len(r['null_by_inactivity_members'])}): "
            f"{r['null_by_inactivity_members']}"
        )
        lines.append(f"- label: {r['label']}")
        rmin = r["descriptive_resolution_min"]
        rmax = r["descriptive_resolution_max"]
        lines.append(
            "- descriptive resolution range (2.4865 x SE_boot / activity_per_day, "
            "members with activity > 0): "
            f"min {fmt_ticks(rmin['value'])} ({rmin['member']}), "
            f"max {fmt_ticks(rmax['value'])} ({rmax['member']})"
        )
        lines.append("")

    # T4
    lines.append("## T4: Family accounting (decisions.json \"family\")")
    lines.append("")
    f4 = out["t4_family"]
    lines.append(f"- n_trials: {f4['n_trials']}")
    lines.append("")
    lines.append("### DSR at N=58")
    d58 = f4["dsr_n58"]
    lines.append(f"- sharpe_variance: {fmt_ticks(d58['sharpe_variance'])}")
    lines.append(
        f"- expected_max_daily_sharpe_under_null: "
        f"{fmt_ticks(d58['expected_max_daily_sharpe_under_null'])}"
    )
    lines.append(f"- variance_over_n_members: {fmt_ticks(d58['variance_over_n_members'])}")
    lines.append(f"- n_trials: {d58['n_trials']}")
    lines.append(
        f"- members with DSR > 0.95 ({d58['n_members_dsr_gt_0_95']}): "
        f"{d58['members_dsr_gt_0_95']}"
    )
    lines.append("")
    lines.append("### PBO at N=58")
    lines.append(f"- {f4['pbo_n58']}")
    lines.append("")
    lines.append("### Reported DSR at N=101")
    d101 = f4["reported_dsr_n101"]
    lines.append(f"- sharpe_variance: {fmt_ticks(d101['sharpe_variance'])}")
    lines.append(
        f"- expected_max_daily_sharpe_under_null: "
        f"{fmt_ticks(d101['expected_max_daily_sharpe_under_null'])}"
    )
    lines.append(f"- variance_over_n_members: {fmt_ticks(d101['variance_over_n_members'])}")
    lines.append(f"- n_trials: {d101['n_trials']}")
    lines.append(
        f"- members with DSR > 0.95 ({d101['n_members_dsr_gt_0_95']}): "
        f"{d101['members_dsr_gt_0_95']}"
    )
    lines.append("")
    lines.append("### Reported PBO at N=101")
    lines.append(f"- {f4['reported_pbo_n101']}")
    lines.append("")
    lines.append("### Reported DSR at N=186")
    d186 = f4["reported_dsr_n186"]
    lines.append(f"- sharpe_variance: {fmt_ticks(d186['sharpe_variance'])}")
    lines.append(
        f"- expected_max_daily_sharpe_under_null: "
        f"{fmt_ticks(d186['expected_max_daily_sharpe_under_null'])}"
    )
    lines.append(f"- variance_over_n_members: {fmt_ticks(d186['variance_over_n_members'])}")
    lines.append(f"- n_trials: {d186['n_trials']}")
    lines.append(
        f"- members with DSR > 0.95 ({d186['n_members_dsr_gt_0_95']}): "
        f"{d186['members_dsr_gt_0_95']}"
    )
    lines.append("")
    lines.append(f"### Holm: {f4['holm']}")
    lines.append(f"### tier_b_bh: {f4['tier_b_bh']}")
    lines.append(f"### window_n_days: {f4['window_n_days']}")
    lines.append(f"### alignment: {f4['alignment']}")
    lines.append("")

    # T5
    lines.append("## T5: Year slices (one row per member per calendar year)")
    lines.append("")
    header = ["id", "tier", "class", "year", "n_days", "activity", "theta_hat", "UCB95"]
    lines.append("| " + " | ".join(header) + " |")
    lines.append("|" + "---|" * len(header))
    for r in t5_rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    str(r["id"]),
                    str(r["tier"]),
                    str(r["class"]),
                    str(r["year"]),
                    str(r["n_days"]),
                    str(r["activity"]),
                    fmt_ticks(r["theta_hat"]),
                    fmt_ticks(r["ucb95"]),
                ]
            )
            + " |"
        )
    lines.append("")

    # T6
    lines.append("## T6: Counts")
    lines.append("")
    lines.append("### Members by status per class and tier")
    lines.append("")
    header = ["class", "tier", "status", "count"]
    lines.append("| " + " | ".join(header) + " |")
    lines.append("|" + "---|" * len(header))
    for r in t6_status_rows:
        lines.append(
            "| "
            + " | ".join([str(r["class"]), str(r["tier"]), str(r["status"]), str(r["count"])])
            + " |"
        )
    lines.append("")
    lines.append("### Counts of each label")
    lines.append("")
    header = ["tier", "label", "count"]
    lines.append("| " + " | ".join(header) + " |")
    lines.append("|" + "---|" * len(header))
    for r in t6_label_rows:
        lines.append(
            "| " + " | ".join([str(r["tier"]), str(r["label"]), str(r["count"])]) + " |"
        )
    lines.append("")

    with open(OUT_MD, "w") as f:
        f.write("\n".join(lines) + "\n")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"T1 rows: {len(t1_rows)} (expect 58)")
    print(f"T2 rows: {len(t2_rows)} (expect 43)")
    print(f"T3 rows: {len(t3_rows)} (expect 7)")
    print(f"T5 rows: {len(t5_rows)}")


if __name__ == "__main__":
    main()
