"""Kiểm thử E3 - dựng khung hình lộ trình"""
import json
import os
import random

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import pytest

from src.app.grid_editor import TRAM, tao_ngau_nhien
from src.app.route_view import dem_o_benh, dung_khung_hinh, lap_lo_trinh


def kiem_tra_khung(ban_do, lo_trinh):
    khung, vet, thoi_diem_phun = dung_khung_hinh(ban_do, lo_trinh)
    assert len(khung) == len(lo_trinh["su_kien"]) + 1
    for kh in khung:
        assert 0 <= kh["thuoc"] <= ban_do["k"]
        assert 0 <= kh["pin"] <= ban_do["p"]
    cuoi = khung[-1]
    assert cuoi["quang_duong"] == lo_trinh["tong_quang_duong"]
    assert cuoi["ve_tram"] == lo_trinh["so_lan_ve_tram"]
    assert cuoi["da_phun"] == dem_o_benh(ban_do) == len(thoi_diem_phun)
    r, c = cuoi["vi_tri"]
    assert ban_do["cells"][r][c] == TRAM  # kết thúc ở trạm
    assert vet == [tuple(o) for o in lo_trinh["duong_di"]]


def test_ban_do_mau_cua_nhom():
    with open("data/sample/maps/map_4x4.json", encoding="utf-8") as f:
        ban_do = json.load(f)
    kiem_tra_khung(ban_do, lap_lo_trinh(ban_do))


@pytest.mark.parametrize("hat_giong", range(5))
def test_tham_lam_tren_ban_do_ngau_nhien(hat_giong):
    ban_do = tao_ngau_nhien(10, 10, p=100, rng=random.Random(hat_giong))
    kiem_tra_khung(ban_do, lap_lo_trinh(ban_do, "greedy"))


def test_astar_tren_ban_do_nho():
    ban_do = tao_ngau_nhien(6, 6, p=100, ty_le_benh=0.15, rng=random.Random(7))
    kiem_tra_khung(ban_do, lap_lo_trinh(ban_do, "astar"))


def test_astar_tu_choi_ban_do_nhieu_o_benh():
    ban_do = tao_ngau_nhien(20, 20, p=100, rng=random.Random(1))
    with pytest.raises(ValueError, match="A\\*"):
        lap_lo_trinh(ban_do, "astar")

