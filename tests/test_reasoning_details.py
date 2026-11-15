"""Kiểm tra API bổ sung; các API cũ vẫn được kiểm tra trong test riêng."""
import copy
import json
from pathlib import Path

import pytest

import src.rules.backward as backward_module
import src.rules.forward as forward_module

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def rules(monkeypatch):
    """Dùng luật và từ vựng ký hiệu riêng, không sửa dữ liệu nghiệp vụ."""
    monkeypatch.setattr(backward_module, "VOCABULARY_PATH", FIXTURES / "backward_vocabulary.json")
    return json.loads((FIXTURES / "backward_rules.json").read_text(encoding="utf-8"))["rules"]


def test_forward_trace_replays_actual_firing_order_and_skips_duplicates():
    rules = json.loads((FIXTURES / "forward_rules.json").read_text(encoding="utf-8"))["rules"]
    original = copy.deepcopy(rules)
    facts = {"a=co", "d=co"}
    known, trace = forward_module.forward_with_trace(facts, rules)
    assert [step["id"] for step in trace] == ["R1", "R2", "R3", "R4", "R5"]
    replay = set(facts)
    for step in trace:
        assert set(step["dieu_kien"]) <= replay
        assert step["ket_luan"] not in replay
        replay.add(step["ket_luan"])
    assert replay == known == forward_module.forward(facts, rules)
    trace[0]["dieu_kien"].append("khong_duoc_sua=co")
    trace[0]["nguon"]["ma"] = "KHONG_DUOC_SUA"
    assert rules == original
    assert facts == {"a=co", "d=co"}


def test_forward_trace_empty_facts_is_empty():
    rules = json.loads((FIXTURES / "forward_rules.json").read_text(encoding="utf-8"))["rules"]
    assert forward_module.forward_with_trace(set(), rules) == (set(), [])


@pytest.mark.parametrize("answer, expected", [
    (True, "xac_nhan"), (False, "bac_bo"), (None, "chua_du"),
])
def test_backward_distinguishes_three_outcomes(rules, answer, expected):
    result = backward_module.backward_with_status("c=co", set(), rules, lambda _: answer)
    assert result["trang_thai"] == expected
    if expected == "xac_nhan":
        assert [step["id"] for step in result["vet"]] == ["B1", "B2"]
    else:
        assert result["vet"] == []


def test_backward_known_false_can_reject_and_even_after_unknown(rules):
    questions = []
    result = backward_module.backward_with_status(
        "c=co", {"d=khong"}, rules, lambda q: questions.append(q))
    assert result["trang_thai"] == "bac_bo"
    assert questions == ["Bạn có quan sát dấu hiệu A không?"]


def test_backward_false_short_circuits_and(rules):
    questions = []
    result = backward_module.backward_with_status(
        "c=co", set(), rules, lambda q: questions.append(q) or False)
    assert result["trang_thai"] == "bac_bo"
    assert questions == ["Bạn có quan sát dấu hiệu A không?"]


def test_backward_or_keeps_only_successful_proof(rules):
    result = backward_module.backward_with_status("e=co", {"h=co"}, rules, lambda _: None)
    assert result["trang_thai"] == "xac_nhan"
    assert [step["id"] for step in result["vet"]] == ["B4"]


def test_backward_or_unknown_branch_prevents_rejection(rules):
    result = backward_module.backward_with_status("e=co", {"h=khong"}, rules, lambda _: None)
    assert result["trang_thai"] == "chua_du"


def test_backward_or_all_rejected_is_rejected(rules):
    result = backward_module.backward_with_status("e=co", set(), rules, lambda _: False)
    assert result["trang_thai"] == "bac_bo"


def test_backward_cycle_is_unknown_but_independent_exit_can_succeed(rules):
    assert backward_module.backward_with_status(
        "f=co", set(), rules, lambda _: True)["trang_thai"] == "chua_du"
    exit_rule = {**rules[0], "id": "EXIT", "thi": "f=co"}
    result = backward_module.backward_with_status(
        "f=co", {"a=co"}, [*rules, exit_rule], lambda _: None)
    assert result["trang_thai"] == "xac_nhan"
    assert [step["id"] for step in result["vet"]] == ["EXIT"]


def test_backward_unknown_fact_and_unsupported_goal_remain_unknown(rules):
    for goal, facts in [("a=co", {"a=chua_biet"}), ("khong_co_trong_luat=co", set())]:
        result = backward_module.backward_with_status(goal, facts, rules, lambda _: True)
        assert result["trang_thai"] == "chua_du"


def test_backward_explicit_unknown_value_is_preserved(rules):
    assert backward_module.backward_with_status(
        "a=chua_biet", set(), rules, lambda _: None)["trang_thai"] == "xac_nhan"


def test_backward_status_asks_once_and_does_not_mutate_inputs(rules):
    original = copy.deepcopy(rules)
    first = {**rules[0], "id": "FIRST", "neu": ["a=co", "d=co"], "thi": "e=co"}
    second = {**first, "id": "SECOND"}
    questions = []
    facts = {"d=khong"}
    result = backward_module.backward_with_status(
        "e=co", facts, [first, second], lambda q: questions.append(q) or True)
    assert result["trang_thai"] == "bac_bo"
    assert questions == ["Bạn có quan sát dấu hiệu A không?"]
    assert facts == {"d=khong"}
    assert rules == original


def test_backward_status_never_asks_derived_attributes(rules):
    questions = []
    result = backward_module.backward_with_status(
        "b=co", set(), [], lambda q: questions.append(q) or True)
    assert result["trang_thai"] == "chua_du"
    assert questions == []


def test_backward_status_rejects_invalid_callback_answer(rules):
    with pytest.raises(ValueError, match="True, False hoặc None"):
        backward_module.backward_with_status("a=co", set(), rules, lambda _: "có")
