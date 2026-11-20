"""Kiểm tra luồng tích hợp bằng CNN giả và bộ luật thật, không cần TensorFlow."""
import copy
import json
import math
from collections import Counter

import pytest

import src.rules.diagnose as diagnose_module
from src.model.predict import predict_top3
from src.rules.diagnose import diagnose

QUESTION_BLAST = "Bạn có thấy vết trên lá lúa hình thoi không?"
QUESTION_BROWN = "Bạn có thấy đốm màu nâu dạng tròn hoặc bầu dục không?"


def test_diagnose_stub_with_unknown_answers_returns_safe_explanation():
    result = diagnose(predict_top3("khong_doc_anh.jpg"), lambda _: None)
    assert result["ket_luan"] is None
    assert result["do_tin_cay"] is None
    assert result["luat_da_dung"] == []
    assert result["nguon"] == []
    assert result["vet"] == []
    assert "Chưa đủ chắc, liên hệ cán bộ khuyến nông" in result["giai_thich"]


def test_diagnose_unique_supported_suggestion_has_real_rule_trace_and_source():
    result = diagnose(predict_top3("gia.jpg"), lambda q: q == QUESTION_BLAST)
    assert result["ket_luan"] == "dao_on"
    assert result["do_tin_cay"] is None
    assert result["luat_da_dung"] == ["DO01", "DO12"]
    assert [step["id"] for step in result["vet"]] == result["luat_da_dung"]
    assert "DO01" in result["giai_thich"] and "DO12" in result["giai_thich"]
    assert "gợi ý" in result["giai_thich"]
    assert "S1" in result["giai_thich"]
    assert any("khuyennongvn.gov.vn" in source for source in result["nguon"])


def test_diagnose_multiple_suggestions_do_not_force_one_label():
    result = diagnose(predict_top3("gia.jpg"),
                      lambda q: q in {QUESTION_BLAST, QUESTION_BROWN})
    assert result["ket_luan"] is None
    assert "Chưa đủ chắc" in result["giai_thich"]
    assert "DO01" in result["luat_da_dung"]
    assert "DN01" in result["luat_da_dung"]


def test_diagnose_one_suggestion_with_other_unknowns_remains_uncertain():
    result = diagnose(predict_top3("gia.jpg"),
                      lambda q: True if q == QUESTION_BLAST else None)
    assert result["ket_luan"] is None
    assert "Chưa đủ chắc" in result["giai_thich"]


def test_diagnose_negative_answers_do_not_imply_healthy_leaf():
    top3 = [("la_khoe", .9), ("dao_on", .06), ("dom_nau", .03)]
    result = diagnose(top3, lambda _: False)
    assert result["ket_luan"] is None
    assert result["do_tin_cay"] is None
    assert "Chưa đủ chắc" in result["giai_thich"]


@pytest.mark.parametrize("answer", [True, None])
def test_diagnose_asks_shared_attribute_only_once_in_whole_session(tmp_path, monkeypatch, answer):
    document = json.loads(diagnose_module.RULES_PATH.read_text(encoding="utf-8"))
    next(rule for rule in document["rules"] if rule["id"] == "BL01")["neu"] = [
        "vet_la_hinh_thoi=co"
    ]
    rules_copy = tmp_path / "rules_copy.json"
    rules_copy.write_text(json.dumps(document, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(diagnose_module, "RULES_PATH", rules_copy)
    questions = []

    def ask(question):
        questions.append(question)
        return answer

    diagnose(predict_top3("gia.jpg"), ask)
    assert Counter(questions)[QUESTION_BLAST] == 1
    assert max(Counter(questions).values()) == 1


def test_diagnose_does_not_mutate_cnn_input():
    top3 = predict_top3("gia.jpg")
    original = copy.deepcopy(top3)
    diagnose(top3, lambda _: False)
    assert top3 == original


@pytest.mark.parametrize("top3", [
    [], [("dao_on", .5)], [("dao_on", .5), ("dao_on", .3), ("bac_la", .1)],
    [("sai", .5), ("dao_on", .3), ("bac_la", .1)],
    [("dao_on", math.nan), ("bac_la", .2), ("dom_nau", .1)],
    [("dao_on", math.inf), ("bac_la", .2), ("dom_nau", .1)],
    [("dao_on", .5), ("bac_la", .2), ("dom_nau", -.1)],
    [("dao_on", .8), ("bac_la", .7), ("dom_nau", .1)],
    [("dao_on", .2), ("bac_la", .5), ("dom_nau", .1)],
    [("dao_on", True), ("bac_la", 0), ("dom_nau", 0)],
    [("dao_on", "0.5"), ("bac_la", .2), ("dom_nau", .1)],
    [("dao_on", 10 ** 1000), ("bac_la", .2), ("dom_nau", .1)],
])
def test_diagnose_rejects_invalid_top3_before_asking(top3):
    questions = []
    with pytest.raises(ValueError):
        diagnose(top3, lambda q: questions.append(q))
    assert questions == []


def test_diagnose_accepts_zero_probability_without_inventing_confidence():
    result = diagnose([("dao_on", 1.), ("bac_la", 0.), ("dom_nau", 0.)], lambda _: None)
    assert result["ket_luan"] is None
    assert result["do_tin_cay"] is None


def test_diagnose_rejects_invalid_callback_result():
    with pytest.raises(ValueError, match="True, False hoặc None"):
        diagnose(predict_top3("gia.jpg"), lambda _: "không rõ")


def test_diagnose_reports_missing_knowledge_file(tmp_path, monkeypatch):
    monkeypatch.setattr(diagnose_module, "RULES_PATH", tmp_path / "khong_ton_tai.json")
    with pytest.raises(ValueError, match="Không đọc được"):
        diagnose(predict_top3("gia.jpg"), lambda _: None)
