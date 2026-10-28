"""PipelineReview N18: sha256 of every evidence result behind the freeze GO, as it stands at the freeze.

Usage: python3 evidence_manifest.py OUT
Writes '<sha256>  <path>' lines (repo-relative, or absolute for DERIVED) and prints counts only.
"""
import hashlib
import sys
from pathlib import Path

REPO = Path("/home/kiros-li/Documents/GitHub/PropExperiment")
W = REPO / "reports/stage_e33_briefs/work"
E = Path("/mnt/large-storage/market_data/PropExperiment/derived/e33")

GLOBS = [
    (W, "*.md"), (W, "*.json"), (W, "*.txt"),
    (W / "b3_runs", "*"), (W / "b4_runs", "*"), (W / "logs", "*"),
    (REPO / "reports/stage_e33_briefs/review", "*.md"),
    (REPO / "reports/stage_e33b_briefs", "*"),
    (E / "b3", "*.parquet"),
    (E / "b4/synthfeat/10", "*.json"), (E / "b4/synthfeat/10", "*.parquet"),
]
FILES = [
    E / "features/2b30cb0e953b/manifest.json",
    E / "labels/b15c4ca10d68/manifest.json",
    E / "proofs/run_manifest.json",
]


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(p: Path) -> str:
    try:
        return str(p.relative_to(REPO))
    except ValueError:
        return str(p)


paths = sorted({p for base, pat in GLOBS for p in base.glob(pat) if p.is_file()} | {p for p in FILES if p.is_file()})
missing = [str(p) for p in FILES if not p.is_file()]
out = Path(sys.argv[1])
lines = [f"{sha(p)}  {rel(p)}" for p in paths]
out.write_text("".join(line + "\n" for line in lines))
print(f"wrote {rel(out)}: {len(lines)} files; missing fixed files: {missing}")
