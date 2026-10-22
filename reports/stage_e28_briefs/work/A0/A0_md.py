"""Stage E.28 A0: write A0_contract_stats.md from A0_contract_stats.json (tables generated, no hand copying)."""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
SRC = REPO / "reports/stage_e28_briefs/A0_contract_stats.json"
OUT = REPO / "reports/stage_e28_briefs/A0_contract_stats.md"
SPEC_CANDIDATES = ["MCL", "QM", "CL", "MNG", "QG", "NG", "MGC", "GC", "SIL", "SI", "MHG", "HG", "M6E",
                   "6E", "M6A", "6A", "MET", "ETH", "MBT", "BTC", "M2K", "RTY", "MYM", "YM", "MNQ", "NQ",
                   "2YY", "5YY", "10Y", "30Y", "ZT", "ZF", "ZN", "ZB", "MZC", "MZS", "MZW", "MZL", "MZM",
                   "XC", "XK", "XW", "ZC", "ZS", "ZW", "ZL", "ZM"]


def f(x, n=2):
    if x is None:
        return "-"
    return f"{x:,.{n}f}" if isinstance(x, float) else str(x)


def main() -> None:
    data = json.loads(SRC.read_text())
    roots = {r["root"]: r for r in data["roots"]}
    stats = [r for r in roots.values() if "R_d_median_ticks" in r]
    nodata = [r for r in roots.values() if "R_d_median_ticks" not in r]
    L = []
    L.append("## Table 1. Standard window 2022-11-01..2023-10-31 (regular trade dates; v_0 front contract)\n")
    L.append("| Root | Spec cand. | Tick (exch. units) | Tick USD | sigma_1m (ticks) | sigma_1m bars-only | zero-change share | R_d median (ticks) | ADV median (v_0) | Vol/min main median (mean) | Vol/min overnight median (mean) | Main vol share | Trade dates (excl. halts) |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for r in sorted(stats, key=lambda r: r["root"]):
        L.append("| {root} | {c} | {t} | {v} | {s} | {sa} | {z} | {rd} | {adv} | {vm} ({vmm}) | {vo} ({vom}) | {ms} | {n} ({x}) |".format(
            root=r["root"], c="yes" if r["root"] in SPEC_CANDIDATES else "no", t=r["tick_size_exchange_units"],
            v=r["tick_value_usd"], s=f(r["sigma_1m_ticks"]), sa=f(r["sigma_1m_consecutive_bars_only_ticks"]),
            z=f(r["sigma_1m_share_zero_changes"]), rd=f(r["R_d_median_ticks"], 1),
            adv=f(r["ADV_median_contracts_v0_front"], 0), vm=f(r["vol_per_min_main_median"], 0),
            vmm=f(r["vol_per_min_main_mean"], 1), vo=f(r["vol_per_min_overnight_median"], 0),
            vom=f(r["vol_per_min_overnight_mean"], 1), ms=f(r["main_session_volume_share"]),
            n=r["n_trade_dates"], x=len(r["early_halt_dates_excluded"])))
    L.append("")
    L.append("## Table 2. C4 big-move days (|daily log return| > 4 x that calendar year's daily SD), owned span to 2023-10-31\n")
    L.append("| Root | First trade date | Full years (>= 240 dates) | Mean per full year | Rate per 252 days, owned span | Rate per 252 days, 2019..2023-10-31 | Per year (big moves / returns) |")
    L.append("|---|---|---|---|---|---|---|")
    for r in sorted(stats, key=lambda r: r["root"]):
        py = r["c4_per_year"]
        per = ", ".join(f"{y}: {v['big_moves']}/{v['n_returns']}" for y, v in py.items())
        L.append(f"| {r['root']} | {r['c4_first_trade_date']} | {len(r['c4_full_years'])} | "
                 f"{f(r['c4_mean_per_full_year'])} | {f(r['c4_rate_per_252d_owned_span'])} | "
                 f"{f(r['c4_rate_per_252d_2019_to_2023_10_31'])} | {per} |")
    L.append("")
    L.append("## Table 3. Owned files by name (every root), tick source, pilot-window coverage by file names only\n")
    L.append("| Root | Tick source | First file start | Last file end (excl.) | Files | Files opened (end <= 2023-11-01) | Gaps in file ranges | Pilot window 2023-11-01..2024-02-29 covered by names |")
    L.append("|---|---|---|---|---|---|---|---|")
    for r in sorted(roots.values(), key=lambda r: r["root"]):
        gaps = "; ".join(f"{a}..{b}" for a, b in r["file_gaps"]) or "none"
        L.append(f"| {r['root']} | {r['tick_source'].split(' ')[0]} | {r['first_owned_file_start_date']} | "
                 f"{r['last_owned_file_end_date_exclusive']} | {r['n_files']} | {r['n_files_opened_allowed']} | "
                 f"{gaps} | {'yes (' + str(len(r['pilot_window_files_by_name'])) + ' monthly files)' if r['pilot_window_covered_by_names'] else 'no'} |")
    L.append("")
    owned_codes = set(roots)
    no_folder = [c for c in SPEC_CANDIDATES if c not in owned_codes]
    late = sorted(r["root"] for r in nodata)
    late_c = [c for c in late if c in SPEC_CANDIDATES]
    late_n = [c for c in late if c not in SPEC_CANDIDATES]
    L.append("## Candidate codes from the spec without owned window data\n")
    L.append(f"- No owned ohlcv-1m folder at all ({len(no_folder)}): {', '.join(no_folder)}.")
    L.append(f"- Owned folder, but no file ends on or before 2023-11-01 (owned files cover only 2025-04-01..2026-06-21, so no statistic here and no pilot-window file by name) ({len(late_c)} spec candidates): {', '.join(late_c)}. Non-candidate roots in the same position: {', '.join(late_n)}.")
    with_data = sorted(r["root"] for r in stats if r["root"] in SPEC_CANDIDATES)
    L.append(f"- Spec candidates with owned window statistics ({len(with_data)}): {', '.join(with_data)}.")
    L.append(f"- Owned roots with statistics that are not spec candidates: {', '.join(sorted(r['root'] for r in stats if r['root'] not in SPEC_CANDIDATES))}.")
    L.append("")
    text = OUT.read_text() if OUT.exists() else ""
    marker = "<!-- GENERATED TABLES BELOW -->"
    head = text.split(marker)[0] if marker in text else text
    OUT.write_text(head + marker + "\n\n" + "\n".join(L))
    print("wrote", OUT, len(L), "lines")


if __name__ == "__main__":
    main()
