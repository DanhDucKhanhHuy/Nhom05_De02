"""A* toàn cục trên trạng thái drone để tìm lộ trình bay ngắn nhất."""

import heapq
from itertools import count
from time import perf_counter

from src.contracts import BanDo, LoTrinh
from src.drone import DroneProblem, DroneState, Transition
from src.search.route_utils import tao_bai_toan, tao_lo_trinh


def astar_route(ban_do: BanDo, k: int, p: int) -> LoTrinh:
    """Tìm lộ trình hoàn tất tối ưu theo số bước bay bằng A* toàn cục."""
    bat_dau = perf_counter()
    bai_toan = tao_bai_toan(ban_do, k, p)
    dau = bai_toan.initial_state
    stt = count()
    mo = [(_uoc_luong(bai_toan, dau), 0, next(stt), dau)]
    tot_nhat = {dau: 0}
    cha: dict[DroneState, tuple[DroneState, Transition]] = {}

    while mo:
        _, do_dai, _, state = heapq.heappop(mo)
        if do_dai != tot_nhat.get(state):
            continue
        if bai_toan.is_goal(state):
            cac_buoc = []
            while state != dau:
                truoc, buoc = cha[state]
                cac_buoc.append(buoc)
                state = truoc
            cac_buoc.reverse()
            return tao_lo_trinh(bai_toan, cac_buoc, bat_dau)

        for buoc in bai_toan.successors(state):
            nut_moi = buoc.state
            dai_moi = do_dai + buoc.cost
            if dai_moi >= tot_nhat.get(nut_moi, float("inf")):
                continue
            tot_nhat[nut_moi] = dai_moi
            cha[nut_moi] = (state, buoc)
            heapq.heappush(
                mo,
                (dai_moi + _uoc_luong(bai_toan, nut_moi), dai_moi, next(stt), nut_moi),
            )

    raise ValueError("Không tìm thấy lộ trình hoàn tất với ngân sách thuốc/pin này.")


def _uoc_luong(problem: DroneProblem, state: DroneState) -> int | float:
    """Cận dưới admissible cho quãng đường còn lại đến khi hoàn tất."""
    if not state.untreated:
        distance = problem.distance_to_station(state.position)
        return float("inf") if distance is None else distance

    lower_bounds = []
    for target in state.untreated:
        station_distance = problem.distance_to_station(target)
        if station_distance is None:
            return float("inf")
        manhattan = abs(state.position[0] - target[0]) + abs(state.position[1] - target[1])
        lower_bounds.append(manhattan + station_distance)
    return max(lower_bounds)
