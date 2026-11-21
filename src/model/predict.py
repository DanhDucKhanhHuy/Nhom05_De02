"""Dự đoán ba lớp bệnh đứng đầu bằng mô hình Keras đã huấn luyện."""
from functools import lru_cache
from pathlib import Path
from typing import cast

import numpy as np
from PIL import Image, UnidentifiedImageError

from src.contracts import Top3

CLASS_NAMES = ("dao_on", "bac_la", "dom_nau", "la_khoe")
IMAGE_SIZE = (224, 224)
MODEL_PATH = Path(__file__).resolve().parents[2] / "models" / "rice_leaf_classifier.keras"
# Chuyển False sau lần dự đoán hợp lệ đầu tiên đã nạp mô hình thật.
IS_STUB = True


@lru_cache(maxsize=2)
def _load_model(model_path: Path) -> object:
    """Nạp mô hình có trọng số; TensorFlow chỉ được nạp khi thật sự dự đoán."""
    try:
        from tensorflow.keras.models import load_model
    except ImportError as exc:
        raise RuntimeError("Cần cài TensorFlow theo requirements.txt để dự đoán.") from exc
    return load_model(model_path)


def _read_image(image_path: Path) -> np.ndarray:
    """Đọc ảnh RGB, đổi kích thước và giữ thang pixel [0, 255]."""
    try:
        with Image.open(image_path) as image:
            image = image.convert("RGB").resize(IMAGE_SIZE, Image.Resampling.BILINEAR)
            return np.asarray(image, dtype=np.float32)
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise ValueError(f"Ảnh không hợp lệ: {image_path}") from exc


def predict_top3(duong_dan_anh: str | Path) -> Top3:
    """Nạp ảnh và mô hình thật, trả ba lớp theo xác suất giảm dần."""
    image_path = Path(duong_dan_anh)
    if not image_path.is_file():
        raise FileNotFoundError(f"Không tìm thấy ảnh: {image_path}")
    if not MODEL_PATH.is_file():
        raise FileNotFoundError(f"Không tìm thấy mô hình đã huấn luyện: {MODEL_PATH}")

    image = _read_image(image_path)
    model = _load_model(MODEL_PATH)
    probabilities = np.asarray(model.predict(image[None, ...], verbose=0), dtype=float)
    if probabilities.shape != (1, len(CLASS_NAMES)):
        raise ValueError("Đầu ra mô hình phải có đúng bốn xác suất theo thứ tự lớp chuẩn.")
    scores = probabilities[0]
    if not np.isfinite(scores).all() or (scores < 0).any() or (scores > 1).any():
        raise ValueError("Đầu ra mô hình chứa xác suất không hợp lệ.")
    if not np.isclose(scores.sum(), 1.0, atol=1e-5):
        raise ValueError("Đầu ra mô hình phải là xác suất softmax có tổng bằng 1.")

    order = np.argsort(scores)[::-1][:3]
    result = [(CLASS_NAMES[index], float(scores[index])) for index in order]
    global IS_STUB
    IS_STUB = False
    return cast(Top3, result)
