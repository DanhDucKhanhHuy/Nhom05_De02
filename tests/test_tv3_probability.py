import importlib
import json
import math
from pathlib import Path

import pytest

from src.app import thoi_tiet
from src.rules import bayes, ket_hop


def test_multiple_symptoms_are_separate_and_order_independent():
    evidence = {
        "vet_bac_ung_nuoc_tren_phien_la": "co",
        "vet_bac_bat_dau_o_chop_la": "co",
        "vet_bac_mep_luon_song": "co",
        "vet_la_hinh_thoi": "co",
        "dom_tron_hoac_bau_duc_nau": "co",
        "dom_nau_vien_sam": "co",
    }
    first = bayes.bang_chung_bayes(evidence)
    second = bayes.bang_chung_bayes(dict(reversed(list(evidence.items()))))
    assert first == second
    assert first[0] == {
        "BacBatDauChop": "co",
        "BacMepLuonSong": "co",
        "BacVetUngNuoc": "co",
        "DomTronBauDuc": "co",
        "DomVienSam": "co",
        "VetHinhThoi": "co",
    }
    assert first[1] == []


def test_symptom_nodes_are_not_collapsed_into_trieuchung():
    assert "TrieuChung" not in bayes.NUT
    assert bayes.NUT["VetTamXamKho"]["cha"] == ["VetHinhThoi"]
    assert bayes.NUT["BacBatDauChop"]["cha"] == ["BacVetUngNuoc"]
    assert bayes.NUT["BacMepLuonSong"]["cha"] == ["BacVetUngNuoc"]
    assert bayes.NUT["DomVienSam"]["cha"] == ["DomTronBauDuc"]
    assert bayes.NUT["DomTamNhatXam"]["cha"] == ["DomTronBauDuc"]


def test_supported_attribute_catalog_is_explicit_and_complete():
    vocabulary = json.loads(
        Path(bayes.__file__).with_name("vocabulary.json").read_text(encoding="utf-8")
    )["thuoc_tinh"]
    assert set(bayes.ANH_XA_THUOC_TINH) == {
        key for key, item in vocabulary.items()
        if item.get("loai") == "du_kien_nguoi_dung"
    }
    supported = {
        key for key, states in bayes.ANH_XA_THUOC_TINH.items()
        if states["co"] is not None
    }
    assert supported == {
        "vet_la_hinh_thoi", "vet_la_tam_xam_kho",
        "am_u_va_suong_som", "thua_dam",
        "vet_bac_ung_nuoc_tren_phien_la", "vet_bac_bat_dau_o_chop_la",
        "vet_la_vang_den_trang", "vet_bac_mep_luon_song",
        "la_heo_hoac_cuon_lai", "dom_tron_hoac_bau_duc_nau",
        "dom_nau_vien_sam", "dom_nau_tam_nhat_xam",
        "dom_nau_tren_be_la", "dom_nau_tren_diep_tieu",
        "dom_nau_tren_vo_trau", "hat_nhe_hoac_bac_phan",
    }
    for key in supported:
        assert bayes.ANH_XA_THUOC_TINH[key]["co"][0] in bayes.NUT
        assert bayes.ANH_XA_THUOC_TINH[key]["khong"][0] in bayes.NUT
        assert bayes.ANH_XA_THUOC_TINH[key]["co"][0] == bayes.ANH_XA_THUOC_TINH[key]["khong"][0]


def test_negative_false_and_unknown_are_not_positive_evidence():
    assert bayes.bang_chung_bayes({"vet_la_hinh_thoi": False})[0] == {
        "VetHinhThoi": "khong"
    }
    assert bayes.bang_chung_bayes({"vet_la_hinh_thoi": "False"})[0] == {
        "VetHinhThoi": "khong"
    }
    for value in ("chua_biet", None):
        evidence, notes = bayes.bang_chung_bayes({"vet_la_hinh_thoi": value})
        assert evidence == {}
        assert notes
    assert bayes.bang_chung_bayes({"vet_la_hinh_thoi": True})[0] == {
        "VetHinhThoi": "co"
    }


def test_close_meaning_mappings_are_removed():
    evidence, notes = bayes.bang_chung_bayes({
        "vet_la_tam_xam_kho": "co",
        "thua_dam": "co",
        "am_u_va_suong_som": "co",
    })
    assert evidence == {
        "AmU_SuongSom": "co",
        "ThuaDam": "co",
        "VetTamXamKho": "co",
    }
    assert "VetHinhThoi" not in evidence
    assert "ThoiTiet" not in evidence
    assert "BonDam" not in evidence
    assert notes == []


def test_unsupported_attributes_are_reported_and_ignored():
    evidence, notes = bayes.bang_chung_bayes({
        "vet_la_vien_nau": "co",
        "ruong_thieu_nuoc": "khong",
        "sa_day": "co",
    })
    assert evidence == {}
    assert len(notes) == 3
    assert all("Bayes chưa hỗ trợ" in note for note in notes)


def test_only_equivalent_legacy_codes_are_converted():
    evidence, notes = bayes.bang_chung_bayes([
        "TrieuChung=dom_tron",
        "TrieuChung=vet_thoi",
        "TrieuChung=chop_la_kho",
        "tt_am_do_cao",
    ])
    assert evidence == {
        "DomTronBauDuc": "co",
        "ThoiTiet": "mua_am",
    }
    assert len(notes) == 2
    assert any("vet_thoi" in note for note in notes)
    assert any("chop_la_kho" in note for note in notes)


def test_old_bondam_high_low_codes_are_not_guessed():
    evidence, notes = bayes.bang_chung_bayes({"BonDam": "cao"})
    assert evidence == {}
    assert any("không tương đương" in note for note in notes)


def test_weather_and_field_observations_are_separate():
    evidence, _ = bayes.bang_chung_bayes({
        "am_u_va_suong_som": "co",
        "thua_dam": "khong",
    })
    assert evidence == {"AmU_SuongSom": "co", "ThuaDam": "khong"}
    assert "ThoiTiet" not in evidence
    assert "DaoOn" not in evidence
    assert "BacLa" not in evidence


def test_weather_measurements_use_only_documented_weather_rules():
    wet = {"humidity_percent": 82, "precipitation_mm": 0.0, "wind_speed_kmh": 12, "weather_code": 0}
    rainy = {"humidity_percent": 65, "precipitation_mm": 2.0, "wind_speed_kmh": 12, "weather_code": 61}
    dry = {"humidity_percent": 55, "precipitation_mm": 0.0, "wind_speed_kmh": 5, "weather_code": 0}
    middle = {"humidity_percent": 70, "precipitation_mm": 0.2, "wind_speed_kmh": 5, "weather_code": 0}
    assert thoi_tiet.tao_bang_chung_bayes(wet) == ["tt_am_do_cao"]
    assert thoi_tiet.tao_bang_chung_bayes(rainy) == ["tt_mua_nhieu"]
    assert thoi_tiet.tao_bang_chung_bayes(dry) == ["tt_kho_han"]
    assert thoi_tiet.tao_bang_chung_bayes(middle) == []
    assert bayes.bang_chung_bayes(thoi_tiet.tao_bang_chung_bayes(wet))[0] == {
        "ThoiTiet": "mua_am"
    }


def test_conflicting_evidence_is_order_independent():
    values = {
        "vet_la_hinh_thoi": "co",
        "vet_la_tam_xam_kho": "co",
        "tt_kho_han": True,
        "tt_am_do_cao": True,
    }
    first = bayes.bang_chung_bayes(values)
    second = bayes.bang_chung_bayes(dict(reversed(list(values.items()))))
    assert first == second
    assert "ThoiTiet" not in first[0]
    assert "VetHinhThoi" in first[0]
    assert any("mâu thuẫn" in note for note in first[1])


def test_four_class_distribution_and_exact_joint_healthy_probability():
    result = bayes.truy_van({
        "vet_la_hinh_thoi": "co",
        "vet_bac_ung_nuoc_tren_phien_la": "co",
        "dom_tron_hoac_bau_duc_nau": "co",
        "thua_dam": "co",
    }, su_dung_pgmpy=False)
    assert sum(result["xac_suat"].values()) == pytest.approx(1.0)
    joint = result["phan_phoi_dong_thoi"]
    exact_healthy = joint["khong|khong|khong"]
    assert result["xac_suat_la_khoe_dong_thoi"] == pytest.approx(exact_healthy)
    assert result["xac_suat_dong_mac"] > 0
    assert len(result["bang_chung"]) == 4


def test_cpd_structure_and_joint_distribution_normalize():
    bayes.kiem_tra_cpd()
    for evidence in (
        {},
        {"VetHinhThoi": "co"},
        {"BacVetUngNuoc": "co", "BacMepLuonSong": "khong"},
        {"DomTronBauDuc": "co", "DomVienSam": "khong"},
    ):
        result = bayes.truy_van(evidence, su_dung_pgmpy=False)
        assert sum(result["phan_phoi_dong_thoi"].values()) == pytest.approx(1.0)


@pytest.mark.parametrize(
    "top3",
    [
        [],
        [("dao_on", 0.8), ("bac_la", 0.1)],
        [("dao_on", 0.5), ("dao_on", 0.2), ("bac_la", 0.1)],
        [("dao_on", 0.5), ("bac_la", 0.2), ("unknown", 0.1)],
        [("dao_on", float("nan")), ("bac_la", 0.2), ("dom_nau", 0.1)],
        [("dao_on", float("inf")), ("bac_la", 0.2), ("dom_nau", 0.1)],
        [("dao_on", -0.1), ("bac_la", 0.2), ("dom_nau", 0.1)],
        [("dao_on", 1.1), ("bac_la", 0.0), ("dom_nau", 0.0)],
        [("dao_on", 0.7), ("bac_la", 0.4), ("dom_nau", 0.1)],
        [("dao_on", True), ("bac_la", 0.2), ("dom_nau", 0.1)],
        [("dao_on", 0.0), ("bac_la", 0.0), ("dom_nau", 0.0)],
    ],
)
def test_invalid_top3_is_rejected(top3):
    with pytest.raises(ValueError):
        ket_hop.chuan_hoa_cnn_top3(top3)


def test_top3_valid_missing_class_is_inferred():
    result = ket_hop.chuan_hoa_cnn_top3([
        ("dao_on", 0.55), ("dom_nau", 0.40), ("bac_la", 0.03)
    ])
    assert result["la_khoe"] == pytest.approx(0.02)
    assert sum(result.values()) == pytest.approx(1.0)


def test_combination_uses_product_and_normalizes():
    result = ket_hop.ket_hop_cnn_bayes(
        [("dao_on", 0.55), ("dom_nau", 0.40), ("bac_la", 0.03)],
        {
            "vet_bac_ung_nuoc_tren_phien_la": "co",
            "vet_bac_bat_dau_o_chop_la": "co",
            "vet_bac_mep_luon_song": "co",
        },
        su_dung_pgmpy=False,
    )
    expected = {
        label: result["xac_suat_cnn"][label] * result["xac_suat_bayes"][label]
        for label in ket_hop.MA_BENH
    }
    total = sum(expected.values())
    expected = {label: value / total for label, value in expected.items()}
    assert result["xac_suat_ket_hop"] == pytest.approx(expected)
    assert sum(result["xac_suat_ket_hop"].values()) == pytest.approx(1.0)


def test_zero_bayes_normalization_is_rejected(monkeypatch):
    monkeypatch.setattr(
        ket_hop, "truy_van",
        lambda *_args, **_kwargs: {"xac_suat": {label: 0.0 for label in ket_hop.MA_BENH}},
    )
    with pytest.raises(ValueError, match="tổng xác suất bằng 0"):
        ket_hop.chuan_hoa_bayes(su_dung_pgmpy=False)


def test_prior_correction_changes_result_and_is_validated():
    cnn = [("dao_on", 0.55), ("dom_nau", 0.40), ("bac_la", 0.03)]
    plain = ket_hop.ket_hop_cnn_bayes(cnn, su_dung_pgmpy=False)
    corrected = ket_hop.ket_hop_cnn_bayes(
        cnn,
        prior_cnn={"dao_on": 0.7, "bac_la": 0.1, "dom_nau": 0.1, "la_khoe": 0.1},
        su_dung_pgmpy=False,
    )
    assert corrected["xac_suat_ket_hop"] != plain["xac_suat_ket_hop"]
    with pytest.raises(ValueError):
        ket_hop.ket_hop_cnn_bayes(cnn, prior_cnn={"dao_on": 1.0}, su_dung_pgmpy=False)


def test_threshold_below_equal_above(monkeypatch):
    target = 0.60
    p = math.sqrt(target) / (math.sqrt(target) + math.sqrt(1 - target))
    distribution = {"dao_on": p, "bac_la": 1 - p, "dom_nau": 0.0, "la_khoe": 0.0}
    monkeypatch.setattr(ket_hop, "chuan_hoa_cnn_top3", lambda _: distribution.copy())
    monkeypatch.setattr(
        ket_hop, "chuan_hoa_bayes",
        lambda *_args, **_kwargs: (distribution.copy(), {
            "phuong_phap": "test", "bang_chung": {}, "ghi_chu": [],
            "xac_suat_dong_mac": 0.0,
        }),
    )
    args = [("dao_on", 0.5), ("bac_la", 0.3), ("dom_nau", 0.2)]
    at = ket_hop.ket_hop_cnn_bayes(args, nguong=target)
    below = ket_hop.ket_hop_cnn_bayes(args, nguong=target + 1e-8)
    above = ket_hop.ket_hop_cnn_bayes(args, nguong=target - 1e-8)
    assert at["xac_suat_ket_hop"]["dao_on"] == pytest.approx(target)
    assert at["ket_luan"] == "dao_on"
    assert below["ket_luan"] is None
    assert below["trang_thai"] == "chua_du_chac"
    assert above["ket_luan"] == "dao_on"


def test_tie_returns_uncertain(monkeypatch):
    uniform = {label: 0.25 for label in ket_hop.MA_BENH}
    monkeypatch.setattr(ket_hop, "chuan_hoa_cnn_top3", lambda _: uniform.copy())
    monkeypatch.setattr(
        ket_hop, "chuan_hoa_bayes",
        lambda *_args, **_kwargs: (uniform.copy(), {
            "phuong_phap": "test", "bang_chung": {}, "ghi_chu": [],
            "xac_suat_dong_mac": 0.0,
        }),
    )
    result = ket_hop.ket_hop_cnn_bayes(
        [("dao_on", 0.25), ("bac_la", 0.25), ("dom_nau", 0.25)],
        nguong=0.2,
    )
    assert result["hoa"] is True
    assert result["ket_luan"] is None


def test_zero_cnn_bayes_product_raises(monkeypatch):
    monkeypatch.setattr(
        ket_hop, "chuan_hoa_cnn_top3",
        lambda _: {"dao_on": 1.0, "bac_la": 0.0, "dom_nau": 0.0, "la_khoe": 0.0},
    )
    monkeypatch.setattr(
        ket_hop, "chuan_hoa_bayes",
        lambda *_args, **_kwargs: (
            {"dao_on": 0.0, "bac_la": 1.0, "dom_nau": 0.0, "la_khoe": 0.0},
            {"phuong_phap": "test", "bang_chung": {}, "ghi_chu": [], "xac_suat_dong_mac": 0.0},
        ),
    )
    with pytest.raises(ValueError, match="Tổng tích CNN–Bayes"):
        ket_hop.ket_hop_cnn_bayes(
            [("dao_on", 0.5), ("bac_la", 0.3), ("dom_nau", 0.2)]
        )


def test_predictor_requires_real_image_and_never_returns_fixed_probabilities():
    module = importlib.import_module("src.model.predict")
    assert module.IS_STUB is True
    with pytest.raises(FileNotFoundError, match="Không tìm thấy ảnh"):
        module.predict_top3("unused.jpg")


def test_cpd_rejects_invalid_probability_values(monkeypatch):
    original = bayes.NUT["ThoiTiet"]["cpd"]
    monkeypatch.setitem(bayes.NUT["ThoiTiet"], "cpd", {(): [float("nan"), 1.0]})
    with pytest.raises(ValueError, match="ngoài"):
        bayes.kiem_tra_cpd()
    monkeypatch.setitem(bayes.NUT["ThoiTiet"], "cpd", original)


def test_cpd_provenance_and_assumptions_cover_every_node():
    catalog = json.loads(
        Path(bayes.__file__).with_name("sources.json").read_text(encoding="utf-8")
    )
    source_ids = {source["ma"] for source in catalog["nguon"]}
    assert set(bayes.NGUON_CPD) == set(bayes.NUT)
    assert set(bayes.GIA_DINH_CPD) == set(bayes.NUT)
    assert all(set(refs) <= source_ids for refs in bayes.NGUON_CPD.values())
    assert all(bayes.NUT[node]["gia_dinh"] for node in bayes.NUT)


def test_pgmpy_025_and_three_opposing_query_pairs_match_independent_enumeration():
    pgmpy = pytest.importorskip("pgmpy")
    assert pgmpy.__version__ == "0.1.25"
    network = bayes.xay_dung_mang_pgmpy()
    assert network.check_model()
    for cpd in network.get_cpds():
        values = cpd.get_values()
        expected_columns = math.prod(cpd.cardinality[1:]) if len(cpd.cardinality) > 1 else 1
        assert values.shape[1] == expected_columns
        for column in range(values.shape[1]):
            assert float(values[:, column].sum()) == pytest.approx(1.0)

    opposing_pairs = [
        ({"VetHinhThoi": "co"}, {"VetHinhThoi": "khong"}),
        (
            {"BacVetUngNuoc": "co", "BacMepLuonSong": "khong"},
            {"BacVetUngNuoc": "khong", "BacMepLuonSong": "co"},
        ),
        (
            {"DomTronBauDuc": "co", "DomVienSam": "co"},
            {"DomTronBauDuc": "co", "DomVienSam": "khong"},
        ),
    ]
    for pair in opposing_pairs:
        for evidence in pair:
            pg_result = bayes._truy_van_joint_pgmpy(evidence)
            enum_result = bayes._truy_van_joint_liet_ke(evidence)
            assert pg_result == pytest.approx(enum_result, abs=1e-8)
