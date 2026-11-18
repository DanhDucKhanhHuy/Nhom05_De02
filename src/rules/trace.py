"""Tạo vết dùng chung cho hai chiều suy diễn, không sửa dữ liệu luật."""
from src.contracts import Luat, VetLuat


def rule_step(rule: Luat) -> VetLuat:
    """Chụp điều kiện và nguồn để sửa vết không làm thay đổi bộ luật gốc."""
    return {
        "id": rule["id"],
        "dieu_kien": list(rule["neu"]),
        "ket_luan": rule["thi"],
        "nguon": {"ma": rule["nguon"]["ma"], "muc": rule["nguon"]["muc"]},
    }


def unique_steps(steps: list[VetLuat]) -> list[VetLuat]:
    """Giữ lần xuất hiện đầu tiên của mỗi luật theo thứ tự chứng minh."""
    seen = set()
    result = []
    for step in steps:
        if step["id"] not in seen:
            seen.add(step["id"])
            result.append(step)
    return result
