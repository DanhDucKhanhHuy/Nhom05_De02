"""Lập lộ trình đầy đủ; đầu vào sai hoặc không khả thi ném ValueError."""
from src.contracts import BanDo, LoTrinh, ThuatToan
from src.search.greedy import greedy_route
from src.search.Hill_Climbing import hill_climbing_route


def plan_route(ban_do: BanDo, k: int, p: int, thuat_toan: ThuatToan) -> LoTrinh:
    """Lập lộ trình đầy đủ theo chiến lược đã chọn.

    - "greedy": tham lam, ghé ô bệnh gần nhất.
    - "hill": leo đồi trên thứ tự ghé, xuất phát từ lời giải tham lam.
    """
    for ten, gia_tri in (("k", k), ("p", p)):
        if not isinstance(gia_tri, int) or isinstance(gia_tri, bool) or gia_tri < 1:
            raise ValueError(f"{ten} phải là số nguyên dương.")

    if thuat_toan == "greedy":
        return greedy_route(ban_do, k, p)
    if thuat_toan == "hill":
        return hill_climbing_route(ban_do, k, p)
    raise ValueError(f"Thuật toán không hợp lệ: {thuat_toan!r}.")
