"""Đặc tả CN1; Dijkstra chỉ là đối chứng trong test, không dùng làm lời giải đồ án.

Luật bay: sang ô kề không phải vật cản tốn 1 bước, 1 pin; được bay thẳng vượt
một dải vật cản liên tiếp để đáp xuống ô đầu tiên sau dải, tốn (số vật cản + 1)
bước và (2 × số vật cản + 1) pin.
"""
import heapq

import pytest

from src.drone import a_star
from src.search.run import plan_route


def chuyen_bay(cells, vt):
    """Các chuyến bay hợp lệ từ vt: (đích, số vật cản vượt qua)."""
    so_hang, so_cot = len(cells), len(cells[0])
    for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
        r, c = vt[0] + dr, vt[1] + dc
        so_vat_can = 0
        while 0 <= r < so_hang and 0 <= c < so_cot and cells[r][c] == -1:
            so_vat_can += 1
            r, c = r + dr, c + dc
        if 0 <= r < so_hang and 0 <= c < so_cot:
            yield (r, c), so_vat_can


def chi_phi_ngan_nhat(cells, start, goal, theo_pin=False):
    """Dijkstra đối chứng: số bước (hoặc số pin) ít nhất từ start đến goal."""
    if cells[goal[0]][goal[1]] == -1:
        return None
    tot_nhat = {start: 0}
    mo = [(0, start)]
    while mo:
        chi_phi, vt = heapq.heappop(mo)
        if vt == goal:
            return chi_phi
        if chi_phi > tot_nhat[vt]:
            continue
        for dich, so_vat_can in chuyen_bay(cells, vt):
            them = 2 * so_vat_can + 1 if theo_pin else so_vat_can + 1
            if chi_phi + them < tot_nhat.get(dich, float("inf")):
                tot_nhat[dich] = chi_phi + them
                heapq.heappush(mo, (chi_phi + them, dich))
    return None


@pytest.mark.parametrize("cells,start,goal", [
    ([[9, 0, 0], [0, -1, 0], [0, 0, 1]], (0, 0), (2, 2)),
    ([[9, -1, 1], [0, -1, 0], [0, 0, 0]], (0, 0), (0, 2)),
    ([[9, -1, 1]], (0, 0), (0, 2)),
    ([[9, -1, -1]], (0, 0), (0, 2)),
    ([[9]], (0, 0), (0, 0)),
])
def test_astar_matches_dijkstra(cells, start, goal):
    expected = chi_phi_ngan_nhat(cells, start, goal)
    ket_qua = a_star(cells, start, goal)
    if expected is None:
        assert ket_qua is None
        return
    path, so_buoc, _ = ket_qua
    assert path[0] == start and path[-1] == goal
    assert so_buoc == expected == len(path) - 1
    for row, col in path:
        assert 0 <= row < len(cells) and 0 <= col < len(cells[0])
    # vật cản chỉ được bay qua, không được đáp xuống
    assert cells[goal[0]][goal[1]] != -1
    assert all(abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1
               for a, b in zip(path, path[1:]))


@pytest.mark.parametrize("algorithm", ["hill", "greedy"])
def test_route_resources_and_completion(algorithm):
    # k=1 buộc nạp; mức 3 vẫn chỉ tốn một đơn vị thuốc.
    grid = {"rows": 2, "cols": 3, "start": [0, 0], "k": 1, "p": 6,
            "cells": [[9, 3, 0], [0, -1, 1]]}
    result = plan_route(grid, 1, 6, algorithm)
    position = (0, 0)
    medicine, battery = 1, 6
    untreated = {(0, 1), (1, 2)}
    path = [position]
    returns = 0
    for event in result["su_kien"]:
        target = tuple(event["vi_tri"])
        if event["loai"] == "bay":
            vat_can = [tuple(o) for o in event["qua_vat_can"]]
            chang = [position, *vat_can, target]
            assert all(abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1
                       for a, b in zip(chang, chang[1:]))
            assert all(grid["cells"][r][c] == -1 for r, c in vat_can)
            assert 0 <= target[0] < 2 and 0 <= target[1] < 3
            assert grid["cells"][target[0]][target[1]] != -1
            assert event["quang_duong"] == len(vat_can) + 1
            assert event["pin_tieu_hao"] == 2 * len(vat_can) + 1
            battery -= event["pin_tieu_hao"]
            position = target
            path.extend(chang[1:])
            returns += position == (0, 0)
        elif event["loai"] == "phun":
            assert target == position and target in untreated
            medicine -= 1
            untreated.remove(target)
        else:
            assert event["loai"] == "nap" and target == position == (0, 0)
            medicine, battery = 1, 6
        assert 0 <= medicine <= 1 and 0 <= battery <= 6
        assert battery >= chi_phi_ngan_nhat(grid["cells"], position, (0, 0), theo_pin=True)
    assert not untreated and position == (0, 0)
    assert [tuple(cell) for cell in result["duong_di"]] == path
    assert result["tong_quang_duong"] == len(path) - 1
    assert result["so_lan_ve_tram"] == returns
    assert result["thoi_gian_chay"] >= 0


@pytest.mark.parametrize("k,p", [(0, 4), (1, 1)])
def test_route_rejects_invalid_or_infeasible(k, p):
    grid = {"rows": 1, "cols": 2, "start": [0, 0], "k": k, "p": p,
            "cells": [[9, 1]]}
    with pytest.raises(ValueError):
        plan_route(grid, k, p, "hill")


def test_route_rejects_unknown_algorithm():
    grid = {"rows": 1, "cols": 2, "start": [0, 0], "k": 1, "p": 4,
            "cells": [[9, 1]]}
    with pytest.raises(ValueError):
        plan_route(grid, 1, 4, "khong_co")
