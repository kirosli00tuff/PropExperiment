"""Render E29_correlations.md tables from E29_correlations.json (no new numbers)."""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
W = REPO / "reports/stage_e29_briefs/work/corr"
d = json.loads((REPO / "reports/stage_e29_briefs/E29_correlations.json").read_text())
head = Path(sys.argv[1]).read_text()
L = [head.rstrip(), ""]


def table(title, block):
    L.append(f"### {title}")
    L.append("")
    L.append("| Pair | Pearson | 95% CI (Fisher z) | Spearman | Days |")
    L.append("|---|---|---|---|---|")
    for p, v in block.items():
        ci = v["pearson_ci95_fisher"]
        L.append(f"| {p} | {v['pearson']:.4f} | {ci[0]:.4f} to {ci[1]:.4f} | {v['spearman']:.4f} | {v['n_days']} |")
    L.append("")


names = {"ret": "Daily close-to-close log return (Globex day)", "range_pct": "Daily range (high - low) / close, % (Globex day)",
         "ret_main": "Main-session return, log(last close / first open) in 06:30-13:00 PT"}
L.append("## Tables, primary (early-halt dates excluded, A0 convention)")
L.append("")
for k, t in d["correlations_primary_early_halt_dates_excluded"].items():
    table(names[k], t)
L.append("## Tables, variant (all trade dates kept)")
L.append("")
for k, t in d["correlations_all_trade_dates"].items():
    table(names[k], t)
L.append("## Per-root facts (primary)")
L.append("")
L.append("| Root | Group calendar | Trade dates in window | Roll dates (dropped) | Front ids | Dates with 2+ ids | Early-halt dates excluded | n ret | n range | n main ret | SD daily ret | Median range % |")
L.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
for r, s in d["per_root_primary"].items():
    L.append(f"| {r} | {s['early_halt_calendar']} | {s['trade_dates_in_window']} | {', '.join(s['roll_dates_in_window'])} | "
             f"{len(s['front_instrument_ids_in_window'])} | {s['dates_with_two_or_more_instruments']} | "
             f"{', '.join(s['early_halt_dates_in_window_excluded'])} | {s['n_ret']} | {s['n_range']} | {s['n_ret_main']} | "
             f"{s['ret_sd_daily']:.4f} | {s['range_pct_median']:.2f} |")
L.append("")
L.append("All-dates variant counts: " + "; ".join(f"{r} n ret {v['n_ret']}, n range {v['n_range']}, n main {v['n_ret_main']}"
                                              for r, v in d["per_root_all_dates"].items()) + ".")
L.append("")
L.append("## Files opened (52; every one passed open_store's name and resolved-path guard)")
L.append("")
L.append("| Root | File (range=start_end) | Rows |")
L.append("|---|---|---|")
for f in d["files_opened"]:
    L.append(f"| {f['root']} | {f['range_start']}_{f['range_end']} | {f['rows']} |")
L.append("")
L.append("Resolved directory for every file: " + ", ".join(sorted({str(Path(f['resolved_path']).parent) for f in d['files_opened']})) + ".")
L.append("")
L.append("## Holdout status (`uv run python -m data.holdout status`, keys all_ok and unlocks_logged only)")
L.append("")
for tag in ("before", "after"):
    L.append(f"{tag.capitalize()} the data read:")
    L.append("")
    L.append("```")
    L.append((W / f"holdout_{tag}.txt").read_text().rstrip())
    L.append("```")
    L.append("")
(REPO / "reports/stage_e29_briefs/E29_correlations.md").write_text("\n".join(L) + "\n")
print("ok", len(L))
