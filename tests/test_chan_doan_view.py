"""Kiểm thử E4 - màn hình chẩn đoán ảnh"""
import os
import time

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
import pytest

from src.app.chan_doan import diagnose_image
from src.app.chan_doan_view import ManHinhChanDoan, do_rong_chu, ngat_dong, tao_noi_dung_ket_qua


class UngDungGia:
    def ve_man_hinh_chinh(self):
        pass


@pytest.fixture(autouse=True)
def khoi_dong_pygame():
    # không quit: phông đã lưu sẵn sẽ hỏng
    pygame.init()


def cho_luong(man_hinh):
    """Chờ tới khi luồng hỏi câu mới hoặc chạy xong, tối đa 5 giây"""
    het_gio = time.time() + 5
    while time.time() < het_gio:
        if man_hinh.cau_hoi is not None:
            return
        if man_hinh.luong_xong:
            man_hinh.cap_nhat(0)
            return
        time.sleep(0.01)
    raise AssertionError("luồng chẩn đoán không phản hồi")


def test_ngat_dong_vua_chieu_rong():
    cac_dong = ngat_dong("một hai ba bốn năm sáu bảy tám chín mười " * 5, 18, 200)
    assert len(cac_dong) > 1
    for dong in cac_dong:
        assert do_rong_chu(dong, 18) <= 200


def test_ngat_dong_giu_xuong_dong():
    assert ngat_dong("dòng 1\ndòng 2", 18, 500) == ["dòng 1", "dòng 2"]


def tra_loi_co_het(cau_hoi):
    return True


def test_noi_dung_ket_qua_co_du_muc():
    ket_qua = diagnose_image("anh_gia.jpg", tra_loi_co_het)
    cac_chu = []
    for dong in tao_noi_dung_ket_qua(ket_qua):
        cac_chu.append(dong["chu"])
    assert "Kết luận: chưa đủ chắc chắn" in cac_chu  # CNN giả không được kết luận
    assert "Giải thích" in cac_chu
    assert "Luật đã dùng" in cac_chu
    assert "Nguồn" in cac_chu


def test_hoi_dap_tren_man_hinh():
    man_hinh = ManHinhChanDoan(UngDungGia())
    man_hinh.mo_anh("anh_khong_co.jpg")  # ảnh không mở được vẫn chẩn đoán được
    assert man_hinh.anh is None
    man_hinh.bat_dau()

    cho_luong(man_hinh)
    assert man_hinh.so_cau == 1
    man_hinh.tra_loi_co()

    cho_luong(man_hinh)
    assert man_hinh.so_cau == 2
    man_hinh.bo_qua_het()

    cho_luong(man_hinh)
    assert man_hinh.dang_chay is False
    assert man_hinh.ket_qua is not None
    assert len(man_hinh.top3) == 3
    assert len(man_hinh.dong_ket_qua) > 0


def test_ve_khong_loi():
    be_mat = pygame.Surface((1100, 720))
    man_hinh = ManHinhChanDoan(UngDungGia())
    man_hinh.ve(be_mat)  # chưa chọn ảnh

    man_hinh.mo_anh("anh_khong_co.jpg")
    man_hinh.bat_dau()
    cho_luong(man_hinh)
    man_hinh.ve(be_mat)  # đang hỏi

    man_hinh.bo_qua_het()
    cho_luong(man_hinh)
    man_hinh.ve(be_mat)  # đã có kết quả

    man_hinh.cuon_ket_qua(1000)
    man_hinh.ve(be_mat)  # cuộn xuống cuối
