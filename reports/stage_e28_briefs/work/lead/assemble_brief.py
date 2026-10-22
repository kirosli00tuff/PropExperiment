"""Assemble reports/stage_e28_methods_brief.md from the lead's front matter, C1, the C2 deep dives, C3 and C4.

Deep dives are included verbatim with headings demoted, so the brief is self-contained. The verdict tables of each
deep dive are also collected into one summary table. Run from the repo root.
"""
import re
from pathlib import Path

B = Path("reports/stage_e28_briefs")
OUT = Path("reports/stage_e28_methods_brief.md")
C2 = [("SDE", "Stochastic calculus and continuous-time models (Ito, jump-diffusions, OU)"),
      ("Hawkes", "Point processes: Poisson and Hawkes order arrivals"),
      ("LOB", "Limit-order-book models and the mathematics of fill probability"),
      ("Control", "Stochastic optimal control, HJB, market making and execution"),
      ("Filter", "Filtering: Kalman, particle filters, hidden Markov regimes"),
      ("StatsRMT", "Random-matrix cleaning, Bayesian shrinkage, information theory"),
      ("AFML", "Fractional differencing, meta-labeling, purged CV, wavelets and spectral methods"),
      ("DeepLOB", "Machine learning on order-book data I: deep models"),
      ("OFI", "Machine learning on order-book data II: order-flow imbalance, trees, labels, latency"),
      ("Pooled", "Single-contract versus pooled multi-contract models"),
      ("Firms", "How top firms run the research process")]


def demote(text, by):
    def rep(m):
        n = min(6, len(m.group(1)) + by)
        return "#" * n + " "
    return re.sub(r"^(#{1,6}) ", rep, text, flags=re.M)


def verdict_rows(text):
    lines = text.splitlines()
    starts = [i for i, l in enumerate(lines) if re.match(r"^## .*[Vv]erdict", l)]
    if not starts:
        return []
    rows = []
    for l in lines[starts[-1] + 1:]:
        if l.startswith("## "):
            break
        if l.startswith("|") and not re.match(r"^\|\s*-", l) and not re.match(r"^\|\s*[Mm]ethod\s*\|", l):
            rows.append(l)
    return rows


def n_sources(key):
    p = B / "pages" / f"C2_{key}" / "log.tsv"
    if not p.exists():
        return 0
    return sum(1 for l in p.read_text(errors="replace").splitlines() if l.strip() and not l.lower().startswith("url"))


def main():
    parts = [(B / "work/lead/C0_front.md").read_text()]
    total_src = 0
    summary = ["| Deep dive | Method | Verdict | Reason (abridged by the deep dive) |", "|---|---|---|---|"]
    for key, title in C2:
        txt = (B / f"C2_{key}.md").read_text()
        total_src += n_sources(key)
        for r in verdict_rows(txt):
            cells = [c.strip() for c in r.strip().strip("|").split("|")]
            if len(cells) >= 3:
                summary.append(f"| {key} | {cells[0]} | {cells[1]} | {' '.join(cells[2:])} |")
    parts.append("## Part 1 (C1). Gap inventory\n\nThe inventory below is C1's file reports/stage_e28_briefs/"
                 "C1_inventory.md, included verbatim (headings demoted).\n\n"
                 + demote((B / "C1_inventory.md").read_text(), 2))
    parts.append("## Part 2 (C2). Deep dives on the methods the program never used\n\n"
                 f"Eleven deep dives by independent readers (opus, high effort), {total_src} fetched sources logged with "
                 "sha256 under reports/stage_e28_briefs/pages/C2_<KEY>/log.tsv. Each is included verbatim (headings "
                 "demoted). Every equation and evidence claim was checked by MathReviewer-FableXHigh; see Part 5.\n\n"
                 "### 2.0 All verdicts in one table\n\nCollected mechanically from each deep dive's verdict section "
                 "(C2_Firms has no verdict table; its sections 3 and 4 carry the recommendations).\n\n"
                 + "\n".join(summary) + "\n")
    for i, (key, title) in enumerate(C2, 1):
        txt = (B / f"C2_{key}.md").read_text()
        parts.append(f"### 2.{i} {title}\n\nSource file: reports/stage_e28_briefs/C2_{key}.md.\n\n" + demote(txt, 3))
    parts.append(demote((B / "C3_lead_draft.md").read_text(), 1).replace(
        "## C3 (lead draft): does", "## Part 3 (C3). Does", 1))
    parts.append(demote((B / "C4_lead_draft.md").read_text(), 1).replace(
        "## C4 (lead draft): the", "## Part 4 (C4). The", 1))
    rev = B / "work/lead/C5_review.md"
    if rev.exists():
        parts.append(rev.read_text())
    OUT.write_text("\n\n".join(p.rstrip() + "\n" for p in parts))
    print(OUT, OUT.stat().st_size, "bytes;", len(summary) - 2, "verdict rows;", total_src, "C2 sources")


if __name__ == "__main__":
    main()
