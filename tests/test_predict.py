"""Kiểm thử hợp đồng dự đoán CNN thật, không dùng xác suất minh họa."""
import numpy as np
import pytest
from PIL import Image

from src.model import predict


class FakeModel:
    def predict(self, batch, verbose=0):
        assert batch.shape == (1, 224, 224, 3)
        return np.array([[0.05, 0.65, 0.20, 0.10]])


def test_predict_top3_loads_model_and_returns_sorted_real_output(tmp_path, monkeypatch):
    image_path = tmp_path / "la.jpg"
    Image.new("RGB", (30, 12), color=(30, 80, 10)).save(image_path)
    monkeypatch.setattr(predict, "MODEL_PATH", tmp_path / "model.keras")
    predict.MODEL_PATH.touch()
    monkeypatch.setattr(predict, "_load_model", lambda path: FakeModel())
    monkeypatch.setattr(predict, "IS_STUB", True)

    assert predict.predict_top3(image_path) == [
        ("bac_la", 0.65),
        ("dom_nau", 0.20),
        ("la_khoe", 0.10),
    ]
    assert predict.IS_STUB is False


def test_predict_top3_raises_for_missing_image(tmp_path, monkeypatch):
    monkeypatch.setattr(predict, "MODEL_PATH", tmp_path / "model.keras")
    with pytest.raises(FileNotFoundError):
        predict.predict_top3(tmp_path / "missing.jpg")


def test_predict_top3_raises_for_missing_model(tmp_path, monkeypatch):
    image_path = tmp_path / "la.jpg"
    Image.new("RGB", (8, 8)).save(image_path)
    monkeypatch.setattr(predict, "MODEL_PATH", tmp_path / "missing.keras")
    with pytest.raises(FileNotFoundError):
        predict.predict_top3(image_path)


def test_predict_top3_rejects_corrupt_image(tmp_path, monkeypatch):
    image_path = tmp_path / "corrupt.jpg"
    image_path.write_bytes(b"khong phai anh")
    monkeypatch.setattr(predict, "MODEL_PATH", tmp_path / "model.keras")
    predict.MODEL_PATH.touch()
    monkeypatch.setattr(predict, "_load_model", lambda path: FakeModel())
    with pytest.raises(ValueError, match="Ảnh không hợp lệ"):
        predict.predict_top3(image_path)


def test_predict_top3_rejects_invalid_model_output(tmp_path, monkeypatch):
    image_path = tmp_path / "la.jpg"
    Image.new("RGB", (8, 8)).save(image_path)

    class BadModel:
        def predict(self, batch, verbose=0):
            return np.array([[0.1, float("nan"), 0.2, 0.7]])

    monkeypatch.setattr(predict, "MODEL_PATH", tmp_path / "model.keras")
    predict.MODEL_PATH.touch()
    monkeypatch.setattr(predict, "_load_model", lambda path: BadModel())
    with pytest.raises(ValueError, match="[Đđ]ầu ra mô hình"):
        predict.predict_top3(image_path)
