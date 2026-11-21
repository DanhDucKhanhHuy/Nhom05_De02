"""Kiểm thử E5 - tư vấn theo triệu chứng (luật + Bayes, không cần CNN)"""
import os

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import pytest

from src.app.tu_van_view import ManHinhTuVan, doc_ten_ket_luan, lay_danh_sach_cau_hoi, suy_dien


class UngDungGia:
    def __init__(self):
        self.ve_lai_menu = False

    def ve_man_hinh_chinh(self):
        self.ve_lai_menu = True

    def chuyen_den(self, man_hinh):
        self.man_hinh = man_hinh


def test_danh_sach_cau_hoi_co_25_cau():
    cau_hoi = lay_danh_sach_cau_hoi()
    assert len(cau_hoi) == 25
    assert cau_hoi[0][0] == "vet_la_hinh_thoi"


def test_chua_tra_loi_thi_xac_suat_cong_lai_bang_1():
    ket_qua = suy_dien({}, [])
    assert sum(ket_qua["xac_suat"].values()) == pytest.approx(1.0)
    assert ket_qua["vet"] == []


def test_vet_hinh_thoi_lam_tang_dao_on_va_kich_hoat_luat():
    truoc = suy_dien({}, [])["xac_suat"]["dao_on"]
    sau = suy_dien({"vet_la_hinh_thoi": "co"}, [])
    assert sau["xac_suat"]["dao_on"] > truoc
    cac_id = [buoc["id"] for buoc in sau["vet"]]
    assert "DO01" in cac_id


def test_thoi_tiet_am_lam_tang_dao_on_them():
    khong_thoi_tiet = suy_dien({"vet_la_hinh_thoi": "co"}, [])["xac_suat"]["dao_on"]
    co_thoi_tiet = suy_dien({"vet_la_hinh_thoi": "co"}, ["tt_am_do_cao"])["xac_suat"]["dao_on"]
    assert co_thoi_tiet > khong_thoi_tiet


def test_doc_ten_ket_luan():
    assert doc_ten_ket_luan("suy_luan=nghi_dao_on") == "Nghi đạo ôn"
    assert "theo dõi ruộng" in doc_ten_ket_luan("khuyen_nghi=theo_doi_ruong_thuong_xuyen")


def test_man_hinh_tra_loi_cau_truoc_lam_lai_quay_lai():
    ung_dung = UngDungGia()
    man_hinh = ManHinhTuVan(ung_dung)
    ban_dau = man_hinh.ket_qua["xac_suat"]["dao_on"]

    man_hinh.tra_loi_co()
    assert man_hinh.vi_tri == 1
    assert man_hinh.ket_qua["xac_suat"]["dao_on"] > ban_dau

    man_hinh.cau_truoc()
    assert man_hinh.vi_tri == 0 and man_hinh.tra_loi == {}

    while not man_hinh.da_hoi_het():
        man_hinh.tra_loi_khong()
    man_hinh.tra_loi_co()  # hết câu thì bấm không có tác dụng
    assert len(man_hinh.tra_loi) == 25

    man_hinh.lam_lai()
    assert man_hinh.vi_tri == 0 and man_hinh.tra_loi == {}

    man_hinh.quay_lai()
    assert ung_dung.ve_lai_menu


def test_chon_dia_diem_di_vong_tron():
    from src.app.tu_van_view import DIA_DIEM

    man_hinh = ManHinhTuVan(UngDungGia())
    assert man_hinh.ten_dia_diem() == "Cần Thơ"
    man_hinh.dia_diem_sau()
    assert man_hinh.ten_dia_diem() == DIA_DIEM[1][0]
    man_hinh.dia_diem_truoc()
    man_hinh.dia_diem_truoc()  # từ đầu lùi thì về cuối danh sách
    assert man_hinh.ten_dia_diem() == DIA_DIEM[-1][0]

    # đang lấy thời tiết thì không đổi địa điểm
    man_hinh.dang_lay_thoi_tiet = True
    man_hinh.dia_diem_sau()
    assert man_hinh.ten_dia_diem() == DIA_DIEM[-1][0]


def test_nhan_ket_qua_thoi_tiet_khong_can_mang():
    man_hinh = ManHinhTuVan(UngDungGia())
    man_hinh.tra_loi_co()
    truoc = man_hinh.ket_qua["xac_suat"]["dao_on"]

    # giả lập luồng thời tiết đã xong
    man_hinh.dang_lay_thoi_tiet = True
    man_hinh.ket_qua_thoi_tiet = ("ok", ["tt_am_do_cao"], "Cần Thơ: 26 °C")
    man_hinh.cap_nhat(0)
    assert not man_hinh.dang_lay_thoi_tiet
    assert man_hinh.ma_thoi_tiet == ["tt_am_do_cao"]
    assert man_hinh.ket_qua["xac_suat"]["dao_on"] > truoc

    man_hinh.dang_lay_thoi_tiet = True
    man_hinh.ket_qua_thoi_tiet = ("loi", [], "Không lấy được thời tiết: mất mạng")
    man_hinh.cap_nhat(0)
    assert "mất mạng" in man_hinh.loi_thoi_tiet
    assert man_hinh.ma_thoi_tiet == ["tt_am_do_cao"]  # giữ kết quả cũ
