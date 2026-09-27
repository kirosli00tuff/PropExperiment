"""The route manifest (M5 step 5, M6, M7.6, M8) and M5 step 4 across the six candidate files.

``finalize_route(out_dir, harness_sha256)`` reads ``candidates/<challenger>_<horizon>.json`` for
both challengers and all three horizons (refusing if one is missing), keeps at most 2 rules per
cluster (ml_route.surrogate.keep_per_cluster), writes each kept rule's JSON to
``rules/<rule_sha256>.json`` and its catalog rendering to ``rules/RULES.md``, and writes
``route_manifest.json`` with: the harness sha256, the block boundaries, S_X per product, the probe
figures and the LSTM batch size, the LSTM machine record (ml_route.lstm_machine, V10-2), the
step 2 parquet sha256 every fit read (pinned to the start rule, review F-3), every
fit's model sha256 and machine (from the hash-chained
ledgers, each chain verified), the surrogate trees' hashes, trial counts per M6 (configurations,
surrogates, candidates, pre-test survivors, kept rules), the library versions and the frozen input
hashes. Returns the manifest's sha256.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path

from ml_route.constants import HORIZONS
from ml_route.ledger import Ledger, canonical, sha256_bytes, verify_chain

CHALLENGERS = ("lgbm", "lstm")


class ManifestError(RuntimeError):
    """The route cannot be finalized as asked."""


def _versions() -> dict[str, str]:
    import lightgbm
    import sklearn
    import torch

    return {"lightgbm": lightgbm.__version__, "torch": torch.__version__,
            "cuda_runtime": str(torch.version.cuda), "sklearn": sklearn.__version__}


def load_candidates(out_dir: Path) -> dict[tuple[str, str], dict]:
    found = {}
    for ch in CHALLENGERS:
        for h in HORIZONS:
            path = Path(out_dir) / "candidates" / f"{ch}_{h}.json"
            if not path.exists():
                raise ManifestError(f"REFUSED: {path.name} is missing; every challenger and "
                                    "horizon must be fitted before the route is finalized")
            found[(ch, h)] = json.loads(path.read_text(encoding="utf-8"))
    return found


def ledger_fits(out_dir: Path) -> list[dict]:
    fits = []
    for path in sorted((Path(out_dir) / "ledger").glob("*.jsonl")):
        ledger = Ledger(path)
        verify_chain(ledger)
        fits += [{"ledger": path.name, "key": r["key"], "model_sha256": r["model_sha256"],
                  "machine": r["machine"], "record_sha256": r["record_sha256"]}
                 for r in ledger.records()]
    return fits


def trial_counts(candidates: Mapping[tuple[str, str], dict], kept: list) -> dict:
    from ml_route import lgbm, lstm

    return {"configurations": {"lgbm": len(lgbm.grid()) * len(HORIZONS),
                               "lstm": len(lstm.grid()) * len(HORIZONS),
                               "total": (len(lgbm.grid()) + len(lstm.grid())) * len(HORIZONS)},
            "surrogates": sum(len(c["surrogates"]) for c in candidates.values()),
            "candidate_leaves": sum(len(c["candidates"]) for c in candidates.values()),
            "pretest_survivors": sum(len(c["survivors"]) for c in candidates.values()),
            "kept_rules": len(kept),
            "program_trials_added_at_test": len(kept)}


def store_hashes(candidates: Mapping[tuple[str, str], dict], inputs) -> dict[str, str]:  # noqa: ANN001
    """Review F-3 (b): the step 2 parquet sha256 each fit read, the same in every candidates
    file and, for real (pinned) inputs, the one each root's start rule recorded."""
    merged: dict[str, str] = {}
    for key, cand in candidates.items():
        for root, sha in cand.get("step2_store_sha256", {}).items():
            if merged.setdefault(root, sha) != sha:
                raise ManifestError(f"REFUSED: candidates {key} read another {root} step 2 "
                                    "parquet than an earlier fit")
    pinned = getattr(inputs, "step2_sha256", None)
    if pinned is not None:
        for root in inputs.traded():
            if merged.get(root) != pinned.get(root):
                raise ManifestError(f"REFUSED: {root}: the fits read step 2 parquet "
                                    f"{str(merged.get(root))[:12]}, the start rule pins "
                                    f"{str(pinned.get(root))[:12]}")
    return dict(sorted(merged.items()))


def write_route_manifest(out_dir: Path, body: dict) -> str:
    body = {**body, "manifest_body_sha256": sha256_bytes(canonical(body))}
    path = Path(out_dir) / "route_manifest.json"
    text = json.dumps(body, indent=1, sort_keys=True, default=str) + "\n"
    path.write_text(text, encoding="utf-8")
    return sha256_bytes(text.encode("utf-8"))


def finalize_route(out_dir: Path, harness_sha256: str, inputs=None, cut=None,  # noqa: ANN001
                   probes_path: Path | None = None) -> str:
    from ml_route.adapters import PROBES_PATH
    from ml_route.blocks import frozen_block_cut
    from ml_route.inputs import load_route_inputs
    from ml_route.lstm_machine import read_machine_record
    from ml_route.surrogate import keep_per_cluster, render_entry

    inputs = inputs if inputs is not None else load_route_inputs()
    cut = cut if cut is not None else frozen_block_cut()
    candidates = load_candidates(out_dir)
    for key, cand in candidates.items():
        if cand.get("harness_sha256") != harness_sha256:
            raise ManifestError(f"REFUSED: candidates {key} were made under another harness")
    survivors = [r for c in candidates.values() for r in c["survivors"]]
    kept = keep_per_cluster(survivors)
    rules_dir = Path(out_dir) / "rules"
    rules_dir.mkdir(parents=True, exist_ok=True)
    for rule in kept:
        (rules_dir / f"{rule['rule_sha256']}.json").write_text(
            json.dumps(rule, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    (rules_dir / "RULES.md").write_text("".join(render_entry(r) + "\n" for r in kept),
                                        encoding="utf-8")
    probes_file = Path(probes_path or PROBES_PATH)
    probes = json.loads(probes_file.read_text(encoding="utf-8")) if probes_file.exists() else {}
    lstm_probe = probes.get("probes", {}).get("lstm", {})
    body = {
        "stage": "E.ML-train (ml_route.manifest)",
        "harness_sha256": harness_sha256,
        "blocks": cut.as_manifest(),
        "s_x": {k: v.isoformat() for k, v in sorted(inputs.s_x.items())},
        "inputs": dict(inputs.provenance) | {"event_calendar_sha256": inputs.events.sha256,
                                             "event_calendar_source": inputs.events.source},
        "probes_file_sha256": sha256_bytes(probes_file.read_bytes()) if probes_file.exists()
        else None,
        "lstm_batch_size": lstm_probe.get("batch_probe", {}).get("batch_size"),
        "lstm_machine": read_machine_record(out_dir),  # V10-2, review NOTE-11 (None: no LSTM fit)
        "step2_store_sha256": store_hashes(candidates, inputs),  # review F-3 (b)
        "lstm_batch_probe": lstm_probe.get("batch_probe"),
        "versions": _versions(),
        "fits": ledger_fits(out_dir),
        "selected": {f"{ch}_{h}": {"config": c["selected"], "model_sha256": c["model_sha256"],
                                   "model_file": c["model_file"]}
                     for (ch, h), c in candidates.items()},
        "surrogates": {f"{ch}_{h}": [{"cluster": s["cluster"],
                                      "tree_sha256": sha256_bytes(canonical(s["tree"]))}
                                     for s in c["surrogates"]]
                       for (ch, h), c in candidates.items()},
        "trial_counts": trial_counts(candidates, kept),
        "rules": [{"rule_sha256": r["rule_sha256"], "cluster": r["cluster"],
                   "challenger": r["challenger"], "horizon": r["horizon"]} for r in kept],
    }
    return write_route_manifest(out_dir, body)
