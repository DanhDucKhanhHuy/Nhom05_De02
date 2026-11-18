"""Kiểm tra suy diễn tiến bằng luật ký hiệu, tách khỏi tri thức bệnh lúa."""
import json
from pathlib import Path

import pytest

from src.rules.forward import forward


@pytest.fixture
def rules():
    """Đọc bộ luật thử nghiệm; tạo dữ liệu mới cho mỗi test."""
    fixture_path = Path(__file__).parent / "fixtures" / "forward_rules.json"
    return json.loads(fixture_path.read_text(encoding="utf-8"))["rules"]


class CountedRules(list):
    """Đếm vòng duyệt; chặn test sau số vòng hữu hạn nếu thuật toán không dừng."""

    def __init__(self, rules, max_passes):
        super().__init__(rules)
        self.passes = 0
        self.max_passes = max_passes

    def __iter__(self):
        self.passes += 1
        assert self.passes <= self.max_passes, "Thuật toán không dừng đúng lúc."
        return super().__iter__()


def test_forward_builds_multi_step_closure(rules):
    """R1 đến R5 nối thành chuỗi, giữ cả dữ kiện không tham gia luật."""
    assert forward({"a=co", "d=co", "ngoai_chuoi=co"}, rules) == {
        "a=co", "b=co", "c=co", "d=co", "e=co", "f=co", "g=co", "ngoai_chuoi=co"
    }


def test_forward_requires_all_conditions(rules):
    """Thiếu d thì R3 không được suy ra e, f hoặc g."""
    assert forward({"a=co"}, rules) == {"a=co", "b=co", "c=co"}


def test_forward_empty_facts_stop_after_one_pass(rules):
    """Không luật nào khớp: vòng đầu không thêm gì và phải dừng."""
    counted = CountedRules(rules, max_passes=1)
    assert forward(set(), counted) == set()
    assert counted.passes == 1


def test_forward_empty_rules_keep_initial_facts():
    """Không có luật thì bao đóng chính là dữ kiện ban đầu."""
    assert forward({"a=co"}, []) == {"a=co"}


def test_forward_duplicate_conclusions_stop(rules):
    """R1 và R6 cùng suy ra b; b chỉ xuất hiện một lần và không gây lặp vô hạn."""
    counted = CountedRules([rules[0], rules[5]], max_passes=2)
    assert forward({"a=co"}, counted) == {"a=co", "b=co"}
    assert counted.passes == 2


def test_forward_reversed_rules_have_same_closure(rules):
    """Đảo luật có thể cần thêm vòng, nhưng không thay đổi bao đóng cuối."""
    facts = {"a=co", "d=co"}
    expected = {"a=co", "b=co", "c=co", "d=co", "e=co", "f=co", "g=co"}
    assert forward(facts, rules) == expected
    assert forward(facts, list(reversed(rules))) == expected


def test_forward_does_not_mutate_inputs(rules):
    """Chỉ tập kết quả được mở rộng; facts và bộ luật đầu vào giữ nguyên."""
    facts = {"a=co", "d=co"}
    original_rules = json.dumps(rules, ensure_ascii=False, sort_keys=True)
    result = forward(facts, rules)
    assert facts == {"a=co", "d=co"}
    assert result is not facts
    assert json.dumps(rules, ensure_ascii=False, sort_keys=True) == original_rules


def test_forward_uses_new_facts_immediately_in_rule_order(rules):
    """Chuỗi đúng thứ tự hoàn tất trong một vòng, rồi một vòng xác nhận dừng."""
    counted = CountedRules(rules, max_passes=2)
    assert forward({"a=co", "d=co"}, counted) == {
        "a=co", "b=co", "c=co", "d=co", "e=co", "f=co", "g=co"
    }
    assert counted.passes == 2


def test_forward_known_conclusions_stop_after_one_pass(rules):
    """Điều kiện vẫn đúng nhưng kết luận đã biết thì không tính là sự kiện mới."""
    facts = {"a=co", "b=co", "c=co", "d=co", "e=co", "f=co", "g=co"}
    counted = CountedRules(rules, max_passes=1)
    assert forward(facts, counted) == facts
    assert counted.passes == 1
