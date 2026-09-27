"""The compute backend's job spec and its fixed registry of job kinds (Stage E.2b, V10).

A job names a KIND, never a module: the registry below fixes each kind's module, the data root
it may be given and the arguments the backend itself supplies (data roots, output directory,
harness sha256). The sender adds only the kind's own choices (a cluster and member, a challenger
and horizon); any of the backend's options or a placeholder in them is refused. Both ends read
this module from the same frozen commit, and the far side re-validates every spec it receives.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field

from compute.datarules import (
    BACKTEST,
    NO_DATA,
    ROOT_STORES,
    TRAINING,
    DataFile,
    DataRuleRefused,
)
from compute.files import is_sha256, sha256_bytes

JOB_SCHEMA = "propexperiment-compute-job/1"
JOB_ID_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
USER_ARG_RE = re.compile(r"^[A-Za-z0-9_.,:=+@/-]{1,200}$")
MAX_USER_ARGS = 32
MIN_THREADS, MAX_THREADS = 1, 14
PLACEHOLDERS = ("{data_root}", "{research_root}", "{step2_root}", "{out_dir}", "{harness_sha256}")


class JobSpecRefused(ValueError):
    """A job spec breaks the registry or its own format."""


@dataclass(frozen=True)
class KindSpec:
    module: str
    data_root_kinds: tuple[str, ...]
    prefix_args: tuple[str, ...]  # before the sender's arguments (a subcommand)
    fixed_args: tuple[str, ...]  # after them; the backend's own values, by placeholder
    note: str

    def reserved_options(self) -> tuple[str, ...]:
        return tuple(a for a in self.fixed_args if a.startswith("--"))


KINDS: dict[str, KindSpec] = {
    "synthetic": KindSpec(
        "compute.synthetic_job", (TRAINING, BACKTEST), (),
        ("--data-root", "{data_root}", "--out-dir", "{out_dir}"),
        "the backend's own test job: reads its data root, writes resumable items"),
    "screening": KindSpec(
        "screening.stage_e_runner", (BACKTEST,), (),
        ("--harness-sha256", "{harness_sha256}", "--research-root", "{research_root}",
         "--step2-root", "{step2_root}", "--out-dir", "{out_dir}"),
        "a cluster's screening or confirmation run (sender gives --cluster, --member or --all, "
        "--window)"),
    "ml_fit": KindSpec(
        "ml_route.train", (TRAINING,), ("fit",),
        ("--store-root", "{data_root}", "--out-dir", "{out_dir}", "--harness-sha256",
         "{harness_sha256}"),
        "E.ML-train's fit for one challenger and horizon (sender gives --challenger, --horizon)"),
    "ml_probe": KindSpec(
        "ml_route.probes", (NO_DATA,), (), ("--out", "{out_dir}/probe.json"),
        "an M8 probe on synthetic inputs (sender gives the probe name); reads no market data"),
}


def validate_user_args(kind: KindSpec, args: tuple[str, ...]) -> None:
    if len(args) > MAX_USER_ARGS:
        raise JobSpecRefused(f"{len(args)} arguments; at most {MAX_USER_ARGS}")
    reserved = kind.reserved_options()
    for arg in args:
        if not isinstance(arg, str) or not USER_ARG_RE.match(arg):
            raise JobSpecRefused(f"argument {arg!r} has characters outside the allowed set")
        if any(arg == opt or arg.startswith(opt + "=") for opt in reserved):
            raise JobSpecRefused(f"argument {arg!r} is the backend's own option for this kind")


@dataclass(frozen=True)
class JobSpec:
    job_id: str
    kind: str
    user_args: tuple[str, ...]
    data_root_kind: str
    data_files: tuple[DataFile, ...]
    threads: int
    harness_sha256: str
    source_commit: str
    export_commit: str
    excluded_paths: tuple[str, ...]
    created: str
    schema: str = field(default=JOB_SCHEMA)

    def kind_spec(self) -> KindSpec:
        return KINDS[self.kind]

    def validate(self) -> JobSpec:
        if self.schema != JOB_SCHEMA:
            raise JobSpecRefused(f"schema {self.schema!r} is not {JOB_SCHEMA!r}")
        if not JOB_ID_RE.match(self.job_id):
            raise JobSpecRefused(f"job id {self.job_id!r} is not [a-z0-9][a-z0-9_-]{{0,63}}")
        if self.kind not in KINDS:
            raise JobSpecRefused(f"kind {self.kind!r} is not one of {sorted(KINDS)}")
        kind = self.kind_spec()
        if self.data_root_kind not in kind.data_root_kinds:
            raise JobSpecRefused(f"kind {self.kind} takes a {'/'.join(kind.data_root_kinds)} "
                                 f"data root, not {self.data_root_kind!r}")
        validate_user_args(kind, self.user_args)
        if not MIN_THREADS <= self.threads <= MAX_THREADS:
            raise JobSpecRefused(f"threads {self.threads} outside {MIN_THREADS}..{MAX_THREADS}")
        if not is_sha256(self.harness_sha256):
            raise JobSpecRefused("harness_sha256 is not a sha256")
        for name in ("source_commit", "export_commit"):
            if not COMMIT_RE.match(getattr(self, name)):
                raise JobSpecRefused(f"{name} is not a 40-hex commit id")
        if self.data_root_kind == NO_DATA and self.data_files:
            raise JobSpecRefused(f"kind {self.kind} reads no data; the spec lists data files")
        if self.data_root_kind != NO_DATA and not self.data_files:
            raise JobSpecRefused("the spec lists no data files")
        dests = []
        for item in self.data_files:
            if item.store not in ROOT_STORES[self.data_root_kind]:
                raise DataRuleRefused("not-allowlisted", item.name, f"a {item.store} file in a "
                                      f"{self.data_root_kind} job")
            if not is_sha256(item.sha256):
                raise JobSpecRefused(f"{item.name}: no sha256")
            dests.append(item.dest(self.data_root_kind))
        if len(set(dests)) != len(dests):
            raise JobSpecRefused("two data files share a destination")
        return self

    def argv(self, values: dict[str, str]) -> list[str]:
        """The module's argument list with the backend's placeholders filled from ``values``."""
        kind = self.kind_spec()
        out = [*kind.prefix_args, *self.user_args]
        for template in kind.fixed_args:
            filled = template
            for placeholder in PLACEHOLDERS:
                if placeholder in filled:
                    name = placeholder.strip("{}")
                    if name not in values:
                        raise JobSpecRefused(f"no value for {placeholder} in a "
                                             f"{self.data_root_kind} job")
                    filled = filled.replace(placeholder, values[name])
            if "{" in filled or "}" in filled:
                raise JobSpecRefused(f"unfilled placeholder in {template!r}")
            out.append(filled)
        return out

    def to_dict(self) -> dict[str, object]:
        return {
            "schema": self.schema, "job_id": self.job_id, "kind": self.kind,
            "module": self.kind_spec().module if self.kind in KINDS else None,
            "user_args": list(self.user_args), "data_root_kind": self.data_root_kind,
            "data_files": [f.as_dict() for f in self.data_files], "threads": self.threads,
            "harness_sha256": self.harness_sha256, "source_commit": self.source_commit,
            "export_commit": self.export_commit, "excluded_paths": list(self.excluded_paths),
            "created": self.created,
        }

    def canonical_bytes(self) -> bytes:
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":")).encode("utf-8")

    def sha256(self) -> str:
        return sha256_bytes(self.canonical_bytes())

    @classmethod
    def from_dict(cls, raw: object) -> JobSpec:
        if not isinstance(raw, dict):
            raise JobSpecRefused("a job spec is a JSON object")
        try:
            spec = cls(
                job_id=raw["job_id"], kind=raw["kind"], user_args=tuple(raw["user_args"]),
                data_root_kind=raw["data_root_kind"],
                data_files=tuple(DataFile.from_dict(f) for f in raw["data_files"]),
                threads=int(raw["threads"]), harness_sha256=raw["harness_sha256"],
                source_commit=raw["source_commit"], export_commit=raw["export_commit"],
                excluded_paths=tuple(raw["excluded_paths"]), created=raw["created"],
                schema=raw["schema"],
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise JobSpecRefused(f"malformed job spec: {exc!r}") from exc
        spec.validate()
        if raw.get("module") != spec.kind_spec().module:
            raise JobSpecRefused(f"module {raw.get('module')!r} is not the registry's for "
                                 f"kind {spec.kind}")
        return spec
