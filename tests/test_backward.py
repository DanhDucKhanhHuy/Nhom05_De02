"""Kiểm thử suy diễn lùi bằng dữ liệu ký hiệu, giữ nguyên hợp đồng bool."""
import itertools
import json
from pathlib import Path

import pytest

import src.rules.backward as backward_module
from src.rules.backward import backward
from src.rules.forward import forward

FIXTURES = Path(__file__).parent / "fixtures"
QUESTION_A = "Bạn có quan sát dấu hiệu A không?"
QUESTION_D = "Bạn có quan sát dấu hiệu D không?"
QUESTION_H = "Bạn có quan sát dấu hiệu H không?"


@pytest.fixture(autouse=True)
def vocabulary(monkeypatch):
    """Chỉ đổi đường dẫn trong test; không sửa từ vựng thật."""
    monkeypatch.setattr(backward_module, "VOCABULARY_PATH", FIXTURES / "backward_vocabulary.json")


@pytest.fixture
def rules():
    """Mỗi test nhận một bộ luật mới, bao gồm chu trình thử nghiệm."""
    return json.loads((FIXTURES / "backward_rules.json").read_text(encoding="utf-8"))["rules"]


def no_question(question):
    """Báo lỗi nếu hàm hỏi khi test yêu cầu chỉ suy diễn từ facts."""
    pytest.fail(f"Không được hỏi: {question}")


def test_backward_known_fact_needs_no_rule_or_question():
    """Đích đã biết được chứng minh ngay cả khi không có luật."""
    assert backward("b=co", {"b=co"}, [], no_question) is True


def test_backward_multi_step_asks_vietnamese_questions_in_order(rules):
    """Đi từ e qua c, b đến dữ kiện A; sau đó hỏi D."""
    questions = []
    assert backward("e=co", set(), rules, lambda q: questions.append(q) or True) is True
    assert questions == [QUESTION_A, QUESTION_D]


def test_backward_short_circuits_and_when_first_condition_is_false(rules):
    """A sai thì b sai, do đó không cần hỏi D để chứng minh c."""
    questions = []
    assert backward("c=co", set(), rules, lambda q: questions.append(q) or False) is False
    assert questions == [QUESTION_A]


@pytest.mark.parametrize("answer", [True, False, None])
@pytest.mark.parametrize("value", ["co", "khong", "chua_biet"])
def test_backward_maps_callback_answer_to_explicit_value(answer, value):
    """None chỉ khớp chua_biet, không khớp co hoặc khong."""
    questions = []

    def ask(question):
        questions.append(question)
        return answer

    expected_value = {True: "co", False: "khong", None: "chua_biet"}[answer]
    assert backward(f"a={value}", set(), [], ask) is (value == expected_value)
    assert questions == [QUESTION_A]


@pytest.mark.parametrize("answer", [True, False, None])
def test_backward_asks_once_for_multiple_values_of_one_attribute(rules, answer):
    """Ba nhánh thử ba giá trị của A nhưng chỉ hỏi A một lần."""
    alternatives = []
    for index, value in enumerate(["co", "khong", "chua_biet"]):
        rule = {**rules[0], "id": f"CACHE{index}", "neu": [f"a={value}", "d=co"],
                "thi": "e=co"}
        alternatives.append(rule)
    questions = []

    def ask(question):
        questions.append(question)
        return answer

    assert backward("e=co", {"d=khong"}, alternatives, ask) is False
    assert questions == [QUESTION_A]


@pytest.mark.parametrize("value", ["co", "khong", "chua_biet"])
def test_backward_known_attribute_is_not_asked_again(value):
    """Câu trả lời đã nằm trong facts thì không hỏi lại thuộc tính đó."""
    assert backward("a=co", {f"a={value}"}, [], no_question) is (value == "co")


def test_backward_does_not_ask_derived_attribute_without_proof():
    """Không có luật chứng minh b thì trả False, không hỏi người dùng về b."""
    assert backward("b=co", set(), [], no_question) is False


def test_backward_tries_another_rule_after_false_or_unknown(rules):
    """Nhánh qua A chưa chứng minh được; nhánh H vẫn chứng minh được e."""
    for answer in (False, None):
        questions = []
        assert backward("e=co", {"h=co"}, rules,
                        lambda q: questions.append(q) or answer) is True
        assert questions == [QUESTION_A]


def test_backward_stops_after_first_successful_rule(rules):
    """Nhánh c đã đúng thì không hỏi H ở nhánh kế tiếp."""
    assert backward("e=co", {"a=co", "d=co"}, rules, no_question) is True


def test_backward_asks_input_of_alternative_rule(rules):
    """Nhánh A đã sai thì có thể hỏi H để kiểm tra nhánh thay thế."""
    questions = []
    assert backward("e=co", {"a=khong"}, rules,
                    lambda q: questions.append(q) or True) is True
    assert questions == [QUESTION_H]


def test_backward_cycle_without_support_returns_false(rules):
    """f và g phụ thuộc lẫn nhau, không có dữ kiện gốc nên không chứng minh được."""
    assert backward("f=co", set(), rules, no_question) is False


def test_backward_cycle_does_not_hide_an_independent_proof(rules):
    """Sau nhánh chu trình, vẫn phải thử nhánh a để chứng minh f."""
    alternative = {**rules[0], "id": "EXIT", "thi": "f=co"}
    assert backward("f=co", {"a=co"}, [*rules, alternative], no_question) is True


def test_backward_releases_cycle_marker_between_branches(rules):
    """b đã xét ở nhánh thất bại vẫn có thể dùng ở nhánh sau."""
    first = {**rules[0], "id": "FIRST", "neu": ["b=co", "d=co"], "thi": "e=co"}
    second = {**rules[0], "id": "SECOND", "neu": ["b=co"], "thi": "e=co"}
    assert backward("e=co", {"a=co", "d=khong"},
                    [rules[0], first, second], no_question) is True


def test_backward_does_not_mutate_facts_or_rules(rules):
    """Dữ kiện hỏi thêm chỉ dùng trong lời gọi hiện tại."""
    facts = set()
    original_rules = json.dumps(rules, sort_keys=True)
    assert backward("e=co", facts, rules, lambda _: True) is True
    assert facts == set()
    assert json.dumps(rules, sort_keys=True) == original_rules


@pytest.mark.parametrize("values", list(itertools.product(["co", "khong"], repeat=3)))
def test_backward_agrees_with_forward_when_inputs_are_known(rules, values):
    """Đủ dữ kiện đầu vào: mọi đích phải khớp bao đóng của suy diễn tiến."""
    facts = {f"{name}={value}" for name, value in zip(["a", "d", "h"], values)}
    closure = forward(facts, rules)
    goals = {rule["thi"] for rule in rules}
    for goal in sorted(goals):
        assert backward(goal, facts, rules, no_question) is (goal in closure)
