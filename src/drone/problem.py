"""Không gian trạng thái của bài toán lập lộ trình drone."""

import heapq

from src.contracts import BanDo, ToaDo
from src.drone.A_star import a_star
from src.drone.navigation import cac_chuyen_bay
from src.drone.operators import Transition, bay, nap, phun
from src.drone.state import DroneState

_MA_HOP_LE = {-1, 0, 1, 2, 3, 9}


class DroneProblem:
    """Mô tả trạng thái đầu, đích và các chuyển trạng thái hợp lệ.

    Mã ô: -1 là vật cản, 0 là lúa khỏe, 1–3 là ô bệnh và 9 là trạm.
    Lưới chính thức tối thiểu 20 × 20; lưới nhỏ vẫn được chấp nhận cho
    kiểm thử và ví dụ minh họa.
    """

    def __init__(self, ban_do: BanDo) -> None:
        self.cells, self.start, self.capacity, self.battery_capacity = self._kt_ban_do(ban_do)
        self.rows = len(self.cells)
        self.cols = len(self.cells[0])
        self.stations = frozenset(
            (row, col)
            for row in range(self.rows)
            for col in range(self.cols)
            if self.cells[row][col] == 9
        )
        self.targets = frozenset(
            (row, col)
            for row in range(self.rows)
            for col in range(self.cols)
            if self.cells[row][col] in {1, 2, 3}
        )
        self._station_distances = self._pin_den_tram()
        self.initial_state = DroneState(
            position=self.start,
            medicine=self.capacity,
            battery=self.battery_capacity,
            untreated=self.targets,
        )

    @staticmethod
    def _so_nguyen(value: object) -> bool:
        return isinstance(value, int) and not isinstance(value, bool)

    @classmethod
    def _kt_ban_do(cls, ban_do: BanDo) -> tuple[tuple[tuple[int, ...], ...], ToaDo, int, int]:
        so_hang, so_cot = ban_do["rows"], ban_do["cols"]
        k, p = ban_do["k"], ban_do["p"]
        bat_dau, luoi = ban_do["start"], ban_do["cells"]

        if not cls._so_nguyen(so_hang) or not cls._so_nguyen(so_cot) or so_hang < 1 or so_cot < 1:
            raise ValueError("rows và cols phải là số nguyên dương.")
        if not cls._so_nguyen(k) or not cls._so_nguyen(p) or k < 1 or p < 1:
            raise ValueError("k và p phải là số nguyên dương.")
        if len(luoi) != so_hang or any(len(hang) != so_cot for hang in luoi):
            raise ValueError("Kích thước cells không khớp rows và cols.")
        if (
            not isinstance(bat_dau, list)
            or len(bat_dau) != 2
            or not all(cls._so_nguyen(v) for v in bat_dau)
        ):
            raise ValueError("start phải gồm hai tọa độ nguyên [hàng, cột].")
        if any(not cls._so_nguyen(o) or o not in _MA_HOP_LE for hang in luoi for o in hang):
            raise ValueError("cells chỉ được chứa -1, 0, 1, 2, 3 hoặc 9.")

        cells = tuple(tuple(hang) for hang in luoi)
        start = (bat_dau[0], bat_dau[1])
        if not (0 <= start[0] < so_hang and 0 <= start[1] < so_cot):
            raise ValueError("start nằm ngoài bản đồ.")
        if cells[start[0]][start[1]] != 9:
            raise ValueError("start phải nằm tại một trạm nạp.")
        if not any(cell == 9 for row in cells for cell in row):
            raise ValueError("Bản đồ phải có ít nhất một trạm nạp.")

        return cells, start, k, p

    def _pin_den_tram(self) -> dict[ToaDo, int]:
        pin_min = {tram: 0 for tram in self.stations}
        mo = [(0, tram) for tram in self.stations]
        heapq.heapify(mo)

        while mo:
            pin, vt = heapq.heappop(mo)
            if pin != pin_min[vt]:
                continue
            for ke, _, _, pin_ton in cac_chuyen_bay(self.cells, vt):
                pin_moi = pin + pin_ton
                if pin_moi < pin_min.get(ke, float("inf")):
                    pin_min[ke] = pin_moi
                    heapq.heappush(mo, (pin_moi, ke))
        return pin_min

    def is_goal(self, state: DroneState) -> bool:
        """Đích: mọi ô bệnh đã phun và drone đang ở một trạm."""
        self._kt_trang_thai(state)
        return not state.untreated and state.position in self.stations

    def successors(self, state: DroneState) -> tuple[Transition, ...]:
        """Trả các toán tử hợp lệ từ trạng thái hiện tại."""
        self._kt_trang_thai(state)
        result: list[Transition] = []

        for dich, vat_can, quang_duong, pin_ton in cac_chuyen_bay(self.cells, state.position):
            pin_den_tram = self._station_distances.get(dich)
            if pin_den_tram is not None:
                chuyen = bay(
                    state,
                    dich,
                    pin_den_tram,
                    quang_duong,
                    pin_ton,
                    vat_can,
                )
                if chuyen is not None:
                    result.append(chuyen)

        if state.position in state.untreated:
            chuyen = phun(state, state.position)
            if chuyen is not None:
                result.append(chuyen)

        chuyen = nap(
            state,
            self.capacity,
            self.battery_capacity,
            tai_tram=state.position in self.stations,
        )
        if chuyen is not None:
            result.append(chuyen)

        return tuple(result)

    def path_to(self, state: DroneState, destination: ToaDo) -> list[ToaDo] | None:
        """Tìm đường bay an toàn đến đích bằng A*, gồm cả ô đầu và ô cuối."""
        self._kt_trang_thai(state)
        kq = a_star(
            self.cells,
            state.position,
            destination,
            battery=state.battery,
            distances_to_station=self._station_distances,
        )
        return None if kq is None else kq[0]

    def distance_to_station(self, position: ToaDo) -> int | None:
        """Trả khoảng cách bay ngắn nhất tới trạm gần nhất, nếu tới được."""
        return self._station_distances.get(position)

    def _kt_trang_thai(self, state: DroneState) -> None:
        if not isinstance(state, DroneState):
            raise ValueError("state phải là DroneState.")
        row, col = state.position
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            raise ValueError("Vị trí trạng thái nằm ngoài bản đồ.")
        if self.cells[row][col] == -1:
            raise ValueError("Drone không thể ở trên ô vật cản.")
        if not 0 <= state.medicine <= self.capacity:
            raise ValueError("Lượng thuốc nằm ngoài giới hạn bình.")
        if not 0 <= state.battery <= self.battery_capacity:
            raise ValueError("Pin nằm ngoài giới hạn pin.")
        if not state.untreated <= self.targets:
            raise ValueError("untreated chỉ được chứa tọa độ ô bệnh trên bản đồ.")
