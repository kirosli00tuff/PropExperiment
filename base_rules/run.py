"""The E.17 command line of the base-rule tests (one command per test). E.16 never runs ``run``.

    uv run python -m base_rules.run run --test H1 --freeze reports/stage_e16_freeze.json \
        --freeze-sha256 <sha> --manifest <run manifest> --manifest-sha256 <sha>
    uv run python -m base_rules.run run --test H5 --freeze ... --freeze-sha256 <sha>
    uv run python -m base_rules.run verdict --freeze ... --freeze-sha256 <sha>
    (--input-paths <json role -> path>: other paths for the inputs; each must be a freeze file)
    uv run python -m base_rules.report counts|release-touch ...   (calendar-only, no bar)

``run``, in order (R-B3: every INPUT problem is found before the marker, so a run that writes
its marker cannot be lost to a predictable refusal): 1 the freeze manifest (sha256, every listed
file, the code, every input role); 2 the registration (E16-Hx in ledger/trial_registrations.jsonl);
3 the output path is free (no marker, no result file of the test); 4 H5: the four complete
component results; H1-H4: the run manifest (sha256, a store per product), then every store the
test reads is preflighted without reading a row (path layout and refusals, existence, sha256,
parquet metadata, rolls booked), then the whole context is built (calendars with their pins, the
settlement table, the windows, the EC-AUC rows, the release rows and the touch report); then the
marker is written (O_EXCL) BEFORE any bar is read; then the run, in which no DATA condition
raises (a refused store, a contract change, a missing bar: excluded and counted). Exit 2:
refused, nothing written. Exit 0: complete. Exit 1: STOPPED after the marker (only a code
invariant can cause it; the attempt is closed, never rerun).
"""

from __future__ import annotations

import argparse
import json
import sys
import traceback
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from base_rules import constants as K
from base_rules import guards as G
from base_rules import hist_plan as HP
from base_rules import results as R
from base_rules.common import RunOutput
from base_rules.context import context_from_freeze
from base_rules.h2 import run_h2
from base_rules.h3 import run_h3
from base_rules.h5 import combine
from base_rules.intraday import run_intraday
from base_rules.store import EXT2010, STEP2_ERA, load_manifest, preflight

PRODUCTS_READ = {"H1": K.PRODUCTS, "H4": K.PRODUCTS, "H2": K.H2_LEGS,
                 "H3": tuple(sorted(set(K.H3_TENOR_ROOT.values())))}


def _now() -> str:
    return datetime.now(ZoneInfo("America/Vancouver")).isoformat(timespec="seconds")


def run_test(test: str, ctx) -> RunOutput:  # noqa: ANN001
    if test in K.INTRADAY_TESTS:
        return run_intraday(test, ctx)
    if test == "H2":
        return run_h2(ctx)
    if test == "H3":
        return run_h3(ctx)
    raise ValueError(f"{test} is not a bar-reading test")


def _components(out_dir: Path, freeze_sha: str) -> dict:
    comps, record = {}, {}
    for name in K.H5_COMPONENTS:
        path = R.result_path(out_dir, name)
        if not path.is_file():
            raise G.Refused(f"H5 needs {name}'s complete result ({path} is missing)")
        rec = json.loads(path.read_text(encoding="utf-8"))
        if rec.get("status") != "complete" or rec.get("freeze_sha256") != freeze_sha:
            raise G.Refused(f"{name}'s result is not complete under this freeze")
        comps[name] = R.component_from_record(rec)
        record[name] = {"path": G.rel(path), "sha256": G.sha256_file(path)}
    return {"components": comps, "record": record}


def cmd_run(a: argparse.Namespace) -> int:
    out_dir = Path(a.out_dir)
    try:
        freeze = G.check_freeze(Path(a.freeze), a.freeze_sha256,
                                input_paths=_input_paths(a))
        registry = G.check_registry_path(Path(a.registry), _input_paths(a) is not None)
        reg = G.check_registered(a.test, freeze, Path(a.registry), a.freeze_sha256)
        G.refuse_if_marked(out_dir, a.test)
        if R.result_path(out_dir, a.test).exists() or R.units_path(out_dir, a.test).exists():
            raise G.Refused(f"{a.test}: a result file already exists in {out_dir}")
        manifest = comps = ctx = None
        if a.test == "H5":
            comps = _components(out_dir, a.freeze_sha256)
        else:
            if not a.manifest or not a.manifest_sha256:
                raise G.Refused(f"{a.test} needs --manifest and --manifest-sha256")
            manifest = load_manifest(Path(a.manifest), a.manifest_sha256)
            missing = [p for p in K.PRODUCTS if p not in manifest.stores]
            if missing:
                raise G.Refused(f"the run manifest has no stores for {missing}")
            resolver = _resolver(a)
            ctx = context_from_freeze(freeze, manifest, resolver)
            for p in PRODUCTS_READ[a.test]:
                cals = ctx.cal(p)
                preflight(p, manifest.stores[p], {EXT2010: cals.hist, STEP2_ERA: cals.frozen},
                          resolver)
    except (G.Refused, Exception) as exc:  # noqa: BLE001 - every precondition refuses
        print(f"REFUSED: {exc}", file=sys.stderr)
        return K.RC_REFUSED
    header = {"test_id": freeze["test_ids"][a.test], "freeze_sha256": a.freeze_sha256,
              "registration": reg.get("entry_id"), "registry": registry,
              "manifest_sha256": a.manifest_sha256, "started_local": _now()}
    G.write_marker(out_dir, a.test, {**header, "components": comps and comps["record"]})
    try:
        if a.test == "H5":
            out = combine(comps["components"])
        else:
            out = run_test(a.test, ctx)
            out.notes["release_rules"] = ctx.releases.record
            out.notes["window_starts"] = {p: str(d) for p, d in ctx.starts.items()}
        R.write(out, out_dir, {**header, "status": "complete", "finished_local": _now(),
                               "components": comps and comps["record"]})
        print(f"{a.test}: complete -> {R.result_path(out_dir, a.test)}")
        return K.RC_OK
    except Exception as exc:  # noqa: BLE001 - after the marker every error closes the attempt
        R.result_path(out_dir, a.test).write_text(json.dumps({
            "schema": K.RESULT_SCHEMA, **header, "test": a.test, "status": "STOPPED",
            "error": repr(exc), "traceback": traceback.format_exc()[-4000:]}, indent=1) + "\n")
        print(f"{a.test}: STOPPED ({exc!r})", file=sys.stderr)
        return K.RC_STOPPED


def cmd_verdict(a: argparse.Namespace) -> int:
    from base_rules.stats import verdict
    from screening.trial_registry import current_n

    try:
        G.check_freeze(Path(a.freeze), a.freeze_sha256, input_paths=_input_paths(a))
        registry = G.check_registry_path(Path(a.registry), _input_paths(a) is not None)
        recs = {}
        for t in K.TESTS:  # F-03: the family is the five registered tests, no subset
            rec = json.loads(R.result_path(Path(a.out_dir), t).read_text(encoding="utf-8"))
            if rec.get("status") != "complete" or rec.get("freeze_sha256") != a.freeze_sha256:
                raise G.Refused(f"{t}'s result is not complete under this freeze")
            recs[t] = rec
        n_trials = current_n(Path(a.registry))
    except Exception as exc:  # noqa: BLE001
        print(f"REFUSED: {exc}", file=sys.stderr)
        return K.RC_REFUSED
    stats = {t: r["stats"] for t, r in recs.items()}
    series = {t: [v for _, v in r["series"][K.BASE]] for t, r in recs.items()}
    out = {"schema": K.VERDICT_SCHEMA, "written_local": _now(), "n_trials_at_verdict": n_trials,
           "registered_tests": list(K.TESTS), "registry": registry,
           "result_sha256": {t: G.sha256_file(R.result_path(Path(a.out_dir), t))
                             for t in K.TESTS},
           **verdict(stats, n_trials, series)}
    path = Path(a.out_dir) / "verdict.json"
    path.write_text(json.dumps(out, indent=1, default=str) + "\n", encoding="utf-8")
    print(f"verdict -> {path}")
    return K.RC_OK


def _input_paths(a: argparse.Namespace) -> dict | None:
    """The TEST MODE (tests and the synthetic probe only): other paths per input role, each still
    a file of the freeze; a registry other than the ledger's; plan windows for a plan the harness
    does not know yet ("plan_windows": {plan: [first, last]})."""
    if not getattr(a, "input_paths", None):
        return None
    return json.loads(Path(a.input_paths).read_text(encoding="utf-8"))


def _resolver(a: argparse.Namespace) -> HP.Resolver:
    stub = (_input_paths(a) or {}).get("plan_windows")
    if not stub:
        return HP.default_resolver
    windows = {k: HP.PlanWindow(k, date.fromisoformat(v[0]), date.fromisoformat(v[1]))
               for k, v in stub.items()}
    return lambda plan: windows[plan] if plan in windows else HP.default_resolver(plan)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="base_rules.run")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--test", required=True, choices=K.TESTS)
    for name in ("--freeze", "--freeze-sha256"):
        r.add_argument(name, required=True)
    r.add_argument("--manifest")
    r.add_argument("--manifest-sha256")
    r.add_argument("--out-dir", default=str(K.repo_path(K.OUT_DIR)))
    r.add_argument("--registry", default=str(K.repo_path(K.REGISTRY_PATH)))
    r.add_argument("--input-paths")
    v = sub.add_parser("verdict")
    for name in ("--freeze", "--freeze-sha256"):
        v.add_argument(name, required=True)
    v.add_argument("--out-dir", default=str(K.repo_path(K.OUT_DIR)))
    v.add_argument("--registry", default=str(K.repo_path(K.REGISTRY_PATH)))
    v.add_argument("--input-paths")
    a = ap.parse_args(argv)
    return {"run": cmd_run, "verdict": cmd_verdict}[a.cmd](a)


if __name__ == "__main__":
    raise SystemExit(main())
