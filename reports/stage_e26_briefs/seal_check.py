"""Stage E.26 T1.2: does the holdout seal mechanism behave the same on /mnt/large-storage (ext4)?

Synthetic data only (random bytes, a 3-row parquet): no real seal, manifest or unlock log is read
or written, nothing is decrypted. Builds one synthetic holdout-1 store in a control directory on
the repo's filesystem and copies it to LARGE STORAGE with cp -a, applies the real seals' permission
scheme (blobs 664 as on disk today; the 444 scheme data/holdout.py applies to unsealed outputs), and
compares data.holdout.verify_seal() on: the control, the LARGE STORAGE copy, and the LARGE STORAGE
copy reached through a symlink in the control directory (the post-move layout). Also checks that
cp -a preserves mode, owner and mtime across the two filesystems, that 444 refuses a write on
both, and that is_sealed_raw / plaintext_absent resolve the same through a symlink.
Usage: uv run python reports/stage_e26_briefs/seal_check.py <out.json>
"""
from __future__ import annotations

import json
import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from data import holdout as h

REPO = Path(__file__).resolve().parents[2]
CONTROL = REPO / "reports" / "stage_e26_briefs" / "sealcheck_control"
LARGE = Path("/mnt/large-storage/_e26_sealcheck")
MODE_SEALED = 0o664  # what `stat` shows on data/sealed/*/ today
MODE_RO = stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH  # data/holdout.py lines 375 and 461
RAW_NAME = "range=2099-01-01_2099-02-01.dbn.zst"


def build_store(root: Path) -> h.HoldoutPaths:
    sealed = root / "sealed"
    (sealed / "raw").mkdir(parents=True)
    salt, nonce = os.urandom(16), os.urandom(16)
    blob = h.seal_bytes(os.urandom(4096), "synthetic acknowledgement", salt, nonce)
    raw_blob = h.seal_bytes(os.urandom(2048), "synthetic acknowledgement", salt, nonce)
    (sealed / "holdout_bars.sealed").write_bytes(blob)
    (sealed / "raw" / (RAW_NAME + ".sealed")).write_bytes(raw_blob)
    research = root / "research.parquet"
    pq.write_table(pa.table({"trade_date": ["2020-01-02", "2020-01-03", "2020-01-06"]}), research)
    log = root / "unlock_log.md"
    log.write_text("# synthetic unlock log\n")
    plaintext = root / "vendor" / RAW_NAME  # never created by the build
    manifest = {
        "holdout": {"sha256_sealed": h.sha256_file(sealed / "holdout_bars.sealed")},
        "research": {"sha256": h.sha256_file(research)},
        "raw_files": [{"original_path": str(plaintext), "sealed_relpath": "raw/" + RAW_NAME + ".sealed",
                       "sha256_sealed": h.sha256_file(sealed / "raw" / (RAW_NAME + ".sealed"))}],
        "unlock_log_at_seal": {"bytes": log.stat().st_size, "sha256": h.sha256_file(log)},
    }
    (root / "manifest.json").write_text(json.dumps(manifest))
    for p in (sealed / "holdout_bars.sealed", sealed / "raw" / (RAW_NAME + ".sealed")):
        p.chmod(MODE_SEALED)
    research.chmod(MODE_RO)
    return h.HoldoutPaths(sealed_root=sealed, manifest=root / "manifest.json", unlock_log=log,
                          registration=root / "REGISTRATION.md", research_parquet=research)


def stat_row(p: Path) -> dict:
    s = p.stat()
    return {"mode": oct(stat.S_IMODE(s.st_mode)), "uid": s.st_uid, "gid": s.st_gid,
            "mtime_ns": s.st_mtime_ns, "size": s.st_size}


def write_refused(p: Path) -> bool:
    try:
        with open(p, "ab"):
            return False
    except PermissionError:
        return True


def fs_type(p: str) -> str:
    return subprocess.run(["stat", "-f", "-c", "%T", p], capture_output=True, text=True).stdout.strip()


def cleanup() -> None:
    for d in (CONTROL, LARGE):
        if d.exists():
            for p in d.rglob("*"):
                if not p.is_symlink():
                    p.chmod(0o700 if p.is_dir() else 0o600)
            shutil.rmtree(d)


def main(out: str) -> int:
    for d in (CONTROL, LARGE):
        if d.exists():
            raise SystemExit(f"{d} exists already; refusing to overwrite")
    rep: dict = {"control_fs": fs_type(str(REPO)), "large_fs": fs_type("/mnt/large-storage")}
    try:
        ctl = build_store(CONTROL)
        rep["verify_control"] = h.verify_seal(ctl)
        subprocess.run(["cp", "-a", str(CONTROL), str(LARGE)], check=True)  # what T1.5 uses
        big = h.HoldoutPaths(sealed_root=LARGE / "sealed", manifest=LARGE / "manifest.json",
                             unlock_log=LARGE / "unlock_log.md", registration=LARGE / "REGISTRATION.md",
                             research_parquet=LARGE / "research.parquet")
        rep["verify_large"] = h.verify_seal(big)  # original_path still names the control's vendor dir
        link = CONTROL / "sealed_link"  # post-move layout: the sealed root reached through a symlink
        link.symlink_to(LARGE / "sealed", target_is_directory=True)
        via = h.HoldoutPaths(sealed_root=link, manifest=ctl.manifest, unlock_log=ctl.unlock_log,
                             registration=ctl.registration, research_parquet=ctl.research_parquet)
        rep["verify_via_symlink"] = h.verify_seal(via)
        rel = "sealed/raw/" + RAW_NAME + ".sealed"
        rep["stat_control"], rep["stat_large"] = stat_row(CONTROL / rel), stat_row(LARGE / rel)
        rep["stat_research_control"] = stat_row(CONTROL / "research.parquet")
        rep["stat_research_large"] = stat_row(LARGE / "research.parquet")
        rep["ro_write_refused_control"] = write_refused(CONTROL / "research.parquet")
        rep["ro_write_refused_large"] = write_refused(LARGE / "research.parquet")
        # plaintext_absent and is_sealed_raw when the recorded vendor dir is a symlink to LARGE STORAGE
        (LARGE / "vendor").mkdir()
        (CONTROL / "vendor").symlink_to(LARGE / "vendor", target_is_directory=True)
        plain = CONTROL / "vendor" / RAW_NAME
        rep["is_sealed_raw_via_symlink"] = h.is_sealed_raw(plain, ctl)
        rep["is_sealed_raw_resolved"] = h.is_sealed_raw(plain.resolve(), ctl)
        rep["plaintext_absent_before"] = h.verify_seal(ctl)["raw_files"]
        (LARGE / "vendor" / RAW_NAME).write_bytes(b"synthetic plaintext stand-in")
        rep["plaintext_absent_after_target_created"] = h.verify_seal(ctl)["raw_files"]
        rep["all_ok_after_target_created"] = h.verify_seal(ctl)["all_ok"]
        rep["summary"] = {
            "all_ok": {k: rep[k]["all_ok"] for k in ("verify_control", "verify_large", "verify_via_symlink")},
            "reports_equal": rep["verify_control"] == rep["verify_large"] == rep["verify_via_symlink"],
            "cp_a_preserves_stat": rep["stat_control"] == rep["stat_large"]
            and rep["stat_research_control"] == rep["stat_research_large"],
            "ro_scheme_same": rep["ro_write_refused_control"] is True and rep["ro_write_refused_large"] is True,
            "is_sealed_raw_same": rep["is_sealed_raw_via_symlink"] is True and rep["is_sealed_raw_resolved"] is True,
            "symlink_detects_plaintext": rep["all_ok_after_target_created"] is False,
        }
    finally:
        cleanup()
        rep["cleaned_up"] = not CONTROL.exists() and not LARGE.exists()
    Path(out).write_text(json.dumps(rep, indent=1, default=str) + "\n")
    print(json.dumps(rep["summary"]), "cleaned_up", rep["cleaned_up"])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
