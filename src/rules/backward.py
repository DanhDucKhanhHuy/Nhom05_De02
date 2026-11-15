"""Suy diễn lùi, hỏi người dùng về dữ kiện đầu vào còn thiếu."""
import json
from pathlib import Path

from src.contracts import HoiNguoiDung, Luat

VOCABULARY_PATH = Path(__file__).with_name("vocabulary.json")


def _questions() -> dict[str, str]:
    """Đọc câu hỏi tiếng Việt cho các thuộc tính đầu vào."""
    try:
        document = json.loads(VOCABULARY_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return {
        name: definition["cau_hoi"]
        for name, definition in document.get("thuoc_tinh", {}).items()
        if isinstance(definition, dict)
        and definition.get("loai") == "du_kien_nguoi_dung"
        and isinstance(definition.get("cau_hoi"), str)
    }


def backward(goal: str, facts: set[str], rules: list[Luat], hoi_nguoi_dung: HoiNguoiDung) -> bool:
    """Chứng minh đích bằng facts, luật đệ quy hoặc câu trả lời người dùng.

    ``None`` được ghi nhận là chưa biết và không được xem như ``False`` trong
    tập facts. Một mục tiêu chỉ được hỏi tối đa một lần trong cùng lần suy diễn.
    """
    answers: dict[str, bool | None] = {}
    visiting: set[str] = set()
    questions = _questions()

    def prove(target: str) -> bool:
        if target in facts:
            return True
        if target in visiting:
            return False
        visiting.add(target)
        try:
            for rule in rules:
                if rule["thi"] == target and all(prove(item) for item in rule["neu"]):
                    return True
            attribute, separator, value = target.partition("=")
            if separator and attribute in questions:
                if any(fact.startswith(f"{attribute}=") for fact in facts):
                    return False
                if attribute not in answers:
                    answers[attribute] = hoi_nguoi_dung(questions[attribute])
                answer = answers[attribute]
                return (
                    (answer is True and value == "co")
                    or (answer is False and value == "khong")
                    or (answer is None and value == "chua_biet")
                )
            return False
        finally:
            visiting.remove(target)

    return prove(goal)
