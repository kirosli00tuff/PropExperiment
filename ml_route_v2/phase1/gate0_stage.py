"""Gate 0 of phase 1: the P-2 test list, its registration and the one run (Stage E.12 Task 1b).

docs/STAGE_E_ML_V2_DESIGN.md V2.2b and "The phase-1 test list"; E.12 lead rule P-2.
- ``list_doc(build)`` (P-2): family A = every panel signal (the covered signals; gate0 uses
  panel.signal_names) x the panel's horizons; family B = every admissible (vehicle, horizon) pair.
  The ids and ledger specs come from gate0's own registration code (gate0._register_a on the
  panel; gate0._b_pairs and gate0._register_b with gate0.DEFAULT_RULE on the admissible pairs) run
  into a recorder, so the run's registration (pipeline._gate0) writes nothing new. pipeline._gate0
  computes no test when no pair is admissible; the list is then empty (|A| = |B| = 0) and the
  verdict FAIL. The document has no time stamp: it follows byte for byte from the saved build.
- ``run_register``: writes reports/stage_e12_gate0_list.json once (an existing file must hold the
  same bytes, else refused) and registers every test in the append-only configs.ConfigLedger (a
  test already registered with the same spec writes nothing). Computes no statistic.
- ``run_gate0``: refuses when the state dir holds the completed marker or the Gate 0 report exists
  (run once); checks the list file's sha256 against the expected one and that it follows from the
  saved build; checks every test is registered with its spec; pins (constants, inputs, list
  sha256) in state_dir/gate0_run.json (a resume with anything else is refused; gate0's own family B
  state also pins its inputs and the constants); then runs pipeline._gate0 unchanged (families A
  and B, the verdict, the B trades and the pooled B) and writes reports/stage_e12_gate0.json and
  .md, then the marker. A crash resumes from gate0's per-split family B state.
"""

from __future__ import annotations

import json
import math
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from ml_route_v2.phase1._io import json_bytes, now_local, sha256_bytes, write_atomic, write_json
from ml_route_v2.phase1.build import Build, load_build
from ml_route_v2.phase1.world import Phase1Error

LIST_FILE = "stage_e12_gate0_list.json"
GATE0_JSON = "stage_e12_gate0.json"
GATE0_MD = "stage_e12_gate0.md"
GATE0_DIR = "gate0"  # gate0's family B state, as pipeline.run_pipeline names it
RUN_META = "gate0_run.json"
DONE_FILE = "gate0_DONE.json"
LIST_SCHEMA = "stage_e12_gate0_list/1"
REPORT_SCHEMA = "stage_e12_gate0/1"
RULE_P2 = ("E.12 lead rule P-2: family A = every panel signal (the covered signals, as gate0 uses "
           "panel.signal_names) x HORIZONS; family B = every admissible (vehicle, horizon) pair. "
           "Rows of family A at h are the ok rows of the admissible pairs at h "
           "(gate0._family_a_horizon). A test with < 2 dates keeps t NaN, p 1 and is counted. "
           "Ids and ledger specs: gate0._register_a / gate0._register_b (gate0.DEFAULT_RULE); "
           "no admissible pair: no test (pipeline._gate0)")


class Gate0ListError(Phase1Error):
    """The Gate 0 list file is not the expected one, or a test is not registered as listed."""


class Gate0AlreadyRan(Phase1Error):
    """Gate 0 has completed for this state dir (or its report exists): it runs once."""


class _Recorder:
    """A ledger stand-in that records gate0's registration calls in order."""

    def __init__(self) -> None:
        self.entries: list[tuple[str, str, dict]] = []

    def register(self, entry_id: str, kind: str, spec: Mapping) -> None:
        from ml_route_v2.configs import _canonical

        self.entries.append((entry_id, kind, json.loads(_canonical(spec))))


# ------------------------------------------------------------------ the list ----
def list_tests(panel: Any, admissible: Sequence[tuple[str, str]]) -> list[dict[str, Any]]:
    """The ordered tests of P-2 with their ledger kinds and specs (module docstring)."""
    from ml_route_v2 import gate0 as g0

    rec = _Recorder()
    if admissible:
        g0._register_a(panel, rec)
        g0._register_b(g0._b_pairs(panel, admissible), rec, g0.DEFAULT_RULE)
    ids = [e[0] for e in rec.entries]
    if len(set(ids)) != len(ids):
        raise Gate0ListError("duplicate Gate 0 test ids")
    return [{"test_id": i, "kind": k, "spec": s} for i, k, s in rec.entries]


def list_doc(build: Build) -> dict[str, Any]:
    adm = [tuple(map(str, p)) for p in build.filt["admissible"]]
    tests = list_tests(build.panel, adm)
    n_a = sum(t["kind"] == "gate0_A" for t in tests)
    n_b = sum(t["kind"] == "gate0_B" for t in tests)
    inputs = build.out["inputs"]
    return {
        "schema": LIST_SCHEMA, "rule": RULE_P2, "vehicles": list(build.vehicles),
        "horizons": list(build.panel.horizons),
        "covered_signals": list(build.panel.signal_names),
        "uncovered_signals": {k: list(v) for k, v in build.out["uncovered"].items()},
        "mes": inputs.get("mes"),  # E.12 lead rule P-1a: MES loaded or refused
        "admissible_pairs": [list(p) for p in adm], "tests": tests,
        "n_a": n_a, "n_b": n_b, "n_tests": n_a + n_b,
        "fingerprints": {"constants": build.constants, "inputs": build.input_fingerprint,
                         "ranking_sha256": inputs["ranking"]["sha256"],  # freeze review F-3
                         "stores": inputs["roots"],
                         "release_calendar_sha256": inputs["release_calendar_sha256"],
                         "frozen_tables": inputs["frozen_tables"]},
    }


def _canon(spec: Any) -> str:  # noqa: ANN401
    from ml_route_v2.configs import _canonical

    return _canonical(spec)


def ledger_entries(path: Path) -> dict[str, tuple[str, str]]:
    """entry_id -> (kind, canonical spec) of the ledger file (read only; ConfigLedger's parse)."""
    from ml_route_v2.configs import ConfigLedger

    path = Path(path)
    if not path.exists():
        return {}
    ConfigLedger(path)  # refuses an unreadable or self-contradicting ledger
    out = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rec = json.loads(line)
            out[rec["entry_id"]] = (rec["kind"], _canon(rec["spec"]))
    return out


def check_registered(doc: Mapping[str, Any], ledger_path: Path) -> None:
    have = ledger_entries(ledger_path)
    missing = [t["test_id"] for t in doc["tests"] if t["test_id"] not in have]
    if missing:
        raise Gate0ListError(f"{len(missing)} listed tests are not registered (first "
                             f"{missing[:3]}); run register first")
    other = [t["test_id"] for t in doc["tests"]
             if have[t["test_id"]] != (t["kind"], _canon(t["spec"]))]
    if other:
        raise Gate0ListError(f"{len(other)} tests are registered with another spec (first "
                             f"{other[:3]})")


def run_register(state_dir: Path, *, ledger_path: Path, reports_dir: Path) -> dict[str, Any]:
    """The register step (module docstring)."""
    from ml_route_v2.configs import ConfigLedger

    build = load_build(Path(state_dir))
    doc = list_doc(build)
    data = json_bytes(doc)
    path = Path(reports_dir) / LIST_FILE
    if path.exists():
        if path.read_bytes() != data:
            raise Gate0ListError(f"{path} exists with other content; the list is written once")
        sha = sha256_bytes(data)
    else:
        sha = write_atomic(path, data)
        path.chmod(0o444)
    ledger = ConfigLedger(Path(ledger_path))
    before = ledger.n_registered()
    for t in doc["tests"]:
        ledger.register(t["test_id"], t["kind"], t["spec"])
    check_registered(doc, ledger_path)
    return {"list": path, "sha256": sha, "n_a": doc["n_a"], "n_b": doc["n_b"],
            "n_new": ledger.n_registered() - before, "n_registered": ledger.n_registered()}


# ------------------------------------------------------------------ the run ----
def _file_sha(path: Path) -> str | None:
    return sha256_bytes(Path(path).read_bytes()) if Path(path).exists() else None


def _num(x: Any) -> float | None:  # noqa: ANN401
    return None if x is None else float(x)


def _test_row(t: Any, holm: Mapping[str, Mapping], passing: set[str]) -> dict[str, Any]:  # noqa: ANN401
    h = holm.get(t.test_id)
    row = {"test_id": t.test_id, "family": t.family, "signal": t.signal, "root": t.root,
           "horizon": t.horizon, "n_dates": t.n_dates, "n_obs": t.n_obs, "mean": t.mean,
           "t": t.t, "p": t.p,
           "holm_rank": None if h is None else h["rank"],
           "holm_threshold": None if h is None else h["threshold"],
           "holm_rejected": None if h is None else bool(h["rejected"])}
    if t.family == "B":
        cost = _num(t.cost_ticks)
        ok = cost is not None and math.isfinite(cost) and cost > 0 and math.isfinite(t.mean)
        row.update({"mean_gross_ticks": t.mean, "cost_ticks": cost,
                    "gross_cost_multiple": t.mean / cost if ok else None, "t_B": t.t,
                    "n_trades": t.n_trades,
                    "decision": "PASS" if t.test_id in passing else "FAIL"})
    else:
        row.update({"ic_spearman": t.ic_spearman, "gross_ticks_sign": t.gross_ticks_sign,
                    "decision": "REJECTED" if row["holm_rejected"] else "NOT REJECTED"})
    return row


def gate0_report(res: Mapping[str, Any], doc: Mapping[str, Any], extra: Mapping[str, Any]
                 ) -> dict[str, Any]:
    from ml_route_v2.constants import GATE0_RIDGE_LAMBDA
    from ml_route_v2.gate0 import DEFAULT_RULE

    verdict = res["verdict"]
    holm = {row["test_id"]: row for row in verdict.holm}
    passing = set(verdict.passing)
    tests = [_test_row(t, holm, passing) for t in res["tests"]]
    return {
        "schema": REPORT_SCHEMA, "verdict": "PASS" if verdict.passed else "FAIL",
        "passing_pairs": [[t.root, t.horizon] for t in res["tests"] if t.test_id in passing],
        "rule": {"cost_multiple": DEFAULT_RULE.cost_multiple, "t_min": DEFAULT_RULE.t_min,
                 "alpha": DEFAULT_RULE.alpha, "top_fraction": DEFAULT_RULE.top_fraction,
                 "min_trades": DEFAULT_RULE.min_trades,
                 "holm_includes_a": DEFAULT_RULE.holm_includes_a,
                 "ridge_lambda": GATE0_RIDGE_LAMBDA},
        "n_a": int(res["n_a"]), "n_b": int(res["n_b"]),
        "n_contributed": int(res["n_a"]) + int(res["n_b"]), "n_holm_family": len(verdict.holm),
        "pooled_b": res["pooled_b"], "tests": tests, "vehicles": doc["vehicles"],
        "admissible_pairs": doc["admissible_pairs"], **extra,
    }


def _fmt(x: Any) -> str:  # noqa: ANN401
    if x is None:
        return "n/a"
    if isinstance(x, bool):
        return "yes" if x else "no"
    if isinstance(x, float):
        return "NaN" if math.isnan(x) else f"{x:.4g}"
    return str(x)


def gate0_markdown(rep: Mapping[str, Any]) -> str:
    out = ["# Stage E.12 Gate 0 (phase 1)", "",
           f"Verdict: **{rep['verdict']}**. Passing pairs: "
           f"{', '.join(f'{r} {h}' for r, h in rep['passing_pairs']) or 'none'}.", "",
           f"Tests: |A| = {rep['n_a']}, |B| = {rep['n_b']}, N contributed = "
           f"{rep['n_contributed']} (Holm family {rep['n_holm_family']}).", "",
           "Rule: " + ", ".join(f"{k} {_fmt(v)}" for k, v in rep["rule"].items()), ""]
    pooled = rep["pooled_b"] or {}
    out += ["Pooled family B (descriptive): " + (", ".join(f"{k} {_fmt(v)}" for k, v in
                                                           pooled.items()) or "none"), ""]
    out += ["## Family B", "", "| test | n_trades | mean gross ticks | cost ticks | multiple | "
            "t_B | p | Holm rank | threshold | rejected | decision |", "|" + "---|" * 11]
    for t in (x for x in rep["tests"] if x["family"] == "B"):
        out.append("| " + " | ".join(_fmt(t[k]) for k in (
            "test_id", "n_trades", "mean_gross_ticks", "cost_ticks", "gross_cost_multiple",
            "t_B", "p", "holm_rank", "holm_threshold", "holm_rejected", "decision")) + " |")
    out += ["", "## Family A", "", "| test | n_dates | n_obs | mean | t | p | Holm rank | "
            "threshold | rejected | Spearman IC | sign gross ticks |", "|" + "---|" * 11]
    for t in (x for x in rep["tests"] if x["family"] == "A"):
        out.append("| " + " | ".join(_fmt(t[k]) for k in (
            "test_id", "n_dates", "n_obs", "mean", "t", "p", "holm_rank", "holm_threshold",
            "holm_rejected", "ic_spearman", "gross_ticks_sign")) + " |")
    out += ["", "## Fingerprints", ""]
    out += [f"- {k}: {_fmt(v)}" for k, v in sorted(rep["fingerprints"].items())]
    out += [f"- list sha256: {rep['list_sha256']}",
            f"- ledger unchanged by the run: {_fmt(rep['ledger']['unchanged'])}", ""]
    return "\n".join(out)


def _guard_once(state_dir: Path, reports_dir: Path) -> None:
    done, rep = state_dir / DONE_FILE, reports_dir / GATE0_JSON
    if done.exists() or rep.exists():
        raise Gate0AlreadyRan(f"Gate 0 already completed ({done if done.exists() else rep}); "
                              "it runs once")


def _pin_run(state_dir: Path, meta: Mapping[str, Any]) -> None:
    path = state_dir / RUN_META
    if path.exists():
        saved = json.loads(path.read_text(encoding="utf-8"))
        if saved != dict(meta):
            raise Phase1Error(f"{path} pins other inputs, constants or list; a changed input or "
                              "constant is a stop, never a rerun")
    else:
        write_json(path, meta)


def _verified_list(build: Build, list_path: Path, expected_sha256: str) -> dict[str, Any]:
    if not Path(list_path).is_file():
        raise Gate0ListError(f"{list_path} does not exist; run register first")
    data = Path(list_path).read_bytes()
    if sha256_bytes(data) != expected_sha256:
        raise Gate0ListError(f"{Path(list_path).name} sha256 {sha256_bytes(data)[:12]}... is not "
                             f"the expected {str(expected_sha256)[:12]}...")
    doc = list_doc(build)
    if json_bytes(doc) != data:
        raise Gate0ListError(f"{Path(list_path).name} does not follow from the saved build")
    return doc


def run_gate0(state_dir: Path, *, ledger_path: Path, reports_dir: Path,
              expected_list_sha256: str, harness_sha256: str | None = None,
              freeze_sha256: str | None = None) -> dict[str, Any]:
    """The run step (module docstring)."""
    from ml_route_v2.configs import ConfigLedger
    from ml_route_v2.pipeline import _gate0

    state_dir, reports_dir = Path(state_dir), Path(reports_dir)
    _guard_once(state_dir, reports_dir)
    build = load_build(state_dir)
    doc = _verified_list(build, reports_dir / LIST_FILE, expected_list_sha256)
    check_registered(doc, ledger_path)
    _pin_run(state_dir, {"constants": build.constants, "inputs": build.input_fingerprint,
                         "list_sha256": expected_list_sha256})
    before = _file_sha(ledger_path)
    ledger = ConfigLedger(Path(ledger_path))
    adm = tuple(tuple(map(str, p)) for p in build.filt["admissible"])
    res = _gate0(build.panel, adm, ledger, state_dir / GATE0_DIR, list(build.calendar))
    after = _file_sha(ledger_path)
    ran = [t.test_id for t in res["tests"]]
    if ran != [t["test_id"] for t in doc["tests"]]:
        raise Gate0ListError("the tests Gate 0 ran are not the registered list")
    meta_b = state_dir / GATE0_DIR / "gate0B_meta.json"
    extra = {"list_sha256": expected_list_sha256,
             "fingerprints": {"constants": build.constants, "inputs": build.input_fingerprint,
                              "gate0_b_state": (json.loads(meta_b.read_text(encoding="utf-8"))
                                                .get("fingerprint") if meta_b.exists() else None),
                              "harness_sha256": harness_sha256, "freeze_sha256": freeze_sha256},
             "ledger": {"path": str(ledger_path), "sha256_before": before, "sha256_after": after,
                        "unchanged": before == after, "n_registered": ledger.n_registered()},
             "created_pdt": now_local()}
    rep = gate0_report(res, doc, extra)
    json_sha = write_json(reports_dir / GATE0_JSON, rep)
    md_sha = write_atomic(reports_dir / GATE0_MD, gate0_markdown(rep).encode())
    write_json(state_dir / DONE_FILE, {"verdict": rep["verdict"], "report_sha256": json_sha,
                                       "markdown_sha256": md_sha, "time": now_local()})
    return {"verdict": rep["verdict"], "n_a": rep["n_a"], "n_b": rep["n_b"],
            "n_passing": len(rep["passing_pairs"]), "json": reports_dir / GATE0_JSON,
            "md": reports_dir / GATE0_MD, "json_sha256": json_sha, "md_sha256": md_sha,
            "ledger_unchanged": before == after}


__all__ = ["DONE_FILE", "GATE0_DIR", "GATE0_JSON", "GATE0_MD", "LIST_FILE", "RULE_P2",
           "RUN_META", "Gate0AlreadyRan", "Gate0ListError", "check_registered", "gate0_markdown",
           "gate0_report", "ledger_entries", "list_doc", "list_tests", "run_gate0",
           "run_register"]
