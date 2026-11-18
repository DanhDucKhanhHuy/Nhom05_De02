"""Suy diễn tiến từ sự kiện đã biết qua các luật IF–THEN."""
from src.contracts import Luat, VetLuat
from src.rules.trace import rule_step


def forward(facts: set[str], rules: list[Luat]) -> set[str]:
    """Trả bao đóng gồm dữ kiện ban đầu và mọi sự kiện suy ra được.

    Duyệt luật theo thứ tự, thêm kết luận ngay khi mọi điều kiện đều đã biết.
    Lặp đến khi một vòng không thêm sự kiện mới. Không sửa facts hoặc rules.
    Hàm chỉ trả tập sự kiện, không lưu thứ tự các luật đã bắn.
    """
    known, _ = forward_with_trace(facts, rules)
    return known


def forward_with_trace(facts: set[str], rules: list[Luat]) -> tuple[set[str], list[VetLuat]]:
    """Tính bao đóng như forward, đồng thời ghi các lần thêm kết luận mới."""
    known = set(facts)
    trace: list[VetLuat] = []
    while True:
        changed = False
        for rule in rules:
            conclusion = rule["thi"]
            if conclusion in known:
                continue
            if all(condition in known for condition in rule["neu"]):
                # Luật phía sau dùng được kết luận này ngay trong cùng vòng.
                known.add(conclusion)
                trace.append(rule_step(rule))
                changed = True
        # Không có sự kiện mới nghĩa là đã đạt điểm cố định.
        if not changed:
            return known, trace
