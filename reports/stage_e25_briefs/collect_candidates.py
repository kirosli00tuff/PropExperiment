"""Stage E.25 S1 helper: collect every reader's candidates into one compact table.

Reads reports/stage_e25_briefs/{R,RD}*_*.json (schema stage_e25_reader/1) and writes
candidates_raw.md: one row per candidate with the reader's stated gross per trade in micro
ticks, the D8 (or Stage D for MES) round trip and the ratio to it. The ratio is arithmetic on
the readers' stated inputs only; the lead re-derives every shortlisted figure by hand.
Usage: python3 -I reports/stage_e25_briefs/collect_candidates.py
"""
import glob
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
# Round trip in vehicle ticks: reports/stage_e2a_costs.md (D8); MES from the Stage D model.
RT_TICKS = {
    "MNQ": 4.119, "MES": 2.03, "M2K": 3.954, "MYM": 3.983, "MCL": 3.167, "MGC": 4.086,
    "MHG": 3.701, "MNG": 5.350, "M6E": 1.922, "M6A": 2.172, "NQ": 3.110, "ZN": 1.168,
    "CL": 1.728, "GC": 4.351, "RTY": 2.359, "YM": 2.823, "ZF": 1.298, "ZT": 1.301,
    "ZB": 1.089, "UB": 1.098, "6E": 1.935, "NG": 1.672,
}
HURDLE = 1.5


def clip(text, n):
    text = " ".join(str(text or "").split())
    return text if len(text) <= n else text[: n - 1] + "~"


def ratio(row):
    micro = str(row.get("micro") or "").upper().strip()
    gross = row.get("gross_per_trade_micro_ticks")
    try:
        gross = float(gross)
    except (TypeError, ValueError):
        return micro, None, None
    rt = RT_TICKS.get(micro)
    if rt is None:
        return micro, gross, None
    return micro, gross, gross / rt


def main():
    rows, problems = [], []
    paths = sorted(glob.glob(os.path.join(HERE, "R*_*.json")))
    for path in paths:
        name = os.path.basename(path)
        try:
            with open(path) as fh:
                data = json.load(fh)
        except (OSError, json.JSONDecodeError) as exc:
            problems.append(f"{name}: unreadable ({type(exc).__name__})")
            continue
        cands = data.get("candidates") or []
        if not cands:
            problems.append(f"{name}: 0 candidates")
        for c in cands:
            micro, gross, r = ratio(c)
            rows.append((name.split("_")[0], c, micro, gross, r))
    out = [
        "# E.25 candidates as stated by readers (collect_candidates.py; lead re-derives shortlisted figures)",
        "",
        f"Files: {len(paths)}; candidates: {len(rows)}",
        "",
        "| reader | id | hypothesis | micro | gross ticks | RT ticks | ratio | clears 1.5 | grade | owned | RW testable | overlap |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for reader, c, micro, gross, r in rows:
        rt = RT_TICKS.get(micro)
        out.append(
            "| " + " | ".join([
                reader, clip(c.get("id"), 14), clip(c.get("hypothesis"), 110), micro or "-",
                "-" if gross is None else f"{gross:.2f}", "-" if rt is None else f"{rt:.3f}",
                "-" if r is None else f"{r:.2f}", "-" if r is None else ("yes" if r > HURDLE else "no"),
                clip(c.get("grade"), 24), clip(c.get("owned"), 8),
                clip(c.get("research_window_testable"), 8), clip(", ".join(c.get("overlap_ids") or []), 40),
            ]) + " |"
        )
    out += ["", "Problems:"] + [f"- {p}" for p in problems or ["none"]]
    with open(os.path.join(HERE, "candidates_raw.md"), "w") as fh:
        fh.write("\n".join(out) + "\n")
    print(f"candidates {len(rows)}; problems {len(problems)}; wrote candidates_raw.md")


if __name__ == "__main__":
    main()
