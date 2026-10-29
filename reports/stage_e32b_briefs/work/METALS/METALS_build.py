"""METALS_build.py: assemble F2_metals.json from work/METALS/METALS_items.jsonl and METALS_meta.json.

Checks every non-reused quote verbatim (whitespace-normalised) against its saved file and fills sha256 and
fetch time from pages/METALS/log.tsv. Prints counts only.
Usage: python3 -I METALS_build.py
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path("/home/kiros-li/Documents/GitHub/PropExperiment")
WORK = ROOT / "reports/stage_e32b_briefs/work/METALS"
PAGES = ROOT / "reports/stage_e32b_briefs/pages/METALS"
OUT = ROOT / "reports/stage_e32b_briefs/F2_metals.json"


def norm(s):
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    s = s.replace("–", "-").replace("—", "-").replace("ﬁ", "fi").replace("ﬂ", "fl")
    return re.sub(r"\s+", " ", s).strip().lower()


def load_log():
    log = {}
    for line in (PAGES / "log.tsv").read_text().splitlines()[1:]:
        parts = line.split("\t")
        if len(parts) >= 6 and parts[4] != "-":
            log[parts[5]] = {"url": parts[0], "fetched_utc": parts[1], "sha256": parts[4]}
    return log


def text_of(path):
    p = Path(path)
    if not p.is_absolute():
        p = ROOT / p
    txt = Path(str(p) + ".txt")
    if txt.exists():
        return txt.read_text(errors="ignore")
    if not p.exists():
        return None
    if p.suffix == ".pdf":
        import subprocess
        cache = WORK / "METALS_quotecache"
        cache.mkdir(exist_ok=True)
        out = cache / (p.name + ".txt")
        if not out.exists():
            subprocess.run(["pdftotext", "-layout", str(p), str(out)], capture_output=True)
        return out.read_text(errors="ignore") if out.exists() else None
    raw = p.read_text(errors="ignore")
    if p.suffix in (".html", ".xml"):
        import html as _h
        raw = _h.unescape(re.sub(r"(?s)<[^>]+>", " ", re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", raw)))
    return raw


def main():
    meta = json.loads((WORK / "METALS_meta.json").read_text())
    log = load_log()
    items, misses = [], []
    seen = set()
    for line in (WORK / "METALS_items.jsonl").read_text().splitlines():
        if not line.strip():
            continue
        it = json.loads(line)
        if it["id"] in seen:
            items = [x for x in items if x["id"] != it["id"]]
        seen.add(it["id"])
        src = it.setdefault("source", {})
        fname = Path(src.get("file", "")).name
        if fname in log:
            for k in ("url", "fetched_utc", "sha256"):
                src.setdefault(k, log[fname][k])
        q = it.get("quote") or ""
        if it.get("verified") in ("full_text", "reused") and q and src.get("file"):
            t = text_of(src["file"])
            ok = t is not None and all(norm(part) in norm(t) for part in q.split(" ... ") if part.strip())
            if not ok:
                misses.append(it["id"])
        items.append(it)
    meta["items"] = items
    meta["quote_check"] = {"checked_against_files": True, "misses": misses}
    OUT.write_text(json.dumps(meta, indent=1, ensure_ascii=False))
    print(f"items={len(items)} quote_misses={misses}")


if __name__ == "__main__":
    sys.exit(main())
