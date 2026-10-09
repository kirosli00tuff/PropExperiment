"""Calendar-only reports (no bar is read): the power table and the release-touch list.

    uv run python -m base_rules.report counts --out-json <power_table.json> --out-md <.md>
    uv run python -m base_rules.report release-touch --out-md <release_touch.md>

Inputs (paths as options; defaults are the repository paths): Task 1's settlement table, U2's
windows file, the EC-AUC 2010-2019 rows, the hist calendars, and Task 3b's livestock calendar.
When the livestock calendar is not on disk, ``--livestock provisional`` builds a PROVISIONAL one
(the grains hist file's full closures and early halts, livestock products, one 08:00-13:05 CT
segment) in a scratch directory, never under data/, and every output says so.
"""

from __future__ import annotations

import argparse
import json
import tempfile
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from base_rules import constants as K
from base_rules.auctions import load_auctions
from base_rules.calendars import GroupCalendars, load_hist
from base_rules.context import empty_release_rules, make_context
from base_rules.counts import CYCLES, calendar_counts
from base_rules.inputs import load_settlement, load_windows, read_json
from base_rules.power import N_SIM, PRIORS, power_table
from base_rules.touch import release_touch
from data.group_session import load_group_calendar


def provisional_livestock(out_dir: Path) -> Path:
    raw, _ = read_json(K.repo_path(K.HIST_CALENDAR_DIR / "grains.json"))
    raw = {**raw, "group": "livestock", "products": ["HE", "LE"],
           "entries": [e for e in raw["entries"] if e["kind"] in ("full_closure", "early_halt")],
           "no_entry_findings": [], "unsourced": [],
           "sessions": [{"valid_from": "2010-06-01", "valid_to": "2019-05-31",
                         "segments": [{"start_offset_days": 0, "start_ct": "08:00",
                                       "end_offset_days": 0, "end_ct": "13:05"}],
                         "day_session_ct": {"HE": ["08:30", "13:00"], "LE": ["08:30", "13:00"]},
                         "evidence": "secondary", "source": "PROVISIONAL", "note": "E.16 coder"}]}
    path = Path(out_dir) / "hist2010_livestock_PROVISIONAL.json"
    path.write_text(json.dumps(raw))
    return path


def build(a: argparse.Namespace, scratch: Path):  # noqa: ANN201
    livestock = Path(a.livestock) if a.livestock != "provisional" else provisional_livestock(
        scratch)
    cals = {}
    for g in sorted(set(K.GROUP_OF.values())):
        hist = load_hist(g, livestock_path=livestock)
        cals[g] = GroupCalendars(g, hist, load_group_calendar(g))
    st = load_settlement(Path(a.settlement))
    windows = load_windows(Path(a.windows))
    auctions, rec = load_auctions(Path(a.ecauc), announcements_path=Path(a.announcements))
    return cals, st, windows, auctions, rec, livestock


def _inputs(a, st, rec, livestock) -> dict:  # noqa: ANN001
    from base_rules.guards import sha256_file

    return {"settlement": [str(a.settlement), st.sha256],
            "windows": [str(a.windows), sha256_file(K.repo_path(a.windows))],
            "ecauc": rec, "livestock_calendar": [str(livestock), sha256_file(livestock)],
            "provisional_livestock": a.livestock == "provisional"}


def cmd_counts(a: argparse.Namespace) -> int:
    with tempfile.TemporaryDirectory(dir=a.scratch) as tmp:
        cals, st, windows, auctions, rec, livestock = build(a, Path(tmp))
        counts = {}
        for window in ("full", "fallback"):
            starts = windows if window == "full" else {p: max(K.FALLBACK_FIRST, windows[p])
                                                       for p in K.PRODUCTS}
            ctx = make_context(cals, st, starts, lambda p: None, tuple(auctions),
                               empty_release_rules())
            counts[window] = calendar_counts(ctx)
        table = power_table({w: counts[w] for w in counts}, n_sim=a.n_sim)
        header = {"schema": "stage_e16_power_table/1", "provisional": a.livestock == "provisional",
                  "written_local": datetime.now(ZoneInfo("America/Vancouver")).isoformat(
                      timespec="seconds"),
                  "inputs": _inputs(a, st, rec, livestock), "cycles_assumed": CYCLES}
    out = {**header, "power": table, "calendar_only_counts": counts}
    Path(a.out_json).write_text(json.dumps(out, indent=1, default=str) + "\n")
    Path(a.out_md).write_text(power_md(out))
    print(f"power table -> {a.out_json}, {a.out_md}")
    return 0


def power_md(out: dict) -> str:
    lines = ["# Stage E.16 Task 3: power table (calendar-only counts)", ""]
    if out["provisional"]:
        lines += ["**PROVISIONAL**: Task 3b's livestock 2010-2019 calendar was not on disk; LE and "
                  "HE use a stand-in (the grains hist file's closures and early halts, one "
                  "08:00-13:05 CT segment). The lead reruns `python -m base_rules.report counts` "
                  "with the real file.", ""]
    lines += [f"Written {out['written_local']}. Seed {out['power']['seed']}, "
              f"{out['power']['n_sim']} simulations per cell. Priors (net Sharpe, annual): "
              + ", ".join(f"{t} {lo}-{hi}" for t, (lo, hi) in PRIORS.items()) + ".", "",
              "Pass = p <= threshold (the larger of plain-t and Newey-West p), mean > 0, n >= 30 "
              "and year stability; 0.01 is Holm's first step (0.05/5), 0.05 its last. "
              "Analytic = one-sided t power at the same threshold (noncentral t).", "",
              "| window | test | prior | SR | units | units/yr | SR/unit | qual. yrs | "
              "pass@0.01 | pass@0.05 | analytic@0.01 | analytic@0.05 |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in out["power"]["rows"]:
        sim, an = r.get("sim_pass_all_bars", {}), r.get("analytic_t_power") or {}
        lines.append(f"| {r['window']} | {r['test']} | {r['prior']} | {r['sr_annual']} | "
                     f"{r['n_units']} | {r.get('units_per_full_year', 0):.1f} | "
                     f"{r.get('sr_unit', 0):.4f} | {r.get('qualifying_years', 0)} | "
                     f"{sim.get('0.01', 0):.3f} | {sim.get('0.05', 0):.3f} | "
                     f"{an.get('0.01', 0):.3f} | {an.get('0.05', 0):.3f} |")
    lines += ["", "## Calendar-only unit counts per year (after warm-up)", ""]
    for window, per in out["calendar_only_counts"].items():
        for test in K.TESTS:
            lines.append(f"- {window} {test}: {per[test]['units_per_year']}")
    lines += ["", "## Exclusions (calendar-only, per test)", ""]
    for window, per in out["calendar_only_counts"].items():
        for test in K.INTRADAY_TESTS:
            tot: dict[str, int] = {}
            for v in per[test]["per_key"].values():
                for k, n in v["exclusions"].items():
                    tot[k] = tot.get(k, 0) + n
            lines.append(f"- {window} {test} (product-dates): {dict(sorted(tot.items()))}")
        for test in ("H2", "H3"):
            lines.append(f"- {window} {test}: {per[test]['exclusions']}")
    lines += ["", "## Assumptions", "",
              "- Roll blackout: 3 trade dates per ESTIMATED splice (the splice and the two "
              "before), "
              "splices from each product's full listed cycle (`cycles_assumed`, an upper bound on "
              "the volume roll's count): equity and FX on the contract month's third Friday minus "
              "8 days, every other product on the 5th-last trade date of the month before each "
              "listed month. The run uses the stores' real roll metadata.",
              "- Early halts, unsourced dates, open intervals: the frozen calendars; a required "
              "minute outside the trade date's open intervals is `missing bar (calendar)`.",
              "- Missing bars inside the session: 0. Zero signals: 0 (not knowable without bars).",
              "- Per-unit returns i.i.d. normal; SR/unit = SR annual / sqrt(units per full year)."
              , ""]
    return "\n".join(lines) + "\n"


def cmd_touch(a: argparse.Namespace) -> int:
    with tempfile.TemporaryDirectory(dir=a.scratch) as tmp:
        cals, st, windows, auctions, rec, livestock = build(a, Path(tmp))
        ctx = make_context(cals, st, windows, lambda p: None, tuple(auctions),
                           empty_release_rules())
        rep = release_touch(ctx)
    lines = ["# Stage E.16 Task 3: release types touching an H fill minute", "",
             f"From the frozen release calendar alone ({rep['frozen_calendar']['path']}, sha256 "
             f"{rep['frozen_calendar']['sha256']}, {rep['frozen_calendar']['rows']} rows "
             "2019-05-01..2024-02-29). A fill at f is touched when r <= f < r + 30 min (D8 event "
             "cost) for a release r concerning the product (price-path or vehicle root); "
             "`guard` counts fills inside r <= f < r + 2 min (D9.5a). Fill minutes: H1 S-30 and "
             "S, H4 O+1 and S-31 (every trade date), H2 the decision minute on d5 and S on dL, H3 "
             "S on t-3, t, t+5 (kept windows), and every calendar date's 23:59 and 00:00 UTC bar "
             "of NQ, ZN, ZT, ZF, ZB (a superset of the roll fills). Settlement minutes from "
             f"{a.settlement}.", ""]
    if a.livestock == "provisional":
        lines += ["Livestock calendar: PROVISIONAL stand-in (Task 3b's file not on disk); it only "
                  "decides which LE/HE dates are trade dates.", ""]
    lines += ["| type | event fills | guard fills | tests | products | CT clock times | rows "
              "before 2019-05 | fallback applies |", "|---|---|---|---|---|---|---|---|"]
    for k, v in rep["types"].items():
        lines.append(f"| {k} | {v['event_fills']} | {v['guard_fills']} | {', '.join(v['tests'])} "
                     f"| {', '.join(v['products'])} | {', '.join(v['clock_times_ct'])} | "
                     f"{'yes' if v['rows_2010_2019'] else 'no'} | "
                     f"{'no' if v['rows_2010_2019'] else 'YES'} |")
    lines += ["", f"Types that never touch an H fill minute: {', '.join(rep['not_touching'])}.",
              "", "Examples (first three per type):", ""]
    lines += [f"- {k}: {'; '.join(v['examples'])}" for k, v in rep["types"].items()]
    Path(a.out_md).write_text("\n".join(lines) + "\n")
    if a.out_json:
        Path(a.out_json).write_text(json.dumps(rep, indent=1, default=str))
    print(f"release touch -> {a.out_md}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="base_rules.report")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("counts", "release-touch"):
        p = sub.add_parser(name)
        p.add_argument("--settlement", default=str(K.SETTLEMENT_PATH))
        p.add_argument("--windows", default=str(K.WINDOWS_PATH))
        p.add_argument("--ecauc", default=str(K.ECAUC_HIST_PATH))
        p.add_argument("--announcements", default=str(K.ANNOUNCEMENTS_PATH))
        p.add_argument("--livestock", default=str(K.LIVESTOCK_HIST_PATH),
                       help="a path, or 'provisional'")
        p.add_argument("--scratch", default=None)
        p.add_argument("--out-md", required=True)
        p.add_argument("--out-json", required=name == "counts")
        if name == "counts":
            p.add_argument("--n-sim", type=int, default=N_SIM)
    a = ap.parse_args(argv)
    return cmd_counts(a) if a.cmd == "counts" else cmd_touch(a)


if __name__ == "__main__":
    raise SystemExit(main())
