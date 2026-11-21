"""Kiểm thử E6 - màn hình mạng Bayes 5 nút"""
import os

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import pytest

from src.app.bayes_view import CAC_NUT_NHAP, ManHinhBayes, tinh_xac_suat


class UngDungGia:
    def __init__(self):
        self.ve_lai_menu = False

    def ve_man_hinh_chinh(self):
        self.ve_lai_menu = True


def test_co_4_nut_nhap_va_nut_dao_on():
    cac_ma = [ma for ma, _, _, _ in CAC_NUT_NHAP]
    assert cac_ma == ["do_am", "nhiet_do", "dam", "vet"]


def test_chua_biet_gi_thi_vet_du_doan_tu_cpd():
    p_dao_on, p_vet, _ = tinh_xac_suat({"do_am": None, "nhiet_do": None, "dam": None, "vet": None})
    assert 0 < p_dao_on < 1
    assert p_vet == pytest.approx(0.84 * p_dao_on + 0.06 * (1 - p_dao_on))


def test_bang_chung_lam_tang_dao_on():
    man_hinh = ManHinhBayes(UngDungGia())
    ban_dau = man_hinh.p_dao_on

    man_hinh.chon("do_am", ("ThoiTiet", "mua_am"))
    man_hinh.chon("nhiet_do", ("NhietDo", "thuan_loi"))
    man_hinh.chon("dam", ("thua_dam", "co"))
    nguy_co_cao = man_hinh.p_dao_on
    assert nguy_co_cao > ban_dau

    man_hinh.chon("vet", ("vet_la_hinh_thoi", "co"))
    assert man_hinh.p_dao_on > nguy_co_cao
    assert man_hinh.p_vet == 1.0

    man_hinh.chon("nhiet_do", ("NhietDo", "khong_thuan_loi"))
    assert man_hinh.p_dao_on < 1.0

    man_hinh.dat_lai()
    assert man_hinh.p_dao_on == pytest.approx(ban_dau)
    man_hinh.quay_lai()
    assert man_hinh.ung_dung.ve_lai_menu
