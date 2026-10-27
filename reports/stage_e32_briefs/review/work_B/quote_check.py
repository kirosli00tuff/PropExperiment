"""Check every quoted string in the evidence tables of M1_order_flow.md and M3_labels.md
against the saved page named in the row's File column. Prints one line per quote segment:
FOUND / NOTFOUND / NOFILE, with the file and a 60-char head of the segment.
Normalisation: whitespace collapsed, curly quotes straightened, unicode minus and dashes
mapped to '-', fi/fl ligatures expanded, soft hyphens dropped, case kept.
"""
import re
import sys
from pathlib import Path

ROOT = Path("/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e32_briefs")
PAGES = {"M1": ROOT / "pages/M1_order_flow", "M3": ROOT / "pages/M3_labels",
         "R4": ROOT / "pages/R4_events"}

TRANS = str.maketrans({
    "“": '"', "”": '"', "‘": "'", "’": "'", "−": "-",
    "–": "-", "—": "-", "­": "", "ﬁ": "fi", "ﬂ": "fl",
    " ": " ",
})


def norm(s: str) -> str:
    s = s.translate(TRANS)
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def load(path: Path) -> str:
    try:
        return norm(path.read_text(errors="replace"))
    except FileNotFoundError:
        return ""


def resolve(file_cell: str, prev: str, group: str):
    cell = file_cell.strip()
    if cell.startswith("same"):
        return prev
    m = re.search(r"([A-Za-z0-9_.\-]+\.(?:txt|py|md|html(?:\.txt)?|rst\.txt))", cell)
    if not m:
        return None
    name = m.group(1).replace(".html(.txt)", ".html.txt")
    if cell.startswith("reports/") or "reports/" in cell:
        return ROOT.parent.parent / re.search(r"(reports/\S+?\.md)", cell).group(1) if re.search(r"(reports/\S+?\.md)", cell) else None
    if name.startswith("R4_"):
        return PAGES["R4"] / name
    return PAGES[group] / name


def segments(cell: str):
    # quoted segments inside the markdown cell; escaped pipes are literal
    cell = cell.replace("\\|", "|")
    segs = re.findall(r'"([^"]{12,})"', cell)
    return [norm(s) for s in segs]


def run(md: Path, group: str):
    rows = []
    prev_file = None
    for ln, line in enumerate(md.read_text().splitlines(), 1):
        if not line.startswith("|"):
            continue
        cells = [c for c in re.split(r"(?<!\\)\|", line)[1:-1]]
        if len(cells) < 4 or set(cells[0].strip()) <= {"-"}:
            continue
        if cells[0].strip() in ("Claim", "Pointer (verbatim)", "Planner claim", "Measure", "Topic"):
            continue
        quote_cell, file_cell = cells[2], cells[3]
        target = resolve(file_cell, prev_file, group)
        if target is not None:
            prev_file = target
        for seg in segments(quote_cell):
            rows.append((ln, target, seg))
    cache = {}
    counts = {"FOUND": 0, "NOTFOUND": 0, "NOFILE": 0}
    for ln, target, seg in rows:
        if target is None or not Path(target).exists():
            status = "NOFILE"
        else:
            if target not in cache:
                cache[target] = load(Path(target))
            text = cache[target]
            if seg in text:
                status = "FOUND"
            else:
                # second try: drop all spaces (PDF extraction may split words)
                status = "FOUND*" if seg.replace(" ", "") in text.replace(" ", "") else "NOTFOUND"
        counts[status.rstrip("*")] += 1
        tname = Path(target).name if target else "-"
        print(f"{group} L{ln:<4} {status:<9} {tname:<55} {seg[:70]}")
    print(f"{group} TOTAL {counts}")


if __name__ == "__main__":
    run(ROOT / "M1_order_flow.md", "M1")
    run(ROOT / "M3_labels.md", "M3")
