"""Chạy thử khung; CNN cần ảnh thật và artifact .keras đã huấn luyện."""
import json
import sys
from pathlib import Path

from src.model.predict import MODEL_PATH
from src.search.run import plan_route


def main() -> None:
    """Đọc dữ liệu mẫu, in giải thích CN2 và báo phần CN1 chưa triển khai."""
    duong_dan = Path(__file__).resolve().parent / "data/sample/maps/map_4x4.json"
    ban_do = json.loads(duong_dan.read_text(encoding="utf-8"))
    print(f"Bản đồ minh họa: {ban_do['rows']} × {ban_do['cols']}")
    trang_thai_cnn = "chưa có mô hình" if not MODEL_PATH.is_file() else "đã có artifact"
    print(f"CN3 — {trang_thai_cnn}; cần ảnh đầu vào để dự đoán.")
    try:
        print("CN1:", plan_route(ban_do, ban_do["k"], ban_do["p"], "hill"))
    except NotImplementedError:
        print("CN1: chưa cài đặt")
    trang_thai_cn2 = (
        "đã có mô hình CNN; chờ ảnh đầu vào để chẩn đoán tích hợp."
        if MODEL_PATH.is_file()
        else "chờ ảnh thật và mô hình CNN đã huấn luyện để chẩn đoán tích hợp."
    )
    print(f"CN2: {trang_thai_cn2}")


if __name__ == "__main__":
    # Bảo đảm in tiếng Việt khi Windows chuyển đầu ra qua pipe dùng mã hóa cũ.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    main()
