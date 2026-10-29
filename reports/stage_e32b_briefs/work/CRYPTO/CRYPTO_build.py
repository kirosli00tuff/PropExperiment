"""CRYPTO_build.py: assemble F2_crypto.json from CRYPTO_items.jsonl and CRYPTO_meta.json.

Fills source.url / fetched_utc / sha256 from pages/CRYPTO/log.tsv (or E.28's A1_crypto log for reused files)
when the item's source.file names a logged page. Prints counts only.
"""
import csv
import json
import sys
from pathlib import Path

BASE = Path("/home/kiros-li/Documents/GitHub/PropExperiment/reports")
WORK = BASE / "stage_e32b_briefs/work/CRYPTO"
LOGS = [BASE / "stage_e32b_briefs/pages/CRYPTO/log.tsv", BASE / "stage_e28_briefs/pages/A1_crypto/log.tsv"]
OUT = BASE / "stage_e32b_briefs/F2_crypto.json"


def load_logs():
    idx = {}
    for log in LOGS:
        if not log.exists():
            continue
        with log.open() as fh:
            rows = list(csv.reader(fh, delimiter="\t"))
        for r in rows[1:]:
            if len(r) >= 6 and r[4]:
                idx[r[5]] = {"url": r[0], "fetched_utc": r[1], "sha256": r[4]}
    return idx


def main():
    idx = load_logs()
    meta = json.loads((WORK / "CRYPTO_meta.json").read_text())
    items = []
    for n, line in enumerate((WORK / "CRYPTO_items.jsonl").read_text().splitlines(), 1):
        if not line.strip():
            continue
        try:
            it = json.loads(line)
        except json.JSONDecodeError as exc:
            sys.exit(f"bad JSON on line {n}: {exc}")
        src = it.setdefault("source", {})
        fname = Path(src.get("file", "")).name
        stem = fname[:-4] if fname.endswith(".txt") else fname
        hit = idx.get(fname) or idx.get(stem) or idx.get(stem + ".json")
        if hit:
            for k, v in hit.items():
                src.setdefault(k, v)
        it.setdefault("pointer", False)
        it.setdefault("negative", False)
        items.append(it)
    ids = [i["id"] for i in items]
    dup = {i for i in ids if ids.count(i) > 1}
    if dup:
        sys.exit(f"duplicate ids: {sorted(dup)}")
    out = dict(meta)
    out["items"] = items
    for k in ("searched_not_found", "per_code", "gaps"):
        p = WORK / f"CRYPTO_{k}.json"
        out[k] = json.loads(p.read_text()) if p.exists() else ([] if k != "per_code" else {})
    OUT.write_text(json.dumps(out, indent=1, ensure_ascii=False))
    missing = [i["id"] for i in items if not i["source"].get("sha256") and i["verified"] != "reused"]
    print(f"items={len(items)} topics={sorted({i['topic'] for i in items})} no_sha={missing}")


if __name__ == "__main__":
    main()
