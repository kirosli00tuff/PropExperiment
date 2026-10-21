"""Stage E.26 T1.4-T1.5: move market data to LARGE STORAGE with a symlink at every old path.

Plan JSON (reports/stage_e26_move_plan.json): {"dest_root": "/mnt/large-storage/market_data/PropExperiment",
"aside_root": "/home/kiros-li/e26_aside", "sources": ["data/vendor/databento", ...]} with repo-relative
sources (directories or files). Each source S goes to dest_root/S (the repo-relative layout mirrored).

  manifest  T1.4: walk every source (no symlink following), record each dir, file and symlink (mode,
            uid, gid, mtime_ns, size, sha256 of files, link targets), write move_manifest.jsonl and
            move_manifest_summary.json. Refuses special files and sources that are already symlinks.
  move      T1.5, per source in plan order, resumable from move_state.json:
            copy   cp -a --no-target-directory S dest (mode, ownership, timestamps, links preserved)
            verify sync, then every manifest entry re-checked AT THE DESTINATION: same set of paths,
            same kind, mode, uid, gid, mtime_ns, size, link target; file sha256 recomputed after
            sync + POSIX_FADV_DONTNEED so the bytes come from disk, not the page cache
            swap    os.rename(S, aside_root/S) (same filesystem, atomic), then os.symlink(dest, S)
            (state "swapped" written at once), then check S is a symlink resolving to dest.
            Nothing is deleted here. A source in state "copied" (after a rollback) is re-verified
            at the destination before it is swapped again (review finding 1).
  finalize  after the T1.6 after-checks pass: for each swapped source whose link resolves to its
            own destination, mark it "finalizing", delete aside_root/S, mark it "finalized" (the
            source "is deleted only after its copy is verified and its symlink is in place").
  rollback  for each swapped source, and each half-swapped one (state verified, aside present):
            remove the link, rename the aside back, state "copied". Refuses a "finalizing" source.
  status    print the state.
Stops at the first mismatch, leaving that source untouched in place. Run at nice 10.
Review: reports/stage_e26_briefs/review_moveplan.md (MovePlanReviewer-FableXHigh), findings 1-4 and 8.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "reports" / "stage_e26_briefs"
MANIFEST = OUT / "move_manifest.jsonl"
SUMMARY = OUT / "move_manifest_summary.json"
STATE = OUT / "move_state.json"
CHUNK = 1 << 20


def sha256_file(path: Path, *, from_disk: bool = False) -> str:
    fd = os.open(path, os.O_RDONLY)
    try:
        if from_disk:
            os.posix_fadvise(fd, 0, 0, os.POSIX_FADV_DONTNEED)  # clean pages after sync: evicted
        digest = hashlib.sha256()
        while block := os.read(fd, CHUNK):
            digest.update(block)
        return digest.hexdigest()
    finally:
        os.close(fd)


def entry(path: Path, rel: str, *, from_disk: bool = False) -> dict:
    st = path.lstat()
    row = {"src": rel, "mode": oct(stat.S_IMODE(st.st_mode)), "uid": st.st_uid, "gid": st.st_gid,
           "mtime_ns": st.st_mtime_ns}
    if stat.S_ISLNK(st.st_mode):
        return {**row, "kind": "symlink", "target": os.readlink(path)}
    if stat.S_ISDIR(st.st_mode):
        return {**row, "kind": "dir"}  # dir mtime is recorded, not compared (cp -a sets it last)
    if stat.S_ISREG(st.st_mode):
        return {**row, "kind": "file", "size": st.st_size, "nlink": st.st_nlink,
                "sha256": sha256_file(path, from_disk=from_disk)}
    raise SystemExit(f"refusing special file {path}")


def walk(root: Path, rel_root: str, *, from_disk: bool = False) -> list[dict]:
    """Every entry under root (root included), keyed by its repo-relative source path."""
    rows = [entry(root, rel_root, from_disk=from_disk)]
    if rows[0]["kind"] != "dir":
        return rows
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        base = Path(dirpath)
        for name in sorted(dirnames) + sorted(filenames):
            p = base / name
            rows.append(entry(p, f"{rel_root}/{p.relative_to(root).as_posix()}", from_disk=from_disk))
    return rows


def load_plan(path: str) -> dict:
    plan = json.loads(Path(path).read_text())
    for s in plan["sources"]:
        if s.startswith("/") or ".." in Path(s).parts or not s.strip():
            raise SystemExit(f"bad source {s!r}")
    return plan


def load_state() -> dict:
    return json.loads(STATE.read_text()) if STATE.exists() else {}


def save_state(state: dict) -> None:
    tmp = STATE.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=1) + "\n")
    os.replace(tmp, STATE)


def manifest_rows() -> dict[str, list[dict]]:
    by_source: dict[str, list[dict]] = {}
    for line in MANIFEST.read_text().splitlines():
        row = json.loads(line)
        by_source.setdefault(row["source"], []).append(row)
    return by_source


def cmd_manifest(plan: dict) -> int:
    if MANIFEST.exists():
        raise SystemExit(f"{MANIFEST} exists; the T1.4 manifest is written once")
    summary = {"dest_root": plan["dest_root"], "sources": {}}
    with MANIFEST.open("w") as out:
        for s in plan["sources"]:
            src = REPO / s
            if src.is_symlink() or not src.exists():
                raise SystemExit(f"source {s} is a symlink or missing")
            rows = walk(src, s)
            files = [r for r in rows if r["kind"] == "file"]
            summary["sources"][s] = {"entries": len(rows), "files": len(files),
                                     "bytes": sum(r["size"] for r in files),
                                     "symlinks": sum(r["kind"] == "symlink" for r in rows),
                                     "hardlinked_files": sum(r["nlink"] > 1 for r in files)}
            for r in rows:
                out.write(json.dumps({"source": s, **r}, sort_keys=True) + "\n")
            print(s, summary["sources"][s], flush=True)
    summary["manifest_sha256"] = sha256_file(MANIFEST)
    summary["total_files"] = sum(v["files"] for v in summary["sources"].values())
    summary["total_bytes"] = sum(v["bytes"] for v in summary["sources"].values())
    SUMMARY.write_text(json.dumps(summary, indent=1) + "\n")
    print("manifest", summary["manifest_sha256"], "files", summary["total_files"], "bytes", summary["total_bytes"])
    return 0


def compare(expected: list[dict], dest: Path, s: str) -> list[str]:
    got = {r["src"]: r for r in walk(dest, s, from_disk=True)}
    want = {r["src"]: r for r in expected}
    problems = [f"missing at dest: {k}" for k in sorted(set(want) - set(got))]
    problems += [f"extra at dest: {k}" for k in sorted(set(got) - set(want))]
    for k in sorted(set(want) & set(got)):
        a, b = want[k], got[k]
        keys = ["kind", "mode", "uid", "gid"] + {"file": ["size", "mtime_ns", "sha256"],
                                                 "symlink": ["target"], "dir": []}[a["kind"]]
        bad = [f"{f} {a.get(f)} != {b.get(f)}" for f in keys if a.get(f) != b.get(f)]
        if bad:
            problems.append(f"{k}: " + "; ".join(bad))
    return problems


def record_problems(s: str, problems: list[str]) -> None:
    with (OUT / "move_problems.txt").open("a") as out:  # appended: the first report is kept
        out.write(f"## {s}\n" + "\n".join(problems) + "\n")


def preconditions(dest_root: Path, aside_root: Path, plan: dict) -> None:
    """Step 0 in code (review note 8): the mount, the aside root on the repo's device, free space."""
    mount = Path(plan.get("mountpoint", "/mnt/large-storage"))
    if not os.path.ismount(mount) or not dest_root.is_relative_to(mount):
        raise SystemExit(f"{mount} is not mounted, or {dest_root} is not under it")
    probe = aside_root if aside_root.exists() else aside_root.parent
    if os.stat(probe).st_dev != os.stat(REPO).st_dev:
        raise SystemExit(f"aside root {aside_root} is not on the repo's filesystem (rename would hit EXDEV)")
    need = json.loads(SUMMARY.read_text())["total_bytes"]
    if shutil.disk_usage(mount).free < 2 * need:
        raise SystemExit(f"less than twice {need} bytes free on {mount}")


def swap(s: str, src: Path, dest: Path, aside: Path, state: dict) -> None:
    if src.is_symlink():
        raise SystemExit(f"{src} is already a symlink but state says verified; run rollback, then move")
    aside.parent.mkdir(parents=True, exist_ok=True)
    if aside.exists():
        raise SystemExit(f"{aside} exists; inspect")
    os.rename(src, aside)
    os.symlink(dest, src, target_is_directory=True)
    state[s] = "swapped"  # at once, so a failed check below leaves a state rollback understands
    save_state(state)
    if not (src.is_symlink() and src.exists() and src.resolve() == dest.resolve()):
        raise SystemExit(f"{s}: symlink check failed after swap; run rollback")
    print(s, "swapped: symlink ->", dest, flush=True)


def cmd_move(plan: dict) -> int:
    dest_root, aside_root = Path(plan["dest_root"]), Path(plan["aside_root"])
    preconditions(dest_root, aside_root, plan)
    rows, state = manifest_rows(), load_state()
    for s in plan["sources"]:
        src, dest, aside = REPO / s, dest_root / s, aside_root / s
        phase = state.get(s, "pending")
        if phase in ("swapped", "finalizing", "finalized"):
            print(s, phase, "(skipped)", flush=True)
            continue
        if phase == "pending":
            if dest.exists() or dest.is_symlink():
                raise SystemExit(f"{dest} exists before copy; inspect it (no overwrite)")
            if src.is_symlink() or not src.exists():
                raise SystemExit(f"{src} is a symlink or missing before copy")
            dest.parent.mkdir(parents=True, exist_ok=True)
            subprocess.run(["cp", "-a", "--no-target-directory", str(src), str(dest)], check=True)
            os.sync()
            phase = "copied"
        if phase == "copied":  # a fresh copy, or a destination kept by rollback: verify before any swap
            if not dest.is_dir() or src.is_symlink() or not src.is_dir():
                raise SystemExit(f"{s}: state copied but destination or source is not a real directory")
            problems = compare(rows[s], dest, s)
            if problems:
                record_problems(s, problems)
                raise SystemExit(f"{s}: {len(problems)} mismatches at dest (move_problems.txt); source untouched")
            state[s] = phase = "verified"
            save_state(state)
            print(s, "copied and verified", len(rows[s]), "entries", flush=True)
        if phase == "verified":
            swap(s, src, dest, aside, state)
    print("move complete:", load_state())
    return 0


def cmd_finalize(plan: dict) -> int:
    dest_root, aside_root, state = Path(plan["dest_root"]), Path(plan["aside_root"]), load_state()
    for s in plan["sources"]:
        if state.get(s) not in ("swapped", "finalizing"):
            print(s, state.get(s, "pending"), "(not finalized)")
            continue
        src, dest, aside = REPO / s, dest_root / s, aside_root / s
        if not (src.is_symlink() and src.exists() and src.resolve() == dest.resolve()):
            raise SystemExit(f"{s}: link missing, dangling or not pointing at {dest}; not deleting the aside")
        state[s] = "finalizing"  # rollback refuses from here on: the aside may be partly deleted
        save_state(state)
        if aside.is_dir():
            for p in [aside, *aside.rglob("*")]:
                if p.is_dir() and not p.is_symlink():
                    p.chmod(stat.S_IMODE(p.stat().st_mode) | stat.S_IWUSR | stat.S_IXUSR)
            shutil.rmtree(aside)
        elif aside.exists():
            aside.unlink()
        state[s] = "finalized"
        save_state(state)
        print(s, "aside deleted")
    return 0


def cmd_rollback(plan: dict) -> int:
    aside_root, state = Path(plan["aside_root"]), load_state()
    interrupted = [s for s in plan["sources"] if state.get(s) == "finalizing"]
    if interrupted:  # checked before anything is rolled back
        raise SystemExit(f"{interrupted}: finalize was interrupted and the aside is partly deleted; the "
                         "destination copy is the complete one: relink it, do not roll back")
    for s in reversed(plan["sources"]):
        src, aside = REPO / s, aside_root / s
        phase = state.get(s)
        half = phase == "verified" and aside.exists() and not (src.exists() and not src.is_symlink())
        if phase != "swapped" and not half:
            continue
        if src.is_symlink():
            src.unlink()
        os.rename(aside, src)
        state[s] = "copied"  # the destination copy is kept and is re-verified before any re-swap
        save_state(state)
        print(s, "rolled back (destination copy kept; re-verified on the next move)")
    return 0


def main(argv: list[str]) -> int:
    if len(argv) != 3 or argv[1] not in ("manifest", "move", "finalize", "rollback", "status"):
        raise SystemExit(__doc__)
    plan = load_plan(argv[2])
    if argv[1] == "status":
        print(json.dumps(load_state(), indent=1))
        return 0
    return {"manifest": cmd_manifest, "move": cmd_move, "finalize": cmd_finalize,
            "rollback": cmd_rollback}[argv[1]](plan)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
