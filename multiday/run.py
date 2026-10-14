"""The E.21 command line.

    uv run python -m multiday.run counts [--out-json ... --out-md ...]      (calendar-only)
    uv run python -m multiday.run evaluate --freeze reports/stage_e21_freeze.json \
        --freeze-sha256 <sha>
    (--input-paths <json>: the TEST MODE only: other paths per input role, each still a file of
    the freeze; a registry other than the ledger's; "plan_windows" for a stub plan resolver;
    --out-dir and --marker other than the defaults)

``evaluate``, in order (R-B3: every INPUT problem is found before the marker): 1 the freeze
manifest (its sha256, every listed file, the code and tests, every input role); 2 the registry is
ledger/trial_registrations.jsonl and holds E21-T1..E21-T4 together under label E21 and this
freeze's sha256; 3 the output is free (no marker reports/stage_e21_RUN_ONCE.json, no result in
reports/stage_e21_runs/); 4 the run manifest (its sha256 from the freeze, a step 2 and an ext2010
store for each of the 17 roots), the whole context (calendars with their pins, the settlement
table, the windows, the EC-AUC and release rows, the touch report), each root's store preflight
(no row read) and H2's result (status complete, its pinned sha256); 5 the marker (O_EXCL) BEFORE
any bar is read; 6 the run, one root at a time at nice 10. Exit 2: refused (nothing written, no
bar read). Exit 0: complete. Exit 1: STOPPED after the marker (the attempt is closed).
"""

from __future__ import annotations

import argparse
import contextlib
import json
import os
import sys
import traceback
from datetime import date, datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from base_rules import guards as BG
from base_rules import hist_plan as HP
from base_rules.context import context_from_freeze, make_context, starts_for, store_loader
from base_rules.store import EXT2010, STEP2_ERA, load_manifest, preflight
from multiday import constants as K
from multiday import freeze_manifest as FM
from multiday.combine import h2_component
from multiday.evaluate import evaluate
from multiday.stats import dsr_at_n, verdict

RESULT_NAMES = ("T1_result.json", "T2_result.json", "T3_result.json", "T4_result.json",
                "verdict.json", "summary.md", "per_root")


class Refused(RuntimeError):
    """A precondition failed: nothing was written and no bar was read."""


def _now() -> str:
    return datetime.now(ZoneInfo("America/Vancouver")).isoformat(timespec="seconds")


def _input_paths(a: argparse.Namespace) -> dict | None:
    if not getattr(a, "input_paths", None):
        return None
    return json.loads(Path(a.input_paths).read_text(encoding="utf-8"))


def _resolver(paths: dict | None) -> HP.Resolver:
    stub = (paths or {}).get("plan_windows")
    if not stub:
        return HP.default_resolver
    windows = {k: HP.PlanWindow(k, date.fromisoformat(v[0]), date.fromisoformat(v[1]))
               for k, v in stub.items()}
    return lambda plan: windows[plan] if plan in windows else HP.default_resolver(plan)


def e21_starts(windows_starts: dict[str, date]) -> dict[str, date]:
    """Window starts: the run context's (windows file or fallback), floored by R-S3 (LE)."""
    out = dict(windows_starts)
    for r, floor in K.WINDOW_START_FLOOR.items():
        if r in out:
            out[r] = max(out[r], floor)
    return out


def write_marker(path: Path, record: dict[str, Any]) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    body = json.dumps({"schema": K.MARKER_SCHEMA, "written_local": _now(), **record},
                      indent=1, default=str).encode()
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o444)
    except FileExistsError as exc:
        raise Refused(f"run-once marker {path} exists: E.21 runs once, never again") from exc
    with os.fdopen(fd, "wb") as fh:
        fh.write(body)
    return path


def preconditions(a: argparse.Namespace) -> dict[str, Any]:
    """Steps 1-4 of the module docstring; raises on any problem (nothing written)."""
    paths = _input_paths(a)
    test_mode = paths is not None
    out_dir, marker = Path(a.out_dir), Path(a.marker)
    if not test_mode and (out_dir.resolve() != K.repo_path(K.OUT_DIR).resolve()
                          or marker.resolve() != K.repo_path(K.MARKER_PATH).resolve()):
        raise Refused("--out-dir and --marker are fixed outside the test mode")
    freeze = FM.verify(Path(a.freeze), a.freeze_sha256, input_overrides=paths)
    if not test_mode:  # outside the test mode every input is the spec's own file
        for role, default in FM.input_roles().items():
            got = Path(freeze["inputs"][role]["path"]).resolve()
            if got != K.repo_path(default).resolve():
                raise Refused(f"input {role} is {got}, not {default} (test mode only)")
    registry = BG.check_registry_path(Path(a.registry), test_mode)
    from screening.trial_registry import TrialRegistryError, require_registered

    try:
        reg = require_registered(list(K.TEST_IDS.values()), test=K.REGISTRY_TEST,
                                 freeze_sha256=a.freeze_sha256, path=Path(a.registry))
    except TrialRegistryError as exc:
        raise Refused(str(exc)) from exc
    if marker.exists():
        raise Refused(f"run-once marker {marker} exists: E.21 runs once, never again")
    taken = [n for n in RESULT_NAMES if (out_dir / n).exists()]
    if taken:
        raise Refused(f"the output path {out_dir} already holds {taken}")
    inputs = freeze["inputs"]
    manifest = load_manifest(Path(inputs["run_manifest"]["path"]),
                             inputs["run_manifest"]["sha256"])
    for r in K.ROOTS:
        refs = manifest.stores.get(r)
        if refs is None or refs.get(STEP2_ERA) is None:
            raise Refused(f"the run manifest has no step 2 store for {r}")
        if refs.get(EXT2010) is None and not test_mode:
            raise Refused(f"the run manifest has no ext2010 store for {r} (F1)")
    resolver = _resolver(paths)
    ctx = context_from_freeze({"inputs": inputs}, manifest, resolver)
    ctx.starts = e21_starts(dict(ctx.starts))
    stores = []
    for r in K.ROOTS:
        cals = ctx.cal(r)
        stores += preflight(r, manifest.stores[r], {EXT2010: cals.hist, STEP2_ERA: cals.frozen},
                            resolver)
    h2_sha = inputs["h2_result"]["sha256"]
    if not test_mode and h2_sha != K.H2_RESULT_SHA256:
        raise Refused(f"H2's result in the freeze is not the pinned {K.H2_RESULT_SHA256[:12]}...")
    h2 = h2_component(Path(inputs["h2_result"]["path"]), h2_sha)
    return {"ctx": ctx, "h2": h2, "registry": registry, "registration": reg.get("entry_id"),
            "manifest_sha256": manifest.sha256, "stores": stores, "out_dir": out_dir,
            "marker": marker, "registry_path": Path(a.registry)}


def cmd_evaluate(a: argparse.Namespace) -> int:
    with contextlib.suppress(OSError):
        os.nice(10)
    try:
        pre = preconditions(a)
    except Exception as exc:  # noqa: BLE001 - every precondition refuses
        print(f"REFUSED: {type(exc).__name__}: {exc}", file=sys.stderr)
        return K.RC_REFUSED
    header = {"test_ids": dict(K.TEST_IDS), "freeze_sha256": a.freeze_sha256,
              "registration": pre["registration"], "registry": pre["registry"],
              "manifest_sha256": pre["manifest_sha256"], "started_local": _now()}
    write_marker(pre["marker"], {**header, "preflight": pre["stores"]})
    out_dir: Path = pre["out_dir"]
    try:
        res = evaluate(pre["ctx"], pre["h2"])
        write_outputs(res, out_dir, header, pre["registry_path"])
        print(f"E.21 evaluate: complete -> {out_dir}")
        return K.RC_OK
    except Exception as exc:  # noqa: BLE001 - after the marker every error closes the attempt
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "STOPPED.json").write_text(json.dumps({
            "schema": K.RESULT_SCHEMA, **header, "status": "STOPPED", "error": repr(exc),
            "traceback": traceback.format_exc()[-4000:]}, indent=1) + "\n")
        print(f"E.21 evaluate: STOPPED ({exc!r})", file=sys.stderr)
        return K.RC_STOPPED


def write_outputs(res, out_dir: Path, header: dict, registry: Path) -> None:  # noqa: ANN001
    from screening.trial_registry import current_n

    out_dir.mkdir(parents=True, exist_ok=True)
    recs = {}
    for t, out in res.tests.items():
        rec = {"schema": K.RESULT_SCHEMA, **header, "status": "complete",
               "finished_local": _now(), **out.record()}
        if t == "T1":
            rec["notes"] = {**rec["notes"], "run": res.notes}
        recs[t] = rec
        (out_dir / f"{t}_result.json").write_text(json.dumps(rec, indent=1, default=str) + "\n")
    roots_dir = out_dir / "per_root"
    roots_dir.mkdir(exist_ok=True)
    for r, row in res.roots.items():
        (roots_dir / f"{r}.json").write_text(json.dumps(row, indent=1, default=str) + "\n")
    base = {t: r["stats"][K.BASE] for t, r in recs.items()}
    boots = {t: r["sharpe_ci95_base"] for t, r in recs.items()}
    n_trials = current_n(registry)
    v = {"schema": K.VERDICT_SCHEMA, **header, "written_local": _now(),
         "n_trials_at_verdict": n_trials, "expected_n": K.EXPECTED_N_AFTER,
         **verdict(base, boots),
         "reported_cases": {t: {c: {k: r["stats"][c].get(k) for k in
                                    ("n", "mean", "t", "p", "sharpe_annualized")}
                                for c in (K.STRESS, K.SLIP150)} for t, r in recs.items()},
         "dsr_descriptive": dsr_at_n({t: [x for _, x in res.tests[t].series[K.BASE]]
                                      for t in res.tests}, n_trials),
         "result_sha256": {t: BG.sha256_file(out_dir / f"{t}_result.json") for t in recs}}
    (out_dir / "verdict.json").write_text(json.dumps(v, indent=1, default=str) + "\n")
    (out_dir / "summary.md").write_text(summary_md(v, recs))


def summary_md(v: dict, recs: dict) -> str:
    lines = ["# Stage E.21 evaluation (one run)", "",
             f"Holm at family alpha {v['holm_alpha']} over the four tests; PASS iff Holm rejects "
             f"and the annualized net Sharpe >= {v['sharpe_bar']}. N at the verdict: "
             f"{v['n_trials_at_verdict']} (expected {v['expected_n']}).", "",
             "| Test | n | mean | t | t_NW | p | Sharpe | 95% CI | Holm | PASS |",
             "|---|---|---|---|---|---|---|---|---|---|"]

    def f(x: Any, d: int = 3) -> str:
        return "n/a" if x is None else f"{x:.{d}f}" if isinstance(x, float) else str(x)

    for t, row in v["tests"].items():
        ci = row.get("sharpe_ci95") or {}
        lines.append(f"| {t} | {row['n']} | {f(row['mean'], 6)} | {f(row['t'])} | "
                     f"{f(row['t_nw'])} | {f(row['p'], 4)} | {f(row['sharpe_annualized'])} | "
                     f"[{f(ci.get('lo'))}, {f(ci.get('hi'))}] | "
                     f"{row['checks']['holm_rejects']} | {row['pass']} |")
    lines += ["", "Reported only (stress, 1.5 x slippage), costs as a share of gross:", ""]
    for t, rec in recs.items():
        gc = rec.get("gross_costs", {}).get(K.BASE, {})
        rc = v["reported_cases"][t]
        lines.append(f"- {t}: stress Sharpe {f(rc['stress']['sharpe_annualized'])}, slip150 "
                     f"Sharpe {f(rc['slip150']['sharpe_annualized'])}, base costs/gross "
                     f"{f(gc.get('costs_share_of_gross'))}")
    return "\n".join(lines) + "\n"


def cmd_counts(a: argparse.Namespace) -> int:
    """Calendar-only counts (no bar row): reads calendars, the settlement table, the windows, the
    release rows and the stores' metadata (preflight)."""
    from base_rules.auctions import load_auctions
    from base_rules.calendars import load_calendars
    from base_rules.inputs import load_settlement, load_windows
    from multiday.counts import calendar_counts, counts_md, metadata_blackout

    with contextlib.suppress(OSError):
        os.nice(10)
    paths = _input_paths(a) or {}
    inp = FM.resolve_inputs(paths)
    cals = load_calendars(hist_dir=inp["hist_calendar_equity"].parent,
                          livestock_path=inp["livestock_hist"])
    st = load_settlement(inp["settlement"])
    windows = load_windows(inp["windows"])
    auctions, _ = load_auctions(inp["ecauc_hist"], inp["release_frozen"],
                                inp["ecauc_announcements"])
    manifest = load_manifest(inp["run_manifest"], BG.sha256_file(inp["run_manifest"]))
    resolver = _resolver(paths)
    ctx = make_context(cals, st, e21_starts(starts_for(manifest, windows)),
                       store_loader(manifest, cals, resolver), tuple(auctions), None,
                       {"frozen_path": inp["release_frozen"], "hist_path": inp["release_hist"],
                        "auctions_path": inp["ecauc_hist"]})
    blackouts, splices = {}, {}
    for r in K.ROOTS:
        blackouts[r], splices[r] = metadata_blackout(ctx, manifest, r, resolver)
    out = {"schema": K.COUNTS_SCHEMA, "written_local": _now(),
           "inputs": {r: [BG.rel(p), BG.sha256_file(p)] for r, p in inp.items()
                      if r not in ("spec", "prereg") and p.is_file()},
           "assumption": "a required bar is present inside its trade date's open intervals",
           "splice_trade_dates": splices,
           "blackout_dates": {r: len(b) for r, b in blackouts.items()},
           "counts": calendar_counts(ctx, blackouts)}
    Path(a.out_json).write_text(json.dumps(out, indent=1, default=str) + "\n")
    Path(a.out_md).write_text(counts_md(out))
    print(f"counts -> {a.out_json}, {a.out_md}")
    return K.RC_OK


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="multiday.run")
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("counts")
    c.add_argument("--out-json", default=str(K.repo_path(K.COUNTS_JSON)))
    c.add_argument("--out-md", default=str(K.repo_path(K.COUNTS_MD)))
    c.add_argument("--input-paths")
    e = sub.add_parser("evaluate")
    for name in ("--freeze", "--freeze-sha256"):
        e.add_argument(name, required=True)
    e.add_argument("--out-dir", default=str(K.repo_path(K.OUT_DIR)))
    e.add_argument("--marker", default=str(K.repo_path(K.MARKER_PATH)))
    e.add_argument("--registry", default=str(K.repo_path(K.REGISTRY_PATH)))
    e.add_argument("--input-paths")
    a = ap.parse_args(argv)
    return {"counts": cmd_counts, "evaluate": cmd_evaluate}[a.cmd](a)


if __name__ == "__main__":
    raise SystemExit(main())
