import importlib
import math

import pytest

from src.rules import bayes, ket_hop


def test_tv2_attributes_are_accepted_and_order_independent():
    first, notes_first = bayes.bang_chung_bayes({
        "vet_la_hinh_thoi": "co",
        "thua_dam": "co",
        "am_u_va_suong_som": "co",
    })
    second, notes_second = bayes.bang_chung_bayes({
        "am_u_va_suong_som": "co",
        "thua_dam": "co",
        "vet_la_hinh_thoi": "co",
    })
    assert first == second == {
        "TrieuChung": "vet_thoi",
        "ThoiTiet": "mua_am",
        "BonDam": "cao",
    }
    assert notes_first == notes_second == []


def test_unknown_unsupported_and_conflicting_evidence_are_deterministic():
    items = {
        "vet_la_hinh_thoi": "chua_biet",
        "am_u_va_suong_som": "co",
        "tt_kho_han": True,
        "thuoc_tinh_khong_co": "co",
    }
    a = bayes.bang_chung_bayes(items)
    b = bayes.bang_chung_bayes(dict(reversed(list(items.items()))))
    assert a == b
    assert "ThoiTiet" not in a[0]
    assert any("mâu thuẫn" in note for note in a[1])
    assert any("chua_biet" in note for note in a[1])
    assert any("không có trong vocabulary" in note for note in a[1])
    known, known_notes = bayes.bang_chung_bayes({"sa_day": "co"})
    assert known == {}
    assert any("có trong vocabulary" in note for note in known_notes)


def test_negative_symptom_is_not_misread_as_no_symptoms():
    evidence, notes = bayes.bang_chung_bayes({"vet_la_hinh_thoi": "khong"})
    assert evidence == {}
    assert notes


def test_four_class_distribution_and_exact_joint_healthy_probability():
    result = bayes.truy_van(
        {"vet_la_hinh_thoi": "co", "thua_dam": "co"},
        su_dung_pgmpy=False,
    )
    assert sum(result["xac_suat"].values()) == pytest.approx(1.0)
    joint = result["phan_phoi_dong_thoi"]
    exact_healthy = joint["khong|khong|khong"]
    assert result["xac_suat_la_khoe_dong_thoi"] == pytest.approx(exact_healthy)
    assert result["xac_suat_la_khoe_dong_thoi"] != pytest.approx(
        (1 - result["chi_tiet"]["DaoOn"]["co"])
        * (1 - result["chi_tiet"]["BacLa"]["co"])
        * (1 - result["chi_tiet"]["DomNau"]["co"]),
        abs=1e-5,
    )
    assert result["xac_suat_dong_mac"] > 0


def test_cpd_structure_and_joint_distribution_normalize():
    bayes.kiem_tra_cpd()
    for evidence in (
        {},
        {"vet_la_hinh_thoi": "co"},
        {"thua_dam": "khong", "am_u_va_suong_som": "co"},
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
        {"vet_la_hinh_thoi": "co", "thua_dam": "co"},
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
    assert result["trang_thai"] in {"da_ket_luan", "chua_du_chac"}



def test_zero_bayes_normalization_is_rejected(monkeypatch):
    monkeypatch.setattr(
        ket_hop,
        "truy_van",
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
    with pytest.raises(ValueError, match="tích CNN–Bayes"):
        ket_hop.ket_hop_cnn_bayes(
            [("dao_on", 0.5), ("bac_la", 0.3), ("dom_nau", 0.2)]
        )


def test_predict_top3_stub_runs_without_tensorflow():
    module = importlib.import_module("src.model.predict")
    assert module.IS_STUB is True
    assert len(module.predict_top3("unused.jpg")) == 3



def test_cpd_rejects_invalid_probability_values(monkeypatch):
    original = bayes.NUT["ThoiTiet"]["cpd"]
    monkeypatch.setitem(bayes.NUT["ThoiTiet"], "cpd", {(): [float("nan"), 1.0]})
    with pytest.raises(ValueError, match="ngoài"):
        bayes.kiem_tra_cpd()
    monkeypatch.setitem(bayes.NUT["ThoiTiet"], "cpd", original)


def test_cpd_provenance_uses_current_source_catalog():
    import json
    from pathlib import Path

    catalog = json.loads(
        (Path(bayes.__file__).with_name("sources.json")).read_text(encoding="utf-8")
    )
    source_ids = {source["ma"] for source in catalog["nguon"]}
    assert set(bayes.NGUON_CPD) == set(bayes.NUT)
    assert all(set(refs) <= source_ids for refs in bayes.NGUON_CPD.values())

def test_pgmpy_025_and_three_joint_queries_match_independent_enumeration():
    pgmpy = pytest.importorskip("pgmpy")
    assert pgmpy.__version__ == "0.1.25"
    network = bayes.xay_dung_mang_pgmpy()
    assert network.check_model()
    for cpd in network.get_cpds():
        values = cpd.get_values()
        expected_columns = (
            math.prod(cpd.cardinality[1:]) if len(cpd.cardinality) > 1 else 1
        )
        assert values.shape[1] == expected_columns
        for column in range(values.shape[1]):
            assert float(values[:, column].sum()) == pytest.approx(1.0)

    queries = [
        {"TrieuChung": "vet_thoi"},
        {"BonDam": "cao", "ThoiTiet": "kho"},
        {"TrieuChung": "dom_tron", "ThoiTiet": "mua_am"},
    ]
    for evidence in queries:
        pg_result = bayes._truy_van_joint_pgmpy(evidence)
        enum_result = bayes._truy_van_joint_liet_ke(evidence)
        assert pg_result == pytest.approx(enum_result, abs=1e-8)
