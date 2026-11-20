"""Điều phối ảnh bằng predictor giả, không tải TensorFlow."""
import pytest

from src.app import chan_doan
from src.model import predict


def test_image_flow_calls_predictor_then_diagnosis(tmp_path, monkeypatch):
    top3 = [("dao_on", .55), ("dom_nau", .4), ("bac_la", .03)]
    calls = []
    image_path = tmp_path / "test.jpg"
    image_path.touch()
    model_path = tmp_path / "model.keras"
    model_path.touch()
    monkeypatch.setattr(predict, "MODEL_PATH", model_path)
    monkeypatch.setattr(predict, "IS_STUB", False)
    monkeypatch.setattr(predict, "predict_top3", lambda path: calls.append(path) or top3)
    expected = {"ket_luan": "dao_on", "do_tin_cay": None,
                "luat_da_dung": ["DO01"], "nguon": ["S1"]}

    def diagnose(items, callback):
        assert items == top3
        assert callback("Câu hỏi kiểm thử?") is None
        return expected

    monkeypatch.setattr(chan_doan, "diagnose", diagnose, raising=False)
    assert chan_doan.diagnose_image(image_path, lambda _: None) == expected
    assert calls == [image_path]


def test_image_flow_reports_missing_model_without_claiming_a_diagnosis(tmp_path, monkeypatch):
    image_path = tmp_path / "la.jpg"
    image_path.touch()
    monkeypatch.setattr(predict, "MODEL_PATH", tmp_path / "missing.keras")
    result = chan_doan.diagnose_image(image_path, lambda q: "hình thoi" in q)
    assert result["ket_luan"] is None
    assert result["do_tin_cay"] is None
    assert "Chưa có mô hình CNN" in result["giai_thich"]
    assert result["luat_da_dung"] == []


def test_predictor_errors_are_not_hidden_as_uncertain_diagnoses(monkeypatch):
    def missing(_):
        raise FileNotFoundError("thiếu ảnh hoặc mô hình")

    monkeypatch.setattr(predict, "predict_top3", missing)
    with pytest.raises(FileNotFoundError, match="thiếu ảnh"):
        chan_doan.diagnose_image("missing.jpg", lambda _: None)
