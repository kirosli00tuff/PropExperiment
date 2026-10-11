"""Stage E.19 rules loader: validation, size views and reading overrides (prop_econ/rules.py)."""

from __future__ import annotations

import copy
import json

import pytest

from prop_econ.rules import (
    RulesError,
    apply_readings,
    load_rules,
    rules_from_dict,
    same_value,
    size_rules,
)
from tests.test_prop_econ_fixtures import hand_book, hand_doc, with_rules


def _problems(doc) -> tuple[str, ...]:
    with pytest.raises(RulesError) as err:
        rules_from_dict(doc)
    return err.value.problems


def test_load_from_file_and_size_view(tmp_path):
    path = tmp_path / "rules.json"
    path.write_text(json.dumps(hand_doc()))
    book = load_rules(path)
    assert book.source == str(path)
    r = size_rules(book, "50K")
    assert r.combine.profit_target_usd == 3000.0 and r.combine.dll_option_usd == 1000.0
    assert r.xfa.scaling == ((1500.0, 2), (2000.0, 3), (None, 5))
    assert r.xfa.payout("consistency").best_day_max_frac == 0.4
    assert r.pricing("no_activation_fee").dll_discount_monthly_usd == 10.0
    assert r.glob.combine_consistency_inclusive and r.glob.xfa_consistency_inclusive  # absent
    with pytest.raises(RulesError):
        size_rules(book, "25K")


def test_inclusive_flags_read_when_present():
    r = size_rules(hand_book(combine_consistency_inclusive=False,
                             xfa_consistency_inclusive=True), "100K")
    assert (r.glob.combine_consistency_inclusive, r.glob.xfa_consistency_inclusive) == (False, True)


def test_schema_version_and_status_checked():
    doc = hand_doc()
    doc["schema_version"] = "e19-rules-0"
    doc["status"] = "DRAFT"
    probs = _problems(doc)
    assert any("schema_version" in p for p in probs) and any("status" in p for p in probs)


def test_every_leaf_needs_exactly_one_rule():
    doc = hand_doc()
    dropped = doc["rules"].pop(5)
    assert any(dropped["path"] in p and "no RULE" in p for p in _problems(doc))
    doc = hand_doc()
    doc["rules"].append({**doc["rules"][0], "id": "R999"})
    assert any("already covered" in p for p in _problems(doc))
    doc = hand_doc()
    doc["rules"].append({**doc["rules"][0], "id": "R998", "path": "sizes.50K.combine.nope"})
    assert any("not a leaf" in p for p in _problems(doc))


def test_readings_first_and_value_must_equal_the_structured_value():
    doc = hand_doc()
    rule = next(r for r in doc["rules"] if r["path"] == "sizes.50K.combine.mll_usd")
    rule["readings"] = [2500.0]
    rule["value"] = 2500.0
    probs = _problems(doc)
    assert any("readings[0]" in p for p in probs) and any("value 2500.0" in p for p in probs)


def test_leaf_types_enums_and_scaling_order_checked():
    doc = hand_doc()
    doc["sizes"]["50K"]["combine"]["max_minis"] = "5"
    doc["sizes"]["50K"]["xfa"]["mll_trail"] = "weekly"
    doc["sizes"]["100K"]["xfa"]["scaling"][1]["below_usd"] = 1000.0  # below the first tier
    doc["global"]["rebill_adds_reset_credit"] = 1  # an int is not a bool
    del doc["sizes"]["150K"]["xfa"]["payout_count_limit"]
    probs = _problems(with_rules(doc))
    for needle in ("combine.max_minis", "xfa.mll_trail", "not strictly ascending",
                   "rebill_adds_reset_credit", "payout_count_limit: missing"):
        assert any(needle in p for p in probs), needle


def test_rule_source_must_exist():
    doc = hand_doc()
    doc["rules"][0]["source"] = "S42"
    assert any("S42" in p for p in _problems(doc))


def test_added_fields_are_carried_and_need_a_rule():
    doc = hand_doc()
    doc["global"]["payout_fee_usd"] = {"ach": 30.0, "wise": 0.0}
    book = rules_from_dict(with_rules(doc))
    assert "global.payout_fee_usd.ach" in book.extra_fields
    assert book.value("global.payout_fee_usd.ach") == 30.0
    bare = copy.deepcopy(hand_doc())
    bare["global"]["payout_fee_usd"] = {"ach": 30.0}
    assert any("global.payout_fee_usd.ach: no RULE" in p for p in _problems(bare))


def test_apply_readings_returns_a_new_book_and_leaves_the_old_one():
    book = hand_book()
    alt = apply_readings(book, {"sizes.50K.xfa.scaling_boundary": "upper"})
    assert alt is not book
    assert book.value("sizes.50K.xfa.scaling_boundary") == "lower"
    assert alt.value("sizes.50K.xfa.scaling_boundary") == "upper"
    assert alt.overrides == (("sizes.50K.xfa.scaling_boundary", "upper"),)
    assert size_rules(alt, "50K").xfa.scaling_boundary == "upper"
    assert size_rules(alt, "100K").xfa.scaling_boundary == "lower"  # other sizes untouched
    with pytest.raises(TypeError):
        book.doc["global"]["max_active_xfas"] = 6  # the frozen document cannot be mutated


def test_apply_readings_rejects_values_outside_the_readings_unless_allowed():
    book = hand_book()
    with pytest.raises(RulesError):
        apply_readings(book, {"sizes.50K.xfa.scaling_boundary": "middle"})
    with pytest.raises(RulesError):
        apply_readings(book, {"global.no_such_rule": 1})
    alt = apply_readings(book, {"global.callup.type": "after_n_payouts", "global.callup.n": 3},
                         allow_unlisted=True)
    assert alt.unlisted == ("global.callup.n",)
    assert size_rules(alt, "50K").glob.callup.n == 3
    with pytest.raises(RulesError):  # still type-checked
        apply_readings(book, {"global.callup.n": "three"}, allow_unlisted=True)


def test_same_value_is_type_aware():
    assert same_value(3000, 3000.0) and same_value(None, None) and same_value("a", "a")
    assert not same_value(True, 1) and not same_value(0, None) and not same_value(1, "1")
