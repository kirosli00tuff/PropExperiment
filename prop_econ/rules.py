"""Stage E.19 rules loader (reports/stage_e19_briefs/rules_schema.md).

Loads and validates a rules JSON, applies alternative readings by dotted path (always returning a
new ``RuleBook``; nothing is mutated) and exposes one account size's rules as frozen dataclasses
for the funnel simulators. No Topstep number lives in this module: every value comes from the JSON.
"""

from __future__ import annotations

import copy
import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any

SCHEMA_VERSION = "e19-rules-1"
SIZES = ("50K", "100K", "150K")
PRICING_PATHS = ("standard", "no_activation_fee")
PAYOUT_PATHS = ("standard", "consistency")
RULE_STATUSES = ("SOURCED", "UNSOURCED", "CONFLICT", "INFERRED")
FILE_STATUSES = ("FINAL", "PROVISIONAL")
RULE_KEYS = ("id", "path", "value", "status", "readings", "source", "quote", "note")


class RulesError(ValueError):
    """The rules JSON breaks the schema; ``problems`` lists every violation found."""

    def __init__(self, problems: Sequence[str]) -> None:
        self.problems = tuple(problems)
        shown = "; ".join(self.problems[:25])
        more = f" (+{len(self.problems) - 25} more)" if len(self.problems) > 25 else ""
        super().__init__(f"{len(self.problems)} rules problem(s): {shown}{more}")


# ------------------------------------------------------------------------------- schema ----
# Leaf tags: "int", "num", "bool", "str", "enum:a|b"; a trailing "?" allows null.
_PRICE = {"standard": "num", "no_activation_fee": "num"}
_PRICE_OR_NULL = {"standard": "num?", "no_activation_fee": "num?"}
_GLOBAL_SPEC: dict[str, Any] = {
    "max_active_xfas": "int",
    "profit_split_trader": "num",
    "billing_period_calendar_days": "int",
    "rebill_adds_reset_credit": "bool",
    "reset_pushes_rebill": "bool",
    "resets_per_day": "int?",
    "combine_time_limit_days": "int?",
    "payout_min_request_usd": "num",
    "payout_day_counts_toward_next_window": "bool",
    "xfa_inactivity_close_days": "int?",
    "callup": {
        "type": "enum:none|after_n_payouts|payout_total_usd|discretionary",
        "n": "int?",
        "usd": "num?",
        "closes_all_xfas": "bool?",
        "xfa_balance_on_callup": "str",
    },
    "dll_doubles_payout_caps": "bool",
}
_SIZE_SPEC: dict[str, Any] = {
    "combine": {
        "monthly_price_usd": _PRICE,
        "reset_price_usd": _PRICE,
        "dll_discount_monthly_usd": _PRICE_OR_NULL,
        "profit_target_usd": "num",
        "mll_usd": "num",
        "mll_trail": "enum:eod|intraday",
        "mll_floor_max_rel_usd": "num",
        "dll_usd": "num?",
        "consistency": {
            "type": "enum:best_day_max_frac_of_profit|best_day_max_frac_of_target|none",
            "frac": "num?",
        },
        "min_trading_days": "int",
        "max_minis": "int",
    },
    "activation_fee_usd": _PRICE,
    "xfa": {
        "start_balance_usd": "num",
        "mll_usd": "num",
        "mll_trail": "enum:eod|intraday",
        "mll_floor_lock_usd": "num",
        "mll_after_first_payout_usd": "num?",
        "dll_option_usd": "num?",
        "scaling": [{"below_usd": "num?", "max_minis": "int"}],
        "scaling_boundary": "enum:lower|upper",
        "payout": {
            "standard": {
                "winning_day_usd": "num",
                "winning_days": "int",
                "frac_of_balance": "num",
                "cap_usd": "num",
                "cap_usd_dll": "num?",
                "net_positive_since_last": "bool",
            },
            "consistency": {
                "traded_days": "int",
                "best_day_max_frac": "num",
                "frac_of_balance": "num",
                "cap_usd": "num",
                "cap_usd_dll": "num?",
                "net_positive_since_last": "bool",
            },
        },
        "payout_count_limit": "int?",
        "back2funded": {
            "price_usd": "num",
            "dll_discount_usd": "num?",
            "max_per_xfa": "int",
            "before_first_payout_only": "bool",
            "window_calendar_days": "int",
        },
    },
}


def _type_ok(tag: str, value: Any) -> bool:
    if tag.endswith("?"):
        if value is None:
            return True
        tag = tag[:-1]
    if tag == "int":
        return isinstance(value, int) and not isinstance(value, bool)
    if tag == "num":
        return isinstance(value, int | float) and not isinstance(value, bool)
    if tag == "bool":
        return isinstance(value, bool)
    if tag == "str":
        return isinstance(value, str)
    if tag.startswith("enum:"):
        return value in tag[5:].split("|")
    raise AssertionError(f"unknown schema tag {tag}")


def _leaves(value: Any, path: str) -> list[tuple[str, Any]]:
    """Every scalar leaf under ``value`` with its dotted path (list items by index)."""
    if isinstance(value, Mapping):
        out: list[tuple[str, Any]] = []
        for key, sub in value.items():
            out.extend(_leaves(sub, f"{path}.{key}"))
        return out
    if isinstance(value, list | tuple):
        out = []
        for i, sub in enumerate(value):
            out.extend(_leaves(sub, f"{path}.{i}"))
        return out
    return [(path, value)]


def _check_shape(spec: Any, value: Any, path: str, problems: list[str], extras: list[str]) -> None:
    if isinstance(spec, dict):
        if not isinstance(value, Mapping):
            problems.append(f"{path}: expected an object")
            return
        for key, sub in spec.items():
            if key not in value:
                problems.append(f"{path}.{key}: missing")
            else:
                _check_shape(sub, value[key], f"{path}.{key}", problems, extras)
        for key in value:
            if key not in spec:
                extras.extend(p for p, _ in _leaves(value[key], f"{path}.{key}"))
        return
    if isinstance(spec, list):
        if not isinstance(value, list | tuple) or not value:
            problems.append(f"{path}: expected a non-empty list")
            return
        for i, item in enumerate(value):
            _check_shape(spec[0], item, f"{path}.{i}", problems, extras)
        return
    if not _type_ok(spec, value):
        problems.append(f"{path}: {value!r} does not match {spec}")


def _check_scaling(sizes: Mapping[str, Any], problems: list[str]) -> None:
    for size, block in sizes.items():
        tiers = block.get("xfa", {}).get("scaling") if isinstance(block, Mapping) else None
        if not isinstance(tiers, list | tuple) or not tiers:
            continue
        bounds = [t.get("below_usd") for t in tiers if isinstance(t, Mapping)]
        if len(bounds) != len(tiers):
            continue
        if bounds[-1] is not None or any(b is None for b in bounds[:-1]):
            problems.append(f"sizes.{size}.xfa.scaling: the last tier, and only it, has null "
                            "below_usd")
        finite = [b for b in bounds[:-1] if isinstance(b, int | float)]
        if any(b2 <= b1 for b1, b2 in zip(finite, finite[1:], strict=False)):
            problems.append(f"sizes.{size}.xfa.scaling: below_usd not strictly ascending")


def same_value(a: Any, b: Any) -> bool:
    """Type-aware equality: numbers numerically, bools only with bools, null only with null."""
    if isinstance(a, bool) or isinstance(b, bool):
        return type(a) is type(b) and a == b
    if a is None or b is None:
        return a is None and b is None
    if isinstance(a, int | float) and isinstance(b, int | float):
        return float(a) == float(b)
    return type(a) is type(b) and a == b


def _check_rules(doc: Mapping[str, Any], problems: list[str]) -> None:
    rules = doc.get("rules")
    if not isinstance(rules, list | tuple):
        problems.append("rules: expected a list")
        return
    leaves = dict(_leaves(doc["global"], "global") + _leaves(doc["sizes"], "sizes"))
    seen_paths: dict[str, str] = {}
    seen_ids: set[str] = set()
    for i, rule in enumerate(rules):
        where = f"rules[{i}]"
        if not isinstance(rule, Mapping):
            problems.append(f"{where}: expected an object")
            continue
        missing = [k for k in RULE_KEYS if k not in rule]
        if missing:
            problems.append(f"{where}: missing keys {missing}")
            continue
        rid, path = rule["id"], rule["path"]
        if rid in seen_ids:
            problems.append(f"{where}: duplicate id {rid}")
        seen_ids.add(rid)
        if rule["status"] not in RULE_STATUSES:
            problems.append(f"{rid}: bad status {rule['status']!r}")
        readings = rule["readings"]
        if not isinstance(readings, list | tuple) or not readings:
            problems.append(f"{rid}: readings must be a non-empty list")
            continue
        if path in seen_paths:
            problems.append(f"{rid}: path {path} already covered by {seen_paths[path]}")
            continue
        seen_paths[path] = rid
        if path not in leaves:
            problems.append(f"{rid}: path {path} is not a leaf of global/sizes")
            continue
        if not same_value(readings[0], leaves[path]):
            problems.append(f"{rid}: readings[0] {readings[0]!r} != structured value "
                            f"{leaves[path]!r}")
        if not same_value(rule["value"], leaves[path]):
            problems.append(f"{rid}: value {rule['value']!r} != structured value {leaves[path]!r}")
        source = rule["source"]
        if source is not None and source not in doc.get("sources", {}):
            problems.append(f"{rid}: source {source} not in sources")
    for path in leaves:
        if path not in seen_paths:
            problems.append(f"{path}: no RULE")


def _shape_problems(doc: Mapping[str, Any], problems: list[str], extras: list[str]) -> None:
    """Schema shape and leaf types of global and sizes (unknown leaves go to ``extras``)."""
    _check_shape(_GLOBAL_SPEC, doc["global"], "global", problems, extras)
    for size in SIZES:
        if size not in doc["sizes"]:
            problems.append(f"sizes.{size}: missing")
        else:
            _check_shape(_SIZE_SPEC, doc["sizes"][size], f"sizes.{size}", problems, extras)
    for size, block in doc["sizes"].items():
        if size not in SIZES:
            extras.extend(p for p, _ in _leaves(block, f"sizes.{size}"))
    _check_scaling(doc["sizes"], problems)


def validate_rules(doc: Mapping[str, Any]) -> tuple[str, ...]:
    """Raise RulesError listing every violation; return the leaf paths outside the known schema.

    Leaves outside the schema (fields Task 1 added) are accepted and carried; like every leaf they
    need exactly one RULE.
    """
    problems: list[str] = []
    extras: list[str] = []
    if not isinstance(doc, Mapping):
        raise RulesError(["top level: expected an object"])
    if doc.get("schema_version") != SCHEMA_VERSION:
        problems.append(f"schema_version {doc.get('schema_version')!r} != {SCHEMA_VERSION!r}")
    if doc.get("status") not in FILE_STATUSES:
        problems.append(f"status {doc.get('status')!r} not in {FILE_STATUSES}")
    for key, kind in (("sources", Mapping), ("terms_check", Mapping), ("prohibited", list | tuple)):
        if not isinstance(doc.get(key), kind):
            problems.append(f"{key}: missing or wrong type")
    if not isinstance(doc.get("global"), Mapping) or not isinstance(doc.get("sizes"), Mapping):
        raise RulesError([*problems, "global and sizes must be objects"])
    _shape_problems(doc, problems, extras)
    _check_rules(doc, problems)
    if problems:
        raise RulesError(problems)
    return tuple(extras)


# ------------------------------------------------------------------------------ RuleBook ----
def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({k: _freeze(v) for k, v in value.items()})
    if isinstance(value, list | tuple):
        return tuple(_freeze(v) for v in value)
    return value


def _thaw(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {k: _thaw(v) for k, v in value.items()}
    if isinstance(value, tuple):
        return [_thaw(v) for v in value]
    return copy.deepcopy(value)


def _get(doc: Any, path: str) -> Any:
    node = doc
    for part in path.split("."):
        node = node[int(part)] if isinstance(node, list | tuple) else node[part]
    return node


def _set(doc: Any, path: str, value: Any) -> None:
    parts = path.split(".")
    node = _get(doc, ".".join(parts[:-1]))
    last = parts[-1]
    if isinstance(node, list):
        node[int(last)] = value
    else:
        node[last] = value


@dataclass(frozen=True)
class RuleBook:
    """A validated rules document (frozen) plus the alternative readings applied to it."""

    doc: Mapping[str, Any]
    overrides: tuple[tuple[str, Any], ...] = ()
    extra_fields: tuple[str, ...] = ()
    source: str | None = None
    unlisted: tuple[str, ...] = ()  # override paths whose value is not among the RULE's readings

    @property
    def status(self) -> str:
        return str(self.doc["status"])

    def value(self, path: str) -> Any:
        """The structured value at a dotted path such as ``sizes.50K.xfa.scaling.0.max_minis``."""
        return _get(self.doc, path)

    def rule(self, path: str) -> Mapping[str, Any]:
        for rule in self.doc["rules"]:
            if rule["path"] == path:
                return rule
        raise KeyError(path)

    def alternative_readings(self) -> dict[str, tuple[Any, ...]]:
        """Every RULE with more than one reading (UNSOURCED / CONFLICT), path -> readings."""
        return {r["path"]: tuple(r["readings"]) for r in self.doc["rules"]
                if len(r["readings"]) > 1}


def rules_from_dict(doc: Mapping[str, Any], source: str | None = None) -> RuleBook:
    extras = validate_rules(doc)
    return RuleBook(doc=_freeze(doc), extra_fields=extras, source=source)


def load_rules(path: str | Path) -> RuleBook:
    with open(path, encoding="utf-8") as fh:
        doc = json.load(fh)
    return rules_from_dict(doc, source=str(path))


def apply_readings(book: RuleBook, choices: Mapping[str, Any], *,
                   allow_unlisted: bool = False) -> RuleBook:
    """A new RuleBook with each path's structured value replaced by one of that RULE's readings.

    ``allow_unlisted=True`` admits a value outside the RULE's readings (a lead-chosen sensitivity,
    for example callup after_n_payouts with n = 3 when the file lists one reading); such paths
    are listed in ``unlisted`` and the new document must still pass the schema's type checks.
    """
    doc = _thaw(book.doc)
    applied = dict(book.overrides)
    unlisted = set(book.unlisted)
    for path, value in choices.items():
        try:
            readings = book.rule(path)["readings"]
        except KeyError as exc:
            raise RulesError([f"{path}: no RULE"]) from exc
        if not any(same_value(value, r) for r in readings):
            if not allow_unlisted:
                raise RulesError([f"{path}: {value!r} is not one of the readings {list(readings)}"])
            unlisted.add(path)
        else:
            unlisted.discard(path)
        _set(doc, path, value)
        applied[path] = value
    problems: list[str] = []
    _shape_problems(doc, problems, [])
    if problems:
        raise RulesError(problems)
    return RuleBook(doc=_freeze(doc), overrides=tuple(sorted(applied.items())),
                    extra_fields=book.extra_fields, source=book.source,
                    unlisted=tuple(sorted(unlisted)))


# ------------------------------------------------------------------------- size views ----
@dataclass(frozen=True)
class CallupRules:
    type: str
    n: int | None
    usd: float | None


@dataclass(frozen=True)
class GlobalRules:
    max_active_xfas: int
    profit_split_trader: float
    billing_period_calendar_days: int
    rebill_adds_reset_credit: bool
    reset_pushes_rebill: bool
    combine_time_limit_days: int | None
    payout_min_request_usd: float
    payout_day_counts_toward_next_window: bool
    callup: CallupRules
    dll_doubles_payout_caps: bool
    combine_consistency_inclusive: bool  # added field; True (<=) when absent
    xfa_consistency_inclusive: bool  # added field; True (<=) when absent


@dataclass(frozen=True)
class PricingRules:
    """One pricing path's prices (USD)."""

    monthly_price_usd: float
    reset_price_usd: float
    dll_discount_monthly_usd: float | None
    activation_fee_usd: float


@dataclass(frozen=True)
class CombineRules:
    profit_target_usd: float
    mll_usd: float
    mll_trail: str
    mll_floor_max_rel_usd: float
    dll_usd: float | None  # mandatory Combine DLL (null = none)
    dll_option_usd: float | None  # added field: the DLL chosen at checkout (None when absent)
    consistency_type: str
    consistency_frac: float | None
    min_trading_days: int
    max_minis: int


@dataclass(frozen=True)
class PayoutRules:
    """One payout path; fields of the other path are None."""

    path: str
    frac_of_balance: float
    cap_usd: float
    cap_usd_dll: float | None
    net_positive_since_last: bool
    winning_day_usd: float | None = None
    winning_days: int | None = None
    traded_days: int | None = None
    best_day_max_frac: float | None = None


@dataclass(frozen=True)
class Back2FundedRules:
    price_usd: float
    dll_discount_usd: float | None
    max_per_xfa: int
    before_first_payout_only: bool
    window_calendar_days: int


@dataclass(frozen=True)
class XfaRules:
    start_balance_usd: float
    mll_usd: float
    mll_trail: str
    mll_floor_lock_usd: float
    mll_after_first_payout_usd: float | None
    dll_option_usd: float | None
    scaling: tuple[tuple[float | None, int], ...]  # (below_usd, max_minis), ascending
    scaling_boundary: str
    payout_standard: PayoutRules
    payout_consistency: PayoutRules
    payout_count_limit: int | None
    back2funded: Back2FundedRules

    def payout(self, path: str) -> PayoutRules:
        if path == "standard":
            return self.payout_standard
        if path == "consistency":
            return self.payout_consistency
        raise ValueError(f"unknown payout path {path!r}")


@dataclass(frozen=True)
class SizeRules:
    """Everything the simulators need for one account size."""

    size: str
    status: str
    overrides: tuple[tuple[str, Any], ...]
    glob: GlobalRules
    combine: CombineRules
    xfa: XfaRules
    pricing_standard: PricingRules
    pricing_no_activation_fee: PricingRules

    def pricing(self, path: str) -> PricingRules:
        if path == "standard":
            return self.pricing_standard
        if path == "no_activation_fee":
            return self.pricing_no_activation_fee
        raise ValueError(f"unknown pricing path {path!r}")


def _opt_float(x: Any) -> float | None:
    return None if x is None else float(x)


def _flag(block: Mapping[str, Any], key: str, default: bool = True) -> bool:
    value = block.get(key, default)
    if not isinstance(value, bool):
        raise RulesError([f"{key}: expected a bool, got {value!r}"])
    return value


def _global_view(g: Mapping[str, Any]) -> GlobalRules:
    c = g["callup"]
    return GlobalRules(
        max_active_xfas=int(g["max_active_xfas"]),
        profit_split_trader=float(g["profit_split_trader"]),
        billing_period_calendar_days=int(g["billing_period_calendar_days"]),
        rebill_adds_reset_credit=bool(g["rebill_adds_reset_credit"]),
        reset_pushes_rebill=bool(g["reset_pushes_rebill"]),
        combine_time_limit_days=g["combine_time_limit_days"],
        payout_min_request_usd=float(g["payout_min_request_usd"]),
        payout_day_counts_toward_next_window=bool(g["payout_day_counts_toward_next_window"]),
        callup=CallupRules(type=str(c["type"]), n=c["n"], usd=_opt_float(c["usd"])),
        dll_doubles_payout_caps=bool(g["dll_doubles_payout_caps"]),
        combine_consistency_inclusive=_flag(g, "combine_consistency_inclusive"),
        xfa_consistency_inclusive=_flag(g, "xfa_consistency_inclusive"),
    )


def _payout_view(path: str, p: Mapping[str, Any]) -> PayoutRules:
    common = {
        "path": path,
        "frac_of_balance": float(p["frac_of_balance"]),
        "cap_usd": float(p["cap_usd"]),
        "cap_usd_dll": _opt_float(p["cap_usd_dll"]),
        "net_positive_since_last": bool(p["net_positive_since_last"]),
    }
    if path == "standard":
        return PayoutRules(**common, winning_day_usd=float(p["winning_day_usd"]),
                           winning_days=int(p["winning_days"]))
    return PayoutRules(**common, traded_days=int(p["traded_days"]),
                       best_day_max_frac=float(p["best_day_max_frac"]))


def _xfa_view(x: Mapping[str, Any]) -> XfaRules:
    b = x["back2funded"]
    return XfaRules(
        start_balance_usd=float(x["start_balance_usd"]),
        mll_usd=float(x["mll_usd"]),
        mll_trail=str(x["mll_trail"]),
        mll_floor_lock_usd=float(x["mll_floor_lock_usd"]),
        mll_after_first_payout_usd=_opt_float(x["mll_after_first_payout_usd"]),
        dll_option_usd=_opt_float(x["dll_option_usd"]),
        scaling=tuple((_opt_float(t["below_usd"]), int(t["max_minis"])) for t in x["scaling"]),
        scaling_boundary=str(x["scaling_boundary"]),
        payout_standard=_payout_view("standard", x["payout"]["standard"]),
        payout_consistency=_payout_view("consistency", x["payout"]["consistency"]),
        payout_count_limit=x["payout_count_limit"],
        back2funded=Back2FundedRules(
            price_usd=float(b["price_usd"]),
            dll_discount_usd=_opt_float(b["dll_discount_usd"]),
            max_per_xfa=int(b["max_per_xfa"]),
            before_first_payout_only=bool(b["before_first_payout_only"]),
            window_calendar_days=int(b["window_calendar_days"]),
        ),
    )


def _combine_view(c: Mapping[str, Any]) -> CombineRules:
    cons = c["consistency"]
    if cons["type"] != "none" and cons["frac"] is None:
        raise RulesError([f"combine consistency {cons['type']} needs a frac"])
    return CombineRules(
        profit_target_usd=float(c["profit_target_usd"]),
        mll_usd=float(c["mll_usd"]),
        mll_trail=str(c["mll_trail"]),
        mll_floor_max_rel_usd=float(c["mll_floor_max_rel_usd"]),
        dll_usd=_opt_float(c["dll_usd"]),
        dll_option_usd=_opt_float(c.get("dll_option_usd")),
        consistency_type=str(cons["type"]),
        consistency_frac=_opt_float(cons["frac"]),
        min_trading_days=int(c["min_trading_days"]),
        max_minis=int(c["max_minis"]),
    )


def _pricing_view(s: Mapping[str, Any], path: str) -> PricingRules:
    c = s["combine"]
    return PricingRules(
        monthly_price_usd=float(c["monthly_price_usd"][path]),
        reset_price_usd=float(c["reset_price_usd"][path]),
        dll_discount_monthly_usd=_opt_float(c["dll_discount_monthly_usd"][path]),
        activation_fee_usd=float(s["activation_fee_usd"][path]),
    )


def size_rules(book: RuleBook, size: str) -> SizeRules:
    """The frozen view of one size's rules (with the book's applied readings)."""
    if size not in book.doc["sizes"]:
        raise RulesError([f"size {size!r} not in {tuple(book.doc['sizes'])}"])
    s = book.doc["sizes"][size]
    return SizeRules(
        size=size,
        status=book.status,
        overrides=book.overrides,
        glob=_global_view(book.doc["global"]),
        combine=_combine_view(s["combine"]),
        xfa=_xfa_view(s["xfa"]),
        pricing_standard=_pricing_view(s, "standard"),
        pricing_no_activation_fee=_pricing_view(s, "no_activation_fee"),
    )
