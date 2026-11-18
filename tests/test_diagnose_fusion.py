"""Kiểm tra chính sách phối hợp luật và xác suất, không đổi hợp đồng kết quả."""
import json
from collections import Counter

import pytest

import src.rules.diagnose as module
from src.rules.backward import VOCABULARY_PATH

CNN = [("dao_on", .55), ("dom_nau", .4), ("bac_la", .03)]


def fake_fusion(monkeypatch, label):
    """Dùng xác suất giả trong test để tách kiểm tra chính sách khỏi CPD."""
    calls = []

    def combine(top3, facts):
        calls.append((top3, set(facts)))
        return {
            "ket_luan": label, "do_tin_cay_dieu_chinh": .8 if label else .4,
            "phuong_phap_bayes": "bản giả kiểm thử", "ghi_chu": [],
            "nguong_ket_luan": .6,
        }

    monkeypatch.setattr(module, "ket_hop_cnn_bayes", combine)
    return calls


@pytest.mark.parametrize("bayes_label, expected", [
    ("dao_on", "dao_on"), ("bac_la", None), (None, None),
])
def test_conclusion_requires_agreement_with_supported_rule(monkeypatch, bayes_label, expected):
    calls = fake_fusion(monkeypatch, bayes_label)
    result = module.diagnose(CNN, lambda q: "hình thoi" in q)
    assert result["ket_luan"] == expected
    assert result["do_tin_cay"] is None
    assert len(calls) == 1
    assert "suy_luan=nghi_dao_on" not in calls[0][1]
    assert "CNN–Bayes" in result["giai_thich"]
    if bayes_label == "bac_la":
        assert "không đồng thuận" in result["giai_thich"]


@pytest.mark.parametrize("answer", [None, False, True])
def test_probability_alone_does_not_override_missing_or_multiple_rule_proofs(monkeypatch, answer):
    fake_fusion(monkeypatch, "dao_on")
    result = module.diagnose(CNN, lambda _: answer)
    assert result["ket_luan"] is None
    assert "Chưa đủ chắc" in result["giai_thich"]


def test_whole_session_shares_all_observations_and_asks_each_once(monkeypatch):
    calls = fake_fusion(monkeypatch, None)
    questions = []
    vocabulary = json.loads(VOCABULARY_PATH.read_text(encoding="utf-8"))["thuoc_tinh"]
    askable = {k: d for k, d in vocabulary.items() if d["loai"] == "du_kien_nguoi_dung"}

    def ask(question):
        questions.append(question)
        return None

    result = module.diagnose(CNN, ask)
    assert Counter(questions) == Counter(d["cau_hoi"] for d in askable.values())
    assert calls[0][1] == {f"{key}=chua_biet" for key in askable}
    assert result["vet"] == []


def test_confirmation_for_recommendation_is_collected_without_inventing_disease(monkeypatch):
    fake_fusion(monkeypatch, None)
    result = module.diagnose(CNN, lambda q: q == "Ruộng đã được xác định là nhiễm bệnh đốm nâu chưa?")
    assert "DN10" in result["luat_da_dung"]
    assert result["ket_luan"] is None
    assert "vụ tiếp theo" in result["giai_thich"]


def test_real_cnn_bayes_disagreement_keeps_the_rule_trace_but_abstains():
    """Ca tái hiện lỗi tích hợp từ rà soát, dùng CPD thật thay bản giả."""
    cnn = [("bac_la", .9999), ("dao_on", .00005), ("dom_nau", .00003)]
    result = module.diagnose(cnn, lambda q: "hình thoi" in q)
    assert result["ket_luan"] is None
    assert result["do_tin_cay"] is None
    assert "DO01" in result["luat_da_dung"]
    assert "không đồng thuận" in result["giai_thich"]
