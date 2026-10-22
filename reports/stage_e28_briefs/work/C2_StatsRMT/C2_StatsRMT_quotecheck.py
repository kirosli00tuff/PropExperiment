"""Extract quoted strings from the C2_StatsRMT brief body and locate each in the saved page texts."""
import json, re, sys, unicodedata
from pathlib import Path

BASE = Path("/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e28_briefs")
PAGES = BASE / "pages" / "C2_StatsRMT"
EXTRA = {"stage_e_verdict.py": Path("/home/kiros-li/Documents/GitHub/PropExperiment/screening/stage_e_verdict.py")}

def norm(s):
    s = unicodedata.normalize("NFKC", s)
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    s = s.replace("–", "-").replace("—", "-").replace("−", "-").replace("ﬁ", "fi").replace("ﬂ", "fl")
    s = re.sub(r"-\s*\n\s*", "-", s)
    s = s.lower()
    return re.sub(r"[^a-z0-9]", "", s)

def load_sources():
    src = {}
    for p in sorted(PAGES.glob("*.txt")):
        src[p.name] = norm(p.read_text(errors="ignore"))
    for k, p in EXTRA.items():
        if p.exists():
            src[k] = norm(p.read_text(errors="ignore"))
    return src

def main():
    text = (BASE / "C2_StatsRMT.md").read_text()
    body = text.split("\n## 14.")[0]
    joined = re.sub(r"\s*\n\s*", " ", body)
    quotes = [q for q in re.findall(r'"([^"]{25,600})"', joined)]
    src = load_sources()
    out = []
    for q in quotes:
        parts = [norm(x) for x in re.split(r"\[\.\.\.\]", q) if len(re.sub(r"[^A-Za-z0-9]", "", x)) > 8]
        hits = [n for n, t in src.items() if parts and all(p in t for p in parts)]
        out.append({"quote": q, "hits": hits})
    (BASE / "work" / "C2_StatsRMT" / "C2_StatsRMT_quotecheck.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
    ok = sum(1 for o in out if o["hits"])
    print(f"quotes={len(out)} found={ok} missing={len(out)-ok}")
    for o in out:
        if not o["hits"]:
            print("MISSING:", o["quote"][:150])

if __name__ == "__main__":
    main()
