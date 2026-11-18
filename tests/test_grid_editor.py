"""Kiểm thử E2 - đọc, ghi, kiểm tra bản đồ"""
import json
import os

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import pytest

from src.app.grid_editor import doc_ban_do, ghi_ban_do, kiem_tra, tao_ban_do


def test_ban_do_mac_dinh_hop_le():
    assert kiem_tra(tao_ban_do()) == []


def test_ghi_roi_doc_lai_giong_nhau(tmp_path):
    ban_do = tao_ban_do(5, 6, k=3, p=20)
    ban_do["cells"][2][3] = 2
    ban_do["cells"][1][1] = -1
    duong_dan = tmp_path / "ban_do.json"
    ghi_ban_do(ban_do, duong_dan)
    assert doc_ban_do(duong_dan) == ban_do


def test_doc_ban_do_mau_cua_nhom():
    assert kiem_tra(doc_ban_do("data/sample/maps/map_4x4.json")) == []


@pytest.mark.parametrize("sua", [
    {"start": 5},
    {"start": [0]},
    {"start": [9, 9]},
    {"cells": [5]},
    {"cells": []},
    {"cells": [[0, 0], [0]]},
    {"rows": 3},
    {"k": -3},
    {"p": "60"},
    {"k": None},
])
def test_ban_do_sai_bi_bao_loi(sua):
    ban_do = {**tao_ban_do(2, 2), **sua}
    assert kiem_tra(ban_do)


def test_thieu_tram_va_xuat_phat_tren_vat_can():
    ban_do = tao_ban_do(2, 2)
    ban_do["cells"] = [[-1, 0], [0, 0]]
    loi = kiem_tra(ban_do)
    assert any("trạm" in x for x in loi)
    assert any("xuất phát" in x for x in loi)


def test_ma_o_la_khong_hop_le():
    ban_do = tao_ban_do(2, 2)
    ban_do["cells"][1][1] = 7
    assert kiem_tra(ban_do) == ["Có mã ô không hợp lệ."]


def test_doc_file_khong_phai_json(tmp_path):
    duong_dan = tmp_path / "sai.json"
    duong_dan.write_text("không phải json", encoding="utf-8")
    with pytest.raises(ValueError, match="JSON"):
        doc_ban_do(duong_dan)


def test_khong_ghi_ban_do_sai(tmp_path):
    ban_do = tao_ban_do(2, 2)
    ban_do["cells"][0][0] = 0  # bỏ trạm duy nhất
    duong_dan = tmp_path / "sai.json"
    with pytest.raises(ValueError):
        ghi_ban_do(ban_do, duong_dan)
    assert not duong_dan.exists()


def test_file_ghi_ra_la_json_chuan(tmp_path):
    duong_dan = tmp_path / "ban_do.json"
    ghi_ban_do(tao_ban_do(3, 3), duong_dan)
    du_lieu = json.loads(duong_dan.read_text(encoding="utf-8"))
    assert du_lieu["rows"] == 3 and len(du_lieu["cells"]) == 3


class UngDungGia:
    def ve_man_hinh_chinh(self):
        pass


def test_man_hinh_mo_va_luu_file(tmp_path):
    from src.app.grid_editor import ManHinhBanDo

    man_hinh = ManHinhBanDo(UngDungGia())
    man_hinh.ban_do["cells"][3][4] = 3
    duong_dan = tmp_path / "ruong.json"
    man_hinh.luu_file(duong_dan)
    assert not man_hinh.la_loi and duong_dan.exists()

    man_hinh2 = ManHinhBanDo(UngDungGia())
    man_hinh2.mo_file(duong_dan)
    assert man_hinh2.ban_do["cells"][3][4] == 3


def test_man_hinh_bao_loi_khi_mo_file_sai(tmp_path):
    from src.app.grid_editor import ManHinhBanDo

    duong_dan = tmp_path / "sai.json"
    duong_dan.write_text('{"cells": []}', encoding="utf-8")
    man_hinh = ManHinhBanDo(UngDungGia())
    cu = man_hinh.ban_do
    man_hinh.mo_file(duong_dan)
    assert man_hinh.la_loi and man_hinh.ban_do is cu
    man_hinh.mo_file(None)  # bấm Hủy
    assert man_hinh.ban_do is cu


def test_ban_do_ngau_nhien_hop_le_va_di_duoc_het():
    import random

    from src.app.grid_editor import VAT_CAN, o_toi_duoc, tao_ngau_nhien

    for hat_giong in range(20):
        ban_do = tao_ngau_nhien(rng=random.Random(hat_giong))
        assert kiem_tra(ban_do) == []
        cells = ban_do["cells"]
        di_duoc = sum(o != VAT_CAN for hang in cells for o in hang)
        assert len(o_toi_duoc(cells, ban_do["start"])) == di_duoc
        assert any(o in (1, 2, 3) for hang in cells for o in hang)


def test_chinh_k_p_khong_vuot_gioi_han():
    from src.app.grid_editor import ManHinhBanDo

    man_hinh = ManHinhBanDo(UngDungGia())
    for _ in range(100):
        man_hinh.chinh("k", -1)
    assert man_hinh.ban_do["k"] == 1
    man_hinh.chinh("p", 5)
    assert man_hinh.ban_do["p"] == 65
    man_hinh.xoa_het()
    assert man_hinh.ban_do["k"] == 1 and kiem_tra(man_hinh.ban_do) == []
