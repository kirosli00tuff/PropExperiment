"""A2_topstep: check every E.19 rules-record quote against today's saved pages.

For each rule and prohibited practice in reports/stage_e19_rules.json, find today's copy of its source page
(pages/A2_topstep/ts_<article id>.html.txt or ts_www_<slug>.html.txt), normalise both texts (drop '|',
collapse whitespace, unify quotes/dashes) and report whether the quote is still present verbatim.
Writes a TSV to work/A2_topstep/A2_topstep_e19diff.tsv and prints counts only.
"""
import json
import re
import sys
from pathlib import Path

REPO = Path("/home/kiros-li/Documents/GitHub/PropExperiment")
PAGES = REPO / "reports/stage_e28_briefs/pages/A2_topstep"
OUT = REPO / "reports/stage_e28_briefs/work/A2_topstep/A2_topstep_e19diff.tsv"


def norm(s: str) -> str:
    s = s.replace("|", " ").replace("​", " ").replace(" ", " ")
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    s = s.replace("—", "-").replace("–", "-")
    return re.sub(r"\s+", " ", s).strip().lower()


def today_file(url: str):
    m = re.search(r"/articles/(\d+)", url or "")
    if m:
        return PAGES / f"ts_{m.group(1)}.html.txt"
    m = re.search(r"www\.topstep\.com/([a-z0-9-]+)$", url or "")
    if m:
        slug = m.group(1)
        return PAGES / ("ts_terms_of_use.html.txt" if slug == "terms-of-use" else f"ts_www_{slug}.html.txt")
    return None


def main() -> None:
    d = json.load(open(REPO / "reports/stage_e19_rules.json"))
    src = d["sources"]
    cache = {}
    rows = []
    items = [("rule", r) for r in d["rules"]] + [("practice", p) for p in d["prohibited"]]
    for kind, it in items:
        sid = it.get("source")
        quote = it.get("quote") or ""
        url = src.get(sid, {}).get("url", "") if sid else ""
        f = today_file(url)
        status = "NO_TODAY_COPY"
        if f is not None and f.exists():
            if f not in cache:
                cache[f] = norm(f.read_text(encoding="utf-8"))
            if not quote:
                status = "NO_QUOTE"
            else:
                parts = [p for p in re.split(r"\s*(?:\.\.\.|…)\s*", quote) if p.strip()]
                status = "FOUND" if all(norm(p) in cache[f] for p in parts) else "MISSING"
        rows.append([kind, it.get("id"), it.get("path", it.get("practice", "")), json.dumps(it.get("value", "")),
                     it.get("status", ""), sid or "", f.name if f else "", status, quote.replace("\t", " ")[:300]])
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("kind\tid\tpath\tvalue\te19_status\tsource\ttoday_file\tcheck\tquote\n")
        for r in rows:
            fh.write("\t".join(str(x) for x in r) + "\n")
    from collections import Counter
    print(Counter(r[7] for r in rows))
    print(Counter((r[5], r[7]) for r in rows if r[7] != "FOUND"))


if __name__ == "__main__":
    sys.exit(main())
