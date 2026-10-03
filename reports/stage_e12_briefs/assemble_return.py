"""Stage E.12: assemble reports/E.12_RETURN.md from return_draft.md and the stage's own files.

    python3 reports/stage_e12_briefs/assemble_return.py <END_TIME> <END_PYTEST line> <cost text file>

Tables are generated from the JSON outputs (ranking, Gate 0, quotes); the check blocks are the check
files quoted verbatim; the cost section is the cost file's text.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
B = ROOT / "reports/stage_e12_briefs"
J = lambda p: json.loads((ROOT / p).read_text())  # noqa: E731


def ranking_table() -> str:
    d = J("reports/stage_e12_ranking.json")
    take = {s["vehicle"]: s for s in d["steps"]}
    out = [f"Median vehicle ADV (YTD 2026): {d['adv_median_ytd2026']:,.0f}; headroom at start acct-1 "
           f"${d['headroom_start']['acct-1']:.6f}, acct-2 ${d['headroom_start']['acct-2']:.6f}.", "",
           "| Rank | Vehicle | Path | Cl | Tier | c $ | E\\|m_1\\| $ | c/proxy | Quote $ | Pass | Account | acct-1 / acct-2 left after (3% reserved) |",
           "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in d["ranking"]:
        s = take[r["vehicle"]]
        h = s["headroom_after"]
        out.append(f"| {r['rank']} | {r['vehicle']} | {r['path']} | {r['cluster']} | {r['tier']} | "
                   f"{r['c_usd']:.2f} | {r['sigma_proxy_usd']:.1f} | {r['c_over_sigma']:.4f} | "
                   f"{r['quote_usd']:.6f} | {s['pass']} | {s.get('account', s.get('reason', ''))} | "
                   f"{h['acct-1']:.6f} / {h['acct-2']:.6f} |")
    out.append("")
    out.append(f"Subset: all {len(d['subset'])}; total ${d['subset_total_usd']:.6f} (acct-1 "
               f"${d['per_account_usd']['acct-1']:.6f}, acct-2 ${d['per_account_usd']['acct-2']:.6f}); "
               "no skips. (Pass 1 = the seven cluster-best in rank order; pass 2 = the rest.)")
    return "\n".join(out)


def b_table() -> str:
    d = J("reports/stage_e12_gate0.json")
    bt = sorted((t for t in d["tests"] if t["family"] == "B"), key=lambda t: -t["t"])[:8]
    out = ["| Pair | Mean gross (ticks) | c (ticks) | Mean / c | t_B | p (one-sided) | Trades | Holm rank | Holm threshold | Rejected |",
           "|---|---|---|---|---|---|---|---|---|---|"]
    for t in bt:
        out.append(f"| {t['root']} {t['horizon']} | {t['mean']:.3f} | {t['cost_ticks']:.3f} | "
                   f"{t['mean'] / t['cost_ticks']:.2f} | {t['t']:.2f} | {t['p']:.2e} | {t['n_trades']} | "
                   f"{t['holm_rank']} | {t['holm_threshold']:.2e} | {t['holm_rejected']} |")
    return "\n".join(out)


def later_table() -> tuple[str, str, str]:
    h = J("reports/stage_e12_quotes_holdout2.json")["sets"]
    hs = next(iter(h.values()))
    e = J("reports/stage_e12_quotes_ext2010.json")["sets"]
    es = next(iter(e.values()))
    left = 1.609980 + 18.070270
    partial = {r: len(row["failed"]) for r, row in es["per_contract"].items() if row["failed"]}
    rows = [
        "| Item | Chunks | Quoted | Notes |", "|---|---|---|---|",
        "| Phase 2, training window of exposures not bought in phase 1 | 0 | $0.00 | none: phase 1 bought all 28 |",
        f"| Holdout-2 chunks 2024-03..2025-03, 28 price paths | {hs['chunks']} ({hs['chunks_failed']} failed) | "
        f"${hs['total_usd']:.6f} | NG's are owned and sealed (E.5); sealed on arrival if ever bought |",
        "| Research-window bars of price-path contracts not owned | 0 | $0.00 | all 28 owned since E.1 |",
        f"| 2010 extension 2010-01..2019-04, 27 price paths (MBT skipped) | {es['chunks']} "
        f"({es['chunks_failed']} unpriced, before listing) | ${es['total_usd']:.6f} | "
        f"roots with unpriced months: {partial} |",
        "",
        f"Funds left: acct-1 $1.609980, acct-2 $18.070270 (combined ${left:.6f}). Top-up needed: "
        f"holdout-2 ${max(0, hs['total_usd'] - left):.2f}; 2010 extension "
        f"${max(0, es['total_usd'] - left):.2f}; both ${max(0, hs['total_usd'] + es['total_usd'] - left):.2f}"
        " (each before the 3% margin). None is planned: Gate 0 failed."]
    return "\n".join(rows), f"${es['total_usd']:.2f}", f"${max(0, hs['total_usd'] + es['total_usd'] - left):.2f}"


def main() -> None:
    end_time, end_pytest, cost_file = sys.argv[1], sys.argv[2], Path(sys.argv[3])
    text = (B / "return_draft.md").read_text()
    later, ext_total, topup = later_table()
    fills = {
        "{{END_TIME}}": end_time, "{{END_PYTEST}}": end_pytest,
        "{{START_CHECKS}}": (B / "start_checks.txt").read_text().rstrip(),
        "{{POST_CHECKS}}": (B / "postpurchase_checks.txt").read_text().rstrip(),
        "{{END_CHECKS}}": (B / "end_checks.txt").read_text().rstrip(),
        "{{RANKING_TABLE}}": ranking_table(), "{{B_TABLE}}": b_table(), "{{LATER_TABLE}}": later,
        "{{EXT_TOTAL}}": ext_total, "{{TOPUP}}": topup,
        "{{DELEGATION}}": (B / "ret_delegation.md").read_text().rstrip(),
        "{{OPEN_CHOICES}}": (B / "ret_open_choices.md").read_text().rstrip(),
        "{{COST}}": cost_file.read_text().rstrip(),
    }
    for k, v in fills.items():
        if k not in text:
            raise SystemExit(f"placeholder {k} missing")
        text = text.replace(k, v)
    if "{{" in text:
        raise SystemExit("unfilled placeholder left")
    (ROOT / "reports/E.12_RETURN.md").write_text(text)
    print("wrote reports/E.12_RETURN.md", len(text.splitlines()), "lines")


if __name__ == "__main__":
    main()
