"""Chạy thử khung; CNN cần ảnh thật và artifact .keras đã huấn luyện."""
import json
import sys
from pathlib import Path

from src.model.predict import MODEL_PATH
from src.search.run import plan_route


def main() -> None:
    """Đọc dữ liệu mẫu, in lộ trình CN1 và trạng thái CN2/CN3."""
    duong_dan = Path(__file__).resolve().parent / "data/sample/maps/map_4x4.json"
    ban_do = json.loads(duong_dan.read_text(encoding="utf-8"))
    print(f"Bản đồ minh họa: {ban_do['rows']} × {ban_do['cols']}")
    trang_thai_cnn = "chưa có mô hình" if not MODEL_PATH.is_file() else "đã có artifact"
    print(f"CN3 — {trang_thai_cnn}; cần ảnh đầu vào để dự đoán.")
    lo_trinh = plan_route(ban_do, ban_do["k"], ban_do["p"], "hill")
    print(f"CN1 — leo đồi: quãng đường {lo_trinh['tong_quang_duong']}, "
          f"về trạm {lo_trinh['so_lan_ve_tram']} lần")
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
