"""E.33 C1: write the freeze file of the 300 registered configurations (protocol P7.1).

The freeze file holds, per registry ID, the set, its features, the label, h, the model and its hyperparameters, the
pipeline sha256 and the protocol sha256 (the prompt's C1 fields; the registry line carries none), and once for the
file the sha256 of reports/stage_e33_protocol_readings.md. It writes the file and prints its sha256; the registration
itself is the separate `python -m screening.trial_registry register` call, run by the lead.

Usage: uv run python reports/stage_e33_briefs/work/lead/c1_freeze.py --pipeline-freeze <freeze list file>
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
PROTOCOL = REPO / "reports/stage_e32_discovery_protocol.md"
PROTOCOL_SHA = "c4ffb9d79af4bbbf10574ac138668aa49a80b22a8f5fba5879184d357d2c7e05"
READINGS = REPO / "reports/stage_e33_protocol_readings.md"
OUT = REPO / "reports/stage_e33_c1_freeze.json"

C_IDS = [f"C_{k}" for k in range(1, 16)]
FAMILY = {"F1": 8, "F2": 11, "F3": 12, "F4": 13}
FEATS = {fam: [f"{fam}_{k}" for k in range(1, n + 1)] for fam, n in FAMILY.items()}
SETS = {  # P2: S1 = C+F1, S2 = C+F2, S3 = C+F3, S4 = C+F4, S5 = C+F1+F2+F3+F4
    "S1": C_IDS + FEATS["F1"], "S2": C_IDS + FEATS["F2"], "S3": C_IDS + FEATS["F3"],
    "S4": C_IDS + FEATS["F4"],
    "S5": C_IDS + FEATS["F1"] + FEATS["F2"] + FEATS["F3"] + FEATS["F4"],
}
LABELS = {  # P3.1, P7.1 label codes: type and horizon (minutes; the vertical barrier for TB)
    "F05": ("FH", 5), "F15": ("FH", 15), "F30": ("FH", 30), "F60": ("FH", 60),
    "T15": ("TB", 15), "T30": ("TB", 30),
}
LOGIT_COMMON = {"solver": "saga", "max_iter": 2000, "tol": 1e-4, "loss": "multinomial",
                "random_state": 20261027, "sample_weight": "P3.7 u_i", "standardise": "P4 G5",
                "intercept_penalised": False}
LGBM_COMMON = {"objective": "multiclass", "num_class": 3, "boosting": "gbdt", "learning_rate": 0.05,
               "num_iterations_max": 500, "early_stopping_rounds": 50,
               "early_stopping_metric": "weighted multi_logloss, inner validation block",
               "inner_validation": "latest 15% of the fold's training dates, rounded up",
               "feature_fraction": 0.8, "bagging_fraction": 0.8, "bagging_freq": 1, "lambda_l2": 1.0,
               "min_gain_to_split": 0, "max_bin": 255, "seed": 20261027, "deterministic": True,
               "force_row_wise": True, "monotone_constraints": None,
               "calibration": "multinomial LR C 1e4 lbfgs max_iter 1000 tol 1e-6 on 3 raw scores, inner block"}


def grid(h: int) -> list[tuple[str, str, dict]]:
    """P5 grids in the P7.1 order: 6 LOGIT then 4 LGBM points."""
    pts = []
    for code, c in (("L001", 0.01), ("L010", 0.1), ("L100", 1.0)):
        for suffix, rho in (("A", 0.0), ("E", 0.5)):
            pts.append((code + suffix, "LOGIT", {**LOGIT_COMMON, "C": c, "rho": rho}))
    for depth in (2, 3):
        for mult, tag in ((50, "050"), (200, "200")):
            pts.append((f"G{depth}{tag}", "LGBM", {**LGBM_COMMON, "max_depth": depth,
                                                    "num_leaves": 2 ** depth,
                                                    "min_data_in_leaf": mult * h}))
    return pts


def configurations(pipeline_sha: str) -> list[dict]:
    rows = []
    for set_id, feats in SETS.items():
        for label, (kind, h) in LABELS.items():
            for code, model, hp in grid(h):
                rows.append({"id": f"E33-{set_id}{label}{code}", "set": set_id, "features": feats,
                             "label": label, "label_type": kind, "h_min": h, "model": model,
                             "hyperparameters": hp, "pipeline_sha256": pipeline_sha,
                             "protocol_sha256": PROTOCOL_SHA})
    return rows


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pipeline-freeze", required=True, type=Path)
    args = ap.parse_args()
    if sha256(PROTOCOL) != PROTOCOL_SHA:
        raise SystemExit("protocol sha256 differs from the frozen v1.0: refusing")
    rows = configurations(sha256(args.pipeline_freeze))
    ids = [r["id"] for r in rows]
    assert len(rows) == 300 and len(set(ids)) == 300
    assert all(len(SETS[r["set"]]) == {"S1": 23, "S2": 26, "S3": 27, "S4": 28, "S5": 59}[r["set"]]
               for r in rows)
    doc = {"stage": "E.33", "test": "E33", "protocol": str(PROTOCOL.relative_to(REPO)),
           "protocol_sha256": PROTOCOL_SHA,
           "pipeline_freeze": str(args.pipeline_freeze.resolve().relative_to(REPO)),
           "pipeline_sha256": sha256(args.pipeline_freeze),
           "protocol_readings": str(READINGS.relative_to(REPO)), "protocol_readings_sha256": sha256(READINGS),
           "n_configurations": len(rows), "configurations": rows}
    OUT.write_text(json.dumps(doc, indent=1) + "\n")
    print(f"wrote {OUT.relative_to(REPO)} sha256 {sha256(OUT)}")
    print("ids:", " ".join(ids))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
