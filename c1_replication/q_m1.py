"""Test C1, part 1: reproduce q from E.12's persisted Gate 0 state and fit M1 once (no 2010-2019
byte is read; ruling C9: both are fixed before any purchase).

    python -m c1_replication.q_m1 --state <E.12 state dir copy> \
        --state-manifest reports/stage_e14_c1_e12_state_manifest.json \
        --out reports/stage_e14_c1_model.json --model-dir <dir outside the repository>

Order (nothing is loaded before step 1 passes; nothing is written unless every step passes):
1. Checks: the v2 freeze (every ml_route_v2 file is E.12's, constants.py byte-identical), the
   state dir against the manifest (45 OOF split files, gate0B_meta.json, both stage pickles,
   phase1_build.json, and nothing else), E.12's Gate 0 report and test list against their pinned
   sha256s. A failure refuses (exit 2), nothing written.
2. ml_route_v2.phase1.build.load_build(state) (its constants-fingerprint check stays on); the
   build's constants and input fingerprints, the family B meta fingerprint, the list sha256 and the
   covered signals must equal what E.12's report and list record ("C1 STOP", exit 3, otherwise).
3. Gate 0's NG family B rows at h60 and hF, reproduced with NO fit (ruling C4): every split file
   gate0B_<h>_sNN.npy the run's blocks name must exist before the call, Gate 0's fit function is
   replaced by one that stops while the call runs, and the call is E.12's own
   (gate0_stage.run_gate0 -> pipeline._gate0 -> gate0.gate0_b_trades with the build's admissible
   pairs and calendar; gate0._b_test as gate0_family_b applies it). Registration goes to a
   temporary copy of ledger/ml_v2_config_ledger.jsonl; the real file's sha256 must not change, and
   neither may the copy's (every test was already registered with its spec). trades (n_trades,
   n_dates, n_obs) must equal the report exactly and mean and t_B within ABSOLUTE 1e-9; any
   mismatch prints "C1 STOP: q reproduction mismatch" and exits 3 with nothing written.
4. q_h = the smallest |r_hat| among NG's Gate 0 trades at h (ruling C3), kept at full precision
   (repr), with the count of NG OOF rows at or above it (= the trades unless |r_hat| ties).
5. M1 per h in (h60, hF): cpcv.horizon_data(panel, h, admissible) (all 81 pairs' ok rows at h,
   pooled), models.fit_model(configs.ridge_spec(gate0.GATE0_RIDGE_LAMBDA), X, y), fitted twice
   (the two payload sha256s must agree, else C1 STOP). The payload bytes go to
   <model-dir>/c1_m1_<h>.ridge (an existing file must hold the same bytes).
6. C10's reference: per covered signal, the count of NG ok rows at h whose app_<signal> is 1
   (counts only).
7. --out (written once): hashes, the reproduced rows, q, M1's payload sha256s, feature_cols and its
   sha256 (sha256 of the UTF-8 JSON list, separators "," and ":"), the C10 counts, the ledger
   sha256s, versions. The state is re-verified after the run.
"""

from __future__ import annotations

import argparse
import json
import math
import platform
import sys
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any

import numpy as np

from c1_replication.constants import (
    CODE_DIR,
    E12_GATE0_DIR,
    E12_GATE0_LIST,
    E12_GATE0_LIST_SHA256,
    E12_GATE0_REPORT,
    E12_GATE0_REPORT_SHA256,
    HORIZONS_TESTED,
    ML_LEDGER,
    MODEL_SCHEMA,
    RC_REFUSED,
    RC_STOP,
    REPRO_TOLERANCE,
    V2_FREEZE_MANIFEST,
    V2_FREEZE_SHA256,
    VEHICLE,
)
from c1_replication.guards import (
    C1Refused,
    C1Stop,
    file_sha256,
    ledger_copy,
    no_fits,
    pinned_file,
    verify_state,
    verify_v2,
)

MISMATCH = "C1 STOP: q reproduction mismatch"
EXACT_KEYS = ("n_trades", "n_dates", "n_obs")
FLOAT_KEYS = (("mean_gross_ticks", "mean"), ("t_B", "t"))
INFO_FLOAT_KEYS = (("cost_ticks", "cost_ticks"), ("p", "p"))


def feature_cols_sha256(cols: Sequence[str]) -> str:
    import hashlib

    return hashlib.sha256(json.dumps(list(cols), separators=(",", ":")).encode()).hexdigest()


def payload_name(h: str) -> str:
    return f"c1_m1_{h}.ridge"


def code_hashes() -> dict[str, str]:
    return {p.name: file_sha256(p) for p in sorted(CODE_DIR.glob("*.py"))}


# ------------------------------------------------------------------ E.12 facts ----
def e12_facts(report_path: Path, report_sha: str, list_path: Path, list_sha: str
              ) -> tuple[dict, dict]:
    report = json.loads(pinned_file(report_path, report_sha, "E.12 Gate 0 report"))
    listed = json.loads(pinned_file(list_path, list_sha, "E.12 Gate 0 list"))
    return report, listed


def report_rows(report: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    want = {f"gate0B_{VEHICLE}_{h}": h for h in HORIZONS_TESTED}
    rows = {want[t["test_id"]]: t for t in report.get("tests", []) if t.get("test_id") in want}
    if set(rows) != set(HORIZONS_TESTED):
        lacking = sorted(set(HORIZONS_TESTED) - set(rows))
        raise C1Stop(f"{MISMATCH} (the E.12 report lacks {lacking})")
    return rows


def check_build(build: Any, report: Mapping[str, Any], listed: Mapping[str, Any],  # noqa: ANN401
                gate_dir: Path, list_sha: str) -> dict[str, Any]:
    fps = report.get("fingerprints", {})
    meta = json.loads((gate_dir / "gate0B_meta.json").read_text(encoding="utf-8"))
    checks = {
        "constants": (build.constants, fps.get("constants")),
        "inputs": (build.input_fingerprint, fps.get("inputs")),
        "gate0_b_state": (meta.get("fingerprint"), fps.get("gate0_b_state")),
        "list_sha256": (list_sha, report.get("list_sha256")),
        "covered_signals": (list(build.panel.signal_names), listed.get("covered_signals")),
        "admissible_pairs": ([list(map(str, p)) for p in build.filt["admissible"]],
                             listed.get("admissible_pairs")),
    }
    bad = [k for k, (a, b) in checks.items() if a != b]
    if bad:
        raise C1Stop(f"{MISMATCH} (the saved build does not match E.12's report or list: {bad})")
    return {k: (a if isinstance(a, str) else len(a)) for k, (a, _b) in checks.items()}


# ------------------------------------------------------------------ reproduction ----
def split_files(build: Any, adm: Sequence[tuple[str, str]], gate_dir: Path) -> list[Path]:  # noqa: ANN401
    from ml_route_v2.constants import HORIZONS
    from ml_route_v2.cpcv import calendar_blocks, outer_splits

    blocks = calendar_blocks(list(build.calendar))
    hs = sorted({h for _, h in adm}, key=HORIZONS.index)
    paths = [gate_dir / f"gate0B_{h}_s{s.index:02d}.npy" for h in hs for s in outer_splits(blocks)]
    missing = [p.name for p in paths if not p.is_file()]
    if missing:
        raise C1Stop(f"{MISMATCH} (OOF split files missing: {missing[:3]}, {len(missing)} in all)")
    return paths


def reproduce(build: Any, gate_dir: Path, ledger: Path) -> tuple[Any, dict[str, Any]]:  # noqa: ANN401
    """(Gate 0's B trade frame, the NG tests per h): E.12's own calls, reload only."""
    from ml_route_v2.configs import ConfigLedger
    from ml_route_v2.gate0 import _b_test, family_b_id, gate0_b_trades

    adm = tuple(tuple(map(str, p)) for p in build.filt["admissible"])
    split_files(build, adm, gate_dir)
    with no_fits() as calls:
        trades = gate0_b_trades(build.panel, ledger=ConfigLedger(ledger), state_dir=gate_dir,
                                admissible=adm if adm else None, calendar=list(build.calendar))
    if calls["fit_attempts"]:
        raise C1Stop(MISMATCH)
    tests = {}
    for h in HORIZONS_TESTED:
        tid = family_b_id(VEHICLE, h)
        sub = trades.loc[trades["test_id"] == tid]
        n_obs = int(sub["n_pair_rows"].iloc[0]) if len(sub) else 0
        tests[h] = {"test": _b_test(tid, VEHICLE, h, sub, n_obs), "trades": sub}
    return trades, tests


def oof_ng(build: Any, gate_dir: Path, h: str) -> np.ndarray:  # noqa: ANN401
    """NG's OOF predictions at h (gate0._oof, reload only)."""
    from ml_route_v2.cpcv import calendar_blocks
    from ml_route_v2.gate0 import _oof

    adm = tuple(sorted({(str(r), str(hh)) for r, hh in build.filt["admissible"]}))
    with no_fits():
        data, r_hat = _oof(build.panel, h, calendar_blocks(list(build.calendar)), gate_dir, adm)
    return r_hat[data.rows["root"].to_numpy() == VEHICLE]


def compare(rows: Mapping[str, Mapping[str, Any]], tests: Mapping[str, Any]) -> dict[str, Any]:
    out, bad = {}, []
    for h in HORIZONS_TESTED:
        t, e12 = tests[h]["test"], rows[h]
        rec: dict[str, Any] = {"e12": {}, "reproduced": {}, "abs_diff": {}}
        for key in EXACT_KEYS:
            got = getattr(t, key)
            rec["e12"][key], rec["reproduced"][key] = e12.get(key), got
            if got != e12.get(key):
                bad.append(f"{h} {key}")
        for key, attr in (*FLOAT_KEYS, *INFO_FLOAT_KEYS):
            got, want = float(getattr(t, attr)), e12.get(key)
            rec["e12"][key], rec["reproduced"][key] = want, got
            diff = abs(got - float(want)) if isinstance(want, (int, float)) else math.inf
            rec["abs_diff"][key] = diff
            if (key, attr) in FLOAT_KEYS and not diff <= REPRO_TOLERANCE:
                bad.append(f"{h} {key}")
        rec["match"] = not any(b.startswith(f"{h} ") for b in bad)
        out[h] = rec
    if bad:
        raise C1Stop(f"{MISMATCH} ({', '.join(bad)})")
    return out


def q_record(tests: Mapping[str, Any], oof: Mapping[str, np.ndarray]) -> dict[str, Any]:
    out = {}
    for h in HORIZONS_TESTED:
        r = tests[h]["trades"]["r_hat"].to_numpy(dtype=np.float64)
        if not len(r):
            raise C1Stop(f"{MISMATCH} (NG has no Gate 0 trades at {h})")
        q = float(np.min(np.abs(r)))
        out[h] = {"q": q, "q_repr": repr(q), "n_trades": int(len(r)),
                  "n_pair_rows": int(tests[h]["trades"]["n_pair_rows"].iloc[0]),
                  "n_oof_rows_at_or_above_q": int(np.sum(np.abs(oof[h]) >= q))}
    return out


# ------------------------------------------------------------------ M1 and C10 ----
def fit_m1(build: Any, h: str) -> tuple[Any, dict[str, Any]]:  # noqa: ANN401
    from ml_route_v2.configs import ridge_spec
    from ml_route_v2.constants import GATE0_RIDGE_LAMBDA
    from ml_route_v2.cpcv import horizon_data
    from ml_route_v2.models import fit_model

    adm = tuple(tuple(map(str, p)) for p in build.filt["admissible"])
    data = horizon_data(build.panel, h, adm)
    spec = ridge_spec(GATE0_RIDGE_LAMBDA)
    first = fit_model(spec, data.X, data.y)
    second = fit_model(spec, data.X, data.y)
    if first.sha256 != second.sha256:
        raise C1Stop(f"C1 STOP: M1 {h} is not deterministic (two fits, two payload sha256s)")
    return first, {"spec": first.spec.as_dict(), "payload_sha256": first.sha256,
                   "payload_bytes": len(first.payload), "n_train_rows": int(data.y.shape[0]),
                   "n_features": int(data.X.shape[1]), "refit_sha256_equal": True}


def c10_reference(panel: Any) -> dict[str, Any]:  # noqa: ANN401
    """Per h: NG's ok rows and, per signal, the count of them with app_<signal> = 1."""
    frame = panel.frame
    ng = frame["root"].to_numpy(object) == VEHICLE
    out = {}
    for h in HORIZONS_TESTED:
        sel = ng & frame[f"ok_{h}"].to_numpy(bool)
        out[h] = {"ng_ok_rows": int(sel.sum()),
                  "applicable": {s: int((frame[f"app_{s}"].to_numpy(np.float64)[sel] > 0).sum())
                                 for s in panel.signal_names}}
    return out


def write_payload(model_dir: Path, h: str, payload: bytes) -> Path:
    from ml_route_v2.phase1._io import write_atomic

    path = Path(model_dir) / payload_name(h)
    if path.exists():
        if path.read_bytes() != payload:
            raise C1Refused(f"{path} exists with other bytes; a model file is never replaced")
        return path
    write_atomic(path, payload)
    path.chmod(0o444)
    return path


def versions() -> dict[str, str]:
    import pandas
    import scipy
    import threadpoolctl

    return {"python": platform.python_version(), "numpy": np.__version__,
            "pandas": pandas.__version__, "scipy": scipy.__version__,
            "threadpoolctl": threadpoolctl.__version__}


# ------------------------------------------------------------------ the step ----
def _outside_repo(model_dir: Path) -> Path:
    from data.config import REPO_ROOT

    resolved = Path(model_dir).expanduser().resolve()
    if resolved.is_relative_to(REPO_ROOT.resolve()):
        raise C1Refused(f"--model-dir {resolved} is inside the repository; M1's payload stays "
                        "outside it")
    return resolved


def run(state: Path, manifest: Path, out: Path, model_dir: Path, *,
        manifest_sha256: str | None = None, ledger: Path | None = None,
        report: tuple[Path, str] | None = None, listed: tuple[Path, str] | None = None,
        v2: tuple[Path, str] | None = None,
        log: Callable[[str], None] = print) -> dict[str, Any]:
    """The step (module docstring). Raises C1Refused or C1Stop; returns the --out document.
    The keyword inputs default to the frozen paths and sha256s (read when the step runs)."""
    from ml_route_v2.phase1._io import now_local, write_json
    from ml_route_v2.phase1.build import load_build

    ledger = Path(ledger or ML_LEDGER)
    report = report or (E12_GATE0_REPORT, E12_GATE0_REPORT_SHA256)
    listed = listed or (E12_GATE0_LIST, E12_GATE0_LIST_SHA256)
    v2 = v2 or (V2_FREEZE_MANIFEST, V2_FREEZE_SHA256)
    out, model_dir = Path(out), _outside_repo(model_dir)
    if out.exists():
        raise C1Refused(f"{out} exists; the model record is written once")
    started = now_local()
    v2_rec = verify_v2(*v2)
    state_rec = verify_state(state, manifest, manifest_sha256)
    e12_report, e12_list = e12_facts(*report, *listed)
    rows = report_rows(e12_report)
    gate_dir = Path(state) / E12_GATE0_DIR
    build = load_build(Path(state))
    facts = check_build(build, e12_report, e12_list, gate_dir, listed[1])
    with ledger_copy(ledger) as (copy, ledger_rec):
        _trades, tests = reproduce(build, gate_dir, copy)
    if not (ledger_rec["unchanged"] and ledger_rec["copy_unchanged"]):
        raise C1Stop(f"{MISMATCH} (the ML ledger or its copy changed: {ledger_rec})")
    repro = compare(rows, tests)
    q = q_record(tests, {h: oof_ng(build, gate_dir, h) for h in HORIZONS_TESTED})
    models, m1 = {}, {}
    for h in HORIZONS_TESTED:
        models[h], m1[h] = fit_m1(build, h)
    c10 = c10_reference(build.panel)
    cols = list(build.panel.feature_cols)
    from c1_replication.evaluate import expected_feature_cols

    follows = tuple(cols) == expected_feature_cols(build.panel.signal_names)
    state_after = verify_state(state, manifest, manifest_sha256)
    for h in HORIZONS_TESTED:
        m1[h]["payload_file"] = str(write_payload(model_dir, h, models[h].payload))
    doc = {
        "schema": MODEL_SCHEMA, "test": "C1", "created_local": now_local(),
        "started_local": started, "q": q, "m1": m1, "feature_cols": cols,
        "feature_cols_sha256": feature_cols_sha256(cols), "n_feature_cols": len(cols),
        "feature_cols_follow_from_signals": follows,
        "signals": list(build.panel.signal_names), "c10_reference": c10,
        "reproduction": {"tolerance_abs": REPRO_TOLERANCE, "exact": list(EXACT_KEYS),
                         "rows": repro},
        "state": {"before": state_rec, "after": state_after},
        "e12": {"report": str(report[0]), "report_sha256": report[1], "list": str(listed[0]),
                "list_sha256": listed[1], **facts},
        "v2_freeze": v2_rec, "ml_ledger": ledger_rec, "model_dir": str(model_dir),
        "versions": versions(), "code_sha256": code_hashes(),
    }
    sha = write_json(out, doc)
    log(f"C1 q/M1: reproduced NG h60 and hF rows (n_trades, mean, t_B) within "
        f"{REPRO_TOLERANCE} absolute")
    for h in HORIZONS_TESTED:
        t = tests[h]["test"]
        log(f"  {h}: n_trades {t.n_trades}, mean {t.mean!r}, t_B {t.t!r}; q {q[h]['q_repr']}; "
            f"M1 payload sha256 {m1[h]['payload_sha256']}")
    log(f"  feature_cols {len(cols)} sha256 {doc['feature_cols_sha256']}; follow from the "
        f"covered signals by the panel rule: {follows}"
        + ("" if follows else " (WARNING: the evaluation's C11 pre-check would refuse)"))
    log(f"  ML ledger unchanged: {ledger_rec['unchanged']}; written {out} sha256 {sha}")
    return doc


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="python -m c1_replication.q_m1")
    p.add_argument("--state", required=True)
    p.add_argument("--state-manifest", required=True)
    p.add_argument("--state-manifest-sha256", default=None)
    p.add_argument("--out", required=True)
    p.add_argument("--model-dir", required=True)
    return p


def main(argv: Sequence[str] | None = None) -> int:
    from compute.platform import lower_priority

    args = _parser().parse_args(argv)
    lower_priority()
    try:
        run(Path(args.state), Path(args.state_manifest), Path(args.out),
            Path(args.model_dir), manifest_sha256=args.state_manifest_sha256)
    except C1Stop as exc:
        print(str(exc) if str(exc).startswith("C1 STOP") else f"{MISMATCH}: {exc}",
              file=sys.stderr)
        return RC_STOP
    except C1Refused as exc:
        print(f"REFUSED, nothing written: {exc}", file=sys.stderr)
        return RC_REFUSED
    return 0


if __name__ == "__main__":
    sys.exit(main())
