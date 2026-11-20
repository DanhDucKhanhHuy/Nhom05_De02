"""Lập lộ trình bằng chiến lược tham lam: ghé ô bệnh khả thi gần nhất."""

from time import perf_counter

from src.contracts import BanDo, LoTrinh
from src.drone import ActionType, DroneProblem, DroneState, Transition
from src.search.route_utils import di_theo_duong, tao_bai_toan, tao_lo_trinh


def greedy_route(ban_do: BanDo, k: int, p: int) -> LoTrinh:
    """Luôn chọn ô bệnh gần nhất đang tới được với lượng thuốc/pin hiện có."""
    bat_dau = perf_counter()
    bai_toan = tao_bai_toan(ban_do, k, p)
    state = bai_toan.initial_state
    cac_buoc: list[Transition] = []

    while not bai_toan.is_goal(state):
        if not state.untreated:
            tram = _tram_gan_nhat(bai_toan, state)
            state, bay_den = di_theo_duong(bai_toan, state, tram)
            cac_buoc.extend(bay_den)
            continue

        cac_o_toi_duoc = []
        if state.medicine > 0:
            for o_benh in sorted(state.untreated):
                duong = bai_toan.path_to(state, o_benh)
                if duong is not None:
                    cac_o_toi_duoc.append((len(duong) - 1, o_benh))

        if cac_o_toi_duoc:
            _, o_benh = min(cac_o_toi_duoc)
            state, bay_den = di_theo_duong(bai_toan, state, o_benh)
            cac_buoc.extend(bay_den)
            phun = next(
                (
                    buoc
                    for buoc in bai_toan.successors(state)
                    if buoc.action.kind is ActionType.SPRAY
                ),
                None,
            )
            if phun is None:
                raise RuntimeError("Ô bệnh được chọn không thể phun ở trạng thái hiện tại.")
            cac_buoc.append(phun)
            state = phun.state
            continue

        tram = _tram_can_nap(bai_toan, state)
        state, bay_den = di_theo_duong(bai_toan, state, tram)
        cac_buoc.extend(bay_den)
        nap = next(
            (buoc for buoc in bai_toan.successors(state) if buoc.action.kind is ActionType.REFILL),
            None,
        )
        if nap is None:
            raise ValueError(
                "Không thể tiếp tục: drone không tới được ô bệnh nào và không cần nạp "
                "tại trạm hiện tại."
            )
        cac_buoc.append(nap)
        state = nap.state

    return tao_lo_trinh(bai_toan, cac_buoc, bat_dau)


def _tram_can_nap(problem: DroneProblem, state: DroneState) -> tuple[int, int]:
    """Chọn trạm gần nhất có thể mở ra đường an toàn tới ô bệnh còn lại."""
    cac_tram = []
    for tram in sorted(problem.stations):
        duong = problem.path_to(state, tram)
        if duong is None:
            continue

        da_nap_day = DroneState(
            position=tram,
            medicine=problem.capacity,
            battery=problem.battery_capacity,
            untreated=state.untreated,
        )
        toi_duoc_o_benh = any(
            problem.path_to(da_nap_day, o_benh) is not None for o_benh in state.untreated
        )
        if toi_duoc_o_benh:
            cac_tram.append((len(duong) - 1, tram))

    if not cac_tram:
        raise ValueError("Không có trạm nào mở ra đường bay an toàn tới ô bệnh còn lại.")
    return min(cac_tram)[1]


def _tram_gan_nhat(problem: DroneProblem, state: DroneState) -> tuple[int, int]:
    cac_tram = []
    for tram in sorted(problem.stations):
        duong = problem.path_to(state, tram)
        if duong is not None:
            cac_tram.append((len(duong) - 1, tram))
    if not cac_tram:
        raise ValueError("Không có đường bay an toàn về trạm.")
    return min(cac_tram)[1]
