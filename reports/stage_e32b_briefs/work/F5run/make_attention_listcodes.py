"""Format-only copy of F2_attention.json with each underlying's `codes` as a list.

Stage E.32b, C5a F5Runner (Opus 5.5, xhigh), 2026-10-29. score32b.py (s32b_layer1.code_attention) iterates
`entry["codes"]` as a list; F2_attention.json stores it as a space-separated string ("MCL QM CL"), so the script
iterates characters and refuses ("code M under two underlyings"). This copy changes nothing else: every other field
and every count is carried over unchanged, and `codes` becomes str.split() of the original string. The original file
is not edited. The lead decides how the real score run handles this.

Usage: uv run python make_attention_listcodes.py  (prints counts only)
"""
import copy
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.abspath(os.path.join(HERE, "..", "..", "F2_attention.json"))
OUT = os.path.join(HERE, "F2_attention_listcodes.json")


def sha256(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def convert(doc: dict) -> dict:
    out = copy.deepcopy(doc)
    for entry in out["underlyings"].values():
        if isinstance(entry.get("codes"), str):
            entry["codes"] = entry["codes"].split()
    out["format_copy"] = {"source": SRC, "source_sha256": sha256(SRC),
                          "change": "underlyings.<name>.codes: space-separated string -> list (str.split()); "
                                    "nothing else changed",
                          "by": "F5Runner-OpusXHigh, make_attention_listcodes.py"}
    return out


def main() -> int:
    with open(SRC, encoding="utf-8") as fh:
        doc = json.load(fh)
    out = convert(doc)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    n = sum(len(e["codes"]) for e in out["underlyings"].values())
    same = all({k: v for k, v in out["underlyings"][u].items() if k != "codes"}
               == {k: v for k, v in doc["underlyings"][u].items() if k != "codes"} for u in doc["underlyings"])
    print(f"wrote {OUT}: {len(out['underlyings'])} underlyings, {n} codes; other fields identical: {same}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
