"""Kiểm thử nút nhiệt độ theo ví dụ của đề: độ ẩm, nhiệt độ, đạm, đạo ôn, vết hình thoi"""
import pytest

from src.app import thoi_tiet
from src.rules import bayes


def p_dao_on(bang_chung):
    return bayes.truy_van(bang_chung, su_dung_pgmpy=False)["xac_suat"]["dao_on"]


def test_mang_co_du_5_nut_cua_de_va_canh_toi_dao_on():
    for nut in ("ThoiTiet", "NhietDo", "ThuaDam", "DaoOn", "VetHinhThoi"):
        assert nut in bayes.NUT
    assert bayes.NUT["DaoOn"]["cha"] == ["ThoiTiet", "ThuaDam", "Giong", "NhietDo"]
    assert bayes.NUT["VetHinhThoi"]["cha"] == ["DaoOn"]
    bayes.kiem_tra_cpd()


def test_chua_biet_nhiet_do_thi_cpd_dao_on_trung_binh_bang_ban_cu():
    cpd = bayes.NUT["DaoOn"]["cpd"]
    p_co = cpd[("mua_am", "co", "nhiem", "thuan_loi")][0]
    p_khong = cpd[("mua_am", "co", "nhiem", "khong_thuan_loi")][0]
    assert (p_co + p_khong) / 2 == pytest.approx(0.78)
    assert p_co > p_khong


def test_nhiet_do_thuan_loi_lam_tang_dao_on():
    nen = {"tt_am_do_cao": "co", "thua_dam": "co", "vet_la_hinh_thoi": "co"}
    thuan_loi = dict(nen, tt_nhiet_do_thuan_loi="co")
    khong_thuan_loi = dict(nen, tt_nhiet_do_khong_thuan_loi="co")
    assert p_dao_on(thuan_loi) > p_dao_on(nen) > p_dao_on(khong_thuan_loi)


def test_pgmpy_va_liet_ke_cho_cung_ket_qua_khi_co_nhiet_do():
    pytest.importorskip("pgmpy")
    bang_chung = {"tt_nhiet_do_thuan_loi": "co", "vet_la_hinh_thoi": "co"}
    pgmpy = bayes.truy_van(bang_chung)["xac_suat"]
    liet_ke = bayes.truy_van(bang_chung, su_dung_pgmpy=False)["xac_suat"]
    for lop in pgmpy:
        assert pgmpy[lop] == pytest.approx(liet_ke[lop], abs=1e-9)


def test_thoi_tiet_tao_bang_chung_nhiet_do():
    am_mat = {"humidity_percent": 90, "precipitation_mm": 0.0, "temperature_c": 26}
    nong = {"humidity_percent": 70, "precipitation_mm": 0.0, "temperature_c": 35}
    assert thoi_tiet.tao_bang_chung_bayes(am_mat) == ["tt_am_do_cao", "tt_nhiet_do_thuan_loi"]
    assert thoi_tiet.tao_bang_chung_bayes(nong) == ["tt_nhiet_do_khong_thuan_loi"]
    assert bayes.bang_chung_bayes(thoi_tiet.tao_bang_chung_bayes(am_mat))[0] == {
        "ThoiTiet": "mua_am",
        "NhietDo": "thuan_loi",
    }
