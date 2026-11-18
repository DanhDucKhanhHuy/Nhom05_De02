"""Dùng chung cách dựng lộ trình và đo chỉ số cho các chiến lược."""

from time import perf_counter

from src.contracts import BanDo, LoTrinh, SuKien, SuKienBay
from src.drone import ActionType, DroneProblem, DroneState, Transition


def tao_bai_toan(ban_do: BanDo, k: int, p: int) -> DroneProblem:
    """Tạo bài toán với ngân sách truyền vào, không sửa bản đồ gốc."""
    return DroneProblem({**ban_do, "k": k, "p": p})


def di_theo_duong(
    problem: DroneProblem,
    state: DroneState,
    dich: tuple[int, int],
) -> tuple[DroneState, list[Transition]]:
    """Đổi một đường A* thành các toán tử bay hợp lệ."""
    duong = problem.path_to(state, dich)
    if duong is None:
        raise ValueError(f"Không có đường bay an toàn đến {dich}.")

    cac_buoc: list[Transition] = []
    i = 1
    while i < len(duong):
        vat_can = []
        while problem.cells[duong[i][0]][duong[i][1]] == -1:
            vat_can.append(duong[i])
            i += 1
        o_den = duong[i]
        buoc = next(
            (
                item
                for item in problem.successors(state)
                if item.action.kind is ActionType.MOVE
                and item.action.position == o_den
                and item.action.crossed_obstacles == tuple(vat_can)
            ),
            None,
        )
        if buoc is None:
            raise RuntimeError("Đường A* chứa một bước bay không hợp lệ.")
        cac_buoc.append(buoc)
        state = buoc.state
        i += 1
    return state, cac_buoc


def tao_lo_trinh(
    problem: DroneProblem,
    transitions: list[Transition],
    started_at: float,
) -> LoTrinh:
    """Dựng kết quả chung, đếm quãng đường và lượt đáp xuống trạm."""
    duong = [problem.start]
    su_kien: list[SuKien | SuKienBay] = []
    quang_duong = 0
    ve_tram = 0

    for buoc in transitions:
        hanh_dong = buoc.action
        if hanh_dong.kind is ActionType.MOVE:
            quang_duong += buoc.cost
            duong.extend(hanh_dong.crossed_obstacles)
            duong.append(hanh_dong.position)
            ve_tram += hanh_dong.position in problem.stations
            su_kien.append(
                {
                    "loai": "bay",
                    "vi_tri": hanh_dong.position,
                    "quang_duong": buoc.cost,
                    "pin_tieu_hao": buoc.battery_cost,
                    "qua_vat_can": hanh_dong.crossed_obstacles,
                }
            )
            continue
        elif hanh_dong.kind is ActionType.SPRAY:
            loai = "phun"
        else:
            loai = "nap"
        su_kien.append({"loai": loai, "vi_tri": hanh_dong.position})

    return {
        "duong_di": duong,
        "su_kien": su_kien,
        "tong_quang_duong": quang_duong,
        "so_lan_ve_tram": ve_tram,
        "thoi_gian_chay": perf_counter() - started_at,
    }
