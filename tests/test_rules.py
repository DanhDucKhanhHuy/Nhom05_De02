"""Kiểm tra schema, từ vựng và suy diễn luật."""
import json
from pathlib import Path

import pytest

from scripts.check_rules import validate_rules
from src.rules.backward import backward
from src.rules.bayes import bang_chung_bayes
from src.rules.forward import forward

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def vocabulary():
    return {
        "thuoc_tinh": {
            "trieu_chung": {
                "loai": "du_kien_nguoi_dung",
                "mo_ta": "Có dấu hiệu triệu chứng",
                "gia_tri": ["co", "khong", "chua_biet"],
                "cau_hoi": "Bạn có quan sát dấu hiệu này không?",
                "lua_chon": [
                    {"ma": "co", "nhan": "Có"},
                    {"ma": "khong", "nhan": "Không"},
                    {"ma": "chua_biet", "nhan": "Chưa biết"},
                ],
            },
            "suy_luan": {"loai": "su_kien_suy_ra", "mo_ta": "Gợi ý bệnh", "gia_tri": ["nghi_benh"]},
            "khuyen_nghi": {"loai": "su_kien_suy_ra", "mo_ta": "Biện pháp", "gia_tri": ["theo_doi"]},
        }
    }


@pytest.fixture
def sources():
    return {"nguon": [
        {"ma": f"S{index}", "ten": "Nguồn kiểm thử", "co_quan": "Đơn vị thử nghiệm",
         "url": "https://example.invalid", "nam": 2024}
        for index in range(4)
    ]}


@pytest.fixture
def symbolic_rules():
    return [
        {"id": "T1", "loai": "chan_doan", "neu": ["trieu_chung=co"], "thi": "suy_luan=nghi_benh",
         "nguon": {"ma": "S0", "muc": "Mục kiểm thử"}},
        {"id": "T2", "loai": "khuyen_nghi", "neu": ["suy_luan=nghi_benh"], "thi": "khuyen_nghi=theo_doi",
         "nguon": {"ma": "S0", "muc": "Mục kiểm thử"}},
    ]


def test_forward_builds_two_step_chain(symbolic_rules):
    assert forward({"trieu_chung=co"}, symbolic_rules) == {
        "trieu_chung=co", "suy_luan=nghi_benh", "khuyen_nghi=theo_doi"
    }


def test_real_rule_set_builds_symptom_suspicion_recommendation_chain():
    rules = json.loads((ROOT / "src/rules/rules.json").read_text(encoding="utf-8"))["rules"]
    facts = forward({"vet_la_hinh_thoi=co"}, rules)
    assert "suy_luan=nghi_dao_on" in facts
    assert "khuyen_nghi=theo_doi_ruong_thuong_xuyen" in facts


def test_backward_proof_and_unknown(symbolic_rules):
    assert backward("khuyen_nghi=theo_doi", {"trieu_chung=co"}, symbolic_rules, lambda _: None) is True
    assert backward("khuyen_nghi=theo_doi", {"trieu_chung=khong"}, symbolic_rules, lambda _: None) is False


def test_backward_asks_question_from_vocabulary():
    rules = json.loads((ROOT / "src/rules/rules.json").read_text(encoding="utf-8"))["rules"]
    questions = []
    assert backward(
        "khuyen_nghi=theo_doi_ruong_thuong_xuyen", set(), rules,
        lambda question: questions.append(question) or True,
    ) is True
    assert questions == ["Bạn có thấy vết trên lá lúa hình thoi không?"]


def test_backward_respects_known_answer_and_caches_question():
    rules = json.loads((ROOT / "src/rules/rules.json").read_text(encoding="utf-8"))["rules"]
    questions = []
    assert backward(
        "khuyen_nghi=theo_doi_ruong_thuong_xuyen", {"vet_la_hinh_thoi=khong"}, rules,
        lambda question: questions.append(question) or False,
    ) is False
    assert "Bạn có thấy vết trên lá lúa hình thoi không?" not in questions
    assert len(questions) == len(set(questions))


def test_repository_rules_use_current_contract():
    document = json.loads((ROOT / "src/rules/rules.json").read_text(encoding="utf-8"))
    vocabulary = json.loads((ROOT / "src/rules/vocabulary.json").read_text(encoding="utf-8"))
    sources = json.loads((ROOT / "src/rules/sources.json").read_text(encoding="utf-8"))
    assert validate_rules(document, vocabulary, sources) == []
    assert len(document["rules"]) >= 20


def test_each_disease_has_diagnosis_and_recommendation_rules():
    document = json.loads((ROOT / "src/rules/rules.json").read_text(encoding="utf-8"))
    for disease in ("dao_on", "bac_la", "dom_nau"):
        assert any(rule["loai"] == "chan_doan" and rule["thi"] == f"suy_luan=nghi_{disease}"
                   for rule in document["rules"])
        assert any(rule["loai"] == "khuyen_nghi" and f"nghi_{disease}" in rule["neu"][0]
                   for rule in document["rules"])


def test_bacterial_rules_only_ask_about_observable_features():
    document = json.loads((ROOT / "src/rules/rules.json").read_text(encoding="utf-8"))
    vocabulary = json.loads((ROOT / "src/rules/vocabulary.json").read_text(encoding="utf-8"))["thuoc_tinh"]
    by_id = {rule["id"]: rule for rule in document["rules"]}
    assert by_id["BL02"]["neu"] == ["vet_bac_bat_dau_o_chop_la=co"]
    assert by_id["BL03"]["neu"] == ["vet_hoai_tu_vang_trang_o_mep_la=co"]
    assert "chuyển dần" not in vocabulary["vet_hoai_tu_vang_trang_o_mep_la"]["cau_hoi"]
    assert "kéo dài ra" not in vocabulary["vet_bac_bat_dau_o_chop_la"]["cau_hoi"]


def test_brown_spot_recommendations_keep_their_season_scope():
    document = json.loads((ROOT / "src/rules/rules.json").read_text(encoding="utf-8"))
    recommendations = {rule["id"]: rule["thi"] for rule in document["rules"]
                       if rule["loai"] == "khuyen_nghi"}
    assert recommendations["DN09"] == "khuyen_nghi=quan_ly_co_dai_trong_vu"
    assert recommendations["DN10"] == "khuyen_nghi=luan_canh_vu_tiep_theo_neu_bi_nhiem"
    dn10 = next(rule for rule in document["rules"] if rule["id"] == "DN10")
    assert dn10["neu"] == ["ruong_xac_nhan_nhiem_dom_nau=co"]


def test_next_season_rotation_requires_confirmed_brown_spot():
    rules = json.loads((ROOT / "src/rules/rules.json").read_text(encoding="utf-8"))["rules"]
    suspected = forward({"suy_luan=nghi_dom_nau"}, rules)
    assert "khuyen_nghi=luan_canh_vu_tiep_theo_neu_bi_nhiem" not in suspected
    confirmed = forward({"ruong_xac_nhan_nhiem_dom_nau=co"}, rules)
    assert "khuyen_nghi=luan_canh_vu_tiep_theo_neu_bi_nhiem" in confirmed

    asked = []
    assert backward(
        "khuyen_nghi=luan_canh_vu_tiep_theo_neu_bi_nhiem",
        set(),
        rules,
        lambda question: asked.append(question) or True,
    )
    assert asked == ["Ruộng đã được xác định là nhiễm bệnh đốm nâu chưa?"]


def test_brown_spot_grain_attribute_matches_source_concept():
    vocabulary = json.loads((ROOT / "src/rules/vocabulary.json").read_text(encoding="utf-8"))
    attributes = vocabulary["thuoc_tinh"]
    assert "hat_lep_nhe_hoac_phoi_bot" not in attributes
    grain_sign = attributes["hat_nhe_hoac_bac_phan"]
    assert grain_sign["mo_ta"] == "Hạt nhẹ hoặc hạt có biểu hiện bạc phấn"
    assert grain_sign["phep_ghep"] == "OR"


def test_compound_symptoms_keep_source_meaning_in_question_and_description():
    vocabulary = json.loads((ROOT / "src/rules/vocabulary.json").read_text(encoding="utf-8"))
    attributes = vocabulary["thuoc_tinh"]
    panicle = attributes["bong_lek_trang_khi_benh_xuat_hien_som"]
    assert "bong_lek_trang_som" not in attributes
    assert "bệnh đạo ôn xuất hiện sớm" in panicle["mo_ta"]
    assert "Nếu bệnh đạo ôn xuất hiện sớm" in panicle["cau_hoi"]
    center = attributes["dom_nau_tam_nhat_xam"]
    assert "nâu đỏ nhạt hoặc xám" in center["mo_ta"]
    assert "nâu đỏ nhạt hoặc xám" in center["cau_hoi"]


def test_vocabulary_questions_match_attribute_meaning_and_explain_join_logic():
    vocabulary = json.loads((ROOT / "src/rules/vocabulary.json").read_text(encoding="utf-8"))
    attributes = vocabulary["thuoc_tinh"]
    waterlogged = attributes["vet_bac_ung_nuoc_tren_phien_la"]
    assert "vet_bac_dau_la_uot_nuoc" not in attributes
    assert waterlogged["mo_ta"] == "Vệt bạc lá dạng úng nước đến vàng trên phiến lá"
    assert waterlogged["cau_hoi"] == "Bạn có thấy vệt bạc lá dạng úng nước đến vàng trên phiến lá không?"

    for name, definition in attributes.items():
        question = definition.get("cau_hoi", "").lower()
        has_and = " và " in question
        has_or = " hoặc " in question
        if has_and or has_or:
            assert definition.get("phep_ghep") == (
                "AND_OR" if has_and and has_or else "AND" if has_and else "OR"
            ), name
            assert definition.get("dien_giai_ghep"), name


def test_compound_negatives_do_not_become_opposite_bayes_states():
    result, notes = bang_chung_bayes([
        "am_u_va_suong_som=khong",
        "thua_dam=khong",
        "am_u_va_suong_som=chua_biet",
        "thua_dam=chua_biet",
    ])
    assert result == {}
    assert any("khô" in note for note in notes)
    assert any("thấp" in note for note in notes)


def test_current_vocabulary_maps_only_supported_positive_bayes_evidence():
    result, notes = bang_chung_bayes([
        "am_u_va_suong_som=co",
        "thua_dam=co",
        "ruong_thieu_nuoc=co",
    ])
    assert result == {"ThoiTiet": "mua_am", "BonDam": "cao"}
    assert any("ruong_thieu_nuoc=co" in note for note in notes)


def test_unknown_facts_do_not_trigger_forward_rules():
    rules = json.loads((ROOT / "src/rules/rules.json").read_text(encoding="utf-8"))["rules"]
    facts = forward({"am_u_va_suong_som=chua_biet", "thua_dam=khong"}, rules)
    assert "yeu_to_nguy_co=dao_on" not in facts
    assert "ThoiTiet=kho" not in facts
    assert "BonDam=thap" not in facts


def test_validator_checks_values_sources_count_and_cycles(vocabulary, sources, symbolic_rules):
    assert validate_rules(
        {"rules": symbolic_rules}, vocabulary, sources, min_rules=2, require_coverage=False
    ) == []
    rules_with_cycle = [*symbolic_rules, {
        "id": "T3", "loai": "trung_gian", "neu": ["khuyen_nghi=theo_doi"],
        "thi": "suy_luan=nghi_benh", "nguon": {"ma": "S0", "muc": "Mục kiểm thử"},
    }]
    errors = validate_rules({"rules": rules_with_cycle}, vocabulary, sources, min_rules=1)
    assert any("chu trình" in error for error in errors)


def test_validator_requires_at_least_four_sources(vocabulary, sources, symbolic_rules):
    errors = validate_rules(
        {"rules": symbolic_rules}, vocabulary, {"nguon": sources["nguon"][:3]},
        min_rules=2, require_coverage=False,
    )
    assert any("ít nhất 4 nguồn" in error for error in errors)


def test_validator_requires_question_choices_and_known_source(vocabulary, sources, symbolic_rules):
    vocabulary["thuoc_tinh"]["trieu_chung"].pop("cau_hoi")
    rule = {**symbolic_rules[0], "nguon": {"ma": "S404", "muc": "Mục không tồn tại"}}
    errors = validate_rules({"rules": [rule]}, vocabulary, sources, min_rules=1)
    assert any("câu hỏi" in error for error in errors)
    assert any("mã nguồn" in error for error in errors)


def test_validator_requires_explicit_logic_for_compound_questions(vocabulary, sources, symbolic_rules):
    vocabulary["thuoc_tinh"]["trieu_chung"]["cau_hoi"] = "Có dấu hiệu A và dấu hiệu B không?"
    errors = validate_rules(
        {"rules": symbolic_rules}, vocabulary, sources, min_rules=2, require_coverage=False
    )
    assert any("phép ghép" in error for error in errors)


def test_validator_requires_a_description_for_every_vocabulary_attribute(
    vocabulary, sources, symbolic_rules
):
    vocabulary["thuoc_tinh"]["trieu_chung"].pop("mo_ta")
    errors = validate_rules(
        {"rules": symbolic_rules}, vocabulary, sources, min_rules=2, require_coverage=False
    )
    assert any("thiếu mô tả" in error for error in errors)


@pytest.mark.parametrize("change", [
    {"nguon": {"ma": "", "muc": "Mục"}}, {"loai": "sai"}, {"neu": []}, {"thi": "không_hợp_lệ=x"},
    {"nguon": {"ma": "S0", "muc": "5 ml/l"}},
    {"nguon": {"ma": "S0", "muc": "2 g mỗi lít"}},
    {"nguon": {"ma": "S0", "muc": "tên thuốc bị cấm"}},
])
def test_validator_rejects_bad_or_prohibited_rules(change, vocabulary, sources, symbolic_rules):
    rule = {**symbolic_rules[0], **change}
    errors = validate_rules({"rules": [rule]}, vocabulary, sources, min_rules=1)
    assert errors
