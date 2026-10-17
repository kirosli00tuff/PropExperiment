"""The E.23 command line (lead_spec section 8), modelled on multiday.run.

    uv run python -m trigger_hold.run power [--config ...] [--out reports/stage_e23_power.json]
        (events + calendars + store METADATA only: no bar row, no price)
    uv run python -m trigger_hold.run evaluate --phase discovery|confirmation \
        --freeze reports/stage_e23_freeze.json --freeze-sha256 <sha>
    (--input-paths <json>: the TEST MODE only: other paths per input role, each still a file
    of the freeze; a registry other than the ledger's; --out-dir and --marker elsewhere)

``evaluate``, in order (every INPUT problem is found before the marker): 1 the freeze (its
sha256, every listed file, the code and tests, every input role, every events and trend file);
2 the config (schema, at most 24 trigger-holds, the freeze's ids); 3 the registry is
ledger/trial_registrations.jsonl and holds every config id together under label E23 and this
freeze's sha256; 4 the output is free (no marker, no result); confirmation: the discovery result
exists (its sha256 goes into the marker) and its survivors re-derive by code; 5 the run
manifest (a step 2 and an ext2010 store for every config root), the context, every needed
root's store preflight (no row read), the power table (the freeze's file); 6 the marker
reports/stage_e23_RUN_ONCE_<phase>.json (O_EXCL) BEFORE any bar is read; 7 the computation, one
root at a time at nice 10. Exit 2: refused (nothing written, no bar read). Exit 0: complete.
Exit 1: STOPPED after the marker (the attempt is closed; never rerun).
"""

from __future__ import annotations

import argparse
import contextlib
import json
import os
import sys
import traceback
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from base_rules import guards as BG
from base_rules import hist_plan as HP
from base_rules.store import EXT2010, STEP2_ERA, load_manifest, preflight
from trigger_hold import constants as K
from trigger_hold import freeze_manifest as FM

RESULT_NAME = {"discovery": "discovery_result.json", "confirmation": "confirmation_result.json"}
PHASES = ("discovery", "confirmation")


class Refused(RuntimeError):
    """A precondition failed: nothing was written and no bar was read."""


def _now() -> str:
    return datetime.now(ZoneInfo("America/Vancouver")).isoformat(timespec="seconds")


def _input_paths(a: argparse.Namespace) -> dict | None:
    if not getattr(a, "input_paths", None):
        return None
    return json.loads(Path(a.input_paths).read_text(encoding="utf-8"))


def write_marker(path: Path, record: dict[str, Any]) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    body = json.dumps({"schema": K.MARKER_SCHEMA, "written_local": _now(), **record},
                      indent=1, default=str).encode()
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o444)
    except FileExistsError as exc:
        raise Refused(f"run-once marker {path} exists: this phase runs once, never again") \
            from exc
    with os.fdopen(fd, "wb") as fh:
        fh.write(body)
    return path


def check_output_free(marker: Path, out_dir: Path, phase: str) -> None:
    if Path(marker).exists():
        raise Refused(f"run-once marker {marker} exists: this phase runs once, never again")
    taken = [n for n in (RESULT_NAME[phase], "STOPPED.json") if (Path(out_dir) / n).exists()]
    if taken:
        raise Refused(f"the output path {out_dir} already holds {taken}")


def _fixed_paths(a: argparse.Namespace, test_mode: bool) -> tuple[Path, Path]:
    out_dir, marker = Path(a.out_dir), Path(a.marker)
    if not test_mode and (out_dir.resolve() != K.repo_path(K.OUT_DIRS[a.phase]).resolve()
                          or marker.resolve() != K.repo_path(K.MARKERS[a.phase]).resolve()):
        raise Refused("--out-dir and --marker are fixed outside the test mode")
    return out_dir, marker


def _discovery_input(a: argparse.Namespace, test_mode: bool) -> tuple[dict, str]:
    path = Path(a.discovery_result) if test_mode and a.discovery_result else \
        K.repo_path(K.OUT_DIRS["discovery"]) / RESULT_NAME["discovery"]
    if not path.is_file():
        raise Refused(f"confirmation needs the discovery result {path}")
    rec = json.loads(path.read_text())
    if rec.get("status") != "complete" or rec.get("phase") != "discovery":
        raise Refused(f"{path} is not a complete discovery result")
    return rec, BG.sha256_file(path)


def preconditions(a: argparse.Namespace) -> dict[str, Any]:
    """Steps 1-5 of the module docstring; raises on any problem (nothing written)."""
    from base_rules.context import context_from_freeze
    from multiday.run import e21_starts
    from screening.trial_registry import TrialRegistryError, require_registered
    from trigger_hold.config import load_config
    from trigger_hold.evaluate import survivors_from

    if a.phase not in PHASES:
        raise Refused(f"--phase must be one of {PHASES}")
    paths = _input_paths(a)
    test_mode = paths is not None
    out_dir, marker = _fixed_paths(a, test_mode)
    freeze = FM.verify(Path(a.freeze), a.freeze_sha256, input_overrides=paths)
    inputs = freeze["inputs"]
    real_manifest = K.repo_path(K.RUN_MANIFEST_PATH).resolve()
    if test_mode and Path(inputs["run_manifest"]["path"]).resolve() == real_manifest:
        raise Refused("the test mode cannot use the real run manifest (review C-01)")
    if not test_mode:
        for role, default in FM.input_roles().items():
            if Path(inputs[role]["path"]).resolve() != K.repo_path(default).resolve():
                raise Refused(f"input {role} is not {default} (test mode only)")
    cfg = load_config(Path(inputs["config"]["path"]))
    if sorted(cfg.ids) != sorted(freeze["test_ids"]):
        raise Refused("the config's ids are not the freeze's ids")
    registry = BG.check_registry_path(Path(a.registry), test_mode)
    try:
        reg = require_registered(cfg.ids, test=K.REGISTRY_TEST, freeze_sha256=a.freeze_sha256,
                                 path=Path(a.registry))
    except TrialRegistryError as exc:
        raise Refused(str(exc)) from exc
    check_output_free(marker, out_dir, a.phase)
    disc, disc_sha = (None, None)
    if a.phase == "confirmation":
        disc, disc_sha = _discovery_input(a, test_mode)
        survivors_from(disc, cfg)
    power = json.loads(Path(inputs["power"]["path"]).read_text())
    if power.get("schema") != K.POWER_SCHEMA or set(power.get("rows", {})) != set(cfg.ids):
        raise Refused("the power table does not cover exactly the config's trigger-holds")
    if not test_mode:  # review C-04: the power table came from these frozen events and config
        for p in cfg.event_paths():
            if power.get("events_sha256", {}).get(str(p)) != BG.sha256_file(K.repo_path(p)):
                raise Refused(f"the power table's events sha256 for {p} is not the frozen file's")
        if (power.get("config") or [None, None])[1] != inputs["config"]["sha256"]:
            raise Refused("the power table's config sha256 is not the frozen config's")
    manifest = load_manifest(Path(inputs["run_manifest"]["path"]),
                             inputs["run_manifest"]["sha256"])
    for r in cfg.roots:
        refs = manifest.stores.get(r)
        if refs is None or refs.get(STEP2_ERA) is None or refs.get(EXT2010) is None:
            raise Refused(f"the run manifest lacks a store era for {r}")
    ctx = context_from_freeze({"inputs": inputs}, manifest, HP.default_resolver)
    ctx.starts = e21_starts(dict(ctx.starts))
    if a.phase == "discovery":
        ctx.last = K.W_EXT_LAST  # no W_cf mark is computed in discovery (Q6)
    stores = []
    for r in cfg.roots:
        cals = ctx.cal(r)
        stores += preflight(r, manifest.stores[r], {EXT2010: cals.hist, STEP2_ERA: cals.frozen},
                            HP.default_resolver)
    return {"ctx": ctx, "cfg": cfg, "power": power, "disc": disc, "disc_sha256": disc_sha,
            "registry": registry, "registration": reg.get("entry_id"),
            "manifest_sha256": manifest.sha256, "stores": stores, "out_dir": out_dir,
            "marker": marker, "registry_path": Path(a.registry),
            "trend_dir": Path(freeze["trend_dir"])}


def compute(pre: dict[str, Any], phase: str) -> dict[str, Any]:
    from screening.trial_registry import current_n
    from trigger_hold.evaluate import confirmation, discovery

    n_trials = current_n(pre["registry_path"])
    if phase == "discovery":
        return discovery(pre["ctx"], pre["cfg"], pre["power"], n_trials,
                         trend_dir=pre["trend_dir"])
    return confirmation(pre["ctx"], pre["cfg"], pre["power"], pre["disc"], n_trials,
                        trend_dir=pre["trend_dir"])


def run_phase(a: argparse.Namespace, *, pre_fn: Callable[[argparse.Namespace], dict] =
              preconditions, compute_fn: Callable[[dict, str], dict] = compute) -> int:
    with contextlib.suppress(OSError):
        os.nice(10)
    try:
        pre = pre_fn(a)
    except Exception as exc:  # noqa: BLE001 - every precondition refuses
        print(f"REFUSED: {type(exc).__name__}: {exc}", file=sys.stderr)
        return K.RC_REFUSED
    header = {"phase": a.phase, "test_ids": pre["cfg"].ids, "freeze_sha256": a.freeze_sha256,
              "registration": pre["registration"], "registry": pre["registry"],
              "manifest_sha256": pre["manifest_sha256"], "started_local": _now(),
              "discovery_result_sha256": pre.get("disc_sha256")}
    try:
        write_marker(pre["marker"], {**header, "preflight": pre["stores"]})
    except Refused as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return K.RC_REFUSED
    out_dir: Path = pre["out_dir"]
    try:
        res = compute_fn(pre, a.phase)
        out_dir.mkdir(parents=True, exist_ok=True)
        rec = {"schema": K.RESULT_SCHEMA, **header, "status": "complete",
               "finished_local": _now(), **res}
        (out_dir / RESULT_NAME[a.phase]).write_text(json.dumps(rec, indent=1, default=str)
                                                    + "\n")
        print(f"E.23 {a.phase}: complete -> {out_dir}")
        return K.RC_OK
    except Exception as exc:  # noqa: BLE001 - after the marker every error closes the attempt
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "STOPPED.json").write_text(json.dumps({
            "schema": K.RESULT_SCHEMA, **header, "status": "STOPPED", "error": repr(exc),
            "traceback": traceback.format_exc()[-4000:]}, indent=1, default=str) + "\n")
        print(f"E.23 {a.phase}: STOPPED ({exc!r})", file=sys.stderr)
        return K.RC_STOPPED


# ------------------------------------------------------------------ power (no price) ----
def power_table(config_path: Path, overrides: dict | None = None) -> dict[str, Any]:
    """Section 5 from events, calendars and the stores' metadata only (preflight; no row)."""
    from base_rules.auctions import load_auctions
    from base_rules.calendars import load_calendars
    from base_rules.context import make_context, starts_for, store_loader
    from base_rules.inputs import load_settlement, load_windows
    from multiday.counts import metadata_blackout
    from multiday.run import e21_starts
    from trigger_hold.config import load_config
    from trigger_hold.power import power_row
    from trigger_hold.units import CalendarMarks, window_for

    inp = FM.resolve_inputs(overrides)
    cfg = load_config(config_path)
    cals = load_calendars(hist_dir=inp["hist_calendar_equity"].parent,
                          livestock_path=inp["livestock_hist"])
    st = load_settlement(inp["settlement"])
    windows = load_windows(inp["windows"])
    auctions, _ = load_auctions(inp["ecauc_hist"], inp["release_frozen"],
                                inp["ecauc_announcements"])
    manifest = load_manifest(inp["run_manifest"], BG.sha256_file(inp["run_manifest"]))
    ctx = make_context(cals, st, e21_starts(starts_for(manifest, windows)),
                       store_loader(manifest, cals), tuple(auctions), None,
                       {"frozen_path": inp["release_frozen"], "hist_path": inp["release_hist"],
                        "auctions_path": inp["ecauc_hist"]})
    k = len(cfg.rows)
    srcs, rows, files = {}, {}, {}
    for th in cfg.rows:
        if th.root not in srcs:
            blackout, _ = metadata_blackout(ctx, manifest, th.root)
            srcs[th.root] = CalendarMarks(ctx, th.root, blackout)
        src = srcs[th.root]
        rows[th.id] = {}
        for w in K.WINDOW_NAMES:
            ev = th.events_file(w)
            if ev is None:
                rows[th.id][w] = None
                continue
            files[th.events[w]] = BG.sha256_file(K.repo_path(th.events[w]))
            rows[th.id][w] = power_row(src, ev.events, window_for(src, w, th.s_x), m=th.m,
                                       h=th.h, k_family=k)
    return {"schema": K.POWER_SCHEMA, "written_local": _now(), "k_family": k,
            "config": [BG.rel(config_path), BG.sha256_file(config_path)],
            "events_sha256": files, "true_sharpe": K.POWER_TRUE_SHARPE,
            "basis": "events, calendars, the settlement table and store metadata; no bar row, "
                     "no price", "rows": rows}


def cmd_power(a: argparse.Namespace) -> int:
    with contextlib.suppress(OSError):
        os.nice(10)
    out = Path(a.out)
    if out.exists():
        print(f"REFUSED: {out} exists (the power table is written once)", file=sys.stderr)
        return K.RC_REFUSED
    tab = power_table(Path(a.config), _input_paths(a))
    out.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(out, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    with os.fdopen(fd, "w") as fh:
        fh.write(json.dumps(tab, indent=1, default=str) + "\n")
    n_inc = sum(1 for r in tab["rows"].values() for w in r.values()
                if w and w["inconclusive_by_design"])
    print(f"power -> {out} ({len(tab['rows'])} trigger-holds, {n_inc} window rows inconclusive)")
    return K.RC_OK


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="trigger_hold.run")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("power")
    p.add_argument("--config", default=str(K.repo_path(K.CONFIG_PATH)))
    p.add_argument("--out", default=str(K.repo_path(K.POWER_PATH)))
    p.add_argument("--input-paths")
    e = sub.add_parser("evaluate")
    e.add_argument("--phase", required=True, choices=PHASES)
    for name in ("--freeze", "--freeze-sha256"):
        e.add_argument(name, required=True)
    e.add_argument("--out-dir")
    e.add_argument("--marker")
    e.add_argument("--registry", default=str(K.repo_path(K.REGISTRY_PATH)))
    e.add_argument("--input-paths")
    e.add_argument("--discovery-result", help="test mode only")
    a = ap.parse_args(argv)
    if a.cmd == "power":
        return cmd_power(a)
    a.out_dir = a.out_dir or str(K.repo_path(K.OUT_DIRS[a.phase]))
    a.marker = a.marker or str(K.repo_path(K.MARKERS[a.phase]))
    return run_phase(a)


if __name__ == "__main__":
    raise SystemExit(main())
