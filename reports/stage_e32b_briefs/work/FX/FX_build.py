"""FX_build.py: assemble F2_fx.json from the FX reader's item list (Stage E.32b, step F2).

Fills source url / fetched_utc / sha256 from the fetch logs (this reader's pages/FX/log.tsv,
E.28's pages/A1_fx/log.tsv, E.20's pages/6E/fetch_log.tsv) and checks every quote verbatim
(whitespace-collapsed) against the saved text. Prints counts only.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path("/home/kiros-li/Documents/GitHub/PropExperiment/reports")
MY = ROOT / "stage_e32b_briefs/pages/FX"
E28 = ROOT / "stage_e28_briefs/pages/A1_fx"
E20 = ROOT / "stage_e20_briefs/pages/6E"
OUT = ROOT / "stage_e32b_briefs/F2_fx.json"

sys.path.insert(0, str(Path(__file__).parent))
from FX_items import ITEMS, META, PER_CODE, NOT_FOUND, GAPS  # noqa: E402


def load_logs():
    idx = {}
    for line in (MY / "log.tsv").read_text().splitlines()[1:]:
        c = line.split("\t")
        if len(c) >= 6 and c[4] not in ("-", ""):
            idx[str(MY / c[5])] = (c[0], c[1], c[4])
    for line in (E28 / "log.tsv").read_text().splitlines()[1:]:
        c = line.split("\t")
        if len(c) >= 6 and c[2] == "OpenAlex API":
            idx[str(E28 / c[4])] = (c[0], c[1], c[3])
        elif len(c) >= 6:
            idx[str(E28 / c[5])] = (c[0], c[1], c[4])
    for line in (E20 / "fetch_log.tsv").read_text().splitlines():
        c = line.split("\t")
        if len(c) >= 6:
            idx[str(E20 / c[3])] = (c[2], c[0], c[5])
    return idx


def text_of(raw: Path) -> str:
    for cand in (Path(str(raw) + ".txt"), raw.with_suffix(".txt"), raw):
        if cand.exists() and cand.suffix != ".pdf":
            return cand.read_text(errors="ignore")
    return ""


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def main():
    idx = load_logs()
    bad, items = [], []
    for n, it in enumerate(ITEMS, 1):
        it = dict(it)
        it["id"] = f"FX-{n}"
        src = dict(it.get("source", {}))
        f = src.get("file")
        if f and not f.endswith(".json") and not f.endswith(".md"):
            raw = Path(f)
            hit = idx.get(str(raw))
            if hit is None and str(raw).endswith(".txt"):
                base = str(raw)[:-4]
                for cand in (base, base + ".pdf", base + ".html", base.replace("_abstract", "") + ".json"):
                    if cand in idx:
                        hit = idx[cand]
                        break
            if hit is None:
                bad.append((it["id"], "no log entry", f))
            else:
                src.setdefault("url", hit[0])
                src.setdefault("fetched_utc", hit[1])
                src.setdefault("sha256", hit[2])
            q = it.get("quote")
            if q and it.get("verified") in ("full_text", "abstract", "reused") and not it.get("quote_unchecked"):
                parts = [p for p in q.split(" [...] ")]
                t = norm(text_of(raw))
                for p in parts:
                    if norm(p) not in t:
                        bad.append((it["id"], "quote not found", p[:60]))
            src["file"] = str(raw.relative_to(ROOT.parent))
        it["source"] = src
        it.pop("quote_unchecked", None)
        it.setdefault("pointer", False)
        it.setdefault("negative", False)
        items.append(it)
    out = dict(META)
    out["items"] = items
    out["searched_not_found"] = NOT_FOUND
    out["per_code"] = PER_CODE
    out["gaps"] = GAPS
    OUT.write_text(json.dumps(out, indent=1, ensure_ascii=False))
    print(f"items={len(items)} problems={len(bad)}")
    for b in bad:
        print("PROBLEM", *b)


if __name__ == "__main__":
    main()
