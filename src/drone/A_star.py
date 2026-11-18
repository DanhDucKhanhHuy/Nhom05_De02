"""A* tìm đường bay giữa hai ô trên bản đồ lưới."""

import heapq
from collections.abc import Mapping, Sequence
from itertools import count

from src.contracts import ToaDo
from src.drone.navigation import cac_chuyen_bay


def a_star(
    cells: Sequence[Sequence[int]],
    start: ToaDo,
    goal: ToaDo,
    *,
    battery: int | None = None,
    distances_to_station: Mapping[ToaDo, int] | None = None,
) -> tuple[list[ToaDo], int, list[ToaDo]] | None:
    """Tìm đường ngắn nhất, trả về (đường, số bước, thứ tự mở rộng).

    Ô -1 không phải ô hạ cánh; bay vượt mỗi ô vật cản tốn thêm một pin.
    Có thể truyền pin hiện có và mức pin tối thiểu cần tới trạm để chỉ xét
    các đường luôn còn đủ pin quay về trạm gần nhất.
    """
    so_hang, so_cot = _kt_luoi(cells)
    if not _toa_do_hop_le(start, so_hang, so_cot) or cells[start[0]][start[1]] == -1:
        raise ValueError("start phải là tọa độ hợp lệ trên ô không phải vật cản.")
    if not _toa_do_hop_le(goal, so_hang, so_cot) or cells[goal[0]][goal[1]] == -1:
        return None
    if (battery is None) != (distances_to_station is None):
        raise ValueError("Phải truyền đồng thời battery và distances_to_station.")
    if battery is not None and (
        not isinstance(battery, int) or isinstance(battery, bool) or battery < 0
    ):
        raise ValueError("battery phải là số nguyên không âm.")
    if battery is not None and battery < distances_to_station.get(start, float("inf")):
        return None

    def uoc_luong(point: ToaDo) -> int:
        return abs(point[0] - goal[0]) + abs(point[1] - goal[1])

    stt = count()
    dau = (start, 0)
    mo = [(uoc_luong(start), 0, 0, next(stt), dau)]
    tot_nhat = {dau: 0}
    cha: dict[tuple[ToaDo, int], tuple[tuple[ToaDo, int], tuple[ToaDo, ...], ToaDo]] = {}
    da_xet: list[ToaDo] = []

    while mo:
        _, do_dai, pin_da_dung, _, nut = heapq.heappop(mo)
        if do_dai != tot_nhat.get(nut):
            continue
        vt = nut[0]
        da_xet.append(vt)
        if vt == goal:
            cac_chang = []
            while nut != dau:
                truoc, vat_can, dich = cha[nut]
                cac_chang.append((vat_can, dich))
                nut = truoc
            duong = [start]
            for vat_can, dich in reversed(cac_chang):
                duong.extend(vat_can)
                duong.append(dich)
            return duong, do_dai, da_xet

        for ke, vat_can, quang_duong, pin_ton in cac_chuyen_bay(cells, vt):
            dai_moi = do_dai + quang_duong
            pin_moi = pin_da_dung + pin_ton
            if battery is not None:
                pin_den_tram = distances_to_station.get(ke, float("inf"))
                if battery - pin_moi < pin_den_tram:
                    continue
            nut_moi = (ke, pin_moi)
            if dai_moi >= tot_nhat.get(nut_moi, float("inf")):
                continue

            tot_nhat[nut_moi] = dai_moi
            cha[nut_moi] = (nut, vat_can, ke)
            heapq.heappush(
                mo,
                (
                    dai_moi + uoc_luong(ke),
                    dai_moi,
                    pin_moi,
                    next(stt),
                    nut_moi,
                ),
            )

    return None


def _kt_luoi(cells: Sequence[Sequence[int]]) -> tuple[int, int]:
    if not cells or not cells[0]:
        raise ValueError("cells phải là lưới không rỗng.")
    so_cot = len(cells[0])
    if any(len(row) != so_cot for row in cells):
        raise ValueError("cells phải là lưới chữ nhật.")
    return len(cells), so_cot


def _toa_do_hop_le(position: ToaDo, rows: int, cols: int) -> bool:
    return (
        isinstance(position, tuple)
        and len(position) == 2
        and all(isinstance(value, int) and not isinstance(value, bool) for value in position)
        and 0 <= position[0] < rows
        and 0 <= position[1] < cols
    )
