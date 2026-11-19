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


class UngDungGia:
    def ve_man_hinh_chinh(self):
        pass

    def chuyen_den(self, man_hinh):
        self.man_hinh = man_hinh


def cho_tinh_xong(man_hinh):
    import time

    for _ in range(300):
        man_hinh.cap_nhat(0)
        if man_hinh.khung or man_hinh.loi:
            return
        time.sleep(0.02)
    raise AssertionError("tính lộ trình quá lâu")


def test_man_hinh_chay_dung_va_tung_buoc():
    from src.app.route_view import TOC_DO, ManHinhLoTrinh

    ban_do = tao_ngau_nhien(8, 8, p=100, rng=random.Random(3))
    man_hinh = ManHinhLoTrinh(UngDungGia(), ban_do)
    cho_tinh_xong(man_hinh)
    assert man_hinh.buoc == 0 and not man_hinh.loi

    man_hinh.di(1)
    man_hinh.di(1)
    man_hinh.di(-1)
    assert man_hinh.buoc == 1

    man_hinh.chay_dung()
    man_hinh.cap_nhat(1 / TOC_DO[man_hinh.muc_toc_do] * 3)
    assert man_hinh.buoc == 4

    man_hinh.cap_nhat(10_000)  # chạy tới cuối thì tự dừng
    assert man_hinh.buoc == len(man_hinh.khung) - 1 and not man_hinh.dang_chay
    man_hinh.ve_dau()
    assert man_hinh.buoc == 0


def test_man_hinh_doi_thuat_toan_va_bao_loi():
    from src.app.route_view import ManHinhLoTrinh

    nho = tao_ngau_nhien(6, 6, p=100, ty_le_benh=0.15, rng=random.Random(7))
    man_hinh = ManHinhLoTrinh(UngDungGia(), nho)
    cho_tinh_xong(man_hinh)
    man_hinh.doi_thuat_toan("astar")
    cho_tinh_xong(man_hinh)
    assert man_hinh.thuat_toan == "astar" and man_hinh.khung

    lon = tao_ngau_nhien(20, 20, p=100, rng=random.Random(1))
    man_hinh = ManHinhLoTrinh(UngDungGia(), lon, thuat_toan="astar")
    cho_tinh_xong(man_hinh)
    assert "A*" in man_hinh.loi and not man_hinh.nut_thuat_toan["astar"].bat


def test_quay_lai_man_hinh_ban_do():
    from src.app.grid_editor import ManHinhBanDo

    ung_dung = UngDungGia()
    ban_do_man_hinh = ManHinhBanDo(ung_dung, tao_ngau_nhien(8, 8, rng=random.Random(2)))
    ban_do_man_hinh.lap_lo_trinh()
    lo_trinh = ung_dung.man_hinh
    assert lo_trinh.ban_do == ban_do_man_hinh.ban_do and lo_trinh.ban_do is not ban_do_man_hinh.ban_do
    lo_trinh.quay_lai()
    assert ung_dung.man_hinh is ban_do_man_hinh
