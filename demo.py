"""Chạy thử CN2 với CNN giả và bản đồ mẫu; không cần thư viện học máy."""
import json
import sys
from pathlib import Path

from src.app.chan_doan import diagnose_image
from src.model.predict import IS_STUB
from src.search.run import plan_route


def main() -> None:
    """Đọc dữ liệu mẫu, in giải thích CN2 và báo phần CN1 chưa triển khai."""
    duong_dan = Path(__file__).resolve().parent / "data/sample/maps/map_4x4.json"
    ban_do = json.loads(duong_dan.read_text(encoding="utf-8"))
    print(f"Bản đồ minh họa: {ban_do['rows']} × {ban_do['cols']}")
    print(f"CN3 — dự đoán GIẢ (IS_STUB={IS_STUB}), không phải kết quả CNN:")
    try:
        print("CN1:", plan_route(ban_do, ban_do["k"], ban_do["p"], "hill"))
    except NotImplementedError:
        print("CN1: chưa cài đặt")
    result = diagnose_image("anh_gia_khong_doc.jpg", lambda cau_hoi: None)
    print("CN2:", result["ket_luan"] or "chưa đủ chắc")
    print("CN2 — giải thích:")
    print(result["giai_thich"])
    print("CN2 đã chạy hệ luật và CNN–Bayes với dự đoán GIẢ; chưa đánh giá ảnh thật.")


if __name__ == "__main__":
    # Bảo đảm in tiếng Việt khi Windows chuyển đầu ra qua pipe dùng mã hóa cũ.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    main()
