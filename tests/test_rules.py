"""Kiểm tra schema, từ vựng và suy diễn luật."""
import json
from pathlib import Path

import pytest

from scripts.check_rules import validate_rules
from src.rules.backward import backward
from src.rules.forward import forward

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def vocabulary():
    return {
        "thuoc_tinh": {
            "trieu_chung": {
                "loai": "du_kien_nguoi_dung",
                "gia_tri": ["co", "khong", "chua_biet"],
                "cau_hoi": "Bạn có quan sát dấu hiệu này không?",
                "lua_chon": [
                    {"ma": "co", "nhan": "Có"},
                    {"ma": "khong", "nhan": "Không"},
                    {"ma": "chua_biet", "nhan": "Chưa biết"},
                ],
            },
            "suy_luan": {"loai": "su_kien_suy_ra", "gia_tri": ["nghi_benh"]},
            "khuyen_nghi": {"loai": "su_kien_suy_ra", "gia_tri": ["theo_doi"]},
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
